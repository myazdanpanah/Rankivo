/* ============================================================
   Comprehensive SEO Report — Full Audit Report Page
   ============================================================ */

const REPORT_CATEGORIES_DEF = {
  technical_seo:        { label: 'Technical SEO',            weight: 22, icon: 'fa-cogs' },
  content_quality:      { label: 'Content Quality',          weight: 23, icon: 'fa-file-alt' },
  onpage_seo:           { label: 'On-Page SEO',              weight: 20, icon: 'fa-tags' },
  schema_structured_data:{ label: 'Schema / Structured Data', weight: 10, icon: 'fa-code' },
  performance:          { label: 'Performance (CWV)',        weight: 10, icon: 'fa-tachometer-alt' },
  ai_search_readiness:  { label: 'AI Search Readiness',      weight: 10, icon: 'fa-robot' },
  images_seo:           { label: 'Images SEO',               weight: 5,  icon: 'fa-images' },
};

let _reportRadarChart = null;

/* ────────────────────────────────────────────
   Run Comprehensive Audit
   ──────────────────────────────────────────── */
async function runComprehensiveAudit() {
  const url = document.getElementById('reportUrl').value.trim();
  if (!url) { showToast('Please enter a URL', 'error'); return; }

  const btn = document.getElementById('btnReportRun');
  const btnExport = document.getElementById('btnReportExport');
  const pipeline = document.getElementById('reportPipeline');
  const results = document.getElementById('reportResults');

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Running Audit...';
  if (btnExport) btnExport.style.display = 'none';
  results.style.display = 'none';

  // Show spinner
  if (pipeline) {
    pipeline.style.display = 'block';
    pipeline.innerHTML = '<div class="batch-progress"><span class="spinner spinner-dark"></span> Running comprehensive SEO audit across all modules...</div>';
  }

  try {
    const res = await fetch(API + '/api/report/comprehensive', {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    const data = await res.json();

    if (data.error) {
      showToast('Audit failed: ' + data.error, 'error');
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-rocket"></i> Run Full Audit';
      if (pipeline) pipeline.style.display = 'none';
      return;
    }

    // Hide pipeline on success
    if (pipeline) {
      pipeline.style.display = 'none';
    }

    renderComprehensiveReport(data);
    results.style.display = 'block';
    if (btnExport) btnExport.style.display = 'inline-flex';
    showToast('Audit completed! Score: ' + data.overall_score + '/100', 'success');
  } catch (e) {
    showToast('Error: ' + e.message, 'error');
    if (pipeline) pipeline.style.display = 'none';
  }

  btn.disabled = false;
  btn.innerHTML = '<i class="fas fa-rocket"></i> Run Full Audit';
}

/* ────────────────────────────────────────────
   Render the Full Comprehensive Report
   ──────────────────────────────────────────── */
function renderComprehensiveReport(data) {
  window._lastComprehensiveReport = data;
  const el = document.getElementById('reportContent');
  let html = '';

  // 1. Hero Section
  const scoreColor = data.overall_score >= 80 ? '#10b981' : data.overall_score >= 60 ? '#f59e0b' : '#ef4444';
  const gradeColor = data.overall_score >= 80 ? 'success' : data.overall_score >= 60 ? 'warning' : 'danger';

  html += `<div class="report-hero">
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:20px;">
      <div style="flex:1;min-width:250px;">
        <h2>SEO Health Audit Report</h2>
        <div class="hero-url"><i class="fas fa-link" style="margin-right:6px;"></i> ${escH(data.url)}</div>
        <div class="hero-date"><i class="fas fa-calendar" style="margin-right:6px;"></i> Generated: ${data.generated_date || new Date().toLocaleDateString()} | Audit time: ${data.total_audit_time || 0}s</div>
        <div style="margin-top:8px;"><span class="badge badge-${gradeColor}" style="font-size:0.82rem;">Business Type: ${escH(data.business_type || 'Unknown')}</span></div>
      </div>
      <div style="text-align:center;">
        <div style="width:130px;height:130px;border-radius:50%;border:5px solid ${scoreColor};display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(255,255,255,0.1);backdrop-filter:blur(4px);">
          <div style="font-size:2.5rem;font-weight:800;line-height:1;">${data.overall_score}</div>
          <div style="font-size:0.7rem;text-transform:uppercase;opacity:0.85;font-weight:600;">/ 100</div>
        </div>
        <div style="margin-top:6px;font-weight:600;font-size:0.9rem;">${data.grade} — ${escH(data.grade_label)}</div>
      </div>
    </div>
  </div>`;

  // 2. Metrics Row
  html += '<div class="metrics-row">';
  html += metricCard('fa-exclamation-triangle', 'red', 'Total Findings', data.total_findings || 0);
  html += metricCard('fa-times-circle', 'red', 'Critical Issues', data.total_critical || 0);
  html += metricCard('fa-exclamation-triangle', 'yellow', 'Warnings', data.total_warnings || 0);
  html += metricCard('fa-check-circle', 'green', 'Modules Run', data.modules_run || 0);
  html += '</div>';

  // 3. Scorecard Table + Radar Chart (side by side)
  html += '<div style="display:grid;grid-template-columns:2fr 1fr;gap:20px;margin-bottom:24px;">';

  // Scorecard Table
  html += '<div class="card"><div class="card-header"><div class="card-title"><i class="fas fa-chart-bar"></i> Category Scorecard</div></div>';
  html += '<div class="table-wrapper"><table class="scorecard-table"><thead><tr>';
  html += '<th>Category</th><th>Weight</th><th>Health Status</th><th>Score</th><th>Findings</th><th>Critical</th>';
  html += '</tr></thead><tbody>';

  (data.categories || []).forEach(cat => {
    const barColor = cat.score >= 80 ? 'var(--success)' : cat.score >= 60 ? 'var(--warning)' : 'var(--danger)';
    const critBadge = cat.critical_issues > 0
      ? `<span class="badge badge-danger">${cat.critical_issues}</span>`
      : '<span style="color:var(--success);">0</span>';
    html += `<tr>
      <td><i class="fas ${cat.icon || 'fa-check'}" style="margin-right:8px;color:var(--accent);"></i> ${escH(cat.label)}</td>
      <td>${cat.weight}%</td>
      <td>${cat.health_status}</td>
      <td>
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-weight:700;color:${barColor};">${cat.score}</span>
          <div class="score-bar" style="flex:1;"><div class="score-bar-fill" style="width:${cat.score}%;background:${barColor};"></div></div>
        </div>
      </td>
      <td>${cat.findings_count}</td>
      <td>${critBadge}</td>
    </tr>`;
  });

  // Total row
  const totalBarColor = data.overall_score >= 80 ? 'var(--success)' : data.overall_score >= 60 ? 'var(--warning)' : 'var(--danger)';
  html += `<tr>
    <td><strong>TOTAL SCORE</strong></td>
    <td>100%</td>
    <td><span class="badge badge-${gradeColor}">${data.grade_label}</span></td>
    <td>
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-weight:800;font-size:1.1rem;color:${totalBarColor};">${data.overall_score}</span>
        <div class="score-bar" style="flex:1;"><div class="score-bar-fill" style="width:${data.overall_score}%;background:${totalBarColor};"></div></div>
      </div>
    </td>
    <td>${data.total_findings}</td>
    <td><span class="badge badge-danger">${data.total_critical}</span></td>
  </tr>`;
  html += '</tbody></table></div></div>';

  // Radar Chart
  html += '<div class="card"><div class="card-header"><div class="card-title"><i class="fas fa-chart-pie"></i> Score Distribution</div></div>';
  html += '<div style="position:relative;height:320px;"><canvas id="reportRadarChart"></canvas></div></div>';

  html += '</div>'; // end grid

  // 4. Executive Summary
  html += '<div class="card"><div class="card-header"><div class="card-title"><i class="fas fa-rocket"></i> Executive Summary</div></div>';
  html += `<div style="padding:4px 0;">`;
  html += `<p style="font-size:0.92rem;margin-bottom:12px;"><strong>SEO Health Score: ${data.overall_score}/100 (${escH(data.grade_label)})</strong></p>`;

  // Top Critical Issues
  if (data.top_critical_issues && data.top_critical_issues.length > 0) {
    html += '<p style="font-weight:600;margin-bottom:8px;">Top Critical Issues:</p>';
    html += '<ul style="list-style:none;padding:0;">';
    data.top_critical_issues.forEach((issue, i) => {
      html += `<li style="padding:6px 0;font-size:0.88rem;color:var(--text-secondary);">
        <span style="color:var(--danger);font-weight:700;">${String.fromCharCode(65 + i)}.</span>
        ${escH(issue.message)}
        ${issue.category ? '<span class="badge badge-danger" style="margin-left:6px;">' + escH(issue.category) + '</span>' : ''}
      </li>`;
    });
    html += '</ul>';
  }

  // Quick Wins
  if (data.quick_wins && data.quick_wins.length > 0) {
    html += '<p style="font-weight:600;margin-top:16px;margin-bottom:8px;">Top Quick Wins:</p>';
    html += '<ul style="list-style:none;padding:0;">';
    data.quick_wins.slice(0, 5).forEach((win, i) => {
      html += `<li style="padding:6px 0;font-size:0.88rem;color:var(--text-secondary);">
        <i class="fas fa-check-circle" style="color:var(--success);margin-right:6px;"></i>
        ${escH(win.action)}
        <span class="badge badge-${win.priority === 'high' ? 'danger' : 'warning'}" style="margin-left:6px;font-size:0.68rem;">${win.priority}</span>
      </li>`;
    });
    html += '</ul>';
  }
  html += '</div></div>';

  // 5. Detailed Category Findings
  html += '<div style="margin-bottom:8px;"><h3 style="font-size:1.1rem;font-weight:700;"><i class="fas fa-search-plus" style="color:var(--accent);margin-right:8px;"></i> Detailed Category Findings</h3></div>';

  (data.categories || []).forEach(cat => {
    const barColor = cat.score >= 80 ? 'var(--success)' : cat.score >= 60 ? 'var(--warning)' : 'var(--danger)';
    const bgClass = cat.score >= 80 ? 'bg-success' : cat.score >= 60 ? 'bg-warning' : 'bg-danger';

    html += `<div class="report-category-card">`;
    html += `<div class="category-header">`;
    html += `<div class="cat-title"><i class="fas ${cat.icon || 'fa-check'} ${bgClass}"></i> ${escH(cat.label)} (Score: ${cat.score}/100 — Weighted ${cat.weight}%)</div>`;
    html += `<span class="badge badge-${cat.color}">${cat.health_status}</span>`;
    html += `</div>`;

    if (cat.findings && cat.findings.length > 0) {
      html += '<div style="max-height:300px;overflow-y:auto;">';
      cat.findings.forEach(f => {
        const sev = f.severity || 'info';
        const icon = sev === 'critical' ? 'fa-times-circle' : sev === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle';
        const sevClass = sev === 'critical' ? 'critical' : sev === 'warning' ? 'warning' : 'info';
        html += `<div class="issue-item ${sevClass}"><i class="fas ${icon} issue-icon"></i><div>`;
        if (f.category) html += `<div class="issue-cat">${escH(f.category)}</div>`;
        html += escH(f.message || String(f));
        html += '</div></div>';
      });
      html += '</div>';
    } else {
      html += '<div style="padding:8px;color:var(--success);font-size:0.88rem;"><i class="fas fa-check-circle"></i> No issues found in this category</div>';
    }
    html += '</div>';
  });

  // 6. Priority Action Plan
  html += '<div style="margin-bottom:8px;"><h3 style="font-size:1.1rem;font-weight:700;"><i class="fas fa-list-check" style="color:var(--accent);margin-right:8px;"></i> Priority Action Plan</h3></div>';

  if (data.action_plan) {
    const phaseMap = {
      phase_1: { cls: 'phase-danger', icon: 'fa-fire', color: 'danger' },
      phase_2: { cls: 'phase-warning', icon: 'fa-bolt', color: 'warning' },
      phase_3: { cls: 'phase-success', icon: 'fa-rocket', color: 'success' },
    };
    Object.keys(data.action_plan).forEach(key => {
      const phase = data.action_plan[key];
      const pm = phaseMap[key] || { cls: '', icon: 'fa-circle', color: 'info' };
      html += `<div class="report-phase">`;
      html += `<div class="report-phase-header ${pm.cls}"><span><i class="fas ${pm.icon}" style="margin-right:8px;"></i> ${escH(phase.title)}</span><span class="badge badge-${pm.color}">${escH(phase.timeline)}</span></div>`;
      html += '<ul class="report-phase-body">';
      phase.items.forEach(item => { html += `<li>${escH(item)}</li>`; });
      html += '</ul></div>';
    });
  }

  el.innerHTML = html;

  // Render radar chart
  renderReportRadarChart(data);
}

/* ────────────────────────────────────────────
   Radar Chart
   ──────────────────────────────────────────── */
function renderReportRadarChart(data) {
  const canvas = document.getElementById('reportRadarChart');
  if (!canvas || !data.categories) return;

  if (_reportRadarChart) { _reportRadarChart.destroy(); }

  const labels = data.categories.map(c => c.label);
  const scores = data.categories.map(c => c.score);

  _reportRadarChart = new Chart(canvas.getContext('2d'), {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Score',
        data: scores,
        backgroundColor: 'rgba(99, 102, 241, 0.2)',
        borderColor: '#6366f1',
        borderWidth: 2,
        pointBackgroundColor: scores.map(s => s >= 80 ? '#10b981' : s >= 60 ? '#f59e0b' : '#ef4444'),
        pointBorderColor: '#fff',
        pointRadius: 5,
        pointHoverRadius: 7,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          ticks: { stepSize: 20, font: { size: 11 } },
          grid: { color: 'rgba(0,0,0,0.06)' },
          pointLabels: { font: { size: 11, weight: '600' } }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ctx.parsed.r + '/100'
          }
        }
      }
    }
  });
}

