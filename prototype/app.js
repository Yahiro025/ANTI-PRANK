const { initial, transition, status } = NiceTry;
let state = initial();
let route = location.hash.slice(1) || 'dashboard';
let pairStep = 0;
let pairTimer;
const paths = {
 dashboard:'<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
 phone:'<rect x="6" y="2" width="12" height="20" rx="3"/><path d="M10 5h4m-3 14h2"/>',
 activity:'<path d="M3 12h4l3-8 4 16 3-8h4"/>',
 settings:'<path d="M4 7h16M4 17h16"/><circle cx="8" cy="7" r="3"/><circle cx="16" cy="17" r="3"/>',
 brand:'<path d="m12 3 3 6 6 3-6 3-3 6-3-6-6-3 6-3Z"/>',
 lock:'<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 5v2"/>',
 shield:'<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="m8 12 3 3 5-6"/>',
 arrow:'<path d="M4 12h16m-6-6 6 6-6 6"/>',
 check:'<path d="m5 12 4 4L19 6"/>',
 coffee:'<path d="M4 8h13v9a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4Zm13 1h2a3 3 0 0 1 0 6h-2M7 2v2m5-2v2"/>',
 bluetooth:'<path d="m8 7 9 10-5 4V3l5 4L8 17"/>',
 warning:'<path d="m12 3 10 18H2Z"/><path d="M12 9v5m0 3v1"/>',
 input:'<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M6 9h1m4 0h1m4 0h1M6 13h1m4 0h1m4 0h1m-9 3h8"/>',
 pause:'<path d="M8 5v14M16 5v14"/>',
};
function icon(name) { return `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">${paths[name] || paths.shield}</svg>`; }
const eyes = '<span class="eyes" aria-hidden="true"><i class="eye"></i><i class="eye"></i></span>';
const labels = { dashboard:'Overview', phone:'My phone', activity:'Activity', settings:'Settings', brand:'Brand kit' };
document.querySelectorAll('[data-route]').forEach(a => a.innerHTML = icon(a.dataset.route) + labels[a.dataset.route]);
function btn(text, action, kind='primary', symbol='') { return `<button class="btn ${kind}" data-action="${action}">${symbol ? icon(symbol) : ''}${text}</button>`; }
function heading(title, description, action='') { return `<div class="page-title"><div><h1>${title}</h1><p>${description}</p></div>${action}</div>`; }
function badge() { const s=status(state); return `<span class="pill ${s.tone}">${icon(s.tone==='safe'?'shield':'warning')}${s.label}</span>`; }
function logs(limit=99) {
 if (!state.events.length) return '<div class="empty">Nothing suspicious. A beautiful lack of drama.<br><span class="small">Try “Walk away”, then “Simulate input” below.</span></div>';
 return state.events.slice(0,limit).map(e=>`<div class="event"><span class="event-symbol ${e.type}">${icon(e.type==='warning'?'warning':e.type==='safe'?'lock':'activity')}</span><div><strong>${e.title}</strong><p>${e.detail}</p></div><time>${e.time}</time></div>`).join('');
}
function phoneName() { return state.paired ? 'Your phone' : 'No phone paired'; }
function proximityLabel() { return !state.paired ? 'Pairing required' : state.proximity==='near' ? 'Nearby · strong signal' : state.proximity==='away' ? 'Away · weak signal' : 'Signal unavailable'; }
function dashboard() {
 const s=status(state);
 return heading('Your laptop. Your rules.','Your coffee break. Your laptop’s business.',btn(state.monitoring?'Pause monitoring':'Enable monitoring','toggle','secondary',state.monitoring?'pause':'shield')) +
 `<div class="dashboard"><section class="guardian ${state.locked?'locked':''}" aria-label="Protection status"><div class="guardian-top">${badge()}<span class="small">Laptop guardian</span></div><div class="guardian-copy"><h2>${s.title}</h2><p>${s.detail}</p></div><div class="proximity" aria-label="${proximityLabel()}"><div class="orbit outer"></div><div class="orbit"></div><div class="orbit inner"></div><div class="laptop">${state.locked?icon('lock'):eyes}</div><div class="phone-dot ${state.proximity!=='near'?'away':''}">${icon('phone')}</div><p class="proximity-label">${proximityLabel()}</p></div><div class="guardian-bottom"><span>${icon(state.locked?'lock':'shield')}${state.locked?'Session locked':'Ready when you leave'}</span><span>${icon('bluetooth')}Proximity, not GPS</span></div></section>
 <div class="right-column"><section class="panel"><div class="panel-heading"><h2>Your plus-one</h2>${icon('bluetooth')}</div><div class="device"><span class="device-icon">${icon('phone')}</span><div><strong>${phoneName()}</strong><p>${state.paired?'Paired demo device':'Automatic protection off'}</p></div></div><div class="device-info"><span>Connection</span><strong>${state.paired&&state.proximity!=='lost'?'Connected':'Unavailable'}</strong></div><a href="#phone" class="text-link">${state.paired?'Manage phone':'Pair your phone'} →</a></section><section class="panel rule">${icon('coffee')}<h3>Protect the session.<br>Not the gossip.</h3><p>No camera. No recorded keystrokes. Just a very firm boundary.</p></section></div></div>
 <div class="section-title"><h2>The latest non-drama</h2><a class="text-link" href="#activity">View all activity →</a></div><section class="activity-list" aria-label="Recent activity">${logs(2)}</section>`;
}
function phone() {
 if (route==='setup') return setup();
 return heading('The phone is the plus-one.','A companion that keeps an eye on your laptop.',btn('Pairing & setup','setup','secondary','bluetooth')) +
 `<div class="phone-stage"><section class="phone-frame" aria-label="Simulated phone companion"><div class="phone-top"><span>9:41</span><span>Companion preview</span></div><span class="wordmark">NICE TRY.</span><h2>${state.locked?'Seat’s taken.':'Coffee, on your terms.'}</h2><p class="small muted">Your laptop · simulated connection</p><div class="phone-state">${eyes}<br>${badge()}<p>${status(state).detail}</p></div>${btn(state.locked?'Session already locked':'Lock my laptop','lock', 'primary','lock')}<p class="auth-hint">Returning with your phone never unlocks the laptop.</p></section><aside class="phone-aside"><h2>Small phone.<br>Big “don’t.”</h2><p>Leave with your phone. The laptop locks when your phone leaves the nearby zone.</p><p>Unexpected input while away? An alert appears here when phone alerts are enabled.</p>${state.alerts&&state.events.some(e=>e.title==='Someone got curious.')?'<div class="notice"><strong>Someone got curious.</strong><br>Input detected while away. The session stayed locked.</div>':'<div class="notice">No away alerts right now.<br>Try the demo controls below.</div>'}<p>Phone UI concept only. No real notification or remote connection is sent.</p></aside></div>`;
}
function setup() {
 return heading('Hire your pocket-sized bouncer.','Pair once. Leave for coffee as often as you like.', '<a class="btn secondary" href="#phone">Back to phone</a>')+
 `<div class="content-split"><section class="panel"><div class="step"><span class="step-number">1</span><div><h3>Bring your phone along</h3><p>The native app would use Bluetooth to recognize your paired phone. This prototype uses a demo device.</p>${btn(pairStep===1?'Searching for demo phone…':pairStep===2?'Demo phone found':'Find demo phone','scan','secondary','bluetooth')}</div></div><div class="step"><span class="step-number">2</span><div><h3>Confirm the match</h3><p>${pairStep===2?'Demo pairing code: <strong>482 619</strong>. In the native app, confirm a matching code on both devices.':'Find the demo phone first to reveal a simulated pairing code.'}</p><button class="btn primary" data-action="pair" ${pairStep!==2?'disabled':''}>Confirm demo pairing</button></div></div><div class="step"><span class="step-number">3</span><div><h3>Take it for a coffee run</h3><p>Use “Walk away” below to test the lock. Use “Return nearby” and “Authenticate” to get back in.</p></div></div></section><aside class="notice"><h3>A boundary, not a tape measure.</h3><p style="margin-top:15px">Walls, pockets and radio interference affect Bluetooth signal strength. The product uses nearby / away states rather than pretending to measure exactly 10 meters.</p><p style="margin-top:15px">Native setup must verify Bluetooth permissions and a working OS lock before enabling protection. Permission failure must keep protection off.</p></aside></div>`;
}
function activity() { return heading('A paper trail. Minus the paper.','Illustrative events from this demo session.',btn('Clear activity','clear','secondary'))+`<section class="activity-list" aria-label="Activity history">${logs()}</section><p class="auth-hint">Session-only log. Nothing persists after reload. No key contents or personal identity are recorded.</p>`; }
function settings() { return heading('Boundaries look good on you.','A few rules for your very tiny security department.')+
 `<div class="content-split"><section class="panel"><div class="settings-section"><h3>Automatic protection</h3><p>Lock the session when your paired phone moves away. Losing the signal also locks it.</p><div class="setting-row"><label for="monitor">Enable monitoring</label><input id="monitor" class="switch" type="checkbox" ${state.monitoring?'checked':''} ${!state.paired?'disabled':''}></div></div><div class="settings-section"><h3>Phone alerts</h3><p>Show a companion alert when input happens while you’re away. Activity stays in the local demo log either way.</p><div class="setting-row"><label for="alerts">Show phone alerts</label><input id="alerts" class="switch" type="checkbox" ${state.alerts?'checked':''}></div></div><div class="settings-section"><h3>Nearby zone</h3><p id="zone-help">A native app would calibrate this to signal strength. This demo stores your preference without measuring a real distance.</p><div class="setting-row"><label for="sensitivity">Sensitivity</label><select id="sensitivity" aria-describedby="zone-help"><option value="close" ${state.sensitivity==='close'?'selected':''}>Close · stricter zone</option><option value="balanced" ${state.sensitivity==='balanced'?'selected':''}>Balanced · café default</option><option value="relaxed" ${state.sensitivity==='relaxed'?'selected':''}>Relaxed · wider zone</option></select></div></div><div class="settings-section"><h3>Paired device</h3><p>${phoneName()}. Disconnecting disables automatic monitoring and never unlocks an existing session.</p>${state.paired?btn('Disconnect demo phone','unpair','secondary'):btn('Pair a phone','setup','primary')}</div></section><aside><div class="notice"><h3>The serious bit.</h3><p style="margin-top:15px">A phone is a proximity hint, not proof of identity. Your laptop password or biometrics should always control unlocking.</p><p style="margin-top:15px">This concept doesn’t identify your friends or undo pranks already made. Lock before you leave when it matters.</p></div></aside></div>`; }
