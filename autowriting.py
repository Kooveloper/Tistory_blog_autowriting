import json
import os
import sys
import time
from pandas.core.frame import DataFrame
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import quote
import pandas as pd
import datetime
from datetime import date, timedelta
import pyautogui
from google_trans_new import google_translator
import textwrap
import math
import urllib.request
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
import pyperclip
import random
from newspaper import Article
from newspaper import Config
import openai

# 집/회사에 따른 path 설정 다름
location = "회사"

# 몇번째 티커로 글 작성 할것인지? | 나중에 for문으로 여러개 작성할 수 있도록
ticker_index = 1

# 티스토리 계정
Kakao_id = 'ID'
Kakao_pw = 'PW'
Kakao_url = 'URL'

# 카카오_이메일인증 계정(네이버)
Naver_id = "ID"
Naver_pw = "PW"

# 오픈AI api key
api_key = "API KEY"


# Driver 옵션 (화면 안보이기)
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")

# Driver 설정
path = "./chromedriver.exe"
driver = webdriver.Chrome(path, options=options)

# 파파고 셀레니움
def papago(text):
    driver = webdriver.Chrome(path, options=options)
    driver.get('https://papago.naver.com/')
    time.sleep(2)
    driver.find_element(By.XPATH,
                        '/html/body/div[1]/div/div[1]/section/div/div[1]/div[1]/div/div[3]/label/textarea').send_keys(
        text)
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/section/div/div[1]/div[2]/div/div[6]/div/button').click()
    time.sleep(2)
    return driver.find_element(By.XPATH, '//*[@id="txtTarget"]').text


# 구글 번역기
translator = google_translator()


def google_translate(text):
    translator.translate(text, lang_src='en', lang_tgt='ko')


# 티커 리스트업
m_naver_url = "https://m.stock.naver.com/worldstock/home/USA/up/NASDAQ"
driver.get(m_naver_url)
time.sleep(2)

soup = BeautifulSoup(driver.page_source, features="html.parser")

Ticker_list = {'example': 0}
tags = soup.select("tr.TableComm_tr__2Mxzo")

for tag in tags:
    TICKER = tag.select_one("span.TableComm_stockName__bf-Ff").text
    RISE = tag.select_one("span.VGap_box__e_XIX").text
    PRICE = tag.select_one("span.TableComm_stockPrice__1u7Tg").text
    PRICE_NUM = float(tag.select_one("span.TableComm_stockPrice__1u7Tg").text.replace(",", ""))
    VOLUME = tag.select("td.TableComm_td__31itE.TableComm_tdHide__MofSh")[1].text
    VOLUME_NUM = int(tag.select("td.TableComm_td__31itE.TableComm_tdHide__MofSh")[1].text.replace(",", ""))
    TOTAL_VOL = int(round(PRICE_NUM * VOLUME_NUM, 0))
    # TOTAL_VOL = format(int(round(PRICE_NUM*VOLUME_NUM,0)),',d')

    if VOLUME_NUM > 10000000:
        Ticker_list[f"{TICKER}/{PRICE}/{RISE}/{VOLUME}"] = TOTAL_VOL

# 티커 선택
try:
    del Ticker_list['example']
    sorted_value = sorted(Ticker_list.items(), key=lambda x: [1], reverse=True)
except:
    pass

sorted_value = sorted(Ticker_list.values(), reverse=True)
print(sorted_value)
total_value = sorted_value[ticker_index]
key = [key for key, value in Ticker_list.items() if value == total_value]

# 티커 및 정보 뽑기
ticker = str(key).replace("'", "").replace("(", "").replace(")", "").replace("[", "").split('/')[0].strip()
ticker_rise = str(key).replace("'", "").replace("(", "").replace(")", "").replace("[", "").split('/')[2].strip()
ticker_volume = str(key).replace("'", "").replace("(", "").replace(")", "").replace("]", "").split('/')[3].strip()

print(Ticker_list)
print()
print(f"티커 : {ticker}")
print(f"상승률 : {ticker_rise}")
print(f"거래량 : {ticker_volume}")

