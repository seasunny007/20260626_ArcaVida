# 精准定位：物资发放追踪系统

> **版本**：0.1.0
> **更新日期**：2026-06-28
> **定位**：ArcaVida 后续功能方向，用于安置点/发放点的物资需求、库存和送达记录追踪。
> **边界**：系统只提供信息整理、地图展示和分配参考；实际派送、路线选择、优先级确认和现场行动必须由人工协调员决定。

核心痛点：**水、食物、卫生用品，到底送到哪里了？哪里还缺？**

## 一、核心价值定位

| 问题                           | 解决方案                                            |
| ------------------------------ | --------------------------------------------------- |
| 物资送到安置点，但协调员不知道 | 地图显示各安置点物资状态和最近更新时间              |
| 某安置点缺水，但信息传不出去   | 安置点负责人或志愿者通过 Web 表单/可选 Bot 上报需求 |
| 捐赠物资不知道往哪送           | 系统按缺货指数列出候选安置点，供协调员确认          |
| 重复派送浪费运力               | 记录已送达量和当前库存，辅助人工分配                |

## 二、系统设计（极简版）

### 2.1 核心数据模型

只新增三张主表，其他能力复用现有 Web、SQLite、地理编码、地图和简报框架。

```python
class DistributionPoint:
    id: str
    name: str
    lat: float | None
    lng: float | None
    contact_person: str | None
    contact_channel: str | None
    population_served: int | None
    status: str  # ACTIVE | FULL | CLOSED
    created_at: datetime
    updated_at: datetime
```

说明：`contact_person` 和 `contact_channel` 属于敏感协作信息。公开演示、Issue、PR、截图和导出样例不得包含真实联系人。

```python
class MaterialNeed:
    id: str
    point_id: str
    material_type: str  # WATER | FOOD | HYGIENE_KIT | MEDICINE | TENT | OTHER
    quantity: int
    current_stock: int
    unit: str  # boxes | packs | liters | kg | people_servings | units
    urgency: str  # CRITICAL | HIGH | MEDIUM | LOW
    reported_by: str | None
    reported_channel: str | None
    updated_at: datetime
```

```python
class DeliveryRecord:
    id: str
    point_id: str
    material_type: str
    quantity: int
    unit: str
    delivered_at: datetime
    delivered_by: str | None
    notes: str | None
    created_at: datetime
```

### 2.2 核心业务流程

```text
1. 安置点负责人/志愿者 -> 上报需求（Web 表单优先，可选 Bot）
   示例：某社区中心缺水 200 箱，食物 100 份

2. 系统 -> 解析、地理编码、入库
   输出结构化需求，并关联安置点坐标或待人工确认地址

3. 系统 -> 计算缺货指数
   参考：(需求量 - 当前库存) / 服务人数，并结合物资类型和紧急度

4. 地图 -> 可视化显示
   红色 = 严重缺货，黄色 = 需要关注，绿色 = 充足或近期已送达

5. 志愿者/协调员 -> 查看地图与排序结果
   按物资类型筛选，人工确认派送优先级

6. 送达后 -> 录入送达记录 -> 更新库存
   库存变化会影响缺货指数和地图颜色
```

### 2.3 关键算法：缺货指数

```python
def calculate_shortage_index(need: MaterialNeed, point: DistributionPoint) -> float:
    """
    缺货指数：0-100，越高越需要协调员关注。
    该值只作为排序和地图提示，不作为自动派送指令。
    """
    daily_per_person = {
        "WATER": 2.0,
        "FOOD": 0.5,
        "HYGIENE_KIT": 0.05,
        "MEDICINE": 0.02,
        "TENT": 0.01,
    }

    served = max(point.population_served or 0, 0)
    daily_need = served * daily_per_person.get(need.material_type, 0.1)
    if daily_need <= 0:
        base = 50.0
    else:
        days_remaining = max(need.current_stock, 0) / daily_need
        base = max(0.0, 100.0 - (days_remaining / 3.0 * 100.0))

    urgency_factor = {
        "CRITICAL": 1.2,
        "HIGH": 1.1,
        "MEDIUM": 1.0,
        "LOW": 0.8,
    }.get(need.urgency, 1.0)

    return min(100.0, max(0.0, base * urgency_factor))
```

