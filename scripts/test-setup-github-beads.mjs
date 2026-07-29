import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("..", import.meta.url));
const fixtureRoot = join(root, "scripts/fixtures/setup-github-beads");
const read = (path) => readFile(join(root, path), "utf8");

const [skill, prerequisites, opencode, precedence, planningMirror] =
  await Promise.all([
    read("setup-github-beads/SKILL.md"),
    read("setup-github-beads/references/PREREQUISITES.md"),
    read("setup-github-beads/references/OPENCODE.md"),
    read("setup-github-beads/templates/TRACKER-PRECEDENCE.md"),
    read("setup-github-beads/templates/refresh-beads-plan.mjs"),
  ]);

const requiredSkillRules = [
  /Record the storage mode and issue count before/,
  /selecting Codex makes\nofficial OpenCode mode mandatory/,
  /assign exactly one generator to each path/,
  /every such directive must occur before the final\nprecedence block/,
  /Every managed marker has exactly one balanced begin\/end pair/,
  /a second setup pass proposes no changes/,
];
for (const rule of requiredSkillRules) {
  assert.match(skill, rule, `SKILL.md is missing rule: ${rule}`);
}

assert.ok(!skill.includes("github.repository"), "obsolete GitHub key remains");
assert.match(prerequisites, /github\.owner/);
assert.match(prerequisites, /github\.repo/);
assert.match(prerequisites, /\$\(gh auth token\)/);
assert.match(prerequisites, /Use `bd doctor` only when/);
assert.match(prerequisites, /newly initialized database to contain zero/);
assert.match(prerequisites, /counts match/);

for (const row of [
  /\| OpenCode\s+\| OpenCode lean\s+\| Lean\s+\|/,
  /\| OpenCode \+ Claude Code\s+\| OpenCode lean and Claude\s+\| Lean\s+\|/,
  /\| Codex \+ Claude Code\s+\| Codex and Claude official\s+\| Not applicable\s+\|/,
  /\| Codex \+ OpenCode\s+\| Codex and OpenCode\s+\| Official\s+\|/,
  /\| Codex \+ OpenCode \+ Claude Code\s+\| All official\s+\| Official\s+\|/,
]) {
  assert.match(opencode, row, `compatibility matrix is missing: ${row}`);
}
assert.match(
  opencode,
  /bd setup codex --check[\s\S]*bd setup opencode --check/,
);
assert.match(precedence, /`docs\/agents\/issue-tracker\.md` is authoritative/);
assert.equal(
  precedence.match(/<!-- BEGIN GITHUB BEADS PRECEDENCE -->/g)?.length,
  1,
);
assert.equal(
  precedence.match(/<!-- END GITHUB BEADS PRECEDENCE -->/g)?.length,
  1,
);
assert.match(skill, /scripts\/refresh-beads-plan\.mjs/);
assert.match(skill, /labels Wayfinder items `phase:planning`/);
assert.match(planningMirror, /--dry-run/);
assert.match(planningMirror, /sub_issues\?per_page=100/);
assert.match(planningMirror, /dependencies\/blocked_by\?per_page=100/);
assert.match(planningMirror, /\["list", "--all", "--json", "--limit", "0"\]/);
assert.match(planningMirror, /const mirrorLabel = "phase:mirror"/);
assert.match(planningMirror, /const executionLabel = "phase:execution"/);
assert.match(planningMirror, /bead\.labels\.includes\(executionLabel\)/);
assert.doesNotMatch(planningMirror, /github", "push"/);
execFileSync("node", [
  "--check",
  join(root, "setup-github-beads/templates/refresh-beads-plan.mjs"),
]);

const universalDirectives = [
  /all issue tracking/i,
  /all task tracking/i,
  /track all work/i,
  /do not use external issue trackers/i,
  /do not duplicate tracking systems/i,
];

function uncoveredDirectives(content) {
  const endMarker = "<!-- END GITHUB BEADS PRECEDENCE -->";
  const precedenceEnd = content.lastIndexOf(endMarker);
  const checkFrom = precedenceEnd === -1 ? 0 : precedenceEnd + endMarker.length;
  let offset = 0;
  return content.split("\n").flatMap((line, index) => {
    const lineOffset = offset;
    offset += line.length + 1;
    const conflicts = universalDirectives.some((pattern) => pattern.test(line));
    return conflicts && lineOffset >= checkFrom ? [{ line, index }] : [];
  });
}

const fixture = (name) => readFile(join(fixtureRoot, name), "utf8");
const [covered, inside, missing, neutral, uncovered] = await Promise.all([
  fixture("covered-instructions.md"),
  fixture("inside-precedence.md"),
  fixture("missing-precedence.md"),
  fixture("neutral-instructions.md"),
  fixture("uncovered-instructions.md"),
]);

assert.deepEqual(uncoveredDirectives(covered), []);
assert.deepEqual(uncoveredDirectives(inside), []);
assert.equal(uncoveredDirectives(missing).length, 1);
assert.deepEqual(uncoveredDirectives(neutral), []);
assert.equal(uncoveredDirectives(uncovered).length, 1);

console.log("Validated setup-github-beads behavioral invariants.");
