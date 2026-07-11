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
      Toast.error('🚨 SOS ACTIVATED! Emergency contacts notified!');
      Modal.open('sosModal');
    }
  }
  return { init };
})();

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
