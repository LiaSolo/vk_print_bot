from vk_api.utils import get_random_id


class Send:
    @staticmethod
    def send_message_with_keyboard(bot, user_id, text_message, keyboard):
        bot.get_api().messages.send(user_id=user_id,
                                    message=text_message,
                                    random_id=get_random_id(),
                                    keyboard=keyboard.get_keyboard())

    @staticmethod
    def send_message(bot, user_id, text_message):
        bot.get_api().messages.send(user_id=user_id,
                                    message=text_message,
                                    random_id=get_random_id())
