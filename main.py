import json
import time
from pprint import pprint

import requests

from tools.mini_progress import mini_progress
from tools.progressbar import ProgressBar
from tools.visual_state import visual_state

'''
Скрипт выводит список групп в ВК в которых состоит пользователь, но не состоит никто из его друзей
Для работы скрипта нужно вставить access_token  API ВК в переменную TOKEN 
и id нужного пользователя в переменную USER_ID
'''
TOKEN = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'
USER_ID = 'eshmargunov'


class SpyGames:

    def __init__(self, access_token, user_id):
        ''' Принимает при инициализации два параметра:
        :param access_token: Токен для доступа к api VK
        :param user_id: Индификатор пользователя или короткое имя страницы VK

        '''
        self.access_token = access_token
        self.user_id = user_id
        self.api = 'https://api.vk.com/method/'
        self.api_version = 5.52
        self.user = None
        self.program_state = None
        self.request_state = 0
        self.timeout = 0
        self.users_subscription = set()
        self.result = []
        self.go()

    def _send_message(self, message, state=None):
        '''
        Метод формирует и печатает сообщение в консоль.

        '''
        generated_message = f'{time.time()} - {self.program_state}: {message}'
        if state != None:
            mini_progress(generated_message)
            visual_state(generated_message, state)
        else:
            print(generated_message)

    def _set_program_state(self, state):
        '''
        Метод устанавливает текст сообщения для отображения
        текущего состояния работы скрипта.
        :param state: str - текст характеризующий состояние

        '''
        self.program_state = state

    def _set_timeout(self, sec):
        ''' Метод запускает анимацию ожидания и ставит
        скрипт на паузу равную продолжительности анимации.
        Продолжительность в секундах передается единственным аргументом

        '''
        self.timeout += 1
        self._set_program_state('Подключение')
        mini_progress('Ожидание', sec)

    def _api_execute(self, code):
        '''
        Метод отправляет запрос к API VK c с помощью метода API - execute
        :param code: str - код запроса
        :return: возвращает ответ сервера
        '''
        params = {
            'access_token': self.access_token,
            'v': self.api_version,
            'code': code
        }
        self.request_state = 1
        self.timeout = 0
        while self.request_state == 1:
            if self.timeout == 3:
                raise TimeoutError('Неработает')
            self.request_state = 0
            try:
                response = requests.get(
                    f'{self.api}execute',
                    params=params
                )
            except requests.exceptions.Timeout:
                self.request_state = 1
                self._set_timeout(1)

                continue
            except requests.exceptions.ConnectionError:
                self._send_message('Ошибка сети', state=False)
                raise ConnectionError('Неработает')
            if response.json().get('error', False):
                error = response.json()['error']
                er_code = error['error_code']
                er_msg = error['error_msg']
                if er_code == 6 or er_code == 1:
                    self.request_state = 1
                    self._send_message('Слишком много запросов.', state=False)
                    self._send_message('Встаем на паузу на секунду', state=True)
                    self._set_timeout(1)
                else:
                    self._set_program_state(f'Ошибка {er_code}')
                    self._send_message(er_msg, state=False)
                    raise Exception('Проверте access_token')
            else:
                data = response.json().get('response', False)
                return data

    def _filter_groups(self, response):
        '''
        Метод отфильтровывает из ответа сервера активные группы.

        '''
        self._set_program_state('Получение данных о группах пользователя')
        self.user['groups'] = {
            item['id']: item for item in filter(
                lambda x: not x.get('deactivated', False),
                response['groups'])
        }
        self.user['group_ids'] = {item for item in self.user['groups'].keys()}
        self._send_message(f'Группы: {len(self.user["group_ids"])}.', state=True)

    def _filter_friends(self, response):
        '''
        Метод отфильтровывает из ответа сервера активных пользователей

        '''
        self._set_program_state('Получение данных о друзьях пользователя')
        self.user['friends'] = {
            item['id']: item for item in filter(
                lambda x: not x.get('deactivated', False),
                response['friends']
            )
        }
        self.user['friend_ids'] = {item for item in self.user['friends'].keys()}
        self._send_message(f'Друзья: {len(response["friends"])}', state=True)
        self._set_program_state('Обработка данных')
        self._send_message(f'Активных аккаунтов: {len(self.user["friend_ids"])}', state=True)
        self._send_message(
            f'Неактивных аккаунтов(страница удалена или забанена и учтена не будет): {len(response["friends"]) - len(self.user["friend_ids"])}',
            state=True)

    def _get_user(self):
        '''
        Метод отправляет запрос к API VK. Возвращает словарь с характеристиками пользователя.
        '''
        user_id = f'"{self.user_id}"' if not isinstance(self.user_id, int) else self.user_id
        self._set_program_state('Получение данных')
        try:
            response = self._api_execute(f'var uid = {user_id};'
                                         ' var user = API.users.get({"user_ids": uid});'
                                         'var id = user[0].id;'
                                         'return {'
                                         '"user": user,'
                                         '"groups": API.groups.get({'
                                         '"user_id": id ,'
                                         '"extended": 1,'
                                         '"fields": "members_count"'
                                         '}).items,'
                                         '"friends": API.friends.get({"user_id": id , "fields":"last_seen"}).items,'
                                         '};')
            self._send_message('Отправка запроса', state=True)

        except Exception as er:
            self._send_message('Отправка запроса', state=False)
            self._set_program_state('Ошибка')
            self._send_message(f'{er} \nЗавершение работы программы.')

            return False
        if response['user']:
            self.user = response['user'][0]
            self._set_program_state('Обработка данных')

            self._send_message(f'Данные пользователя {self.user["first_name"]} {self.user["last_name"]} получены.',
                               state=True)

            if response['groups']:
                self._filter_groups(response)
            if response['friends']:
                self._filter_friends(response)
        return True

    def _get_users_subscription(self, user_ids):
        '''
        Метод получает подписки пользователей и обЪединяет их в одно множество
         уникальных id групп(self.user_subscription). Принимает один параметр список id пользователей.

        '''
        self._set_program_state('Обработка данных')

        requests_list = list(
            ('API.groups.get({"user_id":' + str(item) + '}).items,' for item in
             user_ids)
        )
        self._send_message('Подготовка дополнительных запросов.', state=requests_list)
        if len(requests_list) > 0:
            self._send_message(f'Подготовлено {len(requests_list)} дополнительных запросов')
            one_percent = len(requests_list) / 100
            progressbar = ProgressBar(60)

            while requests_list:
                temp_list = requests_list[:25]
                requests_list = requests_list[25:]
                requests = ''.join(temp_list)
                percent = len(temp_list) / one_percent

                request = self._api_execute(f'return [{requests}];')
                for item in request:
                    if item:
                        for el in item:
                            self.users_subscription.add(el)
                progressbar.set_progress(percent)
            self._send_message(f'Добавлено {len(self.users_subscription)} уникальных group_id')

    def get_result(self):
        '''

        Метод выполняет фильтрацию групп которые есть у пользователя но нет у его друзей.
        '''
        self.user['group_ids'] -= self.users_subscription
        self.result = [{
            'name': self.user['groups'][item].get('name', 'noname'),
            'gid': self.user['groups'][item]['id'],
            'members_count': self.user['groups'][item].get('members_count', 'no'),
        } for item in self.user['groups'].keys() if item in self.user['group_ids']]
        self._set_program_state('Результат')
        self._send_message(f'Искомых групп: {len(self.result)}')

    def save_file(self, filename):
        '''
        Метод сохраняет результат работы скрипта в файл

        '''

        try:
            with open(filename, mode='w', encoding='utf-8') as f:
                f.write(json.dumps(self.result, ensure_ascii=False))
                self._send_message('Сохраненние в файл', state=True)
                self._send_message(f'Результат успешно сохранен в файл {filename}')

        except Exception as e:
            self._send_message('Сохраненние в файл', state=False)
            self._send_message(f'Ошибка: {e}', state=False)

    def _check_token(self):
        ''' Метод проверяет что переменная TOKEN не пустая.

        '''
        self._set_program_state('Проверка конфигурации')
        if TOKEN:
            self._send_message('access_token', state=True)
            return True
        self._send_message('access_token не найден. Проверьте access_token и попробуйте снова.', state=False)

    def _check_uid(self):
        ''' Метод проверяет что переменная USER_ID не пустая.

        '''
        if USER_ID:
            self._send_message('user_id', state=True)
            return True
        self._send_message(f'user_id не найден. Проверьте user_id и попробуйте снова.', state=False)

    def go(self):
        '''
        Метод выполняет запрос информации о пользователе. Разбор полученной информации.

        '''
        self._set_program_state('')
        self._send_message('Начало работы')
        if not self._check_token() or not self._check_uid():
            return
        if self._get_user():
            if self.user and self.user.get('friend_ids', False) and self.user.get('group_ids', False):
                self._get_users_subscription(self.user['friend_ids'])
                self.get_result()
                pprint(self.result)
                self.save_file(f'{self.user_id}-groups.json')
            else:
                self._set_program_state('Результат')
                self._send_message(f'Данные для анализа отсутствуют', state=False)
                return


if __name__ == '__main__':
    user = SpyGames(TOKEN, USER_ID)
