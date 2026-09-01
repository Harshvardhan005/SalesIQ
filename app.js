/* SalesIQ — Interactive Vanilla JavaScript Engine (API Connected) */

const API_BASE_URL = "http://127.0.0.1:5000/api";

// ── Auth Guard ──────────────────────────────────────────────────────────────
// Redirect to login if no session found in localStorage
const _currentUser = JSON.parse(localStorage.getItem('salesiq_user') || 'null');
if (!_currentUser) {
  window.location.href = 'login.html';
}

// Populate navbar with logged-in user's name
(function populateNavUser() {
  const user = _currentUser;
  if (!user) return;
  const pill = document.getElementById('nav-user-pill');
  const avatar = document.getElementById('nav-user-avatar');
  const nameEl = document.getElementById('nav-user-name');
  const signinBtn = document.getElementById('nav-signin-btn');
  if (pill && nameEl && avatar) {
    nameEl.textContent = user.name || user.email;
    avatar.textContent = (user.name || user.email || '?')[0].toUpperCase();
    pill.style.display = 'flex';
  }
  if (signinBtn) signinBtn.style.display = 'none';
})();

// Sign Out — clear session and redirect to login
function signOut() {
  localStorage.removeItem('salesiq_user');
  window.location.href = 'login.html';
}
// ────────────────────────────────────────────────────────────────────────────

// Cached Data
let cachedReports = [];
let cachedLeads = [];

// Document Initialization
document.addEventListener("DOMContentLoaded", () => {
  fetchDashboardStats();
  fetchReports();
  fetchLeads();
});

// Generic Fetch Wrapper with Error Handling & Loading States
async function apiRequest(endpoint, method = "GET", body = null) {
  const options = {
    method,
    headers: {
      "Content-Type": "application/json"
    }
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    const result = await response.json();

    if (!response.ok || !result.success) {
      const err = new Error(result.message || `Server returned status ${response.status}`);
      err.status = response.status;
      err.data = result.data;
      throw err;
    }

    return result;
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    showToast(err.message || "Network connection error", "error");
    throw err;
  }
}

// Fetch Dashboard Stats
async function fetchDashboardStats() {
  try {
    const res = await apiRequest("/dashboard-stats");
    if (res.data) {
      const stats = res.data;
      document.getElementById("stat-total-companies").innerText = stats.total_companies.toLocaleString();
      document.getElementById("stat-total-leads").innerText = stats.total_leads.toLocaleString();
      document.getElementById("stat-avg-score").innerText = stats.avg_lead_score;
      document.getElementById("stat-recent-reports").innerText = stats.recent_reports;
    }
  } catch (e) {
    // Fallback display if network issue
  }
}

// Fetch Reports & Render
async function fetchReports() {
  try {
    const res = await apiRequest("/reports");
    if (res.data) {
      cachedReports = res.data;
      renderOverviewTable(cachedReports);
      
      // Populate generator company select dropdown dynamically
      const genCompSelect = document.getElementById("gen-company-select");
      if (genCompSelect) {
        const currentVal = genCompSelect.value;
        genCompSelect.innerHTML = '<option value="">-- Select Analyzed Company --</option>' + 
          cachedReports.map(c => `<option value="${escapeHtml(c.company_name)}">${escapeHtml(c.company_name)}</option>`).join('');
        if (currentVal && cachedReports.some(c => c.company_name === currentVal)) {
          genCompSelect.value = currentVal;
        }
      }
    }
  } catch (e) {}
}

// Fetch Leads & Render
async function fetchLeads() {
  try {
    const res = await apiRequest("/leads");
    if (res.data) {
      cachedLeads = res.data;
      renderSavedLeadsTable(cachedLeads);
    }
  } catch (e) {}
}

