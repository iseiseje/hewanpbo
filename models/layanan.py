"""Model paket layanan."""


class Layanan:
    def __init__(self, nama, kategori, harga, deskripsi="", layanan_id=None):
        self.__id = layanan_id
        self.__nama = nama
        self.__kategori = kategori
        self.__harga = int(harga)
        self.__deskripsi = deskripsi

    def get_id(self):
        return self.__id

    def get_nama(self):
        return self.__nama

    def set_nama(self, nama):
        self.__nama = nama

    def get_kategori(self):
        return self.__kategori

    def set_kategori(self, kategori):
        self.__kategori = kategori

    def get_harga(self):
        return self.__harga

    def set_harga(self, harga):
        self.__harga = int(harga)

    def get_deskripsi(self):
        return self.__deskripsi

    def set_deskripsi(self, deskripsi):
        self.__deskripsi = deskripsi
