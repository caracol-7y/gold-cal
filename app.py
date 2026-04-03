import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import get_all_prices_comprehensive
from calculator import calculate_prices

# ==========================================
# 1. iOS風 デザイン設定 (ナビゲーション強化)
# ==========================================
st.set_page_config(page_title="地金計算 Pro", page_icon="💰", layout="centered")

st.markdown("""
    <style>
    /* 全体フォント */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif !important;
    }
    
    /* メインコンテナ */
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 500px;
    }

    /* iOS風カード */
    .ios-card {
        background-color: rgba(128, 128, 128, 0.08);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(128, 128, 128, 0.1);
        margin-bottom: 15px;
        text-align: center;
    }

    /* 大きなナビゲーション（ラジオボタンをタブ風に改造） */
    div[data-testid="stRadio"] > div {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 5px;
        border-radius: 15px;
        gap: 5px;
    }
    div[data-testid="stRadio"] label {
        background-color: transparent;
        border-radius: 10px;
        padding: 10px 0 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        flex: 1;
        text-align: center;
        justify-content: center;
    }
    /* 選択中のタブ（Streamlitの仕様に合わせた色調整） */
    div[data-testid="stRadio"] label[data-baseweb="radio"] div:first-child {
        display: none; /* ラジオボタンの丸を消す */
    }
    
    /* 入力エリアの装飾 */
    .stNumberInput, .stCheckbox {
        background-color: rgba(128, 128, 128, 0.05);
        padding: 10px 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    
    /* 保存ボタン */
    .stButton>button {
        border-radius: 15px;
        background-color: #007AFF;
        color: white;
        border: none;
        padding: 15px;
        font-size: 18px;
        font-weight: 700;
        width: 100%;
        margin-top: 10px;
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

# ==========================================
# 2. セッション状態
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
# 3. データ取得
# ==========================================
@st.cache_data(ttl=3600)
def fetch_prices_cached():
    return get_all_prices_comprehensive()

try:
    prices, time_val = fetch_prices_cached()
    st.session_state.all_prices, st.session_state.update_time = prices, time_val
except Exception as e:
    st.error(f"データ取得エラー: {e}")

# ==========================================
# 4. メインナビゲーション (大きく表示)
# ==========================================
# サイドバーではなく、メイン画面最上部に配置
page = st.radio(
    "NAVIGATION", # ラベルはCSSで隠れますが識別用に必要
    ["💰 計算機", "📝 メモ", "📋 相場"],
    horizontal=True,
    label_visibility="collapsed" # ラベルを隠してタブのように見せる
)

st.markdown("---") # 区切り線

# 共通関数
def sync_inputs():
    for w, p in [("weight_widget", "p_weight"), ("rate_sell_widget", "p_rate_sell"), ("use_bukin_widget", "p_use_bukin"), ("rate_buy_widget", "p_rate_buy")]:
        if w in st.session_state: st.session_state[p] = st.session_state[w]

def on_cat_change():
    sync_inputs()
    st.session_state.p_cat = st.session_state.cat_widget
    st.session_state.p_display = OPTIONS_MAP[METAL_CATEGORIES[st.session_state.cat_widget][0]]

# ==========================================
# ページ1：地金計算機
# ==========================================
if page == "💰 計算機":
    st.markdown("<h1 style='text-align: center; font-size: 32px; font-weight: 800; margin-bottom: 0;'>地金計算機</h1>", unsafe_allow_html=True)
    if st.session_state.update_time:
        st.markdown(f"<p style='text-align: center; color: gray; font-size: 13px; margin-bottom: 20px;'>更新: {st.session_state.update_time}</p>", unsafe_allow_html=True)

    selected_cat = st.radio("金属", options=list(METAL_CATEGORIES.keys()), index=list(METAL_CATEGORIES.keys()).index(st.session_state.p_cat), horizontal=True, key="cat_widget", on_change=on_cat_change)
    cat_options = [OPTIONS_MAP[k] for k in METAL_CATEGORIES[selected_cat]]
    selected_display = st.radio("品位", options=cat_options, index=cat_options.index(st.session_state.p_display) if st.session_state.p_display in cat_options else 0, horizontal=True, key="display_widget", on_change=lambda: setattr(st.session_state, 'p_display', st.session_state.display_widget))
    
    selected_key = [k for k, v in OPTIONS_MAP.items() if v == selected_display][0]

    col1, col2 = st.columns(2)
    with col1: weight = st.number_input("重量 (g)", min_value=0.0, value=st.session_state.p_weight, step=1.0, format="%.1f", key="weight_widget", on_change=sync_inputs)
    with col2: rate_sell = st.number_input("割合 (%)", min_value=0, max_value=100, value=st.session_state.p_rate_sell, step=5, key="rate_sell_widget", on_change=sync_inputs)
    
    use_bukin = st.checkbox("買い歩を適用する", value=st.session_state.p_use_bukin, key="use_bukin_widget", on_change=sync_inputs)
    rate_buy = st.number_input("買い歩 (%)", min_value=0, max_value=20, value=st.session_state.p_rate_buy, step=1, key="rate_buy_widget", on_change=sync_inputs) if use_bukin else 0

    if st.session_state.all_prices and st.session_state.all_prices.get(selected_key):
        market_price = st.session_state.all_prices[selected_key]
        st.markdown(f'<div class="ios-card" style="background-color: rgba(0, 122, 255, 0.05); border: 1px solid rgba(0, 122, 255, 0.2);"><span style="font-size: 14px; color: #8e8e93;">{selected_display} ｜ {weight}g</span><br><span style="font-size: 20px; font-weight: 700;">{market_price:,} <small>円/g</small></span></div>', unsafe_allow_html=True)
        
        if weight > 0:
            theory_total, sell_total, buy_total = calculate_prices(market_price, weight, rate_sell, use_bukin, rate_buy)
            st.markdown(f'<div class="ios-card"><span style="font-size: 13px; color: gray;">最大価格 (100%)</span><br><span style="font-size: 28px; font-weight: 700;">¥{theory_total:,.0f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ios-card" style="border: 2px solid #ff4b4b; background-color: rgba(255, 75, 75, 0.05);"><span style="font-size: 13px; color: #ff4b4b;">割合価格 ({rate_sell}%)</span><br><span style="font-size: 32px; font-weight: 800; color: #ff4b4b;">¥{sell_total:,.0f}</span></div>', unsafe_allow_html=True)
            if use_bukin:
                st.markdown(f'<div class="ios-card" style="border: 2px solid #007AFF; background-color: rgba(0, 122, 255, 0.05);"><span style="font-size: 13px; color: #007AFF;">買い歩込価格 ({rate_buy}%)</span><br><span style="font-size: 32px; font-weight: 800; color: #007AFF;">¥{buy_total:,.0f}</span></div>', unsafe_allow_html=True)

            if st.button("💾 計算結果をメモに保存"):
                memo_entry = {"datetime": datetime.now().strftime("%H:%M"), "item": selected_display, "weight": f"{weight}g", "theory": f"¥{theory_total:,.0f}", "rate": f"{rate_sell}%", "sell_total": f"¥{sell_total:,.0f}", "buy_rate": f"{rate_buy}%", "buy_total": f"¥{buy_total:,.0f}" if use_bukin else "-"}
                st.session_state.memo_list.append(memo_entry)
                st.toast("保存しました")

# ==========================================
# ページ2：計算メモ
# ==========================================
elif page == "📝 メモ":
    st.markdown("<h1 style='text-align: center; font-size: 32px; font-weight: 800;'>計算メモ</h1>", unsafe_allow_html=True)
    if not st.session_state.memo_list:
        st.info("履歴はありません")
    else:
        for m in reversed(st.session_state.memo_list):
            buy_rate_val = m.get('buy_rate', '0%')
            buy_val = m['buy_total'] if m["buy_total"] != "-" else "-"
            buy_color = "#007AFF" if m["buy_total"] != "-" else "gray"
            st.markdown(f"""
<div class="ios-card" style="text-align: left; padding: 20px 12px;">
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 15px; border-bottom: 0.5px solid rgba(128, 128, 128, 0.2); padding-bottom: 10px;">
<span style="font-size: 19px; font-weight: 700;">{m['item']} ({m['weight']})</span>
<span style="color: gray; font-size: 12px;">{m['datetime']}</span>
</div>
<div style="display: flex; justify-content: space-between; text-align: center; align-items: flex-end;">
<div style="flex: 1;"><div style="font-size: 12px; color: gray; margin-bottom: 5px;">最大</div><div style="font-size: 20px; font-weight: 700; color: gray;">{m['theory']}</div></div>
<div style="flex: 1; border-left: 0.5px solid rgba(128, 128, 128, 0.2); border-right: 0.5px solid rgba(128, 128, 128, 0.2);"><div style="font-size: 12px; color: #ff4b4b; margin-bottom: 5px;">割合({m['rate']})</div><div style="font-size: 20px; font-weight: 800; color: #ff4b4b;">{m['sell_total']}</div></div>
<div style="flex: 1;"><div style="font-size: 12px; color: {buy_color}; margin-bottom: 5px;">買い歩({buy_rate_val})</div><div style="font-size: 20px; font-weight: 800; color: {buy_color};">{buy_val}</div></div>
</div>
</div>
""", unsafe_allow_html=True)
        if st.button("🗑️ 履歴をすべて削除"):
            st.session_state.memo_list = []
            st.rerun()

# ==========================================
# ページ3：最新価格一覧表
# ==========================================
elif page == "📋 相場":
    st.markdown("<h1 style='text-align: center; font-size: 32px; font-weight: 800;'>最新相場</h1>", unsafe_allow_html=True)
    if st.session_state.all_prices:
        for cat_label, keys in METAL_CATEGORIES.items():
            st.markdown(f"<p style='margin-left: 10px; margin-top: 20px; font-weight: 700; color: #8e8e93; font-size: 13px;'>{cat_label.upper()}</p>", unsafe_allow_html=True)
            html = '<div style="background-color: rgba(128,128,128,0.08); border-radius: 15px; overflow: hidden;">'
            for i, k in enumerate(keys):
                price = st.session_state.all_prices.get(k)
                price_display = f"{price:,} 円" if price else "取得不可"
                border = "border-bottom: 0.5px solid rgba(128,128,128,0.2);" if i < len(keys)-1 else ""
                html += f'<div style="display: flex; justify-content: space-between; padding: 15px; {border}"><span style="font-weight: 500;">{OPTIONS_MAP[k]}</span><span style="font-weight: 700; color: #ff4b4b;">{price_display}</span></div>'
            st.markdown(html + '</div>', unsafe_allow_html=True)

st.caption("※スプレッドシート参照")
