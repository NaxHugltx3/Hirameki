import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tk_font
from appscript import k
import pandas as pd
from gensim.models import KeyedVectors
from calendar import c
import time
import sub_interface as sub
import os
from natsort import natsorted
import random

#fastTextの日本語の学習済み単語ベクトル
model_path ="bin_file/fasttext_wiki_20191019.bin"
model = KeyedVectors.load_word2vec_format(model_path, binary=True)

global LOG_parh
LOG_path = "LOG"

global csv_path
csv_path ="csv"

#回答履歴
log_format_path = csv_path+"/log.csv"

global prior_mondai_path
prior_mondai_path = csv_path+"/prior_mondai.csv"

global after_mondai_path
after_mondai_path = csv_path+"/after_mondai.csv"

global font_size
font_size=18

global border
border = 70

#問題を入れ替える関数
def passing():
    
    global pass_num
    
    if pass_num>=0:
        pass_num-=1
    
    if(pass_num>=0):
        global csv_path
        mondai_df = pd.read_csv(csv_path+"/mondai"+str(hint_num)+".csv",header=0)
        
        global hint_list
        hint_list =[]
        j = random.randint(0,len(mondai_df)-1)
        i=0
        while i<hint_num:
            hint_list.append(mondai_df.iloc[j,i])
            i+=1
        
        global ans_list
        ans_list=[]
        i=4
        while i<7:
            if(mondai_df.iloc[j,i] != "0"):
                ans_list.append(mondai_df.iloc[j,i])
            i+=1

        mondai_df = mondai_df.drop(mondai_df.index[j],axis=0) #ここでdfからmainの行を削除する(indexは数字)
        mondai_df = mondai_df.reset_index(drop=True) #index番号の振り直し(元のindexは削除され残らない)
        mondai_df.to_csv(csv_path+"/mondai"+str(hint_num)+".csv",index=0)

        global printing_ans_list #(10点)あり
        printing_ans_list=[]
        for i in ans_list:
            score_pack = sub.scoring(i,hint_list)
            score = score_pack[0]
            printing_ans_list.append(str(i)+"("+str(score)+"点)")
        
        
        global mondai_frame
        mondai_frame.destroy()
        mondai_gamen()
    else:
        
        mondai_frame.destroy()
        mondai_gamen()

        label = tk.Label(mondai_frame,bg=bg_color, text="※もうパスはできません。",font=font5)
        label.pack()

def mondai_gamen():
    
    global mondai_frame
    mondai_frame = tk.Frame(root,bg=bg_color)
    mondai_frame.pack(fill='both', padx=20,pady=20)
    
    #レベルと何問目
    global n
    global last_n
    global total_score
    global ver 

    if ver ==0 or ver ==2:
        label = tk.Label(mondai_frame,bg=bg_color,justify="center", text=str(n)+" / "+str(last_n)+" 問目",font=font1)
        label.pack(pady=5)

    if ver ==1:
        label = tk.Label(mondai_frame,bg=bg_color,justify="center", text=str(n)+" / "+str(last_n)+" 問目 (現在"+str(total_score)+"点)",font=font1)
        label.pack(pady=5)
    
    
    #問題文作成----------------------------------------------------------
    
    global hint_list
    label = tk.Label(mondai_frame,bg=bg_color,fg=fg_color,text=sub.clean(hint_list),font=font2)
    label.pack()
    
    global font5
    label = tk.Label(mondai_frame,bg=bg_color, text="と共通に関係する単語を解答してください",font=font1)
    label.pack()
    
    """
    if ver ==1:
        
        label = tk.Label(mondai_frame,bg=bg_color, justify="center", text="\n[解答例]",font=font1)
        label.pack()
        
        label = tk.Label(mondai_frame,bg=bg_color, justify="center", text="※ □=漢字,○=ひらがな,△=カタカナ",font=font5)
        label.pack()     

        global ans_list
        for i in ans_list:
            score_pack = sub.scoring(i,hint_list)
            score = score_pack[0]
            label = tk.Label(mondai_frame,
                            bg=bg_color,
                            justify="center",
                            text=str(sub.mozi(i,2))+" -> "+str(score)+"点",
                            font=font1)
            label.pack(pady=1)
        """
    
    global entry
    entry = tk.Entry(mondai_frame,bg=bg_color,
                    font=font2,justify="center",
                    relief="groove")
    entry.pack(pady=10)
    
    # Entryの値を削除してみる
    entry.delete(0, tk.END)
    
    export_button = ttk.Button(mondai_frame,default="active", text='解答する',width=20,command=kaitou_gamen)
    export_button.pack(pady=10)
    
    if ver ==1:
        global pass_num
        if(pass_num<0):
            pass_num=0
        export_button = ttk.Button(mondai_frame,default="active", text='パスする (残り'+str(pass_num)+"回)",width=20,command=passing)
        export_button.pack()
    
    # 時間計測開始
    global time_sta
    global time_flag
    if(time_flag):
        time_sta = time.time()
        print("time start")
        time_flag=False
    
    root.geometry("650x375+25+50") # アプリの画面サイズ（横px × 縦px）

