/**
 * Universal Memory Schema (UMS) - Frontend Application Logic
 * Streamlined 4-Step Focused Migration Studio, Zero-Token Chat Handoff, and Vault.
 */

// State Management
const state = {
  currentTab: "studio",
  currentStep: 1,
  sourceProvider: "chatgpt",
  targetProvider: "claude",
  currentPayload: null,
  cachedPrompts: null,
  demoData: null,
  activeIdeFiles: null,
  handoffData: null
};

// DOM Elements
const elements = {
  tabs: document.querySelectorAll(".nav-tab"),
  tabPanels: document.querySelectorAll(".tab-panel"),
  stepperNodes: document.querySelectorAll(".step-node"),
  providerCards: document.querySelectorAll(".provider-card"),
  targetTabs: document.querySelectorAll(".target-tab"),
  displayExtractionPrompt: document.getElementById("display-extraction-prompt"),
  inputRawMemory: document.getElementById("input-raw-memory"),
  sourceCharCounter: document.getElementById("source-char-counter"),
  btnParseMemory: document.getElementById("btn-parse-memory"),
  btnLoadDemo: document.getElementById("btn-load-demo"),
  btnDemoPaste: document.getElementById("btn-demo-paste"),
  btnCopyExtractionPrompt: document.getElementById("btn-copy-extraction-prompt"),
  btnThemeToggle: document.getElementById("btn-theme-toggle"),
  toast: document.getElementById("toast"),

  // Stepper Navigation Buttons
  btnBackStep1: document.getElementById("btn-back-step-1"),
  btnProceedHydrate: document.getElementById("btn-proceed-hydrate"),
  btnBackStep2: document.getElementById("btn-back-step-2"),
  btnProceedVerify: document.getElementById("btn-proceed-verify"),
  btnBackStep3: document.getElementById("btn-back-step-3"),
  btnRestartMigration: document.getElementById("btn-restart-migration"),
  btnTriggerExtensionInject: document.getElementById("btn-trigger-extension-inject"),

  // Step 2: Pruning & Identity Review
  chkTier1: document.getElementById("chk-tier-1"),
  chkTier2: document.getElementById("chk-tier-2"),
  chkTier3: document.getElementById("chk-tier-3"),
  chkFilterNonWork: document.getElementById("chk-filter-non-work"),
  t1Preview: document.getElementById("t1-preview-items"),
  t2Preview: document.getElementById("t2-preview-items"),
  t3Preview: document.getElementById("t3-preview-items"),

  // Step 3: Target Hydration
  hydratedTokenCount: document.getElementById("hydrated-token-count"),
  tokenSavingsBadge: document.getElementById("token-savings-badge"),
  hydrationInstructions: document.getElementById("hydration-instructions-banner"),
  hydratedOutputDisplay: document.getElementById("hydrated-output-display"),
  btnCopyHydrated: document.getElementById("btn-copy-hydrated"),

  // Step 4: Verification & Diff
  verificationQueryText: document.getElementById("verification-query-text"),
  btnCopyVerifyQuery: document.getElementById("btn-copy-verify-query"),
  inputVerifyResponse: document.getElementById("input-verify-response"),
  btnFillDemoVerification: document.getElementById("btn-fill-demo-verification"),
  btnComputeDiff: document.getElementById("btn-compute-diff"),
  diffDashboard: document.getElementById("diff-dashboard"),
  diffRetentionScore: document.getElementById("diff-retention-score"),
  countLearned: document.getElementById("count-learned"),
  countAdapted: document.getElementById("count-adapted"),
  countFiltered: document.getElementById("count-filtered"),
  diffSuggestions: document.getElementById("diff-suggestions-box"),
  diffEntriesContainer: document.getElementById("diff-entries-container"),

  // Vault & IDE Tooling
  vaultProfilesGrid: document.getElementById("vault-profiles-grid"),
  vaultActiveJson: document.getElementById("vault-active-json"),
  btnSaveCurrentVault: document.getElementById("btn-save-current-vault"),
  btnExportVaultJson: document.getElementById("btn-export-vault-json"),
  ideTabs: document.querySelectorAll(".ide-tab"),
  ideFileTitle: document.getElementById("ide-file-title"),
  ideFileContent: document.getElementById("ide-file-content"),
  btnCopyIdeFile: document.getElementById("btn-copy-ide-file"),
  inputFsPath: document.getElementById("input-fs-path"),
  btnExecuteFsSync: document.getElementById("btn-execute-fs-sync"),
  fsSyncStatusMsg: document.getElementById("fs-sync-status-msg"),

  // Chat Handoff
  handoffSourceSelect: document.getElementById("handoff-source-select"),
  handoffTargetSelect: document.getElementById("handoff-target-select"),
  inputHandoffChat: document.getElementById("input-handoff-chat"),
  btnLoadDemoChat: document.getElementById("btn-load-demo-chat"),
  handoffCharCounter: document.getElementById("handoff-char-counter"),
  btnDistillChat: document.getElementById("btn-distill-chat"),
  handoffResultsPanel: document.getElementById("handoff-results-panel"),
  handoffSavingsBadge: document.getElementById("handoff-savings-badge"),
  handoffTokenCount: document.getElementById("handoff-token-count"),
  handoffExtractedGoal: document.getElementById("handoff-extracted-goal"),
  handoffExtractedTech: document.getElementById("handoff-extracted-tech"),
  handoffExtractedNext: document.getElementById("handoff-extracted-next"),
  handoffPrimerDisplay: document.getElementById("handoff-primer-display"),
  btnCopyHandoffPrimerWeb: document.getElementById("btn-copy-handoff-primer-web"),
  btnLaunchTargetAi: document.getElementById("btn-launch-target-ai"),
  btnDistillFull: document.getElementById("btn-distill-full"),

  // Live Cross-Tab Radar Web Panel
  webRadarPanel: document.getElementById("web-radar-panel"),
  webRadarStatusText: document.getElementById("web-radar-status-text"),
  webRadarCountBadge: document.getElementById("web-radar-count-badge"),
  btnWebRescanTabs: document.getElementById("btn-web-rescan-tabs"),
  webRadarTabsChips: document.getElementById("web-radar-tabs-chips"),
  webRadarSelectorsContainer: document.getElementById("web-radar-selectors-container"),
  webRadarSourceSelect: document.getElementById("web-radar-source-select"),
  webRadarTargetSelect: document.getElementById("web-radar-target-select"),
  btnWebTransferFull: document.getElementById("btn-web-transfer-full"),
  btnWebTransferSummary: document.getElementById("btn-web-transfer-summary")
};

