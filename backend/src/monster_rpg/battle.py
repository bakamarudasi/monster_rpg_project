import random
from typing import cast, List, Dict, Any, Optional
from .player import Player
from .monsters import Monster
from .items.equipment import Equipment, EquipmentInstance, create_titled_equipment
from .skills.skills import Skill, ALL_SKILLS
from .skills.skill_actions import apply_effects

# Attribute compatibility multiplier definition
ELEMENTAL_MULTIPLIERS = {
    ("火", "風"): 1.5,
    ("風", "水"): 1.5,
    ("水", "火"): 1.5,
}

# Critical hit settings
CRITICAL_HIT_CHANCE = 0.1
CRITICAL_HIT_MULTIPLIER = 2.0

# --- Status effect definitions -------------------------------------------------------
def _status_damage(monster: Monster, amount: int, log: List[Dict[str, str]]):
    monster.hp -= amount
    log.append({'type': 'info', 'message': f"{monster.name} は {amount} のダメージを受けた！ (残りHP: {max(0, monster.hp)})"})
    if monster.hp <= 0:
        monster.is_alive = False
        log.append({'type': 'info', 'message': f"{monster.name} は倒れた！"})

def _status_heal(monster: Monster, amount: int, log: List[Dict[str, str]]):
    if not monster.is_alive:
        return
    before = monster.hp
    monster.hp = min(monster.max_hp, monster.hp + amount)
    healed = monster.hp - before
    if healed:
        log.append({'type': 'info', 'message': f"{monster.name} は {healed} 回復した！ (HP: {monster.hp})"})


def _slow_apply(monster: Monster):
    monster.apply_buff('speed', -5, 0)
    if monster.speed < 1:
        monster.apply_buff('speed', 1 - monster.speed, 0)

    def revert(m: Monster = monster):
        m.apply_buff('speed', 5, 0)
    return revert

def _charge_apply(monster: Monster):
    monster.apply_buff('defense', -5, 0)
    def revert(m: Monster = monster):
        m.apply_buff('defense', 5, 0)
    return revert

