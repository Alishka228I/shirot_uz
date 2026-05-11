import telebot
from telebot import types

TOKEN = "8770781211:AAFQVZzW89sf2kAtMu_wo1BKo2Zpkte66lA"
ADMIN_ID = 511784627


bot = telebot.TeleBot(TOKEN)

products = {
    "Рапс шрот / Raps shroti": 420,
    "Подсолнечный шрот / Kungaboqar shroti": 220,
    "Соевый шрот / Soya shroti": 650,
    "Рыбный корм / Baliq ozuqasi": 1100,
}

user_orders = {}


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for product in products:
        markup.add(product)

    bot.send_message(
        message.chat.id,
        "Здравствуйте! Выберите товар.\n"
        "Assalomu alaykum! Mahsulotni tanlang.",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text in products)
def choose_product(message):
    user_orders[message.chat.id] = {
        "product": message.text,
        "price": products[message.text]
    }

    bot.send_message(
        message.chat.id,
        f"Вы выбрали: {message.text}\n"
        f"Siz tanladingiz: {message.text}\n\n"
        f"Цена / Narx: ${products[message.text]} за 1 тонну / 1 tonna uchun\n\n"
        "Введите количество в тоннах.\n"
        "Tonna miqdorini kiriting."
    )


@bot.message_handler(
    func=lambda message:
    message.chat.id in user_orders and
    "quantity" not in user_orders[message.chat.id]
)
def get_quantity(message):
    try:
        quantity = float(message.text.replace(",", "."))

        if quantity <= 0:
            bot.send_message(
                message.chat.id,
                "Введите число больше 0.\n"
                "0 dan katta son kiriting."
            )
            return

        order = user_orders[message.chat.id]
        order["quantity"] = quantity
        order["total"] = quantity * order["price"]

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("✅ Подтвердить / Tasdiqlash")
        markup.add("❌ Отменить / Bekor qilish")

        bot.send_message(
            message.chat.id,
            f"Ваш заказ / Buyurtmangiz:\n\n"
            f"Товар / Mahsulot: {order['product']}\n"
            f"Количество / Miqdor: {quantity} тонн / tonna\n"
            f"Цена / Narx: ${order['price']} за тонну / tonna uchun\n"
            f"Итого / Jami: ${order['total']}\n\n"
            "Подтверждаете заказ?\n"
            "Buyurtmani tasdiqlaysizmi?",
            reply_markup=markup
        )

    except ValueError:
        bot.send_message(
            message.chat.id,
            "Введите количество числом. Например: 5\n"
            "Miqdorni son bilan kiriting. Masalan: 5"
        )


@bot.message_handler(func=lambda message: message.text == "✅ Подтвердить / Tasdiqlash")
def confirm_order(message):
    order = user_orders.get(message.chat.id)

    if not order:
        return

    first_name = message.from_user.first_name

    # Ссылка на профиль
    tg_link = f"tg://user?id={message.chat.id}"

    admin_text = (
        "🛒 Новый заказ / Yangi buyurtma\n\n"
        f"Товар / Mahsulot: {order['product']}\n"
        f"Количество / Miqdor: {order['quantity']} тонн / tonna\n"
        f"Цена / Narx: ${order['price']} за тонну / tonna uchun\n"
        f"Итого / Jami: ${order['total']}\n\n"
        f"Покупатель / Xaridor: {first_name}\n"
        f"Ссылка / Havola: {tg_link}"
    )

    bot.send_message(ADMIN_ID, admin_text)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/start")

    bot.send_message(
        message.chat.id,
        "✅ Заказ принят! Скоро с вами свяжется администратор.\n"
        "✅ Buyurtma qabul qilindi! Tez orada admin siz bilan bog'lanadi.",
        reply_markup=markup
    )

    del user_orders[message.chat.id]


@bot.message_handler(func=lambda message: message.text == "❌ Отменить / Bekor qilish")
def cancel_order(message):
    if message.chat.id in user_orders:
        del user_orders[message.chat.id]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/start")

    bot.send_message(
        message.chat.id,
        "Заказ отменён.\n"
        "Buyurtma bekor qilindi.",
        reply_markup=markup
    )


bot.polling(none_stop=True)
