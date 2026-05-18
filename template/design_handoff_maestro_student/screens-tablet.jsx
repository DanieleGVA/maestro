/* global React */
// MAESTRO — Tablet screens (820×1180, iPad portrait reference)
// Strategy: mobile structure but more spacious, with side panels where it earns its space.

const TI = {
  arrow: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M5 12h14M13 5l7 7-7 7"/></svg>),
  back: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M19 12H5M12 19l-7-7 7-7"/></svg>),
  check: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M4 12l5 5L20 6"/></svg>),
  x: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M5 5l14 14M19 5L5 19"/></svg>),
  home: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M3 11l9-8 9 8"/><path d="M5 10v11h14V10"/></svg>),
  map: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M8 7l8 0M7 8l4 8M17 8l-4 8"/></svg>),
  person: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/></svg>),
  bell: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M6 8a6 6 0 0 1 12 0c0 7 3 8 3 8H3s3-1 3-8Z"/><path d="M10 21a2 2 0 0 0 4 0"/></svg>),
  fire: (p) => (<svg viewBox="0 0 24 24" fill="currentColor" {...p}><path d="M13 2c1 3-2 5-2 8a3 3 0 0 0 6 0c2 2 3 5 3 7a8 8 0 1 1-16 0c0-3 2-6 4-7 0 2 1 4 3 4 0-4-1-7 2-12z"/></svg>),
  play: (p) => (<svg viewBox="0 0 24 24" fill="currentColor" {...p}><path d="M7 4v16l13-8z"/></svg>),
  doc: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4"/></svg>),
  video: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><rect x="2" y="6" width="14" height="12" rx="2"/><path d="M16 10l6-3v10l-6-3z"/></svg>),
  pencil: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M16 3l5 5L8 21H3v-5z"/></svg>),
  hand: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M9 11V5a2 2 0 1 1 4 0v6"/><path d="M13 11V4a2 2 0 1 1 4 0v9"/><path d="M17 11V6a2 2 0 1 1 4 0v9a6 6 0 0 1-6 6h-2a6 6 0 0 1-6-6v-2l-2-3a2 2 0 0 1 3-3l2 2"/></svg>),
  sound: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M11 5L6 9H3v6h3l5 4V5z"/><path d="M15 8.5a4 4 0 0 1 0 7"/></svg>),
  eye: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>),
  spark: (p) => (<svg viewBox="0 0 24 24" fill="currentColor" {...p}><path d="M12 2l1.6 6.4L20 10l-6.4 1.6L12 18l-1.6-6.4L4 10l6.4-1.6L12 2z"/></svg>),
};

const TEyebrow = ({ children, color }) => (
  <div className="m-mono" style={{ fontSize: 11, letterSpacing: '0.18em', textTransform: 'uppercase', opacity: color ? 1 : 0.55, color: color || 'inherit' }}>{children}</div>
);

// ── TabletShell — top status bar + side tab bar ─────────────
function TabletShell({ children, light, active }) {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%',
      background: light ? 'var(--paper)' : 'var(--ink)',
      color: light ? 'var(--ink)' : 'var(--bone)',
      display: 'flex', overflow: 'hidden', position: 'relative',
    }}>
      {/* Left vertical tabbar */}
      <aside style={{
        width: 86, flex: 'none',
        background: light ? '#FFFEF8' : 'var(--ink-2)',
        borderRight: '1px solid ' + (light ? 'rgba(20,17,13,0.06)' : 'var(--ink-line)'),
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        padding: '32px 0 24px',
      }}>
        <div className="m-display" style={{ fontSize: 22, color: light ? 'var(--ink)' : 'var(--bone)', writingMode: 'horizontal-tb' }}>
          M<span style={{ color: 'var(--signal)' }}>.</span>
        </div>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 6, marginTop: 36 }}>
          <TTabIcon Ic={TI.home}   label="Home"     active={active === 'home'} light={light} />
          <TTabIcon Ic={TI.map}    label="Map"      active={active === 'map'} light={light} />
          <TTabIcon Ic={TI.person} label="Profile"  active={active === 'profile'} light={light} />
        </div>
        <div style={{ width: 44, height: 44, borderRadius: 14, background: 'var(--signal)', color: 'var(--signal-ink)', display: 'grid', placeItems: 'center', fontFamily: 'var(--display)', fontSize: 24 }}>L</div>
      </aside>
      <div style={{ flex: 1, overflow: 'auto', minHeight: 0 }}>
        {children}
      </div>
    </div>
  );
}
function TTabIcon({ Ic, label, active, light }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
      padding: '14px 6px', borderRadius: 14, width: 64,
      background: active ? (light ? 'var(--ink)' : 'var(--signal)') : 'transparent',
      color: active ? (light ? 'var(--bone)' : 'var(--signal-ink)') : (light ? 'rgba(20,17,13,0.55)' : 'rgba(245,239,227,0.55)'),
    }}>
      <Ic style={{ width: 20, height: 20 }} />
      <span className="m-mono" style={{ fontSize: 8, letterSpacing: '0.16em', textTransform: 'uppercase', fontWeight: 600 }}>{label}</span>
    </div>
  );
}

// ── T-01 Login ──────────────────────────────────────────────
function TLogin() {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)',
      display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative',
    }}>
      <div style={{ position: 'absolute', top: -180, right: -120, width: 460, height: 460, borderRadius: '50%', background: 'radial-gradient(circle, rgba(212,255,61,0.3), rgba(212,255,61,0) 60%)' }} />
      <div style={{ padding: '40px 48px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'relative' }}>
        <div className="m-display" style={{ fontSize: 28, color: 'var(--bone)' }}>Maestro<span style={{ color: 'var(--signal)' }}>.</span></div>
        <span className="m-mono" style={{ fontSize: 11, letterSpacing: '0.18em', color: 'rgba(245,239,227,0.5)' }}>v 1.0</span>
      </div>

      <div style={{ padding: '48px 64px 0', position: 'relative' }}>
        <TEyebrow color="var(--signal)">welcome back</TEyebrow>
        <div className="m-display" style={{ fontSize: 96, color: 'var(--bone)', marginTop: 18, lineHeight: 0.92 }}>
          Pick up<br/><span className="m-display-i">where</span> you<br/>left off.
        </div>
      </div>

      <div style={{ padding: '48px 64px 0', display: 'flex', flexDirection: 'column', gap: 14, position: 'relative' }}>
        <TField label="USERNAME" value="leo.romano" />
        <TField label="PASSWORD" value="••••••••••" trailing={<TI.eye style={{ width: 20, height: 20, color: 'rgba(245,239,227,0.55)' }} />} />
        <button className="m-btn m-btn-primary" style={{ marginTop: 10, padding: '20px 22px', fontSize: 16 }}>
          Log in <TI.arrow style={{ width: 20, height: 20 }} />
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '10px 0' }}>
          <div style={{ flex: 1, height: 1, background: 'var(--ink-line)' }} />
          <span className="m-mono" style={{ fontSize: 10, letterSpacing: '0.18em', color: 'rgba(245,239,227,0.5)' }}>OR</span>
          <div style={{ flex: 1, height: 1, background: 'var(--ink-line)' }} />
        </div>
        <button className="m-btn m-btn-ghost" style={{ color: 'var(--bone)', padding: '18px 22px', fontSize: 15 }}>
          Continue with school SSO
        </button>
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '0 64px 40px', position: 'relative', textAlign: 'center' }}>
        <span className="m-mono" style={{ fontSize: 12, color: 'rgba(245,239,227,0.45)', letterSpacing: '0.14em' }}>
          forgot password? · ask your school IT
        </span>
      </div>
    </div>
  );
}
function TField({ label, value, trailing }) {
  return (
    <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 20, padding: '16px 22px' }}>
      <div className="m-mono" style={{ fontSize: 10, letterSpacing: '0.18em', color: 'rgba(245,239,227,0.5)' }}>{label}</div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 6 }}>
        <div style={{ flex: 1, fontSize: 18, color: 'var(--bone)' }}>{value}</div>{trailing}
      </div>
    </div>
  );
}

