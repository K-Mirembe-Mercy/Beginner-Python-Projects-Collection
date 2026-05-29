#!/usr/bin/env python3
"""
=============================================================================
  MAMA'S KITCHEN: A JOURNEY TO FEED THE CHILDREN
  An African-themed Python adventure game about feeding hungry children
  across the villages and markets of West, East, and Southern Africa.
=============================================================================
"""

import random
import time
import os
import sys
import textwrap
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
#  DISPLAY / UTILITY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

WIDTH = 70

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def slow_print(text: str, delay: float = 0.03):
    """Print text character by character for dramatic effect."""
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def box_print(text: str, char: str = "═"):
    """Print text inside a decorative box."""
    lines = textwrap.wrap(text, WIDTH - 4)
    border = char * (WIDTH)
    print(border)
    for line in lines:
        print(f"  {line}")
    print(border)

def section(title: str):
    pad = (WIDTH - len(title) - 2) // 2
    print("\n" + "─" * pad + f" {title} " + "─" * pad)

def pause(msg: str = "Press ENTER to continue..."):
    input(f"\n  {msg}")

def choice_menu(options: list[str]) -> int:
    """Display numbered menu, return 1-based index chosen."""
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt}")
    while True:
        raw = input("\n  Your choice: ").strip()
        if raw.isdigit():
            val = int(raw)
            if 1 <= val <= len(options):
                return val
        print("  Please enter a valid number.")

def wrap(text: str):
    for line in textwrap.wrap(text, WIDTH - 2):
        print(f"  {line}")

# ─────────────────────────────────────────────────────────────────────────────
#  GAME DATA  ─  FOOD ITEMS
# ─────────────────────────────────────────────────────────────────────────────

FOOD_DATA = {
    # name: (nutrition, cost, prep_time_minutes, region, description)
    "Ugali":         (35, 5,  10, "East Africa",     "Stiff maize porridge, the backbone of millions of meals."),
    "Jollof Rice":   (40, 8,  25, "West Africa",     "Smoky tomato rice beloved from Lagos to Accra."),
    "Injera":        (30, 6,  40, "East Africa",     "Spongy sourdough flatbread, perfect for scooping stews."),
    "Pap":           (28, 4,  15, "Southern Africa", "Smooth maize meal porridge, gentle on little stomachs."),
    "Egusi Soup":    (50, 10, 30, "West Africa",     "Rich melon-seed soup packed with protein and greens."),
    "Sukuma Wiki":   (25, 3,  20, "East Africa",     "Stir-fried collard greens — name means 'stretch the week'."),
    "Sadza":         (35, 5,  12, "Southern Africa", "Thick maize porridge served with relish in Zimbabwe."),
    "Fufu":          (38, 6,  20, "West Africa",     "Pounded cassava and plantain — soft, filling comfort food."),
    "Nyama Choma":   (60, 15, 45, "East Africa",     "Roasted meat seasoned with simple spices over open fire."),
    "Pilau":         (45, 12, 35, "East Africa",     "Spiced rice with cumin, cardamom, and tender meat."),
    "Biltong":       (55, 14, 5,  "Southern Africa", "Air-dried spiced meat, a protein-rich snack."),
    "Akara":         (32, 7,  25, "West Africa",     "Deep-fried bean cakes, crispy outside, fluffy inside."),
    "Matoke":        (30, 5,  30, "East Africa",     "Steamed green bananas — starchy and satisfying."),
    "Boerewors":     (58, 13, 20, "Southern Africa", "Spiced farmer's sausage grilled over coals."),
    "Thieboudienne": (48, 11, 50, "West Africa",     "Senegalese national dish: fish and rice in tomato broth."),
    "Githeri":       (42, 6,  35, "East Africa",     "Boiled maize and beans — simple, complete protein."),
    "Mopane Worms":  (65, 8,  15, "Southern Africa", "Dried caterpillars — a surprisingly nutritious delicacy."),
    "Kenkey":        (33, 5,  60, "West Africa",     "Fermented corn dumplings, served with pepper sauce."),
    "Chakalaka":     (22, 4,  20, "Southern Africa", "Spicy vegetable relish with beans and peppers."),
    "Mandazi":       (28, 3,  30, "East Africa",     "Coconut-scented fried dough — East Africa's doughnut."),
}

INGREDIENT_DATA = {
    # ingredient: (cost, nutritional_bonus, locations_found)
    "Maize Flour":    (2, 5,  ["Market", "Farm"]),
    "Tomatoes":       (1, 3,  ["Market", "Farm", "Garden"]),
    "Onions":         (1, 2,  ["Market", "Farm"]),
    "Beans":          (3, 8,  ["Market", "Farm"]),
    "Cassava":        (2, 6,  ["Farm", "Forest"]),
    "Plantain":       (2, 5,  ["Market", "Farm"]),
    "Spinach":        (1, 4,  ["Garden", "Market"]),
    "Groundnuts":     (3, 7,  ["Market", "Farm"]),
    "Palm Oil":       (2, 3,  ["Market"]),
    "Dried Fish":     (4, 9,  ["Market", "River"]),
    "Chicken":        (6, 12, ["Market", "Village"]),
    "Goat Meat":      (8, 14, ["Market", "Village"]),
    "Sorghum":        (3, 6,  ["Farm"]),
    "Millet":         (3, 6,  ["Farm"]),
    "Sweet Potato":   (2, 7,  ["Farm", "Garden"]),
    "Coconut":        (3, 5,  ["Market", "Forest"]),
    "Banana":         (1, 4,  ["Farm", "Garden"]),
    "Lemon":          (1, 2,  ["Garden", "Market"]),
    "Chilli Pepper":  (1, 1,  ["Garden", "Market"]),
    "Salt":           (1, 0,  ["Market"]),
}

# ─────────────────────────────────────────────────────────────────────────────
#  CHILDREN DATA
# ─────────────────────────────────────────────────────────────────────────────

CHILD_NAMES = [
    "Amara", "Kofi", "Zuri", "Tendai", "Afia", "Jelani", "Sade", "Obinna",
    "Naledi", "Kwame", "Abena", "Chidi", "Fatima", "Emeka", "Nala", "Seun",
    "Thabo", "Akinyi", "Bamidele", "Zawadi", "Chukwu", "Miriam", "Luca",
    "Adaeze", "Sipho", "Yetunde", "Olumide", "Zanele", "Jabari", "Akosua",
]

