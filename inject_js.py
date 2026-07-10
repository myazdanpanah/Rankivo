"""Directly inject JS functions into index.html before last </script>"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

JS = """
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
    var el = document.getElementById('intentTrainingList');
    if (!el) return;
    var res = await (await fetch(API + '/api/intent-training', { headers: authHeaders() })).json();
    if (res.error) return;
    var data = res.training_data || {};
    var cnt = document.getElementById('intentTrainingCount');
    if (cnt) cnt.textContent = res.total || 0;
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
        var e = entries[i];
        var w = e.word || e;
        var l = e.language || 'auto';
        html += '<div style="display:flex;align-items:center;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border);">';
        html += '<span style="font-size:0.9rem;"><span class="badge badge-' + (colors[intent]||'info') + '">' + intent + '</span> ' + w + ' <span style="font-size:0.75rem;color:var(--text-muted);">[' + l + ']</span></span>';
        html += '<button class="btn btn-sm btn-danger" onclick="removeIntentWord(this.getAttribute(\'data-word\'),this.getAttribute(\'data-intent\'))" data-word="' + w.replace(/"/g, '&quot;') + '" data-intent="' + intent + '"><i class="fas fa-times"></i></button>';
        html += '</div>';
      }
      html += '</div></div>';
    }
    el.innerHTML = html || '<div style="padding:12px;color:var(--text-muted);">No training words yet. Add words above.</div>';
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
    html += '<strong>&quot;' + word + '&quot;</strong> &rarr; <span class="badge badge-' + (colors[r.intent]||'info') + '">' + (r.intent || 'unknown') + '</span>';
    html += ' (confidence: ' + ((r.confidence||0) * 100).toFixed(0) + '%, method: ' + (r.method||'heuristic') + ')';
    html += '</div>';
    var el = document.getElementById('intentTestResult');
    el.style.display = 'block';
    el.innerHTML = html;
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

/* Iran Province Trends */
var provinceChartInstance = null;

async function loadProvinceTrends(keywords) {
  if (!keywords || keywords.length === 0) return;
  var card = document.getElementById('trendsProvinceCard');
  if (!card) return;
  card.style.display = 'block';
  var statusEl = document.getElementById('provinceStatus');
  statusEl.textContent = 'Loading...';
  try {
    var res = await (await fetch(API + '/api/trends/iran-provinces', {
      method: 'POST',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ keywords: keywords.slice(0, 3) })
    })).json();
    if (res.error) { statusEl.textContent = res.error; return; }
    statusEl.textContent = 'Loaded';
    renderProvinceChart(res.data || {});
    renderProvinceRecommendations(res.data || {});
  } catch(e) { statusEl.textContent = 'Error'; console.error(e); }
}

function renderProvinceChart(data) {
  var canvas = document.getElementById('provinceChart');
  if (!canvas) return;
  if (provinceChartInstance) { provinceChartInstance.destroy(); provinceChartInstance = null; }
  var allP = {};
  var kws = Object.keys(data);
  for (var k = 0; k < kws.length; k++) {
    var provs = data[kws[k]].provinces || [];
    for (var p = 0; p < provs.length; p++) {
      var name = provs[p].name_fa || provs[p].name_en;
      if (!allP[name]) allP[name] = {};
      allP[name][kws[k]] = provs[p].score;
    }
  }
  var sorted = Object.entries(allP).sort(function(a, b) {
    var sA = Object.values(a[1]).reduce(function(s, v) { return s + v; }, 0);
    var sB = Object.values(b[1]).reduce(function(s, v) { return s + v; }, 0);
    return sB - sA;
  }).slice(0, 15);
  var labels = sorted.map(function(x) { return x[0]; });
  var palette = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'];
  var datasets = kws.map(function(kw, i) {
    return {
      label: kw,
      data: sorted.map(function(x) { return (x[1][kw] || 0); }),
      backgroundColor: palette[i % palette.length] + '80',
      borderColor: palette[i % palette.length],
      borderWidth: 1,
      borderRadius: 4
    };
  });
  if (!datasets.length || !labels.length) {
    canvas.parentElement.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-muted);">No province data available</div>';
    return;
  }
  provinceChartInstance = new Chart(canvas, {
    type: 'bar',
    data: { labels: labels, datasets: datasets },
    options: {
      responsive: true, maintainAspectRatio: false, indexAxis: 'y',
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
  var el = document.getElementById('provinceRecommendations');
  if (el) el.innerHTML = html;
}

function triggerProvinceTrendsFromKeywords() {
  var kwInput = document.getElementById('trendsKeywords');
  if (kwInput && kwInput.value.trim()) {
    var kws = kwInput.value.split(',').map(function(s) { return s.trim(); }).filter(Boolean);
    if (kws.length > 0) loadProvinceTrends(kws);
  }
}
"""

# Only inject if function definitions are NOT present
if 'function addIntentWord' not in c:
    idx = c.rfind('</script>')
    if idx > 0:
        c = c[:idx] + JS + '\n' + c[idx:]
        with open('static/index.html', 'w', encoding='utf-8') as f:
            f.write(c)
        print('Injected JS functions successfully')
    else:
        print('ERROR: No closing script tag found')
else:
    print('JS functions already exist')

# Hook province trends into loadTrends callback
if 'function triggerProvinceTrendsFromKeywords' in c and 'triggerProvinceTrendsFromKeywords()' not in c.split('function triggerProvinceTrends')[0][-500:]:
    with open('static/index.html', 'r', encoding='utf-8') as f:
        c = f.read()
    for pat in ['renderTrendsChart(data);', 'renderTrendsChart(d);']:
        if pat in c and 'triggerProvinceTrendsFromKeywords' not in c.split(pat)[-1][:100]:
            c = c.replace(pat, pat + '\n          triggerProvinceTrendsFromKeywords();', 1)
            with open('static/index.html', 'w', encoding='utf-8') as f:
                f.write(c)
            print('Hooked province trends into loadTrends')
            break
    else:
        print('Province trends hook already present or pattern not found')

# Hook loadIntentTraining into settings nav
with open('static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()
old_nav = "if (page === 'settings') loadUsers();"
new_nav = "if (page === 'settings') { loadUsers(); loadIntentTraining(); }"
if old_nav in c and 'loadIntentTraining' not in c.split("page === 'settings'")[-1][:200]:
    c = c.replace(old_nav, new_nav)
    with open('static/index.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print('Hooked loadIntentTraining into settings nav')
else:
    print('Settings nav hook already present')

print('Done!')
