"""
parser

Основной модуль для работы с парсером данных из telegram
Все функции класса Parser описаны только в этом модуле.

Created at 11.03.2020 by Dmitriy Romakin. Project <Telegram Parser>
Примеры использования:

$ python parser.py -d -ch https://t.me/CicadaHere -n 1 -c configs/config.ini --csv -p
$ python parser.py -a -n 2 -c configs/config.ini --csv -p

TODO:


"""
import configparser
import json
import csv

from telethon.sync import TelegramClient
from telethon import connection

from datetime import date, datetime

from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from telethon.tl.functions.messages import GetHistoryRequest

import logging
import logging.config

logging.config.fileConfig('configs/logging.conf')

import argparse
import os
import shutil

from joblib import load
from pymystem3 import Mystem
from nltk.stem.snowball import RussianStemmer
from nltk.corpus import stopwords
import pandas as pd
import re

class Parser:

    def __init__(self, mod=None, channel=None, number=None,
                 path_to_config_file=None,
                 proxy_mod=False, csv_save=False,
                 debug="False") -> None:

        self.__mod = mod
        self.__channel = channel
        self.__number = number
        self.__csv_save = csv_save

        if debug == "False":
            self.__logger = logging.getLogger('app')
        else:
            self.__logger = logging.getLogger('root')

        self.__logger.debug("Loading __path_to_config_file")
        if path_to_config_file is None:
            self.__logger.warning("Try to find config file without path to config file.")
            self.__path_to_config_file = "configs/config.ini"
        else:
            self.__path_to_config_file = path_to_config_file

        self.__logger.debug("Get __path_to_save_files from __loadPathFolders()")
        self.__path_to_save_files = self.__loadPathFolders()

        self.__logger.debug("Get Telegram client")
        self.__client = self.__loadingSettingsClient(self.__path_to_config_file, proxy_mod)

        self.__stopwords = self.__loadStopWords()
        self.__m = Mystem()

        super().__init__()

    def start(self):
        self.__client.start()

        self.__logger.info("Client started.")

        with self.__client:
            self.__client.loop.run_until_complete(self.__mainHandler())

        self.__logger.info("Done!")

    async def __mainHandler(self):
        self.__logger.debug("Creating a new folder")
        self.__createFolder(self.__path_to_save_files)

        if self.__mod == 'default':
            self.__logger.debug("DEFAULT: Get jsons from channel")
            jsonsR = await self.__get_messages()

            self.__logger.debug("DEFAULT: predicted class")
            jsonsList = await self.__predictClass(jsonsR)

            self.__saveJsons(jsonsList)

            if self.__csv_save is True:
                self.__saveCSV(jsonsList=jsonsList)

        elif self.__mod == 'auto':
            self.__logger.debug("AUTO: Get channels")
            channels = await self.__loadChannels()
            channels = channels.split(' ')
            jsonsR = []
            for i in range(len(channels)):
                self.__channel = channels[i]
                self.__logger.debug("AUTO: Get jsons from channel")
                partJsonsList = await self.__get_messages()
                jsonsR += partJsonsList

            self.__logger.debug("AUTO: predicted class")
            jsonsList = await self.__predictClass(jsonsR)

            self.__saveJsons(jsonsList)

            if self.__csv_save is True:
                self.__saveCSV(jsonsList=jsonsList)

    def __loadStopWords(self):
        self.__logger.debug("Get path to stopwords")
        config = configparser.ConfigParser()
        config.read(self.__path_to_config_file)
        fullpath = config['Path_to_stopwords']['stopwords']

        stopw = None
        self.__logger.debug("Loading stopwords")
        with open(fullpath, 'r') as f:
            stopw = f.readlines()

        v_stopwords = list(set([x[:-1] for x in stopw]))
        mystopwords = stopwords.words('russian') + v_stopwords
        mystopwords = list(set(mystopwords))

        return mystopwords

    def __remove_stopwords(self, text, mystopwords=None):
        if mystopwords is None:
            mystopwords = self.__stopwords
            # raise Exception("mystopwords is None")
        try:
            return " ".join([token for token in text.split() if not token in mystopwords])
        except:
            return ""

    @staticmethod
    def __lemmatize(text, mystem=Mystem()):
        try:
            return "".join(mystem.lemmatize(text)).strip()
        except:
            return " "

    async def __predictClass(self, jsonsList=None) -> list:
        if jsonsList is None:
            raise Exception("jsonsList is None")

        jsonR = jsonsList

        self.__logger.debug("Get path to models")
        config = configparser.ConfigParser()
        config.read(self.__path_to_config_file)
        path_to_model = config['Models']['model']

        self.__logger.debug("Loading model")
        clf = load(path_to_model)

        jsonResult = []

        for jsn in jsonR:
            if "message" in jsn.keys():
                d = jsn.copy()
                msg = jsn["message"]

                data = [[msg]]
                df = pd.DataFrame(data, columns=['message'])

                self.__logger.debug("Loading __lemmatize")
                df.message = df.message.apply(self.__lemmatize)
                self.__logger.debug("Loading __remove_stopwords")
                df.message = df.message.apply(self.__remove_stopwords)
                self.__logger.debug("Loading predict")
                r = float(clf.predict(df['message'][:1])[0])
                self.__logger.debug("Update json")
                d.update({'Classification': r})

                jsonResult.append(d)

        self.__logger.debug("return jsonResult")
        return jsonResult

    async def __get_id_msg(self) -> int:
        self.__logger.debug("Try to get id from the first message:")
        offset_msg = 0  # номер записи, с которой начинается считывание
        limit_msg = 1  # максимальное число записей, передаваемых за один раз

        all_messages = []  # список всех сообщений
        total_messages = 0
        total_count_limit = 1  # поменяйте это значение, если вам нужны не все сообщения

        self.__logger.debug("Loading message")
        while True:
            history = await self.__client(GetHistoryRequest(
                peer=self.__channel,
                offset_id=offset_msg,
                offset_date=None, add_offset=0,
                limit=limit_msg, max_id=0, min_id=0,
                hash=0))
            if not history.messages:
                break
            messages = history.messages
            for message in messages:
                all_messages.append(message.to_dict())
            offset_msg = messages[len(messages) - 1].id
            total_messages = len(all_messages)
            if total_count_limit != 0 and total_messages >= total_count_limit:
                break

        self.__logger.debug("Get id from the first message")
        id = int(all_messages[0]["id"])
        return id

    async def __get_messages(self) -> list:
        self.__logger.debug("Loading numbers for settings...")
        number_msg = self.__number
        lots_msg = await self.__get_id_msg()
        end = lots_msg - number_msg

        i = lots_msg

        get_limit = lambda n: 100 if n >= 100 else n
        limit_msg = get_limit(number_msg)
        all_messages = []
        total_messages = 0
        total_count_limit = 1

        self.__logger.debug("Start loading messages...")
        while i >= end:
            while True:
                history = await self.__client(GetHistoryRequest(
                    peer=self.__channel,
                    offset_id=i,
                    offset_date=None, add_offset=0,
                    limit=limit_msg, max_id=0, min_id=0,
                    hash=0))
                if not history.messages:
                    break
                messages = history.messages
                for message in messages:
                    all_messages.append(message.to_dict())
                offset_msg = messages[len(messages) - 1].id
                total_messages = len(all_messages)
                if total_count_limit != 0 and total_messages >= total_count_limit:
                    break

            i -= limit_msg

        self.__logger.debug("Returnt all_messages")
        return all_messages

    def __saveJsons(self, jsonsList=None):
        if jsonsList is None:
            raise Exception("jsonsList is None")

        class DateTimeEncoder(json.JSONEncoder):
            '''Класс для сериализации записи дат в JSON'''

            def default(self, o):
                if isinstance(o, datetime):
                    return o.isoformat()
                    # return o.timestamp()
                if isinstance(o, bytes):
                    return list(o)
                return json.JSONEncoder.default(self, o)

        jsons = jsonsList
        with open(self.__path_to_save_files + '/msg.json', 'w', encoding='utf8') as outfile:
            json.dump(jsons, outfile, ensure_ascii=False, cls=DateTimeEncoder)

    def __saveCSV(self, jsonsList: list = None) -> None:
        if jsonsList is None:
            raise Exception('jsonsList is None')

        data = []
        for message in jsonsList:
            d = {}
            keys = ['channel_id', 'id', 'date', 'message', 'url', 'site_name', 'title',
                    'description', 'Classification']
            if message["_"] == "Message":
                for k in keys:

                    if k == "channel_id":
                        d.update({k: message["to_id"]["channel_id"]})

                    elif k == "url" or k == "site_name" or k == "title" or k == "description":
                        if "media" in message.keys() and type(message["media"]) == dict:
                            if "webpage" in message["media"] and type(
                                    message["media"]["webpage"]) == dict:
                                if k in message["media"]["webpage"].keys():
                                    d.update({k: message["media"]["webpage"][k]})
                                else:
                                    d.update({k: ""})
                            else:
                                d.update({k: ""})
                        else:
                            d.update({k: ""})
                    elif k == 'date':
                        d.update({k: datetime.timestamp(message[k])})
                    else:
                        d.update({k: message[k]})

            data.append(d)

        if len(data) > 0:
            self.__data_to_scv(self.__path_to_save_files + '/msg.csv', data=data)

    async def __loadChannels(self):
        config = configparser.ConfigParser()
        config.read(self.__path_to_config_file)
        return config['Channels']['ch']

    def __loadPathFolders(self):
        config = configparser.ConfigParser()
        config.read(self.__path_to_config_file)
        return config['Folder']['path']

    @staticmethod
    def __data_to_scv(path_with_name, data=None):
        fieldnames = ['channel_id', 'id', 'date', 'message', 'url', 'site_name', 'title',
                      'description', 'Classification']
        with open(f'{path_with_name}', 'a', encoding='utf8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for d in data:
                writer.writerow(d)

    @staticmethod
    def __createFolder(directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)

            shutil.rmtree(directory, ignore_errors=True)
            os.makedirs(directory)
        except OSError:
            print('Error: Creating directory. ' + directory)

    def __loadingSettingsClient(self, path_to_config_file, proxy_mod) -> TelegramClient:
        config = configparser.ConfigParser()
        config.read(path_to_config_file)

        api_id = int(config['Telegram']['api_id'])
        api_hash = config['Telegram']['api_hash']
        username = config['Telegram']['username']

        client = None

        self.__logger.debug("Loading api_id, api_hash and username")

        if proxy_mod is True:

            self.__logger.debug("Loading proxy_server, proxy_port and proxy_key")

            proxy_server = config['Proxy']['server']
            proxy_port = int(config['Proxy']['port'])
            proxy_key = config['Proxy']['key']

            # proxy_key = "ddfb175d6d7f820cdc73ab11edbdcdbd74"
            # https://ru.stackoverflow.com/questions/962679/%D0%9A%D0%B0%D0%BA-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D1%8C-mtproto-%D0%B2-telethon-%D0%BD%D0%B0-python
            if proxy_key[:2] == "dd":
                self.__logger.warning(
                    "proxy_key in config file starts with \"dd\"")

            proxy = (proxy_server, proxy_port, proxy_key)

            client = TelegramClient(username, api_id, api_hash,
                                    connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
                                    proxy=proxy)

        else:
            client = TelegramClient(username, api_id, api_hash)

        return client


def app(mod=None, channel=None, number=None,
        path_to_config_file=None, proxy_mod=False, csv_save=False):
    parser = Parser(mod=mod, channel=channel, number=number,
                    path_to_config_file=path_to_config_file,
                    proxy_mod=proxy_mod, csv_save=csv_save)

    parser.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Telegram parser! Welcome!")
    mods = parser.add_mutually_exclusive_group()

    mods.add_argument("-d", "--default", action="store_true", help="The default mod args: ch + n")
    mods.add_argument("-a", "--auto", action="store_true",
                      help="The auto mod args: number of messages")

    parser.add_argument("-ch", "--channel", type=str, help="The channel link")
    parser.add_argument("-n", "--number", type=int, help="The number of messages")

    # options = parser.add_mutually_exclusive_group()
    parser.add_argument("-c", "--config", type=str, help="The path to the configuration file")
    parser.add_argument("-cv", "--csv", action="store_true",
                         help="The answer of classification save to csv")
    parser.add_argument("-p", "--proxy", action="store_true",
                         help="The activation proxy mod")

    args = parser.parse_args()

    try:
        if args.default:
            if args.channel and args.number:
                path_to_config_file = None
                csv_ = False
                proxy_ = False
                if args.config:
                    path_to_config_file = args.config

                if args.csv:
                    csv_ = True

                if args.proxy:
                    proxy_ = True

                app('default', args.channel, int(args.number), path_to_config_file, proxy_, csv_)
            else:
                raise Exception("Write --help for more information or use the documentation.")

        elif args.auto:
            if not args.channel:
                path_to_config_file = None
                csv_ = False
                proxy_ = False
                if args.config:
                    path_to_config_file = args.config

                if args.csv:
                    csv_ = True

                if args.proxy:
                    proxy_ = True

                app('auto', args.channel, int(args.number), path_to_config_file, proxy_, csv_)
            else:
                raise Exception("Write --help for more information or use the documentation.")

    except Exception as err:
        print(str(err))
