<div align="center">
<h1>ArcaVida（轻舟） <small>v2.0.0</small></h1>
<p><strong>地震救援碎片化信息支持系统</strong></p>
<p><small>Sistema de apoyo para rescate ante terremotos</small></p>
<p><small>Earthquake Relief Information Support</small></p>
</div>

**本文档提供中文、西班牙语和英文说明；如三种文本存在不一致，以中文文本为准。**

**Este documento ofrece informacion en chino, espanol e ingles. Si existe alguna inconsistencia entre los tres textos, prevalecera el texto chino.**

**This document provides Chinese, Spanish, and English information. If there is any inconsistency among the three texts, the Chinese text controls.**

**发布叙事：v2.0.0 是 ArcaVida 社区预览版的公开 GitHub Release。Public Release 表示代码、文档、部署路径和安全边界已经整理到可公开审阅和本地试运行的状态；不表示系统可直接用于现场救援、自动核实、资源调度或应急派遣。**

**Narrativa de publicacion: v2.0.0 es la publicacion publica en GitHub de la vista previa comunitaria de ArcaVida. Public Release significa que el codigo, la documentacion, las rutas de despliegue y los limites de seguridad estan listos para revision publica y pruebas locales; no significa que el sistema pueda usarse directamente para rescate en campo, verificacion automatica, asignacion de recursos ni despacho de emergencias.**

**Release narrative: v2.0.0 is the public GitHub Release of the ArcaVida community preview. Public Release means the code, documentation, deployment paths, and safety boundaries are ready for public review and local trial use; it does not mean the system can be used directly for field rescue, automatic verification, resource dispatch, or emergency dispatch.**

**一句话简介：惊悉委内瑞拉发生强烈地震，26日晚间紧急开发了 ArcaVida（轻舟）系统：从社交媒体多语种碎片化求助信息中，梳理线索，为精准高效救援提供参考。**

**欢迎有相关领域知识经验的人士加入开发维护工作。**

**Resumen en una frase: tras conocer la noticia del fuerte terremoto en Venezuela, ArcaVida（轻舟）se desarrollo de emergencia la noche del dia 26 para organizar pistas de rescate a partir de informacion multilingue y fragmentada de solicitud de ayuda en redes sociales, aportando referencias para una respuesta mas precisa y eficiente.**

**Damos la bienvenida a personas con conocimientos o experiencia en campos relacionados para sumarse al desarrollo y mantenimiento.**

**One-sentence summary: after learning of the strong earthquake in Venezuela, ArcaVida（轻舟）was urgently developed on the evening of the 26th to organize rescue leads from multilingual, fragmented help-request information on social media, providing references for more precise and efficient rescue response.**

**People with relevant domain knowledge or experience are welcome to join the development and maintenance work.**

ArcaVida（轻舟）是面向中文救援协调小组的公开社区预览版信息分拣工作台。它用于协调小组收到西语、中文或英文现场文本之后的桌面复核流程：翻译辅助、结构化提取、人工复核、状态跟踪、备注和中文简报草稿。

ArcaVida es una estacion de trabajo de triaje en vista previa comunitaria para equipos de coordinacion de ayuda que trabajan en chino. Apoya la revision de escritorio despues de recibir mensajes de campo en espanol, chino o ingles: ayuda de traduccion, extraccion estructurada, revision humana, seguimiento de estado, notas y borradores de informes en chino.

ArcaVida is a public community-preview triage workstation for Chinese-language relief coordination teams. It supports desk-side review after a team receives Spanish, Chinese, or English field messages: translation assistance, structured extraction, human review, status tracking, notes, and Chinese briefing drafts.

第一次阅读请先看：[一页使用说明 / One-page Usage Guide](docs/usage-quick-guide.md)。它用最短篇幅说明适用场景、不能做什么、安全使用原则和本地试运行步骤。

