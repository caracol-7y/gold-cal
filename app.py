import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import get_all_prices_comprehensive
from calculator import calculate_prices

# ==========================================
# 1. 共通設定・iOS風デザイン (巨大ボタンナビ)
# ==========================================
st.set_page_config(page_title="地金計算 Pro", page_icon="💰", layout="centered")

# デザイン設定（HTMLバグ防止のため左端に詰めて記述）
st.markdown("""
<style>
    /* 全体フォント */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif !important;
    }
    .main .block-container { max-width: 500px; padding-top: 1rem; }

    /* ★ 巨大ナビゲーションボタンのスタイル ★ */
    div[data-testid="stRadio"] > div {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 6px;
        border-radius: 18px;
        display: flex;
        justify-content: space-between;
        gap: 8px;
    }
    div[data-testid="stRadio"] label {
        background-color: transparent;
        border-radius: 14px;
        padding: 15px 0 !important; /* ボタンの高さを大きく */
        font-weight: 700 !important;
        font-size: 18px !important; /* 文字を大きく */
        flex: 1;
        text-align: center;
        justify-content: center;
        border: none !important;
        cursor: pointer;
    }
    /* ラジオボタンの丸を隠す */
    div[data-testid="stRadio"] label[data-baseweb="radio"] div:first-child {
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

    /* 入力パーツ */
    .stNumberInput, .stRadio, .stCheckbox {
        background-color: rgba(128, 128, 128, 0.05);
        padding: 12px;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    
    /* 青い保存ボタン */
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

# 定数定義
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

# セッション初期化
if 'memo_list' not in st.session_state: st.session_state.memo_list = []
if 'p_cat' not in st.session_state: st.session_state.p_cat = "Gold"
if 'p_display' not in st.session_state: st.session_state.p_display = "K18"

# データの取得 (1時間キャッシュ)
@st.cache_data(ttl=3600)
def fetch_data():
    try:
        return get_all_prices_comprehensive()
    except Exception:
        return None, "取得エラー"

prices, update_time = fetch_data()

# ==========================================
# 2. メインナビゲーション (巨大ボタン)
# ==========================================
# 画面の一番上に配置
page_label = st.radio(
    "MENU",
    ["💰 計算", "📝 履歴", "📋 相場"],
    horizontal=True,
    label_visibility="collapsed"
)

st.write("") # スペース用

# コールバック関数
def on_cat_change():
    st.session_state.p_cat = st.session_state.cat_widget
    st.session_state.p_display = OPTIONS_MAP[METAL_CATEGORIES[st.session_state.cat_widget][0]]

# ==========================================
# ページ1：地金計算機
# ==========================================
if page_label == "💰 計算":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>地金計算機</h1>", unsafe_allow_html=True)
    st.caption(f"最終更新: {update_time}")

    selected_cat = st.radio("金属", options=list(METAL_CATEGORIES.keys()), index=list(METAL_CATEGORIES.keys()).index(st.session_state.p_cat), horizontal=True, key="cat_widget", on_change=on_cat_change)
    cat_options = [OPTIONS_MAP[k] for k in METAL_CATEGORIES[selected_cat]]
    selected_display = st.radio("品位", options=cat_options, index=cat_options.index(st.session_state.p_display) if st.session_state.p_display in cat_options else 0, horizontal=True, key="display_widget", on_change=lambda: setattr(st.session_state, 'p_display', st.session_state.display_widget))
    
    selected_key = [k for k, v in OPTIONS_MAP.items() if v == selected_display][0]

    col1, col2 = st.columns(2)
    with col1: weight = st.number_input("重量 (g)", min_value=0.0, value=1.0, step=0.1, format="%.1f")
    with col2: rate_sell = st.number_input("割合 (%)", min_value=0, max_value=100, value=90, step=1)
    
    use_bukin = st.checkbox("買い歩を適用する", value=False)
    rate_buy = st.number_input("買い歩 (%)", min_value=0, max_value=20, value=5) if use_bukin else 0

    if prices and selected_key in prices:
        market_price = prices[selected_key]
        
        # センター情報ボックス
        st.markdown(f"""
<div class="ios-card" style="background-color: rgba(0, 122, 255, 0.05); border: 1px solid rgba(0, 122, 255, 0.2);">
<span style="font-size: 14px; color: #8e8e93;">{selected_display} | {weight}g</span><br>
<span style="font-size: 22px; font-weight: 700;">{market_price:,} 円/g</span>
</div>
""", unsafe_allow_html=True)
        
        if weight > 0:
            theory_total, sell_total, buy_total = calculate_prices(market_price, weight, rate_sell, use_bukin, rate_buy)
            
            st.markdown(f"""
<div class="ios-card"><span style="font-size: 13px; color: gray;">最大価格 (100%)</span><br><span style="font-size: 28px; font-weight: 700;">¥{theory_total:,.0f}</span></div>
<div class="ios-card" style="border: 2px solid #ff4b4b; background-color: rgba(255, 75, 75, 0.05);"><span style="font-size: 13px; color: #ff4b4b;">割合価格 ({rate_sell}%)</span><br><span style="font-size: 32px; font-weight: 800; color: #ff4b4b;">¥{sell_total:,.0f}</span></div>
""", unsafe_allow_html=True)
            
            if use_bukin:
                st.markdown(f"""
<div class="ios-card" style="border: 2px solid #007AFF;"><span style="font-size: 13px; color: #007AFF;">買い歩 ({rate_buy}%)</span><br><span style="font-size: 32px; font-weight: 800; color: #007AFF;">¥{buy_total:,.0f}</span></div>
""", unsafe_allow_html=True)

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
# ページ2：計算メモ (履歴)
# ==========================================
elif page_label == "📝 履歴":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>計算履歴</h1>", unsafe_allow_html=True)
    if not st.session_state.memo_list:
        st.info("保存された履歴はありません")
    else:
        for m in reversed(st.session_state.memo_list):
            br = m.get('buy_rate', '0%')
            bv = m['buy_total']
            bc = "#007AFF" if bv != "-" else "gray"
            st.markdown(f"""
<div class="ios-card" style="text-align: left; padding: 20px 12px;">
<div style="display: flex; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid rgba(128, 128, 128, 0.2); padding-bottom: 10px;">
<span style="font-size: 18px; font-weight: 700;">{m['item']} ({m['weight']})</span>
<span style="color: gray; font-size: 12px;">{m['datetime']}</span>
</div>
<div style="display: flex; justify-content: space-between; text-align: center;">
<div style="flex: 1;"><div style="font-size: 11px; color: gray;">最大</div><div style="font-size: 18px; font-weight: 700;">{m['theory']}</div></div>
<div style="flex: 1; border-left: 1px solid rgba(128,128,128,0.2); border-right: 1px solid rgba(128,128,128,0.2);"><div style="font-size: 11px; color: #ff4b4b;">割合({m['rate']})</div><div style="font-size: 18px; font-weight: 800; color: #ff4b4b;">{m['sell_total']}</div></div>
<div style="flex: 1;"><div style="font-size: 11px; color: {bc};">買い歩({br})</div><div style="font-size: 18px; font-weight: 800; color: {bc};">{bv}</div></div>
</div>
</div>
""", unsafe_allow_html=True)
        if st.button("🗑️ すべての履歴を削除"):
            st.session_state.memo_list = []
            st.rerun()

# ==========================================
# ページ3：最新相場一覧
# ==========================================
elif page_label == "📋 相場":
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
