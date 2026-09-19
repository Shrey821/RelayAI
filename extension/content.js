/**
 * UMS Browser Companion - Content Script
 * Executes directly within claude.ai, chatgpt.com, and the local UMS web app (127.0.0.1:8000).
 * Automates memory ingestion, verification queries, active chat thread scraping, and cross-tab bridging.
 */

// Guard against duplicate injection
if (!window.__UMS_CONTENT_SCRIPT_INITIALIZED__) {
  window.__UMS_CONTENT_SCRIPT_INITIALIZED__ = true;

  // Message Listener from Background / Popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "ping") {
      const prov = getPageProvider();
      sendResponse({
        status: "active",
        provider: prov,
        url: window.location.href
      });
      return true;
    }

  if (request.action === "inject_memory") {
    const text = request.text;
    const provider = request.provider;

    if (provider === "claude") {
      injectIntoClaude(text).then(result => sendResponse(result));
    } else if (provider === "chatgpt") {
      injectIntoChatGPT(text).then(result => sendResponse(result));
    } else {
      sendResponse({ status: "error", message: "Unsupported provider" });
    }
    return true;
  }

  if (request.action === "inject_handoff") {
    const text = request.text;
    injectDirectText(text, "Handoff Primer").then(result => sendResponse(result));
    return true;
  }

  if (request.action === "scrape_chat_thread") {
    scrapeChatThread().then(result => sendResponse(result));
    return true;
  }

  if (request.action === "send_verification") {
    const query = request.query;
    sendVerificationQuery(query).then(result => sendResponse(result));
    return true;
  }
});

// Bridge for local web dashboard (http://127.0.0.1:8000)
if (window.location.hostname.includes("127.0.0.1") || window.location.hostname.includes("localhost")) {
  window.addEventListener("message", (event) => {
    if (!event.data) return;
    if (event.data.type === "UMS_PING") {
      window.postMessage({ type: "UMS_EXTENSION_READY", version: "1.1.0" }, "*");
      chrome.runtime.sendMessage({ action: "get_open_ai_tabs" }, (response) => {
        if (response) {
          window.postMessage({ type: "UMS_DETECT_TABS_RESPONSE", data: response }, "*");
        }
      });
    }
    if (event.data.type === "UMS_DETECT_TABS") {
      chrome.runtime.sendMessage({ action: "get_open_ai_tabs" }, (response) => {
        if (response) {
          window.postMessage({ type: "UMS_DETECT_TABS_RESPONSE", data: response }, "*");
        }
      });
    }
    if (event.data.type === "UMS_AUTO_TRANSFER") {
      chrome.runtime.sendMessage({
        action: "auto_transfer_chat",
        ...event.data.payload
      }, (response) => {
        window.postMessage({ type: "UMS_AUTO_TRANSFER_RESPONSE", data: response }, "*");
      });
    }
  });

  // Signal web page that UMS extension is loaded and active
  window.postMessage({ type: "UMS_EXTENSION_READY", version: "1.1.0" }, "*");
}
} // End __UMS_CONTENT_SCRIPT_INITIALIZED__

function getPageProvider() {
  const host = window.location.hostname.toLowerCase();
  if (host.includes("chatgpt.com") || host.includes("openai.com")) return "chatgpt";
  if (host.includes("claude.ai")) return "claude";
  if (host.includes("gemini.google.com")) return "gemini";
  if (host.includes("perplexity.ai")) return "perplexity";
  if (host.includes("deepseek.com")) return "deepseek";
  if (host.includes("mistral.ai")) return "mistral";
  if (host.includes("copilot.microsoft.com")) return "copilot";
  return "web";
}