# 차트 이미지 다운로드 경로
if location == "회사":
    folder = "User"
elif location == "집":
    folder = "구인화님"

Image_path = f"C:/Users/{folder}/Desktop/python_test/"


# 글 50글자 내외로 자르는 함수
def article_cutter(article):
    b = article.split()
    index = 0
    article = "<br/>"
    for i in range(len(b)):
        article += " "
        article += b[i]

        if 60 > len(article) > 50:
            if article.count('<br/>', 0, len(article)) == 2:
                pass
            elif article.count('<br/>', 0, len(article)) == 1:
                article += '<br/>'

        reverse = ""
        # 나중에 멋있게고치기
        if len(article) > 70:
            for char in article:
                reverse = char + reverse
            if reverse.find('>/rb<') > 50:
                article += '<br/>'
            else:
                continue
    return article

print("완료")

yahoo_url = f"https://finance.yahoo.com/quote/{ticker}"

# yahoo finance 정보 받아오기
driver.get(yahoo_url)
time.sleep(3)
current_volume = int(driver.find_element(By.CSS_SELECTOR,
                                         "#quote-summary > div.D\(ib\).W\(1\/2\).Bxz\(bb\).Pend\(12px\).Va\(t\).ie-7_D\(i\).smartphone_D\(b\).smartphone_W\(100\%\).smartphone_Pend\(0px\).smartphone_BdY.smartphone_Bdc\(\$seperatorColor\) > table > tbody > tr:nth-child(7) > td.Ta\(end\).Fw\(600\).Lh\(14px\)").text.replace(
    ",", ""))
average_volume = int(driver.find_element(By.CSS_SELECTOR,
                                         "#quote-summary > div.D\(ib\).W\(1\/2\).Bxz\(bb\).Pend\(12px\).Va\(t\).ie-7_D\(i\).smartphone_D\(b\).smartphone_W\(100\%\).smartphone_Pend\(0px\).smartphone_BdY.smartphone_Bdc\(\$seperatorColor\) > table > tbody > tr.Bxz\(bb\).Bdbw\(1px\).Bdbs\(s\).Bdc\(\$seperatorColor\).H\(36px\).Bdbw\(0\)\! > td.Ta\(end\).Fw\(600\).Lh\(14px\)").text.replace(
    ",", ""))

# 가격
current_price = float(driver.find_element(By.CSS_SELECTOR,
                                          "#quote-header-info > div.My\(6px\).Pos\(r\).smartphone_Mt\(6px\).W\(100\%\) > div.D\(ib\).Va\(m\).Maw\(65\%\).Ov\(h\) > div.D\(ib\).Mend\(20px\) > fin-streamer.Fw\(b\).Fz\(36px\).Mb\(-4px\).D\(ib\)").text.replace(
    ",", ""))
prev_price = float(driver.find_element(By.CSS_SELECTOR,
                                       "#quote-summary > div.D\(ib\).W\(1\/2\).Bxz\(bb\).Pend\(12px\).Va\(t\).ie-7_D\(i\).smartphone_D\(b\).smartphone_W\(100\%\).smartphone_Pend\(0px\).smartphone_BdY.smartphone_Bdc\(\$seperatorColor\) > table > tbody > tr:nth-child(1) > td.Ta\(end\).Fw\(600\).Lh\(14px\)").text.replace(
    ",", ""))

# 회사 정보
driver.get(f"https://finance.yahoo.com/quote/{ticker}/profile?p={ticker}")
driver.implicitly_wait(3)
companyname = driver.find_element(By.XPATH,
                                  "/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/div/div/section/div[1]/div/h3").text
companywebsite = driver.find_element(By.XPATH,
                                     "/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/div/div/section/div[1]/div/div/p[1]/a[2]").text
# businessSummary = driver.find_element(By.XPATH,"""//*[@id="Col1-0-Profile-Proxy"]/section/section[2]/p""").text
businesstext = driver.find_element(By.XPATH, """//*[@id="Col1-0-Profile-Proxy"]/section/section[2]/p""")
businessSummary = driver.execute_script('return arguments[0].firstChild.textContent;', businesstext).strip()

