/**
 * UMS Browser Companion - Popup Controller
 * Features Live Cross-Tab AI Radar and 1-Click Automated Chat & Memory Transfer.
 */

const UMS_HOST = "http://127.0.0.1:8000";

let detectedTabs = null;
let currentPersonaPayload = null;
let currentProvider = "unknown";
let targetProvider = "claude";
let activeTabId = null;
let lastDistilledData = null;

document.addEventListener("DOMContentLoaded", async () => {
  setupTabs();
  await checkServerHealth();
  await scanOpenAITabs();
  await loadActivePersona();
  setupEventListeners();
});

// Switch between Handoff and Memory tabs in Popup
function setupTabs() {
  const tabs = document.querySelectorAll(".mode-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const mode = tab.getAttribute("data-mode");
      document.getElementById("view-memory").classList.toggle("d-none", mode !== "memory");
      document.getElementById("view-handoff").classList.toggle("d-none", mode !== "handoff");
    });
  });
}

// Check local UMS server health
async function checkServerHealth() {
  const pill = document.getElementById("server-status-pill");
  const text = document.getElementById("server-status-text");

  try {
    const res = await fetch(`${UMS_HOST}/api/health`, { signal: AbortSignal.timeout(1500) });
    const data = await res.json();
    if (data.status === "healthy") {
      pill.className = "status-pill online";
      text.textContent = "Server Online";
      return true;
    }
  } catch (err) {
    pill.className = "status-pill offline";
    text.textContent = "Server Offline";
  }
  return false;
}

// Scan all open tabs to find ChatGPT, Claude, Gemini, Perplexity, DeepSeek, Mistral, Copilot
async function scanOpenAITabs() {
  const radarList = document.getElementById("radar-tabs-list");
  const badge = document.getElementById("radar-count-badge");
  const controlsBox = document.getElementById("radar-controls-box");
  const btnFull = document.getElementById("btn-auto-transfer-full");
  const btnSummary = document.getElementById("btn-auto-transfer-summary");

  const colors = {
    chatgpt: "#10b981",
    claude: "#f59e0b",
    gemini: "#3b82f6",
    perplexity: "#06b6d4",
    deepseek: "#8b5cf6",
    mistral: "#ec4899",
    copilot: "#0284c7"
  };

  const labels = {
    chatgpt: "ChatGPT",
    claude: "Claude",
    gemini: "Gemini",
    perplexity: "Perplexity",
    deepseek: "DeepSeek",
    mistral: "Mistral",
    copilot: "Copilot"
  };

  const icons = {
    chatgpt: "🟢",
    claude: "🟠",
    gemini: "🔵",
    perplexity: "🌐",
    deepseek: "🐋",
    mistral: "🌸",
    copilot: "🟦"
  };

  try {
    // 1. Direct tab query from popup (immediate, resilient)
    let rawTabs = [];
    if (chrome.tabs && chrome.tabs.query) {
      rawTabs = await chrome.tabs.query({});
    }

    const aiTabs = [];
    rawTabs.forEach(t => {
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
        const provLabel = labels[prov] || prov.toUpperCase();
        const displayTitle = t.title ? t.title.replace(/\s*[-–|].*(ChatGPT|Claude|Gemini|Perplexity|DeepSeek|Mistral|Copilot).*/i, "").trim() || t.title : `${provLabel} Chat`;
        aiTabs.push({
          id: t.id,
          title: displayTitle,
          fullTitle: t.title || displayTitle,
          url: rawUrl,
          active: t.active,
          provider: prov,
          label: provLabel,
          color: colors[prov] || "#10b981",
          icon: icons[prov] || "●"
        });
      }
    });

    detectedTabs = {
      status: "success",
      tabs: aiTabs,
      total_ai_tabs: aiTabs.length
    };

    renderRadarTabsUI(detectedTabs);
  } catch (err) {
    console.error("Tab scan failed", err);
    // Fallback: ping background worker
    chrome.runtime.sendMessage({ action: "get_open_ai_tabs" }, (response) => {
      if (response && response.status === "success") {
        detectedTabs = response;
        renderRadarTabsUI(response);
      }
    });
  }
}

