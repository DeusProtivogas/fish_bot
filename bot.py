"""
Работает с этими модулями:
python-telegram-bot==13.15
redis==3.2.1
"""
import os
import requests
import redis
from dotenv import load_dotenv

from io import BytesIO

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Filters, Updater, CallbackContext
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

from strapi_requests import get_products, create_cart, create_product_quantity, add_product_to_cart, get_cart, \
    get_product, remove_item_from_cart, save_email

_database = None


def start(update: Update, context: CallbackContext):
    """Sends a message with three inline buttons attached."""
    # context.user_data['state'] = 'BUTTONS'
    products = get_products(context.user_data['domain'])

    keyboard =[
        [InlineKeyboardButton("Показать корзину", callback_data='/cart')],
    ]

    keyboard += [
        [
            InlineKeyboardButton(
                product.get('attributes').get('Name'),
                callback_data=f'/show_{product.get("id")}'
            )
        ] for product in products.get('data')
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=context.user_data['chat_id'],
        text='Выберите:',
        reply_markup=reply_markup,
    )
    print("HELLO")
    # update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return 'HANDLE_MENU'


def handle_description(update: Update, context: CallbackContext):
    """Sends a message with three inline buttons attached."""
    context.user_data['state'] = 'BUTTONS'
    products = get_products(context.user_data['domain'])

    keyboard =[
        [InlineKeyboardButton("Показать корзину", callback_data='/cart')],
    ]

    keyboard += [
        [
            InlineKeyboardButton(
                product.get('attributes').get('Name'),
                callback_data=f'/show_{product.get("id")}'
            )
        ] for product in products.get('data')
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=context.user_data['chat_id'],
        text='Выберите:',
        reply_markup=reply_markup,
    )
    print("H DESCR")
    # update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return 'HANDLE_MENU'


