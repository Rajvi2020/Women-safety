// SheShield AI — Global JavaScript Utilities
// ─────────────────────────────────────────────

/* ══════════════════════════════════════════
   1. DARK MODE
══════════════════════════════════════════ */
const DarkMode = (() => {
  const key = 'sheshield-theme';
  const html = document.documentElement;
  const body = document.body;

  function get() { return localStorage.getItem(key) || 'light'; }
  function set(mode) {
    localStorage.setItem(key, mode);
    body.classList.toggle('dark', mode === 'dark');
    document.querySelectorAll('[data-dark-icon]').forEach(el => {
      el.textContent = mode === 'dark' ? '☀️' : '🌙';
    });
    document.querySelectorAll('[data-dark-toggle]').forEach(el => {
      el.checked = mode === 'dark';
    });
  }
  function toggle() { set(get() === 'dark' ? 'light' : 'dark'); }
  function init() {
    set(get());
    document.querySelectorAll('[data-dark-toggle-btn]').forEach(btn => {
      btn.addEventListener('click', toggle);
    });
    document.querySelectorAll('[data-dark-toggle]').forEach(inp => {
      inp.addEventListener('change', () => set(inp.checked ? 'dark' : 'light'));
    });
  }
  return { init, toggle, get, set };
})();

/* ══════════════════════════════════════════
   2. SIDEBAR
══════════════════════════════════════════ */
const Sidebar = (() => {
  let sidebar, overlay, toggleBtn;
  function open() {
    sidebar?.classList.add('open');
    overlay?.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
  function close() {
    sidebar?.classList.remove('open');
    overlay?.classList.remove('active');
    document.body.style.overflow = '';
  }
  function toggle() {
    if (sidebar?.classList.contains('open')) close(); else open();
  }
  function init() {
    sidebar   = document.getElementById('sidebar');
    overlay   = document.getElementById('sidebarOverlay');
    toggleBtn = document.getElementById('sidebarToggle');
    toggleBtn?.addEventListener('click', toggle);
    overlay?.addEventListener('click', close);
    // Active link
    const path = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(link => {
      if (link.getAttribute('href') && path.includes(link.getAttribute('href'))) {
        link.classList.add('active');
      }
    });
    // Collapse (desktop)
    document.getElementById('sidebarCollapse')?.addEventListener('click', () => {
      sidebar?.classList.toggle('collapsed');
    });
  }
  return { init, open, close, toggle };
})();

/* ══════════════════════════════════════════
   3. TOAST NOTIFICATIONS
══════════════════════════════════════════ */
const Toast = (() => {
  function show(message, type = 'info', duration = 3500) {
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<span>${message}</span>`;
    document.body.appendChild(el);
    requestAnimationFrame(() => { el.classList.add('show'); });
    setTimeout(() => {
      el.classList.remove('show');
      setTimeout(() => el.remove(), 400);
    }, duration);
  }
  return { show, success: m => show(m,'success'), error: m => show(m,'error'), info: m => show(m,'info') };
})();

/* ══════════════════════════════════════════
   4. MODALS
══════════════════════════════════════════ */
const Modal = (() => {
  function open(id) {
    const el = document.getElementById(id);
    el?.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
  function close(id) {
    const el = document.getElementById(id);
    el?.classList.remove('active');
    document.body.style.overflow = '';
    if (id === 'sosModal' && window.Siren) {
      window.Siren.stop();
    }
  }
  function init() {
    document.querySelectorAll('[data-modal-open]').forEach(btn => {
      btn.addEventListener('click', () => open(btn.dataset.modalOpen));
    });
    document.querySelectorAll('[data-modal-close]').forEach(btn => {
      btn.addEventListener('click', () => close(btn.dataset.modalClose));
    });
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
      overlay.addEventListener('click', e => {
        if (e.target === overlay) close(overlay.id);
      });
    });
  }
  return { open, close, init };
})();

/* ══════════════════════════════════════════
   5. DROPDOWNS
══════════════════════════════════════════ */
const Dropdown = (() => {
  function init() {
    document.querySelectorAll('[data-dropdown]').forEach(trigger => {
      const menu = document.getElementById(trigger.dataset.dropdown);
      if (!menu) return;
      trigger.addEventListener('click', e => {
        e.stopPropagation();
        const isOpen = menu.classList.contains('open');
        document.querySelectorAll('.dropdown-menu.open').forEach(m => m.classList.remove('open'));
        if (!isOpen) menu.classList.add('open');
      });
    });
    document.addEventListener('click', () => {
      document.querySelectorAll('.dropdown-menu.open').forEach(m => m.classList.remove('open'));
    });
  }
  return { init };
})();

/* ══════════════════════════════════════════
   6. FORM VALIDATION
══════════════════════════════════════════ */
const FormValidator = (() => {
  const rules = {
    required: v => v.trim() !== '' || 'This field is required',
    email: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Enter a valid email',
    phone: v => /^\+?[\d\s\-]{10,15}$/.test(v) || 'Enter a valid phone number',
    minLen: n => v => v.length >= n || `Minimum ${n} characters`,
    maxLen: n => v => v.length <= n || `Maximum ${n} characters`,
    password: v => /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/.test(v) || 
      'Password must be 8+ chars with uppercase, lowercase, number & symbol',
  };
  function showError(field, message) {
    field.classList.add('border-red-400');
    field.classList.remove('border-green-400');
    let errEl = field.parentElement.querySelector('.field-error');
    if (!errEl) { errEl = document.createElement('p'); errEl.className = 'field-error text-red-500 text-xs mt-1'; field.parentElement.appendChild(errEl); }
    errEl.textContent = message;
  }
  function clearError(field) {
    field.classList.remove('border-red-400');
    field.classList.add('border-green-400');
    field.parentElement.querySelector('.field-error')?.remove();
  }
  function validate(form) {
    let valid = true;
    form.querySelectorAll('[data-validate]').forEach(field => {
      const fieldRules = field.dataset.validate.split('|');
      let err = null;
      for (const rule of fieldRules) {
        const [name, ...args] = rule.split(':');
        const fn = name.includes('min') ? rules.minLen(+args[0]) :
                   name.includes('max') ? rules.maxLen(+args[0]) :
                   rules[name];
        if (!fn) continue;
        const result = fn(field.value);
        if (result !== true) { err = result; break; }
      }
      if (err) { showError(field, err); valid = false; }
      else clearError(field);
    });
    return valid;
  }
  function init() {
    document.querySelectorAll('form[data-validate-form]').forEach(form => {
      form.addEventListener('submit', e => {
        if (!validate(form)) e.preventDefault();
      });
      form.querySelectorAll('[data-validate]').forEach(field => {
        field.addEventListener('blur', () => {
          const fieldRules = field.dataset.validate.split('|');
          for (const rule of fieldRules) {
            const [name, ...args] = rule.split(':');
            const fn = name.includes('min') ? rules.minLen(+args[0]) :
                       name.includes('max') ? rules.maxLen(+args[0]) :
                       rules[name];
            if (!fn) continue;
            const result = fn(field.value);
            if (result !== true) { showError(field, result); return; }
          }
          clearError(field);
        });
      });
    });
  }
  return { init, validate };
})();

/* ══════════════════════════════════════════
   7. SEARCH
══════════════════════════════════════════ */
const Search = (() => {
  function init(inputId, itemSelector, textSelector = null) {
    const input = document.getElementById(inputId);
    if (!input) return;
    input.addEventListener('input', () => {
      const q = input.value.toLowerCase().trim();
      document.querySelectorAll(itemSelector).forEach(item => {
        const text = textSelector ? item.querySelector(textSelector)?.textContent : item.textContent;
        item.style.display = text?.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }
  return { init };
})();

/* ══════════════════════════════════════════
   8. TABS
══════════════════════════════════════════ */
const Tabs = (() => {
  function init(groupId) {
    const group = document.getElementById(groupId);
    if (!group) return;
    group.querySelectorAll('[data-tab]').forEach(tab => {
      tab.addEventListener('click', () => {
        group.querySelectorAll('[data-tab]').forEach(t => t.classList.remove('active','border-purple-600','text-purple-600'));
        group.querySelectorAll('[data-tab-content]').forEach(c => c.classList.add('hidden'));
        tab.classList.add('active','border-purple-600','text-purple-600');
        document.getElementById(tab.dataset.tab)?.classList.remove('hidden');
      });
    });
    // activate first
    group.querySelector('[data-tab]')?.click();
  }
  return { init };
})();

/* ══════════════════════════════════════════
   9. FILE UPLOAD PREVIEW
══════════════════════════════════════════ */
const FileUpload = (() => {
  function init(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    if (!input || !preview) return;
    input.addEventListener('change', () => {
      const file = input.files[0];
      if (!file) return;
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = e => { preview.src = e.target.result; preview.style.display = 'block'; };
        reader.readAsDataURL(file);
      }
    });
    // Drag & Drop
    const zone = input.closest('.upload-zone');
    if (zone) {
      zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('border-purple-500'); });
      zone.addEventListener('dragleave', () => zone.classList.remove('border-purple-500'));
      zone.addEventListener('drop', e => {
        e.preventDefault();
        zone.classList.remove('border-purple-500');
        const dt = e.dataTransfer;
        if (dt.files.length) { input.files = dt.files; input.dispatchEvent(new Event('change')); }
      });
    }
  }
  return { init };
})();

/* ══════════════════════════════════════════
   10. ANIMATE ON SCROLL
══════════════════════════════════════════ */
const AOS = (() => {
  function init() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fade-in');
          entry.target.style.opacity = '1';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    document.querySelectorAll('[data-aos]').forEach(el => {
      el.style.opacity = '0';
      observer.observe(el);
    });
  }
  return { init };
})();

/* ══════════════════════════════════════════
   11. SOS TIMER
══════════════════════════════════════════ */
const SOS = (() => {
  let timer = null;
  let countdown = 5;
  function init() {
    const btn = document.getElementById('sosBtn');
    const countdownEl = document.getElementById('sosCountdown');
    if (!btn) return;
    btn.addEventListener('mousedown', start);
    btn.addEventListener('touchstart', start, { passive: true });
    btn.addEventListener('mouseup', cancel);
    btn.addEventListener('touchend', cancel);
    btn.addEventListener('mouseleave', cancel);
    function start() {
      countdown = 5;
      if (countdownEl) countdownEl.textContent = countdown;
      timer = setInterval(() => {
        countdown--;
        if (countdownEl) countdownEl.textContent = countdown;
        if (countdown <= 0) { clearInterval(timer); trigger(); }
      }, 1000);
    }
    function cancel() { clearInterval(timer); if (countdownEl) countdownEl.textContent = ''; }
    function trigger() {
      Toast.error('🚨 SOS ACTIVATED! Fetching location...');
      if (window.Siren) {
        window.Siren.start();
      }
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          sendSosAlert(lat, lng);
        }, error => {
          console.warn('Geolocation failed or denied, sending empty coords.');
          sendSosAlert(null, null);
        });
      } else {
        sendSosAlert(null, null);
      }
    }
    function sendSosAlert(lat, lng) {
      const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
      fetch('/safety/sos/trigger/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
          lat: lat,
          lng: lng,
          location: lat && lng ? `${lat.toFixed(4)}, ${lng.toFixed(4)}` : 'Unknown Location'
        })
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'ok') {
          Toast.success('🚨 SOS saved to history!');
          const contactsListEl = document.getElementById('sosContactsList');
          const contactsSection = document.getElementById('sosContactsSection');
          if (contactsListEl && contactsSection) {
            contactsListEl.innerHTML = '';
            const contacts = data.contacts || [];
            if (contacts.length > 0) {
              contacts.forEach(contact => {
                const mapUrl = lat && lng ? `https://www.google.com/maps?q=${lat},${lng}` : 'unknown';
                const smsText = `EMERGENCY! I need help immediately. My live location: ${mapUrl}`;
                const item = document.createElement('div');
                item.className = 'flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-900/30 rounded-xl text-blue-700 dark:text-blue-300 font-semibold text-sm';
                item.innerHTML = `
                  <span>${contact.name} (${contact.phone})</span>
                  <button onclick="sendSmsViaApi('${contact.phone}', '${smsText.replace(/'/g, "\\'")}', this)" class="text-xs py-1 px-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition">Send SMS</button>
                `;
                contactsListEl.appendChild(item);
              });
              contactsSection.classList.remove('hidden');
            } else {
              contactsListEl.innerHTML = '<p class="text-xs text-gray-500">No emergency contacts configured. Please add some.</p>';
              contactsSection.classList.remove('hidden');
            }
          }
          Modal.open('sosModal');
        } else {
          Toast.error('Failed to trigger SOS alert');
        }
      })
      .catch(err => {
        console.error(err);
        Toast.error('Failed to send SOS request');
      });
    }
  }
  return { init };
})();

