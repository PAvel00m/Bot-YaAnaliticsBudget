# -*- codecs: utf-8 -*-
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import sys
import os
import oauth2client
import googleapiclient


class GoogleSheet():
    def __init__(self, SPREADSHEET_ID):
        self.SPREADSHEET_ID = SPREADSHEET_ID
        self.keys = []
        self.regions = []
        self.is_mobile = []
        self.status_ = ''
        self.service = None
        #максимальное количество ключей
        self.Max_keys = 30
        #строка с которой начинается вывод результата
        self.ROW_data_out = 34
        # диапазон чтения данных (столбец с ключами, столбец с регионами и столбец с платформой)
        self.RANGE_data_in = 'Лист1!A2:C' + str(self.Max_keys + 1)

    def ReadSheet(self):
        clear_cells = {
            "requests": [{
                "updateCells":
                    {
                        "range":
                            {
                                "sheetId": 0,
                                "startColumnIndex": 0,
                                "endColumnIndex": 37,
                                "startRowIndex": self.ROW_data_out - 1,
                                "endRowIndex": self.ROW_data_out + self.Max_keys
                            },
                        "fields": "userEnteredValue"
                    }
            }]
        }
        SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
        store = file.Storage(os.path.dirname(os.path.abspath(__file__)) + '/secrets/credentials.json')
        creds = store.get()
        #авторизация на гугл таблицах черз token
        if not creds or creds.invalid:
            try:
                flow = client.flow_from_clientsecrets(os.path.dirname(os.path.abspath(__file__)) + '/secrets/google_client_secret.json', SCOPES)
            except oauth2client.clientsecrets.InvalidClientSecretsError:
                self.status_ = (u'<p><b>ERROR: </b>Файл google_client_secret.json не найден.</p>' \
                                u'<p><b>ERROR: </b>Авторизация в Google Sheets не выполнена</p>')
                return self.keys, self.regions, self.is_mobile, self.status_

            creds = tools.run_flow(flow, store)
        self.service = build('sheets', 'v4', http=creds.authorize(Http()))

        #читаем входящие данные из диапазона RANGE_NAME
        try:
            result = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID, range=self.RANGE_data_in).execute()
        except googleapiclient.errors.HttpError:
            self.status_ = (u'<p><b>ERROR: </b>Таблица с идентификатором ' + self.SPREADSHEET_ID + ' не найдена.</p>')
            return self.keys, self.regions, self.is_mobile, self.status_

        #очищаем диапазон вывода
        request = self.service.spreadsheets().batchUpdate(spreadsheetId=self.SPREADSHEET_ID, body=clear_cells)
        request.execute()

        values = result.get('values', [])
        if not values:
            self.status_ = (u'<p><b>ERROR: </b>Входящие данные в диапазоне ' + self.RANGE_data_in + ' не найдены</p>')
            return self.keys, self.regions, self.is_mobile, self.status_
        else:
            #отделяем ключевые фразы от регионов
            for row in values:
                if len(row) == 0:
                    continue
                else:
                    try:
                        self.is_mobile.append(row[2].strip().lower())
                        self.regions.append(row[1].strip().lower())
                        self.keys.append(row[0].strip().lower())
                    except IndexError:
                        try:
                            self.regions.append(row[1].strip().lower())
                            self.keys.append(row[0].strip().lower())
                        except IndexError:
                            self.keys.append(row[0].strip().lower())

        if len(self.is_mobile) == 0 or len(self.regions) == 0 or len(self.keys) == 0:
            self.status_ = (u'<p><b>ERROR: </b>Вы не заполнили одну или несколько колонок с входными данными</p>' \
                            u'<ul>' \
                                u'<li>А - колонка с ключами</li>' \
                                u'<li>В - колонка с регионами</li>' \
                                u'<li>С - колонка с площадками (мобильные или все)</li>' \
                            u'</ul')
            return self.keys, self.regions, self.is_mobile, self.status_


        return self.keys, self.regions, self.is_mobile, self.status_



    def WriteDataInSheet(self, data, month):
            i = str(self.ROW_data_out + 1)
            j = str(len(self.keys) + self.ROW_data_out)

            #отвечает за перечисление суммы по столбцам
            sum_d = ['Сумма', '=SUM(B' + i + ':B' + j + ')', '=SUM(C' + i + ':C' + j + ')', '=SUM(D' + i + ':D' + j + ')',
                       '=SUM(E' + i + ':E' + j + ')', '=SUM(F' + i + ':F' + j + ')', '=SUM(G' + i + ':G' + j + ')',
                       '=SUM(H' + i + ':H' + j + ')', '=SUM(I' + i + ':I' + j + ')', '=SUM(J' + i + ':J' + j + ')',
                       '=SUM(K' + i + ':K' + j + ')', '=SUM(L' + i + ':L' + j + ')', '=SUM(M' + i + ':M' + j + ')',
                       '=SUM(N' + i + ':N' + j + ')', '=SUM(O' + i + ':O' + j + ')', '=SUM(P' + i + ':P' + j + ')',
                       '=SUM(Q' + i + ':Q' + j + ')', '=SUM(R' + i + ':R' + j + ')', '=SUM(S' + i + ':S' + j + ')',
                       '=SUM(T' + i + ':T' + j + ')', '=SUM(U' + i + ':U' + j + ')', '=SUM(V' + i + ':V' + j + ')',
                       '=SUM(W' + i + ':W' + j + ')', '=SUM(X' + i + ':X' + j + ')', '=SUM(Y' + i + ':Y' + j + ')',
                       '=SUM(Z' + i + ':Z' + j + ')', '=SUM(AA' + i + ':AA' + j + ')', '=SUM(AB' + i + ':AB' + j + ')',
                       '=SUM(AC' + i + ':AC' + j + ')', '=SUM(AD' + i + ':AD' + j + ')', '=SUM(AE' + i + ':AE' + j + ')',
                       '=SUM(AF' + i + ':AF' + j + ')', '=SUM(AG' + i + ':AG' + j + ')', '=SUM(AH' + i + ':AH' + j + ')',
                       '=SUM(AI' + i + ':AI' + j + ')', '=SUM(AJ' + i + ':AJ' + j + ')', '=SUM(AK' + i + ':AK' + j + ')']

            #отвечает за диапазон вывода данных по ключам за месяц
            range_t = ['B' + i + ':D' + j, 'E' + i + ':G' + j, 'H' + i + ':J' + j, 'K' + i + ':M' + j,
                       'N' + i + ':P' + j, 'Q' + i + ':S' + j, 'T' + i + ':V' + j, 'W' + i + ':Y' + j,
                       'Z' + i + ':AB' + j, 'AC' + i + ':AE' + j, 'AF' + i + ':AH' + j, 'AI' + i + ':AK' + j]

            new_data_json = {
                "valueInputOption": 'RAW',
                "data": [
                    {
                        "range": 'Лист1!A' + i + ':B' + j,
                        "majorDimension": 'COLUMNS',
                        "values": [self.keys]
                    }

                ],
                "includeValuesInResponse": 'True',
                "responseValueRenderOption": 'FORMATTED_VALUE',
                "responseDateTimeRenderOption": 'SERIAL_NUMBER'
            }

            if month == 0:
                #записываем в таблицу ключи
                request = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID, body=new_data_json)
                request.execute()

            #выводим построчно данные по каждому ключу на каждый месяц
            new_data_json['data'][0].update({'range': 'Лист1!' + range_t[month]})
            new_data_json['data'][0].update({'majorDimension': 'ROWS'})
            new_data_json['data'][0].update({'values': data[month]})
            request = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID, body=new_data_json)
            request.execute()

            if month == 11:
                #делаем сумму по каждому столбцу
                new_data_json.update({'valueInputOption': 'USER_ENTERED'})
                new_data_json['data'][0].update({'range': 'Лист1!A' + str(self.ROW_data_out)+':AK' + str(self.ROW_data_out)})
                new_data_json['data'][0].update({'values': [sum_d]})
                request = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID, body=new_data_json)
                request.execute()