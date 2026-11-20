// ATS Resume Tracker & Career Suite - Desktop Frontend Application
let currentResumeData = null;
let currentJdData = null;
let currentComparison = null;
let currentSuggestions = null;
let currentFunnelApps = [];
let selectedTailorTier = "tier2";
let currentTailoredResult = null;
let masterResumeData = null;
let masterProfiles = [];
let resumeLedgerEntries = [];

// ================= THEME SYSTEM =================
const THEME_STORAGE_KEY = "ats-theme-vars";

const THEME_VAR_GROUPS = [
  {
    title: "Backgrounds",
    vars: [
      { name: "--bg-main", label: "Page Background" },
      { name: "--bg-header", label: "Top Header Bar" },
      { name: "--bg-nav-strip", label: "Tab Nav Strip" },
      { name: "--bg-card", label: "Card Background" },
      { name: "--bg-card-hover", label: "Card Hover" },
      { name: "--bg-input", label: "Input Fields" },
      { name: "--bg-stat", label: "Stat / Tile Boxes" }
    ]
  },
  {
    title: "Borders",
    vars: [
      { name: "--border-color", label: "Border" },
      { name: "--border-color-strong", label: "Border (Strong)" }
    ]
  },
  {
    title: "Text",
    vars: [
      { name: "--text-primary", label: "Primary Text" },
      { name: "--text-secondary", label: "Secondary Text" },
      { name: "--text-muted", label: "Muted Text" }
    ]
  },
  {
    title: "Buttons & Accents",
    vars: [
      { name: "--accent-primary", label: "Primary Button" },
      { name: "--accent-primary-hover", label: "Primary Button (Hover)" },
      { name: "--accent-cyan", label: "Cyan Accent" },
      { name: "--accent-indigo", label: "Indigo Accent" },
      { name: "--accent-indigo-soft", label: "Indigo (Soft)" },
      { name: "--accent-purple-2", label: "Purple Accent" }
    ]
  },
  {
    title: "Status Colors",
    vars: [
      { name: "--accent-green", label: "Success Button" },
      { name: "--accent-green-hover", label: "Success (Hover)" },
      { name: "--accent-yellow", label: "Warning" },
      { name: "--accent-red", label: "Danger Button" },
      { name: "--accent-red-hover", label: "Danger (Hover)" },
      { name: "--text-success", label: "Success Text" },
      { name: "--text-danger", label: "Danger Text" },
      { name: "--text-info", label: "Info Text" },
      { name: "--text-warning", label: "Warning Text" }
    ]
  },
  {
    title: "Score Hero Gradient (Tab 3)",
    vars: [
      { name: "--score-hero-grad-start", label: "Gradient Start" },
      { name: "--score-hero-grad-end", label: "Gradient End" }
    ]
  }
];

const THEME_PRESETS = {
  midnight: {
    name: "Midnight",
    icon: "🌙",
    vars: {
      "--bg-main": "#0f172a", "--bg-header": "#0d1322", "--bg-nav-strip": "#131b2e", "--bg-card": "#1e293b",
      "--bg-card-hover": "#273549", "--bg-input": "#0b1120", "--bg-stat": "#111928",
      "--border-color": "#334155", "--border-color-strong": "#475569",
      "--text-primary": "#f8fafc", "--text-secondary": "#94a3b8", "--text-muted": "#64748b",
      "--accent-primary": "#6366f1", "--accent-primary-hover": "#4f46e5", "--accent-cyan": "#06b6d4",
      "--accent-indigo": "#818cf8", "--accent-indigo-soft": "#a5b4fc", "--accent-purple-2": "#7c3aed",
      "--accent-green": "#10b981", "--accent-green-hover": "#059669", "--accent-yellow": "#f59e0b",
      "--accent-red": "#ef4444", "--accent-red-hover": "#dc2626",
      "--text-success": "#34d399", "--text-danger": "#f87171", "--text-info": "#38bdf8", "--text-warning": "#fbbf24",
      "--score-hero-grad-start": "#4f46e5", "--score-hero-grad-end": "#7c3aed"
    }
  },
  daylight: {
    name: "Daylight Blue",
    icon: "☀️",
    vars: {
      "--bg-main": "#f1f5f9", "--bg-header": "#ffffff", "--bg-nav-strip": "#eef2f8", "--bg-card": "#ffffff",
      "--bg-card-hover": "#f8fafc", "--bg-input": "#ffffff", "--bg-stat": "#f1f5f9",
      "--border-color": "#e2e8f0", "--border-color-strong": "#cbd5e1",
      "--text-primary": "#0f172a", "--text-secondary": "#475569", "--text-muted": "#94a3b8",
      "--accent-primary": "#2563eb", "--accent-primary-hover": "#1d4ed8", "--accent-cyan": "#0891b2",
      "--accent-indigo": "#4f46e5", "--accent-indigo-soft": "#6366f1", "--accent-purple-2": "#7c3aed",
      "--accent-green": "#16a34a", "--accent-green-hover": "#15803d", "--accent-yellow": "#d97706",
      "--accent-red": "#dc2626", "--accent-red-hover": "#b91c1c",
      "--text-success": "#16a34a", "--text-danger": "#dc2626", "--text-info": "#2563eb", "--text-warning": "#b45309",
      "--score-hero-grad-start": "#2563eb", "--score-hero-grad-end": "#4f46e5"
    }
  },
  slate_indigo: {
    name: "Slate Indigo",
    icon: "🔮",
    vars: {
      "--bg-main": "#0b0f1f", "--bg-header": "#090d1a", "--bg-nav-strip": "#11162a", "--bg-card": "#161b2e",
      "--bg-card-hover": "#1f2540", "--bg-input": "#0a0e1c", "--bg-stat": "#11152a",
      "--border-color": "#2e3356", "--border-color-strong": "#3f466e",
      "--text-primary": "#f5f3ff", "--text-secondary": "#a5a0c9", "--text-muted": "#6f6b94",
      "--accent-primary": "#8b5cf6", "--accent-primary-hover": "#7c3aed", "--accent-cyan": "#22d3ee",
      "--accent-indigo": "#a78bfa", "--accent-indigo-soft": "#c4b5fd", "--accent-purple-2": "#a855f7",
      "--accent-green": "#10b981", "--accent-green-hover": "#059669", "--accent-yellow": "#f59e0b",
      "--accent-red": "#f43f5e", "--accent-red-hover": "#e11d48",
      "--text-success": "#6ee7b7", "--text-danger": "#fda4af", "--text-info": "#67e8f9", "--text-warning": "#fcd34d",
      "--score-hero-grad-start": "#7c3aed", "--score-hero-grad-end": "#c026d3"
    }
  },
  forest_night: {
    name: "Forest Night",
    icon: "🌲",
    vars: {
      "--bg-main": "#0b1410", "--bg-header": "#091210", "--bg-nav-strip": "#0f1b17", "--bg-card": "#142420",
      "--bg-card-hover": "#1c332c", "--bg-input": "#0a1512", "--bg-stat": "#10201b",
      "--border-color": "#2b4a3d", "--border-color-strong": "#3c6350",
      "--text-primary": "#ecfdf5", "--text-secondary": "#9fc5ad", "--text-muted": "#5f8870",
      "--accent-primary": "#10b981", "--accent-primary-hover": "#059669", "--accent-cyan": "#2dd4bf",
      "--accent-indigo": "#34d399", "--accent-indigo-soft": "#6ee7b7", "--accent-purple-2": "#0d9488",
      "--accent-green": "#22c55e", "--accent-green-hover": "#16a34a", "--accent-yellow": "#eab308",
      "--accent-red": "#f87171", "--accent-red-hover": "#ef4444",
      "--text-success": "#6ee7b7", "--text-danger": "#fca5a5", "--text-info": "#5eead4", "--text-warning": "#fde047",
      "--score-hero-grad-start": "#047857", "--score-hero-grad-end": "#0d9488"
    }
  },
  sunset_ember: {
    name: "Sunset Ember",
    icon: "🔥",
    vars: {
      "--bg-main": "#170f0a", "--bg-header": "#130c08", "--bg-nav-strip": "#1c130d", "--bg-card": "#271a12",
      "--bg-card-hover": "#34241a", "--bg-input": "#140d09", "--bg-stat": "#20150e",
      "--border-color": "#4a3324", "--border-color-strong": "#654531",
      "--text-primary": "#fff7ed", "--text-secondary": "#d6b89a", "--text-muted": "#9c7c5e",
      "--accent-primary": "#f97316", "--accent-primary-hover": "#ea580c", "--accent-cyan": "#fb923c",
      "--accent-indigo": "#fbbf24", "--accent-indigo-soft": "#fde68a", "--accent-purple-2": "#dc2626",
      "--accent-green": "#65a30d", "--accent-green-hover": "#4d7c0f", "--accent-yellow": "#facc15",
      "--accent-red": "#ef4444", "--accent-red-hover": "#dc2626",
      "--text-success": "#bef264", "--text-danger": "#fca5a5", "--text-info": "#fdba74", "--text-warning": "#fde047",
      "--score-hero-grad-start": "#ea580c", "--score-hero-grad-end": "#dc2626"
    }
  },
  lavender_light: {
    name: "Lavender Light",
    icon: "💜",
    vars: {
      "--bg-main": "#f6f4fd", "--bg-header": "#ffffff", "--bg-nav-strip": "#f1edfb", "--bg-card": "#ffffff",
      "--bg-card-hover": "#faf8ff", "--bg-input": "#ffffff", "--bg-stat": "#f6f4fd",
      "--border-color": "#e5e0f5", "--border-color-strong": "#cbc0ea",
      "--text-primary": "#1e1b3a", "--text-secondary": "#5b5580", "--text-muted": "#948db8",
      "--accent-primary": "#7c3aed", "--accent-primary-hover": "#6d28d9", "--accent-cyan": "#0891b2",
      "--accent-indigo": "#8b5cf6", "--accent-indigo-soft": "#a78bfa", "--accent-purple-2": "#a855f7",
      "--accent-green": "#16a34a", "--accent-green-hover": "#15803d", "--accent-yellow": "#d97706",
      "--accent-red": "#dc2626", "--accent-red-hover": "#b91c1c",
      "--text-success": "#15803d", "--text-danger": "#dc2626", "--text-info": "#7c3aed", "--text-warning": "#b45309",
      "--score-hero-grad-start": "#7c3aed", "--score-hero-grad-end": "#c026d3"
    }
  },
  meadow_light: {
    name: "Meadow Light",
    icon: "🍃",
    vars: {
      "--bg-main": "#f3faf5", "--bg-header": "#ffffff", "--bg-nav-strip": "#eef8f1", "--bg-card": "#ffffff",
      "--bg-card-hover": "#f6fdf8", "--bg-input": "#ffffff", "--bg-stat": "#f3faf5",
      "--border-color": "#dcf0e2", "--border-color-strong": "#a7dcb6",
      "--text-primary": "#0f2e1a", "--text-secondary": "#3f6b4f", "--text-muted": "#7fab8d",
      "--accent-primary": "#16a34a", "--accent-primary-hover": "#15803d", "--accent-cyan": "#0d9488",
      "--accent-indigo": "#22c55e", "--accent-indigo-soft": "#86efac", "--accent-purple-2": "#0d9488",
      "--accent-green": "#16a34a", "--accent-green-hover": "#15803d", "--accent-yellow": "#ca8a04",
      "--accent-red": "#dc2626", "--accent-red-hover": "#b91c1c",
      "--text-success": "#15803d", "--text-danger": "#dc2626", "--text-info": "#0d9488", "--text-warning": "#a16207",
      "--score-hero-grad-start": "#16a34a", "--score-hero-grad-end": "#0d9488"
    }
  },
  peach_light: {
    name: "Peach Light",
    icon: "🍑",
    vars: {
      "--bg-main": "#fdf6f0", "--bg-header": "#ffffff", "--bg-nav-strip": "#faf0e6", "--bg-card": "#ffffff",
      "--bg-card-hover": "#fffaf5", "--bg-input": "#ffffff", "--bg-stat": "#fdf6f0",
      "--border-color": "#f3e0cc", "--border-color-strong": "#e3b98c",
      "--text-primary": "#3a1f0a", "--text-secondary": "#8a5a2e", "--text-muted": "#c89968",
      "--accent-primary": "#ea580c", "--accent-primary-hover": "#c2410c", "--accent-cyan": "#0891b2",
      "--accent-indigo": "#f97316", "--accent-indigo-soft": "#fdba74", "--accent-purple-2": "#dc2626",
      "--accent-green": "#65a30d", "--accent-green-hover": "#4d7c0f", "--accent-yellow": "#d97706",
      "--accent-red": "#dc2626", "--accent-red-hover": "#b91c1c",
      "--text-success": "#4d7c0f", "--text-danger": "#dc2626", "--text-info": "#c2410c", "--text-warning": "#b45309",
      "--score-hero-grad-start": "#ea580c", "--score-hero-grad-end": "#dc2626"
    }
  }
};

function getAllThemeVarNames() {
  return THEME_VAR_GROUPS.flatMap(g => g.vars.map(v => v.name));
}

function applyThemeVars(varsObj) {
  const root = document.documentElement;
  Object.entries(varsObj).forEach(([name, value]) => {
    root.style.setProperty(name, value);
  });
}

function saveThemeOverride(varsObj) {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(varsObj));
  } catch (e) {
    // Private browsing / storage blocked - theme just won't persist across reloads.
  }
}

function loadThemeOverride() {
  try {
    const raw = localStorage.getItem(THEME_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

function getCurrentThemeVars() {
  const computed = getComputedStyle(document.documentElement);
  const result = {};
  getAllThemeVarNames().forEach(name => {
    result[name] = computed.getPropertyValue(name).trim();
  });
  return result;
}

function initThemeTab() {
  renderThemeTemplateGrid();
  renderThemeCustomizeGroups();

  const resetBtn = document.getElementById("btn-theme-reset");
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      try { localStorage.removeItem(THEME_STORAGE_KEY); } catch (e) {}
      applyThemeVars(THEME_PRESETS.midnight.vars);
      renderThemeTemplateGrid();
      renderThemeCustomizeGroups();
      showToast("Theme reset to Midnight (default).");
    });
  }
}

function initSettingsSidebar() {
  const items = document.querySelectorAll(".settings-sidebar-item");
  items.forEach(item => {
    item.addEventListener("click", () => {
      items.forEach(i => i.classList.remove("active"));
      item.classList.add("active");

      const targetId = item.getAttribute("data-settings-panel");
      document.querySelectorAll(".settings-panel").forEach(panel => {
        panel.classList.remove("active");
      });
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) targetPanel.classList.add("active");
    });
  });
}

function renderThemeTemplateGrid() {
  const grid = document.getElementById("theme-template-grid");
  if (!grid) return;
  const current = getCurrentThemeVars();

  grid.innerHTML = Object.entries(THEME_PRESETS).map(([key, preset]) => {
    const v = preset.vars;
    const isActive = v["--bg-main"] === current["--bg-main"] && v["--accent-primary"] === current["--accent-primary"];
    const swatchKeys = ["--accent-primary", "--accent-green", "--accent-red", "--accent-cyan", "--text-warning"];
    return `
      <div class="theme-template-card ${isActive ? "active" : ""}" data-preset-key="${key}">
        <div class="theme-template-preview">
          <div style="background:${v["--bg-header"]};"></div>
          <div style="background:${v["--bg-main"]};"></div>
          <div style="background:${v["--bg-card"]};"></div>
          <div style="background:${v["--accent-primary"]};"></div>
        </div>
        <div class="theme-template-name">${preset.icon} ${escapeHtml(preset.name)}</div>
        <div class="theme-template-swatches">
          ${swatchKeys.map(k => `<span class="theme-swatch-dot" style="background:${v[k]};"></span>`).join("")}
        </div>
      </div>
    `;
  }).join("");

  grid.querySelectorAll(".theme-template-card").forEach(card => {
    card.addEventListener("click", () => {
      const key = card.getAttribute("data-preset-key");
      const preset = THEME_PRESETS[key];
      if (!preset) return;
      applyThemeVars(preset.vars);
      saveThemeOverride(preset.vars);
      renderThemeTemplateGrid();
      renderThemeCustomizeGroups();
      showToast(`Applied "${preset.name}" theme.`);
    });
  });
}

function renderThemeCustomizeGroups() {
  const container = document.getElementById("theme-customize-groups");
  if (!container) return;
  const current = getCurrentThemeVars();

  container.innerHTML = THEME_VAR_GROUPS.map(group => `
    <div class="theme-color-group">
      <div class="theme-color-group-title">${escapeHtml(group.title)}</div>
      <div class="theme-color-row-list">
        ${group.vars.map(v => `
          <div class="theme-color-row">
            <input type="color" data-var-name="${v.name}" value="${current[v.name] || "#000000"}">
            <div style="flex:1;">
              <div class="theme-color-row-label">${escapeHtml(v.label)}</div>
              <div class="theme-color-row-hex" data-hex-for="${v.name}">${current[v.name] || ""}</div>
            </div>
          </div>
        `).join("")}
      </div>
    </div>
  `).join("");

  container.querySelectorAll('input[type="color"]').forEach(input => {
    input.addEventListener("input", () => {
      const varName = input.getAttribute("data-var-name");
      const value = input.value;
      document.documentElement.style.setProperty(varName, value);
      const hexLabel = container.querySelector(`[data-hex-for="${varName}"]`);
      if (hexLabel) hexLabel.innerText = value;
      saveThemeOverride(getCurrentThemeVars());
      renderThemeTemplateGrid();
    });
  });
}

