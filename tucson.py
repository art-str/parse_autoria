import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import difflib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import datetime
import time

def rename_file(csv_name):
    new_file = f'{csv_name}.csv'
    old_file = f'{csv_name}_old.csv'

    if os.path.exists(new_file):
        if os.path.exists(old_file):
            os.remove(old_file)
        os.rename(new_file, old_file)
    else:
        print(f'Файл {new_file} не существует.')

def collect_data(csv_name):
    hyundai_list = []
    for id in [293, 1268]:
        for page_num in range(1):
            url = f'https://auto.ria.com/uk/search/?indexName=auto,order_auto,newauto_search&year[0].gte=2007&year[0].lte=2010&categories.main.id=1&brand.id[0]=29&model.id[0]={id}&country.import.usa.not=-1&price.currency=1&sort[0].order=dates.created.desc&abroad.not=0&custom.not=1&page={page_num}&size=10'
            print(page_num)
            tucson = requests.get(url)
            soup = BeautifulSoup(tucson.content, 'html.parser')
            cars = soup.find_all('div', class_='content-bar')
            print(len(cars))
            key_words = ['Продає AUTO.RIA', 'Кредит до 3 років під 0.01%', 'Онлайн бронювання', 'Новий Hyundai SANTA FE']
            if cars:
                headings = ['model', 'year', 'price_usd', 'price_hrn', 'mileage', 'city', 'engine', 'transmission']
                for car in cars:
                    car_text = car.text
                    car_text = re.sub(r'Hyundai Santafe 2010.*', '', car_text)
                    car = [info.strip() for info in car.text.split('   ') if info != ''][:10]
                    if any(keyword in ' '.join(car) for keyword in key_words):
                        continue
                    #if 'Онлайн бронювання' in [hyund for hyund in car]: continue
                    car = [car for car in car if len(car) != 1]
                    hyundai_list.append(car)
            else:
                break
            print(f'Сканирую {page_num}_ю страницу')
        hyund_df = pd.DataFrame(hyundai_list, columns=headings)
        hyund_df.to_csv(f'{csv_name}.csv', index=False, encoding='utf-8-sig')
        print(hyundai_list)



def check_files(csv_name):
    print('Проводится проверка файлов')
    new_file = f'{csv_name}.csv'
    old_file = f'{csv_name}_old.csv'
    if os.path.exists(old_file):
        with open(new_file, 'r', encoding='utf-8-sig') as nf, open(old_file,'r', encoding='utf-8-sig') as of:
            diferent = list(difflib.unified_diff(nf.read().splitlines(), of.read().splitlines(), lineterm=''))
    else:
        diferent = []
    if diferent:
        print('В файлах обнаружены изменения')
        for line in diferent:
            print(line)
    return(diferent)

def send_massege(csv_name):
    print('Попытка выполнить операцию')
    server = 'smtp.gmail.com'
    port = 587
    user_email = 'artstr3001@gmail.com'
    password = 'vglt wqjk sxpc allj'
    recipient_email = 'strelnikov-a@ukr.net'
    msg = MIMEMultipart()
    msg['From'] = user_email
    msg['To'] = recipient_email
    msg['Subject'] = 'Новый файл или изменения в файле Hyundai'
    csv_file = f'{csv_name}.csv'
    new_file = f'{csv_name}.csv'
    old_file = f'{csv_name}_old.csv'
    attachment_added = False
    if not os.path.exists(old_file) and os.path.exists(new_file):
        print('Будет отправлен новый файл')
        body = 'Создан новый файл'
        msg.attach(MIMEText(body, 'plain'))
        with open(new_file, 'rb') as cf:
            attachment = MIMEApplication(cf.read(), _subtype="csv")
            attachment.add_header('Content-Disposition', 'attachment', filename=f'{csv_name}.csv')
            msg.attach(attachment)
        attachment_added = True
    else:
        if check_files(csv_name):
            print('Обнаружены изменения')
            body = 'Обнаружены изменения'
            msg.attach(MIMEText(body, 'plain'))
            with open(csv_file, 'rb') as cf:
                attachment = MIMEApplication(cf.read(), _subtype="csv")
                attachment.add_header('Content-Disposition', 'attachment', filename=f'{csv_name}.csv')
                msg.attach(attachment)
            attachment_added = True
        else:
            print('Изменений в файле нет')

    if attachment_added:
        print('Выполняется соединение и отправка письма')
        try:
            gmail_server = smtplib.SMTP(server, port)
            gmail_server.starttls()
            print('Успешно подключено к серверу')
            gmail_server.login(user_email, password)
            print('Успешно авторизовано')
            text = msg.as_string()
            gmail_server.sendmail(user_email, recipient_email, text)
            gmail_server.quit()
            print('Письмо успешно отправлено')
        except Exception as e:
            print('fig')
            print(f'Ошибка отправки: {e}')

def main():
    print('Добрый день!')
    print('Сейчас будет выполнена программа')
    print('по сбору данных автомобильной марки "Hyundai"')
    print('моделей Santa Fe и Tucson 2007-2010 годов выпуска')
    csv_name = 'Hyundai'
    rename_file(csv_name)
    collect_data(csv_name)

    #check_files(csv_name)
    send_massege(csv_name)

if __name__ == '__main__':
    main()