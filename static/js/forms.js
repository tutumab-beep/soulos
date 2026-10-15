// Form handling utilities for SoulOS

(function() {
  'use strict';

  const FormHandler = {
    // Initialize all forms on the page
    init() {
      this.initForms();
      this.initValidation();
      this.initAutosave();
    },

    // Find and enhance all forms
    initForms() {
      document.querySelectorAll('form[data-enhance]').forEach(form => {
        this.enhanceForm(form);
      });
    },

    // Add enhanced behavior to a form
    enhanceForm(form) {
      // Add submit loading state
      form.addEventListener('submit', (e) => {
        const submitBtn = form.querySelector('[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
          submitBtn.dataset.originalText = submitBtn.textContent;
          submitBtn.disabled = true;
          submitBtn.innerHTML = '<span class="spinner"></span> Saving...';
        }
      });

      // Reset button state on error
      form.addEventListener('formError', () => {
        const submitBtn = form.querySelector('[type="submit"]');
        if (submitBtn && submitBtn.dataset.originalText) {
          submitBtn.disabled = false;
          submitBtn.textContent = submitBtn.dataset.originalText;
        }
      });
    },

    // Client-side validation
    initValidation() {
      document.querySelectorAll('form[data-validate]').forEach(form => {
        form.addEventListener('submit', (e) => {
          if (!this.validateForm(form)) {
            e.preventDefault();
            form.dispatchEvent(new Event('formError'));
          }
        });

        // Real-time validation
        form.querySelectorAll('[data-validate-on="blur"]').forEach(field => {
          field.addEventListener('blur', () => this.validateField(field));
        });

        form.querySelectorAll('[data-validate-on="input"]').forEach(field => {
          field.addEventListener('input', () => this.validateField(field));
        });
      });
    },

    validateForm(form) {
      let isValid = true;
      form.querySelectorAll('[required], [aria-required="true"]').forEach(field => {
        if (!this.validateField(field)) {
          isValid = false;
        }
      });
      return isValid;
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

      // Min/max length
      if (isValid && field.hasAttribute('minlength') && field.value.length < parseInt(field.getAttribute('minlength'), 10)) {
        isValid = false;
        errorMessage = `Minimum ${field.getAttribute('minlength')} characters`;
      }

      if (isValid && field.hasAttribute('maxlength') && field.value.length > parseInt(field.getAttribute('maxlength'), 10)) {
        isValid = false;
        errorMessage = `Maximum ${field.getAttribute('maxlength')} characters`;
      }

      // Pattern validation
      if (isValid && field.hasAttribute('pattern')) {
        const pattern = new RegExp(field.getAttribute('pattern'));
        if (!pattern.test(field.value)) {
          isValid = false;
          errorMessage = field.getAttribute('data-pattern-message') || 'Invalid format';
        }
      }

      // Email validation
      if (isValid && field.type === 'email' && field.value) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(field.value)) {
          isValid = false;
          errorMessage = 'Please enter a valid email address';
        }
      }

      // Number validation
      if (isValid && (field.type === 'number' || field.type === 'range') && field.value) {
        const min = field.hasAttribute('min') ? parseFloat(field.getAttribute('min')) : null;
        const max = field.hasAttribute('max') ? parseFloat(field.getAttribute('max')) : null;
        const val = parseFloat(field.value);

        if (min !== null && val < min) {
          isValid = false;
          errorMessage = `Minimum value is ${min}`;
        }
        if (max !== null && val > max) {
          isValid = false;
          errorMessage = `Maximum value is ${max}`;
        }
      }

      // Custom validation function
      if (isValid && field.hasAttribute('data-validate-fn')) {
        const fnName = field.getAttribute('data-validate-fn');
        if (window[fnName] && typeof window[fnName] === 'function') {
          const result = window[fnName](field.value, field);
          if (result !== true) {
            isValid = false;
            errorMessage = result || 'Validation failed';
          }
        }
      }

      // Update UI
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

    // Autosave functionality
    initAutosave() {
      document.querySelectorAll('form[data-autosave]').forEach(form => {
        const key = form.dataset.autosave;
        const delay = parseInt(form.dataset.autosaveDelay || '2000', 10);
        let timeout;

        // Restore saved data
        this.restoreAutosave(form, key);

        // Save on input
        form.addEventListener('input', (e) => {
          if (e.target.type !== 'hidden') {
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
              if (field.type === 'checkbox' || field.type === 'radio') {
                field.checked = data[name];
              } else if (field.type === 'select-multiple') {
                Array.from(field.options).forEach(opt => {
                  opt.selected = data[name].includes(opt.value);
                });
              } else {
                field.value = data[name];
              }
              // Trigger input event for any listeners
              field.dispatchEvent(new Event('input', { bubbles: true }));
            }
          });
          this.showAutosaveIndicator(form, true);
        } catch (e) {
          console.warn('Failed to restore autosave:', e);
        }
      }
    },

    saveAutosave(form, key) {
      const data = {};
      const formData = new FormData(form);
      for (const [name, value] of formData.entries()) {
        const field = form.querySelector(`[name="${name}"]`);
        if (field && field.type !== 'hidden') {
          if (field.type === 'checkbox') {
            data[name] = field.checked;
          } else if (field.type === 'radio') {
            if (field.checked) data[name] = value;
          } else if (field.type === 'select-multiple') {
            data[name] = Array.from(field.selectedOptions).map(opt => opt.value);
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
        form.appendChild(indicator);
      }
      indicator.textContent = restored ? 'Restored from draft' : 'Draft saved';
      indicator.style.opacity = '1';

      setTimeout(() => {
        indicator.style.opacity = '0';
        setTimeout(() => indicator.remove(), 300);
      }, 2000);
    },

    // Get form data as object
    getFormData(form) {
      const data = {};
      const formData = new FormData(form);
      for (const [name, value] of formData.entries()) {
        if (data[name]) {
          if (!Array.isArray(data[name])) data[name] = [data[name]];
          data[name].push(value);
        } else {
          data[name] = value;
        }
      }
      return data;
    },

    // Set form data from object
    setFormData(form, data) {
      Object.keys(data).forEach(name => {
        const field = form.querySelector(`[name="${name}"]`);
        if (field) {
          const value = data[name];
          if (field.type === 'checkbox') {
            field.checked = Boolean(value);
          } else if (field.type === 'radio') {
            field.checked = field.value == value;
          } else if (field.type === 'select-multiple') {
            Array.from(field.options).forEach(opt => {
              opt.selected = Array.isArray(value) ? value.includes(opt.value) : opt.value == value;
            });
          } else {
            field.value = value;
          }
          field.dispatchEvent(new Event('input', { bubbles: true }));
        }
      });
    },

    // Reset form to initial state
    resetForm(form) {
      form.reset();
      form.querySelectorAll('[aria-invalid]').forEach(field => {
        this.setFieldValidity(field, true, '');
      });
      const key = form.dataset.autosave;
      if (key) this.clearAutosave(key);
    }
  };

  // Custom validators
  window.validatePassword = function(value) {
    if (value.length < 8) return 'Password must be at least 8 characters';
    if (!/[A-Z]/.test(value)) return 'Password must contain an uppercase letter';
    if (!/[a-z]/.test(value)) return 'Password must contain a lowercase letter';
    if (!/[0-9]/.test(value)) return 'Password must contain a number';
    return true;
  };

  window.validatePasswordMatch = function(value, field) {
    const passwordField = document.querySelector(`[name="${field.dataset.matchField}"]`);
    if (passwordField && value !== passwordField.value) {
      return 'Passwords do not match';
    }
    return true;
  };

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => FormHandler.init());
  } else {
    FormHandler.init();
  }

  // Export
  window.SoulOS = window.SoulOS || {};
  window.SoulOS.FormHandler = FormHandler;
})();