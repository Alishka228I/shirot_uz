import telebot
from telebot import types

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000)

Thread(target=run).start()



import telebot
from telebot import types

TOKEN = "8770781211:AAFQVZzW89sf2kAtMu_wo1BKo2Zpkte66lA"


ADMIN_IDS = [6716338772, 6764894545, 1818590306, 511784627]

bot = telebot.TeleBot(TOKEN)

CONTACT_NUMBERS = """
📞 Пожалуйста, позвоните по номерам ниже для оформления заказа.
Пожалуйста, скажите, что вы пришли с Telegram-бота.

📞 Iltimos, buyurtma uchun quyidagi raqamlarga qo‘ng‘iroq qiling.
Telegram-bot orqali kelganingizni ayting.

📱 Номера / Raqamlar:

+998 50 553 40 00
+998 93 837 00 75
+998 90 065 00 01
"""
products = {
    "Рапс шрот / Raps shroti": {
        "price": 420,
        "description": """
🌾 Рапс шрот / Raps shroti

Рапсовый шрот получают после переработки семян рапса.
Он используется как кормовая добавка для животных и птиц.

Польза:
• содержит белок;
• помогает росту животных;
• подходит для составления комбикорма.

Raps shroti raps urug‘ini qayta ishlashdan olinadi.
U hayvonlar va parrandalar uchun ozuqa qo‘shimchasi sifatida ishlatiladi.
"""
    },

    "Подсолнечный шрот / Kungaboqar shroti": {
        "price": 220,
        "description": """
🌻 Подсолнечный шрот / Kungaboqar shroti

Подсолнечный шрот получают после переработки семян подсолнечника.
Часто используется в корме для КРС, птицы и других животных.

Польза:
• источник растительного белка;
• улучшает питательность корма;
• подходит для комбикорма.

Kungaboqar shroti kungaboqar urug‘ini qayta ishlashdan olinadi.
U qoramol, parranda va boshqa hayvonlar ozuqasida ishlatiladi.
"""
    },

    "Соевый шрот / Soya shroti": {
        "price": 650,
        "description": """
🫘 Соевый шрот / Soya shroti

Соевый шрот получают после переработки соевых бобов.
Это один из самых популярных белковых кормов.

Польза:
• много белка;
• хорошо подходит для птицы, КРС и рыбы;
• помогает набору массы.

Soya shroti soya donlarini qayta ishlashdan olinadi.
U oqsilga boy bo‘lib, parranda, qoramol va baliq ozuqasida ishlatiladi.
"""
    },

    "Рыбный корм / Baliq ozuqasi": {
        "price": 1100,
        "description": """
🐟 Рыбный корм / Baliq ozuqasi

Рыбный корм используется для выращивания рыбы в хозяйствах и прудах.
Он помогает рыбе быстрее расти и получать нужные питательные вещества.

Польза:
• подходит для кормления рыбы;
• помогает росту;
• содержит питательные компоненты.

Baliq ozuqasi baliqlarni boqish uchun ishlatiladi.
U baliqning o‘sishiga va kerakli oziqa moddalarini olishiga yordam beradi.
"""
    }
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
    product_name = message.text
    product = products[product_name]

    user_orders[message.chat.id] = {
        "product": product_name,
        "price": product["price"]
    }

    bot.send_message(
        message.chat.id,
        f"{product['description']}\n\n"
        f"💵 Цена / Narx: ${product['price']} за 1 тонну / 1 tonna uchun\n\n"
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
            "Подтверждаете?\n"
            "Tasdiqlaysizmi?",
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
        bot.send_message(message.chat.id, "Сначала выберите товар / Avval mahsulot tanlang.")
        return

    tg_link = f"tg://user?id={message.chat.id}"

    admin_text = (
        "🛒 Новый заказ / Yangi buyurtma\n\n"
        f"Товар / Mahsulot: {order['product']}\n"
        f"Количество / Miqdor: {order['quantity']} тонн / tonna\n"
        f"Цена / Narx: ${order['price']} за тонну / tonna uchun\n"
        f"Итого / Jami: ${order['total']}\n\n"
        f"Покупатель / Xaridor: {message.from_user.first_name}\n"
        f"Ссылка / Havola: {tg_link}"
    )

    bot.send_message(ADMIN_ID, admin_text)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/start")

    bot.send_message(
        message.chat.id,
        "✅ Ваша заявка принята!\n"
        "✅ Sizning buyurtmangiz qabul qilindi!\n\n"
        f"{CONTACT_NUMBERS}",
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
