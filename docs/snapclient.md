<div align="center">

# 🔊 Konfigurasi Snapclient

<p>
  <img src="https://img.shields.io/badge/Role-Client-8A2BE2?style=flat-square" />
  <img src="https://img.shields.io/badge/OS-Armbian-E95420?style=flat-square&logo=linux&logoColor=white" />
  <img src="https://img.shields.io/badge/Service-Snapclient-FF6B35?style=flat-square" />
</p>

</div>

> ⬅️ [Kembali ke README](../README.md) &nbsp;|&nbsp; ⬅️ [Konfigurasi Snapserver](./snapserver.md)

***

## 📋 Ringkasan Langkah

```
① Pasang USB Audio  →  ② Update Repo  →  ③ Install Snapclient
        ↓
④ Konfigurasi /etc/default/snapclient  →  ⑤ Restart Service
        ↓
⑥ Tes Suara (alsamixer)  →  ⑦ Konfigurasi Auto-Restart  ✅
```

***

## Langkah-Langkah Konfigurasi

### 1️⃣ Pasang Perangkat Audio

Pastikan **USB Audio Device** atau **speaker** sudah dipasang ke **STB/Armbian** terlebih dahulu sebelum memulai konfigurasi.

> [!CAUTION]
> Langkah ini **wajib dilakukan lebih dulu** agar perangkat audio sudah terdeteksi oleh sistem
> dan tidak menimbulkan error saat pengujian nanti.

***

### 2️⃣ Update Repository

Masuk ke Armbian client melalui SSH atau akses langsung:

```bash
apt-get update
```

Tunggu hingga proses selesai.

***

### 3️⃣ Instalasi Snapclient

```bash
apt-get install snapclient
```

Tunggu hingga proses instalasi selesai.

***

### 4️⃣ Konfigurasi Snapclient

Buka file konfigurasi default:

```bash
nano /etc/default/snapclient
```

Fokus pada bagian **`SNAPCLIENT_OPTS`** dan sesuaikan:

```ini
SNAPCLIENT_OPTS="-h IP_SERVER -s default --soundcard USB"
```

Ganti `IP_SERVER` dengan IP Armbian Server kalian. Untuk mengecek IP server, ketik `ip a` di server.

> [!TIP]
> **Contoh** — jika IP server adalah `172.16.100.238`:
> ```ini
> SNAPCLIENT_OPTS="-h 172.16.100.238 -s default --soundcard USB"
> ```

> [!CAUTION]
> **Konfigurasi ini wajib sama persis seperti di atas!**

Simpan dengan **`CTRL + O`** → **`Enter`**.

***

### 5️⃣ Restart & Cek Status Snapclient

Restart service:

```bash
systemctl restart snapclient.service
```

Cek status untuk memastikan berjalan dengan benar:

```bash
systemctl status snapclient.service
```

Hasil yang diharapkan: status menunjukkan **`active (running)`** ✅

***

### 6️⃣ Pengujian Suara dengan Alsamixer

Jalankan alsamixer:

```bash
alsamixer
```

Ikuti langkah berikut di dalam alsamixer:

| Langkah | Aksi |
|:-------:|------|
| 1 | Tekan tombol **`F6`** di keyboard |
| 2 | Pilih perangkat **`USB Audio Device`** |
| 3 | Atur volume menggunakan **tombol panah atas/bawah** pada bar **Speaker** |
| 4 | Setelah selesai, tekan **`Esc`** untuk keluar |

***

### 7️⃣ Konfigurasi Auto-Restart saat Booting

Agar Snapclient otomatis restart setelah Armbian booting (berguna jika USB Audio dilepas-pasang), modifikasi file service:

```bash
sudo nano /lib/systemd/system/snapclient.service
```

Sesuaikan konfigurasi menjadi seperti berikut:

```ini
[Unit]
Description=Snapcast client
Documentation=man:snapclient(1)
Wants=avahi-daemon.service
After=network-online.target time-sync.target sound.target avahi-daemon.service

[Service]
EnvironmentFile=-/etc/default/snapclient
ExecStart=/usr/bin/snapclient $SNAPCLIENT_OPTS
Restart=always
RestartSec=5
User=snapclient

[Install]
WantedBy=multi-user.target
```

> [!CAUTION]
> **Konfigurasi ini wajib sama persis seperti pada gambar di dokumentasi asli!**

Simpan dengan **`CTRL + O`** → **`Enter`**.

***

### 8️⃣ Reload & Restart Service

Jalankan perintah berikut secara **berurutan**:

```bash
systemctl daemon-reload
systemctl restart snapclient.service
```

***

## ✅ Verifikasi Akhir

Speaker yang terhubung ke Armbian client kini dapat dikendalikan dari server secara terpusat.

Buka browser dan akses web app untuk menguji:

```
http://<IP_SERVER>:5000
```

Jika audio terdengar di speaker client saat lagu diputar dari web — konfigurasi berhasil! 🎉

***

## 🔧 Troubleshooting

| Error | Kemungkinan Penyebab | Solusi |
|-------|----------------------|--------|
| `No chunks available` | FIFO tidak aktif atau MPD belum memutar | Pastikan MPD memutar lagu, cek dengan `mpc status` |
| `Failed to get chunk` | Buffering tidak stabil atau koneksi terputus | Periksa koneksi LAN server dan client |
| `abs(age > 500)` | Sinkronisasi waktu buruk | Restart snapclient, pastikan jaringan stabil |
| Speaker tidak keluar suara | Salah device atau volume 0 | Buka alsamixer, pilih USB Audio Device |
| Snapclient tidak konek ke server | IP server salah di konfigurasi | Cek `SNAPCLIENT_OPTS` di `/etc/default/snapclient` |
| Snapclient berhenti setelah reboot | Auto-restart belum dikonfigurasi | Lakukan langkah 7 di atas |

***

<div align="center">

> ✅ **Konfigurasi Snapclient selesai!**
>
> Sistem audio streaming multi-room sudah siap digunakan.

⬅️ [Kembali ke README](../README.md)

</div>