print(current_price)
print(prev_price)
print(companyname)
print(businessSummary)

# 번역1
business_trans = papago(businessSummary)

# 평균거래량대비 거래량 상승률
DOD_volumenum = round(((current_volume / average_volume) - 1) * 100, 2)
DOD_volume = str(round(((current_volume / average_volume) - 1) * 100, 2)) + "%"

# 전일대비 상승률
DOD_pricenum = round(((current_price / prev_price) - 1) * 100, 2)
DOD_price = str(round(((current_price / prev_price) - 1) * 100, 2)) + "%"

# 상승, 하락 status 판별
if DOD_volumenum > 0:
    DOD_volume_status = "상승"
else:
    DOD_volume_status = "하락"

if DOD_pricenum > 0:
    DOD_price_status = "상승"
else:
    DOD_price_status = "하락"

# 거래량 한글로 변환
kor_volume_num = int(current_volume)

if len(str(kor_volume_num)) == 10:
    num = str(round(kor_volume_num, -8))
    volumetext = f"약 {num[0]}{num[1]}억"

elif len(str(kor_volume_num)) == 9:
    num = str(round(kor_volume_num, -7))
    volumetext = f"약 {num[0]}억{num[1]}천만"

elif len(str(kor_volume_num)) == 8:
    num = str(round(kor_volume_num, -6))
    volumetext = f"약 {num[0]}천{num[1]}백만"

elif len(str(kor_volume_num)) == 7:
    num = str(round(kor_volume_num, -5))
    volumetext = f"약 {num[0]}백{num[1]}십만"

# 글 입력
full_summary = article_cutter(business_trans)

# 제목 입력
title = f"{ticker} 기업분석, 전일 {DOD_price} 급{DOD_price_status}, {DOD_price_status}이유 feat.뉴스"
print("완료")

# 건너 뛸 미디어들 (봇 방지 프로그램 너무 귀찮음)
skip_group = ["TipRanks", "Bloomberg.com", "Investor's Business Daily", "InvestorPlace", "Wall Street Journal", "CNN",
              "Investor's Business Daily", "StockNews", "StreetInsider"]
scrapable_group = ["Yahoo Finance", "Benzinga", "Nasdaq", "Seeking Alpha", "CNBC", "Tastytrade", "Business Wire",
                   "BullionVault", "InvestorsObserver", "PennyStocks.com", "Morningstar", "GlobeNewswire"]

# 뉴스 기사
driver = webdriver.Chrome(path, options=options)

search_url = f"https://www.google.com/search?q=why+{ticker}+rise&tbm=nws&source=lnt&tbs=qdr:d&sa=X&ved=2ahUKEwjv-ub5jfv7AhXBed4KHXFyCeoQpwV6BAgBEBo&biw=1208&bih=968&dpr=1"
driver.get(search_url)
driver.implicitly_wait(5)

url_list = []
media_list = []
soup = BeautifulSoup(driver.page_source, features="html.parser")

# 미디어 저장
for media in soup.select("div.BNeawe.UPmit.AP7Wnd.lRVwie"):
    source = media.getText()
    media_list.append(source)

# 뉴스 url 저장
for tag in soup.select("div.Gx5Zad.fP1Qef.xpd.EtOod.pkphOe > a"):
    href = tag.attrs['href'].split("/url?esrc=s&q=&rct=j&sa=U&url=")[1].split("&ved=")[0]
    url_list.append(href)
print(media_list)
print(url_list)

# skip_group 포함 미디어 제거 및 scrapable 미포함 제거
for i in media_list[:]:
    if i in skip_group or i not in scrapable_group:
        a = media_list.index(i)
        del media_list[a]
        del url_list[a]

content = ""
article = ""

print(media_list)
print(url_list)

