#!/usr/bin/env python3
"""Build a side-scrolling walkthrough of numbered screenshots from a JSON spec.

usage: python3 -I build_report.py spec.json out.html            # standalone report
       python3 -I build_report.py spec.json embed.html --embed    # T3 html_render
       python3 -I build_report.py spec.json out.html --embed --split
           # one page per flow "group" (out-<group>.html) plus an index (out.html)

spec = {"title": str, "note": str,
        "flows": [{"title": str, "status": str, "group": str, "steps": [step, ...]}],  # status, group optional
        "asks": [{"quote": str, "on": str, "did": str, "flow": int|None, "status": str}],
        # asks = EVERY request the user made, questions included: "quote" = their exact words,
        # "on" = what it was attached to (optional), "did" = what you did or the answer in a
        # sentence or two, "status" = required (done, answered, partial, not done, ...), "flow" =
        # 1-based section that shows it (printed inside that section), or None for a question or
        # non-visual ask. The report ends with an "Everything you asked" checklist of all of them,
        # so a dropped ask is visible. flow None: also answer it in full in the chat.
        "limits": [str]}          # limits = honest "not verified / known gaps"
step = {"img": "/abs.png", "caption": str}                        # one screenshot (a full-page one scrolls in a 620px box)
     | {"html": "<div class=x-row>...</div>", "caption": str}      # an explanation (see XP_CSS)
     | {"before": "/abs.png", "after": "/abs.png", "caption": str}  # drag-to-compare
     # add "full_page": true to a pair whose Before and After are full-page captures: a different height is then fine
# optional on a step: "detail": str = the technical evidence (numbers, DOM text, file names) in small
# muted type under the shot, so "caption" stays plain words. Optional on a flow: "summary": str =
# one plain sentence under the title saying what the section is about and how it ended.

Every page opens with a sticky jump bar (counts by status, a numbered link per section). The
embed keeps its height bounded: the sections scroll inside a fixed-height box (html_render
rejects vh units and fits the frame to the page, so the cap is in px). Before/after pairs
are letterboxed, never cropped; the builder warns when the two sizes differ by over 3%.

Standalone: one self-contained file (images as base64 JPEG). Clicking a shot opens a
full-window viewer (arrows / Esc, click to zoom 1:1, drag to pan). Linked from a chat
reply as a plain absolute path to the .html, T3 opens it in its side browser panel.
Nothing here enters the model's context: do not Read the output.

--embed: small JPEGs next to the output (embed-img/<name>/NN.jpg) and a page that references
them by LITERAL absolute path in src="...". T3's html_render inlines only literal
absolute image paths (a regex over the HTML); a path assembled in JS stays broken.
In the chat frame a click on a shot is left to T3, which opens the image in its viewer;
before/after pairs slide.

Colours: both modes use T3's theme variable names. The embed gets T3's live values;
the standalone file defines neutral light/dark fallbacks for the same names. Never
hardcode a colour anywhere else.
"""
import base64, html, io, json, os, re, sys
from PIL import Image

E = html.escape

# Fallback values for T3's theme variables, standalone report only. In the embed T3
# injects these itself; defining them there would override the user's theme.
FALLBACK_VARS = """:root{color-scheme:light dark;--background:#fafafa;--foreground:#18181b;--card:#fff;--card-foreground:#18181b;--muted-foreground:#71717a;--border:#e4e4e7;--ring:#3b82f6;--accent:#2563eb;--accent-foreground:#fff;--success:#16a34a;--info:#0284c7;--warning:#d97706;--destructive:#dc2626;--radius:8px;--font-sans:system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root{--background:#0c0c0f;--foreground:#f4f4f5;--card:#17171c;--card-foreground:#f4f4f5;--muted-foreground:#a1a1aa;--border:#2a2a32;--ring:#60a5fa;--accent:#60a5fa;--accent-foreground:#0c0c0f;--success:#4ade80;--info:#38bdf8;--warning:#fbbf24;--destructive:#f87171}}
body{background:var(--background);padding:24px;max-width:1400px;margin:0 auto}
h1{font-size:26px;margin:0 0 8px}.note{color:var(--muted-foreground);margin:0 0 24px}"""

