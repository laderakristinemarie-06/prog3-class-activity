import random
import re
import os
import sys
import time

# ==================== TERMINAL UTILITIES ====================
def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause(seconds=1):
    """Pause for dramatic effect"""
    time.sleep(seconds)

def slow_print(text, delay=0.03):
    """Print text slowly for dramatic effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_header(title):
    """Print a nice header"""
    print("\n" + "="*75)
    print(f"{title:^75}")
    print("="*75 + "\n")

def print_section(title):
    """Print a section separator"""
    print("\n" + "─"*75)
    print(f"  {title}")
    print("─"*75)

# ==================== ATTRIBUTE CLASS ====================
class Attribute:
    """Character stat - HP, Attack, Defense, etc."""
    def __init__(self, name, value, max_value=None):
        self.name = name
        self.value = value
        self.max_value = max_value or value
    
    def modify(self, amount):
        self.value = max(0, min(self.value + amount, self.max_value))
        return self.value
    
    def __repr__(self):
        return f"{self.name}:{self.value}/{self.max_value}"
    
    def get_bar(self, length=30):
        """Get a visual bar representation"""
        if self.max_value == 0:
            return "█" * length
        filled = int((self.value / self.max_value) * length)
        empty = length - filled
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {self.value}/{self.max_value}"


# ==================== BEHAVIOR CLASSES ====================
class Behavior:
    """Character action patterns"""
    def __init__(self, 
                 name="Idle", 
                 description="Performs no action.", 
                 cooldown=0, 
                 cost=0, 
                 target_type="enemy"):
        self.name = name
        self.description = description
        self.cooldown = cooldown
        self.cost = cost
        self.target_type = target_type

    def execute(self, user, target=None):
        return f"{user.name} {self.name}s"


class AttackBehavior(Behavior):
    def __init__(self):
        super().__init__(
            name="attacks",
            description="Performs an attack on the target.",
            cooldown=1,
            cost=5,
            target_type="enemy"
        )

    def execute(self, user, target=None):
        if target:
            dmg = user.attribute.attack.value
            actual = target.take_damage(dmg)
            if hasattr(user, "gold"):
                user.gold += 15
            return f"{user.name} attacks {target.name} for {actual} damage!"
        return f"{user.name} attacks but there is no target!"


class DefendBehavior(Behavior):
    def __init__(self):
        super().__init__(
            name="defends",
            description="Takes a defensive stance, reducing damage taken.",
            cooldown=2,
            cost=3,
            target_type="self"
        )

    def execute(self, user, target=None):
        user.is_defending = True
        return f"{user.name} takes a defensive stance!"


# ==================== ITEM CLASSES ====================
class Item:
    """Base item class"""
    def __init__(self, name, effect, item_type="Misc"):
        self.name = name
        self.effect = effect
        self.type = item_type
    
    def use(self, user):
        return f"{user.name} uses {self.name}"


class Weapon(Item):
    """Combat weapons with unique passive effects"""
    def __init__(self, name, damage, wtype="Sword", passive=None, price=100):
        super().__init__(name, damage, wtype)
        self.damage = damage
        self.type = wtype
        self.passive = passive or "None"
        self.price = price
    
    def equip(self, user):
        user.attribute.attack.modify(self.damage)
        return f"{user.name} equips {self.name} (+{self.damage} ATK) [{self.passive}]"


class Armor(Item):
    """Defensive gear"""
    def __init__(self, name, defense, armor_type="Chest"):
        super().__init__(name, defense, armor_type)
        self.defense = defense
        self.type = armor_type
    
    def equip(self, user):
        user.attribute.defense.modify(self.defense)
        return f"{user.name} equips {self.name} (+{self.defense} DEF)"


class Potion(Item):
    """Consumable healing"""
    def __init__(self, name, heal):
        super().__init__(name, heal, "Consumable")
        self.heal = heal
    
    def use(self, user):
        old = user.attribute.health.value
        user.attribute.health.modify(self.heal)
        return f"{user.name} drinks {self.name}, recovers {user.attribute.health.value - old} HP"


class Bow(Weapon):
    """Bow weapons for marksmen"""
    def __init__(self, name, damage, passive="None", price=100):
        super().__init__(name, damage, "Bow", passive, price)


# ==================== WEAPON DATABASE ====================
SWORDS = [
    Weapon("Blade of the Six Kings", 55, "Sword", "Lifesteal 10%", 150),
    Weapon("Windtalker", 40, "Sword", "Attack Speed +15%", 120),
    Weapon("Berserker's Fury", 45, "Sword", "Crit Damage +40%", 130),
    Weapon("Rose Gold Meteor", 50, "Sword", "Magic Resist 25%", 140),
    Weapon("Scarlet Phantom", 35, "Sword", "Crit Rate +20%", 100),
    Weapon("Blade of Despair", 60, "Sword", "Extra DMG to low HP", 160),
    Weapon("Golden Staff", 30, "Sword", "Attack Speed +25%", 90),
    Weapon("Flying Dagger", 28, "Sword", "Movement Speed", 80),
    Weapon("Terror Blade", 48, "Sword", "VS Hero 15%", 135),
    Weapon("Great Dragon Sword", 52, "Sword", "AS+10% Lifesteal 8%", 145),
    Weapon("Holy Blade", 45, "Sword", "True Damage 20", 130),
    Weapon("Wrist Slasher", 32, "Sword", "Bounce Attack", 95),
]

STAFFS = [
    Weapon("Starlium Staff", 45, "Staff", "Magic Power +30%", 130),
    Weapon("Crystal Orchid", 40, "Staff", "Cooldown 10%", 120),
    Weapon("Enchanted Talisman", 35, "Staff", "Mana Regen", 100),
    Weapon("Blood Wings", 50, "Staff", "Spell Vamp 15%", 140),
    Weapon("Genius Wand", 38, "Staff", "Magic PEN 20", 115),
    Weapon("Lightning Truncheon", 42, "Staff", "Burst DMG", 125),
    Weapon("Divine Glaive", 48, "Staff", "Magic PEN 35", 135),
    Weapon("Clock of Destiny", 35, "Staff", "HP+500", 100),
    Weapon("Fleeting Time", 40, "Staff", "Reset Ultimate", 120),
    Weapon("Winter Truncheon", 38, "Staff", "Stun Immunity", 115),
    Weapon("Glowing Wand", 32, "Staff", "Burn Damage", 95),
    Weapon("Staff of the Nine Realms", 55, "Staff", "Ultimate CD-20%", 150),
]

DAGGERS = [
    Weapon("Corrosion Dagger", 25, "Dagger", "Attack Speed +20%", 80),
    Weapon("Haas's Claws", 30, "Dagger", "Lifesteal 15%", 95),
    Weapon("Blade of Heptaseas", 28, "Dagger", "Jungle DMG 30%", 90),
    Weapon("Demon Hunter Sword", 35, "Dagger", "VS Minions +30%", 110),
    Weapon("Windblade", 32, "Dagger", "Movement Speed", 100),
    Weapon("KillerExecutioner", 38, "Dagger", "Execute Low HP", 120),
    Weapon("Bahamut", 35, "Dagger", "AOE Magic DMG", 110),
    Weapon("Death Sickle", 30, "Dagger", "Slow Effect", 95),
    Weapon("Malefic Roar", 45, "Dagger", "Physical PEN 30", 135),
    Weapon("Necklace of Durance", 25, "Dagger", "Healing Reduction 50%", 80),
]

MACES = [
    Weapon("War Axe", 45, "Mace", "Damage +10%", 130),
    Weapon("Cursed Helmet", 30, "Mace", "AOE Damage", 95),
    Weapon("Bloodlust Axe", 40, "Mace", "Spell Vamp 15%", 120),
    Weapon("Malefic Roar", 50, "Mace", "Physical PEN 30", 140),
    Weapon("Hunter's Strike", 35, "Mace", "VS Jungle 25%", 110),
    Weapon("Brute Force", 42, "Mace", "ATK+DEF 5%", 125),
    Weapon("Endless Battle", 38, "Mace", "True Damage", 115),
    Weapon("Queen's Wings", 40, "Mace", "Damage Reduction 30%", 120),
    Weapon("Radiant Armor", 35, "Mace", "Counter Attack", 110),
    Weapon("Athenian Shield", 30, "Mace", "Block 50%", 95),
]

SHIELDS = [
    Weapon("Aegis", 20, "Shield", "HP +500", 70),
    Weapon("Dominance Ice", 25, "Shield", "Attack Speed Slow", 85),
    Weapon("Antique Cuirass", 30, "Shield", "AOE Defense", 100),
    Weapon("Cursed Shield", 25, "Shield", "Reflect DMG", 85),
    Weapon("Twilight Armor", 28, "Shield", "VS Marksman 20%", 95),
    Weapon("Oracle Armor", 22, "Shield", "Shield Effect +30%", 75),
    Weapon("Guardian Plate", 35, "Shield", "VS Mage 25%", 110),
    Weapon("Dreadnought Plate", 32, "Shield", "Push Back", 105),
    Weapon("Rose's Metal", 26, "Shield", "Lifesteal Reduction", 90),
    Weapon("Athena's Shield", 30, "Shield", "Magic Shield", 100),
]

BOWS = [
    Weapon("Swift Crossbow", 45, "Bow", "Attack Speed +20%", 130),
    Weapon("Demon's Bane", 50, "Bow", "VS Tank 25%", 140),
    Weapon("Windbow", 40, "Bow", "Movement Speed", 120),
    Weapon("Golden Arrow", 35, "Bow", "Gold Gain +15%", 110),
    Weapon("Arrow of Ice", 42, "Bow", "Slow Effect", 125),
    Weapon("Arrow of Death", 55, "Bow", "Execute", 150),
    Weapon("Serpent's Maw", 38, "Bow", "Lifedrain", 115),
    Weapon("Berserker's Arrow", 48, "Bow", "Crit Rate +25%", 135),
]

ARMORS = [
    Armor("Guardian Plate", 50, "Chest"),
    Armor("Crusader Emblem", 45, "Chest"),
    Armor("Twilight Armor", 40, "Chest"),
    Armor("Oracle Armor", 35, "Chest"),
    Armor("Brute Force", 48, "Chest"),
    Armor("Steel Helmet", 25, "Helmet"),
    Armor("Assault Helmet", 30, "Helmet"),
    Armor("Dreadnought Plate", 35, "Helmet"),
    Armor("Tough Boots", 20, "Boots"),
    Armor("Warrior Boots", 25, "Boots"),
    Armor("Swift Boots", 15, "Boots"),
    Armor("Demon Shoes", 20, "Boots"),
]


# ==================== WEAPON FUNCTIONS ====================
def get_weapons_by_type(weapon_type):
    """Get weapons by type"""
    weapons = {
        "SWORD": SWORDS,
        "STAFF": STAFFS,
        "DAGGER": DAGGERS,
        "MACE": MACES,
        "SHIELD": SHIELDS,
        "BOW": BOWS
    }
    return weapons.get(weapon_type.upper(), [])


def get_class_weapon_types(player):
    """Return weapon type(s) allowable for this class."""
    return {
        "Vanguard": ["SWORD"],
        "Weaver": ["STAFF"],
        "Alchemist": ["MACE"],
        "Rogue": ["DAGGER"],
        "Guardian": ["SHIELD"],
    }.get(player.player_class, ["SWORD"])


def shop_weapon_choices(player):
    """Return weapons available for purchase based on player's gold."""
    allowed_types = get_class_weapon_types(player)
    all_weapons = []
    
    for wtype in allowed_types:
        all_weapons.extend(get_weapons_by_type(wtype))
    
    if player.gold < 100:
        filtered = [w for w in all_weapons if w.price <= player.gold + 50]
    elif player.gold < 250:
        filtered = [w for w in all_weapons if w.price <= player.gold + 100]
    else:
        filtered = all_weapons
    
    if not filtered:
        filtered = all_weapons
    
    random.shuffle(filtered)
    filtered = filtered[:8]
    
    defense_weapons = [w for w in filtered if w.type.upper() in ['SHIELD']]
    if not defense_weapons:
        shield_option = [w for w in all_weapons if w.type.upper() == 'SHIELD' 
                        and w.price <= player.gold + 100]
        if shield_option:
            filtered.append(shield_option[0])
    
    return filtered


