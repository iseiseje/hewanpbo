"""Model transaksi penitipan."""


class Transaksi:
    def __init__(self, hewan_id, kandang_id, tanggal_masuk, tanggal_keluar,
                 lama_hari, total_biaya, transaksi_id=None):
        self.__id = transaksi_id
        self.__hewan_id = hewan_id
        self.__kandang_id = kandang_id
        self.__tanggal_masuk = tanggal_masuk
        self.__tanggal_keluar = tanggal_keluar
        self.__lama_hari = int(lama_hari)
        self.__total_biaya = int(total_biaya)

    def get_id(self):
        return self.__id

    def get_hewan_id(self):
        return self.__hewan_id

    def get_kandang_id(self):
        return self.__kandang_id

    def get_tanggal_masuk(self):
        return self.__tanggal_masuk

    def get_tanggal_keluar(self):
        return self.__tanggal_keluar

    def get_lama_hari(self):
        return self.__lama_hari

    def get_total_biaya(self):
        return self.__total_biaya
