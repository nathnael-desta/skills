---
name: t3-visualize
description: Use T3 Code's built-in visualization tools (html_render, html_preview) to show results inline. Use whenever an answer has numbers to compare, a before/after, a timeline, a flow or architecture, or a multi-item status, and T3's html_render tool is available. Also use when the user asks to "visualize", "chart" or "show" something.
---

# Visualize results in T3 Code

When a picture explains results better than text, show a page with `html_render`. Make whatever page the content deserves: any size, any technique (SVG, canvas, CSS, JS). Don't also save the HTML to a file unless asked.

- Open with the conclusion in plain words.
- Choose the form from the question (trade-off, change over time, spread across runs), not a default row of bars per metric.
- Mark key moments and thresholds on the visual itself.
- Add interaction where it helps, such as hover values or highlighting one item across charts.
- Show measured data only and label anything estimated.
- The page must look right at load, so skip entrance animations. Preview once at most and fix only real errors.
