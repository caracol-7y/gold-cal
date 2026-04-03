import streamlit as st

def render_market_info(display_name, weight, market_price):
    st.markdown(f"""
<div class="ios-card" style="background-color: rgba(0, 122, 255, 0.05); border: 1px solid rgba(0, 122, 255, 0.2);">
<span style="font-size: 14px; color: #8e8e93;">{display_name} | {weight}g</span><br>
<span style="font-size: 22px; font-weight: 700;">{market_price:,} 円/g</span>
</div>
""", unsafe_allow_html=True)

def render_calc_results(theory, sell, rate, buy=None, buy_rate=None):
    st.markdown(f"""
<div class="ios-card"><span style="font-size: 13px; color: gray;">最大価格 (100%)</span><br><span style="font-size: 28px; font-weight: 700;">¥{theory:,.0f}</span></div>
<div class="ios-card" style="border: 2px solid #ff4b4b; background-color: rgba(255, 75, 75, 0.05);"><span style="font-size: 13px; color: #ff4b4b;">割合価格 ({rate}%)</span><br><span style="font-size: 32px; font-weight: 800; color: #ff4b4b;">¥{sell:,.0f}</span></div>
""", unsafe_allow_html=True)
    if buy is not None:
        st.markdown(f"""
<div class="ios-card" style="border: 2px solid #007AFF; background-color: rgba(0, 122, 255, 0.05);"><span style="font-size: 13px; color: #007AFF;">買い歩込価格 ({buy_rate})</span><br><span style="font-size: 32px; font-weight: 800; color: #007AFF;">¥{buy:,.0f}</span></div>
""", unsafe_allow_html=True)

def render_history_card(m):
    br = m.get('buy_rate', '0%')
    bv = m['buy_total']
    bc = "#007AFF" if bv != "-" else "gray"
    st.markdown(f"""
<div class="ios-card" style="text-align: left; padding: 12px 10px;">
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; border-bottom: 0.5px solid rgba(128, 128, 128, 0.2); padding-bottom: 6px;">
<div style="flex: 1;"></div>
<div style="flex: 2; text-align: center;"><span style="font-size: 17px; font-weight: 700;">{m['item']} ({m['weight']})</span></div>
<div style="flex: 1; text-align: right;"><span style="color: gray; font-size: 10px; white-space: nowrap;">{m['datetime']}</span></div>
</div>
<div style="display: flex; justify-content: space-between; text-align: center; align-items: flex-end;">
<div style="flex: 1;"><div style="font-size: 10px; color: gray; margin-bottom: 2px;">最大</div><div style="font-size: 18px; font-weight: 700; color: gray;">{m['theory']}</div></div>
<div style="flex: 1; border-left: 0.5px solid rgba(128, 128, 128, 0.2); border-right: 0.5px solid rgba(128, 128, 128, 0.2);"><div style="font-size: 10px; color: #ff4b4b; margin-bottom: 2px;">割合({m['rate']})</div><div style="font-size: 18px; font-weight: 800; color: #ff4b4b;">{m['sell_total']}</div></div>
<div style="flex: 1;"><div style="font-size: 10px; color: {bc}; margin-bottom: 2px;">買い歩({br})</div><div style="font-size: 18px; font-weight: 800; color: {bc};">{bv}</div></div>
</div>
</div>
""", unsafe_allow_html=True)

def render_price_list(label, keys, prices, options):
    st.write(f"### {label}")
    html = '<div style="background-color: rgba(128,128,128,0.08); border-radius: 15px; overflow: hidden; margin-bottom: 20px;">'
    for i, k in enumerate(keys):
        p = prices.get(k)
        txt = f"{p:,} 円" if p else "-"
        border = "border-bottom: 1px solid rgba(128,128,128,0.1);" if i < len(keys)-1 else ""
        html += f'<div style="display: flex; justify-content: space-between; padding: 15px; {border}"><span>{options[k]}</span><span style="font-weight: 700; color: #ff4b4b;">{txt}</span></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
