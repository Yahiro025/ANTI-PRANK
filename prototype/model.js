(function (root) {
  const initial = () => ({ paired: true, monitoring: true, proximity: 'near', locked: false, alerts: true, sensitivity: 'balanced', events: [] });
  function transition(state, action) {
    const s = { ...state, events: [...state.events] };
    const log = (title, detail, type = 'neutral') => s.events.unshift({ title, detail, type, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) });
    if (action === 'away' && s.paired) { s.proximity = 'away'; if (s.monitoring) { s.locked = true; log('Coffee break. Session locked.', 'Phone moved out of the nearby zone.', 'safe'); } }
    if (action === 'near' && s.paired) { s.proximity = 'near'; log('Welcome back, main character.', s.locked ? 'Phone is nearby. OS authentication is still required.' : 'Phone is back in the nearby zone.'); }
    if (action === 'lost' && s.paired) { s.proximity = 'lost'; if (s.monitoring) s.locked = true; log('Phone signal lost.', s.monitoring ? 'Locked as a precaution. Check Bluetooth on your phone.' : 'Monitoring is paused. No automatic lock.', 'warning'); }
    if (action === 'input') {
      if (s.monitoring && s.paired && s.proximity !== 'near') log('Someone got curious.', s.locked ? 'Input detected while away. The session stayed locked.' : 'Input detected while away.', 'warning');
      else log('Input received.', 'No away alert: you are nearby or monitoring is off.');
    }
    if (action === 'toggle' && s.paired) { s.monitoring = !s.monitoring; if (s.monitoring && s.proximity !== 'near') s.locked = true; log(s.monitoring ? 'Bouncer on duty.' : 'Monitoring paused.', s.locked ? 'The existing session lock stays in place.' : 'Session is unlocked.'); }
    if (action === 'lock') { s.locked = true; log('Session locked.', 'Manual lock from the demo.', 'safe'); }
    if (action === 'authenticate' && s.locked && s.proximity === 'near' && s.paired) { s.locked = false; log('You’re in.', 'OS authentication simulated.'); }
    if (action === 'unpair') { s.paired = false; s.monitoring = false; s.proximity = 'lost'; log('Phone disconnected.', 'Pair a phone to enable automatic protection.', 'warning'); }
    if (action === 'pair') { s.paired = true; s.proximity = 'near'; s.monitoring = true; log('Phone paired. Bouncer hired.', 'Demo phone connected. No real Bluetooth connection.', 'safe'); }
    if (action === 'clear') s.events = [];
    return s;
  }
  function status(s) {
    if (!s.paired) return { title: 'Every bouncer needs a plus-one.', label: 'No phone paired', detail: 'Pair your phone to try automatic away protection.', tone: 'warning' };
    if (!s.monitoring) return { title: 'Bouncer on a break.', label: 'Monitoring paused', detail: 'Automatic protection is off. Your existing lock stays as it is.', tone: 'warning' };
    if (s.proximity === 'lost') return { title: 'Lost signal. Kept the lock.', label: 'Signal unavailable', detail: 'Your session is locked. Reconnect your phone before checking back in.', tone: 'warning' };
    if (s.locked) return { title: s.proximity === 'near' ? 'You’re back. Prove it’s you.' : 'Go on. Get that coffee.', label: 'Session locked', detail: s.proximity === 'near' ? 'Your phone is nearby. Only OS authentication lets you back in.' : 'Your phone is away. Your session is locked. Your friends can cope.', tone: 'safe' };
    return { title: 'Your laptop has a bouncer.', label: 'On duty', detail: 'You’re nearby. We’ll lock your session when your phone moves away.', tone: 'safe' };
  }
  root.NiceTry = { initial, transition, status };
  if (typeof module !== 'undefined') module.exports = root.NiceTry;
})(typeof window !== 'undefined' ? window : globalThis);
