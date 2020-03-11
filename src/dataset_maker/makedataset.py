import configparser
import json
import csv

from pprint import pprint

from telethon.sync import TelegramClient
from telethon import connection

# для корректного переноса времени сообщений в json
from datetime import date, datetime

# классы для работы с каналами
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

class DatasetMaker:

    def __init__(self, path_with_name_csv) -> None:
        self.path_with_name = path_with_name_csv
        # Считываем учетные данные
        config = configparser.ConfigParser()
        config.read("./../config.ini")

        # Присваиваем значения внутренним переменным
        api_id = int(config['Telegram']['api_id'])
        api_hash = config['Telegram']['api_hash']
        username = config['Telegram']['username']

        # print(username, api_id, api_hash)
        self.client = TelegramClient(username, api_id, api_hash)
        # ch1=3338, ch2=5430, ch3=191008, ch4=455247
        # self.channels = [("https://t.me/alexmakus",3337), ("https://t.me/CicadaHere",5429),
        #                  ("https://t.me/spherechat",191007), ("https://t.me/spherechatflood",455246)]

        self.channels = {"https://t.me/alexmakus": 3337,
                         "https://t.me/CicadaHere": 5429,
                         "https://t.me/spherechat": 191007,
                         "https://t.me/spherechatflood": 455246}

        # self.data_to_scv(self.path_with_name)

        super().__init__()

    async def dump_all_messages(self, channel, url, ch):
        i = ch
        end = int()
        if url == "https://t.me/alexmakus":
            end = self.channels[url] - 300
        elif url == "https://t.me/CicadaHere":
            end = self.channels[url] - 300
        elif url == "https://t.me/spherechat":
            end = self.channels[url] - 300
        elif url == "https://t.me/spherechatflood":
            end = self.channels[url] - 600

        while i >= end:
            """Записывает json-файл с информацией о всех сообщениях канала/чата"""
            offset_msg = i  # номер записи, с которой начинается считывание
            limit_msg = 100  # максимальное число записей, передаваемых за один раз

            all_messages = []  # список всех сообщений
            total_messages = 0
            total_count_limit = 1  # меняем это значение, если нам нужны не все сообщения

            # class DateTimeEncoder(json.JSONEncoder):
            #     '''Класс для сериализации записи дат в JSON'''
            #
            #     def default(self, o):
            #         if isinstance(o, datetime):
            #             # return o.isoformat()
            #             return o.timestamp()
            #         if isinstance(o, bytes):
            #             return list(o)
            #         return json.JSONEncoder.default(self, o)

            while True:
                history = await self.client(GetHistoryRequest(
                    peer=channel,
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

            # with open('channel_messages.json', 'w', encoding='utf8') as outfile:
            #     json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder)

            data = []
            for message in all_messages:
                d = {}
                keys = ['channel_id','id','date', 'message', 'url', 'site_name', 'title', 'description', 'class']
                if message["_"] == "Message":
                    for k in keys:

                        if k == "channel_id":
                            d.update({k: message["to_id"]["channel_id"]})

                        elif k == "url" or k == "site_name" or k == "title" or k == "description":
                            if "media" in message.keys() and type(message["media"]) == dict:
                                if "webpage" in message["media"] and type(message["media"]["webpage"]) == dict:
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

                        elif k == 'class':
                            print('\nMessage:\n')
                            pprint(message['message'])
                            print()
                            cl = input("1. Реклама\n2. Новости\n3. Флуд/Спам\n4. Общение\n5. Безопасность, Утечки, Уязвимости\nОтвет: ")
                            cl = int(cl)
                            d.update({k: cl})
                            print('OK!\n')
                        else:
                            d.update({k: message[k]})

                data.append(d)

            if len(data) > 0:
                self.data_to_scv(self.path_with_name, data=data, mod='write')
                print(f"i: {i}, load to csv: ok")

            i -= 100

    @staticmethod
    def data_to_scv(path_with_name, data=None, mod='init'):
        fieldnames = ['channel_id', 'id', 'date', 'message', 'url', 'site_name', 'title',
                      'description', 'class']
        if mod == 'init':
            with open(f'{path_with_name}', 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
        elif mod == 'write':
            # print(data)
            with open(f'{path_with_name}', 'a', encoding='utf8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                for d in data:
                    writer.writerow(d)


    def run_app(self,):
        self.client.start()
        with self.client:
            self.client.loop.run_until_complete(self.main())

    async def main(self):
        for channel in self.channels.keys():
            ch = self.channels[channel]
            url = channel
            print("loading channel...")
            channel = await self.client.get_entity(url)
            print("start load messages")
            await self.dump_all_messages(channel, url=url, ch=ch)



if __name__ == '__main__':
    ds = DatasetMaker('dataset_classes.csv')
    ds.run_app()