# article 끌어올때까지 반복
for i in range(len(media_list)):
    source = media_list[i]
    news_url = url_list[i]

    print(source, news_url)

    # 뉴스 크롤링
    user_agent = 'user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
    config = Config()
    config.browser_user_agent = user_agent

    try:
        news = Article(news_url, config=config)
        news.download()
        news.parse()
        # 본문 크롤링
        content = news.text

    except:
        print("newspaper3k오류")
    if content != "": break
try:
    # Morningstar
    if source == "Morningstar":
        if "This content was created" in content:
            content = content.split("\n")
            article = ""
            for i in content:
                if "This content was created" in i: break
                article += i
                article += "\n"
        else:
            article = content
    # PennyStocks.com
    elif source == "PennyStocks.com":
        if "Want the Top" in content:
            content = content.split("\n")
            article = ""
            for i in content:
                if "To Learn More" in i: break
                article += i
                article += "\n"
        else:
            article = content
    # InvestorsObserver
    elif source == "InvestorsObserver":
        if "See Full" in content:
            content = content.split("\n")
            article = ""
            for i in content:
                if "See Full" in i: break
                article += i
                article += "\n"
        else:
            article = content
    # Business Wire
    elif source == "Business Wire":
        article = ""
        article = content
    # BullionVault
    elif source == "BullionVault":
        article = ""
        article = content
    # Tastytrade
    elif source == "Tastytrade":
        article = ""
        article = content
    # Yahoo Finance
    elif source == "Yahoo Finance":
        if "reporter for Yahoo Finance" in content:
            content = content.split("\n")
            index = [i for i in range(len(content)) if "reporter for Yahoo Finance" in content[i]]
            index = index[0]
            content = content[:index - 2]
            article = ""
            for i in content:
                article += i
                article += "\n"
        else:
            article = content
   # Benzinga
    elif source == "Benzinga":
        if "This article was generated by" in content:
            content = content.split("\n")[:-2]
            article = ""
            for i in content:
                article += i
                article += "\n"
        else:
            article = content
    # GlobeNewswire
    elif source == "GlobeNewswire":
        article = ""
        article = content
    # Nasdaq
    elif source == "Nasdaq":
        if "The views and opinions expressed herein" in content:
            content = content.split("\n")[:-1]
            article = ""
            for i in content:
                article += i
                article += "\n"
        else:
            article = content
    # Seeking Alpha
    elif source == "Seeking Alpha":
        if "Getty Images" in content:
            content = content.split("\n")[2:]
            article = ""
            for i in content:
                article += i
                article += "\n"
        else:
            article = content
    # CNBC
    elif source == "CNBC":
        content = content.split("\n")[2:]
        content = content[:-1]
        article = ""
        for i in content:
            article += i
            article += "\n"

except:
    driver.get(news_url)
    print(f"{source} 뉴스를 긁어오지 못했습니다. 본문을 입력해주세요")
    article = input()

if len(article) < 10:
    driver.get(news_url)
    print(f"{source} 뉴스를 제대로 긁어오지 못했습니다. 본문을 입력해주세요")
    article = input()

print("완료")

