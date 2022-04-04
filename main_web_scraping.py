#подключаем необходимые библиотеки
import requests
from bs4 import BeautifulSoup
from lxml import html
import pandas as pd
import re
from time import sleep
import matplotlib
from matplotlib.pyplot import axes
from matplotlib import rcParams
import seaborn as sns
import sqlite3
#обнуление переменных
year = []
product_info = []
number_of_pages = []
price = []
title = []
list_product_info = []
list_title = []
data_info = []
title_info = []
#задаём количество страниц для парсинга, считаем что за неделю не появится больше 10 стр.
pages = 10
#функция запросов
def get_db(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
    req = requests.get(url, headers)
    sleep(3) #небольшая задержка чтобы не заблокировали
    with open("parsingDB_info.html", "w") as file_info:
        file_info.write(req.text)
#пошаговое чтение интересующих страниц
for y in range (1, pages):
    get_db(f"http://lib26.ru/index.php?page={y}")
    with open("parsingDB_info.html") as file_info:
        src = file_info.read()
    soup = BeautifulSoup(src, "html.parser")
    product_info = soup.find_all('div',class_="product_info")
    for i in product_info:
        list_product_info.append(i.text.replace('\xa0',''))
    title_info = soup.find_all('div',class_="templatemo_product_box")
    for i in title_info:
        list_title.append(i.text.replace('\xa0',''))
#вытягивание необходимой информации
for i in range(len(list_product_info)):
    year.append(int(list_product_info[i][list_product_info[i].find('Год издания - ') + 14:list_product_info[i].find(' г.')]))
    st = list_product_info[i][list_product_info[i].find('Страниц - ') + 10:list_product_info[i].find('Год издания')]
    x = re.findall('[0-9]+', st)
    jx = 0
    for j in x:
        jx += int(j)
    number_of_pages.append(jx)
    z = re.findall('[0-9]+',(list_product_info[i][list_product_info[i].find('Цена - ') + 7:len(list_product_info[i])]))
    zx = 0
    for j in z:
        zx += int(j)
    price.append(int(zx))

for i in range(len(list_title)):
    title.append((list_title[i][0:list_title[i].find('Автор')]))
for i in range(len(year)):
    tuple_date = (title[i], year[i], number_of_pages[i], price[i])
    data_info.append(tuple_date)
#обнуляем и создаём датафрейм
df = 0
df = pd.DataFrame(data_info, columns=['TITLE', 'YEAR', 'NUMBER_OF_PAGES', 'PRICE'])
#создаём или подключаемся к базе данных
connection = sqlite3.connect('parsing_old_books.db')
cursor = connection.cursor()
#создаём временную таблицу в БД, в которую вставляем данные с датафрейма
cursor.execute('''CREATE TABLE IF NOT EXISTS OLD_BOOKS_SOURCE
              (TITLE VARCHAR(2000), 
              YEAR INT, 
              NUMBER_OF_PAGES INT, 
              PRICE INT)''')
sql_insert_src = '''
    INSERT INTO OLD_BOOKS_SOURCE(TITLE, YEAR, NUMBER_OF_PAGES, PRICE) 
    VALUES
    (?, ?, ?, ?)
'''
columns = [0, 1, 2, 3]
df_to_export = df[[df.columns[c] for c in columns]].to_dict('list')
cursor.executemany(sql_insert_src, zip(*(df_to_export.values())))
#создаём основную таблицу БД
cursor.execute('''CREATE TABLE IF NOT EXISTS OLD_BOOKS_DWH
             (TITLE VARCHAR(2000), YEAR INT, NUMBER_OF_PAGES INT, PRICE INT)''')
#создаём вспомогательную таблицу БД
cursor.execute('''CREATE TABLE IF NOT EXISTS OLD_BOOKS_DWH_ANOMALY
             (TITLE VARCHAR(2000), YEAR INT, NUMBER_OF_PAGES INT, PRICE INT)''')
#вставляем только уникальные данные из временной таблицы в основную таблицу БД
cursor.execute('''
    INSERT INTO OLD_BOOKS_DWH(TITLE, YEAR, NUMBER_OF_PAGES, PRICE) 
    SELECT SRC.TITLE, SRC.YEAR, SRC.NUMBER_OF_PAGES, SRC.PRICE FROM OLD_BOOKS_SOURCE SRC
    LEFT JOIN OLD_BOOKS_DWH DWH
    ON DWH.TITLE = SRC.TITLE AND DWH.YEAR = SRC.YEAR AND DWH.NUMBER_OF_PAGES = SRC.NUMBER_OF_PAGES AND DWH.PRICE = SRC.PRICE
    WHERE DWH.TITLE IS NULL''')
#вставляем только уникальные данные из постоянной таблицы во вспомогательную таблицу БД, которые нежелательны для основной
cursor.execute('''
    INSERT INTO OLD_BOOKS_DWH_ANOMALY(TITLE, YEAR, NUMBER_OF_PAGES, PRICE) 
    SELECT TITLE, YEAR, NUMBER_OF_PAGES, PRICE FROM
    (SELECT DWH.TITLE, DWH.YEAR, DWH.NUMBER_OF_PAGES, DWH.PRICE FROM OLD_BOOKS_DWH DWH
    LEFT JOIN OLD_BOOKS_DWH_ANOMALY ANM
    ON DWH.TITLE = ANM.TITLE AND DWH.YEAR = ANM.YEAR AND DWH.NUMBER_OF_PAGES = ANM.NUMBER_OF_PAGES AND DWH.PRICE = ANM.PRICE    
    WHERE ANM.TITLE IS NULL)
    WHERE YEAR = 0 OR YEAR < 1950 OR PRICE = 0 OR PRICE >= 500 OR NUMBER_OF_PAGES = 0''')
#удаляем из основной таблицы нежелательные данные
cursor.execute('''
    DELETE FROM OLD_BOOKS_DWH
    WHERE YEAR = 0 OR YEAR < 1950 OR PRICE = 0 OR PRICE >= 500 OR NUMBER_OF_PAGES = 0''')
#удаляем временную таблицу
cursor.execute('''DROP TABLE OLD_BOOKS_SOURCE''')
#создаём ДФ из запроса к БД
df = 0
df = pd.read_sql('''SELECT * FROM OLD_BOOKS_DWH''', connection)
#коммитим и закрываем
connection.commit()
connection.close()
#создаём интересующий нас график
rcParams['figure.figsize'] = 13,10
sns.set_style("darkgrid")
sns.lineplot(data = df, x = "YEAR", y = "PRICE")