from posixpath import split
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from database import DataBase
import datetime
from matplotlib import pyplot as plt
import numpy as np
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from kivy.clock import Clock
import subprocess
import time
import random
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
import csv
import difflib
import kivy

class CreateAccountWindow(Screen):
    namee = ObjectProperty(None)
    password = ObjectProperty(None)

    def submit(self):
        if self.namee.text != "":
            if self.password != "":
                k = db.add_user(self.password.text, self.namee.text)
                if k == -1:
                    usedname()
                self.reset()
                sm.current = "login"
            else:
                invalidForm()
        else:
            invalidForm()

    def login(self):
        self.reset()
        sm.current = "login"

    def reset(self):
        self.password.text = ""
        self.namee.text = ""

class LoginWindow(Screen):
    namee = ObjectProperty(None)
    password = ObjectProperty(None)

    def loginBtn(self):
        if db.validate(self.namee.text, self.password.text):
            MainWindow.current = self.namee.text
            MainTalk.current = self.namee.text
            MainRsp.current = self.namee.text
            HRecord.current = self.namee.text
            self.reset()
            sm.current = "main"
        else:
            invalidLogin()

    def createBtn(self):
        self.reset()
        sm.current = "create"

    def reset(self):
        self.namee.text = ""
        self.password.text = ""


class MainWindow(Screen):
    n = ObjectProperty(None)
    created = ObjectProperty(None)
    current = ""

    def logOut(self):
        sm.current = "login"

    def on_enter(self, *args):
        self.n.text = "Hi," + self.current + "!"

class MainTalk(Screen):
    n = ObjectProperty(None)
    created = ObjectProperty(None)
    current = ""
    input = ObjectProperty(None)
    sm=ObjectProperty(None)
    ill=ObjectProperty(None)
    choice=0
    def on_enter(self, *args):        
        self.sm.bind(on_press=self.press)
        self.ill.bind(on_press=self.press1)
    def press1(self, *args):
        self.choice=1   
        ill()
    def press(self, *args):
        print(self.choice)
        if self.choice==1:
            with open('illness.csv',newline='',encoding='utf-8') as f:
                rows=csv.reader(f,delimiter=',')
                aw=[]
                for row in rows:
                    aw=aw+[row]
                for i in range(len(aw)):
                    print(aw[i][1])
            input=self.input.text
            def string_similar(s1,s2):
                return difflib.SequenceMatcher(None,s1,s2).quick_ratio()
            value=[]
            for i in range(len(aw)):
                kk=string_similar(input,aw[i][0])
                value=value+[kk]
            max_value=None
            for num in value:
                if(max_value is None or num>max_value):
                    max_value=num
            i=0
            for indexx in value:
                if indexx==max_value:
                    max_index=i
                i=i+1
            print(value)
            print(aw[max_index][1])
            
            kkk = str("i:")+self.input.text
            self.input.text=""
            db.add_hr(self.current,kkk)
            MainRsp.ans =aw[max_index]
            self.choice=0
        def on_leave(self, *args):  
            self.input.text="" 


