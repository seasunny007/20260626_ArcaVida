#!/usr/bin/env node

const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const repoRoot = path.resolve(__dirname, "..");
const blockedPatterns = [
  ".DS_Store",
  "._*",
  "node_modules/",
  ".next/",
  "out/",
  "dist/",
  ".vercel/",
  ".venv/",
  "__pycache__/",
  ".pytest_cache/",
  ".mypy_cache/",
  ".ruff_cache/",
  "coverage/",
  "playwright-report/",
  "test-results/",
  "*.tsbuildinfo",
  "npm-install.log",
  "arca_vida.db",
  "*.sqlite",
  "*.sqlite3",
  ".env",
  ".env.local",
  ".env.*.local",
];
const allowedGeneratedSymlinks = new Set([
  "node_modules",
  ".next",
  "out",
  "dist",
  ".vercel",
  ".venv",
  "__pycache__",
  ".pytest_cache",
  ".mypy_cache",
  ".ruff_cache",
  "coverage",
  "playwright-report",
  "test-results",
]);

function runGit(args) {
  return execFileSync("git", args, {
    cwd: repoRoot,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "ignore"],
  });
}

function isGitRepo() {
  try {
    runGit(["rev-parse", "--is-inside-work-tree"]);
    return true;
  } catch {
    return false;
  }
}

function listGitCandidateFiles() {
  const output = runGit(["ls-files", "--cached", "--others", "--exclude-standard"]);
  return output.split(/\r?\n/).filter(Boolean);
}

function listWorkspaceFiles(directory = repoRoot, prefix = "") {
  const ignoredDirectories = new Set([".git"]);
  const files = [];

  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (ignoredDirectories.has(entry.name)) {
      continue;
    }

    const relativePath = prefix ? `${prefix}/${entry.name}` : entry.name;
    const absolutePath = path.join(directory, entry.name);

    if (entry.isSymbolicLink() && allowedGeneratedSymlinks.has(entry.name)) {
      continue;
    }

    if (entry.isDirectory() && !entry.isSymbolicLink()) {
      files.push(relativePath);
      files.push(...listWorkspaceFiles(absolutePath, relativePath));
      continue;
    }

    files.push(relativePath);
  }

  return files;
}

function globToRegExp(pattern) {
  const escaped = pattern.replace(/[.+^${}()|[\]\\]/g, "\\$&");
  const withWildcards = escaped.replace(/\*/g, "[^/]*");

  if (pattern.endsWith("/")) {
    return new RegExp(`(^|/)${withWildcards.slice(0, -1)}(/.*)?$`);
  }

  return new RegExp(`(^|/)${withWildcards}$`);
}

function findBlockedFiles(files) {
  const matchers = blockedPatterns.map((pattern) => ({
    pattern,
    matcher: globToRegExp(pattern),
  }));

  return files.flatMap((file) =>
    matchers
      .filter(({ matcher }) => matcher.test(file))
      .map(({ pattern }) => ({ file, pattern })),
  );
}

function main() {
  const files = isGitRepo() ? listGitCandidateFiles() : listWorkspaceFiles();
  const blockedFiles = findBlockedFiles(files);

  if (blockedFiles.length > 0) {
    console.error("repo:preflight blocked local-only or generated files:");
    for (const { file, pattern } of blockedFiles) {
      console.error(`- ${file} matched ${pattern}`);
    }
    process.exit(1);
  }

  console.log("repo:preflight passed");
}

main();