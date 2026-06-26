# 贡献指南 / Guia de contribucion / Contributing to ArcaVida

本文档提供中文、西班牙语和英文说明；如三种文本存在不一致，以中文文本为准。

Este documento ofrece informacion en chino, espanol e ingles. Si existe alguna inconsistencia entre los tres textos, prevalecera el texto chino.

This document provides Chinese, Spanish, and English information. If there is any inconsistency among the three texts, the Chinese text controls.

ArcaVida 是面向中文救援协调小组的早期社区预览项目，关注多语言求助信息到达之后的桌面流程：翻译辅助、提取、复核、跟踪和简报草稿。

ArcaVida es una vista previa comunitaria temprana para equipos de coordinacion de ayuda que trabajan en chino. Se centra en el flujo de escritorio despues de recibir mensajes de campo: ayuda de traduccion, extraccion, revision, seguimiento y borradores de informes.

ArcaVida is an early community preview for Chinese-language relief coordination teams. It focuses on the desk workflow after inbound field messages arrive: translation assistance, extraction, review, tracking, and briefing drafts.

欢迎能提升可靠性、隐私、安全、文档、部署或协调员可用性的贡献。

Son bienvenidas las contribuciones que mejoren fiabilidad, privacidad, seguridad, documentacion, despliegue o usabilidad para coordinadores.

Contributions are welcome when they improve reliability, privacy, safety, documentation, deployment, or coordinator usability.

## 基本规则 / Reglas basicas / Ground Rules

- 不要提交真实凭证、`.env` 文件、服务账号 JSON、本地数据库、终端日志或受灾者个人数据。
- No subas credenciales reales, archivos `.env`, JSON de cuentas de servicio, bases de datos locales, logs de terminal ni datos personales de personas afectadas.
- Do not commit real credentials, `.env` files, service account JSON files, local databases, terminal logs, or personal data from affected people.
- 不要提交原始私密求助信息，除非它们是合成、公开或充分匿名化的样例。
- No subas mensajes privados originales de emergencia salvo que sean sinteticos, publicos o suficientemente anonimizados.
- Do not submit raw emergency messages unless they are synthetic, public, or fully anonymized.
- 所有提取和翻译输出都只是桌面辅助材料；核实、升级、派遣或现场行动前必须人工复核。
- Todo resultado de extraccion y traduccion es solo material de apoyo de escritorio; requiere revision humana antes de verificar, escalar, despachar o actuar en campo.
- Treat all extraction and translation output as desk-support material that requires human review before verification, escalation, dispatch, or field action.
- 未经开发者或权利人书面授权，不得将 ArcaVida 用于商业产品、托管服务、咨询交付、托管运维或商业运营。
- Sin autorizacion previa por escrito del desarrollador o titular de derechos, no uses ArcaVida para productos comerciales, servicios alojados, consultoria, servicios gestionados u operaciones comerciales.
- Do not use ArcaVida for commercial products, hosted services, consulting delivery, managed services, or commercial operations without prior written authorization from the project developer or rights holder.
- 保持改动聚焦，避免在同一个 PR 中混入无关重写。
- Mantén los cambios enfocados y evita reescrituras no relacionadas en el mismo pull request.
- Keep changes focused. Avoid unrelated rewrites in the same pull request.

## 本地设置 / Configuracion local / Local Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

运行 Web 工作台 / Ejecutar la estacion web / Run the web workstation:

```bash
.venv/bin/uvicorn web.app:app --host 127.0.0.1 --port 8080
```

打开 `http://127.0.0.1:8080/`。

Abre `http://127.0.0.1:8080/`.

Open `http://127.0.0.1:8080/`.

## 质量检查 / Controles de calidad / Quality Checks

提交 PR 前运行以下检查。

Ejecuta estas comprobaciones antes de abrir un pull request.

Run these checks before opening a pull request:

```bash
python -m compileall bot core models config web scripts
python -m pytest -q
npm run repo:preflight
```

如果工作区位于 macOS 外置盘，最终检查前清理 AppleDouble 边车文件。

Si el espacio de trabajo esta en un disco externo de macOS, limpia los archivos AppleDouble antes de la comprobacion final.

If your workspace is on an external macOS drive, clean AppleDouble sidecar files before the final check:

```bash
find . -name '._*' -type f -delete
```

## Pull Requests / 拉取请求

请包含 / Include:
Incluye:

- 正在解决的问题。
- El problema que se resuelve.
- The problem being solved.
- 面向用户的行为变化。
- El cambio de comportamiento visible para usuarios.
- The user-facing behavior change.
- 已执行的测试或手动检查。
- Las pruebas o comprobaciones manuales realizadas.
- Tests or manual checks performed.
- 任何隐私、安全或部署影响。
- Cualquier impacto de privacidad, seguridad o despliegue.
- Any privacy, safety, or deployment impact.

较小、聚焦的 PR 更容易审查和合并。

Los pull requests pequenos y enfocados son mas faciles de revisar y fusionar.

Small pull requests are easier to review and merge.

## 适合贡献的方向 / Areas utiles de contribucion / Useful Contribution Areas

- 西语、中文、英文合成灾情样例。
- Ejemplos sinteticos de desastre en espanol, chino e ingles.
- Synthetic Spanish, Chinese, and English disaster-message samples.
- 提取规则和评估用例。
- Reglas de extraccion y casos de evaluacion.
- Extraction rules and evaluation cases.
- 隐私和安全审查。
- Revision de privacidad y seguridad.
- Privacy and safety review.
- 面向协调小组运行环境的部署文档。
- Documentacion de despliegue para entornos operados por equipos de coordinacion.
- Deployment documentation for coordinator-run environments.
- Web 工作台流程改进。
- Mejoras del flujo de la estacion web.
- Web workstation workflow improvements.
