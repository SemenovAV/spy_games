from urllib.parse import urlencode

config = {
    'APP_ID': '7302199',
    'AUTH_URL': 'https://oauth.vk.com/authorize',
    'v': 5.52,
}



def get_token():
    params = {
        'client_id': config['APP_ID'],
        'display': 'page',
        'scope': 'friends, groups',
        'response_type': 'token',
        'v': config['v'],
    }
    print('Ссылка для получения access_token:')
    print('?'.join((config['AUTH_URL'], urlencode(params))))
    token = input('TOKEN:')
    return token
get_token()
