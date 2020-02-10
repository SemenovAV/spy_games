from sys import argv
from pprint import pprint
import json
import os
import time
import requests


def main():
    API = 'https://api.vk.com/method/'
    TOKEN = os.getenv('TOKEN')
    VERSION = 5.52
    UID = ''

    if len(argv) > 1:
        UID = argv[1]
    if len(argv) > 2:
        TOKEN = argv[2]
    if not TOKEN:
        TOKEN = input('Введите access_token:')
    if not UID:
        UID = 'eshmargunov'

    def set_msg(label, msg):
        print(f'{time.time()} - {label}: {msg}')

    def cls():
        os.system('cls' if os.name == 'nt' else 'clear')

    def ex(code):
        params = {
            'access_token': TOKEN,
            'v': VERSION,
            'code': code
        }
        flag = True
        while flag:
            set_msg('Запрос данных', 'Отправка запроса')
            flag = False
            response = requests.get(
                f'{API}execute',
                params=params
            )
            if response.json().get('error', False):
                error = response.json()['error']
                er_code = error['error_code']
                er_msg = error['error_msg']
                if er_code == 6:
                    flag = True
                    set_msg('Запрос данных', 'Слишком много запросов. Встаем на паузу на секунду')
                    time.sleep(1)
                elif er_code == 5:
                    raise Exception('Ошибка: Авторизация пользователя не удалась. Код: {er_code}')
                elif er_code == 28:
                    raise Exception('Ошибка: Ключ доступа приложения недействителен. Код: {er_code}')
                elif er_code == 29:
                    raise Exception('Ошибка: Достигнут количественный лимит на вызов метода. Код: {er_code}')
                elif er_code == 30:
                    raise Exception('Ошибка: Профиль является приватным. Код: {er_code}')
                else:
                    raise Exception(f'Ошибка: {er_msg} Код: {er_code}.')

            else:
                data = response.json().get('response', False)
                return data

    def get_user(uid):
        response = None
        if not isinstance(uid, int):
            uid = f'"{uid}"'
        try:
            response = ex(f'var uid = {uid};'
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
            print(er)
            return False

        user = response['user'][0]
        set_msg('Обработка данных', f'Данные пользователя {UID} получены.')
        if response['groups']:
            user['groups'] = {item['id']: item for item in
                              filter(lambda x: x.get('type', False) == 'page', response['groups'])}
            user['gids'] = {item for item in user['groups'].keys()}
            set_msg('Обработка данных', f'Группы: {len(user["gids"])}.')
        if response['friends']:
            user['friends'] = {item['id']: item for item in
                               filter(lambda x: not x.get('deactivated', False), response['friends'])}
            user['fids'] = {item for item in user['friends'].keys()}
            set_msg('Обработка данных', f'Друзья: {len(user["fids"])}.')
        return user

    cls()
    set_msg('main', 'Старт')
    us = get_user(UID)
    requests_list = None
    if us.get('fids', False) and us.get('gids', False):
        set_msg('Обработка данных', 'Подготовка дополнительных запросов.')
        requests_list = list(
            ('API.users.getSubscriptions({"user_id":' + str(item) + '}).groups.items,' for item in us['fids']))
        set_msg('Обработка данных', f'Подготовлено {len(requests_list)} дополнительных запросов')
        result = set()
        count = 1
        while requests_list:
            temp_list = requests_list[:25]
            requests_list = requests_list[25:]
            req = ''.join(temp_list)
            r = ex(f'return [{req}];')
            for item in r:
                if item:
                    tmp = len(result)
                    set_msg('Запрос данных', f'Получено {len(item)} group_id')
                    for el in item:
                        result.add(el)
                    set_msg('Обработка данных', f'Добавлено {len(result) - tmp} group_id')
            count += 1
        set_msg('Обработка данных', f'Всего добавлено {len(result)} уникальных group_id')

        us['gids'] -= result
        result = [{
            'name': us['groups'][item].get('name', 'noname'),
            'gid': us['groups'][item]['id'],
            'members_count': us['groups'][item].get('members_count', 'no'),
        } for item in us['groups'].keys() if item in us['gids']]
        set_msg('Результат', f'Искомых групп: {len(result)}')
        pprint(result)
        set_msg('Результат', 'Сохраненние в файл...')
        with open(f'{UID}-groups.json', mode='w', encoding='utf-8') as f:
            f.write(json.dumps(result, ensure_ascii=False))
        set_msg('Результат', f'Результат успешно сохранен в файл {UID}-groups.json')

    else:
        set_msg('Результат', f'Данные для анализа отсутствуют')
        return


if __name__ == '__main__':
    main()
