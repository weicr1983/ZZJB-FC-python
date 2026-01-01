import pygame
import sys
import os
import json
import tkinter as tk
from tkinter import filedialog
import re

# 初始化tkinter
root = tk.Tk()
root.withdraw()  # 隐藏主窗口

# 初始化Pygame
pygame.init()

# 设置编辑器窗口
EDITOR_WIDTH = 1000
EDITOR_HEIGHT = 700
screen = pygame.display.set_mode((EDITOR_WIDTH, EDITOR_HEIGHT))
pygame.display.set_caption("地图编辑器")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (150, 150, 150)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 瓦片设置
TILE_SIZE = 32

# 地图类型常量
TILE_BIG_TREE = 2  # 大树格子（不可通行）
TILE_SMALL_TREE = 3  # 小树格子（可通行）
TILE_HILL1 = 7  # 山头1格子（不可通行）
TILE_HILL2 = 8  # 山头2格子（不可通行）   

# 瓦片配置 - 支持从不同图片提取瓦片
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
    50: {"sheet": "map2", "row": 3, "col": 1},   # 火山1
    51: {"sheet": "map2", "row": 3, "col": 2},   # 火山2
    52: {"sheet": "map2", "row": 3, "col": 3},   # 火山3
    
    53: {"sheet": "map2", "row": 9, "col": 4},   # 石块
    54: {"sheet": "map2", "row": 4, "col": 1},   # 火山4
    55: {"sheet": "map2", "row": 4, "col": 2},   # 火山5
    56: {"sheet": "map2", "row": 4, "col": 3},   # 火山6

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

    202: {"sheet": "town", "row": 15, "col": 2},
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

# 瓦片图片缓存
sheet_images = {}
tile_images = {}

# 编辑器状态
class EditorState:
    def __init__(self):
        self.map_width = 16
        self.map_height = 16
        self.default_tile = TILE_FLOOR
        self.previous_default_tile = TILE_FLOOR  # 保存旧的默认瓦片值
        self.selected_tile = TILE_FLOOR
        self.map_data = []
        self.spawn_point = [8, 8]
        self.switch_points = []
        self.is_dragging = False
        self.is_dragging_tiles = False  # 标记是拖拽瓦片还是拖拽地图
        self.is_dragging_scrollbar = False  # 标记是否在拖拽滚动条
        self.drag_start_pos = None
        self.map_offset_x = -50
        self.map_offset_y = -50
        self.zoom = 1.0
        self.init_map_data()
        # 地图名称
        self.map_name = "new_map"  # 默认地图名
        # 输入模式状态
        self.editing_width = False
        self.editing_height = False
        self.width_input_text = str(self.map_width)
        self.height_input_text = str(self.map_height)
        # 当前点击的瓦片坐标
        self.selected_tile_coords = None  # (x, y)
        # 右键点击的瓦片坐标
        self.right_click_coords = None  # (x, y)
        # 滚动条状态
        self.scrollbar_width = 15
        self.scrollbar_height = 15
        self.is_dragging_hscroll = False
        self.is_dragging_vscroll = False
        # 瓦片选择器滚动状态
        self.tile_selector_offset_y = 0  # 瓦片选择器垂直偏移
        self.is_dragging_tile_scrollbar = False  # 标记是否在拖拽瓦片选择器滚动条
        self.tile_selector_scrollbar_width = 12  # 瓦片选择器滚动条宽度
        self.tile_selector_visible_height = 200  # 瓦片选择器可见高度
        # 是否允许遇敌
        self.enable_encounter = False
    
    def init_map_data(self):
        self.map_data = []
        for _ in range(self.map_height):
            row = [self.default_tile] * self.map_width
            self.map_data.append(row)
    
    def resize_map(self, new_width, new_height):
        """
        调整地图尺寸，保留原有数据，新增部分使用默认瓦片填充
        """
        if new_width <= 0 or new_height <= 0:
            return False
            
        # 创建新的地图数据结构
        new_map_data = []
        
        # 处理每一行
        for y in range(new_height):
            new_row = []
            
            # 处理每一列
            for x in range(new_width):
                # 如果在原有地图范围内，使用原有数据
                if y < len(self.map_data) and x < len(self.map_data[y]):
                    new_row.append(self.map_data[y][x])
                # 否则使用默认瓦片
                else:
                    new_row.append(self.default_tile)
            
            new_map_data.append(new_row)
        
        # 更新地图尺寸和数据
        self.map_width = new_width
        self.map_height = new_height
        self.map_data = new_map_data
        
        return True

# 加载瓦片图片
def load_tile_images():
    for tile_type, config in tile_config.items():
        sheet_name = config["sheet"]
        row = config["row"]
        col = config["col"]
        
        # 加载图片
        if sheet_name not in sheet_images:
            image_path = os.path.join("assets", "images", "ui", f"{sheet_name}.png")
            if os.path.exists(image_path):
                sheet_images[sheet_name] = pygame.image.load(image_path).convert_alpha()
            else:
                print(f"警告: 图片 {image_path} 不存在")
                continue
        
        try:
            # 计算瓦片在图片中的位置
            x = (col - 1) * TILE_SIZE
            y = (row - 1) * TILE_SIZE
            
            # 提取瓦片
            tile = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            tile.blit(sheet_images[sheet_name], (0, 0), (x, y, TILE_SIZE, TILE_SIZE))
            tile_images[tile_type] = tile
        except Exception as e:
            print(f"警告: 无法提取瓦片类型 {tile_type} 的图像，使用占位符。错误信息: {e}")
            # 创建灰色占位符
            tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
            tile.fill((128, 128, 128))
            tile_images[tile_type] = tile

