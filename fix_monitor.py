"""Fix monitoring dashboard and add score drop alerts"""
import os
os.chdir('C:/Rankivo')

changes = []

# 1. Fix monitoring dashboard to use correct element ID
with open('static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

old = "document.getElementById('monitorUrl')"
new = "document.getElementById('perfUrl')"
if old in c:
    c = c.replace(old, new, 1)
    changes.append('Fixed monitorUrl -> perfUrl')

# 2. Add refresh rate selector after perfUrl input
old_input = """<input type="text" class="form-input" id="perfUrl" placeholder="https://example.com" onkeydown="if(event.key==='Enter') loadPerformanceDashboard()">"""
new_input = old_input + """
            <select id="monitorRate" class="form-select" style="width:auto;" onchange="setMonitorRate(this.value)">
              <option value="30000">Refresh: 30s</option>
              <option value="15000">Refresh: 15s</option>
              <option value="60000">Refresh: 60s</option>
              <option value="0">Auto-refresh: Off</option>
            </select>"""

if 'monitorRate' not in c and old_input in c:
    c = c.replace(old_input, new_input, 1)
    changes.append('Added refresh rate selector')

# 3. Add setMonitorRate function
if 'function setMonitorRate' not in c:
    rate_fn = """

function setMonitorRate(ms) {
  monitorRefreshRate = parseInt(ms) || 30000;
  if (monitorRefreshRate > 0) {
    startMonitorAutoRefresh();
    if (typeof showToast === 'function') showToast('Auto-refresh set to ' + (monitorRefreshRate/1000) + 's', 'info');
  } else {
    stopMonitorAutoRefresh();
    if (typeof showToast === 'function') showToast('Auto-refresh disabled', 'info');
  }
}
"""
    marker = '</body>'
    idx = c.find(marker)
    if idx > 0:
        c = c[:idx] + rate_fn + c[idx:]
        changes.append('Added setMonitorRate function')

# 4. Add score drop alert notification
if 'checkScoreDrop' not in c:
    alert_fn = """

// Score Drop Alerts
let _lastScore = null;
function checkScoreDrop(newScore) {
  if (_lastScore !== null && newScore < _lastScore - 5) {
    const drop = _lastScore - newScore;
    if (typeof showToast === 'function') {
      showToast('Score dropped by ' + drop + ' points! (' + _lastScore + ' -> ' + newScore + ')', 'warning');
    }
    if (Notification && Notification.permission === 'granted') {
      new Notification('Rankivo SEO Alert', {
        body: 'Score dropped by ' + drop + ' points: ' + _lastScore + ' -> ' + newScore,
        icon: '/favicon.ico'
      });
    }
  }
  _lastScore = newScore;
}

function requestNotificationPermission() {
  if (Notification && Notification.permission === 'default') {
    Notification.requestPermission();
  }
}
"""
    marker2 = '</body>'
    idx2 = c.find(marker2)
    if idx2 > 0:
        c = c[:idx2] + alert_fn + c[idx2:]
        changes.append('Added score drop alerts')

# 5. Add checkScoreDrop call in updateMonitorDisplay
if 'checkScoreDrop(scores.overall_score)' not in c:
    old_display = 'container.innerHTML = html;'
    new_display = 'if (scores.overall_score !== undefined) checkScoreDrop(scores.overall_score);\n  container.innerHTML = html;'
    if old_display in c:
        c = c.replace(old_display, new_display, 1)
        changes.append('Added score drop check to monitor display')

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

for ch in changes:
    print(ch)
print(f'Total: {len(changes)} changes')
