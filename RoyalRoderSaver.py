from urllib.request import urlopen #urlopen은 따로 설치해야함
from bs4 import BeautifulSoup # 파싱을 위한 모듈
import webbrowser # 웹페이지 열기 모듈
import pyautogui
import pyperclip # pyautogui는 한글입력이 안되서 클립보드 복사 모듈 사용
import time
import math

import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

import os

copy_sleep=1.5
paste_sleep=2
enter_sleep=0.3
close_sleep=0.3

url_t='bluestar'
url_id='2220'

def url_soup(url_t,url_id,x):
    base_url = "https://www.royalroader.co.kr/study/study_list?id=2_"+url_t+"&m_idx="+url_id+"&search=all&findword=&page=" #뒤 숫자만 바꾸면 페이지 이동됨
    html = urlopen(base_url+str(x))
    soup = BeautifulSoup(html, "html.parser")
    return soup

def selector(x,y):
    base_selector = ".tbl_type3 > table > tbody > "
    tr_number = "tr:nth-of-type("+str(x)+") > " #tr 부분은 게시글자체를 나타낸다. 범위는 1~10(최대 10개)
    td_number = "td:nth-of-type("+str(y)+")" #td 부분은 각 조각난 것을 나타낸다. 1~4 사용할 예정
    return base_selector+tr_number+td_number

def title(x):
    title_comp=""
    for i in range(1,5):
        title_comp = title_comp+soup.select(selector(x,i))[0].text.strip()+" "
        table = title_comp.maketrans('\/:*?"<>|','_________')
        title_comp = title_comp.translate(table)
    return title_comp

def ini():
    global soup, total_p, final_n, inital_n
    soup = url_soup(url_t,url_id,1)          
    for i in range(1,11):
        try:
            inital_n=int(soup.select(selector(i,1))[0].text.strip())
            break
        except:
            pass 
    total_p = math.ceil(inital_n/10)
    soup = url_soup(url_t,url_id,total_p)
    final_n = soup.select(selector(1,1))[0].text.strip() #마지막 페이지의 게시물 개수, 공백 제거해야하

