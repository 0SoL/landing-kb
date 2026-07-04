'use strict';

(function () {
  const SVG_NS = 'http://www.w3.org/2000/svg';
  const SLEEPER_GAP_PX = 28;

  const section = document.querySelector('[data-railway]');
  if (!section) return;

  const layout = section.querySelector('[data-railway-layout]');
  const rail = section.querySelector('[data-railway-rail]');
  const svg = section.querySelector('[data-railway-svg]');
  const sleepersMuted = section.querySelector('[data-sleepers-muted]');
  const sleepersActive = section.querySelector('[data-sleepers-active]');
  const train = section.querySelector('[data-railway-train]');
  const stations = Array.from(section.querySelectorAll('[data-railway-station]'));

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Cached geometry — re-measured only on resize/refresh so the per-scroll
  // update never reads layout (avoids layout thrashing).
  let railH = 0;
  let trainH = 0;

  function measure() {
    railH = rail.getBoundingClientRect().height;
    trainH = train ? train.offsetHeight : 0;
  }

  // Move the train to progress p using transform only (compositor-friendly).
  // The nose (bottom edge, minus a small visual overlap) rides the leading
  // edge of the laid track.
  function placeTrain(p) {
    if (!train) return;
    const y = p * railH - trainH * 0.9;
    train.style.transform = 'translate3d(-50%, ' + y.toFixed(1) + 'px, 0)';
  }

  // Static fallback: completed track + all stations active, train at the end.
  function renderStatic() {
    section.style.setProperty('--railway-progress', '1');
    stations.forEach((s) => s.classList.add('is-active'));
    buildSleepers(/* allLaid */ true);
    measure();
    placeTrain(1);
  }

  function buildSleepers(allLaid) {
    const h = rail.getBoundingClientRect().height;
    sleepersMuted.replaceChildren();
    sleepersActive.replaceChildren();
    if (h < 4) return [];

    const count = Math.max(2, Math.floor(h / SLEEPER_GAP_PX));
    const step = h / count;
    const activeNodes = [];

    for (let i = 0; i <= count; i += 1) {
      const y = Math.round(i * step);

      const m = document.createElementNS(SVG_NS, 'line');
      m.setAttribute('x1', '15%');
      m.setAttribute('x2', '85%');
      m.setAttribute('y1', String(y));
      m.setAttribute('y2', String(y));
      sleepersMuted.appendChild(m);

      const a = document.createElementNS(SVG_NS, 'line');
      a.setAttribute('x1', '15%');
      a.setAttribute('x2', '85%');
      a.setAttribute('y1', String(y));
      a.setAttribute('y2', String(y));
      a.dataset.y = String(y);
      if (allLaid) a.classList.add('is-laid');
      sleepersActive.appendChild(a);
      activeNodes.push({ node: a, y });
    }
    return activeNodes;
  }

  if (reduceMotion) {
    renderStatic();
    return;
  }

  // Wait for GSAP + ScrollTrigger to be available.
  function ready() {
    return typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';
  }

  function start() {
    const { gsap, ScrollTrigger } = window;
    gsap.registerPlugin(ScrollTrigger);

    let activeSleepers = buildSleepers(false);
    measure();

    const progressObj = { value: 0 };

    const applyProgress = (p) => {
      section.style.setProperty('--railway-progress', p.toFixed(4));
      placeTrain(p);
      const cutoff = railH * p;
      for (let i = 0; i < activeSleepers.length; i += 1) {
        const item = activeSleepers[i];
        const shouldLay = item.y <= cutoff;
        if (shouldLay && !item.node.classList.contains('is-laid')) {
          item.node.classList.add('is-laid');
        } else if (!shouldLay && item.node.classList.contains('is-laid')) {
          item.node.classList.remove('is-laid');
        }
      }
    };

    // The train image may finish loading after start() — re-measure its height.
    if (train && !train.complete) {
      train.addEventListener('load', () => {
        measure();
        applyProgress(progressObj.value);
      }, { once: true });
    }

    // Main scrub: drive the rail-fill progress across the section's scroll range.
    const mainST = ScrollTrigger.create({
      trigger: layout,
      start: 'top 75%',
      end: 'bottom 70%',
      scrub: 0.6,
      onUpdate: (self) => {
        progressObj.value = self.progress;
        applyProgress(self.progress);
      },
      onRefresh: () => applyProgress(progressObj.value),
    });

    // Per-station reveal triggers — fire when the marker crosses ~mid-viewport.
    const stationTriggers = stations.map((station) => {
      const marker = station.querySelector('.railway-station__marker');
      return ScrollTrigger.create({
        trigger: marker || station,
        start: 'top 70%',
        end: 'bottom 30%',
        onEnter: () => station.classList.add('is-active'),
        onEnterBack: () => station.classList.add('is-active'),
        onLeaveBack: () => station.classList.remove('is-active'),
      });
    });

    // Rebuild sleepers on resize (rail height changes with content/breakpoints).
    let rafId = 0;
    const handleResize = () => {
      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => {
        activeSleepers = buildSleepers(false);
        measure();
        applyProgress(progressObj.value);
        ScrollTrigger.refresh();
      });
    };

    window.addEventListener('resize', handleResize, { passive: true });

    // Initial paint.
    requestAnimationFrame(() => {
      ScrollTrigger.refresh();
      measure();
      applyProgress(progressObj.value);
    });
  }

  // Poll briefly for GSAP if scripts are loading asynchronously.
  if (ready()) {
    start();
  } else {
    let tries = 0;
    const interval = setInterval(() => {
      tries += 1;
      if (ready()) {
        clearInterval(interval);
        start();
      } else if (tries > 80) {
        // ~4s — fall back to static state if GSAP never arrived.
        clearInterval(interval);
        renderStatic();
      }
    }, 50);
  }
})();
