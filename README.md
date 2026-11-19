# Pet Hotel & Salon

Aplikasi desktop sederhana untuk pencatatan penitipan dan grooming hewan. Aplikasi dibuat dengan Python dan hanya menggunakan pustaka standar (`tkinter`, `sqlite3`, `abc`).

## Menjalankan aplikasi

Pastikan Python 3 sudah terpasang, lalu jalankan dari folder proyek:

```text
python main.py
```

Database `pethotel.db` beserta data contoh dibuat otomatis saat aplikasi pertama kali dijalankan.

**Akun contoh**

- Admin: `admin` / `admin123`
- Pegawai: `pegawai` / `pegawai123`

Login modul pengelolaan pegawai hanya menerima akun Admin. Kredensial contoh ini ditujukan untuk demonstrasi tugas, bukan penggunaan produksi.

## Pembagian modul tim

1. `views/login_view.py` — login dan CRUD pegawai.
2. `views/hewan_view.py` — CRUD pemilik dan hewan.
3. `views/layanan_view.py` — CRUD paket grooming serta kandang.
4. `views/checkin_view.py` — check-in, alokasi kandang, dan perhitungan tarif.
5. `views/checkout_view.py` — status layanan, pembayaran, kembalian, dan rekap.

`main.py` adalah dashboard, sedangkan `database.py` mengelola skema serta data awal SQLite. Model OOP terpisah di folder `models/`.

## Konsep OOP

- **Encapsulation:** atribut model disimpan sebagai atribut privat dan diakses melalui getter/setter.
- **Inheritance dan abstraksi:** `HewanPeliharaan` adalah abstract base class, dengan turunan `Kucing`, `Anjing`, dan `Kelinci`.
- **Polymorphism:** setiap jenis hewan mengimplementasikan `hitung_biaya(harga_dasar, lama_hari)` dengan aturan tarifnya sendiri.
- Check-in memakai harga dasar penitipan Rp 30.000 per hari. Layanan grooming yang dipilih ditambahkan ke total biaya.
