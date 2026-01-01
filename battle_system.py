import pygame
import os
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

ANIMATION_DISTANCE = 10
ANIMATION_SPEED = 2
MENU_HEIGHT = 210
MENU_PADDING = 10
MENU_ITEM_HEIGHT = 40
MENU_ITEM_WIDTH = 100
MENU_BORDER_WIDTH = 2

CRIT_MULTIPLIER = 1.5
CRIT_CHANCE_FACTOR = 1000
DODGE_CHANCE_FACTOR = 1000
DAMAGE_RANDOM_MIN = 0.8
DAMAGE_RANDOM_MAX = 1.2

ESCAPE_BASE_CHANCE = 0.5
ESCAPE_AGILITY_FACTOR = 200
ESCAPE_ENEMY_PENALTY = 0.1

font = None
log_font = None
attr_font = None

def init_fonts():
    global font, log_font, attr_font
    if font is None:
        font = pygame.font.Font('C:\\Windows\\Fonts\\msyh.ttc', 24)
        log_font = pygame.font.Font('C:\\Windows\\Fonts\\msyh.ttc', 20)
        attr_font = pygame.font.Font('C:\\Windows\\Fonts\\msyh.ttc', 16)

class SoundManager:
    def __init__(self):
        self.attack_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "机枪.mp3"))
        self.enemy_attack_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "猛扑.mp3"))
        self.battle_start_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "战斗.mp3"))
        self.battle_end_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "战斗结束.mp3"))
        self.battle_defeat_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "战斗失败.mp3"))
        self.attack_sound_playing = False
        self.enemy_attack_sound_playing = False
        self.battle_start_sound_played = False
        self.battle_end_sound_played = False
        self.battle_defeat_sound_played = False
        self.battle_over_sound_queued = False
        self.background_music_loaded = False

    def start_background_music(self):
        if not self.background_music_loaded:
            background_music_path = os.path.join("assets", "sounds", "决战诺亚.mp3")
            if os.path.exists(background_music_path):
                pygame.mixer.music.load(background_music_path)
                pygame.mixer.music.play(-1)
                self.background_music_loaded = True

    def stop_background_music(self):
        if self.background_music_loaded:
            pygame.mixer.music.stop()
            self.background_music_loaded = False

class Entity:
    def __init__(self, name, display_name, image, hp, attack, defense, agility):
        self.name = name
        self.display_name = display_name
        self.image = image
        self.rect = image.get_rect()
        self.original_x = 0
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.agility = agility
        self.attack_animation = False
        self.attack_offset = 0
        self.attack_direction = 1
        self.hit_animation = False
        self.hit_offset = 0
        self.hit_direction = -1

    def update_animation(self):
        if self.hit_animation:
            self.hit_offset += ANIMATION_SPEED * self.hit_direction
            if self.hit_offset >= ANIMATION_DISTANCE:
                self.hit_direction = -1
            elif self.hit_offset <= 0:
                self.hit_animation = False
                self.hit_offset = 0
                self.hit_direction = -1
            self.rect.centerx = self.original_x + self.hit_offset
        
        if self.attack_animation:
            self.attack_offset += ANIMATION_SPEED * self.attack_direction
            if self.attack_offset >= ANIMATION_DISTANCE:
                self.attack_direction = -1
            elif self.attack_offset <= 0:
                self.attack_animation = False
                self.attack_offset = 0
                self.attack_direction = 1
            if not self.hit_animation:
                self.rect.centerx = self.original_x + self.attack_offset

    def reset_animation(self):
        self.hit_animation = False
        self.hit_offset = 0
        self.hit_direction = -1
        self.attack_animation = False
        self.attack_offset = 0
        self.attack_direction = 1
        self.rect.centerx = self.original_x

    def is_alive(self):
        return self.hp > 0

class Player(Entity):
    def __init__(self, image, hp, attack, defense, agility):
        super().__init__("主角", "主角1", image, hp, attack, defense, agility)
        self.defending = False
        self.defense_bonus = 0
        self.max_hp = hp

    def get_total_defense(self):
        return self.defense + self.defense_bonus

    def start_defend(self):
        self.defending = True
        self.defense_bonus = self.defense

    def reset_defense(self):
        self.defending = False
        self.defense_bonus = 0

