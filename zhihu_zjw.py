# -*- coding: utf-8 -*-
# @AuThor  : frank_lee

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from scrapy.selector import Selector
import re
import pymysql


class zhihu_answer():
    """
    """
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 30)  # 设置超时时间
        # 以下保存到Mysql数据库，不想要可以删掉
        self.db = pymysql.connect("localhost", "root", "", "test")
        self.cursor = self.db.cursor()
        # 创建一个表
        sql = """Create table If Not Exists  zhangjiawei (
                  title varchar(50) not null ,
                  votes varchar(20) not null,
                  comment varchar(20) not null,
                  content longtext not null
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
        try:
            # 执行sql语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
        except:
            # 如果发生错误则回滚
            self.db.rollback()
        # mysql部分结束

    def get_pagesource(self, url):
        self.driver.get(url=url)
        self.driver.maximize_window()
        time.sleep(5)

        # 执行点击动作
        for i in range(1, 11):
            content_click = '#Profile-answers > div:nth-child(2) > div:nth-child('+str(i)+\
                      ') > div > div.RichContent.is-collapsed > div.RichContent-inner'
            try:
                complete_content = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, content_click)))
                complete_content.click()
                time.sleep(1)
            except:
                pass
        pagedata = self.driver.page_source
        return pagedata

    def parse_content(self, data):
        response = Selector(text=data)  # 这里如果不使用"text=data",直接写data将会报错 'str' object has no attribute 'text'
        infodata = response.css("#Profile-answers > div:nth-child(2) > div")
        for infoline in infodata:
            title = infoline.css("div h2 div a::text").extract_first("")
            votes = infoline.css("div > div.RichContent > div > span > button.Button.VoteButton.VoteButton--up::text").extract_first("")
            comment = infoline.css("div > div.RichContent > div > button:nth-child(2)::text").extract_first("")
            content_f = infoline.css("div > div.RichContent > div.RichContent-inner > span").extract()
            content = self.handle_content(content_f)

            # 为保存到mysql做的处理，不想保存可以删掉
            result = {
                "title": title,
                "votes": votes,
                "comment": comment,
                "content": content
            }

            # 保存到mysql数据库的操作，可选
            insert_sql = """
                insert into zhangjiawei(title, votes, comment, content) values(%s, %s, %s, %s);
                """
            try:
                # 执行sql语句
                self.cursor.execute(insert_sql,
                                    (result["title"], result["votes"], result["comment"], result["content"]))
                # 提交到数据库执行
                self.db.commit()
            except:
                # 如果发生错误则回滚
                self.db.rollback()
            print(result['title']+"--"+result['votes']+"--"+result['comment'])

    def handle_content(self, content_info):
        content_f = "".join(content_info)
        content_reg = re.compile(r'<[^>]+>', re.S)
        content = content_reg.sub('', content_f)
        return content


if __name__ == '__main__':
    z = zhihu_answer()
    for i in range(1, 5):
        url = 'https://www.zhihu.com/people/zhang-jia-wei/answers?page='+str(i)
        data = z.get_pagesource(url)
        z.parse_content(data=data)
        time.sleep(5)