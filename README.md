
プログラムはVScodeで作成
パッケージはanacondaで管理(pipは使わずcondaのみでinstall)

main_interface.pyは主にインターフェースに関する関数
sub_interfaceはその他の関数

bin_fileはfastTextの日本語学習済みmodel
(読み込みはword2vecの関数で行っている)

csvにあるのは
事前問題(prior_mondai)、事後問題(after_mondai)、ログファイルのフォーマット、常用漢字
作成した問題を格納するファイル(mondai2など)←問題ごとに作成を挟むと時間がかかるのでひとまず事前に作成したものを格納しておいて対応

modelには
上記の日本語学習済みモデルで学習した単語の中から適切な単語をあらかじめ格納してある
目的は単語ごとの検索ヒット数を用意しておくため。(←これが時間がかかって論文には間に合わなかった)
学習済みモデルの登録単語数は23万語あるが、このファイル内には
N0.1~No.90000までで適切な単語(特に名詞)だけが格納できている。
