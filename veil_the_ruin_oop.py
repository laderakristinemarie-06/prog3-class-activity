import random

class Attribute: #Base Class
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


class Behavior:  # Base Class
    """Character action patterns with description, cooldown, cost, and targeting."""
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


class AttackBehavior(Behavior):  # Inheritance
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
                user.gold += 10  # Earn 10 gold per hit
            return f"{user.name} attacks {target.name} for {actual} damage!"
        return f"{user.name} attacks but there is no target!"


class DefendBehavior(Behavior):  # Inheritance
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

class Item: #Base Class
    """Base item class"""
    def __init__(self, name, effect, item_type="Misc"):
        self.name = name
        self.effect = effect
        self.type = item_type
    
    def use(self, user):
        return f"{user.name} uses {self.name}"


class Weapon(Item): #Inheritance
    """
    Combat weapons - inspired by Mobile Legends
    Each weapon has unique passive effects
    """
    def __init__(self, name, damage, wtype="Sword", passive=None):
        super().__init__(name, damage, wtype)
        self.damage = damage
        self.type = wtype
        self.passive = passive or "None"
    
    def equip(self, user):
        user.attribute.attack.modify(self.damage)
        return f"{user.name} equips {self.name} (+{self.damage} ATK) [{self.passive}]"


class Armor(Item): #Inheritance
    """Defensive gear"""
    def __init__(self, name, defense, armor_type="Chest"):
        super().__init__(name, defense, armor_type)
        self.defense = defense
        self.type = armor_type
    
    def equip(self, user):
        user.attribute.defense.modify(self.defense)
        return f"{user.name} equips {self.name} (+{self.defense} DEF)"

class Potion(Item): #Inheritance
    """Consumable healing"""
    def __init__(self, name, heal):
        super().__init__(name, heal, "Consumable")
        self.heal = heal
    
    def use(self, user):
        old = user.attribute.health.value
        user.attribute.health.modify(self.heal)
        return f"{user.name} drinks {self.name}, recovers {user.attribute.health.value - old} HP"


class Bow(Weapon): #Inheritance
    """Bow weapons for marksmen - extends Weapon"""
    def __init__(self, name, damage, passive="None"):
        super().__init__(name, damage, "Bow", passive)


class EssenceOrb(Item): #Inheritance
    """Essence from Blight"""
    def __init__(self, amount):
        super().__init__("Essence Orb", amount, "Material")
        self.amount = amount
    
    def use(self, user):
        user.essence_collected += self.amount
        return f"{user.name} absorbs {self.amount} Essence! (Total: {user.essence_collected})"


# ==================== WEAPON DATABASE (Mobile Legends Inspired) ====================
# Module-level weapon lists (no class variables, no decorators)

SWORDS = [
    Weapon("Blade of the Six Kings", 55, "Sword", "Lifesteal 10%"),
    Weapon("Windtalker", 40, "Sword", "Attack Speed +15%"),
    Weapon("Berserker's Fury", 45, "Sword", "Crit Damage +40%"),
    Weapon("Rose Gold Meteor", 50, "Sword", "Magic Resist 25%"),
    Weapon("Scarlet Phantom", 35, "Sword", "Crit Rate +20%"),
    Weapon("Blade of Despair", 60, "Sword", "Extra DMG to low HP"),
    Weapon("Golden Staff", 30, "Sword", "Attack Speed +25%"),
    Weapon("Flying Dagger", 28, "Sword", "Movement Speed"),
    Weapon("Terror Blade", 48, "Sword", "VS Hero 15%"),
    Weapon("Great Dragon Sword", 52, "Sword", "AS+10% Lifesteal 8%"),
    Weapon("Holy Blade", 45, "Sword", "True Damage 20"),
    Weapon("Wrist Slasher", 32, "Sword", "Bounce Attack"),
]

STAFFS = [
    Weapon("Starlium Staff", 45, "Staff", "Magic Power +30%"),
    Weapon("Crystal Orchid", 40, "Staff", "Cooldown 10%"),
    Weapon("Enchanted Talisman", 35, "Staff", "Mana Regen"),
    Weapon("Blood Wings", 50, "Staff", "Spell Vamp 15%"),
    Weapon("Genius Wand", 38, "Staff", "Magic PEN 20"),
    Weapon("Lightning Truncheon", 42, "Staff", "Burst DMG"),
    Weapon("Divine Glaive", 48, "Staff", "Magic PEN 35"),
    Weapon("Clock of Destiny", 35, "Staff", "HP+500"),
    Weapon("Fleeting Time", 40, "Staff", "Reset Ultimate"),
    Weapon("Winter Truncheon", 38, "Staff", "Stun Immunity"),
    Weapon("Glowing Wand", 32, "Staff", "Burn Damage"),
    Weapon("Staff of the Nine Realms", 55, "Staff", "Ultimate CD-20%"),
]