# Kit for explanation steps ({"html": ...}): boxes in a row joined by arrows, notes, code.
# Agents compose these (or inline SVG with viewBox) instead of styling from scratch.
XP_CSS = """.card.xp{flex-basis:min(96%,1000px)}
.xp .x{font-size:14px;line-height:1.55}
.x-row{display:flex;gap:10px;align-items:stretch;flex-wrap:wrap;margin:10px 0}
.x-box{flex:1 1 150px;padding:10px 12px;border:1px solid var(--border);border-radius:var(--radius);background:color-mix(in srgb,var(--foreground) 4%,var(--card));font-size:14px;line-height:1.5}
.x-box b{display:block;margin-bottom:2px}.x-box.hot{border-color:var(--accent)}
.x-arrow{align-self:center;color:var(--muted-foreground);font-size:18px}
.x-note{font-size:13px;line-height:1.5;color:var(--muted-foreground);margin:6px 0}
.x-code{font-family:var(--font-mono,monospace);font-size:12.5px}
.xp svg{max-width:100%;height:auto}.xp svg text{fill:currentColor;font-family:var(--font-sans)}
"""

CSS = XP_CSS + """body{margin:0;font-family:var(--font-sans);color:var(--foreground)}
.flow{margin:0 0 30px}
.flow h3{font-size:20px;font-weight:700;margin:0 0 2px;color:var(--accent,var(--primary))}
.sum{font-size:15px;line-height:1.55;margin:0 0 6px}
.detail{font-size:12.5px;line-height:1.5;color:var(--muted-foreground);margin:10px 0 0}
.hint{font-size:13px;color:var(--muted-foreground);margin:0 0 12px}
.row{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:10px;scrollbar-width:thin}
.card{flex:0 0 min(92%,1000px);scroll-snap-align:start;margin:0;padding:12px;background:var(--card);color:var(--card-foreground);border:1px solid var(--border);border-radius:calc(var(--radius) + 4px);box-sizing:border-box}
.card.tall{flex-basis:min(80%,380px)}
.lw{max-height:620px;overflow-y:auto;border-radius:var(--radius);scrollbar-width:thin}
.card figcaption{display:flex;gap:10px;align-items:flex-start;font-size:15px;line-height:1.55;margin:0 0 12px;min-height:3.1em}
.n{flex:0 0 26px;height:26px;border-radius:50%;background:var(--accent,var(--primary));color:var(--accent-foreground,var(--primary-foreground));font-weight:700;font-size:13px;display:grid;place-items:center;margin-top:1px}
.shot{border-radius:var(--radius);overflow:hidden;cursor:zoom-in;user-select:none}
.shot img{width:100%;display:block;-webkit-user-drag:none}
ul{font-size:14px;line-height:1.6;color:var(--muted-foreground);padding-left:20px}
.flow{scroll-margin-top:56px}
.jump{position:sticky;top:0;z-index:5;display:flex;gap:6px;align-items:center;overflow-x:auto;white-space:nowrap;padding:8px 12px;margin:0 0 14px;background:var(--card);color:var(--card-foreground);border:1px solid var(--border);border-radius:var(--radius);font-size:13px;scrollbar-width:thin}
.jump .cnt{display:inline-flex;gap:5px;align-items:center;margin-right:6px;font-weight:600}
.jump .cnt::before,.jump a::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--c,var(--border))}
.jump a{display:inline-flex;gap:4px;align-items:center;padding:2px 8px;border:1px solid var(--border);border-radius:999px;color:inherit;text-decoration:none}
.jump a:hover{border-color:var(--ring)}.jump .sep{width:1px;align-self:stretch;background:var(--border);margin:0 4px}
.part{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap;padding:10px 0;border-top:1px solid var(--border)}
.part h3{margin:0}.part ol{margin:4px 0 0;padding-left:22px;width:100%;color:inherit;font-size:14px}
.st{display:inline-flex;align-items:center;gap:6px;vertical-align:middle;margin-left:10px;font-size:12px;font-weight:600;padding:2px 9px;border-radius:999px;border:1px solid var(--c);color:var(--foreground)}
.st::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--c)}"""

