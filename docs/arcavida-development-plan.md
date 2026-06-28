# ArcaVida（轻舟）— VS Code 开发计划文档

> **版本**：2.0.0
> **更新日期**：2026-06-28
> **基于**：委内瑞拉地震信息处理实战经验提炼
> **文档用途**：VS Code 开发环境下的逐项实施指南
> **实施原则**：Web 工作台优先、Telegram 可选、国内化部署优先、外部服务 provider 可插拔、所有输出必须人工复核。

## 一、项目定位与核心价值（重申）

ArcaVida（轻舟）是一套开源的 AI 辅助灾情信息处理工具，核心价值在于把多语言、碎片化、非结构化的求助信息整理为可复核、可定位、可导出、可协同的救援线索。

| 维度         | 描述                                                                                          |
| ------------ | --------------------------------------------------------------------------------------------- |
| **定位**     | 轻量级、个人可部署、志愿者友好的信息分拣与复核工具                                            |
| **核心能力** | 多源数据导入/抓取 -> 地址转坐标 -> 地图可视化 -> 置信度标注 -> 简报生成；后续扩展物资发放追踪 |
| **效率基准** | 将批量地址整理与转坐标从多人小时级流程压缩为 AI 辅助的分钟级流程，最终结果仍需人工确认        |
| **部署成本** | 以低成本 VPS/本地服务器 + OpenAI 兼容模型服务为默认路径，API 费用按实际调用量控制             |
| **入口形态** | 本地 Web 工作台（现有默认）+ 可选 Telegram/飞书/企微适配器（后续扩展）                        |

## 二、基于实战报道的关键发现（需求验证）

| 报道验证的痛点                                           | 对应开发模块                                         | 优先级 |
| -------------------------------------------------------- | ---------------------------------------------------- | ------ |
| 民间寻人网站、公开表单和志愿者转发文本可能成为核心数据源 | `data_sources/website.py`、`data_sources/manual.py`  | P0     |
| 地址转坐标是最大效率瓶颈                                 | `core/geocoder.py`                                   | P0     |
| 地图交互 API 调用量可能巨大                              | 批量缓存 + 视口裁剪 + 聚合显示                       | P1     |
| AI 幻觉是最大风险                                        | `core/confidence.py` + 人工兜底流程                  | P1     |
| 小城镇、非标准地址、跨语言地名更容易解析不准             | 地址规范化 + provider 交叉验证 + 人口/区域提示       | P2     |
| 救援协调需要标准化导出                                   | `exports/geojson.py`、`exports/coordination.py`      | P2     |
| 国内协同工具是现实需要                                   | `bot/adapters/feishu.py`、`bot/adapters/wecom.py`    | P2     |
| 物资送达和缺口信息需要可视化追踪                         | `core/material_manager.py`、`core/shortage_index.py` | P2     |

合规边界：只处理公开、授权、志愿者主动转发或充分匿名化的数据；抓取器必须遵守目标网站条款、robots、限速和隐私要求，不绕过登录、付费墙、验证码或访问控制。

## 三、目录结构升级（Phase 0 必做）