const SAMPLE_JD_TEXT = `Job Title: Senior Machine Learning & Distributed Systems Engineer
Company: AnthroScale Dynamics
Location: San Francisco, CA (Hybrid / Remote)
Compensation: $170,000 - $210,000 + Equity

About the Role:
We are looking for a Senior Machine Learning & Distributed Systems Engineer to design, deploy, and optimize our next-generation enterprise AI infrastructure. You will work closely with research scientists and infrastructure engineers to build resilient, ultra-low latency inference engines and microservices.

Minimum Qualifications (Must-Have):
- 5+ years of software engineering experience building scalable backend architectures in Python or Go.
- Hands-on experience with containerization and orchestration using Docker and Kubernetes (k8s).
- Deep knowledge of modern deep learning and NLP frameworks: PyTorch, Hugging Face, Transformers, and LangChain.
- Strong proficiency in relational and vector databases: PostgreSQL, Pinecone, or Redis.
- Proven experience designing REST APIs and distributed microservices with FastAPI or gRPC.
- Solid understanding of cloud infrastructure on AWS or GCP.

Preferred Qualifications (Nice-to-Have):
- Experience fine-tuning LLMs, quantizing models (vLLM, TensorRT), and building production RAG pipelines.
- Familiarity with Terraform, Ansible, and Kafka event streaming.
- Strong grounding in system design, TDD, and CI/CD automation.
- Bachelor's or Master's degree in Computer Science or related STEM field.

Key Responsibilities:
- Spearhead the architecture and rollout of high-availability AI inference microservices.
- Optimize GPU utilization and memory bandwidth across distributed Kubernetes clusters.
- Collaborate with product and security teams to ensure data privacy and SOC2 compliance.`;

// Document Ready
document.addEventListener("DOMContentLoaded", async () => {
  initTabs();
  initJobsFound();
  initResumeView();
  initMasterImport();
  initJdCompare();
  initSideBySideMatrix();
  initTailor();
  initMasterResume();
  initResumeLedger();
  initSuggestions();
  initFunnel();
  initSettingsModal();
  initAccordions();
  initThemeTab();
  initSettingsSidebar();

  // Load initial data on launch: Master Resume, Active Session, Ledger, and Funnel
  await loadMasterResume();
  await loadMasterResumeAtsView();
  await loadResumeLedger();
  await loadFunnelData();
});

// Toast Helper
function showToast(message) {
  const toast = document.getElementById("toast");
  toast.innerText = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2600);
}

// ================= TAB NAVIGATION =================
function initTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const targetId = tab.getAttribute("data-tab");
      document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.remove("active");
      });
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");

      if (targetId === "tab-funnel") {
        loadFunnelData();
      } else if (targetId === "tab-master") {
        loadMasterResume();
      } else if (targetId === "tab-resume") {
        loadMasterResumeAtsView();
      } else if (targetId === "tab-ledger") {
        loadResumeLedger();
      } else if (targetId === "tab-tailor") {
        updateTailorContext();
      } else if (targetId === "tab-suggestions") {
        fetchRubricAudit();
      }
    });
  });
}

// ================= ACCORDION (detailed breakdown sections) =================
function initAccordions(scope) {
  (scope || document).querySelectorAll("[data-accordion-toggle]").forEach(header => {
    header.addEventListener("click", () => {
      const item = header.closest("[data-accordion]");
      if (!item) return;
      item.classList.toggle("collapsed");
      const label = header.querySelector(".accordion-toggle-label");
      if (label) {
        const collapsed = item.classList.contains("collapsed");
        label.innerHTML = `<span class="chevron">▾</span> ${collapsed ? "Show details" : "Hide details"}`;
      }
    });
  });
}

function switchToTab(tabId) {
  const tabBtn = document.querySelector(`.nav-tab[data-tab="${tabId}"]`);
  if (tabBtn) tabBtn.click();
}

async function loadMasterResumeAtsView() {
  try {
    const resp = await fetch("/api/master-resume/ats-view");
    if (resp.ok) {
      const data = await resp.json();
      if (data && (data.ats_json?.raw_text || data.raw_text)) {
        currentResumeData = data;
        renderResumeView(data);
        updateTailorContext();
      }
    }
  } catch (e) {
    console.warn("Master Resume ATS view hydration note:", e);
  }
}

// ================= TAB 1: JOBS FOUND & RESUME CREATION =================
function initJobsFound() {
  const jdInput = document.getElementById("found-jd-text");
  const previewBox = document.getElementById("new-resume-name-preview");
  const sampleBtn = document.getElementById("btn-load-sample-jd-found");
  const refreshBtn = document.getElementById("btn-refresh-jobs-found");
  const createBtn = document.getElementById("btn-create-resume-from-jd");
  const statusText = document.getElementById("found-status-text");

  function updatePreview() {
    const raw = jdInput ? jdInput.value.trim() : "";
    const lines = raw.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
    const firstLine = lines[0] || "";
    const clean = firstLine.replace(/^(?:job\s*title|position|role)\s*[:\-]\s*/i, "").trim();
    if (previewBox) {
      previewBox.innerText = clean || firstLine || "[First line of JD will appear here...]";
    }
  }

  if (jdInput) {
    jdInput.addEventListener("input", updatePreview);
    jdInput.addEventListener("paste", () => setTimeout(updatePreview, 50));
  }

  if (sampleBtn) {
    sampleBtn.addEventListener("click", () => {
      if (jdInput) {
        jdInput.value = SAMPLE_JD_TEXT;
        updatePreview();
      }
      const compInput = document.getElementById("found-company");
      if (compInput) compInput.value = "AnthroScale Dynamics";
      const locInput = document.getElementById("found-location");
      if (locInput) locInput.value = "San Francisco, CA";
      const salInput = document.getElementById("found-salary");
      if (salInput) salInput.value = "$170,000 - $210,000";
      showToast("Loaded sample Job Description!");
    });
  }

  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => loadJobsFound());
  }

  if (createBtn) {
    createBtn.addEventListener("click", async () => {
      const jdText = jdInput ? jdInput.value.trim() : "";
      if (!jdText) {
        if (statusText) statusText.innerHTML = `<span style="color:var(--text-danger);">⚠️ Please paste a Job Description first.</span>`;
        return;
      }

      createBtn.disabled = true;
      const origBtnHtml = createBtn.innerHTML;
      createBtn.innerHTML = `<span>⏳ Creating Resume & Matching...</span>`;
      if (statusText) statusText.innerText = "Analyzing JD, adding to Funnel, and matching against Master Resume...";

      const payload = {
        jd_text: jdText,
        company: document.getElementById("found-company") ? document.getElementById("found-company").value.trim() : "",
        location: document.getElementById("found-location") ? document.getElementById("found-location").value.trim() : "",
        salary: document.getElementById("found-salary") ? document.getElementById("found-salary").value.trim() : "",
        job_url: document.getElementById("found-url") ? document.getElementById("found-url").value.trim() : ""
      };

      try {
        const resp = await fetch("/api/jobs/create-resume", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!resp.ok) {
          const err = await resp.json();
          throw new Error(err.detail || "Failed to create resume");
        }

        const data = await resp.json();
        currentJdData = data.jd_parsed;
        currentComparison = data.comparison;

        // Populate Tab 4 (Compare) input so it stays in sync
        const compareJdInput = document.getElementById("jd-text-input");
        if (compareJdInput) compareJdInput.value = jdText;

        // Render match results in Tab 4 & Tab 5
        renderComparisonResults(data);
        renderMatrixTable(data.comparison.side_by_side_matrix);

        // Fetch suggestions in background
        fetchSuggestions();

        // Refresh all lists
        await loadJobsFound();
        await loadResumeLedger();
        await loadFunnelData();

        if (statusText) {
          statusText.innerHTML = `<span style="color:var(--text-success);">✓ Created Resume "${escapeHtml(data.resume_name)}" and added to Funnel!</span>`;
        }
        showToast(`Resume "${data.resume_name}" created & matched! Score: ${data.comparison.match_score}%`);

        // Switch to Compare tab to show results
        switchToTab("tab-compare");
      } catch (err) {
        if (statusText) {
          statusText.innerHTML = `<span style="color:var(--text-danger);">Error: ${escapeHtml(err.message)}</span>`;
        }
      } finally {
        createBtn.disabled = false;
        createBtn.innerHTML = origBtnHtml;
      }
    });
  }
}

async function loadJobsFound() {
  try {
    const resp = await fetch("/api/jobs/found");
    if (!resp.ok) return;
    const data = await resp.json();
    renderJobsFoundList(data.jobs || []);
  } catch (err) {
    console.error("Failed to load jobs found:", err);
  }
}

function renderJobsFoundList(jobs) {
  const container = document.getElementById("jobs-found-list");
  const countBadge = document.getElementById("jobs-found-count");
  if (countBadge) countBadge.innerText = jobs.length;
  if (!container) return;

  container.innerHTML = "";
  if (jobs.length === 0) {
    container.innerHTML = `
      <div style="grid-column:1/-1; text-align:center; padding:40px 20px; color:var(--text-muted); background:var(--bg-stat); border-radius:8px; border:1px dashed var(--border-color);">
        <div style="font-size:32px; margin-bottom:8px;">🎯</div>
        <div style="font-size:14px; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">No Jobs Found yet</div>
        <div style="font-size:12px;">Paste a job description above or click "⚡ Load Sample JD" to create your first resume!</div>
      </div>
    `;
    return;
  }

  jobs.forEach(job => {
    const card = document.createElement("div");
    card.className = "card";
    card.style.margin = "0";
    card.style.padding = "14px";
    card.style.background = "var(--bg-stat)";
    card.style.border = "1px solid var(--border-color)";

    const score = job.match_score ? `${Math.round(job.match_score)}%` : "Pending";
    const scoreClass = job.match_score >= 80 ? "badge-exact" : (job.match_score >= 60 ? "badge-nice" : "badge-partial");
    const dateStr = job.created_at ? job.created_at.substring(0, 10) : "";

    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
        <div style="flex:1; padding-right:10px;">
          <div style="font-size:13px; font-weight:700; color:var(--text-primary); margin-bottom:2px;">
            ${escapeHtml(job.role || 'Target Role')}
          </div>
          <div style="font-size:11px; color:var(--text-info); font-weight:600;">
            🏢 ${escapeHtml(job.company || 'Unnamed Company')}
            ${job.location ? `<span style="color:var(--text-muted); font-weight:normal;"> • ${escapeHtml(job.location)}</span>` : ''}
          </div>
        </div>
        <div>
          <span class="badge ${scoreClass}" style="font-size:11px;">ATS Score: ${score}</span>
        </div>
      </div>
      ${job.salary ? `<div style="font-size:11px; color:var(--text-success); margin-bottom:6px;">💰 ${escapeHtml(job.salary)}</div>` : ''}
      <div style="font-size:10px; color:var(--text-muted); margin-bottom:12px;">
        Added: ${dateStr} • Stage: <strong style="color:var(--accent-indigo);">Jobs Found</strong>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; border-top:1px solid var(--bg-card); padding-top:10px;">
        <div style="display:flex; gap:6px;">
          <button class="btn btn-outline btn-job-compare" style="font-size:11px; padding:4px 8px;">
            ⚖️ View Match
          </button>
          <button class="btn btn-primary btn-job-tailor" style="font-size:11px; padding:4px 10px; background:var(--accent-primary-hover); border:none;">
            🛠️ Tailor Resume
          </button>
        </div>
        <div style="display:flex; gap:6px;">
          <button class="btn btn-outline btn-job-apply" style="font-size:11px; padding:4px 8px; color:var(--text-success);" title="Move to Applied stage in Funnel">
            ➔ Move to Applied
          </button>
          <button class="btn btn-outline btn-job-del" style="font-size:11px; padding:4px 8px; color:var(--text-danger);" title="Delete this Job">
            🗑
          </button>
        </div>
      </div>
    `;

    // Event listeners
    card.querySelector(".btn-job-compare").addEventListener("click", async () => {
      if (job.jd_text) {
        document.getElementById("jd-text-input").value = job.jd_text;
        document.getElementById("btn-compare-jd").click();
        switchToTab("tab-compare");
      }
    });

    card.querySelector(".btn-job-tailor").addEventListener("click", async () => {
      if (job.jd_text) {
        document.getElementById("jd-text-input").value = job.jd_text;
        try {
          const resp = await fetch("/api/resume/compare", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              jd_text: job.jd_text,
              resume_data: currentResumeData || { master_resume: masterResumeData }
            })
          });
          if (resp.ok) {
            const data = await resp.json();
            currentJdData = data.jd_parsed;
            currentComparison = data.comparison;
            renderComparisonResults(data);
            renderMatrixTable(data.comparison.side_by_side_matrix);
          }
        } catch (e) {
          console.error("Comparison load error:", e);
        }
        switchToTab("tab-tailor");
      }
    });

    card.querySelector(".btn-job-apply").addEventListener("click", async () => {
      await updateAppStage(job.id, "Resume Screening");
      await loadJobsFound();
      await loadFunnelData();
    });

    card.querySelector(".btn-job-del").addEventListener("click", async () => {
      if (confirm(`Delete '${job.role}' at '${job.company}' from Jobs Found?`)) {
        await deleteApp(job.id);
        await loadJobsFound();
        await loadFunnelData();
      }
    });

    container.appendChild(card);
  });
}

// ================= TAB 2: DIRECT MASTER RESUME IMPORT =================
function initMasterImport() {
  const dropzone = document.getElementById("master-dropzone");
  const fileInput = document.getElementById("master-file-input");
  const chooseFileBtn = document.getElementById("btn-master-choose-file");
  const statusEl = document.getElementById("master-import-status");
  const filenameEl = document.getElementById("master-selected-filename");

  if (!dropzone || !fileInput) return;

  // Drag and drop handlers
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "var(--text-info)";
  });
  dropzone.addEventListener("dragleave", () => {
    dropzone.style.borderColor = "var(--border-color)";
  });
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "var(--border-color)";
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      fileInput.files = e.dataTransfer.files;
      if (filenameEl) filenameEl.innerText = `📄 ${e.dataTransfer.files[0].name}`;
      handleDirectMasterUpload(e.dataTransfer.files[0]);
    }
  });

  // Native file input change -- selecting a file immediately imports it,
  // there is no separate "Import" step/button.
  fileInput.addEventListener("change", () => {
    if (fileInput.files && fileInput.files.length > 0) {
      const selected = fileInput.files[0];
      if (filenameEl) filenameEl.innerText = `📄 ${selected.name}`;
      handleDirectMasterUpload(selected);
    }
  });

  async function handleDirectMasterUpload(file) {
    if (!file) return;
    if (statusEl) {
      statusEl.style.display = "block";
      statusEl.innerHTML = `<span style="color:var(--text-secondary);">⏳ Uploading and parsing <strong>${file.name}</strong>...</span>`;
    }
    if (chooseFileBtn) {
      chooseFileBtn.style.pointerEvents = "none";
      chooseFileBtn.style.opacity = "0.6";
      chooseFileBtn.innerText = "⏳ Processing...";
    }

    try {
      const formData = new FormData();
      formData.append("file", file);

      const resp = await fetch("/api/resume/parse", {
        method: "POST",
        body: formData
      });
      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Upload failed");
      }
      const data = await resp.json();
      currentResumeData = data;
      renderResumeView(data);
      await loadMasterResume();
      updateTailorContext();

      if (statusEl) {
        statusEl.innerHTML = `<span style="color:var(--text-success);">✅ Successfully imported <strong>${file.name}</strong>! Master Resume & Career Projects updated.</span>`;
      }
      showToast("Master Resume updated from uploaded resume!");
    } catch (err) {
      if (statusEl) {
        statusEl.innerHTML = `<span style="color:var(--text-danger);">❌ Import error: ${err.message}</span>`;
      }
      alert(`Resume import error: ${err.message}`);
    } finally {
      if (chooseFileBtn) {
        chooseFileBtn.style.pointerEvents = "";
        chooseFileBtn.style.opacity = "";
        chooseFileBtn.innerText = "📁 Choose File to Import...";
      }
      fileInput.value = "";
    }
  }
}

// ================= TAB 2: RESUME & ATS JSON INSPECTOR =================
function initResumeView() {
  // Copy & Download JSON
  document.getElementById("btn-copy-json").addEventListener("click", () => {
    const text = document.getElementById("json-viewer").innerText;
    navigator.clipboard.writeText(text);
    showToast("ATS JSON copied to clipboard!");
  });

  document.getElementById("btn-download-json").addEventListener("click", () => {
    const text = document.getElementById("json-viewer").innerText;
    const blob = new Blob([text], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "ATS_Resume.json";
    a.click();
    URL.revokeObjectURL(url);
    showToast("Downloaded ATS_Resume.json");
  });

  const gotoMasterBtn = document.getElementById("btn-goto-master-resume");
  if (gotoMasterBtn) {
    gotoMasterBtn.addEventListener("click", () => {
      switchToTab("tab-master");
    });
  }
}

function renderResumeView(data) {
  const atsJson = data.ats_json;
  const hygiene = data.hygiene_report;

  // Active resume header badge
  const activeBadge = document.getElementById("active-resume-badge");
  const activeName = document.getElementById("active-resume-name");
  activeName.innerText = atsJson.metadata?.source_file || atsJson.contact_information?.name || "Active Resume";
  activeBadge.style.display = "flex";

  // ATS Hygiene score display
  document.getElementById("hygiene-card").style.display = "block";
  document.getElementById("hygiene-score-val").innerText = hygiene.score;
  const gradeBadge = document.getElementById("hygiene-grade-badge");
  gradeBadge.innerText = `Grade: ${hygiene.grade}`;
  gradeBadge.className = hygiene.score >= 80 ? "badge badge-exact" : (hygiene.score >= 60 ? "badge badge-partial" : "badge badge-missing");

  document.getElementById("metric-verbs").innerText = `${hygiene.metrics?.action_verb_percentage || 0}%`;
  document.getElementById("metric-metrics").innerText = `${hygiene.metrics?.quantified_percentage || 0}%`;
  document.getElementById("metric-words").innerText = hygiene.metrics?.total_words || 0;

  // Warnings & Strengths
  const warnBox = document.getElementById("hygiene-warnings");
  warnBox.innerHTML = (hygiene.warnings || []).map(w => `<div style="color:var(--text-danger); font-size:12px; margin-bottom:4px;">⚠️ ${w}</div>`).join("");

  const strBox = document.getElementById("hygiene-strengths");
  strBox.innerHTML = (hygiene.strengths || []).map(s => `<div style="color:var(--text-success); font-size:12px; margin-bottom:4px;">✓ ${s}</div>`).join("");

  // Formatted JSON Viewer
  document.getElementById("json-viewer").innerText = JSON.stringify(atsJson, null, 2);

  // Parsed Profile Card
  document.getElementById("parsed-summary-card").style.display = "block";
  const contact = atsJson.contact_information || {};
  document.getElementById("parsed-contact-box").innerHTML = `
    <div style="font-weight:700; font-size:15px; color:var(--text-primary);">${contact.name || "Candidate"}</div>
    <div style="color:var(--text-secondary); font-size:12px;">${contact.email || ""} ${contact.phone ? "• " + contact.phone : ""} ${contact.location ? "• " + contact.location : ""}</div>
  `;

  const skillsContainer = document.getElementById("parsed-skills-container");
  skillsContainer.innerHTML = "";
  const allSkills = atsJson.skills?.all_keywords || [];
  allSkills.slice(0, 24).forEach(skill => {
    const pill = document.createElement("span");
    pill.className = "badge badge-exact";
    pill.innerText = skill;
    skillsContainer.appendChild(pill);
  });

  // Auto-derived Master Resume notification
  const syncNotice = document.getElementById("master-sync-notice-card");
  const syncText = document.getElementById("master-sync-notice-text");
  if (syncNotice) {
    if (data.master_synced) {
      syncNotice.style.display = "block";
      const pName = data.master_profile_name || (contact.name ? `${contact.name}'s Master Profile` : "Master Profile");
      const pCount = data.master_projects_count !== undefined ? data.master_projects_count : "";
      if (syncText) {
        syncText.innerText = `Extracted candidate profile (${contact.name || 'Candidate'}), skills, experiences, and ${pCount} projects into "${pName}".`;
      }
      loadMasterResume();
    } else {
      syncNotice.style.display = "none";
    }
  }
}