STATUS_DEFINITIONS = {
    "burn": {
        "duration": 3,
        "on_turn": lambda m, log: _status_damage(m, 3, log),
        "message": "やけど",
    },
    "poison": {
        "duration": 4,
        "on_turn": lambda m, log: _status_damage(m, 2, log),
        "message": "毒",
    },
    "spore_poison": {
        "duration": 3,
        "on_turn": lambda m, log: _status_damage(m, max(1, m.max_hp // 16), log),
        "message": "毒",
    },
    "freeze": {
        "duration": 2,
        "skip_turn": True,
        "message": "こおりつき",
    },
    "paralyze": {
        "duration": 3,
        "skip_chance": 0.5,
        "message": "まひ",
    },
    "regen": {
        "duration": 4,
        "on_turn": lambda m, log: _status_heal(m, 3, log),
        "message": "リジェネ",
    },
    "fear": {
        "duration": 2,
        "skip_chance": 0.25,
        "message": "おびえ",
    },
    "blind": {
        "duration": 3,
        "skip_chance": 0.2,
        "message": "盲目",
    },
    "slow": {
        "duration": 3,
        "message": "スロウ",
        "on_apply": lambda m: _slow_apply(m),
    },
    "silence": {
        "duration": 3,
        "message": "サイレンス",
    },
    "curse": {
        "duration": 4,
        "on_turn": lambda m, log: _status_damage(m, 1, log),
        "message": "呪い",
    },
    "stun": {
        "duration": 1,
        "skip_turn": True,
        "message": "気絶",
    },
    "sleep": {
        "duration": 3,
        "skip_turn": True,
        "message": "睡眠",
    },
    "confuse": {
        "duration": 3,
        "skip_chance": 0.5,
        "message": "混乱",
    },
    "taunt": {
        "duration": 2,
        "message": "挑発",
    },
    "cant_attack": {
        "duration": 1,
        "message": "攻撃不可",
    },
    "charging": {
        "duration": 2,
        "message": "チャージ",
        "on_apply": lambda m: _charge_apply(m),
    },
    "defending": {
        "duration": 1,
        "message": "防御",
    },
    "doom": {
        "duration": 3,
        "on_turn": lambda m, log: _status_damage(m, m.max_hp // 4, log) if m.status_effects and next((e for e in m.status_effects if e['name'] == 'doom' and e['remaining'] == 1), None) else None,
        "message": "終焉の刻印",
    },
    "counter_stance": {
        "duration": 1,
        "message": "カウンター構え",
    },
    "evade": {
        "duration": 1,
        "message": "回避",
    },
}

def apply_status(target: Monster, status_name: str, log: List[Dict[str, str]] | None, duration: int | None = None) -> None:
    if log is None:
        log = []
    data = STATUS_DEFINITIONS.get(status_name)
    if not data:
        log.append({'type': 'info', 'message': f"状態異常 {status_name} は未実装です。"})
        return
    dur = duration if duration is not None else data.get("duration", 1)
    entry = {"name": status_name, "remaining": dur}
    on_apply = data.get("on_apply")
    if callable(on_apply):
        try:
            remove_func = on_apply(target)
            if remove_func:
                entry["remove_func"] = remove_func
        except Exception as e:
            log.append({'type': 'error', 'message': f"状態異常 {status_name} の適用中にエラーが発生しました: {e}"})
    target.status_effects.append(entry)
    log.append({'type': 'info', 'message': f"{target.name} は{data['message']}状態になった！"})

def is_defending(monster: Monster) -> bool:
    return any(e["name"] == "defending" for e in monster.status_effects)

def defend(monster: Monster, log: List[Dict[str, str]]) -> None:
    apply_status(monster, "defending", log, 1)
    log.append({'type': 'info', 'message': f"{monster.name} は身を守っている！"})

def calculate_damage(attacker: Monster, defender: Monster, log: List[Dict[str, str]] | None = None) -> int:
    if log is None:
        log = []
    base = attacker.total_attack() - defender.total_defense()
    damage = max(1, base)

    multiplier = ELEMENTAL_MULTIPLIERS.get((attacker.element, defender.element))
    if multiplier is None:
        rev = ELEMENTAL_MULTIPLIERS.get((defender.element, attacker.element))
        if rev is not None:
            multiplier = 0.5
        else:
            multiplier = 1.0

    damage = int(damage * multiplier)

    if random.random() < CRITICAL_HIT_CHANCE:
        damage = int(damage * CRITICAL_HIT_MULTIPLIER)
        log.append({'type': 'info', 'message': "クリティカルヒット！"})

    if is_defending(defender):
        damage = int(damage * 0.5)

    if any(e["name"] == "evade" for e in defender.status_effects):
        log.append({'type': 'info', 'message': f"{defender.name} は攻撃を回避した！"})
        return 0

    return max(1, damage)

def apply_skill_effect(
    caster: Monster,
    targets: list[Monster],
    skill_obj: Skill,
    log: List[Dict[str, str]] | None,
    all_allies: list[Monster] | None = None,
    all_enemies: list[Monster] | None = None,
) -> None:
    if log is None:
        log = []
    log.append({'type': 'info', 'message': f"{caster.name} は {skill_obj.name} を使った！"})
    if skill_obj.cost > 0:
        caster.mp = max(0, caster.mp - skill_obj.cost)

    targets_to_use = targets
    if skill_obj.scope == "all":
        if skill_obj.target == "ally" and all_allies is not None:
            targets_to_use = [m for m in all_allies if m.is_alive]
        elif skill_obj.target == "enemy" and all_enemies is not None:
            targets_to_use = [m for m in all_enemies if m.is_alive]

    for target in targets_to_use:
        if not target.is_alive:
            log.append({'type': 'info', 'message': f"{target.name} は既に倒れているため、{skill_obj.name} の効果を受けなかった。"})
            continue

        if skill_obj.effects:
            apply_effects(caster, target, skill_obj.effects, skill_obj, log)
        else:
            log.append({'type': 'info', 'message': f"スキル '{skill_obj.name}' は効果がなかった..."})

def display_party_status(party: list[Monster], party_name: str, log: List[Dict[str, str]] | None):
    if log is None:
        log = []
    log.append({'type': 'info', 'message': f"--- {party_name} ---"})
    for i, monster in enumerate(party):
        status_mark = "💀" if not monster.is_alive else "❤️"
        log.append({'type': 'info', 'message': f"  {i + 1}. {monster.name} (Lv.{monster.level}, HP: {monster.hp}/{monster.max_hp}, MP: {monster.mp}/{monster.max_mp}) {status_mark}"})

def process_status_effects(monster: Monster, log: List[Dict[str, str]] | None) -> dict[str, bool]:
    if log is None:
        log = []
    expired = []
    skip_turn = False
    active_names = [e["name"] for e in monster.status_effects]
    for effect in list(monster.status_effects):
        name = effect["name"]
        data = STATUS_DEFINITIONS.get(name, {})
        on_turn = data.get("on_turn")
        if callable(on_turn):
            on_turn(monster, log)
            if not monster.is_alive:
                return {"skip_turn": True, "force_attack": False, "cant_attack": False} # Monster fainted
        if data.get("skip_turn"):
            skip_turn = True
        if "skip_chance" in data and random.random() < float(cast(float, data["skip_chance"])):
            skip_turn = True
        effect["remaining"] -= 1
        if effect["remaining"] <= 0:
            remove_cb = effect.get("remove_func")
            if callable(remove_cb):
                try:
                    remove_cb()
                except Exception as e:
                    log.append({'type': 'error', 'message': f"Error removing effect {e} from {monster.name}"})
            expired.append(effect)
    for e in expired:
        monster.status_effects.remove(e)
        msg = STATUS_DEFINITIONS.get(e["name"], {}).get("message", e["name"])
        log.append({'type': 'info', 'message': f"{monster.name} の {msg} が治った。"})
    return {
        "skip_turn": skip_turn,
        "force_attack": "taunt" in active_names,
        "cant_attack": "cant_attack" in active_names,
    }

def process_charge_state(actor: Monster, allies: list[Monster], enemies: list[Monster], log: List[Dict[str, str]] | None) -> bool:
    if log is None:
        log = []
    entry = next((e for e in actor.status_effects if e["name"] == "charging"), None)
    if not entry:
        return False
    if entry in actor.status_effects:
        actor.status_effects.remove(entry)
    remove_cb = entry.get("remove_func")
    if callable(remove_cb):
        try:
            remove_cb()
        except Exception as e:
            log.append({'type': 'error', 'message': f"Error removing charge effect from {actor.name}: {e}"})
    skill_id = entry.get("release_skill_id")
    if not skill_id:
        return False
    skill_obj = ALL_SKILLS.get(skill_id)
    if skill_obj is None:
        log.append({'type': 'error', 'message': f"不明な解放スキルID: {skill_id}"})
        return False
    targets: list[Monster] = []
    if skill_obj.target == "enemy":
        targets = [m for m in enemies if m.is_alive]
        if skill_obj.scope != "all" and targets:
            targets = [targets[0]]
    elif skill_obj.target == "ally":
        if skill_obj.scope == "all":
            targets = [m for m in allies if m.is_alive]
        else:
            targets = [actor]
    else:
        targets = [actor]
    if targets:
        apply_skill_effect(actor, targets, skill_obj, log, allies, enemies)
    return True

def is_party_defeated(party: list[Monster]) -> bool:
    return all(not monster.is_alive for monster in party)


def determine_turn_order(player_party: list[Monster], enemy_party: list[Monster]) -> list[Monster]:
    """Return monsters sorted by speed in descending order."""
    return sorted(player_party + enemy_party, key=lambda m: m.speed, reverse=True)

class Battle:
    def __init__(self, player_party: list[Monster], enemy_party: list[Monster], player: Player, log: Optional[List[Dict[str, str]]] = None, turn_order_monsters: Optional[List[Monster]] = None):
        self.player_party = player_party
        self.enemy_party = enemy_party
        self.player = player
        self.log = log if log is not None else []
        self.turn_count = 0
        self.finished = False
        self.outcome = ""
        self.current_actor: Optional[Monster] = None
        self.turn_order: List[Monster] = []

        all_monsters = self.player_party + self.enemy_party

        if turn_order_monsters:
            self.turn_order = turn_order_monsters
        else:
            for monster in all_monsters:
                monster.atb_gauge = random.randint(0, 50) # Initialize ATB gauge randomly

    def _update_turn_order(self):
        self.turn_order = sorted(
            [m for m in (self.player_party + self.enemy_party) if m.is_alive],
            key=lambda m: m.atb_gauge,
            reverse=True
        )

    def process_player_action(self, action: Dict[str, Any]):
        if self.finished:
            return

        actor = self.current_actor
        if not actor or actor not in self.player_party:
            self.log.append({'type': 'error', 'message': "あなたのターンではないか、行動可能な味方モンスターがいません。"})
            return

        self.log.append({'type': 'info', 'message': f"{actor.name} のターン！"})

        if action['type'] == 'run':
            if random.random() < 0.5: # 50% chance to flee
                self.log.append({'type': 'info', 'message': "うまく逃げ切れた！"})
                self.finished = True
                self.outcome = "fled"
            else:
                self.log.append({'type': 'info', 'message': "逃げ切れなかった！"})
            actor.reset_atb_gauge()
            return

        status_flags = process_status_effects(actor, self.log)
        if not actor.is_alive:
            self.log.append({'type': 'info', 'message': f"{actor.name} fainted due to status effect."})
            self._check_battle_end()
            actor.reset_atb_gauge()
            return
        if status_flags["skip_turn"]:
            self.log.append({'type': 'info', 'message': f"{actor.name} is unable to act due to status effect."})
            actor.reset_atb_gauge()
            return

        if process_charge_state(actor, self.player_party, self.enemy_party, self.log):
            actor.reset_atb_gauge()
            self._check_battle_end()
            return

        if action['type'] == 'attack':
            target_idx = action.get('target_enemy', 0)
            if target_idx == -1: # If no specific target, pick a random alive enemy
                alive_enemies = [m for m in self.enemy_party if m.is_alive]
                if alive_enemies:
                    target = random.choice(alive_enemies)
                else:
                    self.log.append({'type': 'info', 'message': "No enemies to attack!"})
                    actor.reset_atb_gauge()
                    return
            else:
                try:
                    target = self.enemy_party[target_idx]
                    if not target.is_alive:
                        self.log.append({'type': 'info', 'message': f"{target.name} is already defeated!"})
                        actor.reset_atb_gauge()
                        return
                except IndexError:
                    self.log.append({'type': 'error', 'message': "Invalid target selected."})
                    actor.reset_atb_gauge()
                    return

            self.log.append({'type': 'info', 'message': f"{actor.name} attacks {target.name}!"})
            damage = calculate_damage(actor, target, self.log)
            target.hp -= damage
            self.log.append({'type': 'info', 'message': f"{target.name} took {damage} damage! (HP: {max(0, target.hp)})"})
            if target.hp <= 0:
                target.is_alive = False
                self.log.append({'type': 'info', 'message': f"{target.name} fainted!"})
            else:
                if any(e["name"] == "counter_stance" for e in target.status_effects):
                    self.log.append({'type': 'info', 'message': f"{target.name} counters!"})
                    counter_damage = calculate_damage(target, actor, self.log)
                    actor.hp -= counter_damage
                    self.log.append({'type': 'info', 'message': f"{actor.name} took {counter_damage} damage! (HP: {max(0, actor.hp)})"})
                    if actor.hp <= 0:
                        actor.is_alive = False
                        self.log.append({'type': 'info', 'message': f"{actor.name} fainted!"})

        elif action['type'] == 'skill':
            skill_idx = action.get('skill', 0)
            try:
                skill_obj = actor.skills[skill_idx]
            except IndexError:
                self.log.append({'type': 'error', 'message': "Invalid skill selected."})
                actor.reset_atb_gauge()
                return

            if actor.mp < skill_obj.cost:
                self.log.append({'type': 'info', 'message': f"{actor.name} does not have enough MP for {skill_obj.name}!"})
                actor.reset_atb_gauge()
                return

            targets: List[Monster] = []
            if skill_obj.target == "enemy":
                if skill_obj.scope == "all":
                    targets = [m for m in self.enemy_party if m.is_alive]
                else:
                    target_idx = action.get('target_enemy', 0)
                    try:
                        target = self.enemy_party[target_idx]
                        if target.is_alive:
                            targets = [target]
                        else:
                            self.log.append({'type': 'info', 'message': f"{target.name} is already defeated!"})
                            actor.reset_atb_gauge()
                            return
                    except IndexError:
                        self.log.append({'type': 'error', 'message': "Invalid target selected for skill."})
                        actor.reset_atb_gauge()
                        return
            elif skill_obj.target == "ally":
                if skill_obj.scope == "all":
                    targets = [m for m in self.player_party if m.is_alive]
                else:
                    target_idx = action.get('target_ally', 0)
                    try:
                        target = self.player_party[target_idx]
                        if target.is_alive:
                            targets = [target]
                        else:
                            self.log.append({'type': 'info', 'message': f"{target.name} is already defeated!"})
                            actor.reset_atb_gauge()
                            return
                    except IndexError:
                        self.log.append({'type': 'error', 'message': "Invalid target selected for skill."})
                        actor.reset_atb_gauge()
                        return
            else: # self target
                targets = [actor]

            if targets:
                apply_skill_effect(actor, targets, skill_obj, self.log, self.player_party, self.enemy_party)
            else:
                self.log.append({'type': 'info', 'message': "No valid targets for skill."})

        elif action['type'] == 'item':
            item_idx = action.get('item_idx', 0)
            try:
                item_obj = self.player.items[item_idx]
            except IndexError:
                self.log.append({'type': 'error', 'message': "Invalid item selected."})
                actor.reset_atb_gauge()
                return

            target_idx = action.get('target_ally', 0)
            try:
                target_monster = self.player_party[target_idx]
                if not target_monster.is_alive:
                    self.log.append({'type': 'info', 'message': f"{target_monster.name} is already defeated!"})
                    actor.reset_atb_gauge()
                    return
            except IndexError:
                self.log.append({'type': 'error', 'message': "Invalid target selected for item."})
                actor.reset_atb_gauge()
                return

            if item_obj.use(target_monster, self.log):
                self.player.items.pop(item_idx)
            else:
                self.log.append({'type': 'info', 'message': f"Could not use {item_obj.name}."})

        elif action['type'] == 'scout':
            target_idx = action.get('target_enemy', 0)
            try:
                target_monster = self.enemy_party[target_idx]
            except IndexError:
                self.log.append({'type': 'error', 'message': "Invalid target selected for scout."})
                actor.reset_atb_gauge()
                return
            
            if attempt_scout(self.player, target_monster, self.enemy_party, self.log):
                # If scout successful, monster is removed from enemy_party in attempt_scout
                pass
            else:
                self.log.append({'type': 'info', 'message': f"Scouting {target_monster.name} failed."})

        actor.reset_atb_gauge()
        self._check_battle_end()

    def process_ai_turn(self):
        if self.finished:
            return

        actor = self.current_actor
        if not actor or actor not in self.enemy_party:
            self.log.append({'type': 'error', 'message': "It's not enemy's turn or no active enemy monster."})
            return

        self.log.append({'type': 'info', 'message': f"{actor.name} のターン！"})

        status_flags = process_status_effects(actor, self.log)
        if not actor.is_alive:
            self.log.append({'type': 'info', 'message': f"{actor.name} fainted due to status effect."})
            self._check_battle_end()
            actor.reset_atb_gauge()
            return
        if status_flags["skip_turn"]:
            self.log.append({'type': 'info', 'message': f"{actor.name} is unable to act due to status effect."})
            actor.reset_atb_gauge()
            return

        if process_charge_state(actor, self.enemy_party, self.player_party, self.log):
            actor.reset_atb_gauge()
            self._check_battle_end()
            return

        enemy_take_action(actor, self.player_party, self.enemy_party, self.log)
        actor.reset_atb_gauge()
        self._check_battle_end()

    def _check_battle_end(self):
        if is_party_defeated(self.player_party):
            self.finished = True
            self.outcome = "lose"
            self.log.append({'type': 'info', 'message': "Your party was defeated... Game Over!"})
        elif is_party_defeated(self.enemy_party):
            self.finished = True
            self.outcome = "win"
            self.log.append({'type': 'info', 'message': "Enemy party defeated! Victory!"})
            award_experience(self.player_party, self.enemy_party, self.player, self.log)

    def get_current_state(self):
        return {
            'player_party': [m.to_dict() for m in self.player_party],
            'enemy_party': [m.to_dict() for m in self.enemy_party],
            'log': self.log,
            'turn_count': self.turn_count,
            'finished': self.finished,
            'outcome': self.outcome,
            'current_actor': self.current_actor.to_dict() if self.current_actor else None,
            'turn_order': [m.to_dict() for m in self.turn_order]
        }

    def advance_turn(self):
        if self.finished:
            return

        self.turn_count += 1
        self.log.append({'type': 'info', 'message': f"--- Turn {self.turn_count} ---"})

        all_monsters = self.player_party + self.enemy_party
        for monster in all_monsters:
            if monster.is_alive:
                monster.update_atb_gauge()

        self._update_turn_order()

        if not self.turn_order:
            # If no one can act, advance everyone's gauge a bit
            for monster in all_monsters:
                if monster.is_alive:
                    monster.update_atb_gauge(10)
            self.log.append({'type': 'info', 'message': "No one can act, advancing ATB gauges..."})
            return # Re-evaluate turn order in next call

        self.current_actor = self.turn_order.pop(0)
        self.current_actor.atb_gauge = 0 # Reset ATB after acting

def start_atb_battle(player_party: list[Monster], enemy_party: list[Monster], player: Player, log: Optional[List[Dict[str, str]]] = None, turn_order_monsters: Optional[List[Monster]] = None) -> Battle:
    battle_instance = Battle(player_party, enemy_party, player, log, turn_order_monsters)
    return battle_instance

def enemy_take_action(enemy_actor: Monster, active_player_party: list[Monster], active_enemy_party: list[Monster], log: List[Dict[str, str]]):
    log.append({'type': 'info', 'message': f"{enemy_actor.name}'s action!"})
    alive_player_targets = [m for m in active_player_party if m.is_alive]
    if not alive_player_targets:
        log.append({'type': 'info', 'message': f"{enemy_actor.name} waits..."})
        return

    taunted = any(e["name"] == "taunt" for e in enemy_actor.status_effects)
    cant_attack = any(e["name"] == "cant_attack" for e in enemy_actor.status_effects)

    usable_skills = [s for s in enemy_actor.skills if enemy_actor.mp >= s.cost]

    role = getattr(enemy_actor, "ai_role", "attacker")

    sequence = getattr(enemy_actor, "skill_sequence", [])
    if sequence:
        idx = getattr(enemy_actor, "_seq_idx", 0)
        skill_id = sequence[idx % len(sequence)]
        skill_obj = ALL_SKILLS.get(skill_id)
        enemy_actor._seq_idx = idx + 1
        if skill_obj and enemy_actor.mp >= skill_obj.cost:
            targets: list[Monster] = []
            if skill_obj.target == "enemy":
                if skill_obj.scope == "all":
                    targets = alive_player_targets
                else:
                    targets = [min(alive_player_targets, key=lambda m: m.hp)]
            elif skill_obj.target == "ally":
                allies = [m for m in active_enemy_party if m.is_alive]
                if skill_obj.scope == "all":
                    targets = allies
                else:
                    targets = [enemy_actor]
            else:
                targets = [enemy_actor]
            if targets:
                apply_skill_effect(enemy_actor, targets, skill_obj, log, active_enemy_party, active_player_party)
                return

    if enemy_actor.hp <= enemy_actor.max_hp * 0.3 and not is_defending(enemy_actor):
        defend(enemy_actor, log)
        return

    if taunted:
        if cant_attack:
            log.append({'type': 'info', 'message': f"{enemy_actor.name} is taunted but cannot attack!"})
            return
        if role == "attacker":
            target = min(alive_player_targets, key=lambda m: m.hp)
        else:
            target = random.choice(alive_player_targets)
        log.append({'type': 'info', 'message': f"{enemy_actor.name} attacks due to taunt! -> {target.name}"})
        damage = calculate_damage(enemy_actor, target, log)
        target.hp -= damage
        log.append({'type': 'info', 'message': f"{target.name} took {damage} damage! (HP: {max(0, target.hp)})"})
        if target.hp <= 0:
            target.is_alive = False
            log.append({'type': 'info', 'message': f"{target.name} fainted!"})
        else:
            if any(e["name"] == "counter_stance" for e in target.status_effects):
                log.append({'type': 'info', 'message': f"{target.name} counters!"})
                counter_damage = calculate_damage(target, enemy_actor, log)
                enemy_actor.hp -= counter_damage
                log.append({'type': 'info', 'message': f"{enemy_actor.name} took {counter_damage} damage! (HP: {max(0, enemy_actor.hp)})"})
                if enemy_actor.hp <= 0:
                    enemy_actor.is_alive = False
                    log.append({'type': 'info', 'message': f"{enemy_actor.name} fainted!"})
        return

    selected_skill = None
    skill_targets: list[Monster] = []

    if role == "healer":
        heal_skills = [s for s in usable_skills if s.skill_type == "heal" and s.target == "ally"]
        low_allies = [m for m in active_enemy_party if m.is_alive and m.hp < m.max_hp * 0.5]
        if heal_skills and low_allies:
            ally = min(low_allies, key=lambda m: m.hp / m.max_hp)
            selected_skill = random.choice(heal_skills)
            if selected_skill.scope == "all":
                skill_targets = [m for m in active_enemy_party if m.is_alive]
            else:
                skill_targets = [ally]

    if role == "debuffer" and selected_skill is None:
        debuff_skills = [s for s in usable_skills if s.skill_type == "debuff"]
        if debuff_skills and alive_player_targets:
            target = max(alive_player_targets, key=lambda m: m.attack)
            selected_skill = random.choice(debuff_skills)
            if selected_skill.scope == "all":
                skill_targets = alive_player_targets
            else:
                skill_targets = [target]

    if selected_skill is None and usable_skills and random.random() < 0.5:
        selected_skill = random.choice(usable_skills)
        if selected_skill.target == "enemy":
            if selected_skill.scope == "all":
                skill_targets = alive_player_targets
            else:
                if role == "attacker":
                    target = min(alive_player_targets, key=lambda m: m.hp)
                else:
                    target = random.choice(alive_player_targets)
                skill_targets = [target]
        else:  # ally target
            allies = [m for m in active_enemy_party if m.is_alive]
            if selected_skill.scope == "all":
                skill_targets = allies
            else:
                skill_targets = [random.choice(allies)]

    if selected_skill is not None:
        apply_skill_effect(enemy_actor, skill_targets, selected_skill, log, active_enemy_party, active_player_party)
    else:
        if cant_attack:
            log.append({'type': 'info', 'message': f"{enemy_actor.name} cannot attack and waits..."})
            return
        if role == "attacker":
            target = min(alive_player_targets, key=lambda m: m.hp)
        else:
            target = random.choice(alive_player_targets)
        log.append({'type': 'info', 'message': f"{enemy_actor.name} attacks! -> {target.name}"})
        damage = calculate_damage(enemy_actor, target, log)
        target.hp -= damage
        log.append({'type': 'info', 'message': f"{target.name} took {damage} damage! (HP: {max(0, target.hp)})"})
        if target.hp <= 0:
            target.is_alive = False
            log.append({'type': 'info', 'message': f"{target.name} fainted!"})

RANK_EXP_MULTIPLIERS = {
    "S": 2.0,
    "A": 1.6,
    "B": 1.3,
    "C": 1.1,
    "D": 1.0,
}

def award_experience(alive_party: list[Monster], defeated_enemies: list[Monster], player: Player | None, log: List[Dict[str, str]] | None):
    if log is None:
        log = []
    total_exp_reward = 0
    for enemy in defeated_enemies:
        base = (enemy.level * 10) + (enemy.max_hp // 5)
        mult = RANK_EXP_MULTIPLIERS.get(getattr(enemy, "rank", "D"), 1.0)
        total_exp_reward += int(base * mult)
        if player is not None:
            for item_obj, rate in getattr(enemy, "drop_items", []):
                if random.random() < rate:
                    if isinstance(item_obj, Equipment):
                        new_equip = create_titled_equipment(item_obj.equip_id)
                        if new_equip:
                            player.equipment_inventory.append(new_equip)
                            log.append({'type': 'item_drop', 'message': f"Obtained {new_equip.name}!", 'item_name': new_equip.name})
                        else:
                            log.append({'type': 'info', 'message': f"Failed to obtain {item_obj.name}..."})
                    elif isinstance(item_obj, EquipmentInstance):
                        player.equipment_inventory.append(item_obj)
                        log.append({'type': 'item_drop', 'message': f"Obtained {item_obj.name}!", 'item_name': item_obj.name})
                    else:
                        player.items.append(item_obj)
                        log.append({'type': 'item_drop', 'message': f"Obtained {item_obj.name}!", 'item_name': item_obj.name})

    alive_monsters = [m for m in alive_party if m.is_alive]
    if alive_monsters and total_exp_reward > 0:
        base_share = total_exp_reward // len(alive_monsters)
        remainder = total_exp_reward % len(alive_monsters)
        log.append({'type': 'info', 'message': "--- Experience Gained ---"})
        for idx, monster in enumerate(alive_monsters):
            share = base_share + (1 if idx < remainder else 0)
            if share > 0:
                monster.gain_exp(share)
    else:
        log.append({'type': 'info', 'message': "No experience gained."})

def attempt_scout(player: Player | None, target: Monster, enemy_party: list[Monster], log: List[Dict[str, str]] | None) -> bool:
    if log is None:
        log = []
    if target is None or not target.is_alive:
        log.append({'type': 'info', 'message': "No target selected."})
        return False

    rate = getattr(target, "scout_rate", 0.25)
    log.append({'type': 'info', 'message': f"Attempting to scout {target.name}..."})

    if random.random() < rate:
        log.append({'type': 'info', 'message': f"{target.name} seems to want to join your party!"})
        if player is not None:
            player.add_monster_to_party(target)
        target.is_alive = False
        if target in enemy_party:
            enemy_party.remove(target)
        return True
    else:
        log.append({'type': 'info', 'message': f"{target.name} is wary. Scouting failed."})
        return False
