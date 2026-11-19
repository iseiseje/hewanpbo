"""Dashboard utama Pet Hotel & Salon."""

import tkinter as tk
from tkinter import ttk

from database import init_db
from views.login_view import LoginView
from views.hewan_view import HewanView
from views.layanan_view import LayananView
from views.checkin_view import CheckinView
from views.checkout_view import CheckoutView


class AplikasiPetHotel:
    """Mengatur dashboard dan membuka lima modul aplikasi."""

    def __init__(self, root):
        self.root = root
        self.root.title("Pet Hotel & Salon")
        self.root.geometry("760x520")
        self.root.minsize(650, 450)
        self.root.configure(bg="#f3f6f8")
        self._buat_dashboard()

    def _buat_dashboard(self):
        gaya = ttk.Style()
        gaya.configure("TButton", font=("Segoe UI", 10), padding=9)
        gaya.configure("Judul.TLabel", font=("Segoe UI", 22, "bold"))
        gaya.configure("Info.TLabel", font=("Segoe UI", 10))

        konten = ttk.Frame(self.root, padding=32)
        konten.pack(fill="both", expand=True)
        ttk.Label(konten, text="Pet Hotel & Salon", style="Judul.TLabel").pack(pady=(15, 5))
        ttk.Label(
            konten,
            text="Sistem penitipan dan grooming hewan peliharaan",
            style="Info.TLabel",
        ).pack(pady=(0, 25))

        modul = [
            ("1. Login & CRUD Pegawai", LoginView),
            ("2. Pemilik & Hewan", HewanView),
            ("3. Paket Layanan & Kandang", LayananView),
            ("4. Transaksi Check-In", CheckinView),
            ("5. Check-Out & Pendapatan", CheckoutView),
        ]
        for label, tampilan in modul:
            ttk.Button(
                konten,
                text=label,
                command=lambda view=tampilan: view(self.root),
            ).pack(fill="x", pady=5)

        ttk.Label(
            konten,
            text="Data contoh: admin / admin123  |  pegawai / pegawai123",
            foreground="#5c6870",
        ).pack(pady=(20, 0))


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    AplikasiPetHotel(root)
    root.mainloop()
