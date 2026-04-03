import pandas as pd
import requests
from datetime import datetime
import io

# 提供された正しいURL
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR6Kw8YVw_hFXgzzSxFrYRZsTjQdsHS5Wg1J6sHF8xeGLY7gOAbPTuPBwvDR7WGHFLBuMDDBQe81-V/pub?gid=435870077&single=true&output=csv"

def get_all_prices_comprehensive():
    try:
        response = requests.get(CSV_URL, timeout=10)
        response.raise_for_status()
        csv_data = response.content.decode('utf-8')
        
        # ヘッダーなしとして読み込み
        df = pd.read_csv(io.StringIO(csv_data), header=None)
        
        prices_dict = {}
        for _, row in df.iterrows():
            key = str(row[0]).strip()
            val = str(row[1]).strip()
            
            # 数字だけを抽出 (カンマや"円"を除去)
            try:
                clean_val = "".join(filter(str.isdigit, val))
                if clean_val:
                    prices_dict[key] = int(clean_val)
            except:
                continue

        update_time = datetime.now().strftime("%Y/%m/%d %H:%M")
        return prices_dict, update_time

    except Exception as e:
        return {}, "取得失敗"