```text
arca_vida/
├── bot/                              # 可选 Bot 适配器（已有 Telegram）
│   ├── __init__.py
│   ├── main.py
│   ├── handlers.py                   # 后续新增地图、导出、简报命令
│   ├── commands.py
│   └── adapters/                     # 新增：飞书/企微等适配器
│       ├── __init__.py
│       ├── feishu.py
│       └── wecom.py
│
├── core/                             # 核心 AI 与数据处理逻辑（已有，需扩展）
│   ├── translator.py
│   ├── extractor.py
│   ├── slang_matcher.py
│   ├── briefing.py
│   ├── geocoder.py                   # 新增：地址转坐标
│   ├── aggregator.py                 # 新增：聚合与去重
│   └── confidence.py                 # 新增：置信度评估
│
├── data_sources/                     # 新增：多源数据接入
│   ├── __init__.py
│   ├── base.py                       # 抽象基类
│   ├── website.py                    # 公开/授权网站抓取器
│   ├── manual.py                     # Web 工作台手动导入适配器
│   └── telegram.py                   # 可选 Telegram 数据适配器
│
├── web/                              # Web 工作台与地图看板（已有 app.py，需扩展）
│   ├── __init__.py
│   ├── app.py
│   ├── static/
│   │   ├── index.html
│   │   ├── map.js
│   │   └── style.css
│   └── templates/
│       └── map.html
│
├── exports/                          # 新增：多格式导出
│   ├── __init__.py
│   ├── json.py
│   ├── geojson.py
│   ├── coordination.py
│   └── pdf.py
│
├── models/                           # 数据模型（已有，需扩展）
│   ├── database.py
│   └── schemas.py
│
├── config/                           # 配置（已有，需扩展）
│   ├── settings.py
│   ├── slang.json
│   └── geocoder_cache.json           # 新增：本地地址缓存，默认不提交真实数据
│
├── tests/                            # 测试（已有，需扩展）
│   ├── test_translator.py
│   ├── test_extractor.py
│   ├── test_slang.py
│   ├── test_geocoder.py
│   └── test_aggregator.py
│
├── scripts/                          # 工具脚本（已有）
├── .env.example                      # 新增地图/地理编码配置
├── requirements.txt                  # 新增必要依赖，重型依赖保持可选
├── Dockerfile
├── docker-compose.yml
└── README.md                         # 新增地图看板与导出说明
```

## 四、新增核心模块设计

### 4.1 数据源抓取器（`data_sources/`）

#### 4.1.1 抽象基类（`base.py`）

```python
from abc import ABC, abstractmethod
from typing import Any


class DataSource(ABC):
    """所有数据源的抽象基类。"""

    @abstractmethod
    def fetch(self, since: str | None = None) -> list[dict[str, Any]]:
        """抓取或读取数据，返回原始字典列表。"""

    @abstractmethod
    def normalize(self, raw: dict[str, Any]) -> dict[str, Any]:
        """将原始数据格式化为 ArcaVida 标准字段。"""
```

#### 4.1.2 公开/授权网站抓取器（`website.py`）

目标：对公开、授权或已确认允许抓取的网站实现低频、可审计的数据读取。候选数据源以实际可访问、合规授权为准，不在代码中硬编码不可验证的网站假设。

实现步骤：

1. 手动分析目标页面或公开 API，确认字段、分页、更新时间和使用条款。
2. 优先使用公开 API、CSV、RSS 或手动导出文件；只有必要时才解析 HTML。
3. 使用 `httpx` 或 `requests` + `BeautifulSoup`；确需 JS 渲染时再评估 Playwright/Selenium。
4. 支持增量抓取，记录 `source_url`、`fetched_at`、`source_name`。
5. 映射为标准化字段：

```python
{
    "raw_address": "Av. Libertador, La Guaira",
    "name": "Juan Perez",
    "contact": "+58 412 1234567",
    "disappeared_at": "2026-06-26 14:30",
    "description": "Visto por ultima vez en la zona de Catia La Mar",
    "images": ["https://example.org/photo1.jpg"],
    "source": "website",
    "source_url": "https://example.org/post/123",
}
```

反爬与合规要求：

- 设置清晰、克制的 `User-Agent`，标明项目和联系方式。
- 使用限速与指数退避，不做并发轰炸。
- 遇到验证码、登录墙、封禁或条款禁止时停止抓取。
- 优先支持人工导入缓存，不绕过访问控制。

#### 4.1.3 数据聚合器（`core/aggregator.py`）

功能：

- 合并 Web 手动输入、公开网站、Telegram legacy、CSV/JSON 导入等多源数据。
- 按地址、时间、姓名、联系方式和文本相似度去重。
- 调用 `core/geocoder.py` 批量解析地址。
- 标记来源与置信度，保留人工复核所需证据。

基础去重策略：

