/* ============================================
   VAWC AWARENESS FEATURE
   Floating button + educational modal
   ============================================ */

(function () {
  'use strict';

  const FAB_ID = 'awarenessFab';
  const OVERLAY_ID = 'awarenessOverlay';
  const CLOSE_ID = 'awarenessClose';

  let overlay, fab;

  // ---------- Open modal ----------
  function openModal() {
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    animateCards();
  }

  // ---------- Close modal ----------
  function closeModal() {
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  // ---------- Animate cards on open ----------
  function animateCards() {
    const cards = overlay.querySelectorAll('.right-card, .law-card, .emergency-card');
    cards.forEach(function (el) {
      el.classList.remove('animate-in');
      el.classList.add('animate-in');
    });
  }

  // ---------- Learn more toggle ----------
  function toggleLearnMore(btn) {
    const card = btn.closest('.law-card');
    const details = card.querySelector('.law-details');
    const isActive = details.classList.toggle('active');
    btn.classList.toggle('active');
    btn.innerHTML = isActive
      ? '<i class="fas fa-chevron-up"></i> Show Less'
      : '<i class="fas fa-chevron-down"></i> Learn More';
  }

  // ---------- Init ----------
  function init() {
    fab = document.getElementById(FAB_ID);
    overlay = document.getElementById(OVERLAY_ID);

    if (!fab || !overlay) return;

    var closeBtn = document.getElementById(CLOSE_ID);

    // Open
    fab.addEventListener('click', openModal);

    // Close button
    if (closeBtn) {
      closeBtn.addEventListener('click', closeModal);
    }

    // Click outside to close
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeModal();
    });

    // Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && overlay.classList.contains('active')) {
        closeModal();
      }
    });

    // Delegate learn-more clicks
    overlay.addEventListener('click', function (e) {
      var target = e.target.closest('.learn-more-btn');
      if (target) {
        e.preventDefault();
        toggleLearnMore(target);
      }
    });
  }

  // ---------- Wait for DOM ----------
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
