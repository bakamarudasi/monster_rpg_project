# Item definitions

class Item:
    def __init__(self, item_id, name, description, usable=False):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.usable = usable

    def __repr__(self):
        return f"Item({self.item_id})"

# ── 回復系・サポート系 ───────────────────────────────
small_potion = Item(
    item_id="small_potion",
    name="スモールポーション",
    description="HPを少し回復する小さなポーション。",
    usable=True,
)

medium_potion = Item(
    item_id="medium_potion",
    name="ミディアムポーション",
    description="HPを中程度回復するポーション。",
    usable=True,
)

large_potion = Item(
    item_id="large_potion",
    name="ラージポーション",
    description="HPを大きく回復する高級ポーション。",
    usable=True,
)

ether = Item(
    item_id="ether",
    name="エーテル",
    description="MPを中程度回復する神秘の液体。",
    usable=True,
)

antidote = Item(
    item_id="antidote",
    name="アンチドート",
    description="毒状態を治療する解毒薬。",
    usable=True,
)

elixir = Item(
    item_id="elixir",
    name="エリクサー",
    description="HPとMPを完全に回復する万能薬。",
    usable=True,
)

revive_scroll = Item(
    item_id="revive_scroll",
    name="リバイブスクロール",
    description="戦闘不能の味方1体を復活させる古文書。",
    usable=True,
)

# ── モンスター合成素材 ──────────────────────────────
magic_stone = Item(
    item_id="magic_stone",
    name="魔石",
    description="モンスター合成に用いられる不思議な石。合成研究所で特定の組み合わせに必須。",
)

dragon_scale = Item(
    item_id="dragon_scale",
    name="ドラゴンスケイル",
    description="若きドラゴンの鱗。強力な合成素材。",
)

abyss_shard = Item(
    item_id="abyss_shard",
    name="アビスシャード",
    description="闇の深淵で取れる黒水晶。ダークソウル系モンスターの合成に使う。",
)

celestial_feather = Item(
    item_id="celestial_feather",
    name="セレスティアルフェザー",
    description="光を宿す神鳥の羽根。高ランク合成素材。",
)

thunder_core = Item(
    item_id="thunder_core",
    name="サンダーコア",
    description="強力な電気エネルギーを帯びた核。",
)

frost_crystal = Item(
    item_id="frost_crystal",
    name="フロストクリスタル",
    description="極寒地で採れる冷気を封じ込めた氷晶。",
)

# ── 一括登録辞書 ─────────────────────────────────
ALL_ITEMS = {
    # 消耗品
    "small_potion": small_potion,
    "medium_potion": medium_potion,
    "large_potion": large_potion,
    "ether": ether,
    "antidote": antidote,
    "elixir": elixir,
    "revive_scroll": revive_scroll,
    # 合成素材
    "magic_stone": magic_stone,
    "dragon_scale": dragon_scale,
    "abyss_shard": abyss_shard,
    "celestial_feather": celestial_feather,
    "thunder_core": thunder_core,
    "frost_crystal": frost_crystal,
}
