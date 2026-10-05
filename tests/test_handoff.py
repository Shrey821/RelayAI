"""
Unit & Integration Tests for UMS Chat Handoff & Context Transfer Engine
Tests deterministic zero-token extraction, deduplication, and API endpoints.
"""

import unittest
import json
import io
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.chat_handoff import distill_chat_thread
from server.app import UMSRequestHandler

SAMPLE_CONVERSATION = """
User: I am building a realtime collaborative editor in Next.js and TypeScript. I want to add Redis pub/sub.
Assistant: Sounds good! Here is how you can use ioredis to publish messages.
User: We tried ioredis but got connection timeouts on serverless edge functions.
Assistant: Ah, serverless functions can't maintain persistent TCP sockets easily.
User: We decided to switch to Upstash Redis because we are running on Vercel Edge functions.
Assistant: Great choice. Upstash has an HTTP-based REST client that works seamlessly in Edge environments.
User: Here is my working code:
```typescript
import { Redis } from '@upstash/redis'

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
})

export async function publishEvent(channel: string, data: any) {
  return await redis.publish(channel, JSON.stringify(data))
}
```
Assistant: That looks clean and ready.
User: Now how do I handle subscribing to the messages using Server-Sent Events (SSE) in the App Router?
"""

class DummyServer:
    server_address = ("127.0.0.1", 8000)

class MockRequest:
    def __init__(self, raw_http_bytes: bytes):
        self.rfile = io.BytesIO(raw_http_bytes)
        self.wfile = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if "r" in mode:
            return self.rfile
        return self.wfile

    def sendall(self, b):
        self.wfile.write(b)

