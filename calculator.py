# calculator.py

def calculate_prices(market_price, weight, rate_sell, use_bukin=False, rate_buy=0):
    """
    地金の各種価格を計算する関数
    
    Args:
        market_price (int): 1gあたりの相場価格
        weight (float): 重量(g)
        rate_sell (int): 買取割合(%)
        use_bukin (bool): 買い歩を適用するか
        rate_buy (int): 買い歩の割合(%)
        
    Returns:
        tuple: (理論上の最大価格, 割合価格, 買い歩込み価格)
    """
    
    # 1. 理論価格 (100%)
    theory_total = market_price * weight
    
    # 2. 割合価格 (%指定)
    sell_total = theory_total * (rate_sell / 100)
    
    # 3. 買い歩込み価格
    # ご指定の計算式: 割合価格 / (買い歩%/100 + 1) を適用
    if use_bukin:
        buy_total = sell_total / (rate_buy / 100 + 1)
    else:
        buy_total = sell_total
        
    return theory_total, sell_total, buy_total
