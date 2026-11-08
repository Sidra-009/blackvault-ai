"""Look and feel for BlackVault AI: CSS, animations, logo, icons and small HTML builders.
Pure HTML and CSS (no JavaScript). Animations switch off for people who prefer reduced motion."""

COLORS = {"red": "#ef4444", "amber": "#f59e0b", "green": "#22c55e"}

CSS = """
<style>
@property --n {syntax: '<integer>'; initial-value: 0; inherits: false;}

/* ---------- background: slow aurora + faint grid ---------- */
.stApp {background: #0b0f17;}
.stApp::before {content: ""; position: fixed; inset: -25%; z-index: 0; pointer-events: none; opacity: 0.55; filter: blur(70px);
  background: radial-gradient(40% 35% at 20% 25%, rgba(45,212,191,0.35), transparent 70%),
              radial-gradient(35% 30% at 80% 20%, rgba(56,189,248,0.28), transparent 70%),
              radial-gradient(40% 35% at 60% 85%, rgba(129,140,248,0.22), transparent 70%);
  animation: drift 26s ease-in-out infinite alternate;}
.stApp::after {content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background-image: linear-gradient(rgba(45,212,191,0.045) 1px, transparent 1px), linear-gradient(90deg, rgba(45,212,191,0.045) 1px, transparent 1px);
  background-size: 52px 52px;
  -webkit-mask-image: radial-gradient(ellipse at 50% 20%, #000 0%, transparent 75%);
  mask-image: radial-gradient(ellipse at 50% 20%, #000 0%, transparent 75%);}
[data-testid="stMain"] {position: relative; z-index: 1;}
.block-container {max-width: 1020px; padding-top: 4.5rem;}

/* ---------- keyframes ---------- */
@keyframes drift {from {transform: translate3d(-3%, -2%, 0) scale(1);} to {transform: translate3d(4%, 3%, 0) scale(1.12);}}
@keyframes riseIn {from {opacity: 0; transform: translateY(18px) scale(0.98);} to {opacity: 1; transform: none;}}
@keyframes slideIn {from {opacity: 0; transform: translateX(-16px);} to {opacity: 1; transform: none;}}
@keyframes shimmer {from {background-position: 0% 0;} to {background-position: 300% 0;}}
@keyframes spin {to {transform: rotate(360deg);}}
@keyframes glowPulse {0%,100% {filter: drop-shadow(0 0 4px rgba(45,212,191,0.45));} 50% {filter: drop-shadow(0 0 15px rgba(45,212,191,0.95));}}
@keyframes glowRed {0%,100% {box-shadow: 0 0 0 rgba(239,68,68,0);} 50% {box-shadow: 0 0 30px rgba(239,68,68,0.45);}}
@keyframes glowAmber {0%,100% {box-shadow: 0 0 0 rgba(245,158,11,0);} 50% {box-shadow: 0 0 26px rgba(245,158,11,0.35);}}
@keyframes glowGreen {0%,100% {box-shadow: 0 0 0 rgba(34,197,94,0);} 50% {box-shadow: 0 0 24px rgba(34,197,94,0.30);}}
@keyframes gaugeFill {from {stroke-dasharray: 0 157.1;} to {stroke-dasharray: var(--to) 157.1;}}
@keyframes count {from {--n: 0;}}
@keyframes draw {to {stroke-dashoffset: 0;}}
@keyframes sweep {from {left: -150px;} to {left: 112%;}}
@keyframes flash {0% {box-shadow: 0 0 0 0 rgba(239,68,68,0.9);} 100% {box-shadow: 0 0 0 12px rgba(239,68,68,0);}}
@keyframes pop {from {opacity: 0; transform: scale(0.6);} to {opacity: 1; transform: scale(1);}}
@keyframes iconPulse {0%,100% {transform: scale(1);} 50% {transform: scale(1.13);}}

/* ---------- hero ---------- */
.hero {display: flex; align-items: center; gap: 16px;}
.hero h1 {margin: 0; padding: 0; font-size: 2.6rem; font-weight: 800; letter-spacing: -0.8px; line-height: 1.1;
  background: linear-gradient(90deg, #e6edf3 0%, #2dd4bf 25%, #38bdf8 50%, #e6edf3 75%, #e6edf3 100%); background-size: 300% 100%;
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent;
  animation: shimmer 9s linear infinite;}
.hero .sub {opacity: 0.7; font-size: 0.95rem; letter-spacing: 1px; margin-top: 4px; text-transform: uppercase;}
.logo-wrap svg {animation: glowPulse 3.2s ease-in-out infinite;}
.dial {transform-box: fill-box; transform-origin: center; animation: spin 22s linear infinite;}
.sbrand {margin-bottom: 18px;}
.tag {opacity: 0.88; margin: 14px 0 16px 0; font-size: 1.05rem;}

/* ---------- result tiles ---------- */
.tiles {display: grid; grid-template-columns: 2fr 1.3fr 1.1fr; gap: 14px; margin: 16px 0 8px 0;}
@media (max-width: 760px) {.tiles {grid-template-columns: 1fr;}}
.tile {position: relative; border-radius: 16px; padding: 18px 20px; background: rgba(18,24,38,0.74);
  -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.09);
  animation: riseIn .65s cubic-bezier(.2,.8,.2,1) backwards; transition: transform .25s ease, border-color .25s ease;}
.tile:nth-child(2) {animation-delay: .12s;}
.tile:nth-child(3) {animation-delay: .24s;}
.tile:hover {transform: translateY(-4px); border-color: rgba(45,212,191,0.55);}
.tile .lab {font-size: 0.76rem; text-transform: uppercase; letter-spacing: 1.2px; opacity: 0.62;}
.tile .val {font-size: 1.4rem; font-weight: 700; margin-top: 4px;}
.tile .sub {font-size: 0.92rem; opacity: 0.85; margin-top: 4px;}
.tile.red {border-left: 6px solid #ef4444; background: linear-gradient(135deg, rgba(239,68,68,0.22), rgba(18,24,38,0.78));
  animation: riseIn .65s cubic-bezier(.2,.8,.2,1) backwards, glowRed 2.6s ease-in-out .8s infinite;}
.tile.amber {border-left: 6px solid #f59e0b; background: linear-gradient(135deg, rgba(245,158,11,0.18), rgba(18,24,38,0.78));
  animation: riseIn .65s cubic-bezier(.2,.8,.2,1) backwards, glowAmber 3s ease-in-out .8s infinite;}
.tile.green {border-left: 6px solid #22c55e; background: linear-gradient(135deg, rgba(34,197,94,0.16), rgba(18,24,38,0.78));
  animation: riseIn .65s cubic-bezier(.2,.8,.2,1) backwards, glowGreen 3.4s ease-in-out .8s infinite;}
.vrow {display: flex; align-items: center; gap: 14px; margin-top: 6px;}
.vrow .val {margin-top: 0;}
.vicon svg {display: block; animation: iconPulse 2.4s ease-in-out infinite;}
.draw {stroke-dasharray: 40; stroke-dashoffset: 40; animation: draw .8s ease-out .35s forwards;}
.score {font-size: 2.5rem; font-weight: 800; line-height: 1.05;}
.num {--n: var(--t); counter-reset: n var(--n); animation: count 1.4s cubic-bezier(.2,.8,.2,1) .2s backwards;}
.num::after {content: counter(n);}
.gauge path.fill {animation: gaugeFill 1.4s cubic-bezier(.2,.8,.2,1) .2s backwards;}

/* ---------- chips, boxes, lists ---------- */
.chip {display: inline-block; padding: 4px 12px; margin: 2px 6px 2px 0; border-radius: 999px; font-size: 0.86rem;
  background: rgba(45,212,191,0.16); border: 1px solid rgba(45,212,191,0.5); animation: pop .5s cubic-bezier(.2,.9,.3,1.3) .5s backwards;}
.basis {opacity: 0.7; font-size: 0.88rem; margin: 2px 0 10px 0;}
.msgbox {position: relative; overflow: hidden; border-radius: 14px; padding: 18px; line-height: 2; font-size: 1.05rem;
  background: rgba(18,24,38,0.74); border: 1px solid rgba(255,255,255,0.09);}
.msgbox::after {content: ""; position: absolute; top: 0; bottom: 0; left: -150px; width: 110px; pointer-events: none;
  background: linear-gradient(90deg, transparent, rgba(45,212,191,0.38), transparent); animation: sweep 1.5s ease-out .25s 1 backwards;}
.msgbox mark {border-radius: 5px; padding: 1px 4px; color: inherit; animation: flash 1.1s ease-out .9s backwards;}
.flag, .step {animation: slideIn .5s cubic-bezier(.2,.8,.2,1) backwards; animation-delay: calc(var(--i, 0) * 90ms);}
.flag {padding: 10px 6px; border-bottom: 1px solid rgba(255,255,255,0.10);}
.step {padding: 12px 16px; margin: 8px 0; border-radius: 12px; background: rgba(18,24,38,0.74); border: 1px solid rgba(255,255,255,0.09);
  transition: background .25s ease, border-color .25s ease;}
.step:hover {background: rgba(45,212,191,0.10); border-color: rgba(45,212,191,0.45);}
.urlbox {border-radius: 12px; padding: 12px 16px; margin: 8px 0; background: rgba(18,24,38,0.74); border: 1px solid rgba(255,255,255,0.09);
  animation: riseIn .5s cubic-bezier(.2,.8,.2,1) backwards;}
.urlbox code {word-break: break-all;}
.guide {border-radius: 14px; padding: 16px 18px; margin: 12px 0; background: rgba(18,24,38,0.74); border: 1px solid rgba(255,255,255,0.09);
  animation: riseIn .6s cubic-bezier(.2,.8,.2,1) backwards; animation-delay: calc(var(--i, 0) * 110ms);
  transition: transform .25s ease, border-color .25s ease;}
.guide:hover {transform: translateY(-3px); border-color: rgba(45,212,191,0.5);}
.guide h4 {margin: 0 0 6px 0;}
.foot {opacity: 0.55; font-size: 0.85rem; margin-top: 30px;}

/* ---------- controls ---------- */
[data-testid="stBaseButton-primary"], button[kind="primary"] {
  background: linear-gradient(135deg, #2dd4bf, #38bdf8) !important; border: 0 !important; font-weight: 700 !important;
  transition: transform .15s ease, box-shadow .25s ease !important;}
[data-testid="stBaseButton-primary"] p, button[kind="primary"] p {color: #06202a !important; font-weight: 700;}
[data-testid="stBaseButton-primary"]:hover, button[kind="primary"]:hover {transform: translateY(-2px); box-shadow: 0 10px 28px rgba(45,212,191,0.45) !important;}
[data-testid="stBaseButton-primary"]:active, button[kind="primary"]:active {transform: translateY(0) scale(0.98);}
[data-testid="stBaseButton-secondary"], button[kind="secondary"] {transition: transform .15s ease, border-color .2s ease, box-shadow .25s ease !important;}
[data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover {transform: translateY(-2px); border-color: #2dd4bf !important; box-shadow: 0 6px 20px rgba(45,212,191,0.25) !important;}
textarea {transition: box-shadow .25s ease !important;}
textarea:focus {box-shadow: 0 0 0 1px #2dd4bf, 0 0 26px rgba(45,212,191,0.28) !important;}
button[data-baseweb="tab"] {transition: color .2s ease, transform .2s ease;}
button[data-baseweb="tab"]:hover {transform: translateY(-1px);}
[data-baseweb="tab-panel"] {animation: riseIn .45s ease backwards;}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {animation: none !important; transition: none !important;}
  .draw {stroke-dashoffset: 0;}
}
</style>
"""