// Initialization
document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  await loadPrompts();
  await loadDemoData();
  await loadProfiles();
  await loadIdeFiles();
  queryOpenAITabs();
  setInterval(() => {
    if (state.currentTab === "handoff") {
      queryOpenAITabs();
    }
  }, 3500);
});

// Event Listeners
function setupEventListeners() {
  // Navigation Tabs (Streamlined: studio, handoff, vault)
  elements.tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const tabId = tab.dataset.tab;
      switchTab(tabId);
    });
  });

  // Stepper Node Clicks (Jump directly to steps if payload exists)
  elements.stepperNodes.forEach(node => {
    node.addEventListener("click", () => {
      const targetStep = parseInt(node.dataset.step);
      if (targetStep === 1 || state.currentPayload) {
        setStep(targetStep);
      } else {
        showToast("Parse source memory in Step 1 first.");
      }
    });
  });

  // Theme Toggle
  elements.btnThemeToggle.addEventListener("click", () => {
    const isDark = document.documentElement.classList.toggle("dark");
    document.documentElement.classList.toggle("light", !isDark);
  });

  // Source Provider Selection
  elements.providerCards.forEach(card => {
    card.addEventListener("click", () => {
      elements.providerCards.forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      state.sourceProvider = card.dataset.source;
      updateExtractionPrompt();
    });
  });

  // Target Provider Selection (Step 3)
  elements.targetTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      elements.targetTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      state.targetProvider = tab.dataset.target;
      hydrateTarget();
    });
  });

  // Character Counter for Source Input
  elements.inputRawMemory.addEventListener("input", () => {
    const len = elements.inputRawMemory.value.length;
    elements.sourceCharCounter.textContent = `${len.toLocaleString()} chars`;
  });

  // Copy Extraction Prompt
  elements.btnCopyExtractionPrompt.addEventListener("click", () => {
    copyToClipboard(elements.displayExtractionPrompt.textContent, "Extraction prompt copied!");
  });

  // Fill Demo Data
  elements.btnDemoPaste.addEventListener("click", () => {
    if (state.demoData && state.demoData.demo_chatgpt_raw) {
      elements.inputRawMemory.value = state.demoData.demo_chatgpt_raw;
      elements.sourceCharCounter.textContent = `${elements.inputRawMemory.value.length.toLocaleString()} chars`;
      showToast("Demo ChatGPT memory dump loaded!");
    }
  });

  // File Upload Handlers
  const fileUploadMemory = document.getElementById("file-upload-memory");
  if (fileUploadMemory) {
    fileUploadMemory.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = async (evt) => {
        const text = evt.target.result;
        elements.inputRawMemory.value = text;
        elements.sourceCharCounter.textContent = `${text.length.toLocaleString()} chars`;
        showToast(`Loaded ${file.name} (${text.length.toLocaleString()} chars). Parsing...`);
        await parseMemoryInput();
      };
      reader.readAsText(file);
    });
  }

  const fileUploadHandoff = document.getElementById("file-upload-handoff");
  if (fileUploadHandoff) {
    fileUploadHandoff.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = async (evt) => {
        const text = evt.target.result;
        elements.inputHandoffChat.value = text;
        elements.handoffCharCounter.textContent = `${text.length.toLocaleString()} chars`;
        showToast(`Loaded ${file.name} (${text.length.toLocaleString()} chars). Distilling...`);
        await distillChatThread();
      };
      reader.readAsText(file);
    });
  }

  // 1-Click Complete Demo Execution
  elements.btnLoadDemo.addEventListener("click", async () => {
    switchTab("studio");
    if (!state.demoData) await loadDemoData();
    elements.inputRawMemory.value = state.demoData.demo_chatgpt_raw;
    elements.sourceCharCounter.textContent = `${elements.inputRawMemory.value.length.toLocaleString()} chars`;
    await parseMemoryInput();
    await hydrateTarget();
    elements.inputVerifyResponse.value = state.demoData.demo_claude_verification;
    setStep(4);
    await computeDiff();
    showToast("1-Click Demo executed! Viewing verified retention diff.");
  });

  // Step Navigation: Parse & Next to Step 2
  elements.btnParseMemory.addEventListener("click", async () => {
    await parseMemoryInput();
  });

  if (elements.btnBackStep1) {
    elements.btnBackStep1.addEventListener("click", () => setStep(1));
  }

  // Step Navigation: Step 2 to Step 3
  if (elements.btnProceedHydrate) {
    elements.btnProceedHydrate.addEventListener("click", async () => {
      await hydrateTarget();
      setStep(3);
    });
  }

  if (elements.btnBackStep2) {
    elements.btnBackStep2.addEventListener("click", () => setStep(2));
  }

  // Step Navigation: Step 3 to Step 4
  if (elements.btnProceedVerify) {
    elements.btnProceedVerify.addEventListener("click", () => {
      setStep(4);
    });
  }

  if (elements.btnBackStep3) {
    elements.btnBackStep3.addEventListener("click", () => setStep(3));
  }

  if (elements.btnRestartMigration) {
    elements.btnRestartMigration.addEventListener("click", () => {
      setStep(1);
      showToast("Ready for a new memory migration.");
    });
  }

  // 1-Click Extension Ingest Trigger
  if (elements.btnTriggerExtensionInject) {
    elements.btnTriggerExtensionInject.addEventListener("click", () => {
      const text = elements.hydratedOutputDisplay.textContent;
      if (!text) {
        showToast("No memory payload available. Complete Step 1 first.");
        return;
      }
      copyToClipboard(text, "Memory payload copied!");
      showToast("✓ Copied payload! Click the UMS icon in your browser toolbar on Claude or ChatGPT to inject.");
    });
  }

  // Copy Hydrated Output
  elements.btnCopyHydrated.addEventListener("click", () => {
    copyToClipboard(elements.hydratedOutputDisplay.textContent, "Target ingest text copied!");
  });

  // Copy Verification Query
  elements.btnCopyVerifyQuery.addEventListener("click", () => {
    copyToClipboard(elements.verificationQueryText.textContent.replace(/^"|"$/g, ""), "Verification query copied!");
  });

  // Fill Demo Verification
  elements.btnFillDemoVerification.addEventListener("click", () => {
    if (state.demoData && state.demoData.demo_claude_verification) {
      elements.inputVerifyResponse.value = state.demoData.demo_claude_verification;
      showToast("Simulated verification response filled!");
    }
  });

  // Compute Diff
  elements.btnComputeDiff.addEventListener("click", async () => {
    await computeDiff();
  });

  // Pruning Switches: Re-hydrate on change
  [elements.chkTier1, elements.chkTier2, elements.chkTier3, elements.chkFilterNonWork].forEach(sw => {
    sw.addEventListener("change", () => {
      if (state.currentPayload) hydrateTarget();
    });
  });

  // Vault Actions
  elements.btnSaveCurrentVault.addEventListener("click", saveCurrentToVault);
  elements.btnExportVaultJson.addEventListener("click", () => {
    if (!state.currentPayload) {
      showToast("No active persona to download. Parse one first!");
      return;
    }
    const blob = new Blob([JSON.stringify(state.currentPayload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `persona-${state.currentPayload.metadata.id || "export"}.ums.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("Downloaded .ums.json!");
  });

  // IDE Tab Switching
  elements.ideTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      elements.ideTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      renderIdeFile(tab.dataset.file);
    });
  });

  elements.btnCopyIdeFile.addEventListener("click", () => {
    copyToClipboard(elements.ideFileContent.textContent, "Rule file copied!");
  });

  if (elements.btnExecuteFsSync) {
    elements.btnExecuteFsSync.addEventListener("click", executeDirectFsSync);
  }

  // Chat Handoff Event Listeners
  if (elements.inputHandoffChat) {
    elements.inputHandoffChat.addEventListener("input", () => {
      const len = elements.inputHandoffChat.value.length;
      elements.handoffCharCounter.textContent = `${len.toLocaleString()} chars`;
    });
  }
  if (elements.btnLoadDemoChat) {
    elements.btnLoadDemoChat.addEventListener("click", loadDemoChatThread);
  }
  if (elements.btnDistillFull) {
    elements.btnDistillFull.addEventListener("click", () => distillChatThread("full"));
  }
  if (elements.btnDistillChat) {
    elements.btnDistillChat.addEventListener("click", () => distillChatThread("summary"));
  }
  if (elements.btnCopyHandoffPrimerWeb) {
    elements.btnCopyHandoffPrimerWeb.addEventListener("click", () => {
      copyToClipboard(elements.handoffPrimerDisplay.textContent, "Context Handoff Primer copied!");
    });
  }
  if (elements.btnLaunchTargetAi) {
    elements.btnLaunchTargetAi.addEventListener("click", launchTargetAiTab);
  }

  // Live Cross-Tab Web Radar Listeners (Dual Modes: Full vs Summary)
  if (elements.btnWebTransferFull) {
    elements.btnWebTransferFull.addEventListener("click", () => executeWebAutoTransfer("full"));
  }
  if (elements.btnWebTransferSummary) {
    elements.btnWebTransferSummary.addEventListener("click", () => executeWebAutoTransfer("summary"));
  }
  if (elements.btnWebRescanTabs) {
    elements.btnWebRescanTabs.addEventListener("click", () => {
      queryOpenAITabs();
      showToast("Scanning browser tabs...");
    });
  }
  if (elements.webRadarSourceSelect) {
    elements.webRadarSourceSelect.addEventListener("change", () => {
      if (detectedWebTabs && detectedWebTabs.tabs) {
        populateWebTargetDropdown(detectedWebTabs.tabs);
      } else {
        updateWebButtonLabels();
      }
    });
  }
  if (elements.webRadarTargetSelect) {
    elements.webRadarTargetSelect.addEventListener("change", updateWebButtonLabels);
  }

  // Auto-refresh tabs when window gains focus
  window.addEventListener("focus", queryOpenAITabs);

  // Chrome Extension postMessage Bridge
  window.addEventListener("message", handleExtensionBridgeMessages);
}

// Navigation Tab Switcher
function switchTab(tabId) {
  state.currentTab = tabId;
  elements.tabs.forEach(t => t.classList.toggle("active", t.dataset.tab === tabId));
  elements.tabPanels.forEach(p => p.classList.toggle("active", p.id === `tab-${tabId}`));

  if (tabId === "handoff") {
    queryOpenAITabs();
  }

  if (tabId === "vault") {
    loadProfiles();
    loadIdeFiles();
  }
}

// Strictly Isolate Steps: Only the active step is visible on screen!
function setStep(step) {
  state.currentStep = step;
  elements.stepperNodes.forEach(node => {
    const s = parseInt(node.dataset.step);
    node.classList.toggle("active", s === step);
    node.classList.toggle("completed", s < step);
  });

  // Toggle step sections: Step 1, 2, 3, 4
  for (let i = 1; i <= 4; i++) {
    const sec = document.getElementById(`studio-step-${i}`);
    if (sec) sec.classList.toggle("d-none", i !== step);
  }

  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Load Prompts & Data
async function loadPrompts() {
  try {
    const resp = await fetch("/api/prompts");
    state.cachedPrompts = await resp.json();
    updateExtractionPrompt();
  } catch (err) {
    console.error("Failed to load prompts", err);
  }
}

async function loadDemoData() {
  try {
    const resp = await fetch("/api/demo-data");
    state.demoData = await resp.json();
  } catch (err) {
    console.error("Failed to load demo data", err);
  }
}

function updateExtractionPrompt() {
  if (!state.cachedPrompts) return;
  const prompt = state.cachedPrompts.extraction_prompts[state.sourceProvider] || state.cachedPrompts.extraction_prompts.chatgpt;
  elements.displayExtractionPrompt.textContent = prompt;
}

// Parse Input
async function parseMemoryInput() {
  const text = elements.inputRawMemory.value.trim();
  if (!text) {
    showToast("Please paste memory text or click 'Fill Demo Data'.");
    return;
  }

  try {
    elements.btnParseMemory.disabled = true;
    elements.btnParseMemory.textContent = "Normalizing into UMS...";

    const resp = await fetch("/api/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source: state.sourceProvider,
        text: text,
        name: "Imported Persona"
      })
    });

    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    state.currentPayload = data.payload;
    renderStep2Previews();
    setStep(2);
    showToast("Parsed successfully into UMS v1.0!");
  } catch (err) {
    showToast("Parse error: " + err.message);
  } finally {
    elements.btnParseMemory.disabled = false;
    elements.btnParseMemory.innerHTML = `
      Parse & Continue to Review (Step 2)
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
    `;
  }
}

// Render Step 2 Review Items
function renderStep2Previews() {
  if (!state.currentPayload) return;
  const t1 = state.currentPayload.tier1_identity;
  const t2 = state.currentPayload.tier2_active_context;
  const t3 = state.currentPayload.tier3_conversation_transcript;

  // Tier 1 items
  let t1Html = "";
  if (t1.profile.role) {
    t1Html += `<div class="item-chip"><span class="item-chip-title">Role</span><span class="item-chip-desc">${escapeHtml(t1.profile.role)}</span></div>`;
  }
  const allTech = [...t1.tech_stack.primary_languages, ...t1.tech_stack.frameworks, ...t1.tech_stack.databases];
  if (allTech.length > 0) {
    t1Html += `<div class="item-chip"><span class="item-chip-title">Tech Stack</span><span class="item-chip-desc">${escapeHtml(allTech.join(", "))}</span></div>`;
  }
  if (t1.communication_style.tone) {
    t1Html += `<div class="item-chip"><span class="item-chip-title">Tone</span><span class="item-chip-desc">${escapeHtml(t1.communication_style.tone)}</span></div>`;
  }
  if (t1.communication_style.prohibitions.length > 0) {
    t1Html += `<div class="item-chip"><span class="item-chip-title">Prohibitions</span><span class="item-chip-desc">${t1.communication_style.prohibitions.length} rules</span></div>`;
  }
  if (t1.personal_trivia && t1.personal_trivia.length > 0) {
    t1Html += `<div class="item-chip"><span class="item-chip-title">Lifestyle/Trivia</span><span class="item-chip-desc">${t1.personal_trivia.length} items (filtered by Claude Work policy)</span></div>`;
  }
  elements.t1Preview.innerHTML = t1Html || `<div class="empty-hint">No Tier 1 items detected</div>`;

  // Tier 2 items
  let t2Html = "";
  if (t2.current_objective) {
    t2Html += `<div class="item-chip"><span class="item-chip-title">Objective</span><span class="item-chip-desc">${escapeHtml(t2.current_objective)}</span></div>`;
  }
  if (t2.active_projects && t2.active_projects.length > 0) {
    t2.active_projects.forEach(p => {
      const decCount = p.decisions_made_today ? p.decisions_made_today.length : 0;
      t2Html += `<div class="item-chip"><span class="item-chip-title">${escapeHtml(p.name)}</span><span class="item-chip-desc">${decCount} decisions today</span></div>`;
    });
  }
  elements.t2Preview.innerHTML = t2Html || `<div class="empty-hint">No Tier 2 items detected</div>`;

  // Tier 3 items
  if (t3 && t3.included) {
    elements.t3Preview.innerHTML = `<div class="item-chip"><span class="item-chip-title">Messages</span><span class="item-chip-desc">${t3.message_count || 0} messages</span></div>`;
  } else {
    elements.t3Preview.innerHTML = `<div class="empty-hint">Excluded by default. 0 tokens wasted.</div>`;
  }
}

// Hydrate for Target Provider
async function hydrateTarget() {
  if (!state.currentPayload) return;

  const incT1 = elements.chkTier1.checked;
  const incT2 = elements.chkTier2.checked;
  const incT3 = elements.chkTier3.checked;
  const filterNonWork = elements.chkFilterNonWork.checked;

  try {
    const resp = await fetch("/api/hydrate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        payload: state.currentPayload,
        target: state.targetProvider,
        options: {
          include_tier1: incT1,
          include_tier2: incT2,
          include_tier3: incT3,
          filter_non_work: filterNonWork
        }
      })
    });

    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    // Update Step 3 View
    if (state.targetProvider === "claude") {
      elements.hydratedTokenCount.textContent = `~${data.token_estimate} tokens`;
      elements.tokenSavingsBadge.textContent = "92% smaller than raw transcripts";
      elements.hydrationInstructions.innerHTML = `<strong>Claude Ingestion:</strong> Go to Settings → Memory → Start import, or click 'Push into Active Browser Tab'.`;
      elements.hydratedOutputDisplay.textContent = data.import_text;
      elements.verificationQueryText.textContent = `"${data.verification_query}"`;
    } else if (state.targetProvider === "chatgpt") {
      elements.hydratedTokenCount.textContent = `Box 1: ${data.custom_instructions_box_1_chars}/1500 chars | Box 2: ${data.custom_instructions_box_2_chars}/1500 chars`;
      elements.tokenSavingsBadge.textContent = "Custom Instructions Ready";
      elements.hydrationInstructions.innerHTML = `<strong>ChatGPT Ingestion:</strong> Paste into Custom Instructions, or use the UMS Browser Extension.`;
      elements.hydratedOutputDisplay.textContent = `=== BOX 1: WHAT CHATGPT SHOULD KNOW ABOUT YOU ===\n${data.custom_instructions_box_1}\n\n=== BOX 2: HOW CHATGPT SHOULD RESPOND ===\n${data.custom_instructions_box_2}\n\n=== ALTERNATIVE CONVERSATIONAL INGEST PROMPT ===\n${data.memory_injection_prompt}`;
      elements.verificationQueryText.textContent = `"${data.verification_query}"`;
    } else if (state.targetProvider === "gemini") {
      elements.hydratedTokenCount.textContent = `~${data.token_estimate} tokens`;
      elements.tokenSavingsBadge.textContent = "Gems Ready";
      elements.hydrationInstructions.innerHTML = `<strong>Gemini Ingestion:</strong> Paste into Gems Instructions.`;
      elements.hydratedOutputDisplay.textContent = data.system_instruction;
      elements.verificationQueryText.textContent = `"${data.verification_query}"`;
    }
  } catch (err) {
    showToast("Hydration error: " + err.message);
  }
}

// Compute Semantic Retention Diff
async function computeDiff() {
  if (!state.currentPayload) {
    showToast("No active UMS payload loaded.");
    return;
  }
  const verifyText = elements.inputVerifyResponse.value.trim();
  if (!verifyText) {
    showToast("Please paste the verification answer from the target model.");
    return;
  }

  try {
    elements.btnComputeDiff.disabled = true;
    elements.btnComputeDiff.textContent = "Analyzing semantic retention...";

    const resp = await fetch("/api/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        payload: state.currentPayload,
        verification_response: verifyText,
        target_provider: state.targetProvider,
        save_log: true
      })
    });

    const diff = await resp.json();
    if (diff.error) throw new Error(diff.error);

    renderDiffResults(diff);
    elements.diffDashboard.classList.remove("d-none");
    showToast("Retention Diff computed and recorded!");
  } catch (err) {
    showToast("Diff error: " + err.message);
  } finally {
    elements.btnComputeDiff.disabled = false;
    elements.btnComputeDiff.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>
      Compute Semantic Retention Diff
    `;
  }
}

// Render Diff Results Dashboard
function renderDiffResults(diff) {
  elements.diffRetentionScore.textContent = `${diff.retention_score}%`;
  elements.countLearned.textContent = diff.categories.learned.length;
  elements.countAdapted.textContent = diff.categories.adapted.length;
  elements.countFiltered.textContent = diff.categories.filtered.length;

  // Suggestions
  let sugHtml = "";
  if (diff.suggestions && diff.suggestions.length > 0) {
    diff.suggestions.forEach(s => {
      sugHtml += `<div class="suggestion-item">💡 <strong>Insight:</strong> ${escapeHtml(s)}</div>`;
    });
  } else {
    sugHtml = `<div class="suggestion-item">✓ Outstanding retention! Key preferences fully absorbed.</div>`;
  }
  elements.diffSuggestions.innerHTML = sugHtml;

  // Detailed Entries
  let entriesHtml = "";
  diff.categories.learned.forEach(item => {
    entriesHtml += `
      <div class="diff-card diff-card-learned">
        <div class="diff-card-header">
          <span class="diff-badge badge-green">Retained</span>
          <span class="diff-item-key">${escapeHtml(item.key)}</span>
        </div>
        <div class="diff-card-body">
          <div class="diff-text"><strong>Absorbed:</strong> ${escapeHtml(item.value)}</div>
        </div>
      </div>
    `;
  });

  diff.categories.adapted.forEach(item => {
    entriesHtml += `
      <div class="diff-card diff-card-adapted">
        <div class="diff-card-header">
          <span class="diff-badge badge-yellow">Adapted</span>
          <span class="diff-item-key">${escapeHtml(item.key)}</span>
        </div>
        <div class="diff-card-body">
          <div class="diff-text"><strong>Adapted into:</strong> ${escapeHtml(item.adaptation_note || item.value)}</div>
        </div>
      </div>
    `;
  });

  diff.categories.filtered.forEach(item => {
    entriesHtml += `
      <div class="diff-card diff-card-filtered">
        <div class="diff-card-header">
          <span class="diff-badge badge-red">Filtered</span>
          <span class="diff-item-key">${escapeHtml(item.key)}</span>
        </div>
        <div class="diff-card-body">
          <div class="diff-text"><strong>Omitted item:</strong> ${escapeHtml(item.value)}</div>
          <div class="diff-reason"><em>Reason: ${escapeHtml(item.reason || "Non-work trivia filtered by Claude policy")}</em></div>
        </div>
      </div>
    `;
  });

  elements.diffEntriesContainer.innerHTML = entriesHtml;
}

// Vault Persistence Functions
async function loadProfiles() {
  try {
    const resp = await fetch("/api/profiles");
    const data = await resp.json();
    renderProfilesGrid(data.profiles || []);
  } catch (err) {
    console.error("Failed to load profiles", err);
  }
}

function renderProfilesGrid(profiles) {
  if (!elements.vaultProfilesGrid) return;
  if (!profiles || profiles.length === 0) {
    elements.vaultProfilesGrid.innerHTML = `<div class="empty-state">No personas saved in SQLite vault yet.</div>`;
    return;
  }

  let html = "";
  profiles.forEach(p => {
    html += `
      <div class="vault-card" data-id="${p.id}">
        <div class="vault-card-top">
          <h4>${escapeHtml(p.name)}</h4>
          <span class="badge badge-subtle">${escapeHtml(p.source)}</span>
        </div>
        <div class="vault-details">
          <div><strong>Role:</strong> ${escapeHtml(p.role || "Developer")}</div>
          <div><strong>Tech:</strong> ${escapeHtml((p.primary_languages || []).join(", ") || "Full-Stack")}</div>
          <div class="vault-date">${new Date(p.created_at).toLocaleDateString()}</div>
        </div>
      </div>
    `;
  });
  elements.vaultProfilesGrid.innerHTML = html;
}

async function saveCurrentToVault() {
  if (!state.currentPayload) {
    showToast("Please parse or load a persona first.");
    return;
  }

  try {
    const resp = await fetch("/api/profiles", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state.currentPayload)
    });
    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    showToast("Saved persona to SQLite vault!");
    await loadProfiles();
  } catch (err) {
    showToast("Save failed: " + err.message);
  }
}

// IDE Exporter Functions
async function loadIdeFiles() {
  if (!state.currentPayload) return;
  try {
    const resp = await fetch("/api/hydrate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        payload: state.currentPayload,
        target: "ide"
      })
    });
    const data = await resp.json();
    if (data.files) {
      state.activeIdeFiles = data.files;
      renderIdeFile("claude_md");
    }
  } catch (err) {
    console.error("Failed to generate IDE files", err);
  }
}

