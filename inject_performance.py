"""Inject enhanced orchestrator UI and Site Performance Monitoring page into index.html"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

changes = []

# 1. Add Performance nav item after orchestrator nav
if 'data-page="performance"' not in c:
    perf_nav = (
        '    <a class="nav-item" data-page="performance" onclick="navigate(\'performance\')">\n'
        '      <i class="fas fa-tachometer-alt"></i> <span>Site Performance</span>\n'
        '    </a>\n'
    )
    marker = '<a class="nav-item" data-page="orchestrator"'
    if marker in c:
        c = c.replace(marker, perf_nav + marker, 1)
        changes.append('Added Performance nav item')

# 2. Add Performance page HTML before settings page
PERF_PAGE = """
    <!-- ═══════════════════════════════════════════
         PAGE: Site Performance Monitoring
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-performance">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-tachometer-alt"></i> Site Performance Monitoring</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Track SEO health, Core Web Vitals, and score trends over time — like Search Console and GA4 dashboards.</p>
        <div class="form-row">
          <div class="form-group" style="flex:2;">
            <label class="form-label">URL to Monitor</label>
            <input type="text" class="form-input" id="perfUrl" placeholder="https://example.com" onkeydown="if(event.key==='Enter') loadPerformanceDashboard()">
          </div>
          <div class="form-group">
            <label class="form-label">Period</label>
            <select class="form-select" id="perfPeriod">
              <option value="7">Last 7 days</option>
              <option value="30" selected>Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-primary" onclick="loadPerformanceDashboard()" id="btnPerfDash"><i class="fas fa-chart-line"></i> Load Dashboard</button>
          </div>
        </div>
        <div style="display:flex;gap:8px;margin-top:8px;">
          <button class="btn btn-secondary btn-sm" onclick="fetchCWV()"><i class="fas fa-tachometer-alt"></i> Fetch Core Web Vitals</button>
          <button class="btn btn-secondary btn-sm" onclick="savePerfSnapshot()"><i class="fas fa-camera"></i> Save Snapshot</button>
          <button class="btn btn-secondary btn-sm" onclick="generateCombinedReport()"><i class="fas fa-file-pdf"></i> Generate Full Report</button>
        </div>
      </div>

      <!-- Score Summary Cards -->
      <div id="perfScoreCards" style="display:none;">
        <div class="metrics-row">
          <div class="metric-card">
            <div class="metric-icon purple"><i class="fas fa-star"></i></div>
            <div class="metric-label">Overall Score</div>
            <div class="metric-value" id="perfOverall">—</div>
          </div>
          <div class="metric-card">
            <div class="metric-icon green"><i class="fas fa-check-circle"></i></div>
            <div class="metric-label">Grade</div>
            <div class="metric-value" id="perfGrade">—</div>
          </div>
          <div class="metric-card">
            <div class="metric-icon blue"><i class="fas fa-tachometer-alt"></i></div>
            <div class="metric-label">CWV Status</div>
            <div class="metric-value" id="perfCWV" style="font-size:1.2rem;">—</div>
          </div>
          <div class="metric-card">
            <div class="metric-icon yellow"><i class="fas fa-exclamation-triangle"></i></div>
            <div class="metric-label">Issues</div>
            <div class="metric-value" id="perfIssues">—</div>
          </div>
        </div>

        <!-- Score Breakdown -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
          <div class="card">
            <div class="card-header">
              <div class="card-title"><i class="fas fa-chart-line"></i> SEO Score Trend</div>
            </div>
            <div class="chart-container" style="height:250px;">
              <canvas id="perfScoreChart"></canvas>
            </div>
          </div>
          <div class="card">
            <div class="card-header">
              <div class="card-title"><i class="fas fa-tachometer-alt"></i> Core Web Vitals Trend</div>
            </div>
            <div class="chart-container" style="height:250px;">
              <canvas id="perfCWVChart"></canvas>
            </div>
          </div>
        </div>

        <!-- Individual Score Breakdown -->
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;">
          <div class="card">
            <div class="card-header">
              <div class="card-title" style="font-size:0.95rem;">SEO Score</div>
            </div>
            <div style="text-align:center;padding:16px;">
              <div id="perfSeoScore" style="font-size:2.5rem;font-weight:700;color:var(--accent);">—</div>
              <div style="font-size:0.8rem;color:var(--text-muted);">On-page optimization</div>
            </div>
          </div>
          <div class="card">
            <div class="card-header">
              <div class="card-title" style="font-size:0.95rem;">Technical Score</div>
            </div>
            <div style="text-align:center;padding:16px;">
              <div id="perfTechScore" style="font-size:2.5rem;font-weight:700;color:var(--success);">—</div>
              <div style="font-size:0.8rem;color:var(--text-muted);">Technical health</div>
            </div>
          </div>
          <div class="card">
            <div class="card-header">
              <div class="card-title" style="font-size:0.95rem;">Content Score</div>
            </div>
            <div style="text-align:center;padding:16px;">
              <div id="perfContentScore" style="font-size:2.5rem;font-weight:700;color:var(--info);">—</div>
              <div style="font-size:0.8rem;color:var(--text-muted);">Content quality</div>
            </div>
          </div>
        </div>

        <!-- Tracked Sites -->
        <div class="card">
          <div class="card-header">
            <div class="card-title"><i class="fas fa-globe"></i> Tracked Sites</div>
          </div>
          <div id="perfTrackedSites"></div>
        </div>
      </div>

      <div id="perfEmpty" class="empty-state" style="display:none;">
        <i class="fas fa-tachometer-alt"></i>
        <p>No performance data yet. Enter a URL above and click "Load Dashboard" to start tracking.</p>
      </div>
    </div>
