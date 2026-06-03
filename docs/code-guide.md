<div align="center">

# 🗂️ Panduan Kode — app.py

<p>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-Web%20App-000000?style=flat-square&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/MPD-Music%20Control-1DB954?style=flat-square" />
  <img src="https://img.shields.io/badge/Snapcast-JSON--RPC-FF6B35?style=flat-square" />
</p>

Panduan ini menjelaskan **letak bagian kode** di `app.py` agar kamu tahu harus mengubah di mana jika ingin menyesuaikan sesuatu.

</div>

> ⬅️ [Kembali ke README](../README.md)

***

## 📋 Daftar Isi

- [Konfigurasi Utama](#-konfigurasi-utama)
- [Alur Kerja Sistem](#-alur-kerja-sistem)
- [Peta Fungsi](#-peta-fungsi)
- [Panduan Ubah per Fitur](#-panduan-ubah-per-fitur)
- [Referensi API Endpoint](#-referensi-api-endpoint)

***

## ⚙️ Konfigurasi Utama

Semua **variabel yang perlu disesuaikan** ada di bagian paling atas `app.py`, setelah baris `app = Flask(__name__)`.

```python
# ── Lokasi folder musik ──────────────────────────────────
MUSIC_FOLDER = "/etc/musics"          # ← Ubah jika folder musik berbeda

# ── Koneksi Snapserver ───────────────────────────────────
SNAPSERVER_HOST = "127.0.0.1"         # ← Ubah jika Snapserver di host lain
SNAPSERVER_PORT = 1705                # ← Port JSON-RPC Snapserver (default 1705)

# ── Volume default saat pertama jalan ────────────────────
current_volume = 50                   # ← Ubah angka 0–100

# ── ID Target Device Snapcast ────────────────────────────
GROUP_SPEAKER_ID = "1f61d533-e8bb-316c-0932-f5201a9faf3f"  # ← ID Group speaker
CLIENT_MAC_ID    = "00:15:18:01:81:31"                      # ← MAC Address client
```

> [!IMPORTANT]
> `GROUP_SPEAKER_ID` dan `CLIENT_MAC_ID` **unik untuk setiap perangkat**.
> Jika ganti STB atau install ulang, kedua ID ini harus diperbarui.
> Cara cek ID: akses endpoint `/clients` di browser → `http://IP_SERVER:5000/clients`

***

## 🔄 Alur Kerja Sistem

```
Browser / User
     │
     │  HTTP Request
     ▼
┌─────────────────────────────────────────────────┐
│                   app.py (Flask)                │
│                                                 │
│  Route Handler  ──►  Helper Function            │
│  (misal /play)        (run_cmd, snapcast_rpc)   │
└───────────┬──────────────────┬──────────────────┘
            │                  │
            ▼                  ▼
     ┌─────────┐        ┌──────────────┐
     │   MPC   │        │  Snapserver  │
     │ (shell) │        │  (JSON-RPC)  │
     └────┬────┘        └──────┬───────┘
          │                    │
          ▼                    ▼
     ┌─────────┐        ┌──────────────┐
     │   MPD   │        │  Snapclient  │
     │ (audio) │        │  (speaker)   │
     └─────────┘        └──────────────┘
```

***

## 🗺️ Peta Fungsi

Seluruh fungsi di `app.py` dibagi menjadi **3 kelompok**:

### 🔧 Helper Functions (Fungsi Pembantu)

Fungsi-fungsi ini **tidak bisa diakses dari browser**, hanya dipanggil oleh fungsi lain di dalam kode.

| Fungsi | Kegunaan | Ubah jika... |
|--------|----------|--------------|
| `run_cmd(cmd)` | Menjalankan perintah shell (mpc, systemctl, dll) | Ingin menambahkan logging atau error handling |
| `load_files()` | Membaca daftar file `.mp3`/`.wav` dari `MUSIC_FOLDER` | Ingin support format lain (`.flac`, `.ogg`, dll) |
| `rebuild_mpd_playlist()` | Memperbarui playlist MPD dari folder musik | Ingin urutan playlist berbeda |
| `get_current_song()` | Mengambil nama lagu yang sedang diputar | — |
| `get_status_raw()` | Mengambil output mentah dari `mpc status` | — |
| `get_status_text()` | Mengubah status MPD menjadi teks: `MUSIC ON / PAUSED / STOPPED / PAGING ON` | Ingin menambah status baru |
| `get_random_state()` | Mengecek apakah mode random aktif | — |
| `get_queue_info()` | Mengambil posisi lagu saat ini di playlist (misal: lagu ke-2 dari 5) | — |
| `get_playlist_info()` | Mengambil info detail lagu saat ini (posisi, total, nama file) | — |
| `snapcast_rpc(method, params)` | Mengirim perintah ke Snapserver via JSON-RPC (TCP socket) | Ingin ganti cara komunikasi ke Snapserver |
| `list_snapclients()` | Mengambil daftar semua Snapclient yang terhubung ke server | — |

***

### 🌐 Route Handlers (Endpoint API)

Fungsi-fungsi ini **bisa diakses dari browser atau JavaScript**.

| Route | Fungsi | Kegunaan |
|-------|--------|----------|
| `GET /` | `index()` | Halaman utama web — tampilan UI |
| `GET /status` | `status()` | Ambil status terkini (status, lagu, volume, paging) |
| `GET /upload` | `upload()` | Upload file musik ke server |
| `GET /play/<filename>` | `play_music()` | Putar lagu berdasarkan nama file |
| `GET /next` | `next_music()` | Lagu berikutnya |
| `GET /prev` | `prev_music()` | Lagu sebelumnya |
| `GET /random` | `random_music()` | Putar lagu acak |
| `GET /volume/<value>` | `volume()` | Set volume semua client (0–100) |
| `GET /clients` | `clients()` | Lihat daftar Snapclient yang terhubung |
| `GET /client-volume/<id>/<value>` | `client_volume()` | Set volume client tertentu saja |
| `GET /music/on` | `music_on()` | Nyalakan musik (resume/play) |
| `GET /music/off` | `music_off()` | Matikan musik (stop) |
| `GET /paging/on` | `paging_on()` | Aktifkan mode paging (mic siaran) |
| `GET /paging/off` | `paging_off()` | Matikan mode paging, kembali ke musik |

***

## 🛠️ Panduan Ubah per Fitur

### 📁 Ingin mengubah lokasi folder musik?

Cari di bagian **konfigurasi utama** (baris atas `app.py`):

```python
MUSIC_FOLDER = "/etc/musics"   # ← Ganti path di sini
```

> [!TIP]
> Pastikan path yang baru memiliki permission yang benar dan konsisten dengan konfigurasi MPD di `/etc/mpd.conf`.

***

### 🔊 Ingin mengubah volume default saat aplikasi pertama dijalankan?

```python
current_volume = 50   # ← Ganti angka ini (0–100)
```

***

### 🎵 Ingin menambahkan support format audio selain MP3/WAV?

Cari fungsi `load_files()`:

```python
def load_files():
    return sorted([
        f for f in os.listdir(MUSIC_FOLDER)
        if f.lower().endswith((".mp3", ".wav"))   # ← Tambahkan format di sini
    ])
```

Contoh — tambahkan `.flac` dan `.ogg`:

```python
if f.lower().endswith((".mp3", ".wav", ".flac", ".ogg"))
```

***

### 🎤 Ingin mengubah volume saat paging aktif?

Cari fungsi `paging_on()` di bagian bawah kode:

```python
snapcast_rpc("Client.SetVolume", {
    "id": CLIENT_MAC_ID,
    "volume": {"percent": 90, "muted": False}   # ← Ganti 90 sesuai kebutuhan
})
```

***

### ⏱️ Ingin mengubah seberapa sering status di-refresh di browser?

Cari di bagian `<script>` dalam fungsi `index()`:

```javascript
setInterval(refreshStatus, 2000);   // ← 2000 = setiap 2 detik, ubah sesuai kebutuhan
```

***

### 🎨 Ingin mengubah tampilan UI (warna tombol, layout, dll)?

Semua tampilan HTML dan CSS ada di dalam fungsi `index()`, pada variabel `html_template`. Cari bagian `<style>`:

```python
html_template = f"""
<!DOCTYPE html>
...
<style>
  /* ← Ubah CSS di sini */
  .music {{ background: green; color: white; }}   /* Tombol Music ON */
  .stop  {{ background: gray;  color: white; }}   /* Tombol Stop/Off */
  .paging {{ background: red; color: white; }}    /* Tombol Paging   */
  .random {{ background: orange; color: white; }} /* Tombol Random   */
</style>
```

***

### 🆔 Ingin mengubah target Group/Client Snapcast?

Jika kamu ganti perangkat atau install ulang, ID akan berubah. Perbarui di bagian konfigurasi utama:

```python
GROUP_SPEAKER_ID = "1f61d533-e8bb-316c-0932-f5201a9faf3f"  # ← ID baru
CLIENT_MAC_ID    = "00:15:18:01:81:31"                      # ← MAC baru
```

Untuk mencari ID yang benar, buka browser dan akses:

```
http://<IP_SERVER>:5000/clients
```

Akan muncul JSON berisi semua client yang terhubung beserta ID-nya.

***

### 🔌 Ingin mengubah port aplikasi web?

Cari di baris **paling bawah** `app.py`:

```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)   # ← Ganti 5000 ke port lain
```

***

## 🔗 Referensi API Endpoint

Semua endpoint bisa diakses langsung dari browser atau `curl` untuk keperluan pengujian.

| Endpoint | Contoh | Hasil |
|----------|--------|-------|
| `GET /` | `http://IP:5000/` | Halaman utama web |
| `GET /status` | `http://IP:5000/status` | JSON status sistem |
| `GET /clients` | `http://IP:5000/clients` | JSON daftar Snapclient + ID |
| `GET /play/<file>` | `http://IP:5000/play/lagu.mp3` | Putar lagu tertentu |
| `GET /volume/80` | `http://IP:5000/volume/80` | Set volume semua client ke 80% |
| `GET /music/on` | `http://IP:5000/music/on` | Nyalakan musik |
| `GET /music/off` | `http://IP:5000/music/off` | Matikan musik |
| `GET /paging/on` | `http://IP:5000/paging/on` | Aktifkan paging |
| `GET /paging/off` | `http://IP:5000/paging/off` | Matikan paging |
| `GET /next` | `http://IP:5000/next` | Lagu berikutnya |
| `GET /prev` | `http://IP:5000/prev` | Lagu sebelumnya |
| `GET /random` | `http://IP:5000/random` | Putar lagu acak |

***

<div align="center">

⬅️ [Kembali ke README](../README.md)

</div>