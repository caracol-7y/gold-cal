import streamlit as st
from datetime import datetime
from scraper import get_all_prices_comprehensive
from calculator import calculate_prices
import ui_parts
import config

st.set_page_config(page_title="地金計算 Pro", page_icon="💰", layout="centered")

# --- 【最終手段】CSSを外部ファイルではなく、ここに直接書く ---
st.html("""
<style>
    /* 全体フォント */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif !important;
    }

    .main .block-container {
        max-width: 500px;
        padding-top: 1.5rem !important;
    }

    .stAppDeployButton { display: none !important; }

    /* --- 金属・品位ボタン（Segmented Control）の強制巨大化 --- */
    /* 枠全体の高さを確保 */
    div[data-testid="stSegmentedControl"] {
        min-height: 120px !important; 
        padding: 10px !important;
        background-color: rgba(128, 128, 128, 0.1) !important;
        border-radius: 20px !important;
        display: flex !important;
        align-items: center !important;
    }

    /* ボタン自体のサイズ */
    div[data-testid="stSegmentedControl"] button {
        height: 90px !important; 
        min-height: 90px !important;
        border-radius: 15px !important;
        margin: 5px !important;
        flex: 1 !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
    }

    /* 中の文字を圧倒的に大きく（32px） */
    div[data-testid="stSegmentedControl"] button p {
        font-size: 32px !important; 
        font-weight: 900 !important;
        line-height: 1 !important;
        color: white !important;
    }

    /* 選択中の色 */
    div[data-testid="stSegmentedControl"] button[aria-selected="true"] {
        background-color: #007AFF !important;
    }

    /* --- その他パーツ --- */
    .ios-card {
        background-color: rgba(128, 128, 128, 0.08);
        border-radius: 22px;
        padding: 8px 15px;
        border: 1px solid rgba(128, 128, 128, 0.1);
        margin-bottom: 10px;
    }

    .stNumberInput input {
        font-size: 26px !important;
        font-weight: 700 !important;
    }

    .stButton>button {
        border-radius: 20px;
        background-color: #007AFF !important;
        color: white !important;
        padding: 15px;
        font-size: 24px;
        font-weight: 800;
    }
</style>
""")

# --- セッション状態の初期化 ---
if 'memo_list' not in st.session_state: st.session_state.memo_list = []
if 'p_cat' not in st.session_state: st.session_state.p_cat = "Gold"
if 'p_display' not in st.session_state: st.session_state.p_display = "K18"
if 'p_weight' not in st.session_state: st.session_state.p_weight = 1.0
if 'p_rsell' not in st.session_state: st.session_state.p_rsell = 90
if 'p_ubukin' not in st.session_state: st.session_state.p_ubukin = False
if 'p_rbuy' not in st.session_state: st.session_state.p_rbuy = 5

def update_state():
    st.session_state.p_weight = st.session_state.weight_key
    st.session_state.p_rsell = st.session_state.rsell_key
    st.session_state.p_ubukin = st.session_state.ubukin_key
    if 'rbuy_key' in st.session_state:
        st.session_state.p_rbuy = st.session_state.rbuy_key

def cat_change():
    new_cat = st.session_state.cat_w
    st.session_state.p_cat = new_cat
    if new_cat == "Gold": st.session_state.p_display = "K18"
    elif new_cat == "Platinum": st.session_state.p_display = "Pt900"
    elif new_cat == "Silver": st.session_state.p_display = "Sv1000"
    elif new_cat == "Palladium": st.session_state.p_display = "Bar"
    else: st.session_state.p_display = config.OPTIONS_MAP[config.METAL_CATEGORIES[new_cat][0]]

@st.cache_data(ttl=60)
def fetch(): return get_all_prices_comprehensive()
prices, utime = fetch()

page = st.sidebar.radio("MENU", ["💰 計算機", "📝 履歴", "📋 最新相場"], label_visibility="collapsed")

if page == "💰 計算機":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>地金計算機</h1>", unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: right; color: gray; font-size: 0.8rem; margin-bottom: 10px;">更新日時: {utime}</div>', unsafe_allow_html=True)
    
    # 金属選択
    cat = st.segmented_control("金属", options=list(config.METAL_CATEGORIES.keys()), selection_mode="single", default=st.session_state.p_cat, key="cat_w", on_change=cat_change)
    if not cat: cat = st.session_state.p_cat
    
    # 品位選択
    opts = [config.OPTIONS_MAP[k] for k in config.METAL_CATEGORIES[cat]]
    try:
        default_val = st.session_state.p_display if st.session_state.p_display in opts else opts[0]
    except:
        default_val = opts[0]
        
    disp = st.segmented_control("品位", options=opts, selection_mode="single", default=default_val, key="disp_w")
    if not disp: disp = default_val
    st.session_state.p_display = disp
    
    cat_keys = config.METAL_CATEGORIES[cat]
    key = [k for k in cat_keys if config.OPTIONS_MAP[k] == disp][0]
    
    # 入力
    c1, c2 = st.columns(2)
    with c1:
        weight = st.number_input("重量(g)", value=st.session_state.p_weight, step=0.1, format="%.1f", key="weight_key", on_change=update_state)
    with c2:
        rsell = st.number_input("割合(%)", value=st.session_state.p_rsell, step=1, key="rsell_key", on_change=update_state)
    
    ubukin = st.checkbox("買い歩あり", value=st.session_state.p_ubukin, key="ubukin_key", on_change=update_state)
    rbuy = st.number_input("歩金 (%)", min_value=0, value=st.session_state.p_rbuy, key="rbuy_key", on_change=update_state) if ubukin else 0

    if prices and key in prices:
        m_price = prices[key]
        ui_parts.render_market_info(disp, weight, m_price)
        if weight > 0:
            th, sl, by = calculate_prices(m_price, weight, rsell, ubukin, rbuy)
            ui_parts.render_calc_results(th, sl, rsell, by if ubukin else None, f"{rbuy}%")
            if st.button("💾 この結果を保存"):
                st.session_state.memo_list.append({
                    "datetime": datetime.now().strftime("%m/%d %H:%M"),
                    "metal": cat, "item": disp, "weight": f"{weight:.1f}g",
                    "theory": f"¥{th:,.0f}", "rate": f"{rsell}%", "sell_total": f"¥{sl:,.0f}",
                    "buy_rate": f"{rbuy}%", "buy_total": f"¥{by:,.0f}" if ubukin else "-"
                })
                st.toast("履歴に保存しました")

elif page == "📝 履歴":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>計算履歴</h1>", unsafe_allow_html=True)
    if not st.session_state.memo_list:
        st.info("履歴はありません")
    else:
        for m in reversed(st.session_state.memo_list):
            ui_parts.render_history_card(m)
        if st.button("🗑️ すべての履歴を削除"):
            st.session_state.memo_list = []; st.rerun()

elif page == "📋 最新相場":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>最新相場</h1>", unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: right; color: gray; font-size: 0.8rem; margin-bottom: 10px;">更新日時: {utime}</div>', unsafe_allow_html=True)
    if prices:
        for l, ks in config.METAL_CATEGORIES.items():
            ui_parts.render_price_list(l, ks, prices, config.OPTIONS_MAP)