def get_equip_limit(tower_gold):
    """Determine how many weapons player can equip based on gold earned THIS tower."""
    if tower_gold >= 150:
        return 3
    else:
        return 2


# ==================== INVENTORY CLASS ====================
class Inventory:
    """Player's equipment and items - supports multiple weapons"""
    def __init__(self, size=20):
        self.capacity = size
        self.items = []
        self.equipped_weapons = []
        self.armor = None
        self.accessory = None
    
    def add(self, item):
        if len(self.items) >= self.capacity:
            return False
        self.items.append(item)
        return True
    
    def equip(self, item, user):
        """Equip an item and apply stats"""
        if isinstance(item, Weapon):
            if any(w.name == item.name for w in self.equipped_weapons):
                return f"{user.name} already has {item.name} equipped!"
            
            self.equipped_weapons.append(item)
            user.attribute.attack.modify(item.damage)
            return f"{user.name} equips {item.name} (+{item.damage} ATK) [{item.passive}]"
        elif isinstance(item, Armor):
            if self.armor:
                user.attribute.defense.modify(-self.armor.defense)
            self.armor = item
            return item.equip(user)
        return "Cannot equip this"
    
    def show(self):
        print(f"\n{'═'*75}")
        print(f"📦 INVENTORY ({len(self.items)}/{self.capacity})")
        print(f"{'═'*75}")
        if self.equipped_weapons:
            print("⚔️  Equipped Weapons:")
            for w in self.equipped_weapons:
                print(f"  ⚔️  {w.name} (+{w.damage} ATK) [{w.passive}]")
        if self.armor:
            print(f"🛡️  Armor: {self.armor.name} (+{self.armor.defense} DEF)")
        print("Items:")
        for i in self.items:
            if not isinstance(i, (Weapon, Armor)):
                print(f"  - {i.name}")


