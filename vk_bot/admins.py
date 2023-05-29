from json import dump
from bd_worker_vk import DB
from conditions import Condition
from sender import Send
from vk_config import printers_names, printers


class Admin:
    @staticmethod
    def ban_or_unban(bot, admin_id, text):
        text = str(text)

        try:
            vk_id, is_ban = text.split()
            if is_ban != 'True' and is_ban != 'False':
                raise Exception()
            if DB.is_registered(vk_id):
                DB.ban_bd(vk_id, is_ban)
                if is_ban == 'True':
                    Send.send_message(bot, admin_id, "Пользователь заблокирован!")
                else:
                    Send.send_message(bot, admin_id, "Пользователь разблокирован!")
            else:
                Send.send_message(bot, admin_id, "Такого пользователя не существует!")
        except ValueError:
            Send.send_message(bot, admin_id, "Неверный ввод!")

    @staticmethod
    def get_statistics(bot, admin_id):
        info = DB.get_statistics().decode().lstrip("[(Decimal('").rstrip(")]").split("'), ")
        text = f"Распечатано страниц: {info[0]}. Пользователей авторизовано: {info[1]}"
        Send.send_message(bot, admin_id, text)

    @staticmethod
    def change_limit(bot, admin_id, text):
        text = str(text)
        try:
            vk_id, param = map(int, text.split())
            if DB.is_registered(vk_id):
                DB.set_limit(vk_id, DB.data_by_id(vk_id)[0][2] + param)
                Send.send_message(bot, admin_id, "Лимит изменён!")
            else:
                Send.send_message(bot, admin_id, "Такого пользователя не существует!")
        except ValueError:
            Send.send_message(bot, admin_id, "Неверный ввод!")

    @staticmethod
    def add_paper(bot, admin_id, text):
        text = str(text)
        try:
            printer, papers = text.split()
            if printer not in {'Lomo', 'Gk'}:
                Send.send_message(bot, admin_id, "Такого принтера не существует!")
            else:
                DB.set_paper_count_bd(printer, DB.get_paper_count_bd(printer) + int(papers))
                Condition.control_alarm_paper(bot, printer)
                Send.send_message(bot, admin_id, "Сведения о количестве листов изменены!")
        except ValueError:
            Send.send_message(bot, admin_id, "Неверный ввод!")

    @staticmethod
    def clean_queue_one_printer(bot, admin_id, printer):
        if printer in printers:
            DB.set_cancel_queue_flag_bd(printers_names[printer], True)
            Send.send_message(bot, admin_id, "Запрос на очистку очереди печати на принтере отправлен")
        else:
            Send.send_message(bot, admin_id, "Такого принтера не существует!")

    @staticmethod
    def ask_info(bot, admin_id, user_id):
        try:
            if DB.is_registered(int(user_id)):
                info_user = DB.data_by_id(user_id)[0]
                answer = f"vk_id: {info_user[5]}, tg_id: {info_user[1]},  itmo_id: {info_user[3]}, " \
                         f"limit: {info_user[2]}, is_banned: {info_user[4]}, session: {info_user[6]}"
            else:
                answer = "Пользователя с таким vk_id не существует"
            Send.send_message(bot, admin_id, answer)
        except ValueError:
            Send.send_message(bot, admin_id, "Неверный ввод!")

    @staticmethod
    def maintenance(bot, admin_id, mode: str):
        with open("TO.json", 'w') as file:
            dump({"service_mode": str(not mode)}, file)
            if mode:
                Send.send_message(bot, admin_id, "Режим ТО выключен")
            else:
                Send.send_message(bot, admin_id, "Режим ТО активирован")
