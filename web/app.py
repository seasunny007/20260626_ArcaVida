from contextlib import asynccontextmanager
from html import escape
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

from bot.commands import command_help
from config.settings import get_settings
from core.briefing import generate_briefing
from core.extractor import extract_info
from core.material_manager import (
    audit_summary,
    material_dashboard,
    material_map_markers,
    record_delivery,
    report_need,
    sanitized_export,
)
from core.translator import translate_text
from models.database import (
    add_note,
    create_distribution_point,
    create_record,
    init_db,
    list_records,
    update_status,
)
from models.schemas import (
    DeliveryRecordCreate,
    DistributionPointCreate,
    MaterialNeedCreate,
    RecordStatus,
    RescueRecord,
    RescueRecordCreate,
    priority_to_int,
)

SESSION_COOKIE = "arcavida_session"
SESSION_VALUE = "local-admin"


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    del app_instance
    get_settings().validate_runtime_security()
    init_db()
    yield


app = FastAPI(title="ArcaVida Web Workstation", version="0.2.0", lifespan=lifespan)


class LoginPayload(BaseModel):
    password: str = ""


class IntakePayload(BaseModel):
    raw_text: str
    source_label: str = "web-local"


class StatusPayload(BaseModel):
    status: RecordStatus


class NotePayload(BaseModel):
    note: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    settings = get_settings()
    if requires_login(request):
        return HTMLResponse(login_html())
    return HTMLResponse(workstation_html(auth_enabled=bool(settings.admin_password)))


@app.post("/api/login")
async def login(payload: LoginPayload) -> Response:
    settings = get_settings()
    if not settings.admin_password:
        return JSONResponse({"ok": True, "mode": "development"})
    if payload.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid password")
    response = JSONResponse({"ok": True})
    response.set_cookie(SESSION_COOKIE, SESSION_VALUE, httponly=True, samesite="strict")
    return response


@app.post("/api/logout")
def logout() -> Response:
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.get("/api/records")
def records(request: Request) -> list[dict[str, Any]]:
    ensure_authorized(request)
    return [record_to_json(record) for record in list_records()]


@app.get("/api/status")
def status_summary(request: Request) -> dict[str, int]:
    ensure_authorized(request)
    records = list_records()
    return {
        "total": len(records),
        "pending": sum(1 for record in records if record.status == RecordStatus.pending),
        "verified": sum(1 for record in records if record.status == RecordStatus.verified),
        "dispatched": sum(1 for record in records if record.status == RecordStatus.dispatched),
        "closed": sum(1 for record in records if record.status == RecordStatus.closed),
    }


@app.get("/api/help")
def help_text(request: Request) -> dict[str, str]:
    ensure_authorized(request)
    return {"help": command_help()}


@app.get("/api/material/dashboard")
def material_dashboard_api(request: Request) -> dict[str, Any]:
    ensure_authorized(request)
    return material_dashboard()


@app.get("/api/material/map")
def material_map_api(request: Request) -> list[dict[str, Any]]:
    ensure_authorized(request)
    return material_map_markers()


@app.post("/api/material/points")
def create_material_point(payload: DistributionPointCreate, request: Request) -> dict[str, str]:
    ensure_authorized(request)
    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="name is required")
    return {"id": create_distribution_point(payload)}


@app.post("/api/material/needs")
def create_material_need(payload: MaterialNeedCreate, request: Request) -> dict[str, str]:
    ensure_authorized(request)
    try:
        return {"id": report_need(payload)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/material/deliveries")
def create_material_delivery(payload: DeliveryRecordCreate, request: Request) -> dict[str, str]:
    ensure_authorized(request)
    try:
        return {"id": record_delivery(payload)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/export/sanitized")
def export_sanitized(request: Request) -> dict[str, Any]:
    ensure_authorized(request)
    return sanitized_export()


@app.get("/api/audit")
def audit_events(request: Request) -> list[dict[str, Any]]:
    ensure_authorized(request)
    return audit_summary()


@app.post("/api/records")
async def intake(payload: IntakePayload, request: Request) -> dict[str, str]:
    ensure_authorized(request)
    raw_text = payload.raw_text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="raw_text is required")

    translated = await translate_text(raw_text)
    extracted = await extract_info(translated.translated_text)
    record_id = create_record(
        RescueRecordCreate(
            raw_text=raw_text,
            detected_lang=translated.detected_lang,
            translated_text=translated.translated_text,
            location=extracted.location,
            needs=extracted.needs,
            trapped=extracted.trapped,
            priority=priority_to_int(extracted.priority),
            slang_alert=extracted.slang_alert,
            slang_hint=extracted.slang_meaning,
            source_chat_id=payload.source_label,
        )
    )
    return {"id": record_id}


@app.patch("/api/records/{record_id}/status")
def change_status(record_id: str, payload: StatusPayload, request: Request) -> dict[str, bool]:
    ensure_authorized(request)
    ok = update_status(record_id, payload.status)
    if not ok:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"ok": True}


