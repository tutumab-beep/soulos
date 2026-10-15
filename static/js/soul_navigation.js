// Soul Navigation - Enhanced mobile-first interactions
document.addEventListener('DOMContentLoaded', function() {
  // Card selection with smooth animation
  const cards = document.querySelectorAll('.sn-card');
  cards.forEach(card => {
    const input = card.querySelector('input[type="checkbox"], input[type="radio"]');
    if (input) {
      // Set initial state
      if (input.checked) {
        card.classList.add('selected');
      }
      
      input.addEventListener('change', function() {
        if (this.type === 'checkbox') {
          card.classList.toggle('selected', this.checked);
        } else if (this.type === 'radio') {
          const name = this.name;
          document.querySelectorAll(`.sn-card input[name="${name}"]`).forEach(r => {
            const parentCard = r.closest('.sn-card');
            if (parentCard) {
              parentCard.classList.toggle('selected', r.checked);
            }
          });
        }
      });
      
      card.addEventListener('click', function(e) {
        // Let the input handle it, just ensure state updates
        setTimeout(() => {
          if (input.type === 'checkbox') {
            card.classList.toggle('selected', input.checked);
          }
        }, 0);
      });
    }
  });
  
  // Enable continue button based on selection
  function updateContinueButton() {
    const forms = document.querySelectorAll('.sn-form');
    forms.forEach(form => {
      const submitBtn = form.querySelector('.sn-btn[type="submit"]');
      if (!submitBtn) return;
      
      let hasSelection = false;
      
      // Check checkboxes
      const checkboxes = form.querySelectorAll('input[type="checkbox"]:checked');
      if (checkboxes.length > 0) {
        hasSelection = true;
      }
      
      // Check radios
      const radios = form.querySelectorAll('input[type="radio"]:checked');
      if (radios.length > 0) {
        hasSelection = true;
      }
      
      // Check custom inputs
      const customInputs = form.querySelectorAll('input[name="custom_action"], textarea[name="custom_reframe"]');
      customInputs.forEach(input => {
        if (input.value.trim()) {
          // Also check if the corresponding radio is selected
          const customRadio = form.querySelector('input[value="custom"]:checked');
          if (customRadio) {
            hasSelection = true;
          }
        }
      });
      
      submitBtn.disabled = !hasSelection;
    });
  }
  
  document.addEventListener('change', updateContinueButton);
  document.addEventListener('input', updateContinueButton);
  setTimeout(updateContinueButton, 100);
  
  // Prevent double submission
  const forms = document.querySelectorAll('.sn-form');
  forms.forEach(form => {
    form.addEventListener('submit', function() {
      const submitBtn = form.querySelector('.sn-btn[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.disabled = true;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span>Loading...</span>';
      }
    });
  });
});