if len(article) > 4900:
    article1 = article[:len(article) // 2]
    article2 = article[len(article) // 2:]

    article_trans1 = papago(article1)
    article_trans2 = papago(article2)
    article_trans = article_trans1 + article_trans2

else:
    article_trans = papago(article)

try:
    # 내용 정리 및 요약
    question = f"""아래 내용 중 {ticker}({companyname})의 가격변화에 대한 내용을 위주로 15줄 이내로 정리해줘 \n{article_trans}"""
    api_key = "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"
    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a chatbot"},
            {"role": "user", "content": f"{question}"},
        ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content

    ai_script = article_cutter(result)
    print(ai_script)

except:
    article_trans = article_cutter(article_trans)

# 차트 이미지 다운로드
driver = webdriver.Chrome(path)
driver.get(f"https://kr.investing.com/search/?q={ticker}")
driver.maximize_window()
driver.implicitly_wait(3)

# 팝업창 확인, 닫기
try:

    driver.find_elements_by_xpath("/html/body/div[7]/div[2]/i").click()
    driver.implicitly_wait(3)
except:
    pass

# 팝업창 확인, 닫기
try:
    driver.find_element(By.XPATH, "/html/body/div[7]/div[2]/i").click()
    driver.implicitly_wait(3)
except:
    pass

# 제일 첫번째항목 클릭
driver.find_element(By.XPATH, "/html/body/div[5]/section/div/div[2]/div[2]/div[1]/a[1]").click()
driver.implicitly_wait(5)

# 팝업창 확인, 닫기
try:
    driver.find_element(By.XPATH, "/html/body/div[7]/div[2]/i").click()
except:
    pass

# 차트 섹션 스크린샷 저장
chart = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div/div[2]/main/div/div[7]/div/div[1]/div')
chart.screenshot(f"{Image_path}Chart.png")
time.sleep(2)

# 웹사이트 이미지 다운로드
driver.get(companywebsite)
driver.maximize_window()
time.sleep(1)
elem = driver.find_element(By.TAG_NAME, 'body')
elem.screenshot(f"{Image_path}Website.png")

# 로고 이미지 다운로드

# 로고 이미지 다운로드
driver = webdriver.Chrome(path)
driver.get(f"https://www.google.com/search?q={companyname}&tbm=isch")
soup = BeautifulSoup(driver.page_source, features="html.parser")
time.sleep(2)
images = driver.find_element(By.XPATH, '/html/body/div[2]/c-wiz/div[3]/div[1]/div/div/div/div/div[1]/div[1]/span/div[1]/div[1]/div[1]/a[1]/div[1]/img').click()
time.sleep(2)

logo_url=""

#가끔 XPATH값이 바뀜
XPATH_list = ["/html/body/div[2]/c-wiz/div[3]/div[2]/div[3]/div[2]/div/div[2]/div[2]/div[2]/c-wiz/div/div[1]/div[2]/div[2]/div/a/img","/html/body/div[2]/c-wiz/div[3]/div[2]/div[3]/div[2]/div/div[2]/div[2]/div[2]/c-wiz/div/div[2]/div[1]/a/img[1]"]
while True:
    try :
        for i in XPATH_list :
            logo_url = driver.find_element(By.XPATH,
                                           i).get_attribute("src")
            print(logo_url)
            if logo_url!="" :break
        if logo_url != "": break
    except : pass

urllib.request.urlretrieve(logo_url, f"{Image_path}Logo.png")
time.sleep(1)

###차트 사진 업로드 및 img 주소 만들기
driver.get("https://postimg.cc/")
driver.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div/div[2]/div/form/div[1]/div[1]/div[3]/div/span").click()
print("chart image upload")
time.sleep(3)

# 이미지 업로드 스크립트 실행
os.system(f"{Image_path}Image_upload_Chart.exe")
time.sleep(3)

# 링크 종류 선택
soup = BeautifulSoup(driver.page_source, features="html.parser")
tag_url = ""
time.sleep(1)
tag_url = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[3]/div/form/div[8]/div[2]/div/input").get_attribute('value')

img_Chart_url = tag_url.split("_blank'><img src='")[1].split("' border='0'")[0]
print(img_Chart_url)

###로고 사진 업로드 및 img 주소 만들기
driver.get("https://postimg.cc/")
driver.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div/div[2]/div/form/div[1]/div[1]/div[3]/div/span").click()
print("logo image upload")
time.sleep(3)

# 이미지 업로드 스크립트 실행
os.system(f"{Image_path}Image_upload_Logo.exe")
time.sleep(3)

# 링크 종류 선택
soup = BeautifulSoup(driver.page_source, features="html.parser")
tag_url = ""
time.sleep(1)
tag_url = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[3]/div/form/div[8]/div[2]/div/input").get_attribute('value')

img_Logo_url = tag_url.split("_blank'><img src='")[1].split("' border='0'")[0]
print(img_Logo_url)

###웹사이트 사진 업로드 및 img 주소 만들기
driver.get("https://postimg.cc/")
driver.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div/div[2]/div/form/div[1]/div[1]/div[3]/div/span").click()
print("website image upload")
time.sleep(3)

# 이미지 업로드 스크립트 실행
os.system(f"{Image_path}Image_upload_Website.exe")
time.sleep(3)

# 링크 종류 선택
soup = BeautifulSoup(driver.page_source, features="html.parser")
tag_url = ""
time.sleep(1)
tag_url = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[3]/div/form/div[8]/div[2]/div/input").get_attribute('value')

img_Website_url = tag_url.split("_blank'><img src='")[1].split("' border='0'")[0]

ment = ['다루는 소식들은 급등주 관련 소식들이지만<br/>투자의 영역은 항상 보수적으로<br/>접근하시기를 권고드리며<br/><br/>오늘도 안전하고 성공적인<br/>투자하시길 바라겠습니다 :)<br/>',
        '개인투자는 항상 여유자금으로 하셔서<br/>일상과 멘탈에 지장이 없기를 바라겠습니다,<br/><br/>오늘도 안전하고 성공적인<br/>투자하시길 바라겠습니다 :)<br/>',
        '무리하게 급등주를 쫓기보단<br/>자신의 가설과 기업조사를 통한<br/>건전한 투자 생활 하시기 바라며,<br/><br/>오늘도 안전하고 성공적인<br/> 투자가 되시길 바라겠습니다! :)<br/>']
ending_phrase = random.choice(ment)

full_html = f"""
<blockquote data-ke-style="style1"><span style="font-family: 'Noto Sans Demilight', 'Noto Sans KR';"><b>{ticker} : {companyname}<br/> 전일 대비 {DOD_price} {DOD_price_status}한 ${current_price}로 마감<br/>전일 거래량 {volumetext}주로, 평균거래량 대비 {DOD_volume} {DOD_volume_status}</b></span></blockquote>
<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style2" />
<p style="text-align: center;" data-ke-size="size18"><div style="text-align:center"><img src="{img_Chart_url}" width ="600"></div></p>
<p style="text-align: center;" data-ke-size="size18"><span style="color: #555555; font-family: 'Noto Sans Light';">오늘의 종목▼</span><br /><span style="color: #555555; font-family: 'Noto Sans Demilight', 'Noto Sans KR';"><b>{ticker} ({companyname})</b></span></p>
<p style="text-align: center;" data-ke-size="size18">&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16">&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16">
<span style="font-family: 'Noto Sans Demilight', 'Noto Sans KR';">오늘의 주제 {ticker} : {companyname}은<br/> 전일 장중 강한 {DOD_price_status}세를 보여줬는데요 <br/> {ticker}는 전일 대비 <b><span style="color: #ee2323;">{DOD_price} {DOD_price_status}</span></b>한 <b><span style="color: #ee2323;">${current_price}</span></b>로 마감하였고,<b><br/><span style="color: #ee2323;">전일 거래량은 {volumetext}주</span></b>로, 평균거래량 대비 <b><span style="color: #ee2323;">{DOD_volume} {DOD_volume_status}</span><br/>하는 모습을 보여주었습니다.</b></span>
</p>
<p style="text-align: center;" data-ke-size="size16">&nbsp;</p>
<p data-ke-size="size16">&nbsp;</p>
<div class="book-toc">
<p data-ke-size="size16">목차</p>
<ul id="toc" style="list-style-type: disc;" data-ke-list-type="disc"></ul>
<div>&nbsp;</div>
</div>
<h3 style="text-align: center;" data-ke-size="size23"><span style="font-family: 'Noto Sans Demilight', 'Noto Sans KR';"><b>&lt;{companyname} : {ticker}&gt;</b></span></h3>
<p style="text-align: center;" data-ke-size="size16">
<div style="text-align:center">
</div>
<p style="text-align: center;" data-ke-size="size16">&nbsp;</p>
<p style="text-align: center;" data-ke-size="size18"><div style="text-align:center"><img src="{img_Logo_url}" width ="600"></div></p>
<p style="text-align: center;" data-ke-size="size32">기업명 : {companyname}</p></br>
<p style="text-align: center;" data-ke-size="size16">{full_summary}</p>
<br/>

<br/>
<p style="text-align: center;" data-ke-size="size16">&nbsp;</p>
<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style2" />
<h3 style="text-align: center;" data-ke-size="size23"><span style="font-family: 'Noto Sans Demilight', 'Noto Sans KR';"><b>&lt;{ticker} {DOD_price_status} 이유&gt;</b></span></h3>
<p style="text-align: center;" data-ke-size="size16">&nbsp;</p>
<p style="text-align: center;" data-ke-size="size18"><div style="text-align:center"><img src="{img_Website_url}" width ="600"></div></p>
<p style="text-align: center;" data-ke-size="size16">{ai_script}</p></br>
<p style="text-align: center;" data-ke-size="size12"><span style="color: #9d9d9d;">출처 : {source}</span></p>
<p style="text-align: center;" data-ke-size="size16">&nbsp;</p>



<p style="text-align: center;" data-ke-size="size16">&nbsp;</p>
<div style="margin: 15px 0; text-align: center;"><!-- 본문 중간1_디스플레이_수평 --> <ins class="adsbygoogle" style="display: block;" data-ad-client="ca-pub-2488357035555802" data-ad-slot="6157169451" data-ad-format="auto" data-full-width-responsive="true"> </ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({{}});
  </script>
</div>
<p style="text-align: center;" data-ke-size="size16">&nbsp;</p>
<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style2" />
<p style="text-align: center;" data-ke-size="size16">{ending_phrase}</p>
<p style="text-align: center;" data-ke-size="size16">&nbsp;</p>
<p style="text-align: center;" data-ke-size="size14"><span style="color: #dddddd; font-family: 'Noto Sans Light';">※절대 매수, 매도에 대한 추천 아닙니다.</span></p>
<p style="text-align: center;" data-ke-size="size14"><span style="background-color: #ffffff; color: #dddddd; font-family: 'Noto Sans Light';">※투자의 책임은 본인에게 있습니다.</span></p>
<p style="text-align: center;" data-ke-size="size14"><span style="background-color: #ffffff; color: #dddddd; font-family: 'Noto Sans Light';">※반박 시&nbsp;님말이 다 맞음</span></p>
<p data-ke-size="size18">&nbsp;</p>
"""

BLOG_URL = "https://accounts.kakao.com/login/?continue=https%3A%2F%2Fkauth.kakao.com%2Foauth%2Fauthorize%3Fis_popup%3Dfalse%26ka%3Dsdk%252F1.43.0%2520os%252Fjavascript%2520sdk_type%252Fjavascript%2520lang%252Fko-KR%2520device%252FWin32%2520origin%252Fhttps%25253A%25252F%25252Fwww.tistory.com%26auth_tran_id%3Dhb19ipxfpii3e6ddd834b023f24221217e370daed18lbkjs6p5%26response_type%3Dcode%26state%3DaHR0cHM6Ly93d3cudGlzdG9yeS5jb20v%26redirect_uri%3Dhttps%253A%252F%252Fwww.tistory.com%252Fauth%252Fkakao%252Fredirect%26through_account%3Dtrue%26client_id%3D3e6ddd834b023f24221217e370daed18&talk_login=hidden"
path = "./chromedriver.exe"
# chrome_options = Options()
# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(path)
driver.get(BLOG_URL)

#카카오 로그인
# ID 입력

driver.find_element(By.XPATH, "/html/body/div/div/div/main/article/div/div/form/div[1]/input").send_keys(
    Kakao_id)
driver.implicitly_wait(3)

# PW 입력
driver.find_element(By.XPATH, "/html/body/div/div/div/main/article/div/div/form/div[2]/input").send_keys(
    Kakao_pw)
driver.implicitly_wait(3)

# 로그인 클릭
driver.find_element(By.XPATH, "/html/body/div[1]/div/div/main/article/div/div/form/div[4]/button[1]").click()
driver.implicitly_wait(3)
driver.find_element(By.XPATH,"/html/body/div/div/div/main/article/div/div/a").click()

time.sleep(2)

#네이버 로그인 및 인증번호 확인
driver.execute_script('window.open("https://mail.naver.com/v2/folders/-1");')
driver.switch_to.window(driver.window_handles[1])

#ID입력
pyperclip.copy(Naver_id)
driver.find_element(By.XPATH,"/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div[1]/input").send_keys(Keys.CONTROL,'v')
time.sleep(1)

#PW입력
pyperclip.copy(Naver_pw)
driver.find_element(By.XPATH,"/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[1]/div[2]/input").send_keys(Keys.CONTROL,'v')
time.sleep(1)

#로그인 클릭
driver.find_element(By.XPATH,"/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[7]/button").click()
driver.implicitly_wait(3)

#첫번째 메일 클릭
driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div/div/div[4]/div/ul/li[1]/div/div[4]/div").click()
driver.implicitly_wait(3)
verification = driver.find_element(By.XPATH, "/html/body/div[3]/div/div[2]/div/div/div[3]/div/div/div/div[2]/div/div/div/table/tbody/tr[1]/td/table/tbody/tr[9]/td[2]/table/tbody/tr[5]/td[3]").text

#인증번호 입력
driver.switch_to.window(driver.window_handles[0])
pyperclip.copy(verification)
driver.find_element(By.XPATH,"/html/body/div/div/div/main/article/div/div/form/div[2]/input").send_keys(Keys.CONTROL,'v')

#카카오 로그인 클릭
driver.find_element(By.XPATH,"/html/body/div/div/div/main/article/div/div/form/div[4]/button").click()
time.sleep(1)

# 글쓰기 이동
driver.get(f"{Kakao_url}/manage/newpost/?type=post&returnURL=%2Fmanage%2Fposts%2F")
time.sleep(2)

#임시저장글 확인
try:
    WebDriverWait(driver, 3).until(EC.alert_is_present())
    alert = driver.switch_to.alert

    # 취소하기(닫기)
    alert.dismiss()

    # 확인하기
    alert.accept()
except:
    print("no alert")

# 카테고리 설정
driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div[1]/div/button").click()
driver.implicitly_wait(3)
driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div[1]/div[2]/div/div[6]").click()
driver.implicitly_wait(3)

# HTML 작성모드로 전환
driver.find_element(By.XPATH,
                    "/html/body/div[1]/div/main/div/div[5]/div/div/div[1]/div/div/div/div/div/div[5]/div/div/button").click()
driver.implicitly_wait(3)
driver.find_element(By.ID, "editor-mode-html").click()
driver.implicitly_wait(3)

# 본문 입력
driver.find_element(By.XPATH,
                    "/html/body/div[1]/div/main/div/div[3]/div[2]/div/div/div[6]/div[1]/div/div/div/div[5]/div/pre").click()
driver.implicitly_wait(3)
pyperclip.copy(full_html)
driver.implicitly_wait(3)
time.sleep(3)
ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
driver.implicitly_wait(3)

# 일반 모드로 전환
driver.find_element(By.XPATH,
                    "/html/body/div[1]/div/main/div/div[3]/div[1]/div/div/div/div/div/div[5]/div/div/button").click()
driver.implicitly_wait(3)
driver.find_element(By.ID, "editor-mode-kakao-tistory").click()
driver.implicitly_wait(3)

# 제목 입력
driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div[2]/textarea").send_keys(title)

# 태그 입력
if DOD_price_status=="상승":
    tag="급등"
else : tag="급락"

tag_text = f"{ticker},{ticker}주가, {ticker}주식, {ticker}전일, {ticker}{DOD_price_status}, {tag}, {companyname},{ticker.lower()} "

# 태그 쉼표 구분 및 공백 제거
tag_list = [x.strip() for x in tag_text.split(',')]
print(tag_list)

# 태그 입력
for tag in tag_list:
    driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div[6]/span/div/input").send_keys(tag)
    driver.implicitly_wait(3)
    driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div[6]/span/div/input").send_keys(Keys.ENTER)
    driver.implicitly_wait(3)
    print("글 작성 완료! 검토 후 업로드를 눌러주세요!")
