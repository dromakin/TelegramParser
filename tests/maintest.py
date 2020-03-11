import unittest
from joblib import load
from pymystem3 import Mystem
from nltk.stem.snowball import RussianStemmer
import pandas as pd
import re

from nltk.corpus import stopwords

with open("./../docs/stopwords/fullstopwords.txt", 'r') as f:
    stopw = f.readlines()

v_stopwords = list(set([x[:-1] for x in stopw]))
print(len(v_stopwords))
mystopwords = stopwords.words('russian') + v_stopwords
mystopwords_ = list(set(mystopwords))

def remove_stopwords(text, mystopwords=None):
    if mystopwords is None:
        mystopwords = mystopwords_
    try:
        return " ".join([token for token in text.split() if not token in mystopwords])
    except:
        return ""


m = Mystem()
regex = re.compile("[А-Яа-я]+")


def words_only(text, regex=regex):
    try:
        return " ".join(regex.findall(text))
    except:
        return ""


def lemmatize(text, mystem=m):
    try:
        return "".join(m.lemmatize(text)).strip()
    except:
        return " "


def stemming(text, stemmer=RussianStemmer()):
    try:
        return " ".join([stemmer.stem(w) for w in text.split()])
    except:
        return " "

class TestStringMethods(unittest.TestCase):

    def test_model(self):


        s = "Buzzfeed пишет о том, как компания по сбору аналитики из приложений (Senson Tower) для скрытого сбора подобной аналитики, но уже из других приложений также выпускает приложения как VPN-сервисы и блокировщики рекламы: Free and Unlimited VPN, Luna VPN, Mobile Data и Adblock Focus. Будучи установленными, эти приложения предлагали поставить корневой сертификат, после чего пропусткали через себя весь трафик с телефона. Компания утверждает, что собирала анонимные данные по использованию приложений. Проблема, как говорят эксперты, в том, что пользователи думают, что речь идет о блокировке рекламы или о том, что \"соединение безопасно и данные никто не видит\", но на самом деле все совсем не так. Ну и то, что компания никак не раскрывала принадлежность таких приложений и сбор данных через них, доверия всей этой схеме не добавляет.  Google и Apple удалили некоторые приложения из магазинов, с остальными разбираются. Бесплатные продукты иногда бывают такими, да\nhttps://www.buzzfeednews.com/article/craigsilverman/vpn-and-ad-blocking-apps-sensor-tower"

        clf = load('/Users/romakindmitriy/PycharmProjects/TelegramParser/docs/models/clf_all.sav')

        data = [[s]]
        df = pd.DataFrame(data, columns=['message'])

        df.message = df.message.apply(lemmatize)
        df.message = df.message.apply(remove_stopwords)

        r = float(clf.predict(df['message'][:1])[0])

        self.assertTrue(r in [1., 2., 3., 4., 5.])




if __name__ == '__main__':
    unittest.main()
