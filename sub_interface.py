from calendar import c
from statistics import mode
from turtle import back
from appscript import k
import pandas as pd
import random
from gensim.models import KeyedVectors
import MeCab
import os
from natsort import natsorted
import numpy as np
import re
import math as m
import pandas as pd
import random
import numpy as np
import os
from natsort import natsorted
import jaconv
import datetime
import codecs
import requests
from bs4 import BeautifulSoup
import time

global model #binaryファイルのパス
model_path ="bin_file/fasttext_wiki_20191019.bin"
model = KeyedVectors.load_word2vec_format(model_path, binary=True)

global folder_path #名詞リストのパス
folder_path ="model"

global csv_path
csv_path ="csv/"

global joyo_path
joyo_path = csv_path+"joyo_kanji.csv"

#文字型を返す,0 -> ひらがな ,1 -> ひらがな3文字 ,2 -> ○ ◯ ○
def mozi(word,numflag=0,pflag=0):
    
    re_hiragana = re.compile(r'^[あ-ん]+$')
    re_katakana = re.compile('^[\u30A0-\u30FF]+$')
    re_kanji = re.compile(r'^[\u4E00-\u9FD0]+$')
    re_roman = re.compile(r'^[a-zA-Z]+$') #a-z:小文字、A-Z:大文字
    re_suuji = re.compile(r'^[0-9]+$')
    
    dic={"ひらがな":0,"カタカナ":0,"アルファベット":0,"漢字":0,"数字":0}
    
    okikae=""
    i=0
    while i < len(word):
        
        if re_hiragana.match(word[i]): #fullmatch:完全一致
            dic["ひらがな"]+=1
            okikae+="○ "
        
        if re_katakana.match(word[i]): #fullmatch:完全一致
            dic["カタカナ"]+=1
            okikae+="△ "
        
        if re_roman.match(word[i]): #fullmatch:完全一致
            dic["アルファベット"]+=1
        
        if re_kanji.match(word[i]): #fullmatch:完全一致
            dic["漢字"]+=1
            okikae+="□ "
        
        if re_suuji.match(word[i]): #fullmatch:完全一致
            dic["数字"]+=1
        i+=1
        
    string=""
    flag=0
    if dic["ひらがな"]>0:
        string+="ひらがな"
        if(numflag==1):
            string+=str(dic["ひらがな"])+"文字"
        flag=1
        
    if dic["カタカナ"]>0:
        if(flag==1):
            string+=","
        string+="カタカナ"
        if(numflag==1):
            string+=str(dic["カタカナ"])+"文字"
        flag=1
        
    if dic["漢字"]>0:
        if(flag==1):
            string+=","
        string+="漢字"
        if(numflag==1):
            string+=str(dic["漢字"])+"文字"
        
        flag=1
    
    if dic["数字"]>0:
        if(flag==1):
            string+=","
        string+="数字"
        if(numflag==1):
            string+=str(dic["数字"])+"文字"
        flag=1

    if dic["アルファベット"]>0:
        if(flag==1):
            string+=","
        string+="アルファベット"
        if(numflag==1):
            string+=str(dic["アルファベット"])+"文字"
        flag=1
    
    if(numflag==0 or numflag==1):
        if(pflag==1):
            print(string)
        return string
    
    if(numflag==2):
        if(pflag==1):
            print(okikae)
        return okikae

#完全一致する検索ヒット件数を取得
def hit_num(f1,flag=0):
    
    #search_url = f"https://www.google.com/search?q="+"allinurl:ja.wikipedia.org "+f1
    search_url = f"https://www.google.com/search?q="+"\""+f1+"\""
    
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}

    #リクエスト
    response = requests.get(search_url,headers=headers)
    response.encoding = response.apparent_encoding
    site_info = BeautifulSoup(response.text, 'html.parser')

    #抽出
    try:
        total_results_text = site_info.find("div", {"id": "result-stats"}).find(text=True, recursive=False)
        result_num = ''.join([num for num in total_results_text if num.isdigit()])
        if(flag==1):
            print("「"+str(f1)+"」 is ... -> ", end="")
            print(result_num+"("+str(len(result_num))+")")
        
        result_num=len(result_num)
    
    except AttributeError:
        if(flag==1):
            print("「"+str(f1)+"」 is ... -> ", end="")
            print("AttributeError")
        
        result_num="error"
    
    return result_num

