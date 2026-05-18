/* global React, MaestroIcon, MaestroSafeTop, MaestroSafeBottom, MaestroWordmark */
// MAESTRO — Main app screens: Home, Knowledge map, Node detail, Mission

const I = window.MaestroIcon;
const SafeTop = window.MaestroSafeTop;
const SafeBottom = window.MaestroSafeBottom;
const Wordmark = window.MaestroWordmark;

// extra icons
const I2 = {
  home: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M3 11l9-8 9 8"/><path d="M5 10v11h14V10"/></svg>),
  map: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M8 7l8 0M7 8l4 8M17 8l-4 8"/></svg>),
  person: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/></svg>),
  bell: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M6 8a6 6 0 0 1 12 0c0 7 3 8 3 8H3s3-1 3-8Z"/><path d="M10 21a2 2 0 0 0 4 0"/></svg>),
  fire: (p) => (<svg viewBox="0 0 24 24" fill="currentColor" {...p}><path d="M13 2c1 3-2 5-2 8a3 3 0 0 0 6 0c2 2 3 5 3 7a8 8 0 1 1-16 0c0-3 2-6 4-7 0 2 1 4 3 4 0-4-1-7 2-12z"/></svg>),
  play: (p) => (<svg viewBox="0 0 24 24" fill="currentColor" {...p}><path d="M7 4v16l13-8z"/></svg>),
  open: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M7 17L17 7M9 7h8v8"/></svg>),
  doc: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M9 13h6M9 17h6"/></svg>),
  pencil: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M16 3l5 5L8 21H3v-5z"/></svg>),
  video: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><rect x="2" y="6" width="14" height="12" rx="2"/><path d="M16 10l6-3v10l-6-3z"/></svg>),
  info: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 8v.5"/></svg>),
};

// ── SCR-ST-03 — Home dashboard ──────────────────────────────
function ScreenHome() {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)',
      display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    }}>
      <SafeTop />

      {/* header */}
      <div style={{ padding: '12px 24px 8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div className="m-mono" style={{ fontSize: 10, color: 'rgba(245,239,227,0.5)', letterSpacing: '0.16em' }}>WED · 18 MAY</div>
          <div className="m-display" style={{ fontSize: 26, color: 'var(--bone)', marginTop: 2 }}>
            Hey <span className="m-display-i">Leo</span>.
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <button style={{ position: 'relative', background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 100, width: 38, height: 38, color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
            <I2.bell style={{ width: 16, height: 16 }} />
            <span style={{ position: 'absolute', top: 6, right: 6, width: 8, height: 8, borderRadius: 100, background: 'var(--signal)' }} />
          </button>
          <div style={{ width: 38, height: 38, borderRadius: 100, background: 'var(--signal)', color: 'var(--signal-ink)', display: 'grid', placeItems: 'center', fontWeight: 700, fontSize: 14 }}>L</div>
        </div>
      </div>

      {/* streak strip */}
      <div style={{ margin: '8px 24px 0', padding: '10px 14px', background: 'var(--ink-2)', borderRadius: 'var(--r-md)', border: '1px solid var(--ink-line)', display: 'flex', alignItems: 'center', gap: 12 }}>
        <I2.fire style={{ width: 22, height: 22, color: 'var(--orange)' }} />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 13, color: 'var(--bone)', fontWeight: 600 }}>12-day streak</div>
          <div className="m-mono" style={{ fontSize: 9, letterSpacing: '0.14em', color: 'rgba(245,239,227,0.5)' }}>3 MISSIONS · 86 XP THIS WEEK</div>
        </div>
        <div style={{ display: 'flex', gap: 3 }}>
          {[1,1,1,1,1,1,0].map((d, i) => (
            <div key={i} style={{ width: 5, height: 18, borderRadius: 2, background: d ? 'var(--signal)' : 'var(--ink-3)' }} />
          ))}
        </div>
      </div>

      {/* missions section */}
      <div style={{ padding: '22px 24px 10px', display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <div className="m-eyebrow">your missions</div>
        <span style={{ fontSize: 11, color: 'rgba(245,239,227,0.5)' }}>2 open</span>
      </div>

      {/* carousel */}
      <div style={{ paddingLeft: 24, display: 'flex', gap: 12, overflowX: 'hidden' }}>
        <MissionCard
          state="lacuna" tag="OPEN GAP"
          title="SQL JOIN" sub="From PHP test · 12 May"
          cta="Start mission" big
        />
        <MissionCard
          state="recovery" tag="IN RECOVERY"
          title="PHP sessions" sub="Step 2 of 4 · keep going"
          cta="Continue"
        />
        <MissionCard
          state="consolidate" tag="REVIEW"
          title="Arrays" sub="Final quiz"
          cta="Quiz me"
        />
      </div>

      {/* mini-map preview */}
      <div style={{ padding: '20px 24px 0' }}>
        <div className="m-eyebrow" style={{ marginBottom: 10 }}>your map</div>
        <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 'var(--r-md)', padding: 14, position: 'relative' }}>
          <MiniMap />
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 10, alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: 14, fontSize: 11, color: 'rgba(245,239,227,0.7)' }}>
              <span><span className="m-dot" style={{ background: 'var(--green)' }} /> 12</span>
              <span><span className="m-dot" style={{ background: 'var(--yellow)' }} /> 4</span>
              <span><span className="m-dot" style={{ background: 'var(--orange)' }} /> 1</span>
              <span><span className="m-dot" style={{ background: 'var(--red)' }} /> 1</span>
            </div>
            <span style={{ fontSize: 12, color: 'var(--signal)', fontWeight: 600 }}>See full map →</span>
          </div>
        </div>
      </div>

      <div style={{ flex: 1 }} />

      {/* tabbar */}
      <div className="m-tabbar">
        <div className="m-tab active"><I2.home /> Home</div>
        <div className="m-tab"><I2.map /> Map</div>
        <div className="m-tab"><I2.person /> Profile</div>
      </div>
    </div>
  );
}

