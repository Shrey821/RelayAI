# UMS Browser Companion Extension

The official browser extension for the **Universal Memory Schema (UMS)**.  
Enables **1-Click AI Memory Ingestion & Verification** directly inside your authenticated `claude.ai` and `chatgpt.com` sessions without manual copy-pasting.

---

## 🚀 How to Install in 30 Seconds (Chrome, Brave, Arc, Edge)

1. Open your browser and navigate to the Extensions page:
   - **Chrome / Brave**: `chrome://extensions`
   - **Edge**: `edge://extensions`
   - **Arc**: Open Settings → Extensions
2. Enable **"Developer mode"** (toggle in the top right corner).
3. Click the **"Load unpacked"** button in the top left.
4. Select the `extension/` directory inside this cloned repository.
5. Pin the **UMS Memory Bridge** extension to your toolbar!

---

## ⌨️ Universal Keyboard Shortcuts

* **`Alt + Shift + R`** (Mac: **`Option + Shift + R`**): Instantly opens the RelayAI popup anywhere on your screen.
* **`Alt + Shift + U`** (Mac: **`Option + Shift + U`**): 1-Click Transfer—distills the active chat and injects it into your target AI model without opening the popup.

---

## ⚡ How to Use

1. Ensure the local UMS server is running (`python3 run.py` at `http://127.0.0.1:8000`).
2. Open **[claude.ai](https://claude.ai)** or **[chatgpt.com](https://chatgpt.com)** in your browser.
3. Click the **UMS icon** in your extensions toolbar:
   - It will automatically detect your active tab and account.
   - Click **"⚡ 1-Click Inject Memory into Account"**.
   - Your memory payload is automatically placed and submitted into your active AI session!
4. After ingestion completes, click **"🔍 Send Verification Query in Chat"**:
   - Sends `"I updated my memory. What did you learn about me?"` into the session.
   - Verifies what the target model absorbed.

---

## 🔄 How to Use Chat Thread Transfer (Zero-Token Handoff)

1. Open an ongoing conversation in **ChatGPT** or **Claude.ai** where you are debugging or writing code.
2. Click the **UMS icon** and select the **"🔄 Chat Handoff"** tab.
3. Click **"⚡ 1-Click Distill & Transfer This Chat"**:
   - The extension reads the active thread from your page without using external tokens.
   - Deterministically extracts:
     - Primary objective & goal
     - Tech stack & environment
     - Architectural & library decisions
     - Latest working code block (deduplicating previous failed attempts)
     - Immediate next unresolved task
   - Reduces the conversation payload by **>90%** while burning **0 extra LLM tokens**.
4. Click **"🚀 Open Target Tab & Inject Context"**:
   - Opens the target platform (e.g., Claude.ai if you were on ChatGPT) and places the primed handoff prompt directly into the chat box.
5. The target LLM immediately continues solving your next task with full context!
