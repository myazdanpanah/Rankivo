"""Inject Intent Training UI, Province Trends, and JS functions into index.html"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

changes = []

# 1. Add Intent Training card before Preferences
if 'intentTrainingCount' not in c:
    old = '<i class="fas fa-palette"></i> <span data-i18n="preferences">Preferences</span>'
    replacement = (
        '<div class="card">\n'
        '        <div class="card-header">\n'
        '          <div class="card-title"><i class="fas fa-brain"></i> Intent Training</div>\n'
        '          <span class="badge badge-purple" id="intentTrainingCount">0</span>\n'
        '        </div>\n'
        '        <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">Add custom words/phrases to improve AI intent classification.</p>\n'
        '        <div class="form-row">\n'
        '          <div class="form-group">\n'
        '            <label class="form-label" for="intentWord">Word / Phrase</label>\n'
        '            <input type="text" class="form-input" id="intentWord" placeholder="e.g. cost calculator" onkeydown="if(event.key===\'Enter\') addIntentWord()">\n'
        '          </div>\n'
        '          <div class="form-group">\n'
        '            <label class="form-label" for="intentCategory">Intent Category</label>\n'
        '            <select class="form-select" id="intentCategory">\n'
        '              <option value="transactional">Transactional (buy/download)</option>\n'
        '              <option value="navigational">Navigational (login/official)</option>\n'
        '              <option value="informational">Informational (how-to/guide)</option>\n'
        '              <option value="commercial">Commercial (best/review)</option>\n'
        '            </select>\n'
        '          </div>\n'
        '        </div>\n'
        '        <div style="display:flex;gap:8px;margin-bottom:16px;">\n'
        '          <button class="btn btn-primary btn-sm" onclick="addIntentWord()"><i class="fas fa-plus"></i> Add Word</button>\n'
        '          <button class="btn btn-secondary btn-sm" onclick="loadIntentTraining()"><i class="fas fa-sync"></i> Refresh</button>\n'
        '          <button class="btn btn-secondary btn-sm" onclick="testIntentClassifier()"><i class="fas fa-play"></i> Test</button>\n'
        '        </div>\n'
        '        <div id="intentTrainingList"></div>\n'
        '        <div id="intentTestResult" style="display:none;margin-top:12px;"></div>\n'
        '      </div>\n\n'
        '      <div class="card">\n'
        '        <div class="card-header">\n'
        '          <div class="card-title"><i class="fas fa-palette"></i> <span data-i18n="preferences">Preferences</span></div>'
    )
    c = c.replace(old, replacement, 1)
    changes.append('Added Intent Training card')

# 2. Add Iran Province Trends card
if 'provinceChart' not in c:
    old = '<div id="trendsRelatedContainer"'
    replacement = (
        '<div class="card" id="trendsProvinceCard" style="display:none;">\n'
        '          <div class="card-header">\n'
        '            <div class="card-title"><i class="fas fa-map-marked-alt" style="color:var(--accent);"></i> Iran Province Trends</div>\n'
        '            <span class="badge badge-info" id="provinceStatus">Loading...</span>\n'
        '          </div>\n'
        '          <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:12px;">Search interest by Iranian province.</p>\n'
        '          <div class="chart-container" style="height:350px;"><canvas id="provinceChart"></canvas></div>\n'
        '          <div id="provinceRecommendations" style="margin-top:12px;"></div>\n'
        '        </div>\n\n'
        '        <div id="trendsRelatedContainer"'
    )
    c = c.replace(old, replacement, 1)
    changes.append('Added Province Trends card')

# 3. Add JavaScript functions
JS = r"""
/* Intent Training Functions */
async function addIntentWord() {
  var word = document.getElementById('intentWord').value.trim();
  var intent = document.getElementById('intentCategory').value;
  if (!word) { showToast('Enter a word or phrase', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/intent-training', {
      method: 'POST',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ word: word, intent: intent })
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    document.getElementById('intentWord').value = '';
    showToast('Added: ' + word + ' -> ' + intent, 'success');
    loadIntentTraining();
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function loadIntentTraining() {
  try {
    var res = await (await fetch(API + '/api/intent-training', { headers: authHeaders() })).json();
    if (res.error) return;
    var data = res.training_data || {};
    document.getElementById('intentTrainingCount').textContent = res.total || 0;
    var html = '';
    var colors = { transactional: 'danger', navigational: 'info', informational: 'success', commercial: 'warning' };
    for (var intent in data) {
      var entries = data[intent];
      if (!entries || entries.length === 0) continue;
      html += '<div class="expander">';
      html += '<div class="expander-header" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">';
      html += '<span>' + intent.charAt(0).toUpperCase() + intent.slice(1) + ' (' + entries.length + ')</span>';
      html += '<i class="fas fa-chevron-right chevron"></i></div>';
      html += '<div class="expander-body">';
      for (var i = 0; i < entries.length; i++) {
        var entry = entries[i];
        var word = entry.word || entry;
        var lang = entry.language || 'auto';
        html += '<div style="display:flex;align-items:center;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border);">';
        html += '<span style="font-size:0.9rem;"><span class="badge badge-' + (colors[intent]||'info') + '">' + intent + '</span> ' + word + ' <span style="font-size:0.75rem;color:var(--text-muted);">[' + lang + ']</span></span>';
        html += '<button class="btn btn-sm btn-danger" onclick="removeIntentWord(\'' + word.replace(/'/g,"\\'") + '\',\'' + intent + '\')"><i class="fas fa-times"></i></button>';
        html += '</div>';
      }
      html += '</div></div>';
    }
    document.getElementById('intentTrainingList').innerHTML = html || '<div style="padding:12px;color:var(--text-muted);">No training words yet.</div>';
  } catch(e) { console.error('Load intent error:', e); }
}

async function removeIntentWord(word, intent) {
  try {
    await fetch(API + '/api/intent-training', {
      method: 'DELETE',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ word: word, intent: intent })
    });
    showToast('Removed: ' + word, 'success');
    loadIntentTraining();
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function testIntentClassifier() {
  var word = document.getElementById('intentWord').value.trim() || 'buy shoes online';
  try {
    var res = await (await fetch(API + '/api/persian-intent/classify', {
      method: 'POST',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ keyword: word })
    })).json();
    var r = res.result || {};
    var colors = { transactional: 'danger', navigational: 'info', informational: 'success', commercial: 'warning' };
    var html = '<div style="padding:12px;border-radius:8px;background:var(--bg-input);">';
    html += '<strong>"' + word + '"</strong> -> <span class="badge badge-' + (colors[r.intent]||'info') + '">' + (r.intent || 'unknown') + '</span>';
    html += ' (confidence: ' + ((r.confidence||0) * 100).toFixed(0) + '%, method: ' + (r.method||'heuristic') + ')';
    html += '</div>';
    document.getElementById('intentTestResult').style.display = 'block';
    document.getElementById('intentTestResult').innerHTML = html;
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

/* Iran Province Trends */
var provinceChartInstance = null;

async function loadProvinceTrends(keywords) {
  if (!keywords || keywords.length === 0) return;
  var card = document.getElementById('trendsProvinceCard');
  if (!card) return;
  card.style.display = 'block';
  document.getElementById('provinceStatus').textContent = 'Loading...';
  try {
    var res = await (await fetch(API + '/api/trends/iran-provinces', {
      method: 'POST',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ keywords: keywords.slice(0, 3) })
    })).json();
    if (res.error) { document.getElementById('provinceStatus').textContent = res.error; return; }
    document.getElementById('provinceStatus').textContent = 'Loaded';
    renderProvinceChart(res.data || {});
    renderProvinceRecommendations(res.data || {});
  } catch(e) { document.getElementById('provinceStatus').textContent = 'Error'; console.error(e); }
}

