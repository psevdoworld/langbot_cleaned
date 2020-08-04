from markups import stop_talk_murkup, hideBoard, main_markup


class Talk:

    def __init__(self, bot, users):
        self.bot = bot
        self.users = users
        self.queue = []
        self.waiter = None
        self.connected = {}

    def new_talking(self, user_id):
        if self.waiter:
            self.connected[self.waiter] = user_id
            self.connected[user_id] = self.waiter
            self.waiter = None
            self.start_talking(user_id)
            return True
        else:
            self.waiter = user_id
            self.users.set_state(user_id, "wait_talk")
            return False

    def start_talking(self, user_id):
        self.users.set_state(user_id, "talking")
        self.users.set_state(self.connected[user_id], "talking")
        self.bot.send_message(user_id,
                              "Собеседник найден!\n\nЧтобы прекратить диалог нажми\n\n*Я устал болтать*.\n\nЧтобы продолжить открой клавиатуру.",
                              reply_markup=stop_talk_murkup, parse_mode="Markdown")
        # self.bot.send_message(user_id, "Поздоровайся, напиши _Hello_", reply_markup=hideBoard, parse_mode="Markdown")
        photo = open('open_keyboard.jpg', 'rb')
        self.bot.send_photo(user_id,
                            photo)
        self.bot.send_message(self.connected[user_id],
                              "Собеседник найден!\n\nЧтобы прекратить диалог нажми *Я устал болтать*.\n\nЧтобы продолжить открой клавиатуру.",
                              reply_markup=stop_talk_murkup, parse_mode="Markdown")
        photo = open('open_keyboard.jpg', 'rb')
        self.bot.send_photo(self.connected[user_id],
                            photo)
        # self.bot.send_message(self.connected[user_id], "Поздоровайся, напиши _Hello_", reply_markup=hideBoard, parse_mode="Markdown")

    def redirect_message(self, user_id, text):
        if self.users.users_stat.get(self.connected[user_id]) == "talking":
            to_user = self.connected[user_id]
            self.bot.send_message(to_user, text)
        else:
            self.connected.pop(user_id, None)
            self.users.reset_state(user_id)
            self.bot.send_message(user_id, "Твой собеседник прервал беседу :-(", reply_markup=main_markup)

    def stop_talking(self, user_id):
        try:
            to_user = self.connected[user_id]
            self.connected.pop(to_user, None)
            self.connected.pop(user_id, None)
            self.users.reset_state(user_id)
            self.users.reset_state(to_user)
            self.bot.send_message(user_id, "Чем теперь займемся?", reply_markup=main_markup)
            self.bot.send_message(to_user, "Твой собеседник прервал беседу :-(", reply_markup=main_markup)
        except Exception as e:
            print(e)
            self.users.reset_state(user_id)

    def stop_wait(self, user_id):
        self.waiter = None
        self.users.reset_state(user_id)
        self.bot.send_message(user_id, "Чем теперь займемся?", reply_markup=main_markup)
