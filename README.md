# Букинистическая стоимость книг  и web scraping
С ростом цен на книги, у любителей чтения становится всё меньше возможностей по приобретению интересной литературы.
Некоторые интернет-ресурсы занимаются продажей "букинистических" книг. 
Например, http://lib26.ru/index.php - мой любимый местный ресурс. 
Любопытства ради, я решил исследовать данный ресурс, а именно провести так называемый web scraping.
Целью является определение стоимости книг в зависимости от года выпуска и автоматизация сбора информации.

Скрипт был написан на Python и SQLite. На выходе имеется небольшая БД, которая содержит год выпуска книги, её стоимость, название, количество страниц. В БД создано две таблицы, основная и вспомогательная. Я считаю, что стоимость книг не должна превышать 500 рублей (если речь не об антиквариате), поэтому, в основную таблицу, я вносил данные отвечающие некоторым критериям, а именно: стоимость не более 500 рублей, год выпуска не старше 1950 года. Всё что не соответствовало данным требованиям, отправлялось во вспомогательную талицу, возможно в будущем такая информация мне пригодится. Кроме того, во вспомогательную таблицу, отправлись записи в с "аномальными" значениями, то есть с очень высокой стомостью, с нулевой стоимость, ранние года выпуска и т.п.

По данным основной таблицы БД строится график позволяющий оценить стоимость книг по годам выпуска. 

Данный скрипт, запускается у меня автоматически, раз в неделю через обычный планировщик задач windows.
## Динамика изменения цен
![grab-landing-page](https://github.com/RuslanGeybatovDE/web_scraping/blob/main/P1.gif)
## Планы на будущее
В дальнейшем я планирую добавить парраллельный скрапинг ещё одного местного онлайн ресурс. Это позволит проводить сравнение цен и выявлять лучшие цены на одну и ту же позицию.
