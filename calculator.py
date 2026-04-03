# calculator.py

def calculate_prices(market_price, weight, rate_sell, use_bukin=False, rate_buy=0):
    """
    地金の各種価格を計算する関数
    
    Args:
        market_price (int): 1gあたりの相場価格
        weight (float): 重量(g)
        rate_sell (int): 買取割合(%)
        use_bukin (bool): 買い歩（手数料）を適用するか
        rate_buy (int): 買い歩の割合(%)
        
    Returns:
        tuple: (理論上の最大価格, 割合適用後の価格, 買い歩適用後の最終価格)
    """
    
    # 1. 理論価格 (100%) の計算
    theory_total = market_price * weight
    
    # 2. 割合価格 (%指定) の計算
    sell_total = theory_total * (rate_sell / 100)
    
    # 3. 買い歩込価格の計算
    # 割合価格からさらに指定の%分を差し引く（または調整する）計算
    if use_bukin:
        buy_total = sell_total * (1 - rate_buy / 100)
    else:
        buy_total = sell_total
        
    return theory_total, sell_total, buy_total
