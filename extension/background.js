/**
 * UMS Browser Companion - Background Service Worker
 * Manages Cross-Tab AI Detection and 1-Click Automated Chat & Memory Transfer.
 */

const UMS_HOST = "http://127.0.0.1:8000";

// Listen for messages from popup or web dashboard content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "get_open_ai_tabs") {
    detectOpenAITabs().then(result => sendResponse(result));
    return true;
  }

  if (request.action === "auto_transfer_chat") {
    const payload = { ...request };
    if (!payload.source_tab_id && sender.tab && sender.tab.id) {
      payload.source_tab_id = sender.tab.id;
    }
    executeCrossTabTransfer(payload).then(result => sendResponse(result));
    return true;
  }

  if (request.action === "auto_transfer_memory") {
    executeMemoryTransfer(request).then(result => sendResponse(result));
    return true;
  }
});

const TARGET_URLS = {
  chatgpt: "https://chatgpt.com/",
  claude: "https://claude.ai/new",
  gemini: "https://gemini.google.com/app",
  perplexity: "https://www.perplexity.ai/",
  deepseek: "https://chat.deepseek.com/",
  mistral: "https://chat.mistral.ai/",
  copilot: "https://copilot.microsoft.com/"
};

const PROVIDER_META = {
  chatgpt: { label: "ChatGPT", color: "#10b981", icon: "🟢" },
  claude: { label: "Claude", color: "#f59e0b", icon: "🟠" },
  gemini: { label: "Gemini", color: "#3b82f6", icon: "🔵" },
  perplexity: { label: "Perplexity", color: "#06b6d4", icon: "🌐" },
  deepseek: { label: "DeepSeek", color: "#8b5cf6", icon: "🐋" },
  mistral: { label: "Mistral", color: "#ec4899", icon: "🌸" },
  copilot: { label: "Copilot", color: "#0284c7", icon: "🟦" }
};

const AI_URL_PATTERNS = [
  "https://chatgpt.com/*",
  "https://*.chatgpt.com/*",
  "https://*.openai.com/*",
  "https://claude.ai/*",
  "https://*.claude.ai/*",
  "https://gemini.google.com/*",
  "https://*.perplexity.ai/*",
  "https://perplexity.ai/*",
  "https://*.deepseek.com/*",
  "https://deepseek.com/*",
  "https://*.mistral.ai/*",
  "https://chat.mistral.ai/*",
  "https://copilot.microsoft.com/*",
  "https://*.copilot.microsoft.com/*"
];

