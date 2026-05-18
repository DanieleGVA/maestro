/* global React, MaestroIcon, MaestroSafeTop, MaestroSafeBottom, MaestroWordmark */
// MAESTRO — Learning + profile screens: Quiz Q, Quiz Result, Review Document, Profile, Why-this

const I3 = window.MaestroIcon;
const ST = window.MaestroSafeTop;
const SB = window.MaestroSafeBottom;

const I4 = {
  close: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M5 5l14 14M19 5L5 19" /></svg>),
  trophy: (p) => (<svg viewBox="0 0 24 24" fill="currentColor" {...p}><path d="M6 3h12v3a6 6 0 0 1-12 0V3zM4 5h2v2a3 3 0 0 1-3-3h1zm16 0h-1a3 3 0 0 1-3 3V5h2v2h2V5zM10 14h4l1 4H9l1-4zM7 19h10v2H7z"/></svg>),
  sound: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M11 5L6 9H3v6h3l5 4V5z"/><path d="M15 8.5a4 4 0 0 1 0 7"/><path d="M18 5.5a8 8 0 0 1 0 13"/></svg>),
  spark: (p) => (<svg viewBox="0 0 24 24" fill="currentColor" {...p}><path d="M12 2l1.6 6.4L20 10l-6.4 1.6L12 18l-1.6-6.4L4 10l6.4-1.6L12 2z"/></svg>),
  type: (p) => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M5 6h14M12 6v14M9 20h6"/></svg>),
};

// ── SCR-ST-07 (a) — Quiz question ───────────────────────────
function ScreenQuizQuestion() {
  const options = [
    { l: 'A', t: 'INNER JOIN returns only rows where the key exists in both tables.', state: 'selected' },
    { l: 'B', t: 'INNER JOIN returns all rows from the left table.', state: 'idle' },
    { l: 'C', t: 'INNER JOIN merges columns regardless of keys.', state: 'idle' },
    { l: 'D', t: 'INNER JOIN is the same as UNION.', state: 'idle' },
  ];
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--bone)', color: 'var(--ink)',
      display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    }}>
      <ST />
      <div style={{ padding: '10px 20px', display: 'flex', alignItems: 'center', gap: 10 }}>
        <button style={{ width: 38, height: 38, borderRadius: 100, background: 'transparent', border: '1px solid rgba(20,17,13,0.18)', color: 'var(--ink)', display: 'grid', placeItems: 'center' }}>
          <I4.close style={{ width: 18, height: 18 }} />
        </button>
        <div style={{ flex: 1, display: 'flex', gap: 4 }}>
          {[1,1,1,0,0].map((d, i) => (
            <div key={i} style={{ flex: 1, height: 6, borderRadius: 100, background: d ? 'var(--ink)' : 'rgba(20,17,13,0.12)' }} />
          ))}
        </div>
        <span className="m-mono" style={{ fontSize: 11, color: 'var(--ink)', opacity: 0.6, letterSpacing: '0.14em' }}>03 / 05</span>
      </div>

      <div style={{ padding: '12px 24px 0' }}>
        <div className="m-mono" style={{ fontSize: 10, letterSpacing: '0.16em', color: 'rgba(20,17,13,0.5)' }}>QUIZ · SQL JOIN</div>
        <div className="m-display" style={{ fontSize: 30, color: 'var(--ink)', marginTop: 6 }}>
          What does an<br/>
          <span className="m-display-i">INNER JOIN</span> do?
        </div>
      </div>

      <div style={{ padding: '24px 18px 0', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {options.map((o) => <Option key={o.l} {...o} />)}
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '0 24px 16px' }}>
        <button className="m-btn" style={{ width: '100%', background: 'var(--ink)', color: 'var(--bone)' }}>
          Confirm <I3.arrow style={{ width: 18, height: 18 }} />
        </button>
      </div>
      <SB h={28} />
    </div>
  );
}

