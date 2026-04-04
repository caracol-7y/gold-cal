import streamlit as st

def render_market_info(display_name, weight, market_price):
    st.markdown(f"""
<div class="ios-card" style="background-color: rgba(0, 122, 255, 0.05); border: 1px solid rgba(0, 122, 255, 0.2); display: flex; justify-content: space-between; align-items: center; text-align: center; padding: 12px 10px;">
    <div style="flex: 1;">
        <div style="font-size: 11px; color: #8e8e93; margin-bottom: 2px;">品位</div>
        <div style="font-size: 18px; font-weight: 700;">{display_name}</div>
    </div>
    <div style="flex: 1; border-left: 1px solid rgba(128, 128, 128, 0.2); border-right: 1px solid rgba(128, 128, 128, 0.2);">
        <div style="font-size: 11px; color: #8e8e93; margin-bottom: 2px;">重量</div>
        <div style="font-size: 18px; font-weight: 700;">{weight:.1f}g</div>
    </div>
    <div style="flex: 1.5;">
        <div style="font-size: 11px; color: #8e8e93; margin-bottom: 2px;">相場</div>
        <div style="font-size: 18px; font-weight: 700; color: #007AFF;">¥{market_price:,}/g</div>
    </div>
</div>
""", unsafe_allow_html=True)

def render_calc_results(theory, sell, rate, buy=None, buy_rate=None):
    # スマホでも強制的に横並びにするHTML（改行なし・min-width:0指定）
    html = '<div style="display: flex; flex-direction: row; gap: 6px; align-items: stretch; margin-bottom: 12px;">'
    
    html += f'<div class="ios-card" style="flex: 1; text-align: center; padding: 8px 2px; margin: 0; min-width: 0;"><div style="font-size: 10px; color: gray; margin-bottom: 2px;">最大(100%)</div><div style="font-size: 18px; font-weight: 800; letter-spacing: -0.5px;">¥{theory:,.0f}</div></div>'
    
    html += f'<div class="ios-card" style="flex: 1; border: 2px solid #ff4b4b; background-color: rgba(255, 75, 75, 0.05); text-align: center; padding: 8px 2px; margin: 0; min-width: 0;"><div style="font-size: 10px; color: #ff4b4b; margin-bottom: 2px;">割合({rate}%)</div><div style="font-size: 18px; font-weight: 800; color: #ff4b4b; letter-spacing: -0.5px;">¥{sell:,.0f}</div></div>'
    
    if buy is not None:
        html += f'<div class="ios-card" style="flex: 1; border: 2px solid #007AFF; background-color: rgba(0, 122, 255, 0.05); text-align: center; padding: 8px 2px; margin: 0; min-width: 0;"><div style="font-size: 10px; color: #007AFF; margin-bottom: 2px;">歩金({buy_rate})</div><div style="font-size: 18px; font-weight: 800; color: #007AFF; letter-spacing: -0.5px;">¥{buy:,.0f}</div></div>'
        
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)

def render_history_card(m):
    br = m.get('buy_rate', '0%')
    bv = m['buy_total']
    bc = "#007AFF" if bv != "-" else "gray"
    
    metal = m.get('metal', '') 
    item = m.get('item', '')
    title = f"{metal} {item}".strip()
    m_class = f"metal-{metal.lower()}"
    
    st.markdown(f"""
<div class="ios-card">
    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; border-bottom: 0.5px solid rgba(128, 128, 128, 0.2); padding-bottom: 6px;">
        <div style="flex: 1;"></div>
        <div style="flex: 3; text-align: center;">
            <span style="font-size: 17px; font-weight: 700;">
                <span class="{m_class}">{title}</span>
                <span class="history-weight"> ({m['weight']})</span>
            </span>
        </div>
        <div style="flex: 1; text-align: right;">
            <span style="color: gray; font-size: 10px; white-space: nowrap;">{m['datetime']}</span>
        </div>
    </div>
    <div style="display: flex; justify-content: space-between; text-align: center; align-items: flex-end;">
        <div style="flex: 1;"><div style="font-size: 10px; color: gray;">最大</div><div style="font-size: 18px; font-weight: 700;">{m['theory']}</div></div>
        <div style="flex: 1; border-left: 0.5px solid rgba(128, 128, 128, 0.2); border-right: 0.5px solid rgba(128, 128, 128, 0.2);"><div style="font-size: 10px; color: #ff4b4b;">割合({m['rate']})</div><div style="font-size: 18px; font-weight: 800; color: #ff4b4b;">{m['sell_total']}</div></div>
        <div style="flex: 1;"><div style="font-size: 10px; color: {bc};">歩金({br})</div><div style="font-size: 18px; font-weight: 800; color: {bc};">{bv}</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

def render_price_list(category, keys, prices, options_map):
    st.markdown(f"<h3 style='font-weight: 700;'>{category}</h3>", unsafe_allow_html=True)
    for k in keys:
        if k in prices:
            st.markdown(f"""
<div style="display: flex; justify-content: space-between; padding: 12px 10px; border-bottom: 1px solid rgba(128, 128, 128, 0.2);">
<span style="font-size: 16px; font-weight: 500;">{options_map[k]}</span>
<span style="font-size: 16px; font-weight: 700;">{prices[k]:,} 円</span>
</div>
""", unsafe_allow_html=True)