// Detect open tabs for all major LLMs (scoped strictly to allowed AI domains)
async function detectOpenAITabs() {
  try {
    const tabs = await chrome.tabs.query({ url: AI_URL_PATTERNS });
    const chatgptTabs = [];
    const claudeTabs = [];
    const geminiTabs = [];
    const perplexityTabs = [];
    const deepseekTabs = [];
    const mistralTabs = [];
    const copilotTabs = [];
    const allAITabs = [];

    tabs.forEach(t => {
      const rawUrl = t.url || t.pendingUrl || "";
      if (!rawUrl) return;
      const url = rawUrl.toLowerCase();
      let prov = null;

      if (url.includes("chatgpt.com") || url.includes("openai.com")) {
        prov = "chatgpt";
      } else if (url.includes("claude.ai")) {
        prov = "claude";
      } else if (url.includes("gemini.google.com") || (url.includes("google.com") && (url.includes("/gemini") || url.includes("bard.google.com")))) {
        prov = "gemini";
      } else if (url.includes("perplexity.ai")) {
        prov = "perplexity";
      } else if (url.includes("deepseek.com")) {
        prov = "deepseek";
      } else if (url.includes("mistral.ai")) {
        prov = "mistral";
      } else if (url.includes("copilot.microsoft.com") || url.includes("bing.com/chat")) {
        prov = "copilot";
      }

      if (prov) {
        const meta = PROVIDER_META[prov] || { label: prov.toUpperCase(), color: "#10b981", icon: "●" };
        const displayTitle = t.title ? t.title.replace(/\s*[-–|].*(ChatGPT|Claude|Gemini|Perplexity|DeepSeek|Mistral|Copilot).*/i, "").trim() || t.title : `${meta.label} Chat`;
        const tabItem = {
          id: t.id,
          title: displayTitle,
          fullTitle: t.title || `${meta.label} Chat`,
          url: rawUrl,
          active: t.active,
          provider: prov,
          label: meta.label,
          color: meta.color,
          icon: meta.icon
        };

        if (prov === "chatgpt") chatgptTabs.push(tabItem);
        else if (prov === "claude") claudeTabs.push(tabItem);
        else if (prov === "gemini") geminiTabs.push(tabItem);
        else if (prov === "perplexity") perplexityTabs.push(tabItem);
        else if (prov === "deepseek") deepseekTabs.push(tabItem);
        else if (prov === "mistral") mistralTabs.push(tabItem);
        else if (prov === "copilot") copilotTabs.push(tabItem);

        allAITabs.push(tabItem);
      }
    });

    return {
      status: "success",
      tabs: allAITabs,
      chatgpt_tabs: chatgptTabs,
      claude_tabs: claudeTabs,
      gemini_tabs: geminiTabs,
      perplexity_tabs: perplexityTabs,
      deepseek_tabs: deepseekTabs,
      mistral_tabs: mistralTabs,
      copilot_tabs: copilotTabs,
      has_chatgpt: chatgptTabs.length > 0,
      has_claude: claudeTabs.length > 0,
      has_gemini: geminiTabs.length > 0,
      has_perplexity: perplexityTabs.length > 0,
      has_deepseek: deepseekTabs.length > 0,
      has_mistral: mistralTabs.length > 0,
      total_ai_tabs: allAITabs.length
    };
  } catch (err) {
    return { status: "error", message: err.message };
  }
}

// Helper: dynamically ensures content script is injected into any open AI tab
async function ensureContentScriptInjected(tabId) {
  try {
    const res = await chrome.tabs.sendMessage(tabId, { action: "ping" });
    if (res && res.status === "active") return true;
  } catch (e) {
    // Content script not yet listening in this tab
  }

  try {
    await chrome.scripting.executeScript({
      target: { tabId: tabId },
      files: ["content.js"]
    });
    await new Promise(resolve => setTimeout(resolve, 250));
    return true;
  } catch (err) {
    console.error(`Script injection error on tab ${tabId}:`, err);
    throw new Error(`Please refresh your AI tab once to allow connection (${err.message}).`);
  }
}

