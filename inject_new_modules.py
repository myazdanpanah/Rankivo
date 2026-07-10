"""Inject new SEO module pages and JS functions into index.html"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

changes = []

# 1. Add new navigation items after SPA nav item
if 'data-page="images"' not in c:
    nav_items = (
        '    <a class="nav-item" data-page="images" onclick="navigate(\'images\')">\n'
        '      <i class="fas fa-images"></i> <span>Image SEO</span>\n'
        '    </a>\n'
        '    <a class="nav-item" data-page="sitemap-deep" onclick="navigate(\'sitemap-deep\')">\n'
        '      <i class="fas fa-sitemap"></i> <span>Sitemap Audit</span>\n'
        '    </a>\n'
        '    <a class="nav-item" data-page="hreflang" onclick="navigate(\'hreflang\')">\n'
        '      <i class="fas fa-globe"></i> <span>Hreflang / i18n</span>\n'
        '    </a>\n'
        '    <a class="nav-item" data-page="local-seo" onclick="navigate(\'local-seo\')">\n'
        '      <i class="fas fa-map-marker-alt"></i> <span>Local SEO</span>\n'
        '    </a>\n'
        '    <a class="nav-item" data-page="ecommerce" onclick="navigate(\'ecommerce\')">\n'
        '      <i class="fas fa-shopping-cart"></i> <span>E-commerce SEO</span>\n'
        '    </a>\n'
        '    <a class="nav-item" data-page="sxo" onclick="navigate(\'sxo\')">\n'
        '      <i class="fas fa-user-check"></i> <span>SXO</span>\n'
        '    </a>\n'
        '    <a class="nav-item" data-page="content-brief" onclick="navigate(\'content-brief\')">\n'
        '      <i class="fas fa-file-alt"></i> <span>Content Brief</span>\n'
        '    </a>\n'
        '    <a class="nav-item" data-page="programmatic" onclick="navigate(\'programmatic\')">\n'
        '      <i class="fas fa-cubes"></i> <span>Programmatic SEO</span>\n'
        '    </a>\n'
        '    <a class="nav-item" data-page="seo-plan" onclick="navigate(\'seo-plan\')">\n'
        '      <i class="fas fa-chess"></i> <span>SEO Strategy</span>\n'
        '    </a>\n'
        '    <a class="nav-item" data-page="orchestrator" onclick="navigate(\'orchestrator\')">\n'
        '      <i class="fas fa-layer-group"></i> <span>Full Audit (Parallel)</span>\n'
        '    </a>\n'
    )
    marker = '<a class="nav-item" data-page="recommendations"'
    if marker in c:
        c = c.replace(marker, nav_items + marker, 1)
        changes.append('Added 10 new nav items')

# 2. Add new page HTML sections before settings page
NEW_PAGES = """
    <!-- ═══════════════════════════════════════════
         PAGE: Image SEO
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-images">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-images"></i> Image Optimization Analysis</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Analyze alt text, file sizes, formats (WebP/AVIF), responsive images, lazy loading, and CLS prevention.</p>
        <div class="form-row">
          <div class="form-group" style="flex:2;">
            <label class="form-label">URL to Analyze</label>
            <input type="text" class="form-input" id="imageUrl" placeholder="https://example.com" onkeydown="if(event.key==='Enter') runImageAnalysis()">
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-primary" onclick="runImageAnalysis()" id="btnImages"><i class="fas fa-images"></i> Analyze</button>
          </div>
        </div>
      </div>
      <div id="imageResults" style="display:none;"></div>
    </div>

    <!-- ═══════════════════════════════════════════
         PAGE: Sitemap Deep Audit
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-sitemap-deep">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-sitemap"></i> Sitemap Audit</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Discover, parse, and validate XML sitemaps. Checks URL counts, lastmod dates, deprecated tags, and best practices.</p>
        <div class="form-row">
          <div class="form-group" style="flex:2;">
            <label class="form-label">URL to Audit</label>
            <input type="text" class="form-input" id="sitemapUrl" placeholder="https://example.com" onkeydown="if(event.key==='Enter') runSitemapAudit()">
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-primary" onclick="runSitemapAudit()" id="btnSitemapAudit"><i class="fas fa-sitemap"></i> Audit</button>
          </div>
        </div>
      </div>
      <div id="sitemapResults" style="display:none;"></div>
    </div>

    <!-- ═══════════════════════════════════════════
         PAGE: Hreflang / i18n SEO
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-hreflang">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-globe"></i> Hreflang / International SEO</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Validate hreflang tags: self-referencing, return tag reciprocity, x-default, language codes, and canonical alignment.</p>
        <div class="form-row">
          <div class="form-group" style="flex:2;">
            <label class="form-label">URL to Audit</label>
            <input type="text" class="form-input" id="hreflangUrl" placeholder="https://example.com" onkeydown="if(event.key==='Enter') runHreflangAudit()">
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-primary" onclick="runHreflangAudit()" id="btnHreflang"><i class="fas fa-globe"></i> Audit</button>
          </div>
        </div>
      </div>
      <div id="hreflangResults" style="display:none;"></div>
    </div>

    <!-- ═══════════════════════════════════════════
         PAGE: Local SEO
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-local-seo">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-map-marker-alt"></i> Local SEO Analysis</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Evaluate Google Business Profile signals, NAP consistency, reviews, local schema, and map pack readiness.</p>
        <div class="form-row">
          <div class="form-group" style="flex:2;">
            <label class="form-label">URL to Analyze</label>
            <input type="text" class="form-input" id="localUrl" placeholder="https://example.com" onkeydown="if(event.key==='Enter') runLocalSeoAudit()">
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-primary" onclick="runLocalSeoAudit()" id="btnLocalSeo"><i class="fas fa-map-marker-alt"></i> Analyze</button>
          </div>
        </div>
      </div>
      <div id="localResults" style="display:none;"></div>
    </div>

    <!-- ═══════════════════════════════════════════
         PAGE: E-commerce SEO
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-ecommerce">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-shopping-cart"></i> E-commerce SEO</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Analyze product schema, pricing signals, availability, marketplace presence, and e-commerce-specific SEO factors.</p>
        <div class="form-row">
          <div class="form-group" style="flex:2;">
            <label class="form-label">Product Page URL</label>
            <input type="text" class="form-input" id="ecomUrl" placeholder="https://shop.example.com/product/x" onkeydown="if(event.key==='Enter') runEcommerceAudit()">
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-primary" onclick="runEcommerceAudit()" id="btnEcom"><i class="fas fa-shopping-cart"></i> Analyze</button>
          </div>
        </div>
      </div>
      <div id="ecomResults" style="display:none;"></div>
    </div>

    <!-- ═══════════════════════════════════════════
         PAGE: SXO - Search Experience Optimization
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-sxo">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-user-check"></i> Search Experience Optimization (SXO)</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Classify page type, analyze intent alignment, score user personas, and evaluate content quality for search experience.</p>
        <div class="form-row">
          <div class="form-group" style="flex:2;">
            <label class="form-label">URL to Analyze</label>
            <input type="text" class="form-input" id="sxoUrl" placeholder="https://example.com" onkeydown="if(event.key==='Enter') runSxoAudit()">
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-primary" onclick="runSxoAudit()" id="btnSxo"><i class="fas fa-user-check"></i> Analyze</button>
          </div>
        </div>
      </div>
      <div id="sxoResults" style="display:none;"></div>
    </div>

    <!-- ═══════════════════════════════════════════
         PAGE: Content Brief Generator
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-content-brief">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-file-alt"></i> Content Brief Generator</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Generate comprehensive content briefs with heading outlines, keyword targets, competitor angles, and SEO checklists.</p>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Topic</label>
            <input type="text" class="form-input" id="briefTopic" placeholder="e.g. Python web frameworks" onkeydown="if(event.key==='Enter') runContentBrief()">
          </div>
          <div class="form-group">
            <label class="form-label">Keywords (comma separated)</label>
            <input type="text" class="form-input" id="briefKeywords" placeholder="python frameworks, web development">
          </div>
        </div>
        <div class="form-row-3">
          <div class="form-group">
            <label class="form-label">Search Intent</label>
            <select class="form-select" id="briefIntent">
              <option value="informational">Informational</option>
              <option value="commercial">Commercial</option>
              <option value="transactional">Transactional</option>
              <option value="navigational">Navigational</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Language</label>
            <select class="form-select" id="briefLang">
              <option value="en">English</option>
              <option value="fa">فارسی (Persian)</option>
            </select>
          </div>
          <div class="form-group" style="display:flex;align-items:flex-end;">
            <button class="btn btn-primary" onclick="runContentBrief()" id="btnBrief"><i class="fas fa-file-alt"></i> Generate Brief</button>
          </div>
        </div>
      </div>
      <div id="briefResults" style="display:none;"></div>
    </div>

    <!-- ═══════════════════════════════════════════
         PAGE: Programmatic SEO
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-programmatic">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-cubes"></i> Programmatic SEO Analysis</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Detect URL patterns, thin content, index bloat, and template issues for pages generated at scale.</p>
        <div class="form-row">
          <div class="form-group" style="flex:2;">
            <label class="form-label">URL to Analyze</label>
            <input type="text" class="form-input" id="progUrl" placeholder="https://example.com/tools/" onkeydown="if(event.key==='Enter') runProgSeoAudit()">
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-primary" onclick="runProgSeoAudit()" id="btnProg"><i class="fas fa-cubes"></i> Analyze</button>
          </div>
        </div>
      </div>
      <div id="progResults" style="display:none;"></div>
    </div>

    <!-- ═══════════════════════════════════════════
         PAGE: SEO Strategy Planning
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-seo-plan">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-chess"></i> SEO Strategy Planning</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Generate industry-specific SEO strategies with phased implementation plans, content types, schema recommendations, and KPIs.</p>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Industry</label>
            <select class="form-select" id="planIndustry">
              <option value="saas">💻 SaaS / Software</option>
              <option value="local">📍 Local Business</option>
              <option value="ecommerce">🛒 E-commerce</option>
              <option value="publisher">📰 Publisher / Media</option>
              <option value="agency">🏢 Agency / Services</option>
            </select>
          </div>
          <div class="form-group" style="display:flex;align-items:flex-end;">
            <button class="btn btn-primary" onclick="runSeoPlan()" id="btnPlan"><i class="fas fa-chess"></i> Generate Strategy</button>
          </div>
        </div>
      </div>
      <div id="planResults" style="display:none;"></div>
    </div>

    <!-- ═══════════════════════════════════════════
         PAGE: Full Parallel Audit Orchestrator
         ═══════════════════════════════════════════ -->
    <div class="page" id="page-orchestrator">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-layer-group"></i> Full Parallel SEO Audit</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Run ALL SEO modules simultaneously using parallel agent orchestration. This is the equivalent of claude-seo's parallel sub-agent dispatch.</p>
        <div class="form-row">
          <div class="form-group" style="flex:2;">
            <label class="form-label">URL to Audit</label>
            <input type="text" class="form-input" id="orchUrl" placeholder="https://example.com" onkeydown="if(event.key==='Enter') runFullOrchestrator()">
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">Workers</label>
            <input type="number" class="form-input" id="orchWorkers" value="6" min="2" max="12" style="width:80px;">
          </div>
          <div class="form-group" style="flex:0;">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-primary" onclick="runFullOrchestrator()" id="btnOrch"><i class="fas fa-play"></i> Run Full Audit</button>
          </div>
        </div>
        <div id="orchProgress" style="display:none;margin-top:12px;">
          <div class="pipeline-step active" id="orchStep"><i class="fas fa-spinner fa-spin"></i> Running parallel analysis...</div>
        </div>
      </div>
      <div id="orchResults" style="display:none;"></div>
    </div>

