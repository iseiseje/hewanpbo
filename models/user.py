"""Model pegawai dengan atribut terenkapsulasi (encapsulation)."""


class User:
    def __init__(self, nama, username, password, role="Pegawai", user_id=None):
        self.__id = user_id
        self.__nama = nama
        self.__username = username
        self.__password = password
        self.__role = role

    def get_id(self):
        return self.__id

    def get_nama(self):
        return self.__nama

    def set_nama(self, nama):
        self.__nama = nama

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def set_password(self, password):
        self.__password = password

    def get_role(self):
        return self.__role
