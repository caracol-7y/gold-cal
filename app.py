import streamlit as st
import requests
import json
import re
import pandas as pd
from datetime import datetime

# ==========================================
# 設定 (Secretsから読み込む)
# ==========================================
try:
    # Streamlit Cloud上のSecretsから取得
    PHANTOM_API_KEY = st.secrets["PHANTOM_API_KEY"]
except Exception:
    # ローカル環境用。ここを空にするか、ダミーを入れておく
    PHANTOM_API_KEY = st.secrets.get("PHANTOM_API_KEY", "YOUR_API_KEY_HERE")
# ==========================================

st.set_page_config(page_title="地金価格管理システム Pro", page_icon="💰", layout="centered")

# --- スクレイピング関数 ---
def get_all_prices_comprehensive():
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
    api_url = f"https://phantomjscloud.com/api/browser/v2/{PHANTOM_API_KEY}/?request={json.dumps(payload)}"
    
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
        purity_targets = ["K24", "K22", "K20", "K18", "K14", "K10", "K9", "Pt1000", "Pt950", "Pt900", "Pt850", "Sv1000", "Sv925"]
        
        all_prices = {}
        for key, label in base_targets.items():
            regex = rf'{label}\s*([0-9,]+)\s*円'
            match = re.search(regex, text_only)
            all_prices[key] = int(match.group(1).replace(',', '')) if match else None
        for t in purity_targets:
            regex = rf'{t}[^0-9]*?([0-9,]+)\s*円'
            match = re.search(regex, text_only)
            all_prices[t] = int(match.group(1).replace(',', '')) if match else None
                
        return all_prices, update_time
    except Exception as e:
        st.error(f"API通信エラー: {e}")
        return None, None

# --- セッション状態の初期化 ---
if 'all_prices' not in st.session_state:
    st.session_state.all_prices = None
if 'update_time' not in st.session_state:
    st.session_state.update_time = None
# メモ保存用のリストを初期化
if 'memo_list' not in st.session_state:
    st.session_state.memo_list = []

# ==========================================
# サイドバー
# ==========================================
st.sidebar.title("⚙️ メニュー")
page = st.sidebar.radio("ページ選択", ["💰 価格計算機", "📋 最新価格一覧表", "📝 計算メモ"])

if st.sidebar.button("🔄 最新相場に更新"):
    with st.spinner("クラウド解析中..."):
        prices, time_val = get_all_prices_comprehensive()
        if prices:
            st.session_state.all_prices = prices
            st.session_state.update_time = time_val
            st.sidebar.success("更新完了！")
        else:
            st.sidebar.error("更新失敗")

st.sidebar.markdown("---")
st.sidebar.markdown(
    '<a href="https://www.net-japan.co.jp/precious_metal_partner/" target="_blank" style="text-decoration: none; color: #0000EE; font-weight: bold;">🔗 公式サイトで価格を確認する</a>', 
    unsafe_allow_html=True
)