```python
def deduplicate(records: list[dict]) -> list[dict]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict] = []
    for record in records:
        address_key = (record.get("raw_address") or "").strip().lower()[:40]
        date_key = (record.get("disappeared_at") or "")[:10]
        name_key = (record.get("name") or "").strip().lower()
        key = (address_key, date_key, name_key)
        if key not in seen:
            seen.add(key)
            unique.append(record)
    return unique
```

### 4.2 地理编码器（`core/geocoder.py`）

核心功能：将文字地址转化为经纬度，并返回置信度、provider、原始响应摘要和是否需要人工复核。

设计原则：

- provider-neutral：默认优先 OpenStreetMap/Nominatim 或国内可访问 provider；Google/Mapbox 仅为可选项。
- 缓存优先：相同地址绝不重复调用外部 API。
- 人工复核：低精度、模糊匹配、多结果冲突必须标记。
- 不提交真实缓存：`config/geocoder_cache.json` 只保留空模板或合成样例，真实缓存放入本地数据目录并加入忽略规则。

建议接口：

```python
from dataclasses import dataclass


@dataclass
class GeocodeResult:
    lat: float | None
    lng: float | None
    accuracy: str | None
    provider: str
    confidence: float
    requires_human_review: bool


class Geocoder:
    def geocode(self, address: str) -> GeocodeResult:
        """单条地址转坐标，优先读缓存。"""

    def batch_geocode(self, addresses: list[str]) -> list[GeocodeResult]:
        """批量地址转坐标，先命中缓存，再限速调用 provider。"""
```

环境变量：

```env
GEOCODER_PROVIDER=nominatim
GEOCODER_API_KEY=
GEOCODER_BASE_URL=https://nominatim.openstreetmap.org
GEOCODER_CACHE_PATH=./data/geocoder_cache.json
MAP_TILE_LAYER=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

备选 provider：

| Provider    | 用途             | 备注                     |
| ----------- | ---------------- | ------------------------ |
| `nominatim` | 默认免费地理编码 | 限速严格，适合低频与缓存 |
| `amap`      | 国内部署可选     | 需自行配置高德 Key       |
| `mapbox`    | 海外部署可选     | 需自行配置 Key           |
| `google`    | 可选             | 不作为默认依赖           |

### 4.3 Web 地图看板（`web/`）

后端新增端点：

```python
@app.get("/api/map-data")
async def get_map_data(bounds: str | None = None, limit: int = 10000):
    """返回 GeoJSON，支持视口裁剪与数量限制。"""
```

GeoJSON 输出字段：

```json
{
  "type": "Feature",
  "geometry": { "type": "Point", "coordinates": [-66.932, 10.602] },
  "properties": {
    "id": "record-id",
    "address": "Av. Libertador, La Guaira",
    "priority": 3,
    "status": "pending",
    "confidence_score": 0.72,
    "requires_human_review": true
  }
}
```

前端技术选型：Leaflet + MarkerCluster。功能包括：

1. 加载 `/api/map-data` 数据点。
2. 按优先级、状态、置信度筛选。
3. 点击标记展示地址、时间、来源、状态、置信度。
4. 密集点聚合显示。
5. 地图移动后按 bbox 重新加载，避免一次性拉取过多数据。

### 4.4 置信度评估（`core/confidence.py`）

```python
def calculate_confidence(
    address: str,
    geocode_accuracy: str | None,
    has_image: bool,
    has_contact: bool,
    source: str,
    area_type: str | None = None,
) -> dict:
    score = 0.5
    if address and len(address) > 10:
        score += 0.15
    if geocode_accuracy in {"rooftop", "street", "exact"}:
        score += 0.15
    elif geocode_accuracy in {"approximate", "city"}:
        score -= 0.1
    if has_image:
        score += 0.1
    if has_contact:
        score += 0.1
    if source == "website_verified":
        score += 0.1
    if area_type in {"rural", "remote"}:
        score -= 0.1

    score = min(max(score, 0.0), 1.0)
    return {
        "score": score,
        "requires_human_review": score < 0.7,
    }