// Robust Chat Scraper across all major LLMs
async function scrapeChatThread() {
  try {
    const provider = getPageProvider();
    let turns = [];

    // 1. Check if user highlighted a specific chat excerpt
    const selection = window.getSelection().toString().trim();
    if (selection && selection.length > 50) {
      return {
        status: "success",
        raw_chat: selection,
        turns_count: 1,
        provider: provider
      };
    }

    // 2. Provider-Specific DOM Parsing
    if (provider === "chatgpt") {
      // ChatGPT Approach A: data-message-author-role
      const roleElements = document.querySelectorAll('[data-message-author-role]');
      if (roleElements && roleElements.length > 0) {
        roleElements.forEach(el => {
          const roleAttr = el.getAttribute('data-message-author-role');
          const role = roleAttr === 'user' ? 'User' : 'Assistant';
          let text = '';
          if (role === 'Assistant') {
            const md = el.querySelector('.markdown') || el.querySelector('.prose') || el;
            text = md.innerText.trim();
          } else {
            const userEl = el.querySelector('.whitespace-pre-wrap') || el;
            text = userEl.innerText.trim();
          }
          if (text) turns.push(`${role}: ${text}`);
        });
      }

      // ChatGPT Approach B: article elements fallback
      if (turns.length === 0) {
        const articles = document.querySelectorAll('article');
        articles.forEach(art => {
          const isUser = art.querySelector('[data-message-author-role="user"]') || 
                         art.textContent.includes("You said:") ||
                         art.querySelector('img[alt="User"]');
          const role = isUser ? "User" : "Assistant";
          let text = '';
          if (role === 'Assistant') {
            const md = art.querySelector('.markdown') || art.querySelector('.prose') || art;
            text = md.innerText.trim();
          } else {
            const userEl = art.querySelector('.whitespace-pre-wrap') || art;
            text = userEl.innerText.trim();
          }
          if (text) turns.push(`${role}: ${text}`);
        });
      }
    } else if (provider === "claude") {
      const userSelector = '.font-user-message, [data-testid="user-message"]';
      const claudeSelector = '.font-claude-message, [data-testid="assistant-message"], .prose';

      const containers = document.querySelectorAll(`${userSelector}, ${claudeSelector}`);
      if (containers && containers.length > 0) {
        containers.forEach(el => {
          const isUser = el.matches(userSelector) || el.closest(userSelector);
          const role = isUser ? "User" : "Assistant";
          const text = el.innerText.trim();
          if (text && text.length > 2) turns.push(`${role}: ${text}`);
        });
      }
    } else if (provider === "gemini") {
      // Google Gemini query/response selectors
      const geminiTurns = document.querySelectorAll('user-query, model-response, .query-text, .response-text, div[class*="user-query"], div[class*="model-response"]');
      if (geminiTurns && geminiTurns.length > 0) {
        geminiTurns.forEach(el => {
          const isUser = el.tagName.toLowerCase().includes('user') || el.className.toLowerCase().includes('user');
          const role = isUser ? "User" : "Assistant";
          const text = el.innerText.trim();
          if (text && text.length > 2) turns.push(`${role}: ${text}`);
        });
      }
    } else if (provider === "perplexity") {
      // Perplexity queries and answers
      const pItems = document.querySelectorAll('div[class*="query"], div[class*="answer"], .font-display, .prose');
      pItems.forEach(el => {
        const isUser = el.className.includes('query') || el.className.includes('question') || el.className.includes('font-display');
        const role = isUser ? "User" : "Assistant";
        const text = el.innerText.trim();
        if (text && text.length > 5) turns.push(`${role}: ${text}`);
      });
    } else if (provider === "deepseek") {
      // DeepSeek user and assistant message blocks
      const dsTurns = document.querySelectorAll('div[class*="chat-message"], .ds-markdown');
      dsTurns.forEach(el => {
        const isUser = el.className.includes('user');
        const role = isUser ? "User" : "Assistant";
        const text = el.innerText.trim();
        if (text && text.length > 2) turns.push(`${role}: ${text}`);
      });
    } else if (provider === "mistral") {
      // Mistral Le Chat
      const mTurns = document.querySelectorAll('div[data-role="user"], div[data-role="assistant"], div[class*="user"], div[class*="assistant"]');
      mTurns.forEach(el => {
        const roleAttr = el.getAttribute('data-role');
        const role = (roleAttr === 'user' || el.className.includes('user')) ? "User" : "Assistant";
        const text = el.innerText.trim();
        if (text && text.length > 2) turns.push(`${role}: ${text}`);
      });
    }

    // Approach C: Universal fallback to main conversation body text
    if (turns.length === 0) {
      const mainEl = document.querySelector('main') || document.querySelector('[role="main"]') || document.body;
      const text = mainEl.innerText.trim();
      if (text.length > 30) {
        turns.push(text);
      }
    }

    if (turns.length === 0) {
      return {
        status: "error",
        message: `No active conversation text found on ${provider.toUpperCase()}. Make sure you have a chat open.`
      };
    }

    return {
      status: "success",
      raw_chat: turns.join("\n\n"),
      turns_count: turns.length,
      provider: provider
    };
  } catch (err) {
    return { status: "error", message: err.message };
  }
}

