#크롤링 메뉴

import pickle
from django.http import HttpResponse
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import os
from selenium.common import exceptions
import re
import nltk
import numpy as np
import tensorflow as tf
from konlpy.tag import Okt
import json


class Text(object):
    def __init__(self, file_name):
        self.file_name = file_name

    def _write_text(self, text, types='a'):
        # print(type(text))
        with open(self.file_name, types, encoding='utf8') as file:
            file.write(text + "\n")


# Setting class
class Setting(object):

    def __init__(self):
        self.__options = webdriver.ChromeOptions()
        self.__options.add_argument('headless')
        self.__options.add_argument('window-size=1920x1080')
        self.__options.add_argument('--disable-gpu')
        self.__options.add_argument("lang=ko_KR")  # 한국어!
        self.__options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        self.__dirver = ""
        # dirver가 없는 경우.
        try:
            self.__driver = webdriver.Chrome('C:\\Program Files\\chromedriver_win32\\chromedriver',
                                             options=self.__options)
        except:
            print("드라이브를 설치하거나 경로를 다시 설정 해주세요")
            # self.check_chrome_version()

    def get_driver(self):

        return self.__driver


class DeepleringModel(object):

    def __init__(self):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        with open('C:\\Users\\hallym\\djangogirls\\blog\\static\\crawling\\train_docs.json', encoding="utf-8") as f:
            self.train_docs = json.load(f)

        with open('C:\\Users\\hallym\\djangogirls\\blog\\static\\crawling\\tokens.txt', 'rb') as file:
            self.tokens = pickle.load(file)

        self.model = tf.keras.models.load_model(
            'C:\\Users\\hallym\\djangogirls\\blog\\static\\crawling\\emotional analysis1.h5')
        self.okt = Okt()
        self.text = nltk.Text(self.tokens, name='NMSC')
        self.selected_words = [f[0] for f in self.text.vocab().most_common(10000)]

        self.bad = 0
        self.good = 0

    def comment_top(self, files):
        line = None

        with open(files, 'r') as file:
            line = [line for line in file.read().splitlines()]

        line = [self.tokenize(row) for row in line]
        tokens = [t for d in line for t in d[0]]
        text = nltk.Text(tokens, name='NMSC')
        print(text.vocab().most_common(10))




    def tokenize(self, doc):

        # norm은 정규화, stem은 근어로 표시하기를 나타냄
        return ['/'.join(t) for t in self.okt.pos(doc, norm=True, stem=True)]

    def term_frequencys(self, doc):
        return [doc.count(word) for word in self.selected_words]

    def predict_pos_neg(self, review):

        # 형태소 구별.
        token = self.tokenize(review)

        tf = self.term_frequencys(token)

        data = np.expand_dims(np.asarray(tf).astype('float32'), axis=0)

        score = float(self.model.predict(data))

        if score > 0.5:
            self.good += 1

        else:
            print(review)
            self.bad += 1
            return review

    def bad_or_good(self):

        return self.bad, self.good