Para una primera lectura, comienza con [一页使用说明 / One-page Usage Guide](docs/usage-quick-guide.md). Resume el uso previsto, lo que no hace, las reglas de uso seguro y los pasos para una prueba local.

First-time readers should start with [一页使用说明 / One-page Usage Guide](docs/usage-quick-guide.md). It briefly covers the intended use, non-goals, safe-use rules, and local trial run steps.

**定位 / Positioning:** 面向中文救援协调小组的信息分拣工作台，把多语言求助文本辅助整理成可人工复核的记录和简报草稿。它不是公众求助入口、现场救援系统、资源调度平台或应急派遣权威。

**Posicionamiento:** estacion de trabajo de clasificacion de informacion para equipos de coordinacion de ayuda que trabajan en chino. Ayuda a organizar mensajes multilingues de solicitud de ayuda como registros revisables por humanos y borradores de informes. No es un portal publico de solicitud de ayuda, un sistema de rescate en campo, una plataforma de asignacion de recursos ni una autoridad de despacho de emergencias.

ArcaVida focuses on multilingual relief-message triage for Chinese-language coordination teams. It helps turn multilingual messages into reviewable records and briefing drafts. It is not a public help-request portal, field rescue system, resource-dispatch platform, or emergency-dispatch authority.

**状态 / Status:** v2.0.0 是公开发布的社区预览版，适合本地试运行、架构审阅、合成样例测试和协调流程评估。未经人工复核，不得将 ArcaVida 输出用于核实、升级、派遣或现场行动。

**Estado:** v2.0.0 es una vista previa comunitaria publicada publicamente, adecuada para pruebas locales, revision de arquitectura, ejemplos sinteticos y evaluacion de flujos de coordinacion. Sin revision humana, los resultados de ArcaVida no deben usarse para verificacion, escalamiento, despacho ni accion en campo.

v2.0.0 is a publicly released community preview suitable for local trials, architecture review, synthetic-sample testing, and coordination-workflow evaluation. ArcaVida must not be used for verification, escalation, dispatch, or field action without human review.

## 能力边界 / What It Does

- 辅助把非结构化求助文本整理为可复核记录。
- Ayuda a convertir textos no estructurados de solicitud de ayuda en registros revisables.
- Helps turn unstructured inbound field messages into reviewable relief records.
- 提示地点、需求、被困信号、优先级标签和备注，供人工复核。
- Sugiere ubicacion, necesidades, senales de personas atrapadas, etiquetas de prioridad y notas para revision humana.
- Suggests locations, needs, trapped-person signals, priority labels, and notes for human review.
- 支持可选 LLM 或 Google 翻译；缺少外部凭证时保留本地开发回退能力。
- Admite LLM opcional o Google Translate; sin credenciales externas conserva una ruta local de respaldo para desarrollo.
- Provides optional LLM or Google translation, with local fallback behavior for development.
- 使用 SQLite 保存记录，并支持 `pending`、`verified`、`dispatched`、`closed` 状态。
- Guarda registros en SQLite y admite los estados `pending`, `verified`, `dispatched` y `closed`.
- Stores records in SQLite and supports `pending`, `verified`, `dispatched`, and `closed` statuses.
- 为协调和后勤复核生成中文简报草稿。
- Genera borradores de informes en chino para revision de coordinacion y logistica.
- Drafts Chinese briefings for coordinator and logistics review.
- `bot/` 中保留旧版 Telegram 适配器；本地 Web 工作台是默认入口。
- Se conserva un adaptador heredado de Telegram en `bot/`; la estacion web local es la entrada predeterminada.
- Keeps a legacy Telegram adapter in `bot/`; the local web workstation is the default entry point.

## 安全与隐私 / Safety and Privacy