function Option({ l, t, state }) {
  const selected = state === 'selected';
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', gap: 12, padding: '14px 14px',
      background: selected ? 'var(--ink)' : '#fff',
      color: selected ? 'var(--bone)' : 'var(--ink)',
      border: '1px solid ' + (selected ? 'var(--ink)' : 'rgba(20,17,13,0.12)'),
      borderRadius: 'var(--r-md)',
    }}>
      <div style={{
        width: 28, height: 28, borderRadius: 100, flex: 'none',
        background: selected ? 'var(--signal)' : 'transparent',
        color: selected ? 'var(--signal-ink)' : 'var(--ink)',
        border: selected ? '0' : '1px solid rgba(20,17,13,0.25)',
        display: 'grid', placeItems: 'center', fontSize: 12, fontWeight: 700, fontFamily: 'var(--mono)',
      }}>{l}</div>
      <div style={{ fontSize: 14, lineHeight: 1.4, paddingTop: 4 }}>{t}</div>
    </div>
  );
}

// ── SCR-ST-07 (b) — Quiz result ─────────────────────────────
function ScreenQuizResult() {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)',
      display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    }}>
      {/* celebratory glow */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: 'radial-gradient(circle at 50% 30%, rgba(74,222,128,0.18), rgba(0,0,0,0) 55%)',
      }} />
      <ST />
      <div style={{ padding: '10px 20px 0', display: 'flex', justifyContent: 'flex-end' }}>
        <button style={{ width: 38, height: 38, borderRadius: 100, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
          <I4.close style={{ width: 18, height: 18 }} />
        </button>
      </div>

      <div style={{ padding: '20px 24px 0', textAlign: 'center', position: 'relative' }}>
        <I4.spark style={{ width: 28, height: 28, color: 'var(--signal)', marginBottom: 12 }} />
        <div className="m-eyebrow" style={{ color: 'var(--green)', opacity: 1, marginBottom: 6 }}>nailed it</div>
        <div className="m-display" style={{ fontSize: 36, color: 'var(--bone)' }}>
          4<span className="m-display-i" style={{ color: 'var(--signal)' }}>/</span>5
        </div>
        <div style={{ marginTop: 4, fontSize: 12, color: 'rgba(245,239,227,0.55)' }}>that's 80% · keep this in your head</div>
      </div>

      {/* state pill */}
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: 18 }}>
        <div className="m-pill m-pill-yellow" style={{ padding: '6px 12px', fontSize: 12 }}>
          <span>◷</span> SQL JOIN moved to "TO REVIEW"
        </div>
      </div>

      {/* per-question */}
      <div style={{ padding: '22px 24px 0' }}>
        <div className="m-eyebrow" style={{ marginBottom: 12 }}>by question</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {[
            { n: 1, ok: true,  q: 'What is a relation?' },
            { n: 2, ok: true,  q: 'INNER vs LEFT JOIN' },
            { n: 3, ok: true,  q: 'JOIN on multiple keys' },
            { n: 4, ok: false, q: 'Self-join example' },
            { n: 5, ok: true,  q: 'Result table semantics' },
          ].map(r => (
            <div key={r.n} style={{
              display: 'flex', alignItems: 'center', gap: 10,
              background: 'var(--ink-2)', border: '1px solid var(--ink-line)',
              borderRadius: 12, padding: '10px 12px',
            }}>
              <span style={{
                width: 24, height: 24, borderRadius: 100, flex: 'none',
                background: r.ok ? 'var(--green)' : 'var(--orange)',
                color: 'var(--ink)', display: 'grid', placeItems: 'center',
              }}>
                {r.ok ? <I3.check style={{ width: 14, height: 14 }} /> : <I3.x style={{ width: 14, height: 14 }} />}
              </span>
              <span className="m-mono" style={{ fontSize: 10, color: 'rgba(245,239,227,0.55)', letterSpacing: '0.14em' }}>Q0{r.n}</span>
              <span style={{ flex: 1, fontSize: 13, color: 'var(--bone)' }}>{r.q}</span>
              <span style={{ fontSize: 11, color: 'rgba(245,239,227,0.45)' }}>review</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '0 24px 14px', display: 'flex', flexDirection: 'column', gap: 8 }}>
        <button className="m-btn m-btn-primary" style={{ width: '100%' }}>
          Back to your map <I3.arrow style={{ width: 18, height: 18 }} />
        </button>
        <button className="m-btn m-btn-ghost" style={{ width: '100%' }}>
          Try a fresh angle
        </button>
      </div>
      <SB h={28} />
    </div>
  );
}

