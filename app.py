import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import get_all_prices_comprehensive
from calculator import calculate_prices

# ==========================================
# 設定 (Secretsから読み込む)
# ==========================================
try:
    PHANTOM_API_KEY = st.secrets["PHANTOM_API_KEY"]
except Exception:
    PHANTOM_API_KEY = st.secrets.get("PHANTOM_API_KEY", "ak-b9gn3-wrv64-rxq31-n4mt7-95srr")
# ==========================================

st.set_page_config(page_title="地金価格管理システム Pro", page_icon="💰", layout="centered")

# --- セッション状態の初期化 ---
if 'all_prices' not in st.session_state:
    st.session_state.all_prices = None
if 'update_time' not in st.session_state:
    st.session_state.update_time = None
if 'memo_list' not in st.session_state:
    st.session_state.memo_list = []

# ==========================================
# サイドバー
# ==========================================
st.sidebar.title("⚙️ メニュー")
page = st.sidebar.radio("ページ選択", ["💰 価格計算機", "📋 最新価格一覧表", "📝 計算メモ"])

if st.sidebar.button("🔄 最新相場に更新"):
    with st.spinner("クラウド解析中..."):
        try:
            prices, time_val = get_all_prices_comprehensive(PHANTOM_API_KEY)
            if prices:
                st.session_state.all_prices = prices
                st.session_state.update_time = time_val
                st.sidebar.success("更新完了！")
            else:
                st.sidebar.error("更新失敗")
        except Exception as e:
            st.sidebar.error(str(e))

st.sidebar.markdown("---")
st.sidebar.markdown(
    '<a href="https://www.net-japan.co.jp/precious_metal_partner/" target="_blank" style="text-decoration: none; color: #0000EE; font-weight: bold;">🔗 公式サイトで価格を確認する</a>', 
    unsafe_allow_html=True
)

# ==========================================
# ページ1：価格計算機
# ==========================================
if page == "💰 価格計算機":
    st.title("💍 地金価格計算機")
    
    if st.session_state.update_time:
        st.caption(f"🕒 サイト更新時刻: {st.session_state.update_time}")
    else:
        st.warning("⚠️ 相場が取得できていません。サイドバーから「更新」してください。")

    metal_categories = {
        "Gold": ["Gold_Ingot", "K24", "K22", "K21.6", "K20", "K18", "K14", "K10", "K9", "Combo"],
        "Platinum": ["Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850"],
        "Silver": ["Silver_Ingot", "Sv1000", "Sv925"],
        "Palladium": ["Pd_Ingot"]
    }
    
    options_map = {
        "Gold_Ingot": "Gold Bar", "K24": "K24", "K22": "K22", "K21.6": "K21.6", "K20": "K20", "K18": "K18", "K14": "K14", "K10": "K10", "K9": "K9", "Combo": "金プラコンビ",
        "Pt_Ingot": "Platinum Bar", "Pt1000": "Pt1000", "Pt950": "Pt950", "Pt900": "Pt900", "Pt850": "Pt850",
        "Silver_Ingot": "Silver Bar", "Sv1000": "Sv1000", "Sv925": "Sv925",
        "Pd_Ingot": "Palladium Bar"
    }

    if 'selected_cat' not in st.session_state:
        st.session_state.selected_cat = "Gold"
    if 'selected_display' not in st.session_state:
        st.session_state.selected_display = "Gold Bar"
    if 'saved_weight' not in st.session_state:
        st.session_state.saved_weight = 1.0
    if 'saved_rate_sell' not in st.session_state:
        st.session_state.saved_rate_sell = 90
    if 'saved_use_bukin' not in st.session_state:
        st.session_state.saved_use_bukin = True
    if 'saved_rate_buy' not in st.session_state:
        st.session_state.saved_rate_buy = 5

    selected_cat = st.radio(
        "金属を選択", 
        options=list(metal_categories.keys()), 
        index=list(metal_categories.keys()).index(st.session_state.selected_cat),
        horizontal=True,
        key="cat_radio"
    )
    st.session_state.selected_cat = selected_cat

    cat_keys = metal_categories[selected_cat]
    cat_options = [options_map[k] for k in cat_keys]
    
    try:
        current_index = cat_options.index(st.session_state.selected_display)
    except ValueError:
        current_index = 0
        
    selected_display = st.radio(
        "品位を選択", 
        options=cat_options, 
        index=current_index,
        horizontal=True
    )
    st.session_state.selected_display = selected_display
    selected_key = [k for k, v in options_map.items() if v == selected_display][0]

    weight = st.number_input("重量 (g)", min_value=0.0, value=st.session_state.saved_weight, step=1.0, format="%.1f")
    st.session_state.saved_weight = weight

    rate_sell = st.number_input("割合 (%)", min_value=0, max_value=100, value=st.session_state.saved_rate_sell, step=5)
    st.session_state.saved_rate_sell = rate_sell

    use_bukin = st.checkbox("歩金を適用する", value=st.session_state.saved_use_bukin)
    st.session_state.saved_use_bukin = use_bukin
    
    if use_bukin:
        rate_buy = st.number_input("歩金 (%)", min_value=0, max_value=20, value=st.session_state.saved_rate_buy, step=1)
        st.session_state.saved_rate_buy = rate_buy
    else:
        rate_buy = 0

    if st.session_state.all_prices and st.session_state.all_prices.get(selected_key):
        market_price = st.session_state.all_prices[selected_key]
        st.info(f"現在の相場単価: **{market_price:,} 円/g**")
        
        if weight > 0:
            theory_total, sell_total, buy_total = calculate_prices(market_price, weight, rate_sell, use_bukin, rate_buy)
            
            st.markdown(f"""<div style="background-color: #ffffff; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #cccccc; margin-bottom: 10px;"><span style="font-size: 16px; color: #666;">最大価格 (100%)</span><br><span style="font-size: 32px; font-weight: bold; color: #333;">{theory_total:,.0f} 円</span></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div style="background-color: #fff0f0; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #ff4b4b; margin-bottom: 10px;"><span style="font-size: 16px; color: #ff4b4b;">割合価格 ({rate_sell}%)</span><br><span style="font-size: 32px; font-weight: bold; color: #ff4b4b;">{sell_total:,.0f} 円</span></div>""", unsafe_allow_html=True)
            
            if use_bukin and buy_total is not None:
                st.markdown(f"""<div style="background-color: #f0f7ff; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #4b89ff; margin-bottom: 10px;"><span style="font-size: 16px; color: #4b89ff;">買い歩込価格 ({rate_buy}%)</span><br><span style="font-size: 32px; font-weight: bold; color: #4b89ff;">{buy_total:,.0f} 円</span></div>""", unsafe_allow_html=True)

            st.write("")
            if st.button("💾 この結果をメモに保存", use_container_width=True):
                memo_entry = {
                    "datetime": datetime.now().strftime("%Y/%m/%d %H:%M"),
                    "item": selected_display,
                    "weight": f"{weight}g",
                    "theory": f"{theory_total:,.0f}円",
                    "rate": f"{rate_sell}%",
                    "sell_total": f"{sell_total:,.0f}円",
                    "buy_total": f"{buy_total:,.0f}円" if use_bukin else "-"
                }
                st.session_state.memo_list.append(memo_entry)
                st.success("メモに保存しました！")
    else:
        st.warning("⚠️ 相場が取得できていません。サイドバーから「更新」してください。")