// 1-Click Automated Cross-Tab Transfer (Supports mode: "full" | "summary")
async function executeCrossTabTransfer({ source_tab_id, target_tab_id, source_provider, target_provider, mode = "full" }) {
  try {
    const numSourceId = (source_tab_id && !isNaN(Number(source_tab_id))) ? Number(source_tab_id) : null;
    if (!numSourceId) {
      throw new Error("Please select an active source AI chat tab.");
    }

    // 1. Ensure content script is active in source tab
    await ensureContentScriptInjected(numSourceId);

    // 2. Scrape source tab
    const scrapeResponse = await chrome.tabs.sendMessage(numSourceId, { action: "scrape_chat_thread" });
    if (!scrapeResponse || scrapeResponse.status !== "success" || !scrapeResponse.raw_chat) {
      throw new Error(scrapeResponse ? scrapeResponse.message : "Could not scrape active conversation from source tab.");
    }

    const actualSourceProv = source_provider || scrapeResponse.provider || "chatgpt";
    const actualTargetProv = target_provider || "claude";

    let primer = "";
    let distillData = {
      primary_goal: "Transferred Chat Session",
      immediate_next_task: "Continue the active discussion",
      token_savings_percent: mode === "summary" ? 82.0 : 0
    };

    // 3. Call local UMS server for compilation / distillation (with offline fallback)
    try {
      const distillRes = await fetch(`${UMS_HOST}/api/handoff/distill`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw_chat: scrapeResponse.raw_chat,
          source: actualSourceProv,
          target: actualTargetProv,
          mode: mode || "full"
        })
      });
      const data = await distillRes.json();
      if (data && data.handoff_primer) {
        distillData = data;
        primer = data.handoff_primer;
      } else {
        throw new Error(data.error || "Invalid response");
      }
    } catch (err) {
      console.warn("UMS Server offline, using local extension handoff compiler:", err.message);
      // Offline in-extension handoff compiler
      const srcLabel = (PROVIDER_META[actualSourceProv]?.label || actualSourceProv);
      const tgtLabel = (PROVIDER_META[actualTargetProv]?.label || actualTargetProv);
      
      if (mode === "summary") {
        const rawLines = scrapeResponse.raw_chat.split("\n");
        const userLines = [];
        const keyBullets = [];
        let inCode = false;
        let lastUserMsg = "";

        rawLines.forEach(l => {
          const trimmed = l.trim();
          if (trimmed.startsWith("```")) {
            inCode = !inCode;
            return;
          }
          if (inCode) return;
          if (/^(User|Human):\s*/i.test(trimmed)) {
            const clean = trimmed.replace(/^(User|Human):\s*/i, "").trim();
            if (clean.length > 10) {
              userLines.push(clean);
              lastUserMsg = clean;
            }
          } else if ((trimmed.startsWith("-") || trimmed.startsWith("*") || trimmed.startsWith("•") || /^\d+\./.test(trimmed)) && trimmed.length > 15) {
            keyBullets.push(trimmed);
          }
        });

        const goal = userLines.length > 0 ? userLines[0].slice(0, 200) : "Active Cross-Model Collaboration";
        const uniqueBullets = Array.from(new Set(keyBullets)).slice(0, 20);

        const summaryParts = [
          `### 🔄 ACTIVE CHAT HANDOFF (${srcLabel} ➔ ${tgtLabel})`,
          `ROLE INSTRUCTION: You are seamlessly taking over an active session transferred from ${srcLabel}.`,
          ``,
          `### 📋 SESSION OVERVIEW & OBJECTIVE`,
          `- **Primary Goal**: ${goal}`,
        ];

        if (userLines.length > 1) {
          summaryParts.push(``, `### 📌 USER REQUIREMENTS & INQUIRIES`);
          userLines.slice(1, 8).forEach(u => summaryParts.push(`• ${u}`));
        }

        if (uniqueBullets.length > 0) {
          summaryParts.push(``, `### 💡 SYNTHESIZED KNOWLEDGE & ESTABLISHED POINTS`);
          summaryParts.push(uniqueBullets.join("\n"));
        } else {
          summaryParts.push(``, `### 💬 CONVERSATION WORKING CONTEXT`);
          summaryParts.push(scrapeResponse.raw_chat.slice(0, 3000));
        }

        summaryParts.push(
          ``,
          `### 🎯 IMMEDIATE NEXT TASK TO SOLVE`,
          lastUserMsg || `Context recovered if done.`,
          ``,
          `---`,
          `Simply reply with "Context recovered" if done.`
        );

        primer = summaryParts.join("\n");
        distillData.token_savings_percent = 78.5;
      } else {
        primer = [
          `### 🔄 ACTIVE CHAT THREAD HANDOFF (${srcLabel} ➔ ${tgtLabel})`,
          `ROLE INSTRUCTION: You are taking over an ongoing session transferred directly from ${srcLabel}.`,
          ``,
          `### 💬 CONVERSATION TRANSCRIPT & SHARED CONTEXT`,
          scrapeResponse.raw_chat,
          ``,
          `---`,
          `Simply reply with "Context recovered" if done.`
        ].join("\n");
        distillData.token_savings_percent = 0;
      }
    }

    // 4. Inject into target tab
    const numTargetId = (target_tab_id && !isNaN(Number(target_tab_id))) ? Number(target_tab_id) : null;
    if (numTargetId) {
      await ensureContentScriptInjected(numTargetId);
      await chrome.tabs.sendMessage(numTargetId, {
        action: "inject_handoff",
        text: primer
      });
      // Focus target tab
      await chrome.tabs.update(numTargetId, { active: true });
    } else {
      // If target tab not already open, open it
      const targetUrl = TARGET_URLS[actualTargetProv] || "https://claude.ai/new";
      const newTab = await chrome.tabs.create({ url: targetUrl, active: true });
      
      // Inject after short wait for page load
      setTimeout(async () => {
        try {
          await chrome.tabs.sendMessage(newTab.id, {
            action: "inject_handoff",
            text: primer
          });
        } catch (e) {
          console.log("Tab injection fallback", e);
        }
      }, 2500);
    }

    return {
      status: "success",
      mode: mode,
      message: `Transferred successfully to ${(target_provider || "target").toUpperCase()} (${mode === "summary" ? "Condensed Summary" : "Full Chat As-Is"})!`,
      primary_goal: distillData.primary_goal,
      token_savings_percent: distillData.token_savings_percent,
      immediate_next_task: distillData.immediate_next_task,
      handoff_primer: primer
    };
  } catch (err) {
    return { status: "error", message: err.message };
  }
}

