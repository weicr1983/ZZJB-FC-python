import pygame
import sys
import os
import random
import battle_system

# 初始化Pygame
pygame.init()

# 设置游戏窗口
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("重装机兵")

# 定义颜色
BLACK = (0, 0, 0)

# 瓦片格子
TILE_SIZE = 32  # 每个地图格子的尺寸

# 当前地图的实际尺寸
current_map_width = 0
current_map_height = 0
# 当前使用的地图名称
current_map_name = "世界地图"
# 地图数据
map_data = []
# 当前地图的切换点配置
current_switch_points = []
# 当前地图的默认瓦片类型
current_default_tile = 1
# 当前地图是否允许遇敌
current_map_enable_encounter = True

# 地图边缘扩展配置
EXTEND_SIZE = 15  # 扩展10个格子

# 地图类型常量
TILE_BIG_TREE = 2  # 大树格子（不可通行）
TILE_SMALL_TREE = 3  # 小树格子（可通行）
TILE_HILL1 = 7  # 山头1格子（不可通行）
TILE_HILL2 = 8  # 山头2格子（不可通行）

# 瓦片配置 - 支持从不同图片提取瓦片
# 格式: {瓦片类型: {"sheet": "图片名称", "row": 行索引(从1开始), "col": 列索引(从1开始)}}
tile_config = {
    1: {"sheet": "map", "row": 5, "col": 4},      # map2.png 中(2,5)：平地格子
    TILE_BIG_TREE: {"sheet": "map", "row": 6, "col": 3},   # map2.png 中(1,1)：大树格子
    TILE_SMALL_TREE: {"sheet": "map", "row": 5, "col": 3}, # map2.png 中(1,2)：小树格子
    4: {"sheet": "map", "row": 5, "col": 2},       # map2.png 中(5,7)：山洞格子
    5: {"sheet": "map", "row": 9, "col": 8},       # map2.png 中(3,1)：沙地格子
    6: {"sheet": "map", "row": 9, "col": 7},   # map2.png 中(3,2)：旱地格子
    TILE_HILL1: {"sheet": "map", "row": 4, "col": 5},      # map.png 中(4,5)：山头1格子
    TILE_HILL2: {"sheet": "map", "row": 4, "col": 8},      # map.png 中(4,8)：山头2格子
    9: {"sheet": "map", "row": 4, "col": 3},      # map.png 中(3,4)：草地格子
    10: {"sheet": "map2", "row": 1, "col": 3},   # 新增瓦片12
    11: {"sheet": "map2", "row": 1, "col": 4},   # 新增瓦片12
    12: {"sheet": "map2", "row": 1, "col": 7},   # 新增瓦片12
    13: {"sheet": "map2", "row": 2, "col": 3},   # 新增瓦片12
    14: {"sheet": "map2", "row": 2, "col": 4},   # 新增瓦片12
    15: {"sheet": "map2", "row": 3, "col": 4},   # 新增瓦片15
    16: {"sheet": "map2", "row": 3, "col": 5},   # 新增瓦片16
    17: {"sheet": "map2", "row": 3, "col": 6},   # 新增瓦片17
    18: {"sheet": "map2", "row": 3, "col": 7},   # 新增瓦片18
    19: {"sheet": "map2", "row": 8, "col": 6},   # 新增瓦片18
    20: {"sheet": "map2", "row": 8, "col": 7},   # 新增瓦片18
  
    21: {"sheet": "map2", "row": 4, "col": 6},   # 新增瓦片21
    22: {"sheet": "map2", "row": 4, "col": 7},   # 新增瓦片22
    23: {"sheet": "map2", "row": 4, "col": 5},   # 新增瓦片23
    24: {"sheet": "map2", "row": 8, "col": 8},   # 新增瓦片24
    
    25: {"sheet": "map2", "row": 4, "col": 4},   # 新增瓦片25
    26: {"sheet": "map2", "row": 5, "col": 1},   # 新增瓦片26
    27: {"sheet": "map2", "row": 5, "col": 2},   # 新增瓦片27
    28: {"sheet": "map2", "row": 5, "col": 3},   # 新增瓦片28
    29: {"sheet": "map2", "row": 5, "col": 6},   # 新增瓦片29
    30: {"sheet": "map2", "row": 4, "col": 8},   # 新增瓦片30
    31: {"sheet": "map2", "row": 5, "col": 8},   # 新增瓦片31
    32: {"sheet": "map2", "row": 8, "col": 5},   # 新增瓦片32
    33: {"sheet": "map2", "row": 6, "col": 4},   # 新增瓦片33
    34: {"sheet": "map2", "row": 6, "col": 5},   # 新增瓦片34
    35: {"sheet": "map2", "row": 6, "col": 6},   # 新增瓦片35
    36: {"sheet": "map2", "row": 7, "col": 5},   # 新增瓦片36

    37: {"sheet": "map", "row": 1, "col": 1},   # 水左上
    38: {"sheet": "map", "row": 1, "col": 2},   # 水上
    39: {"sheet": "map", "row": 1, "col": 3},   # 水右上
    40: {"sheet": "map2", "row": 7, "col": 4},   # 新增瓦片40
    41: {"sheet": "map", "row": 2, "col": 1},   # 水左
    42: {"sheet": "map", "row": 2, "col": 2},   # 水中
    43: {"sheet": "map", "row": 2, "col": 3},   # 水右
    44: {"sheet": "map2", "row": 7, "col": 6},   # 新增瓦片44
    45: {"sheet": "map", "row": 3, "col": 1},   # 水左下
    46: {"sheet": "map", "row": 3, "col": 2},   # 水下
    47: {"sheet": "map", "row": 3, "col": 3},   # 水右下
    48: {"sheet": "map2", "row": 2, "col": 7},   # 水

    49: {"sheet": "map",  "row": 4, "col": 2},   # 新增瓦片49
    50: {"sheet": "map2", "row": 3, "col": 1},   # 新增瓦片50
    51: {"sheet": "map2", "row": 3, "col": 2},   # 新增瓦片51
    52: {"sheet": "map2", "row": 3, "col": 3},   # 新增瓦片52
    
    53: {"sheet": "map2", "row": 9, "col": 4},   # 新增瓦片53
    54: {"sheet": "map2", "row": 4, "col": 1},   # 新增瓦片54
    55: {"sheet": "map2", "row": 4, "col": 2},   # 新增瓦片55
    56: {"sheet": "map2", "row": 4, "col": 3},   # 新增瓦片56

    57: {"sheet": "map2", "row": 9, "col": 5}, 
    58: {"sheet": "map2", "row": 9, "col": 6},   
    59: {"sheet": "map2", "row": 9, "col": 7},   
    60: {"sheet": "map2", "row": 9, "col": 8},   

    61: {"sheet": "map", "row": 1, "col": 5},   
    62: {"sheet": "map", "row": 1, "col": 6},   
    63: {"sheet": "map", "row": 2, "col": 4},   
    64: {"sheet": "map", "row": 2, "col": 5},   

    65: {"sheet": "map", "row": 3, "col": 4},   
    66: {"sheet": "map", "row": 3, "col": 5},   
    67: {"sheet": "map", "row": 3, "col": 6},   
    68: {"sheet": "map", "row": 3, "col": 7},

    69: {"sheet": "map", "row": 7, "col": 4},   
    70: {"sheet": "map", "row": 7, "col": 5},   
    71: {"sheet": "map", "row": 4, "col": 6},   
    72: {"sheet": "map", "row": 4, "col": 7},

    100: {"sheet": "town", "row": 2, "col": 5},
    101: {"sheet": "town", "row": 2, "col": 6},  
    102: {"sheet": "town", "row": 2, "col": 7},   
    103: {"sheet": "town", "row": 2, "col": 8},

    104: {"sheet": "town", "row": 1, "col": 4},
    105: {"sheet": "town", "row": 1, "col": 5},
    106: {"sheet": "town", "row": 1, "col": 6},
    107: {"sheet": "town", "row": 1, "col": 7},

    108: {"sheet": "town", "row": 1, "col": 2},
    109: {"sheet": "town", "row": 1, "col": 3},
    110: {"sheet": "town", "row": 2, "col": 2},
    111: {"sheet": "town", "row": 1, "col": 8},

    112: {"sheet": "town", "row": 4, "col": 3}, #城镇1修理店
    113: {"sheet": "town", "row": 4, "col": 4},
    114: {"sheet": "town", "row": 4, "col": 5},
    115: {"sheet": "town", "row": 5, "col": 6},

    116: {"sheet": "town", "row": 5, "col": 3},
    117: {"sheet": "town", "row": 5, "col": 4},
    118: {"sheet": "town", "row": 5, "col": 5},
    119: {"sheet": "town", "row": 5, "col": 1},

    120: {"sheet": "town", "row": 6, "col": 3},
    121: {"sheet": "town", "row": 6, "col": 4},
    122: {"sheet": "town", "row": 6, "col": 5},
    123: {"sheet": "town", "row": 4, "col": 6},
    
    124: {"sheet": "town", "row": 4, "col": 1},
    125: {"sheet": "town", "row": 4, "col": 2},
    126: {"sheet": "town", "row": 6, "col": 1},
    127: {"sheet": "town", "row": 6, "col": 2},

    150: {"sheet": "town", "row": 23, "col": 1}, #建筑内
    151: {"sheet": "town", "row": 23, "col": 4},
    152: {"sheet": "town", "row": 23, "col": 5},
    153: {"sheet": "town", "row": 20, "col": 6},

    154: {"sheet": "town", "row": 24, "col": 1},
    155: {"sheet": "town", "row": 24, "col": 4},
    156: {"sheet": "town", "row": 24, "col": 5},
    157: {"sheet": "town", "row": 21, "col": 6},

    158: {"sheet": "town", "row": 7, "col": 1}, 
    159: {"sheet": "town", "row": 7, "col": 2},
    160: {"sheet": "town", "row": 7, "col": 3},
    161: {"sheet": "town", "row":12, "col": 3},

    162: {"sheet": "town", "row": 8, "col": 1},
    163: {"sheet": "town", "row": 8, "col": 2},
    164: {"sheet": "town", "row": 8, "col": 3},
    165: {"sheet": "town", "row":10, "col": 2},

    166: {"sheet": "town", "row": 9, "col": 1},
    167: {"sheet": "town", "row": 9, "col": 2},
    168: {"sheet": "town", "row": 9, "col": 3},
    169: {"sheet": "town", "row": 10, "col": 3},

    170: {"sheet": "town", "row": 7, "col": 4},
    171: {"sheet": "town", "row": 7, "col": 5},
    172: {"sheet": "town", "row": 7, "col": 6},
    173: {"sheet": "town", "row": 8, "col": 8},

    174: {"sheet": "town", "row": 8, "col": 4},
    175: {"sheet": "town", "row": 8, "col": 5},
    176: {"sheet": "town", "row": 8, "col": 6},
    177: {"sheet": "town", "row": 16, "col": 2},

    178: {"sheet": "town", "row": 9, "col": 4},
    179: {"sheet": "town", "row": 9, "col": 5},
    180: {"sheet": "town", "row": 9, "col": 6},
    181: {"sheet": "town", "row": 16, "col": 3},

    182: {"sheet": "town", "row": 16, "col": 7},
    183: {"sheet": "town", "row": 16, "col": 8},
    184: {"sheet": "town", "row": 18, "col": 7},
    185: {"sheet": "town", "row": 3, "col": 8},

    186: {"sheet": "town", "row": 14, "col": 2},
    187: {"sheet": "town", "row": 14, "col": 7},
    188: {"sheet": "town", "row": 16, "col": 1},
    189: {"sheet": "town", "row": 18, "col": 3},

    190: {"sheet": "town", "row": 15, "col": 2},
    191: {"sheet": "town", "row": 15, "col": 7},
    192: {"sheet": "town", "row": 18, "col": 2},
    193: {"sheet": "town", "row": 18, "col": 6},

    194: {"sheet": "town", "row": 18, "col": 1},
    195: {"sheet": "town", "row": 18, "col": 4},
    196: {"sheet": "town", "row": 18, "col": 5},
    197: {"sheet": "town", "row": 17, "col": 3},

    198: {"sheet": "town", "row": 14, "col": 1},
    199: {"sheet": "town", "row": 14, "col": 3},
    200: {"sheet": "town", "row": 4, "col": 7},
    201: {"sheet": "town", "row": 4, "col": 8},

    202: {"sheet": "town", "row": 14, "col": 2},
    203: {"sheet": "town", "row": 15, "col": 3},
    204: {"sheet": "town", "row": 5, "col": 7},
    205: {"sheet": "town", "row": 5, "col": 8},

    206: {"sheet": "town", "row": 14, "col": 5},
    207: {"sheet": "town", "row": 14, "col": 6},
    208: {"sheet": "town", "row": 12, "col": 5},
    209: {"sheet": "town", "row": 12, "col": 6},

    210: {"sheet": "town", "row": 15, "col": 5},
    211: {"sheet": "town", "row": 15, "col": 6},
    212: {"sheet": "town", "row": 13, "col": 5},
    213: {"sheet": "town", "row": 13, "col": 6},

    214: {"sheet": "town", "row": 8, "col": 7},
    215: {"sheet": "town", "row": 8, "col": 8},
    216: {"sheet": "town", "row": 9, "col": 7},
    217: {"sheet": "town", "row": 9, "col": 8},

    218: {"sheet": "town", "row": 12, "col": 7},
    219: {"sheet": "town", "row": 12, "col": 8},
    220: {"sheet": "town", "row": 7, "col": 7},
    221: {"sheet": "town", "row": 12, "col": 4},

    222: {"sheet": "town", "row": 13, "col": 7},
    223: {"sheet": "town", "row": 13, "col": 8},
    224: {"sheet": "town", "row": 16, "col": 5},
    225: {"sheet": "town", "row": 13, "col": 4},

    226: {"sheet": "town", "row": 19, "col": 1},
    227: {"sheet": "town", "row": 19, "col": 2},
    228: {"sheet": "town", "row": 22, "col": 1},
    229: {"sheet": "town", "row": 22, "col": 2},
}
# 瓦片图片缓存 - 存储已加载的瓦片图片
# 格式: {"图片名称": pygame.Surface}
sheet_images = {}