def kaitou_gamen():
    
    global entry
    ans = entry.get()
    
    #entry.getしてから
    mondai_frame.destroy()
    
    flag=0
    
    if(ans not in model):
        flag=1

    global hint_list
    for i in hint_list:
        if(i==ans):
            flag=2
    
    if flag==0:
        
        # 時間計測終了
        time_end = time.time()
        print("time stop")

        # 経過時間（秒）
        global time_sta
        tim = time_end- time_sta
        print("time:"+str(tim))
        
        global ver
        if ver ==1:
            
            global kaitou_frame
            kaitou_frame = tk.Frame(root,bg=bg_color)
            kaitou_frame.pack(fill='both', padx=20,pady=20) #設置
        
            global n
            global last_n
            label = tk.Label(kaitou_frame,bg=bg_color, text=str(n)+" / "+str(last_n)+" 問目",font=font1)
            label.pack()
        
        score_pack = sub.scoring(ans,hint_list,1)
        score = score_pack[0]
        cos_list = score_pack[1]

        global total_score
        total_score += score
        total_score = round(total_score,1)
        
        if ver==1:
            
            global font2
            
            label = tk.Label(kaitou_frame,bg=bg_color, text=str(score)+"点ゲット!!  (現在"+str(total_score)+"点)",font=font2)
            label.pack(pady=5)
            #"""
            string=""
            m=0
            for i in cos_list:
                if m == 1:
                    string+=" × "
                string+=str(i)
                m=1
            
            global font5
            
            label = tk.Label(kaitou_frame,bg=bg_color, text="\n"+"[ユーザの解答] "+str(ans),font=font5)
            label.pack()
            
            #label = tk.Label(kaitou_frame,bg=bg_color, text="関連単語 "+str(sub.ave_word([ans])),font=font5)
            #label.pack()
            
            label = tk.Label(kaitou_frame,bg=bg_color,text="\nキーワード "+str(hint_list)+" とのcos類似度",font=font5)
            label.pack()

            label = tk.Label(kaitou_frame,bg=bg_color, text=string,font=font5)
            label.pack()
            #"""
            
            label = tk.Label(kaitou_frame,bg=bg_color, text="\n【解答例】",font=font1)
            label.pack()
            
            global printing_ans_list
            label = tk.Label(kaitou_frame,bg=bg_color,fg=fg_color,text=sub.clean(printing_ans_list)+" など",font=font3)
            label.pack()

            if n<last_n:
                change_button = ttk.Button(kaitou_frame,default="active",text="次の問題へ",width=20, command=gate_2)
                change_button.pack(pady=20)
                
            if n==last_n:
                change_button = ttk.Button(kaitou_frame,default="active",text="結果画面へ",width=20, command=gate_2)
                change_button.pack(pady=20)
            
            root.geometry("650x375+25+50") # アプリの画面サイズ（横px × 縦px）
        
        global result_list
        result_list.append(str(hint_list)+" ->  "+str(ans)+" ("+str(score)+"点) , "+str(printing_ans_list[0])+"など")
        
        global log_df
        global ans_list
        
        i = len(log_df)
        log_df.loc[i]=0
        log_df.iloc[i,0]=str(hint_list)
        log_df.iloc[i,1]=str(ans_list)
        log_df.iloc[i,2]=ans
        log_df.iloc[i,3]=score
        log_df.iloc[i,4]=round(tim,2)
        global save_path
        log_df.to_csv(save_path,index=0)
        
        if(ver ==0 or ver ==2):
            gate_2()
    
    #modelにない単語を入力したとき
    if(flag==1):
        mondai_gamen()
        
        label = tk.Label(mondai_frame,bg=bg_color, text="※その単語は登録されていません。",font=font5)
        label.pack()
    
    if(flag==2):
        mondai_gamen()
        
        label = tk.Label(mondai_frame,bg=bg_color, text="※キーワードと同じ単語です。",font=font5)
        label.pack()