function sendSmsViaApi(phone, message, btnEl) {
  const originalText = btnEl.innerHTML;
  btnEl.disabled = true;
  btnEl.innerHTML = 'Sending...';
  const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
  fetch('/safety/sos/send-sms/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({ phone: phone, message: message })
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'ok') {
      Toast.success('✉️ SMS sent successfully!');
      btnEl.innerHTML = '✓ Sent';
      btnEl.disabled = true;
      btnEl.className = 'text-xs py-1 px-2.5 bg-green-600 text-white rounded-lg pointer-events-none';
    } else if (data.status === 'fallback') {
      if (data.message && !data.message.includes('not configured')) {
        Toast.error('Twilio error: ' + data.message);
      }
      
      // Auto-copy message to clipboard as safety backup for desktop SMS handlers like Phone Link
      if (navigator.clipboard) {
        navigator.clipboard.writeText(message)
          .then(() => {
            Toast.success('📋 Emergency message copied to clipboard! You can paste it (Ctrl+V).');
          })
          .catch(err => console.error('Clipboard copy failed:', err));
      }
      
      Toast.info('Opening device SMS app...');
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
      const smsUrl = `sms:${phone}${isIOS ? '&' : '?'}body=${encodeURIComponent(message)}`;
      
      const link = document.createElement('a');
      link.href = smsUrl;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      btnEl.innerHTML = '✓ Opened';
      btnEl.disabled = true;
      btnEl.className = 'text-xs py-1 px-2.5 bg-blue-600 text-white rounded-lg pointer-events-none';
    } else {
      Toast.error('Failed to send SMS: ' + data.message);
      btnEl.disabled = false;
      btnEl.innerHTML = originalText;
    }
  })
  .catch(err => {
    console.error(err);
    Toast.error('Network error sending SMS');
    btnEl.disabled = false;
    btnEl.innerHTML = originalText;
  });
}
window.sendSmsViaApi = sendSmsViaApi;

