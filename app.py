from flask import Flask, jsonify, render_template_string, request, redirect
from werkzeug.utils import secure_filename
import os
import subprocess
import json
import socket

app = Flask(__name__)

MUSIC_FOLDER = "/etc/musics"
SNAPSERVER_HOST = "127.0.0.1"
SNAPSERVER_PORT = 1705
current_volume = 50
paging_active = False
previous_player_state = "STOPPED"

# TARGET DEVICE ID (Hasil temuan sukses dari data JSON-RPC kamu)
GROUP_SPEAKER_ID = "1f61d533-e8bb-316c-0932-f5201a9faf3f"
CLIENT_MAC_ID = "00:15:18:01:81:31"

def run_cmd(cmd, shell=False):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=shell)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        code = result.returncode
    except Exception as e:
        print("EXCEPTION:", cmd, str(e))
        return {"ok": False, "stdout": "", "stderr": str(e), "code": -1}

    print("CMD:", cmd)
    print("CODE:", code)
    print("STDOUT:", stdout)
    print("STDERR:", stderr)

    return {"ok": code == 0, "stdout": stdout, "stderr": stderr, "code": code}

def load_files():
    if not os.path.exists(MUSIC_FOLDER):
        os.makedirs(MUSIC_FOLDER, exist_ok=True)

    return sorted([
        f for f in os.listdir(MUSIC_FOLDER)
        if f.lower().endswith((".mp3", ".wav"))
    ])


def rebuild_mpd_playlist():
    files = load_files()
    run_cmd(["mpc", "update"])
    run_cmd(["mpc", "clear"])
    run_cmd("mpc ls | mpc add", shell=True)
    return files


def get_current_song():
    if paging_active:
        return "🎙️ Streaming Suara Laptop Client..."
    r = run_cmd(["mpc", "current"])
    return r["stdout"] if r["ok"] else ""


def get_status_raw():
    r = run_cmd(["mpc", "status"])
    return r["stdout"] if r["ok"] else ""


def get_status_text():
    if paging_active:
        return "PAGING ON"

    text = get_status_raw().lower()
    if "[playing]" in text:
        return "MUSIC ON"
    if "[paused]" in text:
        return "PAUSED"
    return "STOPPED"


def get_random_state():
    text = get_status_raw().lower()
    return "random: on" in text

def get_queue_info():
    r = run_cmd(["mpc", "status"])
    if not r["ok"] or not r["stdout"]:
        return None

    lines = [line.strip() for line in r["stdout"].splitlines() if line.strip()]
    if len(lines) < 2:
        return None

    status_line = lines[1]

    if "#" not in status_line or "/" not in status_line:
        return None

    try:
        after_hash = status_line.split("#", 1)[1]
        pos_part = after_hash.split()[0]      # 1/5
        current_str, total_str = pos_part.split("/", 1)
        return {
            "position": int(current_str),
            "length": int(total_str)
        }
    except:
        return None

def get_playlist_info():
    r = run_cmd(["mpc", "-f", "%position%|%length%|%file%", "current"])
    if not r["ok"] or not r["stdout"]:
        return None

    parts = r["stdout"].split("|", 2)
    if len(parts) < 3:
        return None

    try:
        return {
            "position": int(parts[0]),
            "length": int(parts[1]),
            "file": parts[2]
        }
    except:
        return None


def snapcast_rpc(method, params=None, request_id=1):
    payload = {
        "id": request_id,
        "jsonrpc": "2.0",
        "method": method
    }
    if params is not None:
        payload["params"] = params

    with socket.create_connection((SNAPSERVER_HOST, SNAPSERVER_PORT), timeout=3) as sock:
        sock.sendall((json.dumps(payload) + "\r\n").encode())
        data = b""
        while not data.endswith(b"\n"):
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk

    return json.loads(data.decode().strip())

def list_snapclients():
    data = snapcast_rpc("Server.GetStatus")
    groups = data.get("result", {}).get("server", {}).get("groups", [])
    clients = []

    for group in groups:
        for client in group.get("clients", []):
            clients.append({
                "id": client.get("id"),
                "name": client.get("host", {}).get("name", client.get("id")),
                "volume": client.get("config", {}).get("volume", {}).get("percent", 100),
                "muted": client.get("config", {}).get("volume", {}).get("muted", False)
            })

    return clients

@app.route("/volume/<value>")
def volume(value):
    global current_volume

    try:
        v = int(float(value))
    except:
        v = 100

    if v < 0:
        v = 0
    if v > 100:
        v = 100

    current_volume = v

    clients = list_snapclients()
    if not clients:
        return jsonify({"error": "no snapclients found"}), 404

    errors = []

    for client in clients:
        result = snapcast_rpc("Client.SetVolume", {
            "id": client["id"],
            "volume": {
                "percent": current_volume,
                "muted": False
            }
        })

        if "error" in result:
            errors.append({
                "client": client["name"],
                "error": result["error"]
            })

    if errors:
        return jsonify({
            "status": "partial",
            "volume": current_volume,
            "errors": errors
        }), 207

    return jsonify({
        "status": "ok",
        "volume": current_volume,
        "clients_updated": len(clients)
    })