function renderIdeFile(fileKey) {
  if (!state.activeIdeFiles) return;
  const titles = {
    claude_md: "CLAUDE.md (Claude Code Rules)",
    cursorrules: ".cursorrules (Cursor IDE Guidelines)",
    agents_md: "AGENTS.md (Windsurf & Autonomous Agents)"
  };

  elements.ideFileTitle.textContent = titles[fileKey] || fileKey;
  elements.ideFileContent.textContent = state.activeIdeFiles[fileKey] || "// File not generated yet";
}

async function executeDirectFsSync() {
  if (!state.currentPayload) {
    showToast("Please parse or load a memory payload first.");
    return;
  }

  const path = (elements.inputFsPath ? elements.inputFsPath.value.trim() : "") || ".";
  elements.btnExecuteFsSync.disabled = true;
  elements.fsSyncStatusMsg.className = "sync-status-indicator status-loading mt-2";
  elements.fsSyncStatusMsg.classList.remove("d-none");
  elements.fsSyncStatusMsg.innerHTML = `Writing CLAUDE.md, .cursorrules to ${escapeHtml(path)}...`;

  try {
    const resp = await fetch("/api/sync/filesystem", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        payload: state.currentPayload,
        target_dir: path
      })
    });

    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    elements.fsSyncStatusMsg.className = "sync-status-indicator status-success mt-2";
    elements.fsSyncStatusMsg.innerHTML = `✓ <strong>Files Created:</strong> ${escapeHtml(data.message)}`;
    showToast("Wrote rule files directly to project on disk!");
  } catch (err) {
    elements.fsSyncStatusMsg.className = "sync-status-indicator status-error mt-2";
    elements.fsSyncStatusMsg.innerHTML = `✕ <strong>Write Failed:</strong> ${escapeHtml(err.message)}`;
    showToast("Filesystem write error: " + err.message);
  } finally {
    elements.btnExecuteFsSync.disabled = false;
  }
}