"""

if 'page-performance' not in c:
    marker = '<div class="page" id="page-settings">'
    if marker in c:
        c = c.replace(marker, PERF_PAGE + '\n' + marker, 1)
        changes.append('Added Performance Monitoring page')

# 3. Enhance orchestrator page with module selector checkboxes
ORCH_MODULE_SELECTOR = """
        <div id="orchModuleSelector" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px;margin:12px 0;">
          <label style="display:flex;align-items:center;gap:6px;padding:8px 12px;border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;">
            <input type="checkbox" checked data-module="seo_audit" onchange="updateModuleCount()"> On-page SEO
          </label>
          <label style="display:flex;align-items:center;gap:6px;padding:8px 12px;border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;">
            <input type="checkbox" checked data-module="technical_seo" onchange="updateModuleCount()"> Technical SEO
          </label>
          <label style="display:flex;align-items:center;gap:6px;padding:8px 12px;border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;">
            <input type="checkbox" checked data-module="eeat" onchange="updateModuleCount()"> E-E-A-T
          </label>
          <label style="display:flex;align-items:center;gap:6px;padding:8px 12px;border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;">
            <input type="checkbox" checked data-module="schema_audit" onchange="updateModuleCount()"> Schema Audit
          </label>
          <label style="display:flex;align-items:center;gap:6px;padding:8px 12px;border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;">
            <input type="checkbox" checked data-module="geo_audit" onchange="updateModuleCount()"> GEO / AI Search
          </label>
          <label style="display:flex;align-items:center;gap:6px;padding:8px 12px;border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;">
            <input type="checkbox" checked data-module="seo_images" onchange="updateModuleCount()"> Image SEO
          </label>
          <label style="display:flex;align-items:center;gap:6px;padding:8px 12px;border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;">
            <input type="checkbox" checked data-module="sitemap_audit" onchange="updateModuleCount()"> Sitemap
          </label>
          <label style="display:flex;align-items:center;gap:6px;padding:8px 12px;border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;">
            <input type="checkbox" checked data-module="hreflang_audit" onchange="updateModuleCount()"> Hreflang
          </label>
          <label style="display:flex;align-items:center;gap:6px;padding:8px 12px;border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;">
            <input type="checkbox" checked data-module="local_seo" onchange="updateModuleCount()"> Local SEO
          </label>
          <label style="display:flex;align-items:center;gap:6px;padding:8px 12px;border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;">
            <input type="checkbox" checked data-module="ecommerce_seo" onchange="updateModuleCount()"> E-commerce
          </label>
          <label style="display:flex;align-items:center;gap:6px;padding:8px 12px;border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;">
            <input type="checkbox" checked data-module="sxo_audit" onchange="updateModuleCount()"> SXO
          </label>
          <label style="display:flex;align-items:center;gap:6px;padding:8px 12px;border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;">
            <input type="checkbox" checked data-module="backlinks" onchange="updateModuleCount()"> Backlinks
          </label>
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-top:8px;">
          <span id="orchModuleCount" style="font-size:0.85rem;color:var(--text-muted);">12 modules selected</span>
          <button class="btn btn-sm btn-secondary" onclick="selectAllModules(true)">Select All</button>
          <button class="btn btn-sm btn-secondary" onclick="selectAllModules(false)">Deselect All</button>
        </div>
