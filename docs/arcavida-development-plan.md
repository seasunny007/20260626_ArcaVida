# ArcaVida（轻舟）开发计划 / Plan de desarrollo / Development Plan

本文档提供中文、西班牙语和英文说明；如三种文本存在不一致，以中文文本为准。

Este documento ofrece informacion en chino, espanol e ingles. Si existe alguna inconsistencia entre los tres textos, prevalecera el texto chino.

This document provides Chinese, Spanish, and English information. If there is any inconsistency among the three texts, the Chinese text controls.

文档版本：1.0.0
Version del documento: 1.0.0
Document version: 1.0.0

最后更新：2026-06-26
Ultima actualizacion: 2026-06-26
Last updated: 2026-06-26

许可：ArcaVida Community Non-Commercial License（默认仅允许非商业使用，商业化需开发者或权利人书面授权）
Licencia: ArcaVida Community Non-Commercial License. El uso no comercial esta permitido por defecto; el uso comercial requiere autorizacion previa por escrito del desarrollador o titular de derechos.
License: ArcaVida Community Non-Commercial License. Non-commercial use is allowed by default; commercial use requires prior written authorization from the developer or rights holder.

## 项目概述 / Resumen del proyecto / Project Overview

ArcaVida（轻舟）是一款面向中文救援协调小组的信息分拣工作台，覆盖“收到多语言求助文本之后、人工核实和协调之前”的桌面流程：协调员粘贴西语/中文灾情文本，系统辅助翻译、结构化提取、优先级提示、状态管理和中文简报草稿生成。项目不定位为公众求助入口、现场救援系统、资源调度平台或应急派遣权威；所有输出都必须经过人工复核。项目以降低上手和运维门槛为设计目标，源代码可公开查看和非商业使用，商业化需开发者或权利人书面授权；项目可独立运行，也可作为未来“伏羲”完整版的原型。

ArcaVida es una estacion de trabajo de clasificacion de informacion para equipos de coordinacion de ayuda que trabajan en chino. Cubre el flujo de escritorio despues de recibir mensajes multilingues y antes de la verificacion o coordinacion humana: los coordinadores pegan textos de campo en espanol o chino, y el sistema ayuda con traduccion, extraccion estructurada, pistas de prioridad, gestion de estados y borradores de informes en chino. El proyecto no es un portal publico de solicitud de ayuda, sistema de rescate en campo, plataforma de asignacion de recursos ni autoridad de despacho de emergencias; todo resultado requiere revision humana. El objetivo de diseno es reducir la barrera de uso y operacion. El codigo fuente esta disponible para uso no comercial; el uso comercial requiere autorizacion previa por escrito del desarrollador o titular de derechos. El proyecto puede ejecutarse de forma independiente y tambien servir como prototipo para el futuro sistema completo "Fuxi".

ArcaVida is a triage workstation for Chinese-language relief coordination teams. It covers the desk workflow after multilingual messages arrive and before human verification or coordination: coordinators paste Spanish or Chinese field text, and the system assists with translation, structured extraction, priority hints, status management, and Chinese briefing drafts. The project is not a public help-request portal, field rescue system, resource-dispatch platform, or emergency-dispatch authority; all output requires human review. The design goal is to lower setup and operations barriers. The source is available for non-commercial use, while commercial use requires written authorization from the developer or rights holder. The project can run independently and may also serve as a prototype for the future full "Fuxi" system.

## MVP 范围 / Alcance MVP / MVP Scope

| 功能模块 / Module                 | 说明 / Description                                                                                                                                                                                                                          |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 消息接收 / Message intake         | Web 工作台粘贴/导入文本，尝试识别西语/中文。 / Paste/import text in the web workstation and attempt Spanish/Chinese detection.                                                                                                              |
| 智能翻译 / Translation assistance | OpenAI 兼容 LLM 翻译优先，Google Translate 作为可选插件，缺少凭证时本地回退。 / Prefer OpenAI-compatible LLM translation; Google Translate is optional; local fallback is used when credentials are missing.                                |
| 信息提取 / Information extraction | 辅助提取地点、需求、被困情况、优先级提示、暗语标记，缺少凭证时启发式回退。 / Assist extraction of location, needs, trapped-person signals, priority hints, and coded-language markers; use heuristic fallback when credentials are missing. |
| 俚语/暗语匹配 / Slang matching    | `config/slang.json` 内置委内瑞拉西语俚语/暗语词典。 / `config/slang.json` includes Venezuelan Spanish slang and coded-language hints.                                                                                                       |
| 结构化存储 / Structured storage   | SQLite 保存原文、译文、提取字段、状态与备注。 / SQLite stores raw text, translation, extracted fields, status, and notes.                                                                                                                   |
| 简报生成 / Briefing drafts        | Web 工作台生成可人工编辑的中文简报草稿。 / The web workstation generates editable Chinese briefing drafts.                                                                                                                                  |
| 状态管理 / Status management      | Web 工作台更新 `verified`、`dispatched`、`closed` 与备注。 / The web workstation updates `verified`, `dispatched`, `closed`, and notes.                                                                                                     |

## 不包含功能 / Fuera de alcance / Out of Scope

- 自动抓取社交媒体。 / Automatic social media crawling.
- 图像/视频分析。 / Image/video analysis.
- 语音识别与方言支持。 / Speech recognition and dialect support.
- 多队伍协同、路况、资源匹配等复杂模块。 / Complex multi-team collaboration, road conditions, or resource matching.
- 离线部署。 / Offline deployment.
- 多级权限管理。 / Multi-level permission management.

## 技术选型 / Elecciones tecnicas / Technology Choices

