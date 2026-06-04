# 🎵 Snapcast Audio Streaming Manager

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-Web%20App-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/Snapcast-Audio%20Stream-FF6B35?style=for-the-badge&logo=audiomack&logoColor=white" />
  <img src="https://img.shields.io/badge/Armbian-Linux-E95420?style=for-the-badge&logo=linux&logoColor=white" />
  <img src="https://img.shields.io/badge/MPD-Music%20Player-1DB954?style=for-the-badge&logo=spotify&logoColor=white" />
</p>

<p align="center">
  Aplikasi web berbasis Python untuk manajemen sistem audio streaming Snapcast, <br/>
  dilengkapi dokumentasi konfigurasi Snapserver, Snapclient, dan transfer file musik via SFTP di Armbian.
</p>

<p align="center">
  <a href="./docs/snapserver.md">📖 Dokumentasi Snapserver</a> &nbsp;- &nbsp;
  <a href="./docs/snapclient.md">📖 Dokumentasi Snapclient</a> &nbsp;- &nbsp;
  <a href="https://docs.google.com/document/d/15V6Q-O73UdcTIVRZ8_yipzSrp0qxL2ZS/edit?usp=drive_link">📄 Dokumentasi Armbian</a>
</p>

</div>

---

> [!WARNING]
> Sebelum membaca dokumentasi ini, pastikan kalian sudah membaca **Dokumentasi Instalasi Armbian** terlebih dahulu.
> [📄 Klik di sini untuk membaca Dokumentasi Instalasi Armbian](https://docs.google.com/document/d/15V6Q-O73UdcTIVRZ8_yipzSrp0qxL2ZS/edit?usp=drive_link&ouid=118088395299377037506&rtpof=true&sd=true)

---

## 📋 Daftar Isi

- [Pendahuluan](#-pendahuluan)
- [Cara Kerja Sistem](#-cara-kerja-sistem)
- [Prerequisite](#-prerequisite)
- [Struktur Project](#-struktur-project)
- [Cara Menjalankan](#-cara-menjalankan-web-app)
- [Dokumentasi](#-dokumentasi)
- [Kelebihan & Kekurangan](#-kelebihan--kekurangan)
- [Teknologi](#-teknologi-yang-digunakan)

---

## 📖 Pendahuluan

Sistem ini menggunakan **Music Player Daemon (MPD)** sebagai sumber audio, **Snapserver** sebagai distributor stream, dan **Snapclient** sebagai penerima audio pada sisi endpoint.

Audio dari MPD diteruskan ke **FIFO pipe**, lalu dibaca oleh Snapserver untuk dikirim ke client melalui jaringan, kemudian diputar melalui **ALSA** ke perangkat audio tujuan. Transfer file musik ke server dilakukan melalui **SFTP menggunakan FileZilla**.

---

## ⚙️ Cara Kerja Sistem

```text
┌─────────────────────────────────────────────────────────────┐
│                          SERVER (STB)                       │
│                                                             │
│   ┌───────┐    FIFO     ┌────────────┐    TCP/UDP           │
│   │  MPD  │ ─────────►  │ Snapserver │ ──────────────────┐  │
│   └───────┘  /tmp/snapfifo└────────────┘                  │  │
│       ▲                                                     │  │
│       │                                                     │  │
│   [File Musik]                                              │  │
│   /etc/music                                                │  │
└─────────────────────────────────────────────────────────────┼──┘
                                                              │
                           Jaringan LAN                       │
                 ┌────────────────────────────────────────────┘
                 │                            │
                 ▼                            ▼
┌──────────────────────┐         ┌──────────────────────┐
│   CLIENT 1 (STB)     │         │   CLIENT 2 (STB)     │
│  ┌──────────────┐    │         │  ┌──────────────┐    │
│  │ Snapclient   │    │         │  │ Snapclient   │    │
│  └──────┬───────┘    │         │  └──────┬───────┘    │
│         │ ALSA       │         │         │ ALSA       │
│         ▼            │         │         ▼            │
│     [🔊 Speaker]     │         │     [🔊 Speaker]     │
└──────────────────────┘         └──────────────────────┘
```

---

## ✅ Prerequisite

<table>
  <tr>
    <th>Kategori</th>
    <th>Kebutuhan</th>
  </tr>
  <tr>
    <td>🖥️ <b>Perangkat Keras</b></td>
    <td>
      - 1x STB sebagai <b>Server</b> (MPD + Snapserver)<br/>
      - 2x STB sebagai <b>Client</b> (Snapclient)<br/>
      - Speaker atau USB Audio Device<br/>
      - Kabel LAN (server & client harus terhubung)
    </td>
  </tr>
  <tr>
    <td>💾 <b>Perangkat Lunak</b></td>
    <td>
      - Armbian (Linux OS)<br/>
      - MPD, Snapserver, Snapclient<br/>
      - ALSA sebagai backend audio<br/>
      - Python 3 + pip<br/>
      - FileZilla untuk transfer file via SFTP<br/>
      - OpenSSH server aktif di Armbian
    </td>
  </tr>
  <tr>
    <td>🌐 <b>Jaringan & Akses</b></td>
    <td>
      - Server dan client dalam jaringan yang sama<br/>
      - IP server sudah diketahui<br/>
      - Akses <b>root</b> atau <b>sudo</b><br/>
      - Port SSH/SFTP dapat diakses dari client
    </td>
  </tr>
</table>

---

## 📁 Struktur Project

```text
web-audio/
├── 📄 app.py            ← ✅ FILE UTAMA — jalankan ini
├── 📄 requirements.txt  ← Daftar dependency Python
├── 📁 templates/        ← File HTML halaman web
├── 📁 scripts/          ← File CSS, JS, gambar
├── 📄 README.md         ← Dokumentasi proyek
├── 📁 docs/             ← Dokumentasi detail konfigurasi dan panduan
│   ├── 📄 snapserver.md ← Panduan instalasi & konfigurasi Snapserver di Armbian Server
│   ├── 📄 snapclient.md ← Panduan instalasi & konfigurasi Snapclient di Armbian Client
│   └── 📄 code-guide.md ← Panduan lengkap isi kode app.py (fungsi, variabel, endpoint)
```

> [!IMPORTANT]
> Dalam folder project ini terdapat beberapa file script Python seperti `music.py` dan lainnya.
> **Abaikan semua file tersebut.** File yang perlu dijalankan hanyalah **`app.py`**.
> Jangan menjalankan script lain kecuali diminta secara khusus dalam dokumentasi ini.

---

## 🚀 Cara Menjalankan Web App di Armbian Server

**① Clone repository**

```bash
git clone https://github.com/username/repo-name.git
cd repo-name
```

**② Pindahkan folder ke `/opt/`**

```bash
mv web-audio /opt/web-audio
cd /opt/web-audio
```

**③ Install Python & aktifkan virtual environment**

```bash
sudo apt install python3 python3-venv python3-pip -y
source .venv/bin/activate
pip install -r requirements.txt
```

**④ Jalankan aplikasi**

```bash
python3 app.py
```

**⑤ Buka di browser**

```text
http://<IP_SERVER>:5000
```

---

## 📚 Dokumentasi

| No | Dokumen | Deskripsi |
| :-: | --- | --- |
| 1 | [🖥️ Konfigurasi Snapserver](./docs/snapserver.md) | Instalasi & konfigurasi MPD, transfer file via SFTP/FileZilla, Snapserver, dan Web App di Armbian Server |
| 2 | [🔊 Konfigurasi Snapclient](./docs/snapclient.md) | Instalasi & konfigurasi Snapclient beserta pengaturan audio di Armbian Client |
| 3 | [🗂️ Panduan Kode app.py](./docs/code-guide.md) | Peta seluruh fungsi dan endpoint di app.py — panduan jika ingin mengubah sesuatu di kode |

---

## ⚖️ Kelebihan & Kekurangan

<table>
  <tr>
    <th>✅ Kelebihan</th>
    <th>❌ Kekurangan</th>
  </tr>
  <tr>
    <td>Pemutaran audio dipusatkan di server</td>
    <td>Konfigurasi awal lebih kompleks</td>
  </tr>
  <tr>
    <td>Sinkronisasi audio ke banyak client</td>
    <td>Jika satu bagian salah, seluruh alur bisa gagal</td>
  </tr>
  <tr>
    <td>Queue lagu dikelola dari satu titik</td>
    <td>Sinkronisasi waktu & buffering sangat kritis</td>
  </tr>
  <tr>
    <td>Mendukung berbagai output device ALSA</td>
    <td>Integrasi MPD–Snapcast masih via FIFO (manual)</td>
  </tr>
  <tr>
    <td>Komponen dapat diuji secara terpisah</td>
    <td>Manajemen stream group bisa membingungkan</td>
  </tr>
</table>

---

## 🛠️ Teknologi yang Digunakan

<p align="center">
  <img src="https://img.shields.io/badge/Python_3-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/MPD-Music_Player_Daemon-1DB954?style=flat-square" />
  <img src="https://img.shields.io/badge/Snapcast-FF6B35?style=flat-square" />
  <img src="https://img.shields.io/badge/ALSA-Audio_Backend-009688?style=flat-square" />
  <img src="https://img.shields.io/badge/Armbian-Linux-E95420?style=flat-square&logo=linux&logoColor=white" />
  <img src="https://img.shields.io/badge/SFTP-FileZilla-3776AB?style=flat-square" />
</p>

---

<div align="center">

**Disusun oleh Alvin (Ipin)**

</div>