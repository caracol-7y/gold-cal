import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import get_all_prices_comprehensive
from calculator import calculate_prices

st.set_page_config(page_title="地金計算システム Pro", page_icon="💰", layout="centered")

# --- セッション状態の初期化 ---
if 'all_prices' not in st.session_state:
    st.session_state.all_prices = None
if 'update_time' not in st.session_state:
    st.session_state.update_time = None
if 'memo_list' not in st.session_state:
    st.session_state.memo_list = []

# ==========================================
# 共通関数：相場データの自動取得（キャッシュ付き）
# ==========================================
@st.cache_data(ttl=3600) 
def fetch_prices_auto():
    return get_all_prices_comprehensive()

try:
    if st.session_state.all_prices is None:
        with st.spinner("最新相場を自動取得しています..."):
            prices, time_val = fetch_prices_auto()
    else:
        prices, time_val = fetch_prices_auto()

    if prices:
        st.session_state.all_prices = prices
        st.session_state.update_time = time_val
except Exception as e:
    st.error(f"自動取得エラー: {e}")

def force_update():
    fetch_prices_auto.clear()

# ==========================================
# サイドバー
# ==========================================
st.sidebar.title("⚙️ メニュー")
page = st.sidebar.radio("ページ選択", ["💰 地金計算機", "📝 計算メモ", "📋 最新価格一覧表"])

if st.sidebar.button("🔄 最新相場に強制更新", key="sidebar_update_btn"):
    force_update()
    st.sidebar.success("最新相場を取得しました！")
    st.rerun()

st.sidebar.markdown("---")

# ==========================================
# ページ1：地金計算機
# ==========================================
if page == "💰 地金計算機":
    st.title("💍 地金計算機")
    
    if st.session_state.update_time:
        st.caption(f"🕒 スプレッドシート更新時刻: {st.session_state.update_time}")
    else:
        st.warning("⚠️ 相場が取得できていません。下のボタンから最新相場を取得してください。")
        if st.button("🔄 相場データを取得する", key="main_top_update_btn"):
            force_update()
            st.success("更新完了！")
            st.rerun()

    metal_categories = {
        "Gold": ["Gold_Ingot", "K24", "K22", "K20", "K18", "K14", "K10", "K9"],
        "Platinum": ["Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850"],
        "Silver":