@app.route("/")
def index():
    files = load_files()

    current_song_info = get_current_song()

    playlist_items_html = ""
    if not files:
        playlist_items_html = "<p style='color: gray; text-align: center;'>Folder musik kosong.</p>"
    else:
        for f in files:
            is_current = "background: #e9f7ef; font-weight: bold; border-left: 5px solid green;" if f in current_song_info else ""
            playlist_items_html += f"""
            <div class="song" style="{is_current}">
                <div>🎵 {f}</div>
                <button class="music" onclick="playMusic('{f}')" style="padding: 5px 12px; font-size: 13px;">▶ PLAY</button>
            </div>
            """

    html_template = f"""
<!DOCTYPE html>
<html>
<head>
<title>Office Audio Control</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{
    font-family: Arial, sans-serif;
    background: #f2f2f2;
    padding: 20px;
}}
.card {{
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}}
button {{
    padding: 12px 20px;
    margin: 5px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-size: 15px;
    font-weight: bold;
}}
.music {{ background: green; color: white; }}
.stop {{ background: gray; color: white; }}
.paging {{ background: red; color: white; }}
.random {{ background: orange; color: white; }}
.song {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
    border-radius: 10px;
    background: #fafafa;
}}
input[type=range] {{ width: 100%; }}
</style>
</head>
<body>

<h1>🎛 Office Audio Control</h1>

<div class="card">
    <h2>Status: <span id="status">READY</span></h2>
    <div id="currentsong">No song</div>
    <br>

    <button class="music" onclick="musicOn()">▶️ Music ON</button>
    <button class="stop" onclick="musicOff()">⛔ Music OFF</button>
    <button class="paging" onclick="pagingOn()">🎤 Paging ON</button>
    <button class="stop" onclick="pagingOff()">🔇 Paging OFF</button>
</div>

<div class="card">
    <h2>🎵 Playlist Control</h2>
    <button onclick="prevMusic()">⏮ PREV</button>
    <button onclick="nextMusic()">⏭ NEXT</button>
    <button class="random" onclick="randomMusic()">🔀 RANDOM</button>

    <br><br>

    <label>🔊 Volume</label>
    <input type="range" id="volumeInput" min="0" max="100" step="1" value="100" onchange="setVolume(this.value)">
</div>

<div class="card">
    <h2>📤 Upload Lagu</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit" class="stop">UPLOAD</button>
    </form>
</div>

<div class="card">
    <h2>🎵 Playlist</h2>
    {playlist_items_html}
</div>

<script>
function musicOn() {{ fetch('/music/on').then(refreshStatus); }}

function musicOff() {{ fetch('/music/off').then(refreshStatus); }}

function pagingOn() {{ fetch('/paging/on').then(refreshStatus); }}

function pagingOff() {{ fetch('/paging/off').then(refreshStatus); }}

function playMusic(name) {{ fetch('/play/' + encodeURIComponent(name)).then(refreshStatus); }}

function nextMusic() {{ fetch('/next').then(refreshStatus); }}

function prevMusic() {{ fetch('/prev').then(refreshStatus); }}

function randomMusic() {{ fetch('/random').then(refreshStatus); }}

function setVolume(v) {{
    localStorage.setItem('volume', v);
    fetch('/volume/' + v).then(refreshStatus);
}}

function loadVolume() {{
    const savedVolume = localStorage.getItem('volume');
    const volumeSlider = document.getElementById('volumeInput');
    if (savedVolume !== null && volumeSlider) {{
        volumeSlider.value = savedVolume;
        fetch('/volume/' + savedVolume).then(refreshStatus);
    }}
}}

function refreshStatus() {{
    fetch('/status')
        .then(r => r.json())
        .then(data => {{
            let statusLabel = document.getElementById("status");
            statusLabel.innerText = data.status || "READY";
            document.getElementById("currentsong").innerText = data.song || "No song";

            if (data.status === "PAGING ON") {{
                statusLabel.style.color = "red";
            }} else if (data.status === "MUSIC ON") {{
                statusLabel.style.color = "green";
            }} else {{
                statusLabel.style.color = "black";
            }}
        }})
        .catch(() => {{
            document.getElementById("status").innerText = "ERROR";
        }});
}}

loadVolume();
refreshStatus();
setInterval(refreshStatus, 2000);
</script>

</body>
</html>
"""
    return render_template_string(html_template)

@app.route("/status")
def status():
    return jsonify({
        "status": get_status_text(),
        "song": get_current_song(),
        "volume": current_volume,
        "paging": paging_active,
    })


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return redirect("/")

    file = request.files["file"]

    if file.filename == "":
        return redirect("/")

    os.makedirs(MUSIC_FOLDER, exist_ok=True)

    filename = secure_filename(file.filename)
    save_path = os.path.join(MUSIC_FOLDER, filename)
    file.save(save_path)

    run_cmd(["mpc", "update"])
    return redirect("/")


