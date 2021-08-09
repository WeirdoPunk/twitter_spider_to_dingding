import re
import time
from urllib import parse
from dingtalkchatbot.chatbot import DingtalkChatbot
import crawlertool as tool
from selenium import webdriver
import configparser
import os

path = '/usr/bin/chromedriver'
webhook = ''#你的钉钉机器人的Webhook地址
secret = ''#你的钉钉机器人加签时生成的secret


class SpiderTwitterAccountPost(tool.abc.SingleSpider):
    def __init__(self, driver):
        self.driver = driver
        # 爬虫实例的变量
        self.user_name = None

    @staticmethod
    def get_twitter_user_name(page_url: str) -> str:
        """提取Twitter的账号用户名称
        主要用于从Twitter任意账号页的Url中提取账号用户名称
        :param page_url: Twitter任意账号页的Url
        :return: Twitter账号用户名称
        """
        if pattern := re.search(r"(?<=twitter.com/)[^/]+", page_url):
            return pattern.group()
        
    def running(self, user_name: str):
        """执行Twitter账号推文爬虫
        :param user_name: twitter账号主页名称（可以通过get_twitter_user_name获取）
        :return: 推文信息列表
        """

        self.user_name = user_name
        item_list = []
        # 生成请求的Url
        query_sentence = []
        query_sentence.append("from:%s" % user_name)  # 搜索目标用户发布的推文
        query_sentence.append("-filter:retweets")  # 过滤到所有转推的推文
        query = " ".join(query_sentence)  # 计算q(query)参数的值
        params = {
            "q": query,
            "f": "live"
        }
        actual_url = "https://twitter.com/search?" + parse.urlencode(params)
        self.console("实际请求Url:" + actual_url)

        # 打开目标Url
        self.driver.get(actual_url)
        time.sleep(3)

        # 定位标题外层标签
        label_outer = self.driver.find_element_by_css_selector(
            "main > div > div > div > div:nth-child(1) > div > div:nth-child(2) > div > div > section > div > div")
        self.driver.execute_script("arguments[0].id = 'outer';", label_outer)  # 设置标题外层标签的ID

        # 循环遍历外层标签
        all_twID = []
        for _ in range(1):
            for label_tweet in label_outer.find_elements_by_xpath('//*[@id="outer"]/div'):  # 定位到推文标签               
                item = {}
                # 读取推文ID
                if label := label_tweet.find_element_by_css_selector(
                        "article > div > div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > div > div:nth-child(1) > a"):
                    if pattern := re.search("[0-9]+$", label.get_attribute("href")):
                        item["tweet_id"] = pattern.group()
                        all_twID.append(int(pattern.group()))

                # 解析推文发布时间
                if label := label_tweet.find_element_by_css_selector(
                        "article > div > div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > div > div:nth-child(1) > a > time"):
                    item["time"] = label.get_attribute("datetime").replace("T", " ").replace(".000Z", "")

                # 解析推文内容
                if label := label_tweet.find_element_by_css_selector(
                        "article > div > div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1)"):
                    item["text"] = label.text
                item_list.append(item)
        max_ID = str(max(all_twID))
        for i in item_list:
            if i['tweet_id'] == max_ID:
                tw_time = i['time']
                tw_text = i['text']
                tw_url = 'https://twitter.com/mangomarkets/status/' + i['tweet_id']
                return tw_time, tw_text, tw_url, max_ID


if __name__ == "__main__":
    # 读配置文件
    urlpath = os.path.dirname(os.path.realpath(__file__))
    coinurlpath = os.path.join(urlpath, "coin_url.ini")
    conf = configparser.ConfigParser()
    conf.read(coinurlpath, encoding="utf-8")
    # 获取所有key
    options = conf.options("coin_url")
    key_ID = {}
    # 初始化key_ID
    for k in options:
        key_ID[k] = '1'
    option = webdriver.ChromeOptions()
    option.add_argument("headless")
    option.add_argument('no-sandbox')
    option.add_argument('disable-dev-shm-usage')
    option.add_argument("user-agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'")
    driver = webdriver.Chrome(path, chrome_options=option)
    while True:        
        for j in options:
            host = conf.get("coin_url", j)
            all_text = SpiderTwitterAccountPost(driver).running(user_name=SpiderTwitterAccountPost.get_twitter_user_name(host))
            if key_ID[j] != all_text[3]:
                key_ID[j] = all_text[3]
                xiaoding = DingtalkChatbot(webhook, secret=secret)
                xiaoding.send_text(msg='币种名称：' + j +'\n时间：'+ all_text[0]  + '\n推文：' + all_text[1] +'\n链接：'+ all_text[2])
                driver.quit()
            else:
                driver.quit()