class BattleSystem:
    def __init__(self, player, enemies, sound_manager):
        self.player = player
        self.enemies = enemies
        self.sound_manager = sound_manager
        self.battle_log = []
        self.battle_over = False
        self.battle_winner = None
        self.battle_ended_waiting = False
        self.current_round_index = 0
        self.attack_queue = []
        self.current_attacker_index = 0
        self.round_complete = False
        self.waiting_for_player_input = True
        self.player_target = None
        # 战斗场景滑入效果相关
        self.slide_in_position = SCREEN_HEIGHT  # 初始位置在屏幕下方
        self.slide_in_complete = False  # 滑入是否完成

    def calculate_damage(self, attacker_attack, defender_defense, attacker_agility):
        base_damage = max(1, attacker_attack - defender_defense)
        random_factor = random.uniform(DAMAGE_RANDOM_MIN, DAMAGE_RANDOM_MAX)
        damage = int(base_damage * random_factor)
        
        crit_chance = attacker_agility / CRIT_CHANCE_FACTOR
        if random.random() < crit_chance:
            damage = int(damage * CRIT_MULTIPLIER)
            return damage, True
        
        return damage, False

    def check_dodge(self, defender_agility):
        dodge_chance = defender_agility / DODGE_CHANCE_FACTOR
        return random.random() < dodge_chance

    def initialize_attack_queue(self):
        self.attack_queue.clear()
        
        if not self.battle_over:
            self.battle_log.clear()
        
        self.attack_queue.append({
            "type": "player",
            "agility": self.player.agility
        })
        
        for enemy in self.enemies:
            if enemy.is_alive():
                self.attack_queue.append({
                    "type": "enemy",
                    "enemy": enemy,
                    "agility": enemy.agility
                })
        
        self.attack_queue.sort(key=lambda x: x["agility"], reverse=True)
        
        self.current_attacker_index = 0
        self.round_complete = False
        self.waiting_for_player_input = False

    def player_attack(self, enemy_index):
        if self.sound_manager.attack_sound_playing:
            return
        
        if enemy_index < 0 or enemy_index >= len(self.enemies):
            return
        
        enemy = self.enemies[enemy_index]
        
        if enemy.is_alive():
            self.sound_manager.attack_sound_playing = True
            self.sound_manager.attack_sound.play()
            self.player.attack_animation = True
            self.player.attack_offset = 0
            self.player.attack_direction = 1
            
            if self.check_dodge(enemy.agility):
                self.battle_log.append(f"{enemy.display_name}闪避了主角的攻击！")
            else:
                damage, is_crit = self.calculate_damage(self.player.attack, enemy.defense, self.player.agility)
                enemy.hp -= damage
                enemy.hit_animation = True
                enemy.hit_offset = 0
                enemy.hit_direction = 1
                if is_crit:
                    self.battle_log.append(f"主角暴击攻击了{enemy.display_name}！")
                    self.battle_log.append(f"造成{damage}点伤害！")
                else:
                    self.battle_log.append(f"主角攻击了{enemy.display_name}！")
                    self.battle_log.append(f"造成{damage}点伤害！")
                
                if enemy.hp <= 0:
                    enemy.hp = 0
                    self.battle_log.append(f"{enemy.display_name}被击败了！")
            
            self.current_attacker_index += 1
            self.check_battle_over()

    def player_defend(self):
        self.initialize_attack_queue()
        
        self.player.start_defend()
        self.battle_log.append("主角进入防御状态！")
        self.battle_log.append(f"防御力提升{self.player.defense}点！")
        self.current_attacker_index += 1

    def player_escape(self):
        base_chance = ESCAPE_BASE_CHANCE
        agility_bonus = self.player.agility / ESCAPE_AGILITY_FACTOR
        enemy_penalty = (len(self.enemies) - 1) * ESCAPE_ENEMY_PENALTY
        escape_chance = min(0.9, max(0.1, base_chance + agility_bonus - enemy_penalty))
        
        if random.random() < escape_chance:
            self.battle_over = True
            self.battle_winner = "主角"
            self.battle_log.append("主角成功逃跑！")
        else:
            self.initialize_attack_queue()
            self.battle_log.append("主角逃跑失败！")
            self.current_attacker_index += 1
        
        if self.battle_over:
            self.sound_manager.battle_over_sound_queued = True

    def enemy_attack(self, enemy):
        if self.sound_manager.enemy_attack_sound_playing:
            return
        
        if enemy.is_alive() and self.player.is_alive():
            self.sound_manager.enemy_attack_sound_playing = True
            self.sound_manager.enemy_attack_sound.play()
            enemy.attack_animation = True
            enemy.attack_offset = 0
            enemy.attack_direction = -1
            
            if self.check_dodge(self.player.agility):
                self.battle_log.append(f"主角闪避了{enemy.display_name}的攻击！")
            else:
                damage, is_crit = self.calculate_damage(enemy.attack, self.player.get_total_defense(), enemy.agility)
                self.player.hp -= damage
                self.player.hit_animation = True
                self.player.hit_offset = 0
                self.player.hit_direction = 1
                if is_crit:
                    self.battle_log.append(f"{enemy.display_name}暴击攻击！")
                    self.battle_log.append(f"对主角造成{damage}点伤害！")
                else:
                    self.battle_log.append(f"{enemy.display_name}攻击！")
                    self.battle_log.append(f"对主角造成{damage}点伤害！")
                
                if self.player.hp <= 0:
                    self.player.hp = 0
                    self.battle_log.append("主角被击败了！")
            
            self.check_battle_over()

    def execute_next_attack(self):
        if self.sound_manager.attack_sound_playing or self.sound_manager.enemy_attack_sound_playing:
            return
        
        if self.player.attack_animation or self.player.hit_animation:
            return
        
        for enemy in self.enemies:
            if enemy.is_alive() and (enemy.attack_animation or enemy.hit_animation):
                return
        
        if self.current_attacker_index >= len(self.attack_queue):
            self.round_complete = True
            return
        
        attacker = self.attack_queue[self.current_attacker_index]
        
        if attacker["type"] == "player":
            self.player_attack(self.player_target)
            self.current_attacker_index += 1
        else:
            enemy = attacker["enemy"]
            self.enemy_attack(enemy)
            self.current_attacker_index += 1

    def check_battle_over(self):
        if self.player.hp <= 0:
            self.battle_over = True
            self.battle_winner = "怪物"
            self.battle_log.append("战斗结束，怪物胜利！")
        else:
            all_enemies_dead = True
            for enemy in self.enemies:
                if enemy.is_alive():
                    all_enemies_dead = False
                    break
            
            if all_enemies_dead:
                self.battle_over = True
                self.battle_winner = "主角"
                self.battle_log.append("战斗结束，主角胜利！")
        
        if self.battle_over:
            self.battle_ended_waiting = True
            self.sound_manager.battle_over_sound_queued = True

    def update(self):
        if not self.battle_over:
            self.sound_manager.start_background_music()
        
        if not self.battle_over:
            if self.sound_manager.attack_sound_playing and not pygame.mixer.get_busy():
                self.sound_manager.attack_sound_playing = False
                if not self.battle_over:
                    if not self.waiting_for_player_input:
                        self.execute_next_attack()
            
            if self.sound_manager.enemy_attack_sound_playing and not pygame.mixer.get_busy():
                self.sound_manager.enemy_attack_sound_playing = False
                if not self.battle_over:
                    self.execute_next_attack()
            
            if self.round_complete and not self.battle_over:
                self.current_round_index += 1
                self.waiting_for_player_input = True
                self.player.reset_defense()
            
            if not self.waiting_for_player_input and not self.sound_manager.attack_sound_playing and not self.sound_manager.enemy_attack_sound_playing:
                self.execute_next_attack()
        
        if self.battle_over:
            if self.sound_manager.attack_sound_playing and not pygame.mixer.get_busy():
                self.sound_manager.attack_sound_playing = False
            
            if self.sound_manager.enemy_attack_sound_playing and not pygame.mixer.get_busy():
                self.sound_manager.enemy_attack_sound_playing = False
            
            if self.sound_manager.battle_over_sound_queued and not self.sound_manager.attack_sound_playing and not self.sound_manager.enemy_attack_sound_playing and not pygame.mixer.get_busy():
                self.sound_manager.stop_background_music()
                if self.battle_winner == "主角" and not self.sound_manager.battle_end_sound_played:
                    self.sound_manager.battle_end_sound.play()
                    self.sound_manager.battle_end_sound_played = True
                    self.sound_manager.battle_over_sound_queued = False
                elif self.battle_winner == "怪物" and not self.sound_manager.battle_defeat_sound_played:
                    self.sound_manager.battle_defeat_sound.play()
                    self.sound_manager.battle_defeat_sound_played = True
                    self.sound_manager.battle_over_sound_queued = False

