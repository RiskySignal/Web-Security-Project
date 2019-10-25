# coding=utf-8
import glob
import os

if __name__ == '__main__':
    root_path = "D:\\workspace\\Web-Security-Project\\dataset\\useful dataset"
    output_path = "D:\\workspace\\Web-Security-Project\\dataset\\total_dict.txt"

    # o_file_handler = open(output_path, 'w')
    pw_lists = []
    num = 0
    for _file in glob.glob(os.path.join(root_path, "*.txt")):
        print(_file)
        i_file_handler = open(_file, 'r')
        i_file_handler.readlines()
        # for _line in i_file_handler.readlines():
        #     _line = _line.strip()
        #     if _line and _line not in pw_lists:
        #         num += 1
        #         pw_lists.append(_line)
        #         o_file_handler.write(_line + "\n")
        i_file_handler.close()

    # o_file_handler.close()
