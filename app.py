import streamlit as st
from datetime import datetime
from scraper import get_all_prices_comprehensive
from calculator import calculate_prices
import ui_parts
import config

st.set_page_config(page_title="地金計算 Pro", page_icon="💰", layout="centered")

try:
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

if 'memo_list' not in st.session_state: st.session_state.memo_list = []
if 'p_cat' not in st.session_state: st.session_state.p_cat = "Gold"
if 'p_display' not in st.session_state: st.session_state.p_display = "K18"

def sync():
    for k in ["w_v", "r_s", "b_o", "r_b"]:
        if f"p_{k}" in st.session_state: st.session_state[f"p_{k}"] = st.session_state[k]

def cat_change():
    sync()
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
    
    # --- 右詰めの更新日時 ---
    st.markdown(f"""
        <div style="text-align: right; color: gray; font-size: 0.8rem; margin-bottom: 10px;">
            更新日時: {utime}
        </div>
    """, unsafe_allow_html=True)
    
    # --- 金属選択 (セグメントコントロール) ---
    cat = st.segmented_control(
        "金属", 
        options=list(config.METAL_CATEGORIES.keys()), 
        selection_mode="single",
        default=st.session_state.p_cat,
        key="cat_w", 
        on_change=cat_change
    )
    # 選択が空になった場合のフォールバック
    if not cat: cat = st.session_state.p_cat
    
    # 品位の選択肢を取得
    opts = [config.OPTIONS_MAP[k] for k in config.METAL_CATEGORIES[cat]]
    
    # 現在の選択が新しいリストにあるか確認し、なければデフォルト(0番目)
    try:
        d_idx = opts.index(st.session_state.p_display)
        default_val = st.session_state.p_display
    except:
        default_val = opts[0]
        
    # --- 品位選択 (セグメントコントロール) ---
    disp = st.segmented_control(
        "品位", 
        options=opts, 
        selection_mode="single",
        default=default_val,
        key="disp_w"
    )
    if not disp: disp = default_val
    st.session_state.p_display = disp
    
    # スプレッドシート検索用のキーを特定
    cat_keys = config.METAL_CATEGORIES[cat]
    key = [k for k in cat_keys if config.OPTIONS_MAP[k] == disp][0]
    
    # --- 入力エリア ---
# お手元の c1, c2 に合わせた書き方です
    c1, c2 = st.columns(2)
    with c1:
        weight = st.number_input("重量(g)", value=1.0, step=0.1, format="%.1f")
    with c2:
        # ここが 'rate' になっているとエラーになります。必ず 'rsell' にしてください。
        rsell = st.number_input("割合(%)", value=100, step=1)
    
    ubukin = st.checkbox("買い歩あり", value=st.session_state.get('p_b_o', False), key="b_o", on_change=sync)
    
    if ubukin:
        rbuy = st.number_input(
            "歩金 (%)", 
            min_value=0, 
            value=st.session_state.get('p_r_b', 5), 
            key="r_b", 
            on_change=sync
        )
    else:
        rbuy = 0

    # --- 計算と結果表示 ---
    if prices and key in prices:
        m_price = prices[key]
        
        # 市場価格カード
        ui_parts.render_market_info(disp, weight, m_price)
        
        if weight > 0:
            # 計算実行 (rsell を渡す)
            th, sl, by = calculate_prices(m_price, weight, rsell, ubukin, rbuy)
            
            # 結果カード表示 (th, sl, rsell, buy, rate_label の順番で渡す)
            ui_parts.render_calc_results(th, sl, rsell, by if ubukin else None, f"{rbuy}%")
            
            # 保存ボタン
            if st.button("💾 この結果を保存"):
                st.session_state.memo_list.append({
                    "datetime": datetime.now().strftime("%m/%d %H:%M"),
                    "metal": cat,
                    "item": disp,
                    "weight": f"{weight:.1f}g",
                    "theory": f"¥{th:,.0f}", 
                    "rate": f"{rsell}%", 
                    "sell_total": f"¥{sl:,.0f}",
                    "buy_rate": f"{rbuy}%", 
                    "buy_total": f"¥{by:,.0f}" if ubukin else "-"
                })
                st.toast("履歴に保存しました")

elif page == "📝 履歴":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>計算履歴</h1>", unsafe_allow_html=True)
    if not st.session_state.memo_list:
        st.info("履歴はありません")
    else:
        for m in reversed(st.session_state.memo_list):
            ui_parts.render_history_card(m)
        st.markdown("---")
        if st.button("🗑️ すべての履歴を削除"):
            st.session_state.memo_list = []; st.rerun()

elif page == "📋 最新相場":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>最新相場</h1>", unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: right; color: gray; font-size: 0.8rem; margin-bottom: 10px;">更新日時: {utime}</div>', unsafe_allow_html=True)
    if prices:
        for l, ks in config.METAL_CATEGORIES.items():
            ui_parts.render_price_list(l, ks, prices, config.OPTIONS_MAP)
