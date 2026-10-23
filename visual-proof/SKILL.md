---
name: visual-proof
description: "MANDATORY whenever you change anything the user can see in a browser (UI, copy, layout, a page's behaviour) in answer to their feedback, annotations, screenshots or a fix list, and for any request to walk through, test or show a flow working. Drive the real app, fix what you find, re-walk to prove it, and hand back a side-scrolling HTML report of captioned screenshots and drag-to-compare before/after pairs, one section per issue or flow, with a status, ending in a checklist of every ask so none is missed; how-it-works questions in the same message get a visual explanation section. Capture Before shots BEFORE the first edit. For any agent (Claude, Codex, a subagent). Formerly flow-walkthrough."
---

# Visual proof report

The user is busy and wants to *see* the work: a flow end to end, or each reported issue shown
broken, then fixed. Output: one HTML file with a snap-scrolling row of numbered steps per section,
plus (in T3 Code) an inline copy in the chat. Applies to whoever drives the browser, the main
agent or a subagent; the project's browser rules win (which tool, banned tools, where scratch files go).
`<scratch>` below is the task's scratch folder (`<scratch>/` in the author's setup, never `/tmp`);
`<skill-dir>` is the folder holding this SKILL.md (`~/.agents/skills/visual-proof` for a global install, `.agents/skills/visual-proof` in a project).

## When it is mandatory (do not wait to be asked)

Use it whenever a turn changes something a person sees in a browser: UI, copy, layout, styling or
a page's behaviour. That includes **feedback as annotated screenshots, questions mixed with
fixes, "fix these", or a pasted list**. A mixed message is still a batch: the fixes need proof, and every question is an ask that gets answered in the chat and listed in the report (see Coverage check; a how-it-works question gets an explanation section).

1. **Before the first edit**, write the asks (exact words) to `<scratch>/asks.md` and capture a
   Before shot of every visual ask. Once the code changes, a Before cannot be recreated cheaply.
2. Fix, re-walk (see the loop below), capture the Afters, build the report.
3. The reply leads with the report (inline in T3 Code), then the written answers.

A text summary, a DOM-text check or "tsc and vitest pass" is evidence for you, not the deliverable.
Skip the report only for changes nobody can see (backend, docs, tests, scripts) and say "no visual change, no report".

**If you edited first by mistake:** rebuild the Before from git. `git worktree add <scratch>/before <sha>`,
run its dev server on another port under `systemd-run --user -p MemoryMax=6G`, shoot there, then stop
it and remove the worktree. Say in `limits` that the Befores were rebuilt.

## Verification loop

Driving the real app is for finding real problems and fixing them. A "not fixed" on something you
could have fixed is a failed run.

- **Only these stay open, each with a stated reason:** owner decisions, missing data or environment, backend or production concerns outside this task.
- **A fix is not done until you re-ran the path in the browser** and captured a fresh After (or a measurement). A claimed fix without one is `unverified`, never `fixed`.
- **A product call is still fixed.** Where a documented decision conflicts with the user's own stated rule, fix toward the user's rule and flag it in the section (`fixed`, plus the note), instead of leaving it open.
- **Loop:** walk, catalog, fix, re-walk. The re-walk *is* the next loop's walk: any new or surviving bug goes back into the catalog and gets fixed, then walked again. There is no fixed number of loops. Stop on one fully clean pass, or when only the open kinds above remain.
- **Runaway guard:** if the same item still fails after three fix attempts, or three passes in a row find no fewer problems than the one before, stop looping on it and report it open with the reason.

**Verdict: catalog first, fix in batches, then walk again.** Do not fix as you meet each problem.
- During a walk only record: a screenshot plus one line per problem in `issues.md` (or the manifest).
- After the walk, fix in batches grouped by file or component. Cataloguing first exposes shared
  causes, so one fix closes several findings, and it keeps the walk on one stable build so the
  later Befores still match what the user saw.
