from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / 'app/assets/index.html'
s = p.read_text(encoding='utf-8')
assert 'v1.7.9 Test' in s, 'Run only against the unmodified v1.7.9 UI.'
s = s.replace('v1.7.9 Test', 'Desktop Beta 0.1.0', 1).replace('class="footerVersion">v1.7.9', 'class="footerVersion">Desktop Beta 0.1.0', 1)
s = s.replace('localStorage', 'appStorage')
needle = '<script>\n(()=>{const $='
assert needle in s
s = s.replace(needle, '<!--DESKTOP_BOOTSTRAP-->\n<script>\n(()=>{const appStorage=window.FTDesktopStorage;if(!appStorage){document.body.textContent="Launch freETarget Desktop with START_DESKTOP.bat or the built executable.";return}const $=', 1)
a = s.index('async function logoStore(operation,value){')
b = s.index('function displayLogo(', a)
s = s[:a] + """async function logoStore(operation,value){
 if(operation==='get')return readJSON('ft-custom-logo-v1',null);
 if(operation==='put')appStorage.setItem('ft-custom-logo-v1',JSON.stringify(value));else appStorage.removeItem('ft-custom-logo-v1');
}
""" + s[b:]
s = s.replace('<div id="settingsGeneral" data-tab="general" class="settingsContent">', '<div id="settingsGeneral" data-tab="general" class="settingsContent">'+(root/'app/assets/desktop_data.html').read_text(), 1)
s = s.replace("alert('The score could not be saved. Your shots are still here. Free browser storage and try again.')", "alert('The score could not be saved. Your shots are still here. '+e.message)")
s = s.replace('Browser storage may be full.', 'Local data could not be saved. Check available disk space.')
s = s.replace('browser storage may be full', 'local data could not be saved')
s = s.replace("window.addEventListener('beforeunload',e=>{if(shots.length&&!logged&&!reviewingHistory){e.preventDefault();e.returnValue=''}});", '// The native close coordinator stops the session and confirms unlogged results.')
extra = """
window.FTDesktopSessionState=()=>{const state=reviewingHistory&&liveSnapshot?liveSnapshot:{shots,sightingShots,runtime,ended,logged};return {unsaved:!state.logged&&!!(state.shots?.length||state.sightingShots?.length||state.runtime),active:!!state.runtime&&!state.ended,connected:liveConnected||liveConnecting}};
window.FTDesktopPrepareClose=()=>{if(reviewingHistory&&liveSnapshot){liveSnapshot.running=false}else if(isFiveLive()&&!ended){fiveInterrupt('Desktop Window Closing.')}else if(running){pauseTimer();running=false;render()}return window.FTDesktopSessionState()};
""" + (root/'app/assets/desktop_ui.js').read_text() + '\ninitDesktopData();\n'
needle = 'loadShooters();refreshSessionOptions();loadRuleCatalog();renderColorFields();'
assert needle in s
s = s.replace(needle, extra+needle, 1)
s = s.replace("function selectSettingsTab(tab){", "function selectSettingsTab(tab){if(tab==='general')window.FTDesktopRefreshInfo?.();", 1)
s = s.replace('</style></head>', '''</style><style>
.desktopDataControls{padding-bottom:18px;margin-bottom:18px;border-bottom:1px solid var(--line)}.desktopDataControls h3{margin:0 0 10px}.desktopDataControls .settingsHelp{margin:8px 0}.desktopDataControls details{font-size:12px;margin-top:10px}.desktopDataControls code{display:block;overflow-wrap:anywhere;font-size:11px;margin-top:7px}.desktopRestoreConfirm{padding:12px;margin-top:12px;border:1px solid #cb595b;background:var(--bg)}#desktopRestoreConfirm[hidden]{display:none!important}#desktopRestorePreview{font:12px/1.6 inherit;white-space:pre-wrap;margin:0}
</style></head>''', 1)
p.write_text(s, encoding='utf-8')
print('Desktop UI prepared from v1.7.9; scoring and hardware algorithms retained.')