function renderRadarTabsUI(tabsData) {
  const radarList = document.getElementById("radar-tabs-list");
  const badge = document.getElementById("radar-count-badge");
  const controlsBox = document.getElementById("radar-controls-box");
  const allTabs = (tabsData && tabsData.tabs) ? tabsData.tabs : [];
  const total = allTabs.length;

  if (total === 0) {
    badge.textContent = "0 Tabs";
    radarList.innerHTML = `<div class="radar-tab-row"><span class="radar-tab-role" style="color: #94a3b8;">No AI tabs found. Open ChatGPT, Claude, Gemini, etc.</span></div>`;
    if (controlsBox) controlsBox.classList.add("d-none");
    return;
  }

  badge.textContent = `${total} Tab${total !== 1 ? 's' : ''} Detected`;

  let html = "";
  allTabs.forEach(tab => {
    html += `
      <div class="radar-tab-row">
        <span class="radar-tab-role" style="color: ${tab.color};">${tab.icon} ${tab.label}${tab.active ? ' (Active)' : ''}:</span>
        <span class="radar-tab-title" title="${escapeHtml(tab.fullTitle)}">${escapeHtml(tab.title)}</span>
      </div>
    `;
  });
  radarList.innerHTML = html;

  if (controlsBox) {
    controlsBox.classList.remove("d-none");
    populateSourceDropdown(allTabs);
  }
}

function populateSourceDropdown(allTabs) {
  const srcSelect = document.getElementById("radar-source-select");
  if (!srcSelect) return;

  srcSelect.innerHTML = "";
  let activeIndex = 0;

  allTabs.forEach((tab, idx) => {
    const opt = document.createElement("option");
    opt.value = tab.id;
    opt.dataset.provider = tab.provider;
    opt.dataset.label = tab.label;
    opt.textContent = `${tab.icon} [${tab.label}] ${tab.title}`;
    if (tab.active) activeIndex = idx;
    srcSelect.appendChild(opt);
  });

  if (allTabs.length > 0) {
    srcSelect.selectedIndex = activeIndex;
  }

  populateTargetDropdown(allTabs);
}

function populateTargetDropdown(allTabs) {
  const srcSelect = document.getElementById("radar-source-select");
  const tgtSelect = document.getElementById("radar-target-select");
  if (!srcSelect || !tgtSelect) return;

  const selectedSourceId = Number(srcSelect.value);
  const selectedSourceProv = srcSelect.selectedOptions[0]?.dataset?.provider || "chatgpt";

  tgtSelect.innerHTML = "";

  // 1. Add other open tabs (exclude current source tab)
  const otherTabs = allTabs.filter(t => t.id !== selectedSourceId);
  if (otherTabs.length > 0) {
    const groupOther = document.createElement("optgroup");
    groupOther.label = "── Open Browser Tabs ──";
    otherTabs.forEach(t => {
      const opt = document.createElement("option");
      opt.value = t.id;
      opt.dataset.provider = t.provider;
      opt.dataset.label = t.label;
      opt.textContent = `${t.icon} [${t.label}] ${t.title}`;
      groupOther.appendChild(opt);
    });
    tgtSelect.appendChild(groupOther);
  }

  // 2. Add New Tab launch options for all providers
  const groupNew = document.createElement("optgroup");
  groupNew.label = "── Open in New Tab ──";
  const newOptions = [
    { prov: "claude", label: "Claude", icon: "🟠" },
    { prov: "chatgpt", label: "ChatGPT", icon: "🟢" },
    { prov: "gemini", label: "Gemini", icon: "🔵" },
    { prov: "perplexity", label: "Perplexity", icon: "🌐" },
    { prov: "deepseek", label: "DeepSeek", icon: "🐋" },
    { prov: "mistral", label: "Mistral", icon: "🌸" }
  ];

  newOptions.forEach(item => {
    const opt = document.createElement("option");
    opt.value = `new_${item.prov}`;
    opt.dataset.provider = item.prov;
    opt.dataset.label = item.label;
    opt.textContent = `${item.icon} ➕ Open New Tab: ${item.label}`;
    groupNew.appendChild(opt);
  });
  tgtSelect.appendChild(groupNew);

  // Default selection: pick first open tab if available, else new tab different from source
  if (otherTabs.length > 0) {
    tgtSelect.selectedIndex = 0;
  } else {
    // If only 1 tab open, default to opening Claude (if source is not claude) or ChatGPT
    const defaultNewProv = selectedSourceProv === "claude" ? "chatgpt" : "claude";
    const foundIndex = Array.from(tgtSelect.options).findIndex(o => o.value === `new_${defaultNewProv}`);
    if (foundIndex >= 0) tgtSelect.selectedIndex = foundIndex;
  }

  updateButtonLabels();
}

