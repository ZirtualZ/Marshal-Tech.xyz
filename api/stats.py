# api/stats.py
import psutil, platform, socket, subprocess, time
from collections import deque
from flask import Blueprint, jsonify

stats_api = Blueprint('stats_api', __name__, url_prefix='/api/stats')

net_state = {"last_bytes": psutil.net_io_counters(), "last_time": time.time()}
net_history = deque(maxlen=60)
cpu_history = deque(maxlen=60)
psutil.cpu_percent(interval=None)

REQUEST_COUNT = 0

@stats_api.before_request
def count_requests():
    global REQUEST_COUNT
    REQUEST_COUNT += 1

@stats_api.route('')
def get_stats():
    try:
        # CPU
        cpu_threads = psutil.cpu_percent(interval=None, percpu=True)
        cpu_total = psutil.cpu_percent(interval=None)
        cpu_history.append(cpu_total)

        # RAM
        mem = psutil.virtual_memory()

        # DISKS
        disks = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks.append({"mount": part.mountpoint, "percent": usage.percent})
            except:
                pass

        # NETWORK SPEED
        now = time.time()
        curr = psutil.net_io_counters()
        dt = max(now - net_state["last_time"], 0.1)
        up_kb = (curr.bytes_sent - net_state["last_bytes"].bytes_sent) / dt / 1024
        dl_kb = (curr.bytes_recv - net_state["last_bytes"].bytes_recv) / dt / 1024
        net_state["last_bytes"] = curr
        net_state["last_time"] = now
        net_history.append({"up": round(up_kb,1), "dl": round(dl_kb,1)})

        total_up = round(curr.bytes_sent / (1024**3),2)
        total_dl = round(curr.bytes_recv / (1024**3),2)

        # TEMP
        temp = 0
        sensors = psutil.sensors_temperatures()
        for name in sensors:
            temps = [t.current for t in sensors[name] if t.current]
            if temps:
                temp = sum(temps)/len(temps)
                break

        # TOP PROCESSES
        procs = []
        for p in psutil.process_iter(['name','cpu_percent']):
            try: procs.append(p.info)
            except: pass
        top = sorted(procs, key=lambda x:x['cpu_percent'], reverse=True)[:5]

        # SYSTEM INFO
        system = {
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "kernel": platform.release(),
            "cpu": platform.processor()
        }

        uptime = subprocess.check_output(["uptime","-p"], text=True).strip()

        return jsonify({
            "system": system,
            "cpu_threads": cpu_threads,
            "cpu_total": cpu_total,
            "cpu_history": list(cpu_history),
            "ram": {"used": round(mem.used / (1024**3),1), "total": round(mem.total / (1024**3),1), "pct": mem.percent},
            "disks": disks,
            "network": {"up": round(up_kb,1), "dl": round(dl_kb,1), "total_up": total_up, "total_dl": total_dl, "history": list(net_history)},
            "temperature": round(temp,1),
            "uptime": uptime,
            "top_processes": top,
            "requests": REQUEST_COUNT
        })

    except Exception as e:
        return jsonify({"error": str(e)}),500
