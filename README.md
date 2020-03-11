# TelegramParser
Тестовое задание

## Что это?

Модуль, который парсит данные из 4 каналлов телеграмма, классифицирует по 5 классам, сохраняет в json (+ csv).

## На какие классы разбиваются сообщения?

1. Реклама
2. Новости
3. Флуд/Спам
4. Общение (Вопросы/Ответы)
5. Тексты про взломы, утечки информации, критические уязвимости

## Как использовать?

1. Переходим в корень проекта через терминал

2. Вводим: 
    $ python parser.py --help
    
```
    python parser.py --help

    usage: parser.py [-h] [-d | -a] [-ch CHANNEL] [-n NUMBER] [-c CONFIG] [-cv] [-p]

    Telegram parser! Welcome!

    optional arguments:
    -h, --help            show this help message and exit
    -d, --default         The default mod args: ch + n
    -a, --auto            The auto mod args: number of messages
    -ch CHANNEL, --channel CHANNEL
                            The channel link
    -n NUMBER, --number NUMBER
                            The number of messages
    -c CONFIG, --config CONFIG
                            The path to the configuration file
    -cv, --csv            The answer of classification save to csv
    -p, --proxy           The activation proxy mod
```

## Пояснение

### Главные режимы работы

1. -d, --default         The default mod args: ch + n

Default режим работы для парсера. 
Обязательно указывать параметры -ch (ссылка на канал) и -n (количество сообщений, которые мы хотим загрузить и обработать).

Пример:
```
    $ python parser.py -d -ch https://t.me/CicadaHere -n 1
```

2. -a, --auto            The auto mod args: number of messages

Авто режим работы для парсера.
Обязательно укать параметр -n (количество сообщений, которые мы хотим загрузить и обработать).
Произойдет итерация по 4 каналам, из которых будет скачано n последних сообщений и они же будут обработаны классификатором и сохранены в json файл.

Пример:
```
    $ python parser.py -a -n 2
```

### Опции

1. -c CONFIG, --config CONFIG The path to the configuration file

Можно указать путь до конфигурационного канала, если парсер его не находит.

Пример 1.1:
```
    $ python parser.py -d -ch https://t.me/CicadaHere -n 1 -c configs/config.ini
```

Пример 1.2:
```
    $ python parser.py -a -n 2 -c configs/config.ini
```

2. -cv, --csv            The answer of classification save to csv

Помимо сохранения в json всех сообщений, парсер может также все сохранить в csv.

Пример 2.1:
```
    $ python parser.py -d -ch https://t.me/CicadaHere -n 1 -c configs/config.ini --csv
```

Пример 2.2:
```
    $ python parser.py -a -n 2 -c configs/config.ini --csv
```

3. -p, --proxy           The activation proxy mod

В конфигурационном файле указываем прокси сервер и необходимые данные, которые парсер будет использовать при подключении.

Пример 3.1:
```
    $ python parser.py -d -ch https://t.me/CicadaHere -n 1 -c configs/config.ini --csv -p
```

Пример 3.2:
```
    $ python parser.py -a -n 2 -c configs/config.ini --csv -p
```

## Куда сохраняется json/csv?

Json и csv файл сохраняются в папку, которая указана в конфигурационном файле config.ini

Folder - это путь + название папки, которая будет перезаписываться при каждом запуске парсера.
```
    [Folder]
    path = ./parser_msg
```

## Как настроить прокси / куда вставлять свои данные?

Данные о себе добавляем в конфигурационный файл config.ini

```
    [Telegram]
    api_id = your_id
    api_hash = your_api_hash
    username = your_username_from_telegram_without_@
    [Proxy]
    server = proxy.digitalresistance.dog
    port = 443
    key = d41d8cd98f00b204e9800998ecf8427e
```
