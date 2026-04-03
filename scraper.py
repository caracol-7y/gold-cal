import pandas as pd
import requests
from datetime import datetime
import io

# ユーザー提供の正しいURLに差し替え
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR6Kw8YVw_hFXgzzSxFrYRZsTjQdsHS5Wg1J6sHF8xeGLY7gOAbPTuPBwvDR7WGHFLBuMDDBQe81-V/pub?gid=435870077&single=true&output=csv"

def get_all_prices_comprehensive():
    """
    スプレッドシートから最新の地金相場を取得する関数
    """
    try:
        # 1. データを取得（タイムアウトを設定して固まらないようにする）
        response = requests.get(CSV_URL, timeout=10)
        response.raise_for_status()
        
        # 文字化け防止のため明示的にUTF-8でデコード
        csv_data = response.content.decode('utf-8')
        
        # 2. Pandasで読み込み
        # header=None にすることで、1行目からデータとして正しく読み込みます
        df = pd.read_csv(io.StringIO(csv_data), header=None)
        
        # 3. 辞書形式に変換 (1列目が項目キー、2列目が価格数値)
        # スプレッドシートの A列に "K18"、B列に "9500" と入っている想定です
        raw_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
        
        prices_dict = {}
        for key, val in raw_dict.items():
            if pd.isna(key): continue # 空白行はスキップ
            
            try:
                # 数字以外の文字（円、カンマなど）を除去して数値化
                clean_val = str(val).replace(',', '').replace('円', '').replace(' ', '')
                prices_dict[str(key).strip()] = int(float(clean_val))
            except:
                continue

        # 4. 更新時刻
        update_time = datetime.now().strftime("%Y/%m/%d %H:%M")
        
        return prices_dict, update_time

    except Exception as e:
        # 失敗した場合はエラー内容をターミナルに表示し、アプリ側にはエラーを通知
        print(f"Scraper Error: {e}")
        return {}, f"取得失敗 ({datetime.now().strftime('%H:%M')})"