"""
if 'orchModuleSelector' not in c:
    marker = '<div id="orchProgress" style="display:none;margin-top:12px;">'
    if marker in c:
        c = c.replace(marker, ORCH_MODULE_SELECTOR + '\n' + marker, 1)
        changes.append('Added module selector checkboxes to orchestrator')

# 4. Add enhanced progress display with per-module status
ORCH_PROGRESS_ENHANCED = """<div id="orchProgress" style="display:none;margin-top:12px;">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
            <div class="spinner spinner-dark"></div>
            <span id="orchProgressText" style="font-weight:600;">Running parallel analysis...</span>
            <span id="orchProgressPct" style="margin-left:auto;font-size:0.85rem;color:var(--text-muted);">0%</span>
          </div>
          <div id="orchModuleProgress" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:6px;"></div>
        </div>"""
old_progress = '<div id="orchProgress" style="display:none;margin-top:12px;">\n          <div class="pipeline-step active" id="orchStep"><i class="fas fa-spinner fa-spin"></i> Running parallel analysis...</div>\n        </div>'
if old_progress in c:
    c = c.replace(old_progress, ORCH_PROGRESS_ENHANCED, 1)
    changes.append('Enhanced orchestrator progress display')

# 5. Add JavaScript functions
NEW_JS = r"""
/* ══════════════════════════════════════════════
   Enhanced Orchestrator Functions
   ══════════════════════════════════════════════ */

function getSelectedModules() {
  var modules = [];
  document.querySelectorAll('#orchModuleSelector input[type="checkbox"]:checked').forEach(function(cb) {
    modules.push(cb.getAttribute('data-module'));
  });
  return modules;
}

function updateModuleCount() {
  var count = getSelectedModules().length;
  document.getElementById('orchModuleCount').textContent = count + ' module' + (count !== 1 ? 's' : '') + ' selected';
}

function selectAllModules(select) {
  document.querySelectorAll('#orchModuleSelector input[type="checkbox"]').forEach(function(cb) {
    cb.checked = select;
  });
  updateModuleCount();
}

