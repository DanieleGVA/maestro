/* global React */
// MAESTRO — Desktop screens (1280×820, sidebar + topbar shell)

const DI = {
  arrow: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M5 12h14M13 5l7 7-7 7"/></svg>),
  back: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M19 12H5M12 19l-7-7 7-7"/></svg>),
  check: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M4 12l5 5L20 6"/></svg>),
  x: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M5 5l14 14M19 5L5 19"/></svg>),
  home: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M3 11l9-8 9 8"/><path d="M5 10v11h14V10"/></svg>),
  map: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M8 7l8 0M7 8l4 8M17 8l-4 8"/></svg>),
  person: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/></svg>),
  rocket: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M14 4s5 1 5 6-6 10-6 10-5-1-5-6 6-10 6-10z"/><circle cx="14" cy="9" r="2"/><path d="M9 15l-4 4M5 14l-2 6 6-2"/></svg>),
  doc: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4"/></svg>),
  bell: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M6 8a6 6 0 0 1 12 0c0 7 3 8 3 8H3s3-1 3-8Z"/><path d="M10 21a2 2 0 0 0 4 0"/></svg>),
  search: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>),
  fire: (p) => (<svg viewBox="0 0 24 24" fill="currentColor" {...p}><path d="M13 2c1 3-2 5-2 8a3 3 0 0 0 6 0c2 2 3 5 3 7a8 8 0 1 1-16 0c0-3 2-6 4-7 0 2 1 4 3 4 0-4-1-7 2-12z"/></svg>),
  eye: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>),
  spark: (p) => (<svg viewBox="0 0 24 24" fill="currentColor" {...p}><path d="M12 2l1.6 6.4L20 10l-6.4 1.6L12 18l-1.6-6.4L4 10l6.4-1.6L12 2z"/></svg>),
  play: (p) => (<svg viewBox="0 0 24 24" fill="currentColor" {...p}><path d="M7 4v16l13-8z"/></svg>),
  pencil: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M16 3l5 5L8 21H3v-5z"/></svg>),
  video: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><rect x="2" y="6" width="14" height="12" rx="2"/><path d="M16 10l6-3v10l-6-3z"/></svg>),
  hand: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M9 11V5a2 2 0 1 1 4 0v6"/><path d="M13 11V4a2 2 0 1 1 4 0v9"/><path d="M17 11V6a2 2 0 1 1 4 0v9a6 6 0 0 1-6 6h-2a6 6 0 0 1-6-6v-2l-2-3a2 2 0 0 1 3-3l2 2"/></svg>),
  sound: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M11 5L6 9H3v6h3l5 4V5z"/><path d="M15 8.5a4 4 0 0 1 0 7"/></svg>),
};

// ── DesktopShell — sidebar + topbar ─────────────────────────
function DesktopShell({ children, active = 'home', subtitle, title, light, hideTopBreadcrumb }) {
  const items = [
    { id: 'home', label: 'Home', Ic: DI.home },
    { id: 'map', label: 'Map', Ic: DI.map },
    { id: 'missions', label: 'Missions', Ic: DI.rocket },
    { id: 'library', label: 'Library', Ic: DI.doc },
    { id: 'profile', label: 'Profile', Ic: DI.person },
  ];
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%',
      background: light ? 'var(--paper)' : 'var(--ink)',
      color: light ? 'var(--ink)' : 'var(--bone)',
      display: 'grid', gridTemplateColumns: '220px 1fr',
      overflow: 'hidden', position: 'relative',
    }}>
      {/* sidebar */}
      <aside style={{
        background: light ? '#FFFEF8' : 'var(--ink-2)',
        borderRight: '1px solid ' + (light ? 'rgba(20,17,13,0.08)' : 'var(--ink-line)'),
        padding: '24px 16px', display: 'flex', flexDirection: 'column', gap: 6,
      }}>
        <div style={{ padding: '4px 8px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div className="m-display" style={{ fontSize: 24, color: light ? 'var(--ink)' : 'var(--bone)' }}>
            Maestro<span style={{ color: 'var(--signal)' }}>.</span>
          </div>
        </div>
        <div className="m-mono" style={{ fontSize: 9, letterSpacing: '0.18em', opacity: 0.45, padding: '12px 10px 6px' }}>NAVIGATE</div>
        {items.map(it => {
          const isActive = it.id === active;
          return (
            <div key={it.id} style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '10px 12px', borderRadius: 12,
              background: isActive ? (light ? 'var(--ink)' : 'var(--signal)') : 'transparent',
              color: isActive ? (light ? 'var(--bone)' : 'var(--signal-ink)') : (light ? 'var(--ink)' : 'rgba(245,239,227,0.75)'),
              fontWeight: isActive ? 600 : 500, fontSize: 14,
            }}>
              <it.Ic style={{ width: 18, height: 18 }} /> {it.label}
              {isActive && <span style={{ marginLeft: 'auto', fontSize: 10 }}>●</span>}
            </div>
          );
        })}

        <div style={{ flex: 1 }} />

        {/* mini streak in sidebar */}
        <div style={{
          padding: 12, borderRadius: 14,
          background: light ? 'rgba(20,17,13,0.04)' : 'var(--ink-3)',
          border: '1px solid ' + (light ? 'rgba(20,17,13,0.05)' : 'var(--ink-line)'),
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, fontWeight: 600 }}>
            <DI.fire style={{ width: 14, height: 14, color: 'var(--orange)' }} /> 12-day streak
          </div>
          <div style={{ display: 'flex', gap: 3, marginTop: 8 }}>
            {[1,1,1,1,1,1,0].map((d, i) => (
              <div key={i} style={{ flex: 1, height: 14, borderRadius: 2, background: d ? 'var(--signal)' : (light ? 'rgba(20,17,13,0.12)' : 'var(--ink-3)') }} />
            ))}
          </div>
        </div>

        {/* user row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 6px', marginTop: 8 }}>
          <div style={{ width: 32, height: 32, borderRadius: 10, background: 'var(--signal)', color: 'var(--signal-ink)', display: 'grid', placeItems: 'center', fontFamily: 'var(--display)', fontSize: 18 }}>L</div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600 }}>Leo Romano</div>
            <div className="m-mono" style={{ fontSize: 9, letterSpacing: '0.14em', opacity: 0.55 }}>3AI · INFORMATICS</div>
          </div>
        </div>
      </aside>

      {/* main */}
      <main style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* topbar */}
        <header style={{
          height: 68, padding: '0 32px', flex: 'none',
          display: 'flex', alignItems: 'center', gap: 16,
          borderBottom: '1px solid ' + (light ? 'rgba(20,17,13,0.08)' : 'var(--ink-line)'),
        }}>
          {!hideTopBreadcrumb && (
            <div className="m-mono" style={{ fontSize: 10, letterSpacing: '0.16em', opacity: 0.55 }}>
              {subtitle || 'MAESTRO · STUDENT'}
            </div>
          )}
          {title && (
            <div className="m-display" style={{ fontSize: 22 }}>{title}</div>
          )}
          <div style={{ flex: 1 }} />
          {/* search */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '8px 14px', borderRadius: 100,
            background: light ? 'rgba(20,17,13,0.04)' : 'var(--ink-2)',
            border: '1px solid ' + (light ? 'rgba(20,17,13,0.06)' : 'var(--ink-line)'),
            minWidth: 280,
          }}>
            <DI.search style={{ width: 14, height: 14, opacity: 0.5 }} />
            <span style={{ flex: 1, fontSize: 13, opacity: 0.5 }}>Search a concept, mission…</span>
            <span className="m-mono" style={{ fontSize: 10, opacity: 0.4, padding: '2px 6px', borderRadius: 4, border: '1px solid currentColor' }}>⌘K</span>
          </div>
          <button style={{
            width: 38, height: 38, borderRadius: 100,
            background: light ? '#fff' : 'var(--ink-2)',
            border: '1px solid ' + (light ? 'rgba(20,17,13,0.08)' : 'var(--ink-line)'),
            display: 'grid', placeItems: 'center', position: 'relative', color: 'inherit',
          }}>
            <DI.bell style={{ width: 16, height: 16 }} />
            <span style={{ position: 'absolute', top: 8, right: 8, width: 7, height: 7, borderRadius: 100, background: 'var(--signal)' }} />
          </button>
        </header>

        <div style={{ flex: 1, overflow: 'auto', minHeight: 0 }}>
          {children}
        </div>
      </main>
    </div>
  );
}

// ── helpers ─────────────────────────────────────────────────
function DEyebrow({ children, color }) {
  return <div className="m-mono" style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', opacity: color ? 1 : 0.55, color: color || 'inherit' }}>{children}</div>;
}
function DPill({ children, tone }) {
  return <span className={'m-pill m-pill-' + tone}>{children}</span>;
}