def result_gamen():
    
    global result_frame
    result_frame = tk.Frame(root,bg=bg_color)
    result_frame.pack(fill='both', padx=20,pady=20)
    
    global ver
    global total_score
    global last_n
    
    if ver==0:
        label2 = tk.Label(result_frame,bg=bg_color, text="初回テストは終了です",font=font1)
        label2.pack()
        
        label2 = tk.Label(result_frame,bg=bg_color, text="合計"+str(total_score)+"点",font=font1)
        label2.pack()


    if ver==2:
        label2 = tk.Label(result_frame,bg=bg_color, text="最終テストは終了です",font=font1)
        label2.pack()
        
        label2 = tk.Label(result_frame,bg=bg_color, text="合計"+str(total_score)+"点",font=font1)
        label2.pack()

    if ver==1:
        global border
        if(total_score>=border):
            
            label = tk.Label(result_frame,bg=bg_color, text="最終結果 : 合格！！",font=font4)
            label.pack()

            label2 = tk.Label(result_frame,bg=bg_color, text="合計"+str(total_score)+"点",font=font1)
            label2.pack()

            label2 = tk.Label(result_frame,bg=bg_color, text="次のレベルに進んでください",font=font1)
            label2.pack()
        
        else:
            label = tk.Label(result_frame,bg=bg_color, text="最終結果 : 不合格……",font=font4)
            label.pack()

            label2 = tk.Label(result_frame,bg=bg_color, text="合計"+str(total_score)+"点",font=font1)
            label2.pack()

            label2 = tk.Label(result_frame,bg=bg_color, text="もう一度同じレベルにチャレンジしてください",font=font1)
            label2.pack()

    
    label = tk.Label(result_frame,fg=fg_color,bg=bg_color, text=" [問題] -> ユーザの解答 , 解答例 ",font=font3)
    label.pack(pady=5)

    global result_list
    for i in result_list:
        label = tk.Label(result_frame,fg=fg_color,bg=bg_color, text=i,font=font3)
        label.pack(pady=5)
    
    export_button = ttk.Button(result_frame,default="active",text='スタート画面に戻る',width=20,command=gate_3)
    export_button.pack(pady=10)
    
    global log_df
    global value
    i = len(log_df)
    log_df.loc[i]=0
    log_df.iloc[i,2]="[合計点]"
    log_df.iloc[i,3]=total_score
    global save_path
    log_df.to_csv(save_path,index=0)

    global login_name
    global clear_df
    global clear_path
    
    a=0
    if ver ==1:
        if(total_score>=border):#合格なら
            clear_df.iloc[0,value]="clear"
            clear_df.to_csv(clear_path,index=0)
            
            if clear_df.iloc[0,3]=="clear":
                ver =2
                a=1
    
    if ver ==0 and a==0:
        clear_df.iloc[0,0]="clear"
        clear_df.to_csv(clear_path,index=0)
        ver=1
    
    if ver ==2 and a==0:
        clear_df.iloc[0,4]="clear"
        clear_df.to_csv(clear_path,index=0)
        ver=1
    
    if(last_n>5):
        root.geometry("650x600+25+50") # アプリの画面サイズ（横px × 縦px）

