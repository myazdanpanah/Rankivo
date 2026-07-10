"""Inject Phase 1 (E-E-A-T, Schema, GEO) UI into static/index.html"""
import re

filepath = "static/index.html"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add page HTML sections before page-settings
EEAT_PAGES = """
    <!-- PAGE: E-E-A-T Analysis -->
    <div class="page" id="page-eeat">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-award"></i> E-E-A-T Analysis</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Evaluate your page against Google Search Quality Rater Guidelines (Sept 2025). Scores Experience, Expertise, Authoritativeness, and Trustworthiness.</p>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">URL to Analyze</label>
            <input type="text" class="form-input" id="eeatUrl" placeholder="https://example.com" onkeydown="if(event.key==='Enter') runEeatAnalysis()">
          </div>
          <div class="form-group" style="display:flex;align-items:flex-end;">
            <button class="btn btn-primary" onclick="runEeatAnalysis()" id="btnEeat">
              <i class="fas fa-award"></i> Run E-E-A-T Analysis
            </button>
          </div>
        </div>
      </div>
      <div id="eeatResults" style="display:none;"></div>
    </div>

    <!-- PAGE: Schema Deep Audit -->
    <div class="page" id="page-schema-deep">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-code"></i> Schema.org Deep Audit</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Detect, validate, and get recommendations for 15+ Schema.org types. Tracks deprecated types per Google 2024-2026 guidelines.</p>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">URL to Audit</label>
            <input type="text" class="form-input" id="schemaDeepUrl" placeholder="https://example.com" onkeydown="if(event.key==='Enter') runSchemaDeepAudit()">
          </div>
          <div class="form-group" style="display:flex;align-items:flex-end;">
            <button class="btn btn-primary" onclick="runSchemaDeepAudit()" id="btnSchemaDeep">
              <i class="fas fa-code"></i> Run Schema Audit
            </button>
          </div>
        </div>
      </div>
      <div id="schemaDeepResults" style="display:none;"></div>
    </div>

    <!-- PAGE: GEO / AI Search Audit -->
    <div class="page" id="page-geo">
      <div class="card">
        <div class="card-header">
          <div class="card-title"><i class="fas fa-robot"></i> GEO / AI Search Optimization</div>
        </div>
        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Evaluate AI search readiness: passage citability, question headings, entity presence, and attribution density.</p>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">URL to Analyze</label>
            <input type="text" class="form-input" id="geoUrl" placeholder="https://example.com" onkeydown="if(event.key==='Enter') runGeoAudit()">
          </div>
          <div class="form-group" style="display:flex;align-items:flex-end;">
            <button class="btn btn-primary" onclick="runGeoAudit()" id="btnGeo">
              <i class="fas fa-robot"></i> Run GEO Audit
            </button>
          </div>
        </div>
      </div>
      <div id="geoResults" style="display:none;"></div>
    </div>
"""

# Check if pages already injected
if 'id="page-eeat"' not in content:
    content = content.replace(
        '<div class="page" id="page-settings">',
        EEAT_PAGES + '    <div class="page" id="page-settings">',
    )
    print("Injected page sections")
else:
    print("Page sections already present")

