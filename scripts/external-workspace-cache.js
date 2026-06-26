#!/usr/bin/env node

const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const repoRoot = path.resolve(__dirname, "..");
const packageJsonPath = path.join(repoRoot, "package.json");
const lockfilePath = path.join(repoRoot, "package-lock.json");
const cacheNamespace = process.env.WORKSPACE_CACHE_NAMESPACE || "external-drive-workspaces";
const projectKey =
  process.env.WORKSPACE_CACHE_PROJECT_KEY ||
  path
    .basename(repoRoot)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
const cacheRoot = process.env.WORKSPACE_CACHE_ROOT || getDefaultCacheRoot();
const shouldInstall = !process.argv.includes("--no-install");
const shouldCleanCache = process.argv.includes("--clean-cache");

function getDefaultCacheRoot() {
  if (process.platform === "darwin") {
    return path.join(os.homedir(), "Library", "Caches", cacheNamespace, projectKey);
  }

  if (process.platform === "win32") {
    return path.join(
      process.env.LOCALAPPDATA || path.join(os.homedir(), "AppData", "Local"),
      cacheNamespace,
      projectKey,
    );
  }

  return path.join(
    process.env.XDG_CACHE_HOME || path.join(os.homedir(), ".cache"),
    cacheNamespace,
    projectKey,
  );
}

function removePath(targetPath) {
  fs.rmSync(targetPath, { recursive: true, force: true });
}

function ensureParent(targetPath) {
  fs.mkdirSync(path.dirname(targetPath), { recursive: true });
}

function replaceWithSymlink(linkPath, targetPath) {
  removePath(linkPath);
  ensureParent(targetPath);
  fs.mkdirSync(targetPath, { recursive: true });
  fs.symlinkSync(
    targetPath,
    linkPath,
    process.platform === "win32" ? "junction" : "dir",
  );
  removeAppleDoubleSidecar(linkPath);
}

function removeAppleDoubleSidecar(linkPath) {
  removePath(path.join(path.dirname(linkPath), `._${path.basename(linkPath)}`));
}

function copyInstallManifests() {
  fs.copyFileSync(packageJsonPath, path.join(cacheRoot, "package.json"));
  fs.copyFileSync(lockfilePath, path.join(cacheRoot, "package-lock.json"));
}

function filesMatch(leftPath, rightPath) {
  return (
    fs.existsSync(leftPath) &&
    fs.existsSync(rightPath) &&
    fs.readFileSync(leftPath, "utf8") === fs.readFileSync(rightPath, "utf8")
  );
}

function runNpmCi() {
  execFileSync(
    "npm",
    [
      "ci",
      "--prefix",
      cacheRoot,
      "--no-audit",
      "--no-fund",
      "--prefer-offline",
      "--loglevel=error",
    ],
    {
      cwd: repoRoot,
      stdio: "inherit",
    },
  );
}

function assertInstalledCache() {
  const nodeModulesPath = path.join(cacheRoot, "node_modules");
  const cachedPackageJsonPath = path.join(cacheRoot, "package.json");
  const cachedLockfilePath = path.join(cacheRoot, "package-lock.json");

  if (!fs.existsSync(nodeModulesPath) || !fs.existsSync(cachedLockfilePath)) {
    throw new Error(
      `Cached dependencies are missing at ${nodeModulesPath}. Run npm run workspace:external-cache first.`,
    );
  }

  if (
    !filesMatch(packageJsonPath, cachedPackageJsonPath) ||
    !filesMatch(lockfilePath, cachedLockfilePath)
  ) {
    throw new Error(
      "Cached dependency manifests are stale. Run npm run workspace:external-cache:clean after package or lockfile changes.",
    );
  }
}

function main() {
  fs.mkdirSync(cacheRoot, { recursive: true });

  if (shouldCleanCache) {
    removePath(path.join(cacheRoot, "node_modules"));
    removePath(path.join(cacheRoot, ".next"));
  }

  if (!shouldInstall) {
    assertInstalledCache();
  } else {
    copyInstallManifests();
  }

  replaceWithSymlink(
    path.join(repoRoot, "node_modules"),
    path.join(cacheRoot, "node_modules"),
  );
  replaceWithSymlink(path.join(repoRoot, ".next"), path.join(cacheRoot, ".next"));

  if (shouldInstall) {
    runNpmCi();
  }

  console.log(`Generated directories are linked to ${cacheRoot}`);
}

main();