#start_frame -> mondai_frame
def gate_1():

    global pass_num
    pass_num = 3
    global ver
    global hint_num
    global hint_list
    global ans_list #(10点)なし

    global log_df
    log_df = pd.read_csv(log_format_path,header=0)

    global dt_now
    dt_now = sub.ima()
    
    global save_path

    if ver ==0 or ver==2:
        if ver ==0:
            save_path="LOG/"+str(login_name)+"/"+"(初回)"+str(dt_now)+".csv"
        if ver ==2:
            save_path="LOG/"+str(login_name)+"/"+"(最終)"+str(dt_now)+".csv"
        
        hint_num=3
        
        global mondai_df
        global n
        
        if(ver==0):
            global prior_mondai_path
            mondai_df = pd.read_csv(prior_mondai_path,header=0)
        
        if(ver==2):
            global after_mondai_path
            mondai_df = pd.read_csv(after_mondai_path,header=0)
        
        hint_list=[]
        i=0
        while i < hint_num:
            hint_list.append(mondai_df.iloc[n-1,i])
            i+=1
        
        ans_list=""

    if ver ==1:
        
        global var
        global value
        
        value = var.get()
        
        if(value==1):
            hint_num=2
        if(value==2):
            hint_num=3
        if(value==3):
            hint_num=4
        
        global csv_path
        mondai_df = pd.read_csv(csv_path+"/mondai"+str(hint_num)+".csv",header=0)
        
        hint_list =[]
        
        #j = random.randint(0,len(mondai_df)-1) 
        j=0 #上から順にとる
        
        i=0
        while i<hint_num:
            hint_list.append(mondai_df.iloc[j,i])
            i+=1
        
        ans_list=[]
        i=4
        while i<7:
            if(mondai_df.iloc[j,i] != "0"):
                ans_list.append(mondai_df.iloc[j,i])
            i+=1

        mondai_df = mondai_df.drop(mondai_df.index[j],axis=0) #ここでdfからmainの行を削除する(indexは数字)
        mondai_df = mondai_df.reset_index(drop=True) #index番号の振り直し(元のindexは削除され残らない)
        mondai_df.to_csv(csv_path+"/mondai"+str(hint_num)+".csv",index=0)

        global printing_ans_list #(10点)あり
        printing_ans_list=[]
        for i in ans_list:
            score_pack = sub.scoring(i,hint_list)
            score = score_pack[0]
            printing_ans_list.append(str(i)+"("+str(score)+"点)")
    
        global LOG_path
        save_path=LOG_path+"/"+str(login_name)+"/"+"(レベル"+str(value)+")"+str(dt_now)+".csv"
    
    log_df.to_csv(save_path,index=0)
    
    global time_flag
    time_flag = True
    
    start_frame.destroy()
    mondai_gamen()

#kaitou_gamen -> mondai_frame
def gate_2():
    
    global ver
    if(ver==1):
        kaitou_frame.destroy()
    
    global n
    n+=1
    global last_n
    
    global hint_list
    global ans_list
    global hint_num

    if n<=last_n:
        
        if ver == 0 or ver ==2:
            global mondai_df
            hint_list=[]
            i=0
            while i < hint_num:
                hint_list.append(mondai_df.iloc[n-1,i])
                i+=1

        if ver == 1:
            global csv_path
            mondai_df = pd.read_csv(csv_path+"/mondai"+str(hint_num)+".csv",header=0)
            
            hint_list =[]
            #j = random.randint(0,len(mondai_df)-1)
            j=0
            
            i=0
            while i<hint_num:
                hint_list.append(mondai_df.iloc[j,i])
                i+=1
            
            ans_list=[]
            i=4
            while i<7:
                if(mondai_df.iloc[j,i] != "0"):
                    ans_list.append(mondai_df.iloc[j,i])
                i+=1
            
            mondai_df = mondai_df.drop(mondai_df.index[j],axis=0) #ここでdfからmainの行を削除する(indexは数字)
            mondai_df = mondai_df.reset_index(drop=True) #index番号の振り直し(元のindexは削除され残らない)
            mondai_df.to_csv(csv_path+"/mondai"+str(hint_num)+".csv",index=0)
            
            global printing_ans_list #(10点)あり
            printing_ans_list=[]
            for i in ans_list:
                score_pack = sub.scoring(i,hint_list)
                score = score_pack[0]
                printing_ans_list.append(str(i)+"("+str(score)+"点)")
        
        global time_flag
        time_flag = True
        
        mondai_gamen()
    
    if n>last_n:
        result_gamen()