#model/のファイルのerror箇所の検索ヒット数を計算する
def hit():
    
    global folder_path
    folderfile = os.listdir(folder_path)
    folderfile = natsorted(folderfile)#数字の順にsort   
    
    i=0
    for each_path in folderfile:
        
        print(each_path)
        
        if(each_path != ".DS_Store" and i >10):
            
            with codecs.open(folder_path+"/"+each_path, "r", "utf-8", "ignore") as f:
                df = pd.read_csv(f)
            
            count=0
            while count<len(df):
                if (mozi(df.iloc[count,1])=="カタカナ" and df.iloc[count,2]=="error"):
                    
                    print("["+str(df.iloc[count,0])+"] ",end="")
                    word=df.iloc[count,1]
                    num = hit_num(word,1)
                    
                    time.sleep(15) #15秒間
                    
                    if num!="error":
                        df.iloc[count,2]=num
                        df.to_csv(folder_path+"/"+each_path,index=0)
                    else:
                        break#1重目のループを抜ける
                count+=1
                
            else:
                continue
            break #2重目のループを抜ける
        i+=1
        
    
    print("終了")

#読みを返す
def yomi(text,flag=0):
    
    yomikata = text
    
    if(mozi(str(text))=="漢字"):
        
        tagger = MeCab.Tagger() #mecab本体とtextをタグ付けする命令
        node = tagger.parseToNode(text)
        count=0
        while node:
            if count == 0:
                try:
                    yomikata = node.feature.split(",")[6]
                except:
                    yomikata = ""
                count+=1
            else:
                try:
                    yomikata += node.feature.split(",")[6]
                except:
                    yomikata += ""

            node = node.next
        
        yomikata = yomikata.strip("*")
    
    #カタカナをひらがなへ
    if(mozi(yomikata)=="カタカナ"):
        yomikata = jaconv.kata2hira(yomikata)
    
    if(flag==1):
        print(yomikata)
    
    return yomikata

#検索単語が常用漢字かチェック
def check_joyo(search_word,pflag=0):
    
    global joyo_path
    with codecs.open(joyo_path, "r", "utf-8", "ignore") as f:
        df = pd.read_csv(f,header=0)
    
    i=0
    flag=0
    j=0
    while j < len(search_word):
        while i < len(df):
            if(search_word[j] == df.iloc[i,0]):
                flag=1
                break
            i+=1
        j+=1
        
    if(pflag==1):
        if(flag==1):
            print("(常用漢字)")
        else:
            print("(常用漢字ではない)")

    return flag

#文字ヒット率を返す
def mozi_hit_per(hint_kanji,main,flag=0):
    
    hit=0
    i=0
    while i<len(hint_kanji):#リサイクリング
        j=0
        while j<len(main):#リサイクル
            if(hint_kanji[i]==main[j]):
                hit+=1
            j+=1
        i+=1
    
    if(len(hint_kanji)>=len(main)):
        length=len(hint_kanji)
    else:
        length=len(main)
    
    per = round(100*((hit/length)))
    if(flag==1):
        print(per)
    
    return(per)

#受け取った2単語の類似度を計算
def cos_ruiji(f1,f2,flag=0):
    
    try:
        vector1 = model[f1]
        vector2 = model[f2]

        #内積と大きさの初期化
        AB = 0
        A = 0  
        B = 0  

        #300次元でcosの値を求める
        for i in range(300):
            AB += vector1[i]*vector2[i]
            A += vector1[i]*vector1[i]
            B += vector2[i]*vector2[i]

        cos = round(AB/(m.sqrt(A)*m.sqrt(B)),2)

        if(flag==1):
            print(cos)

        #角度を求める
        return cos
    
    except:
        return 0