// ── DSK-ST-01 — Login ───────────────────────────────────────
function DLogin() {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)', display: 'grid',
      gridTemplateColumns: '1.1fr 1fr', overflow: 'hidden', position: 'relative',
    }}>
      {/* left: hero */}
      <div style={{ padding: '64px 64px 48px', display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden' }}>
        <div style={{
          position: 'absolute', top: -200, left: -120, width: 520, height: 520, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(212,255,61,0.28), rgba(212,255,61,0) 60%)',
        }} />
        <div className="m-display" style={{ fontSize: 32, color: 'var(--bone)', position: 'relative' }}>
          Maestro<span style={{ color: 'var(--signal)' }}>.</span>
        </div>
        <div style={{ flex: 1 }} />
        <div style={{ position: 'relative' }}>
          <DEyebrow color="var(--signal)">welcome back</DEyebrow>
          <div className="m-display" style={{ fontSize: 96, color: 'var(--bone)', marginTop: 18, lineHeight: 0.92 }}>
            Pick up<br/><span className="m-display-i">where</span> you<br/>left off.
          </div>
          <div style={{ marginTop: 28, fontSize: 16, color: 'rgba(245,239,227,0.6)', maxWidth: 460, lineHeight: 1.5 }}>
            Your missions, your map, your pace. Maestro tunes each session to how <em>you</em> learn.
          </div>
        </div>
        <div style={{ marginTop: 'auto', display: 'flex', gap: 18, color: 'rgba(245,239,227,0.4)', fontSize: 12, position: 'relative' }}>
          <span className="m-mono" style={{ letterSpacing: '0.14em' }}>v 1.0</span>
          <span>·</span>
          <span>Pixie — your AI study buddy</span>
        </div>
      </div>

      {/* right: form */}
      <div style={{
        margin: 32, borderRadius: 32, background: 'var(--ink-2)',
        border: '1px solid var(--ink-line)', padding: '56px 56px',
        display: 'flex', flexDirection: 'column', justifyContent: 'center',
      }}>
        <DEyebrow>log in</DEyebrow>
        <div className="m-display" style={{ fontSize: 40, marginTop: 8 }}>Sign in</div>
        <div style={{ marginTop: 6, fontSize: 14, color: 'rgba(245,239,227,0.55)' }}>Use your school credentials or SSO.</div>

        <div style={{ marginTop: 32, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <DField label="USERNAME" value="leo.romano" />
          <DField label="PASSWORD" value="••••••••••" trailing={<DI.eye style={{ width: 18, height: 18, color: 'rgba(245,239,227,0.55)' }} />} />
        </div>

        <button className="m-btn m-btn-primary" style={{ width: '100%', marginTop: 18 }}>
          Log in <DI.arrow style={{ width: 18, height: 18 }} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '20px 0' }}>
          <div style={{ flex: 1, height: 1, background: 'var(--ink-line)' }} />
          <span className="m-mono" style={{ fontSize: 9, letterSpacing: '0.18em', opacity: 0.5 }}>OR</span>
          <div style={{ flex: 1, height: 1, background: 'var(--ink-line)' }} />
        </div>

        <button className="m-btn m-btn-ghost" style={{ width: '100%' }}>
          Continue with school SSO
        </button>

        <div style={{ marginTop: 28, fontSize: 12, color: 'rgba(245,239,227,0.45)', textAlign: 'center' }}>
          Forgot password? <span style={{ color: 'var(--bone)', borderBottom: '1px solid var(--ink-line)' }}>Ask your school IT</span>
        </div>
      </div>
    </div>
  );
}
function DField({ label, value, trailing }) {
  return (
    <div style={{ background: 'var(--ink-3)', border: '1px solid var(--ink-line)', borderRadius: 16, padding: '14px 18px' }}>
      <div className="m-mono" style={{ fontSize: 9, letterSpacing: '0.18em', color: 'rgba(245,239,227,0.5)' }}>{label}</div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 6 }}>
        <div style={{ flex: 1, fontSize: 16 }}>{value}</div>{trailing}
      </div>
    </div>
  );
}

// ── DSK-ST-02a — Onboarding welcome ─────────────────────────
function DOnbWelcome() {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--signal)', color: 'var(--signal-ink)',
      display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative',
    }}>
      <div style={{ padding: '28px 48px', display: 'flex', alignItems: 'center' }}>
        <div className="m-display" style={{ fontSize: 24 }}>Maestro<span style={{ opacity: 0.4 }}>.</span></div>
        <div style={{ flex: 1 }} />
        <div className="m-mono" style={{ fontSize: 10, letterSpacing: '0.18em', opacity: 0.6 }}>STEP 1 / 5</div>
        <div style={{ marginLeft: 16, display: 'flex', gap: 4, width: 220 }}>
          {[1,2,3,4,5].map(i => (
            <div key={i} style={{ flex: 1, height: 4, borderRadius: 100, background: i === 1 ? 'var(--signal-ink)' : 'rgba(11,19,0,0.18)' }} />
          ))}
        </div>
        <button style={{ marginLeft: 24, background: 'transparent', border: 0, color: 'var(--signal-ink)', fontWeight: 600, opacity: 0.6, fontSize: 13 }}>Skip ›</button>
      </div>

      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1.2fr 1fr', padding: '0 48px 48px', gap: 48, alignItems: 'center' }}>
        <div>
          <DEyebrow>welcome, leo</DEyebrow>
          <div className="m-display" style={{ fontSize: 124, marginTop: 12, lineHeight: 0.92 }}>
            Let's find<br/><span className="m-display-i">how you</span><br/>learn best.
          </div>
          <div style={{ marginTop: 28, fontSize: 18, lineHeight: 1.45, opacity: 0.78, maxWidth: 540 }}>
            Not a graded test. Just a 5-minute vibe check so we can tune Maestro to <span style={{ fontFamily: 'var(--display)', fontStyle: 'italic' }}>your</span> brain. We'll show you the same idea four different ways and see what clicks.
          </div>

          <div style={{ marginTop: 36, display: 'flex', gap: 10 }}>
            {['Read','Listen','Watch','Try'].map((t, i) => (
              <div key={t} style={{
                padding: '10px 18px', border: '1.5px solid var(--signal-ink)', borderRadius: 100,
                fontSize: 14, fontWeight: 600,
                background: i === 3 ? 'var(--signal-ink)' : 'transparent',
                color: i === 3 ? 'var(--signal)' : 'var(--signal-ink)',
              }}>{t}</div>
            ))}
          </div>

          <button className="m-btn" style={{ marginTop: 36, background: 'var(--signal-ink)', color: 'var(--signal)', fontSize: 16, padding: '18px 30px' }}>
            Let's go <DI.arrow style={{ width: 20, height: 20 }} />
          </button>
        </div>

        {/* right: graphic */}
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <svg width="380" height="380" viewBox="0 0 380 380">
            <defs>
              <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
                <circle cx="2" cy="2" r="1.5" fill="rgba(11,19,0,0.25)" />
              </pattern>
            </defs>
            <circle cx="190" cy="190" r="160" fill="url(#dots)" />
            <circle cx="190" cy="190" r="100" fill="var(--signal-ink)" />
            <text x="190" y="200" fontFamily="Instrument Serif" fontSize="80" fontStyle="italic" fill="var(--signal)" textAnchor="middle">you.</text>
          </svg>
        </div>
      </div>
    </div>
  );
}