# 瓦片图像缓存 - 存储已提取的瓦片
# 格式: {瓦片类型: pygame.Surface}
tile_images = {}

# 游戏时钟
clock = pygame.time.Clock()
FPS = 60

# 初始化音效系统
pygame.mixer.init()
# 设置音效通道数量，确保可以同时播放多个音效
pygame.mixer.set_num_channels(16)

# 音乐配置 - 每个地图有两种音乐：普通音乐和战车音乐
# 格式: {地图名称: {"normal": "普通音乐文件", "vehicle": "战车音乐文件"}}
music_config = {
    "世界地图": {
        "normal": "安详.mp3",
        "vehicle": "战车恰恰.mp3"
    },
    "拉多": {
        "normal": "城镇舞曲.mp3",
        "vehicle": "城镇舞曲.mp3"
    },
    "山洞": {
        "normal": "恐怖山洞.mp3",
        "vehicle": "战车恰恰.mp3"
    },
    "山洞2": {
        "normal": "恐怖山洞.mp3",
        "vehicle": "战车恰恰.mp3"
    }
}

# 当前播放的音乐类型 ("normal" 或 "vehicle")
current_music_type = "normal"

# 当前播放的音乐文件名
current_music = None

# 默认瓦片图像 - 用于优化地图绘制性能
default_tile_image = None

# 地图切换状态管理
map_switch_state = "none"  # none, fading_out, loading, fading_in
map_switch_opacity = 0     # 0-255，用于控制淡入淡出效果
map_switch_target_map = None
map_switch_spawn_point = None