@app.route("/play/<path:filename>")
def play_music(filename):
    files = rebuild_mpd_playlist()

    if filename not in files:
        return jsonify({"error": "file not found"}), 404

    index = files.index(filename) + 1
    
    # PERBAIKAN: Pastikan group diarahkan ke MPD dan volumenya aktif
    snapcast_rpc("Group.SetStream", {"id": GROUP_SPEAKER_ID, "stream_id": "MPD"})
    snapcast_rpc("Client.SetVolume", {"id": CLIENT_MAC_ID, "volume": {"percent": current_volume, "muted": False}})
    
    r = run_cmd(["mpc", "play", str(index)])

    if not r["ok"]:
        return jsonify({"error": r["stderr"] or "failed to play"}), 500

    return jsonify({
        "status": "playing",
        "file": filename
    })

@app.route("/next")
def next_music():
    info = get_queue_info()
    if not info:
        return jsonify({"error": "no current song"}), 400

    if info["position"] >= info["length"]:
        r = run_cmd(["mpc", "play", str(info["position"])])
    else:
        r = run_cmd(["mpc", "play", str(info["position"] + 1)])

    if not r["ok"]:
        return jsonify({"error": r["stderr"] or "failed next"}), 500

    return jsonify({"status": "next"})


@app.route("/prev")
def prev_music():
    info = get_queue_info()
    if not info:
        return jsonify({"error": "no current song"}), 400

    if info["position"] <= 1:
        r = run_cmd(["mpc", "play", "1"])
    else:
        r = run_cmd(["mpc", "play", str(info["position"] - 1)])

    if not r["ok"]:
        return jsonify({"error": r["stderr"] or "failed prev"}), 500

    return jsonify({"status": "prev"})

@app.route("/random")
def random_music():
    files = rebuild_mpd_playlist()

    if not files:
        return jsonify({"error": "no music"}), 400

    import random
    index = random.randint(1, len(files))

    r = run_cmd(["mpc", "play", str(index)])

    if not r["ok"]:
        return jsonify({"error": r["stderr"] or "failed random"}), 500

    return jsonify({
        "status": "random",
        "song": get_current_song()
    })

@app.route("/clients")
def clients():
    return jsonify(list_snapclients())

@app.route("/client-volume/<client_id>/<value>")
def client_volume(client_id, value):
    try:
        v = int(float(value))
    except:
        v = 100

    if v < 0:
        v = 0
    if v > 100:
        v = 100

    result = snapcast_rpc("Client.SetVolume", {
        "id": client_id,
        "volume": {
            "percent": v,
            "muted": False
        }
    })

    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    return jsonify({"status": "ok", "client_id": client_id, "volume": v})

# =========================================================================
# PERBAIKAN: MUSIC ON / OFF (MENGGUNAKAN MPC NATIVE AGAR KONSISTEN)
# =========================================================================

@app.route("/music/on")
def music_on():
    snapcast_rpc("Group.SetStream", {"id": GROUP_SPEAKER_ID, "stream_id": "MPD"})
    snapcast_rpc("Client.SetVolume", {"id": CLIENT_MAC_ID, "volume": {"percent": current_volume, "muted": False}})
    run_cmd(["mpc", "play"])
    return jsonify({"status": "music on"})


@app.route("/music/off")
def music_off():
    run_cmd(["mpc", "stop"])
    return jsonify({"status": "music off"})

# =========================================================================
# INTEGRASI SERVICE & PERBAIKAN TOTAL: PAGING ON / OFF
# =========================================================================

@app.route("/paging/on")
def paging_on():
    global paging_active, previous_player_state

    if paging_active:
        return jsonify({"status": "paging already active"})

    previous_player_state = get_status_text()
    if previous_player_state == "MUSIC ON":
        run_cmd(["mpc", "pause"])

    snapcast_rpc("Group.SetStream", {"id": GROUP_SPEAKER_ID, "stream_id": "Paging"})
    snapcast_rpc("Client.SetVolume", {"id": CLIENT_MAC_ID, "volume": {"percent": 90, "muted": False}})

    run_cmd(["sudo", "systemctl", "start", "audio-paging.service"])

    paging_active = True
    return jsonify({
        "status": "paging on",
        "previous_player_state": previous_player_state
    })

@app.route("/paging/off")
def paging_off():
    global paging_active, previous_player_state

    if not paging_active:
        return jsonify({"status": "paging already off"})

    run_cmd(["sudo", "systemctl", "stop", "audio-paging.service"])

    snapcast_rpc("Group.SetStream", {"id": GROUP_SPEAKER_ID, "stream_id": "MPD"})
    snapcast_rpc("Client.SetVolume", {"id": CLIENT_MAC_ID, "volume": {"percent": current_volume, "muted": False}})

    if previous_player_state == "MUSIC ON":
        run_cmd(["mpc", "play"])

    paging_active = False
    return jsonify({"status": "paging off"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
