---
name: gemini-research
description: "Outside research with Google Gemini Deep Research and Gemini Tasks, driven through the browse tool in the user's own browser. Use when a design decision needs a literature or prior-art sweep beyond what web search gives quickly, when the user asks to research something with Gemini, or to get a second model's read on a technical question. Covers writing the prompt, running both modes in parallel tabs, waiting, extracting, and checking the key numbers against the sources."
---

# Gemini research through browse

Gemini runs the long search; you write the prompt, drive the tabs, extract the reports and check them. The reports are claims until checked: in the first run, two of three headline claim groups needed correcting.

Load the `browse` skill first; this file only adds what is specific to Gemini.

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

| Mode | Select | Verify |
|---|---|---|
| Deep Research | `button "Upload & tools"`, then `menuitemcheckbox "Deep research"` | chip `button "Deselect Deep research"`; placeholder "What do you want to research?" |
| Task | `button "Task"` (exact) on the home screen | heading "What can I get going for you?" |

Paste with `fill()` on the `[role=textbox]`, check `innerText.length` (about one extra character per paragraph break), then `button "Send message"`.

**Record the chat id at once**: poll `page.url()` for `/app/<id>`. The Deep Research tab may fall back to an empty "Where should we start?" screen with the URL still `/app` even though the send worked. Reload and open the newest sidebar chat by its generated title. Do not conclude it failed from an empty screen.

## 3. Wait by reloading

Background tabs freeze Gemini's rendering: in-place waits and screenshots show "Thinking" forever. Reload about once a minute: `page.reload()`, wait 5 s, then check button labels with `page.evaluate`. Do not use `snapshot({ find: /research/ })`, because the pasted prompt matches.

- **Deep Research plan ready:** a `Start research` button exists. Click it. Research then takes about 6 minutes (up to 60).
- **Deep Research done:** `Share & Export` exists and `Stop response` does not.
- **Task done:** "Complete" shows and `Stop response` does not (about 7 minutes in the first run).

Stop at 45 minutes and tell the user. Never poll faster than once a minute.

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

Where the files are, whether each run finished, which key numbers you checked and which you corrected, and that the tabs are left open. Ask before deleting any chat.
