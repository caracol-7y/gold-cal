import requests
import json
import re

def get_all_prices_comprehensive(api_key):
    target_url = "https://www.net-japan.co.jp/precious_metal/print/"
    payload = {
        "url": target_url, 
        "renderType": "html", 
        "outputAsJson": True,
        "requestSettings": { 
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36", 
            "waitInterval": 2000 
        }
    }
    api_url = f"https://phantomjscloud.com/api/browser/v2/{api_key}/?request={json.dumps(payload)}"
    
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if "content" not in data or "data" not in data["content"]:
            return None, None
            
        html_content = data["content"]["data"]
        text_only = re.sub(r'<[^>]*>', ' ', html_content)
        text_only = re.sub(r'\s+', ' ', text_only)
        
        time_match = re.search(r'(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2})', text_only)
        update_time = time_match.group(1) if time_match else "時刻不明"

        base_targets = {"Gold_Ingot": "金", "Pt_Ingot": "Pt", "Silver_Ingot": "銀", "Pd_Ingot": "Pd"}
        
        purity_targets = [
            "K24", "K22", "K21.6", "K20", "K18", "K14", "K10", "K9", 
            "Pt1000", "Pt950", "Pt900", "Pt850", 
            "Sv1000", "Sv925", 
            "Combo"
        ]
        
        all_prices = {}
        for key, label in base_targets.items():
            regex = rf'{label}\s*([0-9,]+)\s*円'
            match = re.search(regex, text_only)
            all_prices[key] = int(match.group(1).replace(',', '')) if match else None
        
        for t in purity_targets:
            if t == "Combo":
                regex = r'金・プラチナコンビ[^0-9]*?([0-9,]+)\s*円'
            else:
                regex = rf'{t}[^0-9]*?([0-9,]+)\s*円'
                
            match = re.search(regex, text_only)
            all_prices[t] = int(match.group(1).replace(',', '')) if match else None
                
        return all_prices, update_time
    except Exception as e:
        raise Exception(f"API通信エラー: {e}")