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

st.set_page_config(page_title="地金計算システム Pro", page_icon="💰", layout="centered")

# --- セッション状態の初期化 ---
if 'all_prices' not in st.session_state:
    st.session_state.all_prices = None
if 'update_time' not in st.session_state:
    st.session_state.update_time = None
if 'memo_list' not in st.session_state:
    st.session_state.memo_list = []
if 'close_sidebar_flag' not in st.session_state:
    st.session_state.close_sidebar_flag = False

# ==========================================
# 共通関数：相場データの更新
# ==========================================
def update_market_prices():
    with st.spinner("クラウド解析中..."):
        try:
            prices, time_val = get_all_prices_comprehensive(PHANTOM_API_KEY)
            if prices:
                st.session_state.all_prices = prices
                st.session_state.update_time = time_val
                return True
            else:
                return False
        except Exception as e:
            st.error(str(e))
            return False

# ==========================================
# サイドバー
# ==========================================
st.sidebar.title("⚙️ メニュー")

# ページ変更時にフラグを立てるコールバック関数を追加
def on_page_change():
    st.session_state.close_sidebar_flag = True

page = st.sidebar.radio(
    "ページ選択", 
    ["💰 地金計算機", "📝 計算メモ", "📋 最新価格一覧表"], 
    on_change=on_page_change
)

if st.sidebar.button("🔄 最新相場に更新", key="sidebar_update_btn"):
    if update_market_prices():
        st.sidebar.success("更新完了！")
        st.rerun()
    else:
        st.sidebar.error("更新失敗")

st.sidebar.markdown("---")
st.sidebar.markdown(
    '<a href="https://www.net-japan.co.jp/precious_metal_partner/" target="_blank" style="text-decoration: none; color: #0000EE; font-weight: bold;">🔗 公式サイトで価格を確認する</a>', 
    unsafe_allow_html=True
)

