"""Inject Phase 2 UI elements into static/index.html"""
import re

with open('static/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Add sidebar nav items after the GEO nav ──
nav_items = """
    <a class="nav-item" data-page="backlinks" onclick="navigate('backlinks')">
      <i class="fas fa-link"></i> <span data-i18n="navBacklinks">Backlinks</span>
    </a>
    <a class="nav-item" data-page="drift" onclick="navigate('drift')">
      <i class="fas fa-history"></i> <span data-i18n="navDrift">SEO Drift</span>
    </a>
    <a class="nav-item" data-page="spa" onclick="navigate('spa')">
      <i class="fas fa-play-circle"></i> <span data-i18n="navSpa">SPA Render</span>
    </a>
"""

# Insert after the GEO nav-item
geo_pattern = r'(<a class="nav-item" data-page="geo"[^>]*>.*?</a>)'
geo_match = re.search(geo_pattern, content, re.DOTALL)
if geo_match:
    insert_pos = geo_match.end()
    content = content[:insert_pos] + nav_items + content[insert_pos:]
    print("OK: Added 3 sidebar nav items after GEO")
else:
    print("WARN: Could not find GEO nav-item, trying recommendations fallback")
    rec_pattern = r'(<a class="nav-item" data-page="recommendations"[^>]*>.*?</a>)'
    rec_match = re.search(rec_pattern, content, re.DOTALL)
    if rec_match:
        insert_pos = rec_match.end()
        content = content[:insert_pos] + nav_items + content[insert_pos:]
        print("OK: Added 3 sidebar nav items before Recommendations")

# ── 2. Add page HTML sections before the settings page ──
pages_html = r"""
    <!-- ═══════════════════════════════════════════
         PAGE: Backlink Analysis
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-backlinks">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-link"></i> Backlink Analysis</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Analyze backlinks for any domain using Bing Webmaster API and Common Crawl. Get domain authority, link quality, and toxic link detection.</p>
        <div class="form-row">
          <div class="form-group" style="flex:2;">
            <label class="form-label">Domain</label>
            <input type="text" class="form-input" id="backlinkDomain" placeholder="example.com" onkeydown="if(event.key==='Enter') runBacklinkAnalysis()">
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-primary" onclick="runBacklinkAnalysis()" id="btnBacklinks">
              <i class="fas fa-search"></i> Analyze
            </button>
          </div>
        </div>
      </div>
      <div id="backlinkResults" style="display:none;">
        <div class="card">
          <div class="card-header">
            <div class="card-title"><i class="fas fa-chart-bar"></i> Backlink Overview</div>
          </div>
          <div id="backlinkStats" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:16px;"></div>
        </div>
        <div class="card">
          <div class="card-header">
            <div class="card-title"><i class="fas fa-exclamation-triangle"></i> Toxic Links</div>
          </div>
          <div id="toxicLinks"></div>
        </div>
        <div class="card">
          <div class="card-header">
            <div class="card-title"><i class="fas fa-star"></i> Top Linking Domains</div>
          </div>
          <div id="topLinkingDomains"></div>
        </div>
        <div class="card">
          <div class="card-header">
            <div class="card-title"><i class="fas fa-chart-line"></i> Link Quality Score</div>
          </div>
          <div style="text-align:center;padding:20px;">
            <div id="linkQualityScore" style="font-size:3rem;font-weight:700;"></div>
            <div id="linkQualityLabel" style="font-size:0.9rem;color:var(--text-muted);"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════
         PAGE: SEO Drift Monitoring
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-drift">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-history"></i> SEO Drift Monitoring</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Track SEO changes over time. Save audit snapshots and compare them to detect regressions and improvements.</p>
        <div class="form-row">
          <div class="form-group" style="flex:2;">
            <label class="form-label">URL to Monitor</label>
            <input type="text" class="form-input" id="driftUrl" placeholder="https://example.com" onkeydown="if(event.key==='Enter') runDriftAnalysis()">
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-primary" onclick="runDriftAnalysis()" id="btnDrift">
              <i class="fas fa-chart-line"></i> Compare
            </button>
          </div>
        </div>
      </div>
      <div id="driftResults" style="display:none;">
        <div class="card">
          <div class="card-header">
            <div class="card-title"><i class="fas fa-exchange-alt"></i> Changes Detected</div>
            <span class="badge badge-info" id="driftChangeCount">0</span>
          </div>
          <div id="driftChanges"></div>
        </div>
        <div class="card">
          <div class="card-header">
            <div class="card-title"><i class="fas fa-camera"></i> Snapshot History</div>
          </div>
          <div id="driftHistory"></div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════
         PAGE: SPA Rendering
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-spa">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-play-circle"></i> SPA / JavaScript Renderer</div>
          <span class="badge" id="playwrightStatus" style="font-size:0.75rem;"></span>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Render JavaScript-heavy pages (React, Next.js, Vue) using headless Chromium. Get the fully rendered HTML that search engines see.</p>
        <div class="form-row">
          <div class="form-group" style="flex:2;">
            <label class="form-label">URL to Render</label>
            <input type="text" class="form-input" id="spaUrl" placeholder="https://example.com (SPA)" onkeydown="if(event.key==='Enter') runSpaRender()">
          </div>
          <div class="form-group">
            <label class="form-label">Wait (seconds)</label>
            <input type="number" class="form-input" id="spaWaitTime" value="3" min="1" max="15" style="width:80px;">
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-primary" onclick="runSpaRender()" id="btnSpa">
              <i class="fas fa-play"></i> Render
            </button>
          </div>
        </div>
      </div>
      <div id="spaResults" style="display:none;">
        <div class="card">
          <div class="card-header">
            <div class="card-title"><i class="fas fa-file-code"></i> Rendered HTML</div>
            <span class="badge badge-info" id="spaWordCount">0 words</span>
          </div>
          <div id="spaRenderedContent" style="background:var(--bg-input);border-radius:8px;padding:12px;font-family:monospace;font-size:0.8rem;max-height:400px;overflow-y:auto;white-space:pre-wrap;word-break:break-all;"></div>
        </div>
        <div class="card">
          <div class="card-header">
            <div class="card-title"><i class="fas fa-info-circle"></i> Render Stats</div>
          </div>
          <div id="spaRenderStats"></div>
        </div>
        <div class="card">
          <div class="card-header">
            <div class="card-title"><i class="fas fa-heading"></i> Extracted Content</div>
          </div>
          <div id="spaExtractedContent"></div>
        </div>
      </div>
    </div>
"""

# Insert before the settings page div
settings_pattern = r'(<div class="page" id="page-settings">)'
settings_match = re.search(settings_pattern, content)
if settings_match:
    insert_pos = settings_match.start()
    content = content[:insert_pos] + pages_html + content[insert_pos:]
    print("OK: Added 3 page sections before settings")
else:
    print("WARN: Could not find settings page div")

# ── 3. Add JavaScript functions before </script> ──
js_functions = r"""

/* ═══════════════════════════════════════════════
   Phase 2 — Backlink Analysis
   ═══════════════════════════════════════════════ */
async function runBacklinkAnalysis() {
  var domain = document.getElementById('backlinkDomain').value.trim();
  if (!domain) { showToast('Enter a domain', 'error'); return; }
  if (domain.startsWith('http')) { domain = domain.replace(/^https?:\/\//, '').replace(/\/.*$/, ''); }
  var btn = document.getElementById('btnBacklinks');
  btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
  try {
    var res = await (await fetch(API + '/api/backlinks/analyze', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ domain: domain })
    })).json();
    btn.disabled = false; btn.innerHTML = '<i class="fas fa-search"></i> Analyze';
    if (res.error) { showToast(res.error, 'error'); return; }
    document.getElementById('backlinkResults').style.display = 'block';
    renderBacklinkResults(res);
    showToast('Backlink analysis complete', 'success');
  } catch(e) {
    btn.disabled = false; btn.innerHTML = '<i class="fas fa-search"></i> Analyze';
    showToast('Error: ' + e.message, 'error');
  }
}

function renderBacklinkResults(data) {
  // Stats cards
  var statsHtml = '';
  var stats = [
    { label: 'Total Backlinks', value: data.total_backlinks || 0, icon: 'fa-link', color: '#6366f1' },
    { label: 'Unique Domains', value: data.unique_domains || 0, icon: 'fa-globe', color: '#10b981' },
    { label: 'DoFollow', value: data.dofollow_count || 0, icon: 'fa-check-circle', color: '#3b82f6' },
    { label: 'NoFollow', value: data.nofollow_count || 0, icon: 'fa-times-circle', color: '#f59e0b' },
    { label: 'Toxic', value: data.toxic_count || 0, icon: 'fa-skull-crossbones', color: '#ef4444' },
    { label: 'Avg Domain Auth', value: (data.avg_domain_authority || 0).toFixed(0), icon: 'fa-chart-line', color: '#8b5cf6' }
  ];
  for (var i = 0; i < stats.length; i++) {
    statsHtml += '<div style="padding:16px;border-radius:8px;background:var(--bg-input);text-align:center;">';
    statsHtml += '<div style="font-size:1.5rem;font-weight:700;color:' + stats[i].color + ';">' + stats[i].value + '</div>';
    statsHtml += '<div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px;">' + stats[i].label + '</div>';
    statsHtml += '</div>';
  }
  document.getElementById('backlinkStats').innerHTML = statsHtml;

  // Quality score
  var qs = data.quality_score || 0;
  var qColor = qs >= 70 ? '#10b981' : qs >= 40 ? '#f59e0b' : '#ef4444';
  var qLabel = qs >= 70 ? 'Excellent' : qs >= 50 ? 'Good' : qs >= 30 ? 'Needs Improvement' : 'Poor';
  document.getElementById('linkQualityScore').innerHTML = '<span style="color:' + qColor + ';">' + qs + '</span><span style="font-size:1rem;color:var(--text-muted);">/100</span>';
  document.getElementById('linkQualityLabel').textContent = qLabel;

  // Toxic links
  var toxicHtml = '';
  var toxic = data.toxic_links || [];
  if (toxic.length === 0) {
    toxicHtml = '<div style="padding:12px;color:var(--text-muted);text-align:center;">No toxic links detected</div>';
  } else {
    for (var t = 0; t < Math.min(toxic.length, 20); t++) {
      toxicHtml += '<div style="padding:8px 12px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;">';
      toxicHtml += '<span style="font-size:0.9rem;">' + (toxic[t].domain || toxic[t].url || '') + '</span>';
      toxicHtml += '<span class="badge badge-danger" style="font-size:0.7rem;">' + (toxic[t].reason || 'toxic') + '</span>';
      toxicHtml += '</div>';
    }
  }
  document.getElementById('toxicLinks').innerHTML = toxicHtml;

  // Top linking domains
  var topHtml = '';
  var topDomains = data.top_linking_domains || [];
  if (topDomains.length === 0) {
    topHtml = '<div style="padding:12px;color:var(--text-muted);text-align:center;">No linking domains found</div>';
  } else {
    topHtml = '<table style="width:100%;border-collapse:collapse;font-size:0.9rem;">';
    topHtml += '<tr style="background:var(--bg-input);"><th style="padding:8px 12px;text-align:left;">Domain</th><th style="padding:8px;text-align:right;">Authority</th><th style="padding:8px;text-align:right;">Links</th></tr>';
    for (var d = 0; d < Math.min(topDomains.length, 20); d++) {
      var da = topDomains[d].domain_authority || 0;
      var daColor = da >= 50 ? '#10b981' : da >= 20 ? '#f59e0b' : '#ef4444';
      topHtml += '<tr style="border-bottom:1px solid var(--border);">';
      topHtml += '<td style="padding:8px 12px;">' + (topDomains[d].domain || '') + '</td>';
      topHtml += '<td style="padding:8px;text-align:right;"><span style="color:' + daColor + ';font-weight:600;">' + da + '</span></td>';
      topHtml += '<td style="padding:8px;text-align:right;">' + (topDomains[d].link_count || 0) + '</td>';
      topHtml += '</tr>';
    }
    topHtml += '</table>';
  }
  document.getElementById('topLinkingDomains').innerHTML = topHtml;
}

/* ═══════════════════════════════════════════════
   Phase 2 — SEO Drift Monitoring
   ═══════════════════════════════════════════════ */
async function runDriftAnalysis() {
  var url = document.getElementById('driftUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  if (!url.startsWith('http')) { url = 'https://' + url; }
  var btn = document.getElementById('btnDrift');
  btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Comparing...';
  try {
    var res = await (await fetch(API + '/api/drift/compare', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ url: url })
    })).json();
    btn.disabled = false; btn.innerHTML = '<i class="fas fa-chart-line"></i> Compare';
    if (res.error) { showToast(res.error, 'error'); return; }
    document.getElementById('driftResults').style.display = 'block';
    renderDriftResults(res);
    showToast('Drift analysis complete', 'success');
  } catch(e) {
    btn.disabled = false; btn.innerHTML = '<i class="fas fa-chart-line"></i> Compare';
    showToast('Error: ' + e.message, 'error');
  }
}

function renderDriftResults(data) {
  // Changes
  var changes = data.changes || [];
  document.getElementById('driftChangeCount').textContent = changes.length;
  var html = '';
  if (changes.length === 0) {
    html = '<div style="padding:20px;text-align:center;color:var(--text-muted);">No snapshots to compare. Run an audit first, then save a snapshot.</div>';
  } else {
    var colorMap = { improved: '#10b981', regressed: '#ef4444', changed: '#f59e0b', unchanged: 'var(--text-muted)' };
    var iconMap = { improved: 'fa-arrow-up', regressed: 'fa-arrow-down', changed: 'fa-exchange-alt', unchanged: 'fa-minus' };
    for (var i = 0; i < changes.length; i++) {
      var c = changes[i];
      var color = colorMap[c.direction] || 'var(--text-muted)';
      var icon = iconMap[c.direction] || 'fa-question';
      html += '<div style="padding:10px 14px;border-left:3px solid ' + color + ';margin-bottom:8px;border-radius:0 8px 8px 0;background:var(--bg-input);">';
      html += '<div style="display:flex;justify-content:space-between;align-items:center;">';
      html += '<span><i class="fas ' + icon + '" style="color:' + color + ';margin-right:8px;"></i><strong>' + (c.metric || '') + '</strong></span>';
      html += '<span style="font-size:0.85rem;color:' + color + ';">' + (c.old_value || 0) + ' → ' + (c.new_value || 0) + ' (' + (c.change_pct || 0) + '%)</span>';
      html += '</div></div>';
    }
  }
  document.getElementById('driftChanges').innerHTML = html;

  // History
  var history = data.history || [];
  var hHtml = '';
  if (history.length === 0) {
    hHtml = '<div style="padding:12px;color:var(--text-muted);text-align:center;">No snapshot history</div>';
  } else {
    hHtml = '<table style="width:100%;border-collapse:collapse;font-size:0.9rem;">';
    hHtml += '<tr style="background:var(--bg-input);"><th style="padding:8px 12px;text-align:left;">Date</th><th style="padding:8px;text-align:right;">Score</th><th style="padding:8px;text-align:right;">Words</th><th style="padding:8px;text-align:right;">Links</th></tr>';
    for (var j = 0; j < history.length; j++) {
      var h = history[j];
      hHtml += '<tr style="border-bottom:1px solid var(--border);">';
      hHtml += '<td style="padding:8px 12px;">' + (h.created_at || h.snapshot_date || '') + '</td>';
      hHtml += '<td style="padding:8px;text-align:right;font-weight:600;">' + (h.score || '-') + '</td>';
      hHtml += '<td style="padding:8px;text-align:right;">' + (h.word_count || '-') + '</td>';
      hHtml += '<td style="padding:8px;text-align:right;">' + (h.total_links || '-') + '</td>';
      hHtml += '</tr>';
    }
    hHtml += '</table>';
  }
  document.getElementById('driftHistory').innerHTML = hHtml;
}

/* ═══════════════════════════════════════════════
   Phase 2 — SPA Rendering
   ═══════════════════════════════════════════════ */
async function checkPlaywrightStatus() {
  try {
    var res = await (await fetch(API + '/api/spa/status', { headers: authHeaders() })).json();
    var el = document.getElementById('playwrightStatus');
    if (!el) return;
    if (res.available) {
      el.className = 'badge badge-success';
      el.textContent = 'Playwright Available';
    } else {
      el.className = 'badge badge-warning';
      el.textContent = 'Playwright Not Installed';
    }
  } catch(e) { console.error(e); }
}

async function runSpaRender() {
  var url = document.getElementById('spaUrl').value.trim();
  var waitTime = parseInt(document.getElementById('spaWaitTime').value) || 3;
  if (!url) { showToast('Enter a URL', 'error'); return; }
  if (!url.startsWith('http')) { url = 'https://' + url; }
  var btn = document.getElementById('btnSpa');
  btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Rendering...';
  try {
    var res = await (await fetch(API + '/api/spa/render', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ url: url, wait_time: waitTime })
    })).json();
    btn.disabled = false; btn.innerHTML = '<i class="fas fa-play"></i> Render';
    if (res.error) { showToast(res.error, 'error'); return; }
    document.getElementById('spaResults').style.display = 'block';
    renderSpaResults(res);
    showToast('SPA render complete', 'success');
  } catch(e) {
    btn.disabled = false; btn.innerHTML = '<i class="fas fa-play"></i> Render';
    showToast('Error: ' + e.message, 'error');
  }
}

function renderSpaResults(data) {
  // Rendered HTML
  var html = data.rendered_html || '';
  document.getElementById('spaRenderedContent').textContent = html;
  // Word count
  var wc = html.replace(/<[^>]+>/g, '').split(/\s+/).filter(Boolean).length;
  document.getElementById('spaWordCount').textContent = wc + ' words';

  // Stats
  var stats = data.stats || {};
  var statsHtml = '';
  var statItems = [
    { label: 'Render Time', value: (stats.render_time || 0).toFixed(1) + 's' },
    { label: 'Title', value: data.title || 'N/A' },
    { label: 'Final URL', value: data.final_url || data.url || 'N/A' },
    { label: 'Scripts', value: stats.scripts_count || 0 },
    { label: 'Images', value: stats.images_count || 0 },
    { label: 'Meta Tags', value: stats.meta_count || 0 }
  ];
  for (var i = 0; i < statItems.length; i++) {
    statsHtml += '<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border);font-size:0.9rem;">';
    statsHtml += '<span style="color:var(--text-muted);">' + statItems[i].label + '</span>';
    statsHtml += '<span style="font-weight:600;">' + statItems[i].value + '</span>';
    statsHtml += '</div>';
  }
  document.getElementById('spaRenderStats').innerHTML = statsHtml;

  // Extracted content
  var content = data.content || {};
  var cHtml = '';
  if (content.headings) {
    cHtml += '<div style="margin-bottom:12px;"><strong style="font-size:0.85rem;color:var(--text-muted);">HEADINGS</strong><ul style="list-style:none;padding:0;margin:0;">';
    for (var tag in content.headings) {
      var headings = content.headings[tag];
      for (var h = 0; h < headings.length; h++) {
        cHtml += '<li style="padding:4px 0;font-size:0.85rem;"><code style="color:var(--accent);">' + tag + '</code> ' + headings[h] + '</li>';
      }
    }
    cHtml += '</ul></div>';
  }
  if (content.meta) {
    cHtml += '<div><strong style="font-size:0.85rem;color:var(--text-muted);">META</strong><ul style="list-style:none;padding:0;margin:0;">';
    for (var mk in content.meta) {
      cHtml += '<li style="padding:4px 0;font-size:0.85rem;"><code>' + mk + '</code>: ' + (content.meta[mk] || '') + '</li>';
    }
    cHtml += '</ul></div>';
  }
  document.getElementById('spaExtractedContent').innerHTML = cHtml || '<div style="padding:12px;color:var(--text-muted);">No content extracted</div>';
}
"""

# Insert before the last </script>
last_script_pos = content.rfind('</script>')
if last_script_pos > 0:
    content = content[:last_script_pos] + js_functions + "\n" + content[last_script_pos:]
    print("OK: Added JS functions before </script>")

# Write the updated file
with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! Phase 2 UI injected into static/index.html")
