import pygame
import sys
import os
from tkinter import Tk, filedialog

# 初始化pygame
pygame.init()

# 窗口设置
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("像素图片编辑器")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 字体设置
FONT = pygame.font.SysFont("Microsoft YaHei", 16)
SMALL_FONT = pygame.font.SysFont("Microsoft YaHei", 14)

# 编辑器状态类
class EditorState:
    def __init__(self):
        self.image = None
        self.image_surface = None
        self.image_path = None
        self.zoom = 10  # 默认放大倍数
        self.cached_scaled_image = None  # 缓存的缩放后的图像
        self.last_zoom = 0  # 上一次的缩放倍数
        self.offset_x = 50
        self.offset_y = 50
        self.selected_color = BLACK
        self.is_dragging = False  # 左键拖拽
        self.is_right_dragging = False  # 右键拖拽
        self.drag_start_pos = None
        self.is_painting = False
        self.erase_mode = False
        self.picker_mode = True  # 取色器模式开关
        self.color_picker_rect = pygame.Rect(WINDOW_WIDTH - 210, 10, 200, 80)
        self.color_preview_rect = pygame.Rect(WINDOW_WIDTH - 180, 150, 140, 30)
        self.color_inputs = {
            'r': pygame.Rect(WINDOW_WIDTH - 180, 190, 50, 24),
            'g': pygame.Rect(WINDOW_WIDTH - 120, 190, 50, 24),
            'b': pygame.Rect(WINDOW_WIDTH - 60, 190, 50, 24)
        }
        self.color_values = {'r': 0, 'g': 0, 'b': 0}
        self.editing_color = None
        self.current_pixel_pos = (-1, -1)  # 当前鼠标指向的像素坐标
        
        # 选择区域相关状态
        self.selection_mode = False  # 选择模式开关
        self.selection_start = None  # 选择区域起始像素坐标
        self.selection_end = None  # 选择区域结束像素坐标
        self.is_selecting = False  # 是否正在选择区域
        self.is_moving_selection = False  # 是否正在移动选中区域
        self.move_start_pos = None  # 移动起始位置（屏幕坐标）
        
        # 复制区域相关状态
        self.copied_surface = None  # 复制的像素表面
        
        # 复制成功提示相关状态
        self.copy_notification = False  # 是否显示复制成功提示
        self.copy_notification_text = ""  # 提示文本
        self.copy_notification_timer = 0  # 提示显示计时器（帧数）

