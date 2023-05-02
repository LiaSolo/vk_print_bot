import random

from sender import Send
from states import State
from information import Info
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from bd_worker_vk import DB
from vk_config import server_addr, email, email_password
import os
import requests
import PyPDF2
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


start_keyboard = VkKeyboard()
start_keyboard.add_button("Начать", color=VkKeyboardColor.POSITIVE)

to_printer_keyboard = VkKeyboard()
to_printer_keyboard.add_button("К выбору принтера", color=VkKeyboardColor.POSITIVE)

admin_keyboard = VkKeyboard()
admin_keyboard.add_button("Забанить", color=VkKeyboardColor.POSITIVE)
admin_keyboard.add_button("Изменить лимит", color=VkKeyboardColor.POSITIVE)
admin_keyboard.add_line()
admin_keyboard.add_button("Режим ТО", color=VkKeyboardColor.POSITIVE)
admin_keyboard.add_line()
admin_keyboard.add_button("Информация", color=VkKeyboardColor.POSITIVE)
admin_keyboard.add_button("Статистика", color=VkKeyboardColor.POSITIVE)
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
extra_settings_keyboard.add_button("Распечатать весь файл", color=VkKeyboardColor.POSITIVE)
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
printers_keyboard.add_button("L364-Series", color=VkKeyboardColor.POSITIVE)
printers_keyboard.add_button("ML-1660-Series", color=VkKeyboardColor.POSITIVE)