class MainRsp(Screen):
    n = ObjectProperty(None)
    created = ObjectProperty(None)
    current = ""
    sm=ObjectProperty(None)
    ans=ObjectProperty(None)
    table=ObjectProperty(None)
    databasehr=ObjectProperty(None)
    def on_enter(self, *args):        
        if self.ans!=None:
            print(self.ans)
            self.n.text="可能得到的症狀為"+self.ans[1]
            lll=""
            for i in range(len(self.ans)-2):
                lll=lll+self.ans[i+2]
            kk=lll.split("。")
            #print(lll1)
            listt=[]
            for i in range(len(kk)):
                for ii in range(len(kk[i])//16):
                    li=""
                    for iii in range(16):
                        li=li+kk[i][ii*16+iii]
                    listt=listt+[[li]]
                li=""
                for i4 in range(len(kk[i])%16):
                    li=li+kk[i][i4+((len(kk[i])//16))*16]
                listt=listt+[[li]]
            print(listt)
            self.table=MDDataTable(
            column_data=[("[color=#CD853F]對策[/color]",dp(100))],
            row_data=listt,
            pos_hint={"center_x":0.5,"center_y":0.385},
            size_hint=(0.95,0.55),
            use_pagination=True,
            rows_num=5,
            pagination_menu_height=dp(10),
            )
            self.databasehr.add_widget(self.table)
    def on_leave(self, *args):   
        self.n.text=""
        self.ans=None



class HRecord(Screen):
    databasehr=ObjectProperty(None)
    current = ""
    dhr=[]
    table=ObjectProperty(None)
    rd=ObjectProperty(None)
    def on_enter(self, *args):
        hisrecord = db.get_user(self.current)[2]
        hisrecord = hisrecord.split("/")
        rd=[]
        for i in range(len(hisrecord)):
            k=[hisrecord[i]]
            rd=rd+[k]
        print(rd)
        self.table=MDDataTable(
            column_data=[("[color=#CD853F]Input[/color]",dp(100))],
            row_data=rd,
            pos_hint={"center_x":0.5,"center_y":0.575},
            size_hint=(0.95,0.53),
            use_pagination=True,
            rows_num=4,
            pagination_menu_height=dp(10),
            check=True
        )
        self.table.bind(on_check_press=self.checked)
        self.databasehr.add_widget(self.table)

    def checked(self,instance_table,current_row):
        k=0
        if self.dhr!=[]:
            for i in range(len(self.dhr)):
                if self.dhr[i]==current_row:
                    self.dhr.remove(current_row)
                    k=1
                    break
        if k==0:
            self.dhr=self.dhr+[current_row]

    def removehr(self):
        indextrd=[]
        for i in range(len(self.table.row_data)):
            for j in range(len(self.dhr)):
                if self.table.row_data[i][0]==self.dhr[j][0]:
                    indextrd=indextrd+[i]
        list=[]
        for k in range(len(indextrd)):
            list=list+[self.table.row_data[indextrd[k]]]
        for kk in range(len(list)): 
            self.table.row_data.remove(list[kk])
        self.rd=self.table.row_data
        db.del_hr(self.current,indextrd)
        self.dhr=[]
    def on_leave(self):
        self.dhr=[]
        self.databasehr.remove_widget(self.table)
        self.table=ObjectProperty(None)

class Ds(Screen):
    def on_enter(self, *args):
        pass

class WindowManager(ScreenManager):
    pass

def invalidLogin():
    pop = Popup(title='Invalid Login',
                  content=Label(text='Invalid username or password.'),
                  size_hint=(None, None), size=(320, 300))
    pop.open()
def notr():
    pop = Popup(title='No record',
                  content=Label(text="You haven't measured today!"),
                  size_hint=(None, None), size=(320, 300))
    pop.open()

def usedname():
    pop = Popup(title='Used Name',
                  content=Label(text='Try another name!'),
                  size_hint=(None, None), size=(320, 300))
    pop.open()

def invalidForm():
    pop = Popup(title='Invalid Form',
                  content=Label(text='Please fill in all inputs with valid information.'),
                  size_hint=(None, None), size=(320, 300))

    pop.open()


def ill():
    pop = Popup(title='Notice',
                  content=Label(text="形容玫瑰花外形上的變化或是症狀，\n以便系統判斷可能的病害並給出相對\n應的對策預防以及治療。",font_name="DroidSansFallback.ttf"),
                  size_hint=(None, None), size=(320, 300))

    pop.open()
kv = Builder.load_file("my.kv")
sm = WindowManager()
db = DataBase("users.txt")

screens = [LoginWindow(name="login"), CreateAccountWindow(name="create")
           , MainWindow(name="main"),MainTalk(name="maint"), HRecord(name="hr"),
           Ds(name="ds"),MainRsp(name="rsp")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "login"

class MyMainApp(MDApp):
    def build(self):
        return sm

if __name__ == "__main__":
    MyMainApp().run()
