"""Modul Anggota 5: status layanan, pembayaran, dan rekap pendapatan."""

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from database import get_connection
from views.common import buat_jendela, buat_tabel, format_rupiah, kosongkan_tabel


class CheckoutView:
    def __init__(self, parent):
        self.jendela = buat_jendela(parent, "Check-Out & Pendapatan", "1050x690")
        self.transaksi_aktif = {}
        self._buat_tampilan()
        self._muat_transaksi()
        self._muat_pendapatan()

    def _buat_tampilan(self):
        ringkasan = ttk.LabelFrame(self.jendela, text="Rekap pendapatan", padding=12)
        ringkasan.pack(fill="x", padx=16, pady=(16, 10))
        self.pendapatan_label = ttk.Label(
            ringkasan, text="Total pendapatan: Rp 0", font=("Segoe UI", 14, "bold")
        )
        self.pendapatan_label.pack(side="left")
        ttk.Button(ringkasan, text="Muat Ulang", command=self._muat_semua).pack(side="right")

        frame = ttk.LabelFrame(self.jendela, text="Transaksi aktif", padding=10)
        frame.pack(fill="both", expand=True, padx=16, pady=8)
        wadah = ttk.Frame(frame)
        wadah.pack(fill="both", expand=True)
        self.tabel = buat_tabel(
            wadah,
            ("ID", "Hewan", "Pemilik", "Kandang", "Keluar", "Hari", "Total", "Status layanan"),
            (45, 120, 140, 80, 95, 55, 110, 150),
        )
        self.tabel.bind("<<TreeviewSelect>>", self._pilih_transaksi)

        kontrol = ttk.LabelFrame(self.jendela, text="Proses layanan & pembayaran", padding=12)
        kontrol.pack(fill="x", padx=16, pady=(8, 16))
        self.status_var = tk.StringVar()
        self.bayar_var = tk.StringVar()
        ttk.Label(kontrol, text="Status layanan").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Combobox(
            kontrol, textvariable=self.status_var,
            values=("Belum Diproses", "Dalam Proses", "Selesai"),
            state="readonly", width=20,
        ).grid(row=1, column=0, padx=5, pady=4)
        ttk.Button(
            kontrol, text="Simpan Status", command=self._simpan_status_layanan
        ).grid(row=1, column=1, padx=8)
        ttk.Label(kontrol, text="Jumlah pembayaran (Rp)").grid(
            row=0, column=2, sticky="w", padx=5
        )
        ttk.Entry(kontrol, textvariable=self.bayar_var, width=22).grid(
            row=1, column=2, padx=5, pady=4
        )
        ttk.Button(kontrol, text="Proses Check-Out", command=self._checkout).grid(
            row=1, column=3, padx=8
        )
        self.kembalian_label = ttk.Label(kontrol, text="Kembalian: —", font=("Segoe UI", 10, "bold"))
        self.kembalian_label.grid(row=1, column=4, padx=10)

    def _id_terpilih(self):
        pilihan = self.tabel.selection()
        if not pilihan:
            messagebox.showwarning("Pilih data", "Pilih transaksi yang akan diproses.")
            return None
        return int(self.tabel.item(pilihan[0], "values")[0])

    def _muat_transaksi(self):
        try:
            with get_connection() as koneksi:
                rows = koneksi.execute(
                    """SELECT t.*, p.nama AS hewan, o.nama AS pemilik, c.nomor AS kandang
                       FROM transactions t
                       JOIN pets p ON p.id=t.pet_id
                       JOIN owners o ON o.id=p.owner_id
                       JOIN cages c ON c.id=t.cage_id
                       WHERE t.status='Menginap' ORDER BY t.tanggal_keluar, t.id"""
                ).fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal memuat transaksi aktif:\n{}".format(error))
            return
        kosongkan_tabel(self.tabel)
        self.transaksi_aktif = {}
        for row in rows:
            self.transaksi_aktif[row["id"]] = dict(row)
            self.tabel.insert(
                "", "end",
                values=(row["id"], row["hewan"], row["pemilik"], row["kandang"],
                        row["tanggal_keluar"], row["lama_hari"],
                        format_rupiah(row["total_biaya"]), row["status_layanan"]),
            )

    def _pilih_transaksi(self, _event):
        pilihan = self.tabel.selection()
        if not pilihan:
            return
        transaksi_id = int(self.tabel.item(pilihan[0], "values")[0])
        transaksi = self.transaksi_aktif.get(transaksi_id)
        if transaksi:
            self.status_var.set(transaksi["status_layanan"])
            self.bayar_var.set(str(transaksi["total_biaya"]))
            self.kembalian_label.configure(text="Kembalian: —")

    def _simpan_status_layanan(self):
        transaksi_id = self._id_terpilih()
        if transaksi_id is None:
            return
        status = self.status_var.get().strip()
        if status not in ("Belum Diproses", "Dalam Proses", "Selesai"):
            messagebox.showwarning("Validasi", "Pilih status layanan yang valid.")
            return
        if not self.transaksi_aktif[transaksi_id]["service_id"]:
            messagebox.showwarning("Tidak ada layanan", "Transaksi ini tidak memiliki paket layanan.")
            return
        try:
            with get_connection() as koneksi:
                koneksi.execute(
                    "UPDATE transactions SET status_layanan=? WHERE id=? AND status='Menginap'",
                    (status, transaksi_id),
                )
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal mengubah status layanan:\n{}".format(error))
            return
        self._muat_transaksi()

    def _checkout(self):
        transaksi_id = self._id_terpilih()
        if transaksi_id is None:
            return
        transaksi = self.transaksi_aktif[transaksi_id]
        try:
            jumlah_bayar = int(self.bayar_var.get().strip().replace(".", "").replace(",", ""))
            if jumlah_bayar < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validasi", "Jumlah pembayaran harus berupa angka nol atau lebih.")
            return
        total = transaksi["total_biaya"]
        if jumlah_bayar < total:
            messagebox.showwarning(
                "Pembayaran kurang",
                "Total tagihan {}. Pembayaran belum mencukupi.".format(format_rupiah(total)),
            )
            return
        kembalian = jumlah_bayar - total
        if not messagebox.askyesno(
            "Konfirmasi Check-Out",
            "Tagihan: {}\nDibayar: {}\nKembalian: {}\nLanjutkan check-out?".format(
                format_rupiah(total), format_rupiah(jumlah_bayar), format_rupiah(kembalian)
            ),
        ):
            return
        try:
            with get_connection() as koneksi:
                hasil = koneksi.execute(
                    """UPDATE transactions
                       SET status='Selesai', jumlah_bayar=?, kembalian=?
                       WHERE id=? AND status='Menginap'""",
                    (jumlah_bayar, kembalian, transaksi_id),
                )
                if hasil.rowcount != 1:
                    messagebox.showwarning("Transaksi berubah", "Transaksi tidak lagi aktif. Muat ulang daftar.")
                    return
                koneksi.execute(
                    "UPDATE cages SET status='Kosong' WHERE id=?",
                    (transaksi["cage_id"],),
                )
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal memproses check-out:\n{}".format(error))
            return
        self.kembalian_label.configure(text="Kembalian: {}".format(format_rupiah(kembalian)))
        messagebox.showinfo(
            "Check-out berhasil",
            "Pembayaran diterima.\nKembalian: {}".format(format_rupiah(kembalian)),
        )
        self.bayar_var.set("")
        self._muat_semua()

    def _muat_pendapatan(self):
        try:
            with get_connection() as koneksi:
                total = koneksi.execute(
                    "SELECT COALESCE(SUM(total_biaya), 0) FROM transactions WHERE status='Selesai'"
                ).fetchone()[0]
        except sqlite3.Error as error:
            messagebox.showerror("Database", "Gagal menghitung pendapatan:\n{}".format(error))
            return
        self.pendapatan_label.configure(
            text="Total pendapatan dari transaksi selesai: {}".format(format_rupiah(total))
        )

    def _muat_semua(self):
        self._muat_transaksi()
        self._muat_pendapatan()