@app.patch("/api/records/{record_id}/note")
def change_note(record_id: str, payload: NotePayload, request: Request) -> dict[str, bool]:
    ensure_authorized(request)
    ok = add_note(record_id, payload.note)
    if not ok:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"ok": True}


@app.get("/api/briefing")
def briefing(request: Request) -> dict[str, str]:
    ensure_authorized(request)
    pending = [record for record in list_records() if record.status != RecordStatus.closed]
    return {"briefing": generate_briefing(pending)}


def requires_login(request: Request) -> bool:
    settings = get_settings()
    if not settings.admin_password:
        return False
    return request.cookies.get(SESSION_COOKIE) != SESSION_VALUE


def ensure_authorized(request: Request) -> None:
    if requires_login(request):
        raise HTTPException(status_code=401, detail="Login required")


def record_to_json(record: RescueRecord) -> dict[str, Any]:
    data = record.model_dump(mode="json")
    data["status"] = str(record.status)
    data["priority_label"] = {3: "高", 2: "中", 1: "低"}.get(record.priority, "低")
    return data


def login_html() -> str:
    return """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ArcaVida 登录</title>
  <style>
    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f6f7f8; color: #182026; }
    main { max-width: 360px; margin: 14vh auto; padding: 24px; }
    h1 { font-size: 24px; margin: 0 0 20px; }
    label { display: block; font-size: 13px; margin-bottom: 8px; }
    input, button { width: 100%; box-sizing: border-box; font-size: 15px; }
    input { padding: 10px 12px; border: 1px solid #b9c0c7; border-radius: 6px; background: white; }
    button { margin-top: 12px; padding: 10px 12px; border: 0; border-radius: 6px; background: #155e75; color: white; cursor: pointer; }
    #error { color: #b42318; min-height: 20px; font-size: 13px; }
  </style>
</head>
<body>
  <main>
    <h1>ArcaVida</h1>
    <form id="login-form">
      <label for="password">管理员密码</label>
      <input id="password" type="password" autocomplete="current-password" autofocus>
      <button type="submit">登录</button>
      <p id="error"></p>
    </form>
  </main>
  <script>
    document.querySelector('#login-form').addEventListener('submit', async (event) => {
      event.preventDefault();
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({password: document.querySelector('#password').value})
      });
      if (response.ok) window.location.href = '/';
      else document.querySelector('#error').textContent = '密码不正确';
    });
  </script>
</body>
</html>
"""


