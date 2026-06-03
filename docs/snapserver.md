<div align="center">

# 🖥️ Konfigurasi Snapserver

<p>
  <img src="https://img.shields.io/badge/Role-Server-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/OS-Armbian-E95420?style=flat-square&logo=linux&logoColor=white" />
  <img src="https://img.shields.io/badge/Service-MPD%20%2B%20Snapserver-1DB954?style=flat-square" />
</p>

</div>

> ⬅️ [Kembali ke README](../README.md)

***

## 📋 Ringkasan Langkah

```
① Update Repo  →  ② Install Paket  →  ③ Set Permission
      ↓
④ Konfigurasi Samba  →  ⑤ Transfer Musik  →  ⑥ Konfigurasi MPD
      ↓
⑦ Konfigurasi Snapserver  →  ⑧ Test MPC  →  ⑨ Buat Service
      ↓
⑩ Jalankan Web App  ✅
```

***

## Langkah-Langkah Konfigurasi

### 1️⃣ Update Repository

Masuk ke sistem Armbian menggunakan user **Root** melalui SSH atau akses langsung:

```bash
apt-get update
```

Tunggu hingga proses selesai.

***

### 2️⃣ Instalasi Paket

Install semua paket yang dibutuhkan sekaligus:

```bash
apt-get install mpd snapserver samba
```

Setelah selesai, buat direktori untuk menyimpan file musik:

```bash
mkdir /etc/music
```

> [!TIP]
> Direktori lain bisa digunakan selama konsisten dengan konfigurasi MPD.
> Namun disarankan **samakan saja** dengan contoh di atas agar tidak kebingungan.

***

### 3️⃣ Atur Permission Direktori Musik

```bash
chown -R mpd:audio /etc/music
chmod -R 775 /etc/music
```

> [!CAUTION]
> **Perintahnya wajib sama persis seperti di atas!**

***

### 4️⃣ Konfigurasi Samba

Buka file konfigurasi Samba:

```bash
nano /etc/samba/smb.conf
```

Tambahkan konfigurasi berikut di **baris paling bawah** file:

```ini
[music]
   path = /etc/music
   browseable = yes
   read only = no
   guest ok = yes
   force user = root
```

> [!CAUTION]
> **Konfigurasi ini wajib sama persis seperti di atas!**

Simpan dengan **`CTRL + O`** → **`Enter`**, lalu restart Samba:

```bash
systemctl restart smbd
```

***

### 5️⃣ Transfer File Musik via Samba

Dari Laptop atau Komputer Windows:

1. Tekan **`Windows + R`**

2. Ketik IP server, contoh:
   ```
   \\172.16.100.238
   ```

3. Cari folder bernama **`music`**

4. Pindahkan file lagu dari komputer ke dalam folder tersebut

***

### 6️⃣ Konfigurasi MPD

Buka file konfigurasi MPD:

```bash
nano /etc/mpd.conf
```

Sesuaikan pengaturan berikut (hapus tanda `#` pada baris yang perlu diaktifkan):

```ini
music_directory     "/etc/music"
playlist_directory  "/var/lib/mpd/playlists"
db_file             "/var/lib/mpd/database"
log_file            "/var/log/mpd/mpd.log"
pid_file            "/run/mpd/pid"
state_file          "/var/lib/mpd/state"

bind_to_address     "127.0.0.1"

audio_output {
    type       "fifo"
    name       "snapcast"
    path       "/tmp/snapfifo"
    format     "48000:16:2"
}
```

> [!CAUTION]
> **Konfigurasi ini wajib sama persis seperti di atas!**

Simpan dengan **`CTRL + O`** → **`Enter`**, lalu restart MPD:

```bash
systemctl restart mpd.service
```

***

### 7️⃣ Konfigurasi Snapserver

Buka file konfigurasi Snapserver:

```bash
nano /etc/snapserver.conf
```

Cari bagian `[stream]` dan sesuaikan (hapus tanda `#` jika ada):

```ini
[stream]
stream = pipe:///tmp/snapfifo?name=default&sampleformat=48000:16:2&codec=pcm
```

> [!CAUTION]
> **Konfigurasi ini wajib sama persis seperti di atas!**
> Urutan baris di file ini tidak selalu sama — cari bagian yang sesuai **satu per satu**.

Simpan dengan **`CTRL + O`** → **`Enter`**, lalu restart Snapserver:

```bash
systemctl restart snapserver
```

***

### 8️⃣ Pengujian MPD dengan MPC

Install paket `mpc`:

```bash
apt-get install mpc
```

Jalankan perintah berikut **secara urut satu per satu**:

```bash
mpc update
mpc ls
mpc add /
mpc play
```

> [!IMPORTANT]
> Wajib memasukkan perintah dari `mpc update` sampai `mpc play` **secara berurutan dari atas ke bawah**.

***

### 9️⃣ Konfigurasi Service Paging

**Paging** adalah sistem penyiaran pengumuman suara satu arah dari server ke banyak speaker client secara bersamaan.

Buat file service:

```bash
nano /etc/systemd/system/audio-paging.service
```

Isi dengan konfigurasi berikut:

```ini
[Unit]
Description=Audio Paging Service
After=network.target snapserver.service

[Service]
ExecStart=/usr/bin/arecord -D default -f cd -t raw | /usr/bin/snapcast-paging
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
```

> [!CAUTION]
> **Konfigurasi ini wajib sama persis seperti pada gambar di dokumentasi asli!**

Simpan, lalu aktifkan service:

```bash
systemctl daemon-reload
systemctl enable audio-paging.service
systemctl start audio-paging.service
```

***

### 🔟 Konfigurasi Service Musik Background

Buat satu service lagi untuk musik background:

```bash
nano /etc/systemd/system/audio-music.service
```

> [!CAUTION]
> **Konfigurasi ini wajib sama persis seperti pada gambar di dokumentasi asli!**

Aktifkan service:

```bash
systemctl daemon-reload
systemctl enable audio-music.service
systemctl start audio-music.service
```

***

### 1️⃣1️⃣ Menjalankan Web App

Pindahkan folder website ke `/opt/`:

```bash
mv /etc/music/web-audio /opt/web-audio
cd /opt/web-audio
```

Install Python dan jalankan aplikasi:

```bash
sudo apt install python3 python3-venv python3-pip -y
source .venv/bin/activate
python3 app.py
```

> [!IMPORTANT]
> Di dalam folder project terdapat beberapa file script Python seperti `music.py`.
> **Abaikan semua file tersebut.**
> Satu-satunya file yang perlu dijalankan adalah **`app.py`**.

Buka browser dan akses:

```
http://<IP_SERVER>:5000
```

Lakukan pengujian upload lagu, play lagu, dan fitur lainnya.

***

<div align="center">

> ✅ **Konfigurasi Snapserver selesai!**
>
> Lanjutkan ke **[🔊 Konfigurasi Snapclient →](./snapclient.md)**

</div>