# ==========================================
# ページ1：価格計算機 (品位も横並びボタン版)
# ==========================================
if page == "💰 価格計算機":
    st.title("💍 地金価格計算機")
    
    if st.session_state.update_time:
        st.caption(f"🕒 サイト更新時刻: {st.session_state.update_time}")
    else:
        st.warning("⚠️ 相場が取得できていません。サイドバーから「更新」してください。")

    # --- 2段階選択システム (すべて横並びボタン形式) ---
    metal_categories = {
        "金 (Gold)": ["Gold_Ingot", "K24", "K22", "K20", "K18", "K14", "K10", "K9"],
        "プラチナ (Platinum)": ["Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850"],
        "銀 (Silver)": ["Silver_Ingot", "Sv1000", "Sv925"],
        "パラジウム (Palladium)": ["Pd_Ingot"]
    }
    
    options_map = {
        "Gold_Ingot": "K24 インゴット", "K24": "K24", "K22": "K22", "K20": "K20", "K18": "K18", "K14": "K14", "K10": "K10", "K9": "K9",
        "Pt_Ingot": "Pt1000 インゴット", "Pt1000": "Pt1000", "Pt950": "Pt950", "Pt900": "Pt900", "Pt850": "Pt850",
        "Silver_Ingot": "Sv1000 インゴット", "Sv1000": "Sv1000", "Sv925": "Sv925",
        "Pd_Ingot": "Pd インゴット"
    }

    # ステップ1: 金属種別を選択 (横並び)
    selected_cat = st.radio(
        "金属を選択", 
        options=list(metal_categories.keys()), 
        horizontal=True
    )
    
    # ステップ2: その金属に属する品位を選択 (ここも横並び)
    cat_keys = metal_categories[selected_cat]
    cat_options = [options_map[k] for k in cat_keys]
    
    # horizontal=True にすることで、品位もボタン形式で横に並びます
    selected_display = st.radio(
        "品位を選択", 
        options=cat_options, 
        horizontal=True
    )
    
    selected_key = [k for k, v in options_map.items() if v == selected_display][0]

    # --- その後の入力 (重量、割合などはそのまま) ---
    # (以下、weight, rate_sell などの入力欄と計算ロジックが続きます)
    # --- その後の入力 (重量、割合などはそのまま) ---
    weight = st.number_input("重量 (g)", min_value=0.0, value=1.0, step=1.0, format="%.1f")
    rate_sell = st.number_input("割合 (%)", min_value=0, max_value=100, value=90, step=5)

    use_bukin = st.checkbox("歩金を適用する", value=True)
    if use_bukin:
        rate_buy = st.number_input("歩金 (%)", min_value=0, max_value=20, value=5, step=1)
    else:
        rate_buy = 0

    # (以下、計算ロジックと結果表示は変更なし)

    if st.session_state.all_prices and st.session_state.all_prices.get(selected_key):
        market_price = st.session_state.all_prices[selected_key]
        st.info(f"現在の相場単価: **{market_price:,} 円/g**")
        
        if weight > 0:
            theory_total = market_price * weight
            sell_unit = market_price * (rate_sell / 100)
            sell_total = sell_unit * weight
            buy_unit = sell_unit / (1 + (rate_buy / 100))
            buy_total = buy_unit * weight
            
            # 結果表示
            if use_bukin:
                res_col1, res_col2, res_col3 = st.columns(3)
                with res_col1:
                    st.markdown(f"""<div style="background-color: #ffffff; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #cccccc;"><span style="font-size: 16px; color: #666;">最大価格 (100%)</span><br><span style="font-size: 28px; font-weight: bold; color: #333;">{theory_total:,.0f} 円</span></div>""", unsafe_allow_html=True)
                with res_col2:
                    st.markdown(f"""<div style="background-color: #fff0f0; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #ff4b4b;"><span style="font-size: 16px; color: #ff4b4b;">割合価格 ({rate_sell}%)</span><br><span style="font-size: 28px; font-weight: bold; color: #ff4b4b;">{sell_total:,.0f} 円</span></div>""", unsafe_allow_html=True)
                with res_col3:
                    st.markdown(f"""<div style="background-color: #f0f7ff; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #4b89ff;"><span style="font-size: 16px; color: #4b89ff;">買い歩込価格 ({rate_buy}%)</span><br><span style="font-size: 28px; font-weight: bold; color: #4b89ff;">{buy_total:,.0f} 円</span></div>""", unsafe_allow_html=True)
            else:
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.markdown(f"""<div style="background-color: #ffffff; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #cccccc;"><span style="font-size: 16px; color: #666;">最大価格 (100%)</span><br><span style="font-size: 28px; font-weight: bold; color: #333;">{theory_total:,.0f} 円</span></div>""", unsafe_allow_html=True)
                with res_col2:
                    st.markdown(f"""<div style="background-color: #fff0f0; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #ff4b4b;"><span style="font-size: 16px; color: #ff4b4b;">割合価格 ({rate_sell}%)</span><br><span style="font-size: 28px; font-weight: bold; color: #ff4b4b;">{sell_total:,.0f} 円</span></div>""", unsafe_allow_html=True)

            # --- メモ保存ボタン ---
            st.write("")
            if st.button("💾 この結果をメモに保存"):
                memo_entry = {
                    "datetime": datetime.now().strftime("%Y/%m/%d %H:%M"),
                    "item": selected_display,
                    "weight": f"{weight}g",
                    "theory": f"{theory_total:,.0f}円",
                    "rate": f"{rate_sell}%",
                    "sell_total": f"{sell_total:,.0f}円",
                    "buy_total": f"{buy_total:,.0f}円" if use_bukin else "-"
                }
                st.session_state.memo_list.append(memo_entry)
                st.success("メモに保存しました！")
    else:
        st.warning("⚠️ 相場が取得できていません。サイドバーから「更新」してください。")

