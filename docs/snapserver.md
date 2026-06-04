# 🖥️ Konfigurasi Snapserver

<p>
  <img src="https://img.shields.io/badge/Role-Server-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/OS-Armbian-E95420?style=for-the-badge&logo=linux&logoColor=white" />
  <img src="https://img.shields.io/badge/Service-MPD%20%2B%20Snapserver-1DB954?style=for-the-badge" />
</p>

<p><i>Panduan konfigurasi sisi server — MPD, Snapserver, dan Web App di atas Armbian</i></p>

</div>

<br>

> ⬅️ [Kembali ke README](../README.md)

---

## 📋 Ringkasan Langkah

```text
① Update Repo  →  ② Install Paket + Buat Direktori  →  ③ Set Permission
      ↓
④ Install OpenSSH  →  ⑤ Transfer Musik via SFTP (FileZilla)  →  ⑥ Konfigurasi MPD
      ↓
⑦ Restart MPD  →  ⑧ Konfigurasi Snapserver  →  ⑨ Restart Snapserver
      ↓
⑩ Install MPC + Test Playback  →  ⑪ Konfigurasi Paging Service
      ↓
⑫ Konfigurasi Music Service  →  ⑬ Clone & Jalankan Web App  ✅
```

---

## Langkah-Langkah Konfigurasi

### 1️⃣ Update Repository

Setelah Armbian terpasang pada server dan client, konfigurasi dimulai dari sisi **server** terlebih dahulu. Pada tahap awal, **masuk** ke sistem Armbian menggunakan user **Root** melalui **SSH** atau **akses langsung** sesuai kebutuhan. Setelah berhasil masuk, lakukan **pembaruan repository** dengan perintah berikut, lalu tunggu hingga proses selesai.

```bash
apt-get update
```

---

### 2️⃣ Instalasi Paket dan Buat Direktori Musik

Setelah repository diperbarui, **instal paket** yang dibutuhkan untuk menjalankan MPD dan Snapserver dengan perintah berikut:

```bash
apt-get install mpd snapserver
```

Setelah proses instalasi selesai, buat direktori khusus untuk menyimpan file musik yang akan diputar oleh server. Pada contoh ini, direktori yang digunakan adalah **/etc/music**, namun direktori lain juga bisa digunakan selama **konsisten** dengan konfigurasi MPD. **Tapi jika tidak ingin pusing samakan saja dengan punya saya**.

```bash
mkdir /etc/music
```

---

### 3️⃣ Atur Permission Direktori Musik

Setelah direktori dibuat, atur **permission** agar direktori tersebut dapat **diakses** oleh service MPD dengan benar. Pengaturan hak akses ini penting agar MPD dapat membaca file musik tanpa kendala.

> [!CAUTION]
> **PERINTAHNYA WAJIB SAMA DENGAN PUNYA SAYA!!**

```bash
chown -R mpd:audio /etc/music
chmod -R 775 /etc/music
```

---

### 4️⃣ Persiapan Transfer File via SFTP (FileZilla)

Selanjutnya, **pindahkan** file musik dari laptop ke server. Untuk mempermudah proses transfer file, digunakan **FileZilla** dengan protokol **SFTP** sebagai media transfer. SFTP lebih stabil dan aman dibanding Samba, serta tidak memerlukan konfigurasi tambahan di sisi server karena berjalan di atas SSH yang sudah aktif di Armbian secara default.

Sebelum melakukan transfer, pastikan service **SSH** sudah berjalan di Armbian Server. Cek statusnya dengan perintah berikut:

```bash
systemctl status ssh
```

Jika status menunjukkan **active (running)**, maka SSH sudah siap digunakan. Jika belum aktif, jalankan perintah berikut untuk mengaktifkannya:

```bash
systemctl enable ssh
systemctl start ssh
```

> [!NOTE]
> Armbian umumnya sudah mengaktifkan SSH secara default. Pastikan juga kalian sudah mengetahui **IP address** dari Armbian Server dengan perintah `ip a`.

Jika belum memiliki **FileZilla**, download terlebih dahulu di:

