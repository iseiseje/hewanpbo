"""Modul Anggota 2: CRUD pemilik dan hewan peliharaan."""

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from database import get_connection
from models.pemilik import Pemilik
from models.hewan import buat_model_hewan
from views.common import buat_jendela, buat_tabel, kosongkan_tabel


class HewanView:
    def __init__(self, parent):
        self.jendela = buat_jendela(parent, "Pemilik & Hewan", "980x680")
        self.tabs = ttk.Notebook(self.jendela)
        self.tabs.pack(fill="both", expand=True, padx=14, pady=14)
        self._buat_tab_pemilik()
        self._buat_tab_hewan()
        self._muat_pemilik()
        self._muat_hewan()

    def _buat_tab_pemilik(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Pemilik")
        form = ttk.LabelFrame(tab, text="Form pemilik", padding=10)
        form.pack(fill="x", pady=(0, 12))
        self.pemilik_vars = {key: tk.StringVar() for key in ("nama", "telepon", "alamat")}
        for kolom, (key, label) in enumerate(
            (("nama", "Nama"), ("telepon", "Telepon"), ("alamat", "Alamat"))
        ):
            ttk.Label(form, text=label).grid(row=0, column=kolom, sticky="w", padx=5)
            ttk.Entry(form, textvariable=self.pemilik_vars[key], width=28).grid(
                row=1, column=kolom, padx=5, pady=4
            )
        tombol = ttk.Frame(form)
        tombol.grid(row=1, column=3, padx=8)
        ttk.Button(tombol, text="Tambah", command=self._tambah_pemilik).pack(side="left", padx=2)
        ttk.Button(tombol, text="Ubah", command=self._ubah_pemilik).pack(side="left", padx=2)
        ttk.Button(tombol, text="Hapus", command=self._hapus_pemilik).pack(side="left", padx=2)
        ttk.Button(tombol, text="Bersihkan", command=self._bersihkan_pemilik).pack(side="left", padx=2)
        wadah = ttk.Frame(tab)
        wadah.pack(fill="both", expand=True)
        self.tabel_pemilik = buat_tabel(
            wadah, ("ID", "Nama", "Telepon", "Alamat"), (55, 200, 150, 360)
        )
        self.tabel_pemilik.bind("<<TreeviewSelect>>", self._pilih_pemilik)

    def _buat_tab_hewan(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Hewan")
        form = ttk.LabelFrame(tab, text="Form hewan", padding=10)
        form.pack(fill="x", pady=(0, 12))
        self.hewan_vars = {
            key: tk.StringVar() for key in ("nama", "jenis", "ras", "umur", "berat")
        }
        self.combo_pemilik = ttk.Combobox(form, state="readonly", width=22)
        self.pemilik_map = {}
        ttk.Label(form, text="Pemilik").grid(row=0, column=0, sticky="w", padx=4)
        self.combo_pemilik.grid(row=1, column=0, padx=4, pady=4)
        field_specs = (
            ("nama", "Nama"), ("jenis", "Jenis"), ("ras", "Ras"),
            ("umur", "Umur (tahun)"), ("berat", "Berat (kg)"),
        )
        for kolom, (key, label) in enumerate(field_specs, start=1):
            ttk.Label(form, text=label).grid(row=0, column=kolom, sticky="w", padx=4)
            if key == "jenis":
                widget = ttk.Combobox(
                    form, textvariable=self.hewan_vars[key],
                    values=("Kucing", "Anjing", "Kelinci"), state="readonly", width=15,
                )
            else:
                widget = ttk.Entry(form, textvariable=self.hewan_vars[key], width=17)
            widget.grid(row=1, column=kolom, padx=4, pady=4)
        tombol = ttk.Frame(tab)
        tombol.pack(fill="x", pady=(0, 10))
        ttk.Button(tombol, text="Tambah", command=self._tambah_hewan).pack(side="left", padx=3)
        ttk.Button(tombol, text="Ubah", command=self._ubah_hewan).pack(side="left", padx=3)
        ttk.Button(tombol, text="Hapus", command=self._hapus_hewan).pack(side="left", padx=3)
        ttk.Button(tombol, text="Bersihkan", command=self._bersihkan_hewan).pack(side="left", padx=3)
        wadah = ttk.Frame(tab)
        wadah.pack(fill="both", expand=True)
        self.tabel_hewan = buat_tabel(
            wadah, ("ID", "Nama", "Jenis", "Ras", "Umur", "Berat kg", "Pemilik"),
            (45, 130, 100, 150, 75, 90, 200),
        )
        self.tabel_hewan.bind("<<TreeviewSelect>>", self._pilih_hewan)

    def _muat_pemilik(self):
        try:
            with get_connection() as koneksi:
                rows = koneksi.execute("SELECT * FROM owners ORDER BY nama").fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal memuat pemilik:\n{}".format(error))
            return
        kosongkan_tabel(self.tabel_pemilik)
        self.pemilik_map = {}
        for row in rows:
            self.tabel_pemilik.insert("", "end", values=(row["id"], row["nama"], row["telepon"], row["alamat"]))
            self.pemilik_map["{} - {}".format(row["id"], row["nama"])] = row["id"]
        pilihan = list(self.pemilik_map)
        self.combo_pemilik["values"] = pilihan
        if pilihan and self.combo_pemilik.get() not in pilihan:
            self.combo_pemilik.set(pilihan[0])

    def _muat_hewan(self):
        try:
            with get_connection() as koneksi:
                rows = koneksi.execute(
                    """SELECT pets.*, owners.nama AS nama_pemilik
                       FROM pets JOIN owners ON owners.id = pets.owner_id
                       ORDER BY pets.nama"""
                ).fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal memuat hewan:\n{}".format(error))
            return
        kosongkan_tabel(self.tabel_hewan)
        for row in rows:
            self.tabel_hewan.insert(
                "", "end",
                values=(row["id"], row["nama"], row["jenis"], row["ras"], row["umur"],
                        row["berat_kg"], row["nama_pemilik"]),
            )

    def _tambah_pemilik(self):
        data = self._nilai_pemilik()
        if data is None:
            return
        try:
            with get_connection() as koneksi:
                koneksi.execute(
                    "INSERT INTO owners (nama, telepon, alamat) VALUES (?, ?, ?)",
                    (data.get_nama(), data.get_telepon(), data.get_alamat()),
                )
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal menambah pemilik:\n{}".format(error))
            return
        self._bersihkan_pemilik()
        self._muat_pemilik()

    def _ubah_pemilik(self):
        terpilih = self.tabel_pemilik.selection()
        data = self._nilai_pemilik()
        if not terpilih:
            messagebox.showwarning("Pilih data", "Pilih pemilik yang akan diubah.")
            return
        if data is None:
            return
        pemilik_id = self.tabel_pemilik.item(terpilih[0], "values")[0]
        try:
            with get_connection() as koneksi:
                koneksi.execute(
                    "UPDATE owners SET nama = ?, telepon = ?, alamat = ? WHERE id = ?",
                    (data.get_nama(), data.get_telepon(), data.get_alamat(), pemilik_id),
                )
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal mengubah pemilik:\n{}".format(error))
            return
        self._bersihkan_pemilik()
        self._muat_pemilik()
        self._muat_hewan()

    def _hapus_pemilik(self):
        terpilih = self.tabel_pemilik.selection()
        if not terpilih:
            messagebox.showwarning("Pilih data", "Pilih pemilik yang akan dihapus.")
            return
        if not messagebox.askyesno("Konfirmasi", "Hapus pemilik terpilih?"):
            return
        pemilik_id = self.tabel_pemilik.item(terpilih[0], "values")[0]
        try:
            with get_connection() as koneksi:
                koneksi.execute("DELETE FROM owners WHERE id = ?", (pemilik_id,))
        except sqlite3.IntegrityError:
            messagebox.showerror("Tidak dapat dihapus", "Hapus data hewan milik pemilik ini terlebih dahulu.")
            return
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal menghapus pemilik:\n{}".format(error))
            return
        self._bersihkan_pemilik()
        self._muat_pemilik()

    def _nilai_pemilik(self):
        nama = self.pemilik_vars["nama"].get().strip()
        telepon = self.pemilik_vars["telepon"].get().strip()
        if not nama or not telepon:
            messagebox.showwarning("Validasi", "Nama dan telepon pemilik wajib diisi.")
            return None
        return Pemilik(nama, telepon, self.pemilik_vars["alamat"].get().strip())

    def _pilih_pemilik(self, _event):
        terpilih = self.tabel_pemilik.selection()
        if terpilih:
            values = self.tabel_pemilik.item(terpilih[0], "values")
            for key, value in zip(("nama", "telepon", "alamat"), values[1:]):
                self.pemilik_vars[key].set(value)

    def _bersihkan_pemilik(self):
        for variabel in self.pemilik_vars.values():
            variabel.set("")

    def _nilai_hewan(self):
        pemilik_key = self.combo_pemilik.get()
        nilai = {key: value.get().strip() for key, value in self.hewan_vars.items()}
        if not pemilik_key or not all(nilai.values()):
            messagebox.showwarning("Validasi", "Pemilik dan seluruh data hewan wajib diisi.")
            return None
        try:
            umur = int(nilai["umur"])
            berat = float(nilai["berat"].replace(",", "."))
            if umur < 0 or berat <= 0:
                raise ValueError
            objek = buat_model_hewan(nilai["nama"], nilai["jenis"], nilai["ras"], umur, berat)
        except ValueError:
            messagebox.showwarning("Validasi", "Umur harus >= 0 dan berat harus berupa angka > 0.")
            return None
        return self.pemilik_map[pemilik_key], objek

    def _simpan_hewan(self, update=False):
        terpilih = self.tabel_hewan.selection()
        if update and not terpilih:
            messagebox.showwarning("Pilih data", "Pilih hewan yang akan diubah.")
            return
        data = self._nilai_hewan()
        if data is None:
            return
        owner_id, hewan = data
        nilai = (
            owner_id, hewan.get_nama(), hewan.get_jenis(), hewan.get_ras(),
            hewan.get_umur(), hewan.get_berat_kg(),
        )
        try:
            with get_connection() as koneksi:
                if update:
                    pet_id = self.tabel_hewan.item(terpilih[0], "values")[0]
                    koneksi.execute(
                        """UPDATE pets SET owner_id=?, nama=?, jenis=?, ras=?, umur=?, berat_kg=?
                           WHERE id=?""",
                        nilai + (pet_id,),
                    )
                else:
                    koneksi.execute(
                        """INSERT INTO pets (owner_id, nama, jenis, ras, umur, berat_kg)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        nilai,
                    )
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal menyimpan hewan:\n{}".format(error))
            return
        self._bersihkan_hewan()
        self._muat_hewan()

    def _tambah_hewan(self):
        self._simpan_hewan()

    def _ubah_hewan(self):
        self._simpan_hewan(update=True)

    def _hapus_hewan(self):
        terpilih = self.tabel_hewan.selection()
        if not terpilih:
            messagebox.showwarning("Pilih data", "Pilih hewan yang akan dihapus.")
            return
        if not messagebox.askyesno("Konfirmasi", "Hapus hewan terpilih?"):
            return
        pet_id = self.tabel_hewan.item(terpilih[0], "values")[0]
        try:
            with get_connection() as koneksi:
                koneksi.execute("DELETE FROM pets WHERE id = ?", (pet_id,))
        except sqlite3.IntegrityError:
            messagebox.showerror("Tidak dapat dihapus", "Hewan sudah memiliki transaksi penitipan.")
            return
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal menghapus hewan:\n{}".format(error))
            return
        self._bersihkan_hewan()
        self._muat_hewan()

    def _pilih_hewan(self, _event):
        terpilih = self.tabel_hewan.selection()
        if not terpilih:
            return
        values = self.tabel_hewan.item(terpilih[0], "values")
        for key, value in zip(("nama", "jenis", "ras", "umur", "berat"), values[1:6]):
            self.hewan_vars[key].set(value)
        try:
            with get_connection() as koneksi:
                row = koneksi.execute(
                    "SELECT owner_id FROM pets WHERE id = ?", (values[0],)
                ).fetchone()
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal membaca pemilik hewan:\n{}".format(error))
            return
        if row:
            for label, owner_id in self.pemilik_map.items():
                if owner_id == row["owner_id"]:
                    self.combo_pemilik.set(label)
                    break

    def _bersihkan_hewan(self):
        for variabel in self.hewan_vars.values():
            variabel.set("")
        if self.combo_pemilik["values"]:
            self.combo_pemilik.current(0)
