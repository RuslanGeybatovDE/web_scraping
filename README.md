С ростом цен на книги, у любителей чтения становится всё меньше возможностей по приобретению интересной литературы.
Некоторые интернет-ресурсы занимаются продажей "букинистических" книг. 
Например, http://lib26.ru/index.php - мой любимый местный ресурс. 
Любопытства ради, я решил исследовать данный ресурс, а именно провести так называемый web scraping.
Целью является определение стоимости книг в зависимости от года выпуска и автоматизация сбора информации.

Скрипт был написан на Python и SQLite. На выходе имеется небольшая БД, которая содержит год выпуска книги, её стоимость, название, количество страниц.
На основе данной БД строится график позволяющий оценить стоимость книг по годам выпуска. Сразу оговорюсь,  

![grab-landing-page](https://github.com/RuslanGeybatovDE/web_scraping/blob/main/P1.gif)