LOGO = (
    '<span class="logo-wrap"><svg viewBox="0 0 72 72" width="{s}" height="{s}">'
    '<path d="M36 4 L64 14 V36 C64 52 52 63 36 68 C20 63 8 52 8 36 V14 Z" fill="#0b1220" stroke="#2dd4bf" stroke-width="3"/>'
    '<g class="dial"><circle cx="36" cy="37" r="17" fill="none" stroke="#2dd4bf" stroke-width="3"/>'
    '<g stroke="#2dd4bf" stroke-width="2.5" stroke-linecap="round">'
    '<line x1="36" y1="17" x2="36" y2="21"/><line x1="36" y1="53" x2="36" y2="57"/>'
    '<line x1="16" y1="37" x2="20" y2="37"/><line x1="52" y1="37" x2="56" y2="37"/></g></g>'
    '<circle cx="36" cy="37" r="11" fill="#12202f" stroke="#38bdf8" stroke-width="2"/>'
    '<circle cx="36" cy="34" r="3.6" fill="#2dd4bf"/><path d="M34 36 H38 L39.5 44 H32.5 Z" fill="#2dd4bf"/></svg></span>'
)


def logo(size=58):
    return LOGO.replace("{s}", str(size))


def icon(color_key):
    c = COLORS[color_key]
    if color_key == "green":
        body = (f'<circle cx="24" cy="24" r="21" fill="none" stroke="{c}" stroke-width="3"/>'
                f'<path class="draw" d="M14 25 L21 32 L34 17" fill="none" stroke="{c}" stroke-width="4" '
                'stroke-linecap="round" stroke-linejoin="round"/>')
    elif color_key == "amber":
        body = (f'<path d="M24 5 L45 41 H3 Z" fill="none" stroke="{c}" stroke-width="3" stroke-linejoin="round"/>'
                f'<line x1="24" y1="18" x2="24" y2="29" stroke="{c}" stroke-width="3.5" stroke-linecap="round"/>'
                f'<circle cx="24" cy="35" r="2.2" fill="{c}"/>')
    else:
        body = (f'<path d="M24 4 L42 11 V24 C42 35 34 42 24 45 C14 42 6 35 6 24 V11 Z" fill="none" stroke="{c}" stroke-width="3" stroke-linejoin="round"/>'
                f'<path d="M17 17 L31 31 M31 17 L17 31" stroke="{c}" stroke-width="3.5" stroke-linecap="round"/>')
    return f'<span class="vicon"><svg viewBox="0 0 48 48" width="42" height="42">{body}</svg></span>'


