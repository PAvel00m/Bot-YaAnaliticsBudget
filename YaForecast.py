# -*- codecs: utf-8 -*-
import base64
import json
import bs4
import requests
import sys 


class Forecast():
    def __init__(self, keys, regions_id, is_mobile, login, passwd, anticapcha_key):
        self.keys = keys
        self.regions = regions_id
        self.is_mobile = is_mobile
        self.login = login
        self.passwd = passwd
        self.ANTICAPTCHA_KEY = anticapcha_key
        self.status_ = ''
        self.session = ''
        self.data_auth = {'retpath' : 'https://passport.yandex.ru/auth/login-status_v2.html?method=password',
                          'source': 'password',
                          'login': login,
                          'passwd': passwd
        }
        self.data_forecast = {'csrf_token': 'DzP6Tb4O6CdUBefp',
                              'cmd': 'ajaxDataForNewBudgetForecast',
                              'advanced_forecast': 'yes',
                              'period': 'month',
                              'period_num': '0',
                              'phrases': keys,
                              'json_minus_words': [],
                              'geo': regions_id,
                              'unglue': '1',
                              'fixate_stopwords': '1',
                              'currency': 'RUB'
        }
        self.headers_auth = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                             'Accept-Encoding': 'gzip, deflate, br',
                             'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                             'Cache-Control': 'max-age=0',
                             'Connection': 'keep-alive',
                             'Content-Length': '263',
                             'Content-Type': 'application/x-www-form-urlencoded',
                             'Host': 'passport.yandex.ru',
                             'Origin': 'https://passport.yandex.ru',
                             'Referer': 'https://passport.yandex.ru/auth',
                             'Upgrade-Insecure-Requests': '1',
                             'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
        }

        self.headers_forecast = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                                 'Accept-Encoding': 'gzip, deflate, br',
                                 'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                                 'Connection': 'keep-alive',
                                 'Content-Length': '227',
                                 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                 'Host': 'direct.yandex.ru',
                                 'Origin': 'https://direct.yandex.ru',
                                 'Referer': 'https://direct.yandex.ru/registered/main.pl?cmd=advancedForecast',
                                 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
                                 'X-Requested-With': 'XMLHttpRequest'
        }

        self.url_ya_auth = 'https://passport.yandex.ru/passport?mode=embeddedauth' #URL авторизации яндекса
        self.url_forecast = 'https://direct.yandex.ru/registered/main.pl?cmd=advancedForecast' # URL прогноза бюджета

    def YDAuth(self):
        self.session = requests.Session()
        # Отправляем данные в POST для авторизации, в session записываются наши куки
        self.session.post(self.url_ya_auth, data=self.data_auth, headers=self.headers_auth)

        # проверяем прошла ли авторизация. парсим данные со страницы и проверяем соответствует ли заголовок
        html = bs4.BeautifulSoup(self.session.get(self.url_forecast).text, "html.parser")
        if html.find_all('title')[0].contents[0] != 'Оценка бюджета рекламной кампании':
            self.status_ = (u'<p><b>ERROR: </b>Неверный логин или пароль Яндекс Директ</p>')
            return self.status_

    def GetForecastData(self, month):
        Resp_data = {}
        # данные за месяц по каждому ключу
        Resp_data_in_month = []
        if 'мобильные' in self.is_mobile:
            self.data_forecast.update({'period_num': month, 'is_mobile': '1'})
        else:
            self.data_forecast.update({'period_num': month})

        # шелм данные для прогноза
        resp_JSON = self.session.post(self.url_forecast, data=self.data_forecast, headers=self.headers_forecast).json()
        if 'error' not in resp_JSON:
            # пока в результате появляется капча отправляем ее на расшифровку
            while 'captcha_id' in resp_JSON:
                # получаем из процедуры текст капчи
                text_capcha, self.status_ = self.AntiCapcha(resp_JSON['captcha_url'])
                if self.status_:
                    return Resp_data, self.status_
                # добавляем к данным для пост запроса прогноза идентификатор капчи и текст с картинки
                new_data_forecast = dict(self.data_forecast, captcha_code=text_capcha, captcha_id=resp_JSON['captcha_id'])
                # отправляем все на сервер
                resp_JSON = self.session.post(self.url_forecast, data=new_data_forecast, headers=self.headers_forecast).json()
                # если выдает ошибку слишком много фраз то шлем заново
                if 'error' in resp_JSON:
                    resp_JSON = self.session.post(self.url_forecast, data=self.data_forecast,
                                             headers=self.headers_forecast).json()

            # цикл по ключевым фразам
            for iter_key in self.keys:
                key = resp_JSON['phrase2key'][iter_key]
                dic = []
                # идем по ответу и тащим нужные нам поля при совпадении шифра
                for iter_json in resp_JSON['data_by_positions']:
                    if iter_json['md5'] == key:
                        dic.insert(0, iter_json['positions']['third_premium']['shows'])
                        dic.insert(1, iter_json['positions']['third_premium']['clicks'])
                        dic.insert(2, round(iter_json['positions']['third_premium']['budget'] / 1000000, 2))
                        # укладываем все в список
                        Resp_data_in_month.append(dic)
                Resp_data[month - 1] = Resp_data_in_month

            return Resp_data, self.status_
        else:
            self.status_ = u'<p><b>ERROR: </b>' + resp_JSON['error'] + '</p>'
            return Resp_data, self.status_




    def AntiCapcha(self, url_capcha):
        api = 'https://api.anti-captcha.com/'
        flag = False

        img_capcha = requests.get(url_capcha)
        encoded_string = base64.b64encode(img_capcha.content)
        json_createTask  = {
            "clientKey": self.ANTICAPTCHA_KEY,
            "task":
                {
                    "type": "ImageToTextTask",
                    "body": encoded_string.decode('utf-8'),
                    "phrase": 'false',
                    "case": 'false',
                    "numeric": 'false',
                    "math": 0,
                    "minLength": 0,
                    "maxLength": 0
                },
            "languagePool": "rn",
        }
        json_getTaskResult = {
            "clientKey": self.ANTICAPTCHA_KEY,
            "taskId": ''
        }

        json_data = json.dumps(json_createTask)
        session = requests.Session()
        # Отправляем капчу на api Антикапчи
        response = session.post(api + 'createTask', data=json_data, headers={'content_type': 'application/json'}).json()
        #если без ошибок
        if response['errorId'] == 0:
            json_getTaskResult.update({'taskId': response['taskId']})
            json_data = json.dumps(json_getTaskResult)
            #цикл пока не получим ответ о завершении обработки капчи
            while flag != True:
                response = session.post(api + 'getTaskResult', data=json_data, headers={'content_type': 'application/json'}).json()
                if response['status'] == 'ready':
                    flag = True
            return response['solution']['text'], self.status_
        else:
            self.status_ = (u'<p><b>ERROR: </b>При передаче капчи возникли ошибки</p>' \
                            u'<p>errorCode: ' + response['errorCode'] + u' errorDescription: ' + response['errorDescription'] + '</p>')
            er = 'eror'
            return er, self.status_
