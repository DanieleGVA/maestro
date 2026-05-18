/* global React */
// MAESTRO — Auth + Onboarding screens
// Components rendered INSIDE an IOSDevice (full bleed; we draw our own header).
// Safe area: ~64px top (status bar + dynamic island), ~34px bottom (home indicator).

// ── shared bits ─────────────────────────────────────────────
const Icon = {
  arrow: (props) => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M5 12h14M13 5l7 7-7 7" />
    </svg>
  ),
  back: (props) => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M19 12H5M12 19l-7-7 7-7" />
    </svg>
  ),
  eye: (props) => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" /><circle cx="12" cy="12" r="3" />
    </svg>
  ),
  book: (props) => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v17H6.5A2.5 2.5 0 0 0 4 21.5V4.5Z" /><path d="M20 19v3H6.5A2.5 2.5 0 0 1 4 19.5" />
    </svg>
  ),
  headphones: (props) => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M3 18v-6a9 9 0 0 1 18 0v6" /><path d="M21 19a2 2 0 0 1-2 2h-1v-7h3v5ZM3 19a2 2 0 0 0 2 2h1v-7H3v5Z" />
    </svg>
  ),
  eye2: (props) => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="3.5" />
    </svg>
  ),
  hand: (props) => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M9 11V5a2 2 0 1 1 4 0v6" /><path d="M13 11V4a2 2 0 1 1 4 0v9" /><path d="M17 11V6a2 2 0 1 1 4 0v9a6 6 0 0 1-6 6h-2a6 6 0 0 1-6-6v-2l-2-3a2 2 0 0 1 3-3l2 2" />
    </svg>
  ),
  sparkle: (props) => (
    <svg viewBox="0 0 24 24" fill="currentColor" {...props}>
      <path d="M12 2l1.6 6.4L20 10l-6.4 1.6L12 18l-1.6-6.4L4 10l6.4-1.6L12 2z" />
    </svg>
  ),
  check: (props) => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M4 12l5 5L20 6" />
    </svg>
  ),
  x: (props) => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M5 5l14 14M19 5L5 19" />
    </svg>
  ),
};

// Top safe area spacer (status bar + dynamic island)
const SafeTop = ({ h = 64 }) => <div style={{ height: h, flex: 'none' }} />;
const SafeBottom = ({ h = 34 }) => <div style={{ height: h, flex: 'none' }} />;

// Wordmark
const Wordmark = ({ size = 22, color }) => (
  <div className="m-display" style={{ fontSize: size, color, lineHeight: 1 }}>
    Maestro<span style={{ color: 'var(--signal)' }}>.</span>
  </div>
);

// ── SCR-ST-01 — Login ───────────────────────────────────────
function ScreenLogin() {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)',
      display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    }}>
      {/* hero gradient blob */}
      <div style={{
        position: 'absolute', top: -120, right: -120, width: 360, height: 360,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(212,255,61,0.35), rgba(212,255,61,0) 60%)',
        filter: 'blur(8px)', pointerEvents: 'none',
      }} />

      <SafeTop />
      <div style={{ padding: '24px 28px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'relative' }}>
        <Wordmark size={20} color="var(--bone)" />
        <span className="m-mono" style={{ fontSize: 10, color: 'rgba(245,239,227,0.5)', letterSpacing: '0.16em' }}>v 1.0</span>
      </div>

      <div style={{ padding: '64px 28px 0', position: 'relative' }}>
        <div className="m-eyebrow" style={{ color: 'var(--signal)', opacity: 1, marginBottom: 14 }}>welcome back</div>
        <div className="m-display" style={{ fontSize: 52, color: 'var(--bone)' }}>
          Pick up<br/>
          <span className="m-display-i">where</span> you<br/>
          left off.
        </div>
      </div>

      <div style={{ padding: '40px 24px 0', display: 'flex', flexDirection: 'column', gap: 12, position: 'relative' }}>
        <Field label="USERNAME" value="leo.romano" />
        <Field label="PASSWORD" value="••••••••••" trailing={<Icon.eye style={{ width: 18, height: 18, color: 'rgba(245,239,227,0.55)' }} />} />
      </div>

      <div style={{ padding: '20px 24px 0', position: 'relative' }}>
        <button className="m-btn m-btn-primary" style={{ width: '100%' }}>
          Log in <Icon.arrow style={{ width: 18, height: 18 }} />
        </button>
        <div style={{ marginTop: 14, textAlign: 'center', fontSize: 13, color: 'rgba(245,239,227,0.55)' }}>
          or <span style={{ color: 'var(--bone)', borderBottom: '1px solid var(--ink-line)', paddingBottom: 1 }}>continue with school SSO</span>
        </div>
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '0 24px 0', position: 'relative', textAlign: 'center' }}>
        <span className="m-mono" style={{ fontSize: 11, color: 'rgba(245,239,227,0.4)', letterSpacing: '0.1em' }}>
          forgot password? · ask your school IT
        </span>
      </div>
      <SafeBottom h={48} />
    </div>
  );
}