// Chat Handoff Studio Functions
async function loadDemoChatThread() {
  try {
    const res = await fetch("/api/handoff/demo");
    const data = await res.json();
    if (data.demo_chat) {
      elements.inputHandoffChat.value = data.demo_chat;
      elements.handoffCharCounter.textContent = `${data.demo_chat.length.toLocaleString()} chars`;
      showToast("Loaded Next.js 15 JWT demo thread!");
    }
  } catch (err) {
    showToast("Failed to load demo thread: " + err.message);
  }
}

async function distillChatThread(mode = "full") {
  const rawChat = elements.inputHandoffChat.value.trim();
  if (!rawChat) {
    showToast("Please enter or load a chat thread first.");
    return;
  }

  const source = elements.handoffSourceSelect.value;
  const target = elements.handoffTargetSelect.value;

  const activeBtn = mode === "full" ? elements.btnDistillFull : elements.btnDistillChat;
  if (activeBtn) {
    activeBtn.disabled = true;
    activeBtn.textContent = mode === "full" ? "Compiling Full Context..." : "Distilling Summary (0 Tokens)...";
  }

  try {
    const res = await fetch("/api/handoff/distill", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        raw_chat: rawChat,
        source: source,
        target: target,
        mode: mode
      })
    });

    const data = await res.json();
    if (data.error) throw new Error(data.error);

    state.handoffData = data;

    elements.handoffSavingsBadge.textContent = `${data.token_savings_percent}% Token Savings`;
    elements.handoffTokenCount.textContent = `~${data.token_estimate} tokens (was ~${data.raw_token_estimate})`;
    elements.handoffExtractedGoal.textContent = data.primary_goal || "General context";
    elements.handoffExtractedTech.textContent = (data.detected_tech && data.detected_tech.length) ? data.detected_tech.join(", ") : "None Detected";
    elements.handoffExtractedNext.textContent = data.immediate_next_task || "Continue session";
    elements.handoffPrimerDisplay.textContent = data.handoff_primer;

    elements.handoffResultsPanel.classList.remove("d-none");
    showToast(`Compiled (${mode === "summary" ? "Condensed Summary" : "Full Chat As-Is"})!`);
  } catch (err) {
    showToast("Distillation failed: " + err.message);
  } finally {
    if (elements.btnDistillFull) {
      elements.btnDistillFull.disabled = false;
      elements.btnDistillFull.textContent = "⚡ Compile Full Context (As-Is Handoff)";
    }
    if (elements.btnDistillChat) {
      elements.btnDistillChat.disabled = false;
      elements.btnDistillChat.textContent = "🧠 Compile Condensed Summary (0 Tokens)";
    }
  }
}

