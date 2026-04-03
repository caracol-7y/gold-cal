# config.py

# ★重要：スプレッドシートの上から順に並べてください
ALL_METAL_KEYS = [
    "Gold_Ingot", "K24", "K22", "K21.6", "K20", "K18", "K14", "K10", "K9",
    "Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850",
    "Silver_Ingot", "Sv1000", "Sv925",
    "Pd_Ingot"
]

# カテゴリ分け（表示用）
METAL_CATEGORIES = {
    "Gold": ["Gold_Ingot", "K24", "K22", "K21.6", "K20", "K18", "K14", "K10", "K9"],
    "Platinum": ["Pt_Ingot", "Pt1000", "Pt950", "Pt900", "Pt850"],
    "Silver": ["Silver_Ingot", "Sv1000", "Sv925"],
    "Palladium": ["Pd_Ingot"]
}

# 画面に表示する名前
# config.py

# ... 他の設定 ...

# 表示名マップを書き換え
OPTIONS_MAP = {
    "Gold_Ingot": "Bar",
    "K24": "K24",
    "K22": "K22",
    "K21.6": "K21.6",
    "K20": "K20",
    "K18": "K18",
    "K14": "K14",
    "K10": "K10",
    "K9": "K9",
    "Pt_Ingot": "Bar",        # Platinum Bar -> Bar
    "Pt1000": "Pt1000",
    "Pt950": "Pt950",
    "Pt900": "Pt900",
    "Pt850": "Pt850",
    "Silver_Ingot": "Bar",    # Silver Bar -> Bar
    "Sv1000": "Sv1000",
    "Sv925": "Sv925",
    "Pd_Ingot": "Bar"         # Pd Bar -> Bar
}

# ... 他の設定 ...

DEFAULT_SETTINGS = {"weight": 1.0, "rate_sell": 90, "rate_buy": 5, "use_bukin": False}
