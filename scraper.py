import pandas as pd

def get_all_prices_comprehensive():
    # 「ウェブに公開」で発行したCSVのURLをここに貼り付けてください
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-xxxxxxxxxxxx/pub?gid=435870077&single=true&output=csv"
    
    try:
        df = pd.read_csv(sheet_url, header=None)
        
        # B4 (3行目, 1列目) から更新時刻取得
        update_time_raw = df.iloc[3, 1]
        update_time = str(update_time_raw) if pd.notna(update_time_raw) else "時刻不明"
        
        # B5:B21 (4〜20行目, 1列目) から価格リスト取得（計17項目）
        prices_list = df.iloc[4:22, 1].tolist()
        
        # スプレッドシートの並び順に完全に一致させる（17項目）
        keys = [
            "Gold_Ingot", "K24", "K22", "K21.6", "K20", "K18", "K14", "K10", "K9",
            "Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850",
            "Silver_Ingot", "Sv1000", "Sv925", "Pd_Ingot"
        ]
        
        all_prices = {}
        for key, price_val in zip(keys, prices_list):
            if pd.isna(price_val):
                all_prices[key] = None
                continue
            
            try:
                if isinstance(price_val, str):
                    clean_str = price_val.replace(',', '').strip()
                    all_prices[key] = int(clean_str) if clean_str else None
                else:
                    all_prices[key] = int(price_val)
            except ValueError:
                all_prices[key] = None
                
        return all_prices, update_time
        
    except Exception as e:
        raise Exception(f"スプレッドシート取得エラー: {e}")
