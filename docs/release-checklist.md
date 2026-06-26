# 发布检查清单 / Lista de verificacion de publicacion / Release Checklist

本文档提供中文、西班牙语和英文说明；如三种文本存在不一致，以中文文本为准。

Este documento ofrece informacion en chino, espanol e ingles. Si existe alguna inconsistencia entre los tres textos, prevalecera el texto chino.

This document provides Chinese, Spanish, and English information. If there is any inconsistency among the three texts, the Chinese text controls.

## 发布目标 / Objetivo de publicacion / Release Goal

首版发布目标是提供一个简洁、可靠、可用、可扩展的社区预览版本，不追求功能完美。

El objetivo de la primera publicacion es ofrecer una vista previa comunitaria simple, fiable, usable y extensible, sin perseguir perfeccion funcional.

The first release aims to provide a simple, reliable, usable, and extensible community-preview version, without aiming for feature perfection.

## 必须通过 / Obligatorio / Required

- [ ] 工作区无未提交改动。 / El arbol de trabajo no tiene cambios sin confirmar. / The working tree has no uncommitted changes.
- [ ] `python -m compileall bot core models config web scripts`
- [ ] `python -m pytest -q`
- [ ] `npm run repo:preflight`
- [ ] 公开文件不包含本机路径、个人账号、凭证、token、`.env`、本地数据库或日志。 / Los archivos publicos no contienen rutas locales, cuentas personales, credenciales, tokens, `.env`, bases de datos locales ni logs. / Public files do not contain local paths, personal accounts, credentials, tokens, `.env`, local databases, or logs.
- [ ] 发布版源码和公开文档只描述当前发布范围。 / El codigo y la documentacion publica describen solo el alcance de la publicacion actual. / Release source and public docs describe only the current release scope.
- [ ] README、许可、安全、贡献、行为准则和主要 docs 均为中文、西班牙语、英文三语，并声明中文为准。 / README, licencia, seguridad, contribucion, conducta y docs principales estan en chino, espanol e ingles, con chino como texto aplicable. / README, license, security, contributing, conduct, and main docs are in Chinese, Spanish, and English, with Chinese as controlling text.
- [ ] Release notes 写明适用场景、非目标、安全边界、许可和验证结果。 / Las notas de publicacion indican alcance, no objetivos, limites de seguridad, licencia y validacion. / Release notes state scope, non-goals, safety boundaries, license, and validation.

## GitHub 设置 / Configuracion de GitHub / GitHub Settings

- [ ] 仓库描述克制，不使用夸大或容易误解的词。 / La descripcion del repositorio es sobria y evita terminos exagerados o ambiguos. / Repository description is restrained and avoids exaggerated or ambiguous terms.
- [ ] Issues 开启，用于 bug、文档、部署和合成样例反馈。 / Issues esta habilitado para bugs, documentacion, despliegue y ejemplos sinteticos. / Issues are enabled for bugs, docs, deployment, and synthetic-sample feedback.
- [ ] Discussions 暂不开启。 / Discussions permanece deshabilitado por ahora. / Discussions remain disabled for now.
- [ ] 优先启用私密漏洞报告或 Security Advisories。 / Se prefiere habilitar reporte privado de vulnerabilidades o Security Advisories. / Private vulnerability reporting or Security Advisories should be enabled where available.
- [ ] 使用 GitHub Release 发布，不把 `main` 当作正式发布物。 / Publicar mediante GitHub Release, no tratar `main` como artefacto oficial. / Publish through GitHub Releases, not by treating `main` as the official artifact.

## Release 页面生成 / Generacion de Release / Release Page Generation

公开 Release 页面可以自动生成，但本项目默认采用“自动命令 + 人工审校发布说明”的方式。生成内容只应来自当前发布范围、验证结果和安全边界，不应从非当前公开范围的提交信息自动摘取变更记录。

La pagina publica de Release puede generarse automaticamente, pero este proyecto usa por defecto comandos automaticos con notas revisadas por una persona. El contenido debe venir solo del alcance actual, resultados de validacion y limites de seguridad; no debe extraerse automaticamente de commits fuera del alcance publico actual.

The public Release page can be generated automatically, but this project defaults to automatic commands with human-reviewed notes. Content should come only from the current release scope, validation results, and safety boundaries; it should not automatically summarize commits outside the current public scope.

```bash
gh release create v0.2.0-alpha --target main --prerelease --title "v0.2.0-alpha - First Public Alpha" --notes-file release-notes.md
```

GitHub 的 `--generate-notes` 可用于历史已清理、提交信息适合公开展示的后续版本；敏感场景首版不建议直接使用。

`--generate-notes` de GitHub puede usarse en versiones posteriores cuando el historial publico ya esta limpio y los mensajes de commit son adecuados para publicacion; no se recomienda directamente para una primera version sensible.

GitHub `--generate-notes` can be used for later releases when public history is clean and commit messages are suitable for display; it is not recommended directly for a sensitive first release.

## 发布后 / Despues de publicar / After Release

- [ ] 小范围邀请救援协调、隐私安全、西语审校和开源维护者审阅。 / Invitar a un grupo pequeno de coordinacion de ayuda, privacidad/seguridad, revision en espanol y mantenedores de codigo abierto. / Invite a small group of relief coordination, privacy/safety, Spanish review, and open-source maintainers.
- [ ] 不在公开 Issue 中处理真实个案、定位请求或派遣请求。 / No gestionar casos reales, ubicacion ni despacho en issues publicos. / Do not handle real cases, location requests, or dispatch requests in public issues.
- [ ] 只使用合成、公开或充分匿名化样例。 / Usar solo ejemplos sinteticos, publicos o suficientemente anonimizados. / Use only synthetic, public, or fully anonymized examples.
