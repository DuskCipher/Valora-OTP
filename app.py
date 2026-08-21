# -*- coding: utf-8 -*-
"""
Flask Web Application Server for NEX-OTP
Provides REST APIs and Server-Sent Events (SSE) for real-time Web Dashboard streaming.
"""

import os
import sys
import time
import json
import queue
import threading
import platform as pf
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response, send_from_directory

from otp_engine import (
    normalize, fmtplus, get_ip, PLATFORMS, verdict
)

try:
    import psutil
except ImportError:
    psutil = None

app = Flask(__name__, template_folder='templates')

# Global Task State
state_lock = threading.Lock()
active_task = False
stop_requested = threading.Event()

current_job = {
    "status": "idle", # "idle", "running", "stopped", "completed"
    "phone": "",
    "phone_fmt": "",
    "mode": "single", # "single", "loop", "pick"
    "delay": 60,
    "selected_platforms": [], # 1-based indices
    "current_round": 0,
    "stats": {
        "total": 0,
        "success": 0,
        "limit": 0,
        "fail": 0
    },
    "logs": []
}

sse_subscribers = []

def broadcast_event(data):
    """Kirim JSON event ke semua koneksi SSE yang terhubung"""
    payload = f"data: {json.dumps(data)}\n\n"
    with state_lock:
        to_remove = []
        for q in sse_subscribers:
            try:
                q.put_nowait(payload)
            except Exception:
                to_remove.append(q)
        for q in to_remove:
            if q in sse_subscribers:
                sse_subscribers.remove(q)