/* ────────────────────────────────────────────
   Export Report as Markdown
   ──────────────────────────────────────────── */
function exportComprehensiveReport() {
  const data = window._lastComprehensiveReport;
  if (!data) { showToast('No report to export', 'error'); return; }

  let md = `# SEO Health Audit Report\n\n`;
  md += `**URL:** ${data.url}\n`;
  md += `**Generated:** ${data.generated_date} | **Audit Time:** ${data.total_audit_time}s\n\n`;
  md += `## Overall Score: ${data.overall_score}/100 (${data.grade} — ${data.grade_label})\n\n`;

  // Scorecard
  md += `## Category Scorecard\n\n`;
  md += `| Category | Weight | Score | Status | Findings | Critical |\n`;
  md += `|---|---|---|---|---|---|\n`;
  (data.categories || []).forEach(cat => {
    md += `| ${cat.label} | ${cat.weight}% | ${cat.score}/100 | ${cat.health_status} | ${cat.findings_count} | ${cat.critical_issues} |\n`;
  });
  md += `| **TOTAL** | **100%** | **${data.overall_score}/100** | **${data.grade_label}** | **${data.total_findings}** | **${data.total_critical}** |\n\n`;

  // Executive Summary
  md += `## Executive Summary\n\n`;
  if (data.top_critical_issues) {
    md += `### Top Critical Issues\n`;
    data.top_critical_issues.forEach((issue, i) => {
      md += `${String.fromCharCode(65 + i)}. ${issue.message}\n`;
    });
    md += '\n';
  }
  if (data.quick_wins) {
    md += `### Quick Wins\n`;
    data.quick_wins.slice(0, 5).forEach(w => {
      md += `- ${w.action} _[${w.priority}]_\n`;
    });
    md += '\n';
  }

  // Detailed Findings
  md += `## Detailed Findings\n\n`;
  (data.categories || []).forEach(cat => {
    md += `### ${cat.label} (Score: ${cat.score}/100)\n\n`;
    if (cat.findings && cat.findings.length > 0) {
      cat.findings.forEach(f => {
        md += `- **[${(f.severity || 'info').toUpperCase()}]** ${f.message}\n`;
      });
    } else {
      md += `- No issues found\n`;
    }
    md += '\n';
  });

  // Action Plan
  md += `## Priority Action Plan\n\n`;
  if (data.action_plan) {
    Object.values(data.action_plan).forEach(phase => {
      md += `### ${phase.title} (${phase.timeline})\n`;
      phase.items.forEach(item => { md += `- [ ] ${item}\n`; });
      md += '\n';
    });
  }

  md += `\n---\n_Generated by Rankivo — Free AI-Powered SEO Tool_\n`;

  // Download
  const blob = new Blob([md], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  const slug = (data.url || 'report').replace(/https?:\/\//, '').replace(/\//g, '_').slice(0, 50);
  a.download = `seo-audit-${slug}-${data.generated_date || 'report'}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('Report exported as Markdown', 'success');
}

/* ────────────────────────────────────────────
   Helpers
   ──────────────────────────────────────────── */
function escH(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function metricCard(icon, color, label, value) {
  return `<div class="metric-card"><div class="metric-icon ${color}"><i class="fas ${icon}"></i></div><div class="metric-label">${label}</div><div class="metric-value" style="color:var(--${color});">${value}</div></div>`;
}
