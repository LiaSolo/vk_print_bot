import psycopg2
import requests
from vk_config import server_addr, api_token


class DB:

    @staticmethod
    def is_registred(user_id: int):
        r = requests.post(server_addr + "/api/bd/{}".format('is_registred'), data=
        {'user_id': user_id})
        print(r.content)
        return eval(r.content)

    @staticmethod
    def db_table_val(user_id: int, limit: int, isu: str):
        r = requests.post(server_addr + "/api/bd/{}".format('db_table_val'), data=
        {'user_id': user_id, 'limit': limit, 'isu': isu})
        print(r.content)
        # return r.content
    @staticmethod
    def create_connection():
        connection = psycopg2.connect(
            # database="itmo_print_db",
            # user="postgres",
            # password="1",
            database="mydb",
            user="vk_bot",
            password="2",
            host="127.0.0.1",
            port="5432", )
        return connection

    @staticmethod
    def is_user_exist(user_id: str):
        connection = DB.create_connection()
        cursor = connection.cursor()
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE vk_id = %s)"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return result[0]

    @staticmethod
    def is_user_ban(user_id: str):
        connection = DB.create_connection()
        cursor = connection.cursor()
        query = "SELECT is_ban FROM users WHERE vk_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return result[0]

    @staticmethod
    def add_user(user_id: str):
        connection = DB.create_connection()
        cursor = connection.cursor()
        query = "INSERT INTO users (vk_id, limits, is_ban) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, 100, False))
        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def change_limit(user_id: str, minus: int):
        connection = DB.create_connection()
        cursor = connection.cursor()
        current_limit = DB.check_limit(user_id)
        new_limit = current_limit - minus
        query = "UPDATE users SET limits = %s WHERE vk_id = %s"
        cursor.execute(query, (new_limit, user_id))
        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def check_limit(user_id: str):
        connection = DB.create_connection()
        cursor = connection.cursor()
        query = "SELECT limits FROM users WHERE vk_id = %s"
        cursor.execute(query, (user_id,))
        limit = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return limit[0]

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

    @staticmethod
    def check_paper(printer: str):
        connection = DB.create_connection()
        cursor = connection.cursor()
        query = "SELECT paper FROM printers WHERE printer_name = %s"
        cursor.execute(query, (printer,))
        limit = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return limit[0]

    @staticmethod
    def change_paper(printer: str, minus):
        connection = DB.create_connection()
        cursor = connection.cursor()
        current_paper = DB.check_paper(printer)
        new_paper = current_paper - minus
        query = "UPDATE printers SET paper = %s WHERE printer_name = %s"
        cursor.execute(query, (new_paper, printer))
        connection.commit()
        cursor.close()
        connection.close()
