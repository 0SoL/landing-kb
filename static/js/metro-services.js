'use strict';

(function () {
  const section = document.querySelector('[data-metro]');
  if (!section) return;

  const hint = section.querySelector('[data-metro-hint]');
  const tablist = section.querySelector('[role="tablist"]');
  const buttons = Array.from(section.querySelectorAll('[data-metro-btn]'));
  const panels = Array.from(section.querySelectorAll('[data-metro-panel]'));
  const edges = Array.from(section.querySelectorAll('[data-metro-edge]'));

  if (!buttons.length || !panels.length) return;

  // The line forks after «Консалтинг» into the two delivery scenarios and
  // merges again at «Проектирование», so reaching a station is a chain of
  // segments rather than a single distance along one path. BRANCH is a
  // placeholder for whichever scenario the visitor last picked.
  const ORDER = {
    consulting:  ['consulting'],
    recon:       ['consulting', 'recon'],
    constr:      ['consulting', 'constr'],
    design:      ['consulting', 'BRANCH', 'design'],
    supervision: ['consulting', 'BRANCH', 'design', 'supervision'],
    operation:   ['consulting', 'BRANCH', 'design', 'supervision', 'operation'],
  };

  // Which SVG segment joins each pair of adjacent stations.
  const EDGE = {
    'consulting>recon': 'A',
    'consulting>constr': 'B',
    'recon>design': 'C',
    'constr>design': 'D',
    'design>supervision': 'E',
    'supervision>operation': 'F',
  };

  // Station the onboarding hint points at next. From «Консалтинг» the route
  // forks, so it points at the branch currently in play.
  const NEXT = {
    recon: 'design',
    constr: 'design',
    design: 'supervision',
    supervision: 'operation',
    operation: null,
  };

  const BRANCHES = ['recon', 'constr'];
  const DEFAULT_BRANCH = 'constr';
  const STAGGER = 0.16;

  const byId = {};
  const stations = buttons.map((btn) => {
    const station = {
      id: btn.dataset.metroId,
      btn: btn,
      ring: section.querySelector('[data-metro-ring="' + btn.dataset.metroBtn + '"]'),
      panel: panels.find((p) => p.dataset.metroPanel === btn.dataset.metroBtn),
    };
    byId[station.id] = station;
    return station;
  });

  let currentIdx = 0;
  let branch = DEFAULT_BRANCH;

  function chainFor(id) {
    return (ORDER[id] || ORDER.consulting).map((n) => (n === 'BRANCH' ? branch : n));
  }

  function moveHint(id) {
    if (!hint) return;
    const nextId = id === 'consulting' ? branch : NEXT[id];
    const next = nextId ? byId[nextId] : null;
    if (!next) {
      hint.classList.remove('is-visible');
      return;
    }
    hint.style.left = next.btn.style.getPropertyValue('--metro-x').trim();
    hint.style.top = next.btn.style.getPropertyValue('--metro-y').trim();
    hint.classList.add('is-visible');
  }

  function render(idx) {
    const active = stations[idx];
    const chain = chainFor(active.id);
    const visited = new Set(chain);

    // Segments light up in chain order, each one delayed behind the last so
    // the route reads as travelling outward from the start.
    const lit = {};
    for (let i = 0; i < chain.length - 1; i++) {
      const key = EDGE[chain[i] + '>' + chain[i + 1]];
      if (key) lit[key] = i;
    }

    edges.forEach((edge) => {
      const step = lit[edge.dataset.metroEdge];
      const on = step !== undefined;
      edge.classList.toggle('is-on', on);
      edge.style.setProperty('--metro-delay', on ? (step * STAGGER).toFixed(2) + 's' : '0s');
    });

    stations.forEach((s) => {
      const isActive = s === active;
      const isOn = visited.has(s.id);
      s.btn.classList.toggle('is-active', isActive);
      s.btn.classList.toggle('is-on', isOn);
      s.btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
      s.btn.setAttribute('tabindex', isActive ? '0' : '-1');
      if (s.ring) {
        s.ring.classList.toggle('is-active', isActive);
        s.ring.classList.toggle('is-on', isOn);
      }
      if (s.panel) {
        s.panel.classList.toggle('is-active', isActive);
        if (isActive) {
          s.panel.removeAttribute('hidden');
        } else {
          s.panel.setAttribute('hidden', '');
        }
      }
    });

    moveHint(active.id);
  }

  function select(idx, opts) {
    const target = stations[idx];
    if (!target) return;

    // Picking either fork station also sets the scenario that the merged part
    // of the route is drawn through.
    const switched = BRANCHES.indexOf(target.id) !== -1 && target.id !== branch;
    if (switched) branch = target.id;

    if (idx === currentIdx && !switched && !(opts && opts.force)) return;
    currentIdx = idx;
    render(idx);
  }

  render(0);

  buttons.forEach((btn, idx) => {
    btn.addEventListener('click', () => select(idx));
  });

  // Keyboard: arrow keys move between stations, Home/End jump to ends.
  // Following the WAI-ARIA tabs pattern: arrow navigation moves focus AND
  // activates (since this is a single-selection scheme with no extra cost).
  if (tablist) {
    tablist.addEventListener('keydown', (e) => {
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
  }

  // If a hash like #metro-panel-2 was used, jump straight to that station.
  if (location.hash) {
    const m = location.hash.match(/^#metro-panel-(\d+)$/);
    if (m) {
      const i = parseInt(m[1], 10);
      if (i >= 0 && i < stations.length) select(i, { force: true });
    }
  }
})();