```

## 五、数据模型升级（`models/schemas.py` / `models/database.py`）

新增字段建议：

```python
raw_address: str | None
lat: float | None
lng: float | None
geocode_accuracy: str | None
geocode_provider: str | None

name: str | None
contact: str | None
disappeared_at: datetime | None
image_urls: list[str]
source: str
source_url: str | None

confidence_score: float
requires_human_review: bool

area_type: str | None
```

数据库迁移策略：MVP 仍使用 SQLite。先以向后兼容方式新增 nullable 字段；后续如引入迁移工具，再补 Alembic 或轻量 migration 脚本。

## 六、新增依赖（`requirements.txt` 升级）

基础依赖建议保持轻量：

```txt
httpx>=0.27,<1
beautifulsoup4>=4.12,<5
lxml>=5,<6
geopy>=2.4,<3
```

可选依赖保持独立 extras 或单独 requirements 文件：

```txt
pandas>=2.2,<3       # 批量清洗/分析，可选
shapely>=2,<3        # 几何计算，可选
playwright>=1.45,<2  # JS 渲染页面抓取，可选且需人工确认合规
```

不把 `leaflet` 放入 pip；前端通过本地静态文件或可信 CDN 加载。

## 七、环境变量升级（`.env.example`）

```env
GEOCODER_PROVIDER=nominatim
GEOCODER_API_KEY=
GEOCODER_BASE_URL=https://nominatim.openstreetmap.org
GEOCODER_CACHE_PATH=./data/geocoder_cache.json
MAP_TILE_LAYER=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
WEBSITE_TARGET_URL=
WEB_PORT=8080
```

现有 AI 配置保持：

```env
TRANSLATION_PROVIDER=llm
OPENAI_API_KEY=your_openai_compatible_key_here
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```

## 八、分阶段开发计划（VS Code 执行清单）

### Phase 0：基础设施与依赖（Day 1）

| 任务             | 文件/操作                                            | 验证标准                       |
| ---------------- | ---------------------------------------------------- | ------------------------------ |
| 创建新增目录结构 | `data_sources/`, `exports/`, `bot/adapters/`         | 目录存在，含 `__init__.py`     |
| 新增地理编码配置 | `.env.example`, `config/settings.py`                 | settings 可读取新增变量        |
| 新增空缓存模板   | `config/geocoder_cache.json`                         | 只含 `{}`，真实缓存走 `./data` |
| 新增占位测试     | `tests/test_geocoder.py`, `tests/test_aggregator.py` | `pytest` 通过                  |
| 更新文档         | README 与本计划                                      | 新用户能理解地图升级目标       |

### Phase 1：地理编码模块（Day 2-3）

| 任务               | 文件/操作                              | 验证标准                     |
| ------------------ | -------------------------------------- | ---------------------------- |
| 实现 `Geocoder` 类 | `core/geocoder.py`                     | 单地址解析返回结构化结果     |
| 实现缓存读写       | `GEOCODER_CACHE_PATH`                  | 缓存命中不调用 API           |
| 实现批量解析       | `batch_geocode()`                      | 100 条合成/缓存地址快速返回  |
| provider 抽象      | `nominatim` 默认，其他 provider 可插拔 | 无 Key 时不崩溃              |
| 单元测试           | `tests/test_geocoder.py`               | 覆盖缓存、fallback、低置信度 |

合成测试地址：

```text
Av. Libertador, La Guaira, Venezuela
Catia La Mar, La Guaira, Venezuela
Centro de Valencia, Carabobo, Venezuela
```

真实 API 联调只在本地手动执行，不进入默认测试。

### Phase 2：数据源接入（Day 4-5）

| 任务                   | 文件/操作                 | 验证标准                            |
| ---------------------- | ------------------------- | ----------------------------------- |
| 实现 `DataSource` 基类 | `data_sources/base.py`    | 抽象方法定义完整                    |
| 实现手动导入适配器     | `data_sources/manual.py`  | 可规范化 Web 输入/CSV 行            |
| 实现公开网站适配器     | `data_sources/website.py` | 用 fixture 测试解析，不默认访问外网 |
| 实现聚合去重           | `core/aggregator.py`      | 多源合并 + 去重通过                 |
| 集成地理编码           | 聚合后填充坐标            | 低置信度标记人工复核                |

### Phase 3：Web 地图看板（Day 6-7）

| 任务         | 文件/操作                                      | 验证标准           |
| ------------ | ---------------------------------------------- | ------------------ |
| 实现地图 API | `web.app` `/api/map-data`                      | 返回 GeoJSON       |
| 实现地图页面 | `web/static/index.html`, `map.js`, `style.css` | 页面可访问         |
| 添加聚合显示 | Leaflet MarkerCluster                          | 密集区域自动聚合   |
| 添加视口裁剪 | bbox 参数                                      | 拖动地图不全量刷新 |
| 添加筛选控件 | 优先级/状态/置信度                             | 筛选后点位正确     |

### Phase 4：置信度与人工兜底（Day 8）

| 任务             | 文件/操作            | 验证标准              |
| ---------------- | -------------------- | --------------------- |
| 实现置信度评估   | `core/confidence.py` | 返回 0-1 分数         |
| 集成处理流程     | 聚合/入库前计算      | 低于 0.7 标记人工复核 |
| Dashboard 标注   | 地图点颜色/边框      | 低置信度显著提示      |
| 幻觉风险样例测试 | 不完整/冲突地址      | 正确降置信度          |

### Phase 5：多格式导出（Day 9）

| 任务             | 文件/操作                     | 验证标准                 |
| ---------------- | ----------------------------- | ------------------------ |
| JSON 导出        | `exports/json.py`             | 标准 JSON                |
| GeoJSON 导出     | `exports/geojson.py`          | 可导入 GIS/地图工具      |
| 协调格式导出     | `exports/coordination.py`     | 字段映射清晰，标注非官方 |
| PDF/HTML 简报    | `exports/pdf.py` 或 HTML 打印 | 含统计与人工复核提示     |
| Web 集成导出按钮 | `web/app.py`                  | 一键下载指定格式         |

### Phase 6：协同集成与部署（Day 10）

| 任务            | 文件/操作                            | 验证标准             |
| --------------- | ------------------------------------ | -------------------- |
| 飞书/企微适配器 | `bot/adapters/feishu.py`, `wecom.py` | 简报可发送至测试群   |
| 每日简报任务    | 轻量调度脚本或 cron                  | 可生成每日工作简报   |
| 性能优化        | 地图加载、缓存、分页                 | 拖动不卡顿           |
| 国内化部署      | Docker Compose + Nginx/Caddy         | `/health` 与首页正常 |
| README 升级     | 地图看板、导出、部署说明             | 新用户可独立上手     |

## 九、验收标准

### 功能验收

- [ ] 能导入或抓取公开/授权数据并解析字段。
- [ ] 地址转坐标支持缓存、限速和 provider fallback。
- [ ] 地图看板显示数据点，聚合与筛选功能正常。
- [ ] 置信度标注完整，低置信度自动标记人工核实。
- [ ] 导出支持 JSON、GeoJSON、非官方协调格式。
- [ ] 飞书/企微适配器可在测试群发送简报。

### 性能验收

- [ ] 地图拖动时使用视口裁剪，避免全量刷新。
- [ ] 数据点聚合显示，密集区不卡顿。
- [ ] 批量地理编码二次运行缓存命中率 > 80%。

### 测试验收

- [ ] `pytest` 全部通过。
- [ ] 地理编码、聚合、导出核心逻辑覆盖率 > 70%。
- [ ] 默认测试不调用真实外部 API。
- [ ] 真实 API 联调通过本地 smoke script 单独执行。

## 十、风险与应对

| 风险                               | 影响 | 应对措施                                                 |
| ---------------------------------- | ---- | -------------------------------------------------------- |
| 目标网站反爬、改版或禁止抓取       | 高   | 优先公开 API/手动导入；抓取器 fixture 化；不绕过访问控制 |
| 地理编码 provider 超配额或不可访问 | 中   | 缓存、限速、多 provider、人工导入坐标                    |
| 地图加载性能差                     | 中   | 视口裁剪、聚合显示、分页、本地缓存                       |
| 地址格式不规范                     | 中   | 地址预处理、低置信度提示、人工复核                       |
| AI 幻觉                            | 高   | 置信度、证据链、人工确认、不得自动派遣                   |
| 协同平台 API 变更                  | 低   | 适配器隔离，核心流程不依赖单一平台                       |

## 十一、Git 提交规范

```bash
<type>(<scope>): <subject>
```

示例：

```bash
feat(geocoder): add cached batch geocoding
feat(web): add Leaflet map dashboard
fix(data_sources): handle missing website fields
test(geocoder): cover cache hit behavior
docs(readme): document map dashboard usage
```

Type 列表：

```text
feat     新功能
fix      修复 Bug
docs     文档更新
test     测试相关
refactor 重构
perf     性能优化
chore    构建/工具配置
```

## 十二、VS Code 调试配置

建议新增 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Web Workstation",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["web.app:app", "--reload", "--port", "8080"],
      "envFile": "${workspaceFolder}/.env",
      "console": "integratedTerminal"
    },
    {
      "name": "Bot (Optional Polling)",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/bot/main.py",
      "envFile": "${workspaceFolder}/.env",
      "console": "integratedTerminal",
      "justMyCode": true
    },
    {
      "name": "Pytest (Current File)",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["${file}", "-v", "--tb=short"],
      "console": "integratedTerminal"
    }
  ]
}
```

