# Refresh Beads Planning Mirror

Create `scripts/refresh-beads-plan.mjs` with this exact content. This template
is Markdown so Vercel Skills installs it with the rest of the skill.

```js
#!/usr/bin/env node

import { execFileSync } from "node:child_process";

const planningLabel = "phase:planning";
const mirrorLabel = "phase:mirror";
const executionLabel = "phase:execution";
const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
const refs = args.filter((arg) => arg !== "--dry-run");

if (refs.length === 0) {
  console.error(
    "Usage: node scripts/refresh-beads-plan.mjs [--dry-run] <issue-url-or-number> [...]",
  );
  process.exit(1);
}

function run(command, commandArgs, options = {}) {
  const output = execFileSync(command, commandArgs, {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
    ...options,
  });
  return output?.trim() ?? "";
}

function ghJson(path) {
  const output = run("gh", ["api", "--paginate", path]);
  return output === "" ? [] : JSON.parse(output);
}

function issueNumber(ref) {
  const issue = JSON.parse(
    run("gh", ["issue", "view", ref, "--json", "number,url"]),
  );
  if (!issue.url.startsWith(`https://github.com/${repository}/issues/`)) {
    throw new Error(`${ref} is not an issue in ${repository}`);
  }
  return issue.number;
}

const repository = run("gh", [
  "repo",
  "view",
  "--json",
  "nameWithOwner",
  "--jq",
  ".nameWithOwner",
]);
const pending = refs.map(issueNumber);
const issues = new Map();
const parentEdges = new Map();
const blockerEdges = new Set();

while (pending.length > 0) {
  const number = pending.shift();
  if (issues.has(number)) continue;
  const issue = ghJson(`repos/${repository}/issues/${number}`);
  issues.set(number, issue);
  for (const child of ghJson(
    `repos/${repository}/issues/${number}/sub_issues?per_page=100`,
  )) {
    parentEdges.set(child.number, number);
    pending.push(child.number);
  }
  for (const blocker of ghJson(
    `repos/${repository}/issues/${number}/dependencies/blocked_by?per_page=100`,
  )) {
    blockerEdges.add(`${number}:${blocker.number}`);
    pending.push(blocker.number);
  }
}

const numbers = [...issues.keys()].sort((left, right) => left - right);
console.log(
  `GitHub planning scope: ${numbers.map((number) => `#${number}`).join(", ")}`,
);

if (dryRun) {
  run("bd", ["github", "pull", "--dry-run", ...numbers.map(String)], {
    stdio: "inherit",
  });
  console.log(
    "Dry run complete. No local labels or relationships were changed.",
  );
  process.exit(0);
}

const existingBeads = JSON.parse(
  run("bd", ["list", "--all", "--json", "--limit", "0"]),
);
const protectedRefs = new Set(
  existingBeads
    .filter((bead) => bead.labels.includes(executionLabel))
    .map((bead) => bead.external_ref),
);
const refsToPull = numbers.filter(
  (number) => !protectedRefs.has(issues.get(number).html_url),
);
if (refsToPull.length > 0)
  run("bd", ["github", "pull", ...refsToPull.map(String)], {
    stdio: "inherit",
  });
const beads = JSON.parse(
  run("bd", ["list", "--all", "--json", "--limit", "0"]),
);
const beadByRef = new Map(
  beads
    .filter((bead) => bead.external_ref)
    .map((bead) => [bead.external_ref, bead]),
);

function beadFor(number) {
  const issue = issues.get(number);
  const bead = beadByRef.get(issue.html_url);
  if (!bead)
    throw new Error(`Beads did not create a local issue for ${issue.html_url}`);
  return bead;
}

for (const [childNumber, parentNumber] of parentEdges) {
  const child = beadFor(childNumber);
  const parent = beadFor(parentNumber);
  if (child.parent !== parent.id)
    run("bd", ["update", child.id, "--parent", parent.id]);
}

for (const edge of blockerEdges) {
  const [blockedNumber, blockerNumber] = edge.split(":").map(Number);
  try {
    run("bd", [
      "dep",
      "add",
      beadFor(blockedNumber).id,
      beadFor(blockerNumber).id,
      "--type",
      "blocks",
    ]);
  } catch (error) {
    if (!String(error.stderr).includes("already exists")) throw error;
  }
}

for (const number of numbers) {
  const bead = beadFor(number);
  const issue = issues.get(number);
  if (bead.labels.includes(executionLabel)) continue;
  const isPlanning = issue.labels.some(
    (label) =>
      label.name === planningLabel || label.name.startsWith("wayfinder:"),
  );
  if (!bead.labels.includes(mirrorLabel))
    run("bd", ["label", "add", bead.id, mirrorLabel]);
  if (isPlanning && !bead.labels.includes(planningLabel))
    run("bd", ["label", "add", bead.id, planningLabel]);
  if (!isPlanning && bead.labels.includes(planningLabel))
    run("bd", ["label", "remove", bead.id, planningLabel]);
}

console.log(
  `Refreshed ${numbers.length} GitHub issues. Browse with: bd list --tree --limit 0`,
);
```
