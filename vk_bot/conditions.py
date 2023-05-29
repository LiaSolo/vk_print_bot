from datetime import datetime, timedelta
import os
import jwt
import PyPDF2
import requests
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from bd_worker_vk import DB
from information import Info
from sender import Send
from states import State
from vk_config import admins, alarm_paper, api_token, auth_link, jwt_secret, server_addr

to_printer_keyboard = VkKeyboard()
to_printer_keyboard.add_button("К выбору принтера", color=VkKeyboardColor.POSITIVE)

auth_keyboard = VkKeyboard()
auth_keyboard.add_button("Я залогинился", color=VkKeyboardColor.POSITIVE)
auth_keyboard.add_line()
auth_keyboard.add_button("Перевыпустить ссылку", color=VkKeyboardColor.POSITIVE)

admin_keyboard = VkKeyboard()
admin_keyboard.add_button("Бан>", color=VkKeyboardColor.POSITIVE)
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

copies_keyboard = VkKeyboard()
copies_keyboard.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
copies_keyboard.add_button("Далее", color=VkKeyboardColor.POSITIVE)

try_now_keyboard = VkKeyboard()
try_now_keyboard.add_button("Попробуй снова", color=VkKeyboardColor.POSITIVE)
try_now_keyboard.add_button("Назад", color=VkKeyboardColor.NEGATIVE)

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
printers_keyboard.add_button('Ломоносова, 9', color=VkKeyboardColor.POSITIVE)
printers_keyboard.add_button('Кронверкский, 49', color=VkKeyboardColor.POSITIVE)