#result_gamen -> start_gamen
def gate_3():
        
    result_frame.destroy()
    root.geometry("650x450+25+50")
    start_gamen()

#スタート画面
def start_gamen():
    
    global login_name
    #root.title("ユーザ:"+str(login_name)) # アプリの名前
    
    #現在の設問数
    global n
    n=1
    
    #何問解くか
    global last_n
    last_n = 10
    
    #スコアの合計点
    global total_score
    total_score = 0
    
    #結果画面にこれまでの問題と答えを入れる
    global result_list
    result_list =[]
    
    #ボタンやラベルをまとめたフレーム
    global start_frame
    start_frame = tk.Frame(root,bg=bg_color) #第一引数に親ウィジェット、第二引数以降はオプション
    start_frame.pack(fill='both', padx=20,pady=20) #x,y両方に30ずつ余白を残しながら引き伸ばし配置
    
    label = tk.Label(start_frame,bg=bg_color,text="共通点発見練習",font=font4)
    label.pack()

    global ver
    if ver==0:
        label = tk.Label(start_frame,bg=bg_color,text="(事前テスト)",font=font4)
        label.pack()
    if ver==2:
        label = tk.Label(start_frame,bg=bg_color,text="(事後テスト)",font=font4)
        label.pack()
    
    label = tk.Label(start_frame,justify="center",bg=bg_color,text="赤字で表示されるすべてのキーワードと\n共通に関係する単語を解答してください",font=font1)
    label.pack(pady=5)
    
    """
    label = tk.Label(start_frame,justify="center",bg=bg_color,text="例）イチゴ,みかん,バナナ -> リンゴ",font=font1)
    label.pack(pady=5)
    
    label = tk.Label(start_frame,justify="center",bg=bg_color,text="文章中で同じような使い方をする\n言い換えや同位語ほど得点は高くなります",font=font1)
    label.pack(pady=5)
    
    """
    if ver==1:
        
        global border
        label = tk.Label(start_frame,justify="center",bg=bg_color,text="10問1セットで"+str(border)+" / 100点以上をでクリアです\nクリアすると次のレベルが選択できるようになります",font=font1)
        label.pack(pady=5)

        # チェック有無変数
        global var
        var = tk.IntVar(value = 1)
        #var.set(0) # value=0のラジオボタンにチェックを入れる
        
        frame = tk.Frame(start_frame,bg=bg_color) #第一引数に親ウィジェット、第二引数以降はオプション
        frame.pack(pady=15) #x,y両方に30ずつ余白を残しながら引き伸ばし配置

        global clear_df
        if(clear_df.iloc[0,0]=="clear"):
            choice = tk.Radiobutton(frame,bg=bg_color,text="レベル1 -> キーワード2個",value=1,variable=var,font=font1)
            choice.pack()
        else:
            label = tk.Label(frame,justify="center",bg=bg_color,text="× レベル1 -> キーワード2個",font=font1)
            label.pack()

        if(clear_df.iloc[0,1]=="clear"):
            choice = tk.Radiobutton(frame,bg=bg_color,text="レベル2 -> キーワード3個",value=2,variable=var,font=font1)
            choice.pack()
        else:
            label = tk.Label(frame,justify="center",bg=bg_color,text="× レベル2 -> キーワード3個",font=font1)
            label.pack()
        
        if(clear_df.iloc[0,2]=="clear"):
            choice = tk.Radiobutton(frame,bg=bg_color,text="レベル3 -> キーワード4個",value=3,variable=var,font=font1)
            choice.pack()
        else:
            label = tk.Label(frame,justify="center",bg=bg_color,text="× レベル3 -> キーワード4個",font=font1)
            label.pack()

    button = ttk.Button(start_frame, text='スタート',width=20,command=gate_1,default="active")
    button.pack(pady=10)
    
    root.geometry("650x450+25+50") # アプリの画面サイズ（横px × 縦px）