def workstation_html(auth_enabled: bool) -> str:
    logout = (
        "<form method='post' action='/api/logout'><button type='submit'>退出</button></form>"
        if auth_enabled
        else ""
    )
    return f"""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ArcaVida 工作台</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f6f7f8; color: #182026; }}
    header {{ display: flex; justify-content: space-between; align-items: center; padding: 14px 20px; border-bottom: 1px solid #d7dce0; background: #fff; }}
    h1 {{ font-size: 20px; margin: 0; }}
    main {{ display: grid; grid-template-columns: minmax(280px, 420px) 1fr; gap: 18px; padding: 18px; }}
    section {{ background: #fff; border: 1px solid #d7dce0; border-radius: 8px; padding: 14px; }}
    h2 {{ font-size: 15px; margin: 0 0 12px; }}
    a {{ color: #155e75; text-decoration: none; }}
    textarea, input, select {{ width: 100%; box-sizing: border-box; border: 1px solid #b9c0c7; border-radius: 6px; padding: 9px 10px; font: inherit; }}
    textarea {{ min-height: 180px; resize: vertical; }}
    button {{ border: 0; border-radius: 6px; background: #155e75; color: white; padding: 8px 10px; cursor: pointer; }}
    button.secondary {{ background: #4b5563; }}
    .entry-grid {{ display: grid; grid-template-columns: repeat(9, minmax(120px, 1fr)); gap: 8px; }}
    .entry {{ border: 1px solid #d7dce0; border-radius: 8px; padding: 10px; background: #f9fafb; }}
    .entry strong {{ display: block; color: #182026; font-size: 14px; margin-bottom: 4px; }}
    .entry span {{ color: #5b6470; font-size: 12px; }}
    .toolbar {{ display: flex; gap: 8px; align-items: center; margin-top: 10px; }}
    .stats {{ display: grid; grid-template-columns: repeat(5, minmax(88px, 1fr)); gap: 8px; }}
    .stat {{ border: 1px solid #d7dce0; border-radius: 8px; padding: 10px; background: #f9fafb; }}
    .stat strong {{ display: block; font-size: 22px; }}
    .stat span {{ color: #5b6470; font-size: 12px; }}
    .records {{ display: grid; gap: 10px; }}
    .record {{ border: 1px solid #d7dce0; border-radius: 8px; padding: 10px; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 8px; font-size: 12px; color: #5b6470; margin-bottom: 8px; }}
    .briefing {{ white-space: pre-wrap; background: #eef4f5; border-radius: 6px; padding: 10px; min-height: 96px; }}
    .help {{ white-space: pre-wrap; background: #f3f6f6; border-radius: 6px; padding: 10px; min-height: 80px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }}
    .wide-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }}
    .material-list {{ display: grid; gap: 8px; margin-top: 10px; }}
    .map {{ position: relative; min-height: 260px; border: 1px solid #d7dce0; border-radius: 8px; background: linear-gradient(90deg, #eef4f5 1px, transparent 1px), linear-gradient(#eef4f5 1px, transparent 1px); background-size: 40px 40px; overflow: hidden; }}
    .marker {{ position: absolute; transform: translate(-50%, -50%); min-width: 120px; border: 1px solid #182026; border-radius: 8px; padding: 8px; background: #fff; box-shadow: 0 4px 14px rgba(24, 32, 38, 0.12); font-size: 12px; }}
    .marker::before {{ content: ''; display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; background: var(--marker-color); }}
    .marker.red {{ --marker-color: #b42318; }}
    .marker.yellow {{ --marker-color: #b7791f; }}
    .marker.green {{ --marker-color: #16794c; }}
    .export-box, .audit-log {{ white-space: pre-wrap; background: #f3f6f6; border-radius: 6px; padding: 10px; max-height: 260px; overflow: auto; }}
    @media (max-width: 980px) {{ .entry-grid, .stats, .wide-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 860px) {{ main {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header><h1>ArcaVida 工作台</h1>{logout}</header>
  <main>
    <section style="grid-column: 1 / -1;">
      <h2>功能入口</h2>
      <nav class="entry-grid" aria-label="功能入口">
        <a class="entry" href="#intake"><strong>新建求救</strong><span>翻译、提取、保存</span></a>
        <a class="entry" href="#status"><strong>状态统计</strong><span>待处理、已核实、已派单</span></a>
        <a class="entry" href="#briefing-section"><strong>简报</strong><span>生成待处理简报</span></a>
        <a class="entry" href="#records-section"><strong>记录队列</strong><span>改状态、写备注</span></a>
        <a class="entry" href="#materials-section"><strong>物资管理</strong><span>需求、库存、送达</span></a>
        <a class="entry" href="#map-section"><strong>地图看板</strong><span>缺货颜色图层</span></a>
        <a class="entry" href="#export-section"><strong>脱敏导出</strong><span>移除联系人和路线</span></a>
        <a class="entry" href="#audit-section"><strong>审计日志</strong><span>查看关键变更</span></a>
        <a class="entry" href="#help-section"><strong>命令说明</strong><span>查看 Bot/协作命令</span></a>
      </nav>
    </section>
    <section id="intake">
      <h2>新建求救记录</h2>
      <textarea id="raw" placeholder="粘贴西语或中文灾情文本"></textarea>
      <div class="grid">
        <input id="source" value="web-local" aria-label="来源标签">
      </div>
      <div class="toolbar">
        <button id="submit">处理并保存</button>
        <button class="secondary" id="refresh">刷新</button>
      </div>
    </section>
    <section id="status">
      <h2>状态统计</h2>
      <div class="stats" id="status-summary">加载中...</div>
    </section>
    <section id="briefing-section">
      <h2>简报</h2>
      <div class="briefing" id="briefing">加载中...</div>
    </section>
    <section id="records-section" style="grid-column: 1 / -1;">
      <h2>记录队列</h2>
      <div class="records" id="records"></div>
    </section>
    <section id="materials-section" style="grid-column: 1 / -1;">
      <h2>物资管理</h2>
      <div class="wide-grid">
        <form id="point-form">
          <h2>新增安置点/发放点</h2>
          <input id="point-name" placeholder="名称" required>
          <input id="point-lat" placeholder="纬度，可选" type="number" step="0.000001">
          <input id="point-lng" placeholder="经度，可选" type="number" step="0.000001">
          <input id="point-population" placeholder="服务人数估算" type="number" min="0">
          <input id="point-contact-person" placeholder="负责人，仅授权可见">
          <input id="point-contact-channel" placeholder="联系方式，仅授权可见">
          <button type="submit">保存点位</button>
        </form>
        <form id="need-form">
          <h2>上报物资需求</h2>
          <select id="need-point"></select>
          <select id="need-type">
            <option value="WATER">水</option><option value="FOOD">食物</option><option value="HYGIENE_KIT">卫生用品</option><option value="MEDICINE">药品</option><option value="TENT">帐篷</option><option value="OTHER">其他</option>
          </select>
          <input id="need-quantity" placeholder="需求量" type="number" min="0" required>
          <input id="need-stock" placeholder="当前库存" type="number" min="0" value="0">
          <input id="need-unit" placeholder="单位" value="units">
          <select id="need-urgency"><option value="CRITICAL">紧急</option><option value="HIGH">高</option><option value="MEDIUM" selected>中</option><option value="LOW">低</option></select>
          <button type="submit">保存需求</button>
        </form>
        <form id="delivery-form">
          <h2>记录物资送达</h2>
          <select id="delivery-point"></select>
          <select id="delivery-type">
            <option value="WATER">水</option><option value="FOOD">食物</option><option value="HYGIENE_KIT">卫生用品</option><option value="MEDICINE">药品</option><option value="TENT">帐篷</option><option value="OTHER">其他</option>
          </select>
          <input id="delivery-quantity" placeholder="送达量" type="number" min="0" required>
          <input id="delivery-unit" placeholder="单位" value="units">
          <input id="delivery-by" placeholder="送达人，仅审计用">
          <input id="delivery-notes" placeholder="备注/路线，导出会脱敏">
          <button type="submit">保存送达</button>
        </form>
      </div>
      <div class="stats" id="material-summary"></div>
      <div class="material-list" id="material-needs"></div>
    </section>
    <section id="map-section" style="grid-column: 1 / -1;">
      <h2>地图看板</h2>
      <div class="map" id="material-map"></div>
    </section>
    <section id="export-section" style="grid-column: 1 / -1;">
      <h2>脱敏导出</h2>
      <div class="toolbar">
        <button id="export-refresh" onclick="refreshExport()">生成脱敏导出</button>
        <a href="/api/export/sanitized" target="_blank" rel="noreferrer">打开 JSON 导出</a>
      </div>
      <div class="export-box" id="sanitized-export">尚未生成</div>
    </section>
    <section id="audit-section" style="grid-column: 1 / -1;">
      <h2>审计日志</h2>
      <div class="audit-log" id="audit-log">加载中...</div>
    </section>
    <section id="help-section" style="grid-column: 1 / -1;">
      <h2>命令说明</h2>
      <div class="help" id="help">加载中...</div>
    </section>
  </main>
  <script>
    const statusOptions = ['pending', 'verified', 'dispatched', 'closed'];
    async function api(path, options = {{}}) {{
      const response = await fetch(path, {{headers: {{'Content-Type': 'application/json'}}, ...options}});
      if (!response.ok) throw new Error(await response.text());
      return response.json();
    }}
    async function load() {{
      const [records, briefing, status, help, materials, markers, audit] = await Promise.all([api('/api/records'), api('/api/briefing'), api('/api/status'), api('/api/help'), api('/api/material/dashboard'), api('/api/material/map'), api('/api/audit')]);
      document.querySelector('#briefing').textContent = briefing.briefing;
      document.querySelector('#status-summary').innerHTML = renderStatus(status);
      document.querySelector('#help').textContent = help.help;
      document.querySelector('#records').innerHTML = records.map(renderRecord).join('') || '暂无记录';
      document.querySelector('#material-summary').innerHTML = renderMaterialSummary(materials.summary);
      document.querySelector('#material-needs').innerHTML = materials.needs.map(renderMaterialNeed).join('') || '暂无物资需求';
      document.querySelector('#material-map').innerHTML = renderMap(markers);
      document.querySelector('#audit-log').textContent = JSON.stringify(audit, null, 2);
      populatePointSelectors(materials.points);
    }}
    function renderStatus(status) {{
      return [
        ['总数', status.total],
        ['待处理', status.pending],
        ['已核实', status.verified],
        ['已派单', status.dispatched],
        ['已关闭', status.closed],
      ].map(([label, value]) => `<div class="stat"><strong>${{value}}</strong><span>${{label}}</span></div>`).join('');
    }}
    function renderRecord(record) {{
      const needs = (record.needs || []).join('、') || '待核实';
      const note = record.volunteer_notes || '';
      return `<article class="record">
        <div class="meta"><strong>${{record.priority_label}}</strong><span>${{escapeHtml(record.status)}}</span><span>${{escapeHtml(record.location || '待核实')}}</span><span>${{record.trapped ? '被困' : '未确认被困'}}</span></div>
        <p>${{escapeHtml(record.translated_text)}}</p>
        <p>需求：${{escapeHtml(needs)}}${{record.slang_alert ? ' | 暗语：' + escapeHtml(record.slang_hint || '') : ''}}</p>
        <div class="toolbar">
          <select data-id="${{record.id}}" class="status">${{statusOptions.map(status => `<option ${{status === record.status ? 'selected' : ''}}>${{status}}</option>`).join('')}}</select>
          <input data-id="${{record.id}}" class="note" value="${{escapeHtml(note)}}" placeholder="备注">
          <button data-id="${{record.id}}" class="save-note">保存备注</button>
        </div>
      </article>`;
    }}
    function renderMaterialSummary(summary) {{
      return [
        ['点位', summary.points], ['需求', summary.needs], ['送达', summary.deliveries], ['紧急缺口', summary.critical_needs], ['送达总量', summary.today_delivered],
      ].map(([label, value]) => `<div class="stat"><strong>${{value}}</strong><span>${{label}}</span></div>`).join('');
    }}
    function renderMaterialNeed(item) {{
      const need = item.need;
      return `<article class="record"><div class="meta"><strong>${{escapeHtml(item.point.name)}}</strong><span>${{escapeHtml(need.material_type)}}</span><span>${{escapeHtml(need.urgency)}}</span><span>缺货指数 ${{item.shortage_index}}</span><span>${{escapeHtml(item.color)}}</span></div><p>需求 ${{need.quantity}} ${{escapeHtml(need.unit)}}，当前库存 ${{need.current_stock}} ${{escapeHtml(need.unit)}}</p></article>`;
    }}
    function renderMap(markers) {{
      if (!markers.length) return '暂无点位';
      return markers.map((marker, index) => {{
        const left = marker.lng === null ? 15 + (index * 17 % 70) : Math.min(94, Math.max(6, ((Number(marker.lng) + 180) / 360) * 100));
        const top = marker.lat === null ? 20 + (index * 23 % 60) : Math.min(94, Math.max(6, ((90 - Number(marker.lat)) / 180) * 100));
        return `<div class="marker ${{marker.color}}" style="left:${{left}}%; top:${{top}}%;"><strong>${{escapeHtml(marker.name)}}</strong><br>缺货指数 ${{marker.shortage_index}}<br>服务人数 ${{marker.population_served ?? '待核实'}}</div>`;
      }}).join('');
    }}
    function populatePointSelectors(points) {{
      const options = points.map(point => `<option value="${{point.id}}">${{escapeHtml(point.name)}}</option>`).join('') || '<option value="">请先新增点位</option>';
      document.querySelector('#need-point').innerHTML = options;
      document.querySelector('#delivery-point').innerHTML = options;
    }}
    function numberValue(selector) {{
      const value = document.querySelector(selector).value;
      return value === '' ? null : Number(value);
    }}
    async function refreshExport() {{
      const exported = await api('/api/export/sanitized');
      document.querySelector('#sanitized-export').textContent = JSON.stringify(exported, null, 2);
    }}
    function escapeHtml(value) {{
      return String(value ?? '').replace(/[&<>"']/g, char => ({{'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'}}[char]));
    }}
    document.querySelector('#submit').addEventListener('click', async () => {{
      await api('/api/records', {{method: 'POST', body: JSON.stringify({{raw_text: document.querySelector('#raw').value, source_label: document.querySelector('#source').value}})}});
      document.querySelector('#raw').value = '';
      await load();
    }});
    document.querySelector('#refresh').addEventListener('click', load);
    document.querySelector('#point-form').addEventListener('submit', async (event) => {{
      event.preventDefault();
      await api('/api/material/points', {{method: 'POST', body: JSON.stringify({{name: document.querySelector('#point-name').value, lat: numberValue('#point-lat'), lng: numberValue('#point-lng'), population_served: numberValue('#point-population'), contact_person: document.querySelector('#point-contact-person').value || null, contact_channel: document.querySelector('#point-contact-channel').value || null}})}});
      event.target.reset();
      await load();
    }});
    document.querySelector('#need-form').addEventListener('submit', async (event) => {{
      event.preventDefault();
      await api('/api/material/needs', {{method: 'POST', body: JSON.stringify({{point_id: document.querySelector('#need-point').value, material_type: document.querySelector('#need-type').value, quantity: Number(document.querySelector('#need-quantity').value), current_stock: Number(document.querySelector('#need-stock').value || 0), unit: document.querySelector('#need-unit').value || 'units', urgency: document.querySelector('#need-urgency').value}})}});
      event.target.reset();
      document.querySelector('#need-stock').value = '0';
      document.querySelector('#need-unit').value = 'units';
      await load();
    }});
    document.querySelector('#delivery-form').addEventListener('submit', async (event) => {{
      event.preventDefault();
      await api('/api/material/deliveries', {{method: 'POST', body: JSON.stringify({{point_id: document.querySelector('#delivery-point').value, material_type: document.querySelector('#delivery-type').value, quantity: Number(document.querySelector('#delivery-quantity').value), unit: document.querySelector('#delivery-unit').value || 'units', delivered_by: document.querySelector('#delivery-by').value || null, notes: document.querySelector('#delivery-notes').value || null}})}});
      event.target.reset();
      document.querySelector('#delivery-unit').value = 'units';
      await load();
    }});
    document.addEventListener('change', async (event) => {{
      if (!event.target.classList.contains('status')) return;
      await api(`/api/records/${{event.target.dataset.id}}/status`, {{method: 'PATCH', body: JSON.stringify({{status: event.target.value}})}});
      await load();
    }});
    document.addEventListener('click', async (event) => {{
      if (event.target.id === 'export-refresh') {{
        await refreshExport();
        return;
      }}
      if (!event.target.classList.contains('save-note')) return;
      const note = document.querySelector(`.note[data-id="${{event.target.dataset.id}}"]`).value;
      await api(`/api/records/${{event.target.dataset.id}}/note`, {{method: 'PATCH', body: JSON.stringify({{note}})}});
      await load();
    }});
    load();
  </script>
</body>
</html>
"""
