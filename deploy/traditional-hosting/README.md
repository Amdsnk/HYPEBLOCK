# Deploy HYPEBLOCK ke hosting tradisional

Panduan ini ditujukan untuk cPanel seperti Jagoan Hosting. HYPEBLOCK terdiri
dari:

- **Frontend React** yang di-upload sebagai file statis ke `public_html`.
- **API FastAPI** yang membutuhkan fitur **Setup Python App / Application
  Manager / Passenger**.
- **Data waitlist** di file JSON lokal, bukan MongoDB.

## Sebelum mulai: cek paket hosting

Di cPanel, cari menu **Setup Python App**, **Python Selector**, atau
**Application Manager**.

- Jika menu itu tersedia, ikuti bagian **A — Hosting Python**.
- Jika hanya ada File Manager/PHP, ikuti bagian **B — PHP-only**. Frontend
  tetap bisa dipasang, tetapi API tidak dapat berjalan di paket tersebut.

Jangan mengubah backend menjadi PHP hanya untuk memaksa shared hosting.
Itu akan menjadi penulisan ulang aplikasi dan berisiko merusak fitur gallery,
rarity, wallpaper, waitlist, dan admin.

## A — Hosting Python/Passenger (jalur yang disarankan)

Contoh alamat:

- Website: `https://hypeblock.amdsnk.id`
- API: `https://api.hypeblock.amdsnk.id`

Nama subdomain boleh diganti. Yang penting website dan API memakai HTTPS.

### 1. Buat dua subdomain di cPanel

Buat:

1. subdomain website, misalnya `hypeblock.amdsnk.id`;
2. subdomain API, misalnya `api.hypeblock.amdsnk.id`.

Pastikan keduanya mengarah ke hosting yang sama dan SSL aktif. Jika domain
dikelola di tempat lain, buat record DNS `A` atau `CNAME` sesuai petunjuk
Jagoan Hosting.

### 2. Upload kode backend

Upload seluruh folder `backend/` ke folder pribadi di luar `public_html`,
misalnya:

```text
/home/USERNAME/hypeblock/backend/
```

Jangan menaruh `backend/.env` atau `backend/data/store.json` di
`public_html`; keduanya berisi konfigurasi/data dan tidak boleh dapat diunduh
sebagai file publik.

### 3. Buat Python App di cPanel

Di **Setup Python App**:

1. pilih Python 3.10 atau yang lebih baru;
2. set **Application root** ke folder `backend`;
3. set **Application URL** ke `api.hypeblock.amdsnk.id`;
4. set **Startup file** ke `passenger_wsgi.py`;
5. set **Entry point** ke `application`;
6. simpan, lalu buka **Enter to the virtual environment** atau terminal app.

Jalankan dari virtual environment aplikasi:

```bash
pip install -r requirements-hosting.txt
```

Setelah itu restart aplikasi dari cPanel. Jika tersedia tombol **Restart**,
gunakan tombol tersebut setelah setiap perubahan backend.

### 4. Tambahkan environment variables backend

Buat file `backend/.env` di server. Mulai dari `backend/.env.example` dan
isi seperti ini:

```dotenv
ADMIN_KEY=ganti-dengan-kunci-admin-panjang-dan-acak
APP_URL=https://api.hypeblock.amdsnk.id
CORS_ORIGINS=https://hypeblock.amdsnk.id
HYPEBLOCK_DATA_FILE=/home/USERNAME/private/hypeblock/store.json
```

Buat folder data jika belum ada:

```bash
mkdir -p /home/USERNAME/private/hypeblock
```

Simpan backup file `store.json` secara berkala. File itu berisi waitlist
yang dikumpulkan dari website.

### 5. Build frontend dengan alamat API

Build dilakukan di komputer lokal atau environment yang memiliki Node.js dan
Yarn. Dari root project:

```bash
cd frontend
cp .env.example .env
```

Ubah `frontend/.env` menjadi:

```dotenv
REACT_APP_BACKEND_URL=https://api.hypeblock.amdsnk.id
```

Lalu jalankan:

```bash
yarn install --frozen-lockfile
yarn build
```

### 6. Upload frontend

Upload **isi** folder `frontend/build/` ke document root website, biasanya
`public_html/` atau folder document root subdomain
`hypeblock.amdsnk.id`.

File `.htaccess` untuk route React seperti `/admin` sudah ikut tersalin dari
`frontend/public/.htaccess`. Jangan menghapusnya.

### 7. Uji website dan admin

Buka:

```text
https://api.hypeblock.amdsnk.id/api/
https://hypeblock.amdsnk.id/
https://hypeblock.amdsnk.id/admin
```

Halaman API harus menampilkan `HYPEBLOCK API online`. Di `/admin`, masukkan
nilai `ADMIN_KEY` dari file `.env`.

## B — Jika paket hanya PHP-only

Paket PHP-only tidak dapat menjalankan `backend/server.py` secara terus-menerus.
Dalam kondisi ini:

1. build frontend seperti pada langkah A.5;
2. upload isi `frontend/build/` ke `public_html`;
3. jalankan backend di hosting Python/VPS terpisah;
4. isi `REACT_APP_BACKEND_URL` dengan URL backend tersebut;
5. build ulang frontend dan upload ulang isinya.

Tanpa backend terpisah, website akan terbuka tetapi gallery, stats, trait lab,
waitlist, wallpaper, dan halaman admin tidak akan berfungsi.

## Checklist keamanan

- Ganti `ADMIN_KEY`; jangan memakai contoh atau nilai bawaan.
- Jangan upload `.env` ke `public_html`.
- Jangan membuka `backend/data/store.json` melalui URL publik.
- Aktifkan SSL untuk website dan API.
- Backup `store.json` dan folder `backend/generated/`.
- Setelah mengganti alamat API, build ulang frontend.