// ================= TAB 3: COMPARE TO JD =================
function initJdCompare() {
  const jdInput = document.getElementById("jd-text-input");
  const sampleBtn = document.getElementById("btn-load-sample-jd");
  const compareBtn = document.getElementById("btn-compare-jd");
  const statusText = document.getElementById("jd-status-text");
  const previewEl = document.getElementById("new-resume-name-preview");

  function updateResumeNamePreview() {
    if (!previewEl || !jdInput) return;
    const lines = jdInput.value.split("\n").map(l => l.trim()).filter(l => l.length > 0);
    if (lines.length > 0) {
      let firstLine = lines[0].replace(/^(?:job\s*title|position|role)\s*[:\-]\s*/i, "").trim() || lines[0];
      previewEl.innerText = `📄 ${firstLine}`;
      previewEl.style.color = "var(--text-info)";
    } else {
      previewEl.innerText = "[First line of JD will automatically become the Resume Name]";
      previewEl.style.color = "var(--text-muted)";
    }
  }

  if (jdInput) {
    jdInput.addEventListener("input", updateResumeNamePreview);
  }

  if (sampleBtn) {
    sampleBtn.addEventListener("click", () => {
      jdInput.value = SAMPLE_JD_TEXT;
      updateResumeNamePreview();
      statusText.innerText = "Loaded sample Job Description.";
    });
  }

  if (compareBtn) {
    compareBtn.addEventListener("click", async () => {
      const jdText = jdInput.value.trim();
      if (!jdText) {
        statusText.innerHTML = `<span style="color:var(--text-danger);">⚠️ Please paste a Job Description or click "⚡ Load Sample JD" above.</span>`;
        return;
      }

      compareBtn.disabled = true;
      compareBtn.innerHTML = `<span>⏳ Comparing...</span>`;
      statusText.innerText = "Deriving resume name from first line of JD, registering in Wishlist, and evaluating ATS match...";

      try {
        const resp = await fetch("/api/jobs/create-resume", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            jd_text: jdText
          })
        });

        if (!resp.ok) {
          const err = await resp.json();
          throw new Error(err.detail || "Comparison and resume creation failed");
        }

        const data = await resp.json();
        currentJdData = data.jd_parsed;
        currentComparison = data.comparison;

        renderComparisonResults(data);
        renderMatrixTable(data.comparison.side_by_side_matrix);
        statusText.innerHTML = `✨ Created Resume: <strong>${escapeHtml(data.resume_name)}</strong> in <strong>Wishlist</strong> (${data.comparison.source || "AI Engine"})`;

        // Refresh Ledger and Funnel
        await loadResumeLedger();
        await loadFunnelData();

        // Automatically fetch suggestions in background
        fetchSuggestions();

        showToast(`✨ Resume "${data.resume_name}" created & added to Wishlist! Score: ${data.comparison.match_score}%`);
      } catch (e) {
        statusText.innerText = `Error: ${e.message}`;
      } finally {
        compareBtn.disabled = false;
        compareBtn.innerHTML = `<span>✨ Compare</span>`;
      }
    });
  }

  // Quick add to funnel button
  const quickAddBtn = document.getElementById("btn-quick-add-funnel");
  if (quickAddBtn) {
    quickAddBtn.addEventListener("click", () => {
      if (!currentComparison || !currentJdData) return;
      openAddAppModal({
        company: currentJdData.company || "Target Company",
        role: currentJdData.role_title || "Target Role",
        score: currentComparison.match_score,
        location: "San Francisco, CA",
        salary: "$170,000 - $210,000"
      });
    });
  }

  // Next-step flow buttons in match results card
  const flowMatrixBtn = document.getElementById("btn-flow-to-matrix");
  if (flowMatrixBtn) {
    flowMatrixBtn.addEventListener("click", () => switchToTab("tab-skills"));
  }
  const flowTailorBtn = document.getElementById("btn-flow-to-tailor");
  if (flowTailorBtn) {
    flowTailorBtn.addEventListener("click", () => switchToTab("tab-tailor"));
  }
  const flowLedgerBtn = document.getElementById("btn-flow-to-ledger");
  if (flowLedgerBtn) {
    flowLedgerBtn.addEventListener("click", () => switchToTab("tab-ledger"));
  }
  const flowFunnelBtn = document.getElementById("btn-flow-to-funnel");
  if (flowFunnelBtn) {
    flowFunnelBtn.addEventListener("click", () => switchToTab("tab-funnel"));
  }
}

function renderComparisonResults(data) {
  const comp = data.comparison;
  const jd = data.jd_parsed;

  document.getElementById("match-empty-state").style.display = "none";
  document.getElementById("match-content-box").style.display = "block";
  document.getElementById("btn-quick-add-funnel").style.display = "inline-flex";

  // Resume Name in status badge
  const createdNameEl = document.getElementById("match-created-resume-name");
  if (createdNameEl) {
    createdNameEl.innerText = data.resume_name || jd.role_title || "New Resume";
  }

  // Also reveal matrix in Tab 4
  const matrixEmpty = document.getElementById("skills-empty-state");
  const matrixContainer = document.getElementById("skills-table-container");
  if (matrixEmpty) matrixEmpty.style.display = "none";
  if (matrixContainer) matrixContainer.style.display = "block";

  // Score Hero: gradient ring (score out of 10) + tier label
  const ringEl = document.getElementById("match-score-ring");
  if (ringEl) ringEl.style.setProperty("--pct", comp.match_score);
  document.getElementById("match-score-val").innerText = (comp.match_score / 10).toFixed(1);
  document.getElementById("match-score-tier").innerText = `${comp.score_tier} — Overall score`;
  document.getElementById("match-role-title").innerText = data.resume_name || jd.role_title;
  document.getElementById("match-company-name").innerText = jd.company;

  renderScoreHeroInsights(comp);

  // Evaluation Source Badge
  const sourceBadge = document.getElementById("matrix-source-badge");
  if (sourceBadge && comp.source) {
    sourceBadge.innerText = `⚡ ${comp.source}`;
    if (comp.source.startsWith("AI")) {
      sourceBadge.className = "badge badge-exact";
    } else {
      sourceBadge.className = "badge badge-nice";
    }
  }

  // Breakdown stats
  document.getElementById("match-must-stat").innerText = comp.summary_counts.must_haves_covered;
  document.getElementById("match-nice-stat").innerText = comp.summary_counts.nice_to_haves_covered;
  document.getElementById("match-exp-stat").innerText = jd.seniority;

  // Missing Keywords
  const missingBox = document.getElementById("missing-keywords-container");
  missingBox.innerHTML = "";
  if (comp.top_missing_keywords && comp.top_missing_keywords.length > 0) {
    comp.top_missing_keywords.forEach(kw => {
      const pill = document.createElement("span");
      pill.className = "badge badge-missing";
      pill.innerText = `+ ${kw}`;
      missingBox.appendChild(pill);
    });
  } else {
    missingBox.innerHTML = `<span style="font-size:12px; color:var(--text-success);">No critical skills missing! Outstanding keyword coverage.</span>`;
  }

  // Candidate Bonus Skills
  const bonusBox = document.getElementById("bonus-skills-container");
  bonusBox.innerHTML = "";
  if (comp.candidate_bonus_skills && comp.candidate_bonus_skills.length > 0) {
    comp.candidate_bonus_skills.forEach(skill => {
      const pill = document.createElement("span");
      pill.className = "badge badge-exact";
      pill.innerText = skill;
      bonusBox.appendChild(pill);
    });
  } else {
    bonusBox.innerHTML = `<span style="font-size:12px; color:var(--text-muted);">None detected.</span>`;
  }
}

// Derives "What's working" / "Issues to fix" bullets from the existing match
// data (no new backend rubric yet — that's a separate future pass).
function renderScoreHeroInsights(comp) {
  const parseCovered = (str) => {
    const m = /^(\d+)\/(\d+)$/.exec(str || "");
    return m ? { have: parseInt(m[1], 10), total: parseInt(m[2], 10) } : null;
  };
  const must = parseCovered(comp.summary_counts && comp.summary_counts.must_haves_covered);
  const nice = parseCovered(comp.summary_counts && comp.summary_counts.nice_to_haves_covered);
  const bonusSkills = comp.candidate_bonus_skills || [];
  const missingKeywords = comp.top_missing_keywords || [];

  // What's working
  const working = [];
  if (must && must.total > 0) {
    working.push(`${must.have}/${must.total} must-have requirements matched.`);
  }
  if (bonusSkills.length > 0) {
    const extra = bonusSkills.slice(0, 3).join(", ");
    working.push(`Additional strengths beyond the JD: ${extra}${bonusSkills.length > 3 ? ", ..." : ""}.`);
  }
  working.push(`${comp.score_tier} — ${comp.match_score}% overall keyword alignment.`);

  const workingBox = document.getElementById("match-whats-working-list");
  if (workingBox) {
    workingBox.innerHTML = working.map(t => `<li>${escapeHtml(t)}</li>`).join("");
  }

  // Issues to fix
  const issues = [];
  if (missingKeywords.length > 0) {
    const top = missingKeywords.slice(0, 3).join(", ");
    issues.push(`Missing ${missingKeywords.length} high-priority keyword${missingKeywords.length === 1 ? "" : "s"}: ${top}${missingKeywords.length > 3 ? ", ..." : ""}.`);
  }
  if (nice && nice.have < nice.total) {
    issues.push(`${nice.have}/${nice.total} nice-to-have skills present — consider adding the rest.`);
  }
  if (comp.match_score < 80) {
    issues.push(`Keyword alignment is ${comp.match_score}% — tailor further to cross 80%.`);
  }

  const issuesTitleEl = document.getElementById("match-issues-title");
  if (issuesTitleEl) {
    issuesTitleEl.innerText = issues.length ? `${issues.length} issue${issues.length === 1 ? "" : "s"} to fix` : "No critical issues";
  }

  const issuesBox = document.getElementById("match-issues-list");
  if (issuesBox) {
    issuesBox.innerHTML = issues.length
      ? issues.map(t => `<li>${escapeHtml(t)}</li>`).join("")
      : `<li>No critical issues detected — great alignment!</li>`;
  }
}

// ================= TAB 4: SIDE-BY-SIDE SKILLS =================
function initSideBySideMatrix() {
  const filterButtons = document.querySelectorAll(".matrix-filter");
  filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      filterButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const filter = btn.getAttribute("data-filter");
      filterMatrixRows(filter);
    });
  });

  const quickSampleBtn = document.getElementById("btn-matrix-quick-sample");
  if (quickSampleBtn) {
    quickSampleBtn.addEventListener("click", () => {
      switchToTab("tab-compare");
      const jdInput = document.getElementById("jd-text-input");
      if (jdInput) jdInput.value = SAMPLE_JD_TEXT;
      const compareBtn = document.getElementById("btn-compare-jd");
      if (compareBtn) compareBtn.click();
    });
  }

  const gotoCompareBtn = document.getElementById("btn-matrix-goto-compare");
  if (gotoCompareBtn) {
    gotoCompareBtn.addEventListener("click", () => switchToTab("tab-compare"));
  }

  const flowTailorBtn = document.getElementById("btn-matrix-flow-to-tailor");
  if (flowTailorBtn) {
    flowTailorBtn.addEventListener("click", () => switchToTab("tab-tailor"));
  }

  const selectAllBtn = document.getElementById("btn-matrix-select-all");
  if (selectAllBtn) {
    selectAllBtn.addEventListener("click", () => {
      document.querySelectorAll("#matrix-table-body .matrix-include-checkbox").forEach(cb => cb.checked = true);
    });
  }
  const clearAllBtn = document.getElementById("btn-matrix-clear-all");
  if (clearAllBtn) {
    clearAllBtn.addEventListener("click", () => {
      document.querySelectorAll("#matrix-table-body .matrix-include-checkbox").forEach(cb => cb.checked = false);
    });
  }
}

function getExcludedMatrixKeywords() {
  return Array.from(document.querySelectorAll("#matrix-table-body .matrix-include-checkbox"))
    .filter(cb => !cb.checked)
    .map(cb => cb.dataset.skill)
    .filter(Boolean);
}