"""

if 'page-images' not in c:
    marker = '<div class="page" id="page-settings">'
    if marker in c:
        c = c.replace(marker, NEW_PAGES + marker, 1)
        changes.append('Added 10 new page sections')

# 3. Add JavaScript functions for all new modules
NEW_JS = r"""
/* ══════════════════════════════════════════════
   New Module JS Functions
   ══════════════════════════════════════════════ */

function renderGenericResult(data, containerId, title) {
  var el = document.getElementById(containerId);
  if (!el) return;
  el.style.display = 'block';
  var score = data.score || data.composite_score || 0;
  var scoreColor = score >= 80 ? 'success' : score >= 50 ? 'warning' : 'danger';
  var html = '<div class="card"><div class="card-header"><div class="card-title">' + title;
  html += ' <span class="badge badge-' + scoreColor + '">' + score + '/100</span></div></div>';

  var issues = data.issues || [];
  if (issues.length > 0) {
    issues.forEach(function(i) {
      var sev = i.severity || 'info';
      var icon = sev === 'critical' ? 'fa-times-circle' : sev === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle';
      html += '<div class="issue-item ' + sev + '"><i class="fas ' + icon + ' issue-icon"></i><div><div class="issue-cat">' + (i.severity||'') + '</div>' + (i.message || JSON.stringify(i)) + '</div></div>';
    });
  }
  var recs = data.recommendations || [];
  if (recs.length > 0) {
    html += '<div style="margin-top:12px;padding:12px;background:var(--success-bg);border-radius:8px;">';
    html += '<strong style="font-size:0.85rem;">💡 Recommendations:</strong>';
    recs.forEach(function(r) {
      var text = typeof r === 'string' ? r : (r.action || r.message || JSON.stringify(r));
      html += '<div style="padding:4px 0;font-size:0.88rem;color:var(--text-secondary);">• ' + text + '</div>';
    });
    html += '</div>';
  }
  html += '</div>';
  el.innerHTML = html;
}

