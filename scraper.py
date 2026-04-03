import pandas as pd
import requests
from datetime import datetime
import io
import config

# 提供されたURL（gid=435870077 は Dataシートを指している前提です）
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR6Kw8YVw_hFXgzzSxFrYRZsTjQdsHS5Wg1J6sHF8xeGLY7gOAbPTuPBwvDR7WGHFLBuMDDBQe81-V/pub?gid=435870077&single=true&output=csv"

def get_all_prices_comprehensive():
    try:
        response = requests.get(CSV_URL, timeout=10)
        response.raise_for_status()
        csv_data = response.content.decode('utf-8')
        
        # header=None で読み込み
        df = pd.read_csv(io.StringIO(csv_data), header=None)
        
        # --------------------------------------------------
        # B5:B22 を抽出する
        # 行: 5行目〜22行目 → インデックスは 4〜21 (Pythonでは 4:22)
        # 列: B列 → インデックス 1
        # --------------------------------------------------
        # iloc[行の範囲, 列のインデックス]
        target_data = df.iloc[4:22, 1] 
        
        prices_dict = {}
        
        # 抽出したデータを config.ALL_METAL_KEYS の順番に割り当て
        for i, key in enumerate(config.ALL_METAL_KEYS):
            if i < len(target_data):
                # セルの値を取得
                val = str(target_data.iloc[i]).strip()
                
                # 数字だけを抽出して数値化
                try:
                    clean_val = "".join(filter(str.isdigit, val))
                    if clean_val:
                        prices_dict[key] = int(clean_val)
                    else:
                        prices_dict[key] = None
                except:
                    prices_dict[key] = None
            else:
                prices_dict[key] = None

        update_time = datetime.now().strftime("%Y/%m/%d %H:%M")
        return prices_dict, update_time

    except Exception as e:
        print(f"Scraper Error: {e}")
        return {}, "取得失敗"
