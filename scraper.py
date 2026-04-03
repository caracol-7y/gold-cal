import pandas as pd

def get_all_prices_comprehensive():
    # スプレッドシートのCSVエクスポートURL（gid=435870077 が Dataシート）
    sheet_url = "https://docs.google.com/spreadsheets/d/1oi78z7eqyIZI6Jh_eRuwUXXVgK_V_xsYaenXSeu7eK4/export?format=csv&gid=435870077"
    
    try:
        # PandasでCSVを読み込む
        df = pd.read_csv(sheet_url, header=None)
        
        # B4セル (行インデックス3, 列インデックス1) からネットジャパンの更新時刻を取得
        update_time_raw = df.iloc[3, 1]
        update_time = str(update_time_raw) if pd.notna(update_time_raw) else "時刻不明"
        
        # B5:B21 (行インデックス4〜20, 列インデックス1) から価格リストを取得
        prices_list = df.iloc[4:21, 1].tolist()
        
        # B5:B21の並び順に合わせた17項目のキー
        keys = [
            "Gold_Ingot", "K24", "K22", "K20", "K18", "K14", "K10", "K9",
            "Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850",
            "Silver_Ingot", "Sv1000", "Sv925", "Pd_Ingot"
        ]
        
        all_prices = {}
        for key, price_val in zip(keys, prices_list):
            if pd.isna(price_val):
                all_prices[key] = None
                continue
            
            # 文字列の場合はカンマを削除して数値に変換
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