# 战斗淡入淡出状态管理（旧系统，已替换）
# battle_fade_state = "none"  # none, fading_out, waiting, fading_in
# battle_fade_opacity = 0
# battle_fade_wait_timer = 0

# 战斗过渡状态管理（新系统）
battle_transition_state = "none"  # none, map_fading_out, map_faded_out_waiting, battle_active, battle_faded_out_waiting, map_fading_in
battle_transition_opacity = 0     # 0-255，用于控制淡入淡出效果
battle_transition_wait_timer = 0  # 等待计时器
battle_transition_flash_counter = 0  # 爆闪效果计数器

# 战斗系统引用
battle_sys = None
menu_sys = None
battle_player = None
enemies = None

# 菜单状态管理
menu_open = False  # 菜单是否打开
menu_stack = []  # 菜单栈，用于追踪当前菜单层级
selected_main_index = 0  # 主菜单选中的索引
selected_sub_index = 0  # 子菜单选中的索引
menu_changed = False  # 菜单状态是否发生变化

# 主菜单选项
main_menu_items = ["对话", "强度", "装备", "调查", "乘降", "工具", "炮弹", "模式"]

# 子菜单定义
sub_menus = {
    "对话": ["查看对话", "对话记录"],
    "强度": ["攻击力", "防御力", "敏捷度"],
    "装备": ["武器", "防具", "饰品"],
    "调查": ["当前位置", "周围环境"],
    "乘降": ["上战车", "下战车"],
    "工具": ["物品栏", "使用物品"],
    "炮弹": ["装填", "发射"],
    "模式": ["战斗模式", "探索模式"]
}

# 字体设置
font = pygame.font.Font('C:\\Windows\\Fonts\\msyh.ttc', 24)

# 主领导者全局变量
main_leader = None

# 角色类
class Player(pygame.sprite.Sprite):
    # 定义类级别的障碍物集合，避免每次update都重新创建
    OBSTACLES = {
        TILE_BIG_TREE, TILE_HILL1, TILE_HILL2, 11, 14, 15, 16, 19, 20,
        27, 28, 29, 30, 37, 38, 39, 41, 42, 43, 45, 46, 47, 48, 50,
        51, 52, 53, 54, 55, 56, 61, 62, 63, 64, 65, 66, 67, 68, 71, 72,
        100,101,102,104,105,110,112,113,114,115,116,117,118,119,120,122,
        124,125,126,127,150,152,153,154,156,157,158,159,160,161,162,163,
        164,165,166,167,168,170,171,172,176,178,178,180,184,185,186,187,
        189,190,191,192,193,194,195,196,197,198,202,206,207,208,209,210,
        211,212,213,218,219,221,222,223,225,226,227,228,229
    }
    
    # 动画参数
    ANIMATION_SPEED = 10  # 每10帧更新一次动画
    
    def __init__(self, character_id=1):
        super().__init__()
        
        self.character_id = character_id
        
        # 角色位置 - 初始设置为(0, 0)，将在load_map后更新为spawn_point
        self.x = 0
        self.y = 0
        
        # 角色速度 - 每次移动半个格子（4像素），降低移动速度
        self.speed = 4
        
        # 角色方向
        self.direction = "down"
        
        # 动画帧
        self.animation_frames = {}
        self.current_frame = 0
        self.frame_count = 0
        
        # 加载角色图片资源
        self.load_sprites()
        
        # 设置初始图像
        self.image = self.animation_frames[self.direction][0]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        # 获取帧尺寸
        self.frame_width = self.image.get_width()
        self.frame_height = self.image.get_height()
        
        # 记录上一次移动的位置，用于检测是否完成了一次格子移动
        self.last_moved_position = (self.x, self.y)
        
        # 按键状态记录，防止按住不放时快速移动
        self.keys_pressed = set()
        
        # 更新全局主领导者变量
        global main_leader
        main_leader = self
        
        # 战车状态 - 默认为False（不在战车上）
        self.on_vehicle = False
        
        # 连续移动状态跟踪变量
        self.movement_direction = None  # 当前移动方向 (None, "up", "down", "left", "right")
        self.steps_remaining = 0
        self.moving_state = False
        self.just_completed_tile = False  # 是否刚刚完成了一个格子的移动
        
        # 地图切换后临时忽略切换点的标志
        self.just_switched_map = False
        self.ignored_switch_point = None
        self.has_left_switch_point = False
    
    def load_sprites(self):
        # 定义角色动画方向和对应的精灵表行号
        # 精灵表结构：4x4网格
        # 第1行：向下走的4个动画帧
        # 第2行：向左走的4个动画帧
        # 第3行：向右走的4个动画帧
        # 第4行：向上走的4个动画帧
        directions = ["down", "left", "right", "up"]
        
        # 精灵表图片路径
        sprite_sheet_path = os.path.join("assets", "images", "characters", f"主角{self.character_id}.png")
        absolute_path = os.path.abspath(sprite_sheet_path)
        
        try:
            # 加载精灵表
            sprite_sheet = pygame.image.load(absolute_path)
            
            # 计算单个帧的尺寸
            # 精灵表是4x4的，所以宽度除以4，高度除以4
            sheet_width, sheet_height = sprite_sheet.get_size()
            frame_width = sheet_width // 4
            frame_height = sheet_height // 4
            
            # 从精灵表中提取每个方向的帧
            for row, direction in enumerate(directions):
                self.animation_frames[direction] = []
                for col in range(4):
                    # 计算当前帧在精灵表中的位置
                    x = col * frame_width
                    y = row * frame_height
                    
                    # 创建一个新的Surface来存储当前帧
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    
                    # 从精灵表中复制当前帧到新Surface
                    frame.blit(sprite_sheet, (0, 0), (x, y, frame_width, frame_height))
                    
                    # 添加到对应方向的动画帧列表
                    self.animation_frames[direction].append(frame)
                    

            
        except (pygame.error, FileNotFoundError) as e:
            # 如果精灵表加载失败，创建红色占位符
            print(f"警告: 未找到精灵表 {absolute_path}，使用占位符。错误信息: {e}")
            
            # 为每个方向创建占位符帧
            for direction in directions:
                self.animation_frames[direction] = []
                for i in range(4):
                    placeholder = pygame.Surface((32, 48))
                    placeholder.fill((255, 0, 0))  # 红色占位符
                    self.animation_frames[direction].append(placeholder)
    
    def toggle_vehicle(self):
        """
        切换角色的战车状态
        """
        self.on_vehicle = not self.on_vehicle

        
        # 战车状态变化时，检查是否需要切换音乐
        play_music()
    
    def update(self):
        """
        更新角色状态
        """
        moving = False
        
        # 领导者角色响应键盘输入
        keys = pygame.key.get_pressed()
        
        # 记录移动前的位置
        prev_x, prev_y = self.x, self.y
        
        # 移动逻辑 - 实现连续8步移动的状态机
        # 检查是否处于移动状态
        if self.steps_remaining > 0:
            # 继续执行当前方向的移动
            direction = self.movement_direction
            
            # 计算目标格子
            current_x = self.x // TILE_SIZE
            current_y = self.y // TILE_SIZE
            target_x, target_y = current_x, current_y
            
            if direction == "up":
                target_y = current_y - 1
            elif direction == "down":
                target_y = current_y + 1
            elif direction == "left":
                target_x = current_x - 1
            elif direction == "right":
                target_x = current_x + 1
            
            # 检查目标格子是否可通行
            collision = False
            tile_size = TILE_SIZE
            speed = self.speed
            
            # 将渲染坐标转换为原始地图坐标
            original_current_x = current_x - EXTEND_SIZE
            original_current_y = current_y - EXTEND_SIZE
            original_target_x = target_x - EXTEND_SIZE
            original_target_y = target_y - EXTEND_SIZE
            
            if direction == "up" or direction == "down":
                # 垂直移动时，检查Y轴是否接近格子边缘
                if (direction == "up" and self.y % tile_size <= speed) or \
                   (direction == "down" and tile_size - (self.y % tile_size) <= speed):
                    # 接近边缘，检查目标格子是否可通行
                    # 使用原始地图坐标进行边界检查
                    if -1 <= original_target_y < (current_map_height - EXTEND_SIZE * 2 + 1):
                        next_tile = map_data[target_y][current_x]
                        if next_tile in self.OBSTACLES:
                            collision = True
                        # 如果目标格子超出原始地图边界外两格，视为碰撞
                        if original_target_y < -1 or original_target_y >= (current_map_height - EXTEND_SIZE * 2 + 1):
                            collision = True
                # 水平方向保持在同一格子内
                if 0 <= original_current_x < (current_map_width - EXTEND_SIZE * 2):
                    current_tile = map_data[current_y][current_x]
                    if current_tile in self.OBSTACLES:
                        collision = True
            elif direction == "left" or direction == "right":
                # 水平移动时，检查X轴是否接近格子边缘
                if (direction == "left" and self.x % tile_size <= speed) or \
                   (direction == "right" and tile_size - (self.x % tile_size) <= speed):
                    # 接近边缘，检查目标格子是否可通行
                    # 使用原始地图坐标进行边界检查
                    if -1 <= original_target_x < (current_map_width - EXTEND_SIZE * 2 + 1):
                        next_tile = map_data[current_y][target_x]
                        if next_tile in self.OBSTACLES:
                            collision = True
                        # 如果目标格子超出原始地图边界外两格，视为碰撞
                        if original_target_x < -1 or original_target_x >= (current_map_width - EXTEND_SIZE * 2 + 1):
                            collision = True
                # 垂直方向保持在同一格子内
                if 0 <= original_current_y < (current_map_height - EXTEND_SIZE * 2):
                    current_tile = map_data[current_y][current_x]
                    if current_tile in self.OBSTACLES:
                        collision = True
            
            if not collision:
                # 执行移动
                if direction == "up":
                    self.y -= self.speed
                    self.direction = "up"
                elif direction == "down":
                    self.y += self.speed
                    self.direction = "down"
                elif direction == "left":
                    self.x -= self.speed
                    self.direction = "left"
                elif direction == "right":
                    self.x += self.speed
                    self.direction = "right"
                
                moving = True
                self.steps_remaining -= 1
                
                # 检查是否完成移动
                if self.steps_remaining <= 0:
                    self.movement_direction = None
                    self.moving_state = False
                    self.just_completed_tile = True
            else:
                # 遇到障碍物，停止移动
                self.steps_remaining = 0
                self.movement_direction = None
                self.moving_state = False
        else:
            # 非移动状态，检查方向键输入
            new_direction = None
            
            if keys[pygame.K_w]:
                new_direction = "up"
            elif keys[pygame.K_s]:
                new_direction = "down"
            elif keys[pygame.K_a]:
                new_direction = "left"
            elif keys[pygame.K_d]:
                new_direction = "right"
            
            if new_direction:
                # 无论是否可通行，先更新角色方向
                self.direction = new_direction
                
                # 计算当前格子
                current_x = self.x // TILE_SIZE
                current_y = self.y // TILE_SIZE
                target_x, target_y = current_x, current_y
                
                if new_direction == "up":
                    target_y = current_y - 1
                elif new_direction == "down":
                    target_y = current_y + 1
                elif new_direction == "left":
                    target_x = current_x - 1
                elif new_direction == "right":
                    target_x = current_x + 1
                
                # 检查目标格子是否可通行
                collision = False
                
                # 将渲染坐标转换为原始地图坐标
                original_current_x = current_x - EXTEND_SIZE
                original_current_y = current_y - EXTEND_SIZE
                original_target_x = target_x - EXTEND_SIZE
                original_target_y = target_y - EXTEND_SIZE
                
                # 检查目标格子是否在原始地图范围内
                if new_direction == "up" and original_target_y < -1:
                    collision = True
                elif new_direction == "down" and original_target_y >= (current_map_height - EXTEND_SIZE * 2 + 1):
                    collision = True
                elif new_direction == "left" and original_target_x < -1:
                    collision = True
                elif new_direction == "right" and original_target_x >= (current_map_width - EXTEND_SIZE * 2 + 1):
                    collision = True
                
                # 检查目标格子是否是障碍物
                if not collision and 0 <= original_target_x < (current_map_width - EXTEND_SIZE * 2) and 0 <= original_target_y < (current_map_height - EXTEND_SIZE * 2):
                    target_tile = map_data[target_y][target_x]
                    if target_tile in self.OBSTACLES:
                        collision = True
                
                if not collision:
                    # 开始连续移动
                    self.movement_direction = new_direction
                    self.steps_remaining = 8
                    self.moving_state = True
                    
                    # 执行第一步移动
                    if new_direction == "up":
                        self.y -= self.speed
                    elif new_direction == "down":
                        self.y += self.speed
                    elif new_direction == "left":
                        self.x -= self.speed
                    elif new_direction == "right":
                        self.x += self.speed
                    
                    moving = True
                    self.steps_remaining -= 1
        
        # 检查是否踩在地图切换点上或走出原始地图边界外一格
        # 仅当完成一个格子的移动后才进行检测
        if self.just_completed_tile:
            # 使用角色中心点坐标来计算网格位置，确保无论从哪个方向移动，都需要完全进入格子才触发切换
            # 获取渲染坐标
            render_grid_x = self.x // TILE_SIZE
            render_grid_y = self.y // TILE_SIZE
            
            # 将渲染坐标转换为原始地图坐标
            original_grid_x = render_grid_x - EXTEND_SIZE
            original_grid_y = render_grid_y - EXTEND_SIZE
            
            # 检查是否已离开初始忽略的切换点
            if self.ignored_switch_point:
                if (render_grid_x, render_grid_y) != self.ignored_switch_point:
                    self.has_left_switch_point = True
                    
            # 仅当已离开初始切换点或无忽略切换点时检测切换
            if (not self.ignored_switch_point) or (self.ignored_switch_point and self.has_left_switch_point):
                # 检查是否走出原始地图边界外一格
                is_outside_original_boundary = False
                original_map_width = current_map_width - EXTEND_SIZE * 2
                original_map_height = current_map_height - EXTEND_SIZE * 2
                
                if original_grid_x < -1 or original_grid_x >= (original_map_width + 1) or \
                   original_grid_y < -1 or original_grid_y >= (original_map_height + 1):
                    # 超出边界外两格，不允许
                    pass
                elif original_grid_x < 0 or original_grid_x >= original_map_width or \
                     original_grid_y < 0 or original_grid_y >= original_map_height:
                    # 刚好超出边界外一格，触发切换
                    is_outside_original_boundary = True
                
                # 检查是否需要触发地图切换
                if is_outside_original_boundary:
                    # 先检查是否有default_switch配置
                    default_switch = None
                    for switch_point in current_switch_points:
                        # 找到没有x和y坐标的切换点（即default_switch）
                        if "x" not in switch_point and "y" not in switch_point:
                            default_switch = switch_point
                            break
                    
                    if default_switch:
                        # 获取目标地图和出生点
                        target_map = default_switch["target_map"]
                        spawn_point = default_switch.get("spawn_point")
                        
                        print(f"检测到地图切换: 渲染坐标({render_grid_y}, {render_grid_x}) -> 原始坐标({original_grid_y}, {original_grid_x})，目标地图: {target_map}，出生点: {spawn_point}")
                        
                        # 执行地图切换
                        switch_map(target_map, spawn_point)
                else:
                    # 检查是否踩在特定坐标的切换点上
                    for switch_point in current_switch_points:
                        if "x" in switch_point and "y" in switch_point:
                            # 如果switch_point有x和y坐标，则使用原始坐标比较
                            if original_grid_y == switch_point["x"] and original_grid_x == switch_point["y"]:
                                # 获取目标地图和出生点
                                target_map = switch_point["target_map"]
                                spawn_point = switch_point.get("spawn_point")
                                
                                print(f"检测到地图切换: 渲染坐标({render_grid_x}, {render_grid_y}) -> 原始坐标({original_grid_x}, {original_grid_y})，目标地图: {target_map}，出生点: {spawn_point}")
                                
                                # 执行地图切换
                                switch_map(target_map, spawn_point)
                                break
        
        # 动画更新
        if moving:
            self.frame_count += 1
            # 使用类级别常量控制动画速度
            if self.frame_count >= self.ANIMATION_SPEED:
                direction_frames = self.animation_frames[self.direction]
                self.current_frame = (self.current_frame + 1) % len(direction_frames)
                self.frame_count = 0
        elif self.current_frame != 0:
            # 只有在当前帧不是第一帧时才重置，避免不必要的赋值
            self.current_frame = 0
        
        # 更新图像（只在必要时更新）
        direction_frames = self.animation_frames[self.direction]
        new_image = direction_frames[self.current_frame]
        if new_image is not self.image:
            self.image = new_image
        
        # 世界坐标更新
        # 限制角色在游戏世界内移动
        # 使用当前地图的实际尺寸计算世界边界
        current_world_width = current_map_width * TILE_SIZE
        current_world_height = current_map_height * TILE_SIZE
        self.x = max(self.frame_width // 2, min(current_world_width - self.frame_width // 2, self.x))
        self.y = max(self.frame_height // 2, min(current_world_height - self.frame_height // 2, self.y))
        
        # 领导者始终在屏幕中心
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# 创建玩家实例
player = Player(character_id=1)

# 地图加载函数
def load_map(map_name="世界地图"):
    global map_data, tile_images, current_map_name, current_map_width, current_map_height, current_default_tile, current_switch_points, current_map_enable_encounter
    
    # 加载所有在瓦片配置中引用的图片
    sheet_names = set()
    for tile_type, config in tile_config.items():
        sheet_names.add(config["sheet"])
    
    # 加载所有配置的图片
    for sheet_name in sheet_names:
        try:
            # 构建地图图片路径
            map_sheet_path = os.path.join("assets", "images", "ui", f"{sheet_name}.png")
            absolute_path = os.path.abspath(map_sheet_path)
            map_sheet = pygame.image.load(absolute_path)
            

            
            # 存储地图图片
            sheet_images[sheet_name] = map_sheet
            
        except Exception as e:
            print(f"警告: 无法加载地图图片 {absolute_path}，使用占位符。错误信息: {e}")
            # 为无法加载的图片创建占位符
            sheet_images[sheet_name] = None
    
    tile_images.clear()
    for tile_type, config in tile_config.items():
        sheet_name = config["sheet"]
        row_idx = config["row"]  # 从1开始的行索引
        col_idx = config["col"]  # 从1开始的列索引
        
        try:
            # 获取对应的地图图片
            map_sheet = sheet_images[sheet_name]
            
            if map_sheet is None:
                raise Exception(f"地图图片 {sheet_name} 未加载成功")
            
            # 创建瓦片图像表面
            tile = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            
            # 将1-based索引转换为0-based索引
            zero_based_row = row_idx - 1
            zero_based_col = col_idx - 1
            
            x = zero_based_col * TILE_SIZE
            y = zero_based_row * TILE_SIZE
            
            # 从地图图片中提取瓦片
            tile.blit(map_sheet, (0, 0), (x, y, TILE_SIZE, TILE_SIZE))
            
            # 存储瓦片图像
            tile_images[tile_type] = tile
        
        except Exception as e:
            print(f"警告: 无法提取瓦片类型 {tile_type} 的图像，使用占位符。错误信息: {e}")
    
    # 设置默认瓦片图像
    global default_tile_image
    if current_default_tile in tile_images:
        default_tile_image = tile_images[current_default_tile]
    elif tile_images:
        # 如果默认瓦片不可用，使用第一个可用瓦片
        default_tile_image = list(tile_images.values())[0]
    else:
        # 作为最后的备选，创建灰色占位符
        default_tile_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        default_tile_image.fill((128, 128, 128))
    

    
    # 加载地图数据
    import json
    try:
        # 构建地图文件路径
        map_file_path = os.path.join("maps", f"{map_name}.json")
        absolute_path = os.path.abspath(map_file_path)
        
        # 读取地图数据
        with open(absolute_path, "r", encoding="utf-8") as f:
            map_json = json.load(f)
        
        # 加载原始地图数据
        original_map_data = map_json["tiles"]
        original_map_width = map_json["width"]
        original_map_height = map_json["height"]
        
        # 加载默认瓦片配置
        current_default_tile = map_json.get("default_tile", 1)

        
        # 构建扩展后的地图数据
        map_data = []
        
        # 添加顶部扩展行
        for _ in range(EXTEND_SIZE):
            map_data.append([current_default_tile] * (original_map_width + EXTEND_SIZE * 2))
        
        # 添加原始地图行（左右各扩展）
        for row in original_map_data:
            extended_row = [current_default_tile] * EXTEND_SIZE + row + [current_default_tile] * EXTEND_SIZE
            map_data.append(extended_row)
        
        # 添加底部扩展行
        for _ in range(EXTEND_SIZE):
            map_data.append([current_default_tile] * (original_map_width + EXTEND_SIZE * 2))
        
        # 更新当前地图的实际尺寸（包括扩展区域）
        current_map_width = original_map_width + EXTEND_SIZE * 2
        current_map_height = original_map_height + EXTEND_SIZE * 2
        

        
        # 加载地图切换点配置
        current_switch_points = []
        
        # 先加载switch_points数组（如果存在）
        if "switch_points" in map_json:
            current_switch_points.extend(map_json["switch_points"])

        
        # 再加载default_switch单个配置（如果存在）
        if "default_switch" in map_json:
            current_switch_points.append(map_json["default_switch"])
            # 切换点加载信息已简化
        
        if not current_switch_points:
            current_switch_points = []
        
        # 加载遇敌配置
        current_map_enable_encounter = map_json.get("enable_encounter", True)

        
        # 更新当前地图名称
        current_map_name = map_name
        
        # 设置角色位置到spawn_point
        if "spawn_point" in map_json:
            spawn_y, spawn_x = map_json["spawn_point"]
            # 保持使用原始地图坐标，仅在渲染时考虑扩展偏移量
            # 将原始格子坐标转换为扩展后地图的渲染坐标
            render_x = spawn_x + EXTEND_SIZE
            render_y = spawn_y + EXTEND_SIZE
            # 将格子坐标转换为像素坐标
            # 将角色中心定位到瓦片中心
            pixel_x = render_x * TILE_SIZE + TILE_SIZE // 2
            pixel_y = render_y * TILE_SIZE + TILE_SIZE // 2
            
            # 设置角色的位置
            player.x = pixel_x
            player.y = pixel_y
            player.last_moved_position = (player.x, player.y)
            # 根据角色类型更新rect中心位置
            player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            

        
        print(f"成功加载地图: {map_name} (尺寸: {map_json['width']}x{map_json['height']} 格子)")
        
    except Exception as e:
        print(f"警告: 无法加载地图文件 {absolute_path}，使用默认地图。错误信息: {e}")
        


# 检查是否有角色开战车
def check_vehicle_status():
    """
    检查主角是否开战车
    返回: bool - 如果主角开战车返回True，否则返回False
    """
    return player.on_vehicle

# 播放音乐函数
def play_music(map_name=None, force_type=None, force_play=False):
    """
    播放指定地图的音乐，根据战车状态选择音乐类型
    map_name: 地图名称，如果为None则使用当前地图
    force_type: 强制播放的音乐类型 ("normal" 或 "vehicle")，如果为None则自动检测
    force_play: 强制播放音乐，即使音乐相同也重新播放
    """
    global current_music, current_music_type
    
    # 使用当前地图或指定地图
    target_map = map_name if map_name else current_map_name
    
    # 检查地图是否有音乐配置
    if target_map not in music_config:
        print(f"警告: 地图 {target_map} 没有音乐配置")
        return
    
    # 确定要播放的音乐类型
    if force_type:
        music_type = force_type
    else:
        # 检测是否有角色开战车
        has_vehicle = check_vehicle_status()
        music_type = "vehicle" if has_vehicle else "normal"
    
    # 获取音乐文件名
    music_file = music_config[target_map][music_type]
    
    # 构建音乐文件路径
    music_path = os.path.join("assets", "audio", "bgm", music_file)
    absolute_path = os.path.abspath(music_path)
    
    # 地图切换时（map_name参数不为None）：
    # 1. 立即停止当前音乐
    # 2. 立即加载并播放新地图的音乐，不做任何优化检查
    # 3. 确保音乐立即切换，无论当前音乐状态如何
    if map_name is not None:
        try:
            # 停止当前播放的音乐
            pygame.mixer.music.stop()
            
            # 加载并播放新音乐
            pygame.mixer.music.load(absolute_path)
            pygame.mixer.music.play(-1)  # -1 表示循环播放
            
            # 更新当前音乐信息
            current_music = music_file
            current_music_type = music_type
            
        except Exception as e:
            print(f"警告: 无法加载或播放音乐 {absolute_path}。错误信息: {e}")
        return
    
    # 非地图切换场景（战车状态变化等）：
    # 优化检查：只有当音乐类型或音乐文件发生变化时才切换音乐
    # 或者 force_play 为 True 时强制播放
    if not force_play and music_type == current_music_type and current_music == music_file:
        return  # 避免重复播放相同的音乐
    
    try:
        # 停止当前播放的音乐
        pygame.mixer.music.stop()
        
        # 加载并播放新音乐
        pygame.mixer.music.load(absolute_path)
        pygame.mixer.music.play(-1)  # -1 表示循环播放
        
        # 更新当前音乐信息
        current_music = music_file
        current_music_type = music_type
        
    except Exception as e:
        print(f"警告: 无法加载或播放音乐 {absolute_path}。错误信息: {e}")

# 绘制菜单函数
def draw_menu():
    global menu_open, menu_stack, selected_main_index, selected_sub_index
    
    # 菜单配置
    item_height = 40
    item_width = 100
    padding = 10
    border_width = 2
    
    # 计算主菜单尺寸（两列）
    main_menu_cols = 2
    main_menu_rows = (len(main_menu_items) + main_menu_cols - 1) // main_menu_cols
    main_menu_width = main_menu_cols * item_width + padding * (main_menu_cols + 1)
    main_menu_height = main_menu_rows * item_height + padding * (main_menu_rows + 1)
    
    # 计算子菜单尺寸
    if menu_stack:
        current_menu = menu_stack[-1]
        sub_items = sub_menus.get(current_menu, [])
        sub_menu_width = SCREEN_WIDTH - main_menu_width - padding * 2
        sub_menu_height = len(sub_items) * item_height + padding * (len(sub_items) + 1)
    else:
        sub_items = []
        sub_menu_width = SCREEN_WIDTH - main_menu_width - padding * 2
        sub_menu_height = 0
    
    # 主菜单固定在左下角
    main_menu_x = padding
    main_menu_y = SCREEN_HEIGHT - main_menu_height - padding
    
    # 子菜单在主菜单右侧
    sub_menu_x = main_menu_x + main_menu_width + padding
    sub_menu_y = main_menu_y
    
    # 创建主菜单表面（始终显示底色）
    main_menu_surface = pygame.Surface((main_menu_width, main_menu_height), pygame.SRCALPHA)
    main_menu_surface.fill((0, 0, 0, 180))
    pygame.draw.rect(main_menu_surface, (255, 255, 255), (0, 0, main_menu_width, main_menu_height), border_width)
    
    # 始终绘制主菜单项背景（选中高亮）
    for i, item in enumerate(main_menu_items):
        col = i % main_menu_cols
        row = i // main_menu_cols
        x = padding + col * (item_width + padding)
        y = padding + row * (item_height + padding)
        
        # 绘制背景（选中项高亮）
        if not menu_stack and i == selected_main_index:
            pygame.draw.rect(main_menu_surface, (100, 100, 200), (x, y, item_width, item_height))
        else:
            pygame.draw.rect(main_menu_surface, (50, 50, 50), (x, y, item_width, item_height))
        
        # 只有菜单打开时才绘制文字
        if menu_open:
            text_surface = font.render(item, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(x + item_width // 2, y + item_height // 2))
            main_menu_surface.blit(text_surface, text_rect)
    
    # 将主菜单绘制到屏幕
    screen.blit(main_menu_surface, (main_menu_x, main_menu_y))
    
    # 绘制子菜单（只有打开时显示）
    if menu_stack:
        # 创建子菜单表面
        sub_menu_surface = pygame.Surface((sub_menu_width, sub_menu_height), pygame.SRCALPHA)
        sub_menu_surface.fill((0, 0, 0, 180))
        pygame.draw.rect(sub_menu_surface, (255, 255, 255), (0, 0, sub_menu_width, sub_menu_height), border_width)
        
        # 始终绘制子菜单项背景（选中高亮）
        for i, item in enumerate(sub_items):
            y = padding + i * (item_height + padding)
            
            # 绘制背景（选中项高亮）
            if i == selected_sub_index:
                pygame.draw.rect(sub_menu_surface, (100, 100, 200), (padding, y, item_width, item_height))
            else:
                pygame.draw.rect(sub_menu_surface, (50, 50, 50), (padding, y, item_width, item_height))
            
            # 只有菜单打开时才绘制文字
            if menu_open:
                text_surface = font.render(item, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(padding + item_width // 2, y + item_height // 2))
                sub_menu_surface.blit(text_surface, text_rect)
        
        # 将子菜单绘制到屏幕
        screen.blit(sub_menu_surface, (sub_menu_x, sub_menu_y))

# 播放音效的函数
def play_sound(sound_name):
    try:
        sound_path = os.path.join("assets", "audio", "se", sound_name)
        absolute_path = os.path.abspath(sound_path)
        sound = pygame.mixer.Sound(absolute_path)
        sound.play()

    except Exception as e:
        print(f"无法播放音效: {e}")

# 绘制地图函数
def draw_map(camera_x, camera_y):
    # 计算可见区域的起始和结束格子（使用局部变量减少属性查找开销）
    tile_size = TILE_SIZE
    screen_width = SCREEN_WIDTH
    screen_height = SCREEN_HEIGHT
    
    # 计算可见区域的起始和结束格子（使用乘法代替除法，优化性能）
    start_x = max(0, (-camera_x) // tile_size)
    start_y = max(0, (-camera_y) // tile_size)
    end_x = min(current_map_width, start_x + (screen_width // tile_size) + 2)
    end_y = min(current_map_height, start_y + (screen_height // tile_size) + 2)
    
    # 绘制可见区域的地图格子
    map_data_local = map_data
    tile_images_local = tile_images
    default_tile = default_tile_image
    
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile_type = map_data_local[y][x]
            
            # 获取当前瓦片类型对应的图像（直接访问，避免get方法的开销）
            try:
                tile_image = tile_images_local[tile_type]
            except KeyError:
                tile_image = default_tile
            
            # 计算屏幕坐标（应用相机偏移）
            screen_x = x * tile_size + camera_x
            screen_y = y * tile_size + camera_y
            
            # 绘制格子
            screen.blit(tile_image, (screen_x, screen_y))

# 地图切换函数
def switch_map(map_name, spawn_point=None):
    global map_switch_state, map_switch_opacity, map_switch_target_map, map_switch_spawn_point
    
    print(f"开始切换到地图: {map_name}")

    # 播放地图切换音效
    play_sound("Walk Down.mp3")
    
    # 初始化地图切换状态
    map_switch_state = "fading_out"
    map_switch_opacity = 0
    map_switch_target_map = map_name
    map_switch_spawn_point = spawn_point

# 处理地图切换的辅助函数
def handle_map_switch():
    global map_switch_state, map_switch_opacity, map_switch_target_map, map_switch_spawn_point, current_map_name
    
    if map_switch_state == "fading_out":
        # 前一个地图变暗
        map_switch_opacity += 8  # 每次增加5的透明度
        if map_switch_opacity >= 255:
            map_switch_opacity = 255
            map_switch_state = "loading"

    
    elif map_switch_state == "loading":
        # 加载新地图
        try:
            load_map(map_switch_target_map)
            
            # 设置角色位置 - 优先使用switch_point指定的出生点
            if map_switch_spawn_point:
                # 将角色中心定位到瓦片中心
                spawn_grid_y, spawn_grid_x = map_switch_spawn_point

                # 将原始坐标转换为渲染坐标（添加扩展偏移量）
                render_spawn_grid_x = spawn_grid_x + EXTEND_SIZE
                render_spawn_grid_y = spawn_grid_y + EXTEND_SIZE

                # 根据渲染坐标计算像素位置
                spawn_x = render_spawn_grid_x * TILE_SIZE + TILE_SIZE // 2
                spawn_y = render_spawn_grid_y * TILE_SIZE + TILE_SIZE // 2
                source = "切换点指定"
                
                # 更新角色的位置
                player.x = spawn_x
                player.y = spawn_y
                player.last_moved_position = (player.x, player.y)
                player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                
            # 重置角色的移动状态和地图切换标志
            # 重置移动状态，防止地图切换后自动移动
            player.movement_direction = None
            player.steps_remaining = 0
            player.moving_state = False
            
            # 设置地图切换标志，临时忽略切换点
            player.just_switched_map = True
            player.ignored_switch_point = None
            player.has_left_switch_point = False
            # 设置just_completed_tile为True，确保地图切换后立即更新标题栏坐标
            player.just_completed_tile = True
            
            # 检查当前位置是否在切换点上
            # 使用角色中心点坐标来计算网格位置，与update方法保持一致
            render_grid_x = player.x // TILE_SIZE
            render_grid_y = player.y // TILE_SIZE
            # 将渲染坐标转换为原始地图坐标
            original_grid_x = render_grid_x - EXTEND_SIZE
            original_grid_y = render_grid_y - EXTEND_SIZE
            for switch_point in current_switch_points:
                # 只有当switch_point包含x和y坐标时才进行比较
                if "x" in switch_point and "y" in switch_point:
                    # 注意x和y的顺序
                    if original_grid_y == switch_point["x"] and original_grid_x == switch_point["y"]:
                        # 设置忽略的切换点（使用渲染坐标）
                        player.ignored_switch_point = (render_grid_x, render_grid_y)

                        break
            
            # 播放新地图的音乐
            play_music(map_switch_target_map)
            
            # 进入淡入状态
            map_switch_state = "fading_in"
            
        except Exception as e:
            print(f"加载新地图时出错: {e}")
            map_switch_state = "none"  # 切换失败，恢复正常状态
    
    elif map_switch_state == "fading_in":
        # 新地图变亮
        map_switch_opacity -= 8  # 每次减少5的透明度
        if map_switch_opacity <= 0:
            map_switch_opacity = 0
            map_switch_state = "none"
            map_switch_target_map = None
            map_switch_spawn_point = None


# 处理战斗过渡的辅助函数（新系统）
def handle_battle_transition():
    global battle_transition_state, battle_transition_opacity, battle_transition_wait_timer, battle_transition_flash_counter, battle_sys, screen, player, main_leader, BLACK, SCREEN_WIDTH, SCREEN_HEIGHT
    
    if battle_transition_state == "map_fading_out":
        # 只在状态刚进入时播放一次战斗开始音效
        if battle_transition_flash_counter == 0:  # 第一次进入状态时播放
            # 播放战斗开始音效
            battle_start_sound_path = os.path.join("assets", "sounds", "战斗.mp3")
            if os.path.exists(battle_start_sound_path):
                try:
                    # 每次战斗开始时都重新加载音效，确保能正常播放
                    battle_start_sound = pygame.mixer.Sound(battle_start_sound_path)
                    
                    # 确保有足够的通道
                    if pygame.mixer.get_num_channels() < 10:
                        pygame.mixer.set_num_channels(10)
                    
                    # 始终使用强制通道播放，确保能播放
                    channel = pygame.mixer.find_channel(True)
                    if channel:
                        channel.play(battle_start_sound)
                except Exception as e:
                    pass
            else:
                pass
        
        # 爆闪效果：快速切换黑白
        battle_transition_flash_counter += 1
        
        # 每4帧切换一次（约0.067秒一次切换）
        if battle_transition_flash_counter % 4 == 0:
            # 交替设置透明度为0（白，原图）和255（黑，全屏黑）
            if battle_transition_opacity == 0:
                battle_transition_opacity = 255
            else:
                battle_transition_opacity = 0
        
        # 爆闪8次（4次黑4次白）后结束，总共32帧
        if battle_transition_flash_counter >= 32:
            # 最后保持全黑状态
            battle_transition_opacity = 255
            # 直接切换到战斗场景状态，没有等待时间
            battle_transition_state = "battle_active"
            battle_transition_flash_counter = 0  # 重置计数器

    # 战斗淡出完成后等待一段时间
    elif battle_transition_state == "battle_faded_out_waiting":
        battle_transition_wait_timer += 1
        # 等待30帧（约0.5秒）
        if battle_transition_wait_timer >= 30:
            # 切换到地图淡入状态
            battle_transition_state = "map_fading_in"
            battle_transition_wait_timer = 0

    elif battle_transition_state == "map_fading_in":
        # 渐变淡入效果：从全黑逐渐恢复到原图
        if battle_transition_flash_counter == 0:
            # 初始状态为全黑
            battle_transition_opacity = 255
        
        # 逐渐降低透明度（每帧减少8）
        battle_transition_opacity -= 8
        
        # 确保透明度不小于0
        if battle_transition_opacity <= 0:
            # 最后保持完全显示地图状态
            battle_transition_opacity = 0
            battle_transition_state = "none"
            battle_transition_flash_counter = 0  # 重置爆闪计数器
            # 恢复地图音乐
            play_music(force_play=True)
            # 强制刷新地图和角色画面
            # 获取当前相机位置
            if main_leader:
                camera_x = SCREEN_WIDTH // 2 - main_leader.x
                camera_y = SCREEN_HEIGHT // 2 - main_leader.y
            else:
                camera_x = SCREEN_WIDTH // 2 - player.x
                camera_y = SCREEN_HEIGHT // 2 - player.y
            # 绘制地图
            draw_map(camera_x, camera_y)
            # 绘制玩家角色
            if main_leader:
                screen.blit(main_leader.image, main_leader.rect)
            else:
                screen.blit(player.image, player.rect)
            # 更新显示
            pygame.display.flip()
        else:
            # 只有当透明度还没有降到0时，才递增计数器
            battle_transition_flash_counter += 1
        
# 游戏主循环
def game_loop():
    global menu_changed, battle_transition_state, battle_transition_opacity, battle_transition_wait_timer
    global battle_sys, menu_sys, battle_player, enemies
    load_map()
    
    # 播放初始地图的音乐
    play_music()
    
    running = True
    
    # 游戏启动时强制绘制一次初始画面
    # 绘制初始地图
    camera_x = SCREEN_WIDTH // 2 - player.x
    camera_y = SCREEN_HEIGHT // 2 - player.y
    screen.fill(BLACK)
    draw_map(camera_x, camera_y)
    
    # 绘制玩家
    screen.blit(player.image, player.rect)
    
    # 显示坐标信息
    if main_leader:
        # 获取渲染坐标
        render_grid_x = main_leader.x // TILE_SIZE
        render_grid_y = main_leader.y // TILE_SIZE
        # 将渲染坐标转换为原始地图坐标
        original_grid_x = render_grid_x - EXTEND_SIZE
        original_grid_y = render_grid_y - EXTEND_SIZE
        # 显示地图名和原始网格坐标在同一行
        pygame.display.set_caption(f"重装机兵 - {current_map_name} | X={original_grid_y} Y={original_grid_x}")
    
    # 更新显示
    pygame.display.flip()
    
    # 缓存全局变量到局部变量，减少属性查找开销
    screen_width = SCREEN_WIDTH
    screen_height = SCREEN_HEIGHT
    tile_size = TILE_SIZE
    
    # 初始化窗口标题
    last_caption = ""
    
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # 菜单相关全局变量
                global menu_open, menu_stack, selected_main_index, selected_sub_index, menu_changed
                
                # J键切换菜单开关
                if event.key == pygame.K_j:
                    if not menu_open:
                        menu_open = True
                        menu_stack = []
                        selected_main_index = 0
                        selected_sub_index = 0
                        menu_changed = True
                    else:
                        # 如果菜单已打开，J键确认选择
                        if not menu_stack:
                            # 主菜单：进入子菜单
                            selected_item = main_menu_items[selected_main_index]
                            if selected_item in sub_menus:
                                menu_stack.append(selected_item)
                                selected_sub_index = 0
                                menu_changed = True
                        else:
                            # 子菜单：处理选项
                            current_menu = menu_stack[-1]
                            current_items = sub_menus[current_menu]
                            selected_item = current_items[selected_sub_index]
                            # 执行菜单项功能（可以在这里添加具体功能实现）
                
                # K键返回上级菜单
                elif event.key == pygame.K_k:
                    if menu_open:
                        if menu_stack:
                            # 返回上级菜单
                            menu_stack.pop()
                            selected_sub_index = 0
                            menu_changed = True
                        else:
                            # 主菜单：关闭菜单
                            menu_open = False
                            menu_changed = True
                
                # WSAD键选择菜单项（只要菜单底色显示就可以选择）
                elif event.key == pygame.K_w:
                    if not menu_stack:
                        # 主菜单：向上选择
                        selected_main_index = (selected_main_index - 2) % len(main_menu_items)
                        menu_changed = True
                    else:
                        # 子菜单：向上选择
                        current_menu = menu_stack[-1]
                        max_index = len(sub_menus[current_menu]) - 1
                        selected_sub_index = (selected_sub_index - 1) % (max_index + 1)
                        menu_changed = True
                
                elif event.key == pygame.K_s:
                    if not menu_stack:
                        # 主菜单：向下选择
                        selected_main_index = (selected_main_index + 2) % len(main_menu_items)
                        menu_changed = True
                    else:
                        # 子菜单：向下选择
                        current_menu = menu_stack[-1]
                        max_index = len(sub_menus[current_menu]) - 1
                        selected_sub_index = (selected_sub_index + 1) % (max_index + 1)
                        menu_changed = True
                
                elif event.key == pygame.K_a:
                    if not menu_stack:
                        # 主菜单：向左选择
                        if selected_main_index % 2 == 1:
                            selected_main_index -= 1
                        menu_changed = True
                
                elif event.key == pygame.K_d:
                    if not menu_stack:
                        # 主菜单：向右选择
                        if selected_main_index % 2 == 0 and selected_main_index < len(main_menu_items) - 1:
                            selected_main_index += 1
                        menu_changed = True
        
        # 处理地图切换状态
        handle_map_switch()
        
        # 处理战斗过渡状态
        handle_battle_transition()
        
        # 检测方向键输入
        keys = pygame.key.get_pressed()
        
        # 检查是否有方向键被按下
        movement_input = keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]
        
        # 检查是否有角色正在移动中
        any_moving = player.steps_remaining > 0 or player.moving_state
        
        # 初始化游戏状态变化标志为false
        game_changed = False
        
        # 只有当有输入或有角色正在移动时，才执行更新
        # 地图切换过程中、菜单打开或战斗过渡过程中禁止玩家移动
        if (movement_input or any_moving) and map_switch_state == "none" and not menu_open and battle_transition_state == "none":
            # 更新游戏状态
            prev_x, prev_y = player.x, player.y
            player.update()
            # 检查是否有实际移动
            if player.x != prev_x or player.y != prev_y:
                game_changed = True
                # 只有刚刚完成一个格子移动时才检测遇敌
                if player.just_completed_tile:
                    # 3%的遇怪概率检测，但如果已经触发地图切换则不检测
                    if current_map_enable_encounter and random.random() < 0.03 and battle_transition_state == "none" and map_switch_state == "none":
                        # 启动战斗淡入淡出效果
                        battle_transition_state = "map_fading_out"
                        battle_transition_opacity = 0
                        battle_transition_wait_timer = 0
                        # 初始化战斗过渡爆闪计数器，用于控制黑白闪烁次数
                        battle_transition_flash_counter = 0
                        # 暂停地图音乐
                        pygame.mixer.music.stop()
                        # 预加载战斗系统
                        battle_sys, menu_sys, battle_player, enemies = battle_system.start_battle(
                            player_hp=100, player_atk=25, player_defense=10, player_agility=4
                        )
        
        # 地图切换过程中或游戏状态变化时，都要重新绘制和刷新屏幕
        # 菜单打开或菜单状态变化时也需要重新绘制
        if game_changed or map_switch_state != "none" or menu_open or menu_changed or battle_transition_state != "none":
            # 绘制游戏
            screen.fill(BLACK)
            
            # 绘制地图
            if main_leader:
                camera_x = screen_width // 2 - main_leader.x
                camera_y = screen_height // 2 - main_leader.y
            else:
                camera_x = 0
                camera_y = 0
            draw_map(camera_x, camera_y)
            
            # 绘制玩家
            screen.blit(player.image, player.rect)
            
            # 显示地图名和主角的当前格子坐标
            if main_leader:
                # 只有当角色完成瓦片移动时才更新标题栏坐标
                if main_leader.just_completed_tile:
                    # 使用角色中心点位置计算所在的格子（渲染坐标）
                    render_grid_x = main_leader.x // tile_size
                    render_grid_y = main_leader.y // tile_size
                    # 将渲染坐标转换为原始地图坐标
                    original_grid_x = render_grid_x - EXTEND_SIZE
                    original_grid_y = render_grid_y - EXTEND_SIZE
                    # 只有当标题内容变化时才更新窗口标题，减少不必要的系统调用
                    new_caption = f"重装机兵 - {current_map_name} | X={original_grid_y} Y={original_grid_x}"
                    if new_caption != last_caption:
                        pygame.display.set_caption(new_caption)
                        last_caption = new_caption
                    # 重置完成瓦片移动标志
                    main_leader.just_completed_tile = False
            
            # 绘制淡入淡出效果的覆盖层
            if map_switch_state != "none":
                overlay = pygame.Surface((screen_width, screen_height))
                overlay.fill((0, 0, 0))  # 黑色覆盖层
                overlay.set_alpha(map_switch_opacity)  # 设置透明度
                screen.blit(overlay, (0, 0))
            
            # 绘制战斗过渡效果的覆盖层
            if battle_transition_state != "none":
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill(BLACK)  # 黑色覆盖层
                overlay.set_alpha(battle_transition_opacity)  # 设置透明度
                screen.blit(overlay, (0, 0))
            
            # 如果进入战斗激活状态，进入战斗循环
            if battle_transition_state == "battle_active" and battle_sys is not None:
                # 重置透明度，确保战斗场景能正常显示
                battle_transition_opacity = 0
                battle_running = True
                while battle_running:
                    for battle_event in pygame.event.get():
                        if battle_event.type == pygame.QUIT:
                            running = False
                            battle_running = False
                        battle_system.handle_battle_input(battle_event, battle_sys, menu_sys)
                    battle_over = battle_system.update_battle(battle_sys, menu_sys, screen)
                    pygame.display.flip()
                    if battle_over:
                        battle_running = False
                        # 设置战斗结束后进入淡出等待状态
                        battle_transition_state = "battle_faded_out_waiting"
                        battle_transition_opacity = 255
                        battle_transition_wait_timer = 0
                        battle_transition_flash_counter = 0  # 重置爆闪计数器
                        # 清空战斗系统引用
                        battle_sys = None
                        menu_sys = None
                        battle_player = None
                        enemies = None
            
            # 绘制菜单
            if menu_open:
                draw_menu()
            
            # 重置菜单变化标志
            menu_changed = False
            
            # 更新显示
            pygame.display.flip()
        
        # 控制帧率
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()