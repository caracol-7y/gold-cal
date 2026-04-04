import streamlit as st

def render_market_info(display_name, weight, market_price):
    """市場価格カード"""
    st.markdown(f"""
    <div class="ios-card" style="background-color: rgba(0, 122, 255, 0.05); border: 1px solid rgba(0, 122, 255, 0.2); display: flex; justify-content: space-between; align-items: center; text-align: center; padding: 12px 10px;">
        <div style="flex: 1;"><div style="font-size: 11px; color: #8e8e93; margin-bottom: 2px;">品位</div><div style="font-size: 18px; font-weight: 700;">{display_name}</div></div>
        <div style="flex: 1; border-left: 1px solid rgba(128, 128, 128, 0.2); border-right: 1px solid rgba(128, 128, 128, 0.2);"><div style="font-size: 11px; color: #8e8e93; margin-bottom: 2px;">重量</div><div style="font-size: 18px; font-weight: 700;">{weight:.1f}g</div></div>
        <div style="flex: 1.5;"><div style="font-size: 11px; color: #8e8e93; margin-bottom: 2px;">相場</div><div style="font-size: 18px; font-weight: 700; color: #007AFF;">¥{market_price:,}/g</div></div>
    </div>
    """, unsafe_allow_html=True)

def render_calc_results(theory, sell, rate, buy=None, buy_rate=None):
    """計算結果カード"""
    st.markdown(f'<div class="ios-card" style="text-align: center; padding: 10px;"><span style="font-size: 12px; color: gray;">最大価格 (100%)</span><br><span style="font-size: 26px; font-weight: 800;">¥{theory:,.0f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ios-card" style="border: 2px solid #ff4b4b; background-color: rgba(255, 75, 75, 0.05); text-align: center; padding: 10px;"><span style="font-size: 12px; color: #ff4b4b;">割合価格 ({rate}%)</span><br><span style="font-size: 26px; font-weight: 800; color: #ff4b4b;">¥{sell:,.0f}</span></div>', unsafe_allow_html=True)
    if buy is not None:
        st.markdown(f'<div class="ios-card" style="border: 2px solid #007AFF; background-color: rgba(0, 122, 255, 0.05); text-align: center; padding: 10px;"><span style="font-size: 12px; color: #007AFF;">歩金込価格 ({buy_rate})</span><br><span style="font-size: 26px; font-weight: 800; color: #007AFF;">¥{buy:,.0f}</span></div>', unsafe_allow_html=True)

def render_history_card(m):
    """履歴カード"""
    html = f"""
    <div class="ios-card" style="padding: 12px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: gray; font-size: 12px;">{m["datetime"]}</span>
            <span style="font-weight: 800; color: #007AFF;">{m["metal"]} - {m["item"]}</span>
        </div>
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 6px; margin-bottom: 6px;">
            <span class="history-weight">重量: {m["weight"]}</span>
            <span style="font-weight: 700; color: gray;">最大: {m["theory"]}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="color: #ff4b4b; font-size: 14px;">割合 ({m["rate"]})</span>
            <span style="color: #ff4b4b; font-weight: 800;">{m["sell_total"]}</span>
        </div>
    """
    if m["buy_total"] != "-":
        html += f'<div style="display: flex; justify-content: space-between;"><span style="color: #007AFF; font-size: 14px;">歩金 ({m["buy_rate"]})</span><span style="color: #007AFF; font-weight: 800;">{m["buy_total"]}</span></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_price_list(label, keys, prices, options_map):
    """相場リスト"""
    st.markdown(f"<h3 style='margin-top: 10px;'>{label}</h3>", unsafe_allow_html=True)
    html = '<div class="ios-card" style="padding: 10px;">'
    for k in keys:
        if k in prices:
            disp, val = options_map.get(k, k), prices[k]
            html += f'<div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(128,128,128,0.1);"><span style="font-weight: 700;">{disp}</span><span style="font-weight: 800; color: #007AFF;">¥{val:,}/g</span></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