function updateButtonLabels() {
  const srcSelect = document.getElementById("radar-source-select");
  const tgtSelect = document.getElementById("radar-target-select");
  const btnFull = document.getElementById("btn-auto-transfer-full");
  const btnSummary = document.getElementById("btn-auto-transfer-summary");

  if (!srcSelect || !tgtSelect || !btnFull || !btnSummary) return;

  const srcLabel = srcSelect.selectedOptions[0]?.dataset?.label || "Source";
  const tgtLabel = tgtSelect.selectedOptions[0]?.dataset?.label || "Target";

  btnFull.innerHTML = `⚡ 1-Click Transfer Full Chat (${srcLabel} ➔ ${tgtLabel})`;
  btnSummary.innerHTML = `🧠 1-Click Transfer Condensed Summary (${srcLabel} ➔ ${tgtLabel})`;
}

// Fetch active persona from local UMS vault or demo
async function loadActivePersona() {
  const titleEl = document.getElementById("persona-name");
  const techEl = document.getElementById("persona-tech");

  try {
    const res = await fetch(`${UMS_HOST}/api/demo-data`);
    const data = await res.json();

    const parseRes = await fetch(`${UMS_HOST}/api/parse`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: "chatgpt", text: data.demo_chatgpt_raw })
    });
    const parsed = await parseRes.json();
    currentPersonaPayload = parsed.payload;

    titleEl.textContent = `${currentPersonaPayload.tier1_identity.profile.role} (${currentPersonaPayload.tier1_identity.profile.name || "Default"})`;
    const tech = [...currentPersonaPayload.tier1_identity.tech_stack.primary_languages, ...currentPersonaPayload.tier1_identity.tech_stack.frameworks];
    techEl.textContent = tech.join(", ") || "Active engineering memory";
  } catch (err) {
    titleEl.textContent = "Lead Full-Stack Architect";
    techEl.textContent = "TypeScript, Next.js, Python (Default)";
  }
}

