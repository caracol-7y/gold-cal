# app.py

import streamlit as st
from datetime import datetime
from scraper import get_all_prices_comprehensive
from calculator import calculate_prices
import ui_parts
import config

st.set_page_config(page_title="地金計算 Pro", page_icon="💰", layout="centered")

# CSS読み込み
try:
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# 状態管理
if 'memo_list' not in st.session_state: st.session_state.memo_list = []
if 'p_cat' not in st.session_state: st.session_state.p_cat = "Gold"
if 'p_display' not in st.session_state: st.session_state.p_display = "K18"

def sync():
    for k in ["w_v", "r_s", "b_o", "r_b"]:
        if k in st.session_state: st.session_state[f"p_{k}"] = st.session_state[k]

def cat_change():
    sync() # 現在の入力値を保持
    new_cat = st.session_state.cat_w
    st.session_state.p_cat = new_cat
    
    # 金属ごとにデフォルトの表示名（config.OPTIONS_MAPの右側の値）を指定
    if new_cat == "Gold":
        st.session_state.p_display = "K18"
    elif new_cat == "Platinum":
        st.session_state.p_display = "Pt900"
    elif new_cat == "Silver":
        st.session_state.p_display = "Sv1000"
    elif new_cat == "Palladium":
        st.session_state.p_display = "Bar"
    else:
        # 万が一設定がない場合はリストの先頭にする
        st.session_state.p_display = config.OPTIONS_MAP[config.METAL_CATEGORIES[new_cat][0]]

@st.cache_data(ttl=3600)
def fetch(): return get_all_prices_comprehensive()
prices, utime = fetch()

page = st.sidebar.radio("MENU", ["💰 計算機", "📝 履歴", "📋 最新相場"], label_visibility="collapsed")

if page == "💰 計算機":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>地金計算機</h1>", unsafe_allow_html=True)
    st.caption(f"最終更新: {utime}")
    
    cat = st.radio("金属", options=list(config.METAL_CATEGORIES.keys()), 
               index=list(config.METAL_CATEGORIES.keys()).index(st.session_state.p_cat), 
               horizontal=True, key="cat_w", on_change=cat_change)

    opts = [config.OPTIONS_MAP[k] for k in config.METAL_CATEGORIES[cat]]
    try:
        # 現在のセッション状態にある品位を選択状態にする
        d_idx = opts.index(st.session_state.p_display)
    except ValueError:
        d_idx = 0
    
    disp = st.radio("品位", options=opts, index=d_idx, horizontal=True, key="disp_w")
    st.session_state.p_display = disp # 選択された値を即座にセッションへ保存

    # ★修正ポイント：今選んでいるカテゴリ(cat)のキーの中から、表示名(disp)に一致するものを探す
    cat_keys = config.METAL_CATEGORIES[cat]
    key = [k for k in cat_keys if config.OPTIONS_MAP[k] == disp][0]
    
    c1, c2 = st.columns(2)
    with c1: weight = st.number_input("重量 (g)", min_value=0.0, value=st.session_state.get('p_w_v', 1.0), step=0.1, format="%.1f", key="w_v", on_change=sync)
    with c2: rsell = st.number_input("割合 (%)", min_value=0, max_value=100, value=st.session_state.get('p_r_s', 90), step=1, key="r_s", on_change=sync)
    ubukin = st.checkbox("買い歩あり", value=st.session_state.get('p_b_o', False), key="b_o", on_change=sync)
    rbuy = st.number_input("歩金 (%)", min_value=0, value=st.session_state.get('p_r_b', 5), key="r_b", on_change=sync) if ubukin else 0

    if prices and key in prices:
        m_price = prices[key]
        ui_parts.render_market_info(disp, weight, m_price)
        if weight > 0:
            th, sl, by = calculate_prices(m_price, weight, rsell, ubukin, rbuy)
            ui_parts.render_calc_results(th, sl, rsell, by if ubukin else None, f"{rbuy}%")
            
            if st.button("💾 この結果を保存"):
                st.session_state.memo_list.append({
                    "datetime": datetime.now().strftime("%m/%d %H:%M"),
                    "metal": cat, # ★金属名(Gold等)を保存
                    "item": disp, # ★Bar等を保存
                    "weight": f"{weight:.1f}g",
                    "theory": f"¥{th:,.0f}", "rate": f"{rsell}%", "sell_total": f"¥{sl:,.0f}",
                    "buy_rate": f"{rbuy}%", "buy_total": f"¥{by:,.0f}" if ubukin else "-"
                })
                st.toast("保存しました")

# app.py の「📝 履歴」セクションを修正

elif page == "📝 履歴":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>計算履歴</h1>", unsafe_allow_html=True)
    
    if not st.session_state.memo_list:
        st.info("履歴はありません")
    else:
        for i, m in enumerate(reversed(st.session_state.memo_list)):
            real_index = len(st.session_state.memo_list) - 1 - i
            
            # --- ここからレイアウトの工夫 ---
            # カードを表示する前に、ボタンをタイトルの位置に浮かせるためのコンテナ
            container = st.container()
            
            # カード本体を表示
            ui_parts.render_history_card(m)
            
            # ボタンをカードの「中」に見える位置に配置（マイナスマージンで調整）
            with container:
                # 3つのカラムでボタンをタイトルの左側に合わせる
                c_btn, c_empty = st.columns([1, 10])
                with c_btn:
                    # このボタンが「Gold K18」の左側に表示されます
                    st.write("") # 少し隙間を調整
                    if st.button("×", key=f"del_{real_index}", help="この履歴を削除"):
                        st.session_state.memo_list.pop(real_index)
                        st.rerun()
            
            # カード間の余白
            st.write("") 
        
        st.markdown("---")
        if st.button("🗑️ すべての履歴を削除", key="clear_all"):
            st.session_state.memo_list = []
            st.rerun()

elif page == "📋 最新相場":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>最新相場</h1>", unsafe_allow_html=True)
    if prices:
        for l, ks in config.METAL_CATEGORIES.items(): ui_parts.render_price_list(l, ks, prices, config.OPTIONS_MAP)
