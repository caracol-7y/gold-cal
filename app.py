import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import get_all_prices_comprehensive
from calculator import calculate_prices

# ==========================================
# 1. iOS風 グローバルデザイン設定
# ==========================================
st.set_page_config(page_title="地金計算 Pro", page_icon="💰", layout="centered")

st.markdown("""
    <style>
    /* フォントと全体の余白 */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", sans-serif !important;
    }
    .main .block-container {
        padding-top: 2rem;
        max-width: 500px;
    }

    /* iOS風カードデザイン */
    .ios-card {
        background-color: rgba(128, 128, 128, 0.08);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(128, 128, 128, 0.1);
        margin-bottom: 15px;
        text-align: center;
    }

    /* 入力パーツの装飾 */
    .stNumberInput, .stRadio, .stCheckbox {
        background-color: rgba(128, 128, 128, 0.05);
        padding: 10px 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    
    /* 青いボタン (iOSカラー) */
    .stButton>button {
        border-radius: 12px;
        background-color: #007AFF;
        color: white;
        border: none;
        padding: 12px;
        font-weight: 600;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- 共通定数 (エラー防止のため冒頭に配置) ---
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
# 影の変数 (入力保持用)
if 'p_cat' not in st.session_state: st.session_state.p_cat = "Gold"
if 'p_display' not in st.session_state: st.session_state.p_display = "K18"
if 'p_weight' not in st.session_state: st.session_state.p_weight = 1.0
if 'p_rate_sell' not in st.session_state: st.session_state.p_rate_sell = 90
if 'p_use_bukin' not in st.session_state: st.session_state.p_use_bukin = False # デフォルトOFF
if 'p_rate_buy' not in st.session_state: st.session_state.p_rate_buy = 5

# ==========================================
# 3. データ取得 (キャッシュ)
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

# ==========================================
# 4. サイドバー・共通関数
# ==========================================
st.sidebar.title("Settings")
page = st.sidebar.radio("メニュー", ["💰 地金計算機", "📝 計算メモ", "📋 最新価格一覧表"])

if st.sidebar.button("🔄 最新相場に強制更新"):
    fetch_prices_cached.clear()
    st.rerun()

def sync_inputs():
    if "weight_widget" in st.session_state: st.session_state.p_weight = st.session_state.weight_widget
    if "rate_sell_widget" in st.session_state: st.session_state.p_rate_sell = st.session_state.rate_sell_widget
    if "use_bukin_widget" in st.session_state: st.session_state.p_use_bukin = st.session_state.use_bukin_widget
    if "rate_buy_widget" in st.session_state: st.session_state.p_rate_buy = st.session_state.rate_buy_widget

def on_cat_change():
    sync_inputs()
    st.session_state.p_cat = st.session_state.cat_widget
    st.session_state.p_display = OPTIONS_MAP[METAL_CATEGORIES[st.session_state.cat_widget][0]]

# ==========================================
# ページ1：地金計算機
# ==========================================
if page == "💰 地金計算機":
    st.markdown("<h1 style='text-align: center; font-size: 32px; font-weight: 800; margin-bottom: 0;'>地金計算機</h1>", unsafe_allow_html=True)
    if st.session_state.update_time:
        st.markdown(f"<p style='text-align: center; color: gray; font-size: 13px; margin-bottom: 20px;'>更新: {st.session_state.update_time}</p>", unsafe_allow_html=True)

    # --- 入力セクション ---
    cat_index = list(METAL_CATEGORIES.keys()).index(st.session_state.p_cat)
    selected_cat = st.radio("金属を選択", options=list(METAL_CATEGORIES.keys()), index=cat_index, horizontal=True, key="cat_widget", on_change=on_cat_change)

    cat_options = [OPTIONS_MAP[k] for k in METAL_CATEGORIES[selected_cat]]
    try:
        display_index = cat_options.index(st.session_state.p_display)
    except ValueError:
        display_index = 0
    selected_display = st.radio("品位を選択", options=cat_options, index=display_index, horizontal=True, key="display_widget", on_change=lambda: setattr(st.session_state, 'p_display', st.session_state.display_widget))
    
    selected_key = [k for k, v in OPTIONS_MAP.items() if v == selected_display][0]

    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("重量 (g)", min_value=0.0, value=st.session_state.p_weight, step=1.0, format="%.1f", key="weight_widget", on_change=sync_inputs)
    with col2:
        rate_sell = st.number_input("割合 (%)", min_value=0, max_value=100, value=st.session_state.p_rate_sell, step=5, key="rate_sell_widget", on_change=sync_inputs)
    
    use_bukin = st.checkbox("買い歩を適用する", value=st.session_state.p_use_bukin, key="use_bukin_widget", on_change=sync_inputs)
    rate_buy = st.number_input("買い歩 (%)", min_value=0, max_value=20, value=st.session_state.p_rate_buy, step=1, key="rate_buy_widget", on_change=sync_inputs) if use_bukin else 0

    # --- 計算・表示セクション ---
    if st.session_state.all_prices and st.session_state.all_prices.get(selected_key):
        market_price = st.session_state.all_prices[selected_key]
        
        # センター情報ボックス (iOS風)
        st.markdown(f"""
            <div class="ios-card" style="background-color: rgba(0, 122, 255, 0.05); border: 1px solid rgba(0, 122, 255, 0.2);">
                <span style="font-size: 14px; color: #8e8e93;">{selected_display} ｜ {weight}g</span><br>
                <span style="font-size: 20px; font-weight: 700;">{market_price:,} <small>円/g</small></span>
            </div>
        """, unsafe_allow_html=True)
        
        if weight > 0:
            theory_total, sell_total, buy_total = calculate_prices(market_price, weight, rate_sell, use_bukin, rate_buy)
            
            st.markdown(f"""
                <div class="ios-card"><span style="font-size: 13px; color: gray;">最大価格 (100%)</span><br><span style="font-size: 28px; font-weight: 700;">¥{theory_total:,.0f}</span></div>
                <div class="ios-card" style="border: 2px solid #ff4b4b; background-color: rgba(255, 75, 75, 0.05);"><span style="font-size: 13px; color: #ff4b4b;">割合価格 ({rate_sell}%)</span><br><span style="font-size: 32px; font-weight: 800; color: #ff4b4b;">¥{sell_total:,.0f}</span></div>
            """, unsafe_allow_html=True)
            
            if use_bukin:
                st.markdown(f"""<div class="ios-card" style="border: 2px solid #007AFF; background-color: rgba(0, 122, 255, 0.05);"><span style="font-size: 13px; color: #007AFF;">買い歩込価格 ({rate_buy}%)</span><br><span style="font-size: 32px; font-weight: 800; color: #007AFF;">¥{buy_total:,.0f}</span></div>""", unsafe_allow_html=True)

            if st.button("💾 計算結果をメモに保存"):
                memo_entry = {
                    "datetime": datetime.now().strftime("%H:%M"), "item": selected_display, "weight": f"{weight}g",
                    "theory": f"¥{theory_total:,.0f}", "rate": f"{rate_sell}%", "sell_total": f"¥{sell_total:,.0f}",
                    "buy_total": f"¥{buy_total:,.0f}" if use_bukin else "-"
                }
                st.session_state.memo_list.append(memo_entry)
                st.toast("保存しました")
    else:
        st.warning("⚠️ 相場データを読み込めていません。")

# ==========================================
# ページ2：計算メモ
# ==========================================
elif page == "📝 計算メモ":
    st.markdown("<h1 style='text-align: center; font-size: 32px; font-weight: 800;'>計算メモ</h1>", unsafe_allow_html=True)
    if not st.session_state.memo_list:
        st.info("保存された履歴はありません")
    else:
        for m in reversed(st.session_state.memo_list):
            st.markdown(f"""
                <div class="ios-card" style="text-align: left; padding: 15px;">
                    <div style="display: flex; justify-content: space-between; color: gray; font-size: 12px;">
                        <span>{m['datetime']}</span><span>{m['item']} ({m['weight']})</span>
                    </div>
                    <div style="font-size: 20px; font-weight: 700; margin-top: 5px; color: #ff4b4b;">{m['sell_total']} <small style="font-size: 12px; color:gray;">({m['rate']})</small></div>
                    {f'<div style="font-size: 16px; color: #007AFF; font-weight: 600;">買い歩込: {m["buy_total"]}</div>' if m["buy_total"] != "-" else ""}
                </div>
            """, unsafe_allow_html=True)
        if st.button("🗑️ 履歴をすべて削除"):
            st.session_state.memo_list = []
            st.rerun()

# ==========================================
# ページ3：最新価格一覧表
# ==========================================
elif page == "📋 最新価格一覧表":
    st.markdown("<h1 style='text-align: center; font-size: 32px; font-weight: 800;'>最新相場</h1>", unsafe_allow_html=True)
    
    if st.session_state.all_prices:
        for cat_label, keys in METAL_CATEGORIES.items():
            st.markdown(f"<p style='margin-left: 10px; margin-top: 20px; font-weight: 700; color: #8e8e93; font-size: 13px;'>{cat_label.upper()}</p>", unsafe_allow_html=True)
            html = '<div style="background-color: rgba(128,128,128,0.08); border-radius: 15px; overflow: hidden;">'
            for i, k in enumerate(keys):
                price = st.session_state.all_prices.get(k)
                price_display = f"{price:,} 円" if price else "取得不可"
                border = "border-bottom: 0.5px solid rgba(128,128,128,0.2);" if i < len(keys)-1 else ""
                html += f"""
                    <div style="display: flex; justify-content: space-between; padding: 15px; {border}">
                        <span style="font-weight: 500;">{OPTIONS_MAP[k]}</span>
                        <span style="font-weight: 700; color: #ff4b4b;">{price_display}</span>
                    </div>
                """
            st.markdown(html + '</div>', unsafe_allow_html=True)

st.caption("※スプレッドシートから抽出した最新データです。")