function MissionCard({ state, tag, title, sub, cta, big }) {
  const colors = {
    lacuna:      { bg: 'var(--bone)', fg: 'var(--ink)', pill: 'm-pill-red',    sym: '✕' },
    recovery:    { bg: 'var(--ink-2)', fg: 'var(--bone)', pill: 'm-pill-orange', sym: '↑' },
    consolidate: { bg: 'var(--ink-2)', fg: 'var(--bone)', pill: 'm-pill-yellow', sym: '◷' },
  }[state];
  return (
    <div style={{
      flex: 'none', width: big ? 260 : 200, background: colors.bg, color: colors.fg,
      borderRadius: 'var(--r-lg)', padding: 18, display: 'flex', flexDirection: 'column', gap: 10,
      border: state === 'lacuna' ? '1px solid var(--ink)' : '1px solid var(--ink-line)',
      minHeight: big ? 200 : 180,
    }}>
      <div className={'m-pill ' + colors.pill} style={{ alignSelf: 'flex-start' }}>
        <span style={{ fontSize: 10 }}>{colors.sym}</span> {tag}
      </div>
      <div className="m-display" style={{ fontSize: big ? 30 : 22, color: 'inherit', marginTop: 4 }}>{title}</div>
      <div style={{ fontSize: 12, opacity: 0.6 }}>{sub}</div>
      <div style={{ flex: 1 }} />
      <button style={{
        background: state === 'lacuna' ? 'var(--ink)' : 'var(--signal)',
        color: state === 'lacuna' ? 'var(--bone)' : 'var(--signal-ink)',
        border: 0, borderRadius: 100, padding: '10px 14px', fontSize: 13, fontWeight: 600,
        display: 'inline-flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer',
      }}>
        {cta} <I.arrow style={{ width: 14, height: 14 }} />
      </button>
    </div>
  );
}

