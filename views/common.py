"""Komponen kecil yang dipakai bersama oleh tampilan aplikasi."""

import tkinter as tk
from tkinter import ttk


def buat_jendela(parent, judul, ukuran="900x600"):
    jendela = tk.Toplevel(parent)
    jendela.title(judul)
    jendela.geometry(ukuran)
    jendela.minsize(720, 480)
    jendela.transient(parent)
    return jendela


def buat_tabel(parent, kolom, lebar=None, tinggi=10):
    tabel = ttk.Treeview(parent, columns=kolom, show="headings", height=tinggi)
    for indeks, nama in enumerate(kolom):
        tabel.heading(nama, text=nama)
        tabel.column(
            nama,
            width=(lebar[indeks] if lebar else 130),
            anchor="w",
        )
    gulir = ttk.Scrollbar(parent, orient="vertical", command=tabel.yview)
    tabel.configure(yscrollcommand=gulir.set)
    tabel.pack(side="left", fill="both", expand=True)
    gulir.pack(side="right", fill="y")
    return tabel


def format_rupiah(jumlah):
    return "Rp {:,}".format(int(jumlah or 0)).replace(",", ".")


def kosongkan_tabel(tabel):
    for item in tabel.get_children():
        tabel.delete(item)
