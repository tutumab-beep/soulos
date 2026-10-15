// Journey-specific JavaScript for SoulOS

(function() {
  'use strict';

  const JourneyManager = {
    init() {
      this.initAutosave();
      this.initProgressStepper();
      this.initFormValidation();
      this.initKeyboardNavigation();
    },

    initAutosave() {
      const form = document.querySelector('.journey-form[data-autosave]');
      if (!form) return;

      const key = form.dataset.autosave;
      const delay = 1500;
      let timeout;

      // Restore saved data
      this.restoreAutosave(form, key);

      // Save on input
      form.addEventListener('input', (e) => {
        if (e.target.type !== 'hidden' && e.target.type !== 'submit') {
          clearTimeout(timeout);
          timeout = setTimeout(() => this.saveAutosave(form, key), delay);
        }
      });

      // Clear on submit
      form.addEventListener('submit', () => {
        clearTimeout(timeout);
        this.clearAutosave(key);
      });

      // Save before unload
      window.addEventListener('beforeunload', () => {
        this.saveAutosave(form, key);
      });
    },

    restoreAutosave(form, key) {
      const saved = localStorage.getItem(`autosave_${key}`);
      if (saved) {
        try {
          const data = JSON.parse(saved);
          Object.keys(data).forEach(name => {
            const field = form.querySelector(`[name="${name}"]`);
            if (field && field.type !== 'hidden') {
              if (field.type === 'checkbox') {
                field.checked = data[name];
              } else if (field.type === 'radio') {
                if (field.value == data[name]) field.checked = true;
              } else {
                field.value = data[name];
              }
              field.dispatchEvent(new Event('input', { bubbles: true }));
            }
          });
          this.showAutosaveIndicator(form, true);
        } catch (e) {
          console.warn('Failed to restore journey autosave:', e);
        }
      }
    },

    saveAutosave(form, key) {
      const data = {};
      const formData = new FormData(form);
      for (const [name, value] of formData.entries()) {
        const field = form.querySelector(`[name="${name}"]`);
        if (field && field.type !== 'hidden' && field.type !== 'submit') {
          if (field.type === 'checkbox') {
            data[name] = field.checked;
          } else if (field.type === 'radio') {
            if (field.checked) data[name] = value;
          } else {
            data[name] = value;
          }
        }
      }
      localStorage.setItem(`autosave_${key}`, JSON.stringify(data));
      this.showAutosaveIndicator(form);
    },

    clearAutosave(key) {
      localStorage.removeItem(`autosave_${key}`);
    },

    showAutosaveIndicator(form, restored = false) {
      let indicator = form.querySelector('.autosave-indicator');
      if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'autosave-indicator text-xs text-tertiary mt-2';
        indicator.style.textAlign = 'center';
        form.appendChild(indicator);
      }
      indicator.textContent = restored ? 'Restored from draft' : 'Draft saved';
      indicator.style.opacity = '1';

      setTimeout(() => {
        indicator.style.opacity = '0';
        setTimeout(() => indicator.remove(), 300);
      }, 2000);
    },

    initProgressStepper() {
      const stepper = document.querySelector('.progress-stepper[data-journey-id]');
      if (!stepper) return;

      const steps = stepper.querySelectorAll('.progress-step');
      const journeyId = stepper.dataset.journeyId;

      steps.forEach((step, index) => {
        step.addEventListener('click', () => {
          if (step.classList.contains('completed')) {
            const stepNumber = index + 1;
            window.location.href = `/journey/${journeyId}/step/${stepNumber}/`;
          }
        });

        // Keyboard navigation
        step.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            step.click();
          }
        });

        // Make focusable
        step.setAttribute('tabindex', '0');
        step.setAttribute('role', 'button');
        step.setAttribute('aria-label', `Go to step ${index + 1}: ${step.querySelector('.progress-step-label')?.textContent}`);
      });
    },

    initFormValidation() {
      const form = document.querySelector('.journey-form[data-validate]');
      if (!form) return;

      // Add validation attributes based on required fields
      form.querySelectorAll('[required]').forEach(field => {
        field.setAttribute('aria-required', 'true');
      });

      // Real-time validation on blur
      form.querySelectorAll('input, textarea, select').forEach(field => {
        field.addEventListener('blur', () => this.validateField(field));
      });
    },

    validateField(field) {
      const errorContainer = document.getElementById(field.id + '_error');
      let isValid = true;
      let errorMessage = '';

      // Required validation
      if (field.hasAttribute('required') || field.getAttribute('aria-required') === 'true') {
        if (field.type === 'checkbox' && !field.checked) {
          isValid = false;
          errorMessage = 'This field is required';
        } else if (field.type === 'radio') {
          const radios = document.querySelectorAll(`input[name="${field.name}"]`);
          const checked = Array.from(radios).some(r => r.checked);
          if (!checked) {
            isValid = false;
            errorMessage = 'Please select an option';
          }
        } else if (!field.value.trim()) {
          isValid = false;
          errorMessage = 'This field is required';
        }
      }

      // Custom validation for trigger field
      if (field.id === 'id_trigger' && field.value === 'other') {
        const customTrigger = document.getElementById('id_custom_trigger');
        if (customTrigger && !customTrigger.value.trim()) {
          isValid = false;
          errorMessage = 'Please specify your custom trigger';
        }
      }

      this.setFieldValidity(field, isValid, errorMessage);
      return isValid;
    },

    setFieldValidity(field, isValid, message) {
      const errorContainer = document.getElementById(field.id + '_error');

      if (isValid) {
        field.removeAttribute('aria-invalid');
        field.classList.remove('error');
        if (errorContainer) {
          errorContainer.textContent = '';
          errorContainer.hidden = true;
        }
      } else {
        field.setAttribute('aria-invalid', 'true');
        field.classList.add('error');
        if (errorContainer) {
          errorContainer.textContent = message;
          errorContainer.hidden = false;
        }
      }
    },

    initKeyboardNavigation() {
      // Allow Enter to submit from any field in the last step
      const form = document.querySelector('.journey-form');
      if (!form) return;

      const isLastStep = form.querySelector('[name="step_index"]')?.value == 4; // 0-indexed

      if (isLastStep) {
        form.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn && !e.target.closest('button')) {
              e.preventDefault();
              submitBtn.click();
            }
          }
        });
      }
    }
  };

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => JourneyManager.init());
  } else {
    JourneyManager.init();
  }

  // Export
  window.SoulOS = window.SoulOS || {};
  window.SoulOS.JourneyManager = JourneyManager;
})();