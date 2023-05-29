from json import load
import re
import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from admins import Admin
from vk_config import admins, group_id, printers, printers_names, vk_token
from sender import Send
from conditions import Condition
from states import State
from information import Info


bot = vk_api.VkApi(token=vk_token)

while True:
    try:
        for event in VkBotLongPoll(bot, group_id).listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                id_user = str(event.object.message['from_id'])
                user_text = event.object.message['text']

                with open("TO.json", 'r') as file:
                    _json = load(file)
                    SERVICE_MODE = eval(_json['service_mode'])

                position = Info.positions_dict.setdefault(id_user, State.CHECK_USER)
                print(Info.positions_dict)

                if user_text == '+admin' and id_user in admins:
                    position = Condition.admin_on(bot, id_user)

                elif user_text == '-admin' and id_user in admins and position == State.ADMIN_MODE:
                    position = Condition.admin_off(bot, id_user)

                elif user_text == "Назад" and (position in {State.CHANGE_BAN, State.CLEAR_QUEUE,
                                                            State.CHANGE_LIMIT, State.ADD_PAPER,
                                                            State.ASK_INFO}):
                    position = Condition.admin_on(bot, id_user)

                elif position == State.ADMIN_MODE:

                    if user_text == "Бан":
                        position = Condition.admin_change_ban(bot, id_user)

                    elif user_text == "Статистика":
                        position = Admin.get_statistics(bot, id_user)

                    elif user_text == "Изменить лимит":
                        position = Condition.admin_change_limit(bot, id_user)

                    elif user_text == "Добавить листы в принтер":
                        position = Condition.admin_add_paper(bot, id_user)

                    elif user_text == "Информация":
                        position = Condition.admin_ask_info(bot, id_user)

                    elif user_text == "Очистка очереди печати на принтере":
                        position = Condition.admin_clean_queue_one(bot, id_user)

                elif position == State.CLEAR_QUEUE:
                    if user_text in printers:
                        Admin.clean_queue_one_printer(bot, id_user, user_text)

                elif position == State.CHANGE_BAN:
                    Admin.ban_or_unban(bot, id_user, user_text)

                elif position == State.CHANGE_LIMIT:
                    Admin.change_limit(bot, id_user, user_text)

                elif position == State.ADD_PAPER:
                    Admin.add_paper(bot, id_user, user_text)

                elif position == State.ASK_INFO:
                    Admin.ask_info(bot, id_user, user_text)

                elif SERVICE_MODE:
                    Condition.bot_on_service(bot, id_user)

                elif user_text == 'Help':
                    position = Condition.condition_help(bot, id_user)

                elif position == State.HELP:
                    if user_text == "К выбору принтера":
                        position = Condition.choose_printer(bot, id_user)
                    else:
                        position = Condition.need_help(bot, id_user, user_text)

                elif position == State.CHECK_USER:
                    position = Condition.check_existing(bot, id_user)

                elif position == State.REGISTRATION:
                    if user_text == "Я залогинился":
                        position = Condition.check_existing(bot, id_user)
                    elif user_text == "Перевыпустить ссылку":
                        Condition.registration(bot, id_user)
                    else:
                        Send.send_message(bot, id_user, 'Пожалуйста, выберите из предложенных вариантов ответа!')

                elif position == State.CHOOSE_PRINTER:
                    if user_text in printers:
                        Info.person_printer[id_user] = printers_names[user_text]
                        position = Condition.wait_file(bot, id_user)
                    else:
                        Send.send_message(bot, id_user, 'Принтер не существует.'
                                                        'Пожалуйста, выберите из предложенных!')

                elif position == State.WAIT_FILE:
                    if user_text == "Назад":
                        position = Condition.choose_printer(bot, id_user)
                    elif (event.object.message['attachments'] != []
                          and event.object.message['attachments'][0]['type'] == 'doc'
                          and event.object.message['attachments'][0]['doc']['ext'] == 'pdf'):

                        position = Condition.process_file(bot, id_user, event.object.message)
                    else:
                        Send.send_message(bot, id_user, 'Пожалуйста, пришлите pdf-файл!')

                elif position == State.PRINT_SETTINGS:
                    if user_text == "Назад":
                        position = Condition.wait_file(bot, id_user)
                    elif user_text == "Распечатать весь файл":
                        position = Condition.ask_copies(bot, id_user)
                    elif user_text == "Выбрать определённые страницы":
                        position = Condition.need_settings(bot, id_user)
                    else:
                        Send.send_message(bot, id_user, 'Пожалуйста, выберите из предложенных вариантов ответа!')

                elif position == State.WAIT_EXTRA_SETTINGS:
                    if user_text == "Назад":
                        position = Condition.wait_extra_settings(bot, id_user)
                    elif re.compile("^[0-9 -]+$").search(str(user_text)) is not None:
                        position = Condition.make_pdf(bot, id_user, str(user_text).split())
                    else:
                        Send.send_message(bot, id_user, "Пожалуйста, следуйте шаблону!")
                    if position == State.WAIT_EXTRA_SETTINGS:
                        Send.send_message(bot, id_user, "Повторите ввод")

                elif position == State.ASK_COPIES:
                    if user_text == "Назад":
                        position = Condition.wait_extra_settings(bot, id_user)
                    elif user_text == 'Далее':
                        Info.person_copies[id_user] = 1
                        position = Condition.full_check(bot, id_user)
                    elif str(user_text).isdigit() and user_text != '0':
                        Info.person_copies[id_user] = int(user_text)
                        position = Condition.full_check(bot, id_user)
                    else:
                        Send.send_message(bot, id_user, 'Введите натуральное число!')

                elif position == State.ACTIVE_SESSION:
                    if user_text == "Назад":
                        position = Condition.ask_copies(bot, id_user)
                    elif user_text == "Попробуй снова":
                        position = Condition.full_check(bot, id_user)
                    else:
                        Send.send_message(bot, id_user, 'Пожалуйста, выберите из предложенных вариантов ответа!')

                elif position == State.CANT_PRINT:
                    if user_text == "К выбору принтера":
                        position = Condition.choose_printer(bot, id_user)
                    elif user_text == "К выбору файла":
                        position = Condition.wait_file(bot, id_user)
                    elif user_text == "К дополнительным настройкам":
                        Send.send_message(bot, id_user, "Будьте внимательны! Если указывались определённые страницы, "
                                                        "бот не помнит исходный файл. Ориентируйтесь на страницы, "
                                                        "которые Вы указывали, или пришлите новый файл")
                        position = Condition.wait_extra_settings(bot, id_user)
                    else:
                        Send.send_message(bot, id_user, 'Пожалуйста, выберите из предложенных вариантов ответа!')

                elif position == State.CHECK_DONE:
                    if user_text == "Назад":
                        position = Condition.active_session_exist(bot, id_user)
                    elif user_text == "К выбору принтера":
                        position = Condition.choose_printer(bot, id_user)
                    elif user_text == "Печатать":
                        position = Condition.send_print(bot, id_user)
                    else:
                        Send.send_message(bot, id_user, 'Пожалуйста, выберите из предложенных вариантов ответа!')

                Info.positions_dict[id_user] = position

    except Exception as e:
        with open('vk_errors.log', 'a') as log_file:
            log_file.write(str(e) + '\n\n')