// 1-Click Automated Memory Transfer
async function executeMemoryTransfer({ payload, target_tab_id, target_provider }) {
  try {
    const hydRes = await fetch(`${UMS_HOST}/api/hydrate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        payload: payload,
        target: target_provider,
        options: { filter_non_work: true }
      })
    });
    const hydData = await hydRes.json();
    const importText = target_provider === "claude" ? hydData.import_text : hydData.custom_instructions_box_1;

    if (target_tab_id) {
      await ensureContentScriptInjected(target_tab_id);
      await chrome.tabs.sendMessage(target_tab_id, {
        action: "inject_memory",
        provider: target_provider,
        text: importText
      });
      await chrome.tabs.update(target_tab_id, { active: true });
    }

    return { status: "success", message: `Memory ingested into ${target_provider.toUpperCase()}!` };
  } catch (err) {
    return { status: "error", message: err.message };
  }
}

// Universal Keyboard Shortcut Handler (Alt+Shift+U / Option+Shift+U for Summary, Alt+Shift+Y for Full)
// STRICT REQUIREMENT: Only executes if the user is on an active AI tab AND there is EXACTLY ONE other AI tab open.
if (chrome.commands && chrome.commands.onCommand) {
  chrome.commands.onCommand.addListener(async (command) => {
    if (command === "quick-transfer-summary" || command === "quick-transfer-full") {
      try {
        const radar = await detectOpenAITabs();
        if (!radar || !radar.tabs || radar.tabs.length === 0) return;

        const [currentTab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (!currentTab) return;

        // 1. Verify the user is currently on an active AI tab
        const sourceTab = radar.tabs.find(t => t.id === currentTab.id);
        if (!sourceTab) {
          console.warn("Relay shortcut ignored: Focused tab is not an active AI chat.");
          return;
        }

        // 2. Identify all other open AI tabs
        const otherAITabs = radar.tabs.filter(t => t.id !== sourceTab.id);

        // 3. STRICT RULE: Must have EXACTLY ONE other AI tab open.
        // If 0: No target exists.
        // If >= 2: Target is ambiguous (multiple AI tabs open, user must pick in popup).
        if (otherAITabs.length !== 1) {
          console.warn(`Relay shortcut ignored: Expected exactly 1 other AI tab, found ${otherAITabs.length}.`);
          return;
        }

        // 4. Exactly one other AI tab exists -> execute transfer!
        const targetTab = otherAITabs[0];
        const mode = (command === "quick-transfer-full") ? "full" : "summary";

        await executeCrossTabTransfer({
          source_tab_id: sourceTab.id,
          target_tab_id: targetTab.id,
          source_provider: sourceTab.provider,
          target_provider: targetTab.provider,
          mode: mode
        });
      } catch (err) {
        console.error("Keyboard shortcut transfer error:", err);
      }
    }
  });
}