DAGGERS = [
    Weapon("Corrosion Dagger", 25, "Dagger", "Attack Speed +20%"),
    Weapon("Haas's Claws", 30, "Dagger", "Lifesteal 15%"),
    Weapon("Blade of Heptaseas", 28, "Dagger", "Jungle DMG 30%"),
    Weapon("Demon Hunter Sword", 35, "Dagger", "VS Minions +30%"),
    Weapon("Windblade", 32, "Dagger", "Movement Speed"),
    Weapon("KillerExecutioner", 38, "Dagger", "Execute Low HP"),
    Weapon("Bahamut", 35, "Dagger", "AOE Magic DMG"),
    Weapon("Death Sickle", 30, "Dagger", "Slow Effect"),
    Weapon("Malefic Roar", 45, "Dagger", "Physical PEN 30"),
    Weapon("Necklace of Durance", 25, "Dagger", "Healing Reduction 50%"),
]

MACES = [
    Weapon("War Axe", 45, "Mace", "Damage +10%"),
    Weapon("Cursed Helmet", 30, "Mace", "AOE Damage"),
    Weapon("Bloodlust Axe", 40, "Mace", "Spell Vamp 15%"),
    Weapon("Malefic Roar", 50, "Mace", "Physical PEN 30"),
    Weapon("Hunter's Strike", 35, "Mace", "VS Jungle 25%"),
    Weapon("Brute Force", 42, "Mace", "ATK+DEF 5%"),
    Weapon("Endless Battle", 38, "Mace", "True Damage"),
    Weapon("Queen's Wings", 40, "Mace", "Damage Reduction 30%"),
    Weapon("Radiant Armor", 35, "Mace", "Counter Attack"),
    Weapon("Athenian Shield", 30, "Mace", "Block 50%"),
]

SHIELDS = [
    Weapon("Aegis", 20, "Shield", "HP +500"),
    Weapon("Dominance Ice", 25, "Shield", "Attack Speed Slow"),
    Weapon("Antique Cuirass", 30, "Shield", "AOE Defense"),
    Weapon("Cursed Shield", 25, "Shield", "Reflect DMG"),
    Weapon("Twilight Armor", 28, "Shield", "VS Marksman 20%"),
    Weapon("Oracle Armor", 22, "Shield", "Shield Effect +30%"),
    Weapon("Guardian Plate", 35, "Shield", "VS Mage 25%"),
    Weapon("Dreadnought Plate", 32, "Shield", "Push Back"),
    Weapon("Rose's Metal", 26, "Shield", "Lifesteal Reduction"),
    Weapon("Athena's Shield", 30, "Shield", "Magic Shield"),
]

BOWS = [
    Weapon("Swift Crossbow", 45, "Bow", "Attack Speed +20%"),
    Weapon("Demon's Bane", 50, "Bow", "VS Tank 25%"),
    Weapon("Windbow", 40, "Bow", "Movement Speed"),
    Weapon("Golden Arrow", 35, "Bow", "Gold Gain +15%"),
    Weapon("Arrow of Ice", 42, "Bow", "Slow Effect"),
    Weapon("Arrow of Death", 55, "Bow", "Execute"),
    Weapon("Serpent's Maw", 38, "Bow", "Lifedrain"),
    Weapon("Berserker's Arrow", 48, "Bow", "Crit Rate +25%"),
]


def get_weapon(name):
    """Find weapon by name"""
    all_weapons = SWORDS + STAFFS + DAGGERS + MACES + SHIELDS + BOWS
    for w in all_weapons:
        if w.name.lower() in name.lower():
            return w
    return None


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
    """Return the list of all weapons for this hero, guaranteeing at least 1 defense weapon,
       and if only defense weapons, add at least one matching attack weapon."""
    allowed_types = get_class_weapon_types(player)  # e.g., ['SWORD']
    all_weapons = []
    
    # Gather allowed weapons by class type
    for wtype in allowed_types:
        all_weapons.extend(get_weapons_by_type(wtype))
    
    # Check defense/attack types
    defense_weapons = [w for w in all_weapons if w.type.upper() in ['SHIELD']]
    attack_weapons = [w for w in all_weapons if w.type.upper() not in ['SHIELD']]
    
    # Guarantee at least 1 defense weapon
    if not defense_weapons:
        all_weapons.append(SHIELDS[0])  # add a default shield
        defense_weapons = [SHIELDS[0]]
    
    # If only defense weapons, add at least one attack weapon matching the class
    if len(attack_weapons) == 0 and len(defense_weapons) > 0:
        attack_candidate = None
        if "SWORD" in allowed_types:
            attack_candidate = SWORDS[0]
        elif "STAFF" in allowed_types:
            attack_candidate = STAFFS[0]
        elif "MACE" in allowed_types:
            attack_candidate = MACES[0]
        elif "DAGGER" in allowed_types:
            attack_candidate = DAGGERS[0]
        elif "BOW" in allowed_types:
            attack_candidate = BOWS[0]
        
        if attack_candidate and attack_candidate not in all_weapons:
            all_weapons.append(attack_candidate)
    
    return all_weapons