# ==================== CHARACTER CLASSES ====================
class Character:
    """Base class - uses Attribute and Behavior (composition)"""
    def __init__(self, name, health, attack):
        self.name = name
        self.is_alive = True
        self.is_defending = False
        
        self.attribute = type('Attr', (), {
            'health': Attribute('HP', health, health),
            'attack': Attribute('ATK', attack, 100),
            'defense': Attribute('DEF', 10, 50),
            'speed': Attribute('SPD', 10, 50)
        })()
        
        self.behavior = AttackBehavior()
    
    def take_damage(self, dmg):
        defense = self.attribute.defense.value
        actual = max(1, dmg - defense)
        if self.is_defending:
            actual //= 2
            self.is_defending = False
        self.attribute.health.modify(-actual)
        if self.attribute.health.value <= 0:
            self.is_alive = False
        return actual
    
    def heal(self, amount):
        self.attribute.health.modify(amount)
    
    def act(self, target):
        return self.behavior.execute(self, target)
    
    def show_stats(self):
        """Display character stats"""
        print(f"\n👤 {self.name}")
        print(f"   {self.attribute.health.get_bar()}")


class Player(Character):
    """Warrior class - uses Inventory and Weapon (composition)"""
    def __init__(self, name, health, attack, pclass):
        super().__init__(name, health, attack)
        self.player_class = pclass
        self.essence_collected = 0
        self.gold = 0
        self.checkpoint = 1
        self.base_attack = attack
        
        self.inventory = Inventory()
        
        self.weapon = self._get_class_weapon()
        self.inventory.add(self.weapon)
        self.inventory.equip(self.weapon, self)
    
    def _get_class_weapon(self):
        weapons = {
            "Vanguard": ("Voidslayer", 20, "Sword"),
            "Weaver": ("Starfire Staff", 18, "Staff"),
            "Alchemist": ("Mortis Mortar", 15, "Mace"),
            "Rogue": ("Shadowfang", 25, "Dagger"),
            "Guardian": ("Aegis Shield", 12, "Shield"),
        }
        w = weapons.get(self.player_class, ("Fists", 10, "None"))
        return Weapon(w[0], w[1], w[2], price=0)


