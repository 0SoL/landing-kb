'use strict';

// Mark document as JS-enabled (used by CSS to activate animate-on-scroll)
document.documentElement.classList.add('js');

// ============================================
// HEADER SCROLL BEHAVIOR — direction-aware
// ============================================
const header = document.querySelector('.site-header');
const isHomePage = document.body.dataset.page === 'home';

if (header) {
  if (!isHomePage) {
    header.classList.add('site-header--scrolled');
  }

  let lastScroll = 0;
  let ticking = false;

  const updateHeader = () => {
    ticking = false;
    const current = window.scrollY;

    if (isHomePage) {
      header.classList.toggle('site-header--scrolled', current > 60);
    }

    // Hide on scroll-down past 200px, reveal on scroll-up
    if (current > 200) {
      if (current > lastScroll) {
        header.classList.add('is-hidden');
      } else {
        header.classList.remove('is-hidden');
      }
    } else {
      header.classList.remove('is-hidden');
    }

    lastScroll = current;
  };

  // Coalesce scroll events into one rAF-aligned update per frame
  window.addEventListener('scroll', () => {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(updateHeader);
    }
  }, { passive: true });
}

// ============================================
// MOBILE MENU
// ============================================
const menuToggle = document.querySelector('[data-menu-toggle]');
const nav = document.querySelector('[data-nav]');

if (menuToggle && nav) {
  menuToggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('nav--open');
    menuToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  // Close the mobile menu when a navigation link is followed
  // (dropdown toggles are buttons, not links — they must keep the menu open)
  nav.querySelectorAll('.site-nav__link:not([data-dropdown-toggle]), .site-nav__sublink').forEach(link => {
    link.addEventListener('click', () => {
      nav.classList.remove('nav--open');
      menuToggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    });
  });

  document.addEventListener('click', (e) => {
    if (nav.classList.contains('nav--open') && !nav.contains(e.target) && !menuToggle.contains(e.target)) {
      nav.classList.remove('nav--open');
      menuToggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }
  });
}

// ============================================
// NAV DROPDOWN (Инвесторам)
// ============================================
document.querySelectorAll('[data-dropdown]').forEach(item => {
  const toggle = item.querySelector('[data-dropdown-toggle]');
  if (!toggle) return;

  const close = () => {
    item.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
  };

  toggle.addEventListener('click', () => {
    const isOpen = item.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  document.addEventListener('click', (e) => {
    if (item.classList.contains('is-open') && !item.contains(e.target)) close();
  });

  item.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && item.classList.contains('is-open')) {
      close();
      toggle.focus();
    }
  });
});

// ============================================
// COUNTER ANIMATION FOR STATS
// ============================================
function animateCounter(el) {
  const target = parseInt(el.dataset.counter, 10);
  if (isNaN(target)) return;

  const duration = 1800;
  const startTime = performance.now();

  const tick = (now) => {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(eased * target);
    el.textContent = current.toLocaleString('ru-KZ');
    if (progress < 1) requestAnimationFrame(tick);
  };

  requestAnimationFrame(tick);
}

const statsSection = document.querySelector('[data-stats]');

if (statsSection) {
  const counters = statsSection.querySelectorAll('[data-counter]');
  let animated = false;

  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting && !animated) {
        animated = true;
        counters.forEach(animateCounter);
        observer.disconnect();
      }
    },
    { threshold: 0.3 }
  );

  observer.observe(statsSection);
}

// ============================================
// PROJECT FILTER (no page reload)
// ============================================
const filterBtns = document.querySelectorAll('.btn-filter[data-filter]');
const projectCards = document.querySelectorAll('.project-card[data-type]');

if (filterBtns.length && projectCards.length) {
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const type = btn.dataset.filter;

      filterBtns.forEach(b => b.classList.remove('btn-filter--active'));
      btn.classList.add('btn-filter--active');

      projectCards.forEach(card => {
        const show = !type || card.dataset.type === type;
        card.style.display = show ? '' : 'none';
      });
    });
  });
}

// ============================================
// SCROLL REVEAL — .animate-in (cards, existing)
// ============================================
const revealEls = document.querySelectorAll(
  '.project-card, .news-card, .article-card, .equipment-card, ' +
  '.value-item, .timeline__item, .pillar-card'
);

if (revealEls.length && 'IntersectionObserver' in window) {
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  );

  revealEls.forEach(el => revealObserver.observe(el));
}

// ============================================
// SCROLL REVEAL — .animate-on-scroll (sections)
// ============================================
const scrollEls = document.querySelectorAll('.animate-on-scroll');

if (scrollEls.length && 'IntersectionObserver' in window) {
  const scrollObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          scrollObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15, rootMargin: '0px 0px -30px 0px' }
  );

  scrollEls.forEach(el => scrollObserver.observe(el));
}

// ============================================
// CURSOR FOLLOWER — desktop only
// ============================================
if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
  const cursorDot = document.createElement('div');
  cursorDot.className = 'cursor-dot';
  document.body.appendChild(cursorDot);

  let mouseX = 0, mouseY = 0, dotX = 0, dotY = 0;

  document.addEventListener('mousemove', e => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  (function animateCursor() {
    dotX += (mouseX - dotX) * 0.12;
    dotY += (mouseY - dotY) * 0.12;
    cursorDot.style.transform = `translate(${dotX}px, ${dotY}px)`;
    requestAnimationFrame(animateCursor);
  })();

  document.querySelectorAll('a, button').forEach(el => {
    el.addEventListener('mouseenter', () => cursorDot.classList.add('is-hovering'));
    el.addEventListener('mouseleave', () => cursorDot.classList.remove('is-hovering'));
  });
}
