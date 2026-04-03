import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import get_all_prices_comprehensive
from calculator import calculate_prices

# ==========================================
# 1. 共通設定・定数
# ==========================================
st.set_page_config(page_title="地金計算システム Pro", page_icon="💰", layout="centered")

METAL_CATEGORIES = {
    "Gold": ["Gold_Ingot", "K24", "K22", "K21.6", "K20", "K18", "K14", "K10", "K9"],
    "Platinum": ["Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850"],
    "Silver": ["Silver_Ingot", "Sv1000", "Sv925"],
    "Palladium": ["Pd_Ingot"]
}

OPTIONS_MAP = {
    "Gold_Ingot": "Gold Bar", "K24": "K24", "K22": "K22", "K21.6": "K21.6", "K20": "K20", "K18": "K18", "K14": "K14", "K10": "K10", "K9": "K9",
    "Pt_Ingot": "Platinum Bar", "Pt1000": "Pt1000", "Pt950": "Pt950", "Pt900": "Pt900", "Pt850": "Pt850",
    "Silver_Ingot": "Silver Bar", "Sv1000": "Sv1000", "Sv925": "Sv925",
    "Pd_Ingot": "Pd Bar"
}

# ==========================================
# 2. セッション状態の初期化
# ==========================================
if 'all_prices' not in st.session_state: st.session_state.all_prices = None
if 'update_time' not in st.session_state: st.session_state.update_time = None
if 'memo_list' not in st.session_state: st.session_state.memo_list = []
if 'p_cat' not in st.session_state: st.session_state.p_cat = "Gold"
if 'p_display' not in st.session_state: st.session_state.p_display = "K18"
if 'p_weight' not in st.session_state: st.session_state.p_weight = 1.0
if 'p_rate_sell' not in st.session_state: st.session_state.p_rate_sell = 90
if 'p_use_bukin' not in st.session_state: st.session_state.p_use_bukin = False 
if 'p_rate_buy' not in st.session_state: st.session_state.p_rate_buy = 5

# ==========================================
# 3. データ取得ロジック
# ==========================================
@st.cache_data(ttl=3600)
def fetch_prices_cached():
    return get_all_prices_comprehensive()

try:
    prices, time_val = fetch_prices_cached()
    st.session_state.all_prices = prices
    st.session_state.update_time = time_val
except Exception as e:
    st.error(f"データ取得エラー: {e}")

def force_update():
    fetch_prices_cached.clear()
    st.rerun()

# ==========================================
# 4. サイドバー
# ==========================================
st.sidebar.title("⚙️ メニュー")
page = st.sidebar.radio("ページ選択", ["💰 地金計算機", "📝 計算メモ", "📋 最新価格一覧表"])

if st.sidebar.button("🔄 最新相場に強制更新"):
    force_update()

st.sidebar.markdown("---")

# ==========================================
# コールバック関数
# ==========================================
def sync_inputs():
    if "weight_widget" in st.session_state: st.session_state.p_weight = st.session_state.weight_widget
    if "rate_sell_widget" in st.session_state: st.session_state.p_rate_sell = st.session_state.rate_sell_widget
    if "use_bukin_widget" in st.session_state: st.session_state.p_use_bukin = st.session_state.use_bukin_widget
    if "rate_buy_widget" in st.session_state: st.session_state.p_rate_buy = st.session_state.rate_buy_widget

def on_cat_change():
    sync_inputs()
    st.session_state.p_cat = st.session_state.cat_widget
    first_key = METAL_CATEGORIES[st.session_state.cat_widget][0]
    st.session_state.p_display = OPTIONS_MAP[first_key]

