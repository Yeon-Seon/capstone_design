#워드클라우드 

from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from wordcloud import WordCloud, STOPWORDS

path = 'C:\\Users\\hallym\\djangogirls\\blog\\static'


class menu3:
    def __init__(self, keyword, sort, s_date, e_date):
        self.keyword = keyword
        self.sort = sort
        self.s_date = s_date
        self.e_date = e_date

    def crawling(self):
        # title_text = []
        s_from = self.s_date.replace(".", "")
        e_to = self.e_date.replace(".", "")
        page = 1
        maxpage_t = (int(10) - 1) * 10 + 1

        fw = open(path + "\\crawling\\crl_result.txt", 'w', encoding='UTF8')

        while page <= maxpage_t:
            url = "https://search.naver.com/search.naver?where=news&query=" +\
                  self.keyword + "&sort=" + self.sort + "&ds=" + self.s_date + "&de=" + self.e_date + "&nso=so%3Ar%2Cp%3Afrom" +\
                  s_from + "to" + e_to + "%2Ca%3A&start=" + str(page)
            response = requests.get(url)
            html = response.text

            # 뷰티풀소프의 인자값 지정
            soup = BeautifulSoup(html, 'html.parser')

            # 태그에서 제목과 링크주소 추출
            atags = soup.select('._sp_each_title')

            for atag in atags:
                # title_text.append(atag.text)  # 제목
                fw.write(atag.text)

            page += 10

        print('*** success crawling ***')

        fw.close()

    def naver_wordcloud(self):
        fr = open(path + "\\crawling\\crl_result.txt", 'r', encoding='UTF8')
        text = fr.read()

        #경로설정 해주기
        alice_mask = np.array(Image.open(path + "\\img\\cloud.png"))

        # stopwords = set(STOPWORDS)
        # stopwords.add("햄버거")
        naver_cloud = WordCloud(

            font_path='c:/windows/fonts/gulim.ttc',
            width = 100,
            height = 100,
            background_color='#333',
            # , stopwords=stopwords
            mask=alice_mask
            ).generate(text)

        """
        
        fig = plt.figure(figsize=(10, 10))
        plt.imshow(naver_cloud, interpolation='bilinear')
        plt.axis("off")
        """

        naver_cloud.to_file(path + '\\img\\wordcloud.png')

        fr.close()

    def main(self):
        self.crawling()
        self.naver_wordcloud()



