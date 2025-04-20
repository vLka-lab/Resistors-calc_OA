from telebot import *
import os

def File_open(path):
    file = open(path, 'r')
    ret = file.read()
    file.close()
    return ret


def Paralel_count(r1, r2):
    return r1 * r2 / (r1 + r2)


TOKEN = 'YOURTOKEN'  #bot token from @BotFather t.me/ResistanceCalculator_bot
bot = TeleBot(TOKEN)
bot.flag_waiting_v_ref = False
bot.flag_waiting_v_out = False
bot.flag_waiting_res = False 


@bot.message_handler(commands=['start'])
def start(message):
    bot.flag_waiting_v_ref = False
    bot.flag_waiting_v_out = False
    bot.flag_waiting_res = True
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Стандартные значения")
    keyboard.add(button1)
    bot.send_message(message.chat.id, text="Загрузите файл со списком номиналов резисторов имеющихся в наличии (номиналы через пробел или перевод строки) или нажмите использование стандартных значений:".format(message.from_user), reply_markup=keyboard)


@bot.message_handler(content_types=['document'])
def first(message):
    if bot.flag_waiting_res == True:
        try:
            file_info = bot.get_file(message.document.file_id)
            testTXT = os.path.splitext(message.document.file_name)[1].lower()
            if testTXT != '.txt':
                err = int('ERROR')
            downloaded_file = bot.download_file(file_info.file_path)
            src = 'C:/Users/vlad/Documents/NPK2024/resistors_tgbot/databot/' + message.document.file_name
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.all_resistorsT = File_open(src)
            bot.all_resistorsLS = bot.all_resistorsT.split()
            bot.all_resistors = list(map(float, bot.all_resistorsLS)) 
            if list(set(bot.all_resistors)) > bot.all_resistors:
                err = int('ERROR')
            for i in bot.all_resistors:
                err = int('ERROR') if i <= 0 else True
        except:
            bot.send_message(message.chat.id, text="❎ Ошибка! Загрузите коректный файл со списком номиналов резисторов .txt (номиналы через пробел или перевод строки)".format(message.from_user))
            return None
        bot.send_message(message.chat.id, '✅ Файл считан, Введите Vref'.format(message.from_user))
        bot.flag_waiting_res = False
        bot.flag_waiting_v_ref = True