# ==========================================
# ページ1：地金計算機
# ==========================================
if page == "💰 地金計算機":
    st.title("💍 地金計算機")
    if st.session_state.update_time:
        st.caption(f"🕒 価格更新時刻: {st.session_state.update_time}")

    cat_index = list(METAL_CATEGORIES.keys()).index(st.session_state.p_cat)
    selected_cat = st.radio("金属を選択", options=list(METAL_CATEGORIES.keys()), index=cat_index, horizontal=True, key="cat_widget", on_change=on_cat_change)

    cat_options = [OPTIONS_MAP[k] for k in METAL_CATEGORIES[selected_cat]]
    try:
        display_index = cat_options.index(st.session_state.p_display)
    except ValueError:
        display_index = 0
        
    selected_display = st.radio("品位を選択", options=cat_options, index=display_index, horizontal=True, key="display_widget", on_change=lambda: setattr(st.session_state, 'p_display', st.session_state.display_widget))
    selected_key = [k for k, v in OPTIONS_MAP.items() if v == selected_display][0]

    weight = st.number_input("重量 (g)", min_value=0.0, value=st.session_state.p_weight, step=1.0, format="%.1f", key="weight_widget", on_change=sync_inputs)
    rate_sell = st.number_input("割合 (%)", min_value=0, max_value=100, value=st.session_state.p_rate_sell, step=5, key="rate_sell_widget", on_change=sync_inputs)
    
    # 👇 表記を「買い歩を適用する」に変更
    use_bukin = st.checkbox("買い歩を適用する", value=st.session_state.p_use_bukin, key="use_bukin_widget", on_change=sync_inputs)
    
    # 👇 表記を「買い歩 (%)」に変更
    rate_buy = st.number_input("歩金 (%)", min_value=0, max_value=20, value=st.session_state.p_rate_buy, step=1, key="rate_buy_widget", on_change=sync_inputs) if use_bukin else 0

    if st.session_state.all_prices and st.session_state.all_prices.get(selected_key):
        market_price = st.session_state.all_prices[selected_key]
        
        # 👇 表示内容を「品位・重量・単価」に変更
        st.info(f"品位: **{selected_display}** ｜ 重量: **{weight}g** ｜ 単価: **{market_price:,} 円/g**")
        
        if weight > 0:
            theory_total, sell_total, buy_total = calculate_prices(market_price, weight, rate_sell, use_bukin, rate_buy)
            st.markdown(f"""<div style="background-color: rgba(128, 128, 128, 0.05); padding: 15px; border-radius: 10px; text-align: center; border: 2px solid rgba(128, 128, 128, 0.3); margin-bottom: 10px;"><span style="font-size: 16px;">最大価格 (100%)</span><br><span style="font-size: 32px; font-weight: bold;">{theory_total:,.0f} 円</span></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div style="background-color: rgba(255, 75, 75, 0.1); padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #ff4b4b; margin-bottom: 10px;"><span style="font-size: 16px; color: #ff4b4b;">割合価格 ({rate_sell}%)</span><br><span style="font-size: 32px; font-weight: bold; color: #ff4b4b;">{sell_total:,.0f} 円</span></div>""", unsafe_allow_html=True)
            if use_bukin:
                st.markdown(f"""<div style="background-color: rgba(75, 137, 255, 0.1); padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #4b89ff; margin-bottom: 10px;"><span style="font-size: 16px; color: #4b89ff;">買い歩込価格 ({rate_buy}%)</span><br><span style="font-size: 32px; font-weight: bold; color: #4b89ff;">{buy_total:,.0f} 円</span></div>""", unsafe_allow_html=True)

            if st.button("💾 この結果をメモに保存", use_container_width=True):
                memo_entry = {
                    "datetime": datetime.now().strftime("%Y/%m/%d %H:%M"), "item": selected_display, "weight": f"{weight}g",
                    "theory": f"{theory_total:,.0f}円", "rate": f"{rate_sell}%", "sell_total": f"{sell_total:,.0f}円",
                    "buy_total": f"{buy_total:,.0f}円" if use_bukin else "-"
                }
                st.session_state.memo_list.append(memo_entry)
                st.success("メモに保存しました！")
    else:
        st.warning("⚠️ 相場データが読み込めていません。スプレッドシートのURLと公開設定を確認してください。")

# ==========================================
# ページ2：計算メモ
# ==========================================
elif page == "📝 計算メモ":
    st.title("📝 計算メモ")
    if not st.session_state.memo_list:
        st.info("保存されたメモはありません。")
    else:
        df = pd.DataFrame(st.session_state.memo_list)
        df.columns = ["日時", "品位", "重量", "最大価格", "割合(%)", "割合価格", "買い歩込価格"]
        st.table(df)
        if st.button("🗑️ すべてのメモを削除"):
            st.session_state.memo_list = []
            st.rerun()

# ==========================================
# ページ3：最新価格一覧表
# ==========================================
elif page == "📋 最新価格一覧表":
    st.title("📋 最新価格一覧表")
    if st.session_state.update_time:
        st.caption(f"🕒 価格更新時刻: {st.session_state.update_time}")

    if st.session_state.all_prices:
        for cat_label, keys in METAL_CATEGORIES.items():
            st.markdown(f"""<div style="background-color: rgba(128, 128, 128, 0.1); padding: 8px 15px; border-radius: 5px; margin-top: 20px; margin-bottom: 10px; border-left: 5px solid #888888;"><span style="font-weight: bold; font-size: 18px;">{cat_label}</span></div>""", unsafe_allow_html=True)
            category_html = '<div style="display: flex; flex-direction: column;">'
            for k in keys:
                price = st.session_state.all_prices.get(k)
                price_display = f"{price:,} 円" if price else "取得不可"
                display_name = OPTIONS_MAP[k]
                category_html += f"""<div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 10px; border-bottom: 1px solid rgba(128, 128, 128, 0.2); font-family: sans-serif;"><span style="font-weight: bold; font-size: 15px;">{display_name}</span><span style="color: #ff4b4b; font-weight: bold; font-size: 16px;">{price_display}</span></div>"""
            st.markdown(category_html + '</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ 相場データがありません。")

st.caption("※スプレッドシートから抽出した最新データです。")