# 颜色选择器
def draw_color_picker(state):
    # 绘制颜色选择器背景
    pygame.draw.rect(SCREEN, GRAY, state.color_picker_rect)
    pygame.draw.rect(SCREEN, BLACK, state.color_picker_rect, 2)
    
    # 绘制标题
    title = SMALL_FONT.render("颜色选择器", True, BLACK)
    SCREEN.blit(title, (state.color_picker_rect.x + 5, state.color_picker_rect.y + 5))
    
    # 绘制基本颜色
    colors = [
        BLACK, WHITE, RED, GREEN, BLUE,
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (255, 165, 0), (128, 0, 128), (0, 128, 0),
        (0, 0, 128), (128, 128, 0), (128, 0, 128)
    ]
    
    start_x = state.color_picker_rect.x + 10
    start_y = state.color_picker_rect.y + 30
    color_size = 20
    padding = 5
    
    # 存储颜色按钮信息，供事件系统使用
    state.color_buttons = []
    
    for i, color in enumerate(colors):
        x = start_x + (i % 7) * (color_size + padding)
        y = start_y + (i // 7) * (color_size + padding)
        rect = pygame.Rect(x, y, color_size, color_size)
        pygame.draw.rect(SCREEN, color, rect)
        pygame.draw.rect(SCREEN, BLACK, rect, 1)
        
        # 存储颜色按钮信息
        state.color_buttons.append((rect, color))
    
    # 绘制当前颜色预览
    pygame.draw.rect(SCREEN, state.selected_color, state.color_preview_rect)
    pygame.draw.rect(SCREEN, BLACK, state.color_preview_rect, 2)
    
    # 绘制RGB输入框
    for channel, rect in state.color_inputs.items():
        pygame.draw.rect(SCREEN, WHITE, rect)
        pygame.draw.rect(SCREEN, BLACK, rect, 2)
        text = SMALL_FONT.render(str(state.color_values[channel]), True, BLACK)
        SCREEN.blit(text, (rect.x + 5, rect.y + 3))
    
    # 绘制RGB标签
    labels = ['R:', 'G:', 'B:']
    x_positions = [state.color_inputs['r'].x - 30, state.color_inputs['g'].x - 30, state.color_inputs['b'].x - 30]
    for i, label in enumerate(labels):
        text = SMALL_FONT.render(label, True, BLACK)
        SCREEN.blit(text, (x_positions[i], state.color_inputs['r'].y + 3))

# 绘制工具栏
def draw_toolbar(state):
    # 绘制工具栏背景
    toolbar_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 40)
    pygame.draw.rect(SCREEN, LIGHT_GRAY, toolbar_rect)
    pygame.draw.rect(SCREEN, BLACK, toolbar_rect, 1)
    
    # 绘制按钮（顶部水平排列）
    buttons = [
        ("新建图片", 60, 30, None),
        ("加载图片", 60, 30, None),
        ("保存图片", 60, 30, None),
        ("放大", 60, 30, None),
        ("缩小", 60, 30, None),
        ("橡皮擦", 60, 30, state.erase_mode),
        ("铅笔", 60, 30, not (state.erase_mode or state.picker_mode or state.selection_mode)),
        ("取色器", 60, 30, state.picker_mode),
        ("移动区域", 60, 30, state.selection_mode),
        ("导入图片", 60, 30, None)
    ]
    
    # 按钮位置设置：顶部水平排列
    start_x = 10  # 左侧边距10像素
    button_y = 5  # 顶部边距5像素
    button_spacing = 5  # 按钮间距5像素
    
    for i, (text, width, height, is_active) in enumerate(buttons):
        button_x = start_x + i * (width + button_spacing)
        rect = pygame.Rect(button_x, button_y, width, height)
        
        # 根据是否激活选择按钮颜色
        if is_active:
            button_color = GREEN  # 激活状态使用绿色
        else:
            button_color = WHITE  # 非激活状态使用白色
        
        pygame.draw.rect(SCREEN, button_color, rect)
        pygame.draw.rect(SCREEN, BLACK, rect, 1)
        button_text = SMALL_FONT.render(text, True, BLACK)
        SCREEN.blit(button_text, (rect.x + 5, rect.y + 3))
        
        # 返回按钮位置
        if i == 0:  # 新建图片
            state.new_button = rect
        elif i == 1:  # 加载图片
            state.load_button = rect
        elif i == 2:  # 保存图片
            state.save_button = rect
        elif i == 3:  # 放大
            state.zoom_in_button = rect
        elif i == 4:  # 缩小
            state.zoom_out_button = rect
        elif i == 5:  # 橡皮擦
            state.erase_button = rect
        elif i == 6:  # 铅笔
            state.pencil_button = rect
        elif i == 7:  # 取色器
            state.picker_button = rect
        elif i == 8:  # 移动区域
            state.move_area_button = rect
        elif i == 9:  # 导入图片
            state.import_button = rect

# 处理颜色输入
def handle_color_inputs(state, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        for channel, rect in state.color_inputs.items():
            if rect.collidepoint(event.pos):
                state.editing_color = channel
                return
        state.editing_color = None
    
    elif event.type == pygame.KEYDOWN and state.editing_color:
        channel = state.editing_color
        if event.key == pygame.K_RETURN:
            state.editing_color = None
        elif event.key == pygame.K_BACKSPACE:
            state.color_values[channel] = 0
        elif event.unicode.isdigit():
            new_value = int(str(state.color_values[channel]) + event.unicode) if str(state.color_values[channel]) != "0" else int(event.unicode)
            state.color_values[channel] = min(new_value, 255)
        
        # 更新颜色
        state.selected_color = (state.color_values['r'], state.color_values['g'], state.color_values['b'])

# 新建图片
def new_image(state):
    if state.copied_surface is not None:
        # 如果有复制的区域，使用复制区域的大小和内容创建新图片
        state.image_surface = state.copied_surface.copy()
        print(f"基于复制区域创建了一个 {state.image_surface.get_width()}x{state.image_surface.get_height()} 的新图片")
    else:
        # 没有复制区域时，创建默认大小的透明图像
        state.image_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        state.image_surface.fill((0, 0, 0, 0))
    
    state.image_path = None  # 新图像没有文件路径
    state.offset_x = 50
    state.offset_y = 50
    state.zoom = 10
    # 重置选择区域
    state.selection_start = None
    state.selection_end = None
    # 清除缓存
    state.cached_scaled_image = None

# 加载图片
def load_image(state):
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="选择图片",
        filetypes=[("PNG图片", "*.png"), ("JPG图片", "*.jpg"), ("BMP图片", "*.bmp"), ("所有文件", "*.*")]
    )
    root.destroy()  # 销毁Tk实例，避免第二次调用失败
    
    if file_path:
        state.image_path = file_path
        state.image = pygame.image.load(file_path).convert_alpha()
        state.image_surface = state.image.copy()
        state.offset_x = 50
        state.offset_y = 50
        state.zoom = 10

