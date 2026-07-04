'use strict';

(function () {
  const section = document.querySelector('[data-metro]');
  if (!section) return;

  const path = section.querySelector('[data-metro-active-path]');
  const train = section.querySelector('[data-metro-train]');
  const hint = section.querySelector('[data-metro-hint]');
  const ringsHost = section.querySelector('[data-metro-rings]');
  const buttons = Array.from(section.querySelectorAll('[data-metro-btn]'));
  const panels = Array.from(section.querySelectorAll('[data-metro-panel]'));
  const rings = Array.from(section.querySelectorAll('[data-metro-ring]'));

  if (!path || !buttons.length || !panels.length) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Each station carries data-metro-len = its length along the path in user units.
  // We normalise to [0, 1] using the path's total rendered length.
  const totalLen = path.getTotalLength();
  const stations = buttons.map((btn) => {
    const len = parseFloat(btn.dataset.metroLen || '0');
    return {
      btn,
      ring: ringsHost && ringsHost.querySelector('[data-metro-ring="' + btn.dataset.metroBtn + '"]'),
      panel: panels.find((p) => p.dataset.metroPanel === btn.dataset.metroBtn),
      len,
      progress: totalLen > 0 ? len / totalLen : 0,
    };
  });

  let currentIdx = 0;
  let tween = null;
  const state = { progress: 0 };

  function setPoint(progress) {
    section.style.setProperty('--metro-progress', progress.toFixed(4));
    const pt = path.getPointAtLength(progress * totalLen);
    train.setAttribute('cx', pt.x.toFixed(2));
    train.setAttribute('cy', pt.y.toFixed(2));
  }

  // Onboarding hint: point the little figure at the next station so the
  // user knows the dots are clickable. Hidden once the route is completed.
  function moveHint(idx) {
    if (!hint) return;
    const next = stations[idx + 1];
    if (!next) {
      hint.classList.remove('is-visible');
      return;
    }
    hint.style.left = next.btn.style.getPropertyValue('--metro-x').trim();
    hint.style.top = next.btn.style.getPropertyValue('--metro-y').trim();
    hint.classList.add('is-visible');
  }

  function updateClasses(idx) {
    stations.forEach((s, i) => {
      const active = i === idx;
      s.btn.classList.toggle('is-active', active);
      s.btn.setAttribute('aria-selected', active ? 'true' : 'false');
      s.btn.setAttribute('tabindex', active ? '0' : '-1');
      if (s.ring) s.ring.classList.toggle('is-active', active);
      if (s.panel) {
        s.panel.classList.toggle('is-active', active);
        if (active) {
          s.panel.removeAttribute('hidden');
        } else {
          s.panel.setAttribute('hidden', '');
        }
      }
    });
  }

  function select(idx, opts) {
    if (idx === currentIdx && !(opts && opts.force)) return;
    const target = stations[idx];
    if (!target) return;

    updateClasses(idx);
    currentIdx = idx;
    moveHint(idx);

    if (reduceMotion || typeof window.gsap === 'undefined') {
      state.progress = target.progress;
      setPoint(target.progress);
      return;
    }

    if (tween) tween.kill();
    tween = window.gsap.to(state, {
      progress: target.progress,
      duration: 0.85,
      ease: 'power2.inOut',
      onUpdate: () => setPoint(state.progress),
    });
  }

  // Initial paint — show station 0 at progress 0, hint at the next station.
  setPoint(0);
  moveHint(0);

  // Click selection.
  buttons.forEach((btn, idx) => {
    btn.addEventListener('click', () => select(idx));
  });

  // Keyboard: arrow keys move between stations, Home/End jump to ends.
  // Following the WAI-ARIA tabs pattern: arrow navigation moves focus AND
  // activates (since this is a single-selection scheme with no extra cost).
  section.querySelector('[role="tablist"]').addEventListener('keydown', (e) => {
    const max = buttons.length - 1;
    let next = currentIdx;
    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        next = currentIdx >= max ? 0 : currentIdx + 1;
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        next = currentIdx <= 0 ? max : currentIdx - 1;
        break;
      case 'Home':
        next = 0;
        break;
      case 'End':
        next = max;
        break;
      default:
        return;
    }
    e.preventDefault();
    select(next);
    buttons[next].focus();
  });

  // If a hash like #metro-panel-2 was used, jump straight to that station.
  if (location.hash) {
    const m = location.hash.match(/^#metro-panel-(\d+)$/);
    if (m) {
      const i = parseInt(m[1], 10);
      if (i >= 0 && i < stations.length) select(i, { force: true });
    }
  }
})();