# 品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
# node.feature.split(",") = ['名詞', '固有名詞', '人名', '姓', … ]
#['名詞', '普通名詞', 'サ変可能', … ]
#['名詞', '数詞', '*', '*', '*', '*']
def mecab(text,num=-1,flag=0):
    
    tagger = MeCab.Tagger("") #mecab本体とtextをタグ付けする命令
    node = tagger.parseToNode(text)

    count=0
    while node:
        if count == 1:
            if(num!=-1):
                a = node.feature.split(",")[num]
            else:
                a=node.feature.split(",")
        count+=1
        node = node.next
    if(flag==1):
        print(a)
    
    return(a)

#model内の指定した番号に登録されている単語を返す。
def model_word(i):
    
    list = model.most_similar(model[i],topn=1)#model[0]の類似度に近い単語を1つ出力
    word=(list[0][0])
    
    return word

#指定した階層の中からcsvファイルを開き単語をランダムで出力
def random_word(pflag=0):

    global folder_path
    folderfile = os.listdir(folder_path)
    folderfile = natsorted(folderfile)#数字の順にsort   

    flag=0
    while flag==0:#文字が4文字以下
        
        """
        j = random.randint(0,3)
        if(j==0 or j==1 or j==2):
            i=random.randint(0,int((len(folderfile)-1)/2))
        if(j==3):
            i=random.randint(int((len(folderfile)-1)/2)+1,len(folderfile)-1)
        """
        
        i=random.randint(1,len(folderfile)-1) #0は.DS_Store
        
        count=0
        for each_path in folderfile:
            if(count==i):
                with codecs.open(folder_path+"/"+each_path, "r", "utf-8", "ignore") as f:
                    df = pd.read_csv(f,header=0)
            count+=1

        i=random.randint(0,len(df)-1)
        word=df.iloc[i,1]
                
        if(len(word)<4):
            if(mozi(word)=="ひらがな" or mozi(word)=="カタカナ"):
                flag=1
            if(mozi(word)=="漢字"):
                if(check_joyo(word)):
                    flag=1

    if(pflag==1):
        print("\n[正解単語]",end="")
        print(word)
        print("桁数:",end="")
        print(df.iloc[i,2],end="\n\n")
    
    return word

#model内からの削除
def del_word(search_word=""):

    if search_word !="":
        global folder_path
        folderfile = os.listdir(folder_path)
        folderfile = natsorted(folderfile)#数字の順にsort  

        for each_path in folderfile:
            
            with codecs.open(folder_path+"/"+each_path, "r", "utf-8", "ignore") as f:
                df = pd.read_csv(f,header=0)

            
            i=0
            while i<len(df):
                
                word=df.iloc[i,1]
                
                if(word == search_word):
                    df = df.drop(i)
                    df = df.reset_index(drop=True)
                    df.to_csv(folder_path+"/"+each_path,index=False)
                    print(str(each_path)+" "+str(i)+"行目"+str(df.iloc[i,0])+"番",end="")
                    print("「"+str(search_word)+"」を削除しました")
                    break
                i+=1
            
            else:
                continue
            break #2重目のループを抜ける

#dict構造からkeyを取り出す
def take_key(dic,i):
    
    dic_list = list(dic.keys())
    word = dic_list[i]
    
    return word #keyを返す

#dict構造からvalueを取り出す
def take_value(dic,i):
    
    dic_list = list(dic.keys())
    word = dic_list[i]
    num = dic[word]
    
    return num #valueを返す