- 不要在 Issue、PR、聊天或日志中粘贴真实凭证、`.env` 内容、API key、服务账号 JSON 或 bot token。
- No pegues credenciales reales, contenido de `.env`, API keys, JSON de cuentas de servicio ni bot tokens en issues, pull requests, chats o logs.
- Do not paste real credentials, `.env` contents, API keys, service account JSON, or bot tokens into issues, pull requests, chat, or logs.
- 不要发布私密原始消息、电话号码、精确个人位置、身份证件或受灾者其他个人数据。
- No publiques mensajes privados originales, telefonos, ubicaciones personales exactas, documentos de identidad ni otros datos personales de personas afectadas.
- Do not publish raw private messages, phone numbers, exact personal locations, identity documents, or other personal data from affected people.
- 测试和社区讨论只使用合成、公开或充分匿名化的样例。
- Usa solo ejemplos sinteticos, publicos o suficientemente anonimizados para pruebas y discusion comunitaria.
- Use synthetic, public, or fully anonymized examples for testing and community discussion.
- 翻译和提取结果只作为桌面辅助输出；核实、升级、派遣或现场行动前必须人工复核。
- Trata la traduccion y la extraccion solo como apoyo de escritorio. Se requiere revision humana antes de verificar, escalar, despachar o actuar en campo.
- Treat translation and extraction as desk-support output only. Human review is required before verification, escalation, dispatch, or field action.
- 生产或共享部署必须设置 `SOURCE_CHAT_HASH_SALT`、`ADMIN_PASSWORD`，并配套适当的密钥管理。
- Los despliegues de produccion o compartidos deben configurar `SOURCE_CHAT_HASH_SALT`, `ADMIN_PASSWORD` y controles adecuados de gestion de secretos.
- Production or shared deployments must set `SOURCE_CHAT_HASH_SALT`, `ADMIN_PASSWORD`, and appropriate secret-management controls.

