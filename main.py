from pprint import pprint
import json
import time
from progressbar import ProgressBar
import requests

'''
Скрипт выводит список групп в ВК в которых состоит пользователь, но не состоит никто из его друзей
Для работы скрипта нужно вставить access_token  API ВК в переменную TOKEN 
и id нужного пользователя в переменную USER_ID
'''
TOKEN = ''
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
        self.users_subscription = set()
        self.result = []
        self.go()

    def _send_message(self, message):
        '''
        Метод формирует и печатает сообщение в консоль.

        '''
        print(f'{time.time()} - {self.program_state}: {message}')

    def _set_program_state(self, state):
        '''
        Метод устанавливает текст сообщения для отображения
        текущего состояния работы скрипта.
        :param state: str - текст характеризующий состояние

        '''
        self.program_state = state

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
        while self.request_state == 1:
            self.request_state = 0
            response = requests.get(
                f'{self.api}execute',
                params=params
            )
            if response.json().get('error', False):
                error = response.json()['error']
                er_code = error['error_code']
                er_msg = error['error_msg']
                if er_code == 6 or er_code == 1:
                    self.request_state = 1
                    self._send_message('Слишком много запросов. Встаем на паузу на секунду')
                    time.sleep(1)
                else:
                    self._set_program_state(f'Ошибка {er_code}')
                    self._send_message(er_msg)
            else:
                data = response.json().get('response', False)
                return data

    def _filter_groups(self, response):
        '''
        Метод отфильтровывает из ответа сервера подписки пользователя тип которых - группа.

        '''
        self._set_program_state('Получение данных о группах пользователя')
        self.user['groups'] = {
            item['id']: item for item in filter(
                lambda x: x.get('type', False) == 'page' or 'group' or 'event',
                response['groups'])
        }
        self.user['group_ids'] = {item for item in self.user['groups'].keys()}
        self._send_message(f'Группы: {len(self.user["group_ids"])}.')

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
        self._send_message(f'Друзья: {len(self.user["friend_ids"])}.')

    def _get_user(self):
        '''
        Метод отправляет запрос к API VK. Возвращает словарь с характеристиками пользователя.
        '''
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
            self._send_message('Завершение работы программы.')

            return False
        if response['user']:
            self.user = response['user'][0]
            self._set_program_state('Обработка данных')
            self._send_message(f'Данные пользователя {self.user_id} получены.')

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
        self._send_message('Подготовка дополнительных запросов.')

        requests_list = list(
            ('API.users.getSubscriptions({"user_id":' + str(item) + '}).groups.items,' for item in
             user_ids)
        )
        self._send_message(f'Подготовлено {len(requests_list)} дополнительных запросов')

        one_percent = len(requests_list) / 100
        progressbar = ProgressBar(55)

        while requests_list:
            temp_list = requests_list[:25]
            requests_list = requests_list[25:]
            requests = ''.join(temp_list)
            percent = len(temp_list) / one_percent

            request = self._api_execute(f'return [{requests}];')
            for item in request:
                if item:
                    length = len(self.users_subscription)
                    self._set_program_state('Запрос данных')
                    self._send_message(f'Получено {len(item)} group_ids')

                    for el in item:
                        self.users_subscription.add(el)
                    self._set_program_state('Обработка данных')
                    self._send_message(f'Добавлено {len(self.users_subscription) - length} group_ids')

            progressbar.set_progress(percent)
        self._send_message(f'Всего добавлено {len(self.users_subscription)} уникальных group_id')

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
        self._send_message('Сохраненние в файл...')

        with open(filename, mode='w', encoding='utf-8') as f:
            f.write(json.dumps(self.result, ensure_ascii=False))
            self._send_message(f'Результат успешно сохранен в файл {filename}')

    def go(self):
        '''
        Метод выполняет запрос информации о пользователе. Разбор полученной информации.

        '''
        self._set_program_state('Начало работы')
        self._get_user()
        if self.user and self.user.get('friend_ids', False) and self.user.get('group_ids', False):
            self._get_users_subscription(self.user['friend_ids'])
            self.get_result()
            pprint(self.result)
            self.save_file(f'{self.user_id}-groups.json')
        else:
            self._set_program_state('Результат')
            self._send_message(f'Данные для анализа отсутствуют')
            return


if __name__ == '__main__':
    user = SpyGames(TOKEN, USER_ID)