def run_spam_worker(phone_62, mode, delay, chosen_indices):
    global active_task
    stop_requested.clear()
    
    with state_lock:
        active_task = True
        current_job["status"] = "running"
        current_job["phone"] = phone_62
        current_job["phone_fmt"] = fmtplus(phone_62)
        current_job["mode"] = mode
        current_job["delay"] = delay
        current_job["selected_platforms"] = chosen_indices
        current_job["current_round"] = 0
        current_job["stats"] = {"total": 0, "success": 0, "limit": 0, "fail": 0}
        current_job["logs"] = []

    broadcast_event({
        "type": "job_start",
        "job": {
            "phone_fmt": fmtplus(phone_62),
            "mode": mode,
            "delay": delay,
            "total_platforms": len(chosen_indices)
        }
    })

    round_no = 0

    try:
        while not stop_requested.is_set():
            round_no += 1
            with state_lock:
                current_job["current_round"] = round_no

            broadcast_event({
                "type": "round_start",
                "round": round_no,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })

            round_success = 0
            for idx in chosen_indices:
                if stop_requested.is_set():
                    break

                if idx < 1 or idx > len(PLATFORMS):
                    continue

                name, fn = PLATFORMS[idx - 1]

                try:
                    resp = fn(phone_62)
                except Exception as e:
                    resp = None

                status, detail = verdict(resp)

                with state_lock:
                    current_job["stats"]["total"] += 1
                    if status == "SUCCESS":
                        current_job["stats"]["success"] += 1
                        round_success += 1
                    elif status == "LIMIT":
                        current_job["stats"]["limit"] += 1
                    else:
                        current_job["stats"]["fail"] += 1

                    log_entry = {
                        "round": round_no,
                        "platform_id": idx,
                        "platform_name": name,
                        "status": status,
                        "detail": detail,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    current_job["logs"].append(log_entry)
                    # Keep max 500 logs in memory
                    if len(current_job["logs"]) > 500:
                        current_job["logs"].pop(0)

                broadcast_event({
                    "type": "log",
                    "entry": log_entry,
                    "stats": current_job["stats"]
                })

                # Short delay between platforms to prevent local socket exhaustion
                time.sleep(0.5)

            broadcast_event({
                "type": "round_complete",
                "round": round_no,
                "round_success": round_success,
                "stats": current_job["stats"]
            })

            # Check termination for single / pick run
            if mode != "loop" or stop_requested.is_set():
                break

            # Delay countdown for loop mode
            for elapsed in range(delay):
                if stop_requested.is_set():
                    break
                broadcast_event({
                    "type": "countdown",
                    "remaining": delay - elapsed
                })
                time.sleep(1)

    except Exception as e:
        broadcast_event({
            "type": "error",
            "message": str(e)
        })

    finally:
        with state_lock:
            active_task = False
            current_job["status"] = "stopped" if stop_requested.is_set() else "completed"

        broadcast_event({
            "type": "job_complete",
            "status": current_job["status"],
            "stats": current_job["stats"]
        })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/png')

@app.route('/api/info', methods=['GET'])
def api_info():
    ip = get_ip()
    user_agent = request.headers.get('User-Agent', '')
    forwarded = request.headers.get('X-Forwarded-For', '')
    client_ip = forwarded.split(',')[0].strip() if forwarded else request.remote_addr
    is_android = 'android' in user_agent.lower()
    is_external = client_ip not in ('127.0.0.1', 'localhost', '::1')
    is_limited = is_android or is_external

    sys_info = {
        "os": f"{pf.system()} {pf.release()}",
        "python": pf.python_version(),
        "cpu_cores": os.cpu_count(),
        "public_ip": ip,
    }
    if psutil:
        mem = psutil.virtual_memory()
        sys_info["ram"] = f"{mem.percent}% ({mem.used // (1024**3)}GB/{mem.total // (1024**3)}GB)"
    else:
        sys_info["ram"] = "N/A"

    platforms_meta = [
        {"id": i, "name": name}
        for i, (name, _) in enumerate(PLATFORMS, 1)
    ]

    with state_lock:
        task_active = active_task
        status = current_job["status"]

    return jsonify({
        "system": sys_info,
        "platforms": platforms_meta,
        "active": task_active,
        "job_status": status,
        "job": current_job,
        "client": {
            "ip": client_ip,
            "is_android": is_android,
            "is_external": is_external,
            "is_limited": is_limited
        }
    })

@app.route('/api/spam/start', methods=['POST'])
def api_start_spam():
    global active_task
    with state_lock:
        if active_task:
            return jsonify({"success": False, "message": "Proses spam sedang berjalan!"}), 400

    data = request.get_json() or {}
    raw_phone = data.get("phone", "")
    p62 = normalize(raw_phone)
    if not p62:
        return jsonify({"success": False, "message": "Format nomor telepon tidak valid. Gunakan 08xx / 62xx / +62xx"}), 400

    mode = data.get("mode", "single")
    delay = int(data.get("delay", 60))
    if delay < 5:
        delay = 5

    platforms_req = data.get("platforms", [])
    if not platforms_req:
        chosen_indices = list(range(1, len(PLATFORMS) + 1))
    else:
        try:
            chosen_indices = [int(x) for x in platforms_req if 1 <= int(x) <= len(PLATFORMS)]
        except Exception:
            chosen_indices = list(range(1, len(PLATFORMS) + 1))

    if not chosen_indices:
        chosen_indices = list(range(1, len(PLATFORMS) + 1))

    # Proteksi / Limit Perangkat Android & User Eksternal
    user_agent = request.headers.get('User-Agent', '')
    forwarded = request.headers.get('X-Forwarded-For', '')
    client_ip = forwarded.split(',')[0].strip() if forwarded else request.remote_addr
    is_android = 'android' in user_agent.lower()
    is_external = client_ip not in ('127.0.0.1', 'localhost', '::1')

    limited_msg = ""
    if is_android or is_external:
        mode = "single"
        chosen_indices = chosen_indices[:1]  # Batasi HANYA 1 OTP per platform per hari
        limited_msg = " (Batas Pengguna Biasa: Maksimal 1x OTP per platform / hari)"

    # Start background worker thread
    t = threading.Thread(
        target=run_spam_worker,
        args=(p62, mode, delay, chosen_indices),
        daemon=True
    )
    t.start()

    return jsonify({
        "success": True,
        "message": f"Proses spam dimulai ke {fmtplus(p62)}{limited_msg}",
        "target": fmtplus(p62),
        "mode": mode,
        "platforms_count": len(chosen_indices),
        "is_limited": is_android or is_external
    })

@app.route('/api/spam/stop', methods=['POST'])
def api_stop_spam():
    global active_task
    with state_lock:
        if not active_task:
            return jsonify({"success": False, "message": "Tidak ada proses spam yang sedang berjalan"}), 400
        stop_requested.set()

    return jsonify({"success": True, "message": "Sinyal pemberhentian telah dikirim!"})

@app.route('/api/spam/stream')
def api_stream():
    """Server-Sent Events (SSE) Endpoint"""
    q = queue.Queue()
    with state_lock:
        sse_subscribers.append(q)

    def event_generator():
        try:
            # Send initial state event
            with state_lock:
                init_event = f"data: {json.dumps({'type': 'init', 'job': current_job, 'active': active_task})}\n\n"
            yield init_event

            while True:
                data = q.get()
                yield data
        except GeneratorExit:
            with state_lock:
                if q in sse_subscribers:
                    sse_subscribers.remove(q)

    return Response(event_generator(), mimetype='text/event-stream')

if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    print("=" * 60)
    print("[+] NEX-OTP WEB DASHBOARD RUNNING AT http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