class Enemy(Character):
    """Blighted enemy - twisted by corruption"""
    def __init__(self, name, health, attack, essence, gold_drop=0):
        super().__init__(name, health, attack)
        self.essence_drop = essence
        self.gold_drop = gold_drop
        self.blight_type = "Minion"


class BlightedMinion(Enemy):
    def __init__(self):
        super().__init__("Blighted Minion", 40, 12, essence=5, gold_drop=20)


class JuniorGiant(Enemy):
    def __init__(self):
        super().__init__("Junior Giant", 120, 25, essence=20, gold_drop=50)


class BlightGiant(Enemy):
    def __init__(self):
        super().__init__("Blight Giant", 250, 40, essence=50, gold_drop=100)


class Vanguard(Player):
    def __init__(self, name):
        super().__init__(name, 150, 25, "Vanguard")
        self.inventory.add(Armor("Plate Armor", 30))
        self.inventory.equip(Armor("Plate Armor", 30), self)


class Weaver(Player):
    def __init__(self, name):
        super().__init__(name, 100, 30, "Weaver")
        self.inventory.add(Potion("Mana Potion", 50))


class Alchemist(Player):
    def __init__(self, name):
        super().__init__(name, 120, 20, "Alchemist")
        self.inventory.add(Potion("Health Potion", 75))
        self.inventory.add(Potion("Health Potion", 75))