# 2. Add JS functions before Intent Training Functions
JS_FUNCTIONS = r"""
/* ══════════════════════════════════════════════
   E-E-A-T Analysis
   ══════════════════════════════════════════════ */
async function runEeatAnalysis() {
  var url = document.getElementById('eeatUrl').value.trim();
  if (!url) { showToast('Please enter a URL', 'error'); return; }
  var btn = document.getElementById('btnEeat');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Analyzing...';
  try {
    var res = await (await fetch(API + '/api/eeat/analyze', {
      method: 'POST',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ url: url })
    })).json();
    renderEeatResults(res);
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btn.disabled = false; btn.innerHTML = '<i class="fas fa-award"></i> Run E-E-A-T Analysis';
}
function renderEeatResults(data) {
  var el = document.getElementById('eeatResults'); el.style.display = 'block';
  var score = data.composite_score || 0, grade = data.grade || 'F';
  var c = score >= 70 ? 'success' : score >= 50 ? 'warning' : 'danger';
  var html = '<div class="metrics-row">';
  html += '<div class="metric-card"><div class="metric-icon ' + c + '"><i class="fas fa-award"></i></div><div class="metric-label">Composite Score</div><div class="metric-value" style="color:var(--' + c + ')">' + score + '/100 (' + grade + ')</div></div>';
  html += '<div class="metric-card"><div class="metric-icon blue"><i class="fas fa-shield-alt"></i></div><div class="metric-label">YMYL Risk</div><div class="metric-value">' + (data.ymyl_risk || 'none') + '</div></div>';
  html += '</div>';
  var factors = data.factors || {};
  var names = {experience:'Experience',expertise:'Expertise',authoritativeness:'Authoritativeness',trustworthiness:'Trustworthiness'};
  var icons = {experience:'fa-user-check',expertise:'fa-brain',authoritativeness:'fa-trophy',trustworthiness:'fa-shield-alt'};
  for (var k in names) {
    var f = factors[k] || {}, fs = f.score||0, fm = f.max_score||25, r = fm>0?fs/fm:0;
    var fc = r>=0.6?'success':r>=0.4?'warning':'danger';
    html += '<div class="card"><div class="card-header"><div class="card-title"><i class="fas '+(icons[k]||'fa-check')+'" style="color:var(--'+fc+')"></i> '+names[k]+' <span class="badge badge-'+fc+'">'+fs+'/'+fm+'</span></div></div>';
    if(f.signals) f.signals.forEach(function(s){html+='<div style="padding:4px 14px;font-size:0.85rem;color:var(--text-secondary);">• '+s+'</div>';});
    html += '</div>';
  }
  var recs = data.recommendations||[];
  if(recs.length>0){html+='<div class="card"><div class="card-header"><div class="card-title"><i class="fas fa-lightbulb" style="color:var(--warning);"></i> Recommendations</div></div>';recs.forEach(function(r){html+='<div style="padding:8px 14px;border-radius:8px;background:var(--accent-light);margin-bottom:8px;font-size:0.88rem;"><span class="badge badge-'+(r.priority==='critical'?'danger':r.priority==='high'?'warning':'info')+'">'+r.priority+'</span> '+r.action;if(r.how_to_verify){html+='<div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px;">✓ '+r.how_to_verify+'</div>';}html+='</div>';});html+='</div>';}
  el.innerHTML = html;
}

/* ══════════════════════════════════════════════
   Schema Deep Audit
   ══════════════════════════════════════════════ */
async function runSchemaDeepAudit() {
  var url = document.getElementById('schemaDeepUrl').value.trim();
  if (!url) { showToast('Please enter a URL', 'error'); return; }
  var btn = document.getElementById('btnSchemaDeep');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Auditing...';
  try {
    var res = await (await fetch(API + '/api/schema/audit', {
      method: 'POST',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ url: url })
    })).json();
    renderSchemaDeepResults(res);
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btn.disabled = false; btn.innerHTML = '<i class="fas fa-code"></i> Run Schema Audit';
}
function renderSchemaDeepResults(data) {
  var el = document.getElementById('schemaDeepResults'); el.style.display = 'block';
  var score = data.score || 0;
  var c = score>=70?'success':score>=50?'warning':'danger';
  var html = '<div class="metrics-row">';
  html += '<div class="metric-card"><div class="metric-icon '+c+'"><i class="fas fa-code"></i></div><div class="metric-label">Schema Score</div><div class="metric-value" style="color:var(--'+c+')">'+score+'/100</div></div>';
  html += '<div class="metric-card"><div class="metric-icon purple"><i class="fas fa-cube"></i></div><div class="metric-label">Schemas Found</div><div class="metric-value">'+(data.schemas_found||0)+'</div></div>';
  html += '<div class="metric-card"><div class="metric-icon blue"><i class="fas fa-check-circle"></i></div><div class="metric-label">Valid</div><div class="metric-value">'+(data.valid_schemas||0)+'</div></div>';
  html += '<div class="metric-card"><div class="metric-icon '+(data.deprecated_types&&data.deprecated_types.length>0?'red':'green')+'"><i class="fas fa-exclamation-triangle"></i></div><div class="metric-label">Deprecated</div><div class="metric-value">'+(data.deprecated_types?data.deprecated_types.length:0)+'</div></div>';
  html += '</div>';
  if(data.types_with_rich_results&&data.types_with_rich_results.length>0){html+='<div class="card"><div class="card-header"><div class="card-title"><i class="fas fa-star" style="color:var(--warning);"></i> Rich Result Types</div></div><div style="display:flex;gap:8px;flex-wrap:wrap;">';data.types_with_rich_results.forEach(function(t){html+='<span class="badge badge-success">'+t+'</span>';});html+='</div></div>';}
  if(data.deprecated_types&&data.deprecated_types.length>0){html+='<div class="card"><div class="card-header"><div class="card-title" style="color:var(--danger);"><i class="fas fa-exclamation-circle"></i> Deprecated Types</div></div>';data.deprecated_types.forEach(function(d){html+='<div style="padding:10px 14px;border-radius:8px;background:var(--danger-bg);margin-bottom:8px;font-size:0.88rem;"><strong>'+d.type+'</strong> &mdash; '+d.reason+'<div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px;">Replacement: '+d.replacement+'</div></div>';});html+='</div>';}
  var schemas=data.schemas||[];
  if(schemas.length>0){html+='<div class="card"><div class="card-header"><div class="card-title"><i class="fas fa-list"></i> Schema Details</div></div>';schemas.forEach(function(s){var ic=s.issues?s.issues.length:0;html+='<div class="expander"><div class="expander-header" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')"><span><span class="badge badge-'+(s.has_rich_results?'success':'info')+'">'+s.type+'</span> ';html+=ic>0?'<span style="color:var(--danger);">'+ic+' issues</span>':'<span style="color:var(--success);">✓ Valid</span>';html+='</span><i class="fas fa-chevron-right chevron"></i></div><div class="expander-body">';if(s.fields_present&&s.fields_present.length>0){html+='<div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:6px;">Present: '+s.fields_present.join(', ')+'</div>';}if(s.fields_missing&&s.fields_missing.length>0){html+='<div style="font-size:0.85rem;color:var(--warning);margin-bottom:6px;">Missing: '+s.fields_missing.join(', ')+'</div>';}if(s.issues){s.issues.forEach(function(iss){html+='<div class="issue-item '+iss.severity+'"><i class="fas fa-'+(iss.severity==='critical'?'times-circle':iss.severity==='warning'?'exclamation-triangle':'info-circle')+' issue-icon"></i><div>'+iss.message+'</div></div>';});}html+='</div></div>';});html+='</div>';}
  var recs=data.recommendations||[];
  if(recs.length>0){html+='<div class="card"><div class="card-header"><div class="card-title"><i class="fas fa-lightbulb" style="color:var(--warning);"></i> Recommendations</div></div>';recs.forEach(function(r){html+='<div style="padding:8px 14px;border-radius:8px;background:var(--accent-light);margin-bottom:8px;font-size:0.88rem;"><span class="badge badge-'+(r.priority==='high'?'danger':'warning')+'">'+r.priority+'</span> '+r.action;if(r.how_to_verify){html+='<div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px;">✓ '+r.how_to_verify+'</div>';}html+='</div>';});html+='</div>';}
  el.innerHTML=html;
}

/* ══════════════════════════════════════════════
   GEO / AI Search Audit
   ══════════════════════════════════════════════ */
async function runGeoAudit() {
  var url = document.getElementById('geoUrl').value.trim();
  if (!url) { showToast('Please enter a URL', 'error'); return; }
  var btn = document.getElementById('btnGeo');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Analyzing...';
  try {
    var res = await (await fetch(API + '/api/geo/audit', {
      method: 'POST',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ url: url })
    })).json();
    renderGeoResults(res);
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btn.disabled = false; btn.innerHTML = '<i class="fas fa-robot"></i> Run GEO Audit';
}
function renderGeoResults(data) {
  var el = document.getElementById('geoResults'); el.style.display = 'block';
  var score = data.composite_score||0, grade = data.grade||'F', readiness = data.ai_readiness||'low';
  var c = score>=70?'success':score>=50?'warning':'danger';
  var html = '<div class="metrics-row">';
  html += '<div class="metric-card"><div class="metric-icon '+c+'"><i class="fas fa-robot"></i></div><div class="metric-label">GEO Score</div><div class="metric-value" style="color:var(--'+c+')">'+score+'/100 ('+grade+')</div></div>';
  html += '<div class="metric-card"><div class="metric-icon '+(readiness==='high'?'green':readiness==='medium'?'yellow':'red')+'"><i class="fas fa-brain"></i></div><div class="metric-label">AI Readiness</div><div class="metric-value">'+readiness.replace('_',' ')+'</div></div>';
  html += '</div>';
  var factors = data.factors||{};
  var names = {passage_citability:'Passage Citability',question_headings:'Question Headings',entity_presence:'Entity Presence',attribution_density:'Attribution Density'};
  var icons = {passage_citability:'fa-quote-right',question_headings:'fa-question-circle',entity_presence:'fa-globe',attribution_density:'fa-link'};
  for (var k in names) {
    var f = factors[k]||{}, fs=f.score||0, fm=f.max_score||25, r=fm>0?fs/fm:0;
    var fc=r>=0.6?'success':r>=0.4?'warning':'danger';
    html+='<div class="card"><div class="card-header"><div class="card-title"><i class="fas '+(icons[k]||'fa-check')+'" style="color:var(--'+fc+')"></i> '+names[k]+' <span class="badge badge-'+fc+'">'+fs+'/'+fm+'</span></div></div>';
    if(f.signals) f.signals.forEach(function(s){html+='<div style="padding:4px 14px;font-size:0.85rem;color:var(--text-secondary);">• '+s+'</div>';});
    html+='</div>';
  }
  var recs=data.recommendations||[];
  if(recs.length>0){html+='<div class="card"><div class="card-header"><div class="card-title"><i class="fas fa-lightbulb" style="color:var(--warning);"></i> Recommendations</div></div>';recs.forEach(function(r){html+='<div style="padding:8px 14px;border-radius:8px;background:var(--accent-light);margin-bottom:8px;font-size:0.88rem;"><span class="badge badge-'+(r.priority==='high'?'danger':'warning')+'">'+r.priority+'</span> '+r.action;if(r.how_to_verify){html+='<div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px;">✓ '+r.how_to_verify+'</div>';}html+='</div>';});html+='</div>';}
  el.innerHTML=html;
}

"""

marker = "/* Intent Training Functions */"
if marker in content and "runEeatAnalysis" not in content:
    content = content.replace(marker, JS_FUNCTIONS + marker)
    print("Injected JS functions")
elif "runEeatAnalysis" in content:
    print("JS functions already present")
else:
    print("WARNING: Could not find Intent Training Functions marker")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Done!")
