class Item:
    def __init__(self, item_id, name, description, usable=False):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.usable = usable

    def __repr__(self):
        return f"Item({self.item_id})"


# --- Common Items ---
small_potion = Item(
    item_id="small_potion",
    name="スモールポーション",
    description="HPを少し回復する小さなポーション。",
    usable=True,
)

ALL_ITEMS = {
    "small_potion": small_potion,
}
