<div align="center">

# 🔊 Konfigurasi Snapclient

<p>
  <img src="https://img.shields.io/badge/Role-Client-8A2BE2?style=flat-square" />
  <img src="https://img.shields.io/badge/OS-Armbian-E95420?style=flat-square&logo=linux&logoColor=white" />
  <img src="https://img.shields.io/badge/Service-Snapclient-FF6B35?style=flat-square" />
</p>

</div>

> ⬅️ [Kembali ke README](../README.md) &nbsp;|&nbsp; ⬅️ [Konfigurasi Snapserver](./snapserver.md)

---

## 📋 Ringkasan Langkah

```
① Pasang USB Audio  →  ② Update Repo  →  ③ Install Snapclient
        ↓
④ Konfigurasi /etc/default/snapclient  →  ⑤ Restart & Cek Status
        ↓
⑥ Pengujian Suara (alsamixer)  →  ⑦ Konfigurasi Auto-Restart
        ↓
⑧ Reload & Restart Service  ✅
```

---

## Langkah-Langkah Konfigurasi

### 1️⃣ Pasang Perangkat Audio

Sebelum memulai konfigurasi, pastikan **USB Audio Device** atau **speaker** yang akan digunakan sudah dipasang ke **STB/Armbian** terlebih dahulu. Langkah ini **penting** agar saat proses konfigurasi dilakukan, perangkat audio sudah terdeteksi oleh sistem dan **tidak menimbulkan error** pada saat pengujian.

---

### 2️⃣ Update Repository

Setelah perangkat audio terpasang, masuk ke sistem Armbian client, baik **secara langsung** maupun **melalui SSH**. Setelah berhasil masuk, lakukan update repository terlebih dahulu agar daftar paket yang tersedia pada sistem berada dalam kondisi terbaru dengan menjalankan perintah berikut, lalu tunggu hingga proses update selesai.

```bash
apt-get update
```

---

### 3️⃣ Instalasi Snapclient

Setelah proses update selesai, langkah berikutnya adalah menginstal paket **snapclient**. Instalasi dapat dilakukan dengan perintah berikut, setelah itu tunggu hingga proses instalasi selesai.

```bash
apt-get install snapclient
```

---

### 4️⃣ Konfigurasi Snapclient

Jika proses instalasi telah selesai, selanjutnya **buka file** konfigurasi default Snapclient. Pada sistem Debian atau Armbian, file konfigurasi service ini umumnya berada di **/etc/default/snapclient**. Masuk ke file konfigurasi dengan perintah berikut:

```bash
nano /etc/default/snapclient
```

Setelah masuk ke file konfigurasi, fokus utama ada pada bagian **SNAPCLIENT_OPTS**. Pada bagian ini, parameter Snapclient dapat disesuaikan agar client terhubung ke Snapserver dan menggunakan device audio yang benar.

> [!CAUTION]
> **KONFIGURASI INI WAJIB SAMA DENGAN GAMBAR!!**

```ini
SNAPCLIENT_OPTS="-h IP_SERVER -p 1704 -s default:CARD=Device --stream Auto_Paging"
```

Setelah dikonfigurasi, klik tombol **CTRL + O, lalu Enter** untuk menyimpan perubahan file konfigurasi. Untuk bagian **IP_SERVER** kalian bisa cek sendiri dengan perintah `ip a` di server kalian, IP nya berapa. Kalau punya saya kebetulan mendapat IP **172.16.100.238**.

---

### 5️⃣ Restart dan Cek Status Snapclient

Setelah mengkonfigurasi, sekarang kita perlu **merestart service** snapclient nya. Ketik perintah berikut untuk merestart snapclient:

```bash
systemctl restart snapclient.service
```

Setelah direstart, selanjutnya lihat **status snapclient** nya dengan perintah berikut. Jika hasilnya sudah menunjukkan **active (running)** maka semuanya sudah aman.

```bash
systemctl status snapclient.service
```

