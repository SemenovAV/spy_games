from pprint import pprint
import json
import os
import time
import requests


def main():
    API = 'https://api.vk.com/method/'
    TOKEN = os.getenv('TOKEN') or input('Введите access_token:')
    VERSION = 5.52
    UID = 'eshmargunov'

    def send_message(label, msg):
        print(f'{time.time()} - {label}: {msg}')

    def api_execute(code):
        params = {
            'access_token': TOKEN,
            'v': VERSION,
            'code': code
        }
        make_a_request = True
        while make_a_request:
            send_message('Запрос данных', 'Отправка запроса')
            response = requests.get(
                f'{API}execute',
                params=params
            )
            make_a_request = False
            if response.json().get('error', False):
                error = response.json()['error']
                er_code = error['error_code']
                er_msg = error['error_msg']

                if er_code == 6:
                    make_a_request = True
                    send_message('Запрос данных', 'Слишком много запросов. Встаем на паузу на секунду')
                    time.sleep(1)
                elif er_code == 5:
                    raise Exception(f'Ошибка: Авторизация пользователя не удалась. Код: {er_code}')
                elif er_code == 28:
                    raise Exception(f'Ошибка: Ключ доступа приложения недействителен. Код: {er_code}')
                elif er_code == 29:
                    raise Exception(f'Ошибка: Достигнут количественный лимит на вызов метода. Код: {er_code}')
                elif er_code == 30:
                    raise Exception(f'Ошибка: Профиль является приватным. Код: {er_code}')
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
            response = api_execute(f'var uid = {uid};'
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
            send_message('Завершение работы программы.')
            return False

        user = response['user'][0]
        send_message('Обработка данных', f'Данные пользователя {UID} получены.')
        if response['groups']:
            user['groups'] = {item['id']: item for item in
                              filter(lambda x: x.get('type', False) == 'page', response['groups'])}
            user['gids'] = {item for item in user['groups'].keys()}
            send_message('Обработка данных', f'Группы: {len(user["gids"])}.')
        if response['friends']:
            user['friends'] = {item['id']: item for item in
                               filter(lambda x: not x.get('deactivated', False), response['friends'])}
            user['fids'] = {item for item in user['friends'].keys()}
            send_message('Обработка данных', f'Друзья: {len(user["fids"])}.')
        return user

    send_message('main', 'Старт')
    this_user = get_user(UID)
    requests_list = None
    if this_user and this_user.get('fids', False) and this_user.get('gids', False):
        send_message('Обработка данных', 'Подготовка дополнительных запросов.')
        requests_list = list(
            ('API.users.getSubscriptions({"user_id":' + str(item) + '}).groups.items,' for item in this_user['fids']))
        send_message('Обработка данных', f'Подготовлено {len(requests_list)} дополнительных запросов')
        result = set()
        count = 1
        while requests_list:
            temp_list = requests_list[:25]
            requests_list = requests_list[25:]
            req = ''.join(temp_list)
            r = api_execute(f'return [{req}];')
            for item in r:
                if item:
                    tmp = len(result)
                    send_message('Запрос данных', f'Получено {len(item)} group_id')
                    for el in item:
                        result.add(el)
                    send_message('Обработка данных', f'Добавлено {len(result) - tmp} group_id')
            count += 1
        send_message('Обработка данных', f'Всего добавлено {len(result)} уникальных group_id')

        this_user['gids'] -= result
        result = [{
            'name': this_user['groups'][item].get('name', 'noname'),
            'gid': this_user['groups'][item]['id'],
            'members_count': this_user['groups'][item].get('members_count', 'no'),
        } for item in this_user['groups'].keys() if item in this_user['gids']]
        send_message('Результат', f'Искомых групп: {len(result)}')
        pprint(result)
        send_message('Результат', 'Сохраненние в файл...')
        with open(f'{UID}-groups.json', mode='w', encoding='utf-8') as f:
            f.write(json.dumps(result, ensure_ascii=False))
        send_message('Результат', f'Результат успешно сохранен в файл {UID}-groups.json')

    else:
        send_message('Результат', f'Данные для анализа отсутствуют')
        return


if __name__ == '__main__':
    main()
