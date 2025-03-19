import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
from time import time
from datetime import *
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv('TOKEN_API')
bot = telebot.TeleBot(token)

# coin market cap api key
coinmarketcap_api_key = os.getenv("COIN_API")
coin_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

# weather api key
weathrer_api_key = os.getenv("WEATHER_API")
weather_url = "https://api.openweathermap.org/data/2.5/weather"

headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": coinmarketcap_api_key
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton('استعلام قیمت ارز ها') # اوکی شد
    btn2 = KeyboardButton('وضیعت آب و هوا') # استارت زدن این
    btn3 = KeyboardButton('تبدیل متن به ویس')
    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id, 'میخوای کدوم کار رو واست انجام بدم؟', reply_markup=markup)

# part crypto 

@bot.message_handler(func=lambda m: m.text == 'استعلام قیمت ارز ها')
def crypto_pic(message):
    inline_markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('TOP 20 COIN', callback_data='top20')
    btn2 = InlineKeyboardButton('سرچ ارز دلخواه', callback_data='custom')
    inline_markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, 'یکی از گزینه های زیر رو انتخاب کن', reply_markup=inline_markup)
    
@bot.callback_query_handler(func=lambda m: m.data == 'top20')
def top20_coin(call):
    
    inline_markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('BACK', callback_data='back_mu')
    inline_markup.add(btn1)
    
    params = {
        'start': '1',
        'limit': '20',
        'convert': 'USD'
    }
     
    response = requests.get(url=coin_url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        coins = data['data']
        coin_list = []
        number = 1
        for coin in coins:
            coin_name = coin['symbol']
            price = coin['quote']['USD']['price']
            coin_list.append(f'{number}- {coin_name} in price: ${price:.7f}')
            number += 1
        
        message_text = "\n".join(coin_list)
        bot.send_message(chat_id=call.message.chat.id, text=message_text, reply_markup=inline_markup)
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Error in status code is -> {response.status_code} // please try again!')
    
@bot.callback_query_handler(func=lambda call: call.data == 'back_mu')
def back_mu(call):
    crypto_pic(call.message)
    
@bot.callback_query_handler(func=lambda m: m.data == 'custom')
def custom_run(call):
    
    inline_markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('BACK', callback_data='back_mu2')
    inline_markup.add(btn1)
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='لطفا اسم ارز مورد نظر خود را وارد کن\n برای مثال:\n symbol name: NOT\n slug name: notcoin', reply_markup=inline_markup)
    bot.register_next_step_handler(call.message, custom_search)
    
def custom_search(message):
    inline_markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('BACK', callback_data='back_mu2')
    inline_markup.add(btn1)
    
    params = {
        'start': '1',
        'limit': '5000',
        'convert': 'USD'
    }

    text = message.text
    response = requests.get(url=coin_url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        found = False
        for coin in data['data']:
            coin_name = coin['slug']
            coin_symbol = coin['symbol']
            if text.upper() == coin_symbol.upper() or text.lower() == coin_name.lower():
                price = coin['quote']['USD']['price']
                bot.send_message(message.chat.id, f'{coin_name} ({coin_symbol}) price: ${price:.7f}', reply_markup=inline_markup)        
                found = True
        if not found:
            bot.send_message(message.chat.id, 'ارز مورد نظر پیدا نشد لطفا دوباره تست کنید', reply_markup=inline_markup) 
    else:
        bot.send_message(message.chat.id, f'Error, response status code is -> {response.status_code}, please try again!', reply_markup=inline_markup)
    bot.register_next_step_handler(message, custom_search)
    
@bot.callback_query_handler(func=lambda m: m.data == 'back_mu2')
def back_menu2(call):
    crypto_pic(call.message)
    
# part openweather

@bot.message_handler(func=lambda m: m.text == 'وضیعت آب و هوا')
def send_pim_for_select(message):
    inline_markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton('BACK', callback_data='back_mu3')
    inline_markup.add(btn)
    
    bot.send_message(message.chat.id, 'لطفا اسم شهر رو بفرستید\n برای مثال: Tehran', reply_markup=inline_markup)
    
    bot.register_next_step_handler(message, enter_name_city)
    
def enter_name_city(message):
    inline_markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton('BACK', callback_data='back_mu3')
    inline_markup.add(btn)
    
    city = message.text
    
    params = {
        'q': city,
        'appid': weathrer_api_key,
        'units': 'metric',
        'lang': 'fa',
        'nocache': time()
    }
    
    respones = requests.get(url=weather_url, params=params)
    if respones.status_code == 200:
        data = respones.json()
        country = data['sys']['country']
        name_city = data['name']
        temp = data['main']['temp']
        temp_min = data['main']['temp_min']
        temp_max = data['main']['temp_max']
        humidity = data['main']['humidity']
        speed = data['wind']['speed']
        description = data['weather'][0]['description']
        sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
        sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
        
        weather_info = f"""
🌍 کشور: {country}
🏙 شهر: {name_city}

🌡 دمای فعلی: {temp}°C
🔻 کمترین دما: {temp_min}°C
🔺 بیشترین دما: {temp_max}°C

💧 رطوبت: {humidity}%
💨 سرعت باد: {speed} m/s

🌅 طلوع خورشید: {sunrise}
🌇 غروب خورشید: {sunset}

🌤 وضعیت آب‌وهوا: {description}
"""
        bot.send_message(message.chat.id, text=weather_info, reply_markup=inline_markup)

        
    elif respones.status_code == 404:
        bot.send_message(message.chat.id, f"شهر مورد نظر پیدا نشد لطفا دوباره تلاش کنید -> {respones.status_code}", reply_markup=inline_markup)
    elif respones.status_code == 401:
        bot.send_message(message.chat.id, f'API-KEY Error please try again.', reply_markup=inline_markup)
    elif respones.status_code == 400:
        bot.send_message(message.chat.id, f'دسترسی شما رد شد', reply_markup=inline_markup)
    else:
        bot.send_message(message.chat.id, 'خطایی نا معلوم!', reply_markup=inline_markup)
        

    bot.register_next_step_handler(message, enter_name_city)

    
@bot.message_handler(func=lambda m: m.data == 'back_mu3')
def back_first_mune(call):
    start(call.message)

print('bot is running...')
bot.polling(none_stop=True)