# ==========================================
# ページ1：地金計算機
# ==========================================
if page == "💰 地金計算機":
    st.title("💍 地金計算機")
    
    if st.session_state.update_time:
        st.caption(f"🕒 サイト更新時刻: {st.session_state.update_time}")
    else:
        st.warning("⚠️ 相場が取得できていません。下のボタンから最新相場を取得してください。")
        if st.button("🔄 相場データを取得する", key="main_top_update_btn"):
            if update_market_prices():
                st.success("更新完了！")
                st.rerun()
            else:
                st.error("更新失敗")

    metal_categories = {
        "Gold": ["Gold_Ingot", "K24", "K22", "K21.6", "K20", "K18", "K14", "K10", "K9"],
        "Platinum": ["Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850"],
        "Silver": ["Silver_Ingot", "Sv1000", "Sv925"],
        "Palladium": ["Pd_Ingot"]
    }
    
    options_map = {
        "Gold_Ingot": "Gold Bar", "K24": "K24", "K22": "K22", "K21.6": "K21.6", "K20": "K20", "K18": "K18", "K14": "K14", "K10": "K10", "K9": "K9",
        "Pt_Ingot": "Platinum Bar", "Pt1000": "Pt1000", "Pt950": "Pt950", "Pt900": "Pt900", "Pt850": "Pt850",
        "Silver_Ingot": "Silver Bar", "Sv1000": "Sv1000", "Sv925": "Sv925",
        "Pd_Ingot": "Palladium Bar"
    }

    # 入力保持用設定
    if 'p_cat' not in st.session_state:
        st.session_state.p_cat = "Gold"
    if 'p_display' not in st.session_state:
        st.session_state.p_display = "Gold Bar"
    if 'p_weight' not in st.session_state:
        st.session_state.p_weight = 1.0
    if 'p_rate_sell' not in st.session_state:
        st.session_state.p_rate_sell = 90
    if 'p_use_bukin' not in st.session_state:
        st.session_state.p_use_bukin = True
    if 'p_rate_buy' not in st.session_state:
        st.session_state.p_rate_buy = 5

    def sync_inputs():
        if "weight_widget" in st.session_state:
            st.session_state.p_weight = st.session_state.weight_widget
        if "rate_sell_widget" in st.session_state:
            st.session_state.p_rate_sell = st.session_state.rate_sell_widget
        if "use_bukin_widget" in st.session_state:
            st.session_state.p_use_bukin = st.session_state.use_bukin_widget
        if "rate_buy_widget" in st.session_state:
            st.session_state.p_rate_buy = st.session_state.rate_buy_widget

    def on_cat_change():
        sync_inputs()
        st.session_state.p_cat = st.session_state.cat_widget
        first_key = metal_categories[st.session_state.cat_widget][0]
        st.session_state.p_display = options_map[first_key]

    def on_display_change():
        st.session_state.p_display = st.session_state.display_widget

    cat_index = list(metal_categories.keys()).index(st.session_state.p_cat)
    selected_cat = st.radio("金属を選択", options=list(metal_categories.keys()), index=cat_index, horizontal=True, key="cat_widget", on_change=on_cat_change)

    cat_keys = metal_categories[selected_cat]
    cat_options = [options_map[k] for k in cat_keys]
    
    try:
        display_index = cat_options.index(st.session_state.p_display)
    except ValueError:
        display_index = 0
        
    selected_display = st.radio("品位を選択", options=cat_options, index=display_index, horizontal=True, key="display_widget", on_change=on_display_change)
    selected_key = [k for k, v in options_map.items() if v == selected_display][0]

    weight = st.number_input("重量 (g)", min_value=0.0, value=st.session_state.p_weight, step=1.0, format="%.1f", key="weight_widget", on_change=sync_inputs)
    rate_sell = st.number_input("割合 (%)", min_value=0, max_value=100, value=st.session_state.p_rate_sell, step=5, key="rate_sell_widget", on_change=sync_inputs)
    use_bukin = st.checkbox("買い歩を適用する", value=st.session_state.p_use_bukin, key="use_bukin_widget", on_change=sync_inputs)
    
    rate_buy = st.number_input("歩金 (%)", min_value=0, max_value=20, value=st.session_state.p_rate_buy, step=1, key="rate_buy_widget", on_change=sync_inputs) if use_bukin else 0

    if st.session_state.all_prices and st.session_state.all_prices.get(selected_key):
        market_price = st.session_state.all_prices[selected_key]
        st.info(f"現在の相場単価: **{market_price:,} 円/g**")
        
        if weight > 0:
            theory_total, sell_total, buy_total = calculate_prices(market_price, weight, rate_sell, use_bukin, rate_buy)
            
            # 背景色をベタ塗りではなく、rgba() を使って「色付きの半透明」にすることでダークモードに馴染ませる
            st.markdown(f"""<div style="background-color: rgba(128, 128, 128, 0.05); padding: 15px; border-radius: 10px; text-align: center; border: 2px solid rgba(128, 128, 128, 0.3); margin-bottom: 10px;"><span style="font-size: 16px;">最大価格 (100%)</span><br><span style="font-size: 32px; font-weight: bold;">{theory_total:,.0f} 円</span></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div style="background-color: rgba(255, 75, 75, 0.1); padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #ff4b4b; margin-bottom: 10px;"><span style="font-size: 16px; color: #ff4b4b;">割合価格 ({rate_sell}%)</span><br><span style="font-size: 32px; font-weight: bold; color: #ff4b4b;">{sell_total:,.0f} 円</span></div>""", unsafe_allow_html=True)
            
            if use_bukin and buy_total is not None:
                st.markdown(f"""<div style="background-color: rgba(75, 137, 255, 0.1); padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #4b89ff; margin-bottom: 10px;"><span style="font-size: 16px; color: #4b89ff;">買い歩込価格 ({rate_buy}%)</span><br><span style="font-size: 32px; font-weight: bold; color: #4b89ff;">{buy_total:,.0f} 円</span></div>""", unsafe_allow_html=True)

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
        st.warning("⚠️ 相場が取得できていません。上のボタンから最新相場を取得してください。")

