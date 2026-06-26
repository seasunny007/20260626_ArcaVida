# 维护者笔记：外置存储工作区性能指南 / Nota para mantenedores: guia de rendimiento en almacenamiento externo / Maintainer Note: External Storage Workspace Performance Guide

本文档提供中文、西班牙语和英文说明；如三种文本存在不一致，以中文文本为准。

Este documento ofrece informacion en chino, espanol e ingles. Si existe alguna inconsistencia entre los tres textos, prevalecera el texto chino.

This document provides Chinese, Spanish, and English information. If there is any inconsistency among the three texts, the Chinese text controls.

本文档是维护者笔记，仅适用于在 macOS 外置盘上开发或维护本仓库的场景。它不是 ArcaVida 的常规安装、部署或使用步骤。

Este documento es una nota para mantenedores y solo aplica al desarrollo o mantenimiento de este repositorio en discos externos de macOS. No forma parte de los pasos normales de instalacion, despliegue o uso de ArcaVida.

This document is a maintainer note for developing or maintaining this repository on macOS external drives. It is not part of the normal ArcaVida installation, deployment, or usage path.

本文档记录一种工作区性能模式：源码放在外置盘，较重的生成目录放在本机磁盘。

Esta guia registra un patron de rendimiento: el codigo fuente queda en el disco externo y los directorios generados pesados quedan en el disco local.

This guide captures the filesystem performance pattern for projects that live on an external drive while heavy generated folders live on the local machine.

## 问题 / Problem

外置盘，尤其是 exFAT 格式外置盘，适合在多台机器间移动工作区。但对于会创建大量小文件的开发负载，它们通常更慢或更不稳定，例如：

External drives, especially exFAT-formatted drives, are convenient for moving workspaces between machines. They are often slower or less reliable for development workloads that create many small files, such as:

```text
node_modules
.next
dist
out
coverage
playwright-report
test-results
language server caches
package manager install temp files
```

实用规则 / Practical rule:

```text
Keep source code on the external drive.
Keep generated dependency/build folders on the fastest local disk.
Link generated folders back into the repo.

源码留在外置盘。
依赖和构建产物放在最快的本机磁盘。
再把生成目录链接回仓库。
```

## 推荐设置 / Recommended Setup

对于 Node/Next.js 风格项目，使用 `scripts/external-workspace-cache.js` 完成以下步骤。

For a Node/Next.js-style project, use `scripts/external-workspace-cache.js` to:

1. 在用户最快的本机磁盘下创建本地缓存目录。 / Create a local cache directory under the user's fastest local disk.
2. 将 `package.json` 和 `package-lock.json` 复制到缓存目录。 / Copy `package.json` and `package-lock.json` into that cache directory.
3. 运行 `npm ci --prefix <cacheRoot>`，让依赖安装在本机。 / Run `npm ci --prefix <cacheRoot>` so dependencies install locally.
4. 用指向缓存的 symlink 或 junction 替换仓库内生成目录。 / Replace repo-local generated folders with symlinks or junctions to the cache.
5. 支持不重装依赖的快速重新链接模式。 / Support a fast relink mode that does not reinstall dependencies.
6. 支持依赖损坏或 lockfile 变化后的清理重建模式。 / Support a clean rebuild mode for corrupted installs or lockfile changes.

默认缓存根目录遵循平台习惯 / Default cache roots are platform-native:

```text
macOS:   ~/Library/Caches/<namespace>/<project-key>
Windows: %LOCALAPPDATA%\<namespace>\<project-key>
Linux:   ~/.cache/<namespace>/<project-key>
```

使用稳定的 namespace 和 project key，避免多个项目冲突。

Use a stable namespace and project key so multiple projects do not collide.

## Package Scripts / package 脚本

```json
{
  "scripts": {
    "workspace:external-cache": "node scripts/external-workspace-cache.js",
    "workspace:external-cache:link": "node scripts/external-workspace-cache.js --no-install",
    "workspace:external-cache:clean": "node scripts/external-workspace-cache.js --clean-cache",
    "repo:preflight": "node scripts/repo-preflight.js"
  }
}
```

首次设置 / For a one-time setup:

```bash
npm run workspace:external-cache
```

如果工具删除了 symlink，但本地缓存仍有效 / If a tool deletes symlinks but the local cache is still valid:

```bash
npm run workspace:external-cache:link
```

依赖损坏、lockfile 变化或安装中断后 / After dependency corruption, lockfile changes, or interrupted installs:

```bash
npm run workspace:external-cache:clean
```

对于非 Next 项目，把缓存脚本中的 `.next` 替换成对应生成目录，例如 `dist`、`build`、`.turbo`、`.vite` 或 `.cache`。

For non-Next projects, replace `.next` in the cache script with the relevant generated folder, such as `dist`, `build`, `.turbo`, `.vite`, or `.cache`.