# ==================== ARMOR DATABASE ====================
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

class Inventory: #Base Class
    """Player's equipment and items"""
    def __init__(self, size=20):
        self.capacity = size
        self.items = []
        self.weapon = None
        self.armor = None
        self.accessory = None
    
    def add(self, item):
        if len(self.items) >= self.capacity:
            return False
        
        if isinstance(item, Weapon):
            self.weapon = item
        elif isinstance(item, Armor):
            self.armor = item
        
        self.items.append(item)
        return True
    
    def equip(self, item, user):
        """Equip an item and apply stats"""
        if isinstance(item, Weapon):
            if self.weapon:
                user.attribute.attack.modify(-self.weapon.damage)
            self.weapon = item
            return item.equip(user)
        elif isinstance(item, Armor):
            if self.armor:
                user.attribute.defense.modify(-self.armor.defense)
            self.armor = item
            return item.equip(user)
        elif isinstance(item):
            if self.accessory:
                user.attribute.health.modify(-self.accessory.hp_bonus)
            self.accessory = item
            return item.equip(user)
        return "Cannot equip this"
    
    def use(self, name, user):
        for item in self.items:
            if item.name == name and isinstance(item, Potion):
                self.items.remove(item)
                return item.use(user)
        return "Not found"
    
    def show(self):
        print(f"\n=== INVENTORY ({len(self.items)}/{self.capacity}) ===")
        if self.weapon:
            print(f"Weapon: {self.weapon.name} (+{self.weapon.damage} ATK)")
        if self.armor:
            print(f"Armor: {self.armor.name} (+{self.armor.defense} DEF)")
        if self.accessory:
            print(f"Accessory: {self.accessory.name} (+{self.accessory.hp_bonus} HP)")
        print("Items:")
        for i in self.items:
            if not isinstance(i, (Weapon, Armor)):
                print(f"  - {i.name}")

class Character:
    """Base class - uses Attribute and Behavior (composition)"""
    def __init__(self, name, health, attack):
        self.name = name
        self.is_alive = True
        self.is_defending = False
        
        # COMPOSITION: Character HAS-A Attribute
        self.attribute = type('Attr', (), {
            'health': Attribute('HP', health, health),
            'attack': Attribute('ATK', attack, 100),
            'defense': Attribute('DEF', 10, 50),
            'speed': Attribute('SPD', 10, 50)
        })()
        
        self.behavior = AttackBehavior() #Composition
    
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


class Player(Character): #Inheritance
    """Warrior class - uses Inventory and Weapon (composition)"""
    def __init__(self, name, health, attack, pclass):
        super().__init__(name, health, attack)
        self.player_class = pclass
        self.essence_collected = 0
        self.gold = 0
        self.checkpoint = 1
        
        self.inventory = Inventory() #Composition
        
        # COMPOSITION: Player HAS-A starting Weapon (only gives base damage, no equip)
        self.weapon = self._get_class_weapon()
        # DON'T equip it - player must buy weapons from shop
    
    def _get_class_weapon(self):
        weapons = {
            "Vanguard": ("Voidslayer", 20, "Sword"),
            "Weaver": ("Starfire Staff", 18, "Staff"),
            "Alchemist": ("Mortis Mortar", 15, "Mace"),
            "Rogue": ("Shadowfang", 25, "Dagger"),
            "Guardian": ("Aegis Shield", 12, "Shield"),
        }
        w = weapons.get(self.player_class, ("Fists", 10, "None"))
        return Weapon(w[0], w[1], w[2])
    
    def equip_item(self, item):
        """Equip item from inventory"""
        return self.inventory.equip(item, self)
    
    def buy_weapon(self, weapon, price):
        """Purchase weapon from shop"""
        if self.gold < price:
            return f"❌ Not enough gold! Weapon costs {price}, you have: {self.gold}"
        
        # Check if player already owns this exact weapon
        already_owned = any(w.name == weapon.name for w in self.inventory.items if isinstance(w, Weapon))
        if already_owned:
            return f"❌ You already own {weapon.name}!"
        
        self.gold -= price
        self.inventory.add(weapon)
        result = self.inventory.equip(weapon, self)
        return f"✅ {result}\n   (Purchased for {price} gold. Remaining: {self.gold})"