#dict構造内の全てのvalueの平均をとる
def average_value(dic):
    
    ave=0
    
    i=0
    while i <len(dic):
        
        value = take_value(dic,i)
        ave += value
        
        i+=1
    
    ave = int( ave / len(dic) )
    
    return ave

#現在の時刻を返す
def ima():
    
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    # YYYYMMDDhhmmss形式に書式化
    d = now.strftime('%Y%m%d%H%M%S')
    #print(d)  # 20211104173728
    d = f'{now:%Y%m%d%H%M%S}'  # f文字列
    d = format(now, '%Y%m%d%H%M%S')  # format関数
    d = '{:%Y%m%d%H%M%S}'.format(now)  # 文字列のformatメソッド
    #print(d)  # 20211104173728
    
    return d

#ヒント単語のリストを入れて、平均ベクトルを返す。
def ave_vec(hint_list,pflag=0):
    
    vector = np.zeros((300,),dtype="float32")#特徴ベクトルの入れ物を初期化
    ave_vec = np.zeros((300,),dtype="float32")#特徴ベクトルの入れ物を初期化
    
    i=0
    while i<len(hint_list):
        vector = model[hint_list[i]]
        ave_vec = np.add(ave_vec,vector)
        i+=1
    
    ave_vec = np.divide(ave_vec,len(hint_list))
    
    return ave_vec

############################################
############################################

#正解単語とキーワードの制約
def contract1(parent,hint,p_flag=0):
    
    #読み
    if(yomi(parent) == yomi(hint)): #正解単語->"ウサギ",ヒント単語->"兎"を避ける
        if(p_flag==1):
            print("<p-k> "+str(parent)+"&"+str(hint),end=" -> ")
            print("読み一致")
        return 1
    
    #包含
    if(parent in hint or hint in parent):
        if(p_flag==1):
            print("<p-k> "+str(hint)+"&"+str(parent),end=" -> ")
            print("包含")
        return 1

    #文字ヒット率
    if(mozi_hit_per(hint,parent)>=50):
        if(p_flag==1):
            print("<p-k> "+str(hint)+"&"+str(parent),end=" -> ")
            print("文字ヒット率50以上")
        return 1
    
    #if(p_flag==1):
        #print(str(hint)+"&"+str(parent),end=" -> ")
        #print("問題なし")
    
    if stop_check(hint):
        return 1
    
    return 0

#キーワード同士の制約（0問題なし、1問題あり）
def contract2(hint1,hint2,p_flag=0):
    
    #読み
    if(mozi(hint1)!=mozi(hint2)):
        if(yomi(hint1) == yomi(hint2)): #正解単語->"ウサギ",ヒント単語->"兎"を避ける
            if(p_flag==1):
                print("<k-k> "+str(hint1)+"&"+str(hint2),end=" -> ")
                print("読み一致")
            return 1

    #包含
    if(hint2 in hint1 or hint1 in hint2):
        if(p_flag==1):
            print("<k-k> "+str(hint1)+"&"+str(hint2),end=" -> ")
            print("包含")
        return 1
    
    #文字ヒット率
    if(mozi_hit_per(hint1,hint2)>=50):
        if(p_flag==1):
            print("<k-k> "+str(hint1)+"&"+str(hint2),end=" -> ")
            print("文字ヒット50以上")
        return 1

    cos=model.similarity(hint1,hint2)
    if(cos>0.60):
        if(p_flag==1):
            print("<k-k> "+str(hint1)+"&"+str(hint2),end=" -> ")
            print("類似度0.60以上")
        return 1

    return 0