👉 [**https://filezilla-project.org/download.php**](https://filezilla-project.org/download.php)

---

### 5️⃣ Transfer File Musik ke Server via FileZilla

Setelah FileZilla terinstall di Laptop atau Komputer anda, buka aplikasi FileZilla dan isi kolom koneksi di bagian atas seperti berikut:

| Field | Nilai |
|:------|:------|
| **Host** | `sftp://IP_SERVER` (contoh: `sftp://172.16.100.178`) |
| **Username** | `root` |
| **Password** | Password root Armbian kalian |
| **Port** | `22` |

Setelah diisi, klik tombol **Quickconnect**. Jika berhasil terhubung, panel sebelah kanan akan menampilkan isi folder dari Armbian Server.

Navigasikan panel kanan ke direktori **/etc/music**, kemudian **drag and drop** file musik dari panel kiri (Laptop) ke panel kanan (Server). Tunggu hingga proses transfer selesai.

> [!TIP]
> Jika muncul peringatan **"Unknown host key"** saat pertama kali konek, klik **OK** atau **Always trust** untuk melanjutkan.

---

### 6️⃣ Konfigurasi MPD

Setelah file musik berhasil dipindahkan ke server, masuk kembali ke Armbian Server untuk melakukan konfigurasi MPD. Buka file konfigurasi MPD dengan perintah berikut:

```bash
nano /etc/mpd.conf
```

Pada file ini, sesuaikan pengaturan agar sesuai dengan yang ada pada gambar berikut. Jika ada baris yang masih diberi **tanda #**, hapus tanda tersebut pada bagian yang memang perlu diaktifkan. Setelah selesai, simpan konfigurasi dengan **menekan CTRL + O, lalu tekan Enter**.

> [!CAUTION]
> **KONFIGURASINYA WAJIB SAMA SEPERTI YANG ADA DI GAMBAR!!**

```ini
music_directory    "/etc/music"
playlist_directory "/var/lib/mpd/playlists"
db_file            "/var/lib/mpd/database"
log_file           "/var/log/mpd/mpd.log"
pid_file           "/run/mpd/pid"
state_file         "/var/lib/mpd/state"

bind_to_address    "127.0.0.1"

audio_output {
    type       "fifo"
    name       "snapcast"
    path       "/tmp/snapfifo"
    format     "48000:16:2"
}
```

---

### 7️⃣ Restart MPD

Setelah konfigurasi, selanjutnya **restart** MPD dengan perintah berikut:

```bash
systemctl restart mpd.service
```

---

### 8️⃣ Konfigurasi Snapserver

Langkah berikutnya adalah mengonfigurasi Snapserver. Buka file konfigurasi Snapserver dengan perintah berikut:

```bash
nano /etc/snapserver.conf
```

Pada file ini, sesuaikan konfigurasi stream agar Snapserver membaca audio dari source yang benar. Karena urutan konfigurasi pada file ini tidak selalu sama, maka perlu mencari bagian yang sesuai satu per satu. Jika ada tanda # pada baris yang diperlukan, hapus tanda tersebut.

> [!CAUTION]
> **KONFIGURASINYA WAJIB SAMA SEPERTI YANG ADA DI GAMBAR!!**

**📡 Bagian `[stream]`** — sumber audio dari FIFO pipe MPD:

```ini
[stream]
source = pipe:///tmp/snapfifo?name=MPD&mode=read&sampleformat=48000:16:2
source = tcp://127.0.0.1:1234?name=Paging&sampleformat=44100:16:1
source = meta:///MPD/Paging?name=Auto_Paging&mode=prioritized
```

**🌐 Bagian `[http]`** — mengaktifkan JSON-RPC via HTTP untuk kontrol web:

```ini
[http]
enabled = true
port = 1780
```

**🔌 Bagian `[tcp]`** — mengaktifkan JSON-RPC via TCP untuk kontrol socket:

```ini
[tcp]
enabled = true
port = 1705
```

---

### 9️⃣ Simpan dan Restart Snapserver

Setelah konfigurasi Snapserver selesai, simpan file dengan menekan **CTRL + O, lalu tekan Enter**. Setelah itu restart Snapserver dengan perintah berikut:

```bash
systemctl restart snapserver
```

---

### 🔟 Install MPC dan Test Playback

Setelah MPD dan Snapserver berhasil dikonfigurasi, lakukan pengujian dengan **menambahkan** musik ke MPD. Sebelum itu, instal paket **mpc** terlebih dahulu:

```bash
apt-get install mpc
```

Setelah terinstall, selanjutnya ketik perintah satu-satu **secara urut** mulai dari atas hingga bawah seperti berikut:

```bash
mpc update
mpc ls
mpc add /
mpc play
```

> [!IMPORTANT]
> Kalian **wajib** memasukkan perintah dari **mpc update sampai mpc play** secara berurutan dari atas ke bawah.

Jika lagu sudah diputar tetapi speaker belum mengeluarkan suara, maka tahap berikutnya adalah melakukan konfigurasi pada sisi **Snapclient** di Armbian Client.

---

### 1️⃣1️⃣ Konfigurasi Service Paging (audio-paging.service)

Setelah tes menggunakan perintah `mpc play` sudah berhasil memutar musik, selanjutnya kita akan mulai konfigurasi untuk **paging**. **Paging** (sering juga disebut *Public Address System* atau PA System) adalah **sistem penyiaran pengumuman suara satu arah** dari sebuah titik pusat kontrol (mikrofon/server) ke satu atau banyak titik speaker (client) secara bersamaan.

Untuk konfigurasi paging, pertama kita akan membuat service yang akan dijalankan terus menerus untuk mengaktifkan fitur paging. Ketik perintah berikut:

```bash
nano /etc/systemd/system/audio-paging.service
```

Isi konfigurasinya seperti berikut:

> [!CAUTION]
> **KONFIGURASINYA WAJIB SAMA SEPERTI PADA GAMBAR!**

```ini
[Unit]
Description=Running Paging
After=network-online.target

[Service]
ExecStart=/bin/bash -c "arecord -D plughw:CARD=Device,DEV=0 -r 44100 -f S16_LE -c 1 | nc 127.0.0.1 1234"
Restart=always
RestartSec=5
User=root
Group=root
Type=simple
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=paging

[Install]
WantedBy=multi-user.target
```

Setelah dikonfigurasi seperti pada gambar, selanjutnya klik tombol **CTRL + O**, lalu **Enter** untuk menyimpan file konfigurasi.

Setelah mengkonfigurasi file **audio-paging.service**, selanjutnya **restart** system dan **aktifkan** service audio-paging yang baru saja kita buat. Ketik perintah secara berurutan seperti berikut:

```bash
systemctl daemon-reload
systemctl enable audio-paging.service
systemctl start audio-paging.service
```

---

### 1️⃣2️⃣ Konfigurasi Service Musik Background (audio-music.service)

Setelah mengaktifkan service audio-paging, selanjutnya kita akan membuat satu service lagi untuk menjalankan musik di latar belakang (daemon). Cara untuk membuatnya sama seperti membuat service audio-paging, yang berbeda hanya nama file dan isi dari konfigurasinya. Untuk service ini beri nama **audio-music.service**:

```bash
nano /etc/systemd/system/audio-music.service
```

> [!CAUTION]
> **KONFIGURASINYA WAJIB SAMA SEPERTI PADA GAMBAR!**

```ini
[Unit]
Description=Automated MPD Music Player Service
After=network.target mpd.service snapserver.service
Requires=mpd.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/bash -c "mpc update && mpc clear && mpc add / && mpc repeat on && mpc play"
ExecStop=/usr/bin/mpc stop

[Install]
WantedBy=multi-user.target
```

Setelah dikonfigurasi, selanjutnya restart system dan aktifkan service yang baru saja kita buat seperti sebelumnya:

```bash
systemctl daemon-reload
systemctl enable audio-music.service
systemctl start audio-music.service
```

---

### 1️⃣3️⃣ Integrasi dengan Web App

Setelah membuat audio-paging.service dan audio-music.service, selanjutnya kita akan mengintegrasikan MPD dan Snapserver kita dengan website, agar audionya bisa dikontrol dari website.

Sebelum mengintegrasikan web, kita harus meng-clone terlebih dahulu repository website yang sudah disediakan. Jika kalian ingin membuat website sendiri bebas, tapi kalau tidak mau pusing gunakan repository saya saja.

#### 📦 Install Git Terlebih Dahulu

Sebelum melakukan clone repository, pastikan Git sudah terinstall di sistem operasi Armbian.

Kalau belum, install Git terlebih dahulu dengan perintah berikut:

```bash
apt-get install git -y
```

Jika kalian ingin penjelasan yang lebih lengkap tentang cara install Git di Debian, kalian bisa mengarah ke dokumentasi berikut:

[**Cara Install Git di Debian**](https://www.digitalocean.com/community/tutorials/how-to-install-git-on-debian-10)

#### 🔁 Clone Repository Website

Setelah Git terinstall, selanjutnya clone repository website ke dalam Armbian kita melalui terminal:

```bash
cd /opt
git clone https://github.com/alvinnes/web-audio-snapcast.git
```

Setelah repository berhasil di-clone, selanjutnya masuk ke dalam folder hasil clone tersebut:

```bash
cd /opt/web-audio-snapcast
```

Kalau nama folder hasil clone berbeda, sesuaikan dengan nama repository kalian.

Setelah repository berhasil di-clone, selanjutnya pindahkan folder website tadi ke dalam folder opt jika memang sebelumnya masih berada di folder lain. Kalau repository sudah langsung di-clone ke `/opt`, maka langkah pemindahan ini bisa diabaikan.

Sebelum menjalankan aplikasi, pastikan bahasa pemrograman **Python 3** beserta modul environment-nya telah terpasang di sistem operasi:

```bash
sudo apt install python3 python3-venv python3-pip -y
```

Aktifkan virtual environment:

```bash
source .venv/bin/activate
```

> [!IMPORTANT]
> Di dalam folder project terdapat beberapa file script Python seperti `music.py` dan lainnya.
> **Abaikan semua file tersebut.** Satu-satunya file yang perlu dijalankan adalah **`app.py`**.

Terakhir, jalankan layanan website:

```bash
python3 app.py
```

Setelah mengetik perintah tersebut, akan muncul tulisan seperti berikut:

```text
* Running on http://172.16.100.178:5000
```

Setelah muncul tampilan seperti itu, fokus ke bagian **Running on http://172.16.100.178:5000**. Buka browser di laptop anda, lalu masukkan IP tersebut ke pencarian, maka nanti akan muncul tampilan website.

Setelah muncul tampilan website, selanjutnya coba kalian tes **upload lagu**, **play lagu**, dan **fitur-fitur lainnya**. Jika semua fitur sudah bisa berjalan maka konfigurasi Snapserver sudah selesai sampai disini saja.

---

<div align="center">

> ✅ **Konfigurasi Snapserver selesai!**
>
> Lanjutkan ke **[🔊 Konfigurasi Snapclient →](./snapclient.md)**

</div>