// ── T-02a Welcome ───────────────────────────────────────────
function TOnbWelcome() {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--signal)', color: 'var(--signal-ink)',
      display: 'flex', flexDirection: 'column', overflow: 'hidden',
    }}>
      <div style={{ padding: '32px 48px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="m-display" style={{ fontSize: 24 }}>Maestro<span style={{ opacity: 0.4 }}>.</span></div>
        <button style={{ background: 'transparent', border: 0, color: 'var(--signal-ink)', fontWeight: 600, opacity: 0.65, fontSize: 14 }}>Skip ›</button>
      </div>

      <div style={{ padding: '0 48px 0', display: 'flex', gap: 8, marginBottom: 56 }}>
        {[1,2,3,4,5].map(i => (
          <div key={i} style={{ flex: 1, height: 4, borderRadius: 100, background: i === 1 ? 'var(--signal-ink)' : 'rgba(11,19,0,0.18)' }} />
        ))}
      </div>

      <div style={{ padding: '0 56px', flex: 1, display: 'flex', flexDirection: 'column' }}>
        <TEyebrow>step 1 of 5</TEyebrow>
        <div className="m-display" style={{ fontSize: 124, marginTop: 18, lineHeight: 0.92 }}>
          Let's find<br/><span className="m-display-i">how you</span><br/>learn best.
        </div>
        <div style={{ marginTop: 32, fontSize: 19, lineHeight: 1.45, opacity: 0.78, maxWidth: 560 }}>
          Not a graded test. Just a 5-minute vibe check so we can tune Maestro to <span style={{ fontFamily: 'var(--display)', fontStyle: 'italic' }}>your</span> brain. We'll show you the same idea four different ways.
        </div>

        <div style={{ marginTop: 40, display: 'flex', gap: 10 }}>
          {['Read','Listen','Watch','Try'].map((t, i) => (
            <div key={t} style={{
              padding: '12px 22px', border: '1.5px solid var(--signal-ink)', borderRadius: 100,
              fontSize: 15, fontWeight: 600,
              background: i === 3 ? 'var(--signal-ink)' : 'transparent',
              color: i === 3 ? 'var(--signal)' : 'var(--signal-ink)',
            }}>{t}</div>
          ))}
        </div>

        <div style={{ flex: 1 }} />
        <button className="m-btn" style={{ background: 'var(--signal-ink)', color: 'var(--signal)', alignSelf: 'flex-start', padding: '20px 36px', fontSize: 17, marginBottom: 48 }}>
          Let's go <TI.arrow style={{ width: 20, height: 20 }} />
        </button>
      </div>
    </div>
  );
}

