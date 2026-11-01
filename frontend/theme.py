"""Look and feel. Fonts and styles are registered once for every page."""
from nicegui import ui

FONTS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
"""

CSS = """
:root {
  --bg: #0b0b12; --surface: #13131d; --surface-2: #1a1a27; --text: #ececf4;
  --muted: #8a8aa3; --line: #24243a; --accent: #7c5cff;
  --display: "Space Grotesk", system-ui, sans-serif;
  --body: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono: "JetBrains Mono", ui-monospace, Menlo, Consolas, monospace;
  --ease: cubic-bezier(.22, .8, .26, 1);
}

/* ---------- base ---------- */
@view-transition { navigation: auto; }                       /* smooth cross-fade between pages */
::view-transition-old(root), ::view-transition-new(root) { animation-duration: .35s; }
html { background-color: var(--bg) !important;
       background-image: radial-gradient(900px 500px at 50% -10%, rgba(124,92,255,.16), transparent 70%) !important;
       background-attachment: fixed; }
body, .q-page, .q-layout, .nicegui-content { background: transparent !important; color: var(--text); font-family: var(--body); }
.nicegui-content { padding: 0 !important; gap: 0 !important; align-items: stretch !important; }
a { color: inherit; text-decoration: none; }
::selection { background: var(--accent); color: #0b0b12; }

@keyframes pa-rise  { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes pa-fade  { from { opacity: 0; } to { opacity: 1; } }
@keyframes pa-blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

/* ---------- home ---------- */
.pa-wrap { width: 100%; max-width: 1040px; margin: 0 auto; padding: 0 1.5rem 4rem; gap: 0; }
.pa-logo { font-family: var(--display); font-weight: 700; font-size: clamp(2.75rem, 9vw, 5rem); letter-spacing: -.04em;
           line-height: 1; margin-top: 4.5rem; animation: pa-rise .7s var(--ease) backwards; }
.pa-logo::after { content: ""; display: inline-block; width: .14em; height: .72em; margin-left: .1em;
                  background: var(--accent); animation: pa-blink 1.1s steps(1) infinite; }
.pa-tagline { margin-top: 1.5rem; max-width: 46ch; color: var(--muted); font-size: 1.05rem; line-height: 1.6;
              animation: pa-rise .7s var(--ease) .08s backwards; }
.pa-section { margin: 3rem 0 1rem; font-family: var(--mono); font-size: .75rem; letter-spacing: .18em;
              text-transform: uppercase; color: var(--muted); animation: pa-rise .7s var(--ease) .16s backwards; }
.pa-list { display: grid !important; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 1rem; width: 100%; }

.pa-card { position: relative; display: flex; flex-direction: column; gap: 1.1rem; padding: 1.4rem; overflow: hidden;
           background: var(--surface); border: 1px solid var(--line); border-radius: 18px;
           transition: transform .35s var(--ease), border-color .35s var(--ease), box-shadow .35s var(--ease), background .35s var(--ease);
           animation: pa-rise .7s var(--ease) backwards; animation-delay: calc(var(--i, 0) * 70ms + 240ms); }
.pa-card::before { content: ""; position: absolute; inset: 0 0 auto 0; height: 2px; background: var(--accent);
                   opacity: 0; transition: opacity .35s var(--ease); }
.pa-card:hover { transform: translateY(-5px); background: var(--surface-2);
                 border-color: color-mix(in srgb, var(--accent) 55%, var(--line));
                 box-shadow: 0 18px 44px -18px color-mix(in srgb, var(--accent) 60%, transparent); }
.pa-card:hover::before { opacity: 1; }
.pa-icon { display: grid; place-items: center; width: 3rem; height: 3rem; font-size: 1.5rem; border-radius: 12px;
           background: color-mix(in srgb, var(--accent) 14%, transparent); transition: transform .35s var(--ease); }
.pa-card:hover .pa-icon { transform: scale(1.1) rotate(-5deg); }
.pa-text { gap: .35rem; flex: 1; }
.pa-title { font-family: var(--display); font-weight: 600; font-size: 1.25rem; letter-spacing: -.02em; }
.pa-desc { color: var(--muted); font-size: .95rem; line-height: 1.5; }
.pa-keys { margin-top: .4rem; font-family: var(--mono); font-size: .72rem; color: var(--muted); opacity: .75; }
.pa-cta { font-weight: 600; font-size: .9rem; color: var(--accent); }
.pa-cta::after { content: "\\2192"; display: inline-block; margin-left: .4rem; transition: transform .35s var(--ease); }
.pa-card:hover .pa-cta::after { transform: translateX(5px); }
.pa-notice { grid-column: 1 / -1; padding: 1rem 1.25rem; background: var(--surface); border: 1px dashed var(--line);
             border-radius: 12px; color: var(--muted); }

/* ---------- play page ---------- */
.pa-top { width: 100%; max-width: 1040px; margin: 0 auto; padding: 1.25rem 1.5rem; flex-direction: row;
          justify-content: space-between; align-items: center; animation: pa-fade .5s ease backwards; }
.pa-back { color: var(--muted); font-weight: 500; font-size: .9rem; transition: color .25s ease; }
.pa-back::before { content: "\\2190"; display: inline-block; margin-right: .5rem; transition: transform .3s var(--ease); }
.pa-back:hover { color: var(--text); }
.pa-back:hover::before { transform: translateX(-4px); }
.pa-small-logo { font-family: var(--display); font-weight: 700; font-size: 1.1rem; letter-spacing: -.02em; }

.pa-play { width: 100%; max-width: 1040px; margin: 0 auto; padding: 0 1.5rem; flex-direction: row; gap: 2rem;
           align-items: flex-start; flex-wrap: wrap; }
.pa-stage { gap: .5rem; flex: 1 1 420px; animation: pa-rise .7s var(--ease) backwards; }
.pa-play-title { font-family: var(--display); font-weight: 700; font-size: clamp(1.8rem, 5vw, 2.6rem); letter-spacing: -.03em; line-height: 1.05; }
.pa-play-desc { color: var(--muted); margin-bottom: .75rem; }
.pa-bezel { padding: 10px; background: var(--surface); width: fit-content; max-width: 100%; border-radius: 22px;
            border: 1px solid color-mix(in srgb, var(--accent) 35%, var(--line));
            box-shadow: 0 30px 80px -30px color-mix(in srgb, var(--accent) 45%, transparent); }
.pa-screen { position: relative; min-width: min(420px, 85vw); min-height: 320px; background: #07070c; border-radius: 14px; overflow: hidden; }
.pa-screen img { max-height: 68vh; width: auto !important; max-width: 100%; margin: 0 auto; display: block; }

.pa-overlay { position: absolute; inset: 0; z-index: 5; align-items: center; justify-content: center; gap: 1.25rem;
              padding: 1.5rem; text-align: center; background: rgba(8,8,14,.72); backdrop-filter: blur(10px);
              opacity: 1; visibility: visible; transition: opacity .45s var(--ease), visibility .45s; }
.pa-overlay.pa-hidden { opacity: 0; visibility: hidden; pointer-events: none; }
.pa-msg { font-family: var(--mono); font-size: .85rem; letter-spacing: .05em; color: var(--muted); }

.pa-btn { font-family: var(--body) !important; font-weight: 600 !important; background: var(--accent) !important; color: #0b0b12 !important;
          border-radius: 12px !important; padding: .55rem 2rem !important;
          transition: transform .25s var(--ease), box-shadow .25s var(--ease) !important; }
.pa-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 28px -10px var(--accent); }
.pa-ghost { font-family: var(--body) !important; background: transparent !important; color: var(--muted) !important;
            border: 1px solid var(--line) !important; border-radius: 12px !important; margin-top: .5rem;
            transition: color .25s ease, border-color .25s ease !important; }
.pa-ghost:hover { color: var(--text) !important; border-color: var(--accent) !important; }

.pa-side { flex: 0 0 16rem; background: var(--surface); border: 1px solid var(--line); border-radius: 18px;
           padding: 1.4rem; gap: .35rem; animation: pa-rise .7s var(--ease) .12s backwards; }
.pa-side-title { margin-bottom: .75rem; font-family: var(--mono); font-size: .72rem; letter-spacing: .18em; text-transform: uppercase; color: var(--muted); }
.pa-ctl-key { width: fit-content; padding: .2rem .55rem; font-family: var(--mono); font-size: .78rem; font-weight: 500;
              background: rgba(255,255,255,.03); border: 1px solid var(--line); border-radius: 8px; }
.pa-ctl-act { color: var(--muted); font-size: .9rem; margin-bottom: .8rem; }
.pa-note { margin-top: .5rem; padding-top: .9rem; border-top: 1px solid var(--line); color: var(--muted); font-size: .85rem; line-height: 1.5; }

/* ---------- navbar + auth ---------- */
.pa-nav { background: rgba(11,11,18,.78) !important; color: var(--text) !important; padding: 0 !important;
          border-bottom: 1px solid var(--line); box-shadow: none !important;
          backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); }
.pa-nav-inner { width: 100%; max-width: 1040px; margin: 0 auto; padding: 0 1.5rem; min-height: 64px;
                display: flex; flex-direction: row; align-items: center; justify-content: space-between; }
.pa-nav-right { display: flex; align-items: center; gap: .4rem; }
.pa-nav-link { padding: .45rem .8rem; border-radius: 10px; color: var(--muted); font-size: .9rem; font-weight: 500;
               transition: color .25s ease, background .25s ease; }
.pa-nav-link:hover { color: var(--text); background: rgba(255,255,255,.05); }
.pa-nav-cta { padding: .5rem 1.1rem; border-radius: 10px; background: var(--accent); color: #0b0b12; font-size: .9rem; font-weight: 600;
              transition: transform .25s var(--ease), box-shadow .25s var(--ease); }
.pa-nav-cta:hover { transform: translateY(-2px); box-shadow: 0 10px 28px -10px var(--accent); }
/* ---------- homepage hero + background video ---------- */
html { scroll-behavior: smooth; }
.pa-bgvideo { position: fixed; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; }
.pa-bgshade { position: fixed; inset: 0; z-index: -1;
              background: linear-gradient(rgba(11,11,18,.55), rgba(11,11,18,.88)); }
.pa-hero { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center;
           text-align: center; padding: 6rem 1.5rem 4rem; }
.pa-hero .pa-logo { margin-top: 0; }
.pa-hero .pa-tagline { margin-left: auto; margin-right: auto; color: #cfcfe3; }
.pa-hero-btn { margin-top: 2.25rem; padding: .95rem 2.4rem; border-radius: 14px; background: var(--accent); color: #0b0b12;
               font-weight: 600; font-size: 1.05rem; animation: pa-rise .7s var(--ease) .16s backwards;
               transition: transform .25s var(--ease), box-shadow .25s var(--ease); }
.pa-hero-btn:hover { transform: translateY(-3px); box-shadow: 0 14px 34px -12px var(--accent); }
#games { scroll-margin-top: 80px; padding-top: 3rem; }
.pa-user { color: var(--text) !important; font-family: var(--body) !important; }

.pa-auth-wrap { width: 100%; align-items: center; padding: 4rem 1.5rem; }
.pa-auth-card { width: 100%; max-width: 400px; gap: .9rem; padding: 2rem; background: var(--surface); border: 1px solid var(--line);
                border-radius: 20px; box-shadow: 0 30px 80px -40px color-mix(in srgb, var(--accent) 50%, transparent);
                animation: pa-rise .7s var(--ease) backwards; }
.pa-auth-title { font-family: var(--display); font-weight: 700; font-size: 1.75rem; letter-spacing: -.03em; }
.pa-auth-sub { color: var(--muted); margin-top: -.5rem; margin-bottom: .5rem; }
.pa-error { min-height: 1.2rem; color: #ff6b81; font-size: .85rem; }
.pa-auth-alt { gap: .4rem; color: var(--muted); font-size: .9rem; }
.pa-auth-alt a { color: var(--accent); font-weight: 600; }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
"""
ui.add_head_html(FONTS, shared=True)
ui.add_css(CSS, shared=True)
