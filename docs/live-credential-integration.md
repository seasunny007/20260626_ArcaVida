# 真实凭证联调清单 / Lista de integracion con credenciales reales / Live Credential Integration Checklist

本文档提供中文、西班牙语和英文说明；如三种文本存在不一致，以中文文本为准。

Este documento ofrece informacion en chino, espanol e ingles. Si existe alguna inconsistencia entre los tres textos, prevalecera el texto chino.

This document provides Chinese, Spanish, and English information. If there is any inconsistency among the three texts, the Chinese text controls.

本文档说明如何获取凭证并运行真实联调检查，同时避免把密钥放入聊天、源码仓库或日志。

Esta lista explica como obtener credenciales y ejecutar comprobaciones reales de integracion sin poner secretos en chats, repositorios de codigo fuente ni logs.

This checklist explains how to obtain credentials and run live integration checks without putting secrets in chat, source control, or logs.

## 安全规则 / Reglas de seguridad / Safety Rules

- 直接在本地终端或部署密钥管理器中输入密钥。
- Escribe los secretos directamente en tu terminal local o gestor de secretos de despliegue.
- Type secrets directly into your local terminal or deployment secret manager.
- 不要把 token、API key、服务账号 JSON 或 `.env` 内容粘贴到聊天中。
- No pegues tokens, API keys, JSON de cuentas de servicio ni contenido de `.env` en chats.
- Do not paste tokens, API keys, service account JSON, or `.env` contents into chat.
- 不要提交 `.env`、服务账号 JSON 文件、本地 SQLite 数据库或终端日志。
- No subas `.env`, archivos JSON de cuentas de servicio, bases de datos SQLite locales ni logs de terminal.
- Do not commit `.env`, service account JSON files, local SQLite databases, or terminal logs.
- 使用 `scripts/integration-smoke.py`；它会遮罩凭证值，只报告通过/失败细节。
- Usa `scripts/integration-smoke.py`; enmascara los valores de credenciales y solo informa detalles de exito o fallo.
- Use `scripts/integration-smoke.py`; it masks credential values and only reports pass/fail details.

## 1. Web 工作台管理员密码 / Web Workstation Admin Password

Telegram 不再是主要联调路径。本地开发可省略 `ADMIN_PASSWORD`。生产或共享使用时，请直接在终端或部署密钥管理器中设置。

Telegram is no longer the primary integration path. For local development, `ADMIN_PASSWORD` may be omitted. For production or shared use, set it directly in the terminal or deployment secret manager:

```bash
export ADMIN_PASSWORD="<local admin password>"
```

启动 Web 工作台 / Start the web workstation:

```bash
.venv/bin/uvicorn web.app:app --host 127.0.0.1 --port 8080
```

打开 / Open:

```text
http://127.0.0.1:8080/
```

## 2. Telegram Bot Token 可选旧适配器 / Telegram Bot Token Optional Legacy Adapter

1. 打开 Telegram 并与 `@BotFather` 对话。 / Open Telegram and chat with `@BotFather`.
2. 发送 `/newbot` 并按提示操作。 / Send `/newbot` and follow the prompts.
3. 只把 bot token 复制到本地终端环境。 / Copy the bot token only into your local terminal environment.
4. 启动 bot 一次并发送 `/start`；ArcaVida 会返回数字 chat id。 / Start the bot once and send `/start`; ArcaVida replies with your numeric chat id.
5. 将该数字 chat id 用于 `OPERATOR_CHAT_IDS`。 / Use that numeric chat id for `OPERATOR_CHAT_IDS`.

终端设置 / Terminal setup:

```bash
export TELEGRAM_TOKEN="<telegram bot token>"
export OPERATOR_CHAT_IDS="<your numeric telegram chat id>"
```

常见失败 / Common failures:

- `Unauthorized`：token 错误或复制时带了额外空格。 / Token is wrong or copied with extra spaces.
- 协调员命令被拒绝：`OPERATOR_CHAT_IDS` 与 `/start` 显示的 chat id 不匹配。 / Coordinator commands denied: `OPERATOR_CHAT_IDS` does not match the chat id shown by `/start`.
- Bot 收不到消息：可能已有其他进程或 webhook 正在消费 updates。 / Bot does not receive messages: another process or webhook may already be consuming updates.

## 3. 翻译服务 / Translation Provider

默认值是 `TRANSLATION_PROVIDER=llm`。它与信息提取共用 OpenAI 兼容 API 凭证，避免强依赖 Google 访问。

The default is `TRANSLATION_PROVIDER=llm`. It uses the same OpenAI-compatible API credentials as extraction, which avoids a hard dependency on Google access.

推荐设置 / Recommended setup:

```bash
export TRANSLATION_PROVIDER="llm"
export OPENAI_API_KEY="<openai-compatible api key>"
export OPENAI_BASE_URL=""
export OPENAI_MODEL="gpt-3.5-turbo"
```

