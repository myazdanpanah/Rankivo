"""Inject all missing JS button handler functions into index.html"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

existing = set(re.findall(r'(?:async )?function (\w+)\(', c))

MISSING_JS = r"""
/* ══════════════════════════════════════════════
   Button Handler Functions (injected)
   ══════════════════════════════════════════════ */

async function runEeatAnalysis() {
  var url = document.getElementById('eeatUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnEeat', true);
  try {
    var res = await (await fetch(API + '/api/eeat/analyze', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('eeatResults', res, 'E-E-A-T Analysis');
    showToast('E-E-A-T analysis complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnEeat', false);
}

async function runSchemaDeepAudit() {
  var url = document.getElementById('schemaDeepUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnSchemaDeep', true);
  try {
    var res = await (await fetch(API + '/api/schema/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('schemaDeepResults', res, 'Schema Audit');
    showToast('Schema audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnSchemaDeep', false);
}

async function runGeoAudit() {
  var url = document.getElementById('geoUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnGeo', true);
  try {
    var res = await (await fetch(API + '/api/geo/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('geoResults', res, 'GEO / AI Search Audit');
    showToast('GEO audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnGeo', false);
}

async function runImageAnalysis() {
  var url = document.getElementById('imageUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnImages', true);
  try {
    var res = await (await fetch(API + '/api/images/analyze', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('imageResults', res, 'Image SEO Analysis');
    showToast('Image analysis complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnImages', false);
}

async function runSitemapAudit() {
  var url = document.getElementById('sitemapUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnSitemap', true);
  try {
    var res = await (await fetch(API + '/api/sitemap/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('sitemapResults', res, 'Sitemap Audit');
    showToast('Sitemap audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnSitemap', false);
}

async function runHreflangAudit() {
  var url = document.getElementById('hreflangUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnHreflang', true);
  try {
    var res = await (await fetch(API + '/api/hreflang/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('hreflangResults', res, 'Hreflang Audit');
    showToast('Hreflang audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnHreflang', false);
}

async function runLocalSeoAudit() {
  var url = document.getElementById('localSeoUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnLocalSeo', true);
  try {
    var res = await (await fetch(API + '/api/local-seo/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('localSeoResults', res, 'Local SEO Audit');
    showToast('Local SEO audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnLocalSeo', false);
}

async function runEcommerceAudit() {
  var url = document.getElementById('ecommerceUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnEcommerce', true);
  try {
    var res = await (await fetch(API + '/api/ecommerce/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('ecommerceResults', res, 'E-commerce SEO Audit');
    showToast('E-commerce audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnEcommerce', false);
}

async function runSxoAudit() {
  var url = document.getElementById('sxoUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnSxo', true);
  try {
    var res = await (await fetch(API + '/api/sxo/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('sxoResults', res, 'SXO Audit');
    showToast('SXO audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnSxo', false);
}

async function runContentBrief() {
  var topic = document.getElementById('briefTopic').value.trim();
  if (!topic) { showToast('Enter a topic', 'error'); return; }
  btnLoading('btnBrief', true);
  try {
    var res = await (await fetch(API + '/api/content-brief/generate', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({topic: topic, keywords: [topic]})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('briefResults', res, 'Content Brief');
    showToast('Content brief generated!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnBrief', false);
}

async function runProgSeoAudit() {
  var url = document.getElementById('progSeoUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnProgSeo', true);
  try {
    var res = await (await fetch(API + '/api/programmatic/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('progSeoResults', res, 'Programmatic SEO Audit');
    showToast('Programmatic SEO audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnProgSeo', false);
}

async function runSeoPlan() {
  var industry = document.getElementById('seoPlanIndustry') ? document.getElementById('seoPlanIndustry').value : 'saas';
  btnLoading('btnSeoPlan', true);
  try {
    var res = await (await fetch(API + '/api/plan/generate', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({industry: industry})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('seoPlanResults', res, 'SEO Strategy Plan');
    showToast('SEO plan generated!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnSeoPlan', false);
}

async function loadTrends() {
  var kw = document.getElementById('trendsKeyword') ? document.getElementById('trendsKeyword').value.trim() : '';
  if (!kw) { showToast('Enter a keyword', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/trends/interest-over-time', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({keywords: [kw]})
    })).json();
    showToast('Trends loaded for: ' + kw, 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function runBingAnalysis() {
  var url = document.getElementById('bingUrl') ? document.getElementById('bingUrl').value.trim() : '';
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnBing', true);
  try {
    var res = await (await fetch(API + '/api/bing/analyze', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    showToast('Bing analysis complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnBing', false);
}

async function checkBingIndex() {
  var url = document.getElementById('bingUrl') ? document.getElementById('bingUrl').value.trim() : '';
  if (!url) { showToast('Enter a URL', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/bing/index-status', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    showToast('Index check complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function submitToBing() {
  var url = document.getElementById('bingUrl') ? document.getElementById('bingUrl').value.trim() : '';
  if (!url) { showToast('Enter a URL', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/bing/submit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    showToast('URL submitted to Bing!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function changeMyPassword() {
  var oldPw = document.getElementById('oldPassword') ? document.getElementById('oldPassword').value : '';
  var newPw = document.getElementById('newPassword') ? document.getElementById('newPassword').value : '';
  if (!oldPw || !newPw) { showToast('Enter both passwords', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/auth/change-password', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({old_password: oldPw, new_password: newPw})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    showToast('Password changed!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function createNewUser() {
  var u = document.getElementById('newUsername') ? document.getElementById('newUsername').value.trim() : '';
  var p = document.getElementById('newUserPassword') ? document.getElementById('newUserPassword').value : '';
  var r = document.getElementById('newUserRole') ? document.getElementById('newUserRole').value : 'user';
  if (!u || !p) { showToast('Enter username and password', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/users', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({username: u, password: p, role: r})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    showToast('User created: ' + u, 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}
"""

# Find which functions need injection
all_needed = ['runEeatAnalysis', 'runSchemaDeepAudit', 'runGeoAudit', 'runImageAnalysis',
              'runSitemapAudit', 'runHreflangAudit', 'runLocalSeoAudit', 'runEcommerceAudit',
              'runSxoAudit', 'runContentBrief', 'runProgSeoAudit', 'runSeoPlan',
              'loadTrends', 'runBingAnalysis', 'checkBingIndex', 'submitToBing',
              'changeMyPassword', 'createNewUser']

missing = [f for f in all_needed if f not in existing]

if not missing:
    print('All functions already defined!')
else:
    print(f'Injecting {len(missing)} missing functions...')
    idx = c.rfind('</script>')
    if idx > 0:
        c = c[:idx] + MISSING_JS + '\n' + c[idx:]
        with open('static/index.html', 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'Successfully injected: {", ".join(missing)}')
    else:
        print('ERROR: Could not find </script> tag')

# Verify
with open('static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()
final = set(re.findall(r'(?:async )?function (\w+)\(', c))
still_missing = [f for f in all_needed if f not in final]
if still_missing:
    print(f'STILL MISSING: {still_missing}')
else:
    print(f'All {len(all_needed)} functions verified present!')