def handle_menu(update: Update, context: CallbackContext):
    query = update.callback_query

    if query.data == '/cart':
        chat_id = context.user_data['chat_id']
        cart = get_cart(chat_id, context.user_data['domain'])

        context.user_data['state'] = 'START'

        p_q_pairs = cart.get('data')[0].get('attributes').get('product_quantities').get('data')

        cart_text = [
            f'{item.get("attributes").get("product").get("data").get("attributes").get("Name")}: {item.get("attributes").get("Quantity")} кг'
            for item in p_q_pairs
        ]

        keyboard = [
            [InlineKeyboardButton("В меню", callback_data='/back')],
            [InlineKeyboardButton("Заказать", callback_data='/pay')],
        ]

        keyboard += [
            [InlineKeyboardButton(
                f'Отказаться от {item.get("attributes").get("product").get("data").get("attributes").get("Name")}: {item.get("attributes").get("Quantity")} кг',
                callback_data=f'/remove_{item.get("id")}',
            )] for item in p_q_pairs
        ]

        context.bot.send_message(
            chat_id=context.user_data['chat_id'],
            text='\n'.join(cart_text),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return 'HANDLE_CART'

    elif query.data.startswith('/show'):
        product = get_product(query.data.split('_')[1], context.user_data['domain'])
        descr = product.get('attributes').get('Description')
        image = product.get('attributes').get('Picture').get('data')[0].get('attributes').get('formats').get(
            'small').get('url')

        query.bot.delete_message(
            chat_id=context.user_data['chat_id'],
            message_id=update.callback_query.message.message_id,
        )

        context.user_data['product_id'] = product.get('id')

        keyboard = [
            [InlineKeyboardButton("Добавить в корзину", callback_data='/add')],
            [InlineKeyboardButton("Показать корзину", callback_data='/cart')],
            [InlineKeyboardButton("Назад", callback_data='/back')],
        ]

        query.bot.send_photo(
            chat_id=context.user_data['chat_id'],
            caption=descr,
            photo=BytesIO(requests.get(f'http://{context.user_data["domain"]}/{image}').content),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return 'HANDLE_GOOD'
    else:
        return


def handle_cart(update: Update, context: CallbackContext):
    query = update.callback_query

    if query.data.startswith('/remove'):
        remove_item_from_cart(query.data.split('_')[1], context.user_data['domain'])
        chat_id = context.user_data['chat_id']
        cart = get_cart(chat_id, context.user_data['domain'])

        # context.user_data['state'] = 'START'

        p_q_pairs = cart.get('data')[0].get('attributes').get('product_quantities').get('data')

        cart_text = [
            f'{item.get("attributes").get("product").get("data").get("attributes").get("Name")}: {item.get("attributes").get("Quantity")} кг'
            for item in p_q_pairs
        ]

        keyboard = [
            [InlineKeyboardButton("В меню", callback_data='/back')],
            [InlineKeyboardButton("Заказать", callback_data='/pay')],
        ]

        keyboard += [
            [InlineKeyboardButton(
                f'Отказаться от {item.get("attributes").get("product").get("data").get("attributes").get("Name")}: {item.get("attributes").get("Quantity")} кг',
                callback_data=f'/remove_{item.get("id")}',
            )] for item in p_q_pairs
        ]

        context.bot.send_message(
            chat_id=context.user_data['chat_id'],
            text='\n'.join(cart_text),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return 'HANDLE_CART'

    elif query.data == '/back':
        """Sends a message with three inline buttons attached."""
        # context.user_data['state'] = 'BUTTONS'
        products = get_products(context.user_data['domain'])

        keyboard = [
            [InlineKeyboardButton("Показать корзину", callback_data='/cart')],
        ]

        keyboard += [
            [
                InlineKeyboardButton(
                    product.get('attributes').get('Name'),
                    callback_data=f'/show_{product.get("id")}'
                )
            ] for product in products.get('data')
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_message(
            chat_id=context.user_data['chat_id'],
            text='Выберите:',
            reply_markup=reply_markup,
        )
        print("H DESCR")
        # update.message.reply_text('Please choose:', reply_markup=reply_markup)
        return 'HANDLE_MENU'
        # return 'HANDLE_DESCRIPTION'

    elif query.data == '/pay':
        context.bot.send_message(
            chat_id=context.user_data[f'chat_id'],
            text='Введите свою почту, чтобы с Вами связался продавец:',
        )
        return 'HANDLE_EMAIL'


def handle_email(update: Update, context: CallbackContext):
    # query = update.callback_query
    context.user_data['email'] = update.message.text

    save_email(update.message.chat_id, context.user_data['email'], context.user_data['domain'])

    keyboard = [
        [InlineKeyboardButton("В меню", callback_data='/back')],
    ]

    context.bot.send_message(
        chat_id=context.user_data['chat_id'],
        text='Спасибо! С Вами скоро свяжутся!',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def handle_good(update: Update, context: CallbackContext):
    query = update.callback_query

    user_reply = None

    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id

    if user_reply.startswith('/cart'):
        chat_id = context.user_data['chat_id']
        cart = get_cart(chat_id, context.user_data['domain'])

        context.user_data['state'] = 'START'

        p_q_pairs = cart.get('data')[0].get('attributes').get('product_quantities').get('data')

        cart_text = [
            f'{item.get("attributes").get("product").get("data").get("attributes").get("Name")}: {item.get("attributes").get("Quantity")} кг'
            for item in p_q_pairs
        ]

        keyboard = [
            [InlineKeyboardButton("В меню", callback_data='/back')],
            [InlineKeyboardButton("Заказать", callback_data='/pay')],
        ]

        keyboard += [
            [InlineKeyboardButton(
                f'Отказаться от {item.get("attributes").get("product").get("data").get("attributes").get("Name")}: {item.get("attributes").get("Quantity")} кг',
                callback_data=f'/remove_{item.get("id")}',
            )] for item in p_q_pairs
        ]

        context.bot.send_message(
            chat_id=context.user_data['chat_id'],
            text='\n'.join(cart_text),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return 'HANDLE_CART'

    elif user_reply == '/back':
        """Sends a message with three inline buttons attached."""
        context.user_data['state'] = 'BUTTONS'
        products = get_products(context.user_data['domain'])

        keyboard = [
            [InlineKeyboardButton("Показать корзину", callback_data='/cart')],
        ]

        keyboard += [
            [
                InlineKeyboardButton(
                    product.get('attributes').get('Name'),
                    callback_data=f'/show_{product.get("id")}'
                )
            ] for product in products.get('data')
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_message(
            chat_id=context.user_data['chat_id'],
            text='Выберите:',
            reply_markup=reply_markup,
        )
        print("H DESCR")
        # update.message.reply_text('Please choose:', reply_markup=reply_markup)
        return 'HANDLE_MENU'
        # return 'HANDLE_DESCRIPTION'

    elif user_reply == '/add':
        context.bot.send_message(
            chat_id=context.user_data['chat_id'],
            text='Введите количество (в кг):',
        )
        return 'HANDLE_GOOD'

    else:
        try:
            mass = float(user_reply)
        except ValueError:
            print("Not a float")
        # query = update.callback_query

        ans = create_product_quantity(
            context.user_data['product_id'],
            mass,
            context.user_data['domain'],
        )
        p_q_id = ans.get('data').get('id')

        cart = get_cart(update.message.chat_id, context.user_data['domain'])
        if not cart.get('data'):
            ans = create_cart(update.message.chat_id, context.user_data['domain'])
        c_id = cart.get('data')[0].get('id')
        add_product_to_cart(c_id, p_q_id, context.user_data['domain'])

        keyboard = [
            [InlineKeyboardButton("В меню", callback_data='/back')],
        ]

        context.bot.send_message(
            chat_id=context.user_data['chat_id'],
            text="Товар добавлен в корзину!",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return 'HANDLE_DESCRIPTION'


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    product = get_product(query.data.split('_')[1], context.user_data['domain'])
    descr = product.get('attributes').get('Description')
    image = product.get('attributes').get('Picture').get('data')[0].get('attributes').get('formats').get('small').get('url')

    query.bot.delete_message(
        chat_id=context.user_data['chat_id'],
        message_id=update.callback_query.message.message_id,
    )

    context.user_data['product_id'] = product.get('id')

    keyboard = [
        [InlineKeyboardButton("Добавить в корзину", callback_data='/add')],
        [InlineKeyboardButton("Показать корзину", callback_data='/cart')],
        [InlineKeyboardButton("Назад", callback_data='/back')],
    ]

    query.bot.send_photo(
        chat_id=context.user_data['chat_id'],
        caption=descr,
        photo=BytesIO(requests.get(f'http://{context.user_data["domain"]}/{image}').content),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def ask_quantity(update: Update, context: CallbackContext) -> None:
    context.user_data['state'] = 'ADD'

    query = update.callback_query

    context.bot.send_message(
        chat_id=context.user_data['chat_id'],
        text='Введите количество (в кг):',
    )

def ask_email(update: Update, context: CallbackContext) -> None:
    context.user_data['state'] = 'HANDLE_EMAIL'
    context.bot.send_message(
        chat_id=context.user_data['chat_id'],
        text='Введите свою почту, чтобы с Вами связался продавец:',
    )

def handle_email(update: Update, context: CallbackContext):
    context.user_data['state'] = 'START'

    context.user_data['email'] = update.message.text

    save_email(update.message.chat_id, context.user_data['email'], context.user_data['domain'])

    keyboard = [
        [InlineKeyboardButton("В меню", callback_data='/back')],
    ]

    context.bot.send_message(
        chat_id=context.user_data['chat_id'],
        text='Спасибо! С Вами скоро свяжутся!',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def add_to_cart(update: Update, context: CallbackContext) -> None:
    context.user_data['state'] = 'START'

    query = update.callback_query

    ans = create_product_quantity(
        context.user_data['product_id'],
        update.message.text,
        context.user_data['domain'],
    )
    p_q_id = ans.get('data').get('id')

    cart = get_cart(update.message.chat_id, context.user_data['domain'])
    if not cart.get('data'):
        ans = create_cart(update.message.chat_id, context.user_data['domain'])
    c_id = cart.get('data')[0].get('id')
    add_product_to_cart(c_id, p_q_id, context.user_data['domain'])

    keyboard = [
        [InlineKeyboardButton("В меню", callback_data='/back')],
    ]

    context.bot.send_message(
        chat_id=context.user_data['chat_id'],
        text="Товар добавлен в корзину!",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def show_cart(update: Update, context: CallbackContext):
    chat_id = context.user_data['chat_id']
    cart = get_cart(chat_id, context.user_data['domain'])

    context.user_data['state'] = 'START'

    p_q_pairs = cart.get('data')[0].get('attributes').get('product_quantities').get('data')

    cart_text = [
        f'{item.get("attributes").get("product").get("data").get("attributes").get("Name")}: {item.get("attributes").get("Quantity")} кг' for item in p_q_pairs
    ]

    keyboard = [
        [InlineKeyboardButton("В меню", callback_data='/back')],
        [InlineKeyboardButton("Заказать", callback_data='/pay')],
    ]

    keyboard += [
        [InlineKeyboardButton(
            f'Отказаться от {item.get("attributes").get("product").get("data").get("attributes").get("Name")}: {item.get("attributes").get("Quantity")} кг',
            callback_data=f'/remove_{item.get("id")}',
        )] for item in p_q_pairs
    ]

    context.bot.send_message(
        chat_id=context.user_data['chat_id'],
        text='\n'.join(cart_text),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def handle_users_reply(update, context):
    """
    Функция, которая запускается при любом сообщении от пользователя и решает как его обработать.
    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
        * Отправка команды боту
    Она получает стейт пользователя из базы данных и запускает соответствующую функцию-обработчик (хэндлер).
    Функция-обработчик возвращает следующее состояние, которое записывается в базу данных.
    Если пользователь только начал пользоваться ботом, Telegram форсит его написать "/start",
    поэтому по этой фразе выставляется стартовое состояние.
    Если пользователь захочет начать общение с ботом заново, он также может воспользоваться этой командой.
    """
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    context.user_data['chat_id'] = chat_id
    context.user_data['domain'] = os.getenv("STRAPI_DOMAIN")

    if user_reply == '/start':
        context.user_data['state'] = 'START'
    else:
        context.user_data['state'] = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_CART': handle_cart,
        'HANDLE_GOOD': handle_good,
        'HANDLE_EMAIL': handle_email,
        'HANDLE_DESCRIPTION': handle_description,
    }

    try:
        state_handler = states_functions[context.user_data['state']]
        next_state = state_handler(update, context)
        db.set(chat_id, next_state)
    except requests.exceptions.HTTPError as e:
        print(e)


def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """

    global _database
    if _database is None:
        database_password = os.getenv("REDIS_PASS")
        database_host = os.getenv("REDIS_HOST")
        database_port = os.getenv("REDIS_PORT")
        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
    return _database


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))

    dispatcher.add_handler(CallbackQueryHandler(button))

    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
    updater.idle()