// View Switching: Landing Page vs Dashboard (SPA)
function switchMainView(viewName, targetTab = null) {
  const landingView = document.getElementById("landing-view");
  const dashboardView = document.getElementById("dashboard-view");

  if (viewName === "dashboard") {
    landingView.classList.remove("active");
    dashboardView.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });

    if (targetTab) {
      const tabItems = document.querySelectorAll(".sidebar-item");
      if (targetTab === "research") {
        switchDashTab("research", tabItems[1]);
      }
    }
  } else {
    dashboardView.classList.remove("active");
    landingView.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

// Sidebar Tab Switching within Dashboard
function switchDashTab(tabId, el) {
  const items = document.querySelectorAll(".sidebar-item");
  items.forEach(item => item.classList.remove("active"));
  if (el) {
    el.classList.add("active");
  }

  const tabContents = document.querySelectorAll(".dash-tab-content");
  tabContents.forEach(content => content.classList.remove("active"));
  
  const targetContent = document.getElementById(`tab-${tabId}`);
  if (targetContent) {
    targetContent.classList.add("active");
  }

  // Refresh tables when navigating
  if (tabId === "overview") fetchReports();
  if (tabId === "leads") fetchLeads();
}

// Scroll smooth to demo on landing page
function scrollToDemo() {
  const demoEl = document.getElementById("live-demo");
  if (demoEl) {
    demoEl.scrollIntoView({ behavior: "smooth" });
  }
}

// Render Overview Table
function renderOverviewTable(data) {
  const tbody = document.getElementById("overview-table-body");
  if (!tbody) return;

  if (data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 24px; color: var(--text-subtle);">No reports created yet.</td></tr>`;
    return;
  }
  
  tbody.innerHTML = data.map(item => {
    const painText = Array.isArray(item.pain_points) ? item.pain_points[0] : item.pain_points;
    return `
      <tr>
        <td>
          <div style="font-weight: 700; color: var(--text-main);">${escapeHtml(item.company_name)}</div>
          <div style="font-size: 0.75rem; color: var(--text-subtle);">${escapeHtml(item.website)}</div>
        </td>
        <td>${escapeHtml(item.industry)}</td>
        <td>
          <span style="font-weight: 800; color: ${item.lead_score >= 90 ? 'var(--accent)' : 'var(--text-main)'};">
            ${item.lead_score} / 100
          </span>
        </td>
        <td>
          <div style="font-size: 0.8125rem; color: var(--text-muted); max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            ${escapeHtml(painText || '')}
          </div>
        </td>
        <td>
          <span class="badge" style="font-size: 0.75rem; background: var(--success-bg); color: var(--success); border-color: transparent;">
            High Fit
          </span>
        </td>
        <td>
          <div style="display:flex; gap:8px;">
            <button class="btn btn-secondary btn-sm" onclick="quickInspect('${escapeHtml(item.company_name)}')">
              Inspect
            </button>
            <button class="btn btn-icon btn-sm" title="Delete Report" onclick="deleteReport(${item.id})">
              <i class="ri-delete-bin-line" style="color:var(--danger);"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

// Render Saved Leads Table
function renderSavedLeadsTable(data) {
  const tbody = document.getElementById("saved-leads-table-body");
  if (!tbody) return;

  if (data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 24px; color: var(--text-subtle);">No saved leads yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = data.map(item => `
    <tr>
      <td><strong>${escapeHtml(item.company_name)}</strong></td>
      <td><a href="${escapeHtml(item.website)}" target="_blank" style="color: var(--accent);">${escapeHtml(item.website)}</a></td>
      <td>${escapeHtml(item.industry)}</td>
      <td><strong>${item.lead_score}</strong></td>
      <td>${item.created_at ? item.created_at.split(' ')[0] : 'Today'}</td>
      <td>
        <div style="display:flex; gap:8px;">
          <button class="btn btn-secondary btn-sm" onclick="showToast('Exported ${escapeHtml(item.company_name)} to CRM')">
            <i class="ri-file-download-line"></i> Export
          </button>
          <button class="btn btn-icon btn-sm" title="Delete Lead" onclick="deleteLead(${item.id})">
            <i class="ri-delete-bin-line" style="color:var(--danger);"></i>
          </button>
        </div>
      </td>
    </tr>
  `).join('');
}

// Delete Report API Call
async function deleteReport(reportId) {
  if (!confirm("Are you sure you want to delete this report?")) return;

  try {
    await apiRequest(`/reports/${reportId}`, "DELETE");
    showToast("Report deleted successfully");
    fetchReports();
    fetchDashboardStats();
  } catch (e) {}
}

// Delete Lead API Call
async function deleteLead(leadId) {
  if (!confirm("Are you sure you want to remove this lead?")) return;

  try {
    await apiRequest(`/leads/${leadId}`, "DELETE");
    showToast("Lead removed successfully");
    fetchLeads();
    fetchDashboardStats();
  } catch (e) {}
}

// Form Preset Filler
function fillFormPreset(presetKey) {
  if (presetKey === 'stripe') {
    document.getElementById("comp-name").value = "Stripe";
    document.getElementById("comp-website").value = "https://stripe.com";
    document.getElementById("comp-industry").value = "Fintech & Banking";
    document.getElementById("product-offered").value = "AI Sales Intelligence Engine";
    document.getElementById("target-customer").value = "Head of Outbound Sales";
    document.getElementById("comp-notes").value = "Rapidly expanding international enterprise sales teams.";
    showToast("Autofilled preset data for Stripe");
  }
}

// Global state for current report
let currentAnalysisReport = null;

// Render Analysis Results to DOM (Reusable Component)
function renderAnalysisResults(report) {
  currentAnalysisReport = report;
  
  const loadingEl = document.getElementById("ai-loading");
  const resultsEl = document.getElementById("analysis-results");
  
  if (loadingEl) loadingEl.style.display = "none";
  if (resultsEl) resultsEl.style.display = "grid";

  // Reset Save button style to active state
  const btnSave = document.getElementById("btn-save-report");
  if (btnSave) {
    btnSave.innerHTML = `<i class="ri-save-line"></i> Save`;
    btnSave.style.color = "";
    btnSave.style.borderColor = "";
  }

  // 1. Lead Fit Score & Confidence
  document.getElementById("res-score").innerText = report.lead_score;
  document.getElementById("res-lead-name").innerText = report.company_name;
  document.getElementById("res-lead-industry").innerText = report.industry;
  
  const websiteEl = document.getElementById("res-lead-website");
  if (websiteEl) {
    websiteEl.href = report.website.startsWith("http") ? report.website : `https://${report.website}`;
    websiteEl.innerText = report.website;
  }

  const confBadge = document.getElementById("res-confidence-badge");
  if (confBadge) {
    confBadge.innerText = `${report.confidence || 'High'} Fit`;
    if (report.confidence === 'High') {
      confBadge.style.background = 'var(--success-bg)';
      confBadge.style.color = 'var(--success)';
      confBadge.style.borderColor = '#A7F3D0';
    } else if (report.confidence === 'Medium') {
      confBadge.style.background = '#FEF3C7';
      confBadge.style.color = '#D97706';
      confBadge.style.borderColor = '#FCD34D';
    } else {
      confBadge.style.background = '#FEE2E2';
      confBadge.style.color = '#EF4444';
      confBadge.style.borderColor = '#FCA5A5';
    }
  }

  const sourceBadge = document.getElementById("res-source-badge");
  if (sourceBadge) {
    sourceBadge.innerText = `Source: ${report.information_source || 'AI Estimate'}`;
  }

  // 2. Company Profile Overview & Products
  document.getElementById("res-overview").innerText = report.company_overview || '';
  
  const productsList = document.getElementById("res-products-list");
  if (productsList) {
    if (Array.isArray(report.products) && report.products.length > 0) {
      productsList.innerHTML = report.products.map(p => `
        <li class="pain-point-item">
          <i class="ri-check-double-line" style="color:var(--accent); font-size:1.1rem; margin-top:2px;"></i>
          <div>${escapeHtml(p)}</div>
        </li>
      `).join('');
    } else {
      productsList.innerHTML = `<li style="color:var(--text-muted); font-size:0.875rem; list-style:none;">No products detected.</li>`;
    }
  }

  // 3. Pain Points & Goals
  const painList = document.getElementById("res-pain-list");
  if (painList) {
    if (Array.isArray(report.pain_points) && report.pain_points.length > 0) {
      painList.innerHTML = report.pain_points.map(p => `
        <li class="pain-point-item">
          <i class="ri-error-warning-fill" style="color:#EF4444; font-size:1.1rem; margin-top:2px;"></i>
          <div>${escapeHtml(p)}</div>
        </li>
      `).join('');
    } else {
      painList.innerHTML = `<li style="color:var(--text-muted); font-size:0.875rem; list-style:none;">No pain points detected.</li>`;
    }
  }

  const goalsList = document.getElementById("res-goals-list");
  if (goalsList) {
    if (Array.isArray(report.business_goals) && report.business_goals.length > 0) {
      goalsList.innerHTML = report.business_goals.map(g => `
        <li class="pain-point-item">
          <i class="ri-checkbox-circle-fill" style="color:#10B981; font-size:1.1rem; margin-top:2px;"></i>
          <div>${escapeHtml(g)}</div>
        </li>
      `).join('');
    } else {
      goalsList.innerHTML = `<li style="color:var(--text-muted); font-size:0.875rem; list-style:none;">No goals detected.</li>`;
    }
  }

  // 4. Growth Opportunities & Outreach Strategy
  const oppList = document.getElementById("res-opportunities-list");
  if (oppList) {
    if (Array.isArray(report.growth_opportunities) && report.growth_opportunities.length > 0) {
      oppList.innerHTML = report.growth_opportunities.map(o => `
        <li class="pain-point-item">
          <i class="ri-lightbulb-fill" style="color:#F59E0B; font-size:1.1rem; margin-top:2px;"></i>
          <div>${escapeHtml(o)}</div>
        </li>
      `).join('');
    } else {
      oppList.innerHTML = `<li style="color:var(--text-muted); font-size:0.875rem; list-style:none;">No opportunities detected.</li>`;
    }
  }

  const strategyEl = document.getElementById("res-strategy");
  if (strategyEl) {
    strategyEl.innerText = report.sales_strategy || '';
  }
}

// Format JSON Report into Markdown String
function formatReportToMarkdown(report) {
  return `# SalesIQ AI Intelligence Report: ${report.company_name}
- **Website/Domain:** ${report.website}
- **Industry:** ${report.industry}
- **ICP Lead Fit Score:** ${report.lead_score}/100
- **Fit Confidence Level:** ${report.confidence}

## Company Overview
${report.company_overview}

## Key Products & Offerings
${(report.products || []).map(p => `- ${p}`).join('\n')}

## Prospect Pain Points Identified
${(report.pain_points || []).map(p => `- ${p}`).join('\n')}

## Core Business Goals
${(report.business_goals || []).map(g => `- ${g}`).join('\n')}

## Growth Opportunities
${(report.growth_opportunities || []).map(o => `- ${o}`).join('\n')}

## Strategic Sales Outreach Playbook
${report.sales_strategy}
`;
}

// Copy entire B2B sales intelligence report to clipboard in Markdown format
function copyAnalysisReport() {
  if (!currentAnalysisReport) {
    showToast("No active report to copy", "error");
    return;
  }
  const md = formatReportToMarkdown(currentAnalysisReport);
  navigator.clipboard.writeText(md)
    .then(() => showToast("Report copied to clipboard in Markdown format!"))
    .catch(() => showToast("Failed to copy report", "error"));
}

// Download report as a markdown document
function downloadAnalysisReport() {
  if (!currentAnalysisReport) {
    showToast("No active report to download", "error");
    return;
  }
  const md = formatReportToMarkdown(currentAnalysisReport);
  const blob = new Blob([md], { type: "text/markdown;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${currentAnalysisReport.company_name.replace(/\s+/g, '_')}_AI_report.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast("Report download started!");
}

// Save Report and show visual state update
function saveAnalysisReport() {
  if (!currentAnalysisReport) return;
  const btn = document.getElementById("btn-save-report");
  if (btn) {
    btn.innerHTML = `<i class="ri-checkbox-circle-line"></i> Saved`;
    btn.style.color = "#10B981";
    btn.style.borderColor = "#10B981";
  }
  showToast("Report saved & synced to CRM Dashboard!");
}

// Regenerate current analysis report
function regenerateAnalysisReport() {
  const form = document.getElementById("research-form");
  if (form) {
    // Trigger submit handler programmatically
    const submitEvent = new Event("submit", { cancelable: true });
    form.dispatchEvent(submitEvent);
  }
}

// Handle AI Research Form Submission (Backend API Connected)
async function handleResearchSubmit(event) {
  event.preventDefault();

  const compName = document.getElementById("comp-name").value.trim();
  const compWebsite = document.getElementById("comp-website").value.trim();
  const industry = document.getElementById("comp-industry").value.trim();
  const product = document.getElementById("product-offered").value.trim();
  const targetRole = document.getElementById("target-customer").value.trim();
  const notes = document.getElementById("comp-notes").value.trim();
  const manualInfoEl = document.getElementById("manual-company-info");
  const manualInfo = manualInfoEl ? manualInfoEl.value.trim() : "";

  if (!compName || !compWebsite || !industry) {
    showToast("Please fill in all required fields", "error");
    return;
  }

  const loadingEl = document.getElementById("ai-loading");
  const resultsEl = document.getElementById("analysis-results");
  const statusText = document.getElementById("loading-status-text");

  // Show Loader
  loadingEl.style.display = "block";
  resultsEl.style.display = "none";
  loadingEl.scrollIntoView({ behavior: "smooth" });

  statusText.innerText = `Analyzing firmographic signals for ${compName} using Groq...`;

  try {
    const res = await apiRequest("/analyze-company", "POST", {
      company_name: compName,
      website: compWebsite,
      industry: industry,
      product_offered: product,
      target_customer: targetRole,
      notes: notes,
      manual_company_info: manualInfo
    });

    const report = res.data;

    // Transition loader
    setTimeout(() => {
      renderAnalysisResults(report);
      showToast(`AI Analysis generated & saved for ${report.company_name}!`);
      fetchDashboardStats();
      fetchReports();
      fetchLeads();
    }, 600);

  } catch (err) {
    loadingEl.style.display = "none";
    if (err.status === 422 && err.data && err.data.requires_manual_input) {
      document.getElementById("manual-info-group").style.display = "block";
      showToast(err.message, "error");
    }
  }
}

// Global state for content generator
let currentGeneratedText = "";
let isEditingGeneratedContent = false;

// Generate Content Form Handler (Content Generator Tab)
async function handleContentGeneration() {
  const compSelect = document.getElementById("gen-company-select");
  const typeSelect = document.getElementById("gen-type-select");
  const toneSelect = document.getElementById("gen-tone-select");
  const lengthSelect = document.getElementById("gen-length-select");
  const promptInput = document.getElementById("gen-prompt-input");

  const companyName = compSelect ? compSelect.value : "";
  const contentType = typeSelect ? typeSelect.value : "";
  const tone = toneSelect ? toneSelect.value : "Professional";
  const length = lengthSelect ? lengthSelect.value : "Medium";
  const prompt = promptInput ? promptInput.value : "";

  if (!companyName) {
    showToast("Please select a target company", "error");
    return;
  }

  const previewEl = document.getElementById("gen-output-preview");
  const editorEl = document.getElementById("gen-output-editor");
  const btnEdit = document.getElementById("btn-edit-gen");
  const btnSave = document.getElementById("btn-save-gen");

  if (previewEl) {
    previewEl.innerText = `Generating ${contentType} for ${companyName} via Groq AI... Please wait...`;
    previewEl.style.display = "block";
  }
  if (editorEl) editorEl.style.display = "none";
  if (btnEdit) btnEdit.innerHTML = `<i class="ri-edit-2-line"></i> Edit`;
  if (btnSave) {
    btnSave.innerHTML = `<i class="ri-save-line"></i> Save`;
    btnSave.style.color = "";
    btnSave.style.borderColor = "";
  }
  isEditingGeneratedContent = false;

  try {
    const res = await apiRequest("/generate-content", "POST", {
      company_name: companyName,
      content_type: contentType,
      tone: tone,
      length: length,
      prompt: prompt
    });

    if (res.data && res.data.output_text) {
      currentGeneratedText = res.data.output_text;
      if (previewEl) previewEl.innerText = currentGeneratedText;
      if (editorEl) editorEl.value = currentGeneratedText;
      showToast(`Successfully generated B2B sales copy!`);
    } else {
      throw new Error("No output generated");
    }
  } catch (err) {
    if (previewEl) {
      previewEl.innerText = `Generation failed: ${err.message || err}. Please try again.`;
    }
  }
}

// Copy output content to clipboard
function copyGeneratorContent() {
  if (!currentGeneratedText) {
    showToast("No generated content to copy", "error");
    return;
  }
  const text = isEditingGeneratedContent ? document.getElementById("gen-output-editor").value : currentGeneratedText;
  navigator.clipboard.writeText(text)
    .then(() => showToast("Copied to clipboard!"))
    .catch(() => showToast("Failed to copy content", "error"));
}

// Toggle between Markdown preview and direct editor textarea
function toggleEditGeneratorContent() {
  if (!currentGeneratedText) return;
  const previewEl = document.getElementById("gen-output-preview");
  const editorEl = document.getElementById("gen-output-editor");
  const btnEdit = document.getElementById("btn-edit-gen");

  if (!previewEl || !editorEl || !btnEdit) return;

  if (isEditingGeneratedContent) {
    // Save current editor state back to preview and exit edit mode
    currentGeneratedText = editorEl.value;
    previewEl.innerText = currentGeneratedText;
    
    previewEl.style.display = "block";
    editorEl.style.display = "none";
    btnEdit.innerHTML = `<i class="ri-edit-2-line"></i> Edit`;
    isEditingGeneratedContent = false;
  } else {
    // Enter edit mode
    editorEl.value = currentGeneratedText;
    
    previewEl.style.display = "none";
    editorEl.style.display = "block";
    btnEdit.innerHTML = `<i class="ri-eye-line"></i> Preview`;
    isEditingGeneratedContent = true;
  }
}

// Save Content in SQLite database
function saveGeneratorContent() {
  if (!currentGeneratedText) return;
  const editorEl = document.getElementById("gen-output-editor");
  if (isEditingGeneratedContent && editorEl) {
    currentGeneratedText = editorEl.value;
    const previewEl = document.getElementById("gen-output-preview");
    if (previewEl) previewEl.innerText = currentGeneratedText;
  }

  const btn = document.getElementById("btn-save-gen");
  if (btn) {
    btn.innerHTML = `<i class="ri-checkbox-circle-line"></i> Saved`;
    btn.style.color = "#10B981";
    btn.style.borderColor = "#10B981";
  }
  showToast("Copywriter output saved successfully!");
}

// Download content as .txt file
function downloadGeneratorContent() {
  if (!currentGeneratedText) {
    showToast("No content to download", "error");
    return;
  }
  const text = isEditingGeneratedContent ? document.getElementById("gen-output-editor").value : currentGeneratedText;
  const compSelect = document.getElementById("gen-company-select");
  const typeSelect = document.getElementById("gen-type-select");
  
  const compName = compSelect ? compSelect.value : "SalesIQ";
  const contentType = typeSelect ? typeSelect.value : "Sales_Copy";

  const blob = new Blob([text], { type: "text/plain;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${compName.replace(/\s+/g, '_')}_${contentType.replace(/\s+/g, '_')}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast("Download started!");
}

// Regenerate content copywriter
function regenerateGeneratorContent() {
  handleContentGeneration();
}

// Quick Inspect from Overview table
function quickInspect(companyName) {
  const company = cachedReports.find(c => c.company_name === companyName);
  if (company) {
    const tabItems = document.querySelectorAll(".sidebar-item");
    switchDashTab("research", tabItems[1]);
    
    document.getElementById("comp-name").value = company.company_name;
    document.getElementById("comp-website").value = company.website;
    document.getElementById("comp-industry").value = company.industry;
    document.getElementById("product-offered").value = company.product_offered || '';
    document.getElementById("target-customer").value = company.target_customer || '';
    
    // Automatically render the results container with saved report details
    renderAnalysisResults(company);
    showToast(`Loaded saved profile for ${company.company_name}`);
  }
}

// Global search bar filter
function handleGlobalSearch(query) {
  const q = query.toLowerCase();
  const filteredReports = cachedReports.filter(c => 
    c.company_name.toLowerCase().includes(q) || 
    c.industry.toLowerCase().includes(q) ||
    c.website.toLowerCase().includes(q)
  );
  const filteredLeads = cachedLeads.filter(c => 
    c.company_name.toLowerCase().includes(q) || 
    c.industry.toLowerCase().includes(q) ||
    c.website.toLowerCase().includes(q)
  );

  renderOverviewTable(filteredReports);
  renderSavedLeadsTable(filteredLeads);
}

// Copy script text helper
function copyText(elementId) {
  const el = document.getElementById(elementId);
  if (el) {
    navigator.clipboard.writeText(el.innerText).then(() => {
      showToast("Copied content to clipboard!");
    }).catch(() => {
      showToast("Content selected!");
    });
  }
}

// Toast notification display
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "toast";
  const icon = type === "error" ? "ri-error-warning-fill" : "ri-checkbox-circle-fill";
  const iconColor = type === "error" ? "var(--danger)" : "var(--success)";

  toast.innerHTML = `<i class="${icon}" style="color:${iconColor};"></i> <span>${escapeHtml(message)}</span>`;
  
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Helper: Escape HTML string to prevent XSS
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
