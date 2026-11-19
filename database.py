"""Pengaturan database SQLite dan data awal aplikasi."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "pethotel.db"


@contextmanager
def get_connection():
    """Membuka koneksi yang otomatis commit, rollback, dan ditutup."""
    koneksi = sqlite3.connect(DB_PATH)
    koneksi.row_factory = sqlite3.Row
    koneksi.execute("PRAGMA foreign_keys = ON")
    try:
        yield koneksi
        koneksi.commit()
    except Exception:
        koneksi.rollback()
        raise
    finally:
        koneksi.close()


def init_db():
    """Membuat tabel dan memasukkan data contoh satu kali."""
    with get_connection() as koneksi:
        koneksi.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Pegawai'
            );
            CREATE TABLE IF NOT EXISTS owners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                telepon TEXT NOT NULL,
                alamat TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                nama TEXT NOT NULL,
                jenis TEXT NOT NULL CHECK (jenis IN ('Kucing', 'Anjing', 'Kelinci')),
                ras TEXT NOT NULL,
                umur INTEGER NOT NULL CHECK (umur >= 0),
                berat_kg REAL NOT NULL CHECK (berat_kg > 0),
                FOREIGN KEY (owner_id) REFERENCES owners(id) ON DELETE RESTRICT
            );
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                kategori TEXT NOT NULL,
                harga INTEGER NOT NULL CHECK (harga >= 0),
                deskripsi TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS cages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomor TEXT NOT NULL UNIQUE,
                jenis_hewan TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Kosong'
                    CHECK (status IN ('Kosong', 'Terisi'))
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                cage_id INTEGER NOT NULL,
                service_id INTEGER,
                tanggal_masuk TEXT NOT NULL,
                tanggal_keluar TEXT NOT NULL,
                lama_hari INTEGER NOT NULL CHECK (lama_hari > 0),
                biaya_menginap INTEGER NOT NULL,
                biaya_layanan INTEGER NOT NULL DEFAULT 0,
                total_biaya INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Menginap'
                    CHECK (status IN ('Menginap', 'Selesai')),
                status_layanan TEXT NOT NULL DEFAULT 'Belum Diproses',
                jumlah_bayar INTEGER,
                kembalian INTEGER,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE RESTRICT,
                FOREIGN KEY (cage_id) REFERENCES cages(id) ON DELETE RESTRICT,
                FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE SET NULL
            );
            """
        )
        if koneksi.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            koneksi.executemany(
                "INSERT INTO users (nama, username, password, role) VALUES (?, ?, ?, ?)",
                [
                    ("Administrator", "admin", "admin123", "Admin"),
                    ("Pegawai Contoh", "pegawai", "pegawai123", "Pegawai"),
                ],
            )
        if koneksi.execute("SELECT COUNT(*) FROM owners").fetchone()[0] == 0:
            koneksi.executemany(
                "INSERT INTO owners (nama, telepon, alamat) VALUES (?, ?, ?)",
                [
                    ("Ayu Lestari", "081234567890", "Jl. Melati No. 10"),
                    ("Budi Santoso", "082233445566", "Jl. Kenanga No. 5"),
                ],
            )
        if koneksi.execute("SELECT COUNT(*) FROM pets").fetchone()[0] == 0:
            koneksi.executemany(
                "INSERT INTO pets (owner_id, nama, jenis, ras, umur, berat_kg) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (1, "Milo", "Kucing", "Domestik", 2, 4.2),
                    (2, "Bruno", "Anjing", "Golden Retriever", 3, 18.0),
                    (1, "Mochi", "Kelinci", "Mini Rex", 1, 1.5),
                ],
            )
        if koneksi.execute("SELECT COUNT(*) FROM services").fetchone()[0] == 0:
            koneksi.executemany(
                "INSERT INTO services (nama, kategori, harga, deskripsi) "
                "VALUES (?, ?, ?, ?)",
                [
                    ("Mandi & Sisir", "Grooming", 50000, "Mandi, pengeringan, dan sisir."),
                    ("Potong Kuku", "Perawatan", 20000, "Perawatan kuku hewan."),
                    ("Paket Lengkap", "Grooming", 85000, "Mandi, sisir, dan potong kuku."),
                ],
            )
        if koneksi.execute("SELECT COUNT(*) FROM cages").fetchone()[0] == 0:
            koneksi.executemany(
                "INSERT INTO cages (nomor, jenis_hewan) VALUES (?, ?)",
                [
                    ("K-01", "Kucing"), ("K-02", "Kucing"),
                    ("A-01", "Anjing"), ("A-02", "Anjing"),
                    ("L-01", "Kelinci"), ("L-02", "Kelinci"),
                ],
            )