#解答例の単語同士の制約（0問題なし、1問題あり）
def contract3(ans1,ans2,p_flag=0):
    
    #読み
    if(mozi(ans1)!=mozi(ans2)):
        if(yomi(ans1) == yomi(ans2)): #正解単語->"ウサギ",ヒント単語->"兎"を避ける
            if(p_flag==1):
                print("<a-a> "+str(ans1)+"&"+str(ans2),end=" -> ")
                print("読み一致")
            return 1

    #包含
    if(ans2 in ans1 or ans1 in ans2):
        if(p_flag==1):
            print("<a-a> "+str(ans1)+"&"+str(ans2),end=" -> ")
            print("包含")
        return 1
    
    #文字ヒット率
    if(mozi_hit_per(ans1,ans2)>50):
        if(p_flag==1):
            print("<a-a> "+str(ans1)+"&"+str(ans2),end=" -> ")
            print("文字ヒット50より大きい")
        return 1

    cos=model.similarity(ans1,ans2)
    if(cos>0.70):
        if(p_flag==1):
            print("<a-a> "+str(ans1)+"&"+str(ans2),end=" -> ")
            print("類似度0.70以上")
        return 1

    return 0

#禁止ワードが入っていないか
def stop_check(hint,pflag=0):
    
    stop_list=["上","下","右","左","北","東","南","西","・","色"]
    for i in stop_list:
        if(i in hint):
            if(pflag==1):
                print("<p>"+str(hint),end=" -> ")
                print("禁止ワードが入っている")
            return 1
    
    return 0

#ヒント単語のリストを入れて、平均単語を返す。
def ave_word(hint_list,pflag=0):
    
    vector = np.zeros((300,),dtype="float32")#特徴ベクトルの入れ物を初期化
    ave_vec = np.zeros((300,),dtype="float32")#特徴ベクトルの入れ物を初期化
    
    i=0
    while i<len(hint_list):
        vector = model[hint_list[i]]
        ave_vec = np.add(ave_vec,vector)
        i+=1
    
    ave_vec = np.divide(ave_vec,len(hint_list))

    most_list = model.most_similar(ave_vec)#model[0]の類似度に近い単語を1つ出力
    
    ave_list=[]
    
    count=0
    for i in most_list:
        flag=0
        for j in hint_list:
            if(contract1(i[0],j)):#問題ありなら1が帰ってくる
                flag=1
            if(i[0] == j):
                flag=1
        if(flag==0):
            ave_list.append(i[0])
            count+=1
    
    if(pflag==1):
        print("解答例:",end="")
        print(ave_list)
    
    return ave_list

# ['府','地元','自転車'] -> 府, 地元, 自転車
def clean(list):
    
    st = str(list)
    st = st.strip("[ ]")
    st = st.replace("\"","")
    st = st.replace("\'","")
    
    return st

#点数化
def scoring(ans,hint_list,pflag=0):
    
    count=0
    total_cos=1
    hint_list = list(hint_list)
    hint_num = len(hint_list)
    
    cos_list=[]
    
    for i in hint_list:
        cos = model.similarity(i,ans)
        
        if(pflag==1):
            print("cos:"+str(round(cos,2)))
        
        total_cos = total_cos * cos
        
        cos = round(cos,2)
        cos_list.append(str(cos))
        
        count+=1
    
    if(pflag==1):
        print("total_cos:"+str(round(total_cos,2)))
    
    if(hint_num==2):
        score=47.05*total_cos-4.23
    if(hint_num==3):
        score=71.94*total_cos-1.94
    if(hint_num==4):
        score=119.9*total_cos-0.97

    score = round(score,1)
    
    if(score>10):
        score=10.0
    if(score<0):
        score=0.0
    
    pack = []
    pack.append(score)
    pack.append(cos_list)
    
    return pack