def page(st,ed):
    page=[]
    for i in (st,ed):
        if len(final_n) == 1: # 첫 페이지의 게시물이 한자리 번호일 경우
            cal_p=1
            if math.floor(i/10)*10+int(final_n) < i:
                cal_p+=1+1*(i//10)
            elif (i//10)!=0: # 10*n 단위 게시물부터 속해있는 페이지의 마지막 게시물까지
                cal_p+=(i//10)
            want_p = 1+total_p-cal_p
        else : # 첫 페이지의 게시물이 두자리 번호일 경우
            want_p = 1+total_p-math.ceil(i/10)
        page.append(want_p)
    return page

def macro(count): # 인덱스로 접근한다.
    pyperclip.copy(title_list[count]) #게시글 내용을 클립보드로 복사한다.
    webbrowser.open(address_list[count])
    time.sleep(copy_sleep)
    pyautogui.hotkey('ctrl', 's')
    time.sleep(paste_sleep)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(enter_sleep)
    pyautogui.hotkey('enter')
    time.sleep(close_sleep)
    pyautogui.hotkey('ctrl', 'w')

def list_append():
    for j in range(1,11):
        try:
            title_list.append(title(j))
            index_list.append(soup.select(selector(j,1))[0].text.strip())
            address_list.append(soup.select(".subj > a")[j-1]['href'])
        except:
            break    

def parsing(st,ed):
    global title_list, address_list, index_list, soup
    temp_st = st
    for p in range(page(st,ed)[0],page(st,ed)[1]-1,-1):
        title_list=[]
        address_list=[]
        index_list=[]
        soup = url_soup(url_t,url_id,p)
        list_append()  
        for i in range(temp_st,ed+1):
            if str(i) in index_list:
                macro(index_list.index(str(i)))
            else:
                temp_st = i
                break

##################UI 부분##################
     
form_class = uic.loadUiType("main.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_partsave.clicked.connect(self.btn_partsave_click)
        self.pushButton_sleep.clicked.connect(self.btn_sleep_click)
        self.pushButton_id.clicked.connect(self.btn_id_click)
        self.id_market.itemDoubleClicked.connect(self.id_market_click)
        self.id_evening.itemDoubleClicked.connect(self.id_evening_click)
        self.id_training.itemDoubleClicked.connect(self.id_training_click)
       
    def btn_partsave_click(self):
        st=int(self.ptsave_st.text())
        ed=int(self.ptsave_ed.text())    
        if st>ed :
            QMessageBox.about(self, "오류", "시작이 끝보다 클 수 없습니다.  ")
        else :
            ini()
            if inital_n < ed or 1 > st : # 1차적으로 st>ed를 제시했으니까 음수는 st로 판별하고 게시물 큰수는 ed로 판별.
                QMessageBox.about(self, "오류", "게시물이 범위에서 벗어났습니다.")
            else:
                parsing(st,ed)
                
    def btn_sleep_click(self):
        global copy_sleep, paste_sleep, enter_sleep, close_sleep
        copy_sleep=float(self.copy_sleep.text())
        paste_sleep=float(self.paste_sleep.text())
        enter_sleep=float(self.enter_sleep.text())
        close_sleep=float(self.close_sleep.text()) 
        QMessageBox.about(self, "메세지", "설정이 저장되었습니다.")

    def btn_id_click(self):
        global url_id, url_t
        url_id=self.id.text()
        url_t=self.id_t.text()
        QMessageBox.about(self, "메세지", "설정이 저장되었습니다.")
        
    def id_market_click(self):
        global url_id, url_t
        id_cr = int(self.id_market.currentRow())
        setxt = self.id_market.currentItem().text()[-4:]
        def setname(name,setxt):
            self.id_t.setText(name)
            self.id.setText(setxt)
            
        if id_cr in (0,7,13,20) : # 강사이름 클릭시
            self.id.setText("")
            self.id_t.setText("")
        elif id_cr in (1,2,3,4,5) : #비중법사
            setname("victory",setxt)
        elif id_cr in (8,9,10,11) : #주식신공
            setname("singong",setxt)
        elif id_cr in (14,15,16,17,18) : #자그마치
            setname("master",setxt)
        elif id_cr in (21,22,23,24) : #프로장인
            setname("pro",setxt) 
        url_id=self.id.text()
        url_t=self.id_t.text()
            
    def id_evening_click(self):
        global url_id, url_t
        id_cr = int(self.id_evening.currentRow())
        setxt = self.id_evening.currentItem().text()[-4:]
        def setname(name,setxt):
            self.id_t.setText(name)
            self.id.setText(setxt)
            
        if id_cr in (0,5,10,17) : # 강사이름 클릭시
            self.id.setText("")
            self.id_t.setText("")
        elif id_cr in (1,2,3) : #오성
            setname("dream590",setxt)
        elif id_cr in (6,7,8) : #확률승부
            setname("pppp1245",setxt) 
        elif id_cr in (11,12,13,14,15) : #푸른별
            setname("bluestar",setxt) 
        elif id_cr in (18,19,20,21,22) : #수급쎄오
            setname("ceo",setxt) 
        url_id=self.id.text()
        url_t=self.id_t.text()

    def id_training_click(self):
        global url_id, url_t
        id_cr = int(self.id_training.currentRow())
        setxt = self.id_training.currentItem().text()[-4:]
        def setname(name,setxt):
            self.id_t.setText(name)
            self.id.setText(setxt)
            
        if id_cr in (0,6,13,19) : # 강사이름 클릭시
            self.id.setText("")
            self.id_t.setText("")
        elif id_cr in (1,2,3,4) : #서희파더
            setname("toptrader",setxt)
        elif id_cr in (7,8,9,10,11) : #제시스페라
            setname("spera",setxt)
        elif id_cr in (14,15,16,17) : #포인트지지
            setname("point",setxt)
        elif id_cr in (20,21,22,23) : #한백
            setname("hanbaek",setxt)
        url_id=self.id.text()
        url_t=self.id_t.text()

if __name__ == "__main__":
    app=QApplication(sys.argv)
    myWindow=MyWindow()
    myWindow.show()
    app.exec_()
    