class Condition:

    @staticmethod
    def condition_help(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Опишите свою проблему.\n"
                                                      "Админы свяжутся с вами!", to_printer_keyboard)
        return State.HELP

    @staticmethod
    def condition_check_existing(bot, id_user):
        if not DB.is_registred(int(id_user)):
            Send.send_message(bot, id_user, "Необходима авторизация!")
            return Condition.ask_mail(bot, id_user)
        return Condition.condition_choose_printer(bot, id_user)

    @staticmethod
    def auth_done(bot, id_user):
        info = DB.data_by_itmo_id(Info.person_st[id_user])
        if info == []:
            DB.db_table_val(int(id_user), 50, Info.person_st[id_user])
        else:
            DB.add_vk(id_user, info[0][3])
        Info.person_st.pop(id_user)
        Info.person_code.pop(id_user)
        Send.send_message(bot, id_user, "Авторизация прошла успешно!")
        return Condition.condition_choose_printer(bot, id_user)

    @staticmethod
    def ask_mail(bot, id_user):
        Send.send_message(bot, id_user, 'Введите свой логин единой учетной записи в формате st******')
        return State.WAIT_MAIL

    @staticmethod
    def send_code(bot, id_user, st):
        code = ''
        for i in range(4):
            code += str(random.randint(0, 9))
        Info.person_code[id_user] = code

        address_to = st + '@student.spbu.ru'

        message = MIMEMultipart()
        message['From'] = email
        message['To'] = address_to
        message['Subject'] = 'Код для авторизации бота печати'
        message.attach(MIMEText('Код: ' + code))

        smtp_obj = smtplib.SMTP_SSL('smtp.yandex.ru', 465)

        smtp_obj.login(email, email_password)
        smtp_obj.send_message(message)
        smtp_obj.quit()

        Send.send_message(bot, id_user, 'Код для подтверждения отправлен на указанную электронную почту')
        Send.send_message(bot, id_user, 'Введите код')
        return State.WAIT_CODE

    @staticmethod
    def condition_choose_printer(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Выберите доступный принтер", printers_keyboard)
        return State.CHOOSE_PRINTER

    @staticmethod
    def condition_wait_file(bot, id_user):
        if DB.check_is_alarmed_bd(Info.person_printer[id_user]):
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
        full_path = os.path.join('C:\\Users\\samos\\PycharmProjects\\vk_print_bot\\files_to_send', title)
        with open(full_path, 'wb+') as pdf:
            pdf.write(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf)
            Info.person_pages[id_user] = len(pdf_reader.pages)

        return Condition.condition_extra_settings(bot, id_user)

    @staticmethod
    def condition_make_pdf(bot, id_user, pages):
        file_name = Info.titles[id_user]
        full_path = os.path.join('C:\\Users\\samos\\PycharmProjects\\vk_print_bot\\files_to_send', file_name)
        input_file = PyPDF2.PdfReader(full_path)
        pdf_writer = PyPDF2.PdfWriter()

        with open(full_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

        for i in pages:
            try:
                if '-' in i:
                    beg, end = map(int, str(i).split('-'))
                    if beg > end or end > num_pages:
                        Send.send_message(bot, id_user, f"Неверный формат ввода!")
                        return State.WAIT_EXTRA_SETTINGS
                    for p in range(beg, end + 1):
                        pdf_writer.add_page(input_file.pages[p - 1])
                else:
                     pdf_writer.add_page(input_file.pages[int(i) - 1])
            except:
                Send.send_message(bot, id_user, f"Неверный формат ввода!")
                return State.WAIT_EXTRA_SETTINGS

        new_file_name = file_name + "_selected pages.pdf"
        Info.titles[id_user] = new_file_name

        full_path = os.path.join('C:\\Users\\samos\\PycharmProjects\\vk_print_bot\\files_to_send', new_file_name)
        with open(full_path, 'wb+') as output_file:
            pdf_writer.write(output_file)
            Info.person_pages[id_user] = len(PyPDF2.PdfReader(output_file).pages)

        return Condition.condition_ask_copies(bot, id_user)

    @staticmethod
    def condition_extra_settings(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Укажите дополнительные настройки", extra_settings_keyboard)
        return State.PRINT_SETTINGS

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
    def active_session_exist(bot, id_user):
        what_session = (DB.data_by_id(int(id_user)))[0][5]
        if what_session == 'vk':
            DB.change_status_session('none', id_user)
        return Condition.condition_ask_copies(bot, id_user)

    @staticmethod
    def condition_full_check(bot, id_user):
        info_user = (DB.data_by_id(int(id_user)))[0]
        session = info_user[5]
        if session != 'none':
            Send.send_message_with_keyboard(bot, id_user, "Вы не можете печатать, "
                                                          "так как у Вас уже есть активная сессия в telegram!",
                                            default_keyboard)
            return State.ACTIVE_SESSION

        DB.change_status_session('vk', id_user)
        cur_limit = info_user[2]
        pages = Info.person_pages[id_user] * Info.person_copies[id_user]
        is_ban = info_user[4]
        full_path = os.path.join('C:\\Users\\samos\\PycharmProjects\\vk_print_bot\\files_to_send', Info.titles[id_user])
        size_byte = os.stat(full_path).st_size
        if size_byte > 20971520: # 20 Mb
            Send.send_message_with_keyboard(bot, id_user, "Файл превышает 20 Мб!", not_enough_pages_keyboard)
            DB.change_status_session('none', id_user)
            return State.CANT_PRINT

        if is_ban:
            Send.send_message(bot, id_user, "Вы заблокированы!")
            DB.change_status_session('none', id_user)
            return Info.positions_dict[id_user]
        else:
            text = f"Осталось {cur_limit} страниц. Вы хотите распечатать {pages} страниц. "
            if cur_limit >= pages:
                text += "Отправить на печать?"
                Send.send_message_with_keyboard(bot, id_user, text, send_to_print_keyboard)
                return State.LIMIT_OK
            else:
                text += "Вы не можете распечатать файл!"
                Send.send_message_with_keyboard(bot, id_user, text, not_enough_pages_keyboard)
                DB.change_status_session('none', id_user)
                return State.CANT_PRINT

    @staticmethod
    def condition_send_print(bot, id_user):
        printer = Info.person_printer[id_user]
        pages = Info.person_pages[id_user]
        copies = Info.person_copies[id_user]

        req = server_addr + '/add_task?printer={}&user={}&task=print&file={}&pages={}&copies={}'.format(
            printer,
            id_user,
            Info.titles[id_user],  # file
            pages,
            copies
        )

        all_pages = pages * copies
        paper_in_printer = DB.get_paper_count_bd(printer)

        if paper_in_printer < all_pages:
            Send.send_message_with_keyboard(bot, id_user, "Извините, в принтере недостаточно бумаги!",
                                            not_enough_pages_keyboard)
            Info.person_printer.pop(id_user)
            Info.person_copies.pop(id_user)
            DB.change_status_session('none', id_user)
            return State.CANT_PRINT
        else:
            print('print_action')
            r = requests.post(req)
            print(r.content)
            Send.send_message_with_keyboard(bot, id_user, "Файл отправлен на печать. До новой встречи!",
                                            to_printer_keyboard)
            Info.titles.pop(id_user)
            Info.person_printer.pop(id_user)
            Info.person_copies.pop(id_user)

            DB.set_limit(id_user, DB.data_by_id(int(id_user))[0][2] - all_pages)
            DB.set_paper_count_bd(printer, paper_in_printer - all_pages)
            DB.change_status_session('none', id_user)

            Condition.condition_alarm_paper(bot, printer)
            return Condition.condition_choose_printer(bot, id_user)

    @staticmethod
    def condition_alarm_paper(bot, printer):
        if DB.get_paper_count_bd(printer) < 10:
            if not DB.check_is_alarmed_bd(printer):
                DB.set_is_alarmed_bd(printer, True)
                for id in Info.admins:
                    Send.send_message(bot, id, f"В {printer} менее 10 листов!")
        else:
            if DB.check_is_alarmed_bd(printer):
                DB.set_is_alarmed_bd(printer, False)
                for id in Info.admins:
                    Send.send_message(bot, id, f"В {printer} добавлена бумага!")

    @staticmethod
    def condition_need_help(bot, id_user, text):
        # printer = Info.person_printer[id_user]
        for id in Info.admins:
            Send.send_message(bot, id,
                              f"СООБЩЕНИЕ ОБ ОШИБКЕ\n"
                              f"vk_id: {id_user}\n"
                              f"Текст сообщения:\n{text}")
        Send.send_message_with_keyboard(bot, id_user, "Сообщение успешно отправлено!", to_printer_keyboard)
        return Condition.condition_choose_printer(bot, id_user)

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
                                        "Укажите название принтера",
                                        printers_keyboard)
        return State.CLEAR_QUEUE

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