function renderMatrixTable(matrixRows) {
  const tbody = document.getElementById("matrix-table-body");
  tbody.innerHTML = "";

  if (!matrixRows || matrixRows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px; color:var(--text-muted);">No requirements or skills found.</td></tr>`;
    return;
  }

  matrixRows.forEach(row => {
    const tr = document.createElement("tr");
    tr.setAttribute("data-status", row.status);
    tr.setAttribute("data-priority", row.priority);

    const statusBadge = row.status === "Exact Match" 
      ? `<span class="badge badge-exact">✅ Exact Match</span>`
      : (row.status === "Partial Match" 
          ? `<span class="badge badge-partial">⚠️ Partial Match</span>`
          : `<span class="badge badge-missing">❌ Missing</span>`);

    const priorityBadge = row.priority === "Must-Have"
      ? `<span class="badge badge-must">Must-Have</span>`
      : `<span class="badge badge-nice">Nice-to-Have</span>`;

    // Format How to Incorporate column
    let incorporateHtml = `<div style="font-size:11px; color:var(--text-secondary); margin-bottom:4px;">${row.advice || ""}</div>`;
    if (row.suggested_bullet) {
      incorporateHtml += `
        <div style="background:var(--bg-stat); border-left:3px solid var(--accent-primary); border-radius:4px; padding:6px 8px; margin-top:4px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
            <span style="font-size:10px; color:var(--accent-indigo); font-weight:700;">GOOGLE XYZ BULLET:</span>
            <button class="btn btn-outline btn-copy-matrix-bullet" style="font-size:9px; padding:1px 5px;" title="Copy this bullet point">📋 Copy Bullet</button>
          </div>
          <div class="matrix-bullet-text" style="font-size:11px; color:var(--text-secondary); line-height:1.3;">${row.suggested_bullet}</div>
        </div>
      `;
    }

    tr.innerHTML = `
      <td style="text-align:center;">
        <input type="checkbox" class="matrix-include-checkbox" checked data-skill="${escapeHtml(row.skill)}" title="Include this keyword when generating a tailored resume in Tab 5">
      </td>
      <td>
        <strong style="color:var(--text-primary); display:block; line-height:1.3; font-size:12px;">${row.skill}</strong>
        <span style="font-size:10px; color:var(--text-info); display:inline-block; margin-top:2px;">[${row.category || "General"}]</span>
      </td>
      <td>${priorityBadge}</td>
      <td>${statusBadge}</td>
      <td style="color:var(--text-secondary); font-size:11px; line-height:1.3;">${row.resume_context || "Not detected in resume"}</td>
      <td>${incorporateHtml}</td>
    `;

    // Bullet copy handler
    const copyBulletBtn = tr.querySelector(".btn-copy-matrix-bullet");
    if (copyBulletBtn) {
      copyBulletBtn.addEventListener("click", () => {
        const bulletText = tr.querySelector(".matrix-bullet-text").innerText;
        navigator.clipboard.writeText(bulletText);
        showToast("Ready-to-use resume bullet copied!");
      });
    }

    tbody.appendChild(tr);
  });
}

function filterMatrixRows(filter) {
  const rows = document.querySelectorAll("#matrix-table-body tr");
  rows.forEach(tr => {
    if (filter === "all") {
      tr.style.display = "";
    } else if (filter === "Must-Have") {
      const priority = tr.getAttribute("data-priority");
      tr.style.display = (priority === "Must-Have") ? "" : "none";
    } else {
      const status = tr.getAttribute("data-status");
      tr.style.display = (status === filter) ? "" : "none";
    }
  });
}

// ================= TAB 7: RESUME QUALITY RUBRIC (7-category score) =================
let currentRubricAudit = null;

async function fetchRubricAudit() {
  if (!masterResumeData && !currentResumeData) return;
  const box = document.getElementById("rubric-breakdown-container");
  if (box && !currentRubricAudit) {
    box.innerHTML = `<div style="color:var(--text-muted); font-size:13px; text-align:center; padding:20px;">Scoring your resume...</div>`;
  }

  try {
    const resp = await fetch("/api/resume/audit-rubric", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_data: currentResumeData || null })
    });
    if (!resp.ok) return;

    const data = await resp.json();
    currentRubricAudit = data;
    renderRubricAudit(data);
  } catch (e) {
    console.error("Rubric audit fetch error:", e);
  }
}

function scoreTierLabel(score) {
  if (score >= 8.5) return "Excellent";
  if (score >= 7) return "Good";
  if (score >= 5.5) return "Fair";
  return "Needs Work";
}

function renderRubricAudit(data) {
  const overall = data.overall_score || 0;
  const categories = data.categories || [];

  const ringEl = document.getElementById("rubric-score-ring");
  if (ringEl) ringEl.style.setProperty("--pct", overall * 10);
  const valEl = document.getElementById("rubric-score-val");
  if (valEl) valEl.innerText = overall.toFixed(1);
  const tierEl = document.getElementById("rubric-score-tier");
  if (tierEl) tierEl.innerText = `${scoreTierLabel(overall)} — Overall score`;

  // Aggregate top strengths (from highest-scoring categories) and top issues
  // (from lowest-scoring categories) into the hero summary cards.
  const sortedByScore = [...categories].sort((a, b) => b.score - a.score);
  const working = sortedByScore.slice(0, 2).flatMap(c => (c.strengths || []).slice(0, 2));
  const lowestFirst = [...categories].sort((a, b) => a.score - b.score);
  const issues = lowestFirst.slice(0, 3).flatMap(c => (c.improvements || []).slice(0, 1));

  const workingBox = document.getElementById("rubric-whats-working-list");
  if (workingBox) {
    workingBox.innerHTML = working.length
      ? working.map(t => `<li>${escapeHtml(t)}</li>`).join("")
      : `<li>No standout strengths detected yet.</li>`;
  }
  const issuesTitleEl = document.getElementById("rubric-issues-title");
  if (issuesTitleEl) {
    issuesTitleEl.innerText = issues.length ? `${issues.length} issue${issues.length === 1 ? "" : "s"} to fix` : "No critical issues";
  }
  const issuesBox = document.getElementById("rubric-issues-list");
  if (issuesBox) {
    issuesBox.innerHTML = issues.length
      ? issues.map(t => `<li>${escapeHtml(t)}</li>`).join("")
      : `<li>No critical issues detected — great work!</li>`;
  }

  // Detailed per-category accordion
  const container = document.getElementById("rubric-breakdown-container");
  if (!container) return;

  container.innerHTML = categories.map((cat, idx) => `
    <div class="accordion-item" data-accordion>
      <div class="accordion-header" data-accordion-toggle>
        <div class="accordion-header-text">
          <div class="accordion-title">${escapeHtml(cat.name)}</div>
          <div class="accordion-subtitle">${escapeHtml(cat.description)}</div>
        </div>
        <div style="display:flex; align-items:center; gap:14px; flex-shrink:0;">
          <span style="font-size:15px; font-weight:800; color:var(--text-primary);">${cat.score} <span style="font-size:11px; font-weight:600; color:var(--text-muted);">/10</span></span>
          <span class="accordion-toggle-label"><span class="chevron">▾</span> Hide details</span>
        </div>
      </div>
      <div class="accordion-body">
        <div class="score-insight-card flat" style="margin-bottom:10px;">
          <div class="score-insight-title working"><span>✅</span><span>Strengths</span></div>
          <ul class="score-insight-list">
            ${(cat.strengths || []).map(s => `<li>${escapeHtml(s)}</li>`).join("")}
          </ul>
        </div>
        <div class="score-insight-card flat">
          <div class="score-insight-title issues"><span>⚠️</span><span>Areas for Improvement</span></div>
          <ul class="score-insight-list">
            ${(cat.improvements || []).map(s => `<li>${escapeHtml(s)}</li>`).join("")}
          </ul>
        </div>
      </div>
    </div>
  `).join("");

  initAccordions(container);
}

// ================= TAB 7: RESUME SUGGESTIONS & AUDIT =================
async function fetchSuggestions() {
  if ((!currentResumeData && !masterResumeData) || !currentJdData || !currentComparison) return;

  try {
    const resp = await fetch("/api/resume/suggest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_data: currentResumeData || { master_resume: masterResumeData },
        jd_data: currentJdData,
        comparison: currentComparison
      })
    });
    if (!resp.ok) return;

    const data = await resp.json();
    currentSuggestions = data;
    renderSuggestions(data);
  } catch (e) {
    console.error("Suggestions fetch error:", e);
  }
}

function initSuggestions() {
  document.getElementById("btn-copy-summary").addEventListener("click", () => {
    const text = document.getElementById("summary-recommended-text").innerText;
    navigator.clipboard.writeText(text);
    showToast("Tailored summary copied to clipboard!");
  });
}

