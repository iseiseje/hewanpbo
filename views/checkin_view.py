"""Modul Anggota 4: transaksi check-in dan perhitungan polymorphism."""

import sqlite3
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import messagebox, ttk

from database import get_connection
from models.hewan import buat_model_hewan
from views.common import buat_jendela, buat_tabel, format_rupiah, kosongkan_tabel


HARGA_DASAR_HARI = 30000


class CheckinView:
    def __init__(self, parent):
        self.jendela = buat_jendela(parent, "Transaksi Check-In", "1000x670")
        self.pet_map = {}
        self.kandang_map = {}
        self.layanan_map = {}
        self._buat_form()
        self._buat_daftar()
        self._muat_pilihan()
        self._muat_transaksi()

    def _buat_form(self):
        form = ttk.LabelFrame(self.jendela, text="Data check-in", padding=14)
        form.pack(fill="x", padx=16, pady=16)
        self.pet_combo = ttk.Combobox(form, state="readonly", width=34)
        self.kandang_combo = ttk.Combobox(form, state="readonly", width=24)
        self.layanan_combo = ttk.Combobox(form, state="readonly", width=32)
        hari_ini = date.today()
        self.masuk_var = tk.StringVar(value=hari_ini.isoformat())
        self.keluar_var = tk.StringVar(value=(hari_ini + timedelta(days=1)).isoformat())
        fields = (
            ("Hewan", self.pet_combo), ("Kandang kosong", self.kandang_combo),
            ("Paket layanan (opsional)", self.layanan_combo),
            ("Tanggal masuk (YYYY-MM-DD)", ttk.Entry(form, textvariable=self.masuk_var, width=22)),
            ("Tanggal keluar (YYYY-MM-DD)", ttk.Entry(form, textvariable=self.keluar_var, width=22)),
        )
        for indeks, (label, widget) in enumerate(fields):
            baris, kolom = divmod(indeks, 3)
            ttk.Label(form, text=label).grid(row=baris * 2, column=kolom, sticky="w", padx=6, pady=(4, 0))
            widget.grid(row=baris * 2 + 1, column=kolom, sticky="ew", padx=6, pady=4)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=1)
        ttk.Label(
            form,
            text="Tarif dasar penginapan: {} / hari; tarif hewan dihitung otomatis.".format(
                format_rupiah(HARGA_DASAR_HARI)
            ),
            foreground="#52616b",
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=6, pady=(8, 2))
        ttk.Button(form, text="Proses Check-In", command=self._checkin).grid(
            row=4, column=2, sticky="e", padx=6, pady=5
        )

    def _buat_daftar(self):
        frame = ttk.LabelFrame(self.jendela, text="Transaksi yang masih menginap", padding=10)
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        wadah = ttk.Frame(frame)
        wadah.pack(fill="both", expand=True)
        self.tabel = buat_tabel(
            wadah, ("ID", "Hewan", "Pemilik", "Kandang", "Masuk", "Keluar", "Hari", "Total"),
            (45, 130, 150, 90, 100, 100, 55, 120),
        )

    def _muat_pilihan(self):
        try:
            with get_connection() as koneksi:
                pets = koneksi.execute(
                    """SELECT pets.*, owners.nama AS pemilik FROM pets
                       JOIN owners ON owners.id=pets.owner_id ORDER BY pets.nama"""
                ).fetchall()
                cages = koneksi.execute(
                    "SELECT * FROM cages WHERE status='Kosong' ORDER BY nomor"
                ).fetchall()
                services = koneksi.execute("SELECT * FROM services ORDER BY nama").fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal memuat pilihan check-in:\n{}".format(error))
            return
        self.pet_map = {
            "{} — {} ({})".format(row["nama"], row["jenis"], row["pemilik"]): dict(row)
            for row in pets
        }
        self.pet_combo["values"] = list(self.pet_map)
        if self.pet_map and not self.pet_combo.get():
            self.pet_combo.current(0)
        self.kandang_map = {
            "{} ({})".format(row["nomor"], row["jenis_hewan"]): dict(row) for row in cages
        }
        self.kandang_combo["values"] = list(self.kandang_map)
        if self.kandang_map and not self.kandang_combo.get():
            self.kandang_combo.current(0)
        self.layanan_map = {"Tanpa layanan": None}
        self.layanan_map.update(
            {"{} — {}".format(row["nama"], format_rupiah(row["harga"])): dict(row) for row in services}
        )
        self.layanan_combo["values"] = list(self.layanan_map)
        if not self.layanan_combo.get():
            self.layanan_combo.set("Tanpa layanan")

    def _checkin(self):
        pet = self.pet_map.get(self.pet_combo.get())
        kandang = self.kandang_map.get(self.kandang_combo.get())
        layanan = self.layanan_map.get(self.layanan_combo.get())
        if not pet or not kandang:
            messagebox.showwarning("Validasi", "Pilih hewan dan kandang kosong terlebih dahulu.")
            return
        if pet["jenis"] != kandang["jenis_hewan"]:
            messagebox.showwarning("Jenis tidak sesuai", "Jenis kandang harus sesuai dengan jenis hewan.")
            return
        try:
            masuk = datetime.strptime(self.masuk_var.get().strip(), "%Y-%m-%d").date()
            keluar = datetime.strptime(self.keluar_var.get().strip(), "%Y-%m-%d").date()
            lama_hari = (keluar - masuk).days
            if lama_hari < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Tanggal tidak valid",
                "Tanggal harus berformat YYYY-MM-DD dan tanggal keluar minimal satu hari setelah masuk.",
            )
            return
        hewan = buat_model_hewan(
            pet["nama"], pet["jenis"], pet["ras"], pet["umur"], pet["berat_kg"]
        )
        biaya_menginap = hewan.hitung_biaya(HARGA_DASAR_HARI, lama_hari)
        biaya_layanan = layanan["harga"] if layanan else 0
        total = biaya_menginap + biaya_layanan
        try:
            with get_connection() as koneksi:
                aktif = koneksi.execute(
                    "SELECT COUNT(*) FROM transactions WHERE pet_id=? AND status='Menginap'",
                    (pet["id"],),
                ).fetchone()[0]
                if aktif:
                    messagebox.showwarning(
                        "Hewan masih menginap",
                        "Hewan ini masih memiliki transaksi aktif dan belum dapat check-in lagi.",
                    )
                    return
                hasil = koneksi.execute(
                    "UPDATE cages SET status='Terisi' WHERE id=? AND status='Kosong'",
                    (kandang["id"],),
                )
                if hasil.rowcount != 1:
                    messagebox.showwarning("Kandang berubah", "Kandang sudah tidak kosong. Muat ulang pilihan.")
                    self._muat_pilihan()
                    return
                koneksi.execute(
                    """INSERT INTO transactions
                       (pet_id, cage_id, service_id, tanggal_masuk, tanggal_keluar, lama_hari,
                        biaya_menginap, biaya_layanan, total_biaya, status, status_layanan)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Menginap', ?)""",
                    (
                        pet["id"], kandang["id"], layanan["id"] if layanan else None,
                        masuk.isoformat(), keluar.isoformat(), lama_hari, biaya_menginap,
                        biaya_layanan, total, "Belum Diproses" if layanan else "Tidak Ada",
                    ),
                )
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal memproses check-in:\n{}".format(error))
            return
        messagebox.showinfo(
            "Check-in berhasil",
            "Lama penitipan: {} hari\nBiaya menginap: {}\nBiaya layanan: {}\nTotal: {}".format(
                lama_hari, format_rupiah(biaya_menginap),
                format_rupiah(biaya_layanan), format_rupiah(total),
            ),
        )
        self._muat_pilihan()
        self._muat_transaksi()

    def _muat_transaksi(self):
        try:
            with get_connection() as koneksi:
                rows = koneksi.execute(
                    """SELECT t.id, p.nama AS hewan, o.nama AS pemilik, c.nomor AS kandang,
                              t.tanggal_masuk, t.tanggal_keluar, t.lama_hari, t.total_biaya
                       FROM transactions t
                       JOIN pets p ON p.id=t.pet_id
                       JOIN owners o ON o.id=p.owner_id
                       JOIN cages c ON c.id=t.cage_id
                       WHERE t.status='Menginap' ORDER BY t.id DESC"""
                ).fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal memuat transaksi:\n{}".format(error))
            return
        kosongkan_tabel(self.tabel)
        for row in rows:
            self.tabel.insert(
                "", "end",
                values=(row["id"], row["hewan"], row["pemilik"], row["kandang"],
                        row["tanggal_masuk"], row["tanggal_keluar"], row["lama_hari"],
                        format_rupiah(row["total_biaya"])),
            )