class Enemy(Character): #Inheritance
    """Blighted enemy - twisted by corruption"""
    def __init__(self, name, health, attack, essence):
        super().__init__(name, health, attack)
        self.essence_drop = essence
        self.blight_type = "Minion"

class BlightedMinion(Enemy): #Inheritance
    """Twisted creatures serving the Blight"""
    def __init__(self):
        super().__init__("Blighted Minion", 40, 12, 5)


class JuniorGiant(Enemy): #Inheritance
    """Towering corrupted giants"""
    def __init__(self):
        super().__init__("Junior Giant", 120, 25, 20)


class BlightGiant(Enemy): #Inheritance
    """Colossal anchors of darkness"""
    def __init__(self):
        super().__init__("Blight Giant", 250, 40, 50)


class Vanguard(Player): #Inheritance
    """Heavily armored warrior"""
    def __init__(self, name):
        super().__init__(name, 150, 25, "Vanguard")
        self.inventory.add(Armor("Plate Armor", 30))
        self.inventory.armor.equip(self)


class Weaver(Player): #Inheritance
    """Spell-weaving mage"""
    def __init__(self, name):
        super().__init__(name, 100, 30, "Weaver")
        self.inventory.add(Potion("Mana Potion", 50))


class Alchemist(Player): #Inheritance
    """Resourceful healer and support"""
    def __init__(self, name):
        super().__init__(name, 120, 20, "Alchemist")
        self.inventory.add(Potion("Health Potion", 75))
        self.inventory.add(Potion("Health Potion", 75))


class Rogue(Player): #Inheritance
    """Shadow-dwelling assassin"""
    def __init__(self, name):
        super().__init__(name, 80, 40, "Rogue")


class Guardian(Player):  # Inheritance
    """Unbreakable protector that fights with shields and earns gold & essence."""
    def __init__(self, name):
        super().__init__(name, 200, 15, "Guardian")
        # Add armor for extra defense
        self.inventory.add(Armor("Plate Armor", 30))
        self.inventory.armor.equip(self)


# ==================== SHOP SYSTEM ====================
def show_shop(player):
    """Display all weapons in the shop for the player's class - globally numbered."""
    weapons = shop_weapon_choices(player)
    print("\n" + "="*50)
    print(f"⚔️  WEAPON SHOP ({player.player_class})  ⚔️")
    print("="*50)
    for idx, w in enumerate(weapons, 1):
        print(f"{idx}. {w.name}: {w.damage} ATK [{w.type}] [{w.passive}]")
    print("="*50)
    return weapons


def shop_stage(player):
    """Allow players to buy multiple class-aligned weapons by number as money allows."""
    price = 100
    
    print(f"\n{'='*50}")
    print(f"🛒 SHOP - {player.name}'s Turn")
    print(f"💰 Current Gold: {player.gold}")
    print(f"💎 Essence Collected: {player.essence_collected}")
    print(f"{'='*50}")
    
    while player.gold >= price:
        weapons = show_shop(player)
        print(f"\n💰 Each weapon costs {price} gold. You have: {player.gold}")
        print("Enter weapon number to buy, or press Enter to leave the shop.")
        
        wchoice = input(f"Pick number (1-{len(weapons)}), or Enter to exit: ").strip()
        
        if not wchoice:
            print("⏭️  Left the shop.")
            break
        
        if wchoice.isdigit() and 1 <= int(wchoice) <= len(weapons):
            idx = int(wchoice) - 1
            weapon = weapons[idx]
            
            # Check if player already owns this exact weapon
            already_owned = any(w.name == weapon.name for w in player.inventory.items if isinstance(w, Weapon))
            if already_owned:
                print(f"❌ You already own {weapon.name}. Pick a different one.\n")
                continue
            
            if player.gold < price:
                print(f"❌ Not enough gold! You need {price}, you have: {player.gold}\n")
                continue
            
            result = player.buy_weapon(weapon, price)
            print(result)
        else:
            print(f"❌ Invalid choice. Please pick a number between 1 and {len(weapons)}.\n")
    
    if player.gold < price:
        print(f"\n❌ Not enough gold to buy more weapons. Remaining: {player.gold}")


        
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