class MenuSystem:
    def __init__(self, main_menu_items, sub_menus):
        self.main_menu_items = main_menu_items
        self.sub_menus = sub_menus
        self.open = False
        self.stack = []
        self.selected_main_index = 0
        self.selected_sub_index = 0
        self.changed = False

    def open_menu(self):
        self.open = True
        self.stack = []
        self.selected_main_index = 0
        self.selected_sub_index = 0
        self.changed = True

    def close_menu(self):
        self.open = False
        self.changed = True

    def go_back(self):
        if self.stack:
            self.stack.pop()
            self.selected_sub_index = 0
            self.changed = True
        else:
            self.close_menu()

    def navigate_up(self):
        if not self.stack:
            self.selected_main_index = (self.selected_main_index - 2) % len(self.main_menu_items)
        else:
            current_menu = self.stack[-1]
            max_index = len(self.sub_menus[current_menu]) - 1
            self.selected_sub_index = (self.selected_sub_index - 1) % (max_index + 1)
        self.changed = True

    def navigate_down(self):
        if not self.stack:
            self.selected_main_index = (self.selected_main_index + 2) % len(self.main_menu_items)
        else:
            current_menu = self.stack[-1]
            max_index = len(self.sub_menus[current_menu]) - 1
            self.selected_sub_index = (self.selected_sub_index + 1) % (max_index + 1)
        self.changed = True

    def navigate_left(self):
        if not self.stack:
            if self.selected_main_index % 2 == 1:
                self.selected_main_index -= 1
            self.changed = True

    def navigate_right(self):
        if not self.stack:
            if self.selected_main_index % 2 == 0 and self.selected_main_index < len(self.main_menu_items) - 1:
                self.selected_main_index += 1
            self.changed = True

    def select_item(self, battle_system):
        if not self.stack:
            selected_item = self.main_menu_items[self.selected_main_index]
            if selected_item in self.sub_menus and self.sub_menus[selected_item]:
                if selected_item == "攻击":
                    alive_enemies = [i for i, enemy in enumerate(battle_system.enemies) if enemy.is_alive()]
                    if not alive_enemies:
                        return
                    self.sub_menus["攻击"] = [battle_system.enemies[i].display_name for i in alive_enemies]
                self.stack.append(selected_item)
                self.selected_sub_index = 0
                self.changed = True
        else:
            current_menu = self.stack[-1]
            current_items = self.sub_menus[current_menu]
            if not current_items:
                self.go_back()
                return
            selected_item = current_items[self.selected_sub_index]
            
            if current_menu == "攻击" and not battle_system.battle_over:
                alive_enemies = [i for i, enemy in enumerate(battle_system.enemies) if enemy.is_alive()]
                enemy_index = alive_enemies[self.selected_sub_index]
                battle_system.player_target = enemy_index
                battle_system.initialize_attack_queue()
                battle_system.current_attacker_index = 0
                battle_system.execute_next_attack()
                self.stack.pop()
                self.selected_sub_index = 0
                self.changed = True
            elif current_menu == "辅助" and not battle_system.battle_over:
                if selected_item == "防御":
                    battle_system.player_defend()
                elif selected_item == "逃跑":
                    battle_system.player_escape()
                self.stack.pop()
                self.selected_sub_index = 0
                self.changed = True

    def draw(self, screen, battle_system):
        main_menu_cols = 2
        main_menu_rows = 4
        main_menu_width = main_menu_cols * MENU_ITEM_WIDTH + MENU_PADDING * (main_menu_cols + 1)
        main_menu_height = main_menu_rows * MENU_ITEM_HEIGHT + MENU_PADDING * (main_menu_rows + 1)
        
        if self.stack:
            current_menu = self.stack[-1]
            sub_items = self.sub_menus.get(current_menu, [])
            sub_menu_width = SCREEN_WIDTH - main_menu_width - MENU_PADDING * 2
            sub_menu_height = main_menu_height
        else:
            sub_items = []
            sub_menu_width = SCREEN_WIDTH - main_menu_width - MENU_PADDING * 2
            sub_menu_height = main_menu_height
        
        main_menu_x = MENU_PADDING
        main_menu_y = SCREEN_HEIGHT - main_menu_height - MENU_PADDING
        
        sub_menu_x = main_menu_x + main_menu_width + MENU_PADDING
        sub_menu_y = SCREEN_HEIGHT - max(main_menu_height, sub_menu_height) - MENU_PADDING
        
        main_menu_surface = pygame.Surface((main_menu_width, main_menu_height), pygame.SRCALPHA)
        main_menu_surface.fill((0, 0, 0, 180))
        pygame.draw.rect(main_menu_surface, WHITE, (0, 0, main_menu_width, main_menu_height), MENU_BORDER_WIDTH)
        
        start_row = 1
        for i, item in enumerate(self.main_menu_items):
            col = i % main_menu_cols
            row = start_row + i // main_menu_cols
            x = MENU_PADDING + col * (MENU_ITEM_WIDTH + MENU_PADDING)
            y = MENU_PADDING + row * (MENU_ITEM_HEIGHT + MENU_PADDING)
            
            if not self.stack and i == self.selected_main_index:
                pygame.draw.rect(main_menu_surface, (100, 100, 200), (x, y, MENU_ITEM_WIDTH, MENU_ITEM_HEIGHT))
            else:
                pygame.draw.rect(main_menu_surface, (50, 50, 50), (x, y, MENU_ITEM_WIDTH, MENU_ITEM_HEIGHT))
            
            text_surface = font.render(item, True, WHITE)
            text_rect = text_surface.get_rect(center=(x + MENU_ITEM_WIDTH // 2, y + MENU_ITEM_HEIGHT // 2))
            main_menu_surface.blit(text_surface, text_rect)
        
        screen.blit(main_menu_surface, (main_menu_x, main_menu_y))
        
        if self.stack:
            sub_menu_surface = pygame.Surface((sub_menu_width, sub_menu_height), pygame.SRCALPHA)
            sub_menu_surface.fill((0, 0, 0, 180))
            pygame.draw.rect(sub_menu_surface, WHITE, (0, 0, sub_menu_width, sub_menu_height), MENU_BORDER_WIDTH)
            
            for i, item in enumerate(sub_items):
                y = MENU_PADDING + i * (MENU_ITEM_HEIGHT + MENU_PADDING)
                
                if i == self.selected_sub_index:
                    pygame.draw.rect(sub_menu_surface, (100, 100, 200), (MENU_PADDING, y, MENU_ITEM_WIDTH, MENU_ITEM_HEIGHT))
                else:
                    pygame.draw.rect(sub_menu_surface, (50, 50, 50), (MENU_PADDING, y, MENU_ITEM_WIDTH, MENU_ITEM_HEIGHT))
                
                text_surface = font.render(item, True, WHITE)
                text_rect = text_surface.get_rect(center=(MENU_PADDING + MENU_ITEM_WIDTH // 2, y + MENU_ITEM_HEIGHT // 2))
                sub_menu_surface.blit(text_surface, text_rect)
            
            screen.blit(sub_menu_surface, (sub_menu_x, sub_menu_y))
        else:
            self.draw_info_box(screen, sub_menu_x, sub_menu_y, sub_menu_width, sub_menu_height, battle_system)

    def draw_info_box(self, screen, x, y, width, height, battle_system):
        info_box_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        info_box_surface.fill((0, 0, 0, 180))
        pygame.draw.rect(info_box_surface, WHITE, (0, 0, width, height), MENU_BORDER_WIDTH)
        
        left_width = width * 2 // 3
        right_width = width - left_width - MENU_PADDING
        
        left_x = MENU_PADDING
        right_x = left_width + MENU_PADDING
        
        y_offset = MENU_PADDING
        
        for log in battle_system.battle_log[-8:]:
            log_surface = log_font.render(log, True, (0, 255, 0))
            info_box_surface.blit(log_surface, (left_x, y_offset))
            y_offset += 25
        
        y_offset = MENU_PADDING
        
        player_text = f"主角1 HP:{battle_system.player.hp}/{battle_system.player.max_hp}"
        player_surface = attr_font.render(player_text, True, (0, 255, 0))
        info_box_surface.blit(player_surface, (right_x, y_offset))
        y_offset += 20
        
        player_attr_text = f"  攻:{battle_system.player.attack} 防:{battle_system.player.defense} 敏:{battle_system.player.agility}"
        player_attr_surface = attr_font.render(player_attr_text, True, (200, 200, 200))
        info_box_surface.blit(player_attr_surface, (right_x, y_offset))
        
        screen.blit(info_box_surface, (x, y))

enemy_attributes = {
    "巨蚁": {"attack": 15, "defense": 15, "hp": 5, "agility": 5},
    "金蚁": {"attack": 15, "defense": 100, "hp": 8, "agility": 100},
    "金蚁毯": {"attack": 15, "defense": 800, "hp": 15, "agility": 100},
    "杀人虫": {"attack": 18, "defense": 15, "hp": 12, "agility": 8},
    "变形虫": {"attack": 18, "defense": 20, "hp": 150, "agility": 70},
    "超导虫": {"attack": 19, "defense": 27, "hp": 16, "agility": 53},
    "机械虫": {"attack": 19, "defense": 25, "hp": 14, "agility": 50},
    "军蚁": {"attack": 20, "defense": 200, "hp": 200, "agility": 150},
    "食人蚁": {"attack": 20, "defense": 200, "hp": 6, "agility": 150},
    "炸弹龟": {"attack": 21, "defense": 72, "hp": 36, "agility": 14},
    "毒蝙蝠": {"attack": 22, "defense": 18, "hp": 20, "agility": 25},
    "侦察蝶": {"attack": 220, "defense": 400, "hp": 25, "agility": 150},
    "催眠器": {"attack": 24, "defense": 27, "hp": 32, "agility": 64},
    "彷生蜗牛": {"attack": 17, "defense": 40, "hp": 7, "agility": 12},
    "食人花": {"attack": 31, "defense": 22, "hp": 48, "agility": 27},
    "飞狗": {"attack": 38, "defense": 30, "hp": 35, "agility": 34},
    "加农炮": {"attack": 35, "defense": 30, "hp": 28, "agility": 33},
    "龟式战车": {"attack": 35, "defense": 55, "hp": 68, "agility": 35},
    "古炮": {"attack": 32, "defense": 28, "hp": 18, "agility": 16},
    "监视器": {"attack": 28, "defense": 22, "hp": 12, "agility": 48},
    "光防御器": {"attack": 45, "defense": 44, "hp": 40, "agility": 39},
    "瓦鲁部下": {"attack": 45, "defense": 44, "hp": 40, "agility": 39},
    "防御机器": {"attack": 55, "defense": 30, "hp": 15, "agility": 50},
    "水鬼": {"attack": 90, "defense": 60, "hp": 110, "agility": 30},
    "生物炮": {"attack": 88, "defense": 24, "hp": 50, "agility": 25},
    "巨蟹": {"attack": 108, "defense": 84, "hp": 60, "agility": 65},
    "攻击机": {"attack": 100, "defense": 60, "hp": 30, "agility": 1},
    "电磁花": {"attack": 124, "defense": 620, "hp": 508, "agility": 100},
    "侦察蜂": {"attack": 120, "defense": 380, "hp": 22, "agility": 145},
    "高速车": {"attack": 195, "defense": 60, "hp": 35, "agility": 42},
    "声波蛇": {"attack": 235, "defense": 107, "hp": 148, "agility": 55},
    "雷达花": {"attack": 255, "defense": 620, "hp": 1020, "agility": 100},
    "火焰炮": {"attack": 240, "defense": 120, "hp": 65, "agility": 46},
    "拦截碟": {"attack": 304, "defense": 90, "hp": 40, "agility": 45},
    "离子坦克": {"attack": 280, "defense": 150, "hp": 220, "agility": 20},
    "巨型河马": {"attack": 312, "defense": 264, "hp": 300, "agility": 20},
    "导弹车": {"attack": 320, "defense": 276, "hp": 80, "agility": 53},
    "章鱼坦克": {"attack": 300, "defense": 180, "hp": 180, "agility": 25},
    "激光蚯": {"attack": 280, "defense": 27, "hp": 20, "agility": 113},
    "异形鱼": {"attack": 440, "defense": 360, "hp": 230, "agility": 193},
    "喷火谔": {"attack": 440, "defense": 360, "hp": 230, "agility": 193},
    "沙漠虎": {"attack": 480, "defense": 55, "hp": 100, "agility": 70},
    "反坦克兵": {"attack": 170, "defense": 83, "hp": 50, "agility": 50},
    "步枪鸟": {"attack": 38, "defense": 30, "hp": 35, "agility": 34},
    "异形": {"attack": 74, "defense": 27, "hp": 83, "agility": 17}
}

def load_enemy_types():
    enemy_types = []
    enemy_names = list(enemy_attributes.keys())
    for name in enemy_names:
        image_path = os.path.join("assets", "images", "enemy", f"{name}.png")
        if os.path.exists(image_path):
            max_count = 3
            if name in ["军蚁", "加农炮", "食人蚁", "防御机器", "水鬼", "巨蟹", "攻击机", "侦察蜂", "高速车", "雷达花", "火焰炮", "拦截碟", "离子坦克", "巨型河马", "章鱼坦克", "异形鱼", "步枪鸟", "异形"]:
                max_count = 1
            elif name in ["古炮", "监视器", "光防御器", "瓦鲁部下", "生物炮", "电磁花", "声波蛇", "导弹车", "激光蚯", "喷火谔", "沙漠虎", "反坦克兵"]:
                max_count = 2
            is_active = name in ["巨蚁", "杀人虫" , "加农炮"]
            enemy_types.append({
                "name": name,
                "image": pygame.image.load(image_path),
                "max_count": max_count,
                "active": is_active
            })
    return enemy_types

def generate_enemies(enemy_types, player_atk):
    enemies = []
    enemy_groups = {}
    num_enemy_types = 1
    
    max_allowed_attack = int(player_atk * 1.2)
    eligible_enemy_types = [i for i, enemy_type in enumerate(enemy_types) 
                            if enemy_type["active"]
                            and enemy_type["name"] in enemy_attributes 
                            and enemy_attributes[enemy_type["name"]]["attack"] <= max_allowed_attack]
    
    if len(eligible_enemy_types) > 0:
        selected_indices = random.sample(eligible_enemy_types, min(num_enemy_types, len(eligible_enemy_types)))
    else:
        selected_indices = []
    
    for idx in selected_indices:
        enemy_type = enemy_types[idx]
        count = random.randint(1, enemy_type["max_count"])
        enemy_groups[enemy_type["name"]] = {
            "name": enemy_type["name"],
            "count": count,
            "image": enemy_type["image"],
            "rects": []
        }
        
        for i in range(count):
            image = enemy_type["image"]
            rect = image.get_rect()
            enemy_groups[enemy_type["name"]]["rects"].append(rect)
    
    all_enemies = []
    for group_name, group_data in enemy_groups.items():
        for i, rect in enumerate(group_data["rects"]):
            enemy = Entity(
                group_name,
                f"{group_name}{i+1}",
                group_data["image"],
                0, 0, 0, 0
            )
            enemy.rect = rect
            
            if group_name in enemy_attributes:
                attrs = enemy_attributes[group_name]
                enemy.hp = attrs["hp"]
                enemy.max_hp = attrs["hp"]
                enemy.attack = attrs["attack"]
                enemy.defense = attrs["defense"]
                enemy.agility = attrs["agility"]
            else:
                enemy.hp = 50
                enemy.max_hp = 50
                enemy.attack = 15
                enemy.defense = 10
                enemy.agility = 30
            
            all_enemies.append(enemy)
    
    return all_enemies

def position_enemies(enemies, available_width, available_height):
    if len(enemies) == 1:
        center_x = available_width // 2
        center_y = available_height // 2
        enemies[0].rect.centerx = center_x
        enemies[0].rect.centery = center_y
        enemies[0].original_x = center_x
    else:
        enemy_sizes = []
        for enemy in enemies:
            width = enemy.rect.width
            height = enemy.rect.height
            enemy_sizes.append((width, height))
        
        total_width = sum(size[0] for size in enemy_sizes)
        total_height = max(size[1] for size in enemy_sizes)
        
        if total_width > available_width - MENU_PADDING * 2:
            cols = min(len(enemies), max(1, (available_width - MENU_PADDING * 2) // max(size[0] for size in enemy_sizes)))
        else:
            cols = len(enemies)
        
        rows = (len(enemies) + cols - 1) // cols
        
        cell_width = (available_width - MENU_PADDING * 2) // cols
        cell_height = (available_height - MENU_PADDING * 2) // rows
        
        positions = []
        for row in range(rows - 1, -1, -1):
            for col in range(cols):
                x = MENU_PADDING + col * cell_width + cell_width // 2
                y = MENU_PADDING + row * cell_height + cell_height // 2
                positions.append((x, y))
        
        for i, enemy in enumerate(enemies):
            if i < len(positions):
                enemy.rect.centerx = positions[i][0]
                enemy.rect.centery = positions[i][1]
                enemy.original_x = positions[i][0]

def start_battle(player_hp, player_atk, player_defense, player_agility):
    init_fonts()
    enemy_types = load_enemy_types()
    enemies = generate_enemies(enemy_types, player_atk)
    
    available_height = SCREEN_HEIGHT - MENU_HEIGHT
    available_width = SCREEN_WIDTH // 2
    position_enemies(enemies, available_width, available_height)
    
    player_image = pygame.image.load(os.path.join("assets", "images", "battle_characters", "主角1.png"))
    player_image = pygame.transform.scale(player_image, (int(player_image.get_width() * 0.6), int(player_image.get_height() * 0.6)))
    player = Player(player_image, player_hp, player_atk, player_defense, player_agility)
    
    player_area_x = available_width
    player_area_width = SCREEN_WIDTH - available_width
    player.rect.centerx = player_area_x + player_area_width // 2
    player.rect.centery = available_height // 2
    player.original_x = player.rect.centerx
    
    sound_manager = SoundManager()
    battle_system = BattleSystem(player, enemies, sound_manager)
    
    main_menu_items = ["攻击", "装备", "工具", "辅助"]
    sub_menus = {
        "攻击": [enemy.display_name for enemy in enemies],
        "装备": [],
        "工具": [],
        "辅助": ["防御", "逃跑"]
    }
    menu_system = MenuSystem(main_menu_items, sub_menus)
    
    return battle_system, menu_system, player, enemies

def update_battle(battle_system, menu_system, screen):
    battle_system.update()
    
    player = battle_system.player
    enemies = battle_system.enemies
    
    # 创建临时表面用于绘制战斗场景
    battle_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    battle_surface.fill(BLACK)
    
    player.update_animation()
    
    for enemy in enemies:
        if enemy.is_alive():
            enemy.update_animation()
            battle_surface.blit(enemy.image, enemy.rect)
        elif enemy.hit_animation:
            enemy.update_animation()
            battle_surface.blit(enemy.image, enemy.rect)
        else:
            enemy.reset_animation()
    
    battle_surface.blit(player.image, player.rect)
    
    # 根据战斗状态控制菜单显示
    if battle_system.waiting_for_player_input and not battle_system.battle_over:
        menu_system.open = True
    else:
        menu_system.open = False
    
    menu_system.draw(battle_surface, battle_system)
    
    # 实现战斗场景滑入效果
    if not battle_system.slide_in_complete:
        # 每帧向上移动6像素，600像素高度需要约100帧（1.67秒）完成滑入
        battle_system.slide_in_position -= 6
        # 确保不超过屏幕顶部
        if battle_system.slide_in_position <= 0:
            battle_system.slide_in_position = 0
            battle_system.slide_in_complete = True
    
    # 绘制滑入的战斗场景
    screen.blit(battle_surface, (0, battle_system.slide_in_position))
    

    
    # 战斗场景淡出效果（从全亮到全黑）
    if not hasattr(battle_system, 'fade_out_active'):
        battle_system.fade_out_active = False
    
    if battle_system.fade_out_active:
        if not hasattr(battle_system, 'fade_out_opacity'):
            battle_system.fade_out_opacity = 0
        
        battle_system.fade_out_opacity += 6  # 增加步长，加快淡出速度至约0.71秒
        if battle_system.fade_out_opacity >= 255:
            battle_system.fade_out_opacity = 255
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(battle_system.fade_out_opacity)
        screen.blit(overlay, (0, 0))
    
    # 战斗结束状态：等待玩家确认
    battle_complete = False
    
    # 只有当战斗场景淡出完成时，才返回战斗结束
    if battle_system.fade_out_active and battle_system.fade_out_opacity >= 255:
        battle_complete = True
    
    return battle_complete

def handle_battle_input(event, battle_system, menu_system):
    if event.type == pygame.KEYDOWN:
        if battle_system.battle_ended_waiting:
            if event.key == pygame.K_j:
                # 启动战斗场景淡出效果
                if not hasattr(battle_system, 'fade_out_opacity'):
                    battle_system.fade_out_opacity = 0
                battle_system.fade_out_active = True
                battle_system.battle_ended_waiting = False
        else:
            if event.key == pygame.K_j:
                if not menu_system.open:
                    menu_system.open_menu()
                else:
                    menu_system.select_item(battle_system)
            elif event.key == pygame.K_k:
                menu_system.go_back()
            elif event.key == pygame.K_w:
                menu_system.navigate_up()
            elif event.key == pygame.K_s:
                menu_system.navigate_down()
            elif event.key == pygame.K_a:
                menu_system.navigate_left()
            elif event.key == pygame.K_d:
                menu_system.navigate_right()