# 导入图片到当前图片的右边最上方
def import_image(state):
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="选择要导入的图片",
        filetypes=[("PNG图片", "*.png"), ("JPG图片", "*.jpg"), ("BMP图片", "*.bmp"), ("所有文件", "*.*")]
    )
    root.destroy()  # 销毁Tk实例，避免第二次调用失败
    
    if file_path:
        # 加载新图片
        new_image = pygame.image.load(file_path).convert_alpha()
        
        if state.image_surface is None:
            # 如果当前没有图片，直接加载新图片
            state.image_path = file_path
            state.image_surface = new_image.copy()
            state.offset_x = 50
            state.offset_y = 50
            state.zoom = 10
        else:
            # 计算新的图片尺寸
            current_width = state.image_surface.get_width()
            current_height = state.image_surface.get_height()
            new_width = new_image.get_width()
            new_height = new_image.get_height()
            
            # 新图片的宽度是当前图片宽度加上新图片宽度
            new_surface_width = current_width + new_width
            # 新图片的高度是当前图片高度和新图片高度中的较大值
            new_surface_height = max(current_height, new_height)
            
            # 创建新的更大的表面
            new_surface = pygame.Surface((new_surface_width, new_surface_height), pygame.SRCALPHA)
            new_surface.fill((0, 0, 0, 0))  # 填充透明背景
            
            # 将当前图片复制到新表面的左上角
            new_surface.blit(state.image_surface, (0, 0))
            
            # 将新导入的图片复制到当前图片的右边最上方
            new_surface.blit(new_image, (current_width, 0))
            
            # 更新状态
            state.image_surface = new_surface
            state.image_path = None  # 合并后的图片没有原始文件路径
            state.cached_scaled_image = None  # 清除缓存

# 保存图片
def save_image(state):
    if state.image_surface:
        root = Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            title="保存图片",
            filetypes=[("PNG图片", "*.png"), ("JPG图片", "*.jpg"), ("BMP图片", "*.bmp")],
            defaultextension=".png"
        )
        root.destroy()  # 销毁Tk实例，避免第二次调用失败
        
        if file_path:
            pygame.image.save(state.image_surface, file_path)
            state.image_path = file_path  # 更新图片路径，用于在标题中显示文件名

# 绘制图片
def draw_image(state):
    if state.image_surface:
        # 检查是否需要重新缩放图像（缩放倍数改变或缓存不存在）
        if state.cached_scaled_image is None or state.last_zoom != state.zoom:
            # 绘制放大后的图片
            scaled_width = state.image_surface.get_width() * state.zoom
            scaled_height = state.image_surface.get_height() * state.zoom
            state.cached_scaled_image = pygame.transform.scale(state.image_surface, (scaled_width, scaled_height))
            
            # 在缓存图像上绘制像素网格（如果需要）
            if state.zoom >= 2:
                for x in range(state.image_surface.get_width() + 1):
                    pygame.draw.line(state.cached_scaled_image, DARK_GRAY, 
                                    (x * state.zoom, 0), 
                                    (x * state.zoom, scaled_height), 1)
                for y in range(state.image_surface.get_height() + 1):
                    pygame.draw.line(state.cached_scaled_image, DARK_GRAY, 
                                    (0, y * state.zoom), 
                                    (scaled_width, y * state.zoom), 1)
            
            # 为透明像素绘制特殊效果：对角线分割的三角形
            if state.zoom >= 2:
                for x in range(state.image_surface.get_width()):
                    for y in range(state.image_surface.get_height()):
                        # 获取原始像素颜色
                        color = state.image_surface.get_at((x, y))
                        # 检查是否是完全透明的像素
                        if color[3] == 0:  # alpha通道为0
                            # 计算缩放后的像素位置和大小
                            scaled_x = x * state.zoom
                            scaled_y = y * state.zoom
                            zoom_size = state.zoom
                            
                            # 绘制对角线分割的两个三角形
                            # 第一个三角形：白色
                            points1 = [(scaled_x, scaled_y), 
                                     (scaled_x + zoom_size, scaled_y), 
                                     (scaled_x, scaled_y + zoom_size)]
                            pygame.draw.polygon(state.cached_scaled_image, WHITE, points1)
                            
                            # 第二个三角形：灰色
                            points2 = [(scaled_x + zoom_size, scaled_y), 
                                     (scaled_x + zoom_size, scaled_y + zoom_size), 
                                     (scaled_x, scaled_y + zoom_size)]
                            pygame.draw.polygon(state.cached_scaled_image, GRAY, points2)
            
            state.last_zoom = state.zoom  # 更新上一次缩放倍数
        
        # 使用缓存的缩放图像（包含网格）
        SCREEN.blit(state.cached_scaled_image, (state.offset_x, state.offset_y))

