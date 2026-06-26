# 中国大陆部署指南 / Guia de despliegue en China continental / Mainland China Deployment Guide

本文档提供中文、西班牙语和英文说明；如三种文本存在不一致，以中文文本为准。

Este documento ofrece informacion en chino, espanol e ingles. Si existe alguna inconsistencia entre los tres textos, prevalecera el texto chino.

This document provides Chinese, Spanish, and English information. If there is any inconsistency among the three texts, the Chinese text controls.

本文档给出 ArcaVida 在中国大陆 VPS 或云服务器上的推荐部署方式。默认路径不依赖 Telegram、Google Cloud 或境外 PaaS，使用本地 Web 工作台、SQLite 持久化和中国大陆可访问的 OpenAI 兼容模型服务。

Esta guia describe una ruta recomendada para desplegar ArcaVida en VPS o servidores en la nube de China continental. La ruta predeterminada no depende de Telegram, Google Cloud ni PaaS fuera de China continental; usa la estacion web local, persistencia SQLite y proveedores de modelos compatibles con OpenAI disponibles en China continental.

This guide describes a recommended deployment path for ArcaVida on mainland China VPS or cloud hosts. The default path does not depend on Telegram, Google Cloud, or overseas PaaS platforms; it uses the local web workstation, SQLite persistence, and OpenAI-compatible model providers available in mainland China.

## 部署判断 / Decision de despliegue / Deployment Decision

推荐方案：中国大陆云服务器/VPS + Docker Compose + Nginx/Caddy 反向代理 + HTTPS。

Ruta recomendada: servidor en la nube/VPS de China continental + Docker Compose + proxy inverso Nginx/Caddy + HTTPS.

Recommended path: mainland China cloud/VPS + Docker Compose + Nginx/Caddy reverse proxy + HTTPS.

原因：依赖少、迁移简单、数据在本机 `./data` 目录持久化，适合协调小组先跑通样例流程或受控内测流程。公开域名部署前按服务地区要求完成备案、域名解析和 HTTPS 证书配置。

Motivo: menos dependencias, migracion sencilla y persistencia local en `./data`. Es adecuado para que equipos de coordinacion prueben primero flujos de ejemplo o pruebas controladas. Antes de exponer un dominio publico, completa el registro ICP, DNS y certificados HTTPS segun los requisitos de la region de servicio.

Reason: fewer dependencies, simple migration, and local persistence under `./data`. This is suitable for coordinator teams to run sample flows or controlled pilot flows first. Before exposing a public domain, complete ICP filing, DNS, and HTTPS certificate setup according to the service region.

## 服务器准备 / Preparacion del servidor / Server Preparation

最低配置：1 vCPU、1 GB 内存、10 GB 磁盘。建议配置：2 vCPU、2 GB 内存、40 GB 磁盘。

Minimo: 1 vCPU, 1 GB de RAM, 10 GB de disco. Recomendado: 2 vCPU, 2 GB de RAM, 40 GB de disco.

Minimum: 1 vCPU, 1 GB RAM, 10 GB disk. Recommended: 2 vCPU, 2 GB RAM, 40 GB disk.

安装 Docker 与 Compose 插件后，克隆源码并进入项目目录：

Despues de instalar Docker y el plugin Compose, clona el codigo fuente y entra al directorio del proyecto:

After installing Docker and the Compose plugin, clone the source and enter the project directory:

```bash
git clone <your-repo-url> arcavida
cd arcavida
cp .env.example .env
```

编辑 `.env`，至少设置：

Edita `.env` y configura al menos:

Edit `.env` and set at least:

```bash
ENVIRONMENT=production
ADMIN_PASSWORD=<强密码>
SOURCE_CHAT_HASH_SALT=<openssl rand -hex 32 生成的随机值>
TRANSLATION_PROVIDER=llm
OPENAI_API_KEY=<模型服务 API key>
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

## 中国大陆可访问模型服务示例 / Ejemplos de proveedores accesibles en China continental / Mainland China Accessible Model Provider Examples

ArcaVida 使用 OpenAI 兼容 Chat Completions 接口。以下示例只需要替换 `.env` 中的 `OPENAI_BASE_URL` 和 `OPENAI_MODEL`。

ArcaVida usa una interfaz Chat Completions compatible con OpenAI. Los ejemplos siguientes solo requieren reemplazar `OPENAI_BASE_URL` y `OPENAI_MODEL` en `.env`.

ArcaVida uses an OpenAI-compatible Chat Completions interface. The examples below only require replacing `OPENAI_BASE_URL` and `OPENAI_MODEL` in `.env`.

| 服务商              | `OPENAI_BASE_URL` 示例                              | `OPENAI_MODEL` 示例 |
| ------------------- | --------------------------------------------------- | ------------------- |
| DeepSeek            | `https://api.deepseek.com/v1`                       | `deepseek-chat`     |
| 阿里云百炼/通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus`         |
| 智谱 GLM            | `https://open.bigmodel.cn/api/paas/v4`              | `glm-4-flash`       |
| Moonshot            | `https://api.moonshot.cn/v1`                        | `moonshot-v1-8k`    |

以服务商最新文档为准。如果供应商要求不同的鉴权头或非 OpenAI 兼容协议，需要先通过网关适配成 OpenAI 兼容接口。

Sigue siempre la documentacion mas reciente del proveedor. Si un proveedor requiere cabeceras de autenticacion diferentes o un protocolo no compatible con OpenAI, adaptalo primero mediante una pasarela.

Always follow the provider's latest documentation. If a provider requires different authentication headers or a non-OpenAI-compatible protocol, adapt it through a gateway first.

## 启动服务 / Start the Service

```bash
docker compose up -d --build
docker compose ps
```

健康检查：

Health check:

```bash
curl http://127.0.0.1:8080/health
```

如果只在服务器本机或内网使用，访问：

If using only from the server itself or an internal network, open:

```text
http://<服务器内网或公网 IP>:8080/
```

公网生产环境建议只让 Nginx/Caddy 暴露 80/443，并把 `8080` 限制在本机或安全组内网。

For public production exposure, only expose 80/443 through Nginx/Caddy and restrict `8080` to localhost or an internal security group.

## Nginx 反向代理示例 / Nginx Reverse Proxy Example

```nginx
server {
    listen 80;
    server_name arcavida.example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

HTTPS 证书可以使用云厂商证书、acme.sh 或 Caddy 自动签发；具体取决于域名和服务器环境。

HTTPS certificates can come from the cloud provider, acme.sh, or Caddy automatic issuance, depending on the domain and server environment.

## 数据与备份 / Data and Backup

Compose 会把数据库保存在宿主机：

Compose stores databases on the host:

```text
./data/arca_vida.db
```

备份命令：

Backup command:

```bash
mkdir -p backups
cp data/arca_vida.db "backups/arca_vida-$(date +%Y%m%d-%H%M%S).db"
```

`.env`、`data/`、备份目录和日志都不得提交到源码仓库。

Do not commit `.env`, `data/`, backup directories, or logs to source control.

## 联调检查 / Integration Checks

进入容器运行：

Run inside the container:

```bash
docker compose exec arcavida python scripts/integration-smoke.py translate llm
```

若没有配置模型服务，翻译和 LLM 检查会跳过；Web 工作台仍可用本地 fallback 处理样例文本。

If no model provider is configured, translation and LLM checks are skipped; the web workstation can still use local fallback behavior for sample text.

## 运维命令 / Operations Commands

查看日志：

View logs:

```bash
docker compose logs -f --tail=100 arcavida
```

更新版本：

Update version:

```bash
git pull
docker compose up -d --build
```

停止服务：

Stop service:

```bash
docker compose down
```

不要在生产服务器执行会删除 `data/` 的清理命令。

Do not run cleanup commands that delete `data/` on production servers.