#login_gamen -> start_gamen
def gate0():
    
    global combobox
    new_name = combobox.get()
    
    global login_frame
    login_frame.destroy()
    
    if new_name != "":
        
        global folderfile
        if new_name not in folderfile:
            
            os.mkdir('LOG/'+new_name)
            
            df = pd.read_csv("csv/clear.csv",header=0)
            df.to_csv("LOG/"+str(new_name)+"/clear.csv",index=0)
            
        global clear_df
        global clear_path
        global LOG_path
        clear_path = LOG_path+"/"+str(new_name)+"/clear.csv"
        clear_df = pd.read_csv(clear_path,header=0)
        
        global ver
        ver=1 #学習モード
        if clear_df.iloc[0,0]=="notclear":
            ver=0 #初回モード
        
        if clear_df.iloc[0,3]=="clear":
            ver=2 #最終モード

        global login_name
        login_name = new_name
        
        start_gamen()
    
    else:
        
        login_gamen()
        
        label = tk.Label(login_frame,bg=bg_color, text="※その単語は登録されていません。",font=font5)
        label.pack()

#ログイン画面
def login_gamen():
    
    #ボタンやラベルをまとめたフレーム
    global login_frame
    login_frame = tk.Frame(root,bg=bg_color) #第一引数に親ウィジェット、第二引数以降はオプション
    login_frame.pack(fill='both', padx=20,pady=20) #x,y両方に30ずつ余白を残しながら引き伸ばし配置
    
    global LOG_path
    global folderfile
    folderfile = os.listdir(LOG_path)
    folderfile = natsorted(folderfile)#数字の順にsort  
    
    if(folderfile[0] == ".DS_Store"):
        del folderfile[0]
    
    label = tk.Label(login_frame,justify="center",bg=bg_color,text="初めての場合は新しく名前を入力してください\n2回目以降の場合は自分の名前を選択してください",font=font1)
    label.pack(pady=10)

    global combobox
    combobox = ttk.Combobox(login_frame,width=20,justify="center", values=folderfile,font=font1)
    combobox.pack(pady=10)

    button_error = tk.Button(login_frame, text="始める",width=20,command=gate0,default="active")
    button_error.pack(pady=10)
    
    root.geometry("650x225+25+50") # アプリの画面サイズ（横px × 縦px）
    root.mainloop()

#コマンドラインからスクリプトとして実行された場合にのみ以降の処理を実行する
if __name__ == "__main__":
    
    global bg_color
    bg_color="white"
    
    global fg_color
    fg_color="red"
    
    #メインウィンドウ
    root = tk.Tk()
    root.title("") # アプリの名前
    root.geometry("650x425+25+50") # アプリの画面サイズ（横px × 縦px）
    root.configure(bg=bg_color)
    
    global font1
    font1 = tk_font.Font(root,size=font_size)
    
    global font2
    font2 = tk_font.Font(root,size=font_size+2,weight="bold")

    global font3
    font3 = tk_font.Font(root,size=font_size,weight="bold")

    global font4
    font4 = tk_font.Font(root,size=font_size+5,weight="bold")

    global font5
    font5 = tk_font.Font(root,size=font_size-2)
    
    global font6
    font6 = tk_font.Font(root,size=font_size+2)

    login_gamen()