### 2.4 新增交互命令（可选 Bot）

Web 表单是默认入口；Bot 命令只作为可选适配器，适合已有受控群组或志愿者工作流。

```text
/need 安置点名称 物资 数量
  例：/need 某社区中心 水 200箱
  例：/need 临时安置点 食物 50份

/deliver 安置点名称 物资 数量
  例：/deliver 某社区中心 水 50箱
  -> 记录送达，更新库存，保留审计记录

/status 安置点名称
  例：/status 某社区中心
  -> 返回水、食物、卫生用品等当前库存与缺口

/shortage [物资类型]
  例：/shortage 水
  -> 返回缺货指数最高的安置点列表，供人工确认
```

### 2.5 Web 地图升级

在地图看板中增加：

1. 物资图层切换：水、食物、卫生用品、药品、帐篷、全部。
2. 安置点标记颜色：
   - 绿色：库存相对充足，缺货指数 < 20。
   - 黄色：需要关注，缺货指数 20-60。
   - 红色：紧急，缺货指数 > 60。
3. 点击标记弹出详情：
   - 安置点名称、服务人数估算。
   - 各类物资库存、需求量、单位。
   - 最近送达时间。
   - 负责人联系方式仅在授权角色下显示。
4. 汇总统计：
   - 今日送达总量。
   - 当前紧急需求数量。
   - 物资缺口排名。

## 三、开发计划

| 天数  | 任务                             | 产出                                                           |
| ----- | -------------------------------- | -------------------------------------------------------------- |
| Day 1 | 新增数据模型，扩展数据库         | `distribution_points`、`material_needs`、`delivery_records` 表 |
| Day 2 | 实现需求上报、库存更新和缺货指数 | `core/material_manager.py`、`core/shortage_index.py`           |
| Day 3 | 实现 Web 表单和可选 Bot 命令     | `/need`、`/deliver`、`/status`、`/shortage`，以及 Web API      |
| Day 4 | 地图图层升级和测试               | 物资图层、颜色区分、详情弹窗、排序统计                         |

## 四、使用场景（合成示例）

### 场景 1：安置点负责人上报需求

```text
用户 -> Web/Bot：/need 某社区中心 水 200箱
系统 -> 用户：已记录。某社区中心缺水 200 箱，当前库存 50 箱，缺货指数 82%。请协调员复核后安排配送。
```

### 场景 2：志愿者查看整体情况

```text
用户 -> Web/Bot：/shortage 水
系统 -> 用户：最紧缺水的 5 个安置点：
1. 某社区中心 缺 200 箱，缺货指数 82%
2. 某临时安置点 缺 150 箱，缺货指数 71%
3. 某学校安置点 缺 80 箱，缺货指数 65%
```

### 场景 3：物资送达后更新

```text
用户 -> Web/Bot：/deliver 某社区中心 水 100箱
系统 -> 用户：已记录。某社区中心水库存从 50 箱更新为 150 箱。当前缺口 50 箱，缺货指数从 82% 降至 25%。
```

## 五、为什么选这个方向？

| 理由               | 说明                                                               |
| ------------------ | ------------------------------------------------------------------ |
| **最快落地**       | 复用现有 Web 工作台、SQLite、地图和导出框架，先做受控内测          |
| **志愿者立即能用** | Web 表单和可选 Bot 命令都足够简单                                  |
| **可见成果**       | 地图颜色和缺货指数变化直观，方便协调员复核                         |
| **可扩展**         | 后续可接入仓库、车队、批量导入和导出流程                           |
| **风险可控**       | 不处理受灾者个人身份细节，但仍需保护联系人、库存、路线和安置点信息 |

## 六、风险与边界

- 不公开真实安置点负责人、联系电话、精确库存、路线或未核实需求。
- 不自动决定派送；系统排序只是参考，必须由人工协调员确认。
- 不把送达记录当作官方审计凭证；如需正式审计，应接入当地组织的签收和审批流程。
- 不在公开仓库、Issue、PR、聊天或演示截图中使用真实敏感数据。
- 对外发布前必须完成角色权限、导出脱敏、日志脱敏和备份策略评审。