function launchTargetAiTab() {
  if (!state.handoffData || !state.handoffData.handoff_primer) {
    showToast("Compile or distill a thread first.");
    return;
  }

  copyToClipboard(state.handoffData.handoff_primer, "Handoff Primer copied to clipboard!");

  const target = elements.handoffTargetSelect.value;
  const targetUrls = {
    chatgpt: "https://chatgpt.com/",
    claude: "https://claude.ai/new",
    gemini: "https://gemini.google.com/app",
    perplexity: "https://www.perplexity.ai/",
    deepseek: "https://chat.deepseek.com/",
    mistral: "https://chat.mistral.ai/",
    claude_code: "https://claude.ai/code"
  };

  const url = targetUrls[target] || "https://claude.ai/new";
  window.open(url, "_blank");
  showToast(`Launched ${target.toUpperCase()}! Primer copied to clipboard.`);
}

// Utility Helpers
function copyToClipboard(text, successMessage = "Copied to clipboard!") {
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => {
    showToast(successMessage);
  }).catch(err => {
    console.error("Clipboard copy error", err);
    showToast("Failed to copy to clipboard.");
  });
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.remove("d-none");
  setTimeout(() => {
    elements.toast.classList.add("d-none");
  }, 3000);
}

function escapeHtml(str) {
  if (typeof str !== "string") return str;
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Live Web Cross-Tab Radar & Bridge
let detectedWebTabs = null;

function queryOpenAITabs() {
  window.postMessage({ type: "UMS_PING" }, "*");
  window.postMessage({ type: "UMS_DETECT_TABS" }, "*");
}

function handleExtensionBridgeMessages(event) {
  if (!event.data) return;

  if (event.data.type === "UMS_EXTENSION_READY") {
    state.extensionActive = true;
    queryOpenAITabs();
  }

  if (event.data.type === "UMS_DETECT_TABS_RESPONSE") {
    const data = event.data.data;
    if (data && data.status === "success") {
      detectedWebTabs = data;
      renderWebRadar(data);
    }
  }

  if (event.data.type === "UMS_AUTO_TRANSFER_RESPONSE") {
    const res = event.data.data;
    updateWebButtonLabels();
    if (res && res.status === "success") {
      showToast(`✓ Transferred successfully (${res.mode === "summary" ? "Condensed Summary" : "Full Chat"})! ${res.token_savings_percent || ""}% savings.`);
      if (res.handoff_primer) {
        elements.handoffSavingsBadge.textContent = `${res.token_savings_percent}% Token Savings`;
        elements.handoffExtractedGoal.textContent = res.primary_goal || "Live transferred session";
        elements.handoffExtractedNext.textContent = res.immediate_next_task || "Continue session in target tab";
        elements.handoffPrimerDisplay.textContent = res.handoff_primer;
        elements.handoffResultsPanel.classList.remove("d-none");
      }
    } else {
      showToast(`✕ Transfer failed: ${res ? res.message : "Unknown error"}`);
    }
  }
}

function renderWebRadar(tabsData) {
  if (!elements.webRadarPanel) return;
  const allTabs = (tabsData && tabsData.tabs) ? tabsData.tabs : [];
  const total = allTabs.length;

  if (elements.webRadarCountBadge) {
    elements.webRadarCountBadge.textContent = total > 0 ? `${total} Live Tab${total > 1 ? 's' : ''} Open` : "0 Tabs";
    elements.webRadarCountBadge.className = total > 0 ? "badge badge-emerald" : "badge badge-subtle";
  }

  if (total === 0) {
    if (elements.webRadarStatusText) {
      elements.webRadarStatusText.textContent = "No open AI tabs detected. Open ChatGPT, Claude, Gemini, or DeepSeek in your browser and click 'Rescan Browser Tabs'.";
    }
    if (elements.webRadarTabsChips) {
      elements.webRadarTabsChips.innerHTML = `<span style="color: #64748b; font-size: 0.82rem;">(Radar scanning... open AI tabs will appear here automatically)</span>`;
    }
    if (elements.webRadarSelectorsContainer) {
      elements.webRadarSelectorsContainer.classList.add("d-none");
    }
    return;
  }

  if (elements.webRadarStatusText) {
    elements.webRadarStatusText.textContent = `${total} live AI tab${total > 1 ? 's' : ''} ready. Choose your source chat and destination AI below:`;
  }

  // Render open tabs as colored chips
  if (elements.webRadarTabsChips) {
    let chipsHtml = "";
    allTabs.forEach(tab => {
      const color = tab.color || "#10b981";
      const label = tab.label || tab.provider.toUpperCase();
      chipsHtml += `
        <div class="web-radar-chip" title="${escapeHtml(tab.fullTitle || tab.title)}">
          <span class="web-radar-chip-badge" style="background: rgba(255, 255, 255, 0.06); color: var(--text-main); border: 1px solid var(--border-color);">
            ${label}${tab.active ? ' (Active)' : ''}
          </span>
          <span>${escapeHtml(tab.title)}</span>
        </div>
      `;
    });
    elements.webRadarTabsChips.innerHTML = chipsHtml;
  }

  // Unhide and populate interactive selectors
  if (elements.webRadarSelectorsContainer) {
    elements.webRadarSelectorsContainer.classList.remove("d-none");
    populateWebSourceDropdown(allTabs);
  }
}

function populateWebSourceDropdown(allTabs) {
  if (!elements.webRadarSourceSelect) return;
  const srcSelect = elements.webRadarSourceSelect;
  const currentVal = srcSelect.value;
  srcSelect.innerHTML = "";

  allTabs.forEach((tab) => {
    const opt = document.createElement("option");
    opt.value = tab.id;
    opt.dataset.provider = tab.provider;
    opt.dataset.label = tab.label || tab.provider;
    opt.textContent = `[${tab.label || tab.provider.toUpperCase()}] ${tab.title}`;
    srcSelect.appendChild(opt);
  });

  if (currentVal && allTabs.some(t => String(t.id) === currentVal)) {
    srcSelect.value = currentVal;
  } else {
    srcSelect.selectedIndex = 0;
  }

  populateWebTargetDropdown(allTabs);
}

function populateWebTargetDropdown(allTabs) {
  if (!elements.webRadarSourceSelect || !elements.webRadarTargetSelect) return;
  const srcSelect = elements.webRadarSourceSelect;
  const tgtSelect = elements.webRadarTargetSelect;
  const currentVal = tgtSelect.value;

  const selectedSourceId = Number(srcSelect.value);
  const selectedSourceProv = srcSelect.selectedOptions[0]?.dataset?.provider || "chatgpt";

  tgtSelect.innerHTML = "";

  // 1. Add other open tabs (exclude selected source)
  const otherTabs = allTabs.filter(t => t.id !== selectedSourceId);
  if (otherTabs.length > 0) {
    const groupOther = document.createElement("optgroup");
    groupOther.label = "── Open Browser Tabs ──";
    otherTabs.forEach(t => {
      const opt = document.createElement("option");
      opt.value = t.id;
      opt.dataset.provider = t.provider;
      opt.dataset.label = t.label || t.provider;
      opt.textContent = `[${t.label || t.provider.toUpperCase()}] ${t.title}`;
      groupOther.appendChild(opt);
    });
    tgtSelect.appendChild(groupOther);
  }

  // 2. Add New Tab options for all providers
  const groupNew = document.createElement("optgroup");
  groupNew.label = "── Open in New Tab ──";
  const newOptions = [
    { prov: "claude", label: "Claude" },
    { prov: "chatgpt", label: "ChatGPT" },
    { prov: "gemini", label: "Gemini" },
    { prov: "perplexity", label: "Perplexity" },
    { prov: "deepseek", label: "DeepSeek" },
    { prov: "mistral", label: "Mistral" }
  ];

  newOptions.forEach(item => {
    const opt = document.createElement("option");
    opt.value = `new_${item.prov}`;
    opt.dataset.provider = item.prov;
    opt.dataset.label = item.label;
    opt.textContent = `+ New Tab: ${item.label}`;
    groupNew.appendChild(opt);
  });
  tgtSelect.appendChild(groupNew);

  // Preserve previous choice if valid
  if (currentVal && Array.from(tgtSelect.options).some(o => o.value === currentVal)) {
    tgtSelect.value = currentVal;
  } else if (otherTabs.length > 0) {
    tgtSelect.selectedIndex = 0;
  } else {
    const defaultNewProv = selectedSourceProv === "claude" ? "chatgpt" : "claude";
    const foundIndex = Array.from(tgtSelect.options).findIndex(o => o.value === `new_${defaultNewProv}`);
    if (foundIndex >= 0) tgtSelect.selectedIndex = foundIndex;
  }

  updateWebButtonLabels();
}

function updateWebButtonLabels() {
  if (!elements.webRadarSourceSelect || !elements.webRadarTargetSelect) return;
  const srcLabel = elements.webRadarSourceSelect.selectedOptions[0]?.dataset?.label || "Source";
  const tgtLabel = elements.webRadarTargetSelect.selectedOptions[0]?.dataset?.label || "Target";

  if (elements.btnWebTransferFull) {
    elements.btnWebTransferFull.disabled = false;
    elements.btnWebTransferFull.innerHTML = `⚡ 1-Click Transfer Full Chat (${srcLabel} ➔ ${tgtLabel})`;
  }
  if (elements.btnWebTransferSummary) {
    elements.btnWebTransferSummary.disabled = false;
    elements.btnWebTransferSummary.innerHTML = `🧠 1-Click Transfer Condensed Summary (${srcLabel} ➔ ${tgtLabel})`;
  }
}

async function executeWebAutoTransfer(mode = "full") {
  if (!elements.webRadarSourceSelect || !elements.webRadarTargetSelect || !elements.webRadarSourceSelect.value) {
    showToast("Please select an active source AI chat tab.");
    return;
  }

  const srcOption = elements.webRadarSourceSelect.selectedOptions[0];
  const tgtOption = elements.webRadarTargetSelect.selectedOptions[0];

  const sourceTabId = Number(elements.webRadarSourceSelect.value);
  const sourceProv = srcOption?.dataset?.provider || "chatgpt";

  const targetVal = elements.webRadarTargetSelect.value;
  const isTargetNew = targetVal.startsWith("new_");
  const targetTabId = isTargetNew ? null : Number(targetVal);
  const targetProv = tgtOption?.dataset?.provider || "claude";

  const btn = mode === "full" ? elements.btnWebTransferFull : elements.btnWebTransferSummary;
  if (btn) {
    btn.disabled = true;
    btn.textContent = mode === "full" ? "Extracting & Transferring Full Chat..." : "Extracting & Distilling Summary...";
  }

  window.postMessage({
    type: "UMS_AUTO_TRANSFER",
    payload: {
      source_tab_id: sourceTabId,
      target_tab_id: targetTabId,
      source_provider: sourceProv,
      target_provider: targetProv,
      mode: mode
    }
  }, "*");
}
