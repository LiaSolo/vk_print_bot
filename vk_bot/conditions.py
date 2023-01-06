from sender import Send
from states import State
from information import Info
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from bd_worker_vk import DB
from vk_config import server_addr

import requests
import PyPDF2
from datetime import datetime


start_keyboard = VkKeyboard()
start_keyboard.add_button("Начать", color=VkKeyboardColor.POSITIVE)

to_printer_keyboard = VkKeyboard()
to_printer_keyboard.add_button("К выбору принтера", color=VkKeyboardColor.POSITIVE)

admin_keyboard = VkKeyboard()
admin_keyboard.add_button("Забанить/Разбанить", color=VkKeyboardColor.POSITIVE)
admin_keyboard.add_button("Изменить лимит", color=VkKeyboardColor.POSITIVE)
admin_keyboard.add_line()
admin_keyboard.add_button("Информация", color=VkKeyboardColor.POSITIVE)
admin_keyboard.add_button("Режим ТО", color=VkKeyboardColor.POSITIVE)
admin_keyboard.add_line()
admin_keyboard.add_button("Добавить листы в принтер", color=VkKeyboardColor.POSITIVE)
admin_keyboard.add_line()
admin_keyboard.add_button("Очистка очереди печати на принтере", color=VkKeyboardColor.POSITIVE)

default_keyboard = VkKeyboard()
default_keyboard.add_button("Назад", color=VkKeyboardColor.NEGATIVE)

start_keyboard = VkKeyboard()
start_keyboard.add_button("Начать", color=VkKeyboardColor.POSITIVE)

extra_settings_keyboard = VkKeyboard()
extra_settings_keyboard.add_button("Выбрать определённые страницы", color=VkKeyboardColor.POSITIVE)
extra_settings_keyboard.add_line()
extra_settings_keyboard.add_button("Распечатать весь файл", color=VkKeyboardColor.NEGATIVE)
extra_settings_keyboard.add_line()
extra_settings_keyboard.add_button("Назад", color=VkKeyboardColor.NEGATIVE)

not_enough_pages_keyboard = VkKeyboard()
not_enough_pages_keyboard.add_button("К дополнительным настройкам", color=VkKeyboardColor.PRIMARY)
not_enough_pages_keyboard.add_line()
not_enough_pages_keyboard.add_button("К выбору файла", color=VkKeyboardColor.PRIMARY)
not_enough_pages_keyboard.add_button("К выбору принтера", color=VkKeyboardColor.NEGATIVE)

send_to_print_keyboard = VkKeyboard()
send_to_print_keyboard.add_button("Печатать", color=VkKeyboardColor.POSITIVE)
send_to_print_keyboard.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
send_to_print_keyboard.add_line()
send_to_print_keyboard.add_button("К выбору принтера", color=VkKeyboardColor.NEGATIVE)


printers_keyboard = VkKeyboard()
printers_keyboard.add_button("Принтер_1", color=VkKeyboardColor.POSITIVE)
printers_keyboard.add_button("Принтер_2", color=VkKeyboardColor.POSITIVE)