// Ingestion for Claude.ai
async function injectIntoClaude(importText) {
  const memoryPrompt = `Please store and memorize the following developer profile and active context into your long-term memory:\n\n${importText}`;
  return await injectDirectText(memoryPrompt, "Memory payload");
}

// Ingestion for ChatGPT.com
async function injectIntoChatGPT(importText) {
  const memoryPrompt = `Please remember the following long-term preferences and working context for future chats:\n\n${importText}`;
  return await injectDirectText(memoryPrompt, "Memory payload");
}

// Universal Chat Input Text Ingestion across all major LLMs
async function injectDirectText(text, label = "Payload") {
  try {
    const provider = getPageProvider();

    // Universal input field selector supporting ChatGPT, Claude, Gemini, Perplexity, DeepSeek, Mistral, Copilot
    const inputField = 
      document.querySelector('div[contenteditable="true"]') || 
      document.querySelector('#prompt-textarea') || 
      document.querySelector('textarea#chat-input') || 
      document.querySelector('rich-textarea div[contenteditable="true"]') || 
      document.querySelector('div.ql-editor[contenteditable="true"]') || 
      document.querySelector('textarea[placeholder*="Ask"]') || 
      document.querySelector('textarea[placeholder*="DeepSeek"]') || 
      document.querySelector('textarea#userInput') ||
      document.querySelector('textarea');

    if (!inputField) {
      return { status: "error", message: `Could not find chat input field on ${provider.toUpperCase()}. Open a chat first.` };
    }

    // Set text
    if (inputField.tagName && inputField.tagName.toLowerCase() === 'textarea') {
      inputField.value = text;
      inputField.dispatchEvent(new Event('input', { bubbles: true }));
      inputField.dispatchEvent(new Event('change', { bubbles: true }));
    } else {
      inputField.focus();
      document.execCommand('selectAll', false, null);
      document.execCommand('insertText', false, text);
      inputField.dispatchEvent(new Event('input', { bubbles: true }));
      inputField.dispatchEvent(new Event('change', { bubbles: true }));
    }

    // Click send button
    await sleep(400);
    const sendBtn = 
      document.querySelector('button[aria-label="Send Message"]') || 
      document.querySelector('button[aria-label="Send message"]') || 
      document.querySelector('button[data-testid="send-button"]') || 
      document.querySelector('button[aria-label="Send prompt"]') ||
      document.querySelector('button[aria-label*="Submit"]') || 
      document.querySelector('button[aria-label*="Send"]') || 
      document.querySelector('div[role="button"][aria-label*="Send"]') || 
      document.querySelector('button.send-button') || 
      document.querySelector('button[type="submit"]') || 
      document.querySelector('button.bg-accent');

    if (sendBtn && !sendBtn.disabled) {
      sendBtn.click();
      return { status: "success", message: `${label} automatically sent into chat!` };
    } else {
      return { status: "success", message: `${label} placed into chat input. Press Enter to send.` };
    }
  } catch (err) {
    return { status: "error", message: err.message };
  }
}

// Send Verification Query
async function sendVerificationQuery(query) {
  return await injectDirectText(query, "Verification query");
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