class Crawling(object):

    def __init__(self):
        self.header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)\AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
            "Accept": "text/html,application/xhtml+xml,application/xml;\
                        q=0.9,imgwebp,*/*;q=0.8"}

        self.href = []
        self.news_title = []
        self.company_name = []
        self.name_commpy = []
        self.select_user_company = []
        self.start_date = 0
        self.end_date = 0
        self.keyword = 0
        self.page = 0

        # 설정된 크롬드라이브 가져오기.
        self.__driver = Setting().get_driver()
        self.model = DeepleringModel()

    def parsing_html(self, source):
        soup = BeautifulSoup(source, "lxml")
        return soup

    def parsing(self, url):
        html = requests.get(url, headers=self.header)
        # 파싱
        soup = BeautifulSoup(html.content, "lxml")
        return soup

    def Crawling_run_naver(self, start_date, end_date, keyword, sort=0):
        # 해당 사이트 주소 리스트

        # 접근 오류 해결하기 위함.
        requests.packages.urllib3.disable_warnings()
        page = 1
        s_from = start_date.replace(".", "")
        e_to = end_date.replace(".", "")
        # sort 0 : 관련도,  1 : 최신순 , 2 : 오래된

        max_page = (3 - 1) * 3 + 1

        while page <= max_page:
            url = "https://search.naver.com/search.naver?where=news&query=" + keyword + "&sort=" + str(
                sort) + "&ds=" + start_date + "&de=" + end_date + "&nso=so%3Ar%2Cp%3Afrom" + s_from + "to" + e_to + "%2Ca%3A&start=" + str(
                page)

            soup = self.parsing(url)
            new_title = soup.select("._sp_each_url")
            company_names = soup.select("._sp_each_source")

            years = soup.select(".txt_inline")

            # 뉴스 기사 주소 수집
            for urls, name in zip(new_title, company_names):

                self.href.append(urls['href'])

                try:
                    self.name_commpy.append(name.text.replace("언론사 선정", ""))

                except Exception as e:
                    pass
                    #print(e)
            # continue

            # 네이버 페이지 전환 규칙
            page += 10

        self.collect_comment(keyword)

        return self.model.bad_or_good()

    def get_company_name(self):

        company_xpath = ['//*[@id="content"]/div[1]/div/div[1]/a/img', '//*[@id="main_content"]/div[1]/div[1]/a/img']
        company = ""

        for xpath in company_xpath:

            if self.__driver.find_elements_by_xpath(xpath):
                for i in self.__driver.find_elements_by_xpath(xpath):
                    company = i.get_attribute("alt")
                break

        return company

    def get_news_title(self, company, css_selector):

        news_title = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '',
                            self.__driver.find_element_by_css_selector(css_selector).text)
        collect_text = Text(company + '/' + news_title + ".txt")
        return collect_text

    def collect_comment(self, keyword):

        comment_top = Text('top.txt')
        for news in self.href:

            self.__driver.implicitly_wait(3)
            self.__driver.get(news)

            try:
                # 최초 더보기 버튼 클릭
                self.__driver.find_element_by_css_selector(".u_cbox_btn_view_comment").click()
                self.__driver.implicitly_wait(3)

            # 버튼의 유형이 다른 경우 발생
            except Exception as e:
                try:
                    self.__driver.find_element_by_css_selector(".simplecmt_link_text").click()
                    self.__driver.implicitly_wait(3)
                except:
                    continue

                # pass

            # 더보기 버튼 계속 누르기.

            # 뉴스 기사 및 회사이름 가져오기.
            company = self.get_company_name()

            collect_text = ""
            company = 'C:\\Users\\hallym\\악성댓글수집결과\\' + keyword + "_" + company.strip()

            try:

                if not os.path.exists(company.strip()):
                    os.mkdir(company)

            except Exception as e:
                pass
                #print("os.mkdir 에러", e)

            try:

                collect_text = self.get_news_title(company, '.end_tit')
            except:
                try:
                    collect_text = self.get_news_title(company, '.tts_head')

                except:
                    collect_text = self.get_news_title(company, '#articleTitle')

            try:
                while True:
                    self.__driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
                    self.__driver.find_element_by_css_selector(".u_cbox_btn_more").click()
                    self.__driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")

            except exceptions.ElementNotVisibleException as e:  # 페이지
                pass
            except Exception as e:  # 다른 예외 발생시 확인
                self.page += 1
                #print("에러 :  ", e)

            # document.body.scrollHeight
            # 스크롤 끝으로 올림.
            # self.__driver.execute_script("window.scrollTo(0, 0);")
            soup = self.parsing_html(self.__driver.page_source)
            comment_list = soup.find_all("span", {"class": "u_cbox_contents"})
            # last_height = self.__driver.execute_script("return document.body.scrollHeight")
            # elem = self.__driver.find_element_by_tag_name("body")

            down = 0
            number = 1

            for comment in comment_list:
                try:
                    collect_text._write_text(self.model.predict_pos_neg(comment.text))
                    comment_top._write_text(comment, 'r')
                except:
                    continue


            self.page += 1

        self.model.comment_top('top.txt')
