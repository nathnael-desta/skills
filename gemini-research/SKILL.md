---
name: gemini-research
description: "Outside research with Google Gemini Deep Research and Gemini Tasks, driven through the browse tool in the user's own browser. Use when a design decision needs a literature or prior-art sweep beyond what web search gives quickly, when the user asks to research something with Gemini, or to get a second model's read on a technical question. Covers writing the prompt, running both modes in parallel tabs, waiting, extracting, and checking the key numbers against the sources."
---

# Gemini research through browse

Gemini runs the long search; you write the prompt, drive the tabs, extract the reports and check them. The reports are claims until checked: in the first run, two of three headline claim groups needed correcting.

Load the `browse` skill first; this file only adds what is specific to Gemini.

## What it is good for

Use Gemini for a sweep of prior art and as a list of claims to check, not as a substitute for measuring. When the data is local and can be measured (files, builds, benchmarks), measure it yourself, in parallel with the Gemini runs. On 20 Nov 2026 the reports projected 20-250 KB for a weekly update; building the real patches measured 2.4 KB, because no report could see a layout quirk in the data that only a real diff exposed. The reports still paid off with a few leads that changed the design (a native decoder already in the framework, an API the runtime lacks), each checked in the source before use.

## Rules

- **Privacy.** The prompt contains only the question and the context it needs. No names, emails, account details, repo paths, company or project names unless the user says they may go. Never return a full `snapshot()`: it prints the Google account name and email and every chat title in the sidebar. Read the page with `page.evaluate` or `snapshot({ find })`.
- **No temporary chats.** Gemini may use the user's saved memory. Counter it in the prompt: the context section says "Use only the context in this prompt; ignore anything you remember about me or my projects."
- **Leave the Gemini tabs open** when you finish, so the user can read them. Close only helper tabs you opened for checking sources.
- **Never delete a chat** without the user's approval for that chat.
- Files go in `~/temp/<task>/research/`. `~/temp` is not a browse file root, so move text through `files.write` (browse temp root) and `cp` with Bash.

## 1. Write the prompt

Start from [example-prompt.md](example-prompt.md). Keep its shape:

1. **Context.** What is being built, the constraints that make it unusual, numbered, and the current measured state with its numbers.
2. **Questions.** Numbered, each with the candidates you already know of, so Gemini goes past them.
3. **Rules for the answer.** Mark every number **measured** (where: paper, table, network) or **projected**; never mix them in one column. List each source as **opened in full** or **snippet only**. Say what could not be verified. End with a ranked list of what to try first, and why.

Save it as `prompt.md` in the research folder. Avoid backticks and `${` in it: it gets pasted as a `String.raw` literal.

## 2. Run both modes

Open one tab per mode with `tabs` action `new`, an `id` (`gemini-dr`, `gemini-task`) and `keepOpen: true`, at `https://gemini.google.com/app`. Two tabs in parallel worked; more is untested.

**Always use the Neon model**, in both tabs, before choosing the mode. Read the picker's label first: `button` whose `aria-label` starts with "Open mode picker, currently". If it does not end in "Neon", open it and pick `menuitemradio` "Deeper analysis … Neon" (match `/Neon/`), then read the label again. Leave the thinking level as it is unless the user asks. If Neon is missing from the picker, stop and tell the user; don't fall back to another model.

| Mode | Select | Verify |
|---|---|---|
| Deep Research | `button "Upload & tools"`, then (since 20 Nov 2026) its "More tools" item, then `menuitemcheckbox "Deep research"`, clicked in the page: `page.evaluate(() => [...document.querySelectorAll('[role=menuitemcheckbox]')].find(e => e.innerText.trim() === 'Deep research').click())` | chip `button "Deselect Deep research"`; placeholder "What do you want to research?" |
| Task | `button "Task"` (exact) on the home screen | the Task home screen heading (it changes: "What can I get going for you?", "Let's clear your plate", "Say the word, I'll take it from here"); the picker still reads Neon |

A normal `locator.click()` on the Deep research menu item landed on "Create image" twice (19 Nov 2026), probably because the menu is still animating; the in-page click above works. Check for a "Deselect Images" chip and remove it if one appears.

Before sending, check the picker label still reads Neon. Paste with `fill()` on the `[role=textbox]`, check `innerText.length` (about one extra character per paragraph break), then `button "Send message"`.

**Record the chat id at once**: poll `page.url()` for `/app/<id>`. The Deep Research tab may fall back to an empty "Where should we start?" screen with the URL still `/app` even though the send worked. Reload and open the newest sidebar chat by its generated title. Do not conclude it failed from an empty screen.

## 3. Wait by reloading

Background tabs freeze Gemini's rendering: in-place waits and screenshots show "Thinking" forever. Reload about once a minute: `page.reload()`, wait 5 s, then check button labels with `page.evaluate`. Do not use `snapshot({ find: /research/ })`, because the pasted prompt matches.

- **Deep Research plan ready:** a `Start research` button exists. Click it. Research then took about 6 minutes in the first run and over an hour on 20 Nov 2026.
- **Deep Research done:** `Share & Export` exists and `Stop response` does not.
- **Task done:** "Complete" shows and `Stop response` does not (about 7 minutes in the first run).

Never block on a run. Keep doing your own work while it runs and check between steps, never faster than once a minute.

At 45 minutes, stop polling a run that is still going. Tell the user it is still running, leave its tab open, and finish without it. Say "not finished yet", never that it added nothing. The user may tell you when it finishes or hand you the report. Then extract it (section 4), check it (section 5), and report what it adds beyond what you already have. The open tab is the handoff; nothing else is needed.

## 4. Extract

- **Deep Research:** the report is `deep-research-immersive-panel .markdown`. Convert it in the page (HTML to markdown, tables kept) and `files.write` it. Citations are empty `<source-footnote><sup data-turn-source-index="N">` elements: emit `[Sn]` from the attribute, or they vanish. The numbers do not map reliably to the source list; say so in the file. Sources: `a[data-test-id="browse-web-item-link"]`, split into "used" and "browsed but not used" by the page headings.
- **Task:** the chat text is a short summary; the report is HTML in a Canvas iframe. Read it with `page.frameLocator('iframe[title^="<report title>"]').locator('body')`. Its Code/Preview tabs are `radio` elements, not buttons.

Save `gemini-deep-research.md` and `gemini-tasks.md`.

## 5. Check, then merge

1. Pick the claims a decision would rest on (usually 5-10 numbers). Open at least three primary sources behind them.
2. For a PDF, download the binary (WebFetch saves it even when it will not summarise), run `pdftotext` on a copy in your own folder, and read the numbers there. Never trust a fetch summary for numbers. An arXiv HTML page can be read in a browse tab.
3. Write `merged.md`: one answer per question, each number tagged measured or projected and **checked** or **unchecked**, with corrections called out. Keep the original reports alongside it.
4. Append to `browse-log.md` what broke and what selectors changed, so this skill can be updated.

## Tell the user

Where the files are, whether each run finished, which key numbers you checked and which you corrected, and that the tabs are left open. Name what each report added that you had not found yourself, and where its projections disagreed with your measurements. Ask before deleting any chat.