function Field({ label, value, trailing }) {
  return (
    <div style={{
      background: 'var(--ink-2)', border: '1px solid var(--ink-line)',
      borderRadius: 'var(--r-md)', padding: '12px 16px',
    }}>
      <div className="m-mono" style={{ fontSize: 9, letterSpacing: '0.16em', color: 'rgba(245,239,227,0.5)' }}>{label}</div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
        <div style={{ flex: 1, fontSize: 16, color: 'var(--bone)' }}>{value}</div>
        {trailing}
      </div>
    </div>
  );
}

// ── SCR-ST-02 (a) — Onboarding welcome ───────────────────────
function ScreenOnbWelcome() {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--signal)', color: 'var(--signal-ink)',
      display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    }}>
      <SafeTop />
      {/* header */}
      <div style={{ padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="m-display" style={{ fontSize: 18, color: 'var(--signal-ink)' }}>
          Maestro<span style={{ opacity: 0.45 }}>.</span>
        </div>
        <button style={{ background: 'transparent', border: 0, color: 'var(--signal-ink)', fontSize: 13, fontWeight: 600, opacity: 0.65 }}>Skip ›</button>
      </div>

      {/* progress */}
      <div style={{ padding: '0 24px', display: 'flex', gap: 6, marginBottom: 32 }}>
        {[1,2,3,4,5].map(i => (
          <div key={i} style={{ flex: 1, height: 3, borderRadius: 100, background: i === 1 ? 'var(--signal-ink)' : 'rgba(11,19,0,0.18)' }} />
        ))}
      </div>

      <div style={{ padding: '0 28px', flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div className="m-eyebrow" style={{ color: 'var(--signal-ink)', opacity: 0.55, marginBottom: 18 }}>step 1 of 5</div>

        <div className="m-display" style={{ fontSize: 56, color: 'var(--signal-ink)' }}>
          Let's find<br/>
          <span className="m-display-i">how you</span><br/>
          learn best.
        </div>

        <div style={{ marginTop: 26, fontSize: 16, lineHeight: 1.45, color: 'var(--signal-ink)', opacity: 0.78, maxWidth: 320 }}>
          Not a graded test. Just a 5-minute vibe check so we can tune Maestro to <span style={{ fontStyle: 'italic', fontFamily: 'var(--display)' }}>your</span> brain.
        </div>

        {/* big illustrative numerals */}
        <div style={{ marginTop: 30, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {['Read','Listen','Watch','Try'].map((t, i) => (
            <div key={t} style={{
              padding: '8px 14px', border: '1.5px solid var(--signal-ink)', borderRadius: 100,
              fontSize: 13, fontWeight: 600,
              background: i === 3 ? 'var(--signal-ink)' : 'transparent', color: i === 3 ? 'var(--signal)' : 'var(--signal-ink)',
            }}>{t}</div>
          ))}
        </div>

        <div style={{ flex: 1 }} />

        <button className="m-btn" style={{ background: 'var(--signal-ink)', color: 'var(--signal)', width: '100%', marginTop: 16 }}>
          Let's go <Icon.arrow style={{ width: 18, height: 18 }} />
        </button>
      </div>
      <SafeBottom h={48} />
    </div>
  );
}

// ── SCR-ST-02 (b) — Modality quiz step ──────────────────────
function ScreenOnbQuiz() {
  const cards = [
    { key: 'read',  label: 'Read',   Icon: Icon.book,       blurb: 'A short explainer text', active: true },
    { key: 'listen',label: 'Listen', Icon: Icon.headphones, blurb: '45-second audio clip',  active: false },
    { key: 'watch', label: 'Watch',  Icon: Icon.eye2,        blurb: 'Diagram you can pan',   active: false },
    { key: 'try',   label: 'Try',    Icon: Icon.hand,        blurb: 'Tiny interactive task', active: false, done: true },
  ];
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)',
      display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    }}>
      <SafeTop />
      <div style={{ padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Wordmark size={18} color="var(--bone)" />
        <button style={{ background: 'transparent', border: 0, color: 'rgba(245,239,227,0.55)', fontSize: 13, fontWeight: 600 }}>Skip ›</button>
      </div>
      <div style={{ padding: '0 24px', display: 'flex', gap: 6, marginBottom: 24 }}>
        {[1,2,3,4,5].map(i => (
          <div key={i} style={{ flex: 1, height: 3, borderRadius: 100, background: i <= 3 ? 'var(--signal)' : 'rgba(245,239,227,0.15)' }} />
        ))}
      </div>

      <div style={{ padding: '0 24px' }}>
        <div className="m-eyebrow" style={{ color: 'var(--signal)', opacity: 1, marginBottom: 10 }}>concept 3 / 4</div>
        <div className="m-display" style={{ fontSize: 36, color: 'var(--bone)' }}>
          What's a <span className="m-display-i">variable</span>?
        </div>
        <div style={{ marginTop: 10, fontSize: 14, color: 'rgba(245,239,227,0.6)' }}>Pick the way you'd rather learn it.</div>
      </div>

      <div style={{ padding: '22px 24px 0', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        {cards.map(c => (
          <button key={c.key} style={{
            background: c.active ? 'var(--bone)' : 'var(--ink-2)',
            color: c.active ? 'var(--ink)' : 'var(--bone)',
            border: '1px solid ' + (c.active ? 'var(--bone)' : 'var(--ink-line)'),
            borderRadius: 'var(--r-md)', padding: '18px 16px',
            textAlign: 'left', cursor: 'pointer', position: 'relative',
            minHeight: 140, display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
          }}>
            <c.Icon style={{ width: 24, height: 24 }} />
            <div>
              <div className="m-display" style={{ fontSize: 22 }}>{c.label}</div>
              <div style={{ marginTop: 4, fontSize: 11, opacity: 0.65, lineHeight: 1.3 }}>{c.blurb}</div>
            </div>
            {c.done && (
              <div style={{
                position: 'absolute', top: 12, right: 12, width: 20, height: 20, borderRadius: 100,
                background: 'var(--green)', color: 'var(--ink)', display: 'grid', placeItems: 'center',
              }}><Icon.check style={{ width: 12, height: 12 }} /></div>
            )}
            {c.active && (
              <div style={{
                position: 'absolute', top: 12, right: 12,
                fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.16em',
                padding: '3px 7px', background: 'var(--ink)', color: 'var(--signal)', borderRadius: 100,
              }}>OPEN</div>
            )}
          </button>
        ))}
      </div>

      {/* mini-tracker */}
      <div style={{ padding: '20px 24px 0', display: 'flex', alignItems: 'center', gap: 8 }}>
        <Icon.sparkle style={{ width: 14, height: 14, color: 'var(--signal)' }} />
        <span style={{ fontSize: 12, color: 'rgba(245,239,227,0.6)' }}>
          You spent <span style={{ color: 'var(--bone)' }}>42s</span> reading. Maestro is paying attention.
        </span>
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '0 24px' }}>
        <button className="m-btn m-btn-primary" style={{ width: '100%' }}>
          Next concept <Icon.arrow style={{ width: 18, height: 18 }} />
        </button>
      </div>
      <SafeBottom h={48} />
    </div>
  );
}

// ── SCR-ST-02 (c) — Radar result ────────────────────────────
function ScreenOnbResult() {
  // radar data
  const axes = [
    { label: 'VISUAL',     v: 0.85 },
    { label: 'AUDITORY',   v: 0.55 },
    { label: 'HANDS-ON',   v: 0.78 },
    { label: 'REFLECTIVE', v: 0.40 },
    { label: 'SOCIAL',     v: 0.62 },
  ];
  const cx = 130, cy = 130, R = 95;
  const pts = axes.map((a, i) => {
    const angle = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
    return [cx + Math.cos(angle) * R * a.v, cy + Math.sin(angle) * R * a.v];
  });
  const polyPts = pts.map(p => p.join(',')).join(' ');
  const labelPts = axes.map((a, i) => {
    const angle = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
    return [cx + Math.cos(angle) * (R + 18), cy + Math.sin(angle) * (R + 18), a.label];
  });
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)',
      display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    }}>
      <SafeTop />
      <div style={{ padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Wordmark size={18} color="var(--bone)" />
        <span className="m-mono" style={{ fontSize: 10, color: 'rgba(245,239,227,0.5)', letterSpacing: '0.16em' }}>step 5 / 5</span>
      </div>

      <div style={{ padding: '8px 24px 0' }}>
        <div className="m-eyebrow" style={{ color: 'var(--signal)', opacity: 1, marginBottom: 8 }}>your shape</div>
        <div className="m-display" style={{ fontSize: 30, color: 'var(--bone)' }}>
          You're a <span className="m-display-i">visual,</span><br/>hands-on type.
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', marginTop: 4 }}>
        <svg width="260" height="260" viewBox="0 0 260 260">
          {/* grid */}
          {[0.25, 0.5, 0.75, 1].map(s => {
            const g = axes.map((_, i) => {
              const angle = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
              return [cx + Math.cos(angle) * R * s, cy + Math.sin(angle) * R * s].join(',');
            }).join(' ');
            return <polygon key={s} points={g} fill="none" stroke="rgba(245,239,227,0.08)" />;
          })}
          {axes.map((_, i) => {
            const angle = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
            return <line key={i} x1={cx} y1={cy} x2={cx + Math.cos(angle)*R} y2={cy + Math.sin(angle)*R} stroke="rgba(245,239,227,0.08)" />;
          })}
          {/* shape */}
          <polygon points={polyPts} fill="rgba(212,255,61,0.18)" stroke="var(--signal)" strokeWidth="2" />
          {pts.map((p, i) => (
            <circle key={i} cx={p[0]} cy={p[1]} r="3.5" fill="var(--signal)" />
          ))}
          {/* labels */}
          {labelPts.map(([x, y, t], i) => (
            <text key={i} x={x} y={y} textAnchor="middle" dominantBaseline="middle"
              style={{ fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.12em', fill: 'rgba(245,239,227,0.7)' }}>
              {t}
            </text>
          ))}
        </svg>
      </div>

      {/* preferences row */}
      <div style={{ padding: '0 24px' }}>
        <div className="m-eyebrow" style={{ marginBottom: 8 }}>tune it</div>
        <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
          <Chip label="Casual"  active />
          <Chip label="Calm" />
          <Chip label="Formal" />
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Chip label="Short" active />
          <Chip label="Deep dive" />
        </div>
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '0 24px' }}>
        <button className="m-btn m-btn-primary" style={{ width: '100%' }}>
          Looks like me <Icon.arrow style={{ width: 18, height: 18 }} />
        </button>
        <div style={{ marginTop: 10, textAlign: 'center', fontSize: 12, color: 'rgba(245,239,227,0.55)' }}>
          <span style={{ borderBottom: '1px solid var(--ink-line)' }}>I want to tweak it manually</span>
        </div>
      </div>
      <SafeBottom h={48} />
    </div>
  );
}

function Chip({ label, active }) {
  return (
    <div style={{
      padding: '8px 14px', borderRadius: 100,
      border: '1px solid ' + (active ? 'var(--signal)' : 'var(--ink-line)'),
      background: active ? 'var(--signal)' : 'transparent',
      color: active ? 'var(--signal-ink)' : 'var(--bone)',
      fontSize: 12, fontWeight: 600,
    }}>{label}</div>
  );
}

Object.assign(window, {
  ScreenLogin, ScreenOnbWelcome, ScreenOnbQuiz, ScreenOnbResult,
  MaestroIcon: Icon, MaestroSafeTop: SafeTop, MaestroSafeBottom: SafeBottom, MaestroWordmark: Wordmark,
});