---

### 6️⃣ Pengujian Suara dengan Alsamixer

Jika status nya sudah aktif, selanjutnya kita akan melanjutkan ke tahap **pengujian suara**. Untuk pengujian suara bisa ketik perintah berikut:

```bash
alsamixer
```

Nanti akan muncul tampilan alsamixer di terminal.

Setelah masuk ke alsamixer, selanjutnya klik tombol **F6** di keyboard, lalu pilih perangkat audio kalian, yaitu **USB Audio Device**.

Setelah memilih perangkat audio kalian, akan muncul tampilan equalizer. Hal yang perlu kalian perhatikan adalah di bagian bar **Speaker**, disitulah kalian akan mengatur volume untuk speaker kalian. Kalian bisa menggunakan **tombol panah atas dan bawah** di keyboard untuk mengatur volumenya. Setelah menyesuaikan volume, selanjutnya kalian bisa keluar dari alsamixer dengan cara menekan tombol **Esc** di keyboard.

---

### 7️⃣ Konfigurasi Auto-Restart Snapclient saat Booting

Pada tahap ini, konfigurasi Snapclient sebenarnya telah selesai. Namun, masih ada **satu langkah tambahan** yang dapat dilakukan untuk meningkatkan stabilitas layanan, yaitu membuat **Snapclient** otomatis dijalankan ulang setelah Armbian melakukan booting.

Langkah ini berguna untuk meminimalkan **kemungkinan error**, terutama ketika perangkat audio **dilepas lalu dipasang** kembali, karena pada kondisi tertentu Snapclient dapat berhenti bekerja dan perlu direstart **secara manual**. Oleh karena itu, diperlukan mekanisme restart otomatis saat sistem selesai booting.

Agar layanan dapat pulih otomatis saat terjadi gangguan koneksi atau perangkat keras, modifikasi berkas layanan bawaan dengan mengetik perintah berikut:

```bash
sudo nano /lib/systemd/system/snapclient.service
```

Di dalam berkas tersebut, samakan konfigurasinya seperti berikut:

> [!CAUTION]
> **KONFIGURASINYA WAJIB SAMA SEPERTI PADA GAMBAR!**

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

Jika sudah dikonfigurasi seperti itu, selanjutnya klik tombol **CTRL + O, lalu Enter** untuk menyimpan file konfigurasi.

---

### 8️⃣ Reload dan Restart Service

Selanjutnya restart system dan layanan snapclient dengan perintah **systemctl daemon-reload** dan **systemctl restart snapclient.service** seperti berikut:

```bash
systemctl daemon-reload
systemctl restart snapclient.service
```

Dengan konfigurasi tersebut, speaker yang terhubung ke perangkat Armbian dapat dikendalikan dari satu server secara terpusat.

---

## 🔧 Troubleshooting

| Error | Kemungkinan Penyebab | Solusi |
|-------|----------------------|--------|
| `No chunks available` | FIFO tidak aktif atau MPD belum memutar | Pastikan MPD sedang memutar, cek `mpc status` |
| `Failed to get chunk` | Buffering tidak stabil atau koneksi terputus | Periksa koneksi LAN server dan client |
| `abs(age > 500)` | Sinkronisasi waktu buruk | Restart snapclient, pastikan jaringan stabil |
| Speaker tidak keluar suara | Salah device atau volume 0 | Buka alsamixer, pilih USB Audio Device |
| Snapclient tidak konek ke server | IP server salah di konfigurasi | Cek `SNAPCLIENT_OPTS` di `/etc/default/snapclient` |
| Snapclient berhenti setelah reboot | Auto-restart belum dikonfigurasi | Lakukan langkah 7 di atas |

---

<div align="center">

> ✅ **Konfigurasi Snapclient selesai!**
>
> Sistem audio streaming multi-room sudah siap digunakan. 🎉

⬅️ [Kembali ke README](../README.md)

</div>