对于 OpenAI 兼容服务，请把 `OPENAI_BASE_URL` 和 `OPENAI_MODEL` 设置为该服务商的值。

For an OpenAI-compatible provider, set `OPENAI_BASE_URL` and `OPENAI_MODEL` to that provider's values.

运行 / Run:

```bash
.venv/bin/python scripts/integration-smoke.py translate
```

如果没有翻译凭证，ArcaVida 会保留原文，并继续执行本地启发式提取。

If no translation credential is available, ArcaVida keeps the original text and still performs local heuristic extraction.

## 4. 可选 Google Translate 凭证 / Optional Google Translate Credentials

Google Translate 是可选项。仅在具备 Google Cloud 访问条件时使用。

Google Translate is optional. Use it only when Google Cloud access is available.

安装可选依赖 / Install the optional dependency:

```bash
pip install -e '.[google-translate]'
```

1. 打开 Google Cloud Console。 / Open Google Cloud Console.
2. 创建或选择项目。 / Create or select a project.
3. 启用 Cloud Translation API。 / Enable Cloud Translation API.
4. 创建有权调用 Translation API 的服务账号。 / Create a service account with permission to call Translation API.
5. 为该服务账号创建 JSON key。 / Create a JSON key for that service account.
6. 将 JSON 存放在仓库外，最好放在本地私有凭证目录。 / Store the JSON outside the repository, preferably under a local private credentials folder.

终端设置 / Terminal setup:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/google-service-account.json"
export TRANSLATION_PROVIDER="google"
```

常见失败 / Common failures:

- `DefaultCredentialsError`：路径错误或文件不可读。 / Path is wrong or file is unreadable.
- `403 Permission denied`：未启用 Translation API，或服务账号缺少权限。 / Translation API is not enabled or service account lacks permission.
- 翻译返回原文：凭证缺失，或 smoke 脚本回退到本地行为。 / Translation returns original text: credentials are missing or the smoke script fell back locally.

## 5. OpenAI 或兼容 LLM 凭证 / OpenAI Or Compatible LLM Credentials

OpenAI 官方 API / For OpenAI official API:

```bash
export OPENAI_API_KEY="<openai api key>"
export OPENAI_BASE_URL=""
export OPENAI_MODEL="gpt-3.5-turbo"
```

OpenAI 兼容服务 / For an OpenAI-compatible provider:

```bash
export OPENAI_API_KEY="<compatible provider api key>"
export OPENAI_BASE_URL="https://provider.example.com/v1"
export OPENAI_MODEL="<compatible model name>"
```

常见失败 / Common failures:

- `401 Unauthorized`：key 无效或属于其他服务商。 / Key is invalid or belongs to a different provider.
- `404 model_not_found`：该服务商不存在这个模型名。 / Model name does not exist for that provider.
- JSON/schema 回退：模型输出无效，应用回退到本地提取。 / JSON/schema fallback behavior: model output was invalid, so the app fell back to local extraction.

## 6. 本地隐私与运行设置 / Local Privacy And Runtime Settings

为 chat id 哈希使用足够长的本地随机 salt。

Use a long random local salt for chat id hashing:

```bash
export SOURCE_CHAT_HASH_SALT="$(openssl rand -hex 32)"
```

本地开发保持 / For local development, keep:

```bash
export ENVIRONMENT="development"
```

生产环境设置 / For production, set:

```bash
export ENVIRONMENT="production"
export WEBHOOK_SECRET_PATH="<random path that is not the Telegram token>"
```

## 7. 运行 Smoke 检查 / Run Smoke Checks

运行全部真实检查 / Run all live checks:

```bash
.venv/bin/python scripts/integration-smoke.py all
```

逐项运行 / Run one check at a time:

```bash
.venv/bin/python scripts/integration-smoke.py telegram
.venv/bin/python scripts/integration-smoke.py translate
.venv/bin/python scripts/integration-smoke.py llm
```

脚本会打印遮罩后的凭证状态，例如 `set:abcd...wxyz`；不应打印完整密钥。

The script prints masked credential status such as `set:abcd...wxyz`; it should never print full secrets.

## 8. 可选旧版 Bot / Optional Legacy Bot

Smoke 检查通过后 / After smoke checks pass:

```bash
.venv/bin/python -m bot.main
```

在 Telegram 中 / In Telegram:

1. 发送 `/start`。 / Send `/start`.
2. 确认返回的 chat id 与 `OPERATOR_CHAT_IDS` 匹配。 / Confirm the returned chat id matches `OPERATOR_CHAT_IDS`.
3. 发送西语样例消息。 / Send a Spanish sample message.
4. 运行 `/briefing` 并确认记录出现。 / Run `/briefing` and verify the record appears.

样例消息 / Sample message:

```text
Ubicación: Caracas Centro. Hay una familia atrapada, necesita agua y comida.
```
