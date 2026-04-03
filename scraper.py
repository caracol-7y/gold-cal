import pandas as pd
import requests
from datetime import datetime
import io

# ★ ここにあなたのGoogleスプレッドシートの「ウェブに公開(CSV)」URLを貼り付けてください
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR6Kw8YVw_hFXgzzSxFrYRZsTjQdsHS5Wg1J6sHF8xeGLY7gOAbPTuPBwvDR7WGHFLBuMDDBQe81-V/pub?gid=435870077&single=true&output=csv"

def get_all_prices_comprehensive():
    """
    スプレッドシートから最新の地金相場を取得する関数
    """
    try:
        # 1. スプレッドシートからCSVデータを取得
        response = requests.get(CSV_URL)
        response.raise_for_status() # エラーがあれば例外を出す
        
        # 2. PandasでCSVを読み込む
        # CSVの1列目が「項目名（Gold_Ingotなど）」、2列目が「価格」である想定
        df = pd.read_csv(io.StringIO(response.text))
        
        # 3. 辞書形式に変換 { "Gold_Ingot": 13000, "K18": 9500, ... }
        # 列名はスプレッドシートの1行目に合わせる必要があります
        # ここでは「項目の列」と「価格の列」を辞書に変換しています
        prices_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
        
        # 価格を数値（int）に変換
        for key in prices_dict:
            try:
                prices_dict[key] = int(str(prices_dict[key]).replace(',', '').replace('円', ''))
            except:
                prices_dict[key] = None

        # 4. 現在の更新時刻を取得
        update_time = datetime.now().strftime("%Y/%m/%d %H:%M")
        
        return prices_dict, update_time

    except Exception as e:
        print(f"データ取得エラー: {e}")
        # 失敗した場合は空の辞書とエラーメッセージを返す
        return {}, "取得失敗"