class Rogue(Player):
    def __init__(self, name):
        super().__init__(name, 80, 40, "Rogue")


class Guardian(Player):
    def __init__(self, name):
        super().__init__(name, 200, 15, "Guardian")
        self.inventory.add(Armor("Plate Armor", 30))
        self.inventory.equip(Armor("Plate Armor", 30), self)


# ==================== SHOP & EQUIP SYSTEM ====================
def show_shop(player):
    """Display all weapons in the shop for the player's class"""
    weapons = shop_weapon_choices(player)
    clear_screen()
    print_header("⚔️  WEAPON SHOP")
    print(f"Hero: {player.name} ({player.player_class})")
    print(f"💰 Gold: {player.gold} | 💎 Essence: {player.essence_collected}\n")
    print("Available Weapons:\n")
    for idx, w in enumerate(weapons, 1):
        affordable = "✅" if w.price <= player.gold else "❌"
        owned = any(it.name == w.name for it in player.inventory.items if isinstance(it, Weapon))
        owned_str = " (Already Owned)" if owned else ""
        print(f"{idx}. {w.name:.<40} {w.damage:>2} ATK [{w.type:>6}]")
        print(f"   {w.passive:.<40} {affordable} {w.price:>3} gold{owned_str}")
    print()
    return weapons


def shop_stage(player):
    """
    Allow buying multiple weapons at once!
    """
    while True:
        weapons = shop_weapon_choices(player)
        owned_set = {w.name for w in player.inventory.items if isinstance(w, Weapon)}
        
        show_shop(player)
        print("Enter weapon numbers to buy (e.g., 1 3 5) or (1, 3, 5) or (1 and 3 and 5)")
        print("Or press Enter to leave the shop.\n")
        
        wchoices = input(">> Pick numbers: ").strip()
        
        if not wchoices:
            clear_screen()
            print_section("⏭️  Left the shop")
            pause(1)
            return
        
        # Extract numbers from input
        nums = re.findall(r'\d+', wchoices)
        
        if not nums:
            print(f"❌ Invalid input. Please enter numbers between 1 and {len(weapons)}.")
            pause(2)
            continue
        
        # Convert to integers and filter valid range
        nums = sorted(set([int(n) for n in nums if 1 <= int(n) <= len(weapons)]))
        
        if not nums:
            print(f"❌ Invalid choice. Please pick numbers between 1 and {len(weapons)}.")
            pause(2)
            continue
        
        # Try to buy weapons
        purchases = []
        total_cost = 0
        
        for n in nums:
            weapon = weapons[n - 1]
            
            if weapon.name in owned_set:
                print(f"⏭️  {weapon.name} already owned, skipping...")
                pause(0.5)
                continue
            
            if any(p.name == weapon.name for p in purchases):
                print(f"⏭️  {weapon.name} already chosen, skipping...")
                pause(0.5)
                continue
            
            if total_cost + weapon.price > player.gold:
                print(f"❌ Not enough gold for {weapon.name}! Need {weapon.price} more gold.")
                pause(0.5)
                continue
            
            total_cost += weapon.price
            purchases.append(weapon)
            owned_set.add(weapon.name)
        
        # Apply all purchases
        if purchases:
            clear_screen()
            print_section("✅ PURCHASES COMPLETED")
            player.gold -= total_cost
            for weapon in purchases:
                player.inventory.add(weapon)
                print(f"✅ Acquired: {weapon.name:.<40} +{weapon.damage} ATK")
            print(f"\n💰 Remaining gold: {player.gold}\n")
            pause(2)
        else:
            print("❌ No weapons purchased in this round.\n")
            pause(2)
        
        # Check if player can afford anything else
        min_price = min([w.price for w in weapons if w.name not in owned_set], default=9999)
        if player.gold < min_price:
            clear_screen()
            print_section("⏳ Not enough gold for more purchases")
            pause(1)
            return


