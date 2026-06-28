# ArcaVida v2.0.0 Release Notes

## 发布定位 / Posicionamiento / Positioning

v2.0.0 是 ArcaVida（轻舟）社区预览版的公开发布。它面向公开审阅和本地试运行；不用于现场救援、自动核实、资源调度或应急派遣。

v2.0.0 es la publicacion publica de la vista previa comunitaria de ArcaVida（轻舟）. Esta dirigida a revision publica y pruebas locales; no se usa para rescate en campo, verificacion automatica, asignacion de recursos ni despacho de emergencias.

v2.0.0 is the public release of the ArcaVida community preview. It is intended for public review and local trial use; it is not for field rescue, automatic verification, resource dispatch, or emergency dispatch.

## 能力范围 / Alcance / Scope

- 面向中文救援协调小组的桌面信息分拣工作台。
- Estacion de trabajo de triaje de escritorio para equipos de coordinacion que trabajan en chino.
- Desk-side triage workstation for Chinese-language relief coordination teams.
- 支持西语、中文、英文现场文本的翻译辅助、结构化提取、人工复核、状态跟踪、备注和中文简报草稿。
- Apoya traduccion asistida, extraccion estructurada, revision humana, seguimiento de estado, notas y borradores de informes en chino para textos de campo en espanol, chino e ingles.
- Supports translation assistance, structured extraction, human review, status tracking, notes, and Chinese briefing drafts for Spanish, Chinese, and English field messages.
- 默认本地 Web 工作台；`bot/` 中的 Telegram 适配器仅作为旧版可选入口保留。
- La estacion web local es la entrada predeterminada; el adaptador de Telegram en `bot/` se conserva solo como entrada heredada opcional.
- The local web workstation is the default entry point; the Telegram adapter in `bot/` remains only as an optional legacy path.

## 非目标 / No objetivos / Non-Goals

- 不是公众求助入口。
- No es un portal publico de solicitud de ayuda.
- It is not a public help-request portal.
- 不是现场救援系统、自动核实系统、资源调度平台或应急派遣权威。
- No es un sistema de rescate en campo, sistema de verificacion automatica, plataforma de asignacion de recursos ni autoridad de despacho de emergencias.
- It is not a field rescue system, automatic verification system, resource-dispatch platform, or emergency-dispatch authority.
- 不承诺救援结果、覆盖地区、可用性、响应时间或事实核实能力。
- No promete resultados de rescate, cobertura geografica, disponibilidad, tiempos de respuesta ni capacidad de verificacion de hechos.
- It does not promise rescue outcomes, geographic coverage, availability, response times, or fact verification.

## 安全边界 / Limites de seguridad / Safety Boundaries

- 所有翻译、提取、优先级和简报输出都只是桌面辅助信息；核实、升级、派遣或现场行动前必须人工复核。
- Toda traduccion, extraccion, prioridad e informe es solo apoyo de escritorio; se requiere revision humana antes de verificar, escalar, despachar o actuar en campo.
- All translation, extraction, priority, and briefing output is desk-support information only; human review is required before verification, escalation, dispatch, or field action.
- 公共演示、Issue、PR 和社区讨论只应使用合成、公开或充分匿名化样例。
- Las demostraciones publicas, issues, pull requests y discusiones comunitarias solo deben usar ejemplos sinteticos, publicos o suficientemente anonimizados.
- Public demos, issues, pull requests, and community discussion should use only synthetic, public, or fully anonymized samples.
- 不要在公开仓库或聊天中发布真实凭证、API key、bot token、`.env`、电话号码、精确个人位置、身份证件或私密求助原文。
- No publiques credenciales reales, API keys, bot tokens, `.env`, telefonos, ubicaciones personales exactas, documentos de identidad ni mensajes privados originales en repositorios publicos o chats.
- Do not publish real credentials, API keys, bot tokens, `.env`, phone numbers, exact personal locations, identity documents, or raw private help messages in public repositories or chats.

## 部署路径 / Rutas de despliegue / Deployment Paths

- 本地试运行：按 README 的 Quick Start 启动 Web 工作台。
- Prueba local: inicia la estacion web siguiendo el Quick Start del README.
- Local trial: start the web workstation using the README Quick Start.
- Docker：使用 `docker compose up --build`，SQLite 数据默认持久化到 `./data`。
- Docker: usa `docker compose up --build`; los datos SQLite se persisten por defecto en `./data`.
- Docker: use `docker compose up --build`; SQLite data is persisted under `./data` by default.
- 中国大陆部署：参考 `docs/deployment-cn.md`，使用 OpenAI-compatible 国内模型服务和镜像源。
- Despliegue en China continental: consulta `docs/deployment-cn.md` y usa servicios de modelo compatibles con OpenAI y espejos locales.
- Mainland China deployment: see `docs/deployment-cn.md` and use OpenAI-compatible domestic model providers and mirrors.
- 委内瑞拉部署：参考 `docs/deployment-venezuela.md`，优先考虑低带宽、本地/区域 VPS、访问控制和数据保护。
- Despliegue en Venezuela: consulta `docs/deployment-venezuela.md`, priorizando bajo ancho de banda, VPS local/regional, control de acceso y proteccion de datos.
- Venezuela deployment: see `docs/deployment-venezuela.md`, prioritizing low bandwidth, local/regional VPS, access control, and data protection.

## 验证结果 / Validacion / Validation

发布前门禁：

```text
PYTHONPATH=. .venv/bin/pytest -q
14 passed

npm run repo:preflight
repo:preflight passed
```

## 许可 / Licencia / License

ArcaVida 使用 ArcaVida Community Non-Commercial License。默认允许非商业使用；商业使用必须事先取得开发者或权利人的书面授权。

ArcaVida se publica bajo ArcaVida Community Non-Commercial License. El uso no comercial esta permitido por defecto; el uso comercial requiere autorizacion previa por escrito del desarrollador del proyecto o del titular de derechos.

ArcaVida is released under the ArcaVida Community Non-Commercial License. Non-commercial use is allowed by default; commercial use requires prior written authorization from the project developer or rights holder.