function renderSuggestions(sugg) {
  // Summary
  document.getElementById("summary-current-text").innerText = sugg.summary?.current || "N/A";
  document.getElementById("summary-recommended-text").innerText = sugg.summary?.recommended || "N/A";
  document.getElementById("summary-rationale-text").innerText = sugg.summary?.rationale || "";

  // Work Experience Bullets
  const expContainer = document.getElementById("experience-suggestions-container");
  expContainer.innerHTML = "";

  if (sugg.experience && sugg.experience.length > 0) {
    sugg.experience.forEach(role => {
      const roleBlock = document.createElement("div");
      roleBlock.style.marginBottom = "18px";
      roleBlock.innerHTML = `
        <div style="font-size:13px; font-weight:700; color:var(--accent-indigo); margin-bottom:8px;">
          🏢 ${role.title} at ${role.company}
        </div>
      `;

      role.bullets.forEach((b, idx) => {
        const bulletCard = document.createElement("div");
        bulletCard.className = "card";
        bulletCard.style.padding = "12px";
        bulletCard.style.marginBottom = "8px";
        bulletCard.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted);">BULLET #${idx + 1}</span>
            <button class="btn btn-outline btn-copy-bullet" style="font-size:10px; padding:3px 7px;">📋 Copy Rewritten</button>
          </div>
          <div style="font-size:12px; color:var(--text-secondary); margin-bottom:6px;">
            <strong style="color:var(--text-danger);">Original:</strong> ${b.original}
          </div>
          <div style="font-size:12px; color:var(--text-secondary); font-weight:500; margin-bottom:6px;" class="suggested-bullet-text">
            <strong style="color:var(--text-success);">Google XYZ Rewritten:</strong> ${b.suggested}
          </div>
          <div style="font-size:11px; color:var(--accent-yellow);">
            💡 <em>${b.critique}</em>
          </div>
        `;

        bulletCard.querySelector(".btn-copy-bullet").addEventListener("click", () => {
          const txt = bulletCard.querySelector(".suggested-bullet-text").innerText.replace("Google XYZ Rewritten: ", "");
          navigator.clipboard.writeText(txt);
          showToast("Rewritten bullet copied!");
        });

        roleBlock.appendChild(bulletCard);
      });

      expContainer.appendChild(roleBlock);
    });
  }

  // Skills suggestions
  const skillsBox = document.getElementById("skills-suggestion-content");
  if (sugg.skills) {
    skillsBox.innerHTML = `
      <div style="margin-bottom:10px;">${sugg.skills.recommendation}</div>
      <div style="margin-bottom:8px; font-weight:700; color:var(--text-primary);">Prioritized Skills for this Opening:</div>
      <div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:12px;">
        ${(sugg.skills.priority_skills_to_feature || []).map(s => `<span class="badge badge-exact">${s}</span>`).join("")}
      </div>
      <div style="margin-bottom:8px; font-weight:700; color:var(--text-danger);">Missing Keywords to Add:</div>
      <div style="display:flex; flex-wrap:wrap; gap:6px;">
        ${(sugg.skills.missing_keywords_to_add || []).map(k => `<span class="badge badge-missing">+ ${k}</span>`).join("")}
      </div>
    `;
  }
}

// ================= APPLICATION FUNNEL =================
const FUNNEL_STAGES = [
  "Wishlist",
  "Resume Screening",
  "Recruiter Screening",
  "Interview",
  "Offer",
  "Rejected"
];

const STAGE_ICONS = {
  "Wishlist": "⭐",
  "Resume Screening": "📄",
  "Recruiter Screening": "📞",
  "Interview": "👥",
  "Offer": "🎉",
  "Rejected": "❌"
};

let activeInterviewApp = null;
let activeRejectApp = null;

function initFunnel() {
  const modal = document.getElementById("add-app-modal");
  document.getElementById("btn-open-add-modal").addEventListener("click", () => openAddAppModal());
  document.getElementById("btn-close-modal").addEventListener("click", () => modal.classList.remove("active"));
  document.getElementById("btn-cancel-modal").addEventListener("click", () => modal.classList.remove("active"));

  const createFromJdFunnelBtn = document.getElementById("btn-funnel-create-from-jd");
  if (createFromJdFunnelBtn) {
    createFromJdFunnelBtn.addEventListener("click", () => switchToTab("tab-compare"));
  }

  // Toggle interview step field when stage changes in add modal
  const stageSelect = document.getElementById("form-stage");
  const stepGroup = document.getElementById("form-interview-step-group");
  if (stageSelect && stepGroup) {
    stageSelect.addEventListener("change", () => {
      stepGroup.style.display = stageSelect.value === "Interview" ? "block" : "none";
    });
  }

  document.getElementById("add-app-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const stageVal = document.getElementById("form-stage").value;
    const stepVal = document.getElementById("form-interview-step") ? document.getElementById("form-interview-step").value.trim() : "";
    const payload = {
      company: document.getElementById("form-company").value,
      role: document.getElementById("form-role").value,
      stage: stageVal,
      match_score: parseFloat(document.getElementById("form-score").value) || 0.0,
      location: document.getElementById("form-location").value,
      salary: document.getElementById("form-salary").value,
      job_url: document.getElementById("form-url").value,
      notes: document.getElementById("form-notes").value,
      interview_step: stageVal === "Interview" ? (stepVal || "Round 1: Technical Screen") : ""
    };

    try {
      const resp = await fetch("/api/funnel", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!resp.ok) throw new Error("Failed to save application");
      modal.classList.remove("active");
      showToast(`Job Application added to ${stageVal}!`);
      loadFunnelData();
    } catch (err) {
      alert(err.message);
    }
  });

  initInterviewModal();
  initRejectModal();
  loadFunnelData();
}

function initInterviewModal() {
  const modal = document.getElementById("interview-step-modal");
  if (!modal) return;

  document.getElementById("btn-close-interview-modal")?.addEventListener("click", () => modal.classList.remove("active"));

  // Quick preset chips
  modal.querySelectorAll(".btn-quick-step").forEach(btn => {
    btn.addEventListener("click", () => {
      const stepInput = document.getElementById("interview-modal-step-input");
      if (stepInput) stepInput.value = btn.getAttribute("data-step");
    });
  });

  // Advance to next interview round
  document.getElementById("btn-interview-advance-step")?.addEventListener("click", async () => {
    if (!activeInterviewApp) return;
    const nextStep = document.getElementById("interview-modal-step-input").value.trim() || "Next Interview Round";
    await updateAppStage(activeInterviewApp.id, "Interview", "", nextStep);
    modal.classList.remove("active");
    showToast(`✓ Advanced to: ${nextStep}`);
  });

  // Rename current interview step
  document.getElementById("btn-interview-save-name")?.addEventListener("click", async () => {
    if (!activeInterviewApp) return;
    const stepName = document.getElementById("interview-modal-step-input").value.trim();
    if (!stepName) return;
    try {
      const resp = await fetch(`/api/funnel/${activeInterviewApp.id}/interview-step`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ interview_step: stepName })
      });
      if (resp.ok) {
        modal.classList.remove("active");
        showToast(`Interview step updated to "${stepName}"`);
        loadFunnelData();
      }
    } catch (e) {
      console.error("Error renaming interview step:", e);
    }
  });

  // Pass all rounds to Offer
  document.getElementById("btn-interview-pass-offer")?.addEventListener("click", async () => {
    if (!activeInterviewApp) return;
    await updateAppStage(activeInterviewApp.id, "Offer");
    modal.classList.remove("active");
    showToast(`🏆 Congratulations! Passed all interview rounds to Offer!`);
  });
}

function openInterviewModal(app) {
  activeInterviewApp = app;
  const modal = document.getElementById("interview-step-modal");
  if (!modal) return;

  document.getElementById("interview-modal-company").innerText = `${app.role} at ${app.company}`;
  const curStep = app.interview_step || "Round 1: Technical Screen";
  document.getElementById("interview-modal-current-step").innerText = curStep;

  const stepInput = document.getElementById("interview-modal-step-input");
  // Pre-fill smart suggestion for next round
  if (curStep.toLowerCase().includes("round 1") || curStep.toLowerCase().includes("screen")) {
    stepInput.value = "Round 2: System Design & Architecture";
  } else if (curStep.toLowerCase().includes("round 2") || curStep.toLowerCase().includes("coding") || curStep.toLowerCase().includes("design")) {
    stepInput.value = "Round 3: Hiring Manager & Culture";
  } else if (curStep.toLowerCase().includes("round 3") || curStep.toLowerCase().includes("manager")) {
    stepInput.value = "Round 4: Bar Raiser & Leadership";
  } else {
    stepInput.value = "Next Interview Round";
  }

  modal.classList.add("active");
}

function initRejectModal() {
  const modal = document.getElementById("reject-modal");
  if (!modal) return;

  document.getElementById("btn-close-reject-modal")?.addEventListener("click", () => modal.classList.remove("active"));
  document.getElementById("btn-cancel-reject-modal")?.addEventListener("click", () => modal.classList.remove("active"));

  document.getElementById("btn-confirm-reject")?.addEventListener("click", async () => {
    if (!activeRejectApp) return;
    const stageDisplay = document.getElementById("reject-modal-stage-display").innerText;
    const notes = document.getElementById("reject-modal-notes-input").value.trim();

    await updateAppStage(activeRejectApp.id, "Rejected", stageDisplay, "", notes);
    modal.classList.remove("active");
  });
}

function openRejectModal(app, currentStage) {
  activeRejectApp = app;
  const modal = document.getElementById("reject-modal");
  if (!modal) return;

  document.getElementById("reject-modal-company").innerText = `${app.role} at ${app.company}`;
  const stageDetail = (currentStage === "Interview" && app.interview_step) 
    ? `Interview (${app.interview_step})` 
    : currentStage;

  document.getElementById("reject-modal-stage-display").innerText = stageDetail;
  document.getElementById("reject-modal-notes-input").value = "";
  modal.classList.add("active");
}

function openAddAppModal(prefill = {}) {
  const modal = document.getElementById("add-app-modal");
  document.getElementById("form-company").value = prefill.company || "";
  document.getElementById("form-role").value = prefill.role || "";
  document.getElementById("form-score").value = prefill.score !== undefined ? prefill.score : "";
  document.getElementById("form-location").value = prefill.location || "";
  document.getElementById("form-salary").value = prefill.salary || "";
  document.getElementById("form-url").value = prefill.url || "";
  document.getElementById("form-notes").value = prefill.notes || "";

  const stageSelect = document.getElementById("form-stage");
  const stepGroup = document.getElementById("form-interview-step-group");
  const stepInput = document.getElementById("form-interview-step");

  stageSelect.value = prefill.stage || "Wishlist";
  if (stepGroup && stepInput) {
    stepGroup.style.display = stageSelect.value === "Interview" ? "block" : "none";
    stepInput.value = prefill.interview_step || "Round 1: Technical Screen";
  }

  modal.classList.add("active");
}

async function loadFunnelData() {
  try {
    const resp = await fetch("/api/funnel");
    if (!resp.ok) return;
    const data = await resp.json();
    currentFunnelApps = data.applications || [];
    renderFunnelStats(data.stats);
    renderKanbanBoard(data.applications || []);
  } catch (e) {
    console.error("Error loading funnel:", e);
  }
}

function renderFunnelStats(stats) {
  if (!stats) return;
  document.getElementById("funnel-stat-total").innerText = stats.total_tracked || 0;
  
  const inPipeline = (stats.stage_counts?.Wishlist || 0) +
                     (stats.stage_counts?.["Resume Screening"] || 0) + 
                     (stats.stage_counts?.["Recruiter Screening"] || 0) + 
                     (stats.stage_counts?.Interview || 0);
  document.getElementById("funnel-stat-pipeline").innerText = inPipeline;
  document.getElementById("funnel-stat-interview-rate").innerText = `${stats.conversion_rates?.recruiter_to_interview || 0}%`;
  document.getElementById("funnel-stat-offer-rate").innerText = `${stats.conversion_rates?.overall_offer_rate || 0}%`;
}

function renderKanbanBoard(apps) {
  const board = document.getElementById("kanban-board");
  board.innerHTML = "";

  FUNNEL_STAGES.forEach(stage => {
    const col = document.createElement("div");
    col.className = "kanban-col";

    const colApps = apps.filter(a => a.stage === stage);
    const colId = `kanban-col-${stage.replace(/\s+/g, '-')}`;
    const icon = STAGE_ICONS[stage] || "📌";

    col.innerHTML = `
      <div class="kanban-col-header">
        <span>${icon} ${stage}</span>
        <span class="badge badge-nice">${colApps.length}</span>
      </div>
      <div class="kanban-cards-container" id="${colId}"></div>
    `;

    const container = col.querySelector(`#${colId}`);
    colApps.forEach(app => {
      const card = document.createElement("div");
      card.className = "app-card";

      const scoreBadge = app.match_score 
        ? `<span class="badge ${app.match_score >= 75 ? 'badge-exact' : 'badge-partial'}">${app.match_score}% Match</span>` 
        : "";

      // Stage-specific content blocks
      let stageDetailBlock = "";
      if (stage === "Interview") {
        stageDetailBlock = `
          <div style="display:flex; align-items:center; justify-content:space-between; background:rgba(99,102,241,0.15); border:1px solid var(--accent-primary); border-radius:4px; padding:3px 6px; margin:6px 0; font-size:11px; color:var(--accent-indigo-soft);">
            <span>🎯 <strong>${escapeHtml(app.interview_step || 'Round 1: Technical Screen')}</strong></span>
            <button class="btn btn-outline btn-manage-round" style="padding:1px 5px; font-size:9px;" title="Manage / Advance Rounds">✏️</button>
          </div>
        `;
      } else if (stage === "Rejected") {
        stageDetailBlock = `
          <div style="background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.3); border-radius:4px; padding:3px 6px; margin:6px 0; font-size:10px; color:var(--text-danger);">
            <span>❌ Rejected at: <strong>${escapeHtml(app.rejected_from_stage || 'Application')}</strong></span>
          </div>
        `;
      } else if (stage === "Offer") {
        stageDetailBlock = `
          <div style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3); border-radius:4px; padding:3px 6px; margin:6px 0; font-size:10px; color:var(--text-success); font-weight:700;">
            <span>🎉 Offer Extended!</span>
          </div>
        `;
      }

      // Stage action buttons: Pass (Success in previous step) / Reject at each step / Delete
      let actionButtons = "";
      if (stage === "Wishlist") {
        actionButtons = `
          <button class="btn btn-primary btn-pass-step" style="padding:2px 7px; font-size:10px; background:var(--accent-primary-hover); border:none;" title="Pass to Resume Screening">✓ Pass ➔</button>
          <button class="btn btn-outline btn-reject-step" style="padding:2px 6px; font-size:10px; color:var(--text-danger);" title="Reject">✕</button>
          <button class="btn btn-outline btn-del-app" style="padding:2px 6px; font-size:10px; color:var(--accent-red);" title="Delete">🗑</button>
        `;
      } else if (stage === "Resume Screening") {
        actionButtons = `
          <button class="btn btn-primary btn-pass-step" style="padding:2px 7px; font-size:10px; background:var(--accent-primary-hover); border:none;" title="Pass to Recruiter Screening">✓ Pass ➔</button>
          <button class="btn btn-outline btn-reject-step" style="padding:2px 6px; font-size:10px; color:var(--text-danger);" title="Reject at Resume Screen">✕</button>
          <button class="btn btn-outline btn-del-app" style="padding:2px 6px; font-size:10px; color:var(--accent-red);" title="Delete">🗑</button>
        `;
      } else if (stage === "Recruiter Screening") {
        actionButtons = `
          <button class="btn btn-primary btn-pass-step" style="padding:2px 7px; font-size:10px; background:var(--accent-primary-hover); border:none;" title="Pass to Interview">✓ Pass ➔</button>
          <button class="btn btn-outline btn-reject-step" style="padding:2px 6px; font-size:10px; color:var(--text-danger);" title="Reject at Recruiter Screen">✕</button>
          <button class="btn btn-outline btn-del-app" style="padding:2px 6px; font-size:10px; color:var(--accent-red);" title="Delete">🗑</button>
        `;
      } else if (stage === "Interview") {
        actionButtons = `
          <button class="btn btn-primary btn-interview-pass" style="padding:2px 7px; font-size:10px; background:var(--accent-primary-hover); border:none;" title="Pass Current Round">✓ Pass Round ➔</button>
          <button class="btn btn-success btn-interview-offer" style="padding:2px 6px; font-size:10px;" title="Pass All ➔ Offer">🏆 Offer</button>
          <button class="btn btn-outline btn-reject-step" style="padding:2px 6px; font-size:10px; color:var(--text-danger);" title="Reject at this Round">✕</button>
          <button class="btn btn-outline btn-del-app" style="padding:2px 6px; font-size:10px; color:var(--accent-red);" title="Delete">🗑</button>
        `;
      } else if (stage === "Offer") {
        actionButtons = `
          <button class="btn btn-outline btn-reject-step" style="padding:2px 6px; font-size:10px; color:var(--text-danger);" title="Decline / Reject Offer">✕ Decline</button>
          <button class="btn btn-outline btn-del-app" style="padding:2px 6px; font-size:10px; color:var(--accent-red);" title="Delete">🗑</button>
        `;
      } else if (stage === "Rejected") {
        actionButtons = `
          <button class="btn btn-outline btn-restore-step" style="padding:2px 7px; font-size:10px; color:var(--text-info);" title="Restore to Pipeline">↺ Restore</button>
          <button class="btn btn-outline btn-del-app" style="padding:2px 6px; font-size:10px; color:var(--accent-red);" title="Delete">🗑</button>
        `;
      }

      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div class="app-card-company">${escapeHtml(app.company)}</div>
          ${scoreBadge}
        </div>
        <div class="app-card-role">${escapeHtml(app.role)}</div>
        ${app.salary ? `<div style="font-size:11px; color:var(--text-info); margin-bottom:4px;">💰 ${escapeHtml(app.salary)}</div>` : ""}
        ${app.location ? `<div style="font-size:11px; color:var(--text-muted); margin-bottom:4px;">📍 ${escapeHtml(app.location)}</div>` : ""}
        ${stageDetailBlock}
        <div class="app-card-meta" style="margin-top:6px;">
          <span>${app.date_applied ? '📅 ' + app.date_applied : 'Created: ' + app.created_at.slice(0, 10)}</span>
          <div style="display:flex; gap:4px; align-items:center;">
            ${actionButtons}
          </div>
        </div>
      `;

      // Pass / Advance button
      const passBtn = card.querySelector(".btn-pass-step");
      if (passBtn) {
        passBtn.addEventListener("click", async (e) => {
          e.stopPropagation();
          if (stage === "Wishlist") {
            await updateAppStage(app.id, "Resume Screening");
          } else if (stage === "Resume Screening") {
            await updateAppStage(app.id, "Recruiter Screening");
          } else if (stage === "Recruiter Screening") {
            await updateAppStage(app.id, "Interview", "", "Round 1: Technical Screen");
          }
        });
      }

      // Interview Round Pass & Manage
      const interviewPassBtn = card.querySelector(".btn-interview-pass");
      if (interviewPassBtn) {
        interviewPassBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          openInterviewModal(app);
        });
      }
      const manageRoundBtn = card.querySelector(".btn-manage-round");
      if (manageRoundBtn) {
        manageRoundBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          openInterviewModal(app);
        });
      }

      // Interview direct pass to Offer
      const interviewOfferBtn = card.querySelector(".btn-interview-offer");
      if (interviewOfferBtn) {
        interviewOfferBtn.addEventListener("click", async (e) => {
          e.stopPropagation();
          if (confirm(`Pass all rounds and move '${app.company}' to Offer?`)) {
            await updateAppStage(app.id, "Offer");
          }
        });
      }

      // Reject button (at each step)
      const rejectBtn = card.querySelector(".btn-reject-step");
      if (rejectBtn) {
        rejectBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          openRejectModal(app, stage);
        });
      }

      // Restore button (from Rejected)
      const restoreBtn = card.querySelector(".btn-restore-step");
      if (restoreBtn) {
        restoreBtn.addEventListener("click", async (e) => {
          e.stopPropagation();
          let target = (app.rejected_from_stage || "Wishlist").split(" (")[0];
          if (!FUNNEL_STAGES.includes(target) || target === "Rejected") {
            target = "Wishlist";
          }
          await updateAppStage(app.id, target);
        });
      }

      // Delete app button
      const delBtn = card.querySelector(".btn-del-app");
      if (delBtn) {
        delBtn.addEventListener("click", async (e) => {
          e.stopPropagation();
          if (confirm(`Permanently delete application for ${app.company} (${app.role})?`)) {
            await deleteApp(app.id);
          }
        });
      }

      container.appendChild(card);
    });

    board.appendChild(col);
  });
}

async function updateAppStage(appId, newStage, rejectedFromStage = "", interviewStep = "", notes = "") {
  try {
    const payload = { stage: newStage };
    if (rejectedFromStage) payload.rejected_from_stage = rejectedFromStage;
    if (interviewStep) payload.interview_step = interviewStep;
    if (notes) payload.notes = notes;

    const resp = await fetch(`/api/funnel/${appId}/stage`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (resp.ok) {
      if (newStage === "Rejected") {
        showToast(`Application marked as Rejected (from ${rejectedFromStage || 'Pipeline'})`);
      } else {
        showToast(`Application moved to ${newStage}!`);
      }
      loadFunnelData();
    }
  } catch (e) {
    console.error("Error updating stage:", e);
  }
}

async function deleteApp(appId) {
  try {
    const resp = await fetch(`/api/funnel/${appId}`, {
      method: "DELETE"
    });
    if (resp.ok) {
      showToast("Application removed.");
      loadFunnelData();
    }
  } catch (e) {
    console.error("Error deleting application:", e);
  }
}

// ================= SETTINGS & AI PROVIDER MANAGER =================
const PROVIDER_PRESETS = {
  openai: {
    name: "OpenAI Official",
    url: "https://api.openai.com/v1",
    model: "gpt-4o-mini"
  },
  openrouter: {
    name: "OpenRouter",
    url: "https://openrouter.ai/api/v1",
    model: "meta-llama/llama-3.3-70b-instruct"
  },
  groq: {
    name: "Groq Fast",
    url: "https://api.groq.com/openai/v1",
    model: "llama-3.3-70b-versatile"
  },
  deepseek: {
    name: "DeepSeek",
    url: "https://api.deepseek.com/v1",
    model: "deepseek-chat"
  },
  ollama: {
    name: "Local Ollama",
    url: "http://localhost:11434/v1",
    model: "llama3"
  }
};

function initSettingsModal() {
  const modal = document.getElementById("settings-modal");
  const openBtn = document.getElementById("btn-goto-settings");
  const closeBtn = document.getElementById("btn-close-settings-modal");
  const badge = document.getElementById("active-provider-badge");
  const presetSelect = document.getElementById("setting-preset-select");
  const testBtn = document.getElementById("btn-test-connection");
  const testResultBox = document.getElementById("test-connection-result");
  const form = document.getElementById("provider-form");
  const clearBtn = document.getElementById("btn-clear-provider-form");
  const offlineBtn = document.getElementById("btn-use-offline-engine");
  const toggleKeyBtn = document.getElementById("btn-toggle-key-visibility");
  const keyInput = document.getElementById("setting-key");

  // Open & Close Settings modal
  const openSettings = () => {
    modal.classList.add("active");
    loadSavedProviders();
  };
  openBtn.addEventListener("click", openSettings);
  badge.addEventListener("click", openSettings);
  closeBtn.addEventListener("click", () => modal.classList.remove("active"));

  // Toggle API key visibility
  toggleKeyBtn.addEventListener("click", () => {
    if (keyInput.type === "password") {
      keyInput.type = "text";
      toggleKeyBtn.innerText = "🙈 Hide Key";
    } else {
      keyInput.type = "password";
      toggleKeyBtn.innerText = "👁️ Show Key";
    }
  });

  // Presets Auto-fill
  presetSelect.addEventListener("change", () => {
    const val = presetSelect.value;
    if (PROVIDER_PRESETS[val]) {
      const p = PROVIDER_PRESETS[val];
      document.getElementById("setting-name").value = p.name;
      document.getElementById("setting-url").value = p.url;
      document.getElementById("setting-model").value = p.model;
      testResultBox.style.display = "none";
    }
  });

  // Reset / Clear Form Helper
  function resetProviderForm() {
    document.getElementById("setting-provider-id").value = "";
    document.getElementById("setting-name").value = "";
    document.getElementById("setting-url").value = "";
    document.getElementById("setting-model").value = "";
    keyInput.value = "";
    presetSelect.value = "custom";
    testResultBox.style.display = "none";
    const editInd = document.getElementById("editing-indicator");
    if (editInd) editInd.style.display = "none";
    const btnText = document.getElementById("btn-save-provider-text");
    if (btnText) btnText.innerText = "💾 Save to Database";
  }

  // Clear Form Button
  clearBtn.addEventListener("click", resetProviderForm);

  // Test Connection
  testBtn.addEventListener("click", async () => {
    const baseUrl = document.getElementById("setting-url").value.trim();
    const apiKey = keyInput.value.trim();
    const modelName = document.getElementById("setting-model").value.trim();

    if (!baseUrl || !modelName) {
      alert("Please specify Base URL and Model Name to test connection.");
      return;
    }

    testResultBox.style.display = "block";
    testResultBox.style.background = "var(--bg-card)";
    testResultBox.style.color = "var(--text-info)";
    testResultBox.style.border = "1px solid var(--border-color)";
    testResultBox.innerText = "Testing connection to inference provider...";

    try {
      const resp = await fetch("/api/settings/test-connection", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          base_url: baseUrl,
          api_key: apiKey,
          model_name: modelName
        })
      });
      const data = await resp.json();

      if (data.success) {
        testResultBox.style.background = "rgba(16, 185, 129, 0.15)";
        testResultBox.style.color = "var(--text-success)";
        testResultBox.style.border = "1px solid rgba(16, 185, 129, 0.3)";
        testResultBox.innerHTML = `✅ <strong>Connected!</strong> Response time: ${data.latency_ms}ms | Model '${data.model}' verified.`;
      } else {
        testResultBox.style.background = "rgba(239, 68, 68, 0.15)";
        testResultBox.style.color = "var(--text-danger)";
        testResultBox.style.border = "1px solid rgba(239, 68, 68, 0.3)";
        testResultBox.innerHTML = `❌ <strong>Connection Failed:</strong> ${data.error || "Unknown error"}`;
      }
    } catch (e) {
      testResultBox.style.background = "rgba(239, 68, 68, 0.15)";
      testResultBox.style.color = "var(--text-danger)";
      testResultBox.style.border = "1px solid rgba(239, 68, 68, 0.3)";
      testResultBox.innerText = `❌ Request error: ${e.message}`;
    }
  });

  // Save / Update Provider Form Submit
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const pId = document.getElementById("setting-provider-id").value;
    const payload = {
      name: document.getElementById("setting-name").value.trim(),
      base_url: document.getElementById("setting-url").value.trim(),
      model_name: document.getElementById("setting-model").value.trim(),
      api_key: keyInput.value.trim(),
      is_active: 1
    };
    if (pId) payload.id = parseInt(pId);

    try {
      const resp = await fetch("/api/settings/providers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!resp.ok) throw new Error("Failed to save provider");

      showToast(pId ? "API Provider updated in Database!" : "API Provider & Key saved to Database!");
      resetProviderForm();
      loadSavedProviders();
      updateActiveProviderBadge();
    } catch (err) {
      alert(`Error saving provider: ${err.message}`);
    }
  });

  // Deactivate all / switch to local engine
  offlineBtn.addEventListener("click", async () => {
    try {
      await fetch("/api/settings/deactivate-all", { method: "POST" });
      showToast("Switched to Local Offline Heuristics Engine.");
      resetProviderForm();
      loadSavedProviders();
      updateActiveProviderBadge();
    } catch (e) {
      console.error(e);
    }
  });

  // Initial badge update
  updateActiveProviderBadge();
}

async function updateActiveProviderBadge() {
  try {
    const resp = await fetch("/api/settings/active-provider");
    if (!resp.ok) return;
    const data = await resp.json();
    const textEl = document.getElementById("active-provider-text");
    const dotEl = document.getElementById("active-provider-dot");

    if (data.is_active) {
      textEl.innerText = `AI: ${data.name} (${data.model_name})`;
      dotEl.style.backgroundColor = "var(--accent-green)";
      dotEl.style.boxShadow = "0 0 6px var(--accent-green)";
    } else {
      textEl.innerText = `Offline Local Engine`;
      dotEl.style.backgroundColor = "var(--accent-cyan)";
      dotEl.style.boxShadow = "0 0 6px var(--accent-cyan)";
    }
  } catch (e) {
    console.error("Error updating active provider badge:", e);
  }
}

async function loadSavedProviders() {
  const container = document.getElementById("saved-providers-list");
  const keyInput = document.getElementById("setting-key");
  const testResultBox = document.getElementById("test-connection-result");

  try {
    const resp = await fetch("/api/settings/providers");
    if (!resp.ok) return;
    const data = await resp.json();
    const providers = data.providers || [];

    if (providers.length === 0) {
      container.innerHTML = `<div style="color:var(--text-muted); font-size:12px; text-align:center; padding:10px;">No providers configured yet. Select a preset above or add a custom OpenAI endpoint.</div>`;
      return;
    }

    container.innerHTML = "";
    providers.forEach(p => {
      const item = document.createElement("div");
      item.style.background = p.is_active ? "rgba(99, 102, 241, 0.12)" : "var(--bg-input)";
      item.style.border = p.is_active ? "1px solid var(--accent-primary)" : "1px solid var(--border-color)";
      item.style.borderRadius = "6px";
      item.style.padding = "8px 10px";
      item.style.display = "flex";
      item.style.justifyContent = "space-between";
      item.style.alignItems = "center";
      item.style.fontSize = "12px";

      const activeBadge = p.is_active 
        ? `<span class="badge badge-exact" style="font-size:10px;">Active</span>` 
        : `<button class="btn btn-outline btn-activate-prov" style="font-size:10px; padding:2px 6px;">Set Active</button>`;

      item.innerHTML = `
        <div style="flex:1; cursor:pointer;" class="prov-info-col" title="Click to load into form for testing or editing">
          <div style="font-weight:700; color:var(--text-primary); display:flex; align-items:center; gap:6px;">
            <span>${p.name}</span>
            <span style="font-size:11px; color:var(--text-info); font-weight:normal;">[${p.model_name}]</span>
          </div>
          <div style="font-size:10px; color:var(--text-muted);">${p.base_url} • Key: ${p.masked_key}</div>
        </div>
        <div style="display:flex; align-items:center; gap:6px;">
          <button class="btn btn-outline btn-edit-prov" style="font-size:10px; padding:2px 7px; color:var(--accent-indigo);" title="Fetch details into form to edit and test">✏️ Edit / Test</button>
          ${activeBadge}
          <button class="btn btn-outline btn-del-prov" style="font-size:10px; padding:2px 7px; color:var(--accent-red);" title="Delete this provider">🗑</button>
        </div>
      `;

      // Helper to populate form with this provider's data
      const loadIntoForm = () => {
        document.getElementById("setting-provider-id").value = p.id;
        document.getElementById("setting-name").value = p.name || "";
        document.getElementById("setting-url").value = p.base_url || "";
        document.getElementById("setting-model").value = p.model_name || "";
        keyInput.value = p.api_key || "";

        const editInd = document.getElementById("editing-indicator");
        if (editInd) {
          document.getElementById("editing-provider-name").innerText = `${p.name} (${p.model_name})`;
          editInd.style.display = "flex";
        }
        const btnText = document.getElementById("btn-save-provider-text");
        if (btnText) btnText.innerText = "💾 Update Provider";
        testResultBox.style.display = "none";
        showToast(`Loaded ${p.name}. You can test connection or update.`);
      };

      // Edit Button & Info click
      item.querySelector(".btn-edit-prov").addEventListener("click", loadIntoForm);
      item.querySelector(".prov-info-col").addEventListener("click", loadIntoForm);

      // Set Active handler
      const actBtn = item.querySelector(".btn-activate-prov");
      if (actBtn) {
        actBtn.addEventListener("click", async (e) => {
          e.stopPropagation();
          await fetch(`/api/settings/providers/${p.id}/active`, { method: "PUT" });
          showToast(`Activated ${p.name}!`);
          loadSavedProviders();
          updateActiveProviderBadge();
        });
      }

      // 2-Step Resilient Delete handler (doesn't rely on browser confirm() modal)
      const delBtn = item.querySelector(".btn-del-prov");
      let confirmDelete = false;
      let resetTimer = null;

      delBtn.addEventListener("click", async (e) => {
        e.stopPropagation();
        if (!confirmDelete) {
          confirmDelete = true;
          delBtn.innerText = "Confirm?";
          delBtn.style.backgroundColor = "var(--accent-red)";
          delBtn.style.color = "#ffffff";
          resetTimer = setTimeout(() => {
            confirmDelete = false;
            delBtn.innerText = "🗑";
            delBtn.style.backgroundColor = "";
            delBtn.style.color = "var(--accent-red)";
          }, 4000);
          return;
        }

        clearTimeout(resetTimer);
        delBtn.innerText = "...";

        try {
          const dResp = await fetch(`/api/settings/providers/${p.id}`, { method: "DELETE" });
          if (!dResp.ok) {
            const err = await dResp.json();
            throw new Error(err.detail || "Delete failed");
          }
          showToast(`Deleted ${p.name}.`);

          // If currently editing this provider, reset form
          if (document.getElementById("setting-provider-id").value == p.id) {
            document.getElementById("btn-clear-provider-form").click();
          }

          loadSavedProviders();
          updateActiveProviderBadge();
        } catch (err) {
          alert(`Delete error: ${err.message}`);
          delBtn.innerText = "🗑";
          confirmDelete = false;
        }
      });

      container.appendChild(item);
    });
  } catch (e) {
    container.innerHTML = `<div style="color:var(--text-danger); font-size:12px;">Failed to load saved providers: ${e.message}</div>`;
  }
}

// ================= TAB 5: AI RESUME TAILOR CONTROLLER =================

function initTailor() {
  // Tier Card Clicks
  [1, 2, 3].forEach(tierNum => {
    const card = document.getElementById(`tier-card-${tierNum}`);
    if (card) {
      card.addEventListener("click", () => {
        document.querySelectorAll(".tier-card").forEach(c => c.classList.remove("active"));
        card.classList.add("active");
        const radio = card.querySelector("input[name='tailor-tier']");
        if (radio) {
          radio.checked = true;
          selectedTailorTier = radio.value;
        }
      });
    }
  });

  // Run Tailor Button
  const runBtn = document.getElementById("btn-run-tailor");
  if (runBtn) {
    runBtn.addEventListener("click", () => runTailor());
  }

  // Subviews Toggle (Formatted, Diff, Raw)
  const viewBtns = document.querySelectorAll(".tailor-view-btn");
  viewBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      viewBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const targetView = btn.getAttribute("data-view");
      document.querySelectorAll(".tailor-subview").forEach(sv => sv.style.display = "none");
      const activeSv = document.getElementById(`tailor-view-${targetView}`);
      if (activeSv) activeSv.style.display = "block";
    });
  });

  // Copy Tailored Resume Button
  const copyBtn = document.getElementById("btn-copy-tailored");
  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      const text = document.getElementById("tailor-raw-text").value;
      if (text) {
        navigator.clipboard.writeText(text);
        showToast("Full tailored resume copied to clipboard!");
      }
    });
  }

  // Link Tailored Resume to Funnel
  const linkBtn = document.getElementById("btn-link-tailored-funnel");
  if (linkBtn) {
    linkBtn.addEventListener("click", () => {
      if (!currentTailoredResult || !currentTailoredResult.ledger_entry) {
        alert("Please generate a tailored resume first.");
        return;
      }
      openLinkFunnelModal(currentTailoredResult.ledger_entry.id);
    });
  }

  // View in Ledger Button
  const viewLedgerBtn = document.getElementById("btn-tailor-view-ledger");
  if (viewLedgerBtn) {
    viewLedgerBtn.addEventListener("click", () => switchToTab("tab-ledger"));
  }

  // Quick Sample JD Button in Tailor Tab
  const quickJdBtn = document.getElementById("btn-tailor-quick-sample-jd");
  if (quickJdBtn) {
    quickJdBtn.addEventListener("click", async () => {
      const statusEl = document.getElementById("tailor-status-text");
      if (statusEl) statusEl.innerHTML = `<span>⏳ Loading sample JD & evaluating...</span>`;
      const jdInput = document.getElementById("jd-text-input");
      if (jdInput) jdInput.value = SAMPLE_JD_TEXT;
      try {
        const resp = await fetch("/api/resume/compare", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            jd_text: SAMPLE_JD_TEXT,
            resume_data: currentResumeData || { master_resume: masterResumeData }
          })
        });
        if (resp.ok) {
          const data = await resp.json();
          currentJdData = data.jd_parsed;
          currentComparison = data.comparison;
          renderComparisonResults(data);
          renderMatrixTable(data.comparison.side_by_side_matrix);
          updateTailorContext();
          showToast("Sample Job Description linked for tailoring!");
        }
      } catch (e) {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--text-danger);">Error: ${e.message}</span>`;
      }
    });
  }
}

function updateTailorContext() {
  const masterLabel = document.getElementById("source-master-label");
  if (masterLabel && masterResumeData) {
    masterLabel.innerText = `${masterResumeData.full_name || 'Master Profile'} (${masterResumeData.projects?.length || 0} projects)`;
  }

  // Check if JD is loaded
  const statusEl = document.getElementById("tailor-status-text");
  const quickJdBtn = document.getElementById("btn-tailor-quick-sample-jd");
  if (!currentJdData) {
    if (statusEl) statusEl.innerHTML = `<span style="color:var(--text-danger);">⚠️ No Job Description compared yet.</span>`;
    if (quickJdBtn) quickJdBtn.style.display = "inline-flex";
  } else {
    if (statusEl) statusEl.innerHTML = `<span style="color:var(--text-info);">🎯 Target: ${currentJdData.role_title || 'Role'} at ${currentJdData.company || 'Company'}</span>`;
    if (quickJdBtn) quickJdBtn.style.display = "none";
  }
}

async function runTailor() {
  if (!currentJdData) {
    const statusEl = document.getElementById("tailor-status-text");
    if (statusEl) {
      statusEl.innerHTML = `<span style="color:var(--text-danger);">⚠️ Please compare a Job Description in Tab 3 first or click "⚡ Use Sample JD" above.</span>`;
    }
    return;
  }

  const runBtn = document.getElementById("btn-run-tailor");
  const statusEl = document.getElementById("tailor-status-text");
  const customNotes = document.getElementById("tailor-custom-notes").value.trim();

  runBtn.disabled = true;
  runBtn.innerHTML = `<span>⏳ Optimizing with AI...</span>`;
  statusEl.innerText = "Synthesizing tailored resume and evaluating ATS score...";

  try {
    const jdInput = document.getElementById("jd-text-input");
    const jdTextVal = jdInput ? jdInput.value.trim() : "";

    const resp = await fetch("/api/resume/tailor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tier: selectedTailorTier,
        source_type: "master",
        custom_instructions: customNotes,
        resume_data: currentResumeData,
        jd_data: currentJdData,
        comparison: currentComparison,
        excluded_keywords: getExcludedMatrixKeywords(),
        jd_text: jdTextVal
      })
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Tailoring failed");
    }

    const data = await resp.json();
    currentTailoredResult = data;
    renderTailorResults(data);
    showToast("Resume tailored successfully!");
  } catch (err) {
    alert(`Error tailoring resume: ${err.message}`);
  } finally {
    runBtn.disabled = false;
    runBtn.innerHTML = `<span>✨ Generate Tailored Resume</span>`;
    updateTailorContext();
  }
}

