import streamlit as st
from datetime import datetime
import ui_parts
import config

# ローカルストレージを扱うためのライブラリ
from streamlit_local_storage import LocalStorage

st.set_page_config(page_title="地金計算 Pro", page_icon="💰", layout="centered")

# CSSファイルの読み込み
try:
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# ローカルストレージの初期化
local_storage = LocalStorage()

# ==========================================
# 💾 ローカルストレージからのデータ復元・初期化
# ==========================================
defaults = {
    'memo_list': [],
    'cat': "Gold",
    'display': "K18",
    'weight': 1.0,
    'rsell': 90,
    'ubukin': False,
    'rbuy': 5
}

for key, val in defaults.items():
    if key not in st.session_state:
        saved_val = local_storage.getItem(f"gold_cal_{key}")
        if saved_val is not None:
            st.session_state[key] = saved_val
        else:
            st.session_state[key] = val

# ==========================================
# 📱 サイドバーを自動で閉じるためのJavaScript制御
# ==========================================
if 'trigger_close' not in st.session_state:
    st.session_state.trigger_close = False

def on_menu_change():
    st.session_state.trigger_close = True

# サイドバーによるページ切り替え
page = st.sidebar.radio(
    "MENU", 
    ["💰 計算機", "📝 履歴", "📋 最新相場"], 
    label_visibility="collapsed",
    on_change=on_menu_change
)

if st.session_state.trigger_close:
    st.components.v1.html(
        """
        <script>
            const parentDoc = window.parent.document;
            const closeButton = parentDoc.querySelector('button[data-testid="stSidebarCollapseButton"]');
            if (closeButton) {
                closeButton.click();
            }
        </script>
        """,
        height=0,
        width=0
    )
    st.session_state.trigger_close = False


# 相場データの読み込み関数（キャッシュ化：120秒）
@st.cache_data(ttl=120)
def load_data():
    # 呼び出されたタイミングで scraper と calculator を読み込む（起動速度対策）
    from scraper import get_all_prices_comprehensive
    return get_all_prices_comprehensive()


# ==========================================
# 💰 1. 計算機ページ
# ==========================================
if page == "💰 計算機":
    # ★改善②: データの取得を待たずに、まずタイトルを最優先で描画
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>地金計算機</h1>", unsafe_allow_html=True)
    
    # UIが表示された後に、裏でデータをロード（ロード中はインジケーターを表示）
    with st.spinner("最新の相場データを取得中..."):
        from calculator import calculate_prices
        prices, update_time = load_data()
        
    st.markdown(f'<div style="text-align: right; color: gray; font-size: 0.8rem; margin-bottom: 10px;">更新日時: {update_time}</div>', unsafe_allow_html=True)
    
    def save_input(key):
        local_storage.setItem(f"gold_cal_{key}", st.session_state[key])

    cat = st.segmented_control("金属", options=list(config.METAL_CATEGORIES.keys()), key="cat", on_change=save_input, args=("cat",))
    
    available_options = config.METAL_CATEGORIES.get(cat, [])
    if available_options:
        current_disp = st.session_state.display
        if current_disp not in [config.OPTIONS_MAP.get(k, k) for k in available_options]:
            st.session_state.display = config.OPTIONS_MAP.get(available_options[0], available_options[0])
            save_input("display")
            
    disp_options = [config.OPTIONS_MAP.get(k, k) for k in available_options]
    disp = st.segmented_control("品位", options=disp_options, key="display", on_change=save_input, args=("display",))
    
    selected_key = None
    for k, v in config.OPTIONS_MAP.items():
        if v == disp and k in available_options:
            selected_key = k
            break
    if not selected_key and available_options:
        selected_key = available_options[0]
        
    m_price = prices.get(selected_key, 0) if prices else 0
    
    c1, c2 = st.columns(2)
    with c1:
        weight = st.number_input("重量(g)", min_value=0.0, step=0.1, format="%.1f", key="weight", on_change=save_input, args=("weight",))
    with c2:
        rsell = st.number_input("割合(%)", min_value=0, max_value=100, step=1, key="rsell", on_change=save_input, args=("rsell",))
        
    ubukin = st.checkbox("買い歩あり", key="ubukin", on_change=save_input, args=("ubukin",))
    rbuy = st.number_input("歩金 (%)", min_value=0, max_value=100, step=1, key="rbuy", on_change=save_input, args=("rbuy",)) if ubukin else 0
    
    if m_price > 0:
        ui_parts.render_market_info(disp, weight, m_price)
        if weight > 0:
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
                local_storage.setItem("gold_cal_memo_list", st.session_state.memo_list)
                st.toast("履歴に保存しました")

# ==========================================
# 📝 2. 履歴ページ
# ==========================================
elif page == "📝 履歴":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>計算履歴</h1>", unsafe_allow_html=True)
    if not st.session_state.memo_list:
        st.info("履歴はありません")
    else:
        for m in reversed(st.session_state.memo_list):
            ui_parts.render_history_card(m)
        if st.button("🗑️ すべての履歴を削除"):
            st.session_state.memo_list = []
            local_storage.setItem("gold_cal_memo_list", [])
            st.rerun()

# ==========================================
# 📋 3. 最新相場ページ
# ==========================================
elif page == "📋 最新相場":
    st.markdown("<h1 style='text-align: center; font-weight: 800;'>最新相場</h1>", unsafe_allow_html=True)
    
    with st.spinner("最新の相場データを取得中..."):
        prices, update_time = load_data()
        
    st.markdown(f'<div style="text-align: right; color: gray; font-size: 0.8rem; margin-bottom: 10px;">更新日時: {update_time}</div>', unsafe_allow_html=True)
    if prices:
        for label, keys in config.METAL_CATEGORIES.items():
            ui_parts.render_price_list(label, keys, prices, config.OPTIONS_MAP)
