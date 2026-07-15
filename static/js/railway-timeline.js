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
  const smoke = section.querySelector('[data-railway-smoke]');
  const stations = Array.from(section.querySelectorAll('[data-railway-station]'));

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Smoke spawns DOM nodes each frame the train moves — keep it to precise
  // pointers (desktop) so it never adds paint churn to mobile scrolling.
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const smokeEnabled = !reduceMotion && finePointer;

  // Cached geometry — re-measured only on resize/refresh so the per-scroll
  // update never reads layout (avoids layout thrashing).
  let railH = 0;
  let trainH = 0;

  // Live train state — the scroll mechanism owns trainY, the rock loop owns
  // rock; applyTrainTransform composes them into one compositor-only write.
  let trainY = 0;
  let rock = 0;

  function measure() {
    railH = rail.getBoundingClientRect().height;
    trainH = train ? train.offsetHeight : 0;
  }

  // Compose the current position (trainY) and rock angle into a single
  // transform. Both the scroll updates and the rock loop route through here.
  function applyTrainTransform() {
    if (!train) return;
    train.style.transform =
      'translate3d(-50%, ' + trainY.toFixed(1) + 'px, 0) rotate(' + rock.toFixed(2) + 'deg)';
  }

  // Move the train to progress p using transform only (compositor-friendly).
  // The nose (bottom edge, minus a small visual overlap) rides the leading
  // edge of the laid track. Clamped to [0, railH − 0.4·trainH] so it never
  // rises above the track top (which would overlap the heading/lead text).
  function placeTrain(p) {
    if (!train) return;
    const raw = p * railH - trainH * 0.9;
    trainY = Math.max(0, Math.min(railH - trainH * 0.4, raw));
    applyTrainTransform();
  }

  // Spawn one short-lived smoke puff at the locomotive's rear (top of the box,
  // since it travels nose-down). The puff animates and removes itself via CSS.
  function spawnSmoke() {
    // Cap concurrent puffs so a fast flick never piles up blurred layers.
    if (!smoke || smoke.childElementCount > 10) return;
    const puff = document.createElement('span');
    puff.className = 'railway__smoke-puff';
    puff.style.top = (trainY + 6).toFixed(1) + 'px';
    puff.style.setProperty('--dx', (Math.random() * 40 - 20).toFixed(1) + 'px');
    puff.style.animationDuration = (850 + Math.random() * 450).toFixed(0) + 'ms';
    puff.addEventListener('animationend', () => puff.remove(), { once: true });
    smoke.appendChild(puff);
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

    // ── Rocking engine + smoke ──
    // A gentle idle wobble whose amplitude grows with the train's scroll speed,
    // like a locomotive rolling over sleepers. Runs only while the section is
    // on screen (IntersectionObserver) so it costs nothing elsewhere on the page.
    let loopId = 0;
    let lastTrainY = 0;

    const tick = (t) => {
      loopId = requestAnimationFrame(tick);
      const now = t / 1000;
      const speed = Math.abs(trainY - lastTrainY);
      lastTrainY = trainY;
      const amp = 0.3 + Math.min(speed * 0.06, 1.2);
      rock = Math.sin(now * 5.2) * amp;
      applyTrainTransform();
      if (smokeEnabled && speed > 0.8 && Math.random() < 0.6) spawnSmoke();
    };

    const startLoop = () => {
      if (!loopId && !reduceMotion) {
        lastTrainY = trainY;
        loopId = requestAnimationFrame(tick);
      }
    };
    const stopLoop = () => {
      if (loopId) {
        cancelAnimationFrame(loopId);
        loopId = 0;
        rock = 0;
        applyTrainTransform();
      }
    };

    if ('IntersectionObserver' in window) {
      const visObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => (entry.isIntersecting ? startLoop() : stopLoop()));
      }, { threshold: 0 });
      visObserver.observe(section);
    } else {
      startLoop();
    }

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