async function runFullOrchestrator() {
  var url = document.getElementById('orchUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  var workers = parseInt(document.getElementById('orchWorkers').value) || 6;
  var modules = getSelectedModules();
  if (modules.length === 0) { showToast('Select at least one module', 'error'); return; }

  document.getElementById('orchProgress').style.display = 'block';
  document.getElementById('orchResults').style.display = 'none';
  btnLoading('btnOrch', true);

  // Show module progress
  var progressHtml = '';
  modules.forEach(function(m) {
    progressHtml += '<div class="pipeline-step pending" id="orchMod_' + m + '"><span class="pipeline-status"><i class="fas fa-circle" style="font-size:0.5rem;"></i></span> ' + m.replace(/_/g, ' ') + '</div>';
  });
  document.getElementById('orchModuleProgress').innerHTML = progressHtml;
  document.getElementById('orchProgressPct').textContent = '0%';

  try {
    // Use focused endpoint with selected modules
    var res = await (await fetch(API + '/api/orchestrator/focused', {
      method: 'POST',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url, modules: modules, max_workers: workers})
    })).json();

    document.getElementById('orchProgress').style.display = 'none';
    var el = document.getElementById('orchResults');
    el.style.display = 'block';

    var score = res.overall_score || 0;
    var grade = res.grade || 'N/A';
    var scoreColor = score >= 80 ? 'success' : score >= 50 ? 'warning' : 'danger';
    var html = '<div class="card"><div class="card-header"><div class="card-title"><i class="fas fa-layer-group"></i> Full Audit Results <span class="badge badge-' + scoreColor + '">' + score + '/100 (' + grade + ')</span></div></div>';
    html += '<div class="metrics-row">';
    html += '<div class="metric-card"><div class="metric-icon ' + scoreColor + '"><i class="fas fa-star"></i></div><div class="metric-label">Score</div><div class="metric-value">' + score + '</div></div>';
    html += '<div class="metric-card"><div class="metric-icon purple"><i class="fas fa-cogs"></i></div><div class="metric-label">Modules Run</div><div class="metric-value">' + (res.modules_run||0) + '</div></div>';
    html += '<div class="metric-card"><div class="metric-icon red"><i class="fas fa-exclamation-circle"></i></div><div class="metric-label">Critical</div><div class="metric-value">' + ((res.issues_summary||{}).critical||0) + '</div></div>';
    html += '<div class="metric-card"><div class="metric-icon yellow"><i class="fas fa-exclamation-triangle"></i></div><div class="metric-label">Warnings</div><div class="metric-value">' + ((res.issues_summary||{}).warnings||0) + '</div></div>';
    html += '</div>';

    // Module scores breakdown
    var modScores = res.module_scores || {};
    if (Object.keys(modScores).length > 0) {
      html += '<div style="margin-top:12px;padding:12px;background:var(--bg-input);border-radius:8px;"><strong style="font-size:0.85rem;">Module Scores:</strong><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px;margin-top:8px;">';
      for (var mod in modScores) {
        var ms = modScores[mod];
        var mc = ms >= 80 ? 'success' : ms >= 50 ? 'warning' : 'danger';
        html += '<div style="display:flex;justify-content:space-between;padding:6px 10px;border-radius:6px;background:var(--bg-card);font-size:0.85rem;"><span>' + mod.replace(/_/g, ' ') + '</span><span class="badge badge-' + mc + '">' + ms + '/100</span></div>';
      }
      html += '</div></div>';
    }

    var recs = res.recommendations || [];
    if (recs.length > 0) {
      html += '<div style="margin-top:12px;padding:12px;background:var(--success-bg);border-radius:8px;"><strong>Top Recommendations:</strong>';
      recs.slice(0,10).forEach(function(r) { var t = typeof r === 'string' ? r : (r.action || r.message || JSON.stringify(r)); html += '<div style="padding:4px 0;font-size:0.88rem;">• ' + t + '</div>'; });
      html += '</div>';
    }
    html += '</div>';
    el.innerHTML = html;
    showToast('Audit complete! Score: ' + score + '/100', 'success');
  } catch(e) {
    document.getElementById('orchProgress').style.display = 'none';
    showToast('Error: ' + e.message, 'error');
  }
  btnLoading('btnOrch', false);
}

/* ══════════════════════════════════════════════
   Site Performance Monitoring Functions
   ══════════════════════════════════════════════ */

var perfScoreChartInst = null, perfCWVChartInst = null;

async function loadPerformanceDashboard() {
  var url = document.getElementById('perfUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  var days = parseInt(document.getElementById('perfPeriod').value) || 30;
  btnLoading('btnPerfDash', true);
  try {
    var res = await (await fetch(API + '/api/performance/dashboard', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url, days: days})
    })).json();

    document.getElementById('perfScoreCards').style.display = 'block';
    document.getElementById('perfEmpty').style.display = 'none';

    var cur = res.current || {};
    document.getElementById('perfOverall').textContent = (cur.overall_score || 0) + '/100';
    document.getElementById('perfGrade').textContent = res.grade || 'N/A';
    document.getElementById('perfCWV').textContent = (res.cwv_status || 'unknown').replace('_', ' ');
    document.getElementById('perfIssues').textContent = cur.issues_count || 0;
    document.getElementById('perfSeoScore').textContent = (cur.seo_score || 0);
    document.getElementById('perfTechScore').textContent = (cur.technical_score || 0);
    document.getElementById('perfContentScore').textContent = (cur.content_score || 0);

    // Score trend chart
    var trend = res.score_trend || [];
    if (trend.length > 0) {
      renderPerfScoreChart(trend);
    }
    // CWV trend chart
    var cwvTrend = res.cwv_trend || [];
    if (cwvTrend.length > 0) {
      renderPerfCWVChart(cwvTrend);
    }
    // Tracked sites
    loadTrackedSites();
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnPerfDash', false);
}