class Condition:

    @staticmethod
    def create_link(id_user):
        dt = datetime.now() + timedelta(hours=1)
        encoded_token = jwt.encode({'vk_id': id_user, 'exp': dt}, jwt_secret,
                                   algorithm='HS256')
        link = auth_link + '/auth&state=' + encoded_token.decode()
        client_id = ''
        link = '' \
               + 'client_id=' + client_id + '&response_type=code' + '&scope=openid' + '&redirect_uri={}'.format(link)
        return link

    @staticmethod
    def condition_help(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Опишите свою проблему.\n"
                                                      "Админы свяжутся с вами!", to_printer_keyboard)
        return State.HELP

    @staticmethod
    def check_existing(bot, id_user):
        if not DB.is_registered(int(id_user)):
            Send.send_message(bot, id_user, 'Правила использования ITMO.Print:'
                                            '\n1⃣ печатать, находясь в непосредственной близости от принтера;'
                                            '\n2⃣не злоупотреблять инфраструктурой;'
                                            '\n3⃣не совершать атаки;'
                                            '\n4⃣не трогать принтер руками (если возникла неполадка, '
                                            'отметьтесь в соответствующем разделе меню).'
                                            '\nВ случае выявления нарушений, виновники будут приглашены на '
                                            'воспитательную беседу, где будет решаться вопрос'
                                            'о применении дисциплинарных взысканий в зависимости от тяжести проступка. '
                                            'Продолжая, вы соглашаетесь с данными правилами.')
            return Condition.registration(bot, id_user)
        return Condition.choose_printer(bot, id_user)

    @staticmethod
    def registration(bot, id_user):
        Send.send_message(bot, id_user, "❗❗❗Чтобы воспользоваться сервисом печати, "
                                        "необходима авторизация! Пожалуйста, перейдите по ссылке")
        Send.send_message_with_keyboard(bot, id_user, Condition.create_link(id_user), auth_keyboard)
        Send.send_message(bot, id_user,
                          "✉При возникновении проблем в любой момент напишите Help, чтобы отправить сообщение админам")
        return State.REGISTRATION

    @staticmethod
    def choose_printer(bot, id_user):
        cur_lim = DB.data_by_id(int(id_user))[0][2]
        Send.send_message(bot, id_user, f"Осталось страниц: {cur_lim}")
        Send.send_message_with_keyboard(bot, id_user, "Выберите доступный принтер", printers_keyboard)
        return State.CHOOSE_PRINTER

    @staticmethod
    def wait_file(bot, id_user):
        paper = DB.get_paper_count_bd(Info.person_printer[id_user])
        Send.send_message_with_keyboard(bot, id_user, f"В выбранном принтере примерно {paper} листов",
                                        default_keyboard)
        Send.send_message_with_keyboard(bot, id_user, "Жду pdf-файл для печати", default_keyboard)

        return State.WAIT_FILE

    @staticmethod
    def process_file(bot, id_user, message):

        Send.send_message(bot, id_user, 'Пожалуйста, немного подождите')

        try:
            url = message['attachments'][0]['doc']['url']
            now = datetime.now()
            title = f"{id_user} {now.date()} {now.hour}-{now.minute}-{now.second}.pdf"
            response = requests.get(url)

            Info.titles[id_user] = title
            full_path = os.path.join('../files_to_send', title)
            with open(full_path, 'wb+') as pdf:
                pdf.write(response.content)
                pdf_reader = PyPDF2.PdfFileReader(pdf)
                Info.person_pages[id_user] = len(pdf_reader.pages)

            cur_lim = (DB.data_by_id(int(id_user)))[0][2]
            Send.send_message(bot, id_user, f'Страниц в файле: {Info.person_pages[id_user]}.\
                              \nТекущий лимит: {cur_lim}.')

            return Condition.wait_extra_settings(bot, id_user)
        except PyPDF2.utils.PdfReadError:
            Send.send_message(bot, id_user, 'Ошибка при обработке файла')
            Send.send_message_with_keyboard(bot, id_user, "Жду pdf-файл для печати", default_keyboard)
            return State.WAIT_FILE

    @staticmethod
    def make_pdf(bot, id_user, pages):
        file_name = Info.titles[id_user]
        full_path = os.path.join('../files_to_send', file_name)
        input_file = PyPDF2.PdfReader(full_path)
        pdf_writer = PyPDF2.PdfWriter()

        with open(full_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

        for i in pages:
            try:
                if '-' in i:
                    if i[0] == '-' and int(i) < 0:
                        Send.send_message(bot, id_user, f"Пожалуйста, используйте натуральные числа!")
                        return State.WAIT_EXTRA_SETTINGS
                    beg, end = map(int, str(i).split('-'))
                    if beg > end:
                        Send.send_message(bot, id_user, f"Неверный диапазон!")
                        return State.WAIT_EXTRA_SETTINGS
                    elif end > num_pages or beg > num_pages:
                        Send.send_message(bot, id_user, f"Указанный диапазон не соответствует размеру файла!")
                        return State.WAIT_EXTRA_SETTINGS
                    for p in range(beg, end + 1):
                        pdf_writer.addPage(input_file.pages[p - 1])
                elif int(i) == 0:
                    Send.send_message(bot, id_user, f"Пожалуйста, используйте натуральные числа!")
                    return State.WAIT_EXTRA_SETTINGS
                elif int(i) > num_pages:
                    Send.send_message(bot, id_user, f"Указанный диапазон не соответствует размеру файла!")
                    return State.WAIT_EXTRA_SETTINGS
                else:
                    pdf_writer.addPage(input_file.pages[int(i) - 1])
            except ValueError:
                Send.send_message(bot, id_user, f"Пожалуйста, следуйте шаблону!")
                return State.WAIT_EXTRA_SETTINGS

        new_file_name = file_name + "_selected pages.pdf"
        Info.titles[id_user] = new_file_name

        full_path = os.path.join('../files_to_send', new_file_name)
        with open(full_path, 'wb+') as output_file:
            pdf_writer.write(output_file)
            Info.person_pages[id_user] = len(PyPDF2.PdfReader(output_file).pages)

        cur_lim = (DB.data_by_id(int(id_user)))[0][2]
        Send.send_message(bot, id_user, f'Страниц в файле: {Info.person_pages[id_user]}.'
                                        f'\nТекущий лимит: {cur_lim}.')

        return Condition.ask_copies(bot, id_user)

    @staticmethod
    def wait_extra_settings(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Укажите дополнительные настройки. "
                                                      "Выберите из предложенных вариантов ответа",
                                        extra_settings_keyboard)
        return State.PRINT_SETTINGS

    @staticmethod
    def need_settings(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Введите нужные номера страниц, разделяя их пробелами. "
                                                      "Интервалы страниц укажите через дефис без пробелов. "
                                                      "Пример: 1 3 6-7 10-17", default_keyboard)
        return State.WAIT_EXTRA_SETTINGS

    @staticmethod
    def ask_copies(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Введите количество копий. "
                                                      "Если нажать Далее, будет установлено значение 1",
                                        copies_keyboard)
        return State.ASK_COPIES

    @staticmethod
    def active_session_exist(bot, id_user):
        what_session = (DB.data_by_id(int(id_user)))[0][6]
        if what_session == 'vk':
            DB.change_status_session('none', id_user)
        return Condition.ask_copies(bot, id_user)

    @staticmethod
    def full_check(bot, id_user):
        info_user = (DB.data_by_id(int(id_user)))[0]
        session = info_user[6]
        print(info_user)
        print(session)
        if session == 'tg':
            Send.send_message_with_keyboard(bot, id_user, "Вы не можете печатать, "
                                                          "так как у Вас уже есть активная сессия в telegram! "
                                                          "Завершить её можно, перейдя к выбору принтера. "
                                                          "Чтобы попробовать снова, нажмите на соответствующую кнопку",
                                            try_now_keyboard)
            return State.ACTIVE_SESSION

        DB.change_status_session('vk', id_user)
        cur_limit = info_user[2]
        pages = Info.person_pages[id_user] * Info.person_copies[id_user]
        is_ban = info_user[4]
        full_path = os.path.join('../files_to_send', Info.titles[id_user])
        size_byte = os.stat(full_path).st_size
        # 20 Mb - max size
        if size_byte > 20971520:
            Send.send_message_with_keyboard(bot, id_user, "Файл превышает 20 Мб!", not_enough_pages_keyboard)
            Send.send_message(bot, id_user, 'Выберите из предложенных вариантов ответа!')
            DB.change_status_session('none', id_user)
            return State.CANT_PRINT

        if is_ban:
            Send.send_message_with_keyboard(bot, id_user, "Вы заблокированы! \n"
                                                          "Для дополнительной информации введите Help, "
                                                          "чтобы отправить сообщение админам",
                                            default_keyboard)
            DB.change_status_session('none', id_user)
            return Info.positions_dict[id_user]
        else:
            text = f"Осталось {cur_limit} страниц. Вы хотите распечатать {pages} страниц. "
            if cur_limit >= pages:
                text += "Отправить на печать?\nНажмите на соответствующую кнопку"
                Send.send_message_with_keyboard(bot, id_user, text, send_to_print_keyboard)
                return State.CHECK_DONE
            else:
                text += "Вы не можете распечатать файл!"
                Send.send_message_with_keyboard(bot, id_user, text, not_enough_pages_keyboard)
                Send.send_message(bot, id_user, 'Выберите из предложенных вариантов ответа!')
                DB.change_status_session('none', id_user)
                return State.CANT_PRINT

    @staticmethod
    def send_print(bot, id_user):
        printer = Info.person_printer[id_user]
        pages = Info.person_pages[id_user]
        copies = Info.person_copies[id_user]
        all_pages = pages * copies
        paper_in_printer = DB.get_paper_count_bd(printer)

        if paper_in_printer < all_pages:
            Send.send_message_with_keyboard(bot, id_user, "Извините, в принтере недостаточно бумаги!",
                                            not_enough_pages_keyboard)
            Info.person_printer.pop(id_user)
            Info.person_copies.pop(id_user)
            DB.change_status_session('none', id_user)
            return State.CANT_PRINT
        elif DB.data_by_id(id_user)[0][6] == 'vk':
            req = server_addr + '/add_task?printer={}&user={}&task=print&file={}&pages={}&copies={}'.format(
                printer,
                id_user,
                Info.titles[id_user], 
                pages,
                copies
            )

            print('print_action')
            requests.post(req, data={'token': api_token})
            Send.send_message_with_keyboard(bot, id_user, "Файл отправлен на печать. До новой встречи!",
                                            to_printer_keyboard)
            Info.titles.pop(id_user)
            Info.person_printer.pop(id_user)
            Info.person_copies.pop(id_user)

            DB.set_limit(id_user, DB.data_by_id(int(id_user))[0][2] - all_pages)
            DB.set_paper_count_bd(printer, paper_in_printer - all_pages)
            DB.change_status_session('none', id_user)

            Condition.control_alarm_paper(bot, printer)
            return Condition.choose_printer(bot, id_user)
        else:
            Send.send_message_with_keyboard(bot, id_user, "Вы не можете печатать, "
                                                          "так как у Вас уже есть активная сессия в telegram! "
                                                          "Завершить её можно, перейдя к выбору принтера. "
                                                          "Чтобы попробовать снова, нажмите на соответствующую кнопку",
                                            try_now_keyboard)
            return Condition.full_check

    @staticmethod
    def control_alarm_paper(bot, printer):
        if DB.get_paper_count_bd(printer) < alarm_paper:
            if not DB.check_is_alarmed_bd(printer):
                DB.set_is_alarmed_bd(printer, True)
                for i in admins:
                    Send.send_message(bot, i, f"В {printer} менее {alarm_paper} листов!")
        else:
            if DB.check_is_alarmed_bd(printer):
                DB.set_is_alarmed_bd(printer, False)
                for i in admins:
                    Send.send_message(bot, i, f"В {printer} добавлена бумага!")

    @staticmethod
    def need_help(bot, id_user, text):
        for i in admins:
            Send.send_message(bot, i,
                              f"СООБЩЕНИЕ ОБ ОШИБКЕ\n"
                              f"vk_id: {id_user}\n"
                              f"Текст сообщения:\n{text}")
        Send.send_message_with_keyboard(bot, id_user, "Сообщение успешно отправлено!", to_printer_keyboard)
        return Condition.choose_printer(bot, id_user)

    @staticmethod
    def admin_on(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Вы находитесь в режиме админа", admin_keyboard)
        return State.ADMIN_MODE

    @staticmethod
    def admin_off(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user, "Вы вышли из режима админа", to_printer_keyboard)
        return Condition.choose_printer(bot, id_user)

    @staticmethod
    def admin_change_ban(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user,
                                        "Укажите vk_id человека и параметр блокировки "
                                        "(True - забанить, False - разбанить)", default_keyboard)
        return State.CHANGE_BAN

    @staticmethod
    def admin_change_limit(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user,
                                        "Укажите через пробел vk_id человека и параметр изменения количества"
                                        " (-5 - уменьшить на 5 листов, +5 - увеличить на 5 листов)",
                                        default_keyboard)
        return State.CHANGE_LIMIT

    @staticmethod
    def admin_add_paper(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user,
                                        "Укажите через пробел название принтера и "
                                        "сколько листов (примерно) было добавлено",
                                        default_keyboard)
        return State.ADD_PAPER

    @staticmethod
    def admin_clean_queue_one(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user,
                                        "Выберите название принтера",
                                        printers_keyboard)
        return State.CLEAR_QUEUE

    @staticmethod
    def bot_on_service(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user,
                                        "Извините, я на техобслуживании! Приходите позже!",
                                        default_keyboard)

    @staticmethod
    def admin_ask_info(bot, id_user):
        Send.send_message_with_keyboard(bot, id_user,
                                        "Укажите vk_id нужного пользователя",
                                        default_keyboard)
        return State.ASK_INFO
