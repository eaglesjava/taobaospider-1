# coding=utf-8

# coding=utf-8
import requests
import json
from queue import Queue
import threading

import time


class Taobao(object):
    def __init__(self, goods):
        self.start_url = 'http://s.m.taobao.com/search?q={}&n=200&m=api4h5&style=list&page={}'.format(goods,{})
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"
        }
        self.url_queue = Queue()
        self.html_queue = Queue()
        self.content_queue = Queue()

    def ger_url_list(self):
        # url_list = []
        # for i in range(101):
        #     url = self.start_url.format(i)
        #     url_list.append(url)
        # return url_list
        for i in range(101):
            self.url_queue.put(self.start_url.format(i))

    def _parse_url(self,url):
        response = requests.get(url,headers=self.headers,timeout=3)
        assert response.status_code == 200
        return response.content.decode()

    def parse_url(self):
        while True:
            url = self.url_queue.get()
            try:
                html = self._parse_url(url)
            except:
                html = None
            self.html_queue.put(html)
            self.url_queue.task_done()

    def get_content_list(self):
        while True:
            html = self.html_queue.get()
            if html is not None:
                json_str = json.loads(html)
                data_list = json_str["listItem"]
                content_list = []
                for data in data_list:
                    # time.sleep(5)
                    temp = {}
                    temp["goods"] = data["title"]
                    temp["price"] = data["price"]
                    temp["sold"] = data["sold"]
                    if data.get("commentCount",""):
                        temp["commentCount"] = data["commentCount"]
                    temp["nick"] = data["nick"]
                    temp["location"] = data["location"]
                    # temp["url"] = data[]
                    content_list.append(temp)
                self.content_queue.put(content_list)
            self.html_queue.task_done()

    def save_content(self):
        while True:
            content_list = self.content_queue.get()
            with open("goodslatiao.json", "a", encoding="utf8") as f:
                for content in content_list:

                    f.write(json.dumps(content,ensure_ascii=False, indent=2))
                    f.write(",\n")
            print("success")
            self.content_queue.task_done()



    def run(self):
        threading_list = []
        # 获取url
        t_url = threading.Thread(target=self.ger_url_list)
        threading_list.append(t_url)
        # print(url_list)
        # 发送请求
        for i in range(10):
            t_parse = threading.Thread(target=self.parse_url)
            threading_list.append(t_parse)
        # for url in url_list:
        #     print(url)
        #     html = self.parse_url(url)
        #     json_str = json.loads(html)
        #     content_list = self.get_content_list(json_str)
        #     self.save_content(content_list)
            # print(json_str)
        # 提取数据
        t_content = threading.Thread(target=self.get_content_list)
        threading_list.append(t_content)
        # 保存数据
        for i in range(10):
            t_save = threading.Thread(target=self.save_content)
            threading_list.append(t_save)
        for t in threading_list:
            t.setDaemon(True)
            t.start()
            # print(t_url)
        for q in [self.url_queue, self.html_queue, self.content_queue]:
            q.join()
            print("success1111111")
if __name__ == '__main__':
    a = Taobao('零食辣条')
    a.run()