function brand() { return heading('A little attitude. A clear boundary.','The NICE TRY. identity, in one compact kit.')+
 `<section class="brand-hero"><div><span class="wordmark">NICE TRY.</span><p>Go get coffee.<br>Keep your dignity.</p></div>${eyes}</section><div class="brand-grid"><section class="panel"><h3>Not angry. Just watching.</h3><p>A deadpan bouncer for coffee shops, coworking spaces and the friends who know your unlocked laptop a little too well.</p><p class="voice-sample">“Someone got curious.”</p><p>Say what happened, then add a wink. Keep warnings and recovery instructions literal. Never shame, threaten or claim to know who touched the keyboard.</p></section><section class="panel"><h3>The house colors</h3><div class="swatches"><div class="swatch"><i style="--swatch:var(--ink)"></i>Grape<br>#30233F</div><div class="swatch"><i style="--swatch:var(--citron)"></i>Citron<br>#E4F786</div><div class="swatch"><i style="--swatch:var(--lilac)"></i>Lilac<br>#D8CBF4</div><div class="swatch"><i style="--swatch:var(--paper)"></i>Paper<br>#F7F7F2</div></div></section><section class="panel"><h3>Type with a raised eyebrow.</h3><p class="voice-sample" style="font-size:36px!important;font-weight:750">Bricolage Grotesque</p><p>One expressive variable face. Weight 750 for headings, 650 for controls, 400 for reading. Generous line-height, sentence case, and a little room to breathe.</p></section><section class="panel"><h3>A mark that minds your business.</h3><p>Two watchful eyes. Always together. Grape on citron or lilac, with clear space at least one pupil wide. Keep the mark flat, crisp and un-stretched.</p><a class="btn secondary wide-btn" href="assets/mark.svg" download="nice-try-mark.svg">Download SVG mark</a></section></div>`; }
