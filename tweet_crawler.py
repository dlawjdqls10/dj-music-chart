"""
트위터 크롤러.
by 임정빈.
"""

from bs4 import BeautifulSoup
from selenium import webdriver
import time
import datetime as dt
from pandas import DataFrame
import pandas as pd

#startdate에 원하는 시작 날짜 설정
#untildate는 startdate 하루 뒤로.
#enddate에 원하는 종료 날짜 하루 뒤를 설정(ex:29일까지 긁어오고 싶으면 30일로 설정)
startdate=dt.date(year=2018, month=6, day=10)
untildate=dt.date(year=2018, month=6, day=11)
enddate=dt.date(year=2018, month=9, day=11)

tweet_by_date = {}
frequency_by_date = {}
while not startdate == enddate:
    # url 의 q 뒤에 부분()를 원하는 검색어 내용으로.
    url = "https://twitter.com/search?f=tweets&vertical=default&q=웨이백홈%20since%3A{}%20until%3A{}&src=typd".format(startdate, untildate)
    # 본인의 크롬드라이버 경로 지정.
    driver = webdriver.Chrome("C:\dev\chromedriver.exe")
    time.sleep(3)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    # 현재 스크롤 높이 구함
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 스크롤을 끝까지 내림.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        # 새 스크롤 높이를 구하고, 원래 스크롤 높이와 비교 -> 같으면 종료.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    tweets = soup.find_all("p", {"class": "TweetTextSize"})
    texts = []
    if tweets:
        for tweet in tweets:
            texts.append(tweet.get_text())
    frequency_by_date[startdate] = [len(texts)]
    tweet_by_date[startdate] = texts
    # 코드 얼마나 진행됬는지 보여줌
    print(startdate)
    startdate = untildate
    untildate += dt.timedelta(days=1)
    driver.close()
# 트위터 일별 댓글 수, 엑셀로 저장, sheet name 은 바꾸실 필요 없습니다.
writer = pd.ExcelWriter('웨이백홈.xlsx', engine='xlsxwriter')
df = DataFrame(frequency_by_date)
df.to_excel(writer, sheet_name='일별트윗수', encoding='utf-8')
writer.save()
# 트위터 일별 트윗 내용, txt 파일로 저장
with open("웨이백홈.txt", "w", encoding='utf-8') as f:
    for day in tweet_by_date.keys():
        f.write("작성 날짜 : " + str(day))
        f.write("-"*30)
        f.write("\n트윗 내용" + str(tweet_by_date[day]))