# ==========================================
# ページ2：最新価格一覧表
# ==========================================
elif page == "📋 最新価格一覧表":
    st.title("📋 最新価格一覧表")
    if st.session_state.update_time:
        st.caption(f"🕒 サイト更新時刻: {st.session_state.update_time}")
    else:
        st.warning("⚠️ 相場が取得できていません。サイドバーから「更新」してください。")

    if st.session_state.all_prices:
        categories = {"金 (Gold)": ["Gold_Ingot", "K24", "K22", "K20", "K18", "K14", "K10", "K9"], "プラチナ (Platinum)": ["Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850"], "銀 (Silver)": ["Silver_Ingot", "Sv1000", "Sv925"], "パラジウム (Palladium)": ["Pd_Ingot"]}
        options_map = {"Gold_Ingot": "K24 インゴット", "K24": "K24", "K22": "K22", "K20": "K20", "K18": "K18", "K14": "K14", "K10": "K10", "K9": "K9", "Pt_Ingot": "Pt1000 インゴット", "Pt1000": "Pt1000", "Pt950": "Pt950", "Pt900": "Pt900", "Pt850": "Pt850", "Silver_Ingot": "Sv1000 インゴット", "Sv1000": "Sv1000", "Sv925": "Sv925", "Pd_Ingot": "Pd インゴット"}
        for cat, keys in categories.items():
            st.markdown(f"""<div style="background-color: #f0f2f6; padding: 8px 15px; border-radius: 5px; margin-top: 20px; margin-bottom: 10px; border-left: 5px solid #31333F;"><span style="font-weight: bold; font-size: 18px; color: #31333F;">{cat}</span></div>""", unsafe_allow_html=True)
            category_html = '<div style="display: flex; flex-direction: column;">'
            for k in keys:
                price = st.session_state.all_prices.get(k)
                price_display = f"{price:,} 円" if price else "取得不可"
                display_name = options_map[k]
                category_html += f"""<div style="display: flex; justify-content: space-between; align-items: center; background-color: #ffffff; padding: 12px 10px; border-bottom: 1px solid #eeeeee; font-family: sans-serif;"><span style="font-weight: bold; color: #333333; font-size: 15px;">{display_name}</span><span style="color: #ff0000; font-weight: bold; font-size: 16px;">{price_display}</span></div>"""
            category_html += '</div>'
            st.markdown(category_html, unsafe_allow_html=True)
            st.write("") 
    else:
        st.warning("⚠️ 相場が取得できていません。サイドバーから「更新」してください。")

# ==========================================
# ページ3：計算メモ
# ==========================================
elif page == "📝 計算メモ":
    st.title("📝 計算メモ")
    
    if not st.session_state.memo_list:
        st.info("保存されたメモはありません。計算機ページから保存してください。")
    else:
        # メモ一覧をDataFrameに変換して表示
        df = pd.DataFrame(st.session_state.memo_list)
        # 列名をわかりやすく変更
        df.columns = ["日時", "品位", "重量", "最大価格", "割合(%)", "割合価格", "買い歩込価格"]
        
        st.table(df)
        
        # メモ消去ボタン
        if st.button("🗑️ すべてのメモを消去"):
            st.session_state.memo_list = []
            st.rerun()

st.caption("※ネットジャパンのプリントページから抽出した最新データです。")