# 绘制地图
def draw_map(state, screen):
    scaled_tile_size = int(TILE_SIZE * state.zoom)
    
    # 计算地图区域大小（左侧地图区域，右侧200px为控制面板）
    map_area_width = EDITOR_WIDTH - 200 - state.scrollbar_width
    map_area_height = EDITOR_HEIGHT - state.scrollbar_height
    
    # 绘制地图格子，但只绘制在地图区域内的部分
    for y in range(state.map_height):
        for x in range(state.map_width):
            screen_x = state.map_offset_x + x * scaled_tile_size
            screen_y = state.map_offset_y + y * scaled_tile_size
            
            # 检查瓦片是否在地图区域内，如果完全在地图区域外则跳过绘制
            if (screen_x + scaled_tile_size < 0 or 
                screen_x > map_area_width or 
                screen_y + scaled_tile_size < 0 or 
                screen_y > map_area_height):
                continue
            
            # 绘制格子背景
            pygame.draw.rect(screen, LIGHT_GRAY, (screen_x, screen_y, scaled_tile_size, scaled_tile_size))
            
            # 绘制瓦片
            tile_type = state.map_data[y][x]
            if tile_type in tile_images:
                tile_image = pygame.transform.scale(tile_images[tile_type], (scaled_tile_size, scaled_tile_size))
                screen.blit(tile_image, (screen_x, screen_y))
            
            # 绘制格子边框
            pygame.draw.rect(screen, GRAY, (screen_x, screen_y, scaled_tile_size, scaled_tile_size), 1)
    
    # 绘制出生点
    if state.spawn_point:
        spawn_x, spawn_y = state.spawn_point
        screen_x = state.map_offset_x + spawn_x * scaled_tile_size
        screen_y = state.map_offset_y + spawn_y * scaled_tile_size
        pygame.draw.rect(screen, GREEN, (screen_x, screen_y, scaled_tile_size, scaled_tile_size), 3)
    
    # 绘制切换点
    for i, switch_point in enumerate(state.switch_points):
        x, y = switch_point["y"], switch_point["x"]
        screen_x = state.map_offset_x + x * scaled_tile_size
        screen_y = state.map_offset_y + y * scaled_tile_size
        
        pygame.draw.rect(screen, BLUE, (screen_x, screen_y, scaled_tile_size, scaled_tile_size), 3)
    
    # 计算地图区域大小
    map_area_width = EDITOR_WIDTH - 200 - state.scrollbar_width
    map_area_height = EDITOR_HEIGHT - state.scrollbar_height
    
    # 计算地图实际大小
    map_actual_width = state.map_width * scaled_tile_size
    map_actual_height = state.map_height * scaled_tile_size
    
    # 绘制水平滚动条（仅当地图宽度大于显示区域时）
    if map_actual_width > map_area_width:
        # 滚动条轨道
        hscroll_track = pygame.Rect(0, map_area_height, map_area_width, state.scrollbar_height)
        pygame.draw.rect(screen, DARK_GRAY, hscroll_track)
        
        # 滚动条滑块
        hscroll_slider_width = max(20, int(map_area_width * map_area_width / map_actual_width))
        hscroll_slider_x = int((abs(state.map_offset_x) / (map_actual_width - map_area_width)) * (map_area_width - hscroll_slider_width)) if map_actual_width > map_area_width else 0
        hscroll_slider = pygame.Rect(hscroll_slider_x, map_area_height, hscroll_slider_width, state.scrollbar_height)
        pygame.draw.rect(screen, LIGHT_GRAY, hscroll_slider)
        pygame.draw.rect(screen, BLACK, hscroll_slider, 1)
    
    # 绘制垂直滚动条（仅当地图高度大于显示区域时）
    if map_actual_height > map_area_height:
        # 滚动条轨道
        vscroll_track = pygame.Rect(map_area_width, 0, state.scrollbar_width, map_area_height)
        pygame.draw.rect(screen, DARK_GRAY, vscroll_track)
        
        # 滚动条滑块
        vscroll_slider_height = max(20, int(map_area_height * map_area_height / map_actual_height))
        vscroll_slider_y = int((abs(state.map_offset_y) / (map_actual_height - map_area_height)) * (map_area_height - vscroll_slider_height)) if map_actual_height > map_area_height else 0
        vscroll_slider = pygame.Rect(map_area_width, vscroll_slider_y, state.scrollbar_width, vscroll_slider_height)
        pygame.draw.rect(screen, LIGHT_GRAY, vscroll_slider)
        pygame.draw.rect(screen, BLACK, vscroll_slider, 1)