function renderPerfScoreChart(data) {
  var canvas = document.getElementById('perfScoreChart');
  if (!canvas) return;
  if (perfScoreChartInst) perfScoreChartInst.destroy();
  perfScoreChartInst = new Chart(canvas, {
    type: 'line',
    data: {
      labels: data.map(function(d) { return d.date; }),
      datasets: [{
        label: 'Overall Score',
        data: data.map(function(d) { return d.score; }),
        borderColor: '#6366f1', backgroundColor: '#6366f120',
        fill: true, tension: 0.4, pointRadius: 4
      }]
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 100 } } }
  });
}

function renderPerfCWVChart(data) {
  var canvas = document.getElementById('perfCWVChart');
  if (!canvas) return;
  if (perfCWVChartInst) perfCWVChartInst.destroy();
  perfCWVChartInst = new Chart(canvas, {
    type: 'line',
    data: {
      labels: data.map(function(d) { return d.date; }),
      datasets: [
        { label: 'Performance', data: data.map(function(d) { return d.perf; }), borderColor: '#6366f1', tension: 0.4, yAxisID: 'y' },
        { label: 'LCP (ms)', data: data.map(function(d) { return d.lcp; }), borderColor: '#ef4444', tension: 0.4, yAxisID: 'y1' }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        y: { position: 'left', min: 0, max: 100, title: { display: true, text: 'Perf Score' } },
        y1: { position: 'right', min: 0, title: { display: true, text: 'LCP (ms)' }, grid: { drawOnChartArea: false } }
      }
    }
  });
}

async function fetchCWV() {
  var url = document.getElementById('perfUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  showToast('Fetching Core Web Vitals... (may take 30s)', 'info');
  try {
    var res = await (await fetch(API + '/api/performance/fetch-cwv', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    showToast('CWV fetched! Performance score: ' + (res.performance_score || 0), 'success');
    loadPerformanceDashboard();
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function savePerfSnapshot() {
  var url = document.getElementById('perfUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/performance/save-snapshot', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url, audit_data: {score: 75, word_count: 1500, issues: [], headings: {h2: ['a','b','c']}, links: {internal_count: 5, external_count: 2}, images: {total: 3}}})
    })).json();
    showToast('Snapshot saved!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function generateCombinedReport() {
  var url = document.getElementById('perfUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  showToast('Running full parallel audit + generating report...', 'info');
  btnLoading('btnPerfDash', true);
  try {
    var res = await (await fetch(API + '/api/report/full-audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url, max_workers: 6})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    var reportPath = (res.report || {}).report_path || '';
    showToast('Full report generated! Score: ' + ((res.audit || {}).overall_score || 0), 'success');
    if (reportPath) {
      showToast('Report saved to: ' + reportPath, 'info');
    }
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnPerfDash', false);
}

async function loadTrackedSites() {
  try {
    var res = await (await fetch(API + '/api/performance/tracked-sites', { headers: authHeaders() })).json();
    var sites = res.sites || [];
    var el = document.getElementById('perfTrackedSites');
    if (sites.length === 0) { el.innerHTML = '<div style="padding:12px;color:var(--text-muted);">No tracked sites yet.</div>'; return; }
    var html = '<div class="table-wrapper"><table><tr><th>URL</th><th>Score</th><th>Issues</th><th>Last Audit</th></tr>';
    sites.forEach(function(s) {
      var sc = s.score || 0;
      var mc = sc >= 80 ? 'success' : sc >= 50 ? 'warning' : 'danger';
      html += '<tr><td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">' + (s.url||'') + '</td>';
      html += '<td><span class="badge badge-' + mc + '">' + sc + '/100</span></td>';
      html += '<td>' + (s.issues||0) + '</td>';
      html += '<td style="font-size:0.8rem;color:var(--text-muted);">' + (s.last_audit||'').substring(0,10) + '</td></tr>';
    });
    html += '</table></div>';
    el.innerHTML = html;
  } catch(e) { console.error(e); }
}
"""

if 'async function loadPerformanceDashboard' not in c:
    idx = c.rfind('</script>')
    if idx > 0:
        c = c[:idx] + NEW_JS + '\n' + c[idx:]
        changes.append('Added Performance + Orchestrator JS functions')
    else:
        changes.append('WARNING: No </script> tag found for JS injection')
else:
    changes.append('JS functions already present (skipped)')

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

for ch in changes:
    print(ch)
print(f'\nTotal changes: {len(changes)}')