- Re-walk *everything*, not only the fixed items: it proves each fix and catches regressions the fixes caused.
- **Exception:** a blocker that stops the walk (login broken, page crashes) is fixed at once.
- **Keep it cheap** (per the project's cost policy; the author's is `~/.claude/modes/active.md`): a Haiku-class agent walks and captures. Fixing is a separate job so the walk's window is not filled with code: small, clearly specified fixes (copy, a one-file CSS or prop change; give it the issue line and the file) go to Haiku, which is cheaper and quicker than the big model reading the file. Cross-file, logic or behaviour changes, or anything Haiku got wrong once, go to Sonnet or the main agent. Haiku re-walks.

## Lean rules

Capturing is nearly free; **reading images and re-sending long context are the cost** (a 1280px shot is ~1.5k tokens).

1. **Prove state without looking.** After each step assert on DOM text, an API call or a DB
   query, and put the evidence in the caption. The screenshot is evidence for the human.
2. **Read images sparingly**: only where layout, overlap or dark mode may be wrong. Otherwise one
   contact sheet (`montage -label %t -tile 4x -geometry 600x470+3+3 ...`), read once.
3. **Name shots as you save them**: `<scratch>/raw/NN-step.png`. Never rebuild order from mtimes.
4. **Wait for lagging UI** (modals, toasts, spinners) on a selector, then shoot. A spinner or empty page is a failed shot.
5. With Browser Control, pass `style: "[id^=__browser_control]{display:none!important}"` to `page.screenshot` to hide the agent cursor and session pill.

## Delegating the browser run

- **Use a cheap model for the walk** (a Haiku-class model; the author uses `claude-haiku-5-5` via `delegate_task`, always the exact ID, never an alias). Escalate after it got something wrong once.
- **Haiku can die of compaction** (starts at ~35k, compacts near 80k, three in a row kill it). Size one job to one window: one agent per role area, grep or offset/limit reads, 2-3 files per step, a short reply (counts only).
- **Make progress durable**: it appends `{issue,status,before,after,caption}` to `manifest.jsonl` per item, so a crash loses one item at most; `spec.json` is written last.
- **Concurrent agents on one stack need separate cookies** (`127.0.0.1` vs `localhost`), or run in turn.
- **Verify its verdicts**: open the screenshot behind every "not fixed" before acting.

## Default look: the project's language, light

Every shot uses the project's default language and the light theme (English and light in the author's projects) unless the work is about something else; set both before the first
capture (the toggle shows the *other* language) and note any deviation in the caption or `limits`.

- Check `document.documentElement.lang` is the default language and `document.documentElement` has no `dark` class (test accounts and dev browsers remember another language and dark).
- When a change touches copy, layout or colours, add a **second-language** (e.g. Amharic, or the longest-text language) and a **dark** shot after the base ones. Unchecked variants go in `limits`.
- Before/after pairs use the same language and theme on both sides.

## Sharp, well-framed screenshots

1. Check the first PNG of every tab: `identify <png> | awk '{print $3}'` must be **>= 1280 wide** (a tab can silently capture at half size). Use a 1280-wide viewport; other widths are resampled.
2. `identify` the raw folder right after saving; retake while the page state exists. Never `includeImage:true` to see better; the saved PNG is what the user gets.
3. The builder rejects landscape images under 1100px (portrait phone shots: 720px). `"allow_low_res": true` overrides it and must be named in `limits`. JPEG quality 85, up to 1600px wide.
4. **Phone:** portrait shots (height > 1.3x width) are drawn phone-sized, so two or three sit side by side. Capture at 390x844, device scale 2 (or `adb exec-out screencap`), and say so in `limits`. Never upscale or pad to 1280.

**Cropping.**
- The Before shows the defect clearly: frame the element plus enough surroundings to see where it is.
- The After uses the **same crop, viewport, scroll, zoom, language and theme** as the Before.
- For a local defect prefer an element screenshot or a fixed clip rect over a full page. On a long page scroll the defect into view first.
- Never crop out the label that explains the screen (heading, tab, field name).
- The builder warns when a pair's width or height differs by more than 3%, and the slider letterboxes both at one scale instead of cropping. A warning means retake the After.