## 快速开始 / Quick Start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m pytest
```

启动 Web 工作台 / Start the web workstation:

```bash
.venv/bin/uvicorn web.app:app --host 127.0.0.1 --port 8080
```

打开 / Open:

```text
http://127.0.0.1:8080/
```

可使用合成样例测试 / Try a synthetic sample:

```text
Ubicacion: Caracas Centro. Hay una familia atrapada, necesita agua y comida.
```

默认翻译 provider 是 OpenAI 兼容 LLM。缺少外部凭证时，核心模块仍保留本地检测和启发式提取，便于离线开发与测试。

El proveedor de traduccion predeterminado es un LLM compatible con OpenAI. Cuando faltan credenciales externas, los modulos principales conservan deteccion local y extraccion heuristica para desarrollo y pruebas sin conexion.

The default translation provider is an OpenAI-compatible LLM. When external credentials are missing, core modules keep local detection and heuristic extraction available for offline development and tests.

## 可选翻译服务 / Optional Translation Providers

OpenAI 兼容服务 / OpenAI-compatible providers:

```bash
export TRANSLATION_PROVIDER=llm
export OPENAI_API_KEY="<openai-compatible api key>"
export OPENAI_BASE_URL="https://provider.example.com/v1"
export OPENAI_MODEL="<compatible model name>"
```

中国大陆部署可使用 DeepSeek、通义千问、智谱、Moonshot 等兼容服务。

Para despliegues en China continental se pueden usar servicios compatibles como DeepSeek, Qwen, Zhipu o Moonshot.

For mainland China deployments, compatible providers such as DeepSeek, Qwen, Zhipu, or Moonshot can be used.

```bash
export TRANSLATION_PROVIDER=llm
export OPENAI_API_KEY="<模型服务 API key>"
export OPENAI_BASE_URL="https://api.deepseek.com/v1"
export OPENAI_MODEL="deepseek-chat"
```

Google Translate 是可选项 / Google Translate is optional:

```bash
pip install -e '.[google-translate]'
export TRANSLATION_PROVIDER=google
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/google-service-account.json"
```

## Docker

Docker Compose 默认使用中国大陆 PyPI 镜像，并把 SQLite 数据持久化到 `./data`。

Docker Compose usa de forma predeterminada un espejo PyPI de China continental y persiste los datos SQLite en `./data`.

Docker Compose uses a mainland China PyPI mirror by default and persists SQLite data under `./data`.

```bash
docker compose up --build
```

## 质量门禁 / Quality Gates

```bash
python -m compileall bot core models config web scripts
python -m pytest -q
npm run repo:preflight
```

如果仓库位于 macOS 外置盘，使用缓存脚本维护生成目录位置。

When this repository is on an external macOS drive, maintain generated cache locations with:

```bash
npm run workspace:external-cache
```

如果出现 AppleDouble 边车文件，最终 preflight 或 push 前先清理。

If AppleDouble sidecar files appear, remove them before final preflight or push checks:

```bash
find . -name '._*' -type f -delete
```

## 贡献 / Contributing

社区帮助优先集中在以下方向：合成灾情样例、提取规则和评估用例、隐私与安全审查、协调小组部署测试、Web 工作台流程改进。

La ayuda comunitaria es mas util en estas areas: ejemplos sinteticos de desastre, reglas de extraccion y casos de evaluacion, revision de privacidad y seguridad, pruebas de despliegue para equipos de coordinacion y mejoras del flujo de la estacion web.

Community help is most useful in these areas: synthetic disaster-message samples, extraction rules and evaluation cases, privacy and safety review, deployment testing for coordinator-run environments, and web workstation workflow improvements.

提交 Issue 或 PR 前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

Lee [CONTRIBUTING.md](CONTRIBUTING.md) antes de abrir issues o pull requests.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening issues or pull requests.

## 文档 / Documentation

- [一页使用说明 / One-page Usage Guide](docs/usage-quick-guide.md)
- [ArcaVida VS Code 开发计划 / VS Code Development Plan](docs/arcavida-development-plan.md)
- [物资发放追踪系统设计 / Material Distribution Tracking Design](docs/material-distribution-tracking.md)
- [中国大陆部署指南 / Mainland China Deployment Guide](docs/deployment-cn.md)
- [委内瑞拉部署指南 / Venezuela Deployment Guide](docs/deployment-venezuela.md)
- [真实凭证联调清单 / Live Credential Integration Checklist](docs/live-credential-integration.md)
- [发布安全说明 / Release Safety Notes](docs/release-safety.md)
- [发布检查清单 / Release Checklist](docs/release-checklist.md)

## 维护者笔记 / Maintainer Notes

- [外置存储工作区性能指南 / External Storage Workspace Performance Guide](docs/external-storage-workspace-performance.md)：仅供在 macOS 外置盘上开发或维护本仓库时参考，不是 ArcaVida 的常规使用或部署步骤。
- [External Storage Workspace Performance Guide](docs/external-storage-workspace-performance.md): for development or maintenance on macOS external drives only; it is not part of the normal ArcaVida usage or deployment path.

## 许可 / License

ArcaVida 采用 [ArcaVida Community Non-Commercial License](LICENSE)。默认允许非商业使用。商业使用，包括基于 ArcaVida 的付费产品、托管服务、咨询交付、托管运维或商业运营，必须事先取得开发者或权利人的书面授权。

ArcaVida se publica bajo la [ArcaVida Community Non-Commercial License](LICENSE). El uso no comercial esta permitido por defecto. El uso comercial, incluidos productos de pago, servicios alojados, entregas de consultoria, servicios gestionados u operaciones comerciales basadas en ArcaVida, requiere autorizacion previa por escrito del desarrollador del proyecto o del titular de derechos.

ArcaVida is released under the [ArcaVida Community Non-Commercial License](LICENSE). Non-commercial use is allowed by default. Commercial use, including paid products, hosted services, consulting delivery, managed services, or commercial operations based on ArcaVida, requires prior written authorization from the project developer or rights holder.