# 绘制选择区域
def draw_selection(state):
    if state.selection_mode and state.image_surface:
        # 正在选择区域
        if state.is_selecting and state.selection_start:
            # 计算当前鼠标对应的像素坐标
            mouse_x, mouse_y = pygame.mouse.get_pos()
            pixel_x = (mouse_x - state.offset_x) // state.zoom
            pixel_y = (mouse_y - state.offset_y) // state.zoom
            
            # 确保像素坐标在图片范围内
            pixel_x = max(0, min(pixel_x, state.image_surface.get_width() - 1))
            pixel_y = max(0, min(pixel_y, state.image_surface.get_height() - 1))
            
            # 计算选择区域的矩形
            x1, y1 = state.selection_start
            x2, y2 = pixel_x, pixel_y
            start_x = min(x1, x2) * state.zoom + state.offset_x
            start_y = min(y1, y2) * state.zoom + state.offset_y
            width = abs(x2 - x1 + 1) * state.zoom
            height = abs(y2 - y1 + 1) * state.zoom
            
            # 绘制选择区域的透明覆盖层
            selection_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            selection_surface.fill((0, 128, 255, 64))  # 半透明蓝色
            SCREEN.blit(selection_surface, (start_x, start_y))
            
            # 绘制选择区域的边框
            pygame.draw.rect(SCREEN, (0, 255, 0), (start_x, start_y, width, height), 2)
        
        # 已选择区域
        elif state.selection_start and state.selection_end:
            x1, y1 = state.selection_start
            x2, y2 = state.selection_end
            start_x = min(x1, x2) * state.zoom + state.offset_x
            start_y = min(y1, y2) * state.zoom + state.offset_y
            width = abs(x2 - x1 + 1) * state.zoom
            height = abs(y2 - y1 + 1) * state.zoom
            
            # 绘制选择区域的透明覆盖层
            selection_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            selection_surface.fill((0, 128, 255, 64))  # 半透明蓝色
            SCREEN.blit(selection_surface, (start_x, start_y))
            
            # 绘制选择区域的边框
            pygame.draw.rect(SCREEN, (0, 255, 0), (start_x, start_y, width, height), 2)

