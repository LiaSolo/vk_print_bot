import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import re
from vk_config import vk_token, group_id
from sender import Send
from conditions import Condition
from states import State
from admins import Admin
from information import Info

bot = vk_api.VkApi(token=vk_token)


# при первом запуске выкидывать инструкцию

# апи принимает имя принтера, айди полтзователя, таск тайп (нужен принт) имя файла, количество копий
# /add_task?printer=printer_name&user=000000&task=printer_task&file=name.pdf&copies=copies_num


# защита от дураков в админке (но лучше затестить вообще всё)

# как добавить в очередь на принтер?
# очистить очередь одного принтера
# помощь

try:
    for event in VkBotLongPoll(bot, group_id).listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            id_user = str(event.object.message['from_id'])
            user_text = event.object.message['text']

            with open("TO.txt", 'r') as file:
                mode = file.read()

            position = Info.positions_dict.setdefault(id_user, State.CHECK_USER)
            print(Info.positions_dict)

            if user_text == "Help":
                position = Condition.condition_help(bot, id_user)

            # надеюсь, что админы умные и не прописываю защиту от дураков
            # ладно,  сама попалась, потом переделаю
            elif user_text == '+admin' and id_user in Info.admins:
                position = Condition.admin_on(bot, id_user)

            elif user_text == '-admin' and id_user in Info.admins:
                position = Condition.admin_off(bot, id_user)

            elif position == State.ADMIN_MODE:

                if user_text == "Забанить/Разбанить":
                    position = Condition.condition_change_ban(bot, id_user)

                elif user_text == "Изменить лимит":
                    position = Condition.condition_admin_change_limit(bot, id_user)

                elif user_text == "Добавить листы в принтер":
                    position = Condition.condition_add_paper(bot, id_user)

                elif user_text == "Информация":
                    position = Condition.condition_ask_info(bot, id_user)

                elif user_text == "Режим ТО":
                    position = Condition.condition_maintenance(bot, id_user)

                elif user_text == "Очистка очереди печати на принтере":
                    position = Condition.condition_clean_queue_one(bot, id_user)

            elif position == State.CHANGE_BAN:
                if user_text == "Назад":
                    position = Condition.admin_on(bot, id_user)
                else:
                    Admin.ban_or_unbun(bot, id_user, user_text)

            elif position == State.CHANGE_LIMIT:
                if user_text == "Назад":
                    position = Condition.admin_on(bot, id_user)
                else:
                    Admin.change_limit(bot, id_user, user_text)

            elif position == State.ADD_PAPER:
                if user_text == "Назад":
                    position = Condition.admin_on(bot, id_user)
                else:
                    Admin.add_paper(bot, id_user, user_text)

            elif position == State.ASK_INFO:
                if user_text == "Назад":
                    position = Condition.admin_on(bot, id_user)
                else:
                    Admin.ask_info(bot, id_user, user_text)

            elif position == State.MAINTENANCE:
                if user_text == "Назад":
                    position = Condition.admin_on(bot, id_user)
                elif user_text == "on" or user_text == "off":
                    Admin.maintenance(bot, id_user, user_text)

            # elif position == State.HELP:
            #     if user_text == "К выбору принтера":
            #         position = Condition.condition_start(bot, id_user)
            #     else:
            #         position = Condition.condition_need_help(bot, id_user, user_text)

            elif mode == 'on':
                Condition.condition_on_TO(bot, id_user)
                continue

            elif position == State.CHECK_USER:
                position = Condition.condition_check_existing(bot, id_user)

            elif position == State.CHOOSE_PRINTER:
                if user_text == "Принтер_1" or user_text == "Принтер_2":
                    Info.person_printer[id_user] = user_text
                    position = Condition.condition_wait_file(bot, id_user)

            elif position == State.WAIT_FOR_FILE:
                if user_text == "Назад":
                    position = Condition.condition_choose_printer(bot, id_user)
                elif (event.object.message['attachments'] != []
                      and event.object.message['attachments'][0]['type'] == 'doc'
                      and event.object.message['attachments'][0]['doc']['ext'] == 'pdf'):

                    position = Condition.condition_process_file(bot, id_user, event.object.message)
                else:
                    Send.send_message(bot, id_user, 'Я принимаю только пдф')

            elif position == State.PRINT_SETTINGS:
                if user_text == "Назад":
                    position = Condition.condition_wait_file(bot, id_user)
                elif user_text == "Распечатать весь файл":
                    position = Condition.condition_ask_copies(bot, id_user)
                elif user_text == "Выбрать определённые страницы":
                    position = Condition.condition_need_settings(bot, id_user)

            elif position == State.WAIT_EXTRA_SETTINGS:
                if user_text == "Назад":
                    position = Condition.condition_extra_settings(bot, id_user)
                elif re.compile("^[0-9 -]+$").search(str(user_text)) is not None:
                    position = Condition.condition_make_pdf(bot, id_user, str(user_text).split())
                else:
                    Send.send_message(bot, id_user, "Пожалуйста, следуйте шаблону!")

            elif position == State.ASK_COPIES:
                if user_text == "Назад":
                    position = Condition.condition_extra_settings(bot, id_user)
                elif str(user_text).isdigit() and user_text != '0':
                    Info.person_copies[id_user] = int(user_text)
                    print(Info.person_copies)
                    position = Condition.condition_check_limit(bot, id_user)
                else:
                    Send.send_message(bot, id_user, 'Введите натуральное число!')

            elif position == State.CANT_PRINT:
                if user_text == "К выбору принтера":
                    position = Condition.condition_choose_printer(bot, id_user)
                elif user_text == "К выбору файла":
                    position = Condition.condition_wait_file(bot, id_user)
                elif user_text == "К дополнительным настройкам":
                    position = Condition.condition_extra_settings(bot, id_user)

            elif position == State.LIMIT_OK:
                if user_text == "Назад":
                    position = Condition.condition_ask_copies(bot, id_user)
                if user_text == "К выбору принтера":
                    position = Condition.condition_choose_printer(bot, id_user)
                elif user_text == "Печатать":
                    position = Condition.condition_check_ban(bot, id_user)

            Info.positions_dict[id_user] = position
except:
    bot = vk_api.VkApi(token=vk_token)