## 十三、文档更新清单

| 文档/文件               | 更新内容                                                                      |
| ----------------------- | ----------------------------------------------------------------------------- |
| `README.md`             | 新增地图看板、地理编码、导出功能说明                                          |
| `.env.example`          | 新增 `GEOCODER_PROVIDER`、`GEOCODER_CACHE_PATH`、`MAP_TILE_LAYER`、`WEB_PORT` |
| `requirements.txt`      | 新增轻量抓取与地理编码依赖，可选依赖拆分                                      |
| `config/settings.py`    | 新增地图与地理编码配置读取                                                    |
| `docs/deployment-cn.md` | 补充地图瓦片、反代、数据备份注意事项                                          |
| 本开发计划              | 按 Phase 标记完成状态                                                         |

## 十四、总结

本计划的核心是：**将实战中验证的信息处理瓶颈，转化为可执行、可测试、可部署的工程任务**。

| 实战验证的需求            | 对应开发模块                                        | Phase   |
| ------------------------- | --------------------------------------------------- | ------- |
| 公开/授权数据源是核心输入 | `data_sources/website.py`, `data_sources/manual.py` | Phase 2 |
| 地址转坐标是效率瓶颈      | `core/geocoder.py`                                  | Phase 1 |
| 地图交互需要性能控制      | Web 地图聚合 + 视口裁剪                             | Phase 3 |
| AI 幻觉是最大风险         | `core/confidence.py`                                | Phase 4 |
| 标准化导出需要            | `exports/geojson.py`, `exports/coordination.py`     | Phase 5 |
| 国内协同需要              | `bot/adapters/feishu.py`, `bot/adapters/wecom.py`   | Phase 6 |

预计完成时间：10 天，每天约 3-4 小时完成当日任务。实际发布节奏以安全、隐私、测试和人工复核流程成熟度为准。

准备工作：

1. 确认可用的地理编码 provider 与 API Key，优先选择国内可访问或稳定可访问服务。
2. 确认目标数据源可公开、授权或人工导入，避免任何绕过访问控制的抓取。
3. 确认飞书/企微机器人创建权限（如需）。
4. 准备合成或充分匿名化样例，默认测试不使用真实敏感数据。
