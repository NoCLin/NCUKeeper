# -*- coding: utf-8 -*-
# Author: NoCLin
import configparser

import requests
import re
import logging

logger = logging.getLogger('root')


def get_middle_str(content, left, right):
    pat = re.compile(left + '(.*?)' + right, re.S)
    result = pat.findall(content)
    return result


def print_obj(obj):
    print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))


def http_head(url):
    try:
        r = requests.head(url, timeout=1)
        if r.status_code == 200:
            return True
        logger.error("http_head " + url + " status:" + str(r.status_code))
    except Exception as e:
        logging.exception(e)
    return False


def is_online_by_baidu():
    return http_head("https://www.baidu.com/")


class NCUWLAN():
    URL_DETECT = "http://aaa.ncu.edu.cn:802/srun_portal_pc.php"
    URL_AUTH = "http://aaa.ncu.edu.cn:803/include/auth_action.php"
    URL_STATUS = "http://aaa.ncu.edu.cn:803/srun_portal_pc_succeed.php"

    USERNAME = ""
    PASSWORD = ""

    HEADERS = {
    }

    def __init__(self, username=None, password=None):
        if username is None:
            ini_parser = configparser.ConfigParser()
            with open("./account.ini") as fp:
                ini_parser.read_file(fp)
                self.USERNAME = ini_parser.get("NCUWLAN", "username")
                self.PASSWORD = ini_parser.get("NCUWLAN", "password")
        else:
            self.USERNAME = username
            self.PASSWORD = password

        logger.debug("USERNAME:" + self.USERNAME)

    def status(self):

        try:
            r = requests.get(self.URL_STATUS)
            r_text = r.content.decode("UTF-8")
        except Exception as e:
            logging.exception(e)
            return False

        logger.debug("Status:" + r_text)
        keys = ['username', 'ip', 'data_usage', 'time_usage', 'money']
        keys_cn = ['用户名', 'IP地址', '已用流量', '已用时长', '帐户余额']
        values = get_middle_str(r_text, 'style="font-size:18px;color:#fd7100;">', "</span>")
        rt = {}
        for index, v in enumerate(keys):
            rt[keys_cn[index]] = values[index]
        return rt

    def login(self):
        data = {
            "action": "login",
            "username": self.USERNAME,
            "password": self.PASSWORD,
            "ac_id": "1",
            "user_ip": "",
            "nas_ip": "",
            "user_mac": "",
            "save_me": "1",
            "ajax": "1"
        }

        try:
            r = requests.post(self.URL_AUTH, data=data, headers=self.HEADERS)
            r_text = r.content.decode("UTF-8")
        except Exception as e:
            logging.exception(e)
            return False

        logger.debug("Login:" + r_text)
        if r.text.find("login_ok") > -1:
            return True
        else:
            # TODO: 解析 登录间隔10秒等已知情况
            logger.error("登录失败，未知返回值:" + r_text)
        return False

    def logout(self):
        data = {
            "action": "logout",
            "username": "",
            "password": "",
            "ajax": "1"
        }

        try:
            r = requests.post(self.URL_AUTH, data=data, headers=self.HEADERS)
            r_text = r.content.decode("UTF-8")
        except Exception as e:
            logging.exception(e)
            return False

        logger.debug("Logout:" + r_text)
        if r_text.find("您似乎未曾连接到网络...") > -1:
            return True
        if r_text.find("网络已断开") > -1:
            return True
        else:
            logger.error("登出失败，未知返回值:" + r_text)
            return False

    def is_online_by_ncu(self):
        return http_head(self.URL_DETECT)
