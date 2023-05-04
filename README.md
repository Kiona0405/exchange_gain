# exchange_gain

雑所得となる為替損益(exchange gain)の計算サポートツール. 
使用は自己責任でお願いします.  
算出方法に間違いがあればIssueにて報告をお願いします.  

## How to use

仮定

- 楽天証券のデータを想定
- 外貨は米ドルのみ
- git, python3, pipをインストール済み


1. データの取得 
   1. https://www.rakuten-sec.co.jp/にアクセス
   1. ログイン
   1. "マイメニュー>口座明細（精算履歴）>外貨建て"のページにアクセス  
      マイメニューは画面右上にある。選択後、一覧から口座明細をクリック。  
      ページ遷移後に、外貨建てのタブをクリック。
   1. 検索フィルターを以下のとおりに設定後、取引のデータをcsv形式で取得  
      - 取引種類 ->　すべて
      - 詳細 ->　すべて
      - 口座 -> 空白
      - 通貨 -> 米ドル
      - 期間 -> すべて
   1. 取得したファイルに名前をつける.  
      ここでは便宜上history.csvとする.  

    参考) ダウンロードファイルのヘッダー(2023/05/04)  
    受渡日	約定日	口座区分	取引区分	対象証券名	決済通貨	単価	数量［株 /口］	受渡金額（受取）	受渡金額（受取）[円換算]	受渡金額（支払）	受渡金額（支払）[円換算]	為替レート	預り金

1. レポジトリのダウンロード  
   ```bash
   git clone https://github.com/Kiona0405/exgain.git
   cd exgain
   ```

1. ライブラリのインストール
    ```bash
    pip install -r requirements.txt
    ```

1. プログラムの実行  
    ```bash
    cd 
    python src/exchange_gain.py --input history.csv --output result.csv
    ```
    history.csvは楽天証券のホームページからダウンロードしたデータ

1. 結果の取得  
   result.csvを適当なアプリケーションで開いた後、"exgain_cumsum"列から対象年の為替差益を取得する。  
   example) 2021年の場合->(2021/12/最後のexgain_cumsumの値) - (2020/12最後のexgain_cumsumの値)

