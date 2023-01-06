from sender import Send
from states import State
from bd_worker_vk import DB
from information import Info

class Admin:

    @staticmethod
    def ban_or_unbun(bot, admin_id, text):
        text = str(text)
        vk_id, is_ban = text.split()
        is_ban = bool(is_ban)
        DB.change_ban(is_ban, vk_id)
        if (is_ban):
            Send.send_message(bot, admin_id, "Пользователь заблокирован!")
        else:
            Send.send_message(bot, admin_id, "Пользователь разблокирован!")

    @staticmethod
    def change_limit(bot, admin_id, text):
        text = str(text)
        vk_id, param = text.split()
        DB.change_limit(vk_id, -int(param))
        Send.send_message(bot, admin_id, "Лимит изменён!")

    @staticmethod
    def add_paper(bot, admin_id, text):
        text = str(text)
        printer, papers = text.split()
        DB.change_paper(printer, -int(papers))
        Send.send_message(bot, admin_id, "Сведения о количестве листов изменены!")

    @staticmethod
    # заглушка
    def clean_queue_one_printer():
        print()

    @staticmethod
    def ask_info(bot, admin_id, user_id: str):
        if DB.is_user_exist(user_id):
            answer = f"vk_id: {user_id}, limit: {DB.check_limit(user_id)}, is_ban: {DB.is_user_ban(user_id)}"
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