def equip_phase(player, tower_gold):
    """SINGLE PLAYER ONLY: Choose 2-3 weapons to equip from inventory."""
    equip_limit = get_equip_limit(tower_gold)
    
    owned_weapons = [w for w in player.inventory.items if isinstance(w, Weapon)]
    
    if not owned_weapons:
        clear_screen()
        print_section("⚠️  No weapons in inventory")
        pause(2)
        return
    
    clear_screen()
    print_header(f"🛡️  EQUIP PHASE")
    print(f"Choose {equip_limit} weapons for the next battle!")
    print(f"💰 Gold earned this tower: {tower_gold}\n")
    print("Available Weapons:\n")
    for idx, w in enumerate(owned_weapons, 1):
        print(f"{idx}. {w.name:.<40} +{w.damage} ATK")
    print()
    
    chosen_indices = []
    for n in range(equip_limit):
        while True:
            wchoice = input(f"Select weapon #{n+1} (1-{len(owned_weapons)}): ").strip()
            
            # Extract number from input
            match = re.search(r'\d+', wchoice)
            if not match:
                print("❌ Please enter a valid number.")
                continue
            
            idx = int(match.group()) - 1
            
            if 0 <= idx < len(owned_weapons):
                if idx in chosen_indices:
                    print(f"❌ Already chosen! Pick a different weapon.")
                    continue
                chosen_indices.append(idx)
                break
            else:
                print(f"❌ Invalid number. Please pick between 1 and {len(owned_weapons)}.")
    
    # Clear previous equipped weapons
    old_equipped_bonus = sum(w.damage for w in player.inventory.equipped_weapons)
    player.attribute.attack.modify(-old_equipped_bonus)
    
    # Equip new selection
    player.inventory.equipped_weapons = []
    total_bonus = 0
    for idx in sorted(chosen_indices):
        weapon = owned_weapons[idx]
        player.inventory.equipped_weapons.append(weapon)
        total_bonus += weapon.damage
    
    player.attribute.attack.modify(total_bonus)
    
    clear_screen()
    print_section("✅ WEAPONS EQUIPPED")
    for w in player.inventory.equipped_weapons:
        print(f"⚔️  {w.name:.<40} +{w.damage} ATK")
    print(f"\n📊 Total Attack Power: {player.attribute.attack.value}")
    pause(2)


# ==================== TOWER CLASS ====================
class CorruptedTower:
    """One of 20 corrupted towers"""
    def __init__(self, number, enemies=None):
        self.number = number
        self.corruption = "Severe"
        self.enemies = enemies or []
        self.cleared = False
    
    def get_alive(self):
        return [e for e in self.enemies if e.is_alive]
    
    def check_clear(self):
        if not self.get_alive():
            self.cleared = True
            self.corruption = "Purified"
    
    def calculate_tower_gold(self):
        """Calculate total gold available from enemies in this tower"""
        return sum(e.gold_drop for e in self.enemies)