// ── T-02b Modality quiz ─────────────────────────────────────
function TOnbQuiz() {
  const cards = [
    { l: 'Read',   Ic: TI.doc,   blurb: 'A short explainer text', state: 'open' },
    { l: 'Listen', Ic: TI.sound, blurb: '45-second audio clip',   state: 'idle' },
    { l: 'Watch',  Ic: TI.eye,   blurb: 'Diagram you can pan',    state: 'idle' },
    { l: 'Try',    Ic: TI.hand,  blurb: 'Tiny interactive task',  state: 'done' },
  ];
  return (
    <div className="maestro-screen" style={{ width: '100%', height: '100%', background: 'var(--ink)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <div style={{ padding: '32px 48px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="m-display" style={{ fontSize: 22, color: 'var(--bone)' }}>Maestro<span style={{ color: 'var(--signal)' }}>.</span></div>
        <button style={{ background: 'transparent', border: 0, color: 'rgba(245,239,227,0.55)', fontWeight: 600, fontSize: 14 }}>Skip ›</button>
      </div>
      <div style={{ padding: '0 48px 0', display: 'flex', gap: 8, marginBottom: 36 }}>
        {[1,2,3,4,5].map(i => (
          <div key={i} style={{ flex: 1, height: 4, borderRadius: 100, background: i <= 3 ? 'var(--signal)' : 'rgba(245,239,227,0.15)' }} />
        ))}
      </div>

      <div style={{ padding: '0 56px' }}>
        <TEyebrow color="var(--signal)">concept 3 / 4</TEyebrow>
        <div className="m-display" style={{ fontSize: 64, color: 'var(--bone)', marginTop: 12 }}>
          What's a <span className="m-display-i">variable</span>?
        </div>
        <div style={{ marginTop: 14, fontSize: 17, color: 'rgba(245,239,227,0.6)' }}>Pick the way you'd rather learn it.</div>
      </div>

      <div style={{ padding: '40px 48px 0', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {cards.map(c => {
          const active = c.state === 'open';
          const done = c.state === 'done';
          return (
            <div key={c.l} style={{
              background: active ? 'var(--bone)' : 'var(--ink-2)',
              color: active ? 'var(--ink)' : 'var(--bone)',
              border: '1px solid ' + (active ? 'var(--bone)' : 'var(--ink-line)'),
              borderRadius: 24, padding: 26, minHeight: 200, position: 'relative',
              display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
            }}>
              <c.Ic style={{ width: 28, height: 28 }} />
              <div>
                <div className="m-display" style={{ fontSize: 36 }}>{c.l}</div>
                <div style={{ marginTop: 4, fontSize: 13, opacity: 0.65 }}>{c.blurb}</div>
              </div>
              {done && <div style={{ position: 'absolute', top: 18, right: 18, width: 26, height: 26, borderRadius: 100, background: 'var(--green)', color: 'var(--ink)', display: 'grid', placeItems: 'center' }}><TI.check style={{ width: 14, height: 14 }} /></div>}
              {active && <div style={{ position: 'absolute', top: 18, right: 18, fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.18em', padding: '4px 9px', borderRadius: 100, background: 'var(--ink)', color: 'var(--signal)' }}>OPEN</div>}
            </div>
          );
        })}
      </div>

      <div style={{ padding: '28px 56px 0', display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: 'rgba(245,239,227,0.6)' }}>
        <TI.spark style={{ width: 14, height: 14, color: 'var(--signal)' }} />
        You spent <span style={{ color: 'var(--bone)' }}>42s</span> reading. Maestro is paying attention.
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '0 48px 48px', display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
        <button className="m-btn m-btn-ghost" style={{ color: 'var(--bone)' }}>Back</button>
        <button className="m-btn m-btn-primary">Next concept <TI.arrow style={{ width: 18, height: 18 }} /></button>
      </div>
    </div>
  );
}

// ── T-02c Result ────────────────────────────────────────────
function TOnbResult() {
  const axes = [
    { label: 'VISUAL', v: 0.85 }, { label: 'AUDITORY', v: 0.55 },
    { label: 'HANDS-ON', v: 0.78 }, { label: 'REFLECTIVE', v: 0.40 },
    { label: 'SOCIAL', v: 0.62 },
  ];
  const cx = 180, cy = 180, R = 130;
  const pts = axes.map((a, i) => {
    const an = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
    return [cx + Math.cos(an) * R * a.v, cy + Math.sin(an) * R * a.v];
  });
  return (
    <div className="maestro-screen" style={{ width: '100%', height: '100%', background: 'var(--ink)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <div style={{ padding: '32px 48px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="m-display" style={{ fontSize: 22, color: 'var(--bone)' }}>Maestro<span style={{ color: 'var(--signal)' }}>.</span></div>
        <span className="m-mono" style={{ fontSize: 11, letterSpacing: '0.18em', color: 'rgba(245,239,227,0.55)' }}>STEP 5 / 5</span>
      </div>

      <div style={{ padding: '12px 56px 0' }}>
        <TEyebrow color="var(--signal)">your shape</TEyebrow>
        <div className="m-display" style={{ fontSize: 72, color: 'var(--bone)', marginTop: 10 }}>
          You're a <span className="m-display-i">visual,</span><br/>hands-on type.
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', marginTop: 16 }}>
        <svg width="360" height="360" viewBox="0 0 360 360">
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
          {pts.map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r="4.5" fill="var(--signal)" />)}
          {axes.map((a, i) => {
            const an = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
            return <text key={i} x={cx + Math.cos(an) * (R + 22)} y={cy + Math.sin(an) * (R + 22)} fontFamily="JetBrains Mono" fontSize="11" letterSpacing="0.14em" fill="rgba(245,239,227,0.7)" textAnchor="middle" dominantBaseline="middle">{a.label}</text>;
          })}
        </svg>
      </div>

      <div style={{ padding: '12px 56px 0' }}>
        <TEyebrow>tune the tone</TEyebrow>
        <div style={{ display: 'flex', gap: 10, marginTop: 10 }}>
          {['Casual','Calm','Formal'].map((t, i) => (
            <div key={t} style={{ padding: '10px 18px', borderRadius: 100, border: '1px solid ' + (i === 0 ? 'var(--signal)' : 'var(--ink-line)'), background: i === 0 ? 'var(--signal)' : 'transparent', color: i === 0 ? 'var(--signal-ink)' : 'var(--bone)', fontSize: 13, fontWeight: 600 }}>{t}</div>
          ))}
          <div style={{ width: 24 }} />
          {['Short','Deep dive'].map((t, i) => (
            <div key={t} style={{ padding: '10px 18px', borderRadius: 100, border: '1px solid ' + (i === 0 ? 'var(--signal)' : 'var(--ink-line)'), background: i === 0 ? 'var(--signal)' : 'transparent', color: i === 0 ? 'var(--signal-ink)' : 'var(--bone)', fontSize: 13, fontWeight: 600 }}>{t}</div>
          ))}
        </div>
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '0 48px 48px', display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
        <button className="m-btn m-btn-ghost" style={{ color: 'var(--bone)' }}>Tweak manually</button>
        <button className="m-btn m-btn-primary">Looks like me <TI.check style={{ width: 18, height: 18 }} /></button>
      </div>
    </div>
  );
}

// ── T-03 Home ───────────────────────────────────────────────
function THome() {
  return (
    <TabletShell active="home">
      <div style={{ padding: '32px 40px 40px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
          <div>
            <div className="m-mono" style={{ fontSize: 11, letterSpacing: '0.18em', color: 'rgba(245,239,227,0.5)' }}>WED · 18 MAY</div>
            <div className="m-display" style={{ fontSize: 56, color: 'var(--bone)', marginTop: 6 }}>
              Hey <span className="m-display-i">Leo.</span>
            </div>
          </div>
          <button style={{ position: 'relative', background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 100, width: 48, height: 48, color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
            <TI.bell style={{ width: 20, height: 20 }} />
            <span style={{ position: 'absolute', top: 8, right: 8, width: 10, height: 10, borderRadius: 100, background: 'var(--signal)' }} />
          </button>
        </div>

        {/* streak */}
        <div style={{ marginTop: 18, padding: 18, background: 'var(--ink-2)', borderRadius: 18, border: '1px solid var(--ink-line)', display: 'flex', alignItems: 'center', gap: 16 }}>
          <TI.fire style={{ width: 28, height: 28, color: 'var(--orange)' }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 16, color: 'var(--bone)', fontWeight: 600 }}>12-day streak</div>
            <div className="m-mono" style={{ fontSize: 10, letterSpacing: '0.16em', color: 'rgba(245,239,227,0.5)', marginTop: 3 }}>3 MISSIONS · 86 XP THIS WEEK</div>
          </div>
          <div style={{ display: 'flex', gap: 4 }}>
            {[1,1,1,1,1,1,0].map((d, i) => (
              <div key={i} style={{ width: 8, height: 28, borderRadius: 2, background: d ? 'var(--signal)' : 'var(--ink-3)' }} />
            ))}
          </div>
        </div>

        {/* missions */}
        <div style={{ marginTop: 32, display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
          <TEyebrow>your missions</TEyebrow>
          <span style={{ fontSize: 12, color: 'rgba(245,239,227,0.55)' }}>2 open</span>
        </div>
        <div style={{ marginTop: 14, display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 14 }}>
          <TMissionCard state="lacuna" tag="OPEN GAP" sym="✕" title="SQL JOIN" sub="From PHP test · 12 May" cta="Start mission" big />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <TMissionCard state="recovery" tag="IN RECOVERY" sym="↑" title="PHP sessions" sub="Step 2 of 4" cta="Continue" />
            <TMissionCard state="consolidate" tag="REVIEW" sym="◷" title="Arrays" sub="Final quiz" cta="Quiz me" />
          </div>
        </div>

        {/* map preview */}
        <div style={{ marginTop: 32 }}>
          <TEyebrow>your map</TEyebrow>
          <div style={{ marginTop: 12, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 20, padding: 22 }}>
            <div style={{ height: 180 }}><TMiniMap /></div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 14, alignItems: 'center' }}>
              <div style={{ display: 'flex', gap: 20, fontSize: 13, color: 'rgba(245,239,227,0.7)' }}>
                <span><span className="m-dot" style={{ background: 'var(--green)' }} /> 12 solid</span>
                <span><span className="m-dot" style={{ background: 'var(--yellow)' }} /> 4 to review</span>
                <span><span className="m-dot" style={{ background: 'var(--orange)' }} /> 1 recovering</span>
                <span><span className="m-dot" style={{ background: 'var(--red)' }} /> 1 gap</span>
              </div>
              <span style={{ fontSize: 13, color: 'var(--signal)', fontWeight: 600 }}>See full map →</span>
            </div>
          </div>
        </div>
      </div>
    </TabletShell>
  );
}
function TMissionCard({ state, tag, sym, title, sub, cta, big }) {
  const c = {
    lacuna: { bg: 'var(--bone)', fg: 'var(--ink)', pill: 'm-pill-red' },
    recovery: { bg: 'var(--ink-2)', fg: 'var(--bone)', pill: 'm-pill-orange' },
    consolidate: { bg: 'var(--ink-2)', fg: 'var(--bone)', pill: 'm-pill-yellow' },
  }[state];
  return (
    <div style={{
      background: c.bg, color: c.fg, borderRadius: 22, padding: 22,
      border: state === 'lacuna' ? '1px solid var(--ink)' : '1px solid var(--ink-line)',
      display: 'flex', flexDirection: 'column', minHeight: big ? 220 : 130,
    }}>
      <div className={'m-pill ' + c.pill} style={{ alignSelf: 'flex-start' }}>
        <span style={{ fontSize: 10 }}>{sym}</span> {tag}
      </div>
      <div className="m-display" style={{ fontSize: big ? 44 : 26, marginTop: 14 }}>{title}</div>
      <div style={{ fontSize: 13, opacity: 0.6, marginTop: 4 }}>{sub}</div>
      <div style={{ flex: 1 }} />
      <button style={{
        marginTop: 14, alignSelf: 'flex-start',
        background: state === 'lacuna' ? 'var(--ink)' : 'var(--signal)',
        color: state === 'lacuna' ? 'var(--bone)' : 'var(--signal-ink)',
        border: 0, borderRadius: 100, padding: '12px 18px', fontSize: 13, fontWeight: 600,
        display: 'inline-flex', alignItems: 'center', gap: 8,
      }}>{cta} <TI.arrow style={{ width: 14, height: 14 }} /></button>
    </div>
  );
}
function TMiniMap() {
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
        <line key={i} x1={nodes[a].x} y1={nodes[a].y} x2={nodes[b].x} y2={nodes[b].y} stroke="rgba(245,239,227,0.18)" strokeWidth="1" />
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

// ── T-04 Map ────────────────────────────────────────────────
function TMap() {
  return (
    <TabletShell active="map">
      <div style={{ padding: '24px 32px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
        <button style={{ width: 44, height: 44, borderRadius: 100, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
          <TI.back style={{ width: 18, height: 18 }} />
        </button>
        <div style={{ flex: 1 }}>
          <TEyebrow>informatics · 3ai</TEyebrow>
          <div className="m-display" style={{ fontSize: 32, color: 'var(--bone)' }}>Your map</div>
        </div>
        <div style={{ display: 'flex', background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 100, padding: 4 }}>
          <div style={{ padding: '8px 14px', background: 'var(--bone)', color: 'var(--ink)', borderRadius: 100, fontSize: 12, fontWeight: 600 }}>Macro</div>
          <div style={{ padding: '8px 14px', color: 'rgba(245,239,227,0.6)', fontSize: 12 }}>Micro</div>
        </div>
      </div>

      <div style={{ position: 'relative', height: 'calc(100% - 96px)', overflow: 'hidden', background: 'radial-gradient(circle at 30% 30%, rgba(212,255,61,0.06), rgba(0,0,0,0) 50%)' }}>
        <svg width="100%" height="100%" style={{ position: 'absolute', inset: 0 }}>
          <defs>
            <pattern id="gridT" width="28" height="28" patternUnits="userSpaceOnUse">
              <path d="M28 0H0V28" fill="none" stroke="rgba(245,239,227,0.04)" strokeWidth="1" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#gridT)" />
        </svg>
        <TFullMap />

        <div style={{ position: 'absolute', right: 20, top: 20, display: 'flex', flexDirection: 'column', gap: 6 }}>
          <div style={{ width: 40, height: 40, borderRadius: 12, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', display: 'grid', placeItems: 'center', color: 'var(--bone)', fontSize: 20 }}>+</div>
          <div style={{ width: 40, height: 40, borderRadius: 12, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', display: 'grid', placeItems: 'center', color: 'var(--bone)', fontSize: 20 }}>−</div>
        </div>

        <div style={{ position: 'absolute', left: 20, bottom: 20, right: 20,
          background: 'rgba(28,24,19,0.92)', backdropFilter: 'blur(10px)',
          border: '1px solid var(--ink-line)', borderRadius: 18, padding: '14px 18px',
        }}>
          <TEyebrow>legend</TEyebrow>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 10, fontSize: 11, color: 'rgba(245,239,227,0.85)', marginTop: 8 }}>
            <TLeg color="var(--green)" sym="✓" label="Solid" />
            <TLeg color="var(--yellow)" sym="◷" label="To review" />
            <TLeg color="var(--orange)" sym="↑" label="Recovering" />
            <TLeg color="var(--red)" sym="✕" label="Gap" />
            <TLeg color="var(--white-st)" sym="○" label="Seen" />
            <TLeg color="var(--gray)" sym="·" label="New" />
          </div>
        </div>
      </div>
    </TabletShell>
  );
}
function TLeg({ color, sym, label }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <span style={{ width: 18, height: 18, borderRadius: 100, background: color, color: 'var(--ink)', display: 'grid', placeItems: 'center', fontSize: 10, fontWeight: 700 }}>{sym}</span>
      <span>{label}</span>
    </div>
  );
}
function TFullMap() {
  const nodes = [
    { id: 'fund', label: 'Fundamentals', x: 320, y: 80, s: 'green', big: true },
    { id: 'vars', label: 'Variables',   x: 160, y: 200, s: 'green' },
    { id: 'ctrl', label: 'Control flow', x: 320, y: 200, s: 'green' },
    { id: 'arr',  label: 'Arrays',       x: 480, y: 200, s: 'yellow' },
    { id: 'fn',   label: 'Functions',    x: 160, y: 340, s: 'green' },
    { id: 'oop',  label: 'OOP basics',   x: 320, y: 340, s: 'yellow' },
    { id: 'php',  label: 'PHP sessions', x: 480, y: 340, s: 'orange', current: true },
    { id: 'sql',  label: 'SQL JOIN',     x: 320, y: 480, s: 'red', current: true },
    { id: 'pat',  label: 'Patterns',     x: 160, y: 480, s: 'gray' },
    { id: 'mvc',  label: 'MVC',          x: 480, y: 480, s: 'gray' },
  ];
  const cm = { green: '#4ADE80', yellow: '#F5C53D', orange: '#FF8A3D', red: '#E74C3C', gray: '#8A8275' };
  const sm = { green: '✓', yellow: '◷', orange: '↑', red: '✕', gray: '' };
  const edges = [['fund','vars'],['fund','ctrl'],['fund','arr'],['vars','fn'],['ctrl','oop'],['arr','php'],['fn','pat'],['oop','sql'],['php','sql'],['php','mvc']];
  const nm = Object.fromEntries(nodes.map(n => [n.id, n]));
  return (
    <svg viewBox="0 0 640 560" style={{ width: '100%', height: '100%' }} preserveAspectRatio="xMidYMid meet">
      {edges.map(([a,b], i) => (
        <line key={i} x1={nm[a].x} y1={nm[a].y} x2={nm[b].x} y2={nm[b].y} stroke="rgba(245,239,227,0.22)" strokeWidth="1.4" />
      ))}
      {nodes.map(n => {
        const r = n.big ? 32 : 28;
        return (
          <g key={n.id}>
            {n.current && <circle cx={n.x} cy={n.y} r={r + 7} fill="none" stroke="var(--signal)" strokeWidth="2.5" opacity="0.65" />}
            <circle cx={n.x} cy={n.y} r={r} fill={cm[n.s]} stroke="var(--ink)" strokeWidth="3.5" />
            <text x={n.x} y={n.y + 6} fontSize="16" textAnchor="middle" fill="var(--ink)" fontWeight="700">{sm[n.s]}</text>
            <text x={n.x} y={n.y + r + 20} fontSize="13" textAnchor="middle" fill="rgba(245,239,227,0.9)" style={{ fontFamily: 'Geist, sans-serif' }}>{n.label}</text>
          </g>
        );
      })}
    </svg>
  );
}

// ── T-05 Node detail ────────────────────────────────────────
function TNodeDetail() {
  return (
    <TabletShell active="map">
      <div style={{ padding: '24px 40px 0', display: 'flex', alignItems: 'center', gap: 12 }}>
        <button style={{ width: 44, height: 44, borderRadius: 100, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
          <TI.back style={{ width: 18, height: 18 }} />
        </button>
        <span style={{ fontSize: 13, color: 'rgba(245,239,227,0.55)' }}>Map / Database / <span style={{ color: 'var(--bone)' }}>SQL JOIN</span></span>
      </div>

      <div style={{ padding: '18px 40px 0' }}>
        <div className="m-pill m-pill-red" style={{ marginBottom: 14 }}>
          <span>✕</span> OPEN GAP · 5 DAYS
        </div>
        <div className="m-display" style={{ fontSize: 72, color: 'var(--bone)', lineHeight: 0.95 }}>
          SQL <span className="m-display-i">JOIN.</span>
        </div>
        <div style={{ marginTop: 10, fontSize: 15, color: 'rgba(245,239,227,0.65)', maxWidth: 520 }}>
          Combining rows from two or more tables based on a related column.
        </div>
      </div>

      <div style={{ margin: '24px 40px 0', padding: 22, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 20, display: 'flex', alignItems: 'center', gap: 20 }}>
        <div style={{ width: 80, height: 80, borderRadius: 100, background: 'var(--red)', color: '#fff', display: 'grid', placeItems: 'center', fontSize: 32, fontWeight: 700, boxShadow: '0 0 0 8px rgba(231,76,60,0.18)' }}>✕</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 18, color: 'var(--bone)', fontWeight: 600 }}>Gap detected</div>
          <div style={{ fontSize: 13, color: 'rgba(245,239,227,0.6)', marginTop: 4 }}>From your PHP test on 12 May. Don't sweat it — we have a 4-step path.</div>
          <div className="m-mono" style={{ fontSize: 10, color: 'rgba(245,239,227,0.4)', marginTop: 6, letterSpacing: '0.14em' }}>UPDATED 12.05 · 14:22</div>
        </div>
      </div>

      <div style={{ padding: '28px 40px 0', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div>
          <TEyebrow>history</TEyebrow>
          <div style={{ marginTop: 12, position: 'relative', paddingLeft: 20 }}>
            <div style={{ position: 'absolute', left: 6, top: 8, bottom: 8, width: 1, background: 'var(--ink-line)' }} />
            {[
              { d: '12 MAY', s: 'red', t: 'Gap', f: 'PHP test — 2/10' },
              { d: '08 MAY', s: 'yellow', t: 'To review', f: 'Quiz — 7/10' },
              { d: '02 MAY', s: 'green', t: 'Solid', f: 'Override · Prof.' },
              { d: '20 APR', s: 'white-st', t: 'Introduced', f: 'Lesson 14' },
            ].map((it, i) => (
              <div key={i} style={{ position: 'relative', paddingBottom: 14 }}>
                <span style={{ position: 'absolute', left: -20, top: 4, width: 13, height: 13, borderRadius: 100, background: 'var(--' + it.s + ')', border: '2px solid var(--ink)' }} />
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 13, color: 'var(--bone)', fontWeight: 600 }}>{it.t}</span>
                  <span className="m-mono" style={{ fontSize: 9, letterSpacing: '0.14em', color: 'rgba(245,239,227,0.45)' }}>{it.d}</span>
                </div>
                <div style={{ fontSize: 12, color: 'rgba(245,239,227,0.55)' }}>{it.f}</div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <TEyebrow>materials</TEyebrow>
          <div style={{ marginTop: 12, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 16, padding: '8px 16px' }}>
            {[['Personalised doc', TI.doc],['Lesson clip · 02:14', TI.video],['Practice set', TI.pencil]].map(([t, Ic], i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 0', borderTop: i === 0 ? 0 : '1px solid var(--ink-3)' }}>
                <Ic style={{ width: 18, height: 18, color: 'rgba(245,239,227,0.7)' }} />
                <span style={{ flex: 1, fontSize: 14 }}>{t}</span>
                <TI.arrow style={{ width: 14, height: 14, opacity: 0.6 }} />
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{ padding: '32px 40px 40px' }}>
        <button className="m-btn m-btn-primary" style={{ width: '100%', padding: '20px 22px', fontSize: 16 }}>
          Start mission · 4 steps <TI.arrow style={{ width: 20, height: 20 }} />
        </button>
      </div>
    </TabletShell>
  );
}

// ── T-06 Mission ────────────────────────────────────────────
function TMission() {
  const steps = [
    { Ic: TI.doc,    title: 'Read the explainer', sub: '2 min · personalised to you', state: 'done' },
    { Ic: TI.video,  title: 'Watch the lesson clip', sub: '02:14 · Prof. Russo · lesson 18', state: 'current' },
    { Ic: TI.hand,   title: 'Try a guided exercise', sub: '3 steps · drag & drop', state: 'todo' },
    { Ic: TI.pencil, title: 'Closing quiz', sub: '5 questions · check what stuck', state: 'todo' },
  ];
  return (
    <TabletShell active="home">
      <div style={{ padding: '24px 40px 0', display: 'flex', alignItems: 'center', gap: 12 }}>
        <button style={{ width: 44, height: 44, borderRadius: 100, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
          <TI.back style={{ width: 18, height: 18 }} />
        </button>
        <TEyebrow>mission · step 2 / 4</TEyebrow>
      </div>

      <div style={{ padding: '20px 40px 0' }}>
        <div className="m-display" style={{ fontSize: 64, color: 'var(--bone)', lineHeight: 0.95 }}>
          Mission: <span className="m-display-i">SQL JOIN.</span>
        </div>
        <div style={{ marginTop: 10, fontSize: 15, color: 'rgba(245,239,227,0.6)' }}>
          A short path tuned to how you learn. Take it at your pace.
        </div>
        <div style={{ marginTop: 20, display: 'flex', gap: 6 }}>
          {[1,1,0,0].map((d, i) => (
            <div key={i} style={{ flex: 1, height: 8, borderRadius: 100, background: d ? 'var(--signal)' : 'var(--ink-3)' }} />
          ))}
        </div>
      </div>

      <div style={{ padding: '32px 40px 0', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {steps.map((s, i) => <TStepRow key={i} idx={i} step={s} />)}
      </div>

      <div style={{ padding: '32px 40px 40px' }}>
        <button className="m-btn m-btn-primary" style={{ width: '100%', padding: '20px 22px', fontSize: 16 }}>
          Continue · watch clip <TI.arrow style={{ width: 20, height: 20 }} />
        </button>
      </div>
    </TabletShell>
  );
}
function TStepRow({ step, idx }) {
  const isDone = step.state === 'done';
  const isCurrent = step.state === 'current';
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 16, padding: '18px 20px',
      borderRadius: 18,
      background: isCurrent ? 'var(--bone)' : 'var(--ink-2)',
      color: isCurrent ? 'var(--ink)' : 'var(--bone)',
      border: '1px solid ' + (isCurrent ? 'var(--bone)' : 'var(--ink-line)'),
      opacity: step.state === 'todo' ? 0.55 : 1,
    }}>
      <div style={{ width: 48, height: 48, borderRadius: 14, flex: 'none', background: isDone ? 'var(--green)' : isCurrent ? 'var(--ink)' : 'var(--ink-3)', color: isDone ? 'var(--ink)' : isCurrent ? 'var(--signal)' : 'var(--bone)', display: 'grid', placeItems: 'center' }}>
        {isDone ? <TI.check style={{ width: 22, height: 22 }} /> : <step.Ic style={{ width: 22, height: 22 }} />}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 16, fontWeight: 600 }}>{step.title}</div>
        <div style={{ fontSize: 13, opacity: 0.6, marginTop: 2 }}>{step.sub}</div>
      </div>
      {isCurrent && <TI.play style={{ width: 20, height: 20 }} />}
      <span className="m-mono" style={{ fontSize: 10, opacity: 0.4, letterSpacing: '0.14em' }}>0{idx + 1} / 04</span>
    </div>
  );
}

// ── T-07a Quiz question (light) ─────────────────────────────
function TQuizQ() {
  const opts = [
    { l: 'A', t: 'INNER JOIN returns only rows where the key exists in both tables.', state: 'selected' },
    { l: 'B', t: 'INNER JOIN returns all rows from the left table.', state: 'idle' },
    { l: 'C', t: 'INNER JOIN merges columns regardless of keys.', state: 'idle' },
    { l: 'D', t: 'INNER JOIN is the same as UNION.', state: 'idle' },
  ];
  return (
    <div className="maestro-screen light" style={{ width: '100%', height: '100%', background: 'var(--bone)', color: 'var(--ink)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <div style={{ padding: '24px 40px', display: 'flex', alignItems: 'center', gap: 14 }}>
        <button style={{ width: 44, height: 44, borderRadius: 100, background: 'transparent', border: '1px solid rgba(20,17,13,0.18)', color: 'var(--ink)', display: 'grid', placeItems: 'center' }}>
          <TI.x style={{ width: 18, height: 18 }} />
        </button>
        <div style={{ flex: 1, display: 'flex', gap: 5 }}>
          {[1,1,1,0,0].map((d, i) => (
            <div key={i} style={{ flex: 1, height: 7, borderRadius: 100, background: d ? 'var(--ink)' : 'rgba(20,17,13,0.12)' }} />
          ))}
        </div>
        <span className="m-mono" style={{ fontSize: 12, opacity: 0.6, letterSpacing: '0.14em' }}>03 / 05</span>
      </div>

      <div style={{ padding: '24px 56px 0' }}>
        <TEyebrow>quiz · sql join</TEyebrow>
        <div className="m-display" style={{ fontSize: 56, color: 'var(--ink)', marginTop: 10, lineHeight: 0.98 }}>
          What does an<br/><span className="m-display-i">INNER JOIN</span> do?
        </div>
      </div>

      <div style={{ padding: '32px 40px 0', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {opts.map(o => {
          const sel = o.state === 'selected';
          return (
            <div key={o.l} style={{
              display: 'flex', alignItems: 'center', gap: 14, padding: '18px 22px',
              background: sel ? 'var(--ink)' : '#fff',
              color: sel ? 'var(--bone)' : 'var(--ink)',
              border: '1px solid ' + (sel ? 'var(--ink)' : 'rgba(20,17,13,0.12)'),
              borderRadius: 18,
            }}>
              <div style={{
                width: 36, height: 36, borderRadius: 100, flex: 'none',
                background: sel ? 'var(--signal)' : 'transparent',
                color: sel ? 'var(--signal-ink)' : 'var(--ink)',
                border: sel ? '0' : '1px solid rgba(20,17,13,0.25)',
                display: 'grid', placeItems: 'center', fontSize: 14, fontWeight: 700, fontFamily: 'var(--mono)',
              }}>{o.l}</div>
              <div style={{ flex: 1, fontSize: 15, lineHeight: 1.4 }}>{o.t}</div>
            </div>
          );
        })}
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '0 40px 40px' }}>
        <button className="m-btn" style={{ width: '100%', background: 'var(--ink)', color: 'var(--bone)', padding: '20px 22px', fontSize: 16 }}>
          Confirm <TI.arrow style={{ width: 20, height: 20 }} />
        </button>
      </div>
    </div>
  );
}

// ── T-07b Quiz result ───────────────────────────────────────
function TQuizR() {
  return (
    <div className="maestro-screen" style={{ width: '100%', height: '100%', background: 'var(--ink)', display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative' }}>
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(circle at 50% 20%, rgba(74,222,128,0.16), rgba(0,0,0,0) 55%)', pointerEvents: 'none' }} />
      <div style={{ padding: '24px 40px 0', display: 'flex', justifyContent: 'flex-end' }}>
        <button style={{ width: 44, height: 44, borderRadius: 100, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
          <TI.x style={{ width: 18, height: 18 }} />
        </button>
      </div>

      <div style={{ padding: '32px 40px 0', textAlign: 'center', position: 'relative' }}>
        <TI.spark style={{ width: 36, height: 36, color: 'var(--signal)', marginBottom: 14 }} />
        <TEyebrow color="var(--green)">nailed it</TEyebrow>
        <div className="m-display" style={{ fontSize: 120, color: 'var(--bone)', marginTop: 8, lineHeight: 0.95 }}>
          4<span className="m-display-i" style={{ color: 'var(--signal)' }}>/</span>5
        </div>
        <div style={{ marginTop: 8, fontSize: 14, color: 'rgba(245,239,227,0.55)' }}>That's 80% · keep this in your head</div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', marginTop: 22 }}>
        <div className="m-pill m-pill-yellow" style={{ padding: '6px 14px', fontSize: 13 }}>
          <span>◷</span> SQL JOIN moved to "TO REVIEW"
        </div>
      </div>

      <div style={{ padding: '32px 40px 0' }}>
        <TEyebrow>by question</TEyebrow>
        <div style={{ marginTop: 12, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          {[
            { n: 1, ok: true,  q: 'What is a relation?' },
            { n: 2, ok: true,  q: 'INNER vs LEFT JOIN' },
            { n: 3, ok: true,  q: 'JOIN on multiple keys' },
            { n: 4, ok: false, q: 'Self-join example' },
            { n: 5, ok: true,  q: 'Result table semantics' },
          ].map(r => (
            <div key={r.n} style={{
              display: 'flex', alignItems: 'center', gap: 12,
              background: 'var(--ink-2)', border: '1px solid var(--ink-line)',
              borderRadius: 14, padding: '12px 14px',
            }}>
              <span style={{ width: 28, height: 28, borderRadius: 100, flex: 'none', background: r.ok ? 'var(--green)' : 'var(--orange)', color: 'var(--ink)', display: 'grid', placeItems: 'center' }}>
                {r.ok ? <TI.check style={{ width: 14, height: 14 }} /> : <TI.x style={{ width: 14, height: 14 }} />}
              </span>
              <span className="m-mono" style={{ fontSize: 10, color: 'rgba(245,239,227,0.55)', letterSpacing: '0.14em' }}>Q0{r.n}</span>
              <span style={{ flex: 1, fontSize: 13, color: 'var(--bone)' }}>{r.q}</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '0 40px 40px', display: 'flex', gap: 12 }}>
        <button className="m-btn m-btn-ghost" style={{ color: 'var(--bone)', flex: 1, padding: '18px 20px', fontSize: 15 }}>
          Try a fresh angle
        </button>
        <button className="m-btn m-btn-primary" style={{ flex: 1, padding: '18px 20px', fontSize: 15 }}>
          Back to your map <TI.arrow style={{ width: 18, height: 18 }} />
        </button>
      </div>
    </div>
  );
}

// ── T-08 Document ───────────────────────────────────────────
function TDocument() {
  return (
    <div className="maestro-screen light" style={{ width: '100%', height: '100%', background: 'var(--paper)', color: 'var(--ink)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <div style={{ padding: '24px 40px 0', display: 'flex', alignItems: 'center', gap: 12 }}>
        <button style={{ width: 44, height: 44, borderRadius: 100, background: 'transparent', border: '1px solid rgba(20,17,13,0.15)', color: 'var(--ink)', display: 'grid', placeItems: 'center' }}>
          <TI.back style={{ width: 18, height: 18 }} />
        </button>
        <span style={{ fontSize: 13, color: 'rgba(20,17,13,0.55)' }}>Mission · Step 1</span>
        <div style={{ flex: 1 }} />
        <button style={{ background: 'transparent', border: '1px solid rgba(20,17,13,0.15)', borderRadius: 100, padding: '9px 14px', fontSize: 12, fontWeight: 600, color: 'var(--ink)', display: 'inline-flex', gap: 6, alignItems: 'center' }}>
          <TI.spark style={{ width: 14, height: 14 }} /> Why this?
        </button>
      </div>

      <div style={{ padding: '20px 56px 0' }}>
        <TEyebrow>review · made for you</TEyebrow>
        <div className="m-display" style={{ fontSize: 64, color: 'var(--ink)', marginTop: 8, lineHeight: 0.95 }}>
          PHP <span className="m-display-i">sessions.</span>
        </div>
        <div style={{ marginTop: 8, fontSize: 14, color: 'rgba(20,17,13,0.55)' }}>3 min read · with a basketball analogy, like you wanted</div>
      </div>

      <div style={{ padding: '28px 40px 0', display: 'flex', flexDirection: 'column', gap: 14, overflow: 'auto' }}>
        <TBlock tag="WHERE YOU SLIPPED" tone="yellow" label="ERROR">
          <pre style={tPre}>{`<?php
  session_start();
  $_SESSION['user'] = $name;
?>
<html>
  <body>...`}</pre>
          <div style={{ fontSize: 13, color: 'rgba(20,17,13,0.7)', marginTop: 10 }}>
            You opened the session <em>after</em> some output. Spot it?
          </div>
        </TBlock>
        <TBlock tag="THE BASKETBALL VERSION" tone="ink">
          <div style={{ fontSize: 15, color: 'var(--ink)', lineHeight: 1.5 }}>
            A session is like checking in at the gym desk. If you walk onto the court first, the desk can't log you in anymore — the game's already started.
          </div>
        </TBlock>
        <TBlock tag="HOW IT WORKS RIGHT" tone="green" label="CORRECT">
          <pre style={tPre}>{`<?php
  session_start();   // first thing
?>
<html>
  <body>
    Hello <?= $_SESSION['user'] ?>`}</pre>
        </TBlock>
        <TBlock tag="REMEMBER THIS" tone="signal">
          <div style={{ fontSize: 16, color: 'var(--ink)', fontWeight: 600, lineHeight: 1.4 }}>
            <span className="m-display-i" style={{ fontSize: 22 }}>session_start()</span> must be the very first thing — before any output.
          </div>
        </TBlock>
      </div>

      <div style={{ padding: '20px 40px 40px', display: 'flex', gap: 12 }}>
        <button style={{ padding: '16px 22px', borderRadius: 100, background: '#fff', border: '1px solid rgba(20,17,13,0.15)', color: 'var(--ink)', fontWeight: 600, fontSize: 14, display: 'inline-flex', alignItems: 'center', gap: 8 }}>
          <TI.sound style={{ width: 16, height: 16 }} /> Listen
        </button>
        <button className="m-btn" style={{ flex: 1, background: 'var(--ink)', color: 'var(--bone)' }}>
          Try it <TI.arrow style={{ width: 18, height: 18 }} />
        </button>
      </div>
    </div>
  );
}
const tPre = { margin: 0, padding: '12px 14px', background: 'rgba(20,17,13,0.06)', borderRadius: 10, fontFamily: 'var(--mono)', fontSize: 12.5, lineHeight: 1.55, color: 'var(--ink)', whiteSpace: 'pre-wrap' };
function TBlock({ tag, tone, label, children }) {
  const tones = {
    yellow: { bg: 'rgba(245,197,61,0.18)', stripe: 'var(--yellow)', tag: 'rgba(120,90,10,1)' },
    green:  { bg: 'rgba(74,222,128,0.18)', stripe: 'var(--green)', tag: 'rgba(20,90,40,1)' },
    ink:    { bg: '#fff', stripe: 'var(--ink)', tag: 'rgba(20,17,13,0.65)' },
    signal: { bg: 'var(--signal)', stripe: 'var(--signal-ink)', tag: 'var(--signal-ink)' },
  }[tone];
  return (
    <div style={{ background: tones.bg, borderRadius: 18, padding: '14px 18px 16px', borderLeft: `5px solid ${tones.stripe}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span className="m-mono" style={{ fontSize: 10, letterSpacing: '0.18em', color: tones.tag }}>{tag}</span>
        {label && <span className="m-mono" style={{ fontSize: 9, letterSpacing: '0.18em', padding: '3px 8px', borderRadius: 100, background: tones.stripe, color: tone === 'signal' ? 'var(--signal)' : '#fff' }}>{label}</span>}
      </div>
      {children}
    </div>
  );
}

// ── T-09 Profile ────────────────────────────────────────────
function TProfile() {
  return (
    <TabletShell active="profile">
      <div style={{ padding: '24px 40px 0', display: 'flex', alignItems: 'center', gap: 12 }}>
        <button style={{ width: 44, height: 44, borderRadius: 100, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
          <TI.back style={{ width: 18, height: 18 }} />
        </button>
        <div>
          <TEyebrow>your setup</TEyebrow>
          <div className="m-display" style={{ fontSize: 32, color: 'var(--bone)' }}>Profile</div>
        </div>
      </div>

      <div style={{ padding: '20px 40px 0', display: 'flex', alignItems: 'center', gap: 18 }}>
        <div style={{ width: 72, height: 72, borderRadius: 22, background: 'var(--signal)', color: 'var(--signal-ink)', display: 'grid', placeItems: 'center', fontFamily: 'var(--display)', fontSize: 38 }}>L</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 22, color: 'var(--bone)', fontWeight: 600 }}>Leo Romano</div>
          <div style={{ fontSize: 13, color: 'rgba(245,239,227,0.6)' }}>3AI · Informatics · 17 nodes solid</div>
        </div>
      </div>

      <div style={{ padding: '28px 40px 0', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 20, padding: 22 }}>
          <TEyebrow>how I learn</TEyebrow>
          <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 16 }}>
            <TMiniRadar />
            <div style={{ flex: 1, fontSize: 13, color: 'rgba(245,239,227,0.7)', lineHeight: 1.45 }}>
              You're a <span style={{ color: 'var(--signal)', fontWeight: 600 }}>visual + hands-on</span> type. Diagrams and tiny experiments.
            </div>
          </div>
        </div>

        <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 20, padding: 22 }}>
          <TEyebrow>tone & length</TEyebrow>
          <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div style={{ display: 'flex', background: 'var(--ink-3)', border: '1px solid var(--ink-line)', borderRadius: 100, padding: 3 }}>
              {['Casual','Calm','Formal'].map((t, i) => (
                <div key={t} style={{ flex: 1, textAlign: 'center', padding: '8px 10px', background: i === 0 ? 'var(--bone)' : 'transparent', color: i === 0 ? 'var(--ink)' : 'rgba(245,239,227,0.6)', borderRadius: 100, fontSize: 12, fontWeight: 600 }}>{t}</div>
              ))}
            </div>
            <div style={{ display: 'flex', background: 'var(--ink-3)', border: '1px solid var(--ink-line)', borderRadius: 100, padding: 3 }}>
              {['Short','Deep dive'].map((t, i) => (
                <div key={t} style={{ flex: 1, textAlign: 'center', padding: '8px 10px', background: i === 0 ? 'var(--bone)' : 'transparent', color: i === 0 ? 'var(--ink)' : 'rgba(245,239,227,0.6)', borderRadius: 100, fontSize: 12, fontWeight: 600 }}>{t}</div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div style={{ padding: '16px 40px 0' }}>
        <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 20, padding: 22 }}>
          <TEyebrow>accessibility</TEyebrow>
          <div style={{ marginTop: 14, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18 }}>
            <TRow label="Font" right={<span style={{ color: 'var(--signal)', fontWeight: 600 }}>Geist</span>} />
            <TRow label="Text size" right={<span style={{ color: 'var(--signal)', fontWeight: 600 }}>17 pt</span>} />
            <TRow label="Theme" right={
              <div style={{ display: 'flex', gap: 4, fontSize: 11 }}>
                {['Light','Dark','Sepia'].map((t, i) => (
                  <div key={t} style={{ padding: '4px 10px', borderRadius: 100, background: i === 1 ? 'var(--bone)' : 'transparent', color: i === 1 ? 'var(--ink)' : 'rgba(245,239,227,0.55)', fontWeight: 600 }}>{t}</div>
                ))}
              </div>
            } />
            <TRow label="High contrast" right={<TToggle on={false} />} />
          </div>
        </div>
      </div>

      <div style={{ padding: '24px 40px 40px' }}>
        <button className="m-btn m-btn-primary" style={{ width: '100%', padding: '18px', fontSize: 15 }}>
          Save changes <TI.check style={{ width: 18, height: 18 }} />
        </button>
      </div>
    </TabletShell>
  );
}
function TRow({ label, right }) { return <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 14, color: 'var(--bone)' }}>{label}<div>{right}</div></div>; }
function TToggle({ on }) {
  return <div style={{ width: 44, height: 26, borderRadius: 100, background: on ? 'var(--signal)' : 'var(--ink-3)', position: 'relative', border: '1px solid var(--ink-line)' }}>
    <div style={{ position: 'absolute', top: 2, left: on ? 20 : 2, width: 20, height: 20, borderRadius: 100, background: '#fff' }} />
  </div>;
}
function TMiniRadar() {
  const axes = [0.85, 0.55, 0.78, 0.40, 0.62];
  const cx = 45, cy = 45, R = 36;
  const pts = axes.map((v, i) => {
    const a = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
    return [cx + Math.cos(a) * R * v, cy + Math.sin(a) * R * v];
  });
  return (
    <svg width="90" height="90" viewBox="0 0 90 90">
      <polygon points={axes.map((_, i) => {
        const a = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
        return [cx + Math.cos(a) * R, cy + Math.sin(a) * R].join(',');
      }).join(' ')} fill="none" stroke="rgba(245,239,227,0.12)" />
      <polygon points={pts.map(p => p.join(',')).join(' ')} fill="rgba(212,255,61,0.25)" stroke="var(--signal)" strokeWidth="1.5" />
    </svg>
  );
}

// ── T-10 Why this? (bottom sheet) ───────────────────────────
function TExplain() {
  return (
    <div className="maestro-screen" style={{ width: '100%', height: '100%', background: 'var(--ink)', display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative' }}>
      <div style={{ position: 'absolute', inset: 0, background: 'var(--paper)', opacity: 0.06 }} />
      <div style={{ flex: 1, position: 'relative' }}>
        <div style={{
          position: 'absolute', left: 20, right: 20, bottom: 20, top: 120,
          background: 'var(--ink-2)', borderRadius: 32, border: '1px solid var(--ink-line)',
          boxShadow: '0 -30px 100px rgba(0,0,0,0.7)',
          padding: '18px 36px 36px', display: 'flex', flexDirection: 'column',
        }}>
          <div style={{ width: 48, height: 4, borderRadius: 100, background: 'var(--ink-3)', margin: '4px auto 18px' }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <TI.spark style={{ width: 22, height: 22, color: 'var(--signal)' }} />
            <TEyebrow color="var(--signal)">maestro reasoning</TEyebrow>
          </div>
          <div className="m-display" style={{ fontSize: 56, color: 'var(--bone)', lineHeight: 0.95 }}>
            Why am I<br/>showing you <span className="m-display-i">this</span>?
          </div>

          <div style={{ marginTop: 28, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
            <div>
              <TEyebrow>concepts in play</TEyebrow>
              <div style={{ marginTop: 10, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                <div className="m-pill m-pill-red"><span>✕</span> PHP sessions</div>
                <div className="m-pill m-pill-yellow"><span>◷</span> Output buffering</div>
              </div>
            </div>
            <div>
              <TEyebrow>your profile</TEyebrow>
              <div style={{ marginTop: 10, fontSize: 13, color: 'rgba(245,239,227,0.75)', lineHeight: 1.45 }}>
                Visual + hands-on · Casual tone · Short reads.
              </div>
            </div>
          </div>

          <div style={{ marginTop: 28 }}>
            <TEyebrow>what just happened</TEyebrow>
            <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ display: 'flex', gap: 12, fontSize: 13, color: 'rgba(245,239,227,0.7)' }}>
                <span className="m-dot" style={{ background: 'var(--red)', marginTop: 6 }} />
                <span><b style={{ color: 'var(--bone)' }}>12 May</b> · test answer flagged a gap on PHP sessions</span>
              </div>
              <div style={{ display: 'flex', gap: 12, fontSize: 13, color: 'rgba(245,239,227,0.7)' }}>
                <span className="m-dot" style={{ background: 'var(--orange)', marginTop: 6 }} />
                <span><b style={{ color: 'var(--bone)' }}>13 May</b> · this mission was generated</span>
              </div>
            </div>
          </div>

          <div style={{ flex: 1 }} />
          <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
            <button className="m-btn m-btn-ghost" style={{ color: 'var(--bone)', flex: 1, padding: '16px' }}>Explain it more simply</button>
            <button className="m-btn m-btn-primary" style={{ flex: 1, padding: '16px' }}>Got it <TI.check style={{ width: 18, height: 18 }} /></button>
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, {
  TLogin, TOnbWelcome, TOnbQuiz, TOnbResult,
  THome, TMap, TNodeDetail, TMission,
  TQuizQ, TQuizR, TDocument, TProfile, TExplain,
});
