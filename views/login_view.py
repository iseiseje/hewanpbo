"""Modul Anggota 1: login dan pengelolaan pegawai."""

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from database import get_connection
from models.user import User
from views.common import buat_jendela, buat_tabel, kosongkan_tabel


class LoginView:
    def __init__(self, parent):
        self.jendela = buat_jendela(parent, "Login & Pegawai", "820x580")
        self.pegawai_aktif = None
        self._buat_login()

    def _buat_login(self):
        self.frame_login = ttk.LabelFrame(self.jendela, text="Login Pegawai", padding=18)
        self.frame_login.pack(fill="x", padx=20, pady=20)
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        ttk.Label(self.frame_login, text="Username").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(self.frame_login, textvariable=self.username_var, width=30).grid(
            row=0, column=1, padx=8
        )
        ttk.Label(self.frame_login, text="Password").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(
            self.frame_login, textvariable=self.password_var, show="*", width=30
        ).grid(row=1, column=1, padx=8)
        ttk.Button(self.frame_login, text="Masuk", command=self._login).grid(
            row=0, column=2, rowspan=2, padx=15
        )
        ttk.Label(
            self.frame_login,
            text="Contoh: admin / admin123",
            foreground="#5c6870",
        ).grid(row=2, column=1, sticky="w", padx=8, pady=(5, 0))

    def _login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            messagebox.showwarning("Validasi", "Username dan password wajib diisi.")
            return
        try:
            with get_connection() as koneksi:
                row = koneksi.execute(
                    "SELECT * FROM users WHERE username = ? AND password = ?",
                    (username, password),
                ).fetchone()
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal memeriksa login:\n{}".format(error))
            return
        if row is None:
            messagebox.showerror("Login gagal", "Username atau password tidak sesuai.")
            return
        if row["role"] != "Admin":
            messagebox.showwarning("Akses terbatas", "Hanya Admin yang dapat mengelola pegawai.")
            return
        self.pegawai_aktif = User(row["nama"], row["username"], row["password"], row["role"], row["id"])
        self.frame_login.pack_forget()
        self._buat_panel_pegawai()

    def _buat_panel_pegawai(self):
        panel = ttk.Frame(self.jendela, padding=18)
        panel.pack(fill="both", expand=True)
        ttk.Label(
            panel,
            text="Kelola Pegawai — login sebagai {}".format(self.pegawai_aktif.get_nama()),
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        form = ttk.LabelFrame(panel, text="Data pegawai", padding=10)
        form.pack(fill="x", pady=(0, 12))
        self.field_pegawai = {}
        for kolom, label in enumerate(("Nama", "Username", "Password")):
            ttk.Label(form, text=label).grid(row=0, column=kolom, sticky="w", padx=4)
            variabel = tk.StringVar()
            self.field_pegawai[label.lower()] = variabel
            ttk.Entry(form, textvariable=variabel, width=22, show="*" if label == "Password" else "").grid(
                row=1, column=kolom, padx=4, pady=4
            )
        tombol = ttk.Frame(form)
        tombol.grid(row=1, column=3, padx=8)
        ttk.Button(tombol, text="Tambah", command=self._tambah_pegawai).pack(side="left", padx=2)
        ttk.Button(tombol, text="Ubah", command=self._ubah_pegawai).pack(side="left", padx=2)
        ttk.Button(tombol, text="Hapus", command=self._hapus_pegawai).pack(side="left", padx=2)
        ttk.Button(tombol, text="Bersihkan", command=self._bersihkan).pack(side="left", padx=2)

        wadah = ttk.Frame(panel)
        wadah.pack(fill="both", expand=True)
        self.tabel = buat_tabel(wadah, ("ID", "Nama", "Username", "Role"), (55, 240, 180, 110))
        self.tabel.bind("<<TreeviewSelect>>", self._pilih_pegawai)
        self._muat_pegawai()

    def _muat_pegawai(self):
        try:
            with get_connection() as koneksi:
                rows = koneksi.execute(
                    "SELECT id, nama, username, role FROM users ORDER BY nama"
                ).fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal memuat pegawai:\n{}".format(error))
            return
        kosongkan_tabel(self.tabel)
        for row in rows:
            self.tabel.insert("", "end", values=tuple(row))

    def _nilai_form(self):
        nama = self.field_pegawai["nama"].get().strip()
        username = self.field_pegawai["username"].get().strip()
        password = self.field_pegawai["password"].get().strip()
        if not nama or not username or not password:
            messagebox.showwarning("Validasi", "Nama, username, dan password wajib diisi.")
            return None
        return User(nama, username, password)

    def _tambah_pegawai(self):
        user = self._nilai_form()
        if user is None:
            return
        try:
            with get_connection() as koneksi:
                koneksi.execute(
                    "INSERT INTO users (nama, username, password, role) VALUES (?, ?, ?, ?)",
                    (user.get_nama(), user.get_username(), user.get_password(), "Pegawai"),
                )
        except sqlite3.IntegrityError:
            messagebox.showerror("Data duplikat", "Username sudah digunakan.")
            return
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal menambah pegawai:\n{}".format(error))
            return
        self._bersihkan()
        self._muat_pegawai()

    def _ubah_pegawai(self):
        terpilih = self.tabel.selection()
        user = self._nilai_form()
        if not terpilih:
            messagebox.showwarning("Pilih data", "Pilih pegawai yang akan diubah.")
            return
        if user is None:
            return
        user_id = self.tabel.item(terpilih[0], "values")[0]
        try:
            with get_connection() as koneksi:
                koneksi.execute(
                    "UPDATE users SET nama = ?, username = ?, password = ? WHERE id = ?",
                    (user.get_nama(), user.get_username(), user.get_password(), user_id),
                )
        except sqlite3.IntegrityError:
            messagebox.showerror("Data duplikat", "Username sudah digunakan.")
            return
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal mengubah pegawai:\n{}".format(error))
            return
        self._bersihkan()
        self._muat_pegawai()

    def _hapus_pegawai(self):
        terpilih = self.tabel.selection()
        if not terpilih:
            messagebox.showwarning("Pilih data", "Pilih pegawai yang akan dihapus.")
            return
        values = self.tabel.item(terpilih[0], "values")
        if values[2] == self.pegawai_aktif.get_username():
            messagebox.showwarning("Tidak dapat dihapus", "Akun Admin yang sedang digunakan tidak dapat dihapus.")
            return
        if not messagebox.askyesno("Konfirmasi", "Hapus pegawai terpilih?"):
            return
        try:
            with get_connection() as koneksi:
                koneksi.execute("DELETE FROM users WHERE id = ?", (values[0],))
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal menghapus pegawai:\n{}".format(error))
            return
        self._bersihkan()
        self._muat_pegawai()

    def _pilih_pegawai(self, _event):
        terpilih = self.tabel.selection()
        if not terpilih:
            return
        values = self.tabel.item(terpilih[0], "values")
        self.field_pegawai["nama"].set(values[1])
        self.field_pegawai["username"].set(values[2])
        self.field_pegawai["password"].set("")

    def _bersihkan(self):
        for variabel in self.field_pegawai.values():
            variabel.set("")
