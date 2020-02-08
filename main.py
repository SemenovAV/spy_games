import time
import requests

# 73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1
API = 'https://api.vk.com/method/'
TOKEN = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'
VERSION = 5.52


def ex(code):
    params = {
        'access_token': TOKEN,
        'v': VERSION,
        'code': code
    }
    flag = True
    while flag:
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
    user = response['user'][0]
    if response['groups']:
        user['groups'] = {item['id']: item for item in filter(lambda x: x.get('type', False) == 'page', response['groups'])}
        user['gids'] = {item for item in user['groups'].keys()}
    if response['friends']:
        user['friends'] = {item['id']: item for item in filter(lambda x: not x.get('deactivated', False), response['friends'])}
        user['fids'] = {item for item in user['friends'].keys()}
    print(user)
    return user


us = get_user(25)
requests_list = None
if us.get('fids', False) and us.get('gids', False):
    requests_list = list(
        ('API.users.getSubscriptions({"user_id":' + str(item) + '}).groups.items,' for item in us['fids']))
    result = set()
    count = 1
    while requests_list:
        print(count)
        temp_list = requests_list[:25]
        requests_list = requests_list[25:]
        req = ''.join(temp_list)
        r = ex(f'return [{req}];')
        for item in r:
            if item:
                for el in item:
                    result.add(el)
        count += 1
    us['gids'] -= result
    result = [{
        'name': us['groups'][item].get('name', 'noname'),
        'gid': us['groups'][item]['id'],
        'members_count': us['groups'][item].get('members_count', 'no'),
    } for item in us['groups'].keys() if item in us['gids']]
    print(result)
else:
    print('!!!')


