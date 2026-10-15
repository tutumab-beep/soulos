// Core JavaScript utilities for SoulOS

(function() {
  'use strict';

  // Theme management
  const ThemeManager = {
    init() {
      this.toggle = document.getElementById('theme-toggle');
      if (this.toggle) {
        this.toggle.addEventListener('click', () => this.toggleTheme());
      }
      this.applyTheme(this.getTheme());
    },

    getTheme() {
      return localStorage.getItem('theme') ||
             (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    },

    setTheme(theme) {
      localStorage.setItem('theme', theme);
      document.documentElement.setAttribute('data-theme', theme);
      this.applyTheme(theme);
    },

    toggleTheme() {
      const current = this.getTheme();
      const next = current === 'dark' ? 'light' : 'dark';
      this.setTheme(next);
    },

    applyTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      const toggle = document.getElementById('theme-toggle');
      if (toggle) {
        toggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      }
    }
  };

  // Mobile navigation
  const MobileNav = {
    init() {
      this.toggle = document.getElementById('mobile-menu-toggle');
      this.menu = document.getElementById('mobile-nav');
      this.openIcon = document.getElementById('menu-open-icon');
      this.closeIcon = document.getElementById('menu-close-icon');

      if (this.toggle && this.menu) {
        this.toggle.addEventListener('click', () => this.toggleMenu());
        this.menu.querySelectorAll('a, button').forEach(el => {
          el.addEventListener('click', () => this.closeMenu());
        });
        document.addEventListener('click', (e) => {
          if (!this.toggle.contains(e.target) && !this.menu.contains(e.target)) {
            this.closeMenu();
          }
        });
      }
    },

    toggleMenu() {
      const isOpen = this.toggle.getAttribute('aria-expanded') === 'true';
      this.setMenuState(!isOpen);
    },

    openMenu() {
      this.setMenuState(true);
    },

    closeMenu() {
      this.setMenuState(false);
    },

    setMenuState(open) {
      this.toggle.setAttribute('aria-expanded', open);
      this.menu.setAttribute('aria-hidden', !open);
      if (open) {
        this.openIcon.classList.add('hidden');
        this.closeIcon.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
      } else {
        this.openIcon.classList.remove('hidden');
        this.closeIcon.classList.add('hidden');
        document.body.style.overflow = '';
      }
    }
  };

  // User menu dropdown
  const UserMenu = {
    init() {
      this.trigger = document.getElementById('user-menu-trigger');
      this.dropdown = document.getElementById('user-dropdown');

      if (this.trigger && this.dropdown) {
        this.trigger.addEventListener('click', (e) => {
          e.stopPropagation();
          this.toggle();
        });

        document.addEventListener('click', (e) => {
          if (!this.trigger.contains(e.target) && !this.dropdown.contains(e.target)) {
            this.close();
          }
        });

        this.dropdown.addEventListener('keydown', (e) => {
          if (e.key === 'Escape') {
            this.close();
            this.trigger.focus();
          }
        });
      }
    },

    toggle() {
      const isOpen = this.trigger.getAttribute('aria-expanded') === 'true';
      this.setState(!isOpen);
    },

    open() {
      this.setState(true);
    },

    close() {
      this.setState(false);
    },

    setState(open) {
      this.trigger.setAttribute('aria-expanded', open);
      this.dropdown.setAttribute('aria-hidden', !open);
    }
  };

  // Toast notifications
  const ToastManager = {
    container: null,

    init() {
      this.container = document.getElementById('toast-container');
      if (!this.container) {
        this.container = document.createElement('div');
        this.container.id = 'toast-container';
        this.container.className = 'toast-container';
        this.container.setAttribute('aria-live', 'polite');
        this.container.setAttribute('aria-atomic', 'true');
        document.body.appendChild(this.container);
      }
      this.autoDismiss();
    },

    autoDismiss() {
      const toasts = this.container.querySelectorAll('.toast');
      toasts.forEach(toast => {
        setTimeout(() => this.dismiss(toast), 5000);
      });
    },

    show(message, type = 'info') {
      const toast = document.createElement('div');
      toast.className = `toast toast-${type}`;
      toast.setAttribute('role', 'alert');
      toast.textContent = message;
      this.container.appendChild(toast);

      setTimeout(() => this.dismiss(toast), 5000);
      return toast;
    },

    dismiss(toast) {
      if (!toast || !toast.parentNode) return;
      toast.style.animation = 'slideIn 0.3s ease-in reverse';
      setTimeout(() => toast.remove(), 300);
    }
  };

  // Form enhancements
  const FormEnhancements = {
    init() {
      this.initSliders();
      this.initCharacterCounts();
      this.initAutosave();
    },

    initSliders() {
      document.querySelectorAll('.form-slider').forEach(slider => {
        const valueDisplay = document.getElementById(slider.id + 'Value') ||
                            slider.parentElement.querySelector('.slider-value');
        if (valueDisplay) {
          valueDisplay.textContent = slider.value;
          slider.addEventListener('input', () => {
            valueDisplay.textContent = slider.value;
          });
        }
      });
    },

    initCharacterCounts() {
      document.querySelectorAll('[data-max-length]').forEach(field => {
        const maxLength = parseInt(field.dataset.maxLength, 10);
        const counter = document.createElement('div');
        counter.className = 'character-counter text-xs text-tertiary text-right mt-1';
        counter.innerHTML = `<span class="current">${field.value.length}</span> / ${maxLength}`;
        field.parentNode.insertBefore(counter, field.nextSibling);

        field.addEventListener('input', () => {
          counter.querySelector('.current').textContent = field.value.length;
          if (field.value.length > maxLength * 0.9) {
            counter.classList.add('text-warning');
          } else {
            counter.classList.remove('text-warning');
          }
          if (field.value.length >= maxLength) {
            counter.classList.add('text-danger');
            counter.classList.remove('text-warning');
          }
        });
      });
    },

    initAutosave() {
      document.querySelectorAll('form[data-autosave]').forEach(form => {
        const key = form.dataset.autosave;
        const delay = parseInt(form.dataset.autosaveDelay || '2000', 10);
        let timeout;

        // Restore saved data
        const saved = localStorage.getItem(`autosave_${key}`);
        if (saved) {
          try {
            const data = JSON.parse(saved);
            Object.keys(data).forEach(name => {
              const field = form.querySelector(`[name="${name}"]`);
              if (field && field.type !== 'hidden') {
                if (field.type === 'checkbox' || field.type === 'radio') {
                  field.checked = data[name];
                } else {
                  field.value = data[name];
                }
              }
            });
          } catch (e) {
            console.warn('Failed to restore autosave:', e);
          }
        }

        form.addEventListener('input', () => {
          clearTimeout(timeout);
          timeout = setTimeout(() => this.save(form, key), delay);
        });

        form.addEventListener('submit', () => {
          clearTimeout(timeout);
          localStorage.removeItem(`autosave_${key}`);
        });
      });
    },

    save(form, key) {
      const data = {};
      const formData = new FormData(form);
      for (const [name, value] of formData.entries()) {
        const field = form.querySelector(`[name="${name}"]`);
        if (field && field.type !== 'hidden') {
          data[name] = field.type === 'checkbox' ? field.checked : value;
        }
      }
      localStorage.setItem(`autosave_${key}`, JSON.stringify(data));
    }
  };

  // Accessibility helpers
  const A11y = {
    init() {
      this.initSkipLink();
      this.initFocusManagement();
    },

    initSkipLink() {
      const skipLink = document.querySelector('.skip-link');
      if (skipLink) {
        skipLink.addEventListener('click', (e) => {
          const target = document.querySelector(skipLink.getAttribute('href'));
          if (target) {
            e.preventDefault();
            target.focus();
            target.scrollIntoView({ behavior: 'smooth' });
          }
        });
      }
    },

    initFocusManagement() {
      // Trap focus in modals
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
          const modal = document.querySelector('.modal[aria-hidden="false"]');
          if (modal) {
            const focusable = modal.querySelectorAll(
              'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const first = focusable[0];
            const last = focusable[focusable.length - 1];

            if (e.shiftKey && document.activeElement === first) {
              e.preventDefault();
              last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
              e.preventDefault();
              first.focus();
            }
          }
        }

        if (e.key === 'Escape') {
          const modal = document.querySelector('.modal[aria-hidden="false"]');
          if (modal) {
            const closeBtn = modal.querySelector('.modal-close, [data-modal-close]');
            if (closeBtn) closeBtn.click();
          }
        }
      });
    }
  };

  // Progress stepper
  const ProgressStepper = {
    init() {
      document.querySelectorAll('.progress-stepper').forEach(stepper => {
        const steps = stepper.querySelectorAll('.progress-step');
        steps.forEach((step, index) => {
          step.addEventListener('click', () => {
            if (step.classList.contains('completed')) {
              // Allow going back to completed steps
              const journeyId = stepper.dataset.journeyId;
              const stepNumber = index + 1;
              if (journeyId) {
                window.location.href = `/journey/${journeyId}/step/${stepNumber}/`;
              }
            }
          });
        });
      });
    }
  };

  // Initialize all modules
  function init() {
    ThemeManager.init();
    MobileNav.init();
    UserMenu.init();
    ToastManager.init();
    FormEnhancements.init();
    A11y.init();
    ProgressStepper.init();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export for global access
  window.SoulOS = {
    ThemeManager,
    MobileNav,
    UserMenu,
    ToastManager,
    FormEnhancements,
    A11y,
    ProgressStepper
  };
})();