import streamlit as st
from datetime import datetime
from scraper import get_all_prices_comprehensive
from calculator import calculate_prices
import ui_parts
import config

st.set_page_config(page_title="地金計算 Pro", page_icon="💰", layout="centered")

# CSSファイルの読み込み
try:
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# セッション状態の初期化
if 'memo_list' not in st.session_state: st.session_state.memo_list = []
if 'cat' not in st.session_state: st.session_state.cat = "Gold"
if 'display' not in st.session_state: st.session_state.display = "K18"
if 'weight' not in st.session_state: st.session_state.weight = 1.0
if 'rsell' not in st.session_state: st.session_state.rsell = 90
if 'ubukin' not in st.session_state: st.session_state.ubukin = False
if 'rbuy' not in st.session_state: st.session_state.rbuy = 5

# サイドバーによるページ切り替え
page = st.sidebar.selectbox("メニュー", ["💰 計算ツール", "📝 履歴"])

# 相場データの読み込み（キャッシュ化：120秒）
@st.cache_data(ttl=120)
def load_data():
    return get_all_prices_comprehensive()

prices, update_time = load_data()

if page == "💰 計算ツール":
    st.markdown(f"<p style='text-align: right; color: gray; font-size: 11px; margin-bottom: 0;'>データ更新: {update_time}</p>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-weight: 800; margin-top: 0;'>地金計算 Pro</h1>", unsafe_allow_html=True)

    # 1. 金属カテゴリ選択
    cat = st.segmented_control("貴金属", options=list(config.METAL_CATEGORIES.keys()), key="cat")

    # カテゴリが切り替わった場合の品位初期値の制御
    available_options = config.METAL_CATEGORIES.get(cat, [])
    if available_options:
        current_disp = st.session_state.display
        if current_disp not in [config.OPTIONS_MAP.get(k, k) for k in available_options]:
            st.session_state.display = config.OPTIONS_MAP.get(available_options[0], available_options[0])

    # 2. 品位の選択
    disp_options = [config.OPTIONS_MAP.get(k, k) for k in available_options]
    disp = st.segmented_control("品位", options=disp_options, key="display")

    # 選択された内部キーを特定
    selected_key = None
    for k, v in config.OPTIONS_MAP.items():
        if v == disp and k in available_options:
            selected_key = k
            break
    if not selected_key and available_options:
        selected_key = available_options[0]

    m_price = prices.get(selected_key, 0)

    # 入力フォームエリア
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("重量(g)", min_value=0.0, step=0.1, format="%.1f", key="weight")
    with col2:
        rsell = st.number_input("買取割合(%)", min_value=0, max_value=100, step=1, key="rsell")

    # 買い歩設定
    col_chk, col_num = st.columns([1, 1])
    with col_chk:
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        ubukin = st.checkbox("買い歩（歩金）を適用", key="ubukin")
    with col_num:
        rbuy = st.number_input("買い歩割合(%)", min_value=0, max_value=100, step=1, key="rbuy")

    # 最新相場カードの表示
    if m_price > 0:
        ui_parts.render_market_info(disp, weight, m_price)

    st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid rgba(128,128,128,0.1);'>", unsafe_allow_html=True)

    # 計算と結果表示
    if m_price > 0 and weight > 0:
        th, sl, by = calculate_prices(m_price, weight, rsell, ubukin, rbuy)
        ui_parts.render_calc_results(th, sl, rsell, by if ubukin else None, f"{rbuy}%")
        
        if st.button("💾 この結果を保存"):
            saved_buy_total = f"¥{by:,.0f}" if ubukin else "-"
            st.session_state.memo_list.append({
                "datetime": datetime.now().strftime("%m/%d %H:%M"),
                "metal": cat, 
                "item": disp, 
                "weight": f"{weight:.1f}g",
                "theory": f"¥{th:,.0f}", 
                "rate": f"{rsell}%", 
                "sell_total": f"¥{sl:,.0f}",
                "buy_rate": f"{rbuy}%", 
                "buy_total": saved_buy_total
            })
            st.toast("履歴に保存しました")

    # ★復活：最新相場一覧の表示エリア
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 2px solid rgba(128,128,128,0.2);'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-weight: 700; margin-bottom: 20px;'>📉 本日の最新相場一覧</h2>", unsafe_allow_html=True)
    
    # 4つのカテゴリそれぞれの相場リストを一括表示
    for label, keys in config.METAL_CATEGORIES.items():
        ui_parts.render_price_list(label, keys, prices, config.OPTIONS_MAP)

elif page == "📝 履歴":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>計算履歴</h1>", unsafe_allow_html=True)
    if not st.session_state.memo_list:
        st.info("履歴はありません")
    else:
        for m in reversed(st.session_state.memo_list):
            ui_parts.render_history_card(m)
        if st.button("🗑️ すべての履歴を削除"):
            st.session_state.memo_list = []
            st.rerun()
