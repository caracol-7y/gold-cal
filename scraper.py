# scraper.py

import pandas as pd
import requests
import io

def get_all_prices_comprehensive():
    # URLは変更なし（Dataタブを指定していることを確認してください）
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR6Kw8YVw_hFXgzzSxFrYRZsTjQdsHS5Wg1J6sHF8xeGLY7gOAbPTuPBwvDR7WGHFLBuMDDBQe81-V/pub?gid=435870077&single=true&output=csv"
    
    try:
        response = requests.get(URL)
        response.encoding = 'utf-8'
        df = pd.read_csv(io.StringIO(response.text), header=None)

        # --- 更新日時の取得 (B4セル) ---
        # df.shape[0] は行数、df.shape[1] は列数を確認しています
        if df.shape[0] >= 4 and df.shape[1] >= 2:
            raw_time = df.iloc[3, 1] # B4
            update_time = str(raw_val).strip() if pd.notna(raw_val) else "日時未設定"
        else:
            # B4が存在しない場合のデバッグ用
            update_time = f"取得不可(サイズ:{df.shape[0]}x{df.shape[1]})"

        # --- 価格データの取得 ---
        keys = ["Gold_Ingot","K24","K22","K21.6","K20","K18","K14","K10","K9",
                "Pt_Ingot","Pt1000","Pt950","Pt900","Pt850",
                "Silver_Ingot","Sv1000","Sv925","Pd_Ingot"]
        
        prices = {}
        for i, key in enumerate(keys):
            try:
                # B5セル(4, 1)以降を順番にチェック
                row_idx = i + 4
                if df.shape[0] > row_idx and df.shape[1] >= 2:
                    val = str(df.iloc[row_idx, 1]).replace(',', '')
                    prices[key] = int(float(val))
                else:
                    prices[key] = 0
            except:
                prices[key] = 0

        return prices, update_time

    except Exception as e:
        return None, f"接続エラー: {e}"