CHILD_STORIES = [
    "hasn't eaten since yesterday morning and is too weak to play.",
    "walked 5 km to school on an empty stomach today.",
    "shares whatever little food there is with three younger siblings.",
    "dreams of becoming a doctor but struggles to concentrate when hungry.",
    "helps her mother sell firewood to earn enough for one meal a day.",
    "lost his father last year and now relies on the village for support.",
    "is the brightest student in class but often faints from hunger.",
    "tends the family goats hoping to earn enough for dinner tonight.",
    "wakes up before sunrise to fetch water before school.",
    "smiled for the first time in weeks when given a warm bowl of soup.",
]

# ─────────────────────────────────────────────────────────────────────────────
#  VILLAGE / LOCATION DATA
# ─────────────────────────────────────────────────────────────────────────────

VILLAGES = {
    "Kigali Village": {
        "region": "East Africa",
        "children": 8,
        "description": "A hillside community in Rwanda where terraced fields meet red-dirt paths.",
        "available_foods": ["Ugali", "Sukuma Wiki", "Matoke", "Githeri"],
        "market_distance": 3,
        "difficulty": 1,
    },
    "Lagos Quarter": {
        "region": "West Africa",
        "children": 12,
        "description": "A bustling neighbourhood on the Lagos mainland, busy and vibrant.",
        "available_foods": ["Jollof Rice", "Egusi Soup", "Akara", "Fufu"],
        "market_distance": 1,
        "difficulty": 2,
    },
    "Soweto Township": {
        "region": "Southern Africa",
        "children": 10,
        "description": "A lively township outside Johannesburg, full of colour and community spirit.",
        "available_foods": ["Pap", "Chakalaka", "Biltong", "Boerewors"],
        "market_distance": 2,
        "difficulty": 2,
    },
    "Addis Heights": {
        "region": "East Africa",
        "children": 15,
        "description": "A mountain community in Ethiopia where the air is thin and winters are cold.",
        "available_foods": ["Injera", "Matoke", "Githeri", "Sukuma Wiki"],
        "market_distance": 5,
        "difficulty": 3,
    },
    "Dakar Coast": {
        "region": "West Africa",
        "children": 9,
        "description": "A fishing village near Dakar where Atlantic breezes carry the smell of the sea.",
        "available_foods": ["Thieboudienne", "Jollof Rice", "Kenkey", "Akara"],
        "market_distance": 2,
        "difficulty": 2,
    },
    "Bulawayo Plains": {
        "region": "Southern Africa",
        "children": 11,
        "description": "A semi-arid plain in Zimbabwe where droughts test every family's resilience.",
        "available_foods": ["Sadza", "Mopane Worms", "Chakalaka", "Pap"],
        "market_distance": 6,
        "difficulty": 4,
    },
    "Mombasa Harbour": {
        "region": "East Africa",
        "children": 7,
        "description": "A coastal settlement near Kenya's old port, fragrant with spices.",
        "available_foods": ["Pilau", "Mandazi", "Nyama Choma", "Ugali"],
        "market_distance": 1,
        "difficulty": 2,
    },
    "Kumasi Market Town": {
        "region": "West Africa",
        "children": 14,
        "description": "A trading hub in Ghana's Ashanti region, loud with merchants and colour.",
        "available_foods": ["Fufu", "Egusi Soup", "Jollof Rice", "Kenkey"],
        "market_distance": 1,
        "difficulty": 3,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  RANDOM EVENTS
# ─────────────────────────────────────────────────────────────────────────────

GOOD_EVENTS = [
    ("A generous farmer donates a bag of maize to the children!", "maize", 10),
    ("The village elder blesses your kitchen — cooking time halved today!", "time_boost", 0),
    ("A church group arrives and contributes 20 coins to the food fund.", "coins", 20),
    ("A rain shower waters the community garden — free vegetables!", "vegetables", 8),
    ("An NGO truck delivers dried beans and rice to the village.", "beans_rice", 15),
    ("A local teacher organises a cooking class — you gain extra skill!", "skill", 5),
    ("Children from the next village help with washing and chopping.", "help", 0),
    ("A market vendor gives you a discount — all food costs halved today!", "discount", 0),
]

BAD_EVENTS = [
    ("Heavy rains flood the road — market is unreachable today.", "flood", 0),
    ("Ants invade the food store! You lose some ingredients.", "ants", -5),
    ("A strong wind extinguishes the cooking fire — lost prep time.", "wind", 0),
    ("A child's illness means extra nutrition needed urgently.", "illness", -10),
    ("The market price of maize doubles due to regional shortage.", "price_up", 0),
    ("Your cooking pot breaks — you must borrow or buy a new one.", "pot_break", -8),
    ("Thieves steal coins from the community food fund.", "theft", -15),
    ("Drought warning — water rationing affects cooking!", "drought", 0),
]

NEUTRAL_EVENTS = [
    "A storyteller visits and the children are distracted but happy.",
    "A football match in the village square lifts everyone's spirits.",
    "The eldest grandmother shares an ancient recipe from memory.",
    "A photographer from a newspaper visits to document the village.",
    "Children sing traditional songs while waiting for food.",
    "A travelling merchant passes through with spices from faraway lands.",
    "The community meets under the big acacia tree to discuss plans.",
    "A bright rainbow appears over the village after morning rain.",
]

# ─────────────────────────────────────────────────────────────────────────────
#  ACHIEVEMENTS
# ─────────────────────────────────────────────────────────────────────────────

ACHIEVEMENTS = {
    "first_meal":       ("First Meal 🍲",        "Served your very first meal to a hungry child."),
    "ten_children":     ("Ten Smiles 😊",         "Fed 10 children in a single day."),
    "chef_level_2":     ("Sous-Chef 👨‍🍳",          "Reached Chef Level 2."),
    "chef_level_3":     ("Master Chef 🏆",         "Reached Chef Level 3."),
    "all_regions":      ("Pan-African 🌍",         "Cooked in all three African regions."),
    "no_waste":         ("Zero Waste ♻️",          "Completed a day without wasting any food."),
    "market_master":    ("Market Master 🛒",       "Visited the market 10 times."),
    "generous":         ("Heart of Gold ❤️",      "Donated food to another village."),
    "crisis_cook":      ("Crisis Cook 🔥",         "Fed children during a flood or drought event."),
    "hundred_meals":    ("100 Meals! 🎉",          "Served 100 meals total across all villages."),
    "five_villages":    ("Village Hopper 🏘️",     "Helped children in 5 different villages."),
    "ingredient_hoard": ("Pantry Full 🧺",         "Stored 15 different ingredients at once."),
    "speed_cook":       ("Speed Cook ⚡",          "Prepared 3 dishes in one cooking session."),
    "nutrition_star":   ("Nutrition Star ⭐",      "Served a meal with over 50 nutrition points."),
}

# ─────────────────────────────────────────────────────────────────────────────
#  PLAYER CLASS
# ─────────────────────────────────────────────────────────────────────────────

class Player:
    def __init__(self, name: str):
        self.name = name
        self.coins = 50
        self.chef_level = 1
        self.chef_xp = 0
        self.xp_to_next = 100
        self.inventory: dict[str, int] = {}          # ingredient → qty
        self.cooked_meals: dict[str, int] = {}        # food → times cooked
        self.children_fed_today = 0
        self.children_fed_total = 0
        self.meals_served_total = 0
        self.villages_helped: set[str] = set()
        self.regions_cooked: set[str] = set()
        self.market_visits = 0
        self.donations_made = 0
        self.achievements: set[str] = set()
        self.current_village: Optional[str] = None
        self.active_discount = False
        self.crisis_active = False
        self.flood_active = False
        self.drought_active = False
        self.day = 1
        self.hunger_crisis_days = 0

    # ── XP / LEVELLING ───────────────────────────────────────────────────────

    def gain_xp(self, amount: int):
        self.chef_xp += amount
        while self.chef_xp >= self.xp_to_next:
            self.chef_xp -= self.xp_to_next
            self.chef_level += 1
            self.xp_to_next = int(self.xp_to_next * 1.4)
            print(f"\n  ⭐ LEVEL UP! You are now Chef Level {self.chef_level}!")
            if self.chef_level == 2:
                self.unlock_achievement("chef_level_2")
            if self.chef_level == 3:
                self.unlock_achievement("chef_level_3")

    # ── ACHIEVEMENTS ─────────────────────────────────────────────────────────

    def unlock_achievement(self, key: str):
        if key not in self.achievements and key in ACHIEVEMENTS:
            self.achievements.add(key)
            name, desc = ACHIEVEMENTS[key]
            print(f"\n  🏅 ACHIEVEMENT UNLOCKED: {name}")
            print(f"     {desc}")

    def check_achievements(self):
        if self.meals_served_total >= 1:
            self.unlock_achievement("first_meal")
        if self.children_fed_today >= 10:
            self.unlock_achievement("ten_children")
        if len(self.regions_cooked) >= 3:
            self.unlock_achievement("all_regions")
        if self.market_visits >= 10:
            self.unlock_achievement("market_master")
        if self.meals_served_total >= 100:
            self.unlock_achievement("hundred_meals")
        if len(self.villages_helped) >= 5:
            self.unlock_achievement("five_villages")
        if len(self.inventory) >= 15:
            self.unlock_achievement("ingredient_hoard")

    # ── INVENTORY ────────────────────────────────────────────────────────────

    def add_ingredient(self, item: str, qty: int = 1):
        self.inventory[item] = self.inventory.get(item, 0) + qty

    def remove_ingredient(self, item: str, qty: int = 1) -> bool:
        if self.inventory.get(item, 0) >= qty:
            self.inventory[item] -= qty
            if self.inventory[item] == 0:
                del self.inventory[item]
            return True
        return False

    def show_inventory(self):
        section("YOUR PANTRY")
        if not self.inventory:
            print("  (empty — visit a market or farm!)")
        else:
            for item, qty in sorted(self.inventory.items()):
                cost, nut, _ = INGREDIENT_DATA[item]
                print(f"  {item:<20} x{qty}  (nutrition +{nut} each)")

    # ── STATUS ───────────────────────────────────────────────────────────────

    def show_status(self):
        section("YOUR STATUS")
        print(f"  Name          : {self.name}")
        print(f"  Chef Level    : {self.chef_level}  (XP: {self.chef_xp}/{self.xp_to_next})")
        print(f"  Coins         : {self.coins} 🪙")
        print(f"  Day           : {self.day}")
        print(f"  Village       : {self.current_village or 'None'}")
        print(f"  Children Fed  : {self.children_fed_total} total  ({self.children_fed_today} today)")
        print(f"  Meals Served  : {self.meals_served_total}")
        print(f"  Achievements  : {len(self.achievements)}/{len(ACHIEVEMENTS)}")
        print(f"  Villages Helped: {len(self.villages_helped)}")
        print(f"  Regions Cooked : {', '.join(self.regions_cooked) if self.regions_cooked else 'None yet'}")

# ─────────────────────────────────────────────────────────────────────────────
#  GAME ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class Game:
    def __init__(self):
        self.player: Optional[Player] = None
        self.running = True
        self.game_over = False
        self.total_days = 30   # 30-day campaign
        self.win_target = 200  # meals to win

    # ── TITLE SCREEN ─────────────────────────────────────────────────────────

    def title_screen(self):
        clear()
        print("═" * WIDTH)
        slow_print("          M A M A ' S   K I T C H E N", 0.04)
        print("          A Journey to Feed the Children")
        print("═" * WIDTH)
        print()
        wrap("Set across the villages, markets, and plains of Africa,")
        wrap("you play as a community cook on a mission to ensure")
        wrap("no child goes to bed hungry. Gather ingredients, cook")
        wrap("nourishing meals, and bring hope one bowl at a time.")
        print()
        print("═" * WIDTH)
        print()

    # ── NEW GAME ──────────────────────────────────────────────────────────────

    def new_game(self):
        self.title_screen()
        slow_print("  What is your name, dear cook?", 0.04)
        name = input("  > ").strip() or "Amara"
        self.player = Player(name)
        clear()
        self.title_screen()
        slow_print(f"\n  Welcome, {self.player.name}!", 0.04)
        print()
        wrap("The elders of the village have chosen you to lead the")
        wrap("community kitchen. Children across Africa are hungry.")
        wrap("You have 30 days and must serve 200 meals to win.")
        wrap("Begin your journey by choosing a village to help.")
        print()
        pause()
        self.choose_village()

    # ── VILLAGE SELECTION ────────────────────────────────────────────────────

    def choose_village(self):
        clear()
        section("CHOOSE A VILLAGE TO HELP")
        names = list(VILLAGES.keys())
        helped = self.player.villages_helped
        for i, vname in enumerate(names, 1):
            v = VILLAGES[vname]
            star = "✓" if vname in helped else " "
            diff = "★" * v["difficulty"]
            print(f"  [{i}] {star} {vname}")
            print(f"       Region: {v['region']}  |  Children: {v['children']}  |  Difficulty: {diff}")
            wrap(f"       {v['description']}")
            print()
        print(f"  [{len(names)+1}] Stay in current village")
        ch = choice_menu([v for v in names] + ["Stay here"])
        if ch <= len(names):
            chosen = names[ch - 1]
            self.player.current_village = chosen
            self.player.villages_helped.add(chosen)
            v = VILLAGES[chosen]
            clear()
            box_print(f"You travel to {chosen}!")
            print()
            wrap(v["description"])
            slow_print(f"\n  There are {v['children']} hungry children waiting...", 0.04)
            print()
            pause()

    # ── DAILY LOOP ────────────────────────────────────────────────────────────

    def daily_loop(self):
        while self.running and self.player.day <= self.total_days:
            self.player.children_fed_today = 0
            self.player.active_discount = False
            self.player.crisis_active = False

            clear()
            self.show_day_header()

            # Random event
            self.trigger_random_event()

            # Main daily actions
            self.daily_actions()

            # End of day
            self.end_of_day()

            self.player.day += 1

            # Check win/lose
            if self.player.meals_served_total >= self.win_target:
                self.victory()
                return
            if self.player.day > self.total_days:
                self.game_over_screen()
                return

    def show_day_header(self):
        p = self.player
        vname = p.current_village or "No Village"
        v = VILLAGES.get(vname, {})
        region = v.get("region", "Africa")
        print("═" * WIDTH)
        print(f"  DAY {p.day}/{self.total_days}   |   {vname}  ({region})")
        print(f"  Coins: {p.coins} 🪙   |   Chef Lvl: {p.chef_level}   |"
              f"   Meals Served: {p.meals_served_total}/{self.win_target}")
        print(f"  Children Fed Today: {p.children_fed_today}"
              f"   |   Total: {p.children_fed_total}")
        print("═" * WIDTH)

    # ── RANDOM EVENTS ────────────────────────────────────────────────────────

    def trigger_random_event(self):
        roll = random.random()
        if roll < 0.25:
            event = random.choice(GOOD_EVENTS)
            self.handle_good_event(event)
        elif roll < 0.45:
            event = random.choice(BAD_EVENTS)
            self.handle_bad_event(event)
        elif roll < 0.55:
            msg = random.choice(NEUTRAL_EVENTS)
            section("VILLAGE NEWS")
            wrap(f"📢 {msg}")
            print()

    def handle_good_event(self, event):
        msg, etype, value = event
        section("GOOD NEWS! 🌟")
        wrap(f"✨ {msg}")
        p = self.player
        if etype == "coins" and value > 0:
            p.coins += value
            print(f"  (+{value} coins added to your fund)")
        elif etype in ("maize", "vegetables", "beans_rice"):
            items = {
                "maize": [("Maize Flour", 3)],
                "vegetables": [("Spinach", 4), ("Tomatoes", 3)],
                "beans_rice": [("Beans", 5)],
            }
            for item, qty in items[etype]:
                p.add_ingredient(item, qty)
                print(f"  (+{qty} {item} added to pantry)")
        elif etype == "discount":
            p.active_discount = True
            print("  (Prices halved for today!)")
        elif etype == "skill":
            p.gain_xp(value * 4)
            print(f"  (+{value*4} XP gained)")
        print()

    def handle_bad_event(self, event):
        msg, etype, value = event
        section("BAD NEWS ⚠️")
        wrap(f"⚠️  {msg}")
        p = self.player
        if etype == "ants" and value < 0:
            # Remove some random ingredients
            if p.inventory:
                item = random.choice(list(p.inventory.keys()))
                lost = min(p.inventory[item], abs(value) // 2 + 1)
                p.remove_ingredient(item, lost)
                print(f"  (Lost {lost}x {item} from pantry)")
        elif etype == "theft" and value < 0:
            loss = min(p.coins, abs(value))
            p.coins -= loss
            print(f"  (Lost {loss} coins)")
        elif etype == "pot_break" and value < 0:
            cost = abs(value)
            p.coins = max(0, p.coins - cost)
            print(f"  (Spent {cost} coins on a new pot)")
        elif etype == "flood":
            p.flood_active = True
            print("  (Market is unreachable today — no shopping!)")
        elif etype == "drought":
            p.drought_active = True
            print("  (Water is scarce — all meals cost +5 extra nutrition to prepare.)")
        elif etype == "illness":
            p.hunger_crisis_days += 1
            p.crisis_active = True
            print("  (Extra nutrition urgently needed for sick children!)")
        if p.crisis_active or p.flood_active or p.drought_active:
            p.unlock_achievement("crisis_cook")
        print()

    # ── DAILY ACTIONS MENU ───────────────────────────────────────────────────

    def daily_actions(self):
        while True:
            section("DAILY ACTIONS")
            p = self.player
            options = [
                "🍳  Cook a Meal",
                "🛒  Visit the Market",
                "🌾  Gather from Farm/Garden",
                "👧  Meet the Children",
                "🏘️  Travel to Another Village",
                "📦  Check Pantry",
                "📊  View Status & Achievements",
                "💝  Donate Food to Neighbour",
                "⏭️  End Day Early",
            ]
            ch = choice_menu(options)
            if ch == 1:
                self.cook_meal()
            elif ch == 2:
                self.visit_market()
            elif ch == 3:
                self.gather_ingredients()
            elif ch == 4:
                self.meet_children()
            elif ch == 5:
                self.choose_village()
            elif ch == 6:
                clear()
                self.show_day_header()
                self.player.show_inventory()
                pause()
            elif ch == 7:
                clear()
                self.show_day_header()
                self.player.show_status()
                self.show_achievements()
                pause()
            elif ch == 8:
                self.donate_food()
            elif ch == 9:
                break

    # ── COOK A MEAL ──────────────────────────────────────────────────────────

    def cook_meal(self):
        clear()
        section("COOK A MEAL 🍳")
        p = self.player
        vname = p.current_village
        if not vname:
            wrap("You need to be in a village first!")
            pause()
            return

        v = VILLAGES[vname]
        available = v["available_foods"]
        print(f"  Dishes you can prepare in {vname}:")
        print()

        cookable = []
        for food in available:
            nutr, cost, prep, region, desc = FOOD_DATA[food]
            actual_cost = cost // 2 if p.active_discount else cost
            print(f"  {food}")
            print(f"    Nutrition: {nutr}  |  Cost: {actual_cost} coins  |"
                  f"  Prep: {prep} min  |  Region: {region}")
            wrap(f"    {desc}")
            cookable.append((food, actual_cost, nutr, region))
            print()

        print(f"  [0] Cancel")
        raw = input("  Choose dish number: ").strip()
        if raw == "0" or not raw.isdigit():
            return
        idx = int(raw) - 1
        if idx < 0 or idx >= len(cookable):
            wrap("Invalid choice.")
            pause()
            return

        food, cost, nutr, region = cookable[idx]
        if p.coins < cost:
            wrap(f"Not enough coins! You need {cost} but have {p.coins}.")
            pause()
            return

        # Cooking animation
        clear()
        section(f"COOKING: {food}")
        _, _, prep_time, region, desc = FOOD_DATA[food]
        wrap(desc)
        print()
        slow_print("  🔥 Lighting the fire...", 0.05)
        time.sleep(0.3)
        slow_print("  🥣 Preparing ingredients...", 0.05)
        time.sleep(0.3)
        slow_print("  ♨️  Cooking over the flames...", 0.05)
        time.sleep(0.3)
        slow_print("  🌿 Adding herbs and spices...", 0.05)
        time.sleep(0.3)
        slow_print(f"  ✅ {food} is ready!", 0.05)
        print()

        p.coins -= cost
        p.cooked_meals[food] = p.cooked_meals.get(food, 0) + 1
        p.regions_cooked.add(region)

        # How many children to feed
        children_count = v["children"]
        portions = max(1, nutr // 10)
        fed = min(children_count - p.children_fed_today, portions)
        fed = max(1, fed)

        p.children_fed_today += fed
        p.children_fed_total += fed
        p.meals_served_total += 1

        xp_gain = nutr + fed * 3 + (10 if p.chef_level < 3 else 5)
        p.gain_xp(xp_gain)

        # Present meal to children
        print()
        section("FEEDING THE CHILDREN 👧🧒")
        for _ in range(min(fed, 4)):
            child = random.choice(CHILD_NAMES)
            story = random.choice(CHILD_STORIES)
            slow_print(f"  {child} {story}", 0.02)
            time.sleep(0.1)

        print()
        wrap(f"🍽️  You served {food} to {fed} children!")
        print(f"  (+{xp_gain} XP, -{cost} coins)")
        print()

        if nutr >= 50:
            p.unlock_achievement("nutrition_star")

        # Speed cook tracking (session)
        if not hasattr(self, "_session_cooks"):
            self._session_cooks = 0
        self._session_cooks += 1
        if self._session_cooks >= 3:
            p.unlock_achievement("speed_cook")

        p.check_achievements()
        pause()

    # ── VISIT MARKET ─────────────────────────────────────────────────────────

    def visit_market(self):
        clear()
        p = self.player
        if p.flood_active:
            section("MARKET CLOSED ⚠️")
            wrap("The road is flooded — you cannot reach the market today.")
            pause()
            return

        p.market_visits += 1
        section("VILLAGE MARKET 🛒")
        print(f"  Your coins: {p.coins} 🪙")
        if p.active_discount:
            print("  🎉 SPECIAL: All prices halved today!")
        print()

        items = list(INGREDIENT_DATA.items())
        random.shuffle(items)
        available_today = items[:12]  # market stocks vary

        print(f"  {'ITEM':<22} {'COST':>6}  NUTRITION  DESCRIPTION")
        print("  " + "─" * 56)
        for i, (name, (base_cost, nut, locs)) in enumerate(available_today, 1):
            cost = base_cost // 2 if p.active_discount else base_cost
            print(f"  [{i:2}] {name:<20} {cost:>4}🪙   +{nut:<3}      ")

        print(f"\n  [0] Leave market")
        print()

        while True:
            raw = input("  Buy item # (or 0 to leave): ").strip()
            if raw == "0":
                break
            if not raw.isdigit():
                continue
            idx = int(raw) - 1
            if idx < 0 or idx >= len(available_today):
                print("  Invalid number.")
                continue

            name, (base_cost, nut, locs) = available_today[idx]
            cost = base_cost // 2 if p.active_discount else base_cost

            qty_raw = input(f"  How many {name}? (cost: {cost} each) > ").strip()
            if not qty_raw.isdigit() or int(qty_raw) <= 0:
                print("  Invalid quantity.")
                continue
            qty = int(qty_raw)
            total = cost * qty
            if total > p.coins:
                print(f"  Not enough coins. (Need {total}, have {p.coins})")
                continue

            p.coins -= total
            p.add_ingredient(name, qty)
            print(f"  ✓ Bought {qty}x {name} for {total} coins. (Pantry: {p.inventory.get(name,0)})")
            p.check_achievements()

    # ── GATHER INGREDIENTS ───────────────────────────────────────────────────

    def gather_ingredients(self):
        clear()
        section("GATHER INGREDIENTS 🌾")
        p = self.player
        wrap("You explore the surroundings — farms, gardens, and the forest edge.")
        print()
        locations = ["Farm", "Garden", "Forest", "River"]
        print("  Where will you gather?")
        loc_choice = choice_menu(locations + ["Cancel"])
        if loc_choice > len(locations):
            return
        chosen_loc = locations[loc_choice - 1]

        # Find items available at this location
        found_items = [
            (name, data) for name, data in INGREDIENT_DATA.items()
            if chosen_loc in data[2]
        ]
        if not found_items:
            wrap("Nothing found here today.")
            pause()
            return

        slow_print(f"\n  You head to the {chosen_loc}...", 0.04)
        time.sleep(0.5)

        gathered = []
        for name, (_, nut, _) in found_items:
            if random.random() < 0.55:
                qty = random.randint(1, 3)
                p.add_ingredient(name, qty)
                gathered.append((name, qty))

        if gathered:
            print("\n  You gathered:")
            for name, qty in gathered:
                print(f"    + {qty}x {name}")
            p.gain_xp(5 * len(gathered))
            print(f"  (+{5 * len(gathered)} XP)")
        else:
            wrap("Nothing of use found today. Try again tomorrow.")
        p.check_achievements()
        pause()

    # ── MEET THE CHILDREN ────────────────────────────────────────────────────

    def meet_children(self):
        clear()
        section("MEET THE CHILDREN 👧")
        vname = self.player.current_village
        if not vname:
            wrap("Travel to a village first.")
            pause()
            return
        v = VILLAGES[vname]
        p = self.player
        print(f"  You sit with the children of {vname}.\n")
        for _ in range(min(v["children"], 5)):
            child = random.choice(CHILD_NAMES)
            story = random.choice(CHILD_STORIES)
            slow_print(f"  🧒 {child} {story}", 0.02)
            time.sleep(0.15)
        print()
        wrap(f"There are {v['children']} children in this village.")
        wrap(f"Today you have fed {p.children_fed_today} of them.")
        remaining = max(0, v["children"] - p.children_fed_today)
        if remaining > 0:
            wrap(f"{remaining} children are still waiting for a meal.")
        else:
            wrap("All children in this village have been fed today! 🎉")
        p.gain_xp(3)
        pause()

    # ── DONATE FOOD ──────────────────────────────────────────────────────────

    def donate_food(self):
        clear()
        section("DONATE FOOD 💝")
        p = self.player
        if not p.inventory:
            wrap("Your pantry is empty — nothing to donate.")
            pause()
            return
        wrap("Share ingredients with a neighbouring village in need.")
        print()
        p.show_inventory()
        print()
        items = list(p.inventory.keys())
        for i, item in enumerate(items, 1):
            print(f"  [{i}] {item}  (x{p.inventory[item]})")
        print(f"  [0] Cancel")
        raw = input("  Donate which item? ").strip()
        if raw == "0" or not raw.isdigit():
            return
        idx = int(raw) - 1
        if idx < 0 or idx >= len(items):
            return
        item = items[idx]
        qty_raw = input(f"  How many {item} to donate? ").strip()
        if not qty_raw.isdigit() or int(qty_raw) <= 0:
            return
        qty = int(qty_raw)
        if p.remove_ingredient(item, qty):
            print(f"\n  ❤️  You donated {qty}x {item} to a neighbouring village!")
            p.donations_made += 1
            p.gain_xp(10 * qty)
            p.unlock_achievement("generous")
            print(f"  (+{10*qty} XP)")
        else:
            wrap("Not enough of that ingredient.")
        pause()

    # ── END OF DAY ───────────────────────────────────────────────────────────

    def end_of_day(self):
        clear()
        p = self.player
        section(f"END OF DAY {p.day}")

        print(f"  Children fed today : {p.children_fed_today}")
        print(f"  Total meals served : {p.meals_served_total}/{self.win_target}")
        print(f"  Coins remaining    : {p.coins}")
        print(f"  Chef XP            : {p.chef_xp}/{p.xp_to_next}")
        print()

        # Small daily coin income (community support)
        daily_income = 5 + p.chef_level * 2
        p.coins += daily_income
        print(f"  💰 Community support gives you {daily_income} coins for tomorrow.")

        if p.children_fed_today == 0:
            wrap("⚠️  You didn't feed any children today. Try to cook more tomorrow!")
        elif p.children_fed_today >= 10:
            wrap("🌟 Amazing! You fed 10+ children today. The village thanks you!")
            p.gain_xp(20)

        days_left = self.total_days - p.day
        meals_needed = self.win_target - p.meals_served_total
        if days_left > 0 and meals_needed > 0:
            print(f"\n  {days_left} days left | {meals_needed} more meals needed to win.")

        p.check_achievements()
        print()
        pause("Press ENTER to start the next day...")
        self._session_cooks = 0

    # ── ACHIEVEMENTS DISPLAY ─────────────────────────────────────────────────

    def show_achievements(self):
        section("ACHIEVEMENTS")
        p = self.player
        for key, (name, desc) in ACHIEVEMENTS.items():
            status = "🏅" if key in p.achievements else "🔒"
            print(f"  {status} {name}")
            if key in p.achievements:
                print(f"     {desc}")

    # ── VICTORY / GAME OVER ───────────────────────────────────────────────────

    def victory(self):
        clear()
        print("═" * WIDTH)
        slow_print("  🎉  VICTORY! YOU FED THE CHILDREN!  🎉", 0.05)
        print("═" * WIDTH)
        print()
        wrap(f"Congratulations, {self.player.name}!")
        wrap(f"You served {self.player.meals_served_total} meals across the villages of Africa.")
        wrap(f"You helped children in {len(self.player.villages_helped)} villages.")
        wrap(f"You reached Chef Level {self.player.chef_level}.")
        wrap(f"You unlocked {len(self.player.achievements)} achievements.")
        print()
        wrap("Because of your dedication, no child in your community went to bed")
        wrap("hungry. The warmth of your kitchen spread hope across the continent.")
        print()
        wrap("🌍  Africa thanks you.  🌍")
        print()
        self.show_achievements()
        print()
        pause("Press ENTER to return to the main menu...")

    def game_over_screen(self):
        clear()
        p = self.player
        print("═" * WIDTH)
        slow_print("  📅  30 DAYS HAVE PASSED  📅", 0.05)
        print("═" * WIDTH)
        print()
        wrap(f"Your 30-day mission is complete, {p.name}.")
        print(f"  Total meals served : {p.meals_served_total} / {self.win_target} needed")
        print(f"  Children fed total : {p.children_fed_total}")
        print(f"  Villages helped    : {len(p.villages_helped)}")
        print(f"  Chef Level reached : {p.chef_level}")
        print(f"  Achievements       : {len(p.achievements)}/{len(ACHIEVEMENTS)}")
        print()
        if p.meals_served_total >= self.win_target * 0.75:
            wrap("So close! You fed most of the children. A few still need you — try again!")
        elif p.meals_served_total >= self.win_target * 0.5:
            wrap("A good effort! Half the goal reached. With more planning you can do it!")
        else:
            wrap("The hunger crisis continues. The children need a stronger effort. Try again!")
        print()
        pause("Press ENTER to return to the main menu...")

    # ── MAIN MENU ────────────────────────────────────────────────────────────

    def main_menu(self):
        while True:
            clear()
            self.title_screen()
            print("  [1] New Game")
            print("  [2] How to Play")
            print("  [3] About the Game")
            print("  [4] Quit")
            ch = choice_menu(["New Game", "How to Play", "About the Game", "Quit"])
            if ch == 1:
                self.player = None
                self.new_game()
                self.daily_loop()
            elif ch == 2:
                self.how_to_play()
            elif ch == 3:
                self.about_game()
            elif ch == 4:
                clear()
                slow_print("\n  Thank you for feeding Africa's children. 🌍", 0.04)
                slow_print("  Every meal matters. Every child counts.\n", 0.04)
                break

    def how_to_play(self):
        clear()
        section("HOW TO PLAY")
        instructions = [
            "GOAL: Serve 200 meals to hungry children across Africa in 30 days.",
            "",
            "DAILY CYCLE:",
            "  Each day you choose actions from the menu:",
            "  • Cook a Meal  — spend coins to prepare a dish for children.",
            "  • Visit Market — spend coins to buy ingredients for cooking.",
            "  • Gather       — explore farms/gardens for free ingredients.",
            "  • Meet Kids    — learn about the children you are helping.",
            "  • Travel       — move to a new village with different dishes.",
            "  • Donate       — share food with neighbouring villages for XP.",
            "  • End Day      — finish the day and advance to the next.",
            "",
            "COINS:",
            "  You start with 50 coins. Each cooking session costs coins.",
            "  You earn a small daily income from community support.",
            "  Good events can give bonus coins; bad events can take them.",
            "",
            "CHEF LEVELS:",
            "  Gain XP by cooking meals, gathering, donating, and helping.",
            "  Higher levels unlock more XP and give greater daily income.",
            "",
            "EVENTS:",
            "  Each day a random event may occur — good, bad, or neutral.",
            "  Be ready for floods, droughts, or generous donations!",
            "",
            "ACHIEVEMENTS:",
            "  Unlock 14 achievements by reaching milestones in the game.",
            "",
            "WIN CONDITION:",
            "  Serve 200 total meals before the 30 days are up!",
        ]
        for line in instructions:
            print(f"  {line}")
        print()
        pause()

    def about_game(self):
        clear()
        section("ABOUT THIS GAME")
        text = [
            "Mama's Kitchen was created to raise awareness about childhood",
            "hunger across the African continent.",
            "",
            "According to UNICEF, millions of children in sub-Saharan Africa",
            "face food insecurity every day. Community kitchens, local farmers,",
            "and dedicated volunteers are on the front lines of this challenge.",
            "",
            "This game celebrates the resilience, warmth, and generosity of",
            "African communities — and the simple, powerful act of sharing food.",
            "",
            "Dishes featured in the game are real, beloved recipes from across",
            "West, East, and Southern Africa. Each has a story, a culture, and",
            "a place at the table.",
            "",
            "If you wish to support real hunger-relief efforts in Africa,",
            "consider organisations such as:",
            "  • World Food Programme (WFP) — wfp.org",
            "  • UNICEF Africa — unicef.org",
            "  • African Food Bank — africanfoodbank.org",
            "",
            "Thank you for playing. 🌍❤️",
        ]
        for line in text:
            wrap(line) if line else print()
        print()
        pause()

    # ── ENTRY POINT ──────────────────────────────────────────────────────────

    def run(self):
        self.main_menu()


# ─────────────────────────────────────────────────────────────────────────────
#  EXTRA GAME SYSTEMS: RECIPE BOOK, LEADERBOARD, MINI-GAMES
# ─────────────────────────────────────────────────────────────────────────────

class RecipeBook:
    """Tracks which dishes the player has cooked and their stats."""

    def __init__(self):
        self.entries: dict[str, dict] = {}

    def record(self, food: str, nutrition: int, children_fed: int):
        if food not in self.entries:
            self.entries[food] = {"times_cooked": 0, "total_children": 0, "total_nutrition": 0}
        e = self.entries[food]
        e["times_cooked"] += 1
        e["total_children"] += children_fed
        e["total_nutrition"] += nutrition

    def show(self):
        section("YOUR RECIPE BOOK 📖")
        if not self.entries:
            print("  No recipes cooked yet!")
            return
        for food, stats in sorted(self.entries.items(), key=lambda x: -x[1]["times_cooked"]):
            print(f"  {food}")
            print(f"    Cooked {stats['times_cooked']}x | "
                  f"Fed {stats['total_children']} children | "
                  f"Total nutrition: {stats['total_nutrition']}")


class NutritionCalculator:
    """Calculate combined nutritional value of a set of ingredients."""

    @staticmethod
    def calculate(ingredients: list[str]) -> int:
        total = 0
        for ing in ingredients:
            if ing in INGREDIENT_DATA:
                total += INGREDIENT_DATA[ing][1]
        return total

    @staticmethod
    def recommend_for_child(age: int) -> str:
        """Basic recommendation based on child's age."""
        if age <= 2:
            return "Soft pap or mashed matoke — easy to digest for toddlers."
        elif age <= 6:
            return "Ugali with sukuma wiki — filling and nutritious."
        elif age <= 12:
            return "Jollof rice with beans — protein and carbohydrates for growth."
        else:
            return "Githeri or injera with stew — balanced meal for teenagers."


class WeatherSystem:
    """Simulate seasonal weather patterns affecting crop yields."""

    SEASONS = {
        "dry": {
            "description": "The dry season — crops are scarce, water is precious.",
            "gather_bonus": 0.5,
            "market_price_mult": 1.3,
        },
        "rainy": {
            "description": "The rainy season — crops flourish but roads flood.",
            "gather_bonus": 1.5,
            "market_price_mult": 0.9,
        },
        "harvest": {
            "description": "Harvest season — abundance fills the markets.",
            "gather_bonus": 2.0,
            "market_price_mult": 0.8,
        },
        "planting": {
            "description": "Planting season — fields are being prepared.",
            "gather_bonus": 0.8,
            "market_price_mult": 1.1,
        },
    }

    def __init__(self):
        self.current = random.choice(list(self.SEASONS.keys()))

    def advance(self):
        seasons = list(self.SEASONS.keys())
        idx = seasons.index(self.current)
        self.current = seasons[(idx + 1) % len(seasons)]

    def info(self) -> str:
        return self.SEASONS[self.current]["description"]

    def gather_multiplier(self) -> float:
        return self.SEASONS[self.current]["gather_bonus"]

    def price_multiplier(self) -> float:
        return self.SEASONS[self.current]["market_price_mult"]


class ChildProfile:
    """Represent an individual child's needs and progress."""

    def __init__(self, name: str):
        self.name = name
        self.age = random.randint(2, 14)
        self.hunger_level = random.randint(60, 100)   # 100 = starving
        self.health = random.randint(40, 90)
        self.meals_received = 0
        self.favourite_food = random.choice(list(FOOD_DATA.keys()))
        self.story = random.choice(CHILD_STORIES)

    def feed(self, nutrition: int):
        reduction = min(self.hunger_level, nutrition // 2)
        self.hunger_level -= reduction
        self.health = min(100, self.health + nutrition // 10)
        self.meals_received += 1

    def status(self) -> str:
        if self.hunger_level >= 80:
            return "critically hungry"
        elif self.hunger_level >= 50:
            return "very hungry"
        elif self.hunger_level >= 30:
            return "hungry"
        else:
            return "well-fed"

    def describe(self) -> str:
        return (f"{self.name} (age {self.age}) — {self.status()}. "
                f"Favourite: {self.favourite_food}. {self.story}")


class CommunityGarden:
    """A shared garden that players can tend for bonus ingredients."""

    def __init__(self):
        self.plots: dict[str, int] = {}   # ingredient → days until harvest
        self.max_plots = 6

    def plant(self, ingredient: str):
        if len(self.plots) >= self.max_plots:
            return False, "Garden is full!"
        if ingredient not in INGREDIENT_DATA:
            return False, "Cannot grow that here."
        self.plots[ingredient] = 3  # 3 days to grow
        return True, f"Planted {ingredient} — ready in 3 days."

    def advance_day(self) -> list[str]:
        """Returns list of ingredients that are ready to harvest."""
        ready = []
        for ing in list(self.plots.keys()):
            self.plots[ing] -= 1
            if self.plots[ing] <= 0:
                ready.append(ing)
                del self.plots[ing]
        return ready

    def show(self):
        section("COMMUNITY GARDEN 🌱")
        if not self.plots:
            print("  No plants growing. Visit the garden to plant something!")
        else:
            for ing, days in self.plots.items():
                print(f"  {ing:<20} — ready in {days} day(s)")


class MarketPriceTracker:
    """Tracks price changes over time for market items."""

    def __init__(self):
        self.history: dict[str, list[int]] = {k: [v[0]] for k, v in INGREDIENT_DATA.items()}

    def update(self, multiplier: float = 1.0):
        for ing in self.history:
            base = INGREDIENT_DATA[ing][0]
            noise = random.uniform(-0.2, 0.2)
            new_price = max(1, int(base * multiplier * (1 + noise)))
            self.history[ing].append(new_price)

    def current_price(self, ingredient: str) -> int:
        if ingredient in self.history and self.history[ingredient]:
            return self.history[ingredient][-1]
        return INGREDIENT_DATA.get(ingredient, (5, 0, []))[0]

    def trend(self, ingredient: str) -> str:
        h = self.history.get(ingredient, [])
        if len(h) < 2:
            return "stable"
        if h[-1] > h[-2]:
            return "rising ↑"
        elif h[-1] < h[-2]:
            return "falling ↓"
        return "stable →"


class StoryNarrator:
    """Generate contextual story snippets for immersion."""

    MORNING_GREETINGS = [
        "The rooster crows and smoke rises from the first cooking fires.",
        "Dawn breaks over the acacia trees as children stir from sleep.",
        "The morning mist lifts to reveal a bright African sky.",
        "Birdsong fills the air as the village comes alive at dawn.",
        "The smell of wood smoke and morning dew greets a new day.",
    ]

    COOKING_SCENES = [
        "The sizzle of onions in hot oil draws children to the kitchen door.",
        "Steam rises from the pot as a rich aroma fills the compound.",
        "Little hands reach eagerly as the cooking smell spreads.",
        "The grandmother nods approvingly at the seasoning.",
        "A circle of children sits patiently, eyes bright with anticipation.",
    ]

    EVENING_REFLECTIONS = [
        "The setting sun paints the sky amber as children drift to sleep, full.",
        "Stars appear above the village as full bellies bring peaceful dreams.",
        "The fire burns low; the day's work is done. Another village fed.",
        "Laughter rings out as children play before bedtime — hunger forgotten.",
        "A grandmother whispers thanks into the cooling evening air.",
    ]

    @staticmethod
    def morning() -> str:
        return random.choice(StoryNarrator.MORNING_GREETINGS)

    @staticmethod
    def cooking() -> str:
        return random.choice(StoryNarrator.COOKING_SCENES)

    @staticmethod
    def evening() -> str:
        return random.choice(StoryNarrator.EVENING_REFLECTIONS)


class AfricanProverbs:
    """Display authentic African proverbs during gameplay."""

    PROVERBS = [
        ("It takes a village to raise a child.", "Igbo, Nigeria"),
        ("A child who is not embraced by the village will burn it down.", "African"),
        ("When the music changes, so does the dance.", "Hausa, West Africa"),
        ("Sticks in a bundle are unbreakable.", "Bondei, Tanzania"),
        ("Until the lion learns to write, every story will glorify the hunter.", "African"),
        ("Rain does not fall on one roof alone.", "Cameroonian"),
        ("If you want to go fast, go alone. If you want to go far, go together.", "African"),
        ("The forest would be silent if no bird sang except the one that sang best.", "African"),
        ("A child's eyes are big but the stomach is small.", "Swahili"),
        ("Food is the medicine of the body.", "African"),
        ("He who feeds you, controls you.", "African"),
        ("Sharing food is sharing life.", "Zulu, South Africa"),
        ("A good meal warms the soul as much as the body.", "West African"),
        ("The best way to eat an elephant in your path is cut it up.", "African"),
        ("Knowledge is like a garden: if it is not cultivated, it cannot be harvested.", "African"),
    ]

    @staticmethod
    def random_proverb() -> tuple[str, str]:
        return random.choice(AfricanProverbs.PROVERBS)

    @staticmethod
    def display():
        proverb, origin = AfricanProverbs.random_proverb()
        section("AFRICAN WISDOM 🌿")
        wrap(f'"{proverb}"')
        print(f"                           — {origin}")
        print()


# ─────────────────────────────────────────────────────────────────────────────
#  MINI-GAME: INGREDIENT SORTING
# ─────────────────────────────────────────────────────────────────────────────

class IngredientSortingGame:
    """
    A simple mini-game where the player identifies which region an
    ingredient/dish comes from.
    """

    QUESTIONS = [
        ("Ugali",         "East Africa",     ["East Africa", "West Africa", "Southern Africa"]),
        ("Jollof Rice",   "West Africa",     ["East Africa", "West Africa", "North Africa"]),
        ("Pap",           "Southern Africa", ["East Africa", "West Africa", "Southern Africa"]),
        ("Injera",        "East Africa",     ["West Africa",  "East Africa", "Central Africa"]),
        ("Biltong",       "Southern Africa", ["Southern Africa", "East Africa", "West Africa"]),
        ("Thieboudienne", "West Africa",     ["West Africa", "East Africa", "Southern Africa"]),
        ("Sadza",         "Southern Africa", ["East Africa", "West Africa", "Southern Africa"]),
        ("Pilau",         "East Africa",     ["East Africa", "West Africa", "North Africa"]),
    ]

    def play(self) -> int:
        """Returns coins earned."""
        clear()
        section("MINI-GAME: WHERE IS IT FROM? 🌍")
        wrap("Identify which region of Africa each dish comes from!")
        wrap("Earn 5 coins for each correct answer.")
        print()
        pause("Press ENTER to start...")

        score = 0
        qs = random.sample(self.QUESTIONS, min(5, len(self.QUESTIONS)))
        for i, (dish, correct, options) in enumerate(qs, 1):
            clear()
            print(f"\n  Question {i}/{len(qs)}: Where is {dish} from?\n")
            random.shuffle(options)
            ch = choice_menu(options)
            chosen = options[ch - 1]
            if chosen == correct:
                print(f"  ✅ Correct! {dish} is from {correct}.")
                score += 5
            else:
                print(f"  ❌ Wrong. {dish} is from {correct}.")
            time.sleep(1)

        clear()
        section("MINI-GAME OVER")
        print(f"  You scored {score} coins! 🪙")
        pause()
        return score


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    game = Game()
    game.run()