#解答例を作成する
def creating_anslist(hint_list,pflag=0):
    
    ans_list=[]
    ave_list = ave_word(hint_list)
        
    for i in ave_list:
        
        if(i not in hint_list):
            
            if (mecab(i,0)=="名詞" and not (mozi(i)=="カタカナ" and len(i)>10) and not mozi(i)=="アルファベット"):
                
                score_pack = scoring(i,hint_list)
                score = score_pack[0]
                
                if(score > 9.0):
                    if not stop_check(i):
                        
                        flag=0
                        for j in ans_list:
                            if contract3(i,j,pflag): #0なら問題なし、1なら問題あり
                                flag=1
                                break
                        
                        if flag==0:
                            ans_list.append(i)
                        
                    if(len(ans_list)>=5):
                        break
    
    if(len(ans_list)<3):
        
        global folder_path
        folderfile = os.listdir(folder_path)
        folderfile = natsorted(folderfile)#数字の順にsort  

        for each_path in folderfile:
            
            with codecs.open(folder_path+"/"+each_path, "r", "utf-8", "ignore") as f:
                df = pd.read_csv(f,header=0)

            i=0
            while i < len(df):
            
                word = str(df.iloc[i,1])
                
                if(word not in hint_list):
                    
                    score_pack = scoring(i,hint_list)
                    score = score_pack[0]
                    
                    if(score > 9.0 and word not in ans_list):
                        ans_list.append(word)
                    
                    if(len(ans_list)>=3):
                        break
                
                i+=1
        
    while len(ans_list)>3:
        i=random.randint(0,len(ans_list)-1)
        del ans_list[i]
    
    if(pflag==1):
        print("解答例"+str(ans_list)+"\n")
    
    return ans_list

#検索ヒット数を用いて問題の難易度を推定する
def checking_anslist(hint_list,pflag=0):
    
    ans_list=[]
    ave_list = ave_word(hint_list)#
    
    for i in ave_list:
        
        if(i not in hint_list):
            
            if (mecab(i,0)=="名詞" and not (mozi(i)=="カタカナ" and len(i)>10) and not mozi(i)=="アルファベット"):
                
                score_pack = scoring(i,hint_list)
                score = score_pack[0]
                
                if(score > 9.0):
                    if not stop_check(i):
                        ans_list.append(i)
        
    global folder_path
    folderfile = os.listdir(folder_path)
    folderfile = natsorted(folderfile)#数字の順にsort  

    for each_path in folderfile:
        
        with codecs.open(folder_path+"/"+each_path, "r", "utf-8", "ignore") as f:
            df = pd.read_csv(f,header=0)

        i=0
        while i < len(df):
        
            word = str(df.iloc[i,1])
            
            if(word not in hint_list):
                
                score_pack = scoring(word,hint_list)
                score = score_pack[0]
                
                if(score > 9.0 and word not in ans_list):
                    ans_list.append(word)
            
            i+=1
    
    if(pflag==1):
        print(len(ans_list))
    
    return ans_list