function renderTailorResults(data) {
  document.getElementById("tailor-empty-state").style.display = "none";
  document.getElementById("tailor-results-content").style.display = "block";

  // Scores Banner
  document.getElementById("score-before-display").innerText = `${Math.round(data.score_before)}%`;
  document.getElementById("score-after-display").innerText = `${Math.round(data.score_after)}%`;
  const gain = data.score_gain >= 0 ? `+${data.score_gain}% Gain 🚀` : `${data.score_gain}%`;
  document.getElementById("score-gain-badge").innerText = gain;

  document.getElementById("tailor-engine-badge").innerText = data.engine_used || "AI Optimizer";
  document.getElementById("tailor-tier-display").innerText = data.tier || selectedTailorTier;

  // Downloads
  const docxBtn = document.getElementById("btn-download-docx");
  docxBtn.href = data.docx_download_url;
  docxBtn.setAttribute("download", data.filename);

  const txtBtn = document.getElementById("btn-download-txt");
  txtBtn.href = data.txt_download_url;
  txtBtn.setAttribute("download", data.filename.replace(".docx", ".txt"));

  // Formatted View
  const formattedContainer = document.getElementById("tailor-view-formatted");
  formattedContainer.innerHTML = renderResumeDocumentHTML(data.tailored_data);

  // Changes Log View
  const changesContainer = document.getElementById("tailor-changes-list");
  changesContainer.innerHTML = "";
  if (data.changes_summary && data.changes_summary.length > 0) {
    data.changes_summary.forEach(c => {
      const item = document.createElement("div");
      item.className = "change-item";
      item.innerHTML = `
        <div class="change-item-header">
          <span class="change-item-section">📍 ${c.section || 'General'}</span>
          <span class="badge badge-nice">${c.type || 'Adjustment'}</span>
        </div>
        <div class="change-item-detail">${c.detail}</div>
      `;
      changesContainer.appendChild(item);
    });
  } else {
    changesContainer.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:10px;">No detailed changes recorded.</div>`;
  }

  // Raw Text View
  document.getElementById("tailor-raw-text").value = data.resume_text || "";
}