// ── DSK-ST-02b — Onboarding modality quiz ───────────────────
function DOnbQuiz() {
  const cards = [
    { l: 'Read', Ic: DI.doc, blurb: 'A short explainer text', state: 'open' },
    { l: 'Listen', Ic: DI.sound, blurb: '45-second audio clip', state: 'idle' },
    { l: 'Watch', Ic: DI.eye, blurb: 'Diagram you can pan', state: 'idle' },
    { l: 'Try', Ic: DI.hand, blurb: 'Tiny interactive task', state: 'done' },
  ];
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)', display: 'flex', flexDirection: 'column', overflow: 'hidden',
    }}>
      <div style={{ padding: '28px 48px', display: 'flex', alignItems: 'center' }}>
        <div className="m-display" style={{ fontSize: 22, color: 'var(--bone)' }}>Maestro<span style={{ color: 'var(--signal)' }}>.</span></div>
        <div style={{ flex: 1 }} />
        <div className="m-mono" style={{ fontSize: 10, letterSpacing: '0.18em', color: 'rgba(245,239,227,0.55)' }}>STEP 3 / 5</div>
        <div style={{ marginLeft: 16, display: 'flex', gap: 4, width: 220 }}>
          {[1,2,3,4,5].map(i => (
            <div key={i} style={{ flex: 1, height: 4, borderRadius: 100, background: i <= 3 ? 'var(--signal)' : 'rgba(245,239,227,0.15)' }} />
          ))}
        </div>
        <button style={{ marginLeft: 24, background: 'transparent', border: 0, color: 'rgba(245,239,227,0.55)', fontWeight: 600, fontSize: 13 }}>Skip ›</button>
      </div>

      <div style={{ flex: 1, padding: '12px 80px 48px', display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: 64, alignItems: 'center' }}>
        <div>
          <DEyebrow color="var(--signal)">concept 3 / 4</DEyebrow>
          <div className="m-display" style={{ fontSize: 76, color: 'var(--bone)', marginTop: 14 }}>
            What's a <span className="m-display-i">variable</span>?
          </div>
          <div style={{ marginTop: 18, fontSize: 16, color: 'rgba(245,239,227,0.65)', maxWidth: 380 }}>
            Pick the way you'd rather learn it. There's no wrong answer — Maestro is just watching what clicks.
          </div>
          <div style={{ marginTop: 28, display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: 'rgba(245,239,227,0.55)' }}>
            <DI.spark style={{ width: 14, height: 14, color: 'var(--signal)' }} />
            You spent <span style={{ color: 'var(--bone)' }}>42s</span> reading. Try one more.
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18 }}>
          {cards.map(c => {
            const active = c.state === 'open';
            const done = c.state === 'done';
            return (
              <div key={c.l} style={{
                background: active ? 'var(--bone)' : 'var(--ink-2)',
                color: active ? 'var(--ink)' : 'var(--bone)',
                border: '1px solid ' + (active ? 'var(--bone)' : 'var(--ink-line)'),
                borderRadius: 24, padding: 28, minHeight: 220, position: 'relative',
                display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
              }}>
                <c.Ic style={{ width: 28, height: 28 }} />
                <div>
                  <div className="m-display" style={{ fontSize: 36 }}>{c.l}</div>
                  <div style={{ marginTop: 4, fontSize: 13, opacity: 0.65 }}>{c.blurb}</div>
                </div>
                {done && <div style={{ position: 'absolute', top: 18, right: 18, width: 24, height: 24, borderRadius: 100, background: 'var(--green)', color: 'var(--ink)', display: 'grid', placeItems: 'center' }}><DI.check style={{ width: 14, height: 14 }} /></div>}
                {active && <div style={{ position: 'absolute', top: 18, right: 18, fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.18em', padding: '4px 9px', borderRadius: 100, background: 'var(--ink)', color: 'var(--signal)' }}>OPEN</div>}
              </div>
            );
          })}
        </div>
      </div>

      <div style={{ padding: '0 80px 36px', display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
        <button className="m-btn m-btn-ghost" style={{ color: 'var(--bone)' }}>Back</button>
        <button className="m-btn m-btn-primary">Next concept <DI.arrow style={{ width: 18, height: 18 }} /></button>
      </div>
    </div>
  );
}

// ── DSK-ST-02c — Result ─────────────────────────────────────
function DOnbResult() {
  const axes = [
    { label: 'VISUAL',     v: 0.85 },
    { label: 'AUDITORY',   v: 0.55 },
    { label: 'HANDS-ON',   v: 0.78 },
    { label: 'REFLECTIVE', v: 0.40 },
    { label: 'SOCIAL',     v: 0.62 },
  ];
  const cx = 220, cy = 220, R = 160;
  const pts = axes.map((a, i) => {
    const an = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
    return [cx + Math.cos(an) * R * a.v, cy + Math.sin(an) * R * a.v];
  });
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)', display: 'flex', flexDirection: 'column', overflow: 'hidden',
    }}>
      <div style={{ padding: '28px 48px', display: 'flex', alignItems: 'center' }}>
        <div className="m-display" style={{ fontSize: 22, color: 'var(--bone)' }}>Maestro<span style={{ color: 'var(--signal)' }}>.</span></div>
        <div style={{ flex: 1 }} />
        <div className="m-mono" style={{ fontSize: 10, letterSpacing: '0.18em', color: 'rgba(245,239,227,0.55)' }}>STEP 5 / 5 · DONE</div>
      </div>

      <div style={{ flex: 1, padding: '12px 80px 48px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 64, alignItems: 'center' }}>
        <div>
          <DEyebrow color="var(--signal)">your shape</DEyebrow>
          <div className="m-display" style={{ fontSize: 84, color: 'var(--bone)', marginTop: 12, lineHeight: 0.95 }}>
            You're a<br/><span className="m-display-i">visual,</span><br/>hands-on type.
          </div>
          <div style={{ marginTop: 24, fontSize: 16, color: 'rgba(245,239,227,0.65)', maxWidth: 480, lineHeight: 1.5 }}>
            Maestro will lean into diagrams, short experiments and concrete examples. We'll skip long lectures unless you ask.
          </div>

          <div style={{ marginTop: 30 }}>
            <DEyebrow>tune the tone</DEyebrow>
            <div style={{ display: 'flex', gap: 10, marginTop: 10 }}>
              {['Casual','Calm','Formal'].map((t, i) => (
                <div key={t} style={{ padding: '10px 18px', borderRadius: 100, border: '1px solid ' + (i === 0 ? 'var(--signal)' : 'var(--ink-line)'), background: i === 0 ? 'var(--signal)' : 'transparent', color: i === 0 ? 'var(--signal-ink)' : 'var(--bone)', fontSize: 13, fontWeight: 600 }}>{t}</div>
              ))}
            </div>
            <div style={{ display: 'flex', gap: 10, marginTop: 10 }}>
              {['Short','Deep dive'].map((t, i) => (
                <div key={t} style={{ padding: '10px 18px', borderRadius: 100, border: '1px solid ' + (i === 0 ? 'var(--signal)' : 'var(--ink-line)'), background: i === 0 ? 'var(--signal)' : 'transparent', color: i === 0 ? 'var(--signal-ink)' : 'var(--bone)', fontSize: 13, fontWeight: 600 }}>{t}</div>
              ))}
            </div>
          </div>

          <div style={{ marginTop: 36, display: 'flex', gap: 12 }}>
            <button className="m-btn m-btn-primary">Looks like me <DI.check style={{ width: 18, height: 18 }} /></button>
            <button className="m-btn m-btn-ghost" style={{ color: 'var(--bone)' }}>Tweak it manually</button>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <svg width="440" height="440" viewBox="0 0 440 440">
            {[0.25, 0.5, 0.75, 1].map(s => (
              <polygon key={s} points={axes.map((_, i) => {
                const an = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
                return [cx + Math.cos(an) * R * s, cy + Math.sin(an) * R * s].join(',');
              }).join(' ')} fill="none" stroke="rgba(245,239,227,0.08)" />
            ))}
            {axes.map((_, i) => {
              const an = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
              return <line key={i} x1={cx} y1={cy} x2={cx + Math.cos(an)*R} y2={cy + Math.sin(an)*R} stroke="rgba(245,239,227,0.08)" />;
            })}
            <polygon points={pts.map(p => p.join(',')).join(' ')} fill="rgba(212,255,61,0.18)" stroke="var(--signal)" strokeWidth="2.5" />
            {pts.map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r="5" fill="var(--signal)" />)}
            {axes.map((a, i) => {
              const an = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
              return <text key={i} x={cx + Math.cos(an) * (R + 24)} y={cy + Math.sin(an) * (R + 24)} fontFamily="JetBrains Mono" fontSize="11" letterSpacing="0.14em" fill="rgba(245,239,227,0.7)" textAnchor="middle" dominantBaseline="middle">{a.label}</text>;
            })}
          </svg>
        </div>
      </div>
    </div>
  );
}