class TestChatHandoff(unittest.TestCase):
    def test_distill_chat_thread_deterministic(self):
        result = distill_chat_thread(SAMPLE_CONVERSATION, source_provider="chatgpt", target_provider="claude")

        self.assertIn("realtime collaborative editor", result["primary_goal"].lower())
        self.assertTrue(result["has_code_artifact"])
        self.assertIn("Upstash", result["handoff_primer"])
        self.assertIn("typescript", [t.lower() for t in result["detected_tech"]])
        self.assertIn("Server-Sent Events", result["immediate_next_task"])
        self.assertIn("### 📋 SESSION CONTEXT & OBJECTIVE", result["handoff_primer"])
        self.assertIn("### 🎯 IMMEDIATE NEXT TASK TO SOLVE", result["handoff_primer"])

    def test_handoff_empty_handling(self):
        result = distill_chat_thread("Just a quick test question here", "claude", "chatgpt")
        self.assertEqual(result["source_provider"], "claude")
        self.assertEqual(result["target_provider"], "chatgpt")
        self.assertFalse(result["has_code_artifact"])
        self.assertIsNotNone(result["handoff_primer"])

    def test_handoff_api_endpoints(self):
        # 1. Test GET /api/handoff/demo
        headers = ["GET /api/handoff/demo HTTP/1.1", "Host: localhost", "\r\n"]
        mock_req = MockRequest("\r\n".join(headers).encode("utf-8"))
        handler = UMSRequestHandler(mock_req, ("127.0.0.1", 12345), DummyServer())

        response = mock_req.wfile.getvalue().decode("utf-8")
        parts = response.split("\r\n\r\n", 1)
        self.assertIn("200 OK", parts[0])
        demo_data = json.loads(parts[1])
        self.assertIn("demo_chat", demo_data)
        self.assertIn("Next.js 15", demo_data["demo_chat"])

        # 2. Test POST /api/handoff/distill
        body = json.dumps({
            "raw_chat": demo_data["demo_chat"],
            "source": "chatgpt",
            "target": "claude"
        }).encode("utf-8")
        headers = [
            "POST /api/handoff/distill HTTP/1.1",
            "Host: localhost",
            "Content-Type: application/json",
            f"Content-Length: {len(body)}",
            "\r\n"
        ]
        mock_req2 = MockRequest("\r\n".join(headers).encode("utf-8") + body)
        handler2 = UMSRequestHandler(mock_req2, ("127.0.0.1", 12345), DummyServer())

        response2 = mock_req2.wfile.getvalue().decode("utf-8")
        parts2 = response2.split("\r\n\r\n", 1)
        self.assertIn("200 OK", parts2[0])
        distill_data = json.loads(parts2[1])
        self.assertIn("handoff_primer", distill_data)
        self.assertIn("token_savings_percent", distill_data)
        self.assertGreaterEqual(distill_data["token_savings_percent"], 0.0)
    def test_conversations_json_unpacking(self):
        # Sample ChatGPT conversations.json export object
        chatgpt_json = json.dumps([
            {
                "title": "FastAPI Migration",
                "mapping": {
                    "node_1": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["We are migrating from Flask to FastAPI with Pydantic v2."]}
                        }
                    },
                    "node_2": {
                        "message": {
                            "author": {"role": "assistant"},
                            "content": {"parts": ["Great choice! FastAPI offers automatic OpenAPI documentation."]}
                        }
                    },
                    "node_3": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["Here is my main router:\n```python\nfrom fastapi import FastAPI\napp = FastAPI()\n```\nHow do I add CORS middleware?"]}
                        }
                    }
                }
            }
        ])

        result = distill_chat_thread(chatgpt_json, "chatgpt", "claude")
        self.assertIn("fastapi", result["primary_goal"].lower())
        self.assertTrue(result["has_code_artifact"])
        self.assertIn("cors middleware", result["immediate_next_task"].lower())

    def test_case_study_non_engineering_handoff(self):
        case_study_chat = """User: i have a quiz based on a case study give me a summary and cover all the points
Assistant: Here is the comprehensive summary of the case study on Swiggy delivery logistics:
1. Routing optimization was critical for reducing turnaround time.
2. Demand surges during rain created driver shortages.
3. Pricing strategies included dynamic surge fees.
User: Now give me the top 5 questions that might come in the quiz."""

        res = distill_chat_thread(case_study_chat, source_provider="chatgpt", target_provider="claude")

        # Must NOT assume engineering or hallucinate "Edge" tech stack
        self.assertNotIn("Technology Environment: Edge", res["handoff_primer"])
        self.assertNotIn("active engineering conversation", res["handoff_primer"])
        
        # Must retain the full case study transcript so target AI has 100% context
        self.assertIn("Swiggy delivery logistics", res["handoff_primer"])
        self.assertIn("Routing optimization", res["handoff_primer"])
        self.assertIn("Demand surges during rain", res["handoff_primer"])
        self.assertIn("top 5 questions", res["immediate_next_task"])
        self.assertIn("### 💬 CONVERSATION TRANSCRIPT & SHARED CONTEXT", res["handoff_primer"])

    def test_handoff_dual_modes(self):
        sample = """User: What are the 3 pillars of Observability?
Assistant: The three pillars are Metrics, Logs, and Traces.
1. Metrics provide numerical time-series aggregations.
2. Logs record distinct timestamped events.
3. Traces map end-to-end request journeys across services.
User: Can you show me an example of an OpenTelemetry trace in Python?"""

        # 1. Full Mode
        res_full = distill_chat_thread(sample, "chatgpt", "gemini", mode="full")
        self.assertEqual(res_full["mode"], "full")
        self.assertIn("### 💬 CONVERSATION TRANSCRIPT & SHARED CONTEXT", res_full["handoff_primer"])
        self.assertIn("OpenTelemetry trace in Python", res_full["immediate_next_task"])
        self.assertIn("Metrics, Logs, and Traces", res_full["handoff_primer"])

        # 2. Summary Mode
        res_summary = distill_chat_thread(sample, "chatgpt", "gemini", mode="summary")
        self.assertEqual(res_summary["mode"], "summary")
        self.assertIn("### 💡 SYNTHESIZED KNOWLEDGE & ESTABLISHED POINTS", res_summary["handoff_primer"])
        self.assertIn("OpenTelemetry trace in Python", res_summary["immediate_next_task"])
        self.assertGreaterEqual(res_summary["token_savings_percent"], 60.0)

    def test_multi_llm_providers(self):
        providers = ["chatgpt", "claude", "gemini", "perplexity", "deepseek", "mistral", "copilot"]
        sample = "User: Hello there\nAssistant: Hi, how can I assist you?"

        for src in providers[:3]:
            for tgt in providers[3:]:
                res = distill_chat_thread(sample, source_provider=src, target_provider=tgt, mode="full")
                self.assertIsNotNone(res["handoff_primer"])
                self.assertEqual(res["source_provider"], src)
                self.assertEqual(res["target_provider"], tgt)

    def test_ending_directive_context_recovered(self):
        # 1. Thread ending on user turn
        sample_user = "User: How do I configure Redis?\nAssistant: Install redis-py.\nUser: What port does it use?"
        res_user = distill_chat_thread(sample_user, "chatgpt", "claude")
        self.assertIn('Simply reply with "Context recovered" if done.', res_user["handoff_primer"])

        # 2. Thread ending on assistant turn
        sample_asst = "User: How do I configure Redis?\nAssistant: Redis defaults to port 6379."
        res_asst = distill_chat_thread(sample_asst, "chatgpt", "claude")
        self.assertEqual(res_asst["immediate_next_task"], "Context recovered if done.")
        self.assertIn('Simply reply with "Context recovered" if done.', res_asst["handoff_primer"])

    def test_comprehensive_condensed_summary_coverage(self):
        multi_turn_chat = """User: We are designing an event-driven architecture using Apache Kafka and Python.
Assistant: Kafka is ideal for decoupled asynchronous pipelines. You should use kafka-python or confluent-kafka.
User: We tried kafka-python but had issues with SASL SSL authentication.
Assistant: confluent-kafka wraps librdkafka and handles SASL_SSL much better.
User: We decided to switch to confluent-kafka. Make sure it uses TLS 1.3 and auto-commit is disabled.
Assistant: Here is the producer configuration:
1. bootstrap.servers must point to your brokers.
2. security.protocol is SASL_SSL.
3. enable.auto.commit must be false for exactly-once processing semantics.
User: Here is our consumer setup:
```python
from confluent_kafka import Consumer
conf = {'bootstrap.servers': 'localhost:9092', 'group.id': 'group1', 'enable.auto.commit': False}
c = Consumer(conf)
```
Assistant: That consumer correctly disables auto-commit. Make sure to commit offsets manually after processing.
User: Now how do we handle dead-letter queues (DLQ) when serialization fails?"""

        res = distill_chat_thread(multi_turn_chat, "chatgpt", "claude", mode="summary")
        primer = res["handoff_primer"]

        # 1. Primary goal
        self.assertIn("Apache Kafka", primer)
        # 2. Key decisions
        self.assertIn("confluent-kafka", primer)
        # 3. User requirements & constraints
        self.assertIn("### 📌 USER REQUIREMENTS, INQUIRIES & CONSTRAINTS", primer)
        self.assertIn("auto-commit is disabled", primer)
        # 4. Conversation progression & milestones
        self.assertIn("### 🔄 CONVERSATION PROGRESSION & MILESTONES", primer)
        # 5. Synthesized knowledge points
        self.assertIn("### 💡 SYNTHESIZED KNOWLEDGE & ESTABLISHED POINTS", primer)
        self.assertIn("librdkafka", primer)
        self.assertIn("exactly-once processing", primer)
        # 6. Code artifact
        self.assertIn("### 💻 LATEST WORKING ARTIFACT (PYTHON)", primer)
        self.assertIn("confluent_kafka", primer)
        # 7. Next task
        self.assertIn("dead-letter queues", res["immediate_next_task"])
        self.assertIn('Simply reply with "Context recovered" if done.', primer)
        self.assertGreaterEqual(res["token_savings_percent"], 60.0)

if __name__ == "__main__":
    unittest.main()