// Mini map preview SVG
function MiniMap() {
  const nodes = [
    { x: 30,  y: 50, s: 'green' },
    { x: 80,  y: 25, s: 'green' },
    { x: 80,  y: 75, s: 'yellow' },
    { x: 140, y: 50, s: 'green' },
    { x: 200, y: 25, s: 'orange' },
    { x: 200, y: 75, s: 'red' },
    { x: 260, y: 50, s: 'gray' },
    { x: 310, y: 25, s: 'gray' },
    { x: 310, y: 75, s: 'gray' },
  ];
  const cmap = { green: 'var(--green)', yellow: 'var(--yellow)', orange: 'var(--orange)', red: 'var(--red)', gray: 'var(--gray)' };
  const edges = [[0,1],[0,2],[1,3],[2,3],[3,4],[3,5],[4,6],[5,6],[6,7],[6,8]];
  return (
    <svg viewBox="0 0 340 100" style={{ width: '100%', height: 80 }}>
      {edges.map(([a,b], i) => (
        <line key={i} x1={nodes[a].x} y1={nodes[a].y} x2={nodes[b].x} y2={nodes[b].y} stroke="rgba(245,239,227,0.18)" strokeWidth="1" />
      ))}
      {nodes.map((n, i) => (
        <g key={i}>
          <circle cx={n.x} cy={n.y} r="8" fill={cmap[n.s]} stroke="var(--ink-2)" strokeWidth="2" />
          {n.s === 'red' && <text x={n.x} y={n.y + 3} fontSize="8" textAnchor="middle" fill="#fff" fontWeight="700">✕</text>}
          {n.s === 'green' && <text x={n.x} y={n.y + 3} fontSize="8" textAnchor="middle" fill="#fff" fontWeight="700">✓</text>}
        </g>
      ))}
    </svg>
  );
}