| 组件 / Component             | 选型 / Choice                                                                                                                     |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| 语言 / Language              | Python 3.11+                                                                                                                      |
| Web 框架 / Web framework     | FastAPI                                                                                                                           |
| Bot 库 / Bot library         | python-telegram-bot v20+（保留为可选适配器） / python-telegram-bot v20+, retained as optional adapter                             |
| 翻译 API / Translation API   | OpenAI 兼容接口优先，Google Translate 可选。 / OpenAI-compatible API preferred; Google Translate optional.                        |
| LLM 提取 / LLM extraction    | OpenAI GPT-3.5-turbo，后续可替换 GLM-4-flash。 / OpenAI GPT-3.5-turbo, later replaceable with GLM-4-flash.                        |
| 数据库 / Database            | SQLite                                                                                                                            |
| 部署 / Deployment            | 中国大陆云服务器/VPS + Docker Compose，SQLite 本地持久化。 / Mainland China cloud/VPS + Docker Compose, local SQLite persistence. |
| 开发工具 / Development tools | VS Code + Python + Pylance                                                                                                        |

## 数据模型 / Modelo de datos / Data Model

主表 `rescue_records` 已在 `models/database.py` 中实现，包含：`id`、`raw_text`、`detected_lang`、`translated_text`、`location`、`needs`、`trapped`、`priority`、`slang_alert`、`slang_hint`、`status`、`volunteer_notes`、`created_at`、`updated_at`、`source_chat_id`。其中 `source_chat_id` 使用本地 salt 做 SHA-256 哈希后存储。

La tabla principal `rescue_records` esta implementada en `models/database.py`. Incluye: `id`, `raw_text`, `detected_lang`, `translated_text`, `location`, `needs`, `trapped`, `priority`, `slang_alert`, `slang_hint`, `status`, `volunteer_notes`, `created_at`, `updated_at` y `source_chat_id`. `source_chat_id` se guarda como hash SHA-256 con una sal local.

The main table `rescue_records` is implemented in `models/database.py`. It includes: `id`, `raw_text`, `detected_lang`, `translated_text`, `location`, `needs`, `trapped`, `priority`, `slang_alert`, `slang_hint`, `status`, `volunteer_notes`, `created_at`, `updated_at`, and `source_chat_id`. `source_chat_id` is stored as a SHA-256 hash with a local salt.

## 项目结构 / Estructura del proyecto / Project Structure

```text
web/                  本地 Web 工作台与 API / local web workstation and API
bot/                  可选 Telegram Bot 适配器 / optional Telegram Bot adapter
core/                 翻译、提取、俚语匹配、简报生成 / translation, extraction, slang matching, briefing generation
models/               SQLite 连接、CRUD、Pydantic 模型 / SQLite connection, CRUD, Pydantic models
config/               环境变量与俚语词典 / environment variables and slang dictionary
tests/                离线单元测试 / offline unit tests
docs/                 项目计划与工作区性能指南 / project plan and workspace performance guides
scripts/              外置盘工作区缓存与预检脚本 / external-drive workspace cache and preflight scripts
```

## 响应与发布节奏 / Ritmo de respuesta y publicacion / Response and Release Rhythm

高时效救援场景要求开发和发布节奏保持克制：先保证信息录入、人工复核和记录连续性，再逐步改善简报、部署和协作流程。公开文档不把时间窗口作为宣传点，也不承诺现场救援效果。

Los escenarios de ayuda sensibles al tiempo exigen un ritmo de desarrollo y publicacion sobrio: primero asegurar ingreso de informacion, revision humana y continuidad de registros; despues mejorar informes, despliegue y colaboracion. La documentacion publica no usa ventanas de tiempo como promocion ni promete resultados de rescate en campo.

Time-sensitive relief contexts require a restrained development and release rhythm: first ensure information intake, human review, and record continuity, then improve briefings, deployment, and collaboration. Public documentation does not use response windows as promotional framing or promise field-rescue outcomes.

## 环境变量 / Variables de entorno / Environment Variables

参考 `.env.example`。生产环境必须设置 `ADMIN_PASSWORD` 与 `SOURCE_CHAT_HASH_SALT`。启用真实 AI 能力时优先设置 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`；Google Translate 仅作为可选 provider。

Consulta `.env.example`. Los despliegues de produccion deben configurar `ADMIN_PASSWORD` y `SOURCE_CHAT_HASH_SALT`. Para habilitar capacidades reales de IA, configura primero `OPENAI_API_KEY`, `OPENAI_BASE_URL` y `OPENAI_MODEL`; Google Translate es solo un proveedor opcional.

See `.env.example`. Production deployments must set `ADMIN_PASSWORD` and `SOURCE_CHAT_HASH_SALT`. To enable real AI capabilities, set `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL` first; Google Translate is only an optional provider.

## 合规与隐私 / Cumplimiento y privacidad / Compliance and Privacy

- 默认只处理志愿者主动转发的文本。 / De forma predeterminada, procesa solo textos reenviados voluntariamente por voluntarios. / By default, process only text voluntarily forwarded by volunteers.
- `source_chat_id` 不明文入库。 / `source_chat_id` no se almacena en texto claro. / `source_chat_id` is not stored in plaintext.
- `.env`、本地数据库、生成目录和 AppleDouble 元数据均由 `.gitignore` 与 `repo:preflight` 阻止提交。 / `.env`, bases de datos locales, directorios generados y metadatos AppleDouble son bloqueados por `.gitignore` y `repo:preflight`. / `.env`, local databases, generated directories, and AppleDouble metadata are blocked from commits by `.gitignore` and `repo:preflight`.

## 质量保障 / Aseguramiento de calidad / Quality Assurance

```bash
python -m compileall bot core models config
python -m pytest
npm run repo:preflight
```

测试默认不调用真实外部 API。

Las pruebas no llaman APIs externas reales por defecto.

Tests do not call real external APIs by default.
