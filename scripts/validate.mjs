import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("..", import.meta.url));
const entries = await readdir(root, { withFileTypes: true });
const errors = [];
let skillCount = 0;

async function readTextTree(directory) {
  const contents = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) contents.push(...(await readTextTree(path)));
    if (entry.isFile()) contents.push(await readFile(path, "utf8"));
  }
  return contents;
}

for (const entry of entries) {
  if (
    !entry.isDirectory() ||
    entry.name.startsWith(".") ||
    ["docs", "node_modules", "research", "scripts"].includes(entry.name)
  ) {
    continue;
  }

  const skillPath = join(root, entry.name, "SKILL.md");
  let content;
  try {
    content = await readFile(skillPath, "utf8");
  } catch {
    errors.push(`${entry.name}: missing SKILL.md`);
    continue;
  }

  skillCount += 1;
  const distributableContent = [content];
  for (const directory of ["references", "templates"]) {
    try {
      distributableContent.push(
        ...(await readTextTree(join(root, entry.name, directory))),
      );
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
  }

  if (
    distributableContent.some((text) => /\/(?:home|Users|tmp)\//.test(text))
  ) {
    errors.push(`${entry.name}: contains a machine-specific absolute path`);
  }

  const frontmatter = content.match(/^---\n([\s\S]*?)\n---/);
  if (!frontmatter) {
    errors.push(`${entry.name}: missing YAML frontmatter`);
    continue;
  }

  const name = frontmatter[1].match(/^name:\s*["']?([^\n"']+)/m)?.[1]?.trim();
  const description = frontmatter[1]
    .match(/^description:\s*["']?([^\n]+)/m)?.[1]
    ?.replace(/["']$/, "")
    .trim();
  if (name !== entry.name)
    errors.push(`${entry.name}: frontmatter name must match directory`);
  if (name && !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name))
    errors.push(
      `${entry.name}: name must use lowercase hyphen-separated words`,
    );
  if (name && name.length > 64)
    errors.push(`${entry.name}: name exceeds 64 characters`);
  if (!description) errors.push(`${entry.name}: missing description`);
  if (description && description.length > 1024)
    errors.push(`${entry.name}: description exceeds 1024 characters`);
  if (description?.includes("allowed-tools:"))
    errors.push(`${entry.name}: allowed-tools must be a frontmatter field`);
}

if (skillCount === 0) errors.push("no skills found");
if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}

console.log(`Validated ${skillCount} skills.`);