## Kinds of report

| Kind | Sections and steps | Use when |
|---|---|---|
| **Flow** | one section per role handoff; `img` shots in the order a user lives it, negative paths included | a feature or multi-role journey |
| **Issue batch** | one section per issue, in the user's words, with a `status`; a `before`/`after` pair, then `img` proof it holds | "here are N problems, fix them" |
| **Fix** | one pair per symptom, then proof (follow-on step, edge case) | a single bug fix |
| **Visual change** | one pair per screen or state (light, dark, mobile, empty, error) | a restyle or redesign |

Reports can mix kinds. Every section gets an honest `status`: `fixed`, `partial` (say what is left),
`not reproduced` (show the Before that looks fine), `needs decision`, `unverified`
(fix made, not re-run), `current design` (it works the way it is built and documented today, not a defect: show it and say which rule or decision it follows, never `not fixed`; the name is deliberately neutral, so it never reads as "you fool, this was by design"), `not fixed` (a real defect left open; say why).
**`needs decision` must name the decision**: the section's `summary` states the exact question, the options (A/B/C, each with its consequence) and your recommendation, in plain words. "Left as is; your call" is not a decision. Show a shot per option when they look different. Non-visual issues still get a section: shoot where the user would notice, or put the evidence in the caption.
A pair's caption says what changed ("Approve stays disabled until an ID is uploaded"), not "after".