# 主程序
def main():
    state = EditorState()
    clock = pygame.time.Clock()  # 创建时钟对象控制帧率
    
    running = True
    while running:
        SCREEN.fill(WHITE)
        
        # 绘制图片（底层）
        draw_image(state)
        
        # 绘制选择区域（在图片上方）
        draw_selection(state)
        
        # 绘制工具栏（中间层，在图片上方）
        draw_toolbar(state)
        
        # 绘制颜色选择器（顶层，在所有元素上方）
        draw_color_picker(state)
        
        # 绘制复制成功提示
        if state.copy_notification:
            # 创建提示文本
            notification_text = FONT.render(state.copy_notification_text, True, WHITE)
            text_rect = notification_text.get_rect()
            
            # 设置提示位置（屏幕中央偏上）
            rect_width = text_rect.width + 40
            rect_height = text_rect.height + 20
            rect = pygame.Rect((WINDOW_WIDTH - rect_width) // 2, 50, rect_width, rect_height)
            
            # 绘制提示背景
            pygame.draw.rect(SCREEN, (0, 0, 0), rect)
            pygame.draw.rect(SCREEN, (0, 255, 0), rect, 2)
            
            # 绘制提示文本
            text_x = rect.x + (rect_width - text_rect.width) // 2
            text_y = rect.y + (rect_height - text_rect.height) // 2
            SCREEN.blit(notification_text, (text_x, text_y))
            
            # 更新计时器
            state.copy_notification_timer -= 1
            if state.copy_notification_timer <= 0:
                state.copy_notification = False
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 处理颜色输入
            handle_color_inputs(state, event)
            
            # 键盘事件
            if event.type == pygame.KEYDOWN:
                # 处理复制功能 (Ctrl+C)
                if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if state.image_surface and state.selection_mode and state.selection_start and state.selection_end:
                        # 获取选择区域的边界
                        x1, y1 = state.selection_start
                        x2, y2 = state.selection_end
                        start_x = min(x1, x2)
                        start_y = min(y1, y2)
                        end_x = max(x1, x2)
                        end_y = max(y1, y2)
                        
                        # 计算选择区域的大小
                        width = end_x - start_x + 1
                        height = end_y - start_y + 1
                        
                        # 创建新的表面来存储复制的像素数据（支持透明）
                        state.copied_surface = pygame.Surface((width, height), pygame.SRCALPHA)
                        
                        # 复制选择区域的像素数据到新表面
                        state.copied_surface.blit(state.image_surface, (0, 0), (start_x, start_y, width, height))
                        
                        # 设置复制成功提示
                        state.copy_notification = True
                        state.copy_notification_text = f"已复制 {width}x{height} 的区域"
                        state.copy_notification_timer = 60  # 显示1秒（60帧）
                        
                        print(f"复制了一个 {width}x{height} 的区域")
                
                # 处理粘贴功能 (Ctrl+V)
                elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if state.image_surface and state.copied_surface is not None and state.selection_mode and state.selection_start:
                        # 获取选择区域的左上角坐标
                        x1, y1 = state.selection_start
                        x2, y2 = state.selection_end
                        start_x = min(x1, x2)
                        start_y = min(y1, y2)
                        
                        # 粘贴复制的内容到选择区域的左上角
                        state.image_surface.blit(state.copied_surface, (start_x, start_y))
                        state.cached_scaled_image = None  # 清除缓存
                        
                        print(f"已粘贴 {state.copied_surface.get_width()}x{state.copied_surface.get_height()} 的区域")
                
                # 处理删除选中区域功能 (Del键)
                elif event.key == pygame.K_DELETE:
                    if state.image_surface and state.selection_mode and state.selection_start and state.selection_end:
                        # 获取选择区域的边界
                        x1, y1 = state.selection_start
                        x2, y2 = state.selection_end
                        start_x = min(x1, x2)
                        start_y = min(y1, y2)
                        end_x = max(x1, x2)
                        end_y = max(y1, y2)
                        
                        # 清除选择区域的像素（填充透明）
                        transparent_rect = pygame.Rect(start_x, start_y, end_x - start_x + 1, end_y - start_y + 1)
                        pygame.draw.rect(state.image_surface, (0, 0, 0, 0), transparent_rect)
                        state.cached_scaled_image = None  # 清除缓存
                        
                        # 重置选择区域
                        state.selection_start = None
                        state.selection_end = None
                        
                        print(f"已删除 {end_x - start_x + 1}x{end_y - start_y + 1} 的区域")
                
                elif state.image_surface and state.selection_mode and state.selection_start and state.selection_end:
                    # 获取选择区域的边界
                    x1, y1 = state.selection_start
                    x2, y2 = state.selection_end
                    start_x = min(x1, x2)
                    start_y = min(y1, y2)
                    end_x = max(x1, x2)
                    end_y = max(y1, y2)
                    
                    # 计算移动的方向
                    dx = 0
                    dy = 0
                    if event.key == pygame.K_LEFT:
                        dx = -1
                    elif event.key == pygame.K_RIGHT:
                        dx = 1
                    elif event.key == pygame.K_UP:
                        dy = -1
                    elif event.key == pygame.K_DOWN:
                        dy = 1
                    
                    # 如果有移动方向
                    if dx != 0 or dy != 0:
                        # 计算新的选择区域边界
                        new_start_x = max(0, min(start_x + dx, state.image_surface.get_width() - 1))
                        new_start_y = max(0, min(start_y + dy, state.image_surface.get_height() - 1))
                        new_end_x = max(0, min(end_x + dx, state.image_surface.get_width() - 1))
                        new_end_y = max(0, min(end_y + dy, state.image_surface.get_height() - 1))
                        
                        # 计算实际移动的距离
                        actual_dx = new_start_x - start_x
                        actual_dy = new_start_y - start_y
                        
                        # 如果有实际移动
                        if actual_dx != 0 or actual_dy != 0:
                            # 创建临时表面来存储选择区域的像素数据（支持透明）
                            temp_surface = pygame.Surface((end_x - start_x + 1, end_y - start_y + 1), pygame.SRCALPHA)
                            
                            # 使用blit复制选择区域的像素数据到临时表面
                            temp_surface.blit(state.image_surface, (0, 0), (start_x, start_y, end_x - start_x + 1, end_y - start_y + 1))
                            
                            # 清除原选择区域的像素（填充透明）
                            transparent_rect = pygame.Rect(start_x, start_y, end_x - start_x + 1, end_y - start_y + 1)
                            pygame.draw.rect(state.image_surface, (0, 0, 0, 0), transparent_rect)
                            
                            # 使用blit将临时表面的像素数据复制到新位置
                            state.image_surface.blit(temp_surface, (new_start_x, new_start_y))
                            
                            state.cached_scaled_image = None  # 清除缓存（一次即可）
                            
                            # 更新选择区域的坐标
                            state.selection_start = (new_start_x, new_start_y)
                            state.selection_end = (new_end_x, new_end_y)
            
            # 鼠标事件
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 标记是否点击了按钮
                button_clicked = False
                
                # 处理工具栏按钮点击
                if hasattr(state, 'new_button') and state.new_button.collidepoint(event.pos):
                    new_image(state)
                    button_clicked = True
                elif hasattr(state, 'load_button') and state.load_button.collidepoint(event.pos):
                    load_image(state)
                    button_clicked = True
                elif hasattr(state, 'import_button') and state.import_button.collidepoint(event.pos):
                    import_image(state)
                    button_clicked = True
                elif hasattr(state, 'save_button') and state.save_button.collidepoint(event.pos):
                    save_image(state)
                    button_clicked = True
                elif hasattr(state, 'zoom_in_button') and state.zoom_in_button.collidepoint(event.pos):
                    state.zoom = min(state.zoom + 1, 20)
                    button_clicked = True
                elif hasattr(state, 'zoom_out_button') and state.zoom_out_button.collidepoint(event.pos):
                    state.zoom = max(state.zoom - 1, 1)
                    button_clicked = True
                elif hasattr(state, 'erase_button') and state.erase_button.collidepoint(event.pos):
                    state.erase_mode = True
                    state.picker_mode = False  # 点击橡皮擦时禁用取色器
                    state.selection_mode = False  # 点击橡皮擦时禁用选择模式
                    button_clicked = True
                elif hasattr(state, 'pencil_button') and state.pencil_button.collidepoint(event.pos):
                    state.erase_mode = False
                    state.picker_mode = False  # 点击铅笔时禁用取色器
                    state.selection_mode = False  # 点击铅笔时禁用选择模式
                    button_clicked = True
                elif hasattr(state, 'picker_button') and state.picker_button.collidepoint(event.pos):
                    state.picker_mode = not state.picker_mode  # 切换取色器模式
                    state.erase_mode = False  # 启用取色器时禁用橡皮擦
                    state.selection_mode = False  # 点击取色器时禁用选择模式
                    button_clicked = True
                elif hasattr(state, 'move_area_button') and state.move_area_button.collidepoint(event.pos):
                    state.selection_mode = not state.selection_mode  # 切换选择模式
                    # 切换选择模式时禁用其他模式
                    state.erase_mode = False
                    state.picker_mode = False
                    # 如果关闭选择模式，清除选择区域
                    if not state.selection_mode:
                        state.selection_start = None
                        state.selection_end = None
                    button_clicked = True
                
                # 处理颜色选择器按钮点击
                color_selected = False
                if hasattr(state, 'color_buttons'):
                    for rect, color in state.color_buttons:
                        if rect.collidepoint(event.pos):
                            state.selected_color = color
                            # 处理3元组(RGB)和4元组(RGBA)颜色
                            if len(color) == 4:
                                r, g, b, _ = color
                            else:
                                r, g, b = color
                            state.color_values = {'r': r, 'g': g, 'b': b}
                            color_selected = True
                            button_clicked = True
                            break
                    if color_selected:
                        continue
                
                # 如果点击了按钮，跳过后续的绘画/擦除逻辑
                if button_clicked:
                    continue
                
                # 处理左键点击
                if event.button == 1:  # 左键
                    if state.selection_mode:
                        # 选择模式下的左键操作
                        if state.image_surface and state.offset_x <= event.pos[0] <= state.offset_x + state.image_surface.get_width() * state.zoom and \
                             state.offset_y <= event.pos[1] <= state.offset_y + state.image_surface.get_height() * state.zoom:
                            # 计算像素位置
                            pixel_x = (event.pos[0] - state.offset_x) // state.zoom
                            pixel_y = (event.pos[1] - state.offset_y) // state.zoom
                            
                            # 检查是否在图片范围内
                            if 0 <= pixel_x < state.image_surface.get_width() and 0 <= pixel_y < state.image_surface.get_height():
                                # 检查是否点击了已选择的区域
                                if state.selection_start and state.selection_end:
                                    x1, y1 = state.selection_start
                                    x2, y2 = state.selection_end
                                    if min(x1, x2) <= pixel_x <= max(x1, x2) and min(y1, y2) <= pixel_y <= max(y1, y2):
                                        # 开始移动选择区域
                                        state.is_moving_selection = True
                                        state.move_start_pos = (pixel_x, pixel_y)
                                        continue
                                
                                # 开始选择新区域
                                state.is_selecting = True
                                state.selection_start = (pixel_x, pixel_y)
                                state.selection_end = None
                    else:
                        # 非选择模式下的左键操作
                        if state.image_surface and state.offset_x <= event.pos[0] <= state.offset_x + state.image_surface.get_width() * state.zoom and \
                             state.offset_y <= event.pos[1] <= state.offset_y + state.image_surface.get_height() * state.zoom:
                            # 计算像素位置
                            pixel_x = (event.pos[0] - state.offset_x) // state.zoom
                            pixel_y = (event.pos[1] - state.offset_y) // state.zoom
                            
                            # 检查是否在图片范围内
                            if 0 <= pixel_x < state.image_surface.get_width() and 0 <= pixel_y < state.image_surface.get_height():
                                # 取色器功能：只在取色器模式下获取点击位置的像素颜色
                                if state.picker_mode:
                                    color = state.image_surface.get_at((pixel_x, pixel_y))
                                    # 处理3元组(RGB)和4元组(RGBA)颜色
                                    if len(color) == 4:
                                        r, g, b, _ = color
                                    else:
                                        r, g, b = color
                                    
                                    # 更新选择的颜色和颜色输入框
                                    state.selected_color = (r, g, b)
                                    state.color_values = {'r': r, 'g': g, 'b': b}
                                else:
                                    # 正常绘画模式：直接绘制一个像素
                                    color = (0, 0, 0, 0) if state.erase_mode else state.selected_color
                                    pygame.draw.rect(state.image_surface, color, (pixel_x, pixel_y, 1, 1))
                                    state.cached_scaled_image = None  # 清除缓存
                        
                        # 只有在非取色器模式下才开始绘画
                        state.is_painting = not state.picker_mode
                        state.is_dragging = False  # 确保拖拽状态为False
                
                # 处理右键点击
                elif event.button == 3:  # 右键
                    # 处理右键拖拽
                    if state.image_surface:
                        # 只要有图片加载，右键点击任何位置都可以开始拖拽
                        state.is_right_dragging = True
                        state.drag_start_pos = event.pos
            
            elif event.type == pygame.MOUSEBUTTONUP:
                state.is_dragging = False
                state.is_painting = False
                state.is_right_dragging = False
                
                # 结束选择区域
                if state.is_selecting and state.selection_start:
                    # 计算当前鼠标对应的像素坐标
                    mouse_x, mouse_y = event.pos
                    pixel_x = (mouse_x - state.offset_x) // state.zoom
                    pixel_y = (mouse_y - state.offset_y) // state.zoom
                    
                    # 确保像素坐标在图片范围内
                    if state.image_surface:
                        pixel_x = max(0, min(pixel_x, state.image_surface.get_width() - 1))
                        pixel_y = max(0, min(pixel_y, state.image_surface.get_height() - 1))
                        
                        # 设置选择区域的结束点
                        state.selection_end = (pixel_x, pixel_y)
                        state.is_selecting = False
                
                # 结束移动选择区域
                if state.is_moving_selection:
                    state.is_moving_selection = False
                    state.move_start_pos = None
            
            elif event.type == pygame.MOUSEMOTION:
                # 处理移动选择区域
                if state.is_moving_selection and state.selection_start and state.selection_end and state.image_surface and state.move_start_pos:
                    # 计算当前鼠标对应的像素坐标
                    current_x = (event.pos[0] - state.offset_x) // state.zoom
                    current_y = (event.pos[1] - state.offset_y) // state.zoom
                    
                    # 确保像素坐标在图片范围内
                    current_x = max(0, min(current_x, state.image_surface.get_width() - 1))
                    current_y = max(0, min(current_y, state.image_surface.get_height() - 1))
                    
                    # 计算移动的距离
                    dx = current_x - state.move_start_pos[0]
                    dy = current_y - state.move_start_pos[1]
                    
                    # 如果没有移动，直接返回
                    if dx == 0 and dy == 0:
                        return
                    
                    # 获取选择区域的坐标
                    x1, y1 = state.selection_start
                    x2, y2 = state.selection_end
                    start_x = min(x1, x2)
                    start_y = min(y1, y2)
                    end_x = max(x1, x2)
                    end_y = max(y1, y2)
                    
                    # 计算新的选择区域坐标
                    new_start_x = max(0, min(start_x + dx, state.image_surface.get_width() - 1))
                    new_start_y = max(0, min(start_y + dy, state.image_surface.get_height() - 1))
                    new_end_x = max(0, min(end_x + dx, state.image_surface.get_width() - 1))
                    new_end_y = max(0, min(end_y + dy, state.image_surface.get_height() - 1))
                    
                    # 计算实际移动的距离（可能会被边界限制）
                    actual_dx = new_start_x - start_x
                    actual_dy = new_start_y - start_y
                    
                    # 如果没有实际移动，直接返回
                    if actual_dx == 0 and actual_dy == 0:
                        return
                    
                    # 创建临时表面来存储选择区域的像素数据（支持透明）
                    temp_surface = pygame.Surface((end_x - start_x + 1, end_y - start_y + 1), pygame.SRCALPHA)
                    
                    # 使用blit复制选择区域的像素数据到临时表面
                    temp_surface.blit(state.image_surface, (0, 0), (start_x, start_y, end_x - start_x + 1, end_y - start_y + 1))
                    
                    # 清除原选择区域的像素（填充透明）
                    transparent_rect = pygame.Rect(start_x, start_y, end_x - start_x + 1, end_y - start_y + 1)
                    pygame.draw.rect(state.image_surface, (0, 0, 0, 0), transparent_rect)
                    
                    # 使用blit将临时表面的像素数据复制到新位置
                    state.image_surface.blit(temp_surface, (new_start_x, new_start_y))
                    
                    state.cached_scaled_image = None  # 清除缓存
                    
                    # 更新选择区域的坐标
                    state.selection_start = (new_start_x, new_start_y)
                    state.selection_end = (new_end_x, new_end_y)
                    
                    # 更新移动起始位置
                    state.move_start_pos = (current_x, current_y)
                
                # 处理右键拖拽
                elif state.is_right_dragging:
                    dx = event.pos[0] - state.drag_start_pos[0]
                    dy = event.pos[1] - state.drag_start_pos[1]
                    state.offset_x += dx
                    state.offset_y += dy
                    state.drag_start_pos = event.pos
                
                # 处理绘画
                elif state.is_painting and state.image_surface:
                    # 计算像素位置
                    pixel_x = (event.pos[0] - state.offset_x) // state.zoom
                    pixel_y = (event.pos[1] - state.offset_y) // state.zoom
                    
                    # 检查是否在图片范围内
                    if 0 <= pixel_x < state.image_surface.get_width() and 0 <= pixel_y < state.image_surface.get_height():
                        # 确定颜色
                        color = (0, 0, 0, 0) if state.erase_mode else state.selected_color
                        
                        # 修改像素颜色
                        pygame.draw.rect(state.image_surface, color, (pixel_x, pixel_y, 1, 1))
                        state.cached_scaled_image = None  # 清除缓存
                
                # 计算当前像素坐标
                if state.image_surface:
                    pixel_x = (event.pos[0] - state.offset_x) // state.zoom
                    pixel_y = (event.pos[1] - state.offset_y) // state.zoom
                    if 0 <= pixel_x < state.image_surface.get_width() and 0 <= pixel_y < state.image_surface.get_height():
                        state.current_pixel_pos = (pixel_x, pixel_y)
                    else:
                        state.current_pixel_pos = (-1, -1)
        
        # 更新窗口标题，显示当前像素坐标、格子坐标和选择区域尺寸
        if state.image_surface:
            # 获取选择区域信息
            selection_info = ""
            if state.selection_start and state.selection_end:
                x1, y1 = state.selection_start
                x2, y2 = state.selection_end
                width = abs(x2 - x1) + 1
                height = abs(y2 - y1) + 1
                selection_info = f" 选择区域: {width}x{height}"
            
            if state.current_pixel_pos != (-1, -1):
                pixel_x, pixel_y = state.current_pixel_pos
                # 计算格子坐标（每32像素为一格，从1开始计数）
                grid_x = (pixel_x // 32) + 1
                grid_y = (pixel_y // 32) + 1
                # 获取文件名
                filename = os.path.basename(state.image_path) if state.image_path else "未命名"
                pygame.display.set_caption(f"像素编辑器 - {filename} - 坐标: ({pixel_x}, {pixel_y}) 格子: ({grid_y}, {grid_x}) 缩放: {state.zoom}x{selection_info}")
            else:
                # 获取文件名
                filename = os.path.basename(state.image_path) if state.image_path else "未命名"
                pygame.display.set_caption(f"像素编辑器 - {filename} - 缩放: {state.zoom}x{selection_info}")
        else:
            pygame.display.set_caption("像素编辑器 - 未命名")
        
        # 更新显示
        pygame.display.flip()
        clock.tick(60)  # 限制帧率为60 FPS
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()