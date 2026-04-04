import pandas as pd
import requests
import io

def get_all_prices_comprehensive():
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR6Kw8YVw_hFXgzzSxFrYRZsTjQdsHS5Wg1J6sHF8xeGLY7gOAbPTuPBwvDR7WGHFLBuMDDBQe81-V/pub?gid=435870077&single=true&output=csv"
    
    try:
        response = requests.get(URL)
        response.encoding = 'utf-8'
        df = pd.read_csv(io.StringIO(response.text), header=None)

        # ★ Data!B4 (インデックス 3行目, 1列目) を取得
        # 文字列として取得し、前後の空白などを取り除く
        raw_time = df.iloc[3, 1]
        update_time = str(raw_time).strip() if pd.notna(raw_time) else "日時未設定"

        # 価格データの取得 (B5:B22)
        keys = [
            "Gold_Ingot", "K24", "K22", "K21.6", "K20", "K18", "K14", "K10", "K9",
            "Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850",
            "Silver_Ingot", "Sv1000", "Sv925", "Pd_Ingot"
        ]
        
        prices = {}
        for i, key in enumerate(keys):
            try:
                # B5セルはインデックス[4, 1]からスタート
                val = str(df.iloc[i + 4, 1]).replace(',', '')
                prices[key] = int(float(val))
            except:
                prices[key] = 0

        return prices, update_time

    except Exception as e:
        return None, f"取得エラー: {str(e)}"
