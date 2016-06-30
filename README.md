# ContentParser
Test task for Tenzor.

Находит на странице основной текст, форматирует и сохраняет его вместе с картинками в тексте.

Форматирование:
- обрезка длины строки до 80 символов
- замена ссылок вида [link]text
- замена картинок вида [image]
- удаление всех тегов html

Что можно улучшить:
- больше проверок на оценку текста
- больше методов поиска текста

Использование:

run.py -u http://example.com/

Список проверенных страниц:
https://habrahabr.ru/post/304434/
http://ria.ru/syria/20160630/1455091290.html
http://gmbox.ru/overwatch/overwatch-iz-zari-sdelali-lgbt-ikonu