const Siren = (() => {
  let audioCtx = null;
  let osc1 = null;
  let osc2 = null;
  let gainNode = null;
  let lfo = null;
  let isPlaying = false;

  function start() {
    if (isPlaying) return;
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      audioCtx = new AudioContext();
      
      // Main oscillator: triangle wave gives a smoother, rounder wailing horn sound (ambulance)
      osc1 = audioCtx.createOscillator();
      osc1.type = 'triangle';
      
      // Supporting oscillator for harmonic fullness
      osc2 = audioCtx.createOscillator();
      osc2.type = 'sine';
      
      gainNode = audioCtx.createGain();
      
      // LFO set to 0.8Hz for a slower, smooth wail (ambulance wail)
      lfo = audioCtx.createOscillator();
      lfo.frequency.value = 0.8; 
      
      const lfoGain = audioCtx.createGain();
      lfoGain.gain.value = 250; 
      
      lfo.connect(lfoGain);
      lfoGain.connect(osc1.frequency);
      lfoGain.connect(osc2.frequency);
      
      osc1.frequency.setValueAtTime(650, audioCtx.currentTime);
      osc2.frequency.setValueAtTime(650, audioCtx.currentTime);
      
      osc1.connect(gainNode);
      osc2.connect(gainNode);
      gainNode.connect(audioCtx.destination);
      
      gainNode.gain.setValueAtTime(0.4, audioCtx.currentTime);
      
      lfo.start();
      osc1.start();
      osc2.start();
      isPlaying = true;
    } catch (e) {
      console.error('Failed to play siren:', e);
    }
  }

  function stop() {
    if (!isPlaying) return;
    try {
      if (osc1) { osc1.stop(); osc1 = null; }
      if (osc2) { osc2.stop(); osc2 = null; }
      if (lfo) { lfo.stop(); lfo = null; }
      if (audioCtx) { audioCtx.close(); audioCtx = null; }
      isPlaying = false;
    } catch (e) {
      console.error('Failed to stop siren:', e);
    }
  }

  return { start, stop };
})();
window.Siren = Siren;