**Coverage check (batches).** The user may never reread their prompt, so a dropped ask is invisible.
Inline comments, annotations, "also do X" asides and **questions** each count as an ask.
1. Write each ask with the user's **exact words** and what it was attached to to `asks.md` (say so if an annotation is unreadable).
2. Before building, reread the original message (not your memory of it) against the list.
3. Put **every** ask in the spec, none left out: `"asks":[{"quote","on","did","flow":3,"status"}]`. `status` is required (same words as a section's). `flow` is the section that shows it, or `null` for a question or non-visual ask, which you also answer in full in the chat. The builder warns about a section that answers no ask and refuses an ask with no status.
4. The report ends with an **Everything you asked** checklist: each ask once, its status, where it is shown ("section 3", or "answered in the chat"). Undone or partial asks still appear. Never drop one.
5. In the reply, after the report, state the count against your reread: "9 of 9 asks covered: 6 fixed, 2 answered, 1 needs your decision".

## Explanations (how-it-works questions)

When an ask is "how does X work?", "why does it do Y?" or "explain Z", answer it in the report as its own section, `status: "answered"`, so it sits in the same place as the fixes. Use `html` steps instead of screenshots:

- A step is `{"html":"<div class=x-row>...</div>","caption":"..."}`. Build it from the kit: `.x-row` of `.x-box` joined by `<span class=x-arrow>&rarr;</span>`, `.x-box.hot` for the key one, `.x-note` for the small print, `.x-code` for code, inline `<svg viewBox>` for diagrams (use `currentColor`; it follows light and dark). Colours only from theme variables; no `<script>`, `on*=` handlers or `javascript:` links (the builder refuses them).
- **Ground it in the real thing.** Read the code, the schema or the run first, and use the real names, files and numbers. An explanation from memory is a guess, so say so in `limits`.
- **Detailed, not simplified.** The reader is smart and busy, not a beginner. Show the actual stages, the actual data and what breaks or branches; one concept per card, 3 to 5 cards, the cards left to right in the order the thing happens. No analogies standing in for the mechanism.
- Cost: a detailed card is about 500 to 1,500 tokens of HTML, paid twice (once in the spec, once passed to `html_render`). Two or three cards cost less than reading one screenshot. Skip a diagram when two sentences in the chat explain it.
- A turn with only explanations and no UI change needs no report: use `html_render` directly (see `t3-visualize`), same kit.

## Write for the reader

The reader is busy and not technical. If they must ask what a line means, it failed.

- **Title** = what the user would notice, in everyday words ("A free Code no longer asks for a card"). No issue IDs, ticket numbers or "1." prefixes.
- **`summary`** (per section): one or two sentences, what was wrong and how it ended up. It must agree with `status`.
- **`caption`** (per step): one short sentence on what is on screen, or for a pair what changed. No pixel sizes, CSS/DOM words or jargon.
- **`detail`** (per step, optional): technical evidence (numbers, element names, which account, substituted data) in small grey type. Anything that changes how to read a pair (different account or state) goes in `detail` *and* plainly in the caption.
- **`limits`**: at most ~8 short bullets of what was not checked. No session names or agent chatter.
- Short sentences, active voice, same language as the user.

## One report, shown in the chat

- **One combined report per subject**, not one file per agent. Merge the per-agent specs into one `spec.json`.
- **Show it inline.** In T3 Code the embed goes into the chat via `html_render`; a link alone is not enough.
- **One page unless it is really long.** Up to ~25 sections stay on one page: the jump bar makes them reachable and extra pages only make the reader click. Over ~25, give each flow a `"group"` by *area of the product* ("Buyer", "Admin"), not by role handoff or page, and build with `--split`: at most 4 parts of 6+ sections each, plus a short index. **Show the part pages, never the index on its own**: its list repeats the parts' jump bars as a wall of status text. Link the index in the file reply only. Merge small groups. The builder warns when a split is unneeded or too fine.
- **Jump bar:** every page, standalone and embed, opens with a sticky bar: counts by status (e.g. "3 fixed"), then one numbered, status-coloured link per section, so the reader jumps to any section from anywhere in the report. Keep section titles short; they show on hover. Embeds also sit in a scroll box: 680px inline (so a long part stays short in the chat), and the full window height when opened in the panel or full screen (a script in the page sets it, because `html_render` rejects `vh`). Keep `height` at 760 or below, or the inline frame grows to fit.

## Build the report

1. Write `<scratch>/spec.json`:
   `{"title","note","asks":[...],"flows":[{"title","summary","status","group","steps":[...]}],"limits":[...]}`;
   a step is `{"img":"/abs.png","caption","detail"}`, `{"before":"/abs.png","after":"/abs.png","caption","detail"}` (a drag-to-compare slider) or `{"html","caption"}` (an explanation). `status`, `summary`, `group` and `detail` are optional; every ask needs a `status`.
2. `python3 -I <skill-dir>/build_report.py spec.json index.html` (needs Python 3 and Pillow: `pip install pillow`; standalone, base64 JPEGs, sticky jump bar). Read the warnings it prints (size mismatch, no ask answered, low res) and fix them. It also stops on an ask with no status and on unsafe explanation HTML.
3. Give the user a markdown link to the absolute `.html` path (T3 opens it in the side panel; click a shot for the viewer). Never Read the HTML (megabytes of base64).
4. **In T3 Code (`html_render` exists), also show it inline:** build with `--embed` (add `--split` for several parts; it writes `<base>-<group>.html` plus the index at the given path, images in `embed-img/<name>/`). `cat` the page (a few KB to ~30 KB, no base64) and pass it verbatim as `html_render`'s `html`, with a `title` and `height: 760`. T3 swaps each image path for its data on the server.
   - Image paths must be **literal absolute paths in the markup**; a path built in JS shows broken.
   - Colours come from T3 theme variables (`--accent`, `--card`, `--border`, `--ring`, ...), never hardcoded.
   - `html_render` rejects `vh`/`dvh` units and `height:100%` on html or body, which is why the scroll box is in px. Keep it that way.
   - Limits: 10 MiB per image, 25 MiB per page once inlined. Clicking a shot in the chat is left to T3, which opens the image in its own viewer (the report adds no zoom of its own).
   - Check: the stored page `~/.t3/userdata/attachments/<id>.html` has one `data:image/` per step and no local absolute paths left (grep for your home folder). `html_preview` proves nothing, it reads local paths.

## Honesty section is mandatory

`limits` says what was not driven end to end, which captions came from thumbnails or DB state rather
than a full-size look, which variants (second language, dark, phone) were skipped, what was left open and why, and any pre-existing quirks seen.
