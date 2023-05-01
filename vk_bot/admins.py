from sender import Send
from bd_worker_vk import DB
from conditions import Condition


class Admin:

    @staticmethod
    def ban_or_unban(bot, admin_id, text):
        text = str(text)
        vk_id, is_ban = text.split()
        is_ban = bool(is_ban)
        DB.change_ban(is_ban, vk_id)
        if is_ban:
            Send.send_message(bot, admin_id, "Пользователь заблокирован!")
        else:
            Send.send_message(bot, admin_id, "Пользователь разблокирован!")

    @staticmethod
    def get_statistics(bot, admin_id):
        Send.send_message(bot, admin_id, DB.get_statistics())

    @staticmethod
    def change_limit(bot, admin_id, text):
        text = str(text)
        vk_id, param = map(int, text.split())

        DB.set_limit(vk_id, DB.data_by_id(vk_id)[0][2] + param)
        Send.send_message(bot, admin_id, "Лимит изменён!")

    @staticmethod
    def add_paper(bot, admin_id, text):
        text = str(text)
        printer, papers = text.split()

        DB.set_paper_count_bd(printer, DB.get_paper_count_bd(printer) + int(papers))
        Condition.condition_alarm_paper(bot, printer)
        Send.send_message(bot, admin_id, "Сведения о количестве листов изменены!")

    @staticmethod
    # заглушка
    def clean_queue_one_printer(bot, admin_id, printer):
        DB.set_cancel_queue_flag_bd(printer, True)
        Send.send_message(bot, admin_id, "Запрос на очистку очереди печати на принтере отправлен")

    @staticmethod
    def ask_info(bot, admin_id, user_id):
        if DB.is_registred(int(user_id)):
            info_user = DB.data_by_id(user_id)[0]
            answer = f"vk_id: {info_user[1]}, limit: {info_user[2]}, itmo_id: {info_user[3]} is_ban: {info_user[4]}"
        else:
            answer = "Пользователя с таким vk_id не существует"
        Send.send_message(bot, admin_id, answer)

    @staticmethod
    def maintenance(bot, admin_id, mode: str):
        with open("TO.txt", 'w') as file:
            file.write(mode)
        if mode == "on":
            Send.send_message(bot, admin_id, "Режим ТО активирован")
        else:
            Send.send_message(bot, admin_id, "Режим ТО выключен")