// Document HTML Renderer Helper
function renderResumeDocumentHTML(data) {
  if (!data) return "<p>No resume data.</p>";
  let html = '<div class="resume-preview-doc">';

  const name = data.full_name || data.contact?.name || "CANDIDATE";
  html += `<h1>${escapeHtml(name)}</h1>`;

  const contactParts = [];
  if (data.contact?.location) contactParts.push(escapeHtml(data.contact.location));
  if (data.contact?.phone) contactParts.push(escapeHtml(data.contact.phone));
  if (data.contact?.email) contactParts.push(escapeHtml(data.contact.email));
  if (data.contact?.linkedin) contactParts.push(escapeHtml(data.contact.linkedin));
  if (data.contact?.github) contactParts.push(escapeHtml(data.contact.github));

  if (contactParts.length > 0) {
    html += `<div class="doc-contact">${contactParts.join(" &nbsp;|&nbsp; ")}</div>`;
  }

  if (data.summary) {
    html += `<h2>Professional Summary</h2>`;
    html += `<p>${escapeHtml(data.summary)}</p>`;
  }

  if (data.skills) {
    html += `<h2>Core Competencies & Technical Skills</h2>`;
    if (typeof data.skills === "object" && !Array.isArray(data.skills)) {
      for (const [cat, sList] of Object.entries(data.skills)) {
        const sStr = Array.isArray(sList) ? sList.join(", ") : String(sList);
        html += `<p><strong>${escapeHtml(cat)}:</strong> ${escapeHtml(sStr)}</p>`;
      }
    } else if (Array.isArray(data.skills)) {
      html += `<p>${escapeHtml(data.skills.join(", "))}</p>`;
    }
  }

  const exps = data.experiences || data.work_experience || [];
  if (exps.length > 0) {
    html += `<h2>Professional Experience</h2>`;
    exps.forEach(exp => {
      const title = exp.title || "Role";
      const comp = exp.company ? ` | ${exp.company}` : "";
      const dates = [exp.location, exp.start_date && exp.end_date ? `${exp.start_date} - ${exp.end_date}` : ""].filter(Boolean).join(" | ");
      html += `<div class="doc-role-header"><span>${escapeHtml(title)}${escapeHtml(comp)}</span><span style="font-weight:normal; color:var(--text-muted);">${escapeHtml(dates)}</span></div>`;
      if (exp.bullets && exp.bullets.length > 0) {
        html += `<ul>`;
        exp.bullets.forEach(b => {
          const cleanB = b.replace(/^[•\-\*]\s*/, "");
          html += `<li>${escapeHtml(cleanB)}</li>`;
        });
        html += `</ul>`;
      }
    });
  }

  const projs = data.projects || [];
  if (projs.length > 0) {
    html += `<h2>Key Projects & Technical Architectures</h2>`;
    projs.forEach(p => {
      const pName = p.name || "Project";
      const orgInfo = p.organisation ? ` | ${p.organisation}${p.organisation_duration ? ` (${p.organisation_duration})` : ''}` : '';
      const stack = p.tech_stack ? ` [${p.tech_stack}]` : "";
      html += `<div class="doc-role-header"><span>${escapeHtml(pName)}<span style="font-weight:normal; color:var(--text-muted); font-size:10px;">${escapeHtml(orgInfo)}</span></span><span style="font-weight:normal; color:var(--accent-primary-hover); font-size:10px;">${escapeHtml(stack)}</span></div>`;
      if (p.description) {
        html += `<p style="font-size:10px; color:var(--border-color-strong); margin-bottom:3px;">${escapeHtml(p.description)}</p>`;
      }
      if (p.bullets && p.bullets.length > 0) {
        html += `<ul>`;
        p.bullets.forEach(b => {
          const cleanB = b.replace(/^[•\-\*]\s*/, "");
          html += `<li>${escapeHtml(cleanB)}</li>`;
        });
        html += `</ul>`;
      }
    });
  }

  const edus = data.education || [];
  if (edus.length > 0) {
    html += `<h2>Education</h2>`;
    edus.forEach(e => {
      const deg = e.degree || "Degree";
      const inst = e.institution ? ` | ${e.institution}` : "";
      const yr = e.year ? ` (${e.year})` : "";
      html += `<p><strong>${escapeHtml(deg)}</strong>${escapeHtml(inst)}${escapeHtml(yr)}</p>`;
      if (e.details) {
        html += `<p style="font-size:9.5px; color:var(--text-muted); margin-top:-4px;">${escapeHtml(e.details)}</p>`;
      }
    });
  }

  const certs = data.certifications || [];
  if (certs.length > 0) {
    html += `<h2>Certifications</h2><ul>`;
    certs.forEach(c => {
      const cTxt = typeof c === "string" ? c : (c.name || JSON.stringify(c));
      html += `<li>${escapeHtml(cTxt)}</li>`;
    });
    html += `</ul>`;
  }

  html += '</div>';
  return html;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ================= TAB 5: MASTER RESUME CONTROLLER =================

function initMasterResume() {
  document.getElementById("btn-save-master-resume").addEventListener("click", () => saveMasterResume());
  document.getElementById("btn-reset-sample-master").addEventListener("click", () => resetSampleMaster());

  const profileSelect = document.getElementById("master-profile-select");
  if (profileSelect) {
    profileSelect.addEventListener("change", () => activateMasterProfile(profileSelect.value));
  }
  const newProfileBtn = document.getElementById("btn-new-master-profile");
  if (newProfileBtn) {
    newProfileBtn.addEventListener("click", () => createMasterProfile());
  }
  const dupProfileBtn = document.getElementById("btn-duplicate-master-profile");
  if (dupProfileBtn) {
    dupProfileBtn.addEventListener("click", () => createMasterProfile({ duplicate: true }));
  }
  const renameProfileBtn = document.getElementById("btn-rename-master-profile");
  if (renameProfileBtn) {
    renameProfileBtn.addEventListener("click", () => renameMasterProfile());
  }
  const deleteProfileBtn = document.getElementById("btn-delete-master-profile");
  if (deleteProfileBtn) {
    deleteProfileBtn.addEventListener("click", () => deleteMasterProfile());
  }

  // Master Profile create/duplicate/rename modal
  document.getElementById("btn-close-master-profile-modal")?.addEventListener("click", closeMasterProfileModal);
  document.getElementById("btn-cancel-master-profile-modal")?.addEventListener("click", closeMasterProfileModal);
  document.getElementById("btn-confirm-master-profile-modal")?.addEventListener("click", () => submitMasterProfileModal());
  document.getElementById("master-profile-modal-input")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      submitMasterProfileModal();
    }
  });

  // Master Profile delete confirmation modal
  const deleteProfileModal = document.getElementById("master-profile-delete-modal");
  document.getElementById("btn-close-master-profile-delete-modal")?.addEventListener("click", () => deleteProfileModal?.classList.remove("active"));
  document.getElementById("btn-cancel-master-profile-delete-modal")?.addEventListener("click", () => deleteProfileModal?.classList.remove("active"));
  document.getElementById("btn-confirm-master-profile-delete-modal")?.addEventListener("click", () => confirmDeleteMasterProfile());

  // Project Modal
  const modal = document.getElementById("add-project-modal");
  document.getElementById("btn-open-add-project").addEventListener("click", () => openProjectModal());
  document.getElementById("btn-close-project-modal").addEventListener("click", () => modal.classList.remove("active"));
  document.getElementById("btn-cancel-project-modal").addEventListener("click", () => modal.classList.remove("active"));

  document.getElementById("project-form").addEventListener("submit", (e) => {
    e.preventDefault();
    handleSaveProject();
  });
}

async function loadMasterResume() {
  try {
    const resp = await fetch("/api/master-resume");
    if (!resp.ok) return;
    const data = await resp.json();
    masterResumeData = data.master_resume;
    renderMasterResumeFields(masterResumeData);
    await loadMasterProfiles();
  } catch (e) {
    console.error("Failed to load master resume:", e);
  }
}

// ================= MULTI-PROFILE MASTER RESUME SWITCHER =================

async function loadMasterProfiles() {
  try {
    const resp = await fetch("/api/master-resume/profiles");
    if (!resp.ok) return;
    const data = await resp.json();
    masterProfiles = data.profiles || [];
    renderMasterProfileSelect();
  } catch (e) {
    console.error("Failed to load master profiles:", e);
  }
}

function renderMasterProfileSelect() {
  const select = document.getElementById("master-profile-select");
  const hint = document.getElementById("master-profile-count-hint");
  if (!select) return;

  select.innerHTML = "";
  let activeProfile = null;
  masterProfiles.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.id;
    // Show only the user-owned profile_name -- appending full_name here made the
    // last-parsed resume's name look permanently glued on with no way to remove
    // it (Rename only ever edits profile_name), which read as a name that
    // couldn't be fully renamed.
    opt.innerText = `${p.is_locked ? "🔒 " : ""}${p.profile_name}`;
    if (p.is_active) {
      opt.selected = true;
      activeProfile = p;
    }
    select.appendChild(opt);
  });

  if (hint) {
    hint.innerText = masterProfiles.length === 1
      ? "1 profile"
      : `${masterProfiles.length} profiles`;
  }

  const isActiveLocked = !!(activeProfile && activeProfile.is_locked);
  const deleteBtn = document.getElementById("btn-delete-master-profile");
  if (deleteBtn) deleteBtn.disabled = isActiveLocked || masterProfiles.length <= 1;
  const renameBtn = document.getElementById("btn-rename-master-profile");
  if (renameBtn) renameBtn.disabled = isActiveLocked;
}

async function activateMasterProfile(profileId) {
  try {
    const resp = await fetch(`/api/master-resume/profiles/${profileId}/activate`, { method: "POST" });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Failed to switch profile");
    }
    const data = await resp.json();
    masterResumeData = data.master_resume;
    masterProfiles = data.profiles || masterProfiles;
    renderMasterResumeFields(masterResumeData);
    renderMasterProfileSelect();
    await loadMasterResumeAtsView();
    showToast(`Switched to "${masterResumeData.profile_name}"`);
  } catch (err) {
    alert(`Error switching profile: ${err.message}`);
    renderMasterProfileSelect();
  }
}

// Uses an in-page modal instead of window.prompt()/confirm() -- the desktop app
// window is launched via Edge/Chrome --app mode (see main.py), and Chromium's
// app-mode windows silently no-op native prompt()/confirm() dialogs (they return
// null/false instantly with no visible UI), which made these controls look dead.
let masterProfileModalMode = "create"; // "create" | "duplicate" | "rename"
let masterProfileDeleteTargetId = null;

function createMasterProfile(opts = {}) {
  openMasterProfileModal(opts.duplicate ? "duplicate" : "create");
}

function renameMasterProfile() {
  if (!masterResumeData) return;
  if (masterResumeData.is_locked) {
    showToast("The Sample Profile is read-only and can't be renamed.");
    return;
  }
  openMasterProfileModal("rename");
}

function openMasterProfileModal(mode) {
  masterProfileModalMode = mode;
  const modal = document.getElementById("master-profile-modal");
  const title = document.getElementById("master-profile-modal-title");
  const desc = document.getElementById("master-profile-modal-desc");
  const input = document.getElementById("master-profile-modal-input");
  const confirmBtn = document.getElementById("btn-confirm-master-profile-modal");
  if (!modal || !input) return;

  if (mode === "duplicate") {
    title.innerText = "Duplicate Master Profile";
    desc.innerText = "Creates a copy of the active profile with a new name.";
    input.value = masterResumeData ? `${masterResumeData.profile_name} Copy` : "";
    confirmBtn.innerText = "Duplicate";
  } else if (mode === "rename") {
    title.innerText = "Rename Master Profile";
    desc.innerText = "Give this profile a new name.";
    input.value = masterResumeData ? (masterResumeData.profile_name || "") : "";
    confirmBtn.innerText = "Save";
  } else {
    title.innerText = "New Master Profile";
    desc.innerText = "Create a new blank Master Profile.";
    input.value = "";
    confirmBtn.innerText = "Create";
  }

  modal.classList.add("active");
  setTimeout(() => input.focus(), 50);
}

function closeMasterProfileModal() {
  const modal = document.getElementById("master-profile-modal");
  if (modal) modal.classList.remove("active");
}

async function submitMasterProfileModal() {
  const input = document.getElementById("master-profile-modal-input");
  const name = (input.value || "").trim();
  if (!name) {
    input.focus();
    return;
  }

  if (masterProfileModalMode === "rename") {
    if (!masterResumeData) { closeMasterProfileModal(); return; }
    if (name !== masterResumeData.profile_name) {
      masterResumeData.profile_name = name;
      await saveMasterResume();
      await loadMasterProfiles();
    }
    closeMasterProfileModal();
    return;
  }

  const duplicate = masterProfileModalMode === "duplicate";
  try {
    const payload = { profile_name: name };
    if (duplicate && masterResumeData) {
      payload.clone_from_id = masterResumeData.id;
    }
    const resp = await fetch("/api/master-resume/profiles", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Failed to create profile");
    }
    const data = await resp.json();
    masterResumeData = data.master_resume;
    masterProfiles = data.profiles || masterProfiles;
    renderMasterResumeFields(masterResumeData);
    renderMasterProfileSelect();
    await loadMasterResumeAtsView();
    showToast(duplicate ? `Duplicated as "${masterResumeData.profile_name}"` : `Created "${masterResumeData.profile_name}"`);
    closeMasterProfileModal();
  } catch (err) {
    showToast(`Error: ${err.message}`);
  }
}

function deleteMasterProfile() {
  if (!masterResumeData) return;
  if (masterResumeData.is_locked) {
    showToast("The Sample Profile is built-in and can't be deleted.");
    return;
  }
  if (masterProfiles.length <= 1) {
    showToast("You can't delete the only remaining Master Profile.");
    return;
  }
  masterProfileDeleteTargetId = masterResumeData.id;
  const nameEl = document.getElementById("master-profile-delete-name");
  if (nameEl) nameEl.innerText = masterResumeData.profile_name || "this profile";
  const modal = document.getElementById("master-profile-delete-modal");
  if (modal) modal.classList.add("active");
}

async function confirmDeleteMasterProfile() {
  const modal = document.getElementById("master-profile-delete-modal");
  const targetId = masterProfileDeleteTargetId;
  if (modal) modal.classList.remove("active");
  if (!targetId) return;

  try {
    const resp = await fetch(`/api/master-resume/profiles/${targetId}`, { method: "DELETE" });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Failed to delete profile");
    }
    const data = await resp.json();
    masterProfiles = data.profiles || [];
    showToast("Master Profile deleted.");
    await loadMasterResume();
  } catch (err) {
    showToast(`Error deleting profile: ${err.message}`);
  } finally {
    masterProfileDeleteTargetId = null;
  }
}

function renderMasterResumeFields(data) {
  if (!data) return;
  document.getElementById("master-name").value = data.full_name || "";
  document.getElementById("master-location").value = data.location || "";
  document.getElementById("master-email").value = data.email || "";
  document.getElementById("master-phone").value = data.phone || "";
  document.getElementById("master-linkedin").value = data.linkedin || "";
  document.getElementById("master-github").value = data.github || "";
  document.getElementById("master-summary").value = data.summary || "";

  document.getElementById("master-skills-json").value = JSON.stringify(data.skills || {}, null, 2);

  renderMasterProjectsList(data.projects || []);
  updateMasterFormLockState(!!data.is_locked);
}

// Locks editing UI for the built-in read-only Sample Profile. Fields stay visible
// (so it's usable for viewing) but nothing can be typed/saved/renamed/deleted --
// "Duplicate" is the only way to turn it into an editable profile.
function updateMasterFormLockState(isLocked) {
  const fieldIds = [
    "master-name", "master-location", "master-email", "master-phone",
    "master-linkedin", "master-github", "master-summary", "master-skills-json"
  ];
  fieldIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.disabled = isLocked;
  });

  const saveBtn = document.getElementById("btn-save-master-resume");
  if (saveBtn) saveBtn.disabled = isLocked;

  const addProjectBtn = document.getElementById("btn-open-add-project");
  if (addProjectBtn) addProjectBtn.disabled = isLocked;

  const renameBtn = document.getElementById("btn-rename-master-profile");
  if (renameBtn) renameBtn.disabled = isLocked;

  const deleteBtn = document.getElementById("btn-delete-master-profile");
  if (deleteBtn) deleteBtn.disabled = isLocked || masterProfiles.length <= 1;

  const banner = document.getElementById("master-readonly-banner");
  if (banner) banner.style.display = isLocked ? "flex" : "none";
}

function renderMasterProjectsList(projects) {
  const container = document.getElementById("master-projects-list");
  document.getElementById("master-projects-count").innerText = projects.length;
  container.innerHTML = "";

  if (projects.length === 0) {
    container.innerHTML = `<div style="text-align:center; padding:30px; color:var(--text-muted); font-size:12px;">No projects in repository yet. Click "Add Project" above.</div>`;
    return;
  }

  const locked = !!(masterResumeData && masterResumeData.is_locked);

  projects.forEach((proj, idx) => {
    const card = document.createElement("div");
    card.className = "project-card";
    const orgInfo = proj.organisation ? `<div style="font-size:11px; color:#93c5fd; margin-top:2px;">🏢 ${escapeHtml(proj.organisation)}${proj.organisation_duration ? ` <span style="color:var(--text-secondary); font-weight:normal;">(${escapeHtml(proj.organisation_duration)})</span>` : ''}</div>` : '';
    card.innerHTML = `
      <div class="project-card-header">
        <div>
          <span class="project-card-title">${escapeHtml(proj.name)}</span>
          ${orgInfo}
          <div class="project-card-tech">${escapeHtml(proj.tech_stack || '')}</div>
        </div>
        <div style="display:flex; gap:4px;">
          ${locked ? '' : `
            <button class="btn btn-outline btn-edit-proj" style="font-size:10px; padding:2px 6px;">✏️</button>
            <button class="btn btn-outline btn-del-proj" style="font-size:10px; padding:2px 6px; color:var(--text-danger);">🗑</button>
          `}
        </div>
      </div>
      ${proj.description ? `<div class="project-card-desc">${escapeHtml(proj.description)}</div>` : ''}
      ${proj.metrics ? `<div class="project-card-metrics">📈 <strong>Key Metrics:</strong> ${escapeHtml(proj.metrics)}</div>` : ''}
      ${(proj.bullets && proj.bullets.length > 0) ? `
        <ul class="project-card-bullets">
          ${proj.bullets.map(b => `<li>${escapeHtml(b)}</li>`).join("")}
        </ul>
      ` : ''}
    `;

    if (!locked) {
      card.querySelector(".btn-edit-proj").addEventListener("click", () => openProjectModal(proj));
      card.querySelector(".btn-del-proj").addEventListener("click", () => deleteProject(proj.id || idx));
    }

    container.appendChild(card);
  });
}

