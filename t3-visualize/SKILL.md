---
name: t3-visualize
description: Use T3 Code's built-in visualization tools (html_render, html_preview) to show results inline, while keeping token cost low. Use whenever an answer has numbers to compare, a before/after, a timeline, a flow or architecture, or a multi-item status, and T3's html_render tool is available. Also use when the user asks to "visualize", "chart" or "show" something.
---

# Visualize with T3 Code, on a budget

T3 Code has its own visualization feature. Use it, and don't bring in a separate
charting setup:

- **`html_render`** shows a page inline in the thread, above your reply. This is the
  visualization.
- **`html_preview`** renders the same page headlessly and returns a screenshot, the
  content height and console output. It is for checking a page, and it costs extra.

T3 handles the theme, light/dark mode and width. You supply a small HTML page.

Visualize freely, but stay aware of cost. The HTML you send is **output tokens**
(the expensive kind), roughly 1k tokens per 3–4 KB. Each `html_preview` adds a
screenshot (1–2k input tokens) and a resend of the HTML. The real waste is
duplication: a 20 KB page sent three times with previews cost about 40k tokens.

## When

- **Do:** use a visual whenever it makes the answer clearer: numbers, comparisons,
  before/after, timelines, flows, architecture, status, trade-offs, explanations of how
  something works.
- **Skip:** answers of a line or two, and sessions where `html_render` isn't
  available. Then use a markdown table, and don't fake a chart in ASCII.
- **Use as many visuals as the answer needs.** Several small, focused visuals usually
  beat one giant page, and each one can be any kind: charts, SVG diagrams,
  tables, timelines, small interactive or animated pieces.

## Cost habits

These keep costs low without limiting what you can show:

1. **Size to the content.** Most visuals land at 2–6 KB of HTML. Going up to about
   15 KB is fine when the content needs it. Above that, say roughly what it will cost
   and check with the user first.
2. **Write compact code.** Keep the data in one array and generate repeated markup
   with a loop. Reuse styles, and don't hand-write long lists of rows or elements.
3. **Send the HTML once.** Don't also write it to a file unless the user wants to keep it.
4. **Preview only when it pays off.** Go straight to `html_render` for
   straightforward layouts. Use `html_preview` once for custom SVG, animation, or
   layout you aren't sure about; it adds a screenshot and a resend.
5. **No re-renders to polish.** If something is slightly off, mention it in one line
   and move on. Re-render only for a real error.
6. **Don't describe the page** in your reply. T3 shows it to the reader already, so
   add only what it doesn't show, such as caveats or what was estimated.

## Honesty

Show measured data only. Label estimates and simulations on the page ("est.",
"size ÷ bandwidth"). Never invent numbers to fill a chart.

## Using T3's frame

- **Use T3's theme variables** instead of hard-coded colours, so the page follows the
  user's theme and dark mode: `--foreground`, `--muted-foreground`, `--border`, `--card`,
  `--chart-1` to `--chart-6` (series), `--success`, `--destructive`, `--warning`,
  `--radius`, `--font-sans`, `--font-mono`.
- **The page sits on the thread itself.** It is borderless, about 728px wide, and its
  left edge lines up with the reply text. Don't add an outer card, title banner or
  horizontal padding, and give charts fixed pixel heights.
- **Set `height`** on `html_render` to roughly the content height. Taller content
  scrolls inside the frame.

## Minimal pattern

```html
<!doctype html><html><head><style>
.r{display:grid;grid-template-columns:70px 1fr 70px;gap:8px;align-items:center;font-size:12px;margin:5px 0}
.t{height:14px;border-radius:3px}.n{text-align:right;font-variant-numeric:tabular-nums}
</style></head><body><div id="c"></div><script>
const d=[["Before",47.5,"--muted-foreground"],["After",4.45,"--chart-1"]],m=47.5;
c.innerHTML=d.map(([k,v,col])=>`<div class="r"><span>${k}</span><div class="t" style="width:${v/m*100}%;background:var(${col})"></div><span class="n">${v} MB</span></div>`).join("");
</script></body></html>
```

Starting points, not limits. Any form works:

| Data | Shape |
|---|---|
| before/after, ranking | rows of bars, as above |
| sequential steps / waterfall | bars with a `margin-left` offset per row |
| flow / architecture | a flex row of bordered chips joined by `→` |
| KPI headline | 2–4 tiles in a CSS grid: big number plus muted label |
| status across items | a compact table with coloured dots from the theme variables |
| system / network / data flow | inline SVG with a few shapes and paths |
| how something unfolds over time | a small CSS or SVG animation with a replay button |
