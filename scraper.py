import pandas as pd

def get_all_prices_comprehensive():
    # ⚠️ ここに「ウェブに公開」で取得したURLを貼り付けてください
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR6Kw8YVw_hFXgzzSxFrYRZsTjQdsHS5Wg1J6sHF8xeGLY7gOAbPTuPBwvDR7WGHFLBuMDDBQe81-V/pub?gid=435870077&single=true&output=csv"
    
    try:
        # スプレッドシートを取得
        df = pd.read_csv(sheet_url, header=None)
        
        # B4 (インデックス3) から更新時刻取得
        update_time_raw = df.iloc[3, 1]
        update_time = str(update_time_raw).strip() if pd.notna(update_time_raw) else "時刻不明"
        
        # 18項目（B5〜B22）を取得
        prices_list = df.iloc[4:22, 1].tolist()
        
        keys = [
            "Gold_Ingot", "K24", "K22", "K21.6", "K20", "K18", "K14", "K10", "K9",
            "Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850",
            "Silver_Ingot", "Sv1000", "Sv925", "Pd_Ingot"
        ]
        
        all_prices = {}
        for key, price_val in zip(keys, prices_list):
            if pd.isna(price_val) or str(price_val).strip() == "":
                all_prices[key] = None
                continue
            
            try:
                # 文字列処理: カンマを除去し数値へ
                if isinstance(price_val, str):
                    price_val = price_val.replace(',', '').strip()
                all_prices[key] = int(float(price_val))
            except (ValueError, TypeError):
                all_prices[key] = None
                
        return all_prices, update_time
        
    except Exception as e:
        raise Exception(f"データ解析エラー: {e}")