// ── SCR-ST-08 — Review document ─────────────────────────────
function ScreenDocument() {
  return (
    <div className="maestro-screen light" style={{
      width: '100%', height: '100%', background: 'var(--paper)', color: 'var(--ink)',
      display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    }}>
      <ST />
      <div style={{ padding: '8px 20px 0', display: 'flex', alignItems: 'center', gap: 8 }}>
        <button style={{ width: 38, height: 38, borderRadius: 100, background: 'transparent', border: '1px solid rgba(20,17,13,0.18)', color: 'var(--ink)', display: 'grid', placeItems: 'center' }}>
          <I3.back style={{ width: 18, height: 18 }} />
        </button>
        <div style={{ flex: 1, fontSize: 11, color: 'rgba(20,17,13,0.55)' }}>Mission · Step 1</div>
        <button style={{ background: 'transparent', border: '1px solid rgba(20,17,13,0.18)', borderRadius: 100, padding: '7px 12px', fontSize: 11, fontWeight: 600, color: 'var(--ink)', display: 'inline-flex', gap: 4, alignItems: 'center' }}>
          <I4.spark style={{ width: 12, height: 12 }} /> Why this?
        </button>
      </div>

      <div style={{ padding: '12px 24px 0' }}>
        <div className="m-mono" style={{ fontSize: 10, letterSpacing: '0.16em', color: 'rgba(20,17,13,0.5)' }}>REVIEW · MADE FOR YOU</div>
        <div className="m-display" style={{ fontSize: 30, color: 'var(--ink)', marginTop: 4 }}>
          PHP <span className="m-display-i">sessions</span>
        </div>
        <div style={{ marginTop: 4, fontSize: 12, color: 'rgba(20,17,13,0.55)' }}>3 min read · with a basketball analogy, like you wanted</div>
      </div>

      <div style={{ padding: '20px 20px 0', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {/* Block 1 — your error */}
        <Block tag="WHERE YOU SLIPPED" tone="yellow" label="ERROR">
          <pre style={preStyle}>
{`<?php
  session_start();
  $_SESSION['user'] = $name;
?>
<html>
  <body>...`}
          </pre>
          <div style={{ fontSize: 12, color: 'rgba(20,17,13,0.65)', marginTop: 8 }}>
            You opened the session <em>after</em> some output. Spot it?
          </div>
        </Block>

        {/* Block 2 — analogy */}
        <Block tag="THE BASKETBALL VERSION" tone="ink">
          <div style={{ fontSize: 13.5, color: 'var(--ink)', lineHeight: 1.5 }}>
            A session is like checking in at the gym desk. If you walk onto the court first, the desk can't log you in anymore — the game's already started.
          </div>
        </Block>

        {/* Block 3 — correct */}
        <Block tag="HOW IT WORKS RIGHT" tone="green" label="CORRECT">
          <pre style={preStyle}>
{`<?php
  session_start();   // first thing
?>
<html>
  <body>
    Hello <?= $_SESSION['user'] ?>`}
          </pre>
        </Block>

        {/* Block 4 — remember */}
        <Block tag="REMEMBER THIS" tone="signal">
          <div style={{ fontSize: 14, color: 'var(--ink)', fontWeight: 600, lineHeight: 1.4 }}>
            <span className="m-display-i" style={{ fontSize: 18 }}>session_start()</span> must be the very first thing — before any output.
          </div>
        </Block>
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '12px 20px 0', display: 'flex', gap: 10 }}>
        <button style={{
          flex: 1, padding: '14px', borderRadius: 100, background: '#fff',
          border: '1px solid rgba(20,17,13,0.15)', color: 'var(--ink)',
          fontWeight: 600, fontSize: 13, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 6,
        }}>
          <I4.sound style={{ width: 16, height: 16 }} /> Listen
        </button>
        <button className="m-btn" style={{ flex: 1, background: 'var(--ink)', color: 'var(--bone)' }}>
          Try it <I3.arrow style={{ width: 16, height: 16 }} />
        </button>
      </div>
      <SB h={20} />
    </div>
  );
}