# ==========================================
# ページ2：計算メモ (移動)
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

# ==========================================
# ページ3：最新価格一覧表 (移動)
# ==========================================
elif page == "📋 最新価格一覧表":
    st.title("📋 最新価格一覧表")
    if st.session_state.update_time:
        st.caption(f"🕒 サイト更新時刻: {st.session_state.update_time}")
    else:
        st.warning("⚠️ 相場が取得できていません。")
        if st.button("🔄 相場データを取得する", key="list_update_btn"):
            if update_market_prices():
                st.success("更新完了！")
                st.rerun()
            else:
                st.error("更新失敗")

    if st.session_state.all_prices:
        categories = {"金 (Gold)": ["Gold_Ingot", "K24", "K22", "K20", "K18", "K14", "K10", "K9"], "プラチナ (Platinum)": ["Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850"], "銀 (Silver)": ["Silver_Ingot", "Sv1000", "Sv925"], "パラジウム (Palladium)": ["Pd_Ingot"]}
        options_map = {"Gold_Ingot": "K24 インゴット", "K24": "K24", "K22": "K22", "K20": "K20", "K18": "K18", "K14": "K14", "K10": "K10", "K9": "K9", "Pt_Ingot": "Pt1000 インゴット", "Pt1000": "Pt1000", "Pt950": "Pt950", "Pt900": "Pt900", "Pt850": "Pt850", "Silver_Ingot": "Sv1000 インゴット", "Sv1000": "Sv1000", "Sv925": "Sv925", "Pd_Ingot": "Pd インゴット"}
        for cat, keys in categories.items():
            # ヘッダー部分（背景を半透明のグレーにし、文字色指定を削除してテーマに自動追従させる）
            st.markdown(f"""<div style="background-color: rgba(128, 128, 128, 0.1); padding: 8px 15px; border-radius: 5px; margin-top: 20px; margin-bottom: 10px; border-left: 5px solid #888888;"><span style="font-weight: bold; font-size: 18px;">{cat}</span></div>""", unsafe_allow_html=True)
            
            category_html = '<div style="display: flex; flex-direction: column;">'
            for k in keys:
                price = st.session_state.all_prices.get(k)
                price_display = f"{price:,} 円" if price else "取得不可"
                display_name = options_map[k]
                
                # 行部分（背景を透明に、文字色指定を削除、境界線を半透明のグレーに）
                category_html += f"""<div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 10px; border-bottom: 1px solid rgba(128, 128, 128, 0.2); font-family: sans-serif;"><span style="font-weight: bold; font-size: 15px;">{display_name}</span><span style="color: #ff4b4b; font-weight: bold; font-size: 16px;">{price_display}</span></div>"""
            
            category_html += '</div>'
            st.markdown(category_html, unsafe_allow_html=True)
            st.write("")

st.caption("※ネットジャパンのプリントページから抽出した最新データです。")

# ==========================================
# サイドバー自動格納の裏技（スマホ対応版 JSインジェクション）
# ==========================================
if st.session_state.close_sidebar_flag:
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
            try {
                const parentDoc = window.parent.document;
                
                // スマホ版のサイドバー内にある「×（閉じる）」ボタン
                const mobileCloseBtn = parentDoc.querySelector('[data-testid="stSidebarCollapseButton"]');
                // PC版のトグルボタン
                const pcToggleBtn = parentDoc.querySelector('[data-testid="collapsedControl"]');

                if (mobileCloseBtn) {
                    // スマホの場合はこちらをクリック
                    mobileCloseBtn.click();
                } else if (pcToggleBtn && pcToggleBtn.getAttribute('aria-expanded') === 'true') {
                    // PCの場合はこちらをクリック
                    pcToggleBtn.click();
                }
            } catch (e) {
                console.error("サイドバーを閉じる処理がブロックされました:", e);
            }
        </script>
        """,
        height=0,
        width=0,
    )
    # 実行後はフラグを戻す
    st.session_state.close_sidebar_flag = False