#正解単語から類似度40以上のヒント単語をdictに格納する
def bloading(hint_num,pflag=0):
    
    flag1=0
    while flag1==0:
        
        anki_list=[]
        dic={}
        
        parent="千利休"
        #parent = random_word(pflag)#正解単語
        
        global folder_path
        folderfile = os.listdir(folder_path)
        folderfile = natsorted(folderfile)#数字の順にsort  

        for each_path in folderfile:
            
            with codecs.open(folder_path+"/"+each_path, "r", "utf-8", "ignore") as f:
                    df = pd.read_csv(f,header=0)

            i=0
            while i < len(df):
                
                #ヒント候補単語
                hint = str(df.iloc[i,1])
                
                cos=model.similarity(parent,hint)
                
                if(cos>0.5 and cos!=1 and len(hint)!=1):
                    
                    #正解単語との制約------------------------
                    flag= contract1(parent,hint,pflag) #1は問題あり、0は問題なし
                    
                    #ヒント単語同士の制約------------------------
                    if(flag==0):
                        for anki_word in anki_list:
                            flag = contract2(anki_word,hint,pflag) #1は問題あり、0は問題なし
                            if(flag==1):
                                break
                    #-----------------------------------------
                    
                    if(flag==0):
                        dic[hint]=cos
                        anki_list.append(hint)
                
                i+=1
        
        #key降順ソート
        dic = sorted(dic.items(),key=lambda x:x[1],reverse=True)
        dic = dict((x, y) for x, y in dic)
        
        while len(dic)>hint_num:
            key = take_key(dic,-1)
            del dic[key]
        
        if (len(dic)==hint_num):
            
            hint_list = list(dic.keys()) #listというnameをつけないように
            
            if pflag==1:
                print("\n問題"+str(hint_list)+"\n")

            ans_list = creating_anslist(hint_list,pflag)
            
            max=0
            min=100
            for i in ans_list:
                score_pack = scoring(i,hint_list)
                score = score_pack[0]
                if(score > max):
                    max = score
                if(score < min):
                    min = score
            if(max==10):
                if (min>=8):
                    if(len(ans_list)>=2):
                        flag1=1
                    else:
                        print("The number of answer_list is insufficient ……")
                else:
                    print("Lowest score on the ans_list is 8 or less ……")
            else:
                print("Highest score on the ans_list is not 10 ……")
        else:
            print("The number of hint_list is insufficient ……")
    
    print("creating_problem of "+str(hint_num)+" keyword")
    
    #"""
    #while_flag終わり
    global csv_path
    with codecs.open(csv_path+"mondai"+str(hint_num)+".csv", "r", "utf-8", "ignore") as f:
        mondai_df = pd.read_csv(f,header=0)

    i = len(mondai_df)
    a=0
    mondai_df.loc[i]=0
    for word in hint_list:
        mondai_df.iloc[i,a]=word
        a+=1
    a=4
    for word in ans_list:
        mondai_df.iloc[i,a]=word
        a+=1
    
    mondai_df.to_csv(csv_path+"mondai"+str(hint_num)+".csv",index=0)
    
    return hint_list

#modelファイル内から該当する単語を表示する
def model_search():
    
    global folder_path
    folderfile = os.listdir(folder_path)
    folderfile = natsorted(folderfile)#数字の順にsort  
    count=0
    for each_path in folderfile:
        
        if each_path != ".DS_Store" and count>=0:
        
            list=[]
                
            with codecs.open(folder_path+"/"+each_path, "r", "utf-8", "ignore") as f:
                df = pd.read_csv(f,header=0)
            
            i=0
            while i < len(df):
                
                word = df.iloc[i,1]
                
                #######################
                #ここから検索内容の記入
                
                if(word == "類聚"):
                    print(each_path,end="の")
                    print(str(i)+"行目")
                    break
                
                """
                if word.startswith("テレビ"):
                    list.append(word)
                
                
                if("銀行"in word or "大学" in word):
                    list.append(word)
                
                if(word[-1]=="っ"):
                    list.append(word)
                            
                if(mozi(word)=="漢字" and not check_joyo(word)):
                    list.append(word)
                
                if(mecab(word,2)=="地名" and count>10):
                    list.append(word)

                if("・" in word):
                    list.append(word)
                
                
                if(mozi(word)=="カタカナ" and len(word)>7):
                    list.append(word)
                """
                
                i+=1
        count+=1
            
    print("")
    print(list)
    
    print("終了")

#model.similarity(f1,f2)の実際のコード
def sim(f1,f2):

    StA = f1 #1単語目
    StB = f2 #2単語目

    #StA = "飲料" #1単語目
    #StB = "飲み物" #2単語目


    wordA = model[StA]
    wordB = model[StB]


    #内積と大きさの初期化
    AB = 0
    A = 0  
    B = 0  

    #300次元でcosの値を求める
    for i in range(300):
        AB += wordA[i]*wordB[i]
        A += wordA[i]*wordA[i]
        B += wordB[i]*wordB[i]

    cos = int(100*(round(AB/(m.sqrt(A)*m.sqrt(B)),2)))

#modelファイル内の不適切な単語を削除する
del_list=[]
for i in del_list:
    try:
        del_word(i)
    except IndexError:
        print("")
        