const preStyle = {
  margin: 0, padding: '10px 12px', background: 'rgba(20,17,13,0.06)',
  borderRadius: 10, fontFamily: 'var(--mono)', fontSize: 11.5, lineHeight: 1.5,
  color: 'var(--ink)', whiteSpace: 'pre-wrap',
};

function Block({ tag, tone, label, children }) {
  const tones = {
    yellow: { bg: 'rgba(245,197,61,0.18)', stripe: 'var(--yellow)', tag: 'rgba(120,90,10,1)' },
    green:  { bg: 'rgba(74,222,128,0.18)', stripe: 'var(--green)', tag: 'rgba(20,90,40,1)' },
    ink:    { bg: '#fff', stripe: 'var(--ink)', tag: 'rgba(20,17,13,0.65)' },
    signal: { bg: 'var(--signal)', stripe: 'var(--signal-ink)', tag: 'var(--signal-ink)' },
  }[tone];
  return (
    <div style={{
      background: tones.bg, borderRadius: 'var(--r-md)', padding: '12px 14px 14px',
      borderLeft: `4px solid ${tones.stripe}`,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span className="m-mono" style={{ fontSize: 9, letterSpacing: '0.18em', color: tones.tag }}>{tag}</span>
        {label && <span className="m-mono" style={{ fontSize: 9, letterSpacing: '0.18em', padding: '2px 7px', borderRadius: 100, background: tones.stripe, color: tone === 'signal' ? 'var(--signal)' : '#fff' }}>{label}</span>}
      </div>
      {children}
    </div>
  );
}

// ── SCR-ST-09 — Profile & preferences ───────────────────────
function ScreenProfile() {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)',
      display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    }}>
      <ST />
      <div style={{ padding: '8px 20px 0', display: 'flex', alignItems: 'center', gap: 8 }}>
        <button style={{ width: 38, height: 38, borderRadius: 100, background: 'var(--ink-2)', border: '1px solid var(--ink-line)', color: 'var(--bone)', display: 'grid', placeItems: 'center' }}>
          <I3.back style={{ width: 18, height: 18 }} />
        </button>
        <div style={{ flex: 1 }}>
          <div className="m-mono" style={{ fontSize: 9, letterSpacing: '0.16em', color: 'rgba(245,239,227,0.5)' }}>YOUR SETUP</div>
          <div className="m-display" style={{ fontSize: 24, color: 'var(--bone)' }}>Profile</div>
        </div>
      </div>

      {/* identity card */}
      <div style={{ margin: '14px 20px 0', padding: '16px', background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 'var(--r-md)', display: 'flex', alignItems: 'center', gap: 14 }}>
        <div style={{ width: 56, height: 56, borderRadius: 18, background: 'var(--signal)', color: 'var(--signal-ink)', display: 'grid', placeItems: 'center', fontFamily: 'var(--display)', fontSize: 30 }}>L</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 16, color: 'var(--bone)', fontWeight: 600 }}>Leo Romano</div>
          <div style={{ fontSize: 12, color: 'rgba(245,239,227,0.55)' }}>3AI · Informatics · 17 nodes solid</div>
        </div>
      </div>

      {/* how I learn */}
      <div style={{ padding: '20px 20px 0' }}>
        <div className="m-eyebrow" style={{ marginBottom: 10 }}>how I learn</div>
        <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 'var(--r-md)', padding: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <MiniRadar />
            <div style={{ flex: 1, fontSize: 12, color: 'rgba(245,239,227,0.7)', lineHeight: 1.4 }}>
              You're a <span style={{ color: 'var(--signal)', fontWeight: 600 }}>visual + hands-on</span> type. We'll lean into diagrams and tiny experiments.
            </div>
          </div>
        </div>
      </div>

      {/* content preferences */}
      <div style={{ padding: '18px 20px 0' }}>
        <div className="m-eyebrow" style={{ marginBottom: 10 }}>tone & length</div>
        <Segmented options={['Casual', 'Calm', 'Formal']} active={0} />
        <div style={{ height: 8 }} />
        <Segmented options={['Short', 'Deep dive']} active={0} />
      </div>

      {/* accessibility */}
      <div style={{ padding: '18px 20px 0' }}>
        <div className="m-eyebrow" style={{ marginBottom: 10 }}>accessibility</div>
        <div style={{ background: 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 'var(--r-md)', padding: 14, display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Row left={<span style={{ display: 'flex', alignItems: 'center', gap: 8 }}><I4.type style={{ width: 16, height: 16, opacity: 0.7 }} /> Font</span>} right={<span style={{ color: 'var(--signal)', fontWeight: 600 }}>Geist</span>} />
          <SliderRow label="Text size" min="A" max="A" valLabel="17 pt" pct={0.45} />
          <Row left="Theme" right={<Segmented small options={['Light','Dark','Sepia']} active={1} />} />
          <Row left="High contrast" right={<Toggle on={false} />} />
        </div>
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '12px 20px 14px' }}>
        <button className="m-btn m-btn-primary" style={{ width: '100%' }}>
          Save changes <I3.check style={{ width: 18, height: 18 }} />
        </button>
      </div>
      <SB h={20} />
    </div>
  );
}

