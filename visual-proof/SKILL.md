---
name: visual-proof
description: Hand the user screenshot proof that work is done, as a side-scrolling HTML report of numbered, captioned screenshots (single shots, or drag-to-compare before/after pairs), so they can see it instead of testing by hand. Use for (1) a feature or multi-role flow ("walk through", "test the flows", "show me it working", "screenshots step by step"), (2) a batch of reported issues the user asked to have fixed ("fix these", a pasted list of bugs) — one section per issue with before/after and a status, (3) a single bug fix or page restyle ("show before and after"). Formerly flow-walkthrough.
---

# Visual proof report

Goal: the user is tired or busy and wants to *see* the work, not re-test it themselves:
a flow running end to end, or each issue they reported shown broken and then fixed.
Output is one HTML file with a horizontal, snap-scrolling row of numbered steps per
section, plus an inline copy in the T3 chat.

## Cost model (measured by reasoning, not magic)

- **Capturing is almost free.** `preview_snapshot(save=true, includeImage=false)` writes a
  PNG and returns a path, about 100 tokens.
- **Reading images is the cost.** One 1280px screenshot is about 1.5k tokens; a contact
  sheet of 12-20 shots about 4k. The user's own report is never read back.
- **Driving the flow is the other cost** (navigate, login, click, evaluate: a few hundred
  tokens each, but every call resends the growing context).
- Rough budget for a 30-step, 3-role flow: 20-40k tokens on top of the actual feature
  work, if you follow the lean rules below. Reading every shot individually roughly
  doubles it.

## Lean rules

1. **Do the work first, capture second.** Batch code changes, then one pass of the flow.
2. **Prove state without looking.** After each step assert with `preview_evaluate` on DOM
   text, a `curl`, or a DB query (never trust a caption you did not check). A screenshot
   is evidence for the human, not for you.
3. **Read images sparingly.** Read a shot only when something may be visually wrong
   (layout, overlap, dark mode). For the rest, build one contact sheet
   (`montage -label %t -tile 4x -geometry 600x470+3+3 ...`) and Read that once.
4. **Name shots as you go.** Copy each saved PNG into `~/temp/<task>/raw/NN-step.png`
   immediately. Do not reconstruct order from mtimes afterwards.
5. **Mind what the screenshot lags.** Modals/toasts can lag; retake or wait on a
   selector first.
6. Follow the user's browser rules (T3 preview first, Browser Control fallback, never
   Playwright). Scratch lives in `~/temp/`, not `/tmp`.
7. **English + light first** (see "Default look" below); other languages and dark mode
   come as extra shots after the base ones.

## Default look: English, light mode

Every shot in a report is **English and light theme unless the work is about something
else**. Set both before the first capture, and say in the caption or `limits` if a shot
deviates:

- Language: switch the app to English (the language toggle shows the *other* language,
  so on an Amharic page the button reads "EN"). Test accounts can come up in Amharic;
  check `document.documentElement.lang` is `en` before shooting.
- Theme: light (check `document.documentElement.classList` has no `dark`; in T3 preview
  use `preview_set_appearance`, in Browser Control click the theme toggle). Dev browsers
  often remember dark.
- Not a reason to skip other variants: when a change touches copy, layout, or colours,
  also add **Amharic** and **dark** shots as extra steps (or a before/after pair per
  variant), after the English-light ones. Text-length and dark-token bugs live there.
  If you did not check them, list "Amharic not checked" / "dark not checked" in `limits`.
- Before/after pairs must use the same language and theme on both sides.

## Sharp screenshots (a blurry report is a failed report)

Seen once: a whole report built from 640x400 PNGs, shown at ~950px, so every shot was a
soft smear the user could not read. The cause was upstream of the report builder, in the
capture. Rules:

1. **Verify the size of the first PNG from every tab, before shooting the rest.**
   `identify <png> | awk '{print $3}'` must give **>= 1280 wide**. If it is smaller (a
   tab can silently capture at half size, with no setting that shows it), do not
   continue: `preview_open` with `reuseExistingTab=false`, pass that new `tabId` on
   every call, and test again. Do not carry on with the old tab.
