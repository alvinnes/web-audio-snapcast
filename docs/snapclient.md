# 🔊 Konfigurasi Snapclient

Dokumen ini menjelaskan langkah-langkah instalasi dan konfigurasi **Snapclient** di Armbian pada sisi client untuk menerima dan memutar audio dari Snapserver.

> ⬅️ [Kembali ke README](../README.md) | ⬅️ [Konfigurasi Snapserver](./snapserver.md)

***

## Langkah-Langkah Konfigurasi

### 1. Pasang Perangkat Audio

Sebelum memulai konfigurasi, pastikan **USB Audio Device** atau **speaker** yang akan digunakan sudah dipasang ke **STB/Armbian** terlebih dahulu.

> ⚠️ Langkah ini **penting** agar perangkat audio sudah terdeteksi oleh sistem dan tidak menimbulkan error saat pengujian.

***

### 2. Update Repository

Masuk ke sistem Armbian client melalui SSH atau akses langsung, lalu lakukan update repository:

```bash
apt-get update
```

Tunggu hingga proses selesai.

***

### 3. Instalasi Snapclient

Install paket snapclient:

```bash
apt-get install snapclient
```

Tunggu hingga proses instalasi selesai.

***

### 4. Konfigurasi Snapclient

Buka file konfigurasi default Snapclient:

```bash
nano /etc/default/snapclient
```

Fokus pada bagian **SNAPCLIENT_OPTS** dan sesuaikan seperti berikut:

```ini
SNAPCLIENT_OPTS="-h IP_SERVER -s default --soundcard USB"
```

Ganti `IP_SERVER` dengan IP dari Armbian Server kalian. Untuk mengecek IP server, jalankan perintah `ip a` di server.

> 💡 Contoh: jika IP server adalah `172.16.100.238`, maka:
> ```ini
> SNAPCLIENT_OPTS="-h 172.16.100.238 -s default --soundcard USB"
> ```

> ⚠️ **Konfigurasi ini wajib sama persis seperti di atas!**

Simpan dengan **CTRL + O**, lalu **Enter**.

***

### 5. Restart Snapclient

Restart service snapclient:

```bash
systemctl restart snapclient.service
```

Cek status snapclient untuk memastikan berjalan dengan benar:

```bash
systemctl status snapclient.service
```

Jika statusnya menunjukkan **active (running)**, berarti konfigurasi sudah berhasil.

***

### 6. Pengujian Suara dengan Alsamixer

Jalankan alsamixer untuk mengatur volume:

```bash
alsamixer
```

Setelah masuk ke alsamixer:

1. Tekan tombol **F6** di keyboard
2. Pilih perangkat audio **USB Audio Device**
3. Atur volume menggunakan tombol **panah atas/bawah** pada bagian bar **Speaker**
4. Setelah sesuai, keluar dengan menekan tombol **Esc**

***

### 7. Konfigurasi Auto-Restart Snapclient saat Booting

Agar Snapclient otomatis dijalankan ulang setelah Armbian booting, modifikasi berkas layanan bawaan:

```bash
sudo nano /lib/systemd/system/snapclient.service
```

Tambahkan atau sesuaikan konfigurasi berikut di bagian `[Service]`:

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

> ⚠️ **Konfigurasi ini wajib sama persis seperti pada gambar di dokumentasi asli!**

Simpan dengan **CTRL + O**, lalu **Enter**.

***

### 8. Reload dan Restart Service

Jalankan perintah berikut secara berurutan:

```bash
systemctl daemon-reload
systemctl restart snapclient.service
```

***

## ✅ Verifikasi Akhir

Dengan konfigurasi tersebut, speaker yang terhubung ke perangkat Armbian client dapat dikendalikan dari satu server secara terpusat.

Untuk memastikan sistem berjalan dengan baik, coba putar musik dari web app di browser:
```
http://<IP_SERVER>:5000
```

Jika audio terdengar di speaker client, maka konfigurasi Snapclient telah berhasil. 🎉

***

## 🔧 Troubleshooting

| Error | Kemungkinan Penyebab | Solusi |
|---|---|---|
| `No chunks available` | FIFO tidak aktif atau MPD belum memutar | Pastikan MPD sedang memutar, cek `mpc status` |
| `Failed to get chunk` | Buffering tidak stabil atau koneksi putus | Cek koneksi jaringan antara server dan client |
| `abs(age > 500)` | Sinkronisasi waktu buruk | Restart snapclient, pastikan jaringan stabil |
| Speaker tidak keluar suara | Salah device atau volume 0 | Cek alsamixer, pastikan USB Audio Device dipilih |
| Snapclient tidak konek ke server | IP server salah di konfigurasi | Cek ulang `SNAPCLIENT_OPTS` di `/etc/default/snapclient` |

***

> ⬅️ [Kembali ke README](../README.md)