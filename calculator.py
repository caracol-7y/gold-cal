def calculate_prices(market_price, weight, rate_sell, use_bukin=False, rate_buy=0):
    if weight <= 0 or market_price is None:
        return 0, 0, 0

    theory_total = market_price * weight
    sell_unit = market_price * (rate_sell / 100)
    sell_total = sell_unit * weight
    
    buy_total = None
    if use_bukin:
        buy_unit = sell_unit / (1 + (rate_buy / 100))
        buy_total = buy_unit * weight
        
    return theory_total, sell_total, buy_total