// ── SCR-ST-04 — Knowledge map ───────────────────────────────
function ScreenMap() {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)',
      display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    }}>
      <SafeTop />
      <div style={{ padding: '8px 20px 12px', display: 'flex', alignItems: 'center', gap: 8 }}>
        <button style={{ width: 38, height: 38, borderRadius: 100, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
          <I.back style={{ width: 18, height: 18 }} />
        </button>
        <div style={{ flex: 1 }}>
          <div className="m-mono" style={{ fontSize: 9, letterSpacing: '0.16em', color: 'rgba(245,239,227,0.5)' }}>INFORMATICS · 3AI</div>
          <div className="m-display" style={{ fontSize: 22, color: 'var(--bone)' }}>Your map</div>
        </div>
        <div style={{ display: 'flex', background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 100, padding: 3, fontSize: 11 }}>
          <div style={{ padding: '5px 10px', background: 'var(--bone)', color: 'var(--ink)', borderRadius: 100, fontWeight: 600 }}>Macro</div>
          <div style={{ padding: '5px 10px', color: 'rgba(245,239,227,0.6)' }}>Micro</div>
        </div>
      </div>

      {/* big interactive map */}
      <div style={{ flex: 1, position: 'relative', background: 'radial-gradient(circle at 30% 30%, rgba(212,255,61,0.06), rgba(0,0,0,0) 50%)' }}>
        {/* subtle grid */}
        <svg width="100%" height="100%" style={{ position: 'absolute', inset: 0 }}>
          <defs>
            <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
              <path d="M24 0H0V24" fill="none" stroke="rgba(245,239,227,0.04)" strokeWidth="1" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>

        <FullMap />

        {/* zoom & legend pills */}
        <div style={{ position: 'absolute', right: 16, top: 16, display: 'flex', flexDirection: 'column', gap: 6 }}>
          <div style={{ width: 36, height: 36, borderRadius: 12, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', display: 'grid', placeItems: 'center', color: 'var(--bone)', fontSize: 18 }}>+</div>
          <div style={{ width: 36, height: 36, borderRadius: 12, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', display: 'grid', placeItems: 'center', color: 'var(--bone)', fontSize: 18 }}>−</div>
        </div>

        <div style={{ position: 'absolute', left: 12, bottom: 14, right: 12,
          background: 'rgba(28,24,19,0.92)', backdropFilter: 'blur(10px)',
          border: '1px solid var(--ink-line)', borderRadius: 'var(--r-md)', padding: '12px 14px',
        }}>
          <div className="m-eyebrow" style={{ marginBottom: 8 }}>legend</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, fontSize: 10, color: 'rgba(245,239,227,0.85)' }}>
            <LegRow color="var(--green)" sym="✓" label="Solid" />
            <LegRow color="var(--yellow)" sym="◷" label="To review" />
            <LegRow color="var(--orange)" sym="↑" label="Recovering" />
            <LegRow color="var(--red)" sym="✕" label="Gap" />
            <LegRow color="var(--white-st)" sym="○" label="Seen" />
            <LegRow color="var(--gray)" sym="·" label="New" />
          </div>
        </div>
      </div>
    </div>
  );
}

function LegRow({ color, sym, label }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      <span style={{ width: 14, height: 14, borderRadius: 100, background: color, color: 'var(--ink)', display: 'grid', placeItems: 'center', fontSize: 8, fontWeight: 700 }}>{sym}</span>
      {label}
    </div>
  );
}

function FullMap() {
  // a tree layout
  const nodes = [
    { id: 'fund', label: 'Fundamentals', x: 200, y: 80, s: 'green', big: true },
    { id: 'vars', label: 'Variables',   x: 110, y: 170, s: 'green' },
    { id: 'ctrl', label: 'Control flow', x: 200, y: 170, s: 'green' },
    { id: 'arr',  label: 'Arrays',       x: 290, y: 170, s: 'yellow' },
    { id: 'fn',   label: 'Functions',    x: 110, y: 260, s: 'green' },
    { id: 'oop',  label: 'OOP basics',   x: 200, y: 260, s: 'yellow' },
    { id: 'php',  label: 'PHP sessions', x: 290, y: 260, s: 'orange', current: true },
    { id: 'sql',  label: 'SQL JOIN',     x: 200, y: 360, s: 'red', current: true },
    { id: 'pat',  label: 'Patterns',     x: 110, y: 360, s: 'gray' },
    { id: 'mvc',  label: 'MVC',          x: 290, y: 360, s: 'gray' },
  ];
  const edges = [
    ['fund','vars'],['fund','ctrl'],['fund','arr'],
    ['vars','fn'],['ctrl','oop'],['arr','php'],
    ['fn','pat'],['oop','sql'],['php','sql'],['php','mvc'],
  ];
  const cmap = { green: '#4ADE80', yellow: '#F5C53D', orange: '#FF8A3D', red: '#E74C3C', gray: '#8A8275' };
  const symap = { green: '✓', yellow: '◷', orange: '↑', red: '✕', gray: '' };
  const nm = Object.fromEntries(nodes.map(n => [n.id, n]));
  return (
    <svg viewBox="0 0 400 440" style={{ width: '100%', height: '100%' }}>
      {edges.map(([a,b], i) => (
        <line key={i} x1={nm[a].x} y1={nm[a].y} x2={nm[b].x} y2={nm[b].y} stroke="rgba(245,239,227,0.22)" strokeWidth="1.2" />
      ))}
      {nodes.map(n => {
        const r = n.big ? 26 : 22;
        return (
          <g key={n.id}>
            {n.current && <circle cx={n.x} cy={n.y} r={r + 6} fill="none" stroke="var(--signal)" strokeWidth="2" opacity="0.6" />}
            <circle cx={n.x} cy={n.y} r={r} fill={cmap[n.s]} stroke="var(--ink)" strokeWidth="3" />
            <text x={n.x} y={n.y + 4} fontSize="13" textAnchor="middle" fill="var(--ink)" fontWeight="700">{symap[n.s]}</text>
            <text x={n.x} y={n.y + r + 16} fontSize="11" textAnchor="middle" fill="rgba(245,239,227,0.85)" style={{ fontFamily: 'Geist, sans-serif' }}>{n.label}</text>
          </g>
        );
      })}
    </svg>
  );
}

// ── SCR-ST-05 — Node detail ─────────────────────────────────
function ScreenNodeDetail() {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)',
      display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    }}>
      <SafeTop />
      <div style={{ padding: '8px 20px 0', display: 'flex', alignItems: 'center', gap: 8 }}>
        <button style={{ width: 38, height: 38, borderRadius: 100, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
          <I.back style={{ width: 18, height: 18 }} />
        </button>
        <div style={{ flex: 1, fontSize: 11, color: 'rgba(245,239,227,0.5)' }}>Map / Database / <span style={{ color: 'var(--bone)' }}>SQL JOIN</span></div>
      </div>

      {/* hero state */}
      <div style={{ padding: '14px 24px 0' }}>
        <div className="m-pill m-pill-red" style={{ marginBottom: 12 }}>
          <span>✕</span> OPEN GAP · 5 DAYS
        </div>
        <div className="m-display" style={{ fontSize: 36, color: 'var(--bone)' }}>
          SQL <span className="m-display-i">JOIN</span>
        </div>
        <div style={{ marginTop: 8, fontSize: 13, color: 'rgba(245,239,227,0.6)', maxWidth: 320 }}>
          Combining rows from two or more tables based on a related column.
        </div>
      </div>

      {/* big visual indicator */}
      <div style={{ margin: '18px 24px 0', padding: '18px', background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 'var(--r-md)', display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{
          width: 64, height: 64, borderRadius: 100, background: 'var(--red)',
          display: 'grid', placeItems: 'center', color: '#fff', fontSize: 28, fontWeight: 700,
          boxShadow: '0 0 0 6px rgba(231,76,60,0.18)',
        }}>✕</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 14, color: 'var(--bone)', fontWeight: 600 }}>Gap detected</div>
          <div style={{ fontSize: 12, color: 'rgba(245,239,227,0.6)', marginTop: 2 }}>From your PHP test on 12 May. Don't sweat it — we have a path.</div>
          <div className="m-mono" style={{ fontSize: 10, color: 'rgba(245,239,227,0.4)', marginTop: 6, letterSpacing: '0.14em' }}>UPDATED 12.05 · 14:22</div>
        </div>
      </div>

      {/* timeline */}
      <div style={{ padding: '22px 24px 0' }}>
        <div className="m-eyebrow" style={{ marginBottom: 12 }}>history</div>
        <Timeline />
      </div>

      <div style={{ flex: 1 }} />

      <div style={{ padding: '12px 24px 16px' }}>
        <button className="m-btn m-btn-primary" style={{ width: '100%' }}>
          Start mission · 4 steps <I.arrow style={{ width: 18, height: 18 }} />
        </button>
        <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'rgba(245,239,227,0.55)' }}>
          <span>· Review doc</span>
          <span>· Watch the clip (2m)</span>
          <span>· Quiz</span>
        </div>
      </div>
      <SafeBottom h={28} />
    </div>
  );
}