function renderProvinceChart(data) {
  var canvas = document.getElementById('provinceChart');
  if (!canvas) return;
  if (provinceChartInstance) { provinceChartInstance.destroy(); provinceChartInstance = null; }
  var allProvinces = {};
  var kws = Object.keys(data);
  for (var k = 0; k < kws.length; k++) {
    var provinces = data[kws[k]].provinces || [];
    for (var p = 0; p < provinces.length; p++) {
      var name = provinces[p].name_fa || provinces[p].name_en;
      if (!allProvinces[name]) allProvinces[name] = {};
      allProvinces[name][kws[k]] = provinces[p].score;
    }
  }
  var sorted = Object.entries(allProvinces).sort(function(a, b) {
    var sumA = Object.values(a[1]).reduce(function(s, v) { return s + v; }, 0);
    var sumB = Object.values(b[1]).reduce(function(s, v) { return s + v; }, 0);
    return sumB - sumA;
  }).slice(0, 15);

  var labels = sorted.map(function(x) { return x[0]; });
  var colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'];
  var datasets = kws.map(function(kw, i) {
    return {
      label: kw,
      data: sorted.map(function(x) { return (x[1][kw] || 0); }),
      backgroundColor: colors[i % colors.length] + '80',
      borderColor: colors[i % colors.length],
      borderWidth: 1,
      borderRadius: 4
    };
  });

  if (datasets.length === 0 || labels.length === 0) {
    canvas.parentElement.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-muted);">No province data</div>';
    return;
  }
  provinceChartInstance = new Chart(canvas, {
    type: 'bar',
    data: { labels: labels, datasets: datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: { legend: { position: 'top' } },
      scales: { x: { beginAtZero: true, title: { display: true, text: 'Search Interest (0-100)' } } }
    }
  });
}

