"""Model data pemilik hewan."""


class Pemilik:
    def __init__(self, nama, telepon, alamat="", pemilik_id=None):
        self.__id = pemilik_id
        self.__nama = nama
        self.__telepon = telepon
        self.__alamat = alamat

    def get_id(self):
        return self.__id

    def get_nama(self):
        return self.__nama

    def set_nama(self, nama):
        self.__nama = nama

    def get_telepon(self):
        return self.__telepon

    def set_telepon(self, telepon):
        self.__telepon = telepon

    def get_alamat(self):
        return self.__alamat

    def set_alamat(self, alamat):
        self.__alamat = alamat
