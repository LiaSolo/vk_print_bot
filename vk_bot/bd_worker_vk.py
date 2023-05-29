import requests
from vk_config import api_token, server_addr


class DB:
    @staticmethod
    def is_registered(user_id: int):
        r = requests.post(server_addr + "/api/bd/{}".format('is_registered'),
                          data={'token': api_token, 'user_id': user_id, 'vk_or_tg': 'vk'})
        print(r.content)
        return eval(r.content)

    # add new user
    @staticmethod
    def db_table_val(user_id: int, limit: int, isu: str):
        requests.post(server_addr + "/api/bd/{}".format('db_table_val'),
                      data={'token': api_token, 'user_id': user_id, 'limit': limit, 'isu': isu, 'vk_or_tg': 'vk'})

    # data by vk id
    @staticmethod
    def data_by_id(user_id: int):
        r = requests.post(server_addr + "/api/bd/{}".format('data_by_id'),
                          data={'token': api_token, 'user_id': user_id, 'vk_or_tg': 'vk'})
        return eval(r.content)

    @staticmethod
    def change_status_session(value: str, user_id: int):
        r = requests.post(server_addr + "/api/bd/{}".format('change_status_session'),
                          data={'token': api_token, 'vk_id': user_id, 'session': value, 'vk_or_tg': 'vk'})
        return r.content

    @staticmethod
    def add_vk(user_id: int, itmo_id: int):
        r = requests.post(server_addr + "/api/bd/{}".format('add_tg_vk'),
                          data={'token': api_token, 'user_id': user_id, 'itmo_id': itmo_id, 'vk_or_tg': 'vk'})
        return r.content

    @staticmethod
    def set_limit(user_id: int, count: int):
        r = requests.post(server_addr + "/api/bd/{}".format('set_limit'),
                          data={'token': api_token, 'user_id': user_id, 'count': count, 'vk_or_tg': 'vk'})
        return r.content

    @staticmethod
    def ban_bd(value, flag: bool):
        r = requests.post(server_addr + "/api/bd/{}".format('ban_bd'),
                          data={'token': api_token, 'id_type': 'vk_id', 'value': value, 'flag': flag})
        return r.content

    @staticmethod
    def get_statistics():
        r = requests.post(server_addr + "/api/bd/{}".format('get_statistics'),
                          data={'token': api_token})
        return r.content

    @staticmethod
    def set_paper_count_bd(printer: str, value: int):
        r = requests.post(server_addr + "/api/bd/{}".format('set_paper_count'),
                          data={'token': api_token, 'printer': printer, 'value': value})
        return r.content

    @staticmethod
    def get_paper_count_bd(printer: str):
        r = requests.post(server_addr + "/api/bd/{}".format('get_paper_count'),
                          data={'token': api_token, 'printer': printer})
        return eval(r.content)

    @staticmethod
    def check_is_alarmed_bd(printer: str):
        r = requests.post(server_addr + "/api/bd/{}".format('check_is_alarmed'),
                          data={'token': api_token, 'printer': printer})
        return eval(r.content)

    @staticmethod
    def set_is_alarmed_bd(printer: str, value: bool):
        r = requests.post(server_addr + "/api/bd/{}".format('set_is_alarmed'),
                          data={'token': api_token, 'printer': printer, 'value': value})
        return r.content

    @staticmethod
    def set_cancel_queue_flag_bd(printer: str, value: bool):
        r = requests.post(server_addr + "/api/bd/{}".format('set_cancel_queue_flag'),
                          data={'token': api_token, 'printer': printer, 'value': value})
        print(r.content)
        return r.content