## 自定义缓存位置 / Custom Cache Location

如果项目需要指定本地缓存磁盘，可使用环境变量。

Use environment variables when a project needs a specific local cache disk:

```bash
WORKSPACE_CACHE_ROOT="$HOME/Developer/cache/my-project" npm run workspace:external-cache
WORKSPACE_CACHE_NAMESPACE="my-company" WORKSPACE_CACHE_PROJECT_KEY="new-app" npm run workspace:external-cache
```

不要跨操作系统复用同一个依赖缓存。每台机器、每个 OS 都单独运行一次设置。

Do not reuse one dependency cache across operating systems. Run the setup once per machine and OS.

## VS Code 设置 / VS Code Settings

避免让文件监听和搜索扫描生成目录。本工作区通过 `.vscode/settings.json` 排除依赖树、框架产物、测试报告、覆盖率和 Git 内部目录。

Keep file watching and search away from generated folders. This workspace uses `.vscode/settings.json` to exclude dependency trees, framework output, test reports, coverage, and Git internals.

## Git 卫生 / Git Hygiene

macOS 外置盘可能创建名为 `._*` 的 AppleDouble 元数据文件。不要提交这些文件。

External macOS drives may create AppleDouble metadata files named `._*`. Never commit them.

发布或提交前清理 / Before release or commit cleanup:

```bash
find . -name '._*' -delete
```

运行 preflight 脚本，阻止生成目录、AppleDouble 文件、安装日志和本地密钥进入 Git。

Run the preflight script to block generated folders, AppleDouble files, install logs, and local secrets from entering Git:

```bash
npm run repo:preflight
```

最低阻止模式 / Minimum blocked patterns:

```text
.DS_Store
._*
node_modules/
.next/
out/
dist/
.vercel/
.venv/
coverage/
playwright-report/
test-results/
*.tsbuildinfo
npm-install.log
.env
.env.local
.env.*.local
```

## 操作规则 / Operating Rules

- 通过工作区缓存脚本安装依赖，不要直接装在外置盘。 / Install dependencies through the workspace cache script, not directly on the external drive.
- 源码、文档、测试、配置和需提交资产保留在仓库内。 / Keep source, docs, tests, configs, and committed assets in the repo.
- 依赖树、框架构建产物、测试报告和大型生成缓存放在本机磁盘。 / Keep dependency trees, framework build output, test reports, and large generated caches on local disk.
- lockfile 变化或安装中断后运行清理缓存命令。 / Run the clean cache command after a lockfile change or interrupted install.
- 工具移除 symlink 时运行快速重新链接命令。 / Run the fast relink command when a tool removes symlinks.
- 每个项目、机器、OS 和包管理器保留一套缓存。 / Keep one cache per project, machine, OS, and package manager.
- 将 symlink 生成目录视为可丢弃内容。 / Treat symlinked generated folders as disposable.
- 不要提交生成目录、本地缓存、密钥或 macOS 元数据。 / Do not commit generated folders, local caches, secrets, or macOS metadata.

## 新项目检查清单 / New Project Checklist

```text
1. Add scripts/external-workspace-cache.js. / 添加 scripts/external-workspace-cache.js。
2. Add package scripts for setup, relink, and clean rebuild. / 添加设置、重新链接和清理重建脚本。
3. Add watcher/search excludes to .vscode/settings.json. / 在 .vscode/settings.json 中添加监听和搜索排除项。
4. Add gitignore entries for generated folders and AppleDouble files. / 为生成目录和 AppleDouble 文件添加 gitignore 规则。
5. Add a repo preflight command to block generated or local-only files. / 添加仓库 preflight 命令以阻止生成或本地文件。
6. Run npm run workspace:external-cache once on each machine. / 每台机器运行一次 npm run workspace:external-cache。
7. Verify node_modules and build output are symlinks or junctions to local cache. / 确认 node_modules 和构建产物是指向本地缓存的 symlink 或 junction。
8. Run typecheck, tests, and build from the external-drive workspace. / 从外置盘工作区运行 typecheck、测试和构建。
```

## 何时不使用此模式 / When Not To Use This Pattern

以下情况使用普通本地 checkout。

Use a normal local checkout instead when:

```text
the repo is small and installs are fast
the external drive is APFS/NTFS on a fast SSD and performance is already acceptable
the toolchain does not tolerate symlinked dependency/build folders
the project requires reproducible generated output inside the repo path

仓库很小且安装很快
外置盘是快速 SSD 上的 APFS/NTFS，性能已经可接受
工具链不能容忍 symlink 依赖或构建目录
项目要求生成产物可复现地位于仓库路径内
```

这些情况下，保留 preflight 和 ignore 规则，但跳过 symlink 本地缓存设置。

In those cases, keep the preflight and ignore rules, but skip the symlinked local-cache setup.