function Segmented({ options, active, small }) {
  return (
    <div style={{ display: 'flex', background: small ? 'transparent' : 'var(--ink-2)', border: '1px solid var(--ink-line)', borderRadius: 100, padding: 3 }}>
      {options.map((o, i) => (
        <div key={o} style={{
          flex: 1, textAlign: 'center', padding: small ? '4px 8px' : '8px 10px',
          background: i === active ? 'var(--bone)' : 'transparent',
          color: i === active ? 'var(--ink)' : 'rgba(245,239,227,0.6)',
          borderRadius: 100, fontSize: small ? 11 : 12, fontWeight: 600,
        }}>{o}</div>
      ))}
    </div>
  );
}

function Row({ left, right }) {
  return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 13, color: 'var(--bone)' }}>{left}<div>{right}</div></div>;
}

function Toggle({ on }) {
  return (
    <div style={{ width: 40, height: 24, borderRadius: 100, background: on ? 'var(--signal)' : 'var(--ink-3)', position: 'relative', border: '1px solid var(--ink-line)' }}>
      <div style={{ position: 'absolute', top: 2, left: on ? 18 : 2, width: 18, height: 18, borderRadius: 100, background: '#fff' }} />
    </div>
  );
}

function SliderRow({ label, valLabel, pct }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, color: 'var(--bone)', marginBottom: 6 }}>
        <span>{label}</span><span style={{ color: 'var(--signal)' }}>{valLabel}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 11, color: 'rgba(245,239,227,0.5)' }}>A</span>
        <div style={{ flex: 1, height: 4, borderRadius: 100, background: 'var(--ink-3)', position: 'relative' }}>
          <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: (pct * 100) + '%', background: 'var(--signal)', borderRadius: 100 }} />
          <div style={{ position: 'absolute', left: `calc(${pct * 100}% - 8px)`, top: -6, width: 16, height: 16, borderRadius: 100, background: 'var(--signal)', border: '3px solid var(--ink-2)' }} />
        </div>
        <span style={{ fontSize: 16, color: 'rgba(245,239,227,0.7)', fontWeight: 600 }}>A</span>
      </div>
    </div>
  );
}

function MiniRadar() {
  const axes = [0.85, 0.55, 0.78, 0.40, 0.62];
  const cx = 36, cy = 36, R = 28;
  const pts = axes.map((v, i) => {
    const a = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
    return [cx + Math.cos(a) * R * v, cy + Math.sin(a) * R * v];
  });
  return (
    <svg width="72" height="72" viewBox="0 0 72 72">
      <polygon points={axes.map((_, i) => {
        const a = -Math.PI/2 + (i * 2 * Math.PI / axes.length);
        return [cx + Math.cos(a) * R, cy + Math.sin(a) * R].join(',');
      }).join(' ')} fill="none" stroke="rgba(245,239,227,0.12)" />
      <polygon points={pts.map(p => p.join(',')).join(' ')} fill="rgba(212,255,61,0.25)" stroke="var(--signal)" strokeWidth="1.5" />
    </svg>
  );
}

