import streamlit as st
from datetime import datetime
from scraper import get_all_prices_comprehensive
from calculator import calculate_prices
import ui_parts  # 自作の表示パーツ
import config    # 自作の設定ファイル

# ==========================================
# 1. 初期設定 & デザイン読み込み
# ==========================================
st.set_page_config(page_title="地金計算 Pro", page_icon="💰", layout="centered")

# style.css を読み込んで適用
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# セッション状態の初期化（リセット防止）
if 'memo_list' not in st.session_state: st.session_state.memo_list = []
if 'p_cat' not in st.session_state: st.session_state.p_cat = "Gold"
if 'p_display' not in st.session_state: st.session_state.p_display = "K18"
if 'p_weight' not in st.session_state: st.session_state.p_weight = config.DEFAULT_SETTINGS["weight"]
if 'p_rate_sell' not in st.session_state: st.session_state.p_rate_sell = config.DEFAULT_SETTINGS["rate_sell"]
if 'p_use_bukin' not in st.session_state: st.session_state.p_use_bukin = config.DEFAULT_SETTINGS["use_bukin"]
if 'p_rate_buy' not in st.session_state: st.session_state.p_rate_buy = config.DEFAULT_SETTINGS["rate_buy"]

# コールバック関数：入力値を保存
def sync_inputs():
    if "w_val" in st.session_state: st.session_state.p_weight = st.session_state.w_val
    if "r_sell_val" in st.session_state: st.session_state.p_rate_sell = st.session_state.r_sell_val
    if "bukin_on_off" in st.session_state: st.session_state.p_use_bukin = st.session_state.bukin_on_off
    if "r_buy_val" in st.session_state: st.session_state.p_rate_buy = st.session_state.r_buy_val

def on_cat_change():
    sync_inputs()
    st.session_state.p_cat = st.session_state.cat_widget
    st.session_state.p_display = config.OPTIONS_MAP[config.METAL_CATEGORIES[st.session_state.cat_widget][0]]

# データ取得
@st.cache_data(ttl=3600)
def fetch_data():
    return get_all_prices_comprehensive()

prices, update_time = fetch_data()

# ==========================================
# 2. サイドバー・ナビゲーション
# ==========================================
st.sidebar.markdown("### MENU")
page = st.sidebar.radio("NAV", ["💰 計算機", "📝 履歴", "📋 最新相場"], label_visibility="collapsed")

# ==========================================
# ページ1：地金計算機
# ==========================================
if page == "💰 計算機":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>地金計算機</h1>", unsafe_allow_html=True)
    st.caption(f"最終更新: {update_time}")

    # カテゴリ・品位選択
    selected_cat = st.radio("金属", options=list(config.METAL_CATEGORIES.keys()), index=list(config.METAL_CATEGORIES.keys()).index(st.session_state.p_cat), horizontal=True, key="cat_widget", on_change=on_cat_change)
    cat_opts = [config.OPTIONS_MAP[k] for k in config.METAL_CATEGORIES[selected_cat]]
    selected_display = st.radio("品位", options=cat_opts, index=cat_opts.index(st.session_state.p_display) if st.session_state.p_display in cat_opts else 0, horizontal=True, key="display_widget", on_change=lambda: setattr(st.session_state, 'p_display', st.session_state.display_widget))
    
    selected_key = [k for k, v in config.OPTIONS_MAP.items() if v == selected_display][0]

    # 数値入力
    col1, col2 = st.columns(2)
    with col1: weight = st.number_input("重量 (g)", min_value=0.0, value=st.session_state.p_weight, step=0.1, format="%.1f", key="w_val", on_change=sync_inputs)
    with col2: rate_sell = st.number_input("割合 (%)", min_value=0, max_value=100, value=st.session_state.p_rate_sell, step=1, key="r_sell_val", on_change=sync_inputs)
    
    use_bukin = st.checkbox("買い歩を適用する", value=st.session_state.p_use_bukin, key="bukin_on_off", on_change=sync_inputs)
    rate_buy = st.number_input("買い歩 (%)", min_value=0, max_value=20, value=st.session_state.p_rate_buy, key="r_buy_val", on_change=sync_inputs) if use_bukin else 0

    # 計算と表示
    if prices and selected_key in prices:
        market_price = prices[selected_key]
        ui_parts.render_market_info(selected_display, weight, market_price)
        
        if weight > 0:
            theory_total, sell_total, buy_total = calculate_prices(market_price, weight, rate_sell, use_bukin, rate_buy)
            ui_parts.render_calc_results(theory_total, sell_total, rate_sell, buy_total if use_bukin else None, f"{rate_buy}%")

            if st.button("💾 この結果を保存"):
                memo = {
                    "datetime": datetime.now().strftime("%m/%d %H:%M"), "item": selected_display, "weight": f"{weight}g",
                    "theory": f"¥{theory_total:,.0f}", "rate": f"{rate_sell}%", "sell_total": f"¥{sell_total:,.0f}",
                    "buy_rate": f"{rate_buy}%", "buy_total": f"¥{buy_total:,.0f}" if use_bukin else "-"
                }
                st.session_state.memo_list.append(memo)
                st.toast("保存しました")

# ==========================================
# ページ2：計算履歴
# ==========================================
elif page == "📝 履歴":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>計算履歴</h1>", unsafe_allow_html=True)
    if not st.session_state.memo_list:
        st.info("保存された履歴はありません")
    else:
        for m in reversed(st.session_state.memo_list):
            ui_parts.render_history_card(m)
        if st.button("🗑️ すべての履歴を削除"):
            st.session_state.memo_list = []
            st.rerun()

# ==========================================
# ページ3：最新相場
# ==========================================
elif page == "📋 最新相場":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>最新相場</h1>", unsafe_allow_html=True)
    if prices:
        for cat_label, keys in config.METAL_CATEGORIES.items():
            ui_parts.render_price_list(cat_label, keys, prices, config.OPTIONS_MAP)