function Timeline() {
  const items = [
    { d: '12 MAY',  state: 'red',    title: 'Gap', from: 'PHP test — 2/10', tag: 'auto' },
    { d: '08 MAY',  state: 'yellow', title: 'To review', from: 'Quiz — 7/10', tag: 'auto' },
    { d: '02 MAY',  state: 'green',  title: 'Solid', from: 'Marked by Prof. Russo', tag: 'override' },
    { d: '20 APR',  state: 'white',  title: 'Introduced', from: 'Lesson 14', tag: 'auto' },
  ];
  const cmap = { red: 'var(--red)', yellow: 'var(--yellow)', green: 'var(--green)', white: 'var(--white-st)' };
  return (
    <div style={{ position: 'relative', paddingLeft: 18 }}>
      <div style={{ position: 'absolute', left: 6, top: 8, bottom: 8, width: 1, background: 'var(--ink-line)' }} />
      {items.map((it, i) => (
        <div key={i} style={{ position: 'relative', paddingBottom: 14 }}>
          <span style={{ position: 'absolute', left: -18, top: 4, width: 13, height: 13, borderRadius: 100, background: cmap[it.state], border: '2px solid var(--ink)' }} />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
            <div style={{ fontSize: 13, color: 'var(--bone)', fontWeight: 600 }}>{it.title}</div>
            <div className="m-mono" style={{ fontSize: 9, color: 'rgba(245,239,227,0.45)', letterSpacing: '0.14em' }}>{it.d}</div>
          </div>
          <div style={{ fontSize: 12, color: 'rgba(245,239,227,0.55)' }}>
            {it.from} {it.tag === 'override' && <span className="m-mono" style={{ fontSize: 9, letterSpacing: '0.14em', padding: '2px 6px', borderRadius: 100, background: 'var(--ink-2)', color: 'var(--signal)', marginLeft: 6 }}>OVERRIDE</span>}
          </div>
        </div>
      ))}
    </div>
  );
}

