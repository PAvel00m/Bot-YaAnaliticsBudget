# -*- codecs: utf-8 -*-
import json
import os

import YaForecast
import ReadWriteSheet

#функция для получения id регионов по названию и получению списка этих id
#ВАЖНО! названия регионов все с маленькой буквы
def GetRegion_ID(regions):
    regions_id = []
    warning = []
    with open(os.path.dirname(os.path.abspath(__file__)) + '/regions.json', encoding='utf8') as json_data:
        region_dict = json.load(json_data)
    json_data.close()

    for iter_r in regions:
      if iter_r in region_dict:
        regions_id.append(region_dict[iter_r])
      else:
        warning.append(u'<p><b>WARNING:</b> Введенного региона <b>' + iter_r + '</b> нет в списке</p>')

    return regions_id, warning

#чтение данных из файла конфигураций
def search_and_read_file_config():
    if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + '/secrets/config.ini') == False:
      er = u'<p><b>ERROR: </b>Файл config.ini не найден</p>' \
         u'<p>Создайте файл и заполните его построчно</p>' \
         u'<ul>' \
           u'<li>1 - Логин Директа</li>' \
           u'<li>2 - Пароль Директа</li>' \
           u'<li>3 - Ключ Антикапчи</li>' \
         u'</ul>'
      dataConf = ''
      return dataConf, er
    else:
      with open(os.path.dirname(os.path.abspath(__file__)) + '/secrets/config.ini') as in_f:    #чтение из файла
        dataConf = in_f.read().split('\n')     # dataConf[1] - login
      in_f.closed                       # dataConf[2] - password
                                   # dataConf[3] - Антикапча key
                                   
      for item in dataConf:
        if item == '' or len(dataConf) < 3:
           er = u'<p><b>ERROR: </b>В файле config.ini присутствуют пустые строки</p>' \
              u'<p>Удалите или заполните пустые строки и повторите попытку</p>' \
              u'<ul>' \
                u'<li>1 - Логин Директа</li>' \
                u'<li>2 - Пароль Директа</li>' \
                u'<li>3 - Ключ Антикапчи</li>' \
              u'</ul>'
           break
        else:
           er = ''
      return dataConf, er



def main(GoogleTabID):
    if GoogleTabID:
      dataConf, status_ = search_and_read_file_config()
      if status_ == '':
        # создаем объект класс
        MySheet = ReadWriteSheet.GoogleSheet(GoogleTabID.decode())
        #читаем данные из гугл таблицы
        keys, regions, is_mobile, status_ = MySheet.ReadSheet()
        #если после выполнения вернулась ошибка
        if status_:
           return status_
        #получаем список id регионов
        regions_id, warning = GetRegion_ID(regions)
        #создаем объект класс
        MyForecast = YaForecast.Forecast(keys, regions_id, is_mobile, dataConf[0], dataConf[1], dataConf[2])
        #авторизуемся в директе
        status_ = MyForecast.YDAuth()
        if status_:
            return status_
        #цикл для прогноза на каждый месяц
        for i in range(1, 13):
           DataForecast, status_ = MyForecast.GetForecastData(i)
           if status_:
             return status_
           else:
             MySheet.WriteDataInSheet(DataForecast, i-1)
        status_ = u'<p>Программа отработала без критических ошибок</p>'
        for el in warning: status_ += el
        return status_
      else:
        return status_
    else:
      status_ = u'<p><b>ERROR: </b>Скрипт получил пустой параметер t_id (идентификатор таблицы)</p>'
      return status_