# Issue status -> theme colour. Colour sits on the border and dot, never a fill.
STATUS = {"fixed": "--success", "partial": "--warning", "needs decision": "--warning",
          "not fixed": "--destructive", "unverified": "--warning", "answered": "--info", "current design": "--info", "not reproduced": "--muted-foreground"}

# Embed: a scroll box with the jump bar. Clicking a shot is left to T3, which opens the image
# in its own viewer. (A click-to-magnify lens used to live here; it fought that viewer, so it was removed.)
EMBED_CSS = """.scroller{box-sizing:border-box;max-height:680px;overflow-y:auto;position:relative;padding:0 12px 12px;border:1px solid var(--border);border-radius:var(--radius);scrollbar-width:thin}
.scroller .jump{margin:0 -12px 14px;border-radius:var(--radius) var(--radius) 0 0;border-width:0 0 1px}
.shot:not(.cmp){cursor:pointer}"""
EMBED_JS = """(()=>{const sc=document.querySelector('.scroller'),jb=sc.querySelector('.jump');const fit=()=>{sc.style.maxHeight=(innerHeight>800?innerHeight-2:680)+'px'};fit();addEventListener('resize',fit);jb.addEventListener('click',e=>{const a=e.target.closest('a[href^="#flow"]');if(!a)return;e.preventDefault();const t=sc.querySelector(a.getAttribute('href'));sc.scrollTo({top:t.getBoundingClientRect().top-sc.getBoundingClientRect().top+sc.scrollTop-jb.offsetHeight-8,behavior:'smooth'})});})();"""

# Before/after: both shots stacked, the "after" clipped by a slider. Same route, same
# viewport, same state, or the two will not line up. The box takes the taller of the two
# (at equal width) and both are letterboxed inside it with object-fit:contain, top-aligned:
# at the same scale, never cropped. (It used to be object-fit:cover, which cut the After
# whenever its aspect ratio differed from the Before's.)
CMP_CSS = """.cmp{position:relative;overflow:hidden;border-radius:var(--radius);cursor:ew-resize;background:color-mix(in srgb,var(--foreground) 7%,var(--card))}
.cmp img{position:absolute;inset:0;width:100%;height:100%;display:block;object-fit:contain;object-position:top;background:color-mix(in srgb,var(--foreground) 7%,var(--card))}
.cmp .after{clip-path:inset(0 0 0 var(--x,50%))}
.cmp .bar{position:absolute;top:0;bottom:0;left:var(--x,50%);width:2px;background:var(--ring);pointer-events:none}
.cmp .tag{position:absolute;top:8px;font-size:12px;font-weight:700;padding:2px 8px;border-radius:999px;background:var(--card);color:var(--card-foreground);border:1px solid var(--border);pointer-events:none}
.cmp .tb{left:8px}.cmp .ta{right:8px}
.cmp input{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0;cursor:ew-resize}"""
CMP_JS = """document.querySelectorAll('.cmp input').forEach(i=>i.addEventListener('input',()=>i.parentNode.style.setProperty('--x',i.value+'%')));"""

