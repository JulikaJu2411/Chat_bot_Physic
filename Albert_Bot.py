import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


bot = telebot.TeleBot("8099247456:AAG-ts6NUDVnd6KFKIdgY3b4Wj3tHJD9SBY")  # токен нашего бота


'''___________________________Приветствие________________________________________'''
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_start = KeyboardButton('Начать работу')
    markup.add(button_start)
    bot.send_message(message.chat.id, '''Доброго времени суток😊 Я Ваш персональный помощик Albert.
    Я был создан для того, чтобы помогать молодым ученым в сфере физики.
В мой функционал входит:
    1. Осуществление перевода частоты излучения или энергии фотона в длину волны света и обратно. Предоставление информации о диапазоне длин волн, с которыми Вы работаете.
    
    2. Вычисление по спектру в формате .txt положения резонанса и его ширины на полувысоте (каждая точка спектра - отдельная строчка, длина волны (пробел или таб) интенсивность). Вывод графика с отмеченным положением пика и его ширины на полувысоте.
    
    3. Вычисление флюенса лазерной системы по средней мощности. 
    
Для работы со мной Вам достаточно нажать на кнопку "Начать работу" и выбрать нужную функцию, для завершения 
работы нажмите кнопку "Закончить работу"
    ''', reply_markup=markup)
    bot.send_message(message.chat.id, '''Чуть не забыл...
Не забывайте отдыхать😉''', reply_markup=markup)


'''_____________________________Начало работы бота_________________________________________'''

