"""世界観コーデックス（ものがたり）。

ダークメルヘンの断章。序章は常時、エリア来歴は訪問で、ボス来歴は討伐で解禁される。
進めるほど世界の輪郭が見えてくる。
"""

from __future__ import annotations

PROLOGUE = (
    "むかしむかし――の、その先の話。\n"
    "語り部のいなくなった世界では、終われなかった童話たちが化け物になって彷徨っていた。"
    "毒の后、断頭の少女、紅い牙。頁の隙間から零れ落ちた者たちだ。\n"
    "あなたは一冊の白紙の本を抱え、彼らの“続き”を書きに行く。"
    "仲間を集め、掛け合わせ、育て――いつか『物語を喰らうもの』に辿り着くために。"
)

# location_id -> 来歴
AREA_LORE = {
    "torn_pages_rift": {"title": "裂けた頁の狭間", "text":
        "破れた本のあいだに生まれた裂け目。落丁した挿絵がそのまま魔物になって漂う。"},
    "forgotten_nursery": {"title": "忘却の児話区画", "text":
        "誰も読まなくなった子ども向けの童話が眠る区画。寝かしつけの歌が今も微かに響く。"},
    "graveyard_of_tales": {"title": "物語の墓標", "text":
        "完結を迎えられなかった物語が埋葬される丘。墓標には“つづく”とだけ刻まれている。"},
    "final_chapter_hall": {"title": "終章の間", "text":
        "すべての本の最終頁が集う大広間。ここを捲った者だけが、物語の終わりを知る。"},
}

# monster_id -> 来歴（討伐で解禁）
BOSS_LORE = {
    "poison_queen": {"title": "白雪の毒后", "text":
        "鏡に“一番美しいのは誰”と問い続けた后。答えを誤った鏡を割り、毒の林檎を世界中に配り歩く。"},
    "beheader_alice": {"title": "断頭のアリシア", "text":
        "“あなたの首をおはね！”――不思議の国から迷い出た少女。トランプの兵を従え、処刑遊戯に興じる。"},
    "crimson_hood": {"title": "紅ずきんの牙", "text":
        "狼に喰われた少女と、少女を喰った狼。二つが一つに溶け合い、紅い頭巾の獣となって森を駆ける。"},
    "sleeping_maiden": {"title": "硝子棺の眠り姫", "text":
        "永遠の眠りについたはずの姫。覚めぬまま夢の中で歌い続け、聴く者すべてを微睡みへ誘う。"},
    "match_ember": {"title": "マッチ売りの焔", "text":
        "凍えた夜に最後のマッチを擦った少女。願いの代わりに灯ったのは、世界を焼く煉獄の焔だった。"},
    "tale_devourer": {"title": "物語を喰らうもの", "text":
        "あらゆる童話の結末を喰い尽くす終焉そのもの。これを書き換えたとき、白紙の本に最後の一行が記される。"},
}


def codex_entries(player) -> list[dict]:
    entries = [{"title": "序章 ― 白紙の本", "text": PROLOGUE, "unlocked": True}]

    discovered = set(getattr(player, "exploration_progress", {}) or {})
    discovered.add(getattr(player, "current_location_id", None))
    for loc_id, lore in AREA_LORE.items():
        unlocked = loc_id in discovered
        entries.append({"title": lore["title"], "unlocked": unlocked,
                        "text": lore["text"] if unlocked else "（その地を訪れると明らかになる）"})

    flags = getattr(player, "story_flags", set()) or set()
    for mid, lore in BOSS_LORE.items():
        unlocked = f"defeated:{mid}" in flags
        entries.append({"title": lore["title"], "unlocked": unlocked,
                        "text": lore["text"] if unlocked else "（討伐すると語られる）"})
    return entries


def unlocked_count(player) -> tuple[int, int]:
    entries = codex_entries(player)
    return sum(1 for e in entries if e["unlocked"]), len(entries)
