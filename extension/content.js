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

// =========================================================================
// Dynamic In-Page Floating Relay Pill (Matte Carbon & Zinc Theme)
// Automatically detects active target AI tab and displays platform hotkey
// =========================================================================

function isMacPlatform() {
  return /Mac|iPod|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
}

function initFloatingRelayPill() {
  const currentProv = getPageProvider();
  if (currentProv === "web" || document.getElementById("relayai-floating-pill")) return;

  const isMac = isMacPlatform();
  const summaryKeyLabel = isMac ? "⌥⇧U" : "Alt+Shift+U";

  // Create HUD Pill Container
  const pill = document.createElement("div");
  pill.id = "relayai-floating-pill";
  pill.setAttribute("role", "button");
  pill.setAttribute("aria-label", "RelayAI 1-Click Context Transfer");

  // Modern Matte Carbon Style
  Object.assign(pill.style, {
    position: "fixed",
    bottom: "24px",
    right: "24px",
    zIndex: "2147483647",
    background: "#18191e",
    border: "1px solid #2b2c34",
    borderRadius: "8px",
    color: "#f4f4f5",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    fontSize: "12px",
    fontWeight: "500",
    display: "inline-flex",
    alignItems: "center",
    gap: "8px",
    padding: "7px 12px",
    boxShadow: "0 6px 20px rgba(0, 0, 0, 0.45)",
    cursor: "pointer",
    transition: "all 0.2s cubic-bezier(0.16, 1, 0.3, 1)",
    userSelect: "none",
    backdropFilter: "blur(12px)",
    opacity: "0",
    transform: "translateY(8px)"
  });

  pill.innerHTML = `
    <span style="color: #10b981; font-size: 13px; line-height: 1;">⚡</span>
    <span id="relayai-pill-label" style="letter-spacing: -0.01em;">Checking tabs...</span>
    <kbd id="relayai-pill-kbd" style="background: #22232a; border: 1px solid #33343e; border-radius: 4px; padding: 2px 6px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 10px; color: #a1a1aa; font-weight: 600;">${summaryKeyLabel}</kbd>
    <span id="relayai-pill-close" title="Minimize" style="color: #71717a; margin-left: 2px; font-size: 13px; padding: 0 2px; border-radius: 3px; line-height: 1; cursor: pointer;">✕</span>
  `;

  document.body.appendChild(pill);

  // Fade in
  requestAnimationFrame(() => {
    pill.style.opacity = "1";
    pill.style.transform = "translateY(0)";
  });

  let currentTargetTab = null;
  let isMinimizing = false;

  // Hover animations
  pill.addEventListener("mouseenter", () => {
    if (!pill.classList.contains("disabled")) {
      pill.style.background = "#1f2026";
      pill.style.borderColor = "#3b3c45";
      pill.style.transform = "translateY(-1px)";
      pill.style.boxShadow = "0 8px 28px rgba(0, 0, 0, 0.6)";
    }
  });

  pill.addEventListener("mouseleave", () => {
    pill.style.background = "#18191e";
    pill.style.borderColor = "#2b2c34";
    pill.style.transform = "translateY(0)";
    pill.style.boxShadow = "0 6px 20px rgba(0, 0, 0, 0.45)";
  });

  // Close / Minimize listener
  const closeBtn = pill.querySelector("#relayai-pill-close");
  closeBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    isMinimizing = true;
    pill.style.transition = "all 0.25s ease";
    pill.style.opacity = "0";
    pill.style.transform = "translateY(12px) scale(0.95)";
    setTimeout(() => {
      pill.style.display = "none";
    }, 250);
  });

  // State update logic
  async function updatePillState() {
    if (isMinimizing || !document.body.contains(pill)) return;

    try {
      chrome.runtime.sendMessage({ action: "get_open_ai_tabs" }, (response) => {
        if (chrome.runtime.lastError || !response || response.status !== "success") return;

        const allTabs = response.tabs || [];
        const otherTabs = allTabs.filter(t => t.provider !== currentProv);
        const labelEl = document.getElementById("relayai-pill-label");
        const kbdEl = document.getElementById("relayai-pill-kbd");

        if (!labelEl || !kbdEl) return;

        if (otherTabs.length === 1) {
          // EXACTLY ONE OTHER AI TAB
          currentTargetTab = otherTabs[0];
          pill.classList.remove("disabled");
          pill.style.opacity = "1";
          pill.style.pointerEvents = "auto";
          labelEl.textContent = `Relay to ${currentTargetTab.label}`;
          kbdEl.textContent = summaryKeyLabel;
          kbdEl.style.display = "inline-block";
        } else if (otherTabs.length > 1) {
          // MULTIPLE OTHER TABS (Ambiguous target)
          currentTargetTab = null;
          pill.classList.remove("disabled");
          pill.style.opacity = "1";
          pill.style.pointerEvents = "auto";
          labelEl.textContent = `Relay (${otherTabs.length} Tabs Open)`;
          kbdEl.textContent = isMac ? "⌥⇧R" : "Alt+Shift+R";
          kbdEl.style.display = "inline-block";
        } else {
          // ZERO OTHER AI TABS
          currentTargetTab = null;
          pill.classList.add("disabled");
          pill.style.opacity = "0.65";
          labelEl.textContent = "Relay (Open 2nd AI Tab)";
          kbdEl.style.display = "none";
        }
      });
    } catch (err) {
      // Ignore background transient errors
    }
  }

  // Click Action
  pill.addEventListener("click", async () => {
    const labelEl = document.getElementById("relayai-pill-label");
    if (!labelEl) return;

    if (!currentTargetTab) {
      labelEl.textContent = "Open 2nd AI tab (e.g. Claude) to relay";
      setTimeout(updatePillState, 2000);
      return;
    }

    const originalText = labelEl.textContent;
    labelEl.textContent = `Distilling ➔ ${currentTargetTab.label}...`;
    pill.style.borderColor = "#10b981";

    try {
      chrome.runtime.sendMessage({
        action: "auto_transfer_chat",
        target_tab_id: currentTargetTab.id,
        source_provider: currentProv,
        target_provider: currentTargetTab.provider,
        mode: "summary"
      }, (res) => {
        if (res && res.status === "success") {
          labelEl.textContent = `✓ Teleported to ${currentTargetTab.label}!`;
          setTimeout(updatePillState, 2500);
        } else {
          labelEl.textContent = res ? res.message : "Transfer error";
          setTimeout(updatePillState, 2500);
        }
      });
    } catch (err) {
      labelEl.textContent = "Transfer error";
      setTimeout(updatePillState, 2000);
    }
  });

  // Initial check & periodic sync
  updatePillState();
  window.addEventListener("focus", updatePillState);
  setInterval(updatePillState, 4000);
}

// Initialize pill when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initFloatingRelayPill);
} else {
  initFloatingRelayPill();
}