class Condition:

    @staticmethod
    def condition_help(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Опишите свою проблему.\n"
                                                      "Админы свяжутся с вами!", to_printer_keyboard)
        return State.HELP

    @staticmethod
    def condition_check_existing(bot, id_user):
        if not DB.is_user_exist(id_user):
            DB.add_user(id_user)
            Send.send_message(bot, id_user, "Авторизация прошла успешно!")


        # if not DB.is_registred(int(id_user)):
        #     DB.db_table_val(int(id_user), 50, "it")
        #     Send.send_message(bot, id_user, "Авторизация прошла успешно!")

        return Condition.condition_choose_printer(bot, id_user)

    @staticmethod
    def condition_check_ban(bot, id_user):
        if DB.is_user_ban(id_user):
            Send.send_message(bot, id_user, "Вы заблокированы!")
            return Info.positions_dict[id_user]
        else:
            return Condition.condition_send_print(bot, id_user)

    @staticmethod
    def condition_wait_file(bot, id_user):
        if DB.check_paper(Info.person_printer[id_user]) < 10:
            Send.send_message_with_keyboard(bot, id_user, "Внимание! \nВ выбранном принтере менее 10 листов!",
                                            default_keyboard)
        Send.send_message_with_keyboard(bot, id_user, "Жду pdf-файл для печати", default_keyboard)

        return State.WAIT_FOR_FILE

    @staticmethod
    def condition_process_file(bot, id_user, message):

        Send.send_message(bot, id_user, 'Пожалуйста, немного подождите')

        url = message['attachments'][0]['doc']['url']
        now = datetime.now()
        title = f"{id_user} {now.date()} {now.hour}-{now.minute}-{now.second}.pdf"
        response = requests.get(url)

        Info.titles[id_user] = title
        with open(title, 'wb') as pdf:
            pdf.write(response.content)

        return Condition.condition_extra_settings(bot, id_user)

    @staticmethod
    def condition_make_pdf(bot, id_user, pages):
        file_name = Info.titles[id_user]
        input_file = PyPDF2.PdfFileReader(file_name)
        pdf_writer = PyPDF2.PdfFileWriter()

        with open(Info.titles[id_user], 'rb') as file:
            pdf_reader = PyPDF2.PdfFileReader(file)
            num_pages = pdf_reader.getNumPages()

        for i in pages:
            try:
                if '-' in i:
                    beg, end = map(int, str(i).split('-'))
                    if beg > end or end > num_pages:
                        Send.send_message(bot, id_user, f"Неверный формат ввода!")
                        return State.WAIT_EXTRA_SETTINGS
                    for p in range(beg, end + 1):
                        pdf_writer.addPage(input_file.getPage(p - 1))
                else:
                     pdf_writer.addPage(input_file.getPage(int(i) - 1))
            except:
                Send.send_message(bot, id_user, f"Неверный формат ввода!")
                return State.WAIT_EXTRA_SETTINGS

        new_file_name = file_name + "_selected pages.pdf"
        with open(new_file_name, 'wb') as output_file:
            pdf_writer.write(output_file)
        Info.titles[id_user] = new_file_name

        return Condition.condition_ask_copies(bot, id_user)

    @staticmethod
    def condition_extra_settings(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Укажите дополнительные настройки", extra_settings_keyboard)
        return State.PRINT_SETTINGS

    @staticmethod
    def condition_choose_printer(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Выберите доступный принтер", printers_keyboard)
        return State.CHOOSE_PRINTER

    @staticmethod
    def condition_need_settings(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Введите нужные номера страниц, разделяя их пробелами. "
                                   "Интервалы страниц укажите через дефис без пробелов. "
                                   "Пример: 1 3 6-7 10-17", default_keyboard)
        return State.WAIT_EXTRA_SETTINGS

    @staticmethod
    def condition_ask_copies(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Сколько копий Вы хотите распечатать?", default_keyboard)
        return State.ASK_COPIES

    @staticmethod
    def condition_check_limit(bot, id_user):
        Send.send_message(bot, id_user, "Проверяю лимит")
        print(Info.titles)

        with open(Info.titles[id_user], 'rb') as file:
            pdf_reader = PyPDF2.PdfFileReader(file)
            num_pages = pdf_reader.getNumPages()*Info.person_copies[id_user]

        left_pages = DB.check_limit(id_user)
        text = f"Осталось {left_pages} страниц. Вы хотите распечатать {num_pages} страниц. "
        if left_pages >= num_pages:
            text += "Отправить на печать?"
            Send.send_message_with_keyboard(bot, id_user, text, send_to_print_keyboard)
            return State.LIMIT_OK
        else:
            text += "Вы не можете распечатать файл!"
            Send.send_message_with_keyboard(bot, id_user, text, not_enough_pages_keyboard)
            return State.CANT_PRINT

    @staticmethod
    def condition_send_print(bot, id_user):
        with open(Info.titles[id_user], 'rb') as file:
            pdf_reader = PyPDF2.PdfFileReader(file)
            pages = pdf_reader.getNumPages()*Info.person_copies[id_user]

        if DB.check_paper(Info.person_printer[id_user]) < pages:
            Send.send_message_with_keyboard(bot, id_user, "Извините, в принтере недостаточно бумаги!", not_enough_pages_keyboard)
            return State.CANT_PRINT
        else:
            DB.change_limit(id_user, pages)
            Send.send_message_with_keyboard(bot, id_user, "Файл отправлен на печать. До новой встречи!", to_printer_keyboard)
            Info.titles.pop(id_user)
            DB.change_paper(Info.person_printer[id_user], pages)
            Condition.condition_alarm_paper(bot, id_user)
            Info.person_printer.pop(id_user)
            Info.person_copies.pop(id_user)
            return Condition.condition_choose_printer(bot, id_user)

    @staticmethod
    def condition_alarm_paper(bot, id_user):
        if DB.check_paper(Info.person_printer[id_user]) < 10:
            for id in Info.admins:
                Send.send_message(bot, id, f"Бумага в {Info.person_printer[id_user]} скоро закончится!")

    @staticmethod
    def condition_need_help(bot, id_user, text):
        printer = Info.person_printer[id_user]
        for id in Info.admins:
            Send.send_message(bot, id,
                              f"СООБЩЕНИЕ ОБ ОШИБКЕ\n"
                              f"vk_id: {id_user}; printer: {printer}; file: {Info.titles[id_user]}\n"
                              f"Текст сообщения:\n{text}")
        Send.send_message_with_keyboard(bot, id_user, "Сообщение успешно отправлено!", to_printer_keyboard)
        return State.WAIT_FOR_START

    @staticmethod
    def admin_on(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Вы находитесь в режиме админа", admin_keyboard)
        return State.ADMIN_MODE

    @staticmethod
    def admin_off(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Вы вышли из режима админа", to_printer_keyboard)
        return Condition.condition_choose_printer(bot, id_user)

    @staticmethod
    def condition_change_ban(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user,
                                        "Укажите vk_id человека и параметр блокировки "
                                        "(True - забанить, False - разбанить)", default_keyboard)
        return State.CHANGE_BAN

    @staticmethod
    def condition_admin_change_limit(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user,
                                        "Укажите через пробел vk_id человека и параметр изменения количества"
                                        " (-5 - уменьшить на 5 листов, +5 - увеличить на 5 листов)",
                                        default_keyboard)
        return State.CHANGE_LIMIT

    @staticmethod
    def condition_add_paper(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user,
                                        "Укажите через пробел название принтера и "
                                        "сколько листов (примерно) было добавлено",
                                        default_keyboard)
        return State.ADD_PAPER

    @staticmethod
    def condition_clean_queue_one(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user,
                                        "",
                                        default_keyboard)
        return State

    @staticmethod
    def condition_maintenance(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user,
                                        "Введите параметр (on - включить режим техобслуживания, off - выключить",
                                        default_keyboard)
        return State.MAINTENANCE

    @staticmethod
    def condition_on_TO(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user,
                                        "Извините, я на техобслуживании! Приходите позже!",
                                        default_keyboard)

    @staticmethod
    def condition_ask_info(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user,
                                        "Укажите vk_id нужного пользователя",
                                        default_keyboard)
        return State.ASK_INFO

    # @staticmethod
    # def print_action(id_user, context):
    #     req = server_addr + '/add_task?printer={}&user={}&task=print&file={}&pages={}&copies={}'.format(
    #         Info.person_printer[id_user], # printer
    #         id_user, # user
    #         Info.titles[id_user], # file
    #         Info.person_pages[id_user], #pages
    #         Info.person_pages[id_user] #copies
    #     )
    #     print('print_action')
    #     r = requests.post(req, data={'token': token})
    #     print(r.content)