@bot.message_handler(content_types=['text'])
def second(message):
    if bot.flag_waiting_res == True:
        if message.text == 'Стандартные значения':
            bot.flag_waiting_res = False
            bot.flag_waiting_v_ref = True
            bot.all_resistors = list(map(float, [0.1, 0.3, 0.4, 0.7, 0.6, 0.5, 0.68, 0.75, 1.0, 1.2, 1.5, 1.6, 1.8, 2.0, 2.1, 2.2, 2.3, 2.4, 3.0, 5.0, 15, 30, 10, 24, 68, 70, 100, 680]))
            bot.send_message(message.chat.id, f"✅ Использованы номиналы: {bot.all_resistors}".format(message.from_user))
            bot.send_message(message.chat.id, 'Введите Vref'.format(message.from_user))
        else:
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = telebot.types.KeyboardButton(text="Стандартные значения")
            keyboard.add(button1)
            bot.send_message(message.chat.id, text='❎ Ошибка! Загрузите коректный файл или стандартные значения', reply_markup=keyboard)

    elif bot.flag_waiting_v_ref == True:
        try:
            number = float(message.text.replace(',', '.'))
            if number <= 0:
                i = int('ERROR')
            bot.send_message(message.chat.id, f"✅ Напряжение Vref = {number}В, Введите Vout".format(message.from_user))
            bot.v_ref = number
            bot.flag_waiting_v_ref = False
            bot.flag_waiting_v_out = True
            return None
        except (ValueError, AttributeError):
            bot.send_message(message.chat.id, "❎ Ошибка! Введите корректное число (например: 2.7, 1,9, не 0!)".format(message.from_user))
            return None
    elif bot.flag_waiting_v_out == True:
        try:
            number = float(message.text.replace(',', '.'))
            if number <= 0:
                i = int('ERROR')
            bot.send_message(message.chat.id, f"✅ напряжение Vout = {number}В".format(message.from_user))
            bot.v_out = number
        except (ValueError, AttributeError):
            bot.send_message(message.chat.id, "❎ Ошибка! Введите корректное число (например: 2.7, 1,9, не 0)".format(message.from_user))
            return None
        if bot.v_out == bot.v_ref:
            bot.send_message(message.chat.id, "R1 = 0, R2 = NC (Не подключено)".format(message.from_user))
            bot.send_message(message.chat.id, "Напишите /start для запуска программы с начала".format(message.from_user))
            return None
        if bot.v_out < bot.v_ref:
            bot.send_message(message.chat.id, "❎ Неверные значения для регулируемого источника питания на базе операционного услилителя (Vref > Vout)".format(message.from_user))
            bot.send_message(message.chat.id, "Напишите /start для запуска программы с начала".format(message.from_user))
            return None
        counter = 0
        countersecond = 0
        counterthird = 0
        counterfourth = 0
        for r2 in bot.all_resistors:    #два резистора (--резистор--резистор--)
            r1 = r2 * (bot.v_out / bot.v_ref - 1)
            for res in bot.all_resistors:
                if abs(res - r1) <= 0.0001:
                    resultat = f'R1 = {str(res)},\nR2 = {str(r2)}'
                    bot.send_message(message.chat.id, text=resultat.format(message.from_user))
                    counter =+ 1           
        if counter == 0:    #три резистора (--=два резистора паралельно=--резистор--)
            paralel_var = {}
            for r11 in bot.all_resistors:
                for r12 in bot.all_resistors:
                    for r2 in bot.all_resistors:
                        v_out_calc =  (bot.v_ref) * ((r11 * r12) / ((r11 + r12) * r2) + 1)
                        key = abs(bot.v_out - v_out_calc)
                        if paralel_var.get(key) != None:
                            paralel_var[key].append([r11, r12, r2])
                        else:
                            paralel_var.update({key: [[r11, r12, r2]]})    
            sorted_paralel_var = dict(sorted(paralel_var.items()))
            keys = list(sorted_paralel_var.keys())
            otv =[]
            for i in keys:
                if i <= 0.0001:
                    otv.append(i)
                    for pair in sorted_paralel_var[i]:
                        result_r = pair
                        ekv = round(Paralel_count(round(result_r[0], 6), round(result_r[1], 6)), 6)
                        bot.send_message(message.chat.id, text=f'R1.1 = {result_r[0]}, R1.2 = {result_r[1]} (Эквивалент R1 = {ekv}),\nR2 = {result_r[2]}'.format(message.from_user))
                        countersecond += 1
        if countersecond == 0 and counter == 0:     #три резистора (--резистор--=два резистора паралельно=--)
            paralel_var = {}
            for r1 in bot.all_resistors:
                for r21 in bot.all_resistors:
                    for r22 in bot.all_resistors:
                        v_out_calc = bot.v_ref * ((r1 * (r21 + r22)) / (r21 * r22) + 1)
                        key = abs(bot.v_out - v_out_calc)
                        if paralel_var.get(key) != None:
                            paralel_var[key].append([r1, r21, r22])
                        else:
                            paralel_var.update({key: [[r1, r21, r22]]})
            sorted_paralel_var = dict(sorted(paralel_var.items()))
            keys = list(sorted_paralel_var.keys())
            otv =[]
            for i in keys:
                if i <= 0.00001:
                    otv.append(i)
                    for pair in sorted_paralel_var[i]:
                        result_r = pair
                        ekv = round(Paralel_count(round(result_r[1], 6), round(result_r[2], 6)), 6)
                        bot.send_message(message.chat.id, text=f'R1 = {result_r[0]},\nR2.1 = {result_r[1]}, R2.2 = {result_r[2]} (Эквивалент R2 = {ekv})'.format(message.from_user))
                        counterthird += 1
        if countersecond == 0 and counter == 0 and counterthird == 0:   #четыре резистора (--два резистора паралельно--два резистора паралельно--)
            paralel_var = {}
            for r11 in bot.all_resistors:
                for r12 in bot.all_resistors:
                    for r21 in bot.all_resistors:
                        for r22 in bot.all_resistors:
                            v_out_calc =  ((r11 / r21) * (r12 / r22)  * ((r21 + r22) / (r11 + r12)) + 1) * bot.v_ref 
                            key = abs(bot.v_out - v_out_calc)
                            if paralel_var.get(key) != None:
                                paralel_var[key].append([r11, r12, r21, r22])
                            else:
                                paralel_var.update({key: [[r11, r12, r21, r22]]})
            sorted_paralel_var = dict(sorted(paralel_var.items()))
            keys = list(sorted_paralel_var.keys())
            otv = []
            for i in keys:
                if i <= 0.00001:
                    otv.append(i)
                    for pair in sorted_paralel_var[i]:
                        result_r = pair
                        ekv = round(Paralel_count(round(result_r[0], 6), round(result_r[1], 6)), 6)
                        ekv2 = round(Paralel_count(round(result_r[2], 6), round(result_r[3], 6)), 6)
                        bot.send_message(message.chat.id, text=f'\nR1.1 = {result_r[0]}, R1.2 = {result_r[1]} (Эквивалент R1 = {ekv}),\nR2.1 = {result_r[2]}, R2.2 = {result_r[3]} (Эквивалент R2 = {ekv2})'.format(message.from_user))
                        counterfourth += 1
        if countersecond == 0 and counter == 0 and counterthird == 0 and counterfourth == 0:
            bot.send_message(message.chat.id, "Нет вариантов решения задачи".format(message.from_user))
        bot.send_message(message.chat.id, "Введите новое значение Vout для повторного вычисления, или напишите /start для запуска программы с начала".format(message.from_user))


if __name__ == '__main__':
    bot.polling()
