# 委内瑞拉部署指南 / Guia de despliegue en Venezuela / Venezuela Deployment Guide

本文档提供中文、西班牙语和英文说明；如三种文本存在不一致，以中文文本为准。

Este documento ofrece informacion en chino, espanol e ingles. Si existe alguna inconsistencia entre los tres textos, prevalecera el texto chino.

This document provides Chinese, Spanish, and English information. If there is any inconsistency among the three texts, the Chinese text controls.

本文档给出 ArcaVida 在委内瑞拉现场、近场或面向当地协作网络部署时的建议路径。它与中国大陆部署指南分离：本指南优先考虑当地网络稳定性、低带宽访问、地图与地理编码可用性、数据保护和人工复核流程。

Esta guia describe una ruta recomendada para desplegar ArcaVida en Venezuela, cerca del terreno o para redes locales de colaboracion. Esta separada de la guia de China continental: prioriza estabilidad de red local, acceso con bajo ancho de banda, disponibilidad de mapas y geocodificacion, proteccion de datos y revision humana.

This guide describes a recommended path for deploying ArcaVida in Venezuela, near the field, or for local collaboration networks. It is separate from the mainland China guide: it prioritizes local network stability, low-bandwidth access, map and geocoding availability, data protection, and human review.

## 部署判断 / Decision de despliegue / Deployment Decision

推荐方案：本地或区域 VPS + Docker Compose + HTTPS 反向代理 + 严格访问控制。

Ruta recomendada: VPS local o regional + Docker Compose + proxy inverso HTTPS + control estricto de acceso.

Recommended path: local or regional VPS + Docker Compose + HTTPS reverse proxy + strict access control.

适用场景：协调小组需要在当地网络条件下查看、复核、标注和导出线索。ArcaVida 不应作为公众求助入口，也不应直接替代现场核实、派遣或应急指挥系统。

Casos adecuados: equipos de coordinacion que necesitan revisar, marcar y exportar pistas bajo condiciones de red locales. ArcaVida no debe usarse como portal publico de solicitud de ayuda ni reemplazar verificacion en campo, despacho o sistemas de mando de emergencia.

Suitable use: coordination teams that need to review, annotate, and export leads under local network conditions. ArcaVida should not be used as a public help-request portal and must not replace field verification, dispatch, or emergency command systems.

## 服务器与网络 / Servidor y red / Server and Network

最低配置：1 vCPU、1 GB 内存、10 GB 磁盘。建议配置：2 vCPU、2 GB 内存、40 GB 磁盘。

Minimo: 1 vCPU, 1 GB de RAM, 10 GB de disco. Recomendado: 2 vCPU, 2 GB de RAM, 40 GB de disco.

Minimum: 1 vCPU, 1 GB RAM, 10 GB disk. Recommended: 2 vCPU, 2 GB RAM, 40 GB disk.

建议：

- 优先选择靠近使用者的区域节点，降低地图和页面加载延迟。
- 只向受控协调小组开放访问，不公开收集真实求助数据。
- 在不稳定网络下，优先使用 Web 工作台的手动粘贴、批量导入和本地缓存能力。
- 对外暴露时必须使用 HTTPS，`8080` 只允许本机或内网访问。

## 环境变量 / Variables de entorno / Environment Variables

复制 `.env.example` 后，至少设置：

Despues de copiar `.env.example`, configura al menos:

After copying `.env.example`, set at least:

```bash
ENVIRONMENT=production
ADMIN_PASSWORD=<strong local admin password>
SOURCE_CHAT_HASH_SALT=<random high-entropy value>
TRANSLATION_PROVIDER=llm
OPENAI_API_KEY=<openai-compatible model provider key>
OPENAI_BASE_URL=<provider base url>
OPENAI_MODEL=<provider model name>
PIP_INDEX_URL=https://pypi.org/simple
```

地理编码与地图瓦片建议单独评估：

Configura geocodificacion y teselas de mapa segun disponibilidad local:

Configure geocoding and map tiles according to local availability:

```bash
GEOCODER_PROVIDER=nominatim
GEOCODER_API_KEY=
GEOCODER_BASE_URL=https://nominatim.openstreetmap.org
GEOCODER_CACHE_PATH=./data/geocoder_cache.json
MAP_TILE_LAYER=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

如果网络无法稳定访问默认地图服务，应改用可访问的地图瓦片服务或预先缓存地图数据。不要在公开仓库提交真实地理编码缓存。

Si la red no puede acceder de forma estable al servicio de mapas predeterminado, usa un proveedor de teselas accesible o prepara cache de mapas. No subas caches reales de geocodificacion al repositorio publico.

If the network cannot reliably access the default map service, use an accessible tile provider or prepare cached map data. Do not commit real geocoding caches to the public repository.

## 启动服务 / Start the Service

```bash
docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8080/health
```

受控访问建议：

- 通过 Nginx/Caddy 暴露 HTTPS。
- 配置强 `ADMIN_PASSWORD`。
- 限制安全组、反向代理 allowlist 或 VPN 访问。
- 不在公共页面展示真实个人信息、电话号码、精确住址或未核实个案。

## 数据保护 / Proteccion de datos / Data Protection

委内瑞拉部署可能更接近真实个案数据，默认采取更严格的边界：

- 只处理公开、授权、志愿者主动转发或充分匿名化的数据。
- 不把真实原始消息、电话号码、身份证件、精确个人住址或照片样本提交到仓库、Issue、PR 或聊天。
- 导出文件默认只给受控协调小组使用，不做公开发布。
- 地理编码结果和置信度只作为复核线索，不作为自动核实、派遣或现场行动依据。
- 删除、匿名化和备份策略由部署团队在本地执行并记录。

## 地图与地理编码 / Mapas y geocodificacion / Maps and Geocoding

推荐策略：

1. 先使用手动录入和批量缓存跑通流程。
2. 对高频地址启用本地缓存，降低外部 API 调用。
3. 对低置信度或多结果地址标记人工复核。
4. 若使用第三方地理编码或地图服务，按该服务条款控制配额、缓存和展示方式。
5. 真实 API 联调只在本地或受控环境执行，不进入默认测试。

## 备份与运维 / Copia de seguridad y operaciones / Backup and Operations

数据库默认在宿主机：

```text
./data/arca_vida.db
```

备份示例：

```bash
mkdir -p backups
cp data/arca_vida.db "backups/arca_vida-$(date +%Y%m%d-%H%M%S).db"
```

运维命令：

```bash
docker compose logs -f --tail=100 arcavida
git pull
docker compose up -d --build
```

不要在生产服务器执行会删除 `data/`、`backups/` 或地理编码缓存的清理命令。

## 联调检查 / Integration Checks

```bash
docker compose exec arcavida python scripts/integration-smoke.py translate llm
```

如果模型服务或地图服务暂不可用，Web 工作台仍应能保存记录并进入人工复核流程。外部服务失败不应阻断已有记录查看、备注和状态更新。