# 绘制控制面板
def draw_control_panel(state, screen):
    panel_width = 200
    panel_height = EDITOR_HEIGHT
    
    # 绘制面板背景
    pygame.draw.rect(screen, GRAY, (EDITOR_WIDTH - panel_width, 0, panel_width, panel_height))
    
    # 字体设置 - 使用系统支持中文的字体
    try:
        # 尝试使用微软雅黑（Windows系统默认中文字体）
        font = pygame.font.SysFont("Microsoft YaHei", 24)
        small_font = pygame.font.SysFont("Microsoft YaHei", 18)
    except:
        # 如果找不到微软雅黑，尝试使用黑体
        try:
            font = pygame.font.SysFont("SimHei", 24)
            small_font = pygame.font.SysFont("SimHei", 18)
        except:
            # 如果还是找不到，使用默认字体
            font = pygame.font.Font(None, 24)
            small_font = pygame.font.Font(None, 18)
    
    # 导出图片按钮
    export_btn = pygame.Rect(EDITOR_WIDTH - panel_width + 20, 10, 160, 30)
    pygame.draw.rect(screen, (0, 128, 0), export_btn)  # 绿色按钮
    export_text = small_font.render("导出地图图片", True, WHITE)
    screen.blit(export_text, (EDITOR_WIDTH - panel_width + 40, 15))
    
    # 地图尺寸设置
    y_pos = 50
    label = small_font.render("地图宽度:", True, BLACK)
    screen.blit(label, (EDITOR_WIDTH - panel_width + 20, y_pos))
    width_input = pygame.Rect(EDITOR_WIDTH - panel_width + 100, y_pos, 80, 24)
    # 编辑模式下显示输入的文本，否则显示当前地图宽度
    display_width = state.width_input_text if state.editing_width else str(state.map_width)
    pygame.draw.rect(screen, WHITE, width_input)
    pygame.draw.rect(screen, BLACK, width_input, 2)
    width_text = small_font.render(display_width, True, BLACK)
    screen.blit(width_text, (EDITOR_WIDTH - panel_width + 105, y_pos + 3))
    
    y_pos += 40
    label = small_font.render("地图高度:", True, BLACK)
    screen.blit(label, (EDITOR_WIDTH - panel_width + 20, y_pos))
    height_input = pygame.Rect(EDITOR_WIDTH - panel_width + 100, y_pos, 80, 24)
    # 编辑模式下显示输入的文本，否则显示当前地图高度
    display_height = state.height_input_text if state.editing_height else str(state.map_height)
    pygame.draw.rect(screen, WHITE, height_input)
    pygame.draw.rect(screen, BLACK, height_input, 2)
    height_text = small_font.render(display_height, True, BLACK)
    screen.blit(height_text, (EDITOR_WIDTH - panel_width + 105, y_pos + 3))
    
    y_pos += 40
    resize_btn = pygame.Rect(EDITOR_WIDTH - panel_width + 20, y_pos, 160, 30)
    pygame.draw.rect(screen, BLUE, resize_btn)
    resize_text = small_font.render("调整地图尺寸", True, WHITE)
    screen.blit(resize_text, (EDITOR_WIDTH - panel_width + 55, y_pos + 7))
    
    y_pos += 50
    # 默认瓦片设置
    label = small_font.render("默认瓦片:", True, BLACK)
    screen.blit(label, (EDITOR_WIDTH - panel_width + 20, y_pos))
    
    # 绘制当前默认瓦片
    default_tile_x = EDITOR_WIDTH - panel_width + 100
    default_tile_y = y_pos - 5
    default_tile_rect = pygame.Rect(default_tile_x, default_tile_y, TILE_SIZE, TILE_SIZE)
    if state.default_tile in tile_images:
        screen.blit(tile_images[state.default_tile], (default_tile_x, default_tile_y))
    pygame.draw.rect(screen, BLACK, (default_tile_x, default_tile_y, TILE_SIZE, TILE_SIZE), 2)
    pygame.draw.rect(screen, GREEN, (default_tile_x - 5, default_tile_y - 5, TILE_SIZE + 10, TILE_SIZE + 10), 2)
    
    # 瓦片选择器
    y_pos += 60
    label = small_font.render("选择瓦片:", True, BLACK)
    screen.blit(label, (EDITOR_WIDTH - panel_width + 20, y_pos))
    
    y_pos += 30
    
    # 瓦片选择器容器
    container_x = EDITOR_WIDTH - panel_width + 20
    container_y = y_pos
    container_width = panel_width - 40 - state.tile_selector_scrollbar_width
    container_height = state.tile_selector_visible_height
    
    # 绘制瓦片选择器背景
    pygame.draw.rect(screen, WHITE, (container_x, container_y, container_width, container_height))
    pygame.draw.rect(screen, BLACK, (container_x, container_y, container_width, container_height), 2)
    
    # 计算瓦片网格信息
    tiles_per_row = 4
    tile_spacing = 5
    
    # 计算所有瓦片需要的总高度
    sorted_tiles = sorted(tile_images.keys())
    total_tiles = len(sorted_tiles)
    total_rows = (total_tiles + tiles_per_row - 1) // tiles_per_row
    total_height = total_rows * (TILE_SIZE + tile_spacing)
    
    # 绘制瓦片选择网格
    tile_rects = []
    for index, tile_type in enumerate(sorted_tiles):
        tile_row = index // tiles_per_row
        tile_col = index % tiles_per_row
        
        # 计算瓦片在容器中的位置（考虑滚动偏移）
        tile_x = container_x + tile_col * (TILE_SIZE + tile_spacing)
        tile_y = container_y + tile_row * (TILE_SIZE + tile_spacing) - state.tile_selector_offset_y
        
        # 只有当瓦片在可见区域内时才绘制
        if container_y <= tile_y + TILE_SIZE and tile_y <= container_y + container_height:
            tile_rect = pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)
            tile_rects.append((tile_type, tile_rect))
            
            # 绘制瓦片
            if tile_type in tile_images:
                screen.blit(tile_images[tile_type], (tile_x, tile_y))
            
            # 绘制选中边框
            if tile_type == state.selected_tile:
                pygame.draw.rect(screen, RED, (tile_x, tile_y, TILE_SIZE, TILE_SIZE), 3)
            else:
                pygame.draw.rect(screen, BLACK, (tile_x, tile_y, TILE_SIZE, TILE_SIZE), 1)
    
    # 绘制瓦片选择器滚动条（仅当总高度超过可见高度时）
    scrollbar_rects = []
    if total_height > container_height:
        scrollbar_x = container_x + container_width
        scrollbar_y = container_y
        scrollbar_width = state.tile_selector_scrollbar_width
        scrollbar_height = container_height
        
        # 绘制滚动条轨道
        pygame.draw.rect(screen, DARK_GRAY, (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
        
        # 计算滑块大小和位置
        slider_height = max(20, int(container_height * container_height / total_height))
        slider_y = scrollbar_y + int((state.tile_selector_offset_y / (total_height - container_height)) * (container_height - slider_height))
        
        # 绘制滑块
        slider_rect = pygame.Rect(scrollbar_x, slider_y, scrollbar_width, slider_height)
        pygame.draw.rect(screen, LIGHT_GRAY, slider_rect)
        pygame.draw.rect(screen, BLACK, slider_rect, 1)
        
        # 添加滚动条Rect到UI元素中
        scrollbar_rects.append(('tile_scrollbar', pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)))
        scrollbar_rects.append(('tile_scrollbar_slider', slider_rect))
    
    # 更新y_pos（使用固定的可见高度，不考虑实际瓦片数量）
    y_pos += state.tile_selector_visible_height + 30
    
    # 将滚动条Rect添加到tile_rects中，以便事件处理
    tile_rects.extend(scrollbar_rects)
    # 保存按钮
    save_btn = pygame.Rect(EDITOR_WIDTH - panel_width + 20, y_pos, 160, 30)
    pygame.draw.rect(screen, GREEN, save_btn)
    save_text = small_font.render("保存地图", True, WHITE)
    screen.blit(save_text, (EDITOR_WIDTH - panel_width + 65, y_pos + 7))
    
    y_pos += 40
    # 加载按钮
    load_btn = pygame.Rect(EDITOR_WIDTH - panel_width + 20, y_pos, 160, 30)
    pygame.draw.rect(screen, BLUE, load_btn)
    load_text = small_font.render("加载地图", True, WHITE)
    screen.blit(load_text, (EDITOR_WIDTH - panel_width + 65, y_pos + 7))
    
    # 应用默认瓦片按钮
    y_pos += 40
    apply_default_btn = pygame.Rect(EDITOR_WIDTH - panel_width + 20, y_pos, 160, 30)
    pygame.draw.rect(screen, RED, apply_default_btn)
    apply_default_text = small_font.render("应用默认瓦片", True, WHITE)
    screen.blit(apply_default_text, (EDITOR_WIDTH - panel_width + 35, y_pos + 7))
    
    # 显示选中的瓦片坐标
    y_pos += 60
    label = small_font.render("瓦片坐标:", True, BLACK)
    screen.blit(label, (EDITOR_WIDTH - panel_width + 20, y_pos))
    if state.selected_tile_coords:
        coords_text = small_font.render(f"({state.selected_tile_coords[1]}, {state.selected_tile_coords[0]})", True, BLACK)
    else:
        coords_text = small_font.render("未选中", True, BLACK)
    screen.blit(coords_text, (EDITOR_WIDTH - panel_width + 120, y_pos))
    
    # 显示右键点击的瓦片坐标
    y_pos += 30
    label = small_font.render("右键坐标:", True, BLACK)
    screen.blit(label, (EDITOR_WIDTH - panel_width + 20, y_pos))
    if state.right_click_coords:
        coords_text = small_font.render(f"({state.right_click_coords[1]}, {state.right_click_coords[0]})", True, BLACK)
    else:
        coords_text = small_font.render("未点击", True, BLACK)
    screen.blit(coords_text, (EDITOR_WIDTH - panel_width + 120, y_pos))
    
    # 返回UI元素的Rect信息
    return {
        "width_input": width_input,
        "height_input": height_input,
        "resize_btn": resize_btn,
        "tile_rects": tile_rects,
        "save_btn": save_btn,
        "load_btn": load_btn,
        "default_tile_rect": default_tile_rect,
        "apply_default_btn": apply_default_btn,
        "export_btn": export_btn
    }

# 获取鼠标对应的地图格子
def get_map_grid(pos, state):
    # 首先检查点击位置是否在地图区域内（左侧区域，右侧200px为控制面板）
    if pos[0] >= EDITOR_WIDTH - 200:
        return None
    
    scaled_tile_size = int(TILE_SIZE * state.zoom)
    x = (pos[0] - state.map_offset_x) // scaled_tile_size
    y = (pos[1] - state.map_offset_y) // scaled_tile_size
    
    if 0 <= x < state.map_width and 0 <= y < state.map_height:
        return x, y
    return None

# 保存地图为JSON
def save_map(state, filename):
    # 从文件名中提取地图名称（不含路径和扩展名）
    map_name = os.path.splitext(os.path.basename(filename))[0]
    state.map_name = map_name  # 更新state中的地图名称
    
    # 保存前将默认瓦片转换为0以优化存储
    optimized_tiles = []
    for row in state.map_data:
        optimized_row = []
        for tile in row:
            # 如果瓦片与默认瓦片相同，保存为0
            if tile == state.default_tile:
                optimized_row.append(0)
            else:
                optimized_row.append(tile)
        optimized_tiles.append(optimized_row)
    
    map_json = {
        "width": state.map_width,
        "height": state.map_height,
        "default_tile": state.default_tile,
        "tiles": optimized_tiles,
        "spawn_point": state.spawn_point,
        "switch_points": state.switch_points,
        "enable_encounter": state.enable_encounter
    }
    
    # 确保maps目录存在
    if not os.path.exists("maps"):
        os.makedirs("maps")
    
    # 创建美化的JSON结构
    json_lines = ['{']
    
    # 添加基本信息键值对，每个占一行
    json_lines.append(f'    "width": {state.map_width},')
    json_lines.append(f'    "height": {state.map_height},')
    json_lines.append(f'    "default_tile": {state.default_tile},')
    json_lines.append(f'    "enable_encounter": {str(state.enable_encounter).lower()},')
    
    # 处理tiles数组，确保同一行的数字不被换行
    json_lines.append('    "tiles": [')
    
    for row in optimized_tiles:
        # 将一行的数字转换为字符串，每个占4个字符位置，右对齐，不足时用空格补齐
        row_str = ', '.join(f"{tile:4}" for tile in row)
        json_lines.append(f'        [{row_str}],')
    
    # 移除最后一行的逗号
    if json_lines[-1].endswith(','):
        json_lines[-1] = json_lines[-1][:-1]
    
    json_lines.append('    ],')
    
    # 处理spawn_point
    spawn_str = ', '.join(str(pos) for pos in state.spawn_point)
    json_lines.append(f'    "spawn_point": [{spawn_str}],')
    
    # 处理switch_points
    switch_lines = []
    for switch_point in state.switch_points:
        switch_lines.append(f'        {json.dumps(switch_point, ensure_ascii=False)}')
    
    if switch_lines:
        json_lines.append('    "switch_points": [')
        for i, line in enumerate(switch_lines):
            if i < len(switch_lines) - 1:
                json_lines.append(f'{line},')
            else:
                json_lines.append(line)
        json_lines.append('    ]')
    else:
        json_lines.append('    "switch_points": []')
    
    # 关闭JSON对象
    json_lines.append('}')
    
    # 合并所有行
    beautified_json = '\n'.join(json_lines)
    
    file_path = os.path.join("maps", filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(beautified_json)
    
    # 更新窗口标题，包含地图名称和选中瓦片编号
    update_window_title(state)
    
    print(f"地图已保存到: {file_path}")

# 加载地图

def load_map(state, filename):
    # 从文件名中提取地图名称（不含路径和扩展名）
    map_name = os.path.splitext(os.path.basename(filename))[0]
    state.map_name = map_name  # 更新state中的地图名称
    
    file_path = os.path.join("maps", filename)
    if not os.path.exists(file_path):
        print(f"警告: 地图文件 {file_path} 不存在")
        return False
    
    with open(file_path, "r", encoding="utf-8") as f:
        map_json = json.load(f)
    
    state.map_width = map_json["width"]
    state.map_height = map_json["height"]
    state.default_tile = map_json.get("default_tile", TILE_FLOOR)
    
    # 加载时将0值恢复为默认瓦片
    loaded_tiles = map_json["tiles"]
    state.map_data = []
    for row in loaded_tiles:
        restored_row = []
        for tile in row:
            # 如果瓦片值为0，恢复为默认瓦片
            if tile == 0:
                restored_row.append(state.default_tile)
            else:
                restored_row.append(tile)
        state.map_data.append(restored_row)
    
    state.spawn_point = map_json.get("spawn_point", [0, 0])
    state.switch_points = map_json.get("switch_points", [])
    state.enable_encounter = map_json.get("enable_encounter", False)
    
    # 更新窗口标题，包含地图名称和选中瓦片编号
    update_window_title(state)
    
    print(f"地图已加载: {file_path}")
    return True

# 更新窗口标题
def update_window_title(state):
    """更新窗口标题，包含地图名称和选中瓦片编号"""
    pygame.display.set_caption(f"地图编辑器 - {state.map_name} | 选中瓦片: {state.selected_tile}")

# 导出地图为PNG图片
def export_map_image(state, filename=None):
    """
    将当前编辑的地图导出为完整的PNG图片
    """
    from datetime import datetime
    
    # 生成当前时间戳（格式：年月日时分）
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    
    # 默认文件名格式：地图名_时间戳.png
    default_filename = f"{state.map_name}_{timestamp}.png"
    
    # 打开文件保存对话框，让用户选择导出路径和文件名
    file_path = filedialog.asksaveasfilename(
        title="导出地图图片",
        initialdir=".",
        initialfile=default_filename,
        filetypes=[("PNG图片", "*.png"), ("所有文件", "*.*")],
        defaultextension=".png"
    )
    
    if not file_path:
        # 用户取消了导出
        return False
    
    # 创建与地图实际大小相同的Surface
    map_width_pixels = state.map_width * TILE_SIZE
    map_height_pixels = state.map_height * TILE_SIZE
    map_surface = pygame.Surface((map_width_pixels, map_height_pixels), pygame.SRCALPHA)
    
    # 遍历地图的每个瓦片，将对应的瓦片图片绘制到Surface上
    for y in range(state.map_height):
        for x in range(state.map_width):
            tile_type = state.map_data[y][x]
            if tile_type in tile_images:
                tile_image = tile_images[tile_type]
                map_surface.blit(tile_image, (x * TILE_SIZE, y * TILE_SIZE))
            else:
                # 如果找不到瓦片图片，绘制一个灰色占位符
                pygame.draw.rect(map_surface, (128, 128, 128), 
                               (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
    # 保存图片
    try:
        pygame.image.save(map_surface, file_path)
        print(f"地图图片已导出到: {file_path}")
        return True
    except Exception as e:
        print(f"导出地图图片失败: {e}")
        return False

# 主程序
def main():
    # 加载瓦片图片
    load_tile_images()
    
    # 初始化编辑器状态
    state = EditorState()
    
    # 设置初始窗口标题，包含地图名称和选中瓦片编号
    update_window_title(state)
    
    # 主循环
    running = True
    while running:
        screen.fill(WHITE)
        
        # 绘制地图
        draw_map(state, screen)
        
        # 绘制控制面板并获取UI元素信息
        ui_elements = draw_control_panel(state, screen)
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # 右键点击
                    # 检查是否点击了地图区域（非控制面板区域）
                    if event.pos[0] < EDITOR_WIDTH - 200:
                        # 获取右键点击的地图格子坐标
                        map_grid = get_map_grid(event.pos, state)
                        if map_grid:
                            state.right_click_coords = map_grid
                        else:
                            state.right_click_coords = None
                        # 右键点击地图区域，开始拖拽地图
                        state.is_dragging = True
                        state.drag_start_pos = event.pos
                        state.is_dragging_tiles = False  # 标记为拖拽地图
                        continue
                elif event.button == 1:  # 左键点击
                    scaled_tile_size = int(TILE_SIZE * state.zoom)
                    map_area_width = EDITOR_WIDTH - 200 - state.scrollbar_width
                    map_area_height = EDITOR_HEIGHT - state.scrollbar_height
                    map_actual_width = state.map_width * scaled_tile_size
                    map_actual_height = state.map_height * scaled_tile_size
                    
                    # 检查是否点击了水平滚动条
                    if map_actual_width > map_area_width:
                        hscroll_track = pygame.Rect(0, map_area_height, map_area_width, state.scrollbar_height)
                        hscroll_slider_width = max(20, int(map_area_width * map_area_width / map_actual_width))
                        hscroll_slider_x = int((state.map_offset_x / (map_actual_width - map_area_width)) * (map_area_width - hscroll_slider_width)) if map_actual_width > map_area_width else 0
                        hscroll_slider = pygame.Rect(hscroll_slider_x, map_area_height, hscroll_slider_width, state.scrollbar_height)
                        if hscroll_slider.collidepoint(event.pos):
                            state.is_dragging_hscroll = True
                            state.drag_start_pos = event.pos
                            state.is_dragging = True
                            state.is_dragging_scrollbar = True
                            continue
                    
                    # 检查是否点击了垂直滚动条
                    if map_actual_height > map_area_height:
                        vscroll_track = pygame.Rect(map_area_width, 0, state.scrollbar_width, map_area_height)
                        vscroll_slider_height = max(20, int(map_area_height * map_area_height / map_actual_height))
                        vscroll_slider_y = int((state.map_offset_y / (map_actual_height - map_area_height)) * (map_area_height - vscroll_slider_height)) if map_actual_height > map_area_height else 0
                        vscroll_slider = pygame.Rect(map_area_width, vscroll_slider_y, state.scrollbar_width, vscroll_slider_height)
                        if vscroll_slider.collidepoint(event.pos):
                            state.is_dragging_vscroll = True
                            state.drag_start_pos = event.pos
                            state.is_dragging = True
                            state.is_dragging_scrollbar = True
                            continue
                    
                    # 检查是否点击了地图
                    map_grid = get_map_grid(event.pos, state)
                    if map_grid:
                        state.is_dragging = True
                        state.drag_start_pos = event.pos
                        state.is_dragging_tiles = True  # 标记为拖拽瓦片
                        x, y = map_grid
                        state.map_data[y][x] = state.selected_tile
                        state.selected_tile_coords = (x, y)
                    else:
                        # 检查是否点击了控制面板区域（右侧200px）
                        if event.pos[0] < EDITOR_WIDTH - 200:
                            # 点击地图空白区域，开始拖拽地图
                            state.is_dragging = True
                            state.drag_start_pos = event.pos
                            state.is_dragging_tiles = False  # 标记为拖拽地图
                        else:
                            # 检查是否点击了瓦片选择器滚动条
                            scrollbar_handled = False
                            for tile_id, tile_rect in ui_elements["tile_rects"]:
                                if tile_id == 'tile_scrollbar_slider' and tile_rect.collidepoint(event.pos):
                                    state.is_dragging_tile_scrollbar = True
                                    state.is_dragging = True  # 设置为拖拽状态
                                    state.is_dragging_scrollbar = True  # 设置为拖拽滚动条
                                    state.drag_start_pos = event.pos
                                    scrollbar_handled = True
                                    break
                                elif isinstance(tile_id, int) and tile_rect.collidepoint(event.pos):
                                    state.selected_tile = tile_id
                                    # 更新窗口标题，显示选中的瓦片编号
                                    update_window_title(state)
                                    break
                            # 检查是否点击了默认瓦片显示区域
                            if "default_tile_rect" in ui_elements and ui_elements["default_tile_rect"].collidepoint(event.pos):
                                state.previous_default_tile = state.default_tile  # 保存旧的默认瓦片值
                                state.default_tile = state.selected_tile
                                print(f"默认瓦片已更新为: {state.default_tile}")
                            # 检查是否点击了应用默认瓦片按钮
                            if "apply_default_btn" in ui_elements and ui_elements["apply_default_btn"].collidepoint(event.pos):
                                # 将当前地图中所有等于旧默认瓦片的位置更新为新的默认瓦片
                                count_old = 0
                                for y in range(state.map_height):
                                    for x in range(state.map_width):
                                        if state.map_data[y][x] == state.previous_default_tile:
                                            state.map_data[y][x] = state.default_tile
                                            count_old += 1
                                
                                # 同时将所有值为0的位置也替换为默认瓦片（保持向后兼容）
                                count_zero = 0
                                for y in range(state.map_height):
                                    for x in range(state.map_width):
                                        if state.map_data[y][x] == 0:
                                            state.map_data[y][x] = state.default_tile
                                            count_zero += 1
                                
                                total_count = count_old + count_zero
                                print(f"已将默认瓦片应用到 {total_count} 个位置: {state.default_tile} (其中旧默认瓦片: {count_old}个, 0值瓦片: {count_zero}个)")
                            # 检查是否点击了宽度输入框
                            if ui_elements["width_input"].collidepoint(event.pos):
                                state.editing_width = True
                                state.editing_height = False
                                state.width_input_text = str(state.map_width)
                            # 检查是否点击了高度输入框
                            elif ui_elements["height_input"].collidepoint(event.pos):
                                state.editing_height = True
                                state.editing_width = False
                                state.height_input_text = str(state.map_height)
                            else:
                                # 点击其他地方退出编辑模式
                                state.editing_width = False
                                state.editing_height = False
                                
                            # 检查是否点击了调整地图尺寸按钮
                            if ui_elements["resize_btn"].collidepoint(event.pos):
                                # 重置编辑状态
                                state.editing_width = False
                                state.editing_height = False
                                try:
                                    # 从输入文本获取新尺寸
                                    new_width = int(state.width_input_text) if state.width_input_text else state.map_width
                                    new_height = int(state.height_input_text) if state.height_input_text else state.map_height
                                    if state.resize_map(new_width, new_height):
                                        print(f"地图尺寸已调整为: {new_width}x{new_height}")
                                        # 更新输入框文本为新的地图尺寸
                                        state.width_input_text = str(new_width)
                                        state.height_input_text = str(new_height)
                                    else:
                                        print("地图尺寸调整失败: 尺寸必须大于0")
                                except ValueError:
                                    print("地图尺寸调整失败: 请输入有效的数字")
                                except Exception as e:
                                    print(f"调整地图尺寸失败: {e}")
                            # 检查是否点击了保存按钮
                            if ui_elements["save_btn"].collidepoint(event.pos):
                                # 打开文件保存对话框
                                file_path = filedialog.asksaveasfilename(
                                    title="保存地图文件",
                                    initialdir="maps",
                                    initialfile="新地图",
                                    filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                                    defaultextension=".json"
                                )
                                if file_path:
                                    # 提取文件名（不含路径和扩展名）
                                    map_name = os.path.splitext(os.path.basename(file_path))[0]
                                    save_map(state, f"{map_name}.json")
                            # 检查是否点击了导出按钮
                            if ui_elements["export_btn"].collidepoint(event.pos):
                                export_map_image(state)
                                continue
                            # 检查是否点击了加载按钮
                            if ui_elements["load_btn"].collidepoint(event.pos):
                                # 打开文件选择对话框
                                file_path = filedialog.askopenfilename(
                                    title="选择地图文件",
                                    initialdir="maps",
                                    filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
                                )
                                if file_path:
                                    # 提取文件名（不含路径和扩展名）
                                    map_name = os.path.splitext(os.path.basename(file_path))[0]
                                    load_map(state, f"{map_name}.json")
                elif event.button == 3:  # 右键点击
                    # 检查是否点击了地图区域（非控制面板区域）
                    if event.pos[0] < EDITOR_WIDTH - 200:
                        # 右键点击地图区域，开始拖拽地图
                        state.is_dragging = True
                        state.drag_start_pos = event.pos
                        state.is_dragging_tiles = False  # 标记为拖拽地图
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 or event.button == 3:
                    state.is_dragging = False
                    state.is_dragging_tiles = False
                    state.is_dragging_scrollbar = False
                    state.is_dragging_hscroll = False
                    state.is_dragging_vscroll = False
                    state.is_dragging_tile_scrollbar = False
                    state.drag_start_pos = None
            elif event.type == pygame.KEYDOWN:
                # 处理文本输入
                if state.editing_width:
                    if event.key == pygame.K_RETURN:
                        # 回车键确认输入
                        try:
                            new_width = int(state.width_input_text)
                            if state.resize_map(new_width, state.map_height):
                                print(f"地图宽度已调整为: {new_width}")
                                # 更新输入框文本为新的地图尺寸
                                state.width_input_text = str(new_width)
                        except ValueError:
                            print("宽度输入无效，请输入数字")
                        state.editing_width = False
                    elif event.key == pygame.K_BACKSPACE:
                        # 删除键
                        state.width_input_text = state.width_input_text[:-1]
                    else:
                        # 只允许输入数字
                        key_char = event.unicode
                        if key_char.isdigit():
                            state.width_input_text += key_char
                elif state.editing_height:
                    if event.key == pygame.K_RETURN:
                        # 回车键确认输入
                        try:
                            new_height = int(state.height_input_text)
                            if state.resize_map(state.map_width, new_height):
                                print(f"地图高度已调整为: {new_height}")
                                # 更新输入框文本为新的地图尺寸
                                state.height_input_text = str(new_height)
                        except ValueError:
                            print("高度输入无效，请输入数字")
                        state.editing_height = False
                    elif event.key == pygame.K_BACKSPACE:
                        # 删除键
                        state.height_input_text = state.height_input_text[:-1]
                    else:
                        # 只允许输入数字
                        key_char = event.unicode
                        if key_char.isdigit():
                            state.height_input_text += key_char
            elif event.type == pygame.MOUSEMOTION:
                if state.is_dragging:
                    if state.is_dragging_tile_scrollbar:
                        # 拖拽瓦片选择器滚动条
                        dy = event.pos[1] - state.drag_start_pos[1]
                        state.drag_start_pos = event.pos
                        
                        # 计算瓦片网格信息
                        sorted_tiles = sorted(tile_images.keys())
                        total_tiles = len(sorted_tiles)
                        tiles_per_row = 4
                        total_rows = (total_tiles + tiles_per_row - 1) // tiles_per_row
                        total_height = total_rows * (TILE_SIZE + 5)
                        container_height = state.tile_selector_visible_height
                        
                        if total_height > container_height:
                            # 计算滑块移动范围
                            scrollbar_height = container_height
                            slider_height = max(20, int(container_height * container_height / total_height))
                            total_scroll_range = scrollbar_height - slider_height
                            
                            if total_scroll_range > 0:
                                # 将滑块移动距离转换为瓦片选择器偏移量
                                tile_range = total_height - container_height
                                state.tile_selector_offset_y += (dy / total_scroll_range) * tile_range
                                
                                # 限制偏移在有效范围内
                                state.tile_selector_offset_y = max(0, min(state.tile_selector_offset_y, tile_range))
                    elif state.is_dragging_scrollbar:
                        # 拖拽滚动条
                        scaled_tile_size = int(TILE_SIZE * state.zoom)
                        map_area_width = EDITOR_WIDTH - 200 - state.scrollbar_width
                        map_area_height = EDITOR_HEIGHT - state.scrollbar_height
                        map_actual_width = state.map_width * scaled_tile_size
                        map_actual_height = state.map_height * scaled_tile_size
                        
                        if state.is_dragging_hscroll and map_actual_width > map_area_width:
                            # 拖拽水平滚动条
                            dx = event.pos[0] - state.drag_start_pos[0]
                            state.drag_start_pos = event.pos
                            
                            hscroll_slider_width = max(20, int(map_area_width * map_area_width / map_actual_width))
                            total_scroll_range = map_area_width - hscroll_slider_width
                            
                            if total_scroll_range > 0:
                                map_range = map_actual_width - map_area_width
                                # 计算滑块当前位置
                                current_slider_x = int((abs(state.map_offset_x) / map_range) * total_scroll_range)
                                # 更新滑块位置
                                new_slider_x = current_slider_x + dx
                                # 限制滑块位置
                                new_slider_x = max(0, min(new_slider_x, total_scroll_range))
                                # 计算新的地图偏移量
                                state.map_offset_x = -((new_slider_x / total_scroll_range) * map_range)
                                
                                # 限制地图偏移在有效范围内
                                state.map_offset_x = max(-map_range, min(0, state.map_offset_x))
                        
                        elif state.is_dragging_vscroll and map_actual_height > map_area_height:
                            # 拖拽垂直滚动条
                            dy = event.pos[1] - state.drag_start_pos[1]
                            state.drag_start_pos = event.pos
                            
                            vscroll_slider_height = max(20, int(map_area_height * map_area_height / map_actual_height))
                            total_scroll_range = map_area_height - vscroll_slider_height
                            
                            if total_scroll_range > 0:
                                map_range = map_actual_height - map_area_height
                                # 计算滑块当前位置
                                current_slider_y = int((abs(state.map_offset_y) / map_range) * total_scroll_range)
                                # 更新滑块位置
                                new_slider_y = current_slider_y + dy
                                # 限制滑块位置
                                new_slider_y = max(0, min(new_slider_y, total_scroll_range))
                                # 计算新的地图偏移量
                                state.map_offset_y = -((new_slider_y / total_scroll_range) * map_range)
                                
                                # 限制地图偏移在有效范围内
                                state.map_offset_y = max(-map_range, min(0, state.map_offset_y))
                    
                    elif state.is_dragging_tiles:
                        # 拖拽瓦片
                        map_grid = get_map_grid(event.pos, state)
                        if map_grid:
                            x, y = map_grid
                            state.map_data[y][x] = state.selected_tile
                            state.selected_tile_coords = (x, y)
                    else:
                        # 拖拽地图
                        if state.drag_start_pos:
                            dx = event.pos[0] - state.drag_start_pos[0]
                            dy = event.pos[1] - state.drag_start_pos[1]
                            state.map_offset_x += dx
                            state.map_offset_y += dy
                            state.drag_start_pos = event.pos
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # 保存地图
                    map_name = input("请输入地图名称: ")
                    if map_name:
                        save_map(state, f"{map_name}.json")
                elif event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # 加载地图
                    map_name = input("请输入地图名称: ")
                    if map_name:
                        load_map(state, f"{map_name}.json")
        
        # 更新窗口标题（确保信息最新）
        update_window_title(state)
        # 更新显示
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()