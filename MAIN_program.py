# -*- codecs: utf-8 -*-
import json
import os

import YaForecast
import ReadWriteSheet


# функция для получения id регионов по названию и получению списка этих id
# ВАЖНО! названия регионов все с маленькой буквы
def GetRegion_ID(regions, warning_):
    regions_id = []
    with open(os.path.dirname(os.path.abspath(__file__)) + '/regions.json', encoding='utf8') as json_data:
        region_dict = json.load(json_data)
    json_data.close()

    for iter_r in regions:
        if iter_r in region_dict:
            regions_id.append(region_dict[iter_r])
        else:
            warning_.append(u'<p><b>WARNING:</b> Введенного региона <b>' + iter_r + '</b> нет в списке</p>')

    return regions_id


# чтение данных из файла конфигураций
def search_and_read_file_config(error_):
    if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + '/secrets/config.ini') == False:
        error_.append(u'<p><b>ERROR: </b>Файл config.ini не найден</p>' \
                      u'<p>Создайте файл и заполните его построчно</p>' \
                      u'<ul>' \
                          u'<li>1 - Логин Директа</li>' \
                          u'<li>2 - Пароль Директа</li>' \
                          u'<li>3 - Ключ Антикапчи</li>' \
                      u'</ul>')
        dataConf = ''
        return dataConf
    else:
        with open(os.path.dirname(os.path.abspath(__file__)) + '/secrets/config.ini') as in_f:  # чтение из файла
            dataConf = in_f.read().split('\n')  # dataConf[1] - login
        in_f.closed                             # dataConf[2] - password
                                                # dataConf[3] - Антикапча key

        for item in dataConf:
            if item == '' or len(dataConf) < 3:
                error_.append(u'<p><b>ERROR: </b>В файле config.ini присутствуют пустые строки</p>' \
                              u'<p>Удалите или заполните пустые строки и повторите попытку</p>' \
                              u'<ul>' \
                                  u'<li>1 - Логин Директа</li>' \
                                  u'<li>2 - Пароль Директа</li>' \
                                  u'<li>3 - Ключ Антикапчи</li>' \
                              u'</ul>')
                break
        return dataConf


def main(GoogleTabID):
    error_ = []
    warning_ = []
    if GoogleTabID:
        dataConf = search_and_read_file_config(error_)
        if len(error_) == 0:
            # создаем объект класс
            MySheet = ReadWriteSheet.GoogleSheet(GoogleTabID.decode())
            # читаем данные из гугл таблицы
            DataForForecast = MySheet.ReadSheet(error_)
            # если после выполнения вернулась ошибка
            if len(error_) == 0:
                # получаем список id регионов
                regions_id, = GetRegion_ID(DataForForecast[1], warning_)
                # создаем объект класс
                MyForecast = YaForecast.Forecast(DataForForecast[0], regions_id, dataConf[0], dataConf[1], dataConf[2])
                # авторизуемся в директе
                MyForecast.YDAuth(error_)
                if len(error_) == 0:
                    # цикл для прогноза на каждый месяц
                    for i in range(1, 14):
                        DataForecast = MyForecast.GetForecastData(i, warning_, error_)
                        if len(error_) == 0:
                            MySheet.WriteDataInSheet(DataForecast, i - 1)
                        else:
                            error_ = error_ + warning_
                            return error_
                    error_.append(u'<p>Программа отработала без критических ошибок</p>')
                    error_ = error_ + warning_
                    return error_
                else:
                    error_ = error_ + warning_
                    return error_
            else:
                return error_
        else:
            return error_
    else:
        error_.append(u'<p><b>ERROR: </b>Скрипт получил пустой параметер t_id (идентификатор таблицы)</p>')
        return error_
