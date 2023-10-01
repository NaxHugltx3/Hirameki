発想力を鍛えるPythonアプリケーションで、グラフィカルユーザーインターフェース（GUI）を提供します。
このREADMEでは、アプリケーションのインストールと使用方法に関する情報を提供します。

## 必要なライブラリとリソース

Hiramekiを実行するには、以下のライブラリとリソースが必要です：

- Python 3.x
- tkinter
- appscript
- pandas
- gensim
- calendar
- time
- natsort

さらに、事前に訓練された日本語の単語ベクトルモデルが必要です。
これはは事前にファイルに入っています。

## インストール方法

1. Hiramekiリポジトリをクローンします：

```bash
git clone https://github.com/hoge/Hirameki.git
cd Hirameki
```
2. 以下のコマンドを実行して、必要なライブラリをインストールします。
```bash
pip install tkinter appscript pandas gensim calendar natsort
```
3. main_interface.pyスクリプトを実行します：
```bash
python main_interface.py
```
