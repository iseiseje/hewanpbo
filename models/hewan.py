"""Model hewan dan contoh penerapan inheritance serta polymorphism."""

from abc import ABC, abstractmethod


class HewanPeliharaan(ABC):
    """Kelas induk abstrak untuk semua jenis hewan peliharaan."""

    def __init__(self, nama, jenis, ras, umur, berat_kg):
        self.__nama = nama
        self.__jenis = jenis
        self.__ras = ras
        self.__umur = int(umur)
        self.__berat_kg = float(berat_kg)

    def get_nama(self):
        return self.__nama

    def set_nama(self, nama):
        self.__nama = nama

    def get_jenis(self):
        return self.__jenis

    def get_ras(self):
        return self.__ras

    def set_ras(self, ras):
        self.__ras = ras

    def get_umur(self):
        return self.__umur

    def set_umur(self, umur):
        self.__umur = int(umur)

    def get_berat_kg(self):
        return self.__berat_kg

    def set_berat_kg(self, berat_kg):
        self.__berat_kg = float(berat_kg)

    @abstractmethod
    def hitung_biaya(self, harga_dasar, lama_hari):
        """Menghitung tarif penginapan sesuai jenis hewan."""


class Kucing(HewanPeliharaan):
    def __init__(self, nama, ras, umur, berat_kg):
        super().__init__(nama, "Kucing", ras, umur, berat_kg)

    def hitung_biaya(self, harga_dasar, lama_hari):
        return int(harga_dasar * lama_hari)


class Anjing(HewanPeliharaan):
    def __init__(self, nama, ras, umur, berat_kg):
        super().__init__(nama, "Anjing", ras, umur, berat_kg)

    def hitung_biaya(self, harga_dasar, lama_hari):
        tambahan = 25000 if self.get_berat_kg() > 10 else 0
        return int((harga_dasar + tambahan) * lama_hari)


class Kelinci(HewanPeliharaan):
    def __init__(self, nama, ras, umur, berat_kg):
        super().__init__(nama, "Kelinci", ras, umur, berat_kg)

    def hitung_biaya(self, harga_dasar, lama_hari):
        return int(max(0, harga_dasar - 5000) * lama_hari)


def buat_model_hewan(nama, jenis, ras, umur, berat_kg):
    """Membuat objek hewan dari data yang tersimpan di database."""
    kelas_hewan = {"Kucing": Kucing, "Anjing": Anjing, "Kelinci": Kelinci}
    if jenis not in kelas_hewan:
        raise ValueError("Jenis hewan harus Kucing, Anjing, atau Kelinci.")
    return kelas_hewan[jenis](nama, ras, umur, berat_kg)
