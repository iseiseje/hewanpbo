"""Modul Anggota 3: CRUD paket layanan dan status kandang."""

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from database import get_connection
from models.layanan import Layanan
from views.common import buat_jendela, buat_tabel, format_rupiah, kosongkan_tabel


class LayananView:
    def __init__(self, parent):
        self.jendela = buat_jendela(parent, "Paket Layanan & Kandang", "950x650")
        self.tabs = ttk.Notebook(self.jendela)
        self.tabs.pack(fill="both", expand=True, padx=14, pady=14)
        self._buat_tab_layanan()
        self._buat_tab_kandang()
        self._muat_layanan()
        self._muat_kandang()

    def _buat_tab_layanan(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Paket Layanan")
        form = ttk.LabelFrame(tab, text="Form paket layanan", padding=10)
        form.pack(fill="x", pady=(0, 12))
        self.layanan_vars = {key: tk.StringVar() for key in ("nama", "kategori", "harga", "deskripsi")}
        fields = (("nama", "Nama"), ("kategori", "Kategori"), ("harga", "Harga (Rp)"),
                  ("deskripsi", "Deskripsi"))
        for kolom, (key, label) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=kolom, sticky="w", padx=4)
            ttk.Entry(form, textvariable=self.layanan_vars[key], width=24).grid(
                row=1, column=kolom, padx=4, pady=4
            )
        tombol = ttk.Frame(form)
        tombol.grid(row=1, column=4, padx=6)
        ttk.Button(tombol, text="Tambah", command=self._tambah_layanan).pack(side="left", padx=2)
        ttk.Button(tombol, text="Ubah", command=self._ubah_layanan).pack(side="left", padx=2)
        ttk.Button(tombol, text="Hapus", command=self._hapus_layanan).pack(side="left", padx=2)
        ttk.Button(tombol, text="Bersihkan", command=self._bersihkan_layanan).pack(side="left", padx=2)
        wadah = ttk.Frame(tab)
        wadah.pack(fill="both", expand=True)
        self.tabel_layanan = buat_tabel(
            wadah, ("ID", "Nama", "Kategori", "Harga", "Deskripsi"),
            (50, 180, 130, 130, 320),
        )
        self.tabel_layanan.bind("<<TreeviewSelect>>", self._pilih_layanan)

    def _buat_tab_kandang(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Status Kandang")
        form = ttk.LabelFrame(tab, text="Data kandang", padding=10)
        form.pack(fill="x", pady=(0, 12))
        self.kandang_vars = {key: tk.StringVar() for key in ("nomor", "jenis", "status")}
        ttk.Label(form, text="Nomor").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(form, textvariable=self.kandang_vars["nomor"], width=20).grid(
            row=1, column=0, padx=5, pady=4
        )
        ttk.Label(form, text="Jenis hewan").grid(row=0, column=1, sticky="w", padx=5)
        ttk.Combobox(
            form, textvariable=self.kandang_vars["jenis"],
            values=("Kucing", "Anjing", "Kelinci"), state="readonly", width=18,
        ).grid(row=1, column=1, padx=5, pady=4)
        ttk.Label(form, text="Status").grid(row=0, column=2, sticky="w", padx=5)
        ttk.Combobox(
            form, textvariable=self.kandang_vars["status"],
            values=("Kosong", "Terisi"), state="readonly", width=15,
        ).grid(row=1, column=2, padx=5, pady=4)
        tombol = ttk.Frame(form)
        tombol.grid(row=1, column=3, padx=8)
        ttk.Button(tombol, text="Tambah", command=self._tambah_kandang).pack(side="left", padx=2)
        ttk.Button(tombol, text="Ubah", command=self._ubah_kandang).pack(side="left", padx=2)
        ttk.Button(tombol, text="Hapus", command=self._hapus_kandang).pack(side="left", padx=2)
        ttk.Button(tombol, text="Bersihkan", command=self._bersihkan_kandang).pack(side="left", padx=2)
        wadah = ttk.Frame(tab)
        wadah.pack(fill="both", expand=True)
        self.tabel_kandang = buat_tabel(wadah, ("ID", "Nomor", "Jenis hewan", "Status"), (60, 200, 220, 150))
        self.tabel_kandang.bind("<<TreeviewSelect>>", self._pilih_kandang)

    def _muat_layanan(self):
        try:
            with get_connection() as koneksi:
                rows = koneksi.execute("SELECT * FROM services ORDER BY nama").fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal memuat layanan:\n{}".format(error))
            return
        kosongkan_tabel(self.tabel_layanan)
        for row in rows:
            self.tabel_layanan.insert(
                "", "end",
                values=(row["id"], row["nama"], row["kategori"],
                        format_rupiah(row["harga"]), row["deskripsi"]),
            )

    def _nilai_layanan(self):
        nama = self.layanan_vars["nama"].get().strip()
        kategori = self.layanan_vars["kategori"].get().strip()
        harga_text = self.layanan_vars["harga"].get().strip().replace(".", "").replace(",", "")
        deskripsi = self.layanan_vars["deskripsi"].get().strip()
        if not nama or not kategori or not harga_text:
            messagebox.showwarning("Validasi", "Nama, kategori, dan harga wajib diisi.")
            return None
        try:
            harga = int(harga_text)
            if harga < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validasi", "Harga harus berupa angka nol atau lebih.")
            return None
        return Layanan(nama, kategori, harga, deskripsi)

    def _simpan_layanan(self, ubah=False):
        pilihan = self.tabel_layanan.selection()
        if ubah and not pilihan:
            messagebox.showwarning("Pilih data", "Pilih paket layanan yang akan diubah.")
            return
        layanan = self._nilai_layanan()
        if layanan is None:
            return
        nilai = (layanan.get_nama(), layanan.get_kategori(), layanan.get_harga(), layanan.get_deskripsi())
        try:
            with get_connection() as koneksi:
                if ubah:
                    layanan_id = self.tabel_layanan.item(pilihan[0], "values")[0]
                    koneksi.execute(
                        "UPDATE services SET nama=?, kategori=?, harga=?, deskripsi=? WHERE id=?",
                        nilai + (layanan_id,),
                    )
                else:
                    koneksi.execute(
                        "INSERT INTO services (nama, kategori, harga, deskripsi) VALUES (?, ?, ?, ?)",
                        nilai,
                    )
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal menyimpan layanan:\n{}".format(error))
            return
        self._bersihkan_layanan()
        self._muat_layanan()

    def _tambah_layanan(self):
        self._simpan_layanan()

    def _ubah_layanan(self):
        self._simpan_layanan(ubah=True)

    def _hapus_layanan(self):
        pilihan = self.tabel_layanan.selection()
        if not pilihan:
            messagebox.showwarning("Pilih data", "Pilih layanan yang akan dihapus.")
            return
        if not messagebox.askyesno("Konfirmasi", "Hapus paket layanan terpilih?"):
            return
        layanan_id = self.tabel_layanan.item(pilihan[0], "values")[0]
        try:
            with get_connection() as koneksi:
                koneksi.execute("DELETE FROM services WHERE id=?", (layanan_id,))
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal menghapus layanan:\n{}".format(error))
            return
        self._bersihkan_layanan()
        self._muat_layanan()

    def _pilih_layanan(self, _event):
        pilihan = self.tabel_layanan.selection()
        if not pilihan:
            return
        values = self.tabel_layanan.item(pilihan[0], "values")
        harga = str(values[3]).replace("Rp ", "").replace(".", "")
        for key, value in zip(("nama", "kategori", "harga", "deskripsi"),
                              (values[1], values[2], harga, values[4])):
            self.layanan_vars[key].set(value)

    def _bersihkan_layanan(self):
        for variabel in self.layanan_vars.values():
            variabel.set("")

    def _muat_kandang(self):
        try:
            with get_connection() as koneksi:
                rows = koneksi.execute("SELECT * FROM cages ORDER BY nomor").fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal memuat kandang:\n{}".format(error))
            return
        kosongkan_tabel(self.tabel_kandang)
        for row in rows:
            self.tabel_kandang.insert(
                "", "end", values=(row["id"], row["nomor"], row["jenis_hewan"], row["status"])
            )

    def _nilai_kandang(self):
        nomor = self.kandang_vars["nomor"].get().strip()
        jenis = self.kandang_vars["jenis"].get().strip()
        status = self.kandang_vars["status"].get().strip()
        if not nomor or not jenis or not status:
            messagebox.showwarning("Validasi", "Nomor, jenis hewan, dan status kandang wajib diisi.")
            return None
        return nomor, jenis, status

    def _simpan_kandang(self, ubah=False):
        pilihan = self.tabel_kandang.selection()
        if ubah and not pilihan:
            messagebox.showwarning("Pilih data", "Pilih kandang yang akan diubah.")
            return
        nilai = self._nilai_kandang()
        if nilai is None:
            return
        try:
            with get_connection() as koneksi:
                if ubah:
                    kandang_id = self.tabel_kandang.item(pilihan[0], "values")[0]
                    aktif = koneksi.execute(
                        "SELECT COUNT(*) FROM transactions WHERE cage_id=? AND status='Menginap'",
                        (kandang_id,),
                    ).fetchone()[0]
                    if aktif and nilai[2] == "Kosong":
                        messagebox.showwarning(
                            "Kandang masih dipakai",
                            "Check-out transaksi aktif terlebih dahulu sebelum mengosongkan kandang.",
                        )
                        return
                    koneksi.execute(
                        "UPDATE cages SET nomor=?, jenis_hewan=?, status=? WHERE id=?",
                        nilai + (kandang_id,),
                    )
                else:
                    koneksi.execute(
                        "INSERT INTO cages (nomor, jenis_hewan, status) VALUES (?, ?, ?)", nilai
                    )
        except sqlite3.IntegrityError:
            messagebox.showerror("Data duplikat", "Nomor kandang sudah digunakan.")
            return
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal menyimpan kandang:\n{}".format(error))
            return
        self._bersihkan_kandang()
        self._muat_kandang()

    def _tambah_kandang(self):
        self._simpan_kandang()

    def _ubah_kandang(self):
        self._simpan_kandang(ubah=True)

    def _hapus_kandang(self):
        pilihan = self.tabel_kandang.selection()
        if not pilihan:
            messagebox.showwarning("Pilih data", "Pilih kandang yang akan dihapus.")
            return
        if not messagebox.askyesno("Konfirmasi", "Hapus kandang terpilih?"):
            return
        kandang_id = self.tabel_kandang.item(pilihan[0], "values")[0]
        try:
            with get_connection() as koneksi:
                koneksi.execute("DELETE FROM cages WHERE id=?", (kandang_id,))
        except sqlite3.IntegrityError:
            messagebox.showerror("Tidak dapat dihapus", "Kandang sudah tercatat pada transaksi.")
            return
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal menghapus kandang:\n{}".format(error))
            return
        self._bersihkan_kandang()
        self._muat_kandang()

    def _pilih_kandang(self, _event):
        pilihan = self.tabel_kandang.selection()
        if pilihan:
            values = self.tabel_kandang.item(pilihan[0], "values")
            for key, value in zip(("nomor", "jenis", "status"), values[1:]):
                self.kandang_vars[key].set(value)

    def _bersihkan_kandang(self):
        for variabel in self.kandang_vars.values():
            variabel.set("")
