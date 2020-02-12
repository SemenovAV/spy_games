from pprint import pprint
import json
import os
import time
import sys
import requests


class SpyGames:

    def __init__(self, access_token, user_id):
        self.access_token = access_token
        self.user_id = user_id
        self.api = 'https://api.vk.com/method/'
        self.api_version = 5.52
        self.user = None
        self.message = ''
        self.program_state = None
        self.request_state = 0
        self.friends_groups = set()
        self.result = []

    def _send_message(self):
        print(f'{time.time()} - {self.program_state}: {self.message}')

    def _set_program_state(self, state):
        self.program_state = state

    def _set_message(self, message):
        self.message = message

    def _error_helper(self, error_object):
        er_code = error_object['error_code']
        er_msg = error_object['error_msg']
        if er_code == 6:
            self.request_state = 1
            self._set_message('Слишком много запросов. Встаем на паузу на секунду')
            self._send_message()
            time.sleep(1)
        else:
            self._set_program_state(f'Ошибка {er_code}')
            self._set_message(er_msg)
            self._send_message()

    def _api_execute(self, code):
        params = {
            'access_token': self.access_token,
            'v': self.api_version,
            'code': code
        }
        self._set_program_state('Запрос данных')
        self.request_state = 1
        while self.request_state == 1:
            self._set_message('Отправка запроса')
            self._send_message()
            self.request_state = 0
            response = requests.get(
                f'{self.api}execute',
                params=params
            )
            if response.json().get('error', False):
                self._error_helper(response.json()['error'])
            else:
                data = response.json().get('response', False)
                return data

    def _get_groups(self, response):
        self._set_program_state('Получение данных о группах пользователя')
        self.user['groups'] = {
            item['id']: item for item in filter(
                lambda x: x.get('type', False) == 'page',
                response['groups'])
        }
        self.user['group_ids'] = {item for item in self.user['groups'].keys()}
        self._set_message(f'Группы: {len(self.user["group_ids"])}.')
        self._send_message()

    def _get_friends(self, response):
        self._set_program_state('Получение данных о друзьях пользователя')
        self.user['friends'] = {
            item['id']: item for item in filter(
                lambda x: not x.get('deactivated', False),
                response['friends']
            )
        }
        self.user['friend_ids'] = {item for item in self.user['friends'].keys()}
        self._set_message(f'Друзья: {len(self.user["friend_ids"])}.')
        self._send_message()

    def _get_user(self):
        user_id = f'"{self.user_id}"' if not isinstance(self.user_id, int) else self.user_id
        try:
            response = self._api_execute(f'var uid = {user_id};'
                                        ' var user = API.users.get({"user_ids": uid});'
                                        'var id = user[0].id;'
                                        'return {'
                                        '"user": user,'
                                        '"groups": API.users.getSubscriptions({'
                                        '"user_id": id ,'
                                        '"extended": 1,'
                                        '"fields": "members_count"'
                                        '}).items,'
                                        '"friends": API.friends.get({"user_id": id , "fields":"last_seen"}).items,'
                                        '};')

        except Exception as er:
            self._set_program_state('Ошибка')
            self._set_message('Завершение работы программы.')
            self._send_message()
            return False
        if response['user']:
            self.user = response['user'][0]
            self._set_program_state('Обработка данных')
            self._set_message(f'Данные пользователя {self.user_id} получены.')
            self._send_message()
            if response['groups']:
                self._get_groups(response)
            if response['friends']:
                self._get_friends(response)
        return True
    def go(self):
        self._set_program_state('Начало работы')
        self._get_user()
        if self.user and self.user.get('friend_ids', False) and self.user.get('group_ids', False):
            self._set_program_state('Обработка данных')
            self._set_message('Подготовка дополнительных запросов.')
            self._send_message()
            requests_list = list(
                ('API.users.getSubscriptions({"user_id":' + str(item) + '}).groups.items,' for item in self.user['friend_ids'])
            )
            self._set_message(f'Подготовлено {len(requests_list)} дополнительных запросов')
            self._send_message()
            while requests_list:
                temp_list = requests_list[:25]
                requests_list = requests_list[25:]
                requests = ''.join(temp_list)
                request = self._api_execute(f'return [{requests}];')
                for item in request:
                    if item:
                        length = len(self.friends_groups)
                        self._set_program_state('Запрос данных')
                        self._set_message(f'Получено {len(item)} group_ids')
                        self._send_message()
                        for el in item:
                            self.friends_groups.add(el)
                        self._set_program_state('Обработка данных')
                        self._set_message(f'Добавлено {len(self.friends_groups) - length} group_ids')
                        self._send_message()
            self._set_message(f'Всего добавлено {len(self.result)} уникальных group_id')
            self._send_message()
            self.user['group_ids'] -= self.friends_groups
            self.result = [{
                'name': self.user['groups'][item].get('name', 'noname'),
                'gid': self.user['groups'][item]['id'],
                'members_count': self.user['groups'][item].get('members_count', 'no'),
            } for item in self.user['groups'].keys() if item in self.user['group_ids']]
            self._set_program_state('Результат')
            self._set_message(f'Искомых групп: {len(self.result)}')
            self._send_message()
            pprint(self.result)
            self._set_message('Сохраненние в файл...')
            self._send_message()
            with open(f'{self.user_id}-groups.json', mode='w', encoding='utf-8') as f:
                f.write(json.dumps(self.result, ensure_ascii=False))
                self._set_message(f'Результат успешно сохранен в файл {self.user_id}-groups.json')
                self._send_message()
        else:
            send_message('Результат', f'Данные для анализа отсутствуют')
            return



user = SpyGames(os.getenv('TOKEN'),'eshmargunov')
user2 = SpyGames(os.getenv('TOKEN'),7)
user.go()
user2.go()