// ── SCR-ST-06 — Mission of recovery ─────────────────────────
function ScreenMission() {
  const steps = [
    { type: 'doc',   Ic: I2.doc,    title: 'Read the explainer', sub: '2 min · personalised to you', state: 'done' },
    { type: 'video', Ic: I2.video,  title: 'Watch the lesson clip', sub: '02:14 · Prof. Russo · lesson 18', state: 'current' },
    { type: 'try',   Ic: I.hand,    title: 'Try a guided exercise', sub: '3 steps · drag & drop', state: 'todo' },
    { type: 'quiz',  Ic: I2.pencil, title: 'Closing quiz', sub: '5 questions · check what stuck', state: 'todo' },
  ];
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)',
      display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    }}>
      <SafeTop />
      <div style={{ padding: '8px 20px 0', display: 'flex', alignItems: 'center', gap: 8 }}>
        <button style={{ width: 38, height: 38, borderRadius: 100, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
          <I.back style={{ width: 18, height: 18 }} />
        </button>
        <div className="m-mono" style={{ fontSize: 10, color: 'rgba(245,239,227,0.5)', letterSpacing: '0.16em' }}>MISSION · STEP 2 / 4</div>
      </div>

      <div style={{ padding: '12px 24px 0' }}>
        <div className="m-display" style={{ fontSize: 36, color: 'var(--bone)' }}>
          Mission: <span className="m-display-i">SQL JOIN</span>
        </div>
        <div style={{ marginTop: 6, fontSize: 13, color: 'rgba(245,239,227,0.55)' }}>
          A short path tuned to how you learn. Take it at your pace.
        </div>

        {/* progress */}
        <div style={{ marginTop: 16, display: 'flex', gap: 4 }}>
          {[1,1,0,0].map((d, i) => (
            <div key={i} style={{ flex: 1, height: 6, borderRadius: 100, background: d ? 'var(--signal)' : 'var(--ink-3)' }} />
          ))}
        </div>
      </div>

      <div style={{ padding: '22px 18px 0', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {steps.map((s, i) => <StepRow key={i} idx={i} step={s} />)}
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '0 24px 16px' }}>
        <button className="m-btn m-btn-primary" style={{ width: '100%' }}>
          Continue · watch clip <I.arrow style={{ width: 18, height: 18 }} />
        </button>
      </div>
      <SafeBottom h={28} />
    </div>
  );
}

function StepRow({ step, idx }) {
  const isDone = step.state === 'done';
  const isCurrent = step.state === 'current';
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 12, padding: '14px 16px',
      borderRadius: 'var(--r-md)',
      background: isCurrent ? 'var(--bone)' : 'var(--ink-2)',
      color: isCurrent ? 'var(--ink)' : 'var(--bone)',
      border: '1px solid ' + (isCurrent ? 'var(--bone)' : 'var(--ink-line)'),
      opacity: step.state === 'todo' ? 0.55 : 1,
    }}>
      <div style={{
        width: 38, height: 38, borderRadius: 12, flex: 'none',
        background: isDone ? 'var(--green)' : isCurrent ? 'var(--ink)' : 'var(--ink-3)',
        color: isDone ? 'var(--ink)' : isCurrent ? 'var(--signal)' : 'var(--bone)',
        display: 'grid', placeItems: 'center', position: 'relative',
      }}>
        {isDone ? <I.check style={{ width: 18, height: 18 }} /> : <step.Ic style={{ width: 18, height: 18 }} />}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 14, fontWeight: 600 }}>{step.title}</div>
        <div style={{ fontSize: 11, opacity: 0.6, marginTop: 1 }}>{step.sub}</div>
      </div>
      {isCurrent && <I2.play style={{ width: 18, height: 18 }} />}
      <span className="m-mono" style={{ fontSize: 9, color: 'inherit', opacity: 0.4, letterSpacing: '0.14em' }}>0{idx + 1}</span>
    </div>
  );
}

Object.assign(window, { ScreenHome, ScreenMap, ScreenNodeDetail, ScreenMission });