@bot.message_handler(func=lambda message: message.text == 'Начать работу' or message.text == 'Главное меню' or message.text == 'Продолжить работу')
def send_help_options(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_option1 = KeyboardButton('Длина волны')
    button_option2 = KeyboardButton('Частота и энергия')
    button_option3 = KeyboardButton('График пика')
    button_option4 = KeyboardButton('Лазерный флюенс')
    button_end = KeyboardButton('Закончить работу')
    markup.add(button_option1, button_option2, button_option3, button_option4, button_end)
    bot.send_message(message.chat.id, 'Выберите то, что Вас интересует:', reply_markup=markup)


'''________________________Построекние графика пика по файлу txt____________________________'''

@bot.message_handler(func=lambda message: message.text == 'График пика')
def handle_peak_plot(message):
    bot.send_message(message.chat.id, 'Пожалуйста, отправьте файл спектра в формате .txt.')

@bot.message_handler(content_types=['document'])
def handle_document(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open('spectrum.txt', 'wb') as new_file:
        new_file.write(downloaded_file)

    wavelengths, intensities = read_spectrum('spectrum.txt')
    peak_wavelength, fwhm, peak_idx, left_idx, right_idx = find_peak_and_fwhm(wavelengths, intensities)
    plot_spectrum(wavelengths, intensities, peak_wavelength, fwhm, peak_idx, left_idx, right_idx)

    bot.send_message(message.chat.id, f'Положение пика: {peak_wavelength} nm\nШирина на полувысоте: {fwhm} nm')
    bot.send_photo(message.chat.id, photo=open('spectrum_plot.png', 'rb'))

# Функция для чтения данных из файла
def read_spectrum(file_path):
    wavelengths = []
    intensities = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split()
            wavelengths.append(float(parts[0]))
            intensities.append(float(parts[1]))
    return np.array(wavelengths), np.array(intensities)

# Функция для нахождения положения пика и его ширины на полувысоте
def find_peak_and_fwhm(wavelengths, intensities):
    peaks, _ = find_peaks(intensities)
    peak_idx = peaks[np.argmax(intensities[peaks])]
    peak_wavelength = wavelengths[peak_idx]
    peak_intensity = intensities[peak_idx]

    half_max = peak_intensity / 2
    left_idx = np.where(intensities[:peak_idx] <= half_max)[0][-1]
    right_idx = np.where(intensities[peak_idx:] <= half_max)[0][0] + peak_idx

    fwhm = wavelengths[right_idx] - wavelengths[left_idx]
    return peak_wavelength, fwhm, peak_idx, left_idx, right_idx

# Функция для построения графика
def plot_spectrum(wavelengths, intensities, peak_wavelength, fwhm, peak_idx, left_idx, right_idx):
    plt.plot(wavelengths, intensities, label='Spectrum')
    plt.plot(wavelengths[peak_idx], intensities[peak_idx], 'ro', label='Peak')
    plt.hlines(intensities[peak_idx] / 2, wavelengths[left_idx], wavelengths[right_idx], colors='r', label='FWHM')
    plt.xlabel('Длина волны')
    plt.ylabel('Интенсивность')
    plt.title('Спектр с пиковым значением и полной шириной на полувысоте')
    plt.legend()
    plt.savefig('spectrum_plot.png')
    plt.close()

@bot.message_handler(func=lambda message: message.text == 'Длина волны')
def dlin_voln(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_chastota = KeyboardButton('Частота излучения')
    button_energy = KeyboardButton('Энергия фотона')
    button_end = KeyboardButton('Закончить работу')
    markup.add(button_chastota, button_energy, button_end)
    bot.send_message(message.chat.id, 'Что вы будете использовать?', reply_markup=markup)


'''____________________ Длина волны по частоте___________________'''
@bot.message_handler(func=lambda message: message.text == 'Частота излучения')
def voln1(message):
    bot.send_message(message.chat.id, "Введите частоту излучения в Гц (дробная часть прописывается через точку):")
    bot.register_next_step_handler(message, process_frequency)
def process_frequency(message):
    try:
        frequency = float(message.text)
        wavelength = length_voln(frequency)
        if 1e-12 <= wavelength < 1e-9:
            diapazon = "Гамма-излучением"
        elif 1e-9 <= wavelength < 1e-6:
            diapazon = "Ультрафиолетовым диапазоном"
        elif 1e-6 <= wavelength < 1e-3:
            diapazon = "Инфракрасным диапазоном"
        elif 1e-3 <= wavelength < 1:
            diapazon = "Радиоволнами (миллиметровый диапазон)"
        elif 1 <= wavelength < 10:
            diapazon = "Радиоволнами (сантиметровый диапазон)"
        elif 10 <= wavelength < 100:
            diapazon = "Радиоволнами (дециметровый диапазон)"
        elif 100 <= wavelength < 1000:
            diapazon = "Радиоволнами (метровый диапазон)"
        elif 1e-6 <= wavelength < 1e-3:
            diapazon = "Инфракрасным диапазоном"
        elif 1e-3 <= wavelength < 1:
            diapazon = "Радиоволнами (миллиметровый диапазон)"
        elif 1 <= wavelength < 10:
            diapazon = "Радиоволнами (сантиметровый диапазон)"
        elif 10 <= wavelength < 100:
            diapazon = "Радиоволнами (дециметровый диапазон)"
        elif 100 <= wavelength < 1000:
            diapazon = "Радиоволнами (метровый диапазон)"
        else:
            diapazon = "Неизвестным диапазоном"

        response = f"Вы отправили частоту волны {frequency} Гц. Длина волны света при такой частоте {wavelength} м. \n Вы работаете с {diapazon}"
    except ValueError:
        response = "Пожалуйста, введите корректное число."
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_end = KeyboardButton('Закончить работу')
    button_prod = KeyboardButton('Продолжить работу')
    markup.add(button_end, button_prod)
    bot.send_message(message.chat.id, response, reply_markup=markup)
def length_voln(frequency):
    c = 3e8  # скорость света в вакууме в м/с
    wavelength = c /frequency
    return wavelength


'''____________________длина волны по энергии фотона____________________'''
@bot.message_handler(func=lambda message: message.text == 'Энергия фотона')
def voln1(message):
    bot.send_message(message.chat.id, "Введите энергию фотона в Дж*с (дробная часть прописывается через точку):")
    bot.register_next_step_handler(message, process_energy)
def process_energy(message):
    try:
        energy = float(message.text)
        wavelength = length_voln1(energy)
        if 1e-12 <= wavelength < 1e-9:
            diapazon = "Гамма-излучением"
        elif 1e-9 <= wavelength < 1e-6:
            diapazon = "Ультрафиолетовым диапазоном"
        elif 1e-6 <= wavelength < 1e-3:
            diapazon = "Инфракрасным диапазоном"
        elif 1e-3 <= wavelength < 1:
            diapazon = "Радиоволнами (миллиметровый диапазон)"
        elif 1 <= wavelength < 10:
            diapazon = "Радиоволнами (сантиметровый диапазон)"
        elif 10 <= wavelength < 100:
            diapazon = "Радиоволнами (дециметровый диапазон)"
        elif 100 <= wavelength < 1000:
            diapazon = "Радиоволнами (метровый диапазон)"
        elif 1e-6 <= wavelength < 1e-3:
            diapazon = "Инфракрасным диапазоном"
        elif 1e-3 <= wavelength < 1:
            diapazon = "Радиоволнами (миллиметровый диапазон)"
        elif 1 <= wavelength < 10:
            diapazon = "Радиоволнами (сантиметровый диапазон)"
        elif 10 <= wavelength < 100:
            diapazon = "Радиоволнами (дециметровый диапазон)"
        elif 100 <= wavelength < 1000:
            diapazon = "Радиоволнами (метровый диапазон)"
        else:
            diapazon = "Неизвестным диапазоном"

        response = f"Вы отправили энергию фтона волны {energy} Дж*с. Длина волны света при такой энергии {wavelength} м. \n Вы работаете с {diapazon}"
    except ValueError:
        response = "Пожалуйста, введите корректное число."
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_end = KeyboardButton('Закончить работу')
    button_prod = KeyboardButton('Продолжить работу')
    markup.add(button_end, button_prod)
    bot.send_message(message.chat.id, response, reply_markup=markup)
def length_voln1(energy):
    c = 3e8  # скорость света в вакууме в м/с
    h = 6.626e-34
    wavelength = (h*c)/energy
    return wavelength

@bot.message_handler(func=lambda message: message.text == 'Частота и энергия')
def dlin_voln(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_chastota1 = KeyboardButton('Частоту излучения')
    button_energy1 = KeyboardButton('Энергию фотона')
    button_end = KeyboardButton('Закончить работу')
    markup.add(button_chastota1, button_energy1, button_end)
    bot.send_message(message.chat.id, 'Что Вам нужно найти?', reply_markup=markup)


'''____________________Нахождение Частоты фотона____________________'''

@bot.message_handler(func=lambda message: message.text == 'Частоту излучения')
def voln1(message):
    bot.send_message(message.chat.id, "Введите длину волны в метрах (дробная часть прописывается через точку):")
    bot.register_next_step_handler(message, process_frequency1)
def process_frequency1(message):
    try:
        wavelength = float(message.text)
        frequency = frequency_voln(wavelength)
        if 1e-12 <= wavelength < 1e-9:
            diapazon = "Гамма-излучением"
        elif 1e-9 <= wavelength < 1e-6:
            diapazon = "Ультрафиолетовым диапазоном"
        elif 1e-6 <= wavelength < 1e-3:
            diapazon = "Инфракрасным диапазоном"
        elif 1e-3 <= wavelength < 1:
            diapazon = "Радиоволнами (миллиметровый диапазон)"
        elif 1 <= wavelength < 10:
            diapazon = "Радиоволнами (сантиметровый диапазон)"
        elif 10 <= wavelength < 100:
            diapazon = "Радиоволнами (дециметровый диапазон)"
        elif 100 <= wavelength < 1000:
            diapazon = "Радиоволнами (метровый диапазон)"
        elif 1e-6 <= wavelength < 1e-3:
            diapazon = "Инфракрасным диапазоном"
        elif 1e-3 <= wavelength < 1:
            diapazon = "Радиоволнами (миллиметровый диапазон)"
        elif 1 <= wavelength < 10:
            diapazon = "Радиоволнами (сантиметровый диапазон)"
        elif 10 <= wavelength < 100:
            diapazon = "Радиоволнами (дециметровый диапазон)"
        elif 100 <= wavelength < 1000:
            diapazon = "Радиоволнами (метровый диапазон)"
        else:
            diapazon = "Неизвестным диапазоном"

        response = f"Вы отправили длину волны {wavelength } м. При такой длине света частота равна {frequency} м. \n Вы работаете с {diapazon}"
    except ValueError:
        response = "Пожалуйста, введите корректное число."
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_end = KeyboardButton('Закончить работу')
    button_prod = KeyboardButton('Продолжить работу')
    markup.add(button_end, button_prod)
    bot.send_message(message.chat.id, response, reply_markup=markup)
def frequency_voln(wavelength):
    c = 3e8  # скорость света в вакууме в м/с
    frequency = c / wavelength
    return frequency


'''____________________нахождение энергии фотона____________________'''
@bot.message_handler(func=lambda message: message.text == 'Энергию фотона')
def voln1(message):
    bot.send_message(message.chat.id, "Введите длину волны в метрах (дробная часть прописывается через точку):")
    bot.register_next_step_handler(message, process_energy1)
def process_energy1(message):
    try:
        wavelength = float(message.text)
        energy = energy_voln(wavelength)
        if 1e-12 <= wavelength < 1e-9:
            diapazon = "Гамма-излучением"
        elif 1e-9 <= wavelength < 1e-6:
            diapazon = "Ультрафиолетовым диапазоном"
        elif 1e-6 <= wavelength < 1e-3:
            diapazon = "Инфракрасным диапазоном"
        elif 1e-3 <= wavelength < 1:
            diapazon = "Радиоволнами (миллиметровый диапазон)"
        elif 1 <= wavelength < 10:
            diapazon = "Радиоволнами (сантиметровый диапазон)"
        elif 10 <= wavelength < 100:
            diapazon = "Радиоволнами (дециметровый диапазон)"
        elif 100 <= wavelength < 1000:
            diapazon = "Радиоволнами (метровый диапазон)"
        elif 1e-6 <= wavelength < 1e-3:
            diapazon = "Инфракрасным диапазоном"
        elif 1e-3 <= wavelength < 1:
            diapazon = "Радиоволнами (миллиметровый диапазон)"
        elif 1 <= wavelength < 10:
            diapazon = "Радиоволнами (сантиметровый диапазон)"
        elif 10 <= wavelength < 100:
            diapazon = "Радиоволнами (дециметровый диапазон)"
        elif 100 <= wavelength < 1000:
            diapazon = "Радиоволнами (метровый диапазон)"
        else:
            diapazon = "Неизвестным диапазоном"

        response = f"Вы отправили длину волны {wavelength} м. При такой длине света энергия фотона равна {energy} Дж*с. \n Вы работаете с {diapazon}"
    except ValueError:
        response = "Пожалуйста, введите корректное число."
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_end = KeyboardButton('Закончить работу')
    button_prod = KeyboardButton('Продолжить работу')
    markup.add(button_end, button_prod)
    bot.send_message(message.chat.id, response, reply_markup=markup)
def energy_voln(wavelength):
    c = 3e8  # скорость света в вакууме в м/с
    h = 6.626e-34  #постоянная Планка
    energy = (h * c) / wavelength
    return energy


'''___________________________Опрос пользователя о том, насколько он доволен опытом использования ассистента и каких функций ему не хватает.__________________________________________'''

@bot.message_handler(func=lambda message: message.text == 'Закончить работу')
def go_back_to_menu(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_menu = KeyboardButton('Главное меню')
    markup.add(button_menu)
    bot.send_message(message.chat.id, '''Замечательно поработали. До новых встреч✌
Если я Вам еще понадоблюсь, нажмите на кнопку "Главное меню"''', reply_markup=markup)
    # Опрос пользователя
    bot.send_message(message.chat.id, 'Пожалуйста, оцените ваш опыт использования ассистента от 1 до 5:')
    bot.register_next_step_handler(message, get_feedback)
def get_feedback(message):
    feedback = message.text
    bot.send_message(message.chat.id, 'Спасибо за ваш отзыв! Какие функции вам не хватало?')
    bot.register_next_step_handler(message, get_missing_features, feedback)
def get_missing_features(message, feedback):
    missing_features = message.text
    bot.send_message(message.chat.id, 'Спасибо за ваши предложения! Мы постараемся улучшить наш сервис.')


'''_______________________________________Вычисление флюенса лазерной системы по средней мощности.______________________________________________________________________'''

@bot.message_handler(func=lambda message: message.text == 'Лазерный флюенс')
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_end = KeyboardButton('Закончить работу')
    button_prod = KeyboardButton('Продолжить работу')
    markup.add(button_end, button_prod)
    bot.send_message(message.chat.id, "Давайте начнем. Пожалуйста, введите среднюю мощность лазера (в ваттах):", reply_markup=markup)
    bot.register_next_step_handler(message, get_average_power)
def get_average_power(message):
    try:
        average_power = float(message.text)
        bot.send_message(message.chat.id, "Введите площадь пятна лазера (в квадратных сантиметрах):")
        bot.register_next_step_handler(message, get_spot_area, average_power)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите числовое значение для средней мощности.")
        bot.register_next_step_handler(message, get_average_power)
def get_spot_area(message, average_power):
    try:
        spot_area = float(message.text)
        fluence = calculate_fluence(average_power, spot_area)
        bot.send_message(message.chat.id, f"Флюенс лазерной системы составляет {fluence} Дж/см².")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите числовое значение для площади пятна.")
        bot.register_next_step_handler(message, get_spot_area, average_power)
def calculate_fluence(average_power, spot_area):
    # Флюенс (J/cm²) = Средняя мощность (W) / Площадь пятна (cm²)
    return average_power / spot_area

print("Bot is running...")
bot.polling()