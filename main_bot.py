import json
import requests

from urllib.request import urlopen
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, RegexHandler, CallbackQueryHandler

TOKEN = "602606847:AAGNryoE6AyI9dX5uHNMRrKXAEbZVFGmFDw"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

orderArr = []

namesProduct = []


class Order:
    idGoods = 0
    count = 0
    name = None

    def __init__(self, idGoods, count, name):
        self.idGoods = idGoods
        self.count = count
        self.name = name

    def __str__(self) -> str:
        return "name = {}  count = {}. {}".format(self.name, self.count, str("\n"))

    def increment(self):
        self.count += 1


class Bucket:
    goods = None
    user = None
    description = None

    def __init__(self, goods, user, description):
        self.goods = goods
        self.user = user
        self.description = description


class User:
    address = None
    addressNumber = None
    name = None
    number = None
    surName = None

    def __init__(self):
        self.address = "Пасічна"
        self.addressNumber = 5
        self.name = "ТЕСТ"
        self.number = "0935211662"
        self.surName = "ТЕСТ"


def createCategoriesButtons(categories):
    buttons = []
    for cat in categories:
        data = "cat-{}".format(cat["id"])
        buttons.append([InlineKeyboardButton(cat["name"], callback_data=data)])
    return buttons


def getCategories():
    data = json.loads(urlopen("http://95.46.45.206:8000/public/category").read())
    return data


def getSubCategories(id):
    data = json.loads(urlopen("http://95.46.45.206:8000/public/subCategory/{}".format(id)).read())
    return data


def getProducts(idSubCategory):
    data = json.loads(urlopen("http://95.46.45.206:8000/public/goods/by/subCategory/{}".format(idSubCategory)).read())
    return data


def sendOrder(req):
    header = {"Content-Type": "application/json"}
    data = requests.post("http://95.46.45.206:8000/public/order", data=req, headers=header)
    return data


def showMenu(bot, update):
    categories = getCategories()
    buttons = createCategoriesButtons(categories)
    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(chat_id=update['message']['chat']['id'], text='Виберіть категорію :',
                     reply_markup=reply_markup)


def showMainControllers(bot, update):
    keyboard = [[KeyboardButton("Меню")],
                ["Замовити"]]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    bot.send_message(chat_id=update['message']['chat']['id'], text='Вас вітає DeLuxeDostavka Bot :',
                     reply_markup=reply_markup)


def start(bot, update):
    showMainControllers(bot, update)


def createRequest():
    goods = []
    for o in orderArr:
        goods.append(o.__dict__)
    user = User()
    return Bucket(goods, user.__dict__, "ТЕСТ")


def doOrder(bot, update):
    if len(orderArr) == 0:
        bot.send_message(chat_id=update['message']['chat']['id'], text="Ви ще нічого не замовили перейдіть в відділ меню !!!")
        return
    resp = sendOrder(json.dumps(createRequest().__dict__))
    result = "ERROR спробуйте повторити замовлення"
    if resp.status_code == 200:
        result = "Ваше замовлення прийнято очікуйте дзвінка оператора для підтвердження !!!"
    bot.send_message(chat_id=update['message']['chat']['id'], text=result)


def createSubCategoriesButtons(subCategories):
    buttons = []
    for subCat in subCategories:
        data = "sub-{}".format(subCat["id"])
        buttons.append([InlineKeyboardButton(subCat["name"], callback_data=data)])
    return buttons


def createProductButtons(products):
    buttons = []
    for prod in products:
        data = "prod-{}-{}".format(prod["id"], prod["name"])
        buttons.append([InlineKeyboardButton(prod["name"], callback_data=data)])
    return buttons


def showSubCategories(bot, update, categoryId):
    subCategories = getSubCategories(categoryId)
    buttons = createSubCategoriesButtons(subCategories)
    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(chat_id=update["callback_query"]["message"]["chat"]["id"], text='Виберіть підкатегорію:',
                     reply_markup=reply_markup)


def showProducts(bot, update, subCategoryId):
    products = getProducts(subCategoryId)
    buttons = createProductButtons(products)
    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(chat_id=update["callback_query"]["message"]["chat"]["id"], text='Виберіть Товар:',
                     reply_markup=reply_markup)


def addToBucket(bot, update, idProduct, nameProduct):
    order = Order(idProduct, 0, nameProduct)
    for ord in orderArr:
        if ord.idGoods == idProduct:
            order = ord
            break
    if order.count == 0:
        orderArr.append(order)
    order.increment()
    result = "Ваше замовлення : \n"
    for ord in orderArr:
        result += str(ord)
    bot.send_message(chat_id=update["callback_query"]["message"]["chat"]["id"], text=result)


def queryHandler(bot, update):
    query = update.callback_query
    data = query.data
    id = data.split('-')[1]
    if data.split('-')[0] == "cat":
        showSubCategories(bot, update, id)
        return 1
    if data.split('-')[0] == "sub":
        showProducts(bot, update, id)
        return 1
    if data.split("-")[0] == "prod":
        addToBucket(bot, update, id, data.split("-")[2])


def main():

    updater = Updater(token=TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(RegexHandler('Меню', showMenu))
    updater.dispatcher.add_handler(RegexHandler('Замовити', doOrder))
    updater.dispatcher.add_handler(CallbackQueryHandler(queryHandler))
    updater.dispatcher.add_handler(CommandHandler('help', help))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