function renderProvinceRecommendations(data) {
  var html = '';
  for (var kw in data) {
    if (data[kw].recommendation) {
      html += '<div style="padding:10px 14px;border-radius:8px;background:var(--accent-light);margin-bottom:8px;font-size:0.9rem;color:var(--accent);">';
      html += '<i class="fas fa-lightbulb"></i> <strong>' + kw + ':</strong> ' + data[kw].recommendation;
      html += '</div>';
    }
  }
  document.getElementById('provinceRecommendations').innerHTML = html;
}

function triggerProvinceTrendsFromKeywords() {
  var kwInput = document.getElementById('trendsKeywords');
  if (kwInput && kwInput.value.trim()) {
    var kws = kwInput.value.split(',').map(function(s) { return s.trim(); }).filter(Boolean);
    if (kws.length > 0) loadProvinceTrends(kws);
  }
}
"""

if 'addIntentWord' not in c:
    idx = c.rfind('</script>')
    if idx > 0:
        c = c[:idx] + JS + '\n' + c[idx:]
        changes.append('Added JS functions')
    else:
        changes.append('WARN: no closing script tag found')
else:
    changes.append('WARN: JS functions already exist')

# 4. Hook province trends into loadTrends
if 'triggerProvinceTrendsFromKeywords' not in c:
    for pat in ['renderTrendsChart(data);', 'renderTrendsChart(d);']:
        if pat in c:
            c = c.replace(pat, pat + '\n          triggerProvinceTrendsFromKeywords();', 1)
            changes.append('Hooked province trends into loadTrends')
            break

# 5. Hook loadIntentTraining into settings nav
old_nav = "if (page === 'settings') loadUsers();"
new_nav = "if (page === 'settings') { loadUsers(); loadIntentTraining(); }"
if old_nav in c and 'loadIntentTraining' not in c.split("page === 'settings'")[-1][:200]:
    c = c.replace(old_nav, new_nav)
    changes.append('Hooked loadIntentTraining into settings nav')

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

for ch in changes:
    print(ch)
print(f'\nTotal changes: {len(changes)}')