2. **Capture at a viewport 1280 wide** (`preview_resize` freeform 1280x800, or fill).
   Any other width is resampled to 1280 wide when saved (a 1160px viewport came out as
   1280x883, an upscale), so narrow layouts get soft too. To show a layout that only
   appears in a narrower container, narrow the container with `preview_evaluate`
   (e.g. set a width on the wrapper) instead of resizing the viewport, or accept the
   upscale and say so in `limits`.
3. **Check every shot's size right after saving it**, with one `identify` over the raw
   folder, not at the end. Retake a bad one while the page state still exists.
4. **Never `includeImage:true`** to "see it better"; the saved PNG is what the user gets.
5. **A contact sheet is for you, not the user.** It downsizes, so its blur proves
   nothing, but run `identify` on the sources anyway. Do not ship a report you saw
   looking soft without finding out why.
6. `build_report.py` refuses any landscape image under 1100px wide (portrait phone shots: 720px) and tells you which ones.
   `"allow_low_res": true` in the spec overrides it, only for a deliberately small
   capture, and say so in `limits`. It writes JPEGs at quality 85, up to 1600px wide.

## Phone screenshots (show them at phone size)

Seen once: a report of 1080x2340 phone captures, each drawn at the full ~1000px card
width, so every shot was about 2200px tall, a giant screen the user had to scroll
through several times per step. A phone screen should read like a phone.

- `build_report.py` treats a portrait shot (height > 1.3x width) as a phone screen. It
  gives that card a phone-width column (about 380px), so two or three sit side by side.
  The resolution floor for these is 720px wide (2x the shown width), not 1100px, so do
  **not** set `allow_low_res` for native phone captures.
- Capture phones at their native resolution (e.g. `adb exec-out screencap`). Don't
  upscale them, and don't pad them to 1280 wide to get past the check.
- A before/after pair takes its shape from the Before shot. Pair a portrait with a
  portrait; a phone shot slid against a desktop shot doesn't compare.
- Web views of a mobile layout: use a phone-sized viewport (e.g. 390x844) and say so
  in `limits`. They come out tall and are shown like a phone too.
- Before shipping, look at the embed at its real width once (one `html_preview`, or
  the contact sheet at the card width). If any single shot is taller than a screen,
  something is wrong.

Keep the before/after compare slider: the user likes it, and asked for it on every pair.

## Four kinds of report

| Kind | Sections and steps | Use when |
|---|---|---|
| **Flow** | one section per role handoff; `img` shots in the order a user lives it | a feature or multi-role journey |
| **Issue batch** | one section per issue the user raised, titled in *their* words, with a `status`; a `before`/`after` pair, then any `img` shots proving it holds | "here are N problems, fix them" |
| **Fix** | one `before`/`after` pair per symptom, then `img` shots proving the fix holds (the follow-on step, the edge case) | a single bug fix |
| **Visual change** | one `before`/`after` pair per screen or state (light, dark, mobile, empty, error) | restyling or redesigning a page |

A report can mix them: a fix often wants one pair plus a short flow.

**Issue batches.** Before touching code, capture a Before for *every* issue in the list
(reproduce it first; that also tells you whether it is real). Then fix, then capture
the Afters in one pass. Give every section a `status`, and be honest about it:
`fixed`, `partial` (say what is left in the caption), `not reproduced` (show the Before
that looks fine), `needs decision` (show the options) or `not fixed` (say why). An issue
that is not visual (an API error, a wrong email) still gets a section: shoot the page
where the user would notice it, or put the evidence in the caption.

**Coverage check (batches).** The user may trust the report and never reread their
prompt, so a dropped ask would be invisible. Their message is rarely a clean list: it
can be inline comments on quoted text, preview annotations, "also do X" asides and
questions. Treat each separate comment or instruction as one ask.
1. *Before work*, note every ask with the user's **exact words** (quoted, not
   paraphrased) and what it was attached to, in `~/temp/<task>/asks.md`. If an
   annotation's text is unreadable, say so rather than inventing it.
2. *Before building*, reread the original message (not your memory of it) against the
   list and the work, and add what you missed.
3. Put the ones a screenshot can show in the spec: `"asks": [{"quote": "exact words",
   "on": "what it pointed at", "did": "what you did", "flow": 3, "status": "fixed"}]`.
   `flow` is the section that shows it, and the quote and answer print **inside that
   section**, above its screenshots; there is no separate list at the top. The builder
   warns about a section that answers no ask.
   Questions, discussion points and non-visual asks (`flow: null`) stay **out of the
   report**. Answer them in the normal chat reply, quoting the user's words the same way.
