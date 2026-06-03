# 🖥️ Konfigurasi Snapserver

Dokumen ini menjelaskan langkah-langkah instalasi dan konfigurasi **MPD**, **Samba**, dan **Snapserver** di Armbian sebagai sisi server pada sistem audio streaming Snapcast.

> ⬅️ [Kembali ke README](../README.md)

***

## Langkah-Langkah Konfigurasi

### 1. Update Repository

Masuk ke sistem Armbian menggunakan user **Root** melalui SSH atau akses langsung, lalu lakukan pembaruan repository:

```bash
apt-get update
```

Tunggu hingga proses selesai.

***

### 2. Instalasi Paket

Install paket yang dibutuhkan untuk menjalankan MPD, Samba, dan Snapserver:

```bash
apt-get install mpd snapserver samba
```

Setelah instalasi selesai, buat direktori khusus untuk menyimpan file musik:

```bash
mkdir /etc/music
```

> 💡 Direktori lain bisa digunakan selama konsisten dengan konfigurasi MPD. Namun disarankan samakan saja dengan contoh di atas agar tidak kebingungan.

***

### 3. Atur Permission Direktori Musik

Atur permission agar direktori `/etc/music` dapat diakses oleh service MPD:

```bash
chown -R mpd:audio /etc/music
chmod -R 775 /etc/music
```

> ⚠️ **Perintahnya wajib sama persis seperti di atas!**

***

### 4. Konfigurasi Samba

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

> ⚠️ **Konfigurasi ini wajib sama persis seperti di atas!**

Simpan dengan **CTRL + O**, lalu **Enter**. Setelah itu restart Samba:

```bash
systemctl restart smbd
```

***

### 5. Transfer File Musik via Samba

Dari Laptop atau Komputer Windows, buka **Windows + R**, ketik IP server:

```
\\172.16.100.238
```

Cari folder bernama **music**, lalu pindahkan file lagu yang dimiliki ke dalam folder tersebut.

***

### 6. Konfigurasi MPD

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
    type  "fifo"
    name  "snapcast"
    path  "/tmp/snapfifo"
    format "48000:16:2"
    mixer_type "null"
}
```

> ⚠️ **Konfigurasi ini wajib sama persis seperti di atas!**

Simpan dengan **CTRL + O**, lalu **Enter**.

***

### 7. Restart MPD

```bash
systemctl restart mpd.service
```

***

### 8. Konfigurasi Snapserver

Buka file konfigurasi Snapserver:

```bash
nano /etc/snapserver.conf
```

Cari bagian stream dan sesuaikan konfigurasinya (hapus tanda `#` jika ada):

```ini
[stream]
stream = pipe:///tmp/snapfifo?name=default&sampleformat=48000:16:2&codec=pcm
```

> ⚠️ **Konfigurasi ini wajib sama persis seperti di atas! Urutan baris di file ini tidak selalu sama, cari bagian yang sesuai satu per satu.**

Simpan dengan **CTRL + O**, lalu **Enter**. Kemudian restart Snapserver:

```bash
systemctl restart snapserver
```

***

### 9. Pengujian MPD dengan MPC

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

> ⚠️ **Wajib memasukkan perintah dari `mpc update` sampai `mpc play` secara berurutan.**

***

### 10. Konfigurasi Service Paging (audio-paging.service)

Buat service untuk fitur paging (Public Address System):

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

> ⚠️ **Konfigurasi ini wajib sama persis seperti pada gambar di dokumentasi asli!**

Simpan dengan **CTRL + O**, lalu **Enter**. Kemudian aktifkan service:

```bash
systemctl daemon-reload
systemctl enable audio-paging.service
systemctl start audio-paging.service
```

***

### 11. Konfigurasi Service Musik Background (audio-music.service)

Buat service untuk menjalankan musik di latar belakang:

```bash
nano /etc/systemd/system/audio-music.service
```

> ⚠️ **Konfigurasi ini wajib sama persis seperti pada gambar di dokumentasi asli!**

Setelah dikonfigurasi, aktifkan service:

```bash
systemctl daemon-reload
systemctl enable audio-music.service
systemctl start audio-music.service
```

***

### 12. Menjalankan Web App

Pindahkan folder website ke `/opt/`:

```bash
mv /etc/music/web-audio /opt/web-audio
cd /opt/web-audio
```

Install Python dan jalankan:

```bash
sudo apt install python3 python3-venv python3-pip -y
source .venv/bin/activate
python3 app.py
```

Buka browser dan akses `http://<IP_SERVER>:5000`. Jika muncul tampilan website, lakukan pengujian upload lagu, play lagu, dan fitur lainnya.

***

> ✅ Jika semua fitur sudah bisa berjalan, konfigurasi Snapserver selesai. Lanjutkan ke **[Konfigurasi Snapclient](./snapclient.md)**.