def gauge(risk, color_key):
    arc = 157.1
    c = COLORS[color_key]
    filled = risk * arc
    return (
        '<svg class="gauge" viewBox="0 0 120 66" width="140" height="77">'
        '<path d="M10 60 A50 50 0 0 1 110 60" fill="none" stroke="rgba(255,255,255,0.14)" stroke-width="10" stroke-linecap="round"/>'
        f'<path class="fill" d="M10 60 A50 50 0 0 1 110 60" fill="none" stroke="{c}" stroke-width="10" stroke-linecap="round" '
        f'stroke-dasharray="{filled:.1f} {arc}" style="--to:{filled:.1f}"/></svg>'
    )


def tiles_html(T, title, sub, color, risk, lang_name):
    pct = round(risk * 100)
    c = COLORS[color]
    return f"""<div class="tiles">
<div class="tile {color}"><div class="lab">{T['t_verdict']}</div>
<div class="vrow">{icon(color)}<div class="val">{title}</div></div><div class="sub">{sub}</div></div>
<div class="tile"><div class="lab">{T['t_score']}</div>{gauge(risk, color)}
<div class="score" style="color:{c}"><span class="num" style="--t:{pct}"></span>%</div><div class="sub">{T['score_note']}</div></div>
<div class="tile"><div class="lab">{T['t_lang']}</div><div class="val" style="margin-top:10px">{lang_name}</div></div>
</div>"""


def flag_html(text, i):
    return f'<div class="flag" style="--i:{i}">{text}</div>'


def step_html(n, text):
    return f'<div class="step" style="--i:{n}"><b>{n}.</b> {text}</div>'
