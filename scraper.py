import pandas as pd
import requests
import io

def get_all_prices_comprehensive():
    # スプレッドシートのCSV公開URL
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR6Kw8YVw_hFXgzzSxFrYRZsTjQdsHS5Wg1J6sHF8xeGLY7gOAbPTuPBwvDR7WGHFLBuMDDBQe81-V/pub?gid=435870077&single=true&output=csv"
    
    try:
        response = requests.get(URL)
        response.encoding = 'utf-8'
        df = pd.read_csv(io.StringIO(response.text), header=None)

        # ★ B4セル (インデックス 3行目, 1列目) から更新日時を取得
        update_time = df.iloc[3, 1] if len(df) > 3 else "不明"

        # 価格データの取得 (B5:B22 -> インデックス 4行目から21行目)
        keys = [
            "Gold_Ingot", "K24", "K22", "K21.6", "K20", "K18", "K14", "K10", "K9",
            "Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850",
            "Silver_Ingot", "Sv1000", "Sv925",
            "Pd_Ingot"
        ]
        
        prices = {}
        for i, key in enumerate(keys):
            try:
                # B列 (インデックス1) の 5行目 (インデックス4) から順番に取得
                val = str(df.iloc[i + 4, 1]).replace(',', '')
                prices[key] = int(float(val))
            except:
                prices[key] = 0

        return prices, update_time

    except Exception as e:
        print(f"Error fetching prices: {e}")
        return None, "取得失敗"