function render() {
 const views={dashboard,phone,setup,activity,settings,brand};
 if (!views[route]) route='dashboard';
 document.querySelectorAll('[data-route]').forEach(a=>{ const active=a.dataset.route===(route==='setup'?'phone':route); if(active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current'); });
 document.getElementById('view').innerHTML=views[route]();
 document.title=`${route==='setup'?'Pairing':labels[route]} — NICE TRY.`;
 document.getElementById('simulator').innerHTML=`<section class="simulation" aria-label="Demo controls"><div><strong>Take it for a test walk.</strong><p>Simulate a coffee break. No actual locking.</p></div><div class="simulation-buttons"><button class="btn" data-action="away" aria-pressed="${state.proximity==='away'}" ${!state.paired?'disabled':''}>${icon('coffee')}Walk away</button><button class="btn" data-action="input">${icon('input')}Simulate input</button><button class="btn" data-action="near" aria-pressed="${state.proximity==='near'}" ${!state.paired?'disabled':''}>${icon('phone')}Return nearby</button><button class="btn" data-action="lost" aria-pressed="${state.proximity==='lost'}" ${!state.paired?'disabled':''}>${icon('bluetooth')}Lose signal</button></div>${state.locked?`<div style="width:100%;display:flex;align-items:center;gap:15px;flex-wrap:wrap"><button class="btn citron" data-action="authenticate" ${!state.paired||state.proximity!=='near'?'disabled':''}>Simulate OS authentication</button><p>${state.proximity==='near'&&state.paired?'Demo only: represents password or biometrics.':'Return nearby first to try simulated authentication.'}</p></div>`:''}</section>`;
 if (route==='phone'&&state.locked) document.querySelector('[data-action=lock]').disabled=true;
 if (!state.paired&&route==='dashboard') document.querySelector('[data-action=toggle]').disabled=true;
}
let toastTimer;
function toast(message){const el=document.getElementById('toast');el.textContent=message;el.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.hidden=true,3800);}
document.addEventListener('click',e=>{
 const button=e.target.closest('[data-action]');if(!button||button.disabled)return;
 const action=button.dataset.action;
 if(action==='setup'){location.hash='setup';return;}
 if(action==='scan'){pairStep=1;render();clearTimeout(pairTimer);pairTimer=setTimeout(()=>{pairStep=2;render();toast('Demo phone found. Confirm the matching code.');},700);return;}
 if(action==='pair'&&pairStep!==2)return;
 state=transition(state,action);
 if(action==='pair'){location.hash='phone';toast('Demo phone paired. Bouncer on duty.');}
 else if(action==='clear')toast('Demo activity cleared.');
 else if(action==='input')toast(state.events[0].title+' '+state.events[0].detail);
 else if(action==='unpair')toast('Phone disconnected. Automatic monitoring is off.');
 else if(action==='authenticate')toast('OS authentication simulated. Session unlocked.');
 else toast(status(state).label+'. '+(state.locked?'Session remains locked.':'Session is unlocked.'));
 render();
});
document.addEventListener('change',e=>{if(e.target.id==='monitor')state=transition(state,'toggle');if(e.target.id==='alerts')state.alerts=e.target.checked;if(e.target.id==='sensitivity')state.sensitivity=e.target.value;toast('Demo preference updated.');render();});
window.addEventListener('hashchange',()=>{route=location.hash.slice(1)||'dashboard';render();document.getElementById('view').focus();});
render();