// Setup Event Listeners
function setupEventListeners() {
  const btnRescan = document.getElementById("btn-rescan-tabs");
  const srcSelect = document.getElementById("radar-source-select");
  const tgtSelect = document.getElementById("radar-target-select");
  const btnFull = document.getElementById("btn-auto-transfer-full");
  const btnSummary = document.getElementById("btn-auto-transfer-summary");
  const btnDistill = document.getElementById("btn-distill-active-chat");
  const btnOpenInject = document.getElementById("btn-open-and-inject");
  const btnCopyHandoff = document.getElementById("btn-copy-handoff-primer");
  const btnInject = document.getElementById("btn-auto-inject");
  const btnVerify = document.getElementById("btn-verify-chat");
  const feedback = document.getElementById("status-feedback");

  // Rescan button
  if (btnRescan) {
    btnRescan.addEventListener("click", async () => {
      btnRescan.style.transform = "rotate(360deg)";
      btnRescan.style.transition = "transform 0.5s ease";
      setTimeout(() => { btnRescan.style.transform = "none"; }, 500);
      await scanOpenAITabs();
    });
  }

  // Source tab changed -> update target options and button labels
  if (srcSelect) {
    srcSelect.addEventListener("change", () => {
      if (detectedTabs && detectedTabs.tabs) {
        populateTargetDropdown(detectedTabs.tabs);
      } else {
        updateButtonLabels();
      }
    });
  }

  // Target tab changed -> update button labels
  if (tgtSelect) {
    tgtSelect.addEventListener("change", updateButtonLabels);
  }

  // Multi-Mode Auto-Transfer from Radar
  async function executeRadarTransfer(mode) {
    if (!srcSelect || !tgtSelect || !srcSelect.value) return;

    if (btnFull) btnFull.disabled = true;
    if (btnSummary) btnSummary.disabled = true;
    feedback.classList.add("d-none");

    const srcOption = srcSelect.selectedOptions[0];
    const tgtOption = tgtSelect.selectedOptions[0];

    const sourceTabId = Number(srcSelect.value);
    const sourceProv = srcOption?.dataset?.provider || "chatgpt";

    const targetVal = tgtSelect.value;
    const isTargetNew = targetVal.startsWith("new_");
    const targetTabId = isTargetNew ? null : Number(targetVal);
    const targetProv = tgtOption?.dataset?.provider || "claude";

    chrome.runtime.sendMessage({
      action: "auto_transfer_chat",
      source_tab_id: sourceTabId,
      target_tab_id: targetTabId,
      source_provider: sourceProv,
      target_provider: targetProv,
      mode: mode
    }, (response) => {
      if (btnFull) btnFull.disabled = false;
      if (btnSummary) btnSummary.disabled = false;

      if (response && response.status === "success") {
        feedback.className = "status-feedback success";
        feedback.textContent = `✓ ${response.message} (${response.token_savings_percent || 0}% token reduction).`;
        feedback.classList.remove("d-none");

        // Populate summary card
        if (response.primary_goal) {
          document.getElementById("distill-goal").textContent = response.primary_goal;
          document.getElementById("distill-next").textContent = response.immediate_next_task || "Continue in target chat";
          document.getElementById("metric-savings").textContent = `Savings: ${response.token_savings_percent}%`;
          document.getElementById("distilled-summary-card").classList.remove("d-none");
        }
      } else {
        feedback.className = "status-feedback error";
        feedback.textContent = `✕ ${response ? response.message : "Auto-transfer failed."}`;
        feedback.classList.remove("d-none");
      }
    });
  }

  if (btnFull) {
    btnFull.addEventListener("click", () => executeRadarTransfer("full"));
  }
  if (btnSummary) {
    btnSummary.addEventListener("click", () => executeRadarTransfer("summary"));
  }

  // Distill Active Chat in Current Tab
  btnDistill.addEventListener("click", async () => {
    const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!activeTab) return;

    btnDistill.disabled = true;
    btnDistill.textContent = "Scraping & Distilling Thread...";
    feedback.classList.add("d-none");

    const isClaude = activeTab.url && activeTab.url.includes("claude.ai");
    const isChatGPT = activeTab.url && activeTab.url.includes("chatgpt.com");
    const src = isClaude ? "claude" : (isChatGPT ? "chatgpt" : "chatgpt");
    const tgt = isClaude ? "chatgpt" : "claude";

    chrome.tabs.sendMessage(activeTab.id, { action: "scrape_chat_thread" }, async (response) => {
      if (!response || response.status !== "success") {
        btnDistill.disabled = false;
        btnDistill.textContent = "Distill & Transfer Current Tab";
        feedback.className = "status-feedback error";
        feedback.textContent = `✕ ${response ? response.message : "Could not find active chat on this page."}`;
        feedback.classList.remove("d-none");
        return;
      }

      try {
        const distillRes = await fetch(`${UMS_HOST}/api/handoff/distill`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            raw_chat: response.raw_chat,
            source: src,
            target: tgt
          })
        });

        const data = await distillRes.json();
        lastDistilledData = data;

        document.getElementById("distill-goal").textContent = data.primary_goal;
        document.getElementById("distill-next").textContent = data.immediate_next_task;
        document.getElementById("metric-savings").textContent = `Savings: ${data.token_savings_percent}%`;
        document.getElementById("metric-tokens").textContent = `~${data.token_estimate} tokens`;
        document.getElementById("distilled-summary-card").classList.remove("d-none");

        btnDistill.disabled = false;
        btnDistill.textContent = "Re-Distill Current Tab";

        feedback.className = "status-feedback success";
        feedback.textContent = `✓ Distilled! ${data.token_savings_percent}% token reduction with 0 extra tokens burned.`;
        feedback.classList.remove("d-none");
      } catch (err) {
        btnDistill.disabled = false;
        feedback.className = "status-feedback error";
        feedback.textContent = `✕ Server error: ${err.message}`;
        feedback.classList.remove("d-none");
      }
    });
  });

  // Open Target Tab & Inject Context
  btnOpenInject.addEventListener("click", async () => {
    if (!lastDistilledData || !lastDistilledData.handoff_primer) return;
    const primer = lastDistilledData.handoff_primer;
    await navigator.clipboard.writeText(primer);

    const targetUrl = targetProvider === "claude" ? "https://claude.ai/new" : "https://chatgpt.com/";
    chrome.tabs.create({ url: targetUrl });
    feedback.className = "status-feedback success";
    feedback.textContent = "✓ Opened target tab & copied primer to clipboard!";
    feedback.classList.remove("d-none");
  });

  // Copy Handoff Primer
  btnCopyHandoff.addEventListener("click", async () => {
    if (!lastDistilledData || !lastDistilledData.handoff_primer) return;
    await navigator.clipboard.writeText(lastDistilledData.handoff_primer);
    feedback.className = "status-feedback success";
    feedback.textContent = "✓ Primer copied to clipboard!";
    feedback.classList.remove("d-none");
  });

  // Ingest Memory
  btnInject.addEventListener("click", async () => {
    const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!activeTab) return;

    btnInject.disabled = true;
    btnInject.textContent = "Injecting...";

    const isClaude = activeTab.url && activeTab.url.includes("claude.ai");
    const isChatGPT = activeTab.url && activeTab.url.includes("chatgpt.com");
    const prov = isClaude ? "claude" : (isChatGPT ? "chatgpt" : "claude");

    try {
      const hydRes = await fetch(`${UMS_HOST}/api/hydrate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          payload: currentPersonaPayload,
          target: prov,
          options: { filter_non_work: true }
        })
      });
      const hydData = await hydRes.json();
      const importText = prov === "claude" ? hydData.import_text : hydData.custom_instructions_box_1;

      chrome.tabs.sendMessage(activeTab.id, {
        action: "inject_memory",
        provider: prov,
        text: importText
      }, response => {
        btnInject.disabled = false;
        btnInject.textContent = "1-Click Inject Memory into Account";
        if (response && response.status === "success") {
          feedback.className = "status-feedback success";
          feedback.textContent = `✓ ${response.message}`;
        } else {
          feedback.className = "status-feedback error";
          feedback.textContent = `✕ ${response ? response.message : "Failed to inject."}`;
        }
        feedback.classList.remove("d-none");
      });
    } catch (e) {
      btnInject.disabled = false;
      feedback.className = "status-feedback error";
      feedback.textContent = `✕ Error: ${e.message}`;
      feedback.classList.remove("d-none");
    }
  });

  // Send Verification
  btnVerify.addEventListener("click", async () => {
    const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!activeTab) return;

    chrome.tabs.sendMessage(activeTab.id, {
      action: "send_verification",
      query: "I updated my memory. What did you learn about me?"
    }, response => {
      feedback.className = "status-feedback success";
      feedback.textContent = `✓ Verification query sent! Check model's reply.`;
      feedback.classList.remove("d-none");
    });
  });
}

function escapeHtml(str) {
  if (typeof str !== "string") return str;
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