# Standalone: a proper full-window viewer.
VIEWER_CSS = """.lb{position:fixed;inset:0;z-index:9;display:none;flex-direction:column;background:var(--background)}
.lb.open{display:flex}.lb header{display:flex;gap:12px;align-items:center;padding:10px 16px;border-bottom:1px solid var(--border);font-size:15px}
.lb header .cap{flex:1;min-width:0}.lb button{font:inherit;min-width:44px;min-height:44px;border-radius:var(--radius);border:1px solid var(--border);background:var(--card);color:var(--foreground);cursor:pointer}
.lb .stage{flex:1;overflow:auto;display:flex;cursor:zoom-in}.lb .stage img{margin:auto;max-width:100%;max-height:100%;display:block}
.cmp .tag{pointer-events:auto;z-index:2;cursor:zoom-in}.lb .stage.full{cursor:grab}.lb .stage.full img{max-width:none;max-height:none}"""
VIEWER_HTML = """<div class=lb role=dialog aria-modal=true><header><button data-a=prev aria-label="Previous">&larr;</button><span class=cap></span><button data-a=zoom>1:1</button><button data-a=next aria-label="Next">&rarr;</button><button data-a=close aria-label="Close">&times;</button></header><div class=stage><img alt=""></div></div>"""
VIEWER_JS = """(()=>{const shots=[...document.querySelectorAll('.shot img')],tags=[...document.querySelectorAll('.cmp .tag')],lb=document.querySelector('.lb'),st=lb.querySelector('.stage'),im=st.querySelector('img'),cap=lb.querySelector('.cap');let i=0,d=null;
const show=n=>{i=(n+shots.length)%shots.length;im.src=shots[i].src;const f=shots[i].closest('figure');cap.textContent=f.closest('section').querySelector('h3').textContent+' \\u2014 '+f.querySelector('figcaption').textContent+(shots[i].dataset.v?' ('+shots[i].dataset.v+')':'');st.classList.remove('full');lb.classList.add('open')};
const zoom=()=>st.classList.toggle('full');
shots.forEach((s,n)=>{if(!s.dataset.v)s.closest('.shot').addEventListener('click',()=>show(n))});tags.forEach(t=>t.addEventListener('click',()=>show(shots.indexOf(t.parentNode.querySelector(t.classList.contains('tb')?'.before':'.after')))));
lb.addEventListener('click',e=>{const a=e.target.closest('button')?.dataset.a;if(a==='prev')show(i-1);if(a==='next')show(i+1);if(a==='zoom')zoom();if(a==='close')lb.classList.remove('open')});
st.addEventListener('pointerdown',e=>{d={x:e.clientX,y:e.clientY,l:st.scrollLeft,u:st.scrollTop,m:false}});
st.addEventListener('pointermove',e=>{if(!d||!st.classList.contains('full'))return;const dx=e.clientX-d.x,dy=e.clientY-d.y;if(Math.abs(dx)+Math.abs(dy)>4)d.m=true;st.scrollLeft=d.l-dx;st.scrollTop=d.u-dy});
st.addEventListener('pointerup',()=>{if(d&&!d.m)zoom();d=null});
document.addEventListener('keydown',e=>{if(!lb.classList.contains('open'))return;if(e.key==='Escape')lb.classList.remove('open');if(e.key==='ArrowLeft')show(i-1);if(e.key==='ArrowRight')show(i+1)})})();"""


# One page scrolls fine to this many sections (the jump bar keeps it navigable). Splitting
# earlier only makes the reader open more pages. Parts should stay few and substantial.
SPLIT_OVER, MAX_PARTS, MIN_PART = 25, 4, 6

MIN_WIDTH = 1100  # a 1280-wide capture is the norm; anything below this will look soft
PHONE_MAX_WIDTH = 900  # wider portrait shots are full-page desktop captures, not phones
LONG_RATIO, LONG_BOX = 1.8, 620  # taller than 1.8x its width: scroll inside a 620px box
TALL_MIN_WIDTH = 720  # a phone shot is shown 380px wide, so 2x that is sharp


def is_tall(path):
    """A portrait screenshot (a phone screen). It is shown at phone width, not the
    full card width, or a 1080x2340 shot fills several screens of scrolling."""
    w, h = Image.open(path).size
    return h > w * 1.3 and w <= PHONE_MAX_WIDTH


def is_long(path):
    """A full-page desktop capture (much taller than wide). Shown at full card width inside
    a box that scrolls, so a 6000px page is readable without a 4000px card."""
    w, h = Image.open(path).size
    return h > w * LONG_RATIO and w > PHONE_MAX_WIDTH