async function runImageAnalysis() {
  var url = document.getElementById('imageUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnImages', true);
  try {
    var res = await (await fetch(API + '/api/images/analyze', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'imageResults', '<i class="fas fa-images"></i> Image Optimization');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnImages', false);
}

async function runSitemapAudit() {
  var url = document.getElementById('sitemapUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnSitemapAudit', true);
  try {
    var res = await (await fetch(API + '/api/sitemap/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'sitemapResults', '<i class="fas fa-sitemap"></i> Sitemap Audit');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnSitemapAudit', false);
}

async function runHreflangAudit() {
  var url = document.getElementById('hreflangUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnHreflang', true);
  try {
    var res = await (await fetch(API + '/api/hreflang/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'hreflangResults', '<i class="fas fa-globe"></i> Hreflang Audit');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnHreflang', false);
}

async function runLocalSeoAudit() {
  var url = document.getElementById('localUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnLocalSeo', true);
  try {
    var res = await (await fetch(API + '/api/local-seo/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'localResults', '<i class="fas fa-map-marker-alt"></i> Local SEO');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnLocalSeo', false);
}

async function runEcommerceAudit() {
  var url = document.getElementById('ecomUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnEcom', true);
  try {
    var res = await (await fetch(API + '/api/ecommerce/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'ecomResults', '<i class="fas fa-shopping-cart"></i> E-commerce SEO');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnEcom', false);
}

async function runSxoAudit() {
  var url = document.getElementById('sxoUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnSxo', true);
  try {
    var res = await (await fetch(API + '/api/sxo/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'sxoResults', '<i class="fas fa-user-check"></i> SXO Audit');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnSxo', false);
}

async function runContentBrief() {
  var topic = document.getElementById('briefTopic').value.trim();
  if (!topic) { showToast('Enter a topic', 'error'); return; }
  var kw = document.getElementById('briefKeywords').value.split(',').map(function(s){return s.trim()}).filter(Boolean);
  if (kw.length === 0) kw = [topic];
  btnLoading('btnBrief', true);
  try {
    var res = await (await fetch(API + '/api/content-brief/generate', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({topic: topic, keywords: kw, intent: document.getElementById('briefIntent').value, language: document.getElementById('briefLang').value}) })).json();
    renderGenericResult(res, 'briefResults', '<i class="fas fa-file-alt"></i> Content Brief');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnBrief', false);
}

async function runProgSeoAudit() {
  var url = document.getElementById('progUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnProg', true);
  try {
    var res = await (await fetch(API + '/api/programmatic/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'progResults', '<i class="fas fa-cubes"></i> Programmatic SEO');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnProg', false);
}

async function runSeoPlan() {
  var industry = document.getElementById('planIndustry').value;
  try {
    var res = await (await fetch(API + '/api/plan/generate', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({industry: industry}) })).json();
    var el = document.getElementById('planResults');
    el.style.display = 'block';
    var html = '<div class="card"><div class="card-header"><div class="card-title">' + (res.icon||'') + ' ' + (res.label||industry) + ' SEO Strategy</div></div>';
    html += '<div class="metrics-row">';
    (res.focus_areas||[]).slice(0,4).forEach(function(f) { html += '<div class="metric-card"><div class="metric-icon purple"><i class="fas fa-bullseye"></i></div><div class="metric-label">Focus</div><div class="metric-value" style="font-size:1rem;">' + f + '</div></div>'; });
    html += '</div>';
    (res.implementation_phases||[]).forEach(function(p) {
      html += '<div class="expander"><div class="expander-header" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">';
      html += '<span>Phase ' + p.phase + ' (' + p.timeline + ')</span><i class="fas fa-chevron-right chevron"></i></div>';
      html += '<div class="expander-body"><ul style="list-style:disc;padding-left:20px;">';
      (p.tasks||[]).forEach(function(t) { html += '<li style="padding:3px 0;">' + t + '</li>'; });
      html += '</ul></div></div>';
    });
    html += '</div>';
    el.innerHTML = html;
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function runFullOrchestrator() {
  var url = document.getElementById('orchUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  var workers = parseInt(document.getElementById('orchWorkers').value) || 6;
  document.getElementById('orchProgress').style.display = 'block';
  btnLoading('btnOrch', true);
  try {
    var res = await (await fetch(API + '/api/orchestrator/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url, max_workers: workers}) })).json();
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
    var recs = res.recommendations || [];
    if (recs.length > 0) {
      html += '<div style="margin-top:12px;padding:12px;background:var(--success-bg);border-radius:8px;"><strong>Top Recommendations:</strong>';
      recs.slice(0,10).forEach(function(r) { var t = typeof r === 'string' ? r : (r.action || r.message || JSON.stringify(r)); html += '<div style="padding:4px 0;font-size:0.88rem;">• ' + t + '</div>'; });
      html += '</div>';
    }
    html += '</div>';
    el.innerHTML = html;
  } catch(e) {
    document.getElementById('orchProgress').style.display = 'none';
    showToast('Error: ' + e.message, 'error');
  }
  btnLoading('btnOrch', false);
}

function btnLoading(id, loading) {
  var btn = document.getElementById(id);
  if (!btn) return;
  if (loading) { btn.disabled = true; btn.dataset.origHtml = btn.innerHTML; btn.innerHTML = '<span class="spinner"></span> Running...'; }
  else { btn.disabled = false; if (btn.dataset.origHtml) btn.innerHTML = btn.dataset.origHtml; }
}
"""

if 'runImageAnalysis' not in c:
    idx = c.rfind('</script>')
    if idx > 0:
        c = c[:idx] + NEW_JS + '\n' + c[idx:]
        changes.append('Added new module JS functions')

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

for ch in changes:
    print(ch)
print(f'\nTotal changes: {len(changes)}')