4. Undone or partly done asks still appear (`not fixed`, `partial`). Never drop one.

**Before/after rules.** Take every Before shot before the first edit; it cannot be
recreated once the code changes. Capture the After at the same route, viewport, theme,
scroll position and data, or the slider compares two different pages. For a bug, the
Before shows the symptom (the error, the wrong value), not just the page. A caption
names what changed ("Approve stays disabled until an ID is uploaded"), not "after".

## Flow structure

One flow per role handoff, in the order a real user lives it:
actor does X -> system state changes -> other actor sees it -> decision -> first actor
sees outcome. Include the **negative paths** (blocked approve, reject with reason) and
the **before/after of any fix** (the Before shot is taken before editing).

## Build the report

1. Write `~/temp/<task>/spec.json`:
   `{"title":..., "note":..., "asks":[...], "flows":[{"title":..., "status":"fixed", "steps":[...]}], "limits":[...]}` (`asks` is the coverage checklist, required for issue batches)
   (`status` is optional: `fixed` | `partial` | `not reproduced` | `needs decision` | `not fixed`)
   where each step is `{"img":"/abs.png","caption":...}` or
   `{"before":"/abs.png","after":"/abs.png","caption":...}` (rendered as a drag-to-compare slider).
2. `python3 -I ~/.agents/skills/visual-proof/build_report.py spec.json index.html`
3. Give the user the report as a markdown link to the absolute `.html` path in your reply.
   T3 opens a linked `.html` file in its side browser panel. There, clicking a shot opens a
   full-window viewer: ←/→ to step through, click or "1:1" for full size, drag to pan, Esc
   to close. Do not Read the HTML (it is megabytes of base64).
4. **In T3 Code (the `html_render` tool exists), also show it inline in the chat:**
   `python3 -I ~/.agents/skills/visual-proof/build_report.py spec.json embed.html --embed`,
   `cat embed.html` (a few KB: captions plus image paths, no base64), and pass that
   text verbatim as `html_render`'s `html`, with a `title` and `height: 2000`.
   The T3 server swaps each image path for the image data before it stores the page,
   so the image bytes never pass through the model.
   - Image paths must be **literal absolute paths in the markup** (`src="/home/.../01.jpg"`).
     T3 finds them with a regex. A path assembled in JS (`D+n+'.jpg'`) is not inlined
     and shows as a broken image in the chat, even though `html_preview` displays it.
   - Look: one card per step, with a numbered badge, the caption above the shot and the
     next card peeking in from the right so it is obvious the row scrolls. Clicking a shot
     turns on a magnifier lens that follows the pointer (+ / - change the power; click
     again, Esc or leaving the shot turns it off); a before/after pair is a slider you
     drag across. Tried and rejected: in-place zoom (the frame is narrower than a
     screenshot, so it cropped, and it fought the wheel) and an always-on hover lens (in
     the way). For a wider view, tell the user about T3's own **Open in panel** button,
     top-right of the embed on hover: it opens the same page in the side panel, lens
     included. A link inside the frame cannot open the side panel (the sandbox hands
     http(s) links to the system browser).
   - Every colour comes from T3's theme variables (`--accent`, `--card`, `--border`,
     `--ring`, `--muted-foreground`, …), so it follows the user's theme and light/dark
     mode. Never hardcode a colour in `CSS`, `CMP_CSS` or `EMBED_CSS`. The point is
     readability, not decoration.
   - Limits: 10 MiB per image and 25 MiB for the page once the images are inlined.
     `--embed` writes JPEGs up to 1600px wide (about 90 KB each), so the lens and the
     standalone report's 1:1 view have detail to show.
   - To check it worked, the stored page in `~/.t3/userdata/attachments/<id>.html`
     should contain one `data:image/` per step and no `/home/` paths.
     `html_preview` is not proof, because it can read local paths directly.

## Honesty section is mandatory

`limits` must say what was not driven end to end, which captions were written from
thumbnails or DB state rather than a full-size look, and any pre-existing quirks seen.
