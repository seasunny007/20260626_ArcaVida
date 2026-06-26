from contextlib import asynccontextmanager
from html import escape
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

from config.settings import get_settings
from core.briefing import generate_briefing
from core.extractor import extract_info
from core.translator import translate_text
from models.database import add_note, create_record, init_db, list_records, update_status
from models.schemas import RecordStatus, RescueRecord, RescueRecordCreate, priority_to_int

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
    textarea, input, select {{ width: 100%; box-sizing: border-box; border: 1px solid #b9c0c7; border-radius: 6px; padding: 9px 10px; font: inherit; }}
    textarea {{ min-height: 180px; resize: vertical; }}
    button {{ border: 0; border-radius: 6px; background: #155e75; color: white; padding: 8px 10px; cursor: pointer; }}
    button.secondary {{ background: #4b5563; }}
    .toolbar {{ display: flex; gap: 8px; align-items: center; margin-top: 10px; }}
    .records {{ display: grid; gap: 10px; }}
    .record {{ border: 1px solid #d7dce0; border-radius: 8px; padding: 10px; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 8px; font-size: 12px; color: #5b6470; margin-bottom: 8px; }}
    .briefing {{ white-space: pre-wrap; background: #eef4f5; border-radius: 6px; padding: 10px; min-height: 96px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }}
    @media (max-width: 860px) {{ main {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header><h1>ArcaVida 工作台</h1>{logout}</header>
  <main>
    <section>
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
    <section>
      <h2>简报</h2>
      <div class="briefing" id="briefing">加载中...</div>
    </section>
    <section style="grid-column: 1 / -1;">
      <h2>记录队列</h2>
      <div class="records" id="records"></div>
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
      const [records, briefing] = await Promise.all([api('/api/records'), api('/api/briefing')]);
      document.querySelector('#briefing').textContent = briefing.briefing;
      document.querySelector('#records').innerHTML = records.map(renderRecord).join('') || '暂无记录';
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
    function escapeHtml(value) {{
      return String(value ?? '').replace(/[&<>"']/g, char => ({{'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'}}[char]));
    }}
    document.querySelector('#submit').addEventListener('click', async () => {{
      await api('/api/records', {{method: 'POST', body: JSON.stringify({{raw_text: document.querySelector('#raw').value, source_label: document.querySelector('#source').value}})}});
      document.querySelector('#raw').value = '';
      await load();
    }});
    document.querySelector('#refresh').addEventListener('click', load);
    document.addEventListener('change', async (event) => {{
      if (!event.target.classList.contains('status')) return;
      await api(`/api/records/${{event.target.dataset.id}}/status`, {{method: 'PATCH', body: JSON.stringify({{status: event.target.value}})}});
      await load();
    }});
    document.addEventListener('click', async (event) => {{
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