/* ══════════════════════════════════════════
   12. COUNTER ANIMATION
══════════════════════════════════════════ */
function animateCounter(el, target, duration = 1500) {
  let start = 0;
  const step = timestamp => {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    el.textContent = Math.floor(progress * target);
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

/* ══════════════════════════════════════════
   13. PROGRESS BAR ANIMATION
══════════════════════════════════════════ */
function animateProgress(el, width) {
  setTimeout(() => { el.style.width = width + '%'; }, 300);
}

/* ══════════════════════════════════════════
   14. NOTIFICATION BELL
══════════════════════════════════════════ */
const Notifications = (() => {
  function init() {
    const bell = document.getElementById('notifBell');
    const panel = document.getElementById('notifPanel');
    bell?.addEventListener('click', e => {
      e.stopPropagation();
      panel?.classList.toggle('open');
    });
    document.addEventListener('click', () => panel?.classList.remove('open'));
  }
  return { init };
})();

/* ══════════════════════════════════════════
   INIT ALL
══════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  DarkMode.init();
  Sidebar.init();
  Modal.init();
  Dropdown.init();
  FormValidator.init();
  Notifications.init();
  AOS.init();
  SOS.init();
  // Animate counters
  document.querySelectorAll('[data-counter]').forEach(el => {
    animateCounter(el, parseInt(el.dataset.counter));
  });
  // Animate progress bars
  document.querySelectorAll('[data-progress]').forEach(el => {
    animateProgress(el, parseInt(el.dataset.progress));
  });
});
