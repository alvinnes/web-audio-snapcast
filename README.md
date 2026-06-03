# 🎵 Snapcast Audio Streaming Manager

Aplikasi web berbasis Python untuk manajemen sistem audio streaming Snapcast, dilengkapi dokumentasi konfigurasi Snapserver dan Snapclient di Armbian.

***

## 📖 Pendahuluan

Sistem ini menggunakan **Music Player Daemon (MPD)** sebagai sumber audio, **Snapserver** sebagai distributor stream, dan **Snapclient** sebagai penerima audio pada sisi endpoint. Audio dari MPD diteruskan ke FIFO pipe, lalu dibaca oleh Snapserver untuk dikirim ke client melalui jaringan, kemudian diputar melalui ALSA ke perangkat audio tujuan.

> ⚠️ Sebelum membaca dokumentasi ini, pastikan kalian sudah membaca **Dokumentasi Instalasi Armbian** terlebih dahulu.
> [📄 Klik di sini untuk membaca Dokumentasi Instalasi Armbian](https://docs.google.com/document/d/15V6Q-O73UdcTIVRZ8_yipzSrp0qxL2ZS/edit?usp=drive_link&ouid=118088395299377037506&rtpof=true&sd=true)

***

## 🚀 Cara Menjalankan Web App

1. Clone repository ini
   ```bash
   git clone https://github.com/username/repo-name.git
   cd repo-name
   ```

2. Pindahkan folder ke `/opt/`
   ```bash
   mv web-audio /opt/web-audio
   cd /opt/web-audio
   ```

3. Install Python dan buat virtual environment
   ```bash
   sudo apt install python3 python3-venv python3-pip -y
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Jalankan aplikasi
   ```bash
   python3 app.py
   ```

5. Buka browser dan akses:
   ```
   http://<IP_SERVER>:5000
   ```

***

## 📚 Dokumentasi

| Dokumentasi | Deskripsi |
|---|---|
| [🖥️ Konfigurasi Snapserver](./docs/snapserver.md) | Panduan instalasi dan konfigurasi MPD, Samba, dan Snapserver di Armbian |
| [🔊 Konfigurasi Snapclient](./docs/snapclient.md) | Panduan instalasi dan konfigurasi Snapclient di Armbian client |

***

## ✅ Prerequisite

### Perangkat Keras
- 1 STB sebagai **Server** (menjalankan MPD + Snapserver)
- 2 STB sebagai **Client** (menjalankan Snapclient)
- Speaker atau USB Audio Device
- Kabel LAN untuk menghubungkan server dan client

### Perangkat Lunak
- Sistem operasi Linux (Armbian)
- MPD, Snapserver, Snapclient
- ALSA sebagai backend output audio
- Python 3 + pip

### Jaringan & Akses
- Server dan client berada dalam jaringan yang sama
- Alamat IP server sudah diketahui
- User memiliki akses root atau sudo
- Port layanan Snapcast dapat diakses dari client

***

## ⚖️ Kelebihan & Kekurangan Sistem

### ✅ Kelebihan
- Pemutaran audio dapat dipusatkan di server, output di client
- Mendukung sinkronisasi audio ke beberapa client sekaligus
- Memudahkan pengelolaan queue lagu dari satu titik
- Mendukung berbagai output device ALSA sesuai perangkat client

### ❌ Kekurangan
- Konfigurasi awal lebih kompleks karena ada beberapa komponen yang harus cocok
- Jika satu bagian salah, seluruh alur bisa gagal
- Sinkronisasi waktu dan buffering sangat penting untuk stabilitas

***

## 🛠️ Teknologi yang Digunakan

- Python 3
- Flask (Web Framework)
- Snapcast (Snapserver + Snapclient)
- MPD (Music Player Daemon)
- Samba (File Sharing)
- ALSA (Audio Backend)
- Armbian (Linux OS)

***

## 👤 Disusun oleh

**Alvin (Ipin)**