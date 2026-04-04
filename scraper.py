# scraper.py

def get_all_prices_comprehensive():
    # ★ DataタブのURL（gid=435870077がDataタブであることを想定）
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR6Kw8YVw_hFXgzzSxFrYRZsTjQdsHS5Wg1J6sHF8xeGLY7gOAbPTuPBwvDR7WGHFLBuMDDBQe81-V/pub?gid=435870077&single=true&output=csv"
    
    try:
        response = requests.get(URL)
        response.encoding = 'utf-8'
        # header=None にすることで、スプレッドシートの1行目を「インデックス0」として読みます
        df = pd.read_csv(io.StringIO(response.text), header=None)

        # 【検証用】もし B4 が 2026/04/03 09:30 なら、ここが iloc[3, 1] になります
        # 0=1行目, 1=2行目, 2=3行目, 3=4行目
        # 0=A列, 1=B列
        raw_val = df.iloc[3, 1] 
        
        # もし表示がズレる場合、ここを iloc[2, 1] や iloc[4, 1] にして試してください
        update_time = str(raw_val).strip() if pd.notna(raw_val) else "日時不明"

        # 価格データの取得（B5:B22）
        keys = ["Gold_Ingot","K24","K22","K21.6","K20","K18","K14","K10","K9",
                "Pt_Ingot","Pt1000","Pt950","Pt900","Pt850",
                "Silver_Ingot","Sv1000","Sv925","Pd_Ingot"]
        
        prices = {}
        for i, key in enumerate(keys):
            try:
                # B5セル = インデックス[4, 1]
                val = str(df.iloc[i + 4, 1]).replace(',', '')
                prices[key] = int(float(val))
            except:
                prices[key] = 0

        return prices, update_time

    except Exception as e:
        return None, f"Error: {e}"