// ── SCR-ST-10 — Why this? explainability sheet ──────────────
function ScreenExplain() {
  return (
    <div className="maestro-screen" style={{
      width: '100%', height: '100%', background: 'var(--ink)',
      display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    }}>
      {/* faded backdrop showing a doc behind */}
      <div style={{ position: 'absolute', inset: 0, background: 'var(--paper)', opacity: 0.06 }} />
      <ST />

      {/* sheet */}
      <div style={{ flex: 1, position: 'relative' }}>
        <div style={{
          position: 'absolute', left: 12, right: 12, bottom: 12, top: 100,
          background: 'var(--ink-2)', borderRadius: 28, border: '1px solid var(--ink-line)',
          boxShadow: '0 -20px 60px rgba(0,0,0,0.6)',
          padding: '14px 20px 20px', display: 'flex', flexDirection: 'column',
        }}>
          {/* handle */}
          <div style={{ width: 40, height: 4, borderRadius: 100, background: 'var(--ink-3)', margin: '4px auto 14px' }} />

          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
            <I4.spark style={{ width: 18, height: 18, color: 'var(--signal)' }} />
            <div className="m-eyebrow" style={{ color: 'var(--signal)', opacity: 1 }}>maestro reasoning</div>
          </div>
          <div className="m-display" style={{ fontSize: 28, color: 'var(--bone)' }}>
            Why am I<br/>showing you <span className="m-display-i">this</span>?
          </div>

          {/* sections */}
          <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 14 }}>
            <ExplainSection title="Concepts in play">
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                <div className="m-pill m-pill-red"><span>✕</span> PHP sessions</div>
                <div className="m-pill m-pill-yellow"><span>◷</span> Output buffering</div>
              </div>
            </ExplainSection>

            <ExplainSection title="Your profile">
              <div style={{ fontSize: 12.5, color: 'rgba(245,239,227,0.75)', lineHeight: 1.4 }}>
                Visual + hands-on. Casual tone. Short reads. You said basketball analogies click.
              </div>
            </ExplainSection>

            <ExplainSection title="What just happened">
              <div style={{ fontSize: 12, color: 'rgba(245,239,227,0.65)', lineHeight: 1.5 }}>
                <div style={{ display: 'flex', gap: 8 }}><span className="m-dot" style={{ background: 'var(--red)', marginTop: 4 }} /> <span><b style={{ color: 'var(--bone)' }}>12 May</b> · test answer flagged a gap on PHP sessions</span></div>
                <div style={{ display: 'flex', gap: 8, marginTop: 6 }}><span className="m-dot" style={{ background: 'var(--orange)', marginTop: 4 }} /> <span><b style={{ color: 'var(--bone)' }}>13 May</b> · this mission was generated</span></div>
              </div>
            </ExplainSection>
          </div>

          <div style={{ flex: 1 }} />
          <button className="m-btn m-btn-ghost" style={{ width: '100%', marginTop: 12, color: 'var(--bone)' }}>
            Explain it more simply
          </button>
          <button className="m-btn m-btn-primary" style={{ width: '100%', marginTop: 8 }}>
            Got it <I3.check style={{ width: 18, height: 18 }} />
          </button>
        </div>
      </div>
      <SB h={20} />
    </div>
  );
}

function ExplainSection({ title, children }) {
  return (
    <div>
      <div className="m-mono" style={{ fontSize: 9, letterSpacing: '0.16em', color: 'rgba(245,239,227,0.45)', marginBottom: 6 }}>{title.toUpperCase()}</div>
      {children}
    </div>
  );
}

Object.assign(window, { ScreenQuizQuestion, ScreenQuizResult, ScreenDocument, ScreenProfile, ScreenExplain });
