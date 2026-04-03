import pandas as pd
import requests
from datetime import datetime
import io
import config

# 提供された正しいURL
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR6Kw8YVw_hFXgzzSxFrYRZsTjQdsHS5Wg1J6sHF8xeGLY7gOAbPTuPBwvDR7WGHFLBuMDDBQe81-V/pub?gid=435870077&single=true&output=csv"

def get_all_prices_comprehensive():
    try:
        # 1. データの取得
        response = requests.get(CSV_URL, timeout=10)
        response.raise_for_status()
        csv_data = response.content.decode('utf-8')
        
        # 2. Pandasで読み込み（全列・全行を対象にするためheaderなし）
        df = pd.read_csv(io.StringIO(csv_data), header=None)
        
        # 3. シート内の「数字だけ」をリストに抽出
        # 行・列を問わず、上から順に数字が入っているセルを探します
        all_numbers = []
        for _, row in df.iterrows():
            for cell_val in row:
                s_val = str(cell_val).strip()
                # カンマや「円」を消して数字だけにする
                clean_num = "".join(filter(str.isdigit, s_val))
                if clean_num:
                    all_numbers.append(int(clean_num))
                    break # その行で数字が見つかったら次の行へ
        
        # 4. config.ALL_METAL_KEYS の順番通りに割り当て
        prices_dict = {}
        for i, key in enumerate(config.ALL_METAL_KEYS):
            if i < len(all_numbers):
                prices_dict[key] = all_numbers[i]
            else:
                prices_dict[key] = None # 数字が足りない場合

        update_time = datetime.now().strftime("%Y/%m/%d %H:%M")
        return prices_dict, update_time

    except Exception as e:
        print(f"Scraper Error: {e}")
        return {}, "取得失敗"