def check_resolution(spec):
    """Refuse low-resolution screenshots. A 640x400 PNG shown at the card's ~950px
    width is upscaled ~1.5x and reads as blur, and nothing downstream can fix that.
    Set "allow_low_res": true in the spec only for a deliberately small capture."""
    low = []
    for flow in spec["flows"]:
        for st in flow["steps"]:
            for k in ("img", "before", "after"):
                if k in st:
                    w = Image.open(st[k]).width
                    if w < (TALL_MIN_WIDTH if is_tall(st[k]) else MIN_WIDTH):
                        low.append(f"{st[k]} is {w}px wide")
    if low and not spec.get("allow_low_res"):
        sys.exit("low-resolution screenshots (need >= %dpx wide, or %dpx for a portrait phone shot), "
                 "retake them (see SKILL.md 'Sharp screenshots'):\n  " % (MIN_WIDTH, TALL_MIN_WIDTH) + "\n  ".join(low))


def jpeg(path, width, quality):
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, int(im.height * width / im.width)))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=quality)
    return buf.getvalue()


SIZE_TOLERANCE = 0.03  # warn when a before/after pair differs in width or height by more than this


def check_pair(label, st):
    """Warn about a Before/After pair that was not shot the same way. The slider
    letterboxes, so nothing is cut, but a different size means a different viewport,
    zoom, crop or scroll, and the pair will not line up."""
    (bw, bh), (aw, ah) = Image.open(st["before"]).size, Image.open(st["after"]).size
    dw, dh = abs(aw - bw) / bw, abs(ah - bh) / bh
    if st.get("full_page"):
        dh = 0  # a full-page pair differs in height when the fix changed the page length
    if dw > SIZE_TOLERANCE or dh > SIZE_TOLERANCE:
        print(f"warning: {label}: before is {bw}x{bh}, after is {aw}x{ah} "
              f"(width {dw:.0%}, height {dh:.0%} apart): retake with the same viewport, crop and scroll",
              file=sys.stderr)


def pair_ratio(st):
    """aspect-ratio (w/h) for the compare box: the taller of the two at equal width."""
    ratios = [Image.open(st[k]).height / Image.open(st[k]).width for k in ("before", "after")]
    return f"1000/{round(1000 * max(ratios))}"


def jump_bar(flows, href=lambda i: f"#flow{i}", static=False, pills=True):
    """Strip of counts by status, then a numbered link per section (href None: plain
    labels). Sticky unless static."""
    counts = {}
    for f in flows:
        if f.get("status"):
            counts[f["status"]] = counts.get(f["status"], 0) + 1
    cnt = "".join(f'<span class=cnt style="--c:var({STATUS[k]})">{v} {E(k)}</span>' for k, v in counts.items())
    tag, attr = ("a", lambda i: f' href="{href(i)}"') if href else ("span", lambda i: "")
    links = "".join(f'<{tag}{attr(i)} title="{E(f["title"])}"'
                    + (f' style="--c:var({STATUS[f["status"]]})"' if f.get("status") else "")
                    + f">{i}</{tag}>" for i, f in enumerate(flows, 1)) if pills else ""
    style = ' style="position:static;margin:0;border:0;padding:6px 0;background:none"' if static else ""
    return f'<nav class=jump{style}>{cnt}{"<span class=sep></span>" if cnt and links else ""}{links}</nav>'


ASK_CSS = """.asklist{list-style:none;margin:0;padding:0}.asklist li{padding:8px 0;border-top:1px solid var(--border);font-size:14px;line-height:1.5;color:var(--foreground)}
.asklist q{font-weight:600}.asklist .did{display:block;color:var(--muted-foreground)}.asklist a{color:var(--accent);margin-left:8px}.asklist .where{margin-left:8px;color:var(--muted-foreground)}"""

# Active opening of an event handler or script in an explanation: those would run in the report.
UNSAFE_HTML = re.compile(r"<script|\son\w+\s*=|javascript:", re.I)