// ── DSK-ST-03 — Home ────────────────────────────────────────
function DHome() {
  return (
    <DesktopShell active="home" subtitle="WED · 18 MAY 2026">
      <div style={{ padding: '32px 32px 48px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: 28 }}>
          <div>
            <DEyebrow>good afternoon</DEyebrow>
            <div className="m-display" style={{ fontSize: 56, color: 'var(--bone)', marginTop: 6 }}>
              Hey <span className="m-display-i">Leo.</span>
            </div>
            <div style={{ marginTop: 6, fontSize: 15, color: 'rgba(245,239,227,0.6)' }}>
              You have <span style={{ color: 'var(--signal)', fontWeight: 600 }}>2 open missions</span>. About 22 minutes total.
            </div>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button className="m-btn m-btn-ghost" style={{ color: 'var(--bone)' }}>Open library</button>
            <button className="m-btn m-btn-primary">Pick up where I left <DI.arrow style={{ width: 18, height: 18 }} /></button>
          </div>
        </div>

        {/* missions grid */}
        <DEyebrow>your missions</DEyebrow>
        <div style={{ marginTop: 14, display: 'grid', gridTemplateColumns: '1.4fr 1fr 1fr', gap: 16 }}>
          <DMission state="lacuna" tag="OPEN GAP" sym="✕" title="SQL JOIN" sub="From PHP test · 12 May" cta="Start mission" big />
          <DMission state="recovery" tag="IN RECOVERY" sym="↑" title="PHP sessions" sub="Step 2 of 4" cta="Continue" />
          <DMission state="consolidate" tag="REVIEW" sym="◷" title="Arrays" sub="Final quiz" cta="Quiz me" />
        </div>

        {/* split row: map + recent docs */}
        <div style={{ marginTop: 32, display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 16 }}>
          <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 24, padding: '20px 22px 16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
              <DEyebrow>your map</DEyebrow>
              <span style={{ fontSize: 12, color: 'var(--signal)', fontWeight: 600 }}>See full map →</span>
            </div>
            <div style={{ marginTop: 12, height: 200 }}>
              <DMapMini />
            </div>
            <div style={{ marginTop: 12, display: 'flex', gap: 18, fontSize: 12, color: 'rgba(245,239,227,0.7)' }}>
              <span><span className="m-dot" style={{ background: 'var(--green)' }} /> 12 solid</span>
              <span><span className="m-dot" style={{ background: 'var(--yellow)' }} /> 4 to review</span>
              <span><span className="m-dot" style={{ background: 'var(--orange)' }} /> 1 recovering</span>
              <span><span className="m-dot" style={{ background: 'var(--red)' }} /> 1 gap</span>
            </div>
          </div>

          <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 24, padding: '20px 22px' }}>
            <DEyebrow>recent</DEyebrow>
            <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column' }}>
              {[
                { type: 'doc', title: 'PHP sessions — review', date: 'today' },
                { type: 'quiz', title: 'SQL JOIN quiz', date: 'yesterday' },
                { type: 'doc', title: 'Arrays cheatsheet', date: '15 May' },
                { type: 'video', title: 'Lesson 18 · clip', date: '14 May' },
              ].map((r, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 0', borderTop: i === 0 ? 0 : '1px solid var(--ink-3)' }}>
                  <div style={{ width: 32, height: 32, borderRadius: 10, background: 'var(--ink-3)', display: 'grid', placeItems: 'center', color: 'var(--bone)' }}>
                    {r.type === 'doc' && <DI.doc style={{ width: 14, height: 14 }} />}
                    {r.type === 'quiz' && <DI.pencil style={{ width: 14, height: 14 }} />}
                    {r.type === 'video' && <DI.video style={{ width: 14, height: 14 }} />}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13, color: 'var(--bone)' }}>{r.title}</div>
                    <div className="m-mono" style={{ fontSize: 9, letterSpacing: '0.14em', color: 'rgba(245,239,227,0.4)' }}>{r.date.toUpperCase()}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </DesktopShell>
  );
}

function DMission({ state, tag, sym, title, sub, cta, big }) {
  const c = {
    lacuna:      { bg: 'var(--bone)', fg: 'var(--ink)', pill: 'm-pill-red' },
    recovery:    { bg: 'var(--ink-2)', fg: 'var(--bone)', pill: 'm-pill-orange' },
    consolidate: { bg: 'var(--ink-2)', fg: 'var(--bone)', pill: 'm-pill-yellow' },
  }[state];
  return (
    <div style={{
      background: c.bg, color: c.fg, borderRadius: 24, padding: 22,
      border: state === 'lacuna' ? '1px solid var(--ink)' : '1px solid var(--ink-line)',
      display: 'flex', flexDirection: 'column', minHeight: big ? 220 : 200,
    }}>
      <div className={'m-pill ' + c.pill} style={{ alignSelf: 'flex-start' }}>
        <span style={{ fontSize: 10 }}>{sym}</span> {tag}
      </div>
      <div className="m-display" style={{ fontSize: big ? 44 : 30, marginTop: 14 }}>{title}</div>
      <div style={{ fontSize: 13, opacity: 0.6, marginTop: 4 }}>{sub}</div>
      <div style={{ flex: 1 }} />
      <button style={{
        marginTop: 20, alignSelf: 'flex-start',
        background: state === 'lacuna' ? 'var(--ink)' : 'var(--signal)',
        color: state === 'lacuna' ? 'var(--bone)' : 'var(--signal-ink)',
        border: 0, borderRadius: 100, padding: '12px 18px', fontSize: 13, fontWeight: 600,
        display: 'inline-flex', alignItems: 'center', gap: 8,
      }}>{cta} <DI.arrow style={{ width: 14, height: 14 }} /></button>
    </div>
  );
}

function DMapMini() {
  const nodes = [
    { x: 40, y: 30, s: 'green' }, { x: 100, y: 60, s: 'green' }, { x: 100, y: 100, s: 'yellow' },
    { x: 180, y: 50, s: 'green' }, { x: 180, y: 110, s: 'green' }, { x: 260, y: 30, s: 'orange' },
    { x: 260, y: 90, s: 'red' }, { x: 260, y: 150, s: 'yellow' }, { x: 340, y: 50, s: 'gray' },
    { x: 340, y: 130, s: 'gray' }, { x: 420, y: 80, s: 'gray' },
  ];
  const cm = { green: 'var(--green)', yellow: 'var(--yellow)', orange: 'var(--orange)', red: 'var(--red)', gray: 'var(--gray)' };
  const edges = [[0,1],[0,2],[1,3],[2,3],[2,4],[3,5],[3,6],[4,7],[5,8],[6,8],[6,9],[7,9],[8,10],[9,10]];
  return (
    <svg viewBox="0 0 460 180" style={{ width: '100%', height: '100%' }}>
      {edges.map(([a,b], i) => (
        <line key={i} x1={nodes[a].x} y1={nodes[a].y} x2={nodes[b].x} y2={nodes[b].y} stroke="rgba(245,239,227,0.16)" strokeWidth="1" />
      ))}
      {nodes.map((n, i) => (
        <g key={i}>
          <circle cx={n.x} cy={n.y} r="11" fill={cm[n.s]} stroke="var(--ink-2)" strokeWidth="3" />
          {n.s === 'red' && <text x={n.x} y={n.y + 4} fontSize="11" textAnchor="middle" fill="#fff" fontWeight="700">✕</text>}
          {n.s === 'green' && <text x={n.x} y={n.y + 4} fontSize="11" textAnchor="middle" fill="#fff" fontWeight="700">✓</text>}
        </g>
      ))}
    </svg>
  );
}

// ── DSK-ST-04 — Map ─────────────────────────────────────────
function DMap() {
  return (
    <DesktopShell active="map" subtitle="MAP · INFORMATICS · 3AI" title="Your knowledge map">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', height: '100%', overflow: 'hidden' }}>
        <div style={{ position: 'relative', overflow: 'hidden', background: 'radial-gradient(circle at 30% 30%, rgba(212,255,61,0.05), rgba(0,0,0,0) 50%)' }}>
          <svg width="100%" height="100%" style={{ position: 'absolute', inset: 0 }}>
            <defs>
              <pattern id="grid2" width="28" height="28" patternUnits="userSpaceOnUse">
                <path d="M28 0H0V28" fill="none" stroke="rgba(245,239,227,0.04)" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid2)" />
          </svg>
          <DFullMap />

          {/* zoom + filters */}
          <div style={{ position: 'absolute', top: 20, left: 20, display: 'flex', gap: 8, alignItems: 'center' }}>
            <div style={{ display: 'flex', background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 100, padding: 3 }}>
              <div style={{ padding: '6px 14px', background: 'var(--bone)', color: 'var(--ink)', borderRadius: 100, fontSize: 12, fontWeight: 600 }}>Macro</div>
              <div style={{ padding: '6px 14px', color: 'rgba(245,239,227,0.6)', fontSize: 12 }}>Micro</div>
            </div>
            <div style={{ padding: '6px 14px', background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 100, fontSize: 12, color: 'var(--bone)' }}>Filter ·</div>
          </div>

          <div style={{ position: 'absolute', right: 20, top: 20, display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={{ width: 36, height: 36, borderRadius: 12, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', display: 'grid', placeItems: 'center', color: 'var(--bone)', fontSize: 18 }}>+</div>
            <div style={{ width: 36, height: 36, borderRadius: 12, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', display: 'grid', placeItems: 'center', color: 'var(--bone)', fontSize: 18 }}>−</div>
          </div>
        </div>

        {/* right panel: selected node */}
        <aside style={{ background: 'var(--ink-2)', borderLeft: '1px solid var(--ink-line)', padding: '28px 24px', overflowY: 'auto' }}>
          <DEyebrow color="var(--red)">selected · open gap</DEyebrow>
          <div className="m-display" style={{ fontSize: 40, marginTop: 8 }}>SQL <span className="m-display-i">JOIN</span></div>
          <div className="m-pill m-pill-red" style={{ marginTop: 14 }}><span>✕</span> Open gap · 5 days</div>

          <div style={{ marginTop: 22 }}>
            <DEyebrow>definition</DEyebrow>
            <div style={{ marginTop: 8, fontSize: 13, color: 'rgba(245,239,227,0.75)', lineHeight: 1.5 }}>
              Combining rows from two or more tables based on a related column. The "glue" of relational queries.
            </div>
          </div>

          <div style={{ marginTop: 22 }}>
            <DEyebrow>history</DEyebrow>
            <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {[
                { d: '12 MAY', state: 'red',    title: 'Gap', from: 'PHP test — 2/10' },
                { d: '08 MAY', state: 'yellow', title: 'To review', from: 'Quiz — 7/10' },
                { d: '02 MAY', state: 'green',  title: 'Solid', from: 'Marked by Prof.', tag: 'OVERRIDE' },
                { d: '20 APR', state: 'white',  title: 'Introduced', from: 'Lesson 14' },
              ].map((it, i) => {
                const cm = { red: 'var(--red)', yellow: 'var(--yellow)', green: 'var(--green)', white: 'var(--white-st)' };
                return (
                  <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                    <span style={{ width: 10, height: 10, borderRadius: 100, background: cm[it.state], marginTop: 5 }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ fontSize: 13, color: 'var(--bone)', fontWeight: 600 }}>{it.title}</span>
                        <span className="m-mono" style={{ fontSize: 9, letterSpacing: '0.14em', color: 'rgba(245,239,227,0.45)' }}>{it.d}</span>
                      </div>
                      <div style={{ fontSize: 11, color: 'rgba(245,239,227,0.55)' }}>{it.from} {it.tag && <span className="m-mono" style={{ fontSize: 9, padding: '1px 6px', borderRadius: 100, background: 'var(--ink-3)', color: 'var(--signal)', marginLeft: 4 }}>{it.tag}</span>}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <button className="m-btn m-btn-primary" style={{ width: '100%', marginTop: 28 }}>
            Start mission · 4 steps <DI.arrow style={{ width: 18, height: 18 }} />
          </button>
        </aside>
      </div>
    </DesktopShell>
  );
}

function DFullMap() {
  const nodes = [
    { id: 'fund', label: 'Fundamentals', x: 130, y: 100, s: 'green', big: true },
    { id: 'vars', label: 'Variables',   x: 50,  y: 220, s: 'green' },
    { id: 'ctrl', label: 'Control flow', x: 130, y: 220, s: 'green' },
    { id: 'arr',  label: 'Arrays',       x: 210, y: 220, s: 'yellow' },
    { id: 'fn',   label: 'Functions',    x: 90,  y: 340, s: 'green' },
    { id: 'oop',  label: 'OOP basics',   x: 170, y: 340, s: 'yellow' },
    { id: 'web',  label: 'Web basics',   x: 250, y: 340, s: 'green' },
    { id: 'php',  label: 'PHP sessions', x: 250, y: 460, s: 'orange', current: true },
    { id: 'sql',  label: 'SQL JOIN',     x: 130, y: 460, s: 'red', selected: true },
    { id: 'pat',  label: 'Patterns',     x: 50,  y: 460, s: 'gray' },
    { id: 'mvc',  label: 'MVC',          x: 330, y: 460, s: 'gray' },
    { id: 'rest', label: 'REST',         x: 290, y: 560, s: 'gray' },
  ];
  const cm = { green: '#4ADE80', yellow: '#F5C53D', orange: '#FF8A3D', red: '#E74C3C', gray: '#8A8275' };
  const sm = { green: '✓', yellow: '◷', orange: '↑', red: '✕', gray: '' };
  const edges = [['fund','vars'],['fund','ctrl'],['fund','arr'],['vars','fn'],['ctrl','fn'],['ctrl','oop'],['arr','oop'],['arr','web'],['fn','pat'],['oop','sql'],['oop','php'],['web','php'],['php','mvc'],['php','rest'],['sql','mvc']];
  const nm = Object.fromEntries(nodes.map(n => [n.id, n]));
  return (
    <svg viewBox="0 0 400 640" style={{ width: '100%', height: '100%' }} preserveAspectRatio="xMidYMid meet">
      {edges.map(([a,b], i) => (
        <line key={i} x1={nm[a].x} y1={nm[a].y} x2={nm[b].x} y2={nm[b].y} stroke="rgba(245,239,227,0.22)" strokeWidth="1.2" />
      ))}
      {nodes.map(n => {
        const r = n.big ? 26 : 22;
        return (
          <g key={n.id}>
            {n.current && <circle cx={n.x} cy={n.y} r={r + 6} fill="none" stroke="var(--signal)" strokeWidth="2" opacity="0.6" />}
            {n.selected && <circle cx={n.x} cy={n.y} r={r + 9} fill="none" stroke="var(--bone)" strokeWidth="2" />}
            <circle cx={n.x} cy={n.y} r={r} fill={cm[n.s]} stroke="var(--ink)" strokeWidth="3" />
            <text x={n.x} y={n.y + 5} fontSize="14" textAnchor="middle" fill="var(--ink)" fontWeight="700">{sm[n.s]}</text>
            <text x={n.x} y={n.y + r + 16} fontSize="11" textAnchor="middle" fill="rgba(245,239,227,0.85)" style={{ fontFamily: 'Geist, sans-serif' }}>{n.label}</text>
          </g>
        );
      })}
    </svg>
  );
}

// ── DSK-ST-05 — Node detail page ────────────────────────────
function DNodeDetail() {
  return (
    <DesktopShell active="map" subtitle="MAP / DATABASE / SQL JOIN" title="">
      <div style={{ padding: '28px 32px 48px', display: 'grid', gridTemplateColumns: '1fr 320px', gap: 24 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <button style={{ width: 36, height: 36, borderRadius: 100, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
              <DI.back style={{ width: 16, height: 16 }} />
            </button>
            <DEyebrow color="var(--red)">open gap · 5 days</DEyebrow>
          </div>
          <div className="m-display" style={{ fontSize: 96, lineHeight: 0.92 }}>
            SQL<br/><span className="m-display-i">JOIN.</span>
          </div>
          <div style={{ marginTop: 18, fontSize: 16, color: 'rgba(245,239,227,0.65)', maxWidth: 580, lineHeight: 1.5 }}>
            Combining rows from two or more tables based on a related column. The "glue" of relational queries — once you get it, half of databases unlocks.
          </div>

          {/* status block */}
          <div style={{ marginTop: 28, padding: 22, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 24, display: 'flex', alignItems: 'center', gap: 22 }}>
            <div style={{ width: 80, height: 80, borderRadius: 100, background: 'var(--red)', color: '#fff', display: 'grid', placeItems: 'center', fontSize: 32, fontWeight: 700, boxShadow: '0 0 0 8px rgba(231,76,60,0.18)' }}>✕</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 18, color: 'var(--bone)', fontWeight: 600 }}>Gap detected</div>
              <div style={{ fontSize: 14, color: 'rgba(245,239,227,0.65)', marginTop: 4 }}>From your PHP test on 12 May, question 4. Don't sweat it — we have a 4-step path ready.</div>
            </div>
            <button className="m-btn m-btn-primary">Start mission <DI.arrow style={{ width: 18, height: 18 }} /></button>
          </div>

          {/* prerequisites + dependents */}
          <div style={{ marginTop: 32, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 20, padding: 18 }}>
              <DEyebrow>builds on</DEyebrow>
              <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
                {[['OOP basics','yellow','◷'],['Web basics','green','✓'],['Relations','green','✓']].map(([n,s,g]) => (
                  <div key={n} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ width: 22, height: 22, borderRadius: 100, background: 'var(--' + s + ')', color: 'var(--ink)', display: 'grid', placeItems: 'center', fontSize: 11, fontWeight: 700 }}>{g}</span>
                    <span style={{ fontSize: 14, color: 'var(--bone)' }}>{n}</span>
                  </div>
                ))}
              </div>
            </div>
            <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 20, padding: 18 }}>
              <DEyebrow>unlocks</DEyebrow>
              <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
                {[['MVC','gray','·'],['REST APIs','gray','·'],['Complex queries','gray','·']].map(([n,s,g]) => (
                  <div key={n} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ width: 22, height: 22, borderRadius: 100, background: 'var(--' + s + ')', color: 'var(--ink)', display: 'grid', placeItems: 'center', fontSize: 11, fontWeight: 700, opacity: 0.6 }}>{g}</span>
                    <span style={{ fontSize: 14, color: 'rgba(245,239,227,0.65)' }}>{n}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* right: history + materials */}
        <aside style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 20, padding: 18 }}>
            <DEyebrow>history</DEyebrow>
            <div style={{ marginTop: 12, position: 'relative', paddingLeft: 16 }}>
              <div style={{ position: 'absolute', left: 4, top: 8, bottom: 8, width: 1, background: 'var(--ink-line)' }} />
              {[
                { d: '12 MAY', s: 'red', t: 'Gap', f: 'PHP test — 2/10' },
                { d: '08 MAY', s: 'yellow', t: 'To review', f: 'Quiz — 7/10' },
                { d: '02 MAY', s: 'green', t: 'Solid', f: 'Override · Prof.' },
                { d: '20 APR', s: 'white-st', t: 'Introduced', f: 'Lesson 14' },
              ].map((it, i) => (
                <div key={i} style={{ position: 'relative', paddingBottom: 12 }}>
                  <span style={{ position: 'absolute', left: -16, top: 4, width: 11, height: 11, borderRadius: 100, background: 'var(--' + it.s + ')', border: '2px solid var(--ink-2)' }} />
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: 13, color: 'var(--bone)', fontWeight: 600 }}>{it.t}</span>
                    <span className="m-mono" style={{ fontSize: 9, letterSpacing: '0.14em', color: 'rgba(245,239,227,0.45)' }}>{it.d}</span>
                  </div>
                  <div style={{ fontSize: 11, color: 'rgba(245,239,227,0.55)' }}>{it.f}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 20, padding: 18 }}>
            <DEyebrow>materials</DEyebrow>
            <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 6 }}>
              {[['Personalised doc', DI.doc],['Lesson clip · 02:14', DI.video],['Practice set', DI.pencil]].map(([t, Ic], i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 0', borderTop: i === 0 ? 0 : '1px solid var(--ink-3)' }}>
                  <Ic style={{ width: 16, height: 16, color: 'rgba(245,239,227,0.7)' }} />
                  <span style={{ flex: 1, fontSize: 13 }}>{t}</span>
                  <DI.arrow style={{ width: 14, height: 14, opacity: 0.6 }} />
                </div>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </DesktopShell>
  );
}

// ── DSK-ST-06 — Mission ─────────────────────────────────────
function DMissionPage() {
  const steps = [
    { Ic: DI.doc, title: 'Read the explainer', sub: '2 min · personalised to you', state: 'done' },
    { Ic: DI.video, title: 'Watch the lesson clip', sub: '02:14 · Prof. Russo · lesson 18', state: 'current' },
    { Ic: DI.hand, title: 'Try a guided exercise', sub: '3 steps · drag & drop', state: 'todo' },
    { Ic: DI.pencil, title: 'Closing quiz', sub: '5 questions · check what stuck', state: 'todo' },
  ];
  return (
    <DesktopShell active="missions" subtitle="MISSION · STEP 2 / 4" title="">
      <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1fr', height: '100%', overflow: 'hidden' }}>
        <div style={{ padding: '32px 36px 40px', overflow: 'auto' }}>
          <DEyebrow color="var(--signal)">mission in progress</DEyebrow>
          <div className="m-display" style={{ fontSize: 76, lineHeight: 0.95, marginTop: 10 }}>
            Mission:<br/><span className="m-display-i">SQL JOIN.</span>
          </div>
          <div style={{ marginTop: 16, fontSize: 15, color: 'rgba(245,239,227,0.65)', maxWidth: 540 }}>
            A short path tuned to how you learn. Visuals first, then a tiny exercise, then a check.
          </div>

          <div style={{ marginTop: 24, display: 'flex', gap: 6 }}>
            {[1,1,0,0].map((d, i) => (
              <div key={i} style={{ flex: 1, height: 8, borderRadius: 100, background: d ? 'var(--signal)' : 'var(--ink-3)' }} />
            ))}
          </div>
          <div className="m-mono" style={{ marginTop: 8, fontSize: 10, letterSpacing: '0.14em', color: 'rgba(245,239,227,0.55)' }}>
            50% · ABOUT 8 MINUTES LEFT
          </div>

          <div style={{ marginTop: 32, display: 'flex', flexDirection: 'column', gap: 10 }}>
            {steps.map((s, i) => <DStepRow key={i} idx={i} step={s} />)}
          </div>
        </div>

        {/* right: current step preview */}
        <aside style={{ background: 'var(--ink-2)', borderLeft: '1px solid var(--ink-line)', padding: '32px 30px', display: 'flex', flexDirection: 'column' }}>
          <DEyebrow>current step</DEyebrow>
          <div className="m-display" style={{ fontSize: 36, marginTop: 8 }}>Watch the <span className="m-display-i">lesson clip</span></div>
          <div style={{ marginTop: 6, fontSize: 13, color: 'rgba(245,239,227,0.6)' }}>02:14 · Prof. Russo · Lesson 18</div>

          {/* video preview */}
          <div style={{ marginTop: 20, aspectRatio: '16/10', background: 'linear-gradient(135deg, #1e1812, #14110D)', border: '1px solid var(--ink-line)', borderRadius: 20, position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(circle at 30% 30%, rgba(212,255,61,0.1), rgba(0,0,0,0) 50%)' }} />
            <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center' }}>
              <div style={{ width: 76, height: 76, borderRadius: 100, background: 'var(--signal)', color: 'var(--signal-ink)', display: 'grid', placeItems: 'center', boxShadow: '0 8px 32px rgba(212,255,61,0.3)' }}>
                <DI.play style={{ width: 30, height: 30 }} />
              </div>
            </div>
            <div style={{ position: 'absolute', bottom: 14, left: 14, right: 14, display: 'flex', alignItems: 'center', gap: 10, fontSize: 11, color: 'rgba(245,239,227,0.8)' }}>
              <span className="m-mono" style={{ letterSpacing: '0.12em' }}>00:00 / 02:14</span>
              <div style={{ flex: 1, height: 3, background: 'rgba(245,239,227,0.18)', borderRadius: 100 }}>
                <div style={{ width: '0%', height: '100%', background: 'var(--signal)', borderRadius: 100 }} />
              </div>
            </div>
          </div>

          <div style={{ marginTop: 18, fontSize: 13, color: 'rgba(245,239,227,0.6)', lineHeight: 1.5 }}>
            Prof. Russo draws an INNER JOIN on the board with two tables of students and grades. Pause whenever — Maestro remembers your place.
          </div>

          <div style={{ flex: 1 }} />
          <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
            <button className="m-btn m-btn-ghost" style={{ color: 'var(--bone)' }}>Skip</button>
            <button className="m-btn m-btn-primary" style={{ flex: 1 }}>
              Mark as watched <DI.check style={{ width: 18, height: 18 }} />
            </button>
          </div>
        </aside>
      </div>
    </DesktopShell>
  );
}
function DStepRow({ step, idx }) {
  const isDone = step.state === 'done';
  const isCurrent = step.state === 'current';
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 16, padding: '16px 18px',
      borderRadius: 18,
      background: isCurrent ? 'var(--bone)' : 'var(--ink-2)',
      color: isCurrent ? 'var(--ink)' : 'var(--bone)',
      border: '1px solid ' + (isCurrent ? 'var(--bone)' : 'var(--ink-line)'),
      opacity: step.state === 'todo' ? 0.55 : 1,
    }}>
      <div style={{ width: 44, height: 44, borderRadius: 14, flex: 'none', background: isDone ? 'var(--green)' : isCurrent ? 'var(--ink)' : 'var(--ink-3)', color: isDone ? 'var(--ink)' : isCurrent ? 'var(--signal)' : 'var(--bone)', display: 'grid', placeItems: 'center' }}>
        {isDone ? <DI.check style={{ width: 20, height: 20 }} /> : <step.Ic style={{ width: 20, height: 20 }} />}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 15, fontWeight: 600 }}>{step.title}</div>
        <div style={{ fontSize: 12, opacity: 0.6, marginTop: 2 }}>{step.sub}</div>
      </div>
      {isCurrent && <DI.play style={{ width: 18, height: 18 }} />}
      <span className="m-mono" style={{ fontSize: 10, opacity: 0.4, letterSpacing: '0.14em' }}>0{idx + 1} / 04</span>
    </div>
  );
}

// ── DSK-ST-07a — Quiz question (light) ──────────────────────
function DQuizQ() {
  const opts = [
    { l: 'A', t: 'INNER JOIN returns only rows where the key exists in both tables.', state: 'selected' },
    { l: 'B', t: 'INNER JOIN returns all rows from the left table.', state: 'idle' },
    { l: 'C', t: 'INNER JOIN merges columns regardless of keys.', state: 'idle' },
    { l: 'D', t: 'INNER JOIN is the same as UNION.', state: 'idle' },
  ];
  return (
    <div className="maestro-screen light" style={{
      width: '100%', height: '100%', background: 'var(--bone)', color: 'var(--ink)',
      display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative',
    }}>
      {/* header */}
      <div style={{ padding: '20px 32px', display: 'flex', alignItems: 'center', gap: 16 }}>
        <button style={{ width: 38, height: 38, borderRadius: 100, background: 'transparent', border: '1px solid rgba(20,17,13,0.18)', color: 'var(--ink)', display: 'grid', placeItems: 'center' }}>
          <DI.x style={{ width: 16, height: 16 }} />
        </button>
        <DEyebrow>quiz · sql join</DEyebrow>
        <div style={{ flex: 1, display: 'flex', gap: 4, maxWidth: 280 }}>
          {[1,1,1,0,0].map((d, i) => (
            <div key={i} style={{ flex: 1, height: 6, borderRadius: 100, background: d ? 'var(--ink)' : 'rgba(20,17,13,0.12)' }} />
          ))}
        </div>
        <span className="m-mono" style={{ fontSize: 11, opacity: 0.6, letterSpacing: '0.14em' }}>03 / 05</span>
      </div>

      <div style={{ flex: 1, padding: '24px 80px', display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: 80, alignItems: 'center' }}>
        <div>
          <DEyebrow>question 3</DEyebrow>
          <div className="m-display" style={{ fontSize: 76, lineHeight: 0.95, marginTop: 12 }}>
            What does an<br/><span className="m-display-i">INNER JOIN</span><br/>do?
          </div>
          <div style={{ marginTop: 22, fontSize: 14, color: 'rgba(20,17,13,0.6)' }}>
            Take your time. There's no penalty for thinking.
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {opts.map(o => {
            const sel = o.state === 'selected';
            return (
              <div key={o.l} style={{
                display: 'flex', alignItems: 'center', gap: 16, padding: 22,
                background: sel ? 'var(--ink)' : '#fff',
                color: sel ? 'var(--bone)' : 'var(--ink)',
                border: '1px solid ' + (sel ? 'var(--ink)' : 'rgba(20,17,13,0.1)'),
                borderRadius: 20,
              }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 100, flex: 'none',
                  background: sel ? 'var(--signal)' : 'transparent',
                  color: sel ? 'var(--signal-ink)' : 'var(--ink)',
                  border: sel ? '0' : '1px solid rgba(20,17,13,0.25)',
                  display: 'grid', placeItems: 'center', fontSize: 14, fontWeight: 700, fontFamily: 'var(--mono)',
                }}>{o.l}</div>
                <div style={{ flex: 1, fontSize: 16, lineHeight: 1.4 }}>{o.t}</div>
              </div>
            );
          })}
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 12 }}>
            <button className="m-btn" style={{ background: 'var(--ink)', color: 'var(--bone)', padding: '16px 28px' }}>
              Confirm <DI.arrow style={{ width: 18, height: 18 }} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── DSK-ST-07b — Quiz result ────────────────────────────────
function DQuizR() {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)', overflow: 'hidden', position: 'relative',
      display: 'flex', flexDirection: 'column',
    }}>
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(circle at 50% 0%, rgba(74,222,128,0.18), rgba(0,0,0,0) 55%)', pointerEvents: 'none' }} />
      <div style={{ padding: '20px 32px', display: 'flex', justifyContent: 'flex-end', position: 'relative' }}>
        <button style={{ width: 38, height: 38, borderRadius: 100, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
          <DI.x style={{ width: 16, height: 16 }} />
        </button>
      </div>

      <div style={{ flex: 1, padding: '40px 80px 56px', display: 'grid', gridTemplateColumns: '1fr 1.1fr', gap: 80, alignItems: 'center', position: 'relative' }}>
        <div style={{ textAlign: 'left' }}>
          <DI.spark style={{ width: 36, height: 36, color: 'var(--signal)', marginBottom: 16 }} />
          <DEyebrow color="var(--green)">nailed it</DEyebrow>
          <div className="m-display" style={{ fontSize: 200, lineHeight: 0.9, color: 'var(--bone)', marginTop: 8 }}>
            4<span className="m-display-i" style={{ color: 'var(--signal)' }}>/</span>5
          </div>
          <div style={{ marginTop: 12, fontSize: 16, color: 'rgba(245,239,227,0.6)' }}>
            That's 80% · keep this in your head.
          </div>
          <div className="m-pill m-pill-yellow" style={{ marginTop: 22, padding: '6px 14px', fontSize: 13 }}>
            <span>◷</span> SQL JOIN moved to "TO REVIEW"
          </div>
          <div style={{ marginTop: 28, display: 'flex', gap: 12 }}>
            <button className="m-btn m-btn-primary">Back to your map <DI.arrow style={{ width: 18, height: 18 }} /></button>
            <button className="m-btn m-btn-ghost" style={{ color: 'var(--bone)' }}>Try a fresh angle</button>
          </div>
        </div>

        <div>
          <DEyebrow>by question</DEyebrow>
          <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[
              { n: 1, ok: true,  q: 'What is a relation?' },
              { n: 2, ok: true,  q: 'INNER vs LEFT JOIN' },
              { n: 3, ok: true,  q: 'JOIN on multiple keys' },
              { n: 4, ok: false, q: 'Self-join example' },
              { n: 5, ok: true,  q: 'Result table semantics' },
            ].map(r => (
              <div key={r.n} style={{ display: 'flex', alignItems: 'center', gap: 14, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 16, padding: '14px 18px' }}>
                <span style={{ width: 32, height: 32, borderRadius: 100, background: r.ok ? 'var(--green)' : 'var(--orange)', color: 'var(--ink)', display: 'grid', placeItems: 'center', flex: 'none' }}>
                  {r.ok ? <DI.check style={{ width: 16, height: 16 }} /> : <DI.x style={{ width: 16, height: 16 }} />}
                </span>
                <span className="m-mono" style={{ fontSize: 11, color: 'rgba(245,239,227,0.55)', letterSpacing: '0.14em' }}>Q0{r.n}</span>
                <span style={{ flex: 1, fontSize: 14, color: 'var(--bone)' }}>{r.q}</span>
                <span style={{ fontSize: 12, color: 'rgba(245,239,227,0.5)' }}>review</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── DSK-ST-08 — Document (light/paper) ──────────────────────
function DDocument() {
  return (
    <DesktopShell active="library" light subtitle="MISSION · STEP 1" hideTopBreadcrumb>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', height: '100%', overflow: 'hidden' }}>
        <div style={{ overflowY: 'auto', padding: '40px 80px 80px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <DEyebrow>review · made for you</DEyebrow>
            <span className="m-mono" style={{ fontSize: 9, letterSpacing: '0.16em', padding: '3px 8px', borderRadius: 100, background: 'var(--signal)', color: 'var(--signal-ink)' }}>PERSONALISED</span>
          </div>
          <div className="m-display" style={{ fontSize: 88, lineHeight: 0.92, marginTop: 14 }}>
            PHP <span className="m-display-i">sessions.</span>
          </div>
          <div style={{ marginTop: 14, fontSize: 16, color: 'rgba(20,17,13,0.55)', maxWidth: 600 }}>
            3 min read · with a basketball analogy, like you wanted. We rewrote this version after your test on 12 May.
          </div>

          <div style={{ marginTop: 36, display: 'flex', flexDirection: 'column', gap: 18, maxWidth: 720 }}>
            <DBlock tag="WHERE YOU SLIPPED" tone="yellow" label="ERROR">
              <pre style={dPre}>{`<?php
  session_start();
  $_SESSION['user'] = $name;
?>
<html>
  <body>...`}</pre>
              <div style={{ fontSize: 14, color: 'rgba(20,17,13,0.7)', marginTop: 12, lineHeight: 1.5 }}>
                You opened the session <em>after</em> some output already left the server. PHP doesn't get a second chance to set cookies once HTML has started flowing.
              </div>
            </DBlock>

            <DBlock tag="THE BASKETBALL VERSION" tone="ink">
              <div style={{ fontSize: 16, lineHeight: 1.55, color: 'var(--ink)' }}>
                A session is like checking in at the gym desk. If you walk onto the court first, the desk can't log you in anymore — the game's already started, the doors closed behind you.
              </div>
            </DBlock>

            <DBlock tag="HOW IT WORKS RIGHT" tone="green" label="CORRECT">
              <pre style={dPre}>{`<?php
  session_start();   // first thing — before any output
?>
<html>
  <body>
    Hello <?= $_SESSION['user'] ?>`}</pre>
            </DBlock>

            <DBlock tag="REMEMBER THIS" tone="signal">
              <div style={{ fontSize: 18, color: 'var(--ink)', fontWeight: 600, lineHeight: 1.4 }}>
                <span className="m-display-i" style={{ fontSize: 24 }}>session_start()</span> must be the very first line — before any HTML, whitespace, or echo.
              </div>
            </DBlock>
          </div>

          <div style={{ marginTop: 36, display: 'flex', gap: 12 }}>
            <button style={{ padding: '14px 20px', borderRadius: 100, background: '#fff', border: '1px solid rgba(20,17,13,0.12)', color: 'var(--ink)', fontWeight: 600, fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 8 }}>
              <DI.sound style={{ width: 16, height: 16 }} /> Listen instead
            </button>
            <button className="m-btn" style={{ background: 'var(--ink)', color: 'var(--bone)' }}>
              Continue to step 2 <DI.arrow style={{ width: 16, height: 16 }} />
            </button>
          </div>
        </div>

        {/* right rail: TOC + why-this */}
        <aside style={{ background: '#FFFEF8', borderLeft: '1px solid rgba(20,17,13,0.06)', padding: '32px 24px', overflowY: 'auto' }}>
          <DEyebrow>on this page</DEyebrow>
          <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column' }}>
            {[
              { t: 'Where you slipped', s: 'var(--yellow)' },
              { t: 'The basketball version', s: 'var(--ink)' },
              { t: 'How it works right', s: 'var(--green)' },
              { t: 'Remember this', s: 'var(--signal-ink)' },
            ].map((it, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 0' }}>
                <span style={{ width: 3, height: 18, borderRadius: 2, background: it.s }} />
                <span style={{ fontSize: 13, color: 'var(--ink)' }}>{it.t}</span>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 28, padding: 16, background: '#fff', border: '1px solid rgba(20,17,13,0.06)', borderRadius: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <DI.spark style={{ width: 14, height: 14, color: 'var(--signal-ink)' }} />
              <DEyebrow>why this?</DEyebrow>
            </div>
            <div style={{ marginTop: 8, fontSize: 12, color: 'rgba(20,17,13,0.65)', lineHeight: 1.5 }}>
              You're a visual + hands-on type, casual tone, short reads. We added a sport analogy because you marked them helpful last week.
            </div>
            <button style={{ marginTop: 10, background: 'transparent', border: 0, padding: 0, color: 'var(--ink)', fontSize: 12, fontWeight: 600, borderBottom: '1px solid currentColor' }}>
              See full reasoning →
            </button>
          </div>

          <div style={{ marginTop: 24 }}>
            <DEyebrow>your prefs</DEyebrow>
            <div style={{ marginTop: 8, fontSize: 12, color: 'rgba(20,17,13,0.6)' }}>
              Casual · Short · Sport analogies on
            </div>
          </div>
        </aside>
      </div>
    </DesktopShell>
  );
}
const dPre = {
  margin: 0, padding: '14px 16px', background: 'rgba(20,17,13,0.06)',
  borderRadius: 12, fontFamily: 'var(--mono)', fontSize: 13, lineHeight: 1.55,
  color: 'var(--ink)', whiteSpace: 'pre-wrap',
};
function DBlock({ tag, tone, label, children }) {
  const tones = {
    yellow: { bg: 'rgba(245,197,61,0.18)', stripe: 'var(--yellow)', tag: 'rgba(120,90,10,1)' },
    green:  { bg: 'rgba(74,222,128,0.18)', stripe: 'var(--green)', tag: 'rgba(20,90,40,1)' },
    ink:    { bg: '#fff', stripe: 'var(--ink)', tag: 'rgba(20,17,13,0.65)' },
    signal: { bg: 'var(--signal)', stripe: 'var(--signal-ink)', tag: 'var(--signal-ink)' },
  }[tone];
  return (
    <div style={{ background: tones.bg, borderRadius: 18, padding: '18px 20px 20px', borderLeft: `5px solid ${tones.stripe}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <span className="m-mono" style={{ fontSize: 10, letterSpacing: '0.18em', color: tones.tag }}>{tag}</span>
        {label && <span className="m-mono" style={{ fontSize: 9, letterSpacing: '0.18em', padding: '3px 9px', borderRadius: 100, background: tones.stripe, color: tone === 'signal' ? 'var(--signal)' : '#fff' }}>{label}</span>}
      </div>
      {children}
    </div>
  );
}

// ── DSK-ST-09 — Profile ─────────────────────────────────────
function DProfile() {
  return (
    <DesktopShell active="profile" subtitle="YOUR SETUP">
      <div style={{ padding: '32px 36px 56px' }}>
        <DEyebrow>profile</DEyebrow>
        <div className="m-display" style={{ fontSize: 64, marginTop: 8 }}>
          Hey <span className="m-display-i">Leo.</span>
        </div>
        <div style={{ marginTop: 6, fontSize: 15, color: 'rgba(245,239,227,0.6)' }}>17 nodes solid · 1 open gap · 12-day streak</div>

        <div style={{ marginTop: 32, display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: 20 }}>
          {/* left col */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 24, padding: 28 }}>
              <DEyebrow>how I learn</DEyebrow>
              <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 24 }}>
                <DMiniRadarBig />
                <div style={{ flex: 1 }}>
                  <div className="m-display" style={{ fontSize: 30 }}>Visual · hands-on.</div>
                  <div style={{ marginTop: 10, fontSize: 14, color: 'rgba(245,239,227,0.65)', lineHeight: 1.5 }}>
                    We lean into diagrams and tiny experiments. Long lectures are minimised unless you ask.
                  </div>
                </div>
              </div>
              <div style={{ marginTop: 18, display: 'flex', gap: 18, fontSize: 12, color: 'rgba(245,239,227,0.7)' }}>
                {[['Visual', 85],['Auditory', 55],['Hands-on', 78],['Reflective', 40],['Social', 62]].map(([l, v]) => (
                  <div key={l} style={{ flex: 1 }}>
                    <div className="m-mono" style={{ fontSize: 9, letterSpacing: '0.14em', opacity: 0.6 }}>{l.toUpperCase()}</div>
                    <div style={{ marginTop: 4, fontSize: 16, fontWeight: 600, color: 'var(--bone)' }}>{v}<span style={{ opacity: 0.5, fontSize: 11 }}>%</span></div>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 24, padding: 28 }}>
              <DEyebrow>tone & length</DEyebrow>
              <div style={{ marginTop: 14 }}>
                <div style={{ fontSize: 12, color: 'rgba(245,239,227,0.6)', marginBottom: 6 }}>How Maestro talks to you</div>
                <div style={{ display: 'flex', background: 'var(--ink-3)', border: '1px solid var(--ink-line)', borderRadius: 100, padding: 3 }}>
                  {['Casual','Calm','Formal'].map((t, i) => (
                    <div key={t} style={{ flex: 1, textAlign: 'center', padding: '9px 12px', background: i === 0 ? 'var(--bone)' : 'transparent', color: i === 0 ? 'var(--ink)' : 'rgba(245,239,227,0.6)', borderRadius: 100, fontSize: 13, fontWeight: 600 }}>{t}</div>
                  ))}
                </div>
              </div>
              <div style={{ marginTop: 14 }}>
                <div style={{ fontSize: 12, color: 'rgba(245,239,227,0.6)', marginBottom: 6 }}>Depth of explanations</div>
                <div style={{ display: 'flex', background: 'var(--ink-3)', border: '1px solid var(--ink-line)', borderRadius: 100, padding: 3 }}>
                  {['Short','Deep dive'].map((t, i) => (
                    <div key={t} style={{ flex: 1, textAlign: 'center', padding: '9px 12px', background: i === 0 ? 'var(--bone)' : 'transparent', color: i === 0 ? 'var(--ink)' : 'rgba(245,239,227,0.6)', borderRadius: 100, fontSize: 13, fontWeight: 600 }}>{t}</div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* right col */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 24, padding: 28 }}>
              <DEyebrow>accessibility</DEyebrow>
              <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 16 }}>
                <DRow label="Font" right={<span style={{ color: 'var(--signal)', fontWeight: 600 }}>Geist</span>} />
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 8 }}>
                    <span>Text size</span><span style={{ color: 'var(--signal)' }}>17 pt</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ fontSize: 12, opacity: 0.5 }}>A</span>
                    <div style={{ flex: 1, height: 4, borderRadius: 100, background: 'var(--ink-3)', position: 'relative' }}>
                      <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '45%', background: 'var(--signal)', borderRadius: 100 }} />
                      <div style={{ position: 'absolute', left: 'calc(45% - 9px)', top: -7, width: 18, height: 18, borderRadius: 100, background: 'var(--signal)', border: '3px solid var(--ink-2)' }} />
                    </div>
                    <span style={{ fontSize: 18, opacity: 0.7, fontWeight: 600 }}>A</span>
                  </div>
                </div>
                <DRow label="Theme" right={
                  <div style={{ display: 'flex', gap: 4, fontSize: 11 }}>
                    {['Light','Dark','Sepia'].map((t, i) => (
                      <div key={t} style={{ padding: '5px 12px', borderRadius: 100, background: i === 1 ? 'var(--bone)' : 'transparent', color: i === 1 ? 'var(--ink)' : 'rgba(245,239,227,0.55)', fontWeight: 600 }}>{t}</div>
                    ))}
                  </div>
                } />
                <DRow label="High contrast" right={<DToggle on={false} />} />
                <DRow label="Reduce motion" right={<DToggle on={true} />} />
              </div>
            </div>

            <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 24, padding: 28 }}>
              <DEyebrow>privacy & data</DEyebrow>
              <div style={{ marginTop: 14, fontSize: 13, color: 'rgba(245,239,227,0.6)', lineHeight: 1.5 }}>
                Your family registered 4 of 5 consents. <span style={{ color: 'var(--signal)' }}>View details →</span>
              </div>
              <div style={{ marginTop: 14, display: 'flex', gap: 10 }}>
                <button className="m-btn m-btn-ghost" style={{ color: 'var(--bone)', fontSize: 13, padding: '12px 18px' }}>Download my data</button>
                <button style={{ background: 'transparent', border: '1px solid var(--red)', color: 'var(--red)', borderRadius: 100, padding: '12px 18px', fontSize: 13, fontWeight: 600 }}>Request erasure</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DesktopShell>
  );
}
function DRow({ label, right }) { return <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 14, color: 'var(--bone)' }}>{label}<div>{right}</div></div>; }
function DToggle({ on }) {
  return <div style={{ width: 44, height: 26, borderRadius: 100, background: on ? 'var(--signal)' : 'var(--ink-3)', position: 'relative', border: '1px solid var(--ink-line)' }}>
    <div style={{ position: 'absolute', top: 2, left: on ? 20 : 2, width: 20, height: 20, borderRadius: 100, background: '#fff' }} />
  </div>;
}
function DMiniRadarBig() {
  const axes = [0.85, 0.55, 0.78, 0.40, 0.62];
  const cx = 75, cy = 75, R = 58;
  const pts = axes.map((v, i) => {
    const a = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
    return [cx + Math.cos(a) * R * v, cy + Math.sin(a) * R * v];
  });
  return (
    <svg width="150" height="150" viewBox="0 0 150 150">
      {[0.5, 1].map(s => (
        <polygon key={s} points={axes.map((_, i) => {
          const a = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
          return [cx + Math.cos(a) * R * s, cy + Math.sin(a) * R * s].join(',');
        }).join(' ')} fill="none" stroke="rgba(245,239,227,0.12)" />
      ))}
      <polygon points={pts.map(p => p.join(',')).join(' ')} fill="rgba(212,255,61,0.25)" stroke="var(--signal)" strokeWidth="2" />
      {pts.map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r="3" fill="var(--signal)" />)}
    </svg>
  );
}

// ── DSK-ST-10 — Why this? (modal) ───────────────────────────
function DExplain() {
  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* dimmed page behind */}
      <div style={{ position: 'absolute', inset: 0, opacity: 0.35, pointerEvents: 'none', filter: 'blur(2px)' }}>
        <DDocument />
      </div>
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.45)' }} />

      {/* modal */}
      <div style={{
        position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
        width: 720, maxHeight: 'calc(100% - 80px)',
        background: 'var(--ink-2)', borderRadius: 28, border: '1px solid var(--ink-line)',
        boxShadow: '0 40px 100px rgba(0,0,0,0.6)',
        padding: '36px 40px', color: 'var(--bone)',
        display: 'flex', flexDirection: 'column', overflow: 'auto',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <DI.spark style={{ width: 20, height: 20, color: 'var(--signal)' }} />
            <DEyebrow color="var(--signal)">maestro reasoning</DEyebrow>
          </div>
          <button style={{ width: 32, height: 32, borderRadius: 100, background: 'var(--ink-3)', border: 0, color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
            <DI.x style={{ width: 14, height: 14 }} />
          </button>
        </div>
        <div className="m-display" style={{ fontSize: 56, marginTop: 12, lineHeight: 0.95 }}>
          Why am I showing you <span className="m-display-i">this</span>?
        </div>

        <div style={{ marginTop: 28, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
          <div>
            <DEyebrow>concepts in play</DEyebrow>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 10 }}>
              <div className="m-pill m-pill-red"><span>✕</span> PHP sessions</div>
              <div className="m-pill m-pill-yellow"><span>◷</span> Output buffering</div>
            </div>
          </div>
          <div>
            <DEyebrow>your profile</DEyebrow>
            <div style={{ marginTop: 10, fontSize: 13, color: 'rgba(245,239,227,0.75)', lineHeight: 1.45 }}>
              Visual + hands-on · Casual tone · Short reads · Sport analogies on.
            </div>
          </div>
        </div>

        <div style={{ marginTop: 24 }}>
          <DEyebrow>what just happened</DEyebrow>
          <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', gap: 12, fontSize: 13, color: 'rgba(245,239,227,0.7)' }}>
              <span className="m-dot" style={{ background: 'var(--red)', marginTop: 6 }} />
              <span><b style={{ color: 'var(--bone)' }}>12 May</b> · test answer flagged a gap on PHP sessions (Q4, 0/2 points)</span>
            </div>
            <div style={{ display: 'flex', gap: 12, fontSize: 13, color: 'rgba(245,239,227,0.7)' }}>
              <span className="m-dot" style={{ background: 'var(--orange)', marginTop: 6 }} />
              <span><b style={{ color: 'var(--bone)' }}>13 May</b> · this mission was generated</span>
            </div>
            <div style={{ display: 'flex', gap: 12, fontSize: 13, color: 'rgba(245,239,227,0.7)' }}>
              <span className="m-dot" style={{ background: 'var(--signal)', marginTop: 6 }} />
              <span><b style={{ color: 'var(--bone)' }}>now</b> · this doc was written for you with a basketball analogy</span>
            </div>
          </div>
        </div>

        <div style={{ marginTop: 28, display: 'flex', gap: 12 }}>
          <button className="m-btn m-btn-ghost" style={{ color: 'var(--bone)', flex: 1 }}>Explain it more simply</button>
          <button className="m-btn m-btn-primary" style={{ flex: 1 }}>Got it <DI.check style={{ width: 18, height: 18 }} /></button>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, {
  DLogin, DOnbWelcome, DOnbQuiz, DOnbResult,
  DHome, DMap, DNodeDetail, DMissionPage,
  DQuizQ, DQuizR, DDocument, DProfile, DExplain,
});
