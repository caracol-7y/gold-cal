import streamlit as st

def render_market_info(display_name, weight, market_price):
    """市場価格カード (品位・重量 25px, 相場 26px)"""
    html = f'<div class="ios-card" style="background-color: rgba(0, 122, 255, 0.05); border: 1px solid rgba(0, 122, 255, 0.2); display: flex; justify-content: space-between; align-items: center; text-align: center; padding: 8px 10px;"><div style="flex: 1;"><div style="font-size: 13px; color: #8e8e93; margin-bottom: 2px;">品位</div><div style="font-size: 25px; font-weight: 700;">{display_name}</div></div><div style="flex: 1; border-left: 1px solid rgba(128, 128, 128, 0.2); border-right: 1px solid rgba(128, 128, 128, 0.2);"><div style="font-size: 13px; color: #8e8e93; margin-bottom: 2px;">重量</div><div style="font-size: 25px; font-weight: 700;">{weight:.1f}g</div></div><div style="flex: 1.5;"><div style="font-size: 13px; color: #8e8e93; margin-bottom: 2px;">相場</div><div style="font-size: 26px; font-weight: 700; color: #007AFF;">¥{market_price:,}/g</div></div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_calc_results(theory, sell, rate, buy=None, buy_rate=None):
    """計算結果カード (3つのカードを横並びで表示)"""
    # 3枚並べるため、価格のフォントサイズを24pxに調整
    html = '<div style="display: flex; gap: 8px; margin-bottom: 10px;">'
    
    # 1. 最大価格
    html += f'<div class="ios-card" style="flex: 1; text-align: center; padding: 8px 5px; margin-bottom: 0;">'
    html += f'<div style="font-size: 11px; color: gray; margin-bottom: 2px;">最大(100%)</div>'
    html += f'<div style="font-size: 24px; font-weight: 800;">¥{theory:,.0f}</div></div>'
    
    # 2. 割合価格
    html += f'<div class="ios-card" style="flex: 1; text-align: center; padding: 8px 5px; margin-bottom: 0; border: 2px solid #ff4b4b; background-color: rgba(255, 75, 75, 0.05);">'
    html += f'<div style="font-size: 11px; color: #ff4b4b; margin-bottom: 2px;">割合({rate}%)</div>'
    html += f'<div style="font-size: 24px; font-weight: 800; color: #ff4b4b;">¥{sell:,.0f}</div></div>'
    
    # 3. 歩金込価格 (有効な場合のみ)
    if buy is not None:
        html += f'<div class="ios-card" style="flex: 1; text-align: center; padding: 8px 5px; margin-bottom: 0; border: 2px solid #007AFF; background-color: rgba(0, 122, 255, 0.05);">'
        html += f'<div style="font-size: 11px; color: #007AFF; margin-bottom: 2px;">歩金込({buy_rate})</div>'
        html += f'<div style="font-size: 24px; font-weight: 800; color: #007AFF;">¥{buy:,.0f}</div></div>'
        
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_history_card(m):
    """履歴カード (タイトル 20px, 数値 20px)"""
    buy_val = m["buy_total"] if m["buy_total"] != "-" else "-"
    color_map = {"Gold": "#FFD700", "Platinum": "#87CEEB", "Silver": "#C0C0C0", "Palladium": "#FFFFFF"}
    m_color = color_map.get(m["metal"], "#FFFFFF")

    html = f'<div class="ios-card" style="padding: 8px 15px; margin-bottom: 10px;">'
    html += f'<div style="display: grid; grid-template-columns: 1fr auto 1fr; align-items: baseline; border-bottom: 1px solid rgba(128,128,128,0.1); padding-bottom: 5px; margin-bottom: 8px;">'
    html += f'<div></div>'
    html += f'<div style="text-align: center; font-weight: 800; font-size: 20px;"><span style="color: {m_color};">{m["metal"]} {m["item"]}</span> <span style="color: #FFFFFF; margin-left: 5px;">{m["weight"]}</span></div>'
    html += f'<div style="text-align: right; color: gray; font-size: 11px; white-space: nowrap;">{m["datetime"]}</div></div>'
    html += f'<div style="display: flex; justify-content: space-between; align-items: flex-start;">'
    html += f'<div style="flex: 1; text-align: center;"><div style="font-size: 11px; color: gray; margin-bottom: 2px;">最大価格</div><div style="font-weight: 700; font-size: 20px;">{m["theory"]}</div></div>'
    html += f'<div style="flex: 1; text-align: center; border-left: 1px solid rgba(128,128,128,0.1); border-right: 1px solid rgba(128,128,128,0.1);"><div style="font-size: 11px; color: #ff4b4b; margin-bottom: 2px;">割合({m["rate"]})</div><div style="font-weight: 800; font-size: 20px; color: #ff4b4b;">{m["sell_total"]}</div></div>'
    html += f'<div style="flex: 1; text-align: center;"><div style="font-size: 11px; color: #007AFF; margin-bottom: 2px;">歩金込({m["buy_rate"]})</div><div style="font-weight: 800; font-size: 20px; color: #007AFF;">{buy_val}</div></div>'
    html += f'</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_price_list(label, keys, prices, options_map):
    """最新相場リスト (品位 19px)"""
    st.markdown(f"<h3 style='margin-top: 10px; font-size: 20px;'>{label}</h3>", unsafe_allow_html=True)
    html = '<div class="ios-card" style="padding: 8px 12px;">'
    for k in keys:
        if k in prices:
            disp, val = options_map.get(k, k), prices[k]
            html += f'<div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(128,128,128,0.1);"><span style="font-weight: 700; font-size: 19px;">{disp}</span><span style="font-weight: 800; color: #007AFF; font-size: 22px;">¥{val:,}/g</span></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