def ask_checklist(asks, link=None):
    """The closing 'Everything you asked' section: every ask once, with its status and where
    it is shown. link(ask) -> (href, label) or None. This is what makes a dropped ask visible."""
    counts = {}
    for a in asks:
        counts[a["status"]] = counts.get(a["status"], 0) + 1
    bar = "".join(f'<span class=cnt style="--c:var({STATUS[k]})">{v} {E(k)}</span>' for k, v in counts.items())
    rows = []
    for a in asks:
        where = link(a) if link else None
        rows.append(f'<li><q>{E(a["quote"])}</q><span class=st style="--c:var({STATUS[a["status"]]})">{E(a["status"])}</span>'
                    + ((f'<a href="{E(where[0])}">{E(where[1])}</a>' if where[0] else f'<span class=where>{E(where[1])}</span>') if where else '<span class=where>answered in the chat</span>')
                    + f'<span class=did>{E(a["did"])}</span></li>')
    return (f'<section class=flow id=asks><style>{ASK_CSS}</style><h3>Everything you asked &middot; {len(asks)} ask{"s" * (len(asks) != 1)}</h3>'
            f'<nav class=jump style="position:static;margin:0 0 8px;border:0;padding:4px 0;background:none">{bar}</nav><ul class=asklist>{"".join(rows)}</ul></section>')


def check_asks(asks, nflows):
    """Every ask needs its words, what was done, a known status and a section (or None)."""
    bad = [a for a in asks if not a.get("quote") or not a.get("did") or a.get("status") not in STATUS
           or (a.get("flow") is not None and not 1 <= a["flow"] <= nflows)]
    if bad:
        sys.exit("asks need 'quote', 'did', a 'status' (one of %s) and a 'flow' of 1..%d (or null): %r"
                 % (sorted(STATUS), nflows, bad))


def slug(text):
    return "".join(c if c.isalnum() else "-" for c in text.lower()).strip("-") or "part"


def split_spec(spec):
    """One sub-spec per flow 'group' (in first-seen order). Asks are re-pointed at the
    flow's new number; asks with flow None stay in the index only."""
    order, groups = [], {}
    for fi, f in enumerate(spec["flows"], 1):
        g = f.get("group") or "Other"
        if g not in groups:
            order.append(g); groups[g] = []
        groups[g].append(fi)
    parts = []
    for g in order:
        idx = groups[g]
        asks = [dict(a, flow=idx.index(a["flow"]) + 1) for a in spec.get("asks") or [] if a.get("flow") in idx]
        parts.append((g, {"title": f"{spec['title']}: {g}", "flows": [spec["flows"][i - 1] for i in idx],
                          "asks": asks, "allow_low_res": spec.get("allow_low_res")}))
    return parts


def build_index(spec, parts, out_path, embed, names):
    """The index page: one block per part with its counts by status and its sections. No images."""
    head = CSS + (EMBED_CSS if embed else FALLBACK_VARS)
    out = [f"<!doctype html><html><head><meta charset=utf-8><title>{E(spec['title'])}</title><style>{head}</style></head><body>"]
    out.append("<div class=scroller>" if embed else f"<h1>{E(spec['title'])}</h1>")
    if spec.get("note") and not embed:
        out.append(f"<p class=note>{E(spec['note'])}</p>")
    for (g, sub), name in zip(parts, names):
        flows = sub["flows"]
        title = f'<a href="{E(name)}">{E(g)}</a>' if not embed else E(g)
        bar = jump_bar(flows, static=True, pills=False)
        out.append(f'<div class=part><h3>{title}</h3>{bar}<ol>'
                   + "".join(f'<li>{E(f["title"].removeprefix(g + ": "))}' + (f'<span class=st style="--c:var({STATUS[f["status"]]})">{E(f["status"])}</span>' if f.get("status") else "") + "</li>" for f in flows)
                   + "</ol></div>")
    asks = spec.get("asks") or []
    check_asks(asks, len(spec["flows"]))
    if asks:
        def where(a):
            if not a.get("flow"):
                return None
            g = spec["flows"][a["flow"] - 1].get("group") or "Other"
            return (names[[x for x, _ in parts].index(g)], g) if not embed else (None, g)
        out.append(ask_checklist(asks, where))
    if spec.get("limits"):
        out.append("<section class=flow><h3>Not verified / known limits</h3><ul>" + "".join(f"<li>{E(x)}</li>" for x in spec["limits"]) + "</ul></section>")
    out.append("</div></body></html>" if embed else "</body></html>")
    open(out_path, "w").write("".join(out))
    print(f"index, {len(parts)} parts -> {out_path}")