# ==================== GAME ====================
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
    
    def distribute_essence(self, tower):
        alive = [p for p in self.players if p.is_alive]
        if not alive:
            return
        total = sum(e.essence_drop for e in tower.enemies)
        each = total // len(alive)
        for p in alive:
            p.essence_collected += each
    
    def battle_tower(self, tower):
        if tower.get_alive():
            self.current_enemy = tower.get_alive()[0]
        
        while True:
            alive_p = [p for p in self.players if p.is_alive]
            alive_e = tower.get_alive()
            
            if not alive_e:
                tower.check_clear()
                if self.multiplayer:
                    self.distribute_essence(tower)
                self.current_enemy = None
                return True
            
            if not alive_p:
                for p in self.players:
                    p.heal(p.attribute.health.max_value)
                    p.is_alive = True
                return False
            
            for p in alive_p:
                if tower.get_alive():
                    target = random.choice(tower.get_alive())
                    p.act(target)
            
            for e in alive_e:
                if alive_p:
                    target = random.choice(alive_p)
                    e.act(target)
    
    def play(self):
        while self.current_tower < len(self.towers):
            tower = self.towers[self.current_tower]
            
            if not tower.cleared:
                print(f"\n{'='*50}")
                print(f"TOWER {tower.number}/20 - {tower.corruption}")
                print(f"{'='*50}")
                
                result = self.battle_tower(tower)
                
                if result:
                    print(f"\n✨ Tower {tower.number} PURIFIED! ✨")
                    self.current_tower += 1
                    
                    # ALL MODES: Shop after each tower (single or multiplayer)
                    if self.current_tower < 20:
                        for player in self.players:
                            if player.is_alive:
                                shop_stage(player)
                    
                    if self.current_tower == 20:
                        self._victory()
                        break
                else:
                    print(f"\n💀 Defeated at Tower {tower.number}!")
                    print(f"Respawning at checkpoint...")
                    self.current_tower = max(0, self.players[0].checkpoint - 1)
            else:
                self.current_tower += 1
    
    def _victory(self):
        print("\n" + "="*60)
        print("🎉 AETHERMOOR IS SAVED! 🎉")
        print("="*60)
        
        if self.multiplayer:
            sorted_p = sorted(self.players, key=lambda p: p.essence_collected, reverse=True)
            print("\n=== LEADERBOARD ===")
            for i, p in enumerate(sorted_p, 1):
                print(f"{i}. {p.name}: {p.essence_collected} Essence | 💰 {p.gold} Gold")
        else:
            print(f"\n{self.players[0].name} the {self.players[0].player_class}")
            print(f"Total Essence Collected: {self.players[0].essence_collected}")
            print(f"Total Gold Earned: {self.players[0].gold}")


# ==================== MAIN ====================
def main():
    print("="*60)
    print("AETHERMOOR'S SALVATION")
    print("Mobile Legends Inspired Equipment System")
    print("="*60)
    print("The Blight spreads. 20 towers must fall.")
    print("Collect Essence. Equip legendary weapons. Save Aethermoor.\n")
    
    # Mode selection
    while True:
        try:
            mode = int(input("Mode: (1) Single  (2) Multiplayer: "))
            if mode in (1, 2):
                break
        except:
            pass
    
    game = AethermoorGame(multiplayer=(mode == 2))
    
    # Player count
    num = 1 if mode == 1 else max(2, min(5, int(input("Players (2-5): ") or "2")))
    
    # Class selection
    hero_classes = {
        "1": ("Vanguard", Vanguard),
        "2": ("Weaver", Weaver),
        "3": ("Alchemist", Alchemist),
        "4": ("Rogue", Rogue),
        "5": ("Guardian", Guardian),
    }
    
    for i in range(num):
        print(f"\n--- Player {i+1} ---")
        name = input("Name: ") or f"Hero{i+1}"
        
        print("\nChoose your hero:")
        print("1. Vanguard  2. Weaver  3. Alchemist  4. Rogue  5. Guardian")
        c = input("Class (1-5): ") or "1"
        
        hero = hero_classes.get(c, Vanguard)
        player = hero[1](name)
        game.add_player(player)
        
        print(f"\n{player.name} the {player.player_class}")
        print(f"HP: {player.attribute.health} | ATK: {player.attribute.attack} | DEF: {player.attribute.defense}")
        print(f"Starting Base Weapon: {player.weapon.name} ({player.weapon.damage} base ATK)")
        print("⚠️  You must buy weapons from the shop with gold earned in battle!")
    
    print("\n⚔️  THE PURIFICATION BEGINS  ⚔️\n")
    game.play()


if __name__ == "__main__":
    main()