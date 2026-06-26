# 一页使用说明 / Guia rapida de una pagina / One-page Usage Guide

本文档提供中文、西班牙语和英文说明；如三种文本存在不一致，以中文文本为准。

Este documento ofrece informacion en chino, espanol e ingles. Si existe alguna inconsistencia entre los tres textos, prevalecera el texto chino.

This document provides Chinese, Spanish, and English information. If there is any inconsistency among the three texts, the Chinese text controls.

本文是 ArcaVida 的优先阅读说明。它面向第一次接触项目的协调员、维护者和社区贡献者。

Este es el primer documento que se debe leer sobre ArcaVida. Esta escrito para coordinadores, mantenedores y contribuidores comunitarios que ven el proyecto por primera vez.

This is the first document to read for ArcaVida. It is written for coordinators, maintainers, and community contributors seeing the project for the first time.

## 一句话定位 / Posicionamiento en una frase / One-sentence Positioning

ArcaVida 是面向中文救援协调小组的信息分拣工作台，用于把多语言求助文本辅助整理成可人工复核的记录和中文简报草稿。

ArcaVida es una estacion de trabajo de clasificacion de informacion para equipos de coordinacion de ayuda que trabajan en chino. Ayuda a organizar mensajes multilingues de solicitud de ayuda en registros revisables por humanos y borradores de informes en chino.

ArcaVida is a triage workstation for Chinese-language relief coordination teams. It helps organize multilingual help-request messages into human-reviewable records and Chinese briefing drafts.

## 可以做什么 / Que puede hacer / What It Can Do

- 粘贴西语、中文或英文求助文本。 / Pegar texto de solicitud de ayuda en espanol, chino o ingles. / Paste Spanish, Chinese, or English help-request text.
- 辅助提示地点、需求、被困信号、优先级标签和备注。 / Sugerir ubicacion, necesidades, senales de personas atrapadas, etiquetas de prioridad y notas. / Suggest locations, needs, trapped-person signals, priority labels, and notes.
- 保存可追溯记录，并跟踪 `pending`、`verified`、`dispatched`、`closed` 状态。 / Guardar registros trazables y seguir los estados `pending`, `verified`, `dispatched` y `closed`. / Save traceable records and track `pending`, `verified`, `dispatched`, and `closed` statuses.
- 生成可人工编辑的中文简报草稿。 / Crear borradores de informes en chino editables por humanos. / Draft editable Chinese briefings.
- 在缺少外部 AI 凭证时，用本地回退逻辑处理样例文本。 / Usar logica local de respaldo para textos de ejemplo cuando faltan credenciales externas de IA. / Use local fallback behavior for sample text when external AI credentials are missing.

## 不能做什么 / Que no hace / What It Does Not Do

- 不核实事实。 / No verifica hechos. / It does not verify facts.
- 不定位人员。 / No localiza personas. / It does not locate people.
- 不派遣队伍。 / No despacha equipos. / It does not dispatch teams.
- 不替代现场判断。 / No sustituye el juicio en campo. / It does not replace field judgment.
- 不应接收未经授权的私密原始求助数据。 / No debe recibir datos privados originales de solicitud de ayuda sin autorizacion. / It should not receive unauthorized private raw help-request data.

## 安全使用原则 / Reglas de uso seguro / Safe-use Rules

- 只使用合成、公开或充分匿名化的样例进行测试和公开讨论。 / Usa solo ejemplos sinteticos, publicos o suficientemente anonimizados para pruebas y discusion publica. / Use only synthetic, public, or fully anonymized examples for testing and public discussion.
- 不要提交 `.env`、API key、bot token、服务账号 JSON、本地数据库或日志。 / No subas `.env`, API keys, bot tokens, JSON de cuentas de servicio, bases de datos locales ni logs. / Do not commit `.env`, API keys, bot tokens, service account JSON, local databases, or logs.
- 任何翻译、提取、优先级提示和简报草稿都必须人工复核。 / Toda traduccion, extraccion, pista de prioridad y borrador de informe requiere revision humana. / All translations, extraction results, priority hints, and briefing drafts require human review.
- 核实、升级、派遣或现场行动前，不得直接依赖系统输出。 / No dependas directamente de la salida del sistema antes de verificar, escalar, despachar o actuar en campo. / Do not rely directly on system output before verification, escalation, dispatch, or field action.

## 本地试运行 / Prueba local / Local Trial Run

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m pytest -q
.venv/bin/uvicorn web.app:app --host 127.0.0.1 --port 8080
```

打开 / Abrir / Open:

```text
http://127.0.0.1:8080/
```

可使用合成样例 / Ejemplo sintetico / Synthetic sample:

```text
Ubicacion: Caracas Centro. Hay una familia atrapada, necesita agua y comida.
```

## 发布与许可 / Publicacion y licencia / Release and License

ArcaVida 默认允许非商业使用。商业使用，包括付费产品、托管服务、咨询交付、托管运维或商业运营，必须事先取得开发者或权利人的书面授权。

ArcaVida permite el uso no comercial por defecto. El uso comercial, incluidos productos de pago, servicios alojados, entregas de consultoria, servicios gestionados u operaciones comerciales, requiere autorizacion previa por escrito del desarrollador o del titular de derechos.

ArcaVida allows non-commercial use by default. Commercial use, including paid products, hosted services, consulting delivery, managed services, or commercial operations, requires prior written authorization from the developer or rights holder.