# ==========================================
# ページ2：最新価格一覧表
# ==========================================
elif page == "📋 最新価格一覧表":
    st.title("📋 最新価格一覧表")
    if st.session_state.update_time:
        st.caption(f"🕒 サイト更新時刻: {st.session_state.update_time}")
    else:
        st.warning("⚠️ 相場が取得できていません。サイドバーから「更新」してください。")

    if st.session_state.all_prices:
        categories = {"金 (Gold)": ["Gold_Ingot", "K24", "K22", "K20", "K18", "K14", "K10", "K9"], "プラチナ (Platinum)": ["Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850"], "銀 (Silver)": ["Silver_Ingot", "Sv1000", "Sv925"], "パラジウム (Palladium)": ["Pd_Ingot"]}
        options_map = {"Gold_Ingot": "K24 インゴット", "K24": "K24", "K22": "K22", "K20": "K20", "K18": "K18", "K14": "K14", "K10": "K10", "K9": "K9", "Pt_Ingot": "Pt1000 インゴット", "Pt1000": "Pt1000", "Pt950": "Pt950", "Pt900": "Pt900", "Pt850": "Pt850", "Silver_Ingot": "Sv1000 インゴット", "Sv1000": "Sv1000", "Sv925": "Sv925", "Pd_Ingot": "Pd インゴット"}
        for cat, keys in categories.items():
            st.markdown(f"""<div style="background-color: #f0f2f6; padding: 8px 15px; border-radius: 5px; margin-top: 20px; margin-bottom: 10px; border-left: 5px solid #31333F;"><span style="font-weight: bold; font-size: 18px; color: #31333F;">{cat}</span></div>""", unsafe_allow_html=True)
            category_html = '<div style="display: flex; flex-direction: column;">'
            for k in keys:
                price = st.session_state.all_prices.get(k)
                price_display = f"{price:,} 円" if price else "取得不可"
                display_name = options_map[k]
                category_html += f"""<div style="display: flex; justify-content: space-between; align-items: center; background-color: #ffffff; padding: 12px 10px; border-bottom: 1px solid #eeeeee; font-family: sans-serif;"><span style="font-weight: bold; color: #333333; font-size: 15px;">{display_name}</span><span style="color: #ff0000; font-weight: bold; font-size: 16px;">{price_display}</span></div>"""
            category_html += '</div>'
            st.markdown(category_html, unsafe_allow_html=True)
            st.write("") 
    else:
        st.warning("⚠️ 相場が取得できていません。サイドバーから「更新」してください。")

# ==========================================
# ページ3：計算メモ
# ==========================================
elif page == "📝 計算メモ":
    st.title("📝 計算メモ")
    if not st.session_state.memo_list:
        st.info("保存されたメモはありません。計算機ページから保存してください。")
    else:
        df = pd.DataFrame(st.session_state.memo_list)
        df.columns = ["日時", "品位", "重量", "最大価格", "割合(%)", "割合価格", "買い歩込価格"]
        st.table(df)
        if st.button("🗑️ すべてのメモを削除"):
            st.session_state.memo_list = []
            st.rerun()

st.caption("※ネットジャパンのプリントページから抽出した最新データです。")