# ==================== GAME CLASS ====================
class AethermoorGame:
    """Main game with composition visible"""
    def __init__(self, multiplayer=False):
        self.players = []
        self.towers = []
        self.current_tower = 0
        self.multiplayer = multiplayer
        self.current_enemy = None
        self._build_towers()
    
    def _build_towers(self):
        """Build 20 corrupted towers"""
        # Progressive waves
        for i in range(1, 10):
            count = 5 + i * 3
            enemies = [BlightedMinion() for _ in range(count)]
            self.towers.append(CorruptedTower(i, enemies))
        
        # Boss towers
        self.towers.append(CorruptedTower(10, [BlightedMinion() for _ in range(10)] + [BlightGiant()]))
        self.towers.append(CorruptedTower(11, [BlightedMinion() for _ in range(12)]))
        self.towers.append(CorruptedTower(12, [BlightedMinion() for _ in range(15)]))
        self.towers.append(CorruptedTower(13, [BlightedMinion() for _ in range(18)]))
        self.towers.append(CorruptedTower(14, [JuniorGiant()]))
        self.towers.append(CorruptedTower(15, [JuniorGiant(), JuniorGiant()]))
        self.towers.append(CorruptedTower(16, [BlightedMinion() for _ in range(15)] + [JuniorGiant() for _ in range(3)]))
        self.towers.append(CorruptedTower(17, [BlightGiant()]))
        self.towers.append(CorruptedTower(18, [BlightedMinion() for _ in range(10)] + [JuniorGiant() for _ in range(2)]))
        self.towers.append(CorruptedTower(19, [BlightedMinion() for _ in range(10)] + [JuniorGiant() for _ in range(3)]))
        
        # FINAL BOSS TOWER
        self.towers.append(CorruptedTower(20, 
            [BlightedMinion() for _ in range(15)] + 
            [JuniorGiant() for _ in range(5)] + 
            [BlightGiant(), BlightGiant()]))

    def add_player(self, player):
        if len(self.players) < 5:
            self.players.append(player)
            return True
        return False
    
    def battle_tower(self, tower):
        """Battle system with animations"""
        round_num = 1
        
        while True:
            alive_p = [p for p in self.players if p.is_alive]
            alive_e = tower.get_alive()
            
            if not alive_e:
                tower.check_clear()
                
                # Award gold
                for enemy in tower.enemies:
                    for player in alive_p:
                        if hasattr(player, "gold"):
                            player.gold += enemy.gold_drop
                
                return True
            
            if not alive_p:
                for p in self.players:
                    p.heal(p.attribute.health.max_value)
                    p.is_alive = True
                return False
            
            # Display battle round
            clear_screen()
            print_header(f"⚔️  BATTLE - ROUND {round_num}")
            
            # Show player stats
            print("HEROES:\n")
            for p in alive_p:
                p.show_stats()
            
            # Show enemy stats
            print("\nENEMIES:\n")
            for e in alive_e:
                e.show_stats()
            
            pause(1.5)
            
            # Players attack
            clear_screen()
            print_section("⚔️  HEROES ATTACK")
            for p in alive_p:
                if tower.get_alive():
                    target = random.choice(tower.get_alive())
                    action = p.act(target)
                    slow_print(action, delay=0.02)
                    pause(0.7)
            
            pause(1)
            
            # Enemies attack
            clear_screen()
            print_section("🔥 ENEMIES COUNTER ATTACK")
            for e in alive_e:
                if alive_p:
                    target = random.choice(alive_p)
                    action = e.act(target)
                    slow_print(action, delay=0.02)
                    pause(0.7)
            
            pause(1)
            round_num += 1
    
    def play(self):
        """Main game loop"""
        while self.current_tower < len(self.towers):
            tower = self.towers[self.current_tower]
            
            if not tower.cleared:
                clear_screen()
                print_header(f"🗼 TOWER {tower.number}/20")
                print(f"Status: {tower.corruption}")
                print(f"Enemies: {len(tower.enemies)}")
                tower_gold = tower.calculate_tower_gold()
                print(f"💰 Gold Available: {tower_gold}\n")
                input("Press Enter to begin battle...")
                
                result = self.battle_tower(tower)
                
                if result:
                    clear_screen()
                    print_header("✨ TOWER PURIFIED! ✨")
                    
                    actual_gold_earned = tower.calculate_tower_gold()
                    print(f"💰 Gold Earned: {actual_gold_earned}\n")
                    for player in self.players:
                        if player.is_alive:
                            print(f"{player.name}: {player.gold} gold total")
                    
                    pause(2)
                    self.current_tower += 1
                    
                    # SHOP & EQUIP PHASE
                    if self.current_tower < 20:
                        for player in self.players:
                            if player.is_alive:
                                shop_stage(player)
                                if not self.multiplayer:
                                    equip_phase(player, actual_gold_earned)
                    
                    if self.current_tower == 20:
                        self._victory()
                        break
                else:
                    clear_screen()
                    print_header("💀 DEFEATED!")
                    print("Respawning at checkpoint...\n")
                    pause(2)
                    self.current_tower = max(0, self.players[0].checkpoint - 1)
            else:
                self.current_tower += 1
    
    def _victory(self):
        """Victory screen"""
        clear_screen()
        print_header("🎉 AETHERMOOR IS SAVED! 🎉")
        
        if self.multiplayer:
            sorted_p = sorted(self.players, key=lambda p: p.essence_collected, reverse=True)
            print("═" * 75)
            print("LEADERBOARD\n")
            for i, p in enumerate(sorted_p, 1):
                weapons_owned = [w.name for w in p.inventory.equipped_weapons]
                print(f"{i}. {p.name}")
                print(f"   💎 Essence: {p.essence_collected} | 💰 Gold: {p.gold}")
                print(f"   Equipped: {', '.join(weapons_owned) if weapons_owned else 'None'}\n")
        else:
            print("═" * 75)
            p = self.players[0]
            print(f"\n{p.name} the {p.player_class}\n")
            print(f"💎 Total Essence Collected: {p.essence_collected}")
            print(f"💰 Total Gold Earned: {p.gold}")
            weapons_owned = [w.name for w in p.inventory.equipped_weapons]
            print(f"⚔️  Final Equipped Weapons: {', '.join(weapons_owned) if weapons_owned else 'None'}")
            weapons_in_inventory = [w.name for w in p.inventory.items if isinstance(w, Weapon)]
            print(f"🎁 Total Weapons Collected: {len(weapons_in_inventory)}")
            if weapons_in_inventory:
                for w in weapons_in_inventory:
                    print(f"   - {w}")
        
        print("\n" + "═" * 75)
        print("Thanks for playing AETHERMOOR'S SALVATION!")
        print("═" * 75 + "\n")


