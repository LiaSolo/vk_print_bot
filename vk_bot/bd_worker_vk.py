import psycopg2
import requests
from vk_config import server_addr, api_token


class DB:

    @staticmethod
    def is_registred(user_id: int):
        r = requests.post(server_addr + "/api/bd/{}".format('is_registred'), data=
        {'user_id': user_id, 'vk_or_tg': 'vk'})
        print(r.content)
        return eval(r.content)

    # add new user
    @staticmethod
    def db_table_val(user_id: int, limit: int, isu: str):
        r = requests.post(server_addr + "/api/bd/{}".format('db_table_val'), data=
        {'user_id': user_id, 'limit': limit, 'isu': isu, 'vk_or_tg': 'vk'})
        print(r.content)
        # return r.content

    # данные по вк айди
    @staticmethod
    def data_by_id(user_id: int):
        r = requests.post(server_addr + "/api/bd/{}".format('data_by_id'), data=
        {'user_id': user_id, 'vk_or_tg': 'vk'})
        return eval(r.content)

    @staticmethod
    def data_by_itmo_id(itmo_id: str):
        r = requests.post(server_addr + "/api/bd/{}".format('data_by_itmo_id'), data=
        {'itmo_id': itmo_id})
        return eval(r.content)

    # забанить/разбанить
    @staticmethod
    def ban_bd(key: str, value): # что за что отвечает ?
        r = requests.post(server_addr + "/api/bd/{}".format('ban_bd'), data=
        {'key': key, 'value': value})
        return r.content

    @staticmethod
    def set_paper_count_bd(printer: str, value: int):
        r = requests.post(server_addr + "/api/bd/{}".format('set_paper_count'), data=
        {'printer': printer, 'value': value})
        return r.content

    @staticmethod
    def get_paper_count_bd(printer: str):
        r = requests.post(server_addr + "/api/bd/{}".format('get_paper_count'), data=
        {'printer': printer})
        return eval(r.content)

    @staticmethod
    def set_limit(user_id: int, count: int):
        r = requests.post(server_addr + "/api/bd/{}".format('set_limit'), data=
        {'user_id': user_id, 'count': count, 'vk_or_tg': 'vk'})
        return r.content

    @staticmethod
    def check_is_alarmed_bd(printer: str):
        r = requests.post(server_addr + "/api/bd/{}".format('check_is_alarmed'), data=
        {'printer': printer})
        return eval(r.content)

    @staticmethod
    def set_is_alarmed_bd(printer: str, value: bool):
        r = requests.post(server_addr + "/api/bd/{}".format('set_is_alarmed'), data=
        {'printer': printer, 'value': value})
        return r.content

    @staticmethod
    def set_cancel_queue_flag_bd(printer: str, value: bool):
        r = requests.post(server_addr + "/api/bd/{}".format('set_cancel_queue_flag'), data=
        {'printer': printer, 'value': value})
        print(r.content)
        return r.content

    @staticmethod
    def get_statistics():
        r = requests.post(server_addr + "/api/bd/{}".format('get_statistics'))
        return r.content

    @staticmethod
    def change_status_session(value: str, user_id: int):
        r = requests.post(server_addr + "/api/bd/{}".format('change_status_session'), data=
        {'vk_id': user_id, 'session': value, 'vk_or_tg': 'vk'})
        return r.content

    @staticmethod
    def add_vk(user_id: int, itmo_id: int):
        r = requests.post(server_addr + "/api/bd/{}".format('add_tg_vk'), data=
        {'user_id': user_id, 'itmo_id': itmo_id, 'vk_or_tg': 'vk'})
        return r.content




    @staticmethod
    def create_connection():
        connection = psycopg2.connect(
            database="itmo_print_db",
            user="postgres",
            password="1",
            host="127.0.0.1",
            port="5432", )
        return connection

    @staticmethod
    def change_ban(is_ban, user_id):
        # false - не забанен
        # true - забанен
        connection = DB.create_connection()
        cursor = connection.cursor()
        query = "UPDATE users SET is_ban = %s WHERE vk_id = %s"
        cursor.execute(query, (is_ban, user_id))
        connection.commit()
        cursor.close()
        connection.close()