function openProjectModal(proj = null) {
  const modal = document.getElementById("add-project-modal");
  const title = document.getElementById("project-modal-title");
  const idInput = document.getElementById("project-form-id");
  const orgInput = document.getElementById("project-form-org");
  const orgDurInput = document.getElementById("project-form-org-duration");

  // Populate datalist with candidate's work experiences
  const orgDatalist = document.getElementById("org-options-list");
  if (orgDatalist) {
    orgDatalist.innerHTML = "";
    const exps = masterResumeData?.experiences || currentResumeData?.ats_json?.work_experience || [];
    const knownOrgs = new Map();
    exps.forEach(e => {
      const comp = (e.company || "").trim();
      const dur = (e.dates || `${e.start_date || ''} - ${e.end_date || ''}`).trim();
      if (comp && !knownOrgs.has(comp.toLowerCase())) {
        knownOrgs.set(comp.toLowerCase(), { name: comp, duration: dur });
      }
    });
    knownOrgs.forEach(item => {
      const opt = document.createElement("option");
      opt.value = item.name;
      opt.setAttribute("data-duration", item.duration);
      orgDatalist.appendChild(opt);
    });
  }

  // Quick suggest click
  const suggestBtn = document.getElementById("quick-org-hint");
  if (suggestBtn) {
    suggestBtn.onclick = () => {
      const exps = masterResumeData?.experiences || [];
      if (exps.length > 0) {
        orgInput.value = exps[0].company || "";
        orgDurInput.value = (exps[0].dates || `${exps[0].start_date || ''} - ${exps[0].end_date || ''}`).trim();
        showToast(`Selected: ${orgInput.value} (${orgDurInput.value})`);
      }
    };
  }

  // Auto-fill duration when org name matches an existing work experience company
  orgInput.oninput = () => {
    const val = orgInput.value.trim().toLowerCase();
    const exps = masterResumeData?.experiences || [];
    const matched = exps.find(e => (e.company || "").trim().toLowerCase() === val);
    if (matched) {
      orgDurInput.value = (matched.dates || `${matched.start_date || ''} - ${matched.end_date || ''}`).trim();
    }
  };

  if (proj) {
    title.innerText = "✏️ Edit Career Project";
    idInput.value = proj.id || "";
    document.getElementById("project-form-name").value = proj.name || "";
    orgInput.value = proj.organisation || "";
    orgDurInput.value = proj.organisation_duration || "";
    document.getElementById("project-form-tech").value = proj.tech_stack || "";
    document.getElementById("project-form-desc").value = proj.description || "";
    document.getElementById("project-form-metrics").value = proj.metrics || "";
    document.getElementById("project-form-bullets").value = (proj.bullets || []).join("\n");
  } else {
    title.innerText = "➕ Add Career Project to Master Resume";
    idInput.value = "";
    document.getElementById("project-form").reset();
    // Default to candidate's primary company if available
    const exps = masterResumeData?.experiences || [];
    if (exps.length > 0) {
      orgInput.value = exps[0].company || "";
      orgDurInput.value = (exps[0].dates || `${exps[0].start_date || ''} - ${exps[0].end_date || ''}`).trim();
    } else {
      orgInput.value = "";
      orgDurInput.value = "";
    }
  }
  modal.classList.add("active");
}

async function handleSaveProject() {
  const idVal = document.getElementById("project-form-id").value;
  const name = document.getElementById("project-form-name").value.trim();
  const org = document.getElementById("project-form-org").value.trim();
  const orgDuration = document.getElementById("project-form-org-duration").value.trim();
  const tech = document.getElementById("project-form-tech").value.trim();
  const desc = document.getElementById("project-form-desc").value.trim();
  const metrics = document.getElementById("project-form-metrics").value.trim();
  const bullets = document.getElementById("project-form-bullets").value
    .split("\n")
    .map(b => b.trim())
    .filter(b => b.length > 0);

  if (!masterResumeData) masterResumeData = { projects: [] };
  if (!masterResumeData.projects) masterResumeData.projects = [];

  const projectObj = {
    id: idVal || `proj-${Date.now()}`,
    name,
    organisation: org,
    organisation_duration: orgDuration,
    tech_stack: tech,
    description: desc,
    metrics,
    bullets
  };

  if (idVal) {
    // Edit existing
    const idx = masterResumeData.projects.findIndex(p => p.id === idVal);
    if (idx !== -1) {
      masterResumeData.projects[idx] = projectObj;
    } else {
      masterResumeData.projects.push(projectObj);
    }
  } else {
    // Add new
    masterResumeData.projects.push(projectObj);
  }

  document.getElementById("add-project-modal").classList.remove("active");
  renderMasterProjectsList(masterResumeData.projects);
  await saveMasterResume();
}

async function deleteProject(projId) {
  if (!confirm("Remove this project from Master Resume repository?")) return;
  if (!masterResumeData || !masterResumeData.projects) return;

  masterResumeData.projects = masterResumeData.projects.filter((p, idx) => p.id !== projId && idx !== projId);
  renderMasterProjectsList(masterResumeData.projects);
  await saveMasterResume();
}

async function saveMasterResume() {
  if (!masterResumeData) masterResumeData = {};

  masterResumeData.full_name = document.getElementById("master-name").value.trim();
  masterResumeData.location = document.getElementById("master-location").value.trim();
  masterResumeData.email = document.getElementById("master-email").value.trim();
  masterResumeData.phone = document.getElementById("master-phone").value.trim();
  masterResumeData.linkedin = document.getElementById("master-linkedin").value.trim();
  masterResumeData.github = document.getElementById("master-github").value.trim();
  masterResumeData.summary = document.getElementById("master-summary").value.trim();

  try {
    const rawSkills = document.getElementById("master-skills-json").value.trim();
    if (rawSkills) {
      masterResumeData.skills = JSON.parse(rawSkills);
    }
  } catch (e) {
    alert("Invalid JSON in Skills Taxonomy. Please fix JSON syntax.");
    return;
  }

  try {
    const resp = await fetch("/api/master-resume", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(masterResumeData)
    });

    if (!resp.ok) throw new Error("Save failed");
    const data = await resp.json();
    masterResumeData = data.master_resume;
    showToast("Master Resume saved to database!");
  } catch (err) {
    alert(`Error saving master resume: ${err.message}`);
  }
}

async function resetSampleMaster() {
  // Switches to the permanent, read-only Sample Profile -- it never overwrites
  // whatever profile you currently have active. Duplicate it (📋 on the profile
  // switcher) to get an editable copy.
  try {
    const resp = await fetch("/api/master-resume/sample-profile/activate", { method: "POST" });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Failed to load Sample Profile");
    }
    const data = await resp.json();
    masterResumeData = data.master_resume;
    masterProfiles = data.profiles || masterProfiles;
    renderMasterResumeFields(masterResumeData);
    renderMasterProfileSelect();
    await loadMasterResumeAtsView();
    showToast("Switched to the Sample Profile (read-only reference)");
  } catch (err) {
    showToast(`Error: ${err.message}`);
  }
}

// ================= TAB 6: RESUME LEDGER CONTROLLER =================

function initResumeLedger() {
  document.getElementById("btn-refresh-ledger").addEventListener("click", () => loadResumeLedger());

  const createFromJdLedgerBtn = document.getElementById("btn-ledger-create-from-jd");
  if (createFromJdLedgerBtn) {
    createFromJdLedgerBtn.addEventListener("click", () => switchToTab("tab-compare"));
  }

  // Ledger Inspect Modal close
  const inspectModal = document.getElementById("ledger-inspect-modal");
  document.getElementById("btn-close-inspect-modal").addEventListener("click", () => inspectModal.classList.remove("active"));

  // Inspect subviews toggle
  const viewBtns = document.querySelectorAll(".inspect-view-btn");
  viewBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      viewBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const targetView = btn.getAttribute("data-view");
      document.querySelectorAll(".inspect-subview").forEach(sv => sv.style.display = "none");
      const activeSv = document.getElementById(`inspect-view-${targetView}`);
      if (activeSv) activeSv.style.display = "block";
    });
  });

  // Inspect copy button
  document.getElementById("inspect-btn-copy").addEventListener("click", () => {
    const text = document.getElementById("inspect-raw-text").value;
    if (text) {
      navigator.clipboard.writeText(text);
      showToast("Resume copied to clipboard!");
    }
  });
}

async function loadResumeLedger() {
  try {
    const resp = await fetch("/api/resume/ledger");
    if (!resp.ok) return;
    const data = await resp.json();
    resumeLedgerEntries = data.entries || [];
    renderLedgerSummaryAndTable(resumeLedgerEntries);
  } catch (e) {
    console.error("Failed to load resume ledger:", e);
  }
}

function renderLedgerSummaryAndTable(entries) {
  // Stats
  document.getElementById("ledger-stat-total").innerText = entries.length;

  if (entries.length > 0) {
    const totalGain = entries.reduce((acc, e) => acc + (e.match_score_after - e.match_score_before), 0);
    const avgGain = (totalGain / entries.length).toFixed(1);
    document.getElementById("ledger-stat-avg-gain").innerText = `+${avgGain}%`;
    document.getElementById("ledger-stat-latest-tier").innerText = entries[0].tier || "-";
  } else {
    document.getElementById("ledger-stat-avg-gain").innerText = "+0%";
    document.getElementById("ledger-stat-latest-tier").innerText = "-";
  }

  // Table
  const tbody = document.getElementById("ledger-table-body");
  tbody.innerHTML = "";

  if (entries.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:30px; color:var(--text-muted);">No generated resumes in ledger yet. Tailor a resume in Tab 4 to start tracking versions.</td></tr>`;
    return;
  }

  entries.forEach(entry => {
    const tr = document.createElement("tr");
    const dateStr = entry.created_at ? entry.created_at.substring(0, 16).replace("T", " ") : "-";
    const delta = (entry.match_score_after - entry.match_score_before).toFixed(1);
    const deltaBadge = delta >= 0 ? `<span class="badge badge-exact" style="font-size:10px;">+${delta}%</span>` : `<span class="badge badge-missing">${delta}%</span>`;

    tr.innerHTML = `
      <td style="font-size:11px; color:var(--text-secondary);">${dateStr}</td>
      <td>
        <strong style="color:var(--text-primary); font-size:12px;">${escapeHtml(entry.resume_name || entry.job_title)}</strong>
        <div style="font-size:11px; color:var(--text-muted);">${escapeHtml(entry.company)}</div>
      </td>
      <td><span class="badge badge-nice" style="font-size:10px;">${escapeHtml(entry.source_type || 'Resume')}</span></td>
      <td><span class="badge" style="background:rgba(99,102,241,0.2); color:var(--accent-indigo); font-size:10px;">${escapeHtml(entry.tier)}</span></td>
      <td>
        <div style="display:flex; align-items:center; gap:6px;">
          <span style="color:var(--text-danger); font-size:11px;">${Math.round(entry.match_score_before)}%</span>
          <span style="color:var(--text-muted); font-size:10px;">➔</span>
          <strong style="color:var(--text-success); font-size:12px;">${Math.round(entry.match_score_after)}%</strong>
          ${deltaBadge}
        </div>
      </td>
      <td>
        <div style="display:flex; gap:4px; flex-wrap:wrap;">
          <button class="btn btn-outline btn-ledger-view" style="font-size:10px; padding:3px 7px;">👁️ View</button>
          <a href="/api/resume/download/${entry.id}/docx" download="${escapeHtml(entry.filename || 'Resume.docx')}" class="btn btn-outline" style="font-size:10px; padding:3px 7px; text-decoration:none; color:var(--text-info);">💾 DOCX</a>
          <button class="btn btn-outline btn-ledger-link" style="font-size:10px; padding:3px 7px; color:var(--text-success);">➕ Link Job</button>
          <button class="btn btn-outline btn-ledger-del" style="font-size:10px; padding:3px 7px; color:var(--text-danger);">🗑</button>
        </div>
      </td>
    `;

    tr.querySelector(".btn-ledger-view").addEventListener("click", () => openLedgerInspectModal(entry));
    tr.querySelector(".btn-ledger-link").addEventListener("click", () => openLinkFunnelModal(entry.id));
    tr.querySelector(".btn-ledger-del").addEventListener("click", () => deleteLedgerRow(entry.id));

    tbody.appendChild(tr);
  });
}

function openLedgerInspectModal(entry) {
  const modal = document.getElementById("ledger-inspect-modal");
  document.getElementById("inspect-modal-role").innerText = entry.job_title || "Tailored Resume";
  document.getElementById("inspect-modal-company").innerText = ` | ${entry.company || ''}`;
  document.getElementById("inspect-modal-tier").innerText = entry.tier || "";
  document.getElementById("inspect-modal-date").innerText = entry.created_at ? entry.created_at.substring(0, 16).replace("T", " ") : "";
  document.getElementById("inspect-modal-source").innerText = `Source: ${entry.source_type || 'Resume'}`;

  document.getElementById("inspect-modal-before").innerText = `${Math.round(entry.match_score_before)}%`;
  document.getElementById("inspect-modal-after").innerText = `${Math.round(entry.match_score_after)}%`;

  // Download links
  const docxBtn = document.getElementById("inspect-btn-download-docx");
  docxBtn.href = `/api/resume/download/${entry.id}/docx`;
  docxBtn.setAttribute("download", entry.filename || `Resume_${entry.id}.docx`);

  const txtBtn = document.getElementById("inspect-btn-download-txt");
  txtBtn.href = `/api/resume/download/${entry.id}/txt`;
  txtBtn.setAttribute("download", (entry.filename || `Resume_${entry.id}.docx`).replace(".docx", ".txt"));

  document.getElementById("inspect-btn-link-funnel").onclick = () => openLinkFunnelModal(entry.id);

  // Formatted View
  const formattedBox = document.getElementById("inspect-view-formatted");
  if (entry.ats_json && Object.keys(entry.ats_json).length > 0) {
    const previewData = {
      full_name: entry.ats_json.contact_information?.name || "Candidate",
      contact: entry.ats_json.contact_information,
      summary: entry.ats_json.professional_summary,
      skills: entry.ats_json.skills?.categories,
      experiences: entry.ats_json.work_experience,
      projects: entry.ats_json.projects,
      education: entry.ats_json.education,
      certifications: entry.ats_json.certifications
    };
    formattedBox.innerHTML = renderResumeDocumentHTML(previewData);
  } else {
    formattedBox.innerHTML = `<pre style="white-space:pre-wrap; font-family:monospace; font-size:11px;">${escapeHtml(entry.resume_text || '')}</pre>`;
  }

  // Changes Log View
  const diffBox = document.getElementById("inspect-changes-list");
  diffBox.innerHTML = "";
  if (entry.changes_summary && entry.changes_summary.length > 0) {
    entry.changes_summary.forEach(c => {
      const item = document.createElement("div");
      item.className = "change-item";
      item.innerHTML = `
        <div class="change-item-header">
          <span class="change-item-section">📍 ${escapeHtml(c.section || 'General')}</span>
          <span class="badge badge-nice">${escapeHtml(c.type || 'Modification')}</span>
        </div>
        <div class="change-item-detail">${escapeHtml(c.detail)}</div>
      `;
      diffBox.appendChild(item);
    });
  } else {
    diffBox.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:10px;">No detailed changes recorded.</div>`;
  }

  // Raw Text View
  document.getElementById("inspect-raw-text").value = entry.resume_text || "";

  modal.classList.add("active");
}

async function openLinkFunnelModal(ledgerId) {
  // Fetch applications in funnel
  try {
    const resp = await fetch("/api/funnel");
    if (!resp.ok) return;
    const data = await resp.json();
    const apps = data.applications || [];

    if (apps.length === 0) {
      alert("No job applications currently in your funnel. Add an application in Tab 8 first!");
      switchToTab("tab-funnel");
      return;
    }

    const appOptions = apps.map(a => `${a.id}: ${a.role} at ${a.company} (${a.stage})`).join("\n");
    const chosen = prompt(`Enter the Application ID to link this tailored resume to:\n\n${appOptions}`);
    if (!chosen) return;

    const appId = parseInt(chosen.trim().split(":")[0]);
    if (isNaN(appId)) {
      alert("Invalid Application ID entered.");
      return;
    }

    const linkResp = await fetch(`/api/resume/ledger/${ledgerId}/link-funnel`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ application_id: appId })
    });

    if (!linkResp.ok) throw new Error("Link failed");
    showToast(`Linked tailored resume to application #${appId}!`);
    loadResumeLedger();
  } catch (e) {
    alert(`Failed to link to funnel: ${e.message}`);
  }
}

async function deleteLedgerRow(ledgerId) {
  if (!confirm("Permanently delete this tailored resume version from the ledger?")) return;
  try {
    const resp = await fetch(`/api/resume/ledger/${ledgerId}`, { method: "DELETE" });
    if (!resp.ok) throw new Error("Delete failed");
    showToast("Resume version deleted from ledger.");
    loadResumeLedger();
  } catch (e) {
    alert(`Delete error: ${e.message}`);
  }
}

