import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import get_all_prices_comprehensive
from calculator import calculate_prices

# ==========================================
# 1. デザイン設定（サイドバーのボタンを巨大化）
# ==========================================
st.set_page_config(page_title="地金計算 Pro", page_icon="💰", layout="centered")

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    }
    .main .block-container { max-width: 500px; padding-top: 1rem; }

    /* サイドバーのメニューを巨大ボタンにする */
    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 15px;
        padding-top: 20px;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 15px !important;
        padding: 25px 15px !important;
        width: 100%;
        cursor: pointer;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        font-size: 22px !important;
        font-weight: 800 !important;
        text-align: center;
        width: 100%;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label div[data-baseweb="radio"] {
        display: none;
    }

    /* カードデザイン */
    .ios-card {
        background-color: rgba(128, 128, 128, 0.08);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(128, 128, 128, 0.1);
        margin-bottom: 15px;
        text-align: center;
    }

    /* 保存ボタン */
    .stButton>button {
        border-radius: 18px;
        background-color: #007AFF;
        color: white;
        padding: 18px;
        font-size: 18px;
        font-weight: 700;
        width: 100%;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# 定数
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

# 2. セッション状態の初期化
if 'memo_list' not in st.session_state: st.session_state.memo_list = []
if 'p_cat' not in st.session_state: st.session_state.p_cat = "Gold"
if 'p_display' not in st.session_state: st.session_state.p_display = "K18"
if 'p_weight' not in st.session_state: st.session_state.p_weight = 1.0
if 'p_rate_sell' not in st.session_state: st.session_state.p_rate_sell = 90
if 'p_use_bukin' not in st.session_state: st.session_state.p_use_bukin = False
if 'p_rate_buy' not in st.session_state: st.session_state.p_rate_buy = 5

# コールバック関数：入力値をセッションに同期
def sync_inputs():
    if "w_val" in st.session_state: st.session_state.p_weight = st.session_state.w_val
    if "r_sell_val" in st.session_state: st.session_state.p_rate_sell = st.session_state.r_sell_val
    if "bukin_on_off" in st.session_state: st.session_state.p_use_bukin = st.session_state.bukin_on_off
    if "r_buy_val" in st.session_state: st.session_state.p_rate_buy = st.session_state.r_buy_val

def on_cat_change():
    sync_inputs()
    st.session_state.p_cat = st.session_state.cat_widget
    st.session_state.p_display = OPTIONS_MAP[METAL_CATEGORIES[st.session_state.cat_widget][0]]

@st.cache_data(ttl=3600)
def fetch_data():
    try:
        return get_all_prices_comprehensive()
    except:
        return None, "取得失敗"

prices, update_time = fetch_data()

# サイドバーナビゲーション
st.sidebar.markdown("### MENU")
page = st.sidebar.radio("PAGE_SELECT", ["💰 計算機", "📝 履歴", "📋 最新相場"], label_visibility="collapsed")

# ==========================================
# ページ1：地金計算機
# ==========================================
if page == "💰 計算機":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>地金計算機</h1>", unsafe_allow_html=True)
    st.caption(f"最終更新: {update_time}")

    selected_cat = st.radio("金属", options=list(METAL_CATEGORIES.keys()), index=list(METAL_CATEGORIES.keys()).index(st.session_state.p_cat), horizontal=True, key="cat_widget", on_change=on_cat_change)
    
    cat_options = [OPTIONS_MAP[k] for k in METAL_CATEGORIES[selected_cat]]
    try:
        display_idx = cat_options.index(st.session_state.p_display)
    except:
        display_idx = 0

    selected_display = st.radio("品位", options=cat_options, index=display_idx, horizontal=True, key="display_widget", on_change=lambda: setattr(st.session_state, 'p_display', st.session_state.display_widget))
    
    selected_key = [k for k, v in OPTIONS_MAP.items() if v == selected_display][0]

    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("重量 (g)", min_value=0.0, value=st.session_state.p_weight, step=0.1, format="%.1f", key="w_val", on_change=sync_inputs)
    with col2:
        rate_sell = st.number_input("割合 (%)", min_value=0, max_value=100, value=st.session_state.p_rate_sell, step=1, key="r_sell_val", on_change=sync_inputs)
    
    use_bukin = st.checkbox("買い歩あり", value=st.session_state.p_use_bukin, key="bukin_on_off", on_change=sync_inputs)
    
    # 買い歩の数値入力も状態保持
    rate_buy = 0
    if use_bukin:
        rate_buy = st.number_input("買い歩 (%)", min_value=0, max_value=20, value=st.session_state.p_rate_buy, key="r_buy_val", on_change=sync_inputs)

    if prices and selected_key in prices:
        market_price = prices[selected_key]
        
        info_html = f"""
<div class="ios-card" style="background-color: rgba(0, 122, 255, 0.05); border: 1px solid rgba(0, 122, 255, 0.2);">
<span style="font-size: 14px; color: #8e8e93;">{selected_display} | {weight}g</span><br>
<span style="font-size: 22px; font-weight: 700;">{market_price:,} 円/g</span>
</div>
"""
        st.markdown(info_html, unsafe_allow_html=True)
        
        if weight > 0:
            theory_total, sell_total, buy_total = calculate_prices(market_price, weight, rate_sell, use_bukin, rate_buy)
            
            res_html = f"""
<div class="ios-card"><span style="font-size: 13px; color: gray;">最大価格 (100%)</span><br><span style="font-size: 28px; font-weight: 700;">¥{theory_total:,.0f}</span></div>
<div class="ios-card" style="border: 2px solid #ff4b4b; background-color: rgba(255, 75, 75, 0.05);"><span style="font-size: 13px; color: #ff4b4b;">割合価格 ({rate_sell}%)</span><br><span style="font-size: 32px; font-weight: 800; color: #ff4b4b;">¥{sell_total:,.0f}</span></div>
"""
            st.markdown(res_html, unsafe_allow_html=True)
            
            if use_bukin:
                buy_html = f'<div class="ios-card" style="border: 2px solid #007AFF; background-color: rgba(0, 122, 255, 0.05);"><span style="font-size: 13px; color: #007AFF;">買い歩 ({rate_buy}%)</span><br><span style="font-size: 32px; font-weight: 800; color: #007AFF;">¥{buy_total:,.0f}</span></div>'
                st.markdown(buy_html, unsafe_allow_html=True)

            if st.button("💾 この結果を保存"):
                memo_entry = {
                    "datetime": datetime.now().strftime("%m/%d %H:%M"),
                    "item": selected_display, "weight": f"{weight}g",
                    "theory": f"¥{theory_total:,.0f}", "rate": f"{rate_sell}%",
                    "sell_total": f"¥{sell_total:,.0f}", "buy_rate": f"{rate_buy}%",
                    "buy_total": f"¥{buy_total:,.0f}" if use_bukin else "-"
                }
                st.session_state.memo_list.append(memo_entry)
                st.toast("履歴に保存しました")

# ==========================================
# ページ2：計算履歴 (余白削減・コンパクト版)
# ==========================================
elif page == "📝 履歴":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>計算履歴</h1>", unsafe_allow_html=True)
    if not st.session_state.memo_list:
        st.info("保存された履歴はありません")
    else:
        for m in reversed(st.session_state.memo_list):
            br = m.get('buy_rate', '0%')
            bv = m['buy_total']
            bc = "#007AFF" if bv != "-" else "gray"
            
            st.markdown(f"""
<div class="ios-card" style="text-align: left; padding: 12px 10px;">
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; border-bottom: 0.5px solid rgba(128, 128, 128, 0.2); padding-bottom: 6px;">
<div style="flex: 1;"></div>
<div style="flex: 2; text-align: center;">
<span style="font-size: 17px; font-weight: 700;">{m['item']} ({m['weight']})</span>
</div>
<div style="flex: 1; text-align: right;">
<span style="color: gray; font-size: 10px; white-space: nowrap;">{m['datetime']}</span>
</div>
</div>

<div style="display: flex; justify-content: space-between; text-align: center; align-items: flex-end;">
<div style="flex: 1;">
<div style="font-size: 10px; color: gray; margin-bottom: 2px;">最大</div>
<div style="font-size: 18px; font-weight: 700; color: gray;">{m['theory']}</div>
</div>
<div style="flex: 1; border-left: 0.5px solid rgba(128, 128, 128, 0.2); border-right: 0.5px solid rgba(128, 128, 128, 0.2);">
<div style="font-size: 10px; color: #ff4b4b; margin-bottom: 2px;">割合({m['rate']})</div>
<div style="font-size: 18px; font-weight: 800; color: #ff4b4b;">{m['sell_total']}</div>
</div>
<div style="flex: 1;">
<div style="font-size: 10px; color: {bc}; margin-bottom: 2px;">買い歩({br})</div>
<div style="font-size: 18px; font-weight: 800; color: {bc};">{bv}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

        st.write("")
        if st.button("🗑️ すべての履歴を削除", use_container_width=True):
            st.session_state.memo_list = []
            st.rerun()

# ==========================================
# ページ3：最新相場
# ==========================================
elif page == "📋 最新相場":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>最新相場</h1>", unsafe_allow_html=True)
    if prices:
        for cat, keys in METAL_CATEGORIES.items():
            st.write(f"### {cat}")
            html_list = '<div style="background-color: rgba(128,128,128,0.08); border-radius: 15px; overflow: hidden; margin-bottom: 20px;">'
            for i, k in enumerate(keys):
                p = prices.get(k)
                txt = f"{p:,} 円" if p else "-"
                border = "border-bottom: 1px solid rgba(128,128,128,0.1);" if i < len(keys)-1 else ""
                html_list += f'<div style="display: flex; justify-content: space-between; padding: 15px; {border}"><span>{OPTIONS_MAP[k]}</span><span style="font-weight: 700; color: #ff4b4b;">{txt}</span></div>'
            html_list += '</div>'
            st.markdown(html_list, unsafe_allow_html=True)