# ==================== MAIN ====================
def main():
    clear_screen()
    print_header("AETHERMOOR'S SALVATION")
    print("Mobile Legends Inspired Equipment System\n")
    print("The Blight spreads...")
    print("20 towers must fall.")
    print("Earn gold in battle.")
    print("Buy legendary weapons.")
    print("Choose your arsenal.")
    print("Save Aethermoor.\n")
    pause(2)
    
    # Mode selection
    while True:
        try:
            clear_screen()
            print("MODE SELECTION\n")
            print("(1) Single Player")
            print("(2) Multiplayer\n")
            mode = int(input(">> Choose mode: "))
            if mode in (1, 2):
                break
            print("❌ Please enter 1 or 2")
            pause(2)
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            pause(2)
    
    game = AethermoorGame(multiplayer=(mode == 2))
    
    # Player count
    if mode == 1:
        num = 1
    else:
        while True:
            try:
                clear_screen()
                num = int(input("How many players? (2-5): ") or "2")
                if 2 <= num <= 5:
                    break
                print("❌ Please enter a number between 2 and 5")
                pause(2)
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
                pause(2)
    
    # Class selection
    hero_classes = {
        "1": ("Vanguard", Vanguard),
        "2": ("Weaver", Weaver),
        "3": ("Alchemist", Alchemist),
        "4": ("Rogue", Rogue),
        "5": ("Guardian", Guardian),
    }
    
    for i in range(num):
        clear_screen()
        print_header(f"PLAYER {i+1} - CHARACTER CREATION")
        name = input("Enter hero name: ") or f"Hero{i+1}"
        
        print("\nChoose your hero:")
        print("1. Vanguard   (150 HP, 25 ATK) - Heavy Armor Tank")
        print("2. Weaver     (100 HP, 30 ATK) - Spell Caster")
        print("3. Alchemist  (120 HP, 20 ATK) - Support Healer")
        print("4. Rogue      (80 HP, 40 ATK)  - Assassin")
        print("5. Guardian   (200 HP, 15 ATK) - Shield Master\n")
        
        c = input(">> Select class (1-5): ") or "1"
        
        hero = hero_classes.get(c, ("Vanguard", Vanguard))
        player = hero[1](name)
        game.add_player(player)
        
        clear_screen()
        print_header(f"✨ {player.name} THE {player.player_class.upper()} ✨")
        print(f"\nStats:")
        print(f"  HP:  {player.attribute.health.value}/{player.attribute.health.max_value}")
        print(f"  ATK: {player.attribute.attack.value}")
        print(f"  DEF: {player.attribute.defense.value}")
        print(f"\nStarting Weapon: {player.weapon.name} (+{player.weapon.damage} ATK)")
        print(f"Status: READY FOR BATTLE\n")
        pause(2)
    
    clear_screen()
    print_header("⚔️  THE PURIFICATION BEGINS  ⚔️")
    pause(2)
    
    game.play()


if __name__ == "__main__":
    main()