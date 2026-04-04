import streamlit as st

def render_market_info(display_name, weight, market_price):
    html = f'<div class="ios-card" style="background-color: rgba(0, 122, 255, 0.05); border: 1px solid rgba(0, 122, 255, 0.2); display: flex; justify-content: space-between; align-items: center; text-align: center; padding: 12px 10px;">'
    html += f'<div style="flex: 1;"><div style="font-size: 11px; color: #8e8e93; margin-bottom: 2px;">品位</div><div style="font-size: 18px; font-weight: 700;">{display_name}</div></div>'
    html += f'<div style="flex: 1; border-left: 1px solid rgba(128, 128, 128, 0.2); border-right: 1px solid rgba(128, 128, 128, 0.2);"><div style="font-size: 11px; color: #8e8e93; margin-bottom: 2px;">重量</div><div style="font-size: 18px; font-weight: 700;">{weight:.1f}g</div></div>'
    html += f'<div style="flex: 1.5;"><div style="font-size: 11px; color: #8e8e93; margin-bottom: 2px;">相場</div><div style="font-size: 18px; font-weight: 700; color: #007AFF;">¥{market_price:,}/g</div></div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_calc_results(theory, sell, rate, buy=None, buy_rate=None):
    # 最大価格
    st.markdown(f'<div class="ios-card" style="text-align: center; padding: 10px;"><span style="font-size: 12px; color: gray;">最大価格 (100%)</span><br><span style="font-size: 26px; font-weight: 800;">¥{theory:,.0f}</span></div>', unsafe_allow_html=True)
    # 割合価格
    st.markdown(f'<div class="ios-card" style="border: 2px solid #ff4b4b; background-color: rgba(255, 75, 75, 0.05); text-align: center; padding: 10px;"><span style="font-size: 12px; color: #ff4b4b;">割合価格 ({rate}%)</span><br><span style="font-size: 26px; font-weight: 800; color: #ff4b4b;">¥{sell:,.0f}</span></div>', unsafe_allow_html=True)
    # 歩金込価格
    if buy is not None:
        st.markdown(f'<div class="ios-card" style="border: 2px solid #007AFF; background-color: rgba(0, 122, 255, 0.05); text-align: center; padding: 10px;"><span style="font-size: 12px; color: #007AFF;">歩金込価格 ({buy_rate})</span><br><span style="font-size: 26px; font-weight: 800; color: #007AFF;">¥{buy:,.0f}</span></div>', unsafe_allow_html=True)