def build(spec, out_path, embed, with_limits=True, checklist=True):
    check_resolution(spec)
    stem = os.path.splitext(os.path.basename(out_path))[0]
    img_dir = os.path.join(os.path.dirname(os.path.abspath(out_path)), "embed-img", stem)
    if embed:
        os.makedirs(img_dir, exist_ok=True)
        if len(spec["flows"]) > SPLIT_OVER:
            print(f"warning: {len(spec['flows'])} sections in one embed page; split by area: give flows a 'group' and "
                  "use --split (see SKILL.md 'One report, shown in the chat')", file=sys.stderr)
    head = CSS + CMP_CSS + (EMBED_CSS if embed else FALLBACK_VARS + VIEWER_CSS)
    out = [f"<!doctype html><html><head><meta charset=utf-8><title>{E(spec['title'])}</title><style>{head}</style></head><body>"]
    if not embed:
        out.append(f"<h1>{E(spec['title'])}</h1>")
        if spec.get("note"):
            out.append(f"<p class=note>{E(spec['note'])}</p>")
    out.append(jump_bar(spec["flows"]) if embed is False else "<div class=scroller>" + jump_bar(spec["flows"]))

    asks = spec.get("asks") or []
    nflows = len(spec["flows"])
    check_asks(asks, nflows)
    if asks:
        for i in range(1, nflows + 1):
            if not any(a.get("flow") == i for a in asks):
                print(f"warning: section {i} answers no ask in 'asks'", file=sys.stderr)
        out.append("<style>.ask{margin:0 0 12px;padding:2px 0 2px 12px;border-left:3px solid var(--accent,var(--primary))}"
                   ".ask q{display:block;font-weight:600}.ask small{color:var(--muted-foreground)}.ask p{margin:2px 0 0}</style>")

    def ask_html(fi):
        return "".join("<div class=ask>" + (f"<small>on: {E(a['on'])}</small>" if a.get("on") else "")
                       + f"<q>{E(a['quote'])}</q><p>{E(a['did'])}"
                       + f" &middot; <b>{E(a['status'])}</b></p></div>"
                       for a in asks if a.get("flow") == fi)

    def src(path, name):
        # Up to 1600px so the 1:1 view in the standalone report has detail to show.
        data = jpeg(path, 1600, 85)
        if not embed:
            return "data:image/jpeg;base64," + base64.b64encode(data).decode()
        dst = os.path.join(img_dir, f"{name}.jpg")
        open(dst, "wb").write(data)
        return dst

    n = 0
    for fi, flow in enumerate(spec["flows"], 1):
        steps = flow["steps"]
        cmp = any("before" in s for s in steps)
        shots_in = any("html" not in s for s in steps)
        tip = "" if not shots_in else (" &middot; drag across a shot to compare before and after" if cmp
               else " &middot; click a screenshot to enlarge")
        st = flow.get("status")
        if st and st not in STATUS:
            sys.exit(f"unknown status {st!r} in {flow['title']!r}; use one of {sorted(STATUS)}")
        summ = f'<p class=sum>{E(flow["summary"])}</p>' if flow.get("summary") else ""
        chip = f'<span class=st style="--c:var({STATUS[st]})">{E(st)}</span>' if st else ""
        out.append(f'<section class=flow id=flow{fi}><h3>{fi} &middot; {E(flow["title"])}{chip}</h3>{summ}<p class=hint>{len(steps)} step{"s" * (len(steps) != 1)}{" &rarr; scroll sideways" if len(steps) > 1 else ""}{tip}</p>{ask_html(fi)}<div class=row>')
        for i, s in enumerate(steps, 1):
            n += 1
            if "html" in s:
                if UNSAFE_HTML.search(s["html"]):
                    sys.exit(f"section {fi} step {i}: explanation html may not contain <script>, on*= handlers or javascript: links")
                out.append(f'<figure class="card xp" id=s{n}><figcaption><span class=n>{i}</span><span>{E(s["caption"])}</span></figcaption><div class=x>{s["html"]}</div></figure>')
                continue
            if "before" in s:
                check_pair(f"section {fi} step {i}", s)
                shot = (f'<div class="shot cmp" style="aspect-ratio:{pair_ratio(s)}"><img class=before data-v=before src="{src(s["before"], f"{n:02d}-before")}" alt="Before">'
                        f'<img class=after data-v=after src="{src(s["after"], f"{n:02d}-after")}" alt="After">'
                        '<span class=bar></span><span class="tag tb">Before</span><span class="tag ta">After</span>'
                        '<input type=range min=0 max=100 value=50 aria-label="Before / after"></div>')
            else:
                shot = f'<div class=shot><img src="{src(s["img"], f"{n:02d}")}" alt=""></div>'
            detail = f'<p class=detail>{E(s["detail"])}</p>' if s.get("detail") else ""
            tall = is_tall(s.get("before") or s["img"])
            if any(is_long(s[k]) for k in ("before", "after", "img") if k in s):
                shot = f'<div class=lw>{shot}</div>'
            out.append(f'<figure class="card{" tall" * tall}" id=s{n}><figcaption><span class=n>{i}</span><span>{E(s["caption"])}</span></figcaption>{shot}{detail}</figure>')
        out.append("</div></section>")
    if checklist and asks:
        out.append(ask_checklist(asks, lambda a: (f"#flow{a['flow']}", f"section {a['flow']}") if a.get("flow") else None))
    if with_limits and spec.get("limits"):
        out.append("<section class=flow><h3>Not verified / known limits</h3><ul>" + "".join(f"<li>{E(x)}</li>" for x in spec["limits"]) + "</ul></section>")
    if embed:
        out.append("</div>")
    out.append(f"<script>{CMP_JS}</script>")
    if embed:
        out.append(f"<script>{EMBED_JS}</script>")
    else:
        out.append(f"{VIEWER_HTML}<script>{VIEWER_JS}</script>")
    out.append("</body></html>")
    page = "".join(out)
    open(out_path, "w").write(page)
    print(f"{n} steps, {len(page)//1024} KB -> {out_path}")


if __name__ == "__main__":
    spec_path, out_path, *flags = sys.argv[1:]
    spec, embed = json.load(open(spec_path)), "--embed" in flags
    if "--split" in flags:
        parts = split_spec(spec)
        total = len(spec["flows"])
        if total <= SPLIT_OVER or len(parts) < 2:
            print(f"warning: --split is not needed for {total} sections in {len(parts)} group(s); one page reads better "
                  f"(split only over {SPLIT_OVER} sections, into at most {MAX_PARTS} parts)", file=sys.stderr)
        elif len(parts) > MAX_PARTS or any(len(sub["flows"]) < MIN_PART for _, sub in parts):
            print(f"warning: {len(parts)} parts of {[len(sub['flows']) for _, sub in parts]} sections; merge groups so there are "
                  f"at most {MAX_PARTS} parts of {MIN_PART}+ sections each", file=sys.stderr)
        base, ext = os.path.splitext(out_path)
        names = [f"{base}-{slug(g)}{ext}" for g, _ in parts]
        for (g, sub), path in zip(parts, names):
            build(sub, path, embed, with_limits=False, checklist=False)
        build_index(spec, parts, out_path, embed, [os.path.basename(x) for x in names])
    else:
        build(spec, out_path, embed)
