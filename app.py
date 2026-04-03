import streamlit as st
from datetime import datetime
from scraper import get_all_prices_comprehensive
from calculator import calculate_prices
import ui_parts
import config

st.set_page_config(page_title="地金計算 Pro", page_icon="💰", layout="centered")

with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 状態の初期化
if 'memo_list' not in st.session_state: st.session_state.memo_list = []
if 'p_cat' not in st.session_state: st.session_state.p_cat = "Gold"
if 'p_display' not in st.session_state: st.session_state.p_display = "K18"
if 'p_weight' not in st.session_state: st.session_state.p_weight = config.DEFAULT_SETTINGS["weight"]
if 'p_rate_sell' not in st.session_state: st.session_state.p_rate_sell = config.DEFAULT_SETTINGS["rate_sell"]
if 'p_use_bukin' not in st.session_state: st.session_state.p_use_bukin = config.DEFAULT_SETTINGS["use_bukin"]
if 'p_rate_buy' not in st.session_state: st.session_state.p_rate_buy = config.DEFAULT_SETTINGS["rate_buy"]

def sync():
    if "w_v" in st.session_state: st.session_state.p_weight = st.session_state.w_v
    if "r_s" in st.session_state: st.session_state.p_rate_sell = st.session_state.r_s
    if "b_o" in st.session_state: st.session_state.p_use_bukin = st.session_state.b_o
    if "r_b" in st.session_state: st.session_state.p_rate_buy = st.session_state.r_b

def cat_change():
    sync()
    st.session_state.p_cat = st.session_state.cat_w
    st.session_state.p_display = config.OPTIONS_MAP[config.METAL_CATEGORIES[st.session_state.cat_w][0]]

@st.cache_data(ttl=3600)
def fetch(): return get_all_prices_comprehensive()
prices, utime = fetch()

page = st.sidebar.radio("MENU", ["💰 計算機", "📝 履歴", "📋 最新相場"], label_visibility="collapsed")

if page == "💰 計算機":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>地金計算機</h1>", unsafe_allow_html=True)
    st.caption(f"最終更新: {utime}")
    cat = st.radio("金属", options=list(config.METAL_CATEGORIES.keys()), index=list(config.METAL_CATEGORIES.keys()).index(st.session_state.p_cat), horizontal=True, key="cat_w", on_change=cat_change)
    opts = [config.OPTIONS_MAP[k] for k in config.METAL_CATEGORIES[cat]]
    disp = st.radio("品位", options=opts, index=opts.index(st.session_state.p_display) if st.session_state.p_display in opts else 0, horizontal=True, key="disp_w", on_change=lambda: setattr(st.session_state, 'p_display', st.session_state.disp_w))
    key = [k for k, v in config.OPTIONS_MAP.items() if v == disp][0]
    
    c1, c2 = st.columns(2)
    with c1: weight = st.number_input("重量 (g)", min_value=0.0, value=st.session_state.p_weight, step=0.1, key="w_v", on_change=sync)
    with c2: rsell = st.number_input("割合 (%)", min_value=0, max_value=100, value=st.session_state.p_rate_sell, key="r_s", on_change=sync)
    ubukin = st.checkbox("買い歩を適用する", value=st.session_state.p_use_bukin, key="b_o", on_change=sync)
    rbuy = st.number_input("買い歩 (%)", min_value=0, value=st.session_state.p_rate_buy, key="r_b", on_change=sync) if ubukin else 0

    if prices and key in prices:
        m_price = prices[key]
        ui_parts.render_market_info(disp, weight, m_price)
        if weight > 0:
            th, sl, by = calculate_prices(m_price, weight, rsell, ubukin, rbuy)
            ui_parts.render_calc_results(th, sl, rsell, by if ubukin else None, f"{rbuy}%")
            if st.button("💾 この結果を保存"):
                st.session_state.memo_list.append({"datetime": datetime.now().strftime("%m/%d %H:%M"), "item": disp, "weight": f"{weight}g", "theory": f"¥{th:,.0f}", "rate": f"{rsell}%", "sell_total": f"¥{sl:,.0f}", "buy_rate": f"{rbuy}%", "buy_total": f"¥{by:,.0f}" if ubukin else "-"})
                st.toast("保存しました")

elif page == "📝 履歴":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>計算履歴</h1>", unsafe_allow_html=True)
    if not st.session_state.memo_list: st.info("履歴なし")
    else:
        for m in reversed(st.session_state.memo_list): ui_parts.render_history_card(m)
        if st.button("🗑️ すべて削除"):
            st.session_state.memo_list = []; st.rerun()

elif page == "📋 最新相場":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>最新相場</h1>", unsafe_allow_html=True)
    if prices:
        for l, ks in config.METAL_CATEGORIES.items(): ui_parts.render_price_list(l, ks, prices, config.OPTIONS_MAP)
