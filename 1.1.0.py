import pygame
import random
import sys
import os
import math
import webbrowser
import re
import json
import sqlite3
import hashlib
import base64
from datetime import datetime
from pygame.locals import *

# 初始化 Pygame 库
pygame.init()
pygame.mixer.init()

# 字体配置
CUSTOM_FONT_PATH = "fonts/font.ttf"  # 自定义字体文件路径
FALLBACK_FONT = "Arial Bold"  # 备用字体（当自定义字体加载失败时使用）

# 全局BGM对象
global start_menu_bgm, current_bgm, store_bgm
start_menu_bgm = None  # 开始界面背景音乐
current_bgm = None     # 游戏背景音乐
store_bgm = None       # 商店背景音乐
game_started = False  # 游戏是否开始的标志

# 游戏基础参数
SCREEN_WIDTH = 1000  # 游戏窗口宽度
SCREEN_HEIGHT = 400  # 游戏窗口高度 
FPS = 75  # 游戏帧率
GRAVITY = 0.8  # 重力加速度
JUMP_FORCE = -15  # 跳跃力度
BASE_OBSTACLE_SPEED = 10  # 基础障碍移动速度
BASE_SPAWN_RATE = 1325  # 障碍生成间隔（毫秒）
MAX_SPEED = 30  # 障碍最大移动速度
INITIAL_HEALTH = 2.0  # 初始血量
HEALTH_DECREASE = 1.0  # 每次受击扣除的血量
HEALTH_REGEN_RATE = 0.25   # 每秒恢复血量速度
HEALTH_REGEN_INTERVAL = 1000  # 血量恢复间隔（毫秒）
HEALTH_REGEN_COOLDOWN = 80000  # 血量恢复冷却时间（毫秒）

# 技能冷却时间减免比例
SKILL_CD_REDUCE_RATIO = {
    1: 0.00,  # 零阶难度 
    2: 0.15,  # 一阶难度 
    3: 0.30,  # 二阶难度 
    4: 0.45   # 三阶难度 
}

# 不同难度阶段的障碍速度
STAGE_SPEEDS = {
    1: BASE_OBSTACLE_SPEED,          # 阶段1 - 基础速度
    2: BASE_OBSTACLE_SPEED + 6,      # 阶段2 - 基础速度+2
    3: BASE_OBSTACLE_SPEED + 9,      # 阶段3 - 基础速度+4
    4: min(BASE_OBSTACLE_SPEED + 15, MAX_SPEED)  # 阶段4 - 基础速度+8（不超过最大速度）
}

# 分数与难度分级
SCORE_STAGE_1 = 0  # 阶段1分数起点
SCORE_STAGE_2 = 150  # 阶段2分数起点
SCORE_STAGE_3 = 400  # 阶段3分数起点
SCORE_STAGE_4 = 550  # 阶段4分数起点
SCORE_STAGE_5 = 800  # 阶段5分数起点
MAX_SCORE = 450  # 最高分数（最佳演绎分数线）
SCORE_PER_SECOND = 50  # 每秒获得的分数

# 技能升级闪烁效果
SKILL_UPGRADE_FLASH_COLOR = (255, 215, 0)  # 闪烁颜色（金色）
SKILL_FLASH_DURATION = 600  # 闪烁总时长（毫秒）
SKILL_FLASH_INTERVAL = 150  # 闪烁切换频率（毫秒）

# 技能冷却时间提升标识
BOOST_ICON_SIZE = 15  # 标识尺寸
BOOST_ICON_COLOR = (255, 204, 0)  # 标识背景色（黄色）
BOOST_ICON_TEXT = "UP"  # 标识文字
BOOST_ICON_FONT_SIZE = 12  # 标识文字大小

# 技能1：Brave Dash（勇敢冲刺）
SKILL1_COOLDOWN = 30000  # 冷却时间（毫秒）
SKILL1_DURATION = 600  # 技能生效时长（毫秒）
SKILL1_KEY = pygame.K_LSHIFT  # 触发按键
SKILL1_TEXT_DURATION = 1200  # 技能文字显示时长（毫秒）
SKILL1_DISPLAY_TEXT = "FLYWHEEL EFFECT"  # 技能显示文字

# 技能2：Zoom Boost（快速治疗）
SKILL2_COOLDOWN = 120000  # 冷却时间（毫秒）
SKILL2_KEY = pygame.K_TAB  # 触发按键
SKILL2_HEALTH_BOOST = 1.5  # 额外血量占比
SKILL2_TEXT_DURATION = 1000  # 技能文字显示时长（毫秒）
SKILL2_DISPLAY_TEXT = "Borrowed Time"  # 技能显示文字

# 技能3：Jump（命之跳跃）
SKILL3_COOLDOWN = 60000  # 冷却时间（毫秒）
SKILL3_KEY = pygame.K_CAPSLOCK  # 触发按键
SKILL3_BASE_FPS_BOOST = 0.8  # 基础FPS提升
SKILL3_FPS_BOOST_PER_DIFFICULTY = 0.05  # 每级难度额外FPS提升
SKILL3_DURATION = 5000  # 技能持续时间（毫秒）
SKILL3_INVUL_DURATION = 5000  # 技能启动时的免疫时长（毫秒）
SKILL3_TEXT_DURATION = 1000  # 技能文字显示时长（毫秒）
SKILL3_DISPLAY_TEXT = "命之跳跃"  # 技能显示文字

# 音乐和音效配置
LEVEL_UP_SOUND_PATH = "music_effects/level_up.mp3"  # 难度提升音效路径
LEVEL_UP_SOUND_VOLUME = 0.8  # 难度提升音效音量
RANK_UP_SOUND_PATH = "music_effects/rank_up.mp3"  # 段位提升音效路径
RANK_UP_SOUND_VOLUME = 0.8  # 段位提升音效音量
BGM_LIST = ["game_musics/music1.mp3"]  # 游戏背景音乐列表
BGM_VOLUME = 0.4  # 游戏背景音乐音量
STORE_BGM_PATH = "music_effects/store_music.mp3"  # 商店背景音乐路径
STORE_BGM_VOLUME = 0.6  # 商店背景音乐音量
START_MENU_BGM_PATH = "music_effects/start_menu_music.mp3"  # 开始界面背景音乐路径
START_MENU_BGM_VOLUME = 0.6  # 开始界面背景音乐音量
PREPARATION_BGM_PATH = "music_effects/preparation_music.mp3"  # 准备界面背景音乐路径
PREPARATION_BGM_VOLUME = 0.6  # 准备界面背景音乐音量

# 背景音乐状态变量
current_bgm_index = 0  # 当前播放的背景音乐索引
current_bgm = None  # 当前游戏背景音乐对象
store_bgm = None  # 商店背景音乐对象

# 血条相关配置
HEALTH_BAR_WIDTH = 280  # 血条宽度
HEALTH_BAR_HEIGHT = 30  # 血条高度
HEALTH_BAR_COLOR = (76, 201, 240)  # 血条颜色（亮蓝）
HEALTH_BAR_BG_COLOR = (230, 230, 230)  # 血条背景颜色
HEALTH_BAR_LOW_COLOR = (255, 99, 71)  # 低血量时的血条颜色（番茄红）
HEALTH_LOW_THRESHOLD = 1.0  # 低血量阈值

# 额外血条图标
EXTRA_HEALTH_ICON_COLOR = (230, 230, 230)  # 额外血条图标颜色
EXTRA_HEALTH_ICON_EMPTY_COLOR = (150, 150, 150)  # 空额外血条图标颜色

# 游戏颜色方案
PRIMARY_COLOR = (33, 33, 33)       # 主色（深灰）
SECONDARY_COLOR = (76, 201, 240)   # 辅助色（亮蓝）
ACCENT_COLOR = (255, 99, 71)       # 强调色（番茄红）
BACKGROUND_COLOR = (248, 248, 248) # 背景色（浅灰）
GROUND_COLOR = (200, 200, 200)  # 地面颜色
TEXT_COLOR = (33, 33, 33)  # 文字颜色
WHITE = (255, 255, 255)  # 白色
BLACK = (0, 0, 0)  # 黑色
GRAY_LIGHT = (230, 230, 230)  # 浅灰色
GRAY_MEDIUM = (150, 150, 150)  # 中灰色
GRAY_DARK = (100, 100, 100)  # 深灰色

# 遮罩样式配置
MASK_ALPHA_EASY = 150  # 简单难度下的遮罩透明度
MASK_ALPHA_HARD = 180  # 困难难度下的遮罩透明度
MASK_COLOR = (0, 0, 0)  # 遮罩颜色

# 图标文字样式
ICON_TEXT_FONT_SIZE = 24  # 图标文字大小
ICON_TEXT_COLOR = WHITE  # 图标文字颜色
ICON_TEXT_OUTLINE_COLOR = BLACK  # 图标文字描边颜色
ICON_TEXT_STROKE_WIDTH = 1  # 图标文字描边宽度

# 技能1图标颜色配置
SKILL1_ACTIVE_COLOR = (76, 175, 80)  # 技能激活时的颜色（绿色）
SKILL1_COOLDOWN_COLOR = GRAY_MEDIUM  # 技能冷却时的颜色（中灰色）
SKILL1_READY_COLOR = GRAY_LIGHT  # 技能就绪时的颜色（浅灰色）
SKILL1_TEXT_COLOR = (255, 99, 71)  # 技能文字颜色（番茄红）
SKILL1_DISABLE_COLOR = (255, 99, 71)  # 技能禁用时的颜色（番茄红）

# 技能2图标颜色配置
SKILL2_ACTIVE_COLOR = (76, 175, 80)  # 技能激活时的颜色（绿色）
SKILL2_COOLDOWN_COLOR = GRAY_MEDIUM  # 技能冷却时的颜色（中灰色）
SKILL2_READY_COLOR = GRAY_LIGHT  # 技能就绪时的颜色（浅灰色）
SKILL2_DISABLE_COLOR = (255, 99, 71)  # 技能禁用时的颜色（番茄红）
SKILL2_TEXT_COLOR = (76, 175, 80)  # 技能文字颜色（绿色）

# 速度图标颜色配置
SPEED_ICON_EASY = GRAY_LIGHT  # 简单难度下的速度图标颜色
SPEED_ICON_HARD = GRAY_LIGHT  # 困难难度下的速度图标颜色

# 血迹粒子特效配置
BLOOD_COLORS = [
    (189, 103, 103),  # 柔和红（低饱和）
    (103, 189, 103),  # 柔和绿（低饱和）
    (103, 103, 189),  # 柔和蓝（低饱和）
    (189, 189, 103),  # 柔和黄（低饱和）
    (189, 103, 189),  # 柔和紫（低饱和）
    (103, 189, 189),  # 柔和青（低饱和）
    (189, 145, 103),  # 柔和橙（低饱和）
    (220, 220, 220)   # 浅灰（替代纯白，更柔和）
]
BLOOD_ALPHA = 220  # 血迹粒子不透明度（高不透明度，常驻效果）
BLOOD_MAX_PARTICLES = {  # 不同血量对应的总粒子数量
    2.0: 0,  # 满血 - 无粒子
    1.5: 300,  # 扣0.5血 - 300个粒子
    1.0: 200,  # 扣1.0血 - 200个粒子
    0.5: 350,  # 扣1.5血 - 350个粒子
    0.0: 500  # 扣2.0血（死亡） - 500个粒子
}

# 粒子喷溅区域配置（扩展到界面边缘50px）
BLOOD_SPLATTER_AREAS = [
    {"x": (0, SCREEN_WIDTH), "y": (0, 50), "angle_range": (180, 270), "speed_range": (1, 4)},  # 顶部喷溅区域
    {"x": (0, SCREEN_WIDTH), "y": (SCREEN_HEIGHT - 50, SCREEN_HEIGHT), "angle_range": (0, 90), "speed_range": (1, 4)},  # 底部喷溅区域
    {"x": (0, 50), "y": (0, SCREEN_HEIGHT), "angle_range": (90, 180), "speed_range": (1, 4)},  # 左侧喷溅区域
    {"x": (SCREEN_WIDTH - 50, SCREEN_WIDTH), "y": (0, SCREEN_HEIGHT), "angle_range": (270, 360), "speed_range": (1, 4)}  # 右侧喷溅区域
]

# 粒子尺寸分级
BLOOD_PARTICLE_SIZES = {
    "large": (3, 7),  # 大粒子尺寸范围
    "medium": (2, 4),  # 中粒子尺寸范围
    "small": (1, 2)  # 小粒子尺寸范围
}

# 粒子运动参数（低速微动，模拟血液粘性）
PARTICLE_DRIFT_SPEED = 0.1  # 粒子微动速度
PARTICLE_ROTATE_SPEED = 0.5  # 粒子旋转速度

# 最佳演绎特效配置
PERFECT_COLORS = [(255, 215, 0), (255, 255, 255), (255, 192, 203), (148, 0, 211)]  # 金→白→粉→紫
PERFECT_PARTICLE_COUNT = 100  # 特效粒子数量
PERFECT_TEXT_DURATION = 5000  # 特效文字显示时长（5秒）
PERFECT_SOUND_DURATION = 3000  # 胜利音效时长（3秒）

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # 设置窗口大小
pygame.display.set_caption("Escape")  # 设置窗口标题
clock = pygame.time.Clock()  # 创建时钟对象，用于控制游戏帧率

# 加载自定义字体函数
def load_custom_font(size, bold=False):
    """加载自定义字体（全局通用）
    
    参数:
        size: 字体大小
        bold: 是否加粗
    
    返回:
        加载成功的字体对象
    """
    try:
        # 优先加载自定义字体文件
        font = pygame.font.Font(CUSTOM_FONT_PATH, size)
        if bold:
            font.set_bold(True)
        return font
    except:
        # 加载失败则使用系统备用字体
        sys_font = pygame.font.SysFont(FALLBACK_FONT, size, bold=bold)
        return sys_font

# 全局字体初始化
MAIN_FONT = load_custom_font(48, bold=True)  # 主字体
SMALL_FONT = load_custom_font(24)  # 小字体
ICON_FONT = load_custom_font(ICON_TEXT_FONT_SIZE)  # 图标文字字体
TITLE_FONT = load_custom_font(72, bold=True)  # 标题字体
SKILL_FONT = load_custom_font(72, bold=True)  # 技能文字字体
SCORE_FONT = load_custom_font(36, bold=True)  # 分数字体
PERFECT_FONT = load_custom_font(96, bold=True)  # 最佳演绎字体
END_PANEL_TITLE_FONT = load_custom_font(40, bold=True)  # 结束面板标题字体
END_PANEL_TEXT_FONT = load_custom_font(20)  # 结束面板正文字体
END_PANEL_SMALL_FONT = load_custom_font(16)  # 结束面板小字体

# 全局资源变量
game_resources = None  # 游戏资源对象

# 图标布局配置
ICON_SIZE = 32  # 图标大小
CONTAINER_SIZE = ICON_SIZE + 12  # 容器大小（包含边框）
ICON_SPACING = 15  # 图标之间的间距
ICON_Y_POS = 25  # 图标垂直位置
TOTAL_ICONS_WIDTH = 5 * CONTAINER_SIZE + 4 * ICON_SPACING  # 五个图标总宽度
ICONS_START_X = SCREEN_WIDTH - 40 - TOTAL_ICONS_WIDTH  # 图标组起始X位置（右对齐）

# 血条图标配置
HEALTH_ICON_SIZE = ICON_SIZE  # 血条图标尺寸与其他图标一致
HEALTH_ICON_CONTAINER_SIZE = CONTAINER_SIZE  # 容器尺寸统一
HEALTH_ICON_Y_POS = ICON_Y_POS  # 顶部距离与其他图标一致
HEALTH_ICON_X_POS = 30 + 220 + 15  # 分数面板右侧15px（分数面板x=30，宽度220）
HEALTH_ICON_COLOR = GRAY_LIGHT  # 血条图标容器颜色
HEALTH_ICON_LOW_COLOR = HEALTH_BAR_LOW_COLOR  # 低血量容器颜色

# 难度进度图标配置
DIFFICULTY_ICON_SIZE = ICON_SIZE  # 图标尺寸与其他图标一致
DIFFICULTY_ICON_CONTAINER_SIZE = CONTAINER_SIZE  # 容器尺寸统一
DIFFICULTY_ICON_Y_POS = ICON_Y_POS  # 顶部距离与其他图标一致
DIFFICULTY_ICON_X_POS = HEALTH_ICON_X_POS + HEALTH_ICON_CONTAINER_SIZE + 15  # 血量图标右侧15px
DIFFICULTY_ICON_COLORS = {
    1: GRAY_LIGHT,  # 简单难度（1）
    2: GRAY_LIGHT,  # 下难（2）
    3: GRAY_LIGHT,  # 中难（3）
    4: GRAY_LIGHT   # 上难（4）
}
DIFFICULTY_TEXT_MAP = {
    1: "零阶",
    2: "一阶",
    3: "二阶",
    4: "三阶"
}

# 速度图标配置
SPEED_ICON_X_POS = DIFFICULTY_ICON_X_POS + DIFFICULTY_ICON_CONTAINER_SIZE + 15  # 难度图标右侧15px
SPEED_ICON_Y_POS = ICON_Y_POS  # 顶部对齐
SPEED_ICON_CONTAINER_SIZE = CONTAINER_SIZE  # 容器尺寸

# FPS提升图标配置（常驻显示，与速度图标样式相同）
FPS_BOOST_ICON_X_POS = SPEED_ICON_X_POS + SPEED_ICON_CONTAINER_SIZE + 15  # 速度图标右侧15px
FPS_BOOST_ICON_Y_POS = ICON_Y_POS  # 顶部对齐
FPS_BOOST_ICON_CONTAINER_SIZE = CONTAINER_SIZE  # 容器尺寸
FPS_BOOST_ICON_COLOR = GRAY_LIGHT  # 图标容器颜色

# 额外血量图标配置
EXTRA_HEALTH_ICON_X_POS = FPS_BOOST_ICON_X_POS + CONTAINER_SIZE + 15  # FPS提升图标右侧15px
EXTRA_HEALTH_ICON_Y_POS = ICON_Y_POS  # 顶部对齐
EXTRA_HEALTH_ICON_CONTAINER_SIZE = CONTAINER_SIZE  # 容器尺寸

# 张狂图标配置
FRENZY_ICON_X_POS = EXTRA_HEALTH_ICON_X_POS + CONTAINER_SIZE + 15  # 额外血量图标右侧15px
FRENZY_ICON_Y_POS = ICON_Y_POS  # 顶部对齐
FRENZY_ICON_CONTAINER_SIZE = CONTAINER_SIZE  # 容器尺寸
FRENZY_ICON_COLOR = (255, 215, 0)  # 张狂图标颜色（金色）

# 矫健图标配置
AGILITY_ICON_X_POS = FRENZY_ICON_X_POS + CONTAINER_SIZE + 15  # 张狂图标右侧15px
AGILITY_ICON_Y_POS = ICON_Y_POS  # 顶部对齐
AGILITY_ICON_CONTAINER_SIZE = CONTAINER_SIZE  # 容器尺寸
AGILITY_ICON_COLOR = (50, 205, 50)  # 矫健图标颜色（绿色）

# 技能3颜色配置
SKILL3_ACTIVE_COLOR = (76, 175, 80)  # 技能激活时的颜色（与技能1/2一致）
SKILL3_COOLDOWN_COLOR = GRAY_MEDIUM  # 技能冷却时的颜色（与技能1/2一致）
SKILL3_READY_COLOR = GRAY_LIGHT  # 技能就绪时的颜色（与技能1/2一致）
SKILL3_DISABLE_COLOR = (255, 99, 71)  # 技能禁用时的颜色（与技能1/2一致）
SKILL3_TEXT_COLOR = (148, 0, 211)  # 技能文字颜色

# 技能3跳跃状态图标配置
JUMP_BOOST_ICON_SIZE = ICON_SIZE  # 与其他图标尺寸一致
JUMP_BOOST_ICON_CONTAINER_SIZE = CONTAINER_SIZE  # 容器尺寸统一
JUMP_BOOST_ICON_Y_POS = ICON_Y_POS  # 顶部对齐
JUMP_BOOST_ACTIVE_COLOR = GRAY_LIGHT  # 激活态颜色
JUMP_BOOST_TEXT_COLOR = WHITE  # 文字颜色
JUMP_BOOST_MASK_COLOR = MASK_COLOR  # 遮罩颜色

# 生命值恢复冷却图标配置
HEALTH_REGEN_ICON_SIZE = JUMP_BOOST_ICON_SIZE  # 与技能三图标尺寸一致
HEALTH_REGEN_ICON_CONTAINER_SIZE = JUMP_BOOST_ICON_CONTAINER_SIZE  # 容器尺寸统一
HEALTH_REGEN_ICON_Y_POS = JUMP_BOOST_ICON_Y_POS  # 顶部对齐
HEALTH_REGEN_ACTIVE_COLOR = (255, 99, 71)  # 激活态颜色
HEALTH_REGEN_TEXT_COLOR = JUMP_BOOST_TEXT_COLOR  # 文字颜色
HEALTH_REGEN_MASK_COLOR = JUMP_BOOST_MASK_COLOR  # 遮罩颜色

# 锁定图标配置
LOCKED_ICON_SIZE = ICON_SIZE  # 锁定图标尺寸和技能图标一致
LOCKED_ICON_COLOR = (100, 100, 100)  # 锁定图标颜色（深灰）
LOCKED_TEXT = "🔒"  # 锁定标识
LOCKED_TEXT_FONT_SIZE = 24  # 锁定文字大小

# 技能解锁分数阈值
SKILL1_UNLOCK_SCORE = SCORE_STAGE_2  # 技能1解锁分数
SKILL2_UNLOCK_SCORE = SCORE_STAGE_2  # 技能2解锁分数
SKILL3_UNLOCK_SCORE = SCORE_STAGE_2  # 技能3解锁分数

# 折线图相关配置
END_PANEL_WIDTH = 400  # 结束面板宽度
END_PANEL_HEIGHT = 300  # 结束面板高度
END_PANEL_X = SCREEN_WIDTH // 2 - END_PANEL_WIDTH - 20  # 左面板X坐标
END_PANEL_Y = SCREEN_HEIGHT // 2 - END_PANEL_HEIGHT // 2  # 结束面板Y坐标



# 数据库配置
DATABASE_FILE = "game_data.db"  # 本地数据库文件
ENCRYPTION_KEY = "game_encryption_key_2026"  # 加密密钥

# 积分商店配置
STORE_PROMPT_TEXT = "Skill unlocked successfully! Game will restart shortly."  # 解锁成功提示
SHOP_OPEN_TEXT = "Press 1 to open the score shop"  # 商城打开提示文字

# Rank system configuration
RANK_SCORE_PER_STAGE = 20  # Score needed per stage
RANK_CONFIG = {
    0: {"name": "Rank 0", "stages": 1, "color": (150, 150, 150), "icon": "rankicon/rank0.png"},
    1: {"name": "Rank 1", "stages": 3, "color": (144, 238, 144), "icon": "rankicon/rank1.png"},       # Rank 1: 3 stages, green
    2: {"name": "Rank 2", "stages": 4, "color": (173, 216, 230), "icon": "rankicon/rank2.png"},       # Rank 2: 4 stages, light blue
    3: {"name": "Rank 3", "stages": 5, "color": (100, 200, 255), "icon": "rankicon/rank3.png"},         # Rank 3: 5 stages, blue
    4: {"name": "Rank 4", "stages": 5, "color": (147, 112, 219), "icon": "rankicon/rank4.png"},     # Rank 4: 5 stages, purple
    5: {"name": "Rank 5", "stages": 5, "color": (255, 165, 0), "icon": "rankicon/rank5.png"},        # Rank 5: 5 stages, orange
    6: {"name": "Rank 6", "stages": 5, "color": (255, 215, 0), "icon": "rankicon/rank6.png"}          # Rank 6: 5 stages, gold
}
RANK_STAGE_NAMES = ["V", "IV", "III", "II", "I"]  # Stage names (Roman numerals), from largest to smallest

# 技能和天赋价格配置
RARE_PRICE = 300  # 罕见品质价格
UNIQUE_PRICE = 600  # 独特品质价格
EPIC_PRICE = 1000  # 奇珍品质价格
LEGENDARY_PRICE = 1500  # 稀世品质价格

# 张狂天赋价格配置
FRENZY_RARE_PRICE = 400  # 罕见品质 - 15秒延迟
FRENZY_UNIQUE_PRICE = 800  # 独特品质 - 10秒延迟
FRENZY_EPIC_PRICE = 1200  # 奇珍品质 - 5秒延迟
FRENZY_LEGENDARY_PRICE = 1600  # 稀世品质 - 0秒延迟（立即生效）

# 矫健天赋价格配置
AGILITY_RARE_PRICE = 350  # 罕见品质 - 1% FPS提升
AGILITY_UNIQUE_PRICE = 700  # 独特品质 - 3% FPS提升
AGILITY_EPIC_PRICE = 1050  # 奇珍品质 - 5% FPS提升
AGILITY_LEGENDARY_PRICE = 1400  # 稀世品质 - 7% FPS提升

# Skill rarity configuration (Rare/Unique/Epic/Legendary)
SKILL_RARITY = {
    "rare": {"name": "Rare", "uses": 1, "color": (144, 238, 144), "price": RARE_PRICE},      # Light green, 1 use
    "unique": {"name": "Unique", "uses": 3, "color": (173, 216, 230), "price": UNIQUE_PRICE},    # Light blue, 3 uses
    "epic": {"name": "Epic", "uses": 5, "color": (147, 112, 219), "price": EPIC_PRICE},     # Purple, 5 uses
    "legendary": {"name": "Legendary", "uses": -1, "color": (100, 100, 100), "price": LEGENDARY_PRICE}    # Dark gray, unlimited uses
}

# Frenzy talent rarity configuration (Rare/Unique/Epic/Legendary)
# 效果：15秒/10秒/5秒/0秒延迟后获得150分
# Agility talent rarity configuration (Rare/Unique/Epic/Legendary)
# 效果：FPS提升1%/3%/5%/7%
ITEM_RARITY = {
    "frenzy": {
        "rare": {"name": "Frenzy", "uses": 1, "color": (144, 238, 144), "price": FRENZY_RARE_PRICE, "delay": 15000},      # 15秒
        "unique": {"name": "Frenzy ", "uses": 1, "color": (173, 216, 230), "price": FRENZY_UNIQUE_PRICE, "delay": 10000},    # 10秒
        "epic": {"name": "Frenzy", "uses": 1, "color": (147, 112, 219), "price": FRENZY_EPIC_PRICE, "delay": 5000},     # 5秒
        "legendary": {"name": "Frenzy", "uses": 1, "color": (100, 100, 100), "price": FRENZY_LEGENDARY_PRICE, "delay": 0}    # 0秒（立即）
    },
    "agility": {
        "rare": {"name": "Agility", "uses": -1, "color": (144, 238, 144), "price": AGILITY_RARE_PRICE, "fps_boost": 0.01},      # 1%
        "unique": {"name": "Agility", "uses": -1, "color": (173, 216, 230), "price": AGILITY_UNIQUE_PRICE, "fps_boost": 0.03},    # 3%
        "epic": {"name": "Agility", "uses": -1, "color": (147, 112, 219), "price": AGILITY_EPIC_PRICE, "fps_boost": 0.05},     # 5%
        "legendary": {"name": "Agility", "uses": -1, "color": (100, 100, 100), "price": AGILITY_LEGENDARY_PRICE, "fps_boost": 0.07}    # 7%
    }
}

# 购买成功弹窗配置
SUCCESS_POPUP_WIDTH = 450  # 弹窗宽度
SUCCESS_POPUP_HEIGHT = 200  # 弹窗高度
SUCCESS_POPUP_BG = WHITE  # 弹窗背景颜色
SUCCESS_POPUP_BORDER = GRAY_LIGHT  # 弹窗边框颜色
SUCCESS_POPUP_SHADOW = (0, 0, 0, 50)  # 弹窗阴影效果
SUCCESS_TEXT_COLOR = PRIMARY_COLOR  # 弹窗文字颜色
SUCCESS_TITLE_COLOR = SECONDARY_COLOR  # 弹窗标题颜色
SUCCESS_ANIMATION_DURATION = 500  # 弹窗淡入动画时长（毫秒）
SUCCESS_DISPLAY_DURATION = 1000  # 弹窗停留时长（毫秒）

# 代偿图标配置
COMPENSATION_ICON_SIZE = BOOST_ICON_SIZE  # 与提升图标大小相同
COMPENSATION_ICON_COLOR = (255, 99, 71)  # 红色底色
COMPENSATION_ICON_TEXT = "DG"  # 代偿标识文字
COMPENSATION_ICON_FONT_SIZE = BOOST_ICON_FONT_SIZE  # 文字大小与提升图标一致

# 技能选择界面配置
SKILL_SELECT_WIDTH = 600  # 界面宽度
SKILL_SELECT_HEIGHT = 400  # 界面高度
SKILL_SELECT_BG = WHITE  # 背景颜色
SKILL_SELECT_BORDER = GRAY_LIGHT  # 边框颜色
SKILL_SELECT_TITLE_FONT_SIZE = 36  # 标题字体大小
SKILL_SELECT_ITEM_FONT_SIZE = 28  # 选项字体大小
SKILL_SELECT_ITEM_HEIGHT = 70  # 选项高度
SKILL_SELECT_ITEM_SPACING = 20  # 选项间距
SKILL_SELECT_ACTIVE_COLOR = SECONDARY_COLOR  # 选中技能的颜色
SKILL_SELECT_DISABLE_COLOR = GRAY_MEDIUM  # 禁用技能的颜色
SKILL_SELECT_TEXT_COLOR = PRIMARY_COLOR  # 文字颜色
SKILL_SELECT_PROMPT_TEXT = "Press 1/2/3 to select skill, SPACE to confirm"  # 提示文字

# 全局变量：记录本局选中的技能
selected_skill = None  # 可选值："skill1", "skill2", "skill3", None

# 粒子类（最佳演绎特效）
class Particle:
    """粒子类，用于实现最佳演绎特效
    
    属性:
        x: 粒子的X坐标
        y: 粒子的Y坐标
        size: 粒子的大小
        color: 粒子的颜色
        speed_x: 粒子的X方向速度
        speed_y: 粒子的Y方向速度
        alpha: 粒子的透明度
        fade_speed: 粒子的淡出速度
    """
    def __init__(self, x, y):
        """初始化粒子
        
        参数:
            x: 粒子的初始X坐标
            y: 粒子的初始Y坐标
        """
        self.x = x
        self.y = y
        self.size = random.randint(3, 8)
        self.color = random.choice(PERFECT_COLORS)
        self.speed_x = random.uniform(-5, 5)
        self.speed_y = random.uniform(-5, 5)
        self.alpha = 255
        self.fade_speed = random.uniform(2, 5)

    def update(self):
        """更新粒子状态
        
        返回:
            bool: 粒子是否仍然活跃（透明度大于0）
        """
        self.x += self.speed_x
        self.y += self.speed_y
        self.alpha -= self.fade_speed
        return self.alpha > 0

    def draw(self):
        """绘制粒子"""
        particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(particle_surface, (*self.color, int(self.alpha)), (0, 0, self.size, self.size))
        screen.blit(particle_surface, (self.x, self.y))

# 新增滚动背景类
class ScrollingBackground:
    def __init__(self):
        self.bg_img = game_resources["background_image"]
        if self.bg_img:
            self.width = self.bg_img.get_width()  # 用图片实际宽度，而非强制屏幕宽度
            self.height = self.bg_img.get_height()
            self.x1 = 0
            self.x2 = self.width
            self.speed = 2  # 基础滚动速度（原1过慢）

    def update(self, current_speed):
        if self.bg_img:
            # 调整速度系数：0.5 更适配游戏节奏（原0.2过慢）
            self.speed = current_speed * 0.5
            self.x1 -= self.speed
            self.x2 -= self.speed

            # 重置滚动位置（修复边界判断）
            if self.x1 <= -self.width:
                self.x1 = self.width
            if self.x2 <= -self.width:
                self.x2 = self.width

    def draw(self):
        if self.bg_img:
            # 绘制双份背景实现无缝滚动
            screen.blit(self.bg_img, (self.x1, 0))
            screen.blit(self.bg_img, (self.x2, 0))

# 粒子化血迹类（常驻+微动）
class BloodParticle:
    def __init__(self, area):
        # 基础位置（喷溅区域内随机）
        self.base_x = random.uniform(area["x"][0], area["x"][1])
        self.base_y = random.uniform(area["y"][0], area["y"][1])

        # 喷溅初始偏移
        angle = random.uniform(area["angle_range"][0], area["angle_range"][1])
        speed = random.uniform(*area["speed_range"])
        self.offset_x = math.cos(math.radians(angle)) * speed * random.uniform(2, 8)
        self.offset_y = math.sin(math.radians(angle)) * speed * random.uniform(2, 8)

        # 粒子属性
        self.size_type = random.choice(["large", "medium", "small"])
        self.size = random.uniform(*BLOOD_PARTICLE_SIZES[self.size_type])
        self.color = random.choice(BLOOD_COLORS)
        self.rotation = random.uniform(0, 360)
        self.rotate_dir = random.choice([-1, 1])

        # 微动参数（模拟血液粘性微动）
        self.drift_angle = random.uniform(0, 360)
        self.drift_speed = random.uniform(0, PARTICLE_DRIFT_SPEED)

    def update(self):
        """更新粒子微动和旋转（常驻不消失）"""
        # 缓慢旋转
        self.rotation += self.rotate_dir * PARTICLE_ROTATE_SPEED
        if self.rotation > 360:
            self.rotation -= 360
        elif self.rotation < 0:
            self.rotation += 360

        # 缓慢漂移（模拟空气流动）
        self.drift_angle += random.uniform(-1, 1)
        self.offset_x += math.cos(math.radians(self.drift_angle)) * self.drift_speed
        self.offset_y += math.sin(math.radians(self.drift_angle)) * self.drift_speed

        # 限制漂移范围（防止粒子移出界面）
        max_offset = 30
        self.offset_x = max(-max_offset, min(max_offset, self.offset_x))
        self.offset_y = max(-max_offset, min(max_offset, self.offset_y))

    def draw(self):
        """绘制粒子化血迹（不规则矩形+旋转）"""
        # 计算最终位置
        final_x = self.base_x + self.offset_x
        final_y = self.base_y + self.offset_y

        # 创建粒子表面（带透明度）
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

        # 绘制不规则矩形粒子（模拟血滴）
        rect_width = self.size * random.uniform(0.8, 1.2)
        rect_height = self.size * random.uniform(0.8, 1.2)
        rect_x = (self.size * 2 - rect_width) / 2 + random.uniform(-self.size / 4, self.size / 4)
        rect_y = (self.size * 2 - rect_height) / 2 + random.uniform(-self.size / 4, self.size / 4)

        pygame.draw.rect(
            particle_surface,
            (*self.color, BLOOD_ALPHA),
            (rect_x, rect_y, rect_width, rect_height)
        )

        # 绘制粒子边缘（增强喷溅效果）
        if self.size_type != "small":
            edge_size = self.size * random.uniform(0.3, 0.6)
            edge_x = random.uniform(0, self.size * 2 - edge_size)
            edge_y = random.uniform(0, self.size * 2 - edge_size)
            edge_color = random.choice([c for c in BLOOD_COLORS if c != self.color])
            pygame.draw.rect(
                particle_surface,
                (*edge_color, BLOOD_ALPHA - 50),
                (edge_x, edge_y, edge_size, edge_size)
            )

        # 旋转粒子并绘制到屏幕
        rotated_surface = pygame.transform.rotate(particle_surface, self.rotation)
        draw_x = final_x - rotated_surface.get_width() / 2
        draw_y = final_y - rotated_surface.get_height() / 2
        screen.blit(rotated_surface, (draw_x, draw_y))


# 加密/解密函数
def encrypt_data(data):
    """加密数据"""
    key = hashlib.sha256(ENCRYPTION_KEY.encode()).digest()
    encrypted = []
    for i, char in enumerate(str(data)):
        encrypted_char = chr(ord(char) ^ key[i % len(key)])
        encrypted.append(encrypted_char)
    return ''.join(encrypted)

def decrypt_data(encrypted_data):
    """解密数据"""
    key = hashlib.sha256(ENCRYPTION_KEY.encode()).digest()
    decrypted = []
    for i, char in enumerate(encrypted_data):
        decrypted_char = chr(ord(char) ^ key[i % len(key)])
        decrypted.append(decrypted_char)
    return ''.join(decrypted)

# 数据库初始化
def init_database():
    """初始化数据库，创建表结构"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # 创建游戏数据表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS game_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE,
        value TEXT
    )''')
    
    # 创建技能解锁表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS unlocked_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT,
        rarity TEXT,
        uses_left INTEGER,
        timestamp TEXT
    )''')
    
    # 创建赛季配置表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS season_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE,
        value TEXT
    )''')
    
    # 创建当前赛季表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS current_season (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        season TEXT,
        total_games INTEGER,
        total_wins INTEGER,
        highest_rank_num INTEGER,
        highest_stage_num INTEGER
    )''')
    
    # 创建历史赛季表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS season_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        season TEXT UNIQUE,
        total_games INTEGER,
        total_wins INTEGER,
        highest_rank_num INTEGER,
        highest_stage_num INTEGER,
        timestamp TEXT
    )''')
    
    # 初始化默认数据
    default_data = [
        ('total_score', '0'),
        ('rank_score', '0'),
        ('consecutive_losses', '0')
    ]
    
    for key, value in default_data:
        # 检查是否已存在
        cursor.execute("SELECT id FROM game_data WHERE key = ?", (key,))
        if not cursor.fetchone():
            encrypted_value = encrypt_data(value)
            cursor.execute("INSERT INTO game_data (key, value) VALUES (?, ?)", (key, encrypted_value))
    
    # 初始化赛季配置
    season_config_defaults = [
        ('current_season', datetime.now().strftime("%Y-%m")),
        ('last_reset', datetime.now().strftime("%Y-%m-01"))
    ]
    
    for key, value in season_config_defaults:
        # 检查是否已存在
        cursor.execute("SELECT id FROM season_config WHERE key = ?", (key,))
        if not cursor.fetchone():
            encrypted_value = encrypt_data(value)
            cursor.execute("INSERT INTO season_config (key, value) VALUES (?, ?)", (key, encrypted_value))
    
    # 初始化当前赛季数据
    cursor.execute("SELECT id FROM current_season")
    if not cursor.fetchone():
        current_season_data = (
            datetime.now().strftime("%Y-%m"),
            0,  # total_games
            0,  # total_wins
            1,  # highest_rank_num
            1   # highest_stage_num
        )
        cursor.execute("INSERT INTO current_season (season, total_games, total_wins, highest_rank_num, highest_stage_num) VALUES (?, ?, ?, ?, ?)", current_season_data)
    
    conn.commit()
    conn.close()

# 获取数据库连接
def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect(DATABASE_FILE)

# 从数据库获取值
def get_db_value(key):
    """从数据库获取值"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM game_data WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return decrypt_data(result[0])
    return None

# 向数据库设置值
def set_db_value(key, value):
    """向数据库设置值"""
    conn = get_db_connection()
    cursor = conn.cursor()
    encrypted_value = encrypt_data(value)
    cursor.execute("INSERT OR REPLACE INTO game_data (key, value) VALUES (?, ?)", (key, encrypted_value))
    conn.commit()
    conn.close()

# 获取总分数
def get_total_score():
    """获取总分数"""
    value = get_db_value('total_score')
    return int(value) if value else 0

# 保存总分数
def save_total_score(score):
    """保存总分数"""
    set_db_value('total_score', score)

# 保存总分数到数据库（避免与save_total_score函数名冲突）
def save_total_score_to_db(score):
    """保存总分数到数据库"""
    set_db_value('total_score', score)

# 计算游戏得分对应的商店积分
def calculate_score_points(game_score, game_mode):
    """计算游戏得分对应的商店积分
    排位模式：x1倍率
    练习模式：x0.25倍率
    """
    if game_mode == "ranked":
        return int(game_score * 1)
    else:
        return int(game_score * 0.25)

# 获取段位分数
def get_rank_score():
    """获取段位分数"""
    value = get_db_value('rank_score')
    return int(value) if value else 0

# 保存段位分数
def save_rank_score(score):
    """保存段位分数"""
    set_db_value('rank_score', score)

# 获取连续失败次数
def get_consecutive_losses():
    """获取连续失败次数"""
    value = get_db_value('consecutive_losses')
    return int(value) if value else 0

# 保存连续失败次数
def save_consecutive_losses(count):
    """保存连续失败次数"""
    set_db_value('consecutive_losses', count)

# 保存上次使用的技能
def save_last_used_skills(skills):
    """保存上次使用的技能列表（包含技能名称和品质）"""
    import json
    skills_data = []
    for skill_name in skills:
        if skill_name in unlocked_skills and len(unlocked_skills[skill_name]) > 0:
            # 所有技能和天赋都使用嵌套字典结构，取第一个品质
            rarity = list(unlocked_skills[skill_name].keys())[0]
            skills_data.append({"name": skill_name, "rarity": rarity})
    skills_json = json.dumps(skills_data)
    set_db_value('last_used_skills', skills_json)

# 获取上次使用的技能
def get_last_used_skills():
    """获取上次使用的技能列表（包含技能名称和品质）"""
    import json
    value = get_db_value('last_used_skills')
    if value:
        try:
            return json.loads(value)
        except:
            return []
    return []

# 资源加载（处理文件不存在的情况）
def load_resource():
    # 初始化数据库
    init_database()
    
    resources = {
        "dino_images": [],
        "health_regen_icon": None,
        "cactus_image": None,
        "bird_image": None,
        "skill1_icon": "rect",  # LAST EFFORT技能图标
        "skill2_icon": "rect",  # Quick Heal技能图标
        "speed_icon": "rect",  # 新增：速度图标
        "extra_health_icon": "rect",
        "health_icon": "rect",  # 新增：主血条图标
        "low_health_icon": "rect",  # 新增：低血量图标
        "difficulty_icon": "rect",  # 新增：难度进度图标
        "fps_boost_icon": "rect",  # 新增：FPS提升图标
        "jump_sound": None,
        "hit_sound": None,
        "score_sound": None,
        "skill_sound": None,
        "game_over_sound": None,
        "perfect_sound": None,
        "hurt_sound": None,  # 受伤音效
        "level_up_sound": None,
        "background_image": None,
        "locked_icon": None,
        "skill3_icon": "rect",  # 命之跳跃技能图标
        "jump_boost_icon": "rect"  # 新增：跳跃状态图标

    }

    try:
        health_regen_icon_img = pygame.image.load("game_pics/health_regen_icon.png").convert_alpha()
        resources["health_regen_icon"] = pygame.transform.scale(health_regen_icon_img, (ICON_SIZE, ICON_SIZE))
    except:
        resources["health_regen_icon"] = "rect"  # 加载失败用矩形兜底

    try:
        locked_icon_img = pygame.image.load("game_pics/locked_icon.png").convert_alpha()
        resources["locked_icon"] = pygame.transform.scale(locked_icon_img, (LOCKED_ICON_SIZE, LOCKED_ICON_SIZE))
    except:
        resources["locked_icon"] = "rect"  # 无图片则用矩形绘制

    try:
        bg_img = pygame.image.load("game_pics/background.png").convert()
        # 缩放背景图适配屏幕尺寸
        resources["background_image"] = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        resources["background_image"] = None  # 加载失败则设为None

    try:
        jump_boost_icon_img = pygame.image.load("game_pics/jump_boost_icon.png").convert_alpha()
        resources["jump_boost_icon"] = pygame.transform.scale(jump_boost_icon_img, (ICON_SIZE, ICON_SIZE))
    except:
        resources["jump_boost_icon"] = "rect"

    try:
        skill3_icon_img = pygame.image.load("game_pics/skill3_icon.png").convert_alpha()
        resources["skill3_icon"] = pygame.transform.scale(skill3_icon_img, (ICON_SIZE, ICON_SIZE))
    except:
        resources["skill3_icon"] = "rect"

    try:
        resources["level_up_sound"] = pygame.mixer.Sound(LEVEL_UP_SOUND_PATH)
        resources["level_up_sound"].set_volume(LEVEL_UP_SOUND_VOLUME)
    except:
        resources["level_up_sound"] = None

    try:
        difficulty_icon_img = pygame.image.load("game_pics/difficulty_icon.png").convert_alpha()
        resources["difficulty_icon"] = pygame.transform.scale(difficulty_icon_img, (ICON_SIZE, ICON_SIZE))
    except:
        resources["difficulty_icon"] = "rect"

    try:
        health_icon_img = pygame.image.load("game_pics/health_icon.png").convert_alpha()
        resources["health_icon"] = pygame.transform.scale(health_icon_img, (ICON_SIZE, ICON_SIZE))
    except:
        resources["health_icon"] = "rect"

    try:
        low_health_icon_img = pygame.image.load("game_pics/low_health_icon.png").convert_alpha()
        resources["low_health_icon"] = pygame.transform.scale(low_health_icon_img, (ICON_SIZE, ICON_SIZE))
    except:
        resources["low_health_icon"] = "rect"

    try:
        extra_health_icon_img = pygame.image.load("game_pics/extra_health_icon.png").convert_alpha()
        resources["extra_health_icon"] = pygame.transform.scale(extra_health_icon_img, (ICON_SIZE, ICON_SIZE))
    except:
        resources["extra_health_icon"] = "rect"

    try:
        speed_icon_img = pygame.image.load("game_pics/speed_icon.png").convert_alpha()
        resources["speed_icon"] = pygame.transform.scale(speed_icon_img, (ICON_SIZE, ICON_SIZE))
    except:
        resources["speed_icon"] = "rect"

    
    try:
        dino1 = pygame.image.load("game_pics/dino1.png").convert_alpha()
        dino2 = pygame.image.load("game_pics/dino2.png").convert_alpha()
        dino3 = pygame.image.load("game_pics/dino3.png").convert_alpha()
        
        resources["dino_images"] = [
            pygame.transform.scale(dino1, (100, 100)),  # 放大恐龙尺寸适配新窗口
            pygame.transform.scale(dino2, (100, 100)),
            pygame.transform.scale(dino3, (100, 100)),
            
        ]
    except:
        resources["dino_images"] = ["rect"]

    # 加载障碍物图片
    try:
        cactus = pygame.image.load("game_pics/cactus.gif").convert_alpha()
        resources["cactus_image"] = pygame.transform.scale(cactus, (60, 60))
    except:
        resources["cactus_image"] = "rect"

    try:
        bird = pygame.image.load("game_pics/birds.gif").convert_alpha()
        resources["bird_image"] = pygame.transform.scale(bird, (60, 60))
    except:
        resources["bird_image"] = "rect"

    # 尝试加载技能图标图片（如果有）
    try:
        skill1_icon_img = pygame.image.load("game_pics/skill_icon.png").convert_alpha()
        resources["skill1_icon"] = pygame.transform.scale(skill1_icon_img, (50, 50))
    except:
        resources["skill1_icon"] = "rect"

    try:
        skill2_icon_img = pygame.image.load("game_pics/heal_icon.png").convert_alpha()
        resources["skill2_icon"] = pygame.transform.scale(skill2_icon_img, (50, 50))
    except:
        resources["skill2_icon"] = "rect"

    # 加载FPS提升图标
    try:
        fps_boost_icon_img = pygame.image.load("game_pics/fps_boost_icon.png").convert_alpha()
        resources["fps_boost_icon"] = pygame.transform.scale(fps_boost_icon_img, (ICON_SIZE, ICON_SIZE))
    except:
        resources["fps_boost_icon"] = "rect"

    # 加载张狂图标
    try:
        frenzy_icon_img = pygame.image.load("game_pics/frenzy_icon.png").convert_alpha()
        resources["frenzy_icon"] = pygame.transform.scale(frenzy_icon_img, (ICON_SIZE, ICON_SIZE))
    except:
        resources["frenzy_icon"] = "rect"

    # 加载音效
    try:
        resources["jump_sound"] = pygame.mixer.Sound("music_effects/jump.mp3")
        resources["jump_sound"].set_volume(0.8)
        resources["hit_sound"] = pygame.mixer.Sound("music_effects/hurt.mp3")
        resources["hit_sound"].set_volume(0.8)
        resources["heal_sound"] = pygame.mixer.Sound("music_effects/skill.wav")
        resources["heal_sound"].set_volume(0.8)
        resources["game_over_sound"] = pygame.mixer.Sound("music_effects/death.mp3")
        resources["game_over_sound"].set_volume(0.8)
        resources["last_effort_sound"] = pygame.mixer.Sound("music_effects/last_effort.mp3")
        resources["last_effort_sound"].set_volume(0.8)
    except:
        resources["game_over_sound"] = pygame.mixer.Sound("music_effects/death.mp3")
        resources["game_over_sound"].set_volume(0.8)
        resources["heal_sound"] = pygame.mixer.Sound("music_effects/skill.wav")
        resources["heal_sound"].set_volume(0.8)
        resources["last_effort_sound"] = pygame.mixer.Sound("music_effects/last_effort.mp3")
        resources["last_effort_sound"].set_volume(0.8)
        resources["hit_sound"] = pygame.mixer.Sound("music_effects/hurt.mp3")
        resources["hit_sound"].set_volume(0.8)
        pass
    return resources


def draw_success_popup(screen, skill_names, remaining_score, animation_progress):
    """绘制购买成功弹窗（带淡入动画，适配商店同一窗口，支持多个技能）"""
    # 关键修改1：调整弹窗位置，基于商店窗口尺寸（600x400）居中，而非游戏窗口
    # 原代码：基于游戏窗口(SCREEN_WIDTH, SCREEN_HEIGHT)，现改为商店窗口(600, 400)
    popup_x = (600 - SUCCESS_POPUP_WIDTH) // 2  # 商店窗口宽度600，水平居中
    popup_y = (400 - SUCCESS_POPUP_HEIGHT) // 2 - 20  # 商店窗口高度400，垂直居中略偏上

    # 计算透明度（动画进度：0→1）


    # 创建带透明度的弹窗表面（保留原有逻辑）
    popup_surface = pygame.Surface((SUCCESS_POPUP_WIDTH, SUCCESS_POPUP_HEIGHT), pygame.SRCALPHA)

    # 绘制弹窗阴影（保留原有样式）

    # 绘制弹窗背景和边框（保留原有样式）
    pygame.draw.rect(popup_surface, SUCCESS_POPUP_BG, (0, 0, SUCCESS_POPUP_WIDTH, SUCCESS_POPUP_HEIGHT),
                     border_radius=0)
    pygame.draw.rect(popup_surface, SUCCESS_POPUP_BORDER, (0, 0, SUCCESS_POPUP_WIDTH, SUCCESS_POPUP_HEIGHT), 4,
                     border_radius=0)

    # 加载字体（保留原有逻辑）
    title_font = load_custom_font(32, bold=True)
    content_font = load_custom_font(24)
    tip_font = load_custom_font(18)

    # 绘制弹窗内容（支持多个技能）
    if len(skill_names) == 1:
        title_text = title_font.render("Skill Unlocked Successfully!", True, SUCCESS_TITLE_COLOR)
    else:
        title_text = title_font.render(f"{len(skill_names)} Skills Unlocked!", True, SUCCESS_TITLE_COLOR)
    title_rect = title_text.get_rect(center=(SUCCESS_POPUP_WIDTH // 2, 50))
    popup_surface.blit(title_text, title_rect)

    # 显示解锁的技能列表
    if len(skill_names) == 1:
        skill_text = content_font.render(f"Unlocked: {skill_names[0]}", True, SUCCESS_TEXT_COLOR)
        skill_rect = skill_text.get_rect(center=(SUCCESS_POPUP_WIDTH // 2, 100))
        popup_surface.blit(skill_text, skill_rect)
    else:
        # 显示多个技能
        y_offset = 85
        for skill in skill_names[:3]:  # 最多显示3个技能
            skill_text = content_font.render(f"• {skill}", True, SUCCESS_TEXT_COLOR)
            skill_rect = skill_text.get_rect(center=(SUCCESS_POPUP_WIDTH // 2, y_offset))
            popup_surface.blit(skill_text, skill_rect)
            y_offset += 25
        if len(skill_names) > 3:
            more_text = content_font.render(f"...and {len(skill_names) - 3} more", True, SUCCESS_TEXT_COLOR)
            more_rect = more_text.get_rect(center=(SUCCESS_POPUP_WIDTH // 2, y_offset))
            popup_surface.blit(more_text, more_rect)
            y_offset += 25

    score_text = content_font.render(f"Remaining Score: {remaining_score}", True, SUCCESS_TEXT_COLOR)
    score_rect = score_text.get_rect(center=(SUCCESS_POPUP_WIDTH // 2, y_offset + 10))
    popup_surface.blit(score_text, score_rect)

    tip_text = tip_font.render("Game will restart automatically...", True, GRAY_MEDIUM)
    tip_rect = tip_text.get_rect(center=(SUCCESS_POPUP_WIDTH // 2, y_offset + 50))
    popup_surface.blit(tip_text, tip_rect)

    # 设置弹窗透明度并绘制到屏幕（保留原有逻辑，screen此时是商店窗口）

    screen.blit(popup_surface, (popup_x, popup_y))

def save_total_score(game_score, dino, game_mode="ranked"):
    """Calculate and save rank points
    New mechanism: 
    - Part 1: Game score × obstacle accuracy - skill usage count × 20
    - Part 2: Victory score (when reaching MAX_SCORE)
      Rank 1: 100 × (1 + 100%) = 200
      Rank 2: 100 × (1 + 80%) = 180
      Rank 3: 100 × (1 + 60%) = 160
      Rank 4: 100 × (1 + 40%) = 140
      Rank 5: 100 × (1 + 20%) = 120
      Rank 6: No extra score
    - Part 3: Skill usage bonus
      +100 points for skill usage (if any skill was used during the game)
    - Part 4: Consecutive loss bonus
      +150 points for ending losing streak (3+ consecutive losses followed by victory)
      +50 points for lucky survival (3+ consecutive losses followed by normal ending)
    - Low score penalty: Deduct 300 rank points when game score < 200
    - Rank protection: Ranks 1-5 have protection, rank 6 has none
      Protection rates: Rank 1 50%, Rank 2 40%, Rank 3 30%, Rank 4 20%, Rank 5 10%
      Actual deduction = 300 - 300 × protection rate
    - Score points: Ranked mode x1, Practice mode x0.25
    Returns: (change_type, change_value, details) - change_type: "add" or "deduct"
    Details: Dictionary containing detailed calculation information
    """
    # 读取段位分（从数据库）
    total = get_rank_score()
    
    # 获取当前段位信息（用于段位保护和胜利得分）
    rank_num, stage_num, _, _, rank_name, _, _ = calculate_rank(total)
    
    # 保存游戏总分数到数据库（用于积分商店，根据模式应用倍率）
    current_total_score = get_total_score()
    shop_points = calculate_score_points(game_score, game_mode)
    new_total_score = current_total_score + shop_points
    save_total_score_to_db(new_total_score)
    
    # 段位保护比例（0-5阶有保护，6阶和Honor无保护即0%）
    # 扣除10-10×保护比例
    protection_rates = {0: 1.00, 1: 0.50, 2: 0.40, 3: 0.30, 4: 0.20, 5: 0.10, 6: 0.00}
    protection_rate = protection_rates.get(rank_num, 0.00)
    
    # 初始化详情字典
    details = {
        "game_score": game_score,
        "base_score": 0,
        "win_score": 0,
        "skill_usage_bonus": 0,
        "consecutive_loss_bonus": 0,
        "low_score_penalty": 0,
        "protection_amount": 0,
        "normal_protection_score": 0,
        "rank_num": rank_num
    }
    
    # 读取连续失败次数
    consecutive_losses = get_consecutive_losses()
    
    # 判断是否为低分（低于200分）
    if game_score < 200:
        # 低分惩罚：扣除10段位分，但应用段位保护
        # 实际扣分 = 10 - 10 × 保护比例
        protection_amount = int(10 * protection_rate)
        actual_deduct = int(10 - protection_amount)
        actual_deduct = min(actual_deduct, total)  # 不能扣成负数
        total = max(0, total - actual_deduct)
        
        details["low_score_penalty"] = 10
        details["protection_amount"] = protection_amount
        
        # 更新连续失败次数
        save_consecutive_losses(consecutive_losses + 1)
        
        # 保存段位分到数据库
        save_rank_score(total)
        # 计算新段位
        new_rank_num, new_stage_num, _, _, new_rank_name, new_stage_name, _ = calculate_rank(total)
        # 检测段位变化（所有段位逻辑一致：stage_num越大，段位越高）
        rank_change = None
        # 特殊处理：从Rank 6升到Honor
        if rank_name == "Rank 6" and new_rank_name == "Honor":
            rank_change = ("promotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        # 特殊处理：从Honor掉回Rank 6
        elif rank_name == "Honor" and new_rank_name == "Rank 6":
            rank_change = ("demotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        elif new_rank_num > rank_num:
            rank_change = ("promotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        elif new_rank_num < rank_num:
            rank_change = ("demotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        elif new_rank_num == rank_num:
            if new_stage_num > stage_num:
                rank_change = ("promotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
            elif new_stage_num < stage_num:
                rank_change = ("demotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        return ("deduct", actual_deduct, details, rank_change)
    
    # 计算越过障碍物准确率
    if dino.obstacles_total > 0:
        accuracy = dino.obstacles_cleared / dino.obstacles_total
    else:
        accuracy = 1.0  # 如果没有障碍物，准确率100%
    
    # 第一部分：基础得分
    base_score = int(game_score * accuracy * 0.02 - dino.skill_usage_count * 0.05)
    
    # 第二部分：胜利得分（达到MAX_SCORE时）
    win_score = 0
    if game_score >= MAX_SCORE and rank_num <= 6:
        # 胜利得分：5 × 加成比例
        # Rank 0-1: 100%, Rank 2: 80%, Rank 3: 60%, Rank 4: 40%, Rank 5: 20%, Rank 6和Honor: 0%
        win_multipliers = {0: 1.0, 1: 1.0, 2: 0.8, 3: 0.6, 4: 0.4, 5: 0.2, 6: 0.0}
        multiplier = win_multipliers.get(rank_num, 1.0)
        win_score = int(5 * multiplier)
    
    # 第三部分：技能使用额外得分
    skill_usage_bonus = 0
    if dino.skill_usage_count > 0:
        skill_usage_bonus = 2
    
    # 第四部分：连续失败奖励
    consecutive_loss_bonus = 0
    if consecutive_losses >= 3:
        if game_score >= MAX_SCORE:
            # 连续3次失败后胜利
            consecutive_loss_bonus = 6
        elif game_score >= 200:
            # 连续3次失败后普通结局
            consecutive_loss_bonus = 4
    
    # 第五部分：普通保护得分（200 <= game_score < MAX_SCORE时）
    normal_protection_score = 0
    if 200 <= game_score < MAX_SCORE:
        # 普通保护得分：3 × 加成比例
        # Rank 0-1: 100%, Rank 2: 50%, Rank 3: 40%, Rank 4: 30%, Rank 5: 20%, Rank 6和Honor: 0%
        normal_multipliers = {0: 1.0, 1: 1.0, 2: 0.5, 3: 0.4, 4: 0.3, 5: 0.2, 6: 0.0}
        normal_multiplier = normal_multipliers.get(rank_num, 1.0)
        normal_protection_score = int(3 * normal_multiplier)
    
    # 总段位分
    rank_score = base_score + win_score + skill_usage_bonus + consecutive_loss_bonus + normal_protection_score
    
    details["base_score"] = base_score
    details["win_score"] = win_score
    details["skill_usage_bonus"] = skill_usage_bonus
    details["consecutive_loss_bonus"] = consecutive_loss_bonus
    details["normal_protection_score"] = normal_protection_score
    
    # 更新连续失败次数
    if game_score < 200:
        # 失败结局，连续失败次数+1
        save_consecutive_losses(consecutive_losses + 1)
    else:
        # 普通或胜利结局，重置连续失败次数
        save_consecutive_losses(0)
    
    # 计算新总分
    if rank_score < 0:
        # 扣分情况（非低分惩罚的普通扣分）
        actual_deduct = min(abs(rank_score), total)
        total = max(0, total - actual_deduct)
        # 保存段位分到数据库
        save_rank_score(total)
        # 计算新段位
        new_rank_num, new_stage_num, _, _, new_rank_name, new_stage_name, _ = calculate_rank(total)
        # 检测段位变化
        rank_change = None
        # 特殊处理：从Rank 6升到Honor
        if rank_name == "Rank 6" and new_rank_name == "Honor":
            rank_change = ("promotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        # 特殊处理：从Honor掉回Rank 6
        elif rank_name == "Honor" and new_rank_name == "Rank 6":
            rank_change = ("demotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        elif new_rank_num > rank_num or (new_rank_num == rank_num and new_stage_num < stage_num):
            rank_change = ("promotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        elif new_rank_num < rank_num or (new_rank_num == rank_num and new_stage_num > stage_num):
            rank_change = ("demotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        return ("deduct", actual_deduct, details, rank_change)
    else:
        # 加分情况
        total += rank_score
        # 保存段位分到数据库
        save_rank_score(total)
        # 计算新段位
        new_rank_num, new_stage_num, _, _, new_rank_name, new_stage_name, _ = calculate_rank(total)
        # 检测段位变化（所有段位逻辑一致：stage_num越大，段位越高）
        rank_change = None
        # 特殊处理：从Rank 6升到Honor
        if rank_name == "Rank 6" and new_rank_name == "Honor":
            rank_change = ("promotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        # 特殊处理：从Honor掉回Rank 6
        elif rank_name == "Honor" and new_rank_name == "Rank 6":
            rank_change = ("demotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        elif new_rank_num > rank_num:
            rank_change = ("promotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        elif new_rank_num < rank_num:
            rank_change = ("demotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        elif new_rank_num == rank_num:
            if new_stage_num > stage_num:
                rank_change = ("promotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
            elif new_stage_num < stage_num:
                rank_change = ("demotion", new_rank_name, new_stage_name, new_rank_num, new_stage_num)
        return ("add", rank_score, details, rank_change)



def load_unlocked_skills():
    """从数据库读取已解锁技能，返回字典
    
    所有技能和天赋都支持多品质：
    {skill_name: {rarity: {rarity: str, uses_left: int}, ...}}
    """
    unlocked_skills = {}
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询所有已解锁的技能
    cursor.execute("SELECT skill_name, rarity, uses_left FROM unlocked_skills")
    skills = cursor.fetchall()
    conn.close()
    
    for skill_name, rarity, uses_left in skills:
        # 所有技能和天赋都支持多个品质
        if skill_name in ["Brave Dash", "Zoom Boost", "Lucky Leap"]:
            # 技能
            if rarity not in SKILL_RARITY:
                rarity = "legendary"
        elif skill_name == "Frenzy":
            # 天赋
            if rarity not in ITEM_RARITY["frenzy"]:
                rarity = "rare"
        elif skill_name == "Agility":
            # 天赋
            if rarity not in ITEM_RARITY["agility"]:
                rarity = "rare"
        
        # 使用嵌套字典存储多个品质
        if skill_name not in unlocked_skills:
            unlocked_skills[skill_name] = {}
        unlocked_skills[skill_name][rarity] = {"rarity": rarity, "uses_left": uses_left}
    return unlocked_skills

def get_unlocked_rarities(skill_name):
    """获取某个技能/天赋所有已解锁的品质列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT rarity FROM unlocked_skills WHERE skill_name = ?", (skill_name,))
    rarities = [row[0] for row in cursor.fetchall()]
    conn.close()
    return rarities

def save_unlocked_skill(skill_name, rarity="legendary"):
    """将解锁的技能或道具保存到数据库"""
    # 计算使用次数
    if skill_name in ["Brave Dash", "Zoom Boost", "Lucky Leap"]:
        uses = SKILL_RARITY[rarity]["uses"]
    elif skill_name == "Frenzy":
        if rarity not in ITEM_RARITY["frenzy"]:
            rarity = "rare"
        uses = ITEM_RARITY["frenzy"][rarity]["uses"]
    elif skill_name == "Agility":
        if rarity not in ITEM_RARITY["agility"]:
            rarity = "rare"
        uses = ITEM_RARITY["agility"][rarity]["uses"]
    else:
        uses = 1
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查技能是否已存在
    cursor.execute("SELECT id FROM unlocked_skills WHERE skill_name = ? AND rarity = ?", (skill_name, rarity))
    if not cursor.fetchone():
        # 插入新技能
        timestamp = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO unlocked_skills (skill_name, rarity, uses_left, timestamp) VALUES (?, ?, ?, ?)",
            (skill_name, rarity, uses, timestamp)
        )
        conn.commit()
    conn.close()


def load_season_config():
    """加载赛季配置"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 读取配置
    cursor.execute("SELECT key, value FROM season_config")
    config = {}
    for key, encrypted_value in cursor.fetchall():
        config[key] = decrypt_data(encrypted_value)
    
    conn.close()
    
    # 如果没有配置，返回默认配置
    if not config:
        return {
            "current_season": datetime.now().strftime("%Y-%m"),
            "last_reset": datetime.now().strftime("%Y-%m-01")
        }
    
    return config


def save_season_config(config):
    """保存赛季配置"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for key, value in config.items():
        encrypted_value = encrypt_data(value)
        cursor.execute("INSERT OR REPLACE INTO season_config (key, value) VALUES (?, ?)", (key, encrypted_value))
    
    conn.commit()
    conn.close()


def load_current_season():
    """加载当前赛季数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT season, total_games, total_wins, highest_rank_num, highest_stage_num FROM current_season LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    
    if result:
        season, total_games, total_wins, highest_rank_num, highest_stage_num = result
        return {
            "season": season,
            "total_games": total_games,
            "total_wins": total_wins,
            "highest_rank": {
                "rank_num": highest_rank_num,
                "stage_num": highest_stage_num
            }
        }
    else:
        # 默认数据
        return {
            "season": datetime.now().strftime("%Y-%m"),
            "total_games": 0,
            "total_wins": 0,
            "highest_rank": {
                "rank_num": 1,
                "stage_num": 1
            }
        }


def save_current_season(data):
    """保存当前赛季数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 先检查是否存在记录
    cursor.execute("SELECT id FROM current_season")
    if cursor.fetchone():
        # 更新现有记录
        cursor.execute("UPDATE current_season SET season = ?, total_games = ?, total_wins = ?, highest_rank_num = ?, highest_stage_num = ?", 
                      (data["season"], data["total_games"], data["total_wins"], 
                       data["highest_rank"]["rank_num"], data["highest_rank"]["stage_num"]))
    else:
        # 插入新记录
        cursor.execute("INSERT INTO current_season (season, total_games, total_wins, highest_rank_num, highest_stage_num) VALUES (?, ?, ?, ?, ?)", 
                      (data["season"], data["total_games"], data["total_wins"], 
                       data["highest_rank"]["rank_num"], data["highest_rank"]["stage_num"]))
    
    conn.commit()
    conn.close()


def check_season_reset():
    """检查是否需要重置赛季"""
    config = load_season_config()
    current_date = datetime.now()
    last_reset_date = datetime.strptime(config["last_reset"], "%Y-%m-%d")
    
    # 检查是否到了新的月份
    if (current_date.year > last_reset_date.year) or \
       (current_date.year == last_reset_date.year and current_date.month > last_reset_date.month):
        # 重置赛季
        reset_season()


def reset_season():
    """重置赛季"""
    # 保存当前赛季为历史赛季
    current_season = load_current_season()
    if current_season["total_games"] > 0:
        # 保存到历史赛季表
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否已存在该赛季的历史记录
        cursor.execute("SELECT id FROM season_history WHERE season = ?", (current_season['season'],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO season_history (season, total_games, total_wins, highest_rank_num, highest_stage_num, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                          (current_season['season'], current_season['total_games'], current_season['total_wins'],
                           current_season['highest_rank']['rank_num'], current_season['highest_rank']['stage_num'],
                           datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
        
        conn.close()
    
    # 重置段位分
    save_rank_score(0)
    
    # 创建新赛季
    new_season = datetime.now().strftime("%Y-%m")
    new_season_data = {
        "season": new_season,
        "total_games": 0,
        "total_wins": 0,
        "highest_rank": {
            "rank_num": 1,
            "stage_num": 1
        }
    }
    save_current_season(new_season_data)
    
    # 更新赛季配置
    config = load_season_config()
    config["current_season"] = new_season
    config["last_reset"] = datetime.now().strftime("%Y-%m-01")
    save_season_config(config)


def update_season_data(score):
    """更新赛季数据"""
    # 检查赛季重置
    check_season_reset()
    
    # 加载当前赛季数据
    season_data = load_current_season()
    
    # 更新游戏场次
    if score < 200:
        # 失败结局，增加总场次但不增加胜利次数
        season_data["total_games"] += 1
    elif score >= MAX_SCORE:
        # 胜利结局，计入胜率计算
        season_data["total_games"] += 1
        season_data["total_wins"] += 1
    else:
        # 普通结局，增加总场次但不增加胜利次数
        season_data["total_games"] += 1
    
    # 更新最高段位
    rank_num, stage_num, _, _, _, _, _ = get_rank_info()
    current_highest = season_data["highest_rank"]
    if (rank_num > current_highest["rank_num"]) or \
       (rank_num == current_highest["rank_num"] and stage_num > current_highest["stage_num"]):
        season_data["highest_rank"] = {
            "rank_num": rank_num,
            "stage_num": stage_num
        }
    
    # 保存赛季数据
    save_current_season(season_data)


def get_season_stats():
    """获取当前赛季统计数据"""
    check_season_reset()
    season_data = load_current_season()
    
    # 计算胜率
    if season_data["total_games"] > 0:
        win_rate = (season_data["total_wins"] / season_data["total_games"]) * 100
    else:
        win_rate = 0
    
    return {
        "total_games": season_data["total_games"],
        "total_wins": season_data["total_wins"],
        "win_rate": win_rate,
        "highest_rank": season_data["highest_rank"]
    }


def get_historical_seasons():
    """获取历史赛季数据"""
    historical_seasons = []
    
    # 从数据库读取历史赛季
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT season, total_games, total_wins, highest_rank_num, highest_stage_num FROM season_history ORDER BY season DESC")
    results = cursor.fetchall()
    
    conn.close()
    
    for season, total_games, total_wins, highest_rank_num, highest_stage_num in results:
        # 计算胜率
        if total_games > 0:
            win_rate = (total_wins / total_games) * 100
        else:
            win_rate = 0
        
        historical_seasons.append({
            "season": season,
            "total_games": total_games,
            "total_wins": total_wins,
            "win_rate": win_rate,
            "highest_rank": {
                "rank_num": highest_rank_num,
                "stage_num": highest_stage_num
            }
        })
    
    return historical_seasons


# 历史战绩加密密钥（简单的异或加密）
GAME_HISTORY_KEY = b"EscapeGame2024"
GAME_HISTORY_FILE = "game_history.dat"

def encrypt_game_history(data, key):
    """使用异或加密游戏历史数据"""
    json_data = json.dumps(data).encode('utf-8')
    encrypted = bytearray()
    for i, byte in enumerate(json_data):
        encrypted.append(byte ^ key[i % len(key)])
    return base64.b64encode(bytes(encrypted)).decode('utf-8')

def decrypt_game_history(encrypted_data, key):
    """解密游戏历史数据"""
    try:
        decoded = base64.b64decode(encrypted_data)
        decrypted = bytearray()
        for i, byte in enumerate(decoded):
            decrypted.append(byte ^ key[i % len(key)])
        return json.loads(bytes(decrypted).decode('utf-8'))
    except:
        return []

def save_game_history(game_data):
    """保存游戏战绩到加密文件"""
    history = load_game_history()
    history.insert(0, game_data)  # 新记录添加到开头
    # 只保留最近100条记录
    history = history[:100]
    encrypted = encrypt_game_history(history, GAME_HISTORY_KEY)
    with open(GAME_HISTORY_FILE, 'w') as f:
        f.write(encrypted)

def load_game_history():
    """从加密文件加载游戏战绩"""
    if not os.path.exists(GAME_HISTORY_FILE):
        return []
    try:
        with open(GAME_HISTORY_FILE, 'r') as f:
            encrypted = f.read()
        return decrypt_game_history(encrypted, GAME_HISTORY_KEY)
    except:
        return []

def open_game_history():
    """历史战绩查看页面"""
    global start_menu_bgm
    
    # 加载历史战绩数据
    game_history = load_game_history()
    
    # 字体设置
    title_font = load_custom_font(32, bold=True)
    medium_font = load_custom_font(24)
    shop_font = load_custom_font(20)
    small_font = load_custom_font(16)
    
    margin = 30
    
    # 滚动相关变量
    scroll_offset = 0
    scroll_speed = 30
    content_height = 100  # 每条战绩的高度
    spacing = 15  # 战绩之间的间距
    item_height = content_height + spacing
    # 计算可用高度
    available_height = SCREEN_HEIGHT - 125 - 50
    visible_items = int(available_height / item_height)
    max_scroll = max(0, len(game_history) - visible_items) * item_height
    
    # 返回按钮矩形
    back_button_rect = pygame.Rect(margin, margin, 80, 36)
    
    # 滚动条相关
    scrollbar_dragging = False
    scrollbar_thumb_rect = None
    
    while True:
        # 绘制纯色背景
        screen.fill(BACKGROUND_COLOR)
        
        # 获取鼠标位置
        mouse_pos = pygame.mouse.get_pos()
        
        # 按钮悬停颜色
        BUTTON_HOVER_COLOR = (56, 151, 190)
        
        # 绘制返回按钮
        back_button_color = BUTTON_HOVER_COLOR if back_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
        pygame.draw.rect(screen, back_button_color, back_button_rect)
        pygame.draw.rect(screen, GRAY_LIGHT, back_button_rect, 2)
        back_button_text = small_font.render("Back", True, WHITE)
        screen.blit(back_button_text, (back_button_rect.x + (back_button_rect.width - back_button_text.get_width()) // 2, back_button_rect.y + (back_button_rect.height - back_button_text.get_height()) // 2))
        
        # 标题区域
        title_text = title_font.render("Game History", True, PRIMARY_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))
        
        # 统计信息
        stats_text = shop_font.render(f"Total Games: {len(game_history)}", True, GRAY_DARK)
        screen.blit(stats_text, (margin, 80))
        
        # 创建裁剪区域用于历史战绩滚动
        history_area_top = 110
        history_area_bottom = SCREEN_HEIGHT - 50
        history_area_height = history_area_bottom - history_area_top
        history_clip_rect = pygame.Rect(margin, history_area_top, SCREEN_WIDTH - 2 * margin - 20, history_area_height)
        
        # 显示历史战绩数据（带滚动）
        if game_history:
            # 保存当前裁剪区域
            old_clip = screen.get_clip()
            # 设置裁剪区域
            screen.set_clip(history_clip_rect)
            
            for i, game in enumerate(game_history):
                item_y = history_area_top + i * item_height - scroll_offset
                
                # 只绘制可见区域内的项目
                if item_y + item_height > history_area_top and item_y < history_area_bottom:
                    # 绘制战绩卡片背景
                    card_rect = pygame.Rect(margin + 10, item_y, SCREEN_WIDTH - 2 * margin - 40, content_height)
                    pygame.draw.rect(screen, (240, 240, 240), card_rect)
                    pygame.draw.rect(screen, GRAY_LIGHT, card_rect, 2)
                    
                    # 日期时间
                    datetime_text = shop_font.render(f"{game.get('datetime', 'Unknown')}", True, PRIMARY_COLOR)
                    screen.blit(datetime_text, (margin + 25, item_y + 10))
                    
                    # 分数信息
                    score_text = shop_font.render(f"Score: {game.get('score', 0)}  High Score: {game.get('high_score', 0)}", True, GRAY_DARK)
                    screen.blit(score_text, (margin + 25, item_y + 35))
                    
                    # 游戏结果和模式
                    result_color = (76, 175, 80) if game.get('won', False) else (244, 67, 54)
                    result_text = "Victory" if game.get('won', False) else "Defeat"
                    result_render = shop_font.render(result_text, True, result_color)
                    screen.blit(result_render, (margin + 25, item_y + 60))
                    
                    mode_text = small_font.render(f"Mode: {game.get('mode', 'Practice')}", True, GRAY_DARK)
                    screen.blit(mode_text, (margin + 150, item_y + 62))
                    
                    # 携带技能
                    skills = game.get('skills', [])
                    if skills:
                        skills_str = ", ".join(skills[:3])  # 只显示前3个技能
                        if len(skills) > 3:
                            skills_str += "..."
                        skills_text = small_font.render(f"Skills: {skills_str}", True, GRAY_DARK)
                        screen.blit(skills_text, (SCREEN_WIDTH // 2, item_y + 62))
            
            # 恢复裁剪区域
            screen.set_clip(old_clip)
            
            # 绘制滚动条背景
            scrollbar_x = SCREEN_WIDTH - margin - 15
            scrollbar_height = history_area_height
            pygame.draw.rect(screen, GRAY_LIGHT, (scrollbar_x, history_area_top, 10, scrollbar_height), border_radius=5)
            
            # 绘制滚动条滑块
            if len(game_history) > visible_items:
                thumb_height = max(40, scrollbar_height * visible_items / len(game_history))
                thumb_y = history_area_top + (scroll_offset / max_scroll) * (scrollbar_height - thumb_height) if max_scroll > 0 else history_area_top
                scrollbar_thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 10, thumb_height)
                thumb_color = BUTTON_HOVER_COLOR if scrollbar_dragging or scrollbar_thumb_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
                pygame.draw.rect(screen, thumb_color, scrollbar_thumb_rect, border_radius=5)
        else:
            no_history_text = medium_font.render("No game history found", True, GRAY_DARK)
            screen.blit(no_history_text, (SCREEN_WIDTH // 2 - no_history_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        pygame.display.flip()
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 检查是否点击了返回按钮
                if back_button_rect.collidepoint(event.pos):
                    # 重新加载开始界面BGM
                    if start_menu_bgm is None:
                        try:
                            start_menu_bgm = pygame.mixer.Sound(START_MENU_BGM_PATH)
                            start_menu_bgm.set_volume(START_MENU_BGM_VOLUME)
                            start_menu_bgm.play(-1)
                        except:
                            pass
                    return
                # 检查是否点击了滚动条滑块
                if scrollbar_thumb_rect and scrollbar_thumb_rect.collidepoint(event.pos):
                    scrollbar_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                scrollbar_dragging = False
            elif event.type == pygame.MOUSEMOTION and scrollbar_dragging:
                # 拖动滚动条
                if len(game_history) > visible_items:
                    _, mouse_y = event.pos
                    scrollbar_top = history_area_top
                    scrollbar_bottom = history_area_top + history_area_height
                    thumb_height = max(40, scrollbar_height * visible_items / len(game_history))
                    available_thumb_space = scrollbar_bottom - scrollbar_top - thumb_height
                    
                    # 计算新的滚动位置
                    relative_y = mouse_y - scrollbar_top - thumb_height // 2
                    scroll_ratio = max(0, min(1, relative_y / available_thumb_space))
                    scroll_offset = int(scroll_ratio * max_scroll)
            elif event.type == pygame.MOUSEWHEEL:
                # 鼠标滚轮滚动
                if event.y > 0:
                    scroll_offset = max(0, scroll_offset - scroll_speed)
                elif event.y < 0:
                    scroll_offset = min(max_scroll, scroll_offset + scroll_speed)


def open_season_history():
    """历史赛季查看页面"""
    global start_menu_bgm
    
    # 加载历史赛季数据
    historical_seasons = get_historical_seasons()
    
    # 加载当前赛季数据
    current_season = load_current_season()
    # 计算当前赛季胜率
    if current_season["total_games"] > 0:
        current_win_rate = (current_season["total_wins"] / current_season["total_games"]) * 100
    else:
        current_win_rate = 0
    
    # 字体设置
    title_font = load_custom_font(32, bold=True)
    medium_font = load_custom_font(24)
    shop_font = load_custom_font(20)
    small_font = load_custom_font(16)
    
    margin = 30
    column_width = (SCREEN_WIDTH - 3 * margin) // 2
    
    # 滚动相关变量
    scroll_offset = 0
    scroll_speed = 30
    content_height = 85  # 赛季内容高度
    spacing = 15  # 赛季之间的间距
    item_height = content_height + spacing  # 总高度包括间距
    # 计算可用高度（屏幕高度 - 标题区域 - 底部提示区域）
    available_height = SCREEN_HEIGHT - 125 - 50
    visible_items = int(available_height / item_height)
    max_scroll = max(0, len(historical_seasons) - visible_items) * item_height
    
    # 返回按钮矩形
    back_button_rect = pygame.Rect(margin, margin, 80, 36)
    
    # 滚动条相关
    scrollbar_dragging = False
    scrollbar_thumb_rect = None
    
    while True:
        # 绘制纯色背景
        screen.fill(BACKGROUND_COLOR)
        
        # 获取鼠标位置
        mouse_pos = pygame.mouse.get_pos()
        
        # 按钮悬停颜色
        BUTTON_HOVER_COLOR = (56, 151, 190)
        
        # 绘制返回按钮
        back_button_color = BUTTON_HOVER_COLOR if back_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
        pygame.draw.rect(screen, back_button_color, back_button_rect)
        pygame.draw.rect(screen, GRAY_LIGHT, back_button_rect, 2)
        back_button_text = small_font.render("Back", True, WHITE)
        screen.blit(back_button_text, (back_button_rect.x + (back_button_rect.width - back_button_text.get_width()) // 2, back_button_rect.y + (back_button_rect.height - back_button_text.get_height()) // 2))
        
        # 标题区域
        title_text = title_font.render("Season History", True, PRIMARY_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))
        
        # 左列：当前赛季信息
        left_column_x = margin
        current_season_text = medium_font.render("Current Season", True, SECONDARY_COLOR)
        screen.blit(current_season_text, (left_column_x, 80))
        pygame.draw.line(screen, GRAY_LIGHT, (left_column_x, 110), (left_column_x + column_width, 110), 2)
        
        # 显示当前赛季数据
        current_data_y = 125
        season_text = shop_font.render(f"Season: {current_season['season']}", True, PRIMARY_COLOR)
        screen.blit(season_text, (left_column_x + 20, current_data_y))
        
        games_text = shop_font.render(f"Games: {current_season['total_games']}", True, PRIMARY_COLOR)
        screen.blit(games_text, (left_column_x + 20, current_data_y + 25))
        
        wins_text = shop_font.render(f"Wins: {current_season['total_wins']}", True, PRIMARY_COLOR)
        screen.blit(wins_text, (left_column_x + 20, current_data_y + 50))
        
        win_rate_text = shop_font.render(f"Win Rate: {current_win_rate:.1f}%", True, PRIMARY_COLOR)
        screen.blit(win_rate_text, (left_column_x + 20, current_data_y + 75))
        
        highest_rank = current_season["highest_rank"]
        rank_text = shop_font.render(f"Highest: Rank {highest_rank['rank_num']} Stage {highest_rank['stage_num']}", True, SECONDARY_COLOR)
        screen.blit(rank_text, (left_column_x + 20, current_data_y + 100))
        
        # 右列：历史赛季信息（可滚动）
        right_column_x = 2 * margin + column_width
        history_title_text = medium_font.render("Historical Seasons", True, SECONDARY_COLOR)
        screen.blit(history_title_text, (right_column_x, 80))
        pygame.draw.line(screen, GRAY_LIGHT, (right_column_x, 110), (right_column_x + column_width, 110), 2)
        
        # 创建裁剪区域用于历史赛季滚动（确保不超出按键说明上方）
        history_area_top = 125
        history_area_bottom = SCREEN_HEIGHT - 50  # 按键说明上方
        history_area_height = history_area_bottom - history_area_top
        history_clip_rect = pygame.Rect(right_column_x, history_area_top, column_width, history_area_height)
        
        # 显示历史赛季数据（带滚动）
        if historical_seasons:
            # 保存当前裁剪区域
            old_clip = screen.get_clip()
            # 设置裁剪区域
            screen.set_clip(history_clip_rect)
            
            for i, season in enumerate(historical_seasons):
                item_y = history_area_top + i * item_height - scroll_offset
                
                # 只绘制可见区域内的项目
                if item_y + item_height > history_area_top and item_y < history_area_bottom:
                    season_text = shop_font.render(f"Season: {season['season']}", True, PRIMARY_COLOR)
                    screen.blit(season_text, (right_column_x + 20, item_y))
                    
                    games_text = shop_font.render(f"Games: {season['total_games']}", True, PRIMARY_COLOR)
                    screen.blit(games_text, (right_column_x + 20, item_y + 17))
                    
                    wins_text = shop_font.render(f"Wins: {season['total_wins']}", True, PRIMARY_COLOR)
                    screen.blit(wins_text, (right_column_x + 20, item_y + 34))
                    
                    win_rate_text = shop_font.render(f"Win Rate: {season['win_rate']:.1f}%", True, PRIMARY_COLOR)
                    screen.blit(win_rate_text, (right_column_x + 20, item_y + 51))
                    
                    highest_rank = season['highest_rank']
                    rank_text = shop_font.render(f"Highest: Rank {highest_rank['rank_num']} Stage {highest_rank['stage_num']}", True, SECONDARY_COLOR)
                    screen.blit(rank_text, (right_column_x + 20, item_y + 68))
            
            # 恢复裁剪区域
            screen.set_clip(old_clip)
            
            # 绘制滚动条背景
            scrollbar_x = right_column_x + column_width - 10
            scrollbar_height = history_area_height
            pygame.draw.rect(screen, GRAY_LIGHT, (scrollbar_x, history_area_top, 10, scrollbar_height), border_radius=5)
            
            # 绘制滚动条滑块
            if len(historical_seasons) > visible_items:
                thumb_height = max(40, scrollbar_height * visible_items / len(historical_seasons))
                thumb_y = history_area_top + (scroll_offset / max_scroll) * (scrollbar_height - thumb_height) if max_scroll > 0 else history_area_top
                scrollbar_thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 10, thumb_height)
                thumb_color = BUTTON_HOVER_COLOR if scrollbar_dragging or scrollbar_thumb_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
                pygame.draw.rect(screen, thumb_color, scrollbar_thumb_rect, border_radius=5)
        else:
            no_history_text = shop_font.render("No historical seasons found", True, GRAY_DARK)
            screen.blit(no_history_text, (right_column_x + 20, 125))
        
        pygame.display.flip()
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 检查是否点击了返回按钮
                if back_button_rect.collidepoint(event.pos):
                    # 重新加载开始界面BGM
                    if start_menu_bgm is None:
                        try:
                            start_menu_bgm = pygame.mixer.Sound(START_MENU_BGM_PATH)
                            start_menu_bgm.set_volume(START_MENU_BGM_VOLUME)
                            start_menu_bgm.play(-1)
                        except:
                            pass
                    return
                # 检查是否点击了滚动条滑块
                if scrollbar_thumb_rect and scrollbar_thumb_rect.collidepoint(event.pos):
                    scrollbar_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                scrollbar_dragging = False
            elif event.type == pygame.MOUSEMOTION and scrollbar_dragging:
                # 拖动滚动条
                if len(historical_seasons) > visible_items:
                    _, mouse_y = event.pos
                    scrollbar_top = history_area_top
                    scrollbar_bottom = history_area_top + history_area_height
                    thumb_height = max(40, scrollbar_height * visible_items / len(historical_seasons))
                    available_thumb_space = scrollbar_bottom - scrollbar_top - thumb_height
                    
                    # 计算新的滚动位置
                    relative_y = mouse_y - scrollbar_top - thumb_height // 2
                    scroll_ratio = max(0, min(1, relative_y / available_thumb_space))
                    scroll_offset = int(scroll_ratio * max_scroll)
            elif event.type == pygame.MOUSEWHEEL:
                # 鼠标滚轮滚动
                if event.y > 0:
                    scroll_offset = max(0, scroll_offset - scroll_speed)
                elif event.y < 0:
                    scroll_offset = min(max_scroll, scroll_offset + scroll_speed)


def open_developer_tool():
    """开发者工具 - 快捷修改段位分和商店积分"""
    global start_menu_bgm
    
    # 字体设置
    title_font = load_custom_font(32, bold=True)
    medium_font = load_custom_font(24)
    shop_font = load_custom_font(20)
    small_font = load_custom_font(16)
    
    margin = 30
    
    # 输入框相关变量
    input_active = False
    shop_input_active = False
    input_text = str(get_rank_score())
    shop_input_text = str(get_total_score())
    input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 320, 200, 300, 40)
    shop_input_rect = pygame.Rect(SCREEN_WIDTH // 2 + 20, 200, 300, 40)
    color_inactive = GRAY_LIGHT
    color_active = SECONDARY_COLOR
    color = color_inactive
    shop_color = color_inactive
    
    while True:
        # 绘制纯色背景
        screen.fill(BACKGROUND_COLOR)
        
        # 标题区域
        title_text = title_font.render("Developer Tool", True, PRIMARY_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))
        
        # 副标题
        subtitle_text = shop_font.render("Quick Score Modification", True, GRAY_DARK)
        screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, 80))
        
        # 段位分输入区域
        label_text = medium_font.render("Rank Score:", True, PRIMARY_COLOR)
        screen.blit(label_text, (SCREEN_WIDTH // 2 - 320, 150))
        
        # 段位分输入框
        pygame.draw.rect(screen, color, input_rect, 2)
        text_surface = shop_font.render(input_text, True, PRIMARY_COLOR)
        screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 8))
        input_rect.w = max(300, text_surface.get_width() + 20)
        
        # 商店积分输入区域
        shop_label_text = medium_font.render("Shop Points:", True, PRIMARY_COLOR)
        screen.blit(shop_label_text, (SCREEN_WIDTH // 2 + 20, 150))
        
        # 商店积分输入框
        pygame.draw.rect(screen, shop_color, shop_input_rect, 2)
        shop_text_surface = shop_font.render(shop_input_text, True, PRIMARY_COLOR)
        screen.blit(shop_text_surface, (shop_input_rect.x + 10, shop_input_rect.y + 8))
        shop_input_rect.w = max(300, shop_text_surface.get_width() + 20)
        
        # 按钮
        button_width = 200
        button_height = 50
        apply_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width - 20, 260, button_width, button_height)
        reset_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, 260, button_width, button_height)
        
        # 应用按钮
        pygame.draw.rect(screen, SECONDARY_COLOR, apply_button)
        apply_text = shop_font.render("Apply", True, WHITE)
        screen.blit(apply_text, (apply_button.x + (button_width - apply_text.get_width()) // 2, apply_button.y + (button_height - apply_text.get_height()) // 2))
        
        # 重置按钮
        pygame.draw.rect(screen, GRAY_LIGHT, reset_button)
        reset_text = shop_font.render("Reset", True, GRAY_DARK)
        screen.blit(reset_text, (reset_button.x + (button_width - reset_text.get_width()) // 2, reset_button.y + (button_height - reset_text.get_height()) // 2))
        
        # 清除所有已购买物品按钮
        clear_items_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, 330, button_width, button_height)
        pygame.draw.rect(screen, (200, 50, 50), clear_items_button)
        clear_items_text = shop_font.render("Clear All Items", True, WHITE)
        screen.blit(clear_items_text, (clear_items_button.x + (button_width - clear_items_text.get_width()) // 2, clear_items_button.y + (button_height - clear_items_text.get_height()) // 2))
        
        # 当前段位信息
        current_rank_score = get_rank_score()
        rank_num, stage_num, _, _, rank_name, stage_name, _ = calculate_rank(current_rank_score)
        rank_info_text = shop_font.render(f"Current Rank: {rank_name} {stage_name}", True, ACCENT_COLOR)
        screen.blit(rank_info_text, (SCREEN_WIDTH // 2 - 320, 400))
        
        # 当前商店积分信息
        current_shop_score = get_total_score()
        shop_info_text = shop_font.render(f"Current Shop Points: {current_shop_score}", True, ACCENT_COLOR)
        screen.blit(shop_info_text, (SCREEN_WIDTH // 2 + 20, 400))
        
        # 显示已购买物品数量
        unlocked_skills = load_unlocked_skills()
        total_items = sum(len(rarities) for rarities in unlocked_skills.values())
        items_info_text = shop_font.render(f"Owned Items: {total_items}", True, (255, 100, 100))
        screen.blit(items_info_text, (SCREEN_WIDTH // 2 - items_info_text.get_width() // 2, 370))
        
        # 操作提示
        tip_text = small_font.render("Press ESC to return", True, GRAY_DARK)
        screen.blit(tip_text, (SCREEN_WIDTH // 2 - tip_text.get_width() // 2, SCREEN_HEIGHT - 30))
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if input_active:
                    if event.key == pygame.K_RETURN:
                        # 应用修改
                        try:
                            new_score = int(input_text)
                            save_rank_score(new_score)
                            print(f"Rank score updated to: {new_score}")
                        except ValueError:
                            pass
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        # 只允许输入数字
                        if event.unicode.isdigit():
                            input_text += event.unicode
                elif shop_input_active:
                    if event.key == pygame.K_RETURN:
                        # 应用修改
                        try:
                            new_shop_score = int(shop_input_text)
                            save_total_score_to_db(new_shop_score)
                            print(f"Shop points updated to: {new_shop_score}")
                        except ValueError:
                            pass
                    elif event.key == pygame.K_BACKSPACE:
                        shop_input_text = shop_input_text[:-1]
                    else:
                        # 只允许输入数字
                        if event.unicode.isdigit():
                            shop_input_text += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 检查段位分输入框点击
                if input_rect.collidepoint(event.pos):
                    input_active = True
                    shop_input_active = False
                    color = color_active
                    shop_color = color_inactive
                # 检查商店积分输入框点击
                elif shop_input_rect.collidepoint(event.pos):
                    shop_input_active = True
                    input_active = False
                    shop_color = color_active
                    color = color_inactive
                else:
                    input_active = False
                    shop_input_active = False
                    color = color_inactive
                    shop_color = color_inactive
                
                # 检查应用按钮点击
                if apply_button.collidepoint(event.pos):
                    try:
                        new_score = int(input_text)
                        save_rank_score(new_score)
                        print(f"Rank score updated to: {new_score}")
                    except ValueError:
                        pass
                    try:
                        new_shop_score = int(shop_input_text)
                        save_total_score_to_db(new_shop_score)
                        print(f"Shop points updated to: {new_shop_score}")
                    except ValueError:
                        pass
                
                # 检查重置按钮点击
                if reset_button.collidepoint(event.pos):
                    input_text = "0"
                    shop_input_text = "0"
                    save_rank_score(0)
                    save_total_score_to_db(0)
                    print("Rank score and shop points reset to 0")
                
                # 检查清除所有物品按钮点击
                if clear_items_button.collidepoint(event.pos):
                    clear_all_unlocked_items()
                    print("All unlocked items cleared")
        
        pygame.display.flip()


def update_skill_uses(skill_name, new_uses, rarity=None):
    """更新技能剩余使用次数，如果使用次数为0则删除该技能
    
    Args:
        skill_name: 技能/天赋名称
        new_uses: 新的使用次数
        rarity: 品质（可选，用于天赋的多品质支持）
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if new_uses <= 0:
        # 使用次数用完，删除该技能
        if rarity:
            # 天赋：删除指定品质
            cursor.execute("DELETE FROM unlocked_skills WHERE skill_name = ? AND rarity = ?", (skill_name, rarity))
        else:
            # 技能：删除所有同名技能
            cursor.execute("DELETE FROM unlocked_skills WHERE skill_name = ?", (skill_name,))
    else:
        # 更新使用次数
        if rarity:
            # 天赋：更新指定品质
            cursor.execute("UPDATE unlocked_skills SET uses_left = ? WHERE skill_name = ? AND rarity = ?", (new_uses, skill_name, rarity))
        else:
            # 技能：更新所有同名技能
            cursor.execute("UPDATE unlocked_skills SET uses_left = ? WHERE skill_name = ?", (new_uses, skill_name))
    
    conn.commit()
    conn.close()


def clear_all_unlocked_items():
    """清除所有已解锁的技能和天赋"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM unlocked_skills")
    conn.commit()
    conn.close()
    # 同时清除上次使用的技能记录
    set_db_value('last_used_skills', '[]')
    print("All unlocked items and last used skills cleared from database")


def get_total_score():
    """获取游戏总分数（用于商店购买等）"""
    value = get_db_value('total_score')
    return int(value) if value else 0

def get_rank_score():
    """获取段位分（用于计算段位）"""
    value = get_db_value('rank_score')
    return int(value) if value else 0

def calculate_rank(rank_score):
    """
    Calculate rank information based on rank score
    Returns: (rank number, stage number, current stage progress, points needed for next stage, rank name, stage name, rank color)
    """
    if rank_score < RANK_SCORE_PER_STAGE:
        return (0, 1, rank_score, RANK_SCORE_PER_STAGE, "Rank 0", "I", (150, 150, 150))
    
    remaining_score = rank_score
    current_rank = 0
    current_stage = 1
    
    for rank_num in range(1, 7):
        rank_data = RANK_CONFIG[rank_num]
        stages_in_rank = rank_data["stages"]
        score_needed = stages_in_rank * RANK_SCORE_PER_STAGE
        
        if remaining_score >= score_needed:
            remaining_score -= score_needed
            current_rank = rank_num
            current_stage = 1
        else:
            current_rank = rank_num
            current_stage = remaining_score // RANK_SCORE_PER_STAGE + 1
            progress_in_stage = remaining_score % RANK_SCORE_PER_STAGE
            rank_name = rank_data["name"]
            rank_color = rank_data["color"]
            stage_name = RANK_STAGE_NAMES[current_stage - 1] if current_stage <= len(RANK_STAGE_NAMES) else f"V"
            return (current_rank, current_stage, progress_in_stage, RANK_SCORE_PER_STAGE, rank_name, stage_name, rank_color)
    
    # 巅峰Rank 6（荣耀等级）
    # 每100分为一颗五角星（5个stage × 20分）
    honor_score_per_level = RANK_SCORE_PER_STAGE * 5  # 100分
    honor_level = remaining_score // honor_score_per_level + 1
    honor_progress = remaining_score % honor_score_per_level
    rank_name = "Honor"
    rank_color = (255, 215, 0)  # 金色
    stage_name = f"{honor_level}"
    return (6, honor_level, honor_progress, honor_score_per_level, rank_name, stage_name, rank_color)

def get_rank_info():
    """Get current rank information"""
    rank_score = get_rank_score()
    return calculate_rank(rank_score)

# 矩形绘制函数（纯矩形，无圆角）
def show_rank_change_animation(rank_change):
    """显示段位变化的全屏动画提示"""
    global screen, current_bgm, start_menu_bgm
    
    # 提取段位变化信息
    change_type, rank_name, stage_name, rank_num, stage_num = rank_change
    
    # 停止所有背景音乐
    if current_bgm:
        current_bgm.stop()
    if start_menu_bgm:
        start_menu_bgm.stop()
    
    # 播放段位提升音效
    if change_type == "promotion":
        try:
            rank_up_sound = pygame.mixer.Sound(RANK_UP_SOUND_PATH)
            rank_up_sound.set_volume(RANK_UP_SOUND_VOLUME)
            rank_up_sound.play()
        except:
            pass
    
    # 设置字体
    title_font = load_custom_font(64, bold=True)
    subtitle_font = load_custom_font(32)
    small_font = load_custom_font(16)
    
    # 动画持续时间
    duration = 3000  # 3秒
    start_time = pygame.time.get_ticks()
    
    # 背景颜色
    bg_color = (255, 255, 255)  # 白色背景
    
    # 动画参数
    scale = 0.1
    alpha = 0
    max_scale = 1.0
    
    while True:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time
        
        if elapsed > duration:
            # 动画结束，恢复背景音乐
            if current_bgm:
                current_bgm.play(-1)
            elif start_menu_bgm:
                start_menu_bgm.play(-1)
            break
        
        # 计算动画进度
        progress = min(elapsed / duration, 1.0)
        
        # 缩放动画
        if progress < 0.3:
            scale = 0.1 + (max_scale - 0.1) * (progress / 0.3)
        elif progress < 0.7:
            scale = max_scale
        else:
            scale = max_scale - (max_scale - 0.1) * ((progress - 0.7) / 0.3)
        
        # 透明度动画
        if progress < 0.2:
            alpha = int(255 * (progress / 0.2))
        elif progress < 0.8:
            alpha = 255
        else:
            alpha = int(255 * (1 - (progress - 0.8) / 0.2))
        
        # 清除屏幕
        screen.fill(bg_color)
        
        # 绘制标题
        if change_type == "promotion":
            title_text = "RANK UP!"
            title_color = SECONDARY_COLOR  # 主题蓝
        else:
            title_text = "RANK DOWN!"
            title_color = ACCENT_COLOR  # 主题番茄红
        
        title_surface = title_font.render(title_text, True, title_color)
        title_surface.set_alpha(alpha)
        
        # 绘制副标题
        subtitle_text = f"{rank_name} {stage_name}"
        subtitle_surface = subtitle_font.render(subtitle_text, True, (0, 0, 0))
        subtitle_surface.set_alpha(alpha)
        
        # 计算位置
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        
        # 绘制文本
        screen.blit(title_surface, title_rect)
        screen.blit(subtitle_surface, subtitle_rect)
        
        # 绘制跳过提示
        skip_text = "Press ESC to skip"
        skip_surface = small_font.render(skip_text, True, (100, 100, 100))
        skip_surface.set_alpha(alpha)
        skip_rect = skip_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(skip_surface, skip_rect)
        
        # 更新屏幕
        pygame.display.flip()
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    # 恢复背景音乐
                    if current_bgm:
                        current_bgm.play(-1)
                    elif start_menu_bgm:
                        start_menu_bgm.play(-1)
                    return


def draw_rect(surface, color, rect, shadow=False, border_radius=0, border_color=None):  # 新增 border_radius 参数（默认8px圆角）
    """绘制圆角矩形（可带阴影+描边）"""
    x, y, w, h = rect
    # 使用传入的边框颜色，如果没有则使用默认灰色
    stroke_color = border_color if border_color else (190, 190, 190)

    # 添加描边（圆角）
    stroke_rect = (x - 4, y - 4, w + 8, h + 8)
    pygame.draw.rect(surface, stroke_color, stroke_rect, border_radius=border_radius + 0)  # 描边圆角稍大

    # 绘制阴影（圆角）
    if shadow:
        shadow_surface = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 30), (2, 2, w, h), border_radius=border_radius)
        surface.blit(shadow_surface, (x - 2, y - 2))

    # 绘制主圆角矩形
    pygame.draw.rect(surface, color, (x, y, w, h), border_radius=border_radius)

# 菱形绘制函数
def draw_diamond(surface, color, center_x, center_y, size):
    """绘制菱形"""
    # 计算菱形的四个顶点
    points = [
        (center_x, center_y - size),  # 上
        (center_x + size, center_y),  # 右
        (center_x, center_y + size),  # 下
        (center_x - size, center_y)   # 左
    ]
    # 绘制菱形
    pygame.draw.polygon(surface, color, points)


# 统一绘制图标文字的函数
def draw_icon_text(surface, text, center_x, center_y):
    """统一绘制图标内的文字（带描边）"""
    # 渲染文字
    text_surface = ICON_FONT.render(text, True, ICON_TEXT_COLOR)
    outline_surface = ICON_FONT.render(text, True, ICON_TEXT_OUTLINE_COLOR)

    # 计算文字位置（居中）
    text_x = center_x - text_surface.get_width() // 2
    text_y = center_y - text_surface.get_height() // 2

    # 绘制描边（统一宽度）
    offsets = [
        (-ICON_TEXT_STROKE_WIDTH, -ICON_TEXT_STROKE_WIDTH),
        (ICON_TEXT_STROKE_WIDTH, -ICON_TEXT_STROKE_WIDTH),
        (-ICON_TEXT_STROKE_WIDTH, ICON_TEXT_STROKE_WIDTH),
        (ICON_TEXT_STROKE_WIDTH, ICON_TEXT_STROKE_WIDTH),
        (-ICON_TEXT_STROKE_WIDTH, 0),
        (ICON_TEXT_STROKE_WIDTH, 0),
        (0, -ICON_TEXT_STROKE_WIDTH),
        (0, ICON_TEXT_STROKE_WIDTH)
    ]

    for dx, dy in offsets:
        surface.blit(outline_surface, (text_x + dx, text_y + dy))

    # 绘制主文字
    surface.blit(text_surface, (text_x, text_y))

def draw_text_with_outline(surface, text, font, x, y, text_color, outline_color, outline_width=1):
    """绘制带描边的文字"""
    # 渲染主文字
    text_surface = font.render(text, True, text_color)
    # 渲染描边文字
    outline_surface = font.render(text, True, outline_color)
    
    # 绘制描边（8个方向）
    offsets = [
        (-outline_width, -outline_width),
        (outline_width, -outline_width),
        (-outline_width, outline_width),
        (outline_width, outline_width),
        (-outline_width, 0),
        (outline_width, 0),
        (0, -outline_width),
        (0, outline_width)
    ]
    
    for dx, dy in offsets:
        surface.blit(outline_surface, (x + dx, y + dy))
    
    # 绘制主文字
    surface.blit(text_surface, (x, y))

def draw_boost_icon(surface, icon_rect):
    """在技能图标右上角绘制CD提升标识（圆角）"""
    # 计算提升图标位置（右上角，向内缩进2px）
    boost_x = icon_rect[0] + icon_rect[2] - BOOST_ICON_SIZE  # 右对齐容器边框
    boost_y = icon_rect[1]  # 上对齐容器边框
    boost_rect = (boost_x, boost_y, BOOST_ICON_SIZE, BOOST_ICON_SIZE)

    # 绘制黄色圆角底色
    pygame.draw.rect(surface, BOOST_ICON_COLOR, boost_rect, border_radius=0) #3

    # 绘制提升箭头文字
    boost_font = load_custom_font(BOOST_ICON_FONT_SIZE, bold=True)
    text_surface = boost_font.render(BOOST_ICON_TEXT, True, BLACK)
    text_x = boost_x + (BOOST_ICON_SIZE - text_surface.get_width()) // 2
    text_y = boost_y + (BOOST_ICON_SIZE - text_surface.get_height()) // 2
    surface.blit(text_surface, (text_x, text_y))

def draw_compensation_icon(surface, icon_rect):
    """在速度图标右下角绘制红色代偿图标（与提升图标大小相同）"""
    # 计算代偿图标位置（右下角，向内缩进2px）
    comp_x = icon_rect[0] + icon_rect[2] - COMPENSATION_ICON_SIZE  # 右对齐容器边框
    comp_y = icon_rect[1] + icon_rect[3] - COMPENSATION_ICON_SIZE  # 下对齐容器边框
    comp_rect = (comp_x, comp_y, COMPENSATION_ICON_SIZE, COMPENSATION_ICON_SIZE)

    # 绘制红色底色（与提升图标样式一致，无圆角或保持统一圆角）
    pygame.draw.rect(surface, COMPENSATION_ICON_COLOR, comp_rect, border_radius=0)

    # 绘制代偿标识文字（可选，如需隐藏文字可删除此部分）
    comp_font = load_custom_font(COMPENSATION_ICON_FONT_SIZE, bold=True)
    text_surface = comp_font.render(COMPENSATION_ICON_TEXT, True, BLACK)
    text_x = comp_x + (COMPENSATION_ICON_SIZE - text_surface.get_width()) // 2
    text_y = comp_y + (COMPENSATION_ICON_SIZE - text_surface.get_height()) // 2
    surface.blit(text_surface, (text_x, text_y))

# 统一绘制遮罩的函数
def draw_mask(surface, container_rect, progress, is_easy_mode):
    """统一绘制遮罩（完全复用 health_regen_icon 的视觉样式）"""
    x, y, w, h = container_rect
    # 复用 health_regen_icon 的透明度参数
    mask_alpha = MASK_ALPHA_EASY if is_easy_mode else MASK_ALPHA_HARD

    # 计算遮罩高度（复用 health_regen_icon 的计算逻辑）
    mask_height = int(h * progress)
    if mask_height > 0:
        mask_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        # 复用 health_regen_icon 的圆角（0）和颜色
        pygame.draw.rect(mask_surface, (*HEALTH_REGEN_MASK_COLOR, mask_alpha),
                         (0, h - mask_height, w, mask_height), border_radius=0)
        surface.blit(mask_surface, (x, y))

# 绘制额外血条图标函数
def draw_extra_health_icon(dino, score):
    """绘制额外血条图标（移到原速度图标位置）"""
    # 核心修改：替换原有icon_x为新定义的常量
    pos = get_jump_boost_icon_pos(dino, score)
    icon_x = pos["extra_health_x"]  # 替换原有固定位置
    icon_y = EXTRA_HEALTH_ICON_Y_POS
    container_rect = (icon_x, icon_y, EXTRA_HEALTH_ICON_CONTAINER_SIZE, EXTRA_HEALTH_ICON_CONTAINER_SIZE)

    # 以下逻辑完全保留，仅位置变更
    if dino.extra_health > 0:
        container_color = EXTRA_HEALTH_ICON_COLOR
        draw_rect(screen, container_color, container_rect, shadow=True)

        # 绘制图标（图片/菱形）
        icon_center_x = icon_x + EXTRA_HEALTH_ICON_CONTAINER_SIZE // 2
        icon_center_y = icon_y + EXTRA_HEALTH_ICON_CONTAINER_SIZE // 2
        if game_resources["extra_health_icon"] == "rect":
            draw_diamond(screen, WHITE, icon_center_x, icon_center_y, 15)
        else:
            icon_surface = pygame.transform.scale(game_resources["extra_health_icon"], (ICON_SIZE, ICON_SIZE))
            screen.blit(icon_surface, (icon_center_x - ICON_SIZE // 2, icon_center_y - ICON_SIZE // 2))

        # 血量进度遮罩+文字（原有逻辑不变）
        extra_health_progress = dino.extra_health / (INITIAL_HEALTH * SKILL2_HEALTH_BOOST)
        is_easy_mode = score <= SCORE_STAGE_2
        mask_progress = 1.0 - extra_health_progress
        draw_mask(screen, container_rect, mask_progress, is_easy_mode)

        #percentage = int(extra_health_progress + 1)
        #draw_icon_text(screen, f"{percentage}", icon_center_x, icon_center_y)

# 恐龙类（适配新窗口）
class Dinosaur:
    def __init__(self):
        # 基础属性 - 适配新窗口尺寸
        self.width = 75
        self.height = 75
        self.x = 80  # 右移避免边缘拥挤
        self.y = SCREEN_HEIGHT - self.height - 15  # 调整Y位置适配新窗口
        self.velocity_y = 0
        self.is_jumping = False

        self.skill1_upgrade_flash_end = 0  # 技能1升级闪烁结束时间
        self.skill2_upgrade_flash_end = 0  # 技能2升级闪烁结束时间
        self.skill3_upgrade_flash_end = 0  # 技能3升级闪烁结束时间

        # 动画属性
        self.animation_frames = game_resources["dino_images"]
        self.current_frame = 0
        self.animation_speed = 0.15
        self.frame_timer = 0

        # 技能1相关属性（LAST EFFORT）
        self.skill1_active = False
        self.skill1_cooldown = False
        self.skill1_cd_end = 0
        self.skill1_effect_end = 0
        self.skill1_text_end = 0
        self.skill1_progress = 0  # 技能冷却进度（0-1）

        # 技能2相关属性（Quick Heal）
        self.skill2_cooldown = False
        self.skill2_cd_end = 0
        self.skill2_text_end = 0
        self.skill2_progress = 0  # 技能冷却进度（0-1）
        self.extra_health = 0.0  # 额外血量

        # 技能3相关属性（命之跳跃）
        self.skill3_active = False
        self.skill3_cooldown = False
        self.skill3_cd_end = 0
        self.skill3_effect_end = 0
        self.skill3_text_end = 0
        self.skill3_progress = 0  # 技能冷却进度（0-1）
        self.skill3_fps_boost = 0  # 当前FPS提升比例
        self.skill3_fps_boost_end = 0  # FPS提升结束时间

        # 血条相关属性
        self.health = INITIAL_HEALTH
        self.invulnerable = False
        self.invulnerable_end = 0
        self.invulnerable_duration = 500

        #血量恢复相关属性
        self.last_regen_time = pygame.time.get_ticks()  # 上次恢复时间
        self.is_hurt = False  # 是否受到过伤害（仅受伤后才恢复）
        self.regen_cooldown = False  # 是否处于恢复冷却期
        self.regen_cooldown_end = 0  # 冷却结束时间
        self.regenerated_health_since_hurt = 0.0

        # 视觉效果
        self.scale = 1.0  # 缩放比例（跳跃时轻微缩放）
        self.scale_speed = 0.02

        self.skill_usage_count = 0  # 记录技能使用总次数（每用一次任意技能+1）
        self.compensation_speed_bonus = 0.0  # 代偿带来的速度加成比例（初始0，每次+6%即0.06）
        
        # Obstacle statistics (for rank point calculation)
        self.obstacles_cleared = 0  # Number of successfully cleared obstacles
        self.obstacles_total = 0    # Total number of generated obstacles
        
        # 阶段FPS提升相关属性
        self.stage_fps_boost = 0.0  # 阶段提升的FPS比例（每升一级+15%）

        # 张狂道具相关属性
        self.frenzy_active = False  # 张狂是否激活
        self.frenzy_start_time = 0  # 张狂开始时间
        self.frenzy_duration = 5000  # 张狂持续时间（5秒）
        self.frenzy_delay = 0  # 张狂延迟时间（根据稀有度：0/5000/10000/15000毫秒）

        # 矫健天赋相关属性
        self.agility_active = False  # 矫健是否激活
        self.agility_fps_boost = 0.0  # 矫健提供的FPS提升比例

    def update_health_regen(self, score):
        """更新血量恢复逻辑：受伤后恢复1.0血量就立即进入冷却"""
        current_time = pygame.time.get_ticks()

        # 检查冷却期：冷却期内不恢复血量（优先判断）
        if self.regen_cooldown:
            if current_time > self.regen_cooldown_end:
                self.regen_cooldown = False  # 冷却结束
                # 冷却结束后重置累计恢复量
                self.regenerated_health_since_hurt = 0.0
                # 如果仍处于受伤状态，重置恢复计时
                if self.is_hurt:
                    self.last_regen_time = current_time
            return

        # 未受伤时不恢复血量
        if not self.is_hurt:
            return

        # 计算恢复血量（仅当未冷却、受伤时执行）
        time_passed = current_time - self.last_regen_time
        if time_passed >= HEALTH_REGEN_INTERVAL:  # 按设定的间隔恢复
            regen_amount = (time_passed / 1000) * HEALTH_REGEN_RATE
            # 计算本次实际能恢复的血量（不超过满血）
            actual_regen = min(regen_amount, INITIAL_HEALTH - self.health)

            if actual_regen > 0:
                # 更新累计恢复量
                self.regenerated_health_since_hurt += actual_regen
                # 恢复血量
                self.health += actual_regen

                # 核心修改：检查是否累计恢复了1.0血量
                if self.regenerated_health_since_hurt >= 1.0:
                    # 触发冷却
                    self.regen_cooldown = True
                    # 应用技能CD减免
                    current_difficulty = get_current_difficulty(score)
                    cd_reduce = SKILL_CD_REDUCE_RATIO.get(current_difficulty, 0.0)
                    reduced_cd = HEALTH_REGEN_COOLDOWN * (1 - cd_reduce)
                    self.regen_cooldown_end = current_time + reduced_cd
                    # 重置受伤状态和累计恢复量
                    self.is_hurt = False
                    self.regenerated_health_since_hurt = 0.0
                    # 清空血迹粒子
                    global blood_particles
                    blood_particles = []

            self.last_regen_time = current_time

    def jump(self):
        """恐龙跳跃（带音效和视觉效果）"""
        if not self.is_jumping:
            self.velocity_y = JUMP_FORCE
            self.is_jumping = True
            self.scale = 1.1  # 跳跃时放大
            if game_resources.get("jump_sound"):
                game_resources["jump_sound"].play()

    def activate_skill1(self, score, carried_skills, skill_rarity_map=None):
        """激活翻越障碍物技能（LAST EFFORT）- 新增难度CD减免和使用次数限制"""
        # 检查是否携带了该技能
        if "Brave Dash" not in carried_skills:
            return
        unlocked_skills = load_unlocked_skills()
        if "Brave Dash" not in unlocked_skills or len(unlocked_skills["Brave Dash"]) == 0:
            return
        # 获取当前使用的品质
        if skill_rarity_map and "Brave Dash" in skill_rarity_map:
            current_rarity = skill_rarity_map["Brave Dash"]
        else:
            # 默认使用第一个品质
            current_rarity = list(unlocked_skills["Brave Dash"].keys())[0]
        # 检查使用次数
        uses_left = unlocked_skills["Brave Dash"][current_rarity]["uses_left"]
        if uses_left == 0:
            return  # 使用次数耗尽
        if score <= SCORE_STAGE_2:
            return
        if not self.skill1_cooldown and not self.skill1_active:
            # 减少使用次数
            if uses_left > 0:
                update_skill_uses("Brave Dash", uses_left - 1, current_rarity)
            
            self.skill_usage_count += 1
            self.compensation_speed_bonus += 0.06  # 6%速度加成

            self.skill1_active = True
            self.skill1_cooldown = True
            self.skill1_effect_end = pygame.time.get_ticks() + SKILL1_DURATION

            # 核心修改：根据难度计算减免后的冷却时间
            current_difficulty = get_current_difficulty(score)  # 获取当前难度
            cd_reduce = SKILL_CD_REDUCE_RATIO[current_difficulty]  # 获取减免比例
            reduced_cd = SKILL1_COOLDOWN * (1 - cd_reduce)  # 计算减免后CD
            self.skill1_cd_end = pygame.time.get_ticks() + reduced_cd  # 应用新CD

            self.skill1_text_end = pygame.time.get_ticks() + SKILL1_TEXT_DURATION
            self.skill1_progress = 1.0  # 重置冷却进度

            self.skill1_flash_end = pygame.time.get_ticks() + SKILL_FLASH_DURATION

            if game_resources.get("last_effort_sound"):
                game_resources["last_effort_sound"].play()

    def activate_skill2(self, score, carried_skills, skill_rarity_map=None):
        """激活快速治疗技能（Quick Heal）- 新增一阶以下禁用+难度CD减免"""
        # 检查是否携带了该技能
        if "Zoom Boost" not in carried_skills:
            return
        # ========== 核心修改：一阶以下（≤10分）禁用 ==========
        unlocked_skills = load_unlocked_skills()
        if "Zoom Boost" not in unlocked_skills or len(unlocked_skills["Zoom Boost"]) == 0:
            return
        # 获取当前使用的品质
        if skill_rarity_map and "Zoom Boost" in skill_rarity_map:
            current_rarity = skill_rarity_map["Zoom Boost"]
        else:
            # 默认使用第一个品质
            current_rarity = list(unlocked_skills["Zoom Boost"].keys())[0]
        if score <= SCORE_STAGE_2:
            return

        # 原有逻辑：存在额外血条时无法激活技能
        if self.extra_health > 0:
            return

        if self.skill2_cooldown:  # 冷却中禁用
            return

        if not self.skill2_cooldown:
            # 检查使用次数
            uses_left = unlocked_skills["Zoom Boost"][current_rarity]["uses_left"]
            if uses_left == 0:
                return  # 使用次数耗尽
            
            # 减少使用次数
            if uses_left > 0:
                update_skill_uses("Zoom Boost", uses_left - 1, current_rarity)
            
            self.skill_usage_count += 1
            self.compensation_speed_bonus += 0.06  # 6%速度加成

            # 增加60%额外血量
            self.extra_health = INITIAL_HEALTH * SKILL2_HEALTH_BOOST
            self.skill2_cooldown = True

            # 根据当前分数计算难度，应用CD减免
            current_difficulty = get_current_difficulty(score)  # 获取当前难度
            cd_reduce = SKILL_CD_REDUCE_RATIO[current_difficulty]  # 获取减免比例
            reduced_cd = SKILL2_COOLDOWN * (1 - cd_reduce)  # 计算减免后CD
            self.skill2_cd_end = pygame.time.get_ticks() + reduced_cd  # 应用新CD

            self.skill2_text_end = pygame.time.get_ticks() + SKILL2_TEXT_DURATION
            self.skill2_progress = 1.0  # 重置冷却进度

            self.skill2_flash_end = pygame.time.get_ticks() + SKILL_FLASH_DURATION

            if game_resources.get("heal_sound"):
                game_resources["heal_sound"].play()

    def activate_skill3(self, score, carried_skills, skill_rarity_map=None):
        """激活命之跳跃技能 - 一阶解锁+FPS提升+难度加成+0.5秒免疫+使用次数限制"""
        # 检查是否携带了该技能
        if "Lucky Leap" not in carried_skills:
            return
        # 一阶解锁（难度≥2）
        current_difficulty = get_current_difficulty(score)
        unlocked_skills = load_unlocked_skills()
        if "Lucky Leap" not in unlocked_skills or len(unlocked_skills["Lucky Leap"]) == 0:
            return
        # 获取当前使用的品质
        if skill_rarity_map and "Lucky Leap" in skill_rarity_map:
            current_rarity = skill_rarity_map["Lucky Leap"]
        else:
            # 默认使用第一个品质
            current_rarity = list(unlocked_skills["Lucky Leap"].keys())[0]
        # 检查使用次数
        uses_left = unlocked_skills["Lucky Leap"][current_rarity]["uses_left"]
        if uses_left == 0:
            return  # 使用次数耗尽
        if current_difficulty < 2:  # 一阶（难度2）以下禁用
            return

        if self.skill3_cooldown:  # 冷却中禁用
            return

        # 减少使用次数
        if uses_left > 0:
            update_skill_uses("Lucky Leap", uses_left - 1, current_rarity)

        self.skill_usage_count += 1
        self.compensation_speed_bonus += 0.06  # 6%速度加成

        # 计算FPS提升比例（基础12% + 难度×5%）
        self.skill3_fps_boost = SKILL3_BASE_FPS_BOOST + (current_difficulty - 2) * SKILL3_FPS_BOOST_PER_DIFFICULTY
        self.skill3_fps_boost_end = pygame.time.get_ticks() + SKILL3_DURATION

        self.skill3_active = True
        self.skill3_cooldown = True
        self.skill3_effect_end = pygame.time.get_ticks() + SKILL3_DURATION

        # 新增：技能3启动后立即触发0.5秒免疫
        self.invulnerable = True
        self.invulnerable_end = pygame.time.get_ticks() + SKILL3_INVUL_DURATION

        # CD减免逻辑（保持原有）
        cd_reduce = SKILL_CD_REDUCE_RATIO[current_difficulty]
        reduced_cd = SKILL3_COOLDOWN * (1 - cd_reduce)
        self.skill3_cd_end = pygame.time.get_ticks() + reduced_cd

        self.skill3_text_end = pygame.time.get_ticks() + SKILL3_TEXT_DURATION
        self.skill3_progress = 1.0
        self.skill3_upgrade_flash_end = pygame.time.get_ticks() + SKILL_FLASH_DURATION

        if game_resources.get("skill3_sound"):
            game_resources["skill3_sound"].play()

        boost_percent = int(self.skill3_fps_boost * 100)
        self.skill3_boost_text = f"{boost_percent}%"
        self.skill3_boost_remaining = SKILL3_DURATION // 1000  # 初始剩余时间（秒）

    def update_skill3_state(self):
        """更新技能3状态（含FPS提升）"""
        current_time = pygame.time.get_ticks()

        # 更新剩余持续时间
        if self.skill3_fps_boost > 0:
            remaining_ms = max(0, self.skill3_fps_boost_end - current_time)
            self.skill3_boost_remaining = int(remaining_ms / 1000)
            # 更新提升百分比文字（防止难度变化）
            boost_percent = int(self.skill3_fps_boost * 100)
            self.skill3_boost_text = f"{boost_percent}%"
        else:
            self.skill3_boost_text = ""
            self.skill3_boost_remaining = 0

        # 重置FPS提升
        if self.skill3_fps_boost_end < current_time:
            self.skill3_fps_boost = 0

        if self.skill3_active and current_time > self.skill3_effect_end:
            self.skill3_active = False

        if self.skill3_cooldown:
            if current_time > self.skill3_cd_end:
                self.skill3_cooldown = False
                self.skill3_progress = 0
            else:
                remaining = self.skill3_cd_end - current_time
                original_cd = SKILL3_COOLDOWN
                self.skill3_progress = remaining / original_cd

    def apply_cd_reduction_on_stage_change(self, new_difficulty):
        """阶段切换时，对正在冷却中的技能立即应用CD减免"""
        current_time = pygame.time.get_ticks()
        cd_reduce = SKILL_CD_REDUCE_RATIO.get(new_difficulty, 0.0)

        # 技能1：如果正在冷却，立即减免剩余CD
        if self.skill1_cooldown and current_time < self.skill1_cd_end:
            remaining = self.skill1_cd_end - current_time
            # 计算减免后的剩余时间
            reduced_remaining = remaining * (1 - cd_reduce)
            self.skill1_cd_end = current_time + reduced_remaining

        # 技能2：如果正在冷却，立即减免剩余CD
        if self.skill2_cooldown and current_time < self.skill2_cd_end:
            remaining = self.skill2_cd_end - current_time
            reduced_remaining = remaining * (1 - cd_reduce)
            self.skill2_cd_end = current_time + reduced_remaining

        # 技能3：如果正在冷却，立即减免剩余CD
        if self.skill3_cooldown and current_time < self.skill3_cd_end:
            remaining = self.skill3_cd_end - current_time
            reduced_remaining = remaining * (1 - cd_reduce)
            self.skill3_cd_end = current_time + reduced_remaining

        # 回血冷却：如果正在冷却，立即减免剩余CD
        if self.regen_cooldown and current_time < self.regen_cooldown_end:
            remaining = self.regen_cooldown_end - current_time
            reduced_remaining = remaining * (1 - cd_reduce)
            self.regen_cooldown_end = current_time + reduced_remaining

    def take_damage(self):
        """扣血逻辑（优先扣额外血量）"""
        if not self.invulnerable and not self.skill1_active:
            # 优先扣除额外血量
            if self.extra_health > 0:
                damage = min(self.extra_health, HEALTH_DECREASE)
                self.extra_health -= damage
                remaining_damage = HEALTH_DECREASE - damage
                if remaining_damage > 0:
                    self.health -= remaining_damage
            else:
                self.health -= HEALTH_DECREASE

            self.health = max(0, self.health)
            self.invulnerable = True
            self.invulnerable_end = pygame.time.get_ticks() + self.invulnerable_duration

            # 播放受伤音效
            if game_resources.get("hurt_sound"):
                game_resources["hurt_sound"].play()

            if game_resources.get("hit_sound"):
                game_resources["hit_sound"].play()

            self.is_hurt = True
            self.last_regen_time = pygame.time.get_ticks()
            self.regenerated_health_since_hurt = 0.0

            # 返回当前血量（用于生成对应数量的粒子化血迹）
            return self.health
        return self.health

    def update_skill1_state(self):
        """更新技能1状态 - 适配动态冷却时间"""
        current_time = pygame.time.get_ticks()

        if self.skill1_active and current_time > self.skill1_effect_end:
            self.skill1_active = False

        if self.skill1_cooldown:
            if current_time > self.skill1_cd_end:
                self.skill1_cooldown = False
                self.skill1_progress = 0
            else:
                # 核心修改：基于实际剩余CD计算进度（不再依赖固定SKILL1_COOLDOWN）
                remaining = self.skill1_cd_end - current_time
                # 反向推导原始CD（用于进度计算）
                original_cd = SKILL1_COOLDOWN
                self.skill1_progress = remaining / original_cd  # 保持进度显示一致

    def update_skill2_state(self):
        """更新技能2状态 - 适配动态冷却时间"""
        current_time = pygame.time.get_ticks()

        if self.skill2_cooldown:
            if current_time > self.skill2_cd_end:
                self.skill2_cooldown = False
                self.skill2_progress = 0
            else:
                # 核心修改：基于实际剩余CD计算进度
                remaining = self.skill2_cd_end - current_time
                original_cd = SKILL2_COOLDOWN
                self.skill2_progress = remaining / original_cd

    def update_invulnerable_state(self):
        """更新无敌状态"""
        current_time = pygame.time.get_ticks()
        if self.invulnerable and current_time > self.invulnerable_end:
            self.invulnerable = False

    def update_visual_effects(self):
        """更新视觉效果"""
        # 缩放效果（落地时恢复原大小）
        if self.is_jumping:
            self.scale = max(1.0, self.scale - self.scale_speed)
        else:
            self.scale = 1.0

    def update(self, score):
        """更新恐龙状态"""
        # 应用重力
        self.velocity_y += GRAVITY
        self.y += self.velocity_y

        # 落地检测
        ground_y = SCREEN_HEIGHT - self.height - 15
        if self.y >= ground_y:
            self.y = ground_y
            self.velocity_y = 0
            self.is_jumping = False

        # 动画更新
        if not self.is_jumping:
            self.frame_timer += self.animation_speed
            if self.frame_timer >= len(self.animation_frames):
                self.frame_timer = 0
            self.current_frame = int(self.frame_timer)
        else:
            self.current_frame = 0

        # 更新技能和无敌状态
        self.update_skill1_state()
        self.update_skill2_state()
        self.update_skill3_state()  # 新增技能3状态更新
        self.update_invulnerable_state()
        self.update_health_regen(score)
        # 更新视觉效果
        self.update_visual_effects()

    def draw(self):
        """绘制恐龙（矩形版）"""
        current_time = pygame.time.get_ticks()

        # 计算缩放后的尺寸
        scaled_width = int(self.width * self.scale)
        scaled_height = int(self.height * self.scale)
        scaled_x = self.x - (scaled_width - self.width) // 2
        scaled_y = self.y - (scaled_height - self.height) // 2

        # 无敌时闪烁效果
        if self.invulnerable and int(current_time / 100) % 2 == 0:
            alpha = 128
        else:
            alpha = 255

        if self.animation_frames[0] == "rect":
            # 绘制纯矩形恐龙
            dino_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            pygame.draw.rect(dino_surface, (PRIMARY_COLOR[0], PRIMARY_COLOR[1], PRIMARY_COLOR[2], alpha),
                             (0, 0, scaled_width, scaled_height))
            screen.blit(dino_surface, (scaled_x, scaled_y))
        else:
            # 绘制图片恐龙
            dino_frame = pygame.transform.scale(self.animation_frames[self.current_frame],
                                                (scaled_width, scaled_height))
            dino_frame.set_alpha(alpha)
            screen.blit(dino_frame, (scaled_x, scaled_y))


# 障碍物类（适配新窗口）
class Obstacle:
    def __init__(self, obstacle_type, dino_height):
        self.type = obstacle_type
        self.speed = BASE_OBSTACLE_SPEED

        if self.type == "cactus":
            self.width = random.randint(25, 45)  # 放大尺寸
            self.height = random.randint(50, 85)  # 放大尺寸
            self.x = SCREEN_WIDTH
            # 优化：固定底部位置，让所有仙人掌都在同一高度
            self.y = SCREEN_HEIGHT - 15 - 60  # 使用固定高度60作为参考
            self.image = game_resources["cactus_image"]
        elif self.type == "bird":
            self.width = 60  # 放大尺寸
            self.height = 35  # 放大尺寸
            self.x = SCREEN_WIDTH
            # 优化：固定鸟的高度，让所有鸟都在同一高度，且高于恐龙至少5px
            # 恐龙顶部位置 = SCREEN_HEIGHT - dino_height - 15
            # 鸟的底部位置 = 恐龙顶部位置 - 5
            self.y = SCREEN_HEIGHT - dino_height - 15 - 40 - self.height
            self.image = game_resources["bird_image"]

    def update(self, current_speed):
        """更新障碍物位置"""
        self.speed = current_speed
        self.x -= self.speed

    def draw(self):
        """绘制纯矩形障碍物"""
        if self.image == "rect":
            # 纯矩形障碍物
            draw_rect(screen, PRIMARY_COLOR, (self.x, self.y, self.width, self.height), shadow=True)
        else:
            screen.blit(self.image, (self.x, self.y))

    def is_off_screen(self):
        """判断是否移出屏幕"""
        return self.x < -self.width

def open_score_shop():
    """打开积分商店窗口（列表显示+购物车）"""
    global store_bgm, start_menu_bgm
    # 创建商店窗口（与游戏界面大小一致）
    shop_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Score Shop")
    shop_font = load_custom_font(18)  # 缩小字体
    title_font = load_custom_font(32, bold=True)  # 顶部标题保持大字体
    small_font = load_custom_font(16)  # 返回按钮字体，与其他页面保持一致
    medium_font = load_custom_font(20)  # 缩小字体
    button_font = load_custom_font(20)  # 按钮字体，与主页一致

    # 获取总分数和已解锁技能
    total_score = get_total_score()
    unlocked_skills = load_unlocked_skills()
    skills_list = ["Brave Dash", "Zoom Boost", "Lucky Leap"]
    rarity_list = ["rare", "unique", "epic", "legendary"]

    # 道具列表
    items_list = ["Frenzy"]

    # 购物车：记录待购买的技能 {(skill_name, rarity): price}
    cart = {}
    
    # 页面状态："main"=主页面, "detail"=详情页面, "cart"=购物车页面
    current_page = "main"
    selected_item = None  # 当前选中的技能/天赋
    selected_item_type = None  # "skill" 或 "talent"

    # 购买成功提示相关变量（改为警告消息形式）
    checkout_message = None
    checkout_message_start_time = 0
    CHECKOUT_MESSAGE_DURATION = 3000  # 3秒
    
    # 边距
    margin = 30
    
    # 返回按钮矩形（在所有页面共享）
    back_button_rect = pygame.Rect(margin, margin, 80, 36)
    
    # 滚动条相关
    skills_scroll_offset = 0
    talents_scroll_offset = 0
    cart_scroll_offset = 0  # 购物车页面滚动偏移
    scroll_speed = 30
    scrollbar_dragging = False
    scrollbar_drag_type = None  # "skills", "talents", "cart"
    scrollbar_thumb_rect = None
    item_height = 80  # 增加高度
    item_spacing = 15  # 增加间距
    scrollbar_margin = 20  # 列表与滚动条的距离
    
    # 商店使用主菜单背景音乐，不停止也不播放新音乐

    def draw_main_page():
        """绘制主页面（两栏列表+滚动条）"""
        nonlocal cart, skills_scroll_offset, talents_scroll_offset
        
        # 获取鼠标位置
        mouse_pos = pygame.mouse.get_pos()
        
        # 按钮悬停颜色
        BUTTON_HOVER_COLOR = (56, 151, 190)
        
        # 绘制返回按钮
        back_button_color = BUTTON_HOVER_COLOR if back_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
        pygame.draw.rect(shop_screen, back_button_color, back_button_rect)
        pygame.draw.rect(shop_screen, GRAY_LIGHT, back_button_rect, 2)
        back_button_text = small_font.render("Back", True, WHITE)
        shop_screen.blit(back_button_text, (back_button_rect.x + (back_button_rect.width - back_button_text.get_width()) // 2, back_button_rect.y + (back_button_rect.height - back_button_text.get_height()) // 2))
        
        # 标题区域
        title_text = title_font.render("Score Shop", True, PRIMARY_COLOR)
        score_text = shop_font.render(f"Total Score: {total_score}", True, GRAY_DARK)
        cart_cost = sum(cart.values())
        cart_text = shop_font.render(f"Cart: {len(cart)} items - Total: {cart_cost}", True, ACCENT_COLOR if cart else GRAY_DARK)
        
        shop_screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 15))
        shop_screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 50))
        shop_screen.blit(cart_text, (SCREEN_WIDTH // 2 - cart_text.get_width() // 2, 75))
        
        # 两栏布局
        column_width = (SCREEN_WIDTH - 3 * margin) // 2
        skills_column_x = margin
        talents_column_x = 2 * margin + column_width
        
        # 绘制两栏标题
        title_y = 100
        line_y = 135
        list_start_y = 145
        
        skills_title = medium_font.render("Skills", True, PRIMARY_COLOR)
        shop_screen.blit(skills_title, (skills_column_x, title_y))
        pygame.draw.line(shop_screen, GRAY_LIGHT, (skills_column_x, line_y), (skills_column_x + column_width - scrollbar_margin, line_y), 2)
        
        talents_title = medium_font.render("Talents", True, PRIMARY_COLOR)
        shop_screen.blit(talents_title, (talents_column_x, title_y))
        pygame.draw.line(shop_screen, GRAY_LIGHT, (talents_column_x, line_y), (talents_column_x + column_width - scrollbar_margin, line_y), 2)
        
        # 计算滚动区域
        list_area_top = list_start_y
        list_area_bottom = SCREEN_HEIGHT - 100  # 留出底部购物车按钮区域（按钮高度50+间距）
        list_area_height = list_area_bottom - list_area_top
        
        # 绘制技能列表（左栏）
        skills_item_total_height = len(skills_list) * (item_height + item_spacing)
        skills_max_scroll = max(0, skills_item_total_height - list_area_height)
        
        # 创建裁剪区域
        old_clip = shop_screen.get_clip()
        skills_clip_rect = pygame.Rect(skills_column_x, list_area_top, column_width, list_area_height)
        shop_screen.set_clip(skills_clip_rect)
        
        for idx, skill in enumerate(skills_list):
            item_y = list_area_top + idx * (item_height + item_spacing) - skills_scroll_offset
            
            if item_y + item_height > list_area_top and item_y < list_area_bottom:
                # 所有技能都使用嵌套字典结构
                is_unlocked = skill in unlocked_skills and len(unlocked_skills[skill]) > 0
                # 检查购物车中该技能的所有品质
                cart_rarities = [r for s, r in cart.keys() if s == skill]
                in_cart = len(cart_rarities) > 0
                
                if is_unlocked:
                    # 获取已拥有的所有品质
                    owned_rarities = list(unlocked_skills[skill].keys())
                    # 显示第一个品质的信息
                    first_rarity = owned_rarities[0]
                    # 安全地获取使用次数
                    skill_data = unlocked_skills[skill][first_rarity]
                    if isinstance(skill_data, dict) and "uses_left" in skill_data:
                        uses = skill_data["uses_left"]
                    else:
                        uses = 0
                    uses_str = "∞" if uses == -1 else str(uses)
                    if in_cart:
                        # 已拥有且购物车中有其他品质
                        cart_rarity_names = ", ".join([SKILL_RARITY[r]["name"] for r in cart_rarities])
                        status_text = f"Owned | Cart: {cart_rarity_names}"
                    else:
                        status_text = "Owned"
                    status_color = GRAY_DARK
                    button_color = SECONDARY_COLOR if in_cart else GRAY_MEDIUM
                elif in_cart:
                    cart_rarity_names = ", ".join([SKILL_RARITY[r]["name"] for r in cart_rarities])
                    cart_total = sum([p for (s, r), p in cart.items() if s == skill])
                    status_text = f"Cart: {cart_rarity_names} - {cart_total} pts"
                    status_color = ACCENT_COLOR
                    button_color = (100, 150, 200)
                else:
                    status_text = "Click to buy"
                    status_color = WHITE
                    button_color = SECONDARY_COLOR
                
                # 绘制技能项
                item_rect = pygame.Rect(skills_column_x, item_y, column_width - scrollbar_margin, item_height)  # 留出滚动条空间
                pygame.draw.rect(shop_screen, button_color, item_rect)
                pygame.draw.rect(shop_screen, GRAY_LIGHT, item_rect, 2)
                
                # 技能名称（居中偏上）
                skill_text = medium_font.render(skill, True, WHITE)
                text_y = item_y + 15
                shop_screen.blit(skill_text, (skills_column_x + 20, text_y))
                
                # 状态文字（居中偏下）
                status_render = shop_font.render(status_text, True, status_color)
                shop_screen.blit(status_render, (skills_column_x + 20, text_y + 28))
        
        shop_screen.set_clip(old_clip)
        
        # 绘制技能滚动条
        if skills_max_scroll > 0:
            scrollbar_x = skills_column_x + column_width - scrollbar_margin + 5
            pygame.draw.rect(shop_screen, GRAY_LIGHT, (scrollbar_x, list_area_top, 10, list_area_height), border_radius=5)
            
            thumb_height = max(40, list_area_height * list_area_height / skills_item_total_height)
            thumb_y = list_area_top + (skills_scroll_offset / skills_max_scroll) * (list_area_height - thumb_height) if skills_max_scroll > 0 else list_area_top
            skills_scrollbar_thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 10, thumb_height)
            thumb_color = BUTTON_HOVER_COLOR if scrollbar_dragging or skills_scrollbar_thumb_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
            pygame.draw.rect(shop_screen, thumb_color, skills_scrollbar_thumb_rect, border_radius=5)
        else:
            skills_scrollbar_thumb_rect = None
        
        # 绘制天赋列表（右栏）
        talents_item_total_height = len(items_list) * (item_height + item_spacing)
        talents_max_scroll = max(0, talents_item_total_height - list_area_height)
        
        # 创建裁剪区域
        old_clip = shop_screen.get_clip()
        talents_clip_rect = pygame.Rect(talents_column_x, list_area_top, column_width, list_area_height)
        shop_screen.set_clip(talents_clip_rect)
        
        for idx, item in enumerate(items_list):
            item_y = list_area_top + idx * (item_height + item_spacing) - talents_scroll_offset
            
            if item_y + item_height > list_area_top and item_y < list_area_bottom:
                # 天赋使用嵌套字典结构
                is_unlocked = item in unlocked_skills and len(unlocked_skills[item]) > 0
                # 检查购物车中该天赋的所有品质
                cart_rarities = [r for i, r in cart.keys() if i == item]
                in_cart = len(cart_rarities) > 0
                
                if is_unlocked:
                    # 获取已拥有的所有品质
                    owned_rarities = list(unlocked_skills[item].keys())
                    # 显示第一个品质的信息
                    first_rarity = owned_rarities[0]
                    # 安全地获取使用次数
                    item_data = unlocked_skills[item][first_rarity]
                    if isinstance(item_data, dict) and "uses_left" in item_data:
                        uses = item_data["uses_left"]
                    else:
                        uses = 0
                    uses_str = "∞" if uses == -1 else str(uses)
                    if item == "Frenzy":
                        delay_sec = ITEM_RARITY["frenzy"][first_rarity]["delay"] // 1000
                        delay_str = f"{delay_sec}s" if delay_sec > 0 else "Instant"
                        own_status = f"{ITEM_RARITY['frenzy'][first_rarity]['name']} ({delay_str})"
                    elif item == "Agility":
                        fps_boost = int(ITEM_RARITY["agility"][first_rarity]["fps_boost"] * 100)
                        own_status = f"{ITEM_RARITY['agility'][first_rarity]['name']} (+{fps_boost}% FPS)"
                    else:
                        own_status = f"{item} (Owned)"
                    
                    if in_cart:
                        # 已拥有且购物车中有其他品质
                        cart_rarity_names = ", ".join([ITEM_RARITY["frenzy"][r]["name"] if item == "Frenzy" else ITEM_RARITY["agility"][r]["name"] for r in cart_rarities])
                        status_text = f"Owned | Cart: {cart_rarity_names}"
                    else:
                        status_text = "Owned"
                    status_color = GRAY_DARK
                    button_color = SECONDARY_COLOR if in_cart else GRAY_MEDIUM
                elif in_cart:
                    cart_rarity_names = ", ".join([ITEM_RARITY["frenzy"][r]["name"] if item == "Frenzy" else ITEM_RARITY["agility"][r]["name"] for r in cart_rarities])
                    cart_total = sum([p for (i, r), p in cart.items() if i == item])
                    status_text = f"Cart: {cart_rarity_names} - {cart_total} pts"
                    status_color = ACCENT_COLOR
                    button_color = (100, 150, 200)
                else:
                    status_text = "Click to buy"
                    status_color = WHITE
                    button_color = (255, 100, 100) if item == "Frenzy" else (100, 200, 100)
                
                # 绘制天赋项
                item_rect = pygame.Rect(talents_column_x, item_y, column_width - scrollbar_margin, item_height)  # 留出滚动条空间
                pygame.draw.rect(shop_screen, button_color, item_rect)
                pygame.draw.rect(shop_screen, GRAY_LIGHT, item_rect, 2)
                
                # 天赋名称（居中偏上）
                item_text = medium_font.render(item, True, WHITE)
                text_y = item_y + 15
                shop_screen.blit(item_text, (talents_column_x + 20, text_y))
                
                # 状态文字（居中偏下）
                status_render = shop_font.render(status_text, True, status_color)
                shop_screen.blit(status_render, (talents_column_x + 20, text_y + 28))
        
        shop_screen.set_clip(old_clip)
        
        # 绘制天赋滚动条
        if talents_max_scroll > 0:
            scrollbar_x = talents_column_x + column_width - scrollbar_margin + 5
            pygame.draw.rect(shop_screen, GRAY_LIGHT, (scrollbar_x, list_area_top, 10, list_area_height), border_radius=5)
            
            thumb_height = max(40, list_area_height * list_area_height / talents_item_total_height)
            thumb_y = list_area_top + (talents_scroll_offset / talents_max_scroll) * (list_area_height - thumb_height) if talents_max_scroll > 0 else list_area_top
            talents_scrollbar_thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 10, thumb_height)
            thumb_color = BUTTON_HOVER_COLOR if scrollbar_dragging or talents_scrollbar_thumb_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
            pygame.draw.rect(shop_screen, thumb_color, talents_scrollbar_thumb_rect, border_radius=5)
        else:
            talents_scrollbar_thumb_rect = None
        
        # 绘制购物车按钮（底部）- 主页样式 200x50
        cart_button_y = SCREEN_HEIGHT - 80
        cart_button_width = 200
        cart_button_height = 50
        cart_button_x = SCREEN_WIDTH - margin - cart_button_width
        cart_button_rect = pygame.Rect(cart_button_x, cart_button_y, cart_button_width, cart_button_height)
        
        cart_button_color = BUTTON_HOVER_COLOR if cart_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
        pygame.draw.rect(shop_screen, cart_button_color, cart_button_rect)
        pygame.draw.rect(shop_screen, GRAY_LIGHT, cart_button_rect, 2)
        cart_button_text = button_font.render("Cart", True, WHITE)
        shop_screen.blit(cart_button_text, (cart_button_x + (cart_button_width - cart_button_text.get_width()) // 2, cart_button_y + (cart_button_height - cart_button_text.get_height()) // 2))
        
        # 绘制结算按钮 - 主页样式 200x50
        checkout_button_width = 200
        checkout_button_height = 50
        checkout_button_x = cart_button_x - checkout_button_width - 20
        checkout_button_rect = pygame.Rect(checkout_button_x, cart_button_y, checkout_button_width, checkout_button_height)
        
        if cart:
            checkout_color = BUTTON_HOVER_COLOR if checkout_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
        else:
            checkout_color = GRAY_MEDIUM
        pygame.draw.rect(shop_screen, checkout_color, checkout_button_rect)
        pygame.draw.rect(shop_screen, GRAY_LIGHT, checkout_button_rect, 2)
        checkout_text = button_font.render("Check out", True, WHITE)
        shop_screen.blit(checkout_text, (checkout_button_x + (checkout_button_width - checkout_text.get_width()) // 2, cart_button_y + (cart_button_height - checkout_text.get_height()) // 2))
        
        # 绘制购物车详情（左侧）
        cart_detail_x = margin
        cart_detail_y = cart_button_y
        if cart:
            cart_items_text = shop_font.render(f"Cart: {len(cart)} items", True, GRAY_DARK)
            shop_screen.blit(cart_items_text, (cart_detail_x, cart_detail_y))
            cart_total_text = shop_font.render(f"Total: {cart_cost} pts", True, ACCENT_COLOR)
            shop_screen.blit(cart_total_text, (cart_detail_x, cart_detail_y + 20))
        else:
            cart_empty_text = shop_font.render("Cart is empty", True, GRAY_MEDIUM)
            shop_screen.blit(cart_empty_text, (cart_detail_x, cart_detail_y + 10))

    def draw_detail_page():
        """绘制详情页面（选择品质）"""
        nonlocal cart
        
        # 获取鼠标位置
        mouse_pos = pygame.mouse.get_pos()
        
        # 按钮悬停颜色
        BUTTON_HOVER_COLOR = (56, 151, 190)
        
        # 绘制返回按钮
        back_button_color = BUTTON_HOVER_COLOR if back_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
        pygame.draw.rect(shop_screen, back_button_color, back_button_rect)
        pygame.draw.rect(shop_screen, GRAY_LIGHT, back_button_rect, 2)
        back_button_text = small_font.render("Back", True, WHITE)
        shop_screen.blit(back_button_text, (back_button_rect.x + (back_button_rect.width - back_button_text.get_width()) // 2, back_button_rect.y + (back_button_rect.height - back_button_text.get_height()) // 2))
        
        # 标题
        title_text = title_font.render(f"Buy {selected_item}", True, PRIMARY_COLOR)
        shop_screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 15))
        
        # 显示当前积分
        score_text = shop_font.render(f"Your Score: {total_score}", True, GRAY_DARK)
        shop_screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 50))
        
        # 显示购物车信息
        cart_cost = sum(cart.values())
        cart_text = shop_font.render(f"Cart: {len(cart)} items - Total: {cart_cost}", True, ACCENT_COLOR if cart else GRAY_DARK)
        shop_screen.blit(cart_text, (SCREEN_WIDTH // 2 - cart_text.get_width() // 2, 75))
        
        # 两栏布局
        margin = 30
        left_column_width = 400
        right_column_width = SCREEN_WIDTH - left_column_width - 3 * margin
        left_column_x = margin
        right_column_x = left_column_x + left_column_width + margin
        
        # 左侧：技能信息
        left_column_y = 110
        left_column_height = SCREEN_HEIGHT - left_column_y - 30
        
        # 绘制左侧背景
        left_bg_rect = pygame.Rect(left_column_x, left_column_y, left_column_width, left_column_height)
        pygame.draw.rect(shop_screen, (40, 40, 40), left_bg_rect)
        pygame.draw.rect(shop_screen, GRAY_LIGHT, left_bg_rect, 2)

        # 技能图标
        icon_size = 100
        icon_x = left_column_x + (left_column_width - icon_size) // 2
        icon_y = left_column_y + 30

        # 绘制图标容器（5px边框）
        icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
        pygame.draw.rect(shop_screen, (60, 60, 60), icon_rect)
        pygame.draw.rect(shop_screen, GRAY_LIGHT, icon_rect, 5)
        
        # 绘制图标内容
        icon_center_x = icon_x + icon_size // 2
        icon_center_y = icon_y + icon_size // 2
        icon_inner_size = 80
        
        if selected_item == "Brave Dash" and game_resources.get("skill1_icon") != "rect":
            icon_surface = pygame.transform.scale(game_resources["skill1_icon"], (icon_inner_size, icon_inner_size))
            shop_screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
        elif selected_item == "Zoom Boost" and game_resources.get("skill2_icon") != "rect":
            icon_surface = pygame.transform.scale(game_resources["skill2_icon"], (icon_inner_size, icon_inner_size))
            shop_screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
        elif selected_item == "Lucky Leap" and game_resources.get("skill3_icon") != "rect":
            icon_surface = pygame.transform.scale(game_resources["skill3_icon"], (icon_inner_size, icon_inner_size))
            shop_screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
        elif selected_item == "Frenzy" and game_resources.get("frenzy_icon") != "rect":
            icon_surface = pygame.transform.scale(game_resources["frenzy_icon"], (icon_inner_size, icon_inner_size))
            shop_screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
        elif selected_item == "Agility":
            # 矫健天赋使用文字图标
            agility_font = load_custom_font(40, bold=True)
            agility_text = agility_font.render("A", True, (255, 215, 0))
            shop_screen.blit(agility_text, (icon_center_x - agility_text.get_width() // 2, icon_center_y - agility_text.get_height() // 2))
        else:
            # 兜底样式
            draw_diamond(shop_screen, WHITE, icon_center_x, icon_center_y, 30)
            item_text = load_custom_font(20).render(selected_item[:3], True, WHITE)
            shop_screen.blit(item_text, (icon_center_x - item_text.get_width() // 2, icon_center_y - item_text.get_height() // 2))
        
        # 技能名称
        name_y = icon_y + icon_size + 30
        name_text = medium_font.render(selected_item, True, WHITE)
        shop_screen.blit(name_text, (left_column_x + (left_column_width - name_text.get_width()) // 2, name_y))
        
        # 技能类型
        type_text = shop_font.render(selected_item_type.capitalize(), True, GRAY_LIGHT)
        shop_screen.blit(type_text, (left_column_x + (left_column_width - type_text.get_width()) // 2, name_y + 30))
        
        # 技能说明
        description_y = name_y + 70
        description_font = load_custom_font(16)
        
        if selected_item_type == "skill":
            if selected_item == "Brave Dash":
                description = "A quick dash that helps you avoid obstacles."
            elif selected_item == "Zoom Boost":
                description = "Temporarily increases your speed."
            elif selected_item == "Lucky Leap":
                description = "A high jump that lets you reach new heights."
            else:
                description = "A special skill to help you survive."
        else:  # talent
            if selected_item == "Frenzy":
                description = "Gives you a burst of speed and strength."
            elif selected_item == "Agility":
                description = "Increases your movement speed and reflexes."
            else:
                description = "A special talent to enhance your abilities."
        
        # 绘制多行描述
        words = description.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = description_font.render(test_line, True, GRAY_LIGHT)
            if test_surface.get_width() < left_column_width - 40:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # 计算描述文字总高度
        total_desc_height = len(lines) * 25
        # 计算垂直居中起始位置
        desc_area_top = description_y
        desc_area_bottom = left_column_y + left_column_height - 30
        desc_area_height = desc_area_bottom - desc_area_top
        start_y = desc_area_top + (desc_area_height - total_desc_height) // 2

        for i, line in enumerate(lines):
            line_text = description_font.render(line, True, GRAY_LIGHT)
            # 水平居中
            line_x = left_column_x + (left_column_width - line_text.get_width()) // 2
            shop_screen.blit(line_text, (line_x, start_y + i * 25))
        
        # 右侧：品质购买按钮（2x2网格布局）
        right_column_y = 110
        button_gap = 20
        # 计算按钮尺寸：两列布局，间距与左侧margin一致
        button_width = (right_column_width - button_gap) // 2
        button_height = (SCREEN_HEIGHT - right_column_y - 30 - button_gap) // 2
        
        for idx, rarity in enumerate(rarity_list):
            col = idx % 2
            row = idx // 2
            x = right_column_x + col * (button_width + button_gap)
            y = right_column_y + row * (button_height + button_gap)
            
            # 根据物品类型获取数据
            if selected_item_type == "skill":
                rarity_data = SKILL_RARITY[rarity]
                uses_str = "∞" if rarity_data["uses"] == -1 else f"{rarity_data['uses']} uses"
                effect_text = f"Uses: {uses_str}"
            else:  # talent
                if selected_item == "Frenzy":
                    rarity_data = ITEM_RARITY["frenzy"][rarity]
                    delay_sec = rarity_data["delay"] // 1000
                    effect_text = f"Delay: {delay_sec}s" if delay_sec > 0 else "Instant"
                elif selected_item == "Agility":
                    rarity_data = ITEM_RARITY["agility"][rarity]
                    fps_boost = int(rarity_data["fps_boost"] * 100)
                    effect_text = f"FPS: +{fps_boost}%"
                else:
                    rarity_data = ITEM_RARITY["frenzy"][rarity]
                    effect_text = "Unknown"
            
            color = rarity_data["color"]
            
            # 检查是否已购买或已在购物车
            # 允许购买同种技能的不同品质
            # 所有技能和天赋都使用嵌套字典结构
            is_owned = selected_item in unlocked_skills and len(unlocked_skills[selected_item]) > 0 and rarity in unlocked_skills[selected_item]
            in_cart = (selected_item, rarity) in cart
            can_afford = total_score >= rarity_data["price"]
            # 检查是否已拥有该技能的任何品质
            has_any_rarity = selected_item in unlocked_skills
            
            if is_owned:
                button_color = GRAY_MEDIUM
                border_color = GRAY_LIGHT
                text_color = GRAY_LIGHT
                status_str = "Owned"
            elif in_cart:
                button_color = (100, 150, 200)
                border_color = ACCENT_COLOR
                text_color = WHITE
                status_str = "In Cart"
            elif not can_afford:
                button_color = (80, 80, 80)
                border_color = GRAY_DARK
                text_color = GRAY_MEDIUM
                status_str = "Need Points"
            else:
                button_color = color
                border_color = WHITE
                text_color = BLACK if rarity in ["rare", "unique"] else WHITE
                status_str = "Click to Add"
            
            # 绘制品质按钮
            rarity_rect = pygame.Rect(x, y, button_width, button_height)
            pygame.draw.rect(shop_screen, button_color, rarity_rect)
            pygame.draw.rect(shop_screen, border_color, rarity_rect, 3)
            
            # 品质名称和价格
            name_text = medium_font.render(f"{rarity_data['name']}", True, text_color)
            price_text = shop_font.render(f"{rarity_data['price']} pts", True, text_color)
            effect_render = shop_font.render(effect_text, True, text_color)
            status_render = shop_font.render(status_str, True, ACCENT_COLOR if in_cart else text_color)
            
            shop_screen.blit(name_text, (x + 15, y + 15))
            shop_screen.blit(price_text, (x + 15, y + 40))
            shop_screen.blit(effect_render, (x + 15, y + 60))
            # 状态文字放在右下角，距离右边框和底边框都是15像素
            shop_screen.blit(status_render, (x + button_width - status_render.get_width() - 15, y + button_height - status_render.get_height() - 15))

    def draw_cart_page():
        """绘制购物车页面（带滚动条）"""
        nonlocal cart, cart_scroll_offset
        
        # 获取鼠标位置
        mouse_pos = pygame.mouse.get_pos()
        
        # 按钮悬停颜色
        BUTTON_HOVER_COLOR = (56, 151, 190)
        
        # 绘制返回按钮
        back_button_color = BUTTON_HOVER_COLOR if back_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
        pygame.draw.rect(shop_screen, back_button_color, back_button_rect)
        pygame.draw.rect(shop_screen, GRAY_LIGHT, back_button_rect, 2)
        back_button_text = small_font.render("Back", True, WHITE)
        shop_screen.blit(back_button_text, (back_button_rect.x + (back_button_rect.width - back_button_text.get_width()) // 2, back_button_rect.y + (back_button_rect.height - back_button_text.get_height()) // 2))
        
        # 标题
        title_text = title_font.render("Shopping Cart", True, PRIMARY_COLOR)
        shop_screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 15))
        
        # 显示当前积分
        score_text = shop_font.render(f"Your Score: {total_score}", True, GRAY_DARK)
        shop_screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 50))
        
        # 显示购物车总价
        cart_cost = sum(cart.values())
        cart_text = shop_font.render(f"Total: {cart_cost} pts", True, ACCENT_COLOR if cart else GRAY_DARK)
        shop_screen.blit(cart_text, (SCREEN_WIDTH // 2 - cart_text.get_width() // 2, 75))
        
        if not cart:
            # 购物车为空
            empty_text = medium_font.render("Your cart is empty", True, GRAY_MEDIUM)
            shop_screen.blit(empty_text, (SCREEN_WIDTH // 2 - empty_text.get_width() // 2, SCREEN_HEIGHT // 2))
            tip_text = shop_font.render("Click on items to add them to your cart", True, GRAY_MEDIUM)
            shop_screen.blit(tip_text, (SCREEN_WIDTH // 2 - tip_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
        else:
            # 购物车列表区域设置 - 优化布局，占满更多空间
            list_start_y = 110
            list_item_height = 80
            list_spacing = 20
            list_area_bottom = SCREEN_HEIGHT - 30  # 底部只留少量边距
            list_area_height = list_area_bottom - list_start_y
            
            # 计算滚动相关
            cart_item_total_height = len(cart) * (list_item_height + list_spacing)
            cart_max_scroll = max(0, cart_item_total_height - list_area_height)
            
            # 创建裁剪区域
            old_clip = shop_screen.get_clip()
            cart_clip_rect = pygame.Rect(margin + 20, list_start_y, SCREEN_WIDTH - 2 * margin - 40, list_area_height)
            shop_screen.set_clip(cart_clip_rect)
            
            # 绘制购物车物品列表
            for idx, ((item, rarity), price) in enumerate(cart.items()):
                item_y = list_start_y + idx * (list_item_height + list_spacing) - cart_scroll_offset
                
                # 如果超出显示区域，跳过
                if item_y + list_item_height < list_start_y or item_y > list_area_bottom:
                    continue
                
                # 获取物品信息
                if item in skills_list:
                    rarity_data = SKILL_RARITY[rarity]
                    item_type = "Skill"
                else:
                    if item == "Frenzy":
                        rarity_data = ITEM_RARITY["frenzy"][rarity]
                    elif item == "Agility":
                        rarity_data = ITEM_RARITY["agility"][rarity]
                    else:
                        rarity_data = ITEM_RARITY["frenzy"][rarity]
                    item_type = "Talent"
                
                # 计算物品框宽度和删除按钮位置
                delete_button_width = 80
                delete_button_height = list_item_height
                # 留出滚动条空间
                item_rect_width = SCREEN_WIDTH - 2 * margin - 40 - delete_button_width - 20 - scrollbar_margin
                
                # 根据稀有度获取背景颜色
                rarity_color = rarity_data["color"]
                bg_color = tuple(int(c * 0.6) for c in rarity_color)
                
                # 绘制物品背景
                item_rect = pygame.Rect(margin + 20, item_y, item_rect_width, list_item_height)
                pygame.draw.rect(shop_screen, bg_color, item_rect)
                pygame.draw.rect(shop_screen, GRAY_LIGHT, item_rect, 2)
                
                # 物品名称和类型
                item_name_text = medium_font.render(f"{item}", True, WHITE)
                shop_screen.blit(item_name_text, (margin + 40, item_y + 12))
                
                item_info_text = shop_font.render(f"{item_type} - {rarity_data['name']}", True, GRAY_LIGHT)
                shop_screen.blit(item_info_text, (margin + 40, item_y + 38))
                
                # 价格
                price_text = shop_font.render(f"{price} pts", True, ACCENT_COLOR)
                shop_screen.blit(price_text, (margin + 20 + item_rect_width - 10 - price_text.get_width(), item_y + 22))
                
                # 删除按钮
                delete_button_x = margin + 20 + item_rect_width + 10
                delete_button_y = item_y
                delete_button_rect = pygame.Rect(delete_button_x, delete_button_y, delete_button_width, delete_button_height)
                
                # 番茄红/深红悬停效果
                TOMATO_RED = (255, 99, 71)
                DARK_TOMATO = (200, 50, 40)
                delete_color = DARK_TOMATO if delete_button_rect.collidepoint(mouse_pos) else TOMATO_RED
                pygame.draw.rect(shop_screen, delete_color, delete_button_rect)
                pygame.draw.rect(shop_screen, GRAY_LIGHT, delete_button_rect, 2)
                delete_text = button_font.render("Remove", True, WHITE)
                shop_screen.blit(delete_text, (delete_button_x + (delete_button_width - delete_text.get_width()) // 2, delete_button_y + (delete_button_height - delete_text.get_height()) // 2))
            
            shop_screen.set_clip(old_clip)
            
            # 绘制购物车滚动条
            if cart_max_scroll > 0:
                scrollbar_x = SCREEN_WIDTH - margin - scrollbar_margin + 5
                pygame.draw.rect(shop_screen, GRAY_LIGHT, (scrollbar_x, list_start_y, 10, list_area_height), border_radius=5)
                
                thumb_height = max(40, list_area_height * list_area_height / cart_item_total_height)
                thumb_y = list_start_y + (cart_scroll_offset / cart_max_scroll) * (list_area_height - thumb_height) if cart_max_scroll > 0 else list_start_y
                cart_scrollbar_thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 10, thumb_height)
                thumb_color = BUTTON_HOVER_COLOR if scrollbar_dragging and scrollbar_drag_type == "cart" else SECONDARY_COLOR
                pygame.draw.rect(shop_screen, thumb_color, cart_scrollbar_thumb_rect, border_radius=5)
            else:
                cart_scrollbar_thumb_rect = None
            


    # 商店主循环
    shop_running = True
    while shop_running:
        shop_screen.fill(BACKGROUND_COLOR)
        current_time = pygame.time.get_ticks()

        # 处理购买成功消息显示
        if checkout_message and current_time - checkout_message_start_time > CHECKOUT_MESSAGE_DURATION:
            checkout_message = None

        # 事件循环
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                shop_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                
                # 检查是否点击了返回按钮
                if back_button_rect.collidepoint(mouse_pos):
                    if current_page == "detail" or current_page == "cart":
                        current_page = "main"
                    else:
                        shop_running = False
                
                # 主页面事件处理
                elif current_page == "main":
                    # 计算两栏布局
                    column_width = (SCREEN_WIDTH - 3 * margin) // 2
                    skills_column_x = margin
                    talents_column_x = 2 * margin + column_width
                    
                    # 计算滚动区域
                    list_area_top = 135
                    list_area_bottom = SCREEN_HEIGHT - 80
                    list_area_height = list_area_bottom - list_area_top
                    
                    # 检查是否点击了技能滚动条
                    skills_item_total_height = len(skills_list) * (item_height + item_spacing)
                    skills_max_scroll = max(0, skills_item_total_height - list_area_height)
                    if skills_max_scroll > 0:
                        scrollbar_x = skills_column_x + column_width - scrollbar_margin + 5
                        scrollbar_rect = pygame.Rect(scrollbar_x, list_area_top, 10, list_area_height)
                        if scrollbar_rect.collidepoint(mouse_pos):
                            scrollbar_dragging = True
                            scrollbar_drag_type = "skills"
                    
                    # 检查是否点击了天赋滚动条
                    talents_item_total_height = len(items_list) * (item_height + item_spacing)
                    talents_max_scroll = max(0, talents_item_total_height - list_area_height)
                    if talents_max_scroll > 0:
                        scrollbar_x = talents_column_x + column_width - scrollbar_margin + 5
                        scrollbar_rect = pygame.Rect(scrollbar_x, list_area_top, 10, list_area_height)
                        if scrollbar_rect.collidepoint(mouse_pos):
                            scrollbar_dragging = True
                            scrollbar_drag_type = "talents"
                    
                    # 检查是否点击了技能列表项
                    for idx, skill in enumerate(skills_list):
                        item_y = list_area_top + idx * (item_height + item_spacing) - skills_scroll_offset
                        if item_y + item_height > list_area_top and item_y < list_area_bottom:
                            item_rect = pygame.Rect(skills_column_x, item_y, column_width - scrollbar_margin, item_height)  # 匹配绘制区域
                            if item_rect.collidepoint(mouse_pos):
                                # 允许购买同种技能的不同品质
                                selected_item = skill
                                selected_item_type = "skill"
                                current_page = "detail"
                    
                    # 检查是否点击了天赋列表项
                    for idx, item in enumerate(items_list):
                        item_y = list_area_top + idx * (item_height + item_spacing) - talents_scroll_offset
                        if item_y + item_height > list_area_top and item_y < list_area_bottom:
                            item_rect = pygame.Rect(talents_column_x, item_y, column_width - scrollbar_margin, item_height)  # 匹配绘制区域
                            if item_rect.collidepoint(mouse_pos):
                                # 允许购买同种天赋的不同品质
                                selected_item = item
                                selected_item_type = "talent"
                                current_page = "detail"
                    
                    # 检查是否点击了购物车按钮
                    cart_button_y = SCREEN_HEIGHT - 80
                    cart_button_width = 200
                    cart_button_height = 50
                    cart_button_x = SCREEN_WIDTH - margin - cart_button_width
                    cart_button_rect = pygame.Rect(cart_button_x, cart_button_y, cart_button_width, cart_button_height)
                    if cart_button_rect.collidepoint(mouse_pos):
                        current_page = "cart"
                    
                    # 检查是否点击了结算按钮
                    checkout_button_width = 200
                    checkout_button_height = 50
                    checkout_button_x = cart_button_x - checkout_button_width - 20
                    checkout_button_rect = pygame.Rect(checkout_button_x, cart_button_y, checkout_button_width, checkout_button_height)
                    if checkout_button_rect.collidepoint(mouse_pos) and cart:
                        total_cost = sum(cart.values())
                        if total_score >= total_cost:
                            remaining_score_after_unlock = total_score - total_cost
                            total_score = remaining_score_after_unlock
                            save_total_score_to_db(total_score)
                            # 解锁所有购物车中的技能和道具
                            unlocked_count = 0
                            for (item, rarity), price in cart.items():
                                save_unlocked_skill(item, rarity)
                                if item in skills_list:
                                    # 所有技能和天赋都使用嵌套字典结构
                                    if item not in unlocked_skills:
                                        unlocked_skills[item] = {}
                                    unlocked_skills[item][rarity] = {"rarity": rarity, "uses_left": SKILL_RARITY[rarity]["uses"]}
                                else:
                                    # 所有技能和天赋都使用嵌套字典结构
                                    if item not in unlocked_skills:
                                        unlocked_skills[item] = {}
                                    if item == "Frenzy":
                                        unlocked_skills[item][rarity] = {"rarity": rarity, "uses_left": ITEM_RARITY["frenzy"][rarity]["uses"]}
                                    elif item == "Agility":
                                        unlocked_skills[item][rarity] = {"rarity": rarity, "uses_left": ITEM_RARITY["agility"][rarity]["uses"]}
                                unlocked_count += 1
                            cart = {}
                            # 显示扣除点数的消息
                            checkout_message = f"Deducted {total_cost} points! Unlocked {unlocked_count} items."
                            checkout_message_start_time = current_time
                
                # 详情页面事件处理
                elif current_page == "detail":
                    # 右侧：品质购买按钮（2x2网格布局）
                    margin = 30
                    left_column_width = 400
                    right_column_width = SCREEN_WIDTH - left_column_width - 3 * margin
                    right_column_x = margin + left_column_width + margin
                    right_column_y = 110
                    button_gap = 20
                    button_width = (right_column_width - button_gap) // 2
                    button_height = (SCREEN_HEIGHT - right_column_y - 30 - button_gap) // 2
                    
                    for idx, rarity in enumerate(rarity_list):
                        col = idx % 2
                        row = idx // 2
                        x = right_column_x + col * (button_width + button_gap)
                        y = right_column_y + row * (button_height + button_gap)
                        
                        # 根据物品类型获取数据
                        if selected_item_type == "skill":
                            rarity_data = SKILL_RARITY[rarity]
                        else:
                            if selected_item == "Frenzy":
                                rarity_data = ITEM_RARITY["frenzy"][rarity]
                            elif selected_item == "Agility":
                                rarity_data = ITEM_RARITY["agility"][rarity]
                            else:
                                rarity_data = ITEM_RARITY["frenzy"][rarity]
                        
                        # 所有技能和天赋都使用嵌套字典结构
                        is_owned = selected_item in unlocked_skills and len(unlocked_skills[selected_item]) > 0 and rarity in unlocked_skills[selected_item]
                        in_cart = (selected_item, rarity) in cart
                        can_afford = total_score >= rarity_data["price"]
                        
                        if not is_owned and not in_cart and can_afford:
                            rarity_rect = pygame.Rect(x, y, button_width, button_height)
                            if rarity_rect.collidepoint(mouse_pos):
                                # 添加到购物车（允许同种技能的不同品质同时存在）
                                cart[(selected_item, rarity)] = rarity_data["price"]
                                current_page = "main"
                
                # 购物车页面事件处理
                elif current_page == "cart":
                    if cart:
                        # 购物车列表区域设置 - 与绘制时一致
                        list_start_y = 110
                        list_item_height = 80
                        list_spacing = 20
                        list_area_bottom = SCREEN_HEIGHT - 30
                        list_area_height = list_area_bottom - list_start_y
                        
                        # 计算滚动相关
                        cart_item_total_height = len(cart) * (list_item_height + list_spacing)
                        cart_max_scroll = max(0, cart_item_total_height - list_area_height)
                        
                        # 检查是否点击了购物车滚动条
                        if cart_max_scroll > 0:
                            scrollbar_x = SCREEN_WIDTH - margin - scrollbar_margin + 5
                            scrollbar_rect = pygame.Rect(scrollbar_x, list_start_y, 10, list_area_height)
                            if scrollbar_rect.collidepoint(mouse_pos):
                                scrollbar_dragging = True
                                scrollbar_drag_type = "cart"
                        
                        # 检查是否点击了删除按钮
                        for idx, ((item, rarity), price) in enumerate(list(cart.items())):
                            item_y = list_start_y + idx * (list_item_height + list_spacing) - cart_scroll_offset
                            # 如果超出显示区域，跳过
                            if item_y + list_item_height < list_start_y or item_y > list_area_bottom:
                                continue
                            # 计算删除按钮位置（与绘制时一致）
                            delete_button_width = 80
                            delete_button_height = list_item_height
                            item_rect_width = SCREEN_WIDTH - 2 * margin - 40 - delete_button_width - 20 - scrollbar_margin
                            delete_button_x = margin + 20 + item_rect_width + 10
                            delete_button_y = item_y
                            delete_button_rect = pygame.Rect(delete_button_x, delete_button_y, delete_button_width, delete_button_height)
                            
                            if delete_button_rect.collidepoint(mouse_pos):
                                del cart[(item, rarity)]
                                break
                        

            
            elif event.type == pygame.MOUSEBUTTONUP:
                scrollbar_dragging = False
            
            elif event.type == pygame.MOUSEMOTION and scrollbar_dragging:
                mouse_pos = event.pos
                # 计算两栏布局
                column_width = (SCREEN_WIDTH - 3 * margin) // 2
                skills_column_x = margin
                talents_column_x = 2 * margin + column_width
                
                # 计算滚动区域
                list_area_top = 145
                list_area_bottom = SCREEN_HEIGHT - 100
                list_area_height = list_area_bottom - list_area_top
                
                if scrollbar_drag_type == "skills":
                    skills_item_total_height = len(skills_list) * (item_height + item_spacing)
                    skills_max_scroll = max(0, skills_item_total_height - list_area_height)
                    scrollbar_x = skills_column_x + column_width - scrollbar_margin + 5
                    scrollbar_rect = pygame.Rect(scrollbar_x, list_area_top, 10, list_area_height)
                    
                    if skills_max_scroll > 0:
                        thumb_height = max(40, list_area_height * list_area_height / skills_item_total_height)
                        new_thumb_y = max(list_area_top, min(mouse_pos[1], list_area_bottom - thumb_height))
                        skills_scroll_offset = int((new_thumb_y - list_area_top) / (list_area_height - thumb_height) * skills_max_scroll)
                
                elif scrollbar_drag_type == "talents":
                    talents_item_total_height = len(items_list) * (item_height + item_spacing)
                    talents_max_scroll = max(0, talents_item_total_height - list_area_height)
                    scrollbar_x = talents_column_x + column_width - scrollbar_margin + 5
                    scrollbar_rect = pygame.Rect(scrollbar_x, list_area_top, 10, list_area_height)
                    
                    if talents_max_scroll > 0:
                        thumb_height = max(40, list_area_height * list_area_height / talents_item_total_height)
                        new_thumb_y = max(list_area_top, min(mouse_pos[1], list_area_bottom - thumb_height))
                        talents_scroll_offset = int((new_thumb_y - list_area_top) / (list_area_height - thumb_height) * talents_max_scroll)
                
                elif scrollbar_drag_type == "cart":
                    list_start_y = 110
                    list_area_height = SCREEN_HEIGHT - 100 - list_start_y
                    cart_item_total_height = len(cart) * (70 + 15)
                    cart_max_scroll = max(0, cart_item_total_height - list_area_height)
                    scrollbar_x = SCREEN_WIDTH - margin - scrollbar_margin + 5
                    scrollbar_rect = pygame.Rect(scrollbar_x, list_start_y, 10, list_area_height)
                    
                    if cart_max_scroll > 0:
                        thumb_height = max(40, list_area_height * list_area_height / cart_item_total_height)
                        new_thumb_y = max(list_start_y, min(mouse_pos[1], list_start_y + list_area_height - thumb_height))
                        cart_scroll_offset = int((new_thumb_y - list_start_y) / (list_area_height - thumb_height) * cart_max_scroll)
            
            elif event.type == pygame.MOUSEWHEEL:
                # 鼠标滚轮滚动
                column_width = (SCREEN_WIDTH - 3 * margin) // 2
                skills_column_x = margin
                talents_column_x = 2 * margin + column_width
                
                list_area_top = 145
                list_area_bottom = SCREEN_HEIGHT - 100
                list_area_height = list_area_bottom - list_area_top
                
                mouse_pos = pygame.mouse.get_pos()
                
                # 判断鼠标在哪个栏
                if current_page == "main":
                    skills_item_total_height = len(skills_list) * (item_height + item_spacing)
                    skills_max_scroll = max(0, skills_item_total_height - list_area_height)
                    
                    talents_item_total_height = len(items_list) * (item_height + item_spacing)
                    talents_max_scroll = max(0, talents_item_total_height - list_area_height)
                    
                    if mouse_pos[0] < skills_column_x + column_width:
                        # 技能栏
                        if skills_max_scroll > 0:
                            skills_scroll_offset = max(0, min(skills_scroll_offset - event.y * scroll_speed, skills_max_scroll))
                    elif mouse_pos[0] >= talents_column_x:
                        # 天赋栏
                        if talents_max_scroll > 0:
                            talents_scroll_offset = max(0, min(talents_scroll_offset - event.y * scroll_speed, talents_max_scroll))
                
                elif current_page == "cart":
                    # 购物车页面滚轮滚动
                    list_start_y = 110
                    list_area_height = SCREEN_HEIGHT - 100 - list_start_y
                    cart_item_total_height = len(cart) * (70 + 15)
                    cart_max_scroll = max(0, cart_item_total_height - list_area_height)
                    
                    if cart_max_scroll > 0:
                        cart_scroll_offset = max(0, min(cart_scroll_offset - event.y * scroll_speed, cart_max_scroll))

        # 绘制页面
        if current_page == "main":
            draw_main_page()
        elif current_page == "detail":
            draw_detail_page()
        elif current_page == "cart":
            draw_cart_page()

        # 绘制结算消息（警告形式）
        if checkout_message:
            message_font = load_custom_font(20, bold=True)
            message_color = (255, 200, 0)  # 金黄色警告
            message_text = message_font.render(checkout_message, True, message_color)
            message_x = SCREEN_WIDTH // 2 - message_text.get_width() // 2
            message_y = 50  # 顶部显示
            # 绘制背景
            padding = 10
            bg_rect = pygame.Rect(message_x - padding, message_y - padding, 
                                  message_text.get_width() + 2 * padding, 
                                  message_text.get_height() + 2 * padding)
            pygame.draw.rect(shop_screen, (50, 50, 50, 200), bg_rect)
            pygame.draw.rect(shop_screen, message_color, bg_rect, 2)
            shop_screen.blit(message_text, (message_x, message_y))

        pygame.display.flip()
        clock.tick(FPS)

    # 关闭商店
    if store_bgm is not None:
        store_bgm.stop()
        store_bgm = None

    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Escape")

    global game_started
    if not game_started and (start_menu_bgm is None or not pygame.mixer.Channel(0).get_busy()):
        try:
            start_menu_bgm = pygame.mixer.Sound(START_MENU_BGM_PATH)
            start_menu_bgm.set_volume(START_MENU_BGM_VOLUME)
            start_menu_bgm.play(-1)
        except:
            print(f"警告：开始界面背景音乐 {START_MENU_BGM_PATH} 加载失败")
            start_menu_bgm = None

def draw_success_popup_with_rarity(screen, skill_info_list, remaining_score, animation_progress):
    """绘制购买成功弹窗（支持技能等级显示）"""
    popup_x = (700 - SUCCESS_POPUP_WIDTH) // 2
    popup_y = (500 - SUCCESS_POPUP_HEIGHT) // 2 - 20

    popup_surface = pygame.Surface((SUCCESS_POPUP_WIDTH, SUCCESS_POPUP_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(popup_surface, SUCCESS_POPUP_BG, (0, 0, SUCCESS_POPUP_WIDTH, SUCCESS_POPUP_HEIGHT), border_radius=0)
    pygame.draw.rect(popup_surface, SUCCESS_POPUP_BORDER, (0, 0, SUCCESS_POPUP_WIDTH, SUCCESS_POPUP_HEIGHT), 4, border_radius=0)

    title_font = load_custom_font(28, bold=True)
    content_font = load_custom_font(20)
    tip_font = load_custom_font(16)

    if len(skill_info_list) == 1:
        title_text = title_font.render("Skill Unlocked!", True, SUCCESS_TITLE_COLOR)
    else:
        title_text = title_font.render(f"{len(skill_info_list)} Skills Unlocked!", True, SUCCESS_TITLE_COLOR)
    title_rect = title_text.get_rect(center=(SUCCESS_POPUP_WIDTH // 2, 40))
    popup_surface.blit(title_text, title_rect)

    # 显示解锁的技能和等级
    y_offset = 75
    for skill, rarity_name in skill_info_list[:3]:
        skill_text = content_font.render(f"{skill} ({rarity_name})", True, SUCCESS_TEXT_COLOR)
        skill_rect = skill_text.get_rect(center=(SUCCESS_POPUP_WIDTH // 2, y_offset))
        popup_surface.blit(skill_text, skill_rect)
        y_offset += 25
    if len(skill_info_list) > 3:
        more_text = content_font.render(f"...and {len(skill_info_list) - 3} more", True, SUCCESS_TEXT_COLOR)
        more_rect = more_text.get_rect(center=(SUCCESS_POPUP_WIDTH // 2, y_offset))
        popup_surface.blit(more_text, more_rect)
        y_offset += 25

    score_text = content_font.render(f"Remaining: {remaining_score}", True, SUCCESS_TEXT_COLOR)
    score_rect = score_text.get_rect(center=(SUCCESS_POPUP_WIDTH // 2, y_offset + 10))
    popup_surface.blit(score_text, score_rect)

    tip_text = tip_font.render("Returning to game...", True, GRAY_MEDIUM)
    tip_rect = tip_text.get_rect(center=(SUCCESS_POPUP_WIDTH // 2, y_offset + 40))
    popup_surface.blit(tip_text, tip_rect)

    screen.blit(popup_surface, (popup_x, popup_y))

def open_html_window():
   
    global start_menu_bgm
    # 创建HTML窗口（尺寸与商店一致600x400）
    html_screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Game Guide")
    html_font = load_custom_font(20)
    title_font = load_custom_font(36, bold=True)

    # 读取本地HTML文件内容（替换为你的HTML路径）
    HTML_FILE_PATH = "guide.html"  # 你的HTML文件路径
    html_content = ""
    try:
        with open(HTML_FILE_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        html_content = f"Failed to load HTML: {str(e)}"

    # 处理HTML内容为可显示的文本（简化处理，提取纯文本）
    # 若需要解析HTML标签，可使用html.parser模块，这里简化为换行分隔
    display_lines = []
    # 替换HTML标签换行符，分割成多行（适配窗口宽度）
    import re
    clean_text = re.sub(r'<[^>]+>', '\n', html_content)  # 移除HTML标签
    clean_text = re.sub(r'\n+', '\n', clean_text).strip()  # 合并空行
    # 按窗口宽度拆分长文本（每行最多35个字符）
    for line in clean_text.split('\n'):
        if len(line) > 35:
            # 长行拆分
            for i in range(0, len(line), 35):
                display_lines.append(line[i:i+35])
        else:
            display_lines.append(line)

    # 窗口主循环
    html_running = True
    while html_running:
        html_screen.fill(BACKGROUND_COLOR)

        # 事件循环
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                html_running = False
            if event.type == pygame.KEYDOWN:
                # 按Q关闭窗口
                if event.key == pygame.K_q:
                    html_running = False

        # 绘制窗口标题
        title_text = title_font.render("Game Guide", True, PRIMARY_COLOR)
        html_screen.blit(title_text, (600//2 - title_text.get_width()//2, 30))

        # 绘制文本内容（滚动显示，最多显示15行）
        y_offset = 80
        line_spacing = 25
        max_display_lines = 15
        for i, line in enumerate(display_lines[:max_display_lines]):
            text_surface = html_font.render(line, True, GRAY_DARK)
            html_screen.blit(text_surface, (40, y_offset + i*line_spacing))

        # 绘制关闭提示
        close_text = html_font.render("Press Q to close", True, ACCENT_COLOR)
        html_screen.blit(close_text, (600//2 - close_text.get_width()//2, 360))

        pygame.display.flip()
        clock.tick(FPS)

    # 关闭窗口后恢复原游戏窗口
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Escape")

    # 恢复开始界面BGM
    global game_started
    if not game_started and (start_menu_bgm is None or not pygame.mixer.Channel(0).get_busy()):
        try:
            start_menu_bgm = pygame.mixer.Sound(START_MENU_BGM_PATH)
            start_menu_bgm.set_volume(START_MENU_BGM_VOLUME)
            start_menu_bgm.play(-1)
        except:
            print(f"警告：开始界面背景音乐 {START_MENU_BGM_PATH} 加载失败")
            start_menu_bgm = None


def draw_skill_select_screen():
    """绘制技能选择界面"""
    global selected_skill

    # 创建技能选择界面容器
    select_x = (SCREEN_WIDTH - SKILL_SELECT_WIDTH) // 2
    select_y = (SCREEN_HEIGHT - SKILL_SELECT_HEIGHT) // 2

    # 绘制背景面板
    draw_rect(screen, SKILL_SELECT_BG,
              (select_x, select_y, SKILL_SELECT_WIDTH, SKILL_SELECT_HEIGHT),
              shadow=True)

    # 绘制标题
    title_font = load_custom_font(SKILL_SELECT_TITLE_FONT_SIZE, bold=True)
    title_text = title_font.render("Select Skill For This Round", True, PRIMARY_COLOR)
    screen.blit(title_text, (
        select_x + SKILL_SELECT_WIDTH // 2 - title_text.get_width() // 2,
        select_y + 30
    ))

    # 绘制提示文字
    prompt_font = load_custom_font(20)
    prompt_text = prompt_font.render(SKILL_SELECT_PROMPT_TEXT, True, GRAY_DARK)
    screen.blit(prompt_text, (
        select_x + SKILL_SELECT_WIDTH // 2 - prompt_text.get_width() // 2,
        select_y + SKILL_SELECT_HEIGHT - 40
    ))

    # 技能列表
    skills = [
        ("skill1", "Last Effort (LSHIFT)"),
        ("skill2", "Quick Heal (TAB)"),
        ("skill3", "命之跳跃 (CAPSLOCK)")
    ]

    # 绘制技能选项
    item_font = load_custom_font(SKILL_SELECT_ITEM_FONT_SIZE)
    start_y = select_y + 100

    for idx, (skill_key, skill_name) in enumerate(skills):
        # 计算选项位置
        item_y = start_y + idx * (SKILL_SELECT_ITEM_HEIGHT + SKILL_SELECT_ITEM_SPACING)
        item_rect = (
            select_x + 50,
            item_y,
            SKILL_SELECT_WIDTH - 100,
            SKILL_SELECT_ITEM_HEIGHT
        )

        # 确定选项颜色
        if selected_skill == skill_key:
            bg_color = SKILL_SELECT_ACTIVE_COLOR
            text_color = WHITE
        else:
            bg_color = SKILL_SELECT_DISABLE_COLOR if selected_skill is not None else GRAY_LIGHT
            text_color = SKILL_SELECT_TEXT_COLOR

        # 绘制选项背景
        draw_rect(screen, bg_color, item_rect)

        # 绘制技能文字
        skill_text = item_font.render(f"{idx + 1}. {skill_name}", True, text_color)
        screen.blit(skill_text, (
            item_rect[0] + 20,
            item_rect[1] + (SKILL_SELECT_ITEM_HEIGHT - skill_text.get_height()) // 2
        ))

# 滚动地面类（适配新窗口）
class ScrollingGround:
    def __init__(self):
        self.y = SCREEN_HEIGHT - 15  # 适配新窗口
        self.width = SCREEN_WIDTH
        self.height = 15  # 放大地面高度
        self.speed = BASE_OBSTACLE_SPEED
        self.x1 = 0
        self.x2 = self.width
        self.stripes = []  # 地面条纹装饰

        # 生成地面条纹（适配新窗口）
        for i in range(0, SCREEN_WIDTH * 2, 25):
            self.stripes.append(i)

    def update(self, current_speed):
        """更新滚动地面位置"""
        self.speed = current_speed
        self.x1 -= self.speed
        self.x2 -= self.speed

        if self.x1 <= -self.width:
            self.x1 = self.width
        if self.x2 <= -self.width:
            self.x2 = self.width

        # 更新条纹位置
        for i in range(len(self.stripes)):
            self.stripes[i] -= self.speed
            if self.stripes[i] < -25:
                self.stripes[i] = SCREEN_WIDTH + 25

    def draw(self):
        """绘制纯矩形地面"""
        # 地面主体（纯矩形）
        draw_rect(screen, GROUND_COLOR, (0, self.y, self.width, self.height), shadow=True)

        # 地面条纹装饰（纯矩形）
        for x in self.stripes:
            pygame.draw.rect(screen, GRAY_MEDIUM, (x, self.y + 5, 12, 5))


def get_jump_boost_icon_pos(dino, score):
    """计算跳跃状态图标位置（优先级：移动速度→FPS提升→跳跃→额外血量）"""
    # 基础位置：FPS提升图标右侧15px（FPS提升图标常驻显示在速度图标右侧）
    base_x = FPS_BOOST_ICON_X_POS + FPS_BOOST_ICON_CONTAINER_SIZE + 15

    # 检查额外血量是否显示（有额外血量且已解锁）
    extra_health_visible = False
    current_difficulty = get_current_difficulty(score)
    if current_difficulty >= 2 and dino.extra_health > 0:
        extra_health_visible = True

    # 检查跳跃状态是否显示（技能3激活中）
    jump_boost_visible = dino.skill3_active and dino.skill3_fps_boost > 0

    # 新增：检查生命值恢复冷却是否显示
    health_regen_visible = dino.regen_cooldown  # 冷却中显示

    pos = {
        "jump_boost_x": base_x,
        "extra_health_x": base_x + JUMP_BOOST_ICON_CONTAINER_SIZE + 15 if jump_boost_visible else base_x,
        # 新增：生命值恢复冷却图标位置
        "health_regen_x": base_x + (JUMP_BOOST_ICON_CONTAINER_SIZE + 15 if jump_boost_visible else 0) +
                          (EXTRA_HEALTH_ICON_CONTAINER_SIZE + 15 if extra_health_visible else 0)
    }

    # 如果先显示跳跃，后显示额外血量：跳跃在移动速度右侧，额外血量在跳跃右侧
    if jump_boost_visible and extra_health_visible:
        pos["extra_health_x"] = pos["jump_boost_x"] + JUMP_BOOST_ICON_CONTAINER_SIZE + 15
    # 如果只有额外血量：额外血量在移动速度右侧
    elif extra_health_visible and not jump_boost_visible:
        pos["extra_health_x"] = base_x
    # 如果只有跳跃：跳跃在移动速度右侧
    elif jump_boost_visible and not extra_health_visible:
        pos["jump_boost_x"] = base_x

    # 新增：生命值恢复冷却图标位置优先级（在跳跃/额外血量之后）
    if health_regen_visible:
        # 计算前面有多少个图标，从而确定health_regen的位置
        icons_before = 0
        if jump_boost_visible:
            icons_before += 1
        if extra_health_visible:
            icons_before += 1
        
        # health_regen_x = base_x + 前面所有图标的宽度 + 间距
        pos["health_regen_x"] = base_x + icons_before * (CONTAINER_SIZE + 15)

    # 新增：张狂图标位置（在额外血量/生命值恢复冷却之后）
    frenzy_visible = dino.frenzy_active
    if frenzy_visible:
        # 计算前面有多少个图标，从而确定frenzy的位置
        icons_before = 0
        if jump_boost_visible:
            icons_before += 1
        if extra_health_visible:
            icons_before += 1
        if health_regen_visible:
            icons_before += 1
        
        # frenzy_x = base_x + 前面所有图标的宽度 + 间距
        pos["frenzy_x"] = base_x + icons_before * (CONTAINER_SIZE + 15)

    return pos

def draw_jump_boost_icon(dino, score):
    """绘制技能3跳跃状态图标（仅激活时显示，支持图片/矩形图标）"""
    # 仅在技能3激活且有FPS提升时绘制
    if not dino.skill3_active or dino.skill3_fps_boost <= 0:
        return

    # 获取图标位置
    pos = get_jump_boost_icon_pos(dino, score)
    icon_x = pos["jump_boost_x"]
    icon_y = JUMP_BOOST_ICON_Y_POS
    container_rect = (icon_x, icon_y, JUMP_BOOST_ICON_CONTAINER_SIZE, JUMP_BOOST_ICON_CONTAINER_SIZE)

    # 计算持续时间进度（用于遮罩）
    total_duration = SKILL3_DURATION / 1000  # 总持续时间（秒）
    progress = dino.skill3_boost_remaining / total_duration if total_duration > 0 else 0
    is_easy_mode = get_current_difficulty(score) == 1

    # 绘制容器
    draw_rect(screen, JUMP_BOOST_ACTIVE_COLOR, container_rect, shadow=True)

    # 绘制图标主体（优先图片，兜底矩形）
    icon_center_x = icon_x + JUMP_BOOST_ICON_CONTAINER_SIZE // 2
    icon_center_y = icon_y + JUMP_BOOST_ICON_CONTAINER_SIZE // 2

    # 新增：支持图片图标
    if game_resources.get("jump_boost_icon", "rect") != "rect":
        # 绘制图片图标
        icon_surface = pygame.transform.scale(game_resources["jump_boost_icon"], (ICON_SIZE, ICON_SIZE))
        screen.blit(icon_surface, (icon_center_x - ICON_SIZE // 2, icon_center_y - ICON_SIZE // 2))
    else:
        # 纯菱形兜底（保留原有跳跃箭头）
        draw_diamond(screen, WHITE, icon_center_x, icon_center_y, 15)
        pygame.draw.polygon(screen, JUMP_BOOST_ACTIVE_COLOR, [
            (icon_center_x, icon_center_y - 10),
            (icon_center_x - 8, icon_center_y),
            (icon_center_x + 8, icon_center_y)
        ])

    # 绘制剩余时间文字（下半部分）
    #time_text = f"{dino.skill3_boost_remaining}s"
    #time_text_y = icon_center_y + 10
    #draw_icon_text(screen, time_text, icon_center_x, time_text_y)

    # 绘制持续时间遮罩
    if progress > 0:
        draw_mask(screen, container_rect, progress, is_easy_mode)

        # 绘制提升百分比文字（上半部分）
    boost_text_y = icon_center_y
    draw_icon_text(screen, dino.skill3_boost_text, icon_center_x, boost_text_y)

    current_difficulty = get_current_difficulty(score)
    if current_difficulty >= 3:  # 难度>1（一阶及以上）即有CD提升
        draw_boost_icon(screen, container_rect)

def draw_health_regen_icon(dino, score):
    """绘制生命值恢复冷却图标（使用自定义图标+新遮罩样式）"""
    # 仅在冷却期显示
    if not dino.regen_cooldown:
        return

    # 获取图标位置
    pos = get_jump_boost_icon_pos(dino, score)
    icon_x = pos["health_regen_x"]
    icon_y = HEALTH_REGEN_ICON_Y_POS
    container_rect = (icon_x, icon_y, HEALTH_REGEN_ICON_CONTAINER_SIZE, HEALTH_REGEN_ICON_CONTAINER_SIZE)

    # 计算冷却进度
    current_time = pygame.time.get_ticks()
    remaining_ms = max(0, dino.regen_cooldown_end - current_time)
    total_duration = HEALTH_REGEN_COOLDOWN / 1000
    progress = remaining_ms / HEALTH_REGEN_COOLDOWN if HEALTH_REGEN_COOLDOWN > 0 else 0
    is_easy_mode = get_current_difficulty(score) == 1

    # 绘制容器
    draw_rect(screen, HEALTH_REGEN_ACTIVE_COLOR, container_rect, shadow=True)

    # 绘制自定义图标
    icon_center_x = icon_x + HEALTH_REGEN_ICON_CONTAINER_SIZE // 2
    icon_center_y = icon_y + HEALTH_REGEN_ICON_CONTAINER_SIZE // 2

    # 使用自定义的health_regen_icon
    if game_resources.get("health_regen_icon", "rect") != "rect":
        icon_surface = pygame.transform.scale(game_resources["health_regen_icon"], (HEALTH_REGEN_ICON_SIZE, HEALTH_REGEN_ICON_SIZE))
        screen.blit(icon_surface, (icon_center_x - HEALTH_REGEN_ICON_SIZE // 2, icon_center_y - HEALTH_REGEN_ICON_SIZE // 2))
    else:
        # 兜底样式（自定义）
        draw_diamond(screen, WHITE, icon_center_x, icon_center_y, 15)
        # 绘制回血图标（心形）
        pygame.draw.polygon(screen, HEALTH_REGEN_ACTIVE_COLOR, [
            (icon_center_x, icon_center_y - 8),
            (icon_center_x - 8, icon_center_y),
            (icon_center_x, icon_center_y + 8),
            (icon_center_x + 8, icon_center_y)
        ])
 
    # 使用新的遮罩样式
    if progress > 0:
        draw_mask(screen, container_rect, progress, is_easy_mode)

    # 绘制剩余冷却时间文字
    remaining_seconds = int(remaining_ms / 1000)
    draw_icon_text(screen, f"{remaining_seconds}", icon_center_x, icon_center_y)

def draw_speed_icon(current_speed, score, dino):
    """绘制移动速度图标（移到难度图标右侧10px）"""
    # 核心修改：替换原有icon_x为新定义的常量
    icon_x = SPEED_ICON_X_POS  # 难度图标右侧10px
    icon_y = SPEED_ICON_Y_POS  # 顶部对齐
    container_rect = (icon_x, icon_y, SPEED_ICON_CONTAINER_SIZE, SPEED_ICON_CONTAINER_SIZE)

    # 以下逻辑完全保留（仅移除遮罩的原有逻辑已保留）
    current_stage = 1
    next_stage_score = SCORE_STAGE_2
    current_stage_score = SCORE_STAGE_1
    is_easy_mode = True

    if score >= SCORE_STAGE_2 and score < SCORE_STAGE_3:
        current_stage = 2
        next_stage_score = SCORE_STAGE_3
        current_stage_score = SCORE_STAGE_2
        is_easy_mode = False
    elif score >= SCORE_STAGE_3 and score < SCORE_STAGE_4:
        current_stage = 3
        next_stage_score = SCORE_STAGE_4
        current_stage_score = SCORE_STAGE_3
        is_easy_mode = False
    elif score >= SCORE_STAGE_4:
        current_stage = 4
        next_stage_score = SCORE_STAGE_5
        current_stage_score = SCORE_STAGE_4
        is_easy_mode = False

    container_color = SPEED_ICON_EASY if is_easy_mode else SPEED_ICON_HARD
    draw_rect(screen, container_color, container_rect, shadow=True)

    # 绘制速度图标（图片/菱形）
    icon_center_x = icon_x + SPEED_ICON_CONTAINER_SIZE // 2
    icon_center_y = icon_y + SPEED_ICON_CONTAINER_SIZE // 2
    if game_resources["speed_icon"] == "rect":
        draw_diamond(screen, WHITE, icon_center_x, icon_center_y, 15)
    else:
        icon_surface = pygame.transform.scale(game_resources["speed_icon"], (ICON_SIZE, ICON_SIZE))
        screen.blit(icon_surface, (icon_center_x - ICON_SIZE // 2, icon_center_y - ICON_SIZE // 2))

    # 绘制速度文字（原有逻辑不变）
    draw_icon_text(screen, f"{int(current_speed)}%", icon_center_x, icon_center_y)

    current_difficulty = get_current_difficulty(score)
    if current_difficulty >1 :  # 难度>1（一阶及以上）即有CD提升
        draw_boost_icon(screen, container_rect)

    if dino.compensation_speed_bonus > 0:
        draw_compensation_icon(screen, container_rect)


def draw_health_icon(dino):
    # 图标位置（分数面板右侧10px，顶部与其他图标一致）
    icon_x = HEALTH_ICON_X_POS
    icon_y = HEALTH_ICON_Y_POS
    container_rect = (icon_x, icon_y, HEALTH_ICON_CONTAINER_SIZE, HEALTH_ICON_CONTAINER_SIZE)

    # 1. 确定容器颜色和使用的图标
    HEALTH_LOW_THRESHOLD = 1.0  # 50%血量阈值
    if dino.health > HEALTH_LOW_THRESHOLD:
        container_color = HEALTH_ICON_COLOR  # 正常血量容器色（亮蓝）
        use_icon = game_resources["health_icon"]  # 正常血量图标
        default_icon_color = (255, 255, 255)  # 无图片时白色矩形
    else:
        container_color = HEALTH_ICON_LOW_COLOR  # 低血量容器色（番茄红）
        use_icon = game_resources["low_health_icon"]  # 低血量图标
        default_icon_color = (255, 100, 100)  # 无图片时浅红矩形（便于区分）

    # 2. 绘制容器（带边框，与速度图标样式统一）
    draw_rect(screen, container_color, container_rect, shadow=True)

    # 3. 绘制图标（位于遮罩下方，根据血量切换）
    icon_center_x = icon_x + HEALTH_ICON_CONTAINER_SIZE // 2
    icon_center_y = icon_y + HEALTH_ICON_CONTAINER_SIZE // 2

    if use_icon == "rect":
        # 无图片时绘制纯色菱形（区分正常/低血量）
        draw_diamond(screen, default_icon_color, icon_center_x, icon_center_y, 15)
    else:
        # 有图片时绘制对应图标（正常/低血量）
        icon_surface = pygame.transform.scale(use_icon, (HEALTH_ICON_SIZE, HEALTH_ICON_SIZE))
        screen.blit(icon_surface, (icon_center_x - HEALTH_ICON_SIZE // 2, icon_center_y - HEALTH_ICON_SIZE // 2))

    # 4. 绘制遮罩（在图标上方，体现血量进度）
    health_progress = dino.health / INITIAL_HEALTH if dino.health > 0 else 0
    mask_progress = 1.0 - health_progress
    is_easy_mode = dino.health > HEALTH_LOW_THRESHOLD  # 低血量时遮罩透明度更高
    draw_mask(screen, container_rect, mask_progress, is_easy_mode)

    # 5. 绘制血量文字（百分比，与速度图标文字样式统一）
    # health_text = f"{int(dino.health * 100)}%"
    # draw_icon_text(screen, health_text, icon_center_x, icon_center_y)

    # 修改：仅在冷却期显示代偿图标


def draw_fps_boost_icon(dino):
    """绘制FPS提升图标（常驻显示，与速度图标样式相同）"""
    # 计算总FPS提升百分比（阶段提升 + 技能3提升）
    total_fps_boost = dino.stage_fps_boost + dino.skill3_fps_boost
    
    icon_x = FPS_BOOST_ICON_X_POS
    icon_y = FPS_BOOST_ICON_Y_POS
    container_rect = (icon_x, icon_y, FPS_BOOST_ICON_CONTAINER_SIZE, FPS_BOOST_ICON_CONTAINER_SIZE)
    
    # 绘制容器（与速度图标样式统一）
    draw_rect(screen, FPS_BOOST_ICON_COLOR, container_rect, shadow=True)
    
    # 绘制图标主体
    icon_center_x = icon_x + FPS_BOOST_ICON_CONTAINER_SIZE // 2
    icon_center_y = icon_y + FPS_BOOST_ICON_CONTAINER_SIZE // 2
    
    # 绘制图标（优先图片，兜底菱形）
    if game_resources.get("fps_boost_icon", "rect") != "rect":
        # 绘制图片图标
        icon_surface = pygame.transform.scale(game_resources["fps_boost_icon"], (ICON_SIZE, ICON_SIZE))
        screen.blit(icon_surface, (icon_center_x - ICON_SIZE // 2, icon_center_y - ICON_SIZE // 2))
    else:
        # 兜底样式（菱形）
        draw_diamond(screen, WHITE, icon_center_x, icon_center_y, 15)
    
    # 绘制FPS提升百分比文字（始终显示，即使没有提升也显示0%）
    boost_percent = int(total_fps_boost * 100)
    draw_icon_text(screen, f"{boost_percent}%", icon_center_x, icon_center_y)
    
    # 在右下角绘制提升图标（UP）- 只有有FPS提升时才显示
    if total_fps_boost > 0:
        draw_boost_icon(screen, container_rect)

def draw_frenzy_icon(dino, score):
    """绘制张狂图标（仅在张狂激活时显示）"""
    if not dino.frenzy_active:
        return
    
    # 计算动态位置
    pos = get_jump_boost_icon_pos(dino, score)
    icon_x = pos["frenzy_x"]
    icon_y = FRENZY_ICON_Y_POS
    container_rect = (icon_x, icon_y, FRENZY_ICON_CONTAINER_SIZE, FRENZY_ICON_CONTAINER_SIZE)
    
    # 绘制容器（金色）
    draw_rect(screen, FRENZY_ICON_COLOR, container_rect, shadow=True)
    
    # 绘制图标主体
    icon_center_x = icon_x + FRENZY_ICON_CONTAINER_SIZE // 2
    icon_center_y = icon_y + FRENZY_ICON_CONTAINER_SIZE // 2
    
    # 绘制图标（优先图片，兜底菱形）
    if game_resources.get("frenzy_icon", "rect") != "rect":
        # 绘制图片图标
        icon_surface = pygame.transform.scale(game_resources["frenzy_icon"], (ICON_SIZE, ICON_SIZE))
        screen.blit(icon_surface, (icon_center_x - ICON_SIZE // 2, icon_center_y - ICON_SIZE // 2))
    else:
        # 兜底样式（菱形）
        draw_diamond(screen, WHITE, icon_center_x, icon_center_y, 15)
        
        # 绘制文字"F"
        frenzy_font = load_custom_font(20, bold=True)
        frenzy_text = frenzy_font.render("F", True, FRENZY_ICON_COLOR)
        text_x = icon_center_x - frenzy_text.get_width() // 2
        text_y = icon_center_y - frenzy_text.get_height() // 2
        screen.blit(frenzy_text, (text_x, text_y))
    
    # 绘制时间遮罩（显示剩余延迟时间）
    current_time = pygame.time.get_ticks()
    frenzy_elapsed = current_time - dino.frenzy_start_time
    frenzy_remaining = max(0, dino.frenzy_delay - frenzy_elapsed)
    mask_progress = frenzy_remaining / dino.frenzy_delay if dino.frenzy_delay > 0 else 0  # 1.0 = 满时间，0.0 = 时间结束
    draw_mask(screen, container_rect, mask_progress, is_easy_mode=False)


def draw_agility_icon(dino, score):
    """绘制矫健图标（仅在矫健激活时显示）"""
    if not dino.agility_active:
        return
    
    # 计算位置
    icon_x = AGILITY_ICON_X_POS
    icon_y = AGILITY_ICON_Y_POS
    container_rect = (icon_x, icon_y, AGILITY_ICON_CONTAINER_SIZE, AGILITY_ICON_CONTAINER_SIZE)
    
    # 绘制容器（绿色，带品质边框）
    # 获取品质颜色
    unlocked_skills = load_unlocked_skills()
    if "Agility" in unlocked_skills and len(unlocked_skills["Agility"]) > 0:
        # 获取第一个品质
        first_rarity = list(unlocked_skills["Agility"].keys())[0]
        border_color = ITEM_RARITY["agility"][first_rarity]["color"]
    else:
        border_color = AGILITY_ICON_COLOR
    
    draw_rect(screen, AGILITY_ICON_COLOR, container_rect, shadow=True)
    # 绘制品质边框
    pygame.draw.rect(screen, border_color, container_rect, 3, border_radius=5)
    
    # 绘制图标主体
    icon_center_x = icon_x + AGILITY_ICON_CONTAINER_SIZE // 2
    icon_center_y = icon_y + AGILITY_ICON_CONTAINER_SIZE // 2
    
    # 绘制文字"A"
    agility_font = load_custom_font(20, bold=True)
    agility_text = agility_font.render("A", True, WHITE)
    text_x = icon_center_x - agility_text.get_width() // 2
    text_y = icon_center_y - agility_text.get_height() // 2
    screen.blit(agility_text, (text_x, text_y))
    
    # 绘制FPS提升百分比
    boost_font = load_custom_font(10)
    boost_percent = int(dino.agility_fps_boost * 100)
    boost_text = boost_font.render(f"+{boost_percent}%", True, WHITE)
    boost_x = icon_center_x - boost_text.get_width() // 2
    boost_y = icon_y + AGILITY_ICON_CONTAINER_SIZE - 12
    screen.blit(boost_text, (boost_x, boost_y))


def get_current_difficulty(score):
    """根据分数获取当前难度等级（1-4）"""
    if score < SCORE_STAGE_2:
        return 1  # 简单（零阶）
    elif score < SCORE_STAGE_3:
        return 2  # 下难（一阶）
    elif score < SCORE_STAGE_4:
        return 3  # 中难（二阶）
    else:
        return 4  # 上难（三阶）

def get_difficulty_name(score):
    """根据分数获取难度名称"""
    difficulty = get_current_difficulty(score)
    difficulty_names = {
        1: "Easy",
        2: "Normal",
        3: "Hard",
        4: "Extreme"
    }
    return difficulty_names.get(difficulty, "Unknown")

def draw_difficulty_icon(score):
    """绘制难度进度图标（与速度图标样式统一，带遮罩）"""
    # 1. 确定当前难度等级和进度
    if score < SCORE_STAGE_2:
        current_difficulty = 1  # 简单
        next_stage_score = SCORE_STAGE_2
        current_stage_score = SCORE_STAGE_1
    elif score < SCORE_STAGE_3:
        current_difficulty = 2  # 下难
        next_stage_score = SCORE_STAGE_3
        current_stage_score = SCORE_STAGE_2
    elif score < SCORE_STAGE_4:
        current_difficulty = 3  # 中难
        next_stage_score = SCORE_STAGE_4
        current_stage_score = SCORE_STAGE_3
    else:
        current_difficulty = 4  # 上难
        next_stage_score = SCORE_STAGE_5
        current_stage_score = SCORE_STAGE_4

    # 2. 计算难度进度（当前分数到下一难度的百分比）
    if current_difficulty < 4:
        stage_range = next_stage_score - current_stage_score
        current_progress = score - current_stage_score
        difficulty_progress = min(1.0, max(0.0, current_progress / stage_range))
    else:
        difficulty_progress = 1.0  # 上难进度满

    # 3. 图标位置和容器样式
    icon_x = DIFFICULTY_ICON_X_POS
    icon_y = DIFFICULTY_ICON_Y_POS
    container_rect = (icon_x, icon_y, DIFFICULTY_ICON_CONTAINER_SIZE, DIFFICULTY_ICON_CONTAINER_SIZE)
    container_color = DIFFICULTY_ICON_COLORS[current_difficulty]  # 按难度切换容器色

    # 4. 绘制容器（带阴影，与速度图标样式统一）
    draw_rect(screen, container_color, container_rect, shadow=True)

    # 5. 绘制难度图标（图片优先，无图片则矩形，位于遮罩下方）
    icon_center_x = icon_x + DIFFICULTY_ICON_CONTAINER_SIZE // 2
    icon_center_y = icon_y + DIFFICULTY_ICON_CONTAINER_SIZE // 2

    if game_resources["difficulty_icon"] == "rect":
        # 无图片时绘制实心菱形（与速度图标一致）
        draw_diamond(screen, WHITE, icon_center_x, icon_center_y, 15)
    else:
        # 有图片时绘制难度图标图片
        icon_surface = pygame.transform.scale(game_resources["difficulty_icon"], (DIFFICULTY_ICON_SIZE, DIFFICULTY_ICON_SIZE))
        screen.blit(icon_surface, (icon_center_x - DIFFICULTY_ICON_SIZE // 2, icon_center_y - DIFFICULTY_ICON_SIZE // 2))

    # 6. 绘制遮罩（在图标上方，体现到下一难度的进度）
    mask_progress = 1.0 - difficulty_progress  # 进度越高，遮罩越少
    is_easy_mode = current_difficulty == 1  # 简单难度遮罩透明度略低
    draw_mask(screen, container_rect, mask_progress, is_easy_mode)

    # 7. 绘制难度文字（显示1/2/3/4，与速度图标文字样式统一）
    #difficulty_text = DIFFICULTY_TEXT_MAP[current_difficulty]
    #draw_icon_text(screen, difficulty_text, icon_center_x, icon_center_y)

    current_difficulty = get_current_difficulty(score)
    if current_difficulty <= 3:  # 难度>1（一阶及以上）即有CD提升
        draw_boost_icon(screen, container_rect)

# 绘制技能1图标函数（LAST EFFORT）
def get_skill_rarity_color(skill_name):
    """获取技能的稀有度颜色"""
    unlocked_skills = load_unlocked_skills()
    if skill_name in unlocked_skills and len(unlocked_skills[skill_name]) > 0:
        # 所有技能和天赋都使用嵌套字典结构
        first_rarity = list(unlocked_skills[skill_name].keys())[0]
        if skill_name in ["Brave Dash", "Zoom Boost", "Lucky Leap"]:
            color = SKILL_RARITY[first_rarity]["color"]
        elif skill_name == "Frenzy":
            color = ITEM_RARITY["frenzy"][first_rarity]["color"]
        elif skill_name == "Agility":
            color = ITEM_RARITY["agility"][first_rarity]["color"]
        else:
            color = None
        if color:
            return color
    return None

def get_skill_uses_left(skill_name):
    """获取技能剩余使用次数"""
    unlocked_skills = load_unlocked_skills()
    if skill_name in unlocked_skills and len(unlocked_skills[skill_name]) > 0:
        # 所有技能和天赋都使用嵌套字典结构
        # 返回第一个品质的使用次数
        first_rarity = list(unlocked_skills[skill_name].keys())[0]
        return unlocked_skills[skill_name][first_rarity]["uses_left"]
    return 0

def draw_skill1_icon(dino, score, carried_skills):
    """绘制技能1图标（含锁定/解锁逻辑和使用次数）"""
    # 技能1图标位置（第四个图标）
    icon_x = ICONS_START_X + 3 * (CONTAINER_SIZE + ICON_SPACING)
    icon_y = ICON_Y_POS
    container_rect = (icon_x, icon_y, CONTAINER_SIZE, CONTAINER_SIZE)

    current_time = pygame.time.get_ticks()
    cd_remaining = max(0, dino.skill1_cd_end - current_time)

    # ========== 新增：判断技能1是否解锁 ==========
    unlocked_skills = load_unlocked_skills()
    is_skill1_unlocked = "Brave Dash" in unlocked_skills and "Brave Dash" in carried_skills and score >= SKILL1_UNLOCK_SCORE
    
    # 获取技能稀有度颜色和使用次数
    rarity_color = get_skill_rarity_color("Brave Dash") if is_skill1_unlocked else None
    uses_left = get_skill_uses_left("Brave Dash") if is_skill1_unlocked else 0
    is_exhausted = uses_left == 0 and rarity_color is not None

    # ========== 核心：技能升级闪烁逻辑 ==========
    is_upgrade_flashing = current_time < dino.skill1_upgrade_flash_end
    if is_upgrade_flashing:
        # 闪烁时交替显示金黄色和原颜色（100ms间隔）
        if int(current_time / SKILL_FLASH_INTERVAL) % 2 == 0:
            container_color = SKILL_UPGRADE_FLASH_COLOR  # 升级闪烁黄色
        else:
            # 原有颜色逻辑（仅解锁后生效）
            if not is_skill1_unlocked:
                container_color = LOCKED_ICON_COLOR  # 锁定状态容器色
            elif is_exhausted:
                container_color = LOCKED_ICON_COLOR  # 使用次数耗尽显示锁定色
            elif dino.skill1_active:
                container_color = SKILL1_ACTIVE_COLOR
            elif dino.skill1_cooldown:
                container_color = SKILL1_COOLDOWN_COLOR
            else:
                container_color = SKILL1_READY_COLOR
    else:
        # 非闪烁状态：原有颜色逻辑 + 锁定状态
        if not is_skill1_unlocked:
            container_color = LOCKED_ICON_COLOR  # 锁定状态容器色
        elif is_exhausted:
            container_color = LOCKED_ICON_COLOR  # 使用次数耗尽显示锁定色
        elif score <= SCORE_STAGE_2:  # 简单难度（≤1000分）禁用，显示禁用色
            container_color = SKILL1_DISABLE_COLOR
        elif dino.skill1_active:
            container_color = SKILL1_ACTIVE_COLOR
        elif dino.skill1_cooldown:
            container_color = SKILL1_COOLDOWN_COLOR
        else:
            container_color = SKILL1_READY_COLOR

    # 判断是否为简单模式（用于统一遮罩透明度）
    is_easy_mode = score <= SCORE_STAGE_2

    # 纯矩形容器（带阴影，与速度图标样式一致）
    # 如果有稀有度颜色，将品质颜色应用到最外层边框
    border_color = rarity_color if (rarity_color and is_skill1_unlocked and not is_exhausted) else None
    draw_rect(screen, container_color, container_rect, shadow=True, border_color=border_color)

    # 绘制图标主体（新增：解锁显示原图标，锁定显示锁定图标）
    icon_center_x = icon_x + CONTAINER_SIZE // 2
    icon_center_y = icon_y + CONTAINER_SIZE // 2

    if not is_skill1_unlocked or is_exhausted:
        # 锁定状态：绘制锁定图标/文字
        if game_resources["locked_icon"] == "rect":
            # 无锁定图片时绘制锁形文字
            draw_icon_text(screen, LOCKED_TEXT, icon_center_x, icon_center_y)
        else:
            # 有锁定图片时绘制锁定图标
            locked_surface = pygame.transform.scale(game_resources["locked_icon"], (ICON_SIZE, ICON_SIZE))
            screen.blit(locked_surface, (icon_center_x - ICON_SIZE // 2, icon_center_y - ICON_SIZE // 2))
    else:
        # 解锁状态：绘制原技能图标
        if game_resources["skill1_icon"] == "rect":
            # 纯菱形技能图标（实心菱形，与速度图标一致）
            draw_diamond(screen, WHITE, icon_center_x, icon_center_y, 15)
        else:
            # 缩放图标到容器中心（保持尺寸一致）
            icon_surface = pygame.transform.scale(game_resources["skill1_icon"], (ICON_SIZE, ICON_SIZE))
            screen.blit(icon_surface, (icon_center_x - ICON_SIZE // 2, icon_center_y - ICON_SIZE // 2))

    # 锁定状态不绘制冷却遮罩和CD文字
    if is_skill1_unlocked and not is_exhausted:
        # 绘制冷却进度遮罩（统一样式）
        if dino.skill1_cooldown and dino.skill1_progress > 0:
            draw_mask(screen, container_rect, dino.skill1_progress, is_easy_mode)

            # 冷却时间文本（统一样式）
            cd_seconds = int(cd_remaining / 1000)
            draw_icon_text(screen, f"{cd_seconds}", icon_center_x, icon_center_y)

        # 绘制剩余使用次数（如果不是无限次）
        if uses_left > 0:
            uses_text = str(uses_left)
            uses_font = load_custom_font(14)
            # 计算文字宽度，紧贴右侧但不超出图标框
            text_width = uses_font.size(uses_text)[0]
            text_x = icon_x + CONTAINER_SIZE - text_width - 4  # 距离右边框4像素
            text_y = icon_y + CONTAINER_SIZE - 18  # 距离底部18像素
            # 在图标右下角显示剩余次数，带黑色描边
            draw_text_with_outline(screen, uses_text, uses_font,
                                   text_x, text_y,
                                   WHITE, BLACK, 2)

        current_difficulty = get_current_difficulty(score)
        if current_difficulty >= 3:  # 难度>1（一阶及以上）即有CD提升
            draw_boost_icon(screen, container_rect)


def draw_skill2_icon(dino, score, carried_skills):
    """绘制技能2图标（含锁定/解锁逻辑和使用次数）"""
    # 技能2图标位置（第三个图标）
    icon_x = ICONS_START_X + 2 * (CONTAINER_SIZE + ICON_SPACING)
    icon_y = ICON_Y_POS
    container_rect = (icon_x, icon_y, CONTAINER_SIZE, CONTAINER_SIZE)

    current_time = pygame.time.get_ticks()
    cd_remaining = max(0, dino.skill2_cd_end - current_time)

    # ========== 新增：判断技能2是否解锁 ==========
    unlocked_skills = load_unlocked_skills()
    is_skill2_unlocked = score >= SKILL2_UNLOCK_SCORE and "Zoom Boost" in unlocked_skills and "Zoom Boost" in carried_skills

    # 获取技能稀有度颜色和使用次数
    rarity_color = get_skill_rarity_color("Zoom Boost") if is_skill2_unlocked else None
    uses_left = get_skill_uses_left("Zoom Boost") if is_skill2_unlocked else 0
    is_exhausted = uses_left == 0 and rarity_color is not None

    # ========== 核心：技能升级闪烁逻辑 ==========
    is_upgrade_flashing = current_time < dino.skill2_upgrade_flash_end
    if is_upgrade_flashing:
        # 闪烁时交替显示金黄色和原颜色（100ms间隔）
        if int(current_time / SKILL_FLASH_INTERVAL) % 2 == 0:
            container_color = SKILL_UPGRADE_FLASH_COLOR  # 升级闪烁黄色
        else:
            # 原有颜色逻辑（仅解锁后生效）
            if not is_skill2_unlocked:
                container_color = LOCKED_ICON_COLOR  # 锁定状态容器色
            elif is_exhausted:
                container_color = LOCKED_ICON_COLOR  # 使用次数耗尽显示锁定色
            elif dino.skill2_cooldown:
                container_color = SKILL2_COOLDOWN_COLOR
            elif dino.extra_health > 0:  # CD结束但有额外血条时显示禁用色
                container_color = SKILL2_DISABLE_COLOR
            else:  # CD结束且无额外血条时显示就绪色
                container_color = SKILL2_READY_COLOR
    else:
        # 非闪烁状态：原有颜色逻辑 + 锁定状态
        if not is_skill2_unlocked:
            container_color = LOCKED_ICON_COLOR  # 锁定状态容器色
        elif is_exhausted:
            container_color = LOCKED_ICON_COLOR  # 使用次数耗尽显示锁定色
        elif score <= SCORE_STAGE_2:  # 简单难度（≤10分）禁用，显示禁用色
            container_color = SKILL2_DISABLE_COLOR
        elif dino.skill2_cooldown:
            container_color = SKILL2_COOLDOWN_COLOR
        elif dino.extra_health > 0:  # CD结束但有额外血条时显示禁用色
            container_color = SKILL2_DISABLE_COLOR
        else:  # CD结束且无额外血条时显示就绪色
            container_color = SKILL2_READY_COLOR

    # 判断是否为简单模式（用于统一遮罩透明度）
    is_easy_mode = score <= SCORE_STAGE_2

    # 纯矩形容器（带阴影，与速度图标样式一致）
    # 如果有稀有度颜色，将品质颜色应用到最外层边框
    border_color = rarity_color if (rarity_color and is_skill2_unlocked and not is_exhausted) else None
    draw_rect(screen, container_color, container_rect, shadow=True, border_color=border_color)

    # 绘制图标主体（新增：解锁显示原图标，锁定显示锁定图标）
    icon_center_x = icon_x + CONTAINER_SIZE // 2
    icon_center_y = icon_y + CONTAINER_SIZE // 2

    if not is_skill2_unlocked or is_exhausted:
        # 锁定状态：绘制锁定图标/文字
        if game_resources["locked_icon"] == "rect":
            draw_icon_text(screen, LOCKED_TEXT, icon_center_x, icon_center_y)
        else:
            locked_surface = pygame.transform.scale(game_resources["locked_icon"], (ICON_SIZE, ICON_SIZE))
            screen.blit(locked_surface, (icon_center_x - ICON_SIZE // 2, icon_center_y - ICON_SIZE // 2))
    else:
        # 解锁状态：绘制原技能图标
        if game_resources["skill2_icon"] == "rect":
            # 纯菱形技能图标（实心菱形，绿色十字）
            draw_diamond(screen, WHITE, icon_center_x, icon_center_y, 15)
            # 绘制十字标志
            pygame.draw.line(screen, SKILL2_ACTIVE_COLOR,
                             (icon_center_x - 8, icon_center_y),
                             (icon_center_x + 8, icon_center_y), 3)
            pygame.draw.line(screen, SKILL2_ACTIVE_COLOR,
                             (icon_center_x, icon_center_y - 8),
                             (icon_center_x, icon_center_y + 8), 3)
        else:
            # 缩放图标到容器中心（保持尺寸一致）
            icon_surface = pygame.transform.scale(game_resources["skill2_icon"], (ICON_SIZE, ICON_SIZE))
            screen.blit(icon_surface, (icon_center_x - ICON_SIZE // 2, icon_center_y - ICON_SIZE // 2))

    # 锁定状态不绘制冷却遮罩和CD文字
    if is_skill2_unlocked and not is_exhausted:
        # 绘制冷却进度遮罩（统一样式）
        if dino.skill2_cooldown and dino.skill2_progress > 0:
            draw_mask(screen, container_rect, dino.skill2_progress, is_easy_mode)

            # 冷却时间文本（统一样式）
            cd_seconds = int(cd_remaining / 1000)
            draw_icon_text(screen, f"{cd_seconds}", icon_center_x, icon_center_y)

        # 绘制剩余使用次数（如果不是无限次）
        if uses_left > 0:
            uses_text = str(uses_left)
            uses_font = load_custom_font(14)
            # 计算文字宽度，紧贴右侧但不超出图标框
            text_width = uses_font.size(uses_text)[0]
            text_x = icon_x + CONTAINER_SIZE - text_width - 4  # 距离右边框4像素
            text_y = icon_y + CONTAINER_SIZE - 18  # 距离底部18像素
            # 在图标右下角显示剩余次数，带黑色描边
            draw_text_with_outline(screen, uses_text, uses_font,
                                   text_x, text_y,
                                   WHITE, BLACK, 2)

        # 同步修改提升图标显示条件（可选：和skill1统一为二阶及以上）
        current_difficulty = get_current_difficulty(score)
        if current_difficulty >= 3:  # 若需和skill1一致，改为二阶及以上显示提升图标
            draw_boost_icon(screen, container_rect)


def draw_skill3_icon(dino, score, carried_skills):
    """绘制技能3图标（含锁定/解锁逻辑和使用次数）"""
    # 技能3图标位置（第五个图标）
    icon_x = ICONS_START_X + 4 * (CONTAINER_SIZE + ICON_SPACING)
    icon_y = ICON_Y_POS
    container_rect = (icon_x, icon_y, CONTAINER_SIZE, CONTAINER_SIZE)

    current_time = pygame.time.get_ticks()
    cd_remaining = max(0, dino.skill3_cd_end - current_time)

    # ========== 新增：判断技能3是否解锁 ==========
    unlocked_skills = load_unlocked_skills()
    is_skill3_unlocked = score >= SKILL3_UNLOCK_SCORE and "Lucky Leap" in unlocked_skills and "Lucky Leap" in carried_skills

    # 获取技能稀有度颜色和使用次数
    rarity_color = get_skill_rarity_color("Lucky Leap") if is_skill3_unlocked else None
    uses_left = get_skill_uses_left("Lucky Leap") if is_skill3_unlocked else 0
    is_exhausted = uses_left == 0 and rarity_color is not None

    # 技能升级闪烁逻辑
    is_upgrade_flashing = current_time < dino.skill3_upgrade_flash_end
    if is_upgrade_flashing:
        # 闪烁时交替显示金黄色和原颜色（100ms间隔）
        if int(current_time / SKILL_FLASH_INTERVAL) % 2 == 0:
            container_color = SKILL_UPGRADE_FLASH_COLOR  # 升级闪烁黄色
        else:
            # 原有颜色逻辑 + 锁定状态
            if not is_skill3_unlocked:
                container_color = LOCKED_ICON_COLOR  # 锁定状态容器色
            elif is_exhausted:
                container_color = LOCKED_ICON_COLOR  # 使用次数耗尽显示锁定色
            elif dino.skill3_cooldown:
                container_color = SKILL3_COOLDOWN_COLOR
            else:  # CD结束且无额外血条时显示就绪色
                container_color = SKILL3_READY_COLOR
    else:
        # 非闪烁状态：原有颜色逻辑 + 锁定状态
        if not is_skill3_unlocked:
            container_color = LOCKED_ICON_COLOR  # 锁定状态容器色
        elif is_exhausted:
            container_color = LOCKED_ICON_COLOR  # 使用次数耗尽显示锁定色
        elif score <= SCORE_STAGE_2:  # 简单难度（≤10分）禁用，显示禁用色
            container_color = SKILL3_DISABLE_COLOR
        elif dino.skill3_cooldown:
            container_color = SKILL3_COOLDOWN_COLOR
        else:  # CD结束且无额外血条时显示就绪色
            container_color = SKILL3_READY_COLOR

    # 判断是否为简单模式
    is_easy_mode = get_current_difficulty(score) == 2

    # 绘制容器
    # 如果有稀有度颜色，将品质颜色应用到最外层边框
    border_color = rarity_color if (rarity_color and is_skill3_unlocked and not is_exhausted) else None
    draw_rect(screen, container_color, container_rect, shadow=True, border_color=border_color)

    # 绘制图标主体（新增：解锁显示原图标，锁定显示锁定图标）
    icon_center_x = icon_x + CONTAINER_SIZE // 2
    icon_center_y = icon_y + CONTAINER_SIZE // 2

    if not is_skill3_unlocked or is_exhausted:
        # 锁定状态：绘制锁定图标/文字
        if game_resources["locked_icon"] == "rect":
            draw_icon_text(screen, LOCKED_TEXT, icon_center_x, icon_center_y)
        else:
            locked_surface = pygame.transform.scale(game_resources["locked_icon"], (ICON_SIZE, ICON_SIZE))
            screen.blit(locked_surface, (icon_center_x - ICON_SIZE // 2, icon_center_y - ICON_SIZE // 2))
    else:
        # 解锁状态：绘制原技能图标
        if game_resources.get("skill3_icon", "rect") == "rect":
            # 绘制跳跃图标（纯菱形）
            draw_diamond(screen, WHITE, icon_center_x, icon_center_y, 15)
            # 绘制向上箭头
            pygame.draw.polygon(screen, SKILL3_ACTIVE_COLOR, [
                (icon_center_x, icon_center_y - 10),
                (icon_center_x - 8, icon_center_y),
                (icon_center_x + 8, icon_center_y)
            ])
        else:
            icon_surface = pygame.transform.scale(game_resources["skill3_icon"], (ICON_SIZE, ICON_SIZE))
            screen.blit(icon_surface, (icon_center_x - ICON_SIZE // 2, icon_center_y - ICON_SIZE // 2))

    # 锁定状态不绘制冷却遮罩和CD文字
    if is_skill3_unlocked and not is_exhausted:
        # 绘制冷却进度遮罩
        if dino.skill3_cooldown and dino.skill3_progress > 0:
            draw_mask(screen, container_rect, dino.skill3_progress, is_easy_mode)
            cd_seconds = int(cd_remaining / 1000)
            draw_icon_text(screen, f"{cd_seconds}", icon_center_x, icon_center_y)

        # 绘制剩余使用次数（如果不是无限次）
        if uses_left > 0:
            uses_text = str(uses_left)
            uses_font = load_custom_font(14)
            # 计算文字宽度，紧贴右侧但不超出图标框
            text_width = uses_font.size(uses_text)[0]
            text_x = icon_x + CONTAINER_SIZE - text_width - 4  # 距离右边框4像素
            text_y = icon_y + CONTAINER_SIZE - 18  # 距离底部18像素
            # 在图标右下角显示剩余次数，带黑色描边
            draw_text_with_outline(screen, uses_text, uses_font,
                                   text_x, text_y,
                                   WHITE, BLACK, 2)

        # 绘制CD提升标识
        current_difficulty = get_current_difficulty(score)
        if current_difficulty >= 4:
            draw_boost_icon(screen, container_rect)

        current_difficulty = get_current_difficulty(score)
        if current_difficulty >= 3:  # 若需和skill1一致，改为二阶及以上显示提升图标
            draw_boost_icon(screen, container_rect)

# 绘制中央技能文字提示
def draw_skill_text(dino):
    """绘制技能文字提示"""
    current_time = pygame.time.get_ticks()

    # 绘制技能1文字
    if current_time < dino.skill1_text_end:
        # 文字渐变效果
        alpha = max(0,
                    255 - (current_time - (dino.skill1_text_end - SKILL1_TEXT_DURATION)) * 255 / SKILL1_TEXT_DURATION)

        # 主文字（带描边）
        text_main = SKILL_FONT.render(SKILL1_DISPLAY_TEXT, True, SKILL1_TEXT_COLOR)
        text_main.set_alpha(alpha)

        text_outline = SKILL_FONT.render(SKILL1_DISPLAY_TEXT, True, BLACK)
        text_outline.set_alpha(alpha)

        # 文字位置（居中）
        text_x = SCREEN_WIDTH // 2 - text_main.get_width() // 2
        text_y = SCREEN_HEIGHT // 2 - text_main.get_height() // 2 - 20

        # 多层描边
        for dx, dy in [(-4, -4), (-4, 4), (4, -4), (4, 4), (-4, 0), (4, 0), (0, -4), (0, 4)]:
            screen.blit(text_outline, (text_x + dx, text_y + dy))

        # 文字缩放动画
        scale = 1.0 + 0.1 * math.sin(current_time / 100)
        scaled_text = pygame.transform.scale(text_main,
                                             (int(text_main.get_width() * scale),
                                              int(text_main.get_height() * scale)))
        scaled_x = SCREEN_WIDTH // 2 - scaled_text.get_width() // 2
        scaled_y = SCREEN_HEIGHT // 2 - scaled_text.get_height() // 2 - 20

        screen.blit(scaled_text, (scaled_x, scaled_y))

    # 绘制技能2文字
    if current_time < dino.skill2_text_end:
        # 文字渐变效果
        alpha = max(0,
                    255 - (current_time - (dino.skill2_text_end - SKILL2_TEXT_DURATION)) * 255 / SKILL2_TEXT_DURATION)

        # 主文字（带描边）
        text_main = SKILL_FONT.render(SKILL2_DISPLAY_TEXT, True, SKILL2_TEXT_COLOR)
        text_main.set_alpha(alpha)

        text_outline = SKILL_FONT.render(SKILL2_DISPLAY_TEXT, True, BLACK)
        text_outline.set_alpha(alpha)

        # 文字位置（居中偏下）
        text_x = SCREEN_WIDTH // 2 - text_main.get_width() // 2
        text_y = SCREEN_HEIGHT // 2 - text_main.get_height() // 2 + 20

        # 多层描边
        for dx, dy in [(-4, -4), (-4, 4), (4, -4), (4, 4), (-4, 0), (4, 0), (0, -4), (0, 4)]:
            screen.blit(text_outline, (text_x + dx, text_y + dy))

        # 文字缩放动画
        scale = 1.0 + 0.1 * math.sin(current_time / 100)
        scaled_text = pygame.transform.scale(text_main,
                                             (int(text_main.get_width() * scale),
                                              int(text_main.get_height() * scale)))
        scaled_x = SCREEN_WIDTH // 2 - scaled_text.get_width() // 2
        scaled_y = SCREEN_HEIGHT // 2 - scaled_text.get_height() // 2 + 20

        screen.blit(scaled_text, (scaled_x, scaled_y))


# 绘制血条函数（移除额外血条和数字）
def draw_health_bar(dino):
    """绘制纯矩形血条（仅主血条，无数字）"""
    # 血条容器（中心顶部）
    bar_x = SCREEN_WIDTH // 2 - HEALTH_BAR_WIDTH // 2
    bar_y = 30
    container_height = HEALTH_BAR_HEIGHT + 12

    # 绘制容器背景（纯矩形+阴影）
    draw_rect(screen, WHITE, (bar_x - 6, bar_y - 6, HEALTH_BAR_WIDTH + 12, container_height), shadow=True)

    # 计算主血条当前宽度和颜色
    main_health_width = (dino.health / INITIAL_HEALTH) * HEALTH_BAR_WIDTH
    if dino.health <= HEALTH_LOW_THRESHOLD:
        bar_color = HEALTH_BAR_LOW_COLOR
        # 低血量闪烁
        if int(pygame.time.get_ticks() / 200) % 2 == 0:
            bar_color = (255, 150, 130)
    else:
        bar_color = HEALTH_BAR_COLOR

    # 主血条背景（纯矩形）
    pygame.draw.rect(screen, HEALTH_BAR_BG_COLOR, (bar_x, bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))

    # 当前主血量（纯矩形）
    if main_health_width > 0:
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, main_health_width, HEALTH_BAR_HEIGHT))

    # 主血条边框（纯矩形）
    pygame.draw.rect(screen, GRAY_MEDIUM, (bar_x, bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), 2)


# 绘制分数面板（纯矩形+仅显示得分，移除难度）
def draw_score_panel(score):
    """绘制纯矩形分数面板（仅显示得分）"""
    # 分数面板容器（纯矩形）

    # 从数据库获取高分
    high_score = int(get_db_value('high_score') or 0)

    panel_x = 30
    panel_y = 25
    panel_width = 220
    panel_height = 100

    # 纯矩形容器（带阴影）
    draw_rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), shadow=True)

    # 分数标题和数值
    score_title = ICON_FONT.render("Score", True, GRAY_MEDIUM)
    score_text = SCORE_FONT.render(f"{score}/{high_score}", True, PRIMARY_COLOR)

    # 绘制文本
    screen.blit(score_title, (panel_x + 20, panel_y + 15))
    screen.blit(score_text, (panel_x + 20, panel_y + 45))


# 生成粒子化常驻血迹
# 生成粒子化常驻血迹
def generate_blood_particles(current_health, existing_particles):
    """修改逻辑：只要生命值 < 1.0 就生成血迹粒子"""
    # 核心修改：移除原有按血量值匹配的逻辑，改为简单的阈值判断
    if current_health > 1.0:
        return []  # 生命值≥1.0时清空粒子

    # 定义生命值<1.0时的总粒子数量（可根据需求调整）
    TOTAL_PARTICLES = 400  # 你可以根据需要调整这个数值

    current_count = len(existing_particles)
    need_count = max(0, TOTAL_PARTICLES - current_count)

    # 生成新的粒子化血迹
    for _ in range(need_count):
        area = random.choice(BLOOD_SPLATTER_AREAS)
        existing_particles.append(BloodParticle(area))

    return existing_particles


# 更新并绘制粒子化血迹
def update_and_draw_blood_particles(particles):
    """更新所有粒子的微动状态并绘制（常驻不消失）"""
    for particle in particles:
        particle.update()
        particle.draw()


# 碰撞检测函数
def check_collision(dino, obstacle):
    """精确碰撞检测"""
    if dino.skill1_active or dino.invulnerable:
        return False
    dino_rect = pygame.Rect(dino.x, dino.y, dino.width, dino.height)
    obstacle_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
    return dino_rect.colliderect(obstacle_rect)







# 主游戏函数（统一图标样式）
def main():
    global game_resources, start_menu_bgm, selected_skill, blood_particles  # 新增selected_skill
    selected_skill = None  # 初始化本局选中的技能
    game_resources = load_resource()
    unlocked_skills = load_unlocked_skills()

    # 初始化游戏元素（保留）
    bg_scroll = ScrollingBackground()  # 滚动背景初始化
    dino = Dinosaur()
    ground = ScrollingGround()
    obstacles = []
    score = 0
    high_score = 0
    game_over = False
    game_started = False
    last_obstacle_time = pygame.time.get_ticks()
    last_score_time = pygame.time.get_ticks()
    current_speed = BASE_OBSTACLE_SPEED
    blood_particles = []
    last_difficulty = 1
    carried_skills = []  # 初始化本局携带的技能列表
    success_mode = False
    success_start_time = 0
    rank_change_info = None  # 段位分变化信息 (type, value)

    start_menu_bgm = None  # 开始界面BGM对象
    if start_menu_bgm is None:
        try:
            # 加载开始界面专属BGM
            start_menu_bgm = pygame.mixer.Sound(START_MENU_BGM_PATH)
            start_menu_bgm.set_volume(START_MENU_BGM_VOLUME)
            start_menu_bgm.play(-1)  # -1表示循环播放
        except:
            print(f"警告：开始界面背景音乐 {START_MENU_BGM_PATH} 加载失败")
            start_menu_bgm = None

    # 初始化轮流播放的BGM
    bgm_sounds = []
    for bgm_file in BGM_LIST:
        try:
            bgm = pygame.mixer.Sound(bgm_file)
            bgm.set_volume(BGM_VOLUME)
            bgm_sounds.append(bgm)
        except:
            # 加载失败时跳过该文件
            print(f"警告：{bgm_file} 加载失败")
            continue

    # 初始化当前播放状态
    current_bgm_index = 0
    current_bgm = None
    # 记录当前BGM播放开始时间
    bgm_play_start_time = 0

    # 从数据库获取高分
    high_score = int(get_db_value('high_score') or 0)

    while True:
        # FPS控制（保留）- 叠加技能3、阶段和矫健天赋的FPS提升
        total_fps_boost = dino.skill3_fps_boost + dino.stage_fps_boost + dino.agility_fps_boost
        current_fps = FPS * (1 + total_fps_boost)
        clock.tick(current_fps)
        current_time = pygame.time.get_ticks()

        # 事件处理（保留）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if start_menu_bgm is not None:
                    start_menu_bgm.stop()
                if current_bgm is not None:
                    current_bgm.stop()
                # 保存高分到数据库
                set_db_value('high_score', high_score)
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_m:
                    # 【修改点】重启前停止所有BGM
                    if start_menu_bgm is not None:
                        start_menu_bgm.stop()
                        start_menu_bgm = None  # 重置BGM状态
                    if current_bgm is not None:
                        current_bgm.stop()
                        current_bgm = None

                    global store_bgm
                    if store_bgm is not None:
                        store_bgm.stop()
                        store_bgm = None
                    main()
                    return

            if event.type == pygame.USEREVENT + 1:
                if "_level_up_second_play" in game_resources:
                    game_resources["_level_up_second_play"]()
                    del game_resources["_level_up_second_play"]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if game_started and not game_over:
                        dino.jump()

                # 按D键打开开发者工具
                if not game_started and event.key == pygame.K_d:
                    open_developer_tool()
                    print("Developer tool opened")

            # 鼠标点击事件（主界面按钮）
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_started:
                mouse_pos = event.pos
                # 检查是否点击了开始游戏按钮
                if start_button_rect.collidepoint(mouse_pos):
                    selection_result = open_skill_selection()
                    if selection_result is not False:
                        selected_skills, game_mode = selection_result
                        # 停止主菜单音乐
                        if start_menu_bgm is not None:
                            start_menu_bgm.stop()
                            start_menu_bgm = None
                        game_started = True
                        current_time = pygame.time.get_ticks()
                        last_score_time = current_time
                        # 设置为更早的时间，确保游戏开始后立即生成第一个障碍物
                        last_obstacle_time = current_time - BASE_SPAWN_RATE - 1
                        # 保存本局携带的技能名称列表 - 新结构: (name, type, rarity)
                        carried_skills = [item[0] for item in selected_skills] if selected_skills else []
                        # 创建技能到品质的映射
                        skill_rarity_map = {item[0]: item[2] for item in selected_skills} if selected_skills else {}
                        print(f"Carried skills this game: {carried_skills}")
                        print(f"Skill rarity map: {skill_rarity_map}")
                        print(f"Game mode: {game_mode}")
                        # 保存上次使用的技能
                        save_last_used_skills(carried_skills)
                        # 检查张狂道具（必须在本局携带列表中）
                        print(f"Loaded skills: {unlocked_skills}")
                        if "Frenzy" in carried_skills:
                            frenzy_rarity = skill_rarity_map.get("Frenzy", "rare")
                            dino.frenzy_start_time = current_time
                            dino.frenzy_active = True
                            # 根据稀有度设置延迟时间
                            dino.frenzy_delay = ITEM_RARITY["frenzy"][frenzy_rarity]["delay"]
                            print(f"Frenzy activated! Rarity: {frenzy_rarity}, Delay: {dino.frenzy_delay}ms")
                        else:
                            print("Frenzy not carried this game")
                        
                        # 检查矫健天赋（必须在本局携带列表中）
                        if "Agility" in carried_skills:
                            agility_rarity = skill_rarity_map.get("Agility", "rare")
                            dino.agility_active = True
                            dino.agility_fps_boost = ITEM_RARITY["agility"][agility_rarity]["fps_boost"]
                            print(f"Agility activated! Rarity: {agility_rarity}, FPS Boost: {dino.agility_fps_boost*100}%")
                        else:
                            print("Agility not carried this game")
                # 检查是否点击了积分商店按钮
                elif shop_button_rect.collidepoint(mouse_pos):
                    open_score_shop()
                    print("store is opened")
                # 检查是否点击了赛季历史按钮
                elif season_button_rect.collidepoint(mouse_pos):
                    open_season_history()
                    print("Season history opened")
                # 检查是否点击了历史战绩按钮
                elif history_button_rect.collidepoint(mouse_pos):
                    open_game_history()
                    print("Game history opened")
            
            # 鼠标点击事件（结算界面继续按钮）
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_over:
                mouse_pos = event.pos
                # 检查是否点击了继续按钮
                if continue_button_rect.collidepoint(mouse_pos):
                    if current_bgm is not None:
                        current_bgm.stop()
                    main()
                    return

            if event.type == pygame.KEYDOWN:
                if event.key == SKILL1_KEY and game_started and not game_over:
                    dino.activate_skill1(score, carried_skills, skill_rarity_map)
                    print("skill1 key activated")
                elif event.key == SKILL2_KEY and game_started and not game_over:
                    dino.activate_skill2(score, carried_skills, skill_rarity_map)
                    print("skill 2 key activated")
                elif event.key == SKILL3_KEY and game_started and not game_over:
                    dino.activate_skill3(score, carried_skills, skill_rarity_map)
                    print("skill 3 key activated")

        # 游戏未开始界面（改为积分商店风格）
        if not game_started:
            # 绘制纯色背景
            screen.fill(BACKGROUND_COLOR)

            # 字体设置（与商店风格一致）
            title_font = load_custom_font(48, bold=True)
            medium_font = load_custom_font(24)
            shop_font = load_custom_font(20)
            small_font = load_custom_font(16)

            margin = 30

            # 标题区域（居中）
            title_text = title_font.render("ESCAPE!", True, PRIMARY_COLOR)
            subtitle_text = shop_font.render("Endless Running Adventure", True, GRAY_DARK)

            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))
            screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, 85))

            # 段位显示区域（右上角）
            rank_num, stage_num, progress, needed, rank_name, stage_name, rank_color = get_rank_info()
            rank_display_text = f"{rank_name} {stage_name}"
            rank_text = medium_font.render(rank_display_text, True, BLACK)
            rank_margin = 20
            
            # 段位进度条（右上角，段位名称下方）
            progress_bar_width = 100
            progress_bar_height = 6
            progress_bar_x = SCREEN_WIDTH - progress_bar_width - rank_margin
            progress_bar_y = rank_margin + 28
            
            # 加载并显示段位图标
            icon_size = 48
            icon_y = rank_margin - 2
            try:
                if rank_name == "Honor":
                    icon_filename = "rankicon/rank7.png"
                else:
                    rank_data = RANK_CONFIG.get(rank_num, {})
                    icon_filename = rank_data.get("icon", f"rank{rank_num}.png")
                rank_icon = pygame.image.load(icon_filename).convert_alpha()
                rank_icon = pygame.transform.scale(rank_icon, (icon_size, icon_size))
                
                # 计算图标位置：优先显示在段位文本左侧8px，如果距离小于进度条距离则显示在进度条左侧5px
                icon_x_text = SCREEN_WIDTH - rank_text.get_width() - rank_margin - icon_size - 8
                icon_x_bar = progress_bar_x - icon_size - 5
                icon_x = min(icon_x_text, icon_x_bar)
                
                screen.blit(rank_icon, (icon_x, icon_y))
            except:
                pass
            
            screen.blit(rank_text, (SCREEN_WIDTH - rank_text.get_width() - rank_margin, rank_margin))
            
            # 判断是否达到最高段位
            is_max_rank = (rank_num == 6 and stage_num == 4 and progress >= needed)
            
            if is_max_rank:
                rank_score = get_rank_score()
                progress_text = small_font.render(f"{rank_score}", True, rank_color)
                screen.blit(progress_text, (SCREEN_WIDTH - progress_text.get_width() - rank_margin, progress_bar_y))
            else:
                pygame.draw.rect(screen, GRAY_DARK, (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height))
                fill_width = int((progress / needed) * progress_bar_width) if needed > 0 else 0
                if fill_width > 0:
                    pygame.draw.rect(screen, rank_color, (progress_bar_x, progress_bar_y, fill_width, progress_bar_height))
                
                progress_text = small_font.render(f"{progress}/{needed}", True, GRAY_DARK)
                screen.blit(progress_text, (SCREEN_WIDTH - progress_text.get_width() - rank_margin, progress_bar_y + 8))
            
            # 赛季统计信息
            season_stats = get_season_stats()
            stats_y = progress_bar_y + 25
            win_rate_text = small_font.render(f"Win Rate: {season_stats['win_rate']:.1f}%", True, GRAY_DARK)
            screen.blit(win_rate_text, (SCREEN_WIDTH - win_rate_text.get_width() - rank_margin, stats_y))
            
            games_text = small_font.render(f"Games: {season_stats['total_games']}", True, GRAY_DARK)
            screen.blit(games_text, (SCREEN_WIDTH - games_text.get_width() - rank_margin, stats_y + 15))
            
            wins_text = small_font.render(f"Wins: {season_stats['total_wins']}", True, GRAY_DARK)
            screen.blit(wins_text, (SCREEN_WIDTH - wins_text.get_width() - rank_margin, stats_y + 30))

            # 最高分显示
            high_score_text = shop_font.render(f"High Score: {high_score}", True, ACCENT_COLOR)
            screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 115))

            # 快速操作区域
            y_offset = 145
            section_title = medium_font.render("Quick Actions", True, PRIMARY_COLOR)
            screen.blit(section_title, (margin, y_offset))
            pygame.draw.line(screen, GRAY_LIGHT, (margin, y_offset + 30), (SCREEN_WIDTH - margin, y_offset + 30), 2)

            # 按钮并排显示（三个按钮）- 使用准备界面Start按钮样式（主题蓝，无边框，文字居中）
            button_width = 200
            button_height = 50
            button_spacing = 30
            
            # 计算四个按钮的总宽度，使其居中
            total_buttons_width = 4 * button_width + 3 * button_spacing
            buttons_start_x = (SCREEN_WIDTH - total_buttons_width) // 2

            # 按钮文字字体（比medium_font小一点）
            button_font = load_custom_font(20)
            
            # 按钮悬停颜色（比SECONDARY_COLOR深）
            BUTTON_HOVER_COLOR = (56, 151, 190)
            
            # 获取鼠标位置
            mouse_pos = pygame.mouse.get_pos()

            # 开始游戏按钮（左侧）
            start_button_rect = pygame.Rect(buttons_start_x, y_offset + 45, button_width, button_height)
            start_button_color = BUTTON_HOVER_COLOR if start_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
            pygame.draw.rect(screen, start_button_color, start_button_rect)
            pygame.draw.rect(screen, GRAY_LIGHT, start_button_rect, 2)
            start_text = button_font.render("Start Game", True, WHITE)
            screen.blit(start_text, (start_button_rect.x + (button_width - start_text.get_width()) // 2, start_button_rect.y + (button_height - start_text.get_height()) // 2))

            # 积分商店按钮（左中）
            shop_button_rect = pygame.Rect(buttons_start_x + button_width + button_spacing, y_offset + 45, button_width, button_height)
            shop_button_color = BUTTON_HOVER_COLOR if shop_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
            pygame.draw.rect(screen, shop_button_color, shop_button_rect)
            pygame.draw.rect(screen, GRAY_LIGHT, shop_button_rect, 2)
            shop_text = button_font.render("Score Shop", True, WHITE)
            screen.blit(shop_text, (shop_button_rect.x + (button_width - shop_text.get_width()) // 2, shop_button_rect.y + (button_height - shop_text.get_height()) // 2))

            # 赛季历史按钮（右中）
            season_button_rect = pygame.Rect(buttons_start_x + 2 * (button_width + button_spacing), y_offset + 45, button_width, button_height)
            season_button_color = BUTTON_HOVER_COLOR if season_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
            pygame.draw.rect(screen, season_button_color, season_button_rect)
            pygame.draw.rect(screen, GRAY_LIGHT, season_button_rect, 2)
            season_text = button_font.render("Season History", True, WHITE)
            screen.blit(season_text, (season_button_rect.x + (button_width - season_text.get_width()) // 2, season_button_rect.y + (button_height - season_text.get_height()) // 2))

            # 历史战绩按钮（右侧）
            history_button_rect = pygame.Rect(buttons_start_x + 3 * (button_width + button_spacing), y_offset + 45, button_width, button_height)
            history_button_color = BUTTON_HOVER_COLOR if history_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
            pygame.draw.rect(screen, history_button_color, history_button_rect)
            pygame.draw.rect(screen, GRAY_LIGHT, history_button_rect, 2)
            history_text = button_font.render("Game History", True, WHITE)
            screen.blit(history_text, (history_button_rect.x + (button_width - history_text.get_width()) // 2, history_button_rect.y + (button_height - history_text.get_height()) // 2))

            # 操作提示区域
            y_offset += 130
            section_title = medium_font.render("Controls", True, PRIMARY_COLOR)
            screen.blit(section_title, (margin, y_offset))
            pygame.draw.line(screen, GRAY_LIGHT, (margin, y_offset + 30), (SCREEN_WIDTH - margin, y_offset + 30), 2)

            # 控制说明（单行并排显示）
            controls_y = y_offset + 45
            controls = [
                ("SPACE/UP", "Jump"),
                ("LSHIFT", "Dash"),
                ("CAPSLOCK", "Zoom"),
                ("TAB", "Leap")
            ]

            # 计算每个控制项的宽度
            total_width = SCREEN_WIDTH - 2 * margin - 40
            item_width = total_width // 4

            for i, (key, action) in enumerate(controls):
                x = margin + 20 + i * item_width
                y = controls_y

                key_text = small_font.render(key, True, ACCENT_COLOR)
                action_text = small_font.render(f"- {action}", True, GRAY_DARK)
                screen.blit(key_text, (x, y))
                screen.blit(action_text, (x + key_text.get_width() + 5, y))

            # 版本信息（右下角）
            version_text = small_font.render("Version 1.1.0", True, GRAY_DARK)
            version_x = SCREEN_WIDTH - version_text.get_width() - margin
            version_y = SCREEN_HEIGHT - version_text.get_height() - margin
            screen.blit(version_text, (version_x, version_y))

            pygame.display.flip()
            continue

        # 游戏未结束（核心修改：删除静态背景，仅保留滚动背景）
        if not game_over:
            # 更新并绘制滚动背景（唯一背景绘制入口）
            bg_scroll.update(current_speed)
            bg_scroll.draw()

            # 分数更新（保留）
            if current_time - last_score_time >= 1000:
                score += SCORE_PER_SECOND
                last_score_time = current_time
                if game_resources.get("score_sound"):
                    game_resources["score_sound"].play()

            # 张狂道具：根据延迟时间后瞬间获得150分数
            if dino.frenzy_active:
                # 检查是否已过延迟时间
                elapsed = current_time - dino.frenzy_start_time
                if elapsed >= dino.frenzy_delay:
                    # 延迟结束，瞬间增加150分
                    score += 150
                    dino.frenzy_active = False
                    # 使用后删除指定品质的道具
                    frenzy_rarity = skill_rarity_map.get("Frenzy", "rare")
                    update_skill_uses("Frenzy", 0, frenzy_rarity)

            # 难度更新（保留）
            current_difficulty = get_current_difficulty(score)
            if current_difficulty > last_difficulty:
                # 只有携带的技能才会触发升级闪光效果
                if "Brave Dash" in carried_skills and current_difficulty >= 1:
                    dino.skill1_upgrade_flash_end = current_time + SKILL_FLASH_DURATION
                if "Zoom Boost" in carried_skills and current_difficulty >= 1:
                    dino.skill2_upgrade_flash_end = current_time + SKILL_FLASH_DURATION
                if "Lucky Leap" in carried_skills and current_difficulty >= 1:
                    dino.skill3_upgrade_flash_end = current_time + SKILL_FLASH_DURATION

                # 阶段切换时，对正在冷却的技能立即应用CD减免
                dino.apply_cd_reduction_on_stage_change(current_difficulty)

                # 阶段每升一级，FPS提升15%
                stage_diff = current_difficulty - last_difficulty
                dino.stage_fps_boost += stage_diff * 0.15
                
                level_up_sound = game_resources.get("level_up_sound")
                if level_up_sound:
                    level_up_sound.play()  # 仅这一行，删除所有定时器/二次播放逻辑


                last_difficulty = current_difficulty

            # 速度计算（保留）
            if score <= SCORE_STAGE_2:
                base_speed = STAGE_SPEEDS[1]
                current_spawn_rate = BASE_SPAWN_RATE - 400
            elif score <= SCORE_STAGE_3:
                base_speed = STAGE_SPEEDS[2]
                current_spawn_rate = BASE_SPAWN_RATE - 600
            elif score <= SCORE_STAGE_4:
                base_speed = STAGE_SPEEDS[3]
                current_spawn_rate = BASE_SPAWN_RATE - 750
            else:
                base_speed = STAGE_SPEEDS[4]
                current_spawn_rate = max(BASE_SPAWN_RATE - 800, 600)

            # 新增：叠加代偿速度加成（确保不超过MAX_SPEED）
            current_speed = min(base_speed * (1 + dino.compensation_speed_bonus), MAX_SPEED + 10)



            if bgm_sounds:  # 确保有可用的BGM文件
                # 首次播放：启动第一个BGM
                if current_bgm is None:
                    current_bgm = bgm_sounds[current_bgm_index]
                    current_bgm.play(-1)  # 循环播放当前BGM
                    bgm_play_start_time = pygame.time.get_ticks()
                else:
                    # 获取当前BGM的时长（秒）
                    bgm_duration = current_bgm.get_length()
                    # 计算已播放时间（毫秒转秒）
                    played_seconds = (pygame.time.get_ticks() - bgm_play_start_time) / 1000

                    # 当当前BGM播放完一轮后，切换到下一个
                    if played_seconds >= bgm_duration:
                        # 停止当前BGM
                        current_bgm.stop()
                        # 切换到下一个索引（循环）
                        current_bgm_index = (current_bgm_index + 1) % len(bgm_sounds)
                        # 播放下一个BGM
                        current_bgm = bgm_sounds[current_bgm_index]
                        current_bgm.play(-1)
                        # 重置播放时间
                        bgm_play_start_time = pygame.time.get_ticks()

            # 游戏元素更新（保留）
            dino.update(score)
            ground.update(current_speed)

            if not dino.skill1_active and current_time - last_obstacle_time > current_spawn_rate:
                obstacle_type = random.choice(["cactus"] * 8 + ["bird"] * 2)
                obstacles.append(Obstacle(obstacle_type, dino.height))
                dino.obstacles_total += 1  # 统计生成的障碍物
                last_obstacle_time = current_time

            # 碰撞检测（保留）
            for obstacle in obstacles[:]:
                obstacle.update(current_speed)
                if check_collision(dino, obstacle):
                    current_health = dino.take_damage()
                    blood_particles = generate_blood_particles(current_health, blood_particles)
                if obstacle.is_off_screen():
                    dino.obstacles_cleared += 1  # 统计成功越过的障碍物
                    obstacles.remove(obstacle)

            blood_particles = generate_blood_particles(dino.health, blood_particles)

            # 游戏结束判断（保留）
            if dino.health <= 0:
                game_over = True
                blood_particles = generate_blood_particles(0.0, blood_particles)

                if current_bgm is not None:
                    current_bgm.stop()
                
                # 计算段位分，保存变化信息（仅在排位模式下）
                if game_mode == "ranked":
                    change_type, change_value, details, rank_change = save_total_score(score, dino, game_mode)
                    rank_change_info = (change_type, change_value, details, rank_change)  # 保存返回值到rank_change_info
                    update_season_data(score)  # 新增：更新赛季数据
                else:
                    # 练习模式不计算段位分，但仍然获得商店积分（x0.25倍率）
                    rank_change_info = None
                    rank_change = None
                    # 保存商店积分
                    current_total_score = get_total_score()
                    shop_points = calculate_score_points(score, game_mode)
                    new_total_score = current_total_score + shop_points
                    save_total_score_to_db(new_total_score)
                
                # 根据分数决定是否清空技能
                cleared_skills = []
                if score < MAX_SCORE and carried_skills:
                    # 从数据库中删除携带的技能（只删除相应品质）
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    try:
                        # 删除携带的技能（根据名称和品质）
                        for skill_name in carried_skills:
                            if skill_name in skill_rarity_map:
                                rarity = skill_rarity_map[skill_name]
                                cursor.execute("DELETE FROM unlocked_skills WHERE skill_name = ? AND rarity = ?", (skill_name, rarity))
                                cleared_skills.append(f"{skill_name} ({rarity})")
                            else:
                                # 兼容旧数据，只根据名称删除
                                cursor.execute("DELETE FROM unlocked_skills WHERE skill_name = ?", (skill_name,))
                                cleared_skills.append(skill_name)
                        conn.commit()
                    except:
                        pass
                    finally:
                        conn.close()

                # 显示成功界面（类似game over界面）
                game_over = True
                # 只有达到MAX_SCORE才显示成功界面
                if score >= MAX_SCORE:
                    success_mode = True
                else:
                    success_mode = False
                success_start_time = current_time

                if game_resources.get("game_over_sound"):
                    game_resources["game_over_sound"].play()

                # 检查段位变化并显示动画（在音效播放后）
                if rank_change:
                    show_rank_change_animation(rank_change)

                if score > high_score:
                    high_score = score
                    # 保存高分到数据库
                    set_db_value('high_score', high_score)
                
                # 保存游戏战绩
                game_data = {
                    'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'score': score,
                    'high_score': high_score,
                    'won': score >= MAX_SCORE,
                    'mode': 'Ranked' if game_mode == 'ranked' else 'Practice',
                    'skills': carried_skills
                }
                save_game_history(game_data)
                
                continue

            # 绘制游戏元素（保留，删除静态背景）
            update_and_draw_blood_particles(blood_particles)
            ground.draw()
            dino.draw()

            for obstacle in obstacles:
                if dino.skill1_active:
                    obstacle_surface = screen.copy()
                    obstacle.draw()
                    screen.blit(obstacle_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                else:
                    obstacle.draw()

            # 绘制UI（保留）
            draw_score_panel(score)
            draw_health_icon(dino)
            draw_difficulty_icon(score)
            draw_speed_icon(current_speed, score, dino)
            draw_fps_boost_icon(dino)  # 绘制FPS提升图标
            draw_jump_boost_icon(dino, score)
            draw_extra_health_icon(dino, score)
            draw_frenzy_icon(dino, score)  # 绘制张狂图标
            draw_agility_icon(dino, score)  # 绘制矫健图标
            draw_skill2_icon(dino, score, carried_skills)
            draw_skill1_icon(dino, score, carried_skills)
            draw_skill3_icon(dino, score, carried_skills)
            draw_health_regen_icon(dino, score)
            #draw_skill_text(dino)


        else:

            # 游戏结束界面（修改：添加滚动背景）

            bg_scroll.update(current_speed)

            bg_scroll.draw()

            update_and_draw_blood_particles(blood_particles)

            # 绘制游戏结束面板（积分商店样式）
            margin = 30
            
            # 绘制纯色背景
            screen.fill(BACKGROUND_COLOR)
            
            # 字体设置（与商店风格一致）
            title_font = load_custom_font(48, bold=True)
            medium_font = load_custom_font(24)
            shop_font = load_custom_font(20)
            small_font = load_custom_font(16)
            
            # 标题区域（居中）
            # 根据分数判定结局类型
            if score < 200:
                # 迷失结局
                title_text = title_font.render("Lost", True, ACCENT_COLOR)  # 红色迷失标题
                subtitle_text = medium_font.render("You are lost in the apocalypse", True, PRIMARY_COLOR)
            elif score >= MAX_SCORE:
                # 逃脱结局
                title_text = title_font.render("Survived", True, SECONDARY_COLOR)  # 蓝色存活标题
                subtitle_text = medium_font.render("Congratulations! You escaped the apocalypse!", True, PRIMARY_COLOR)
            else:
                # 普通结局
                title_text = title_font.render("Normal Ending", True, PRIMARY_COLOR)  # 普通结局标题
                subtitle_text = medium_font.render("You survived but didn't escape", True, PRIMARY_COLOR)
            
            score_text = medium_font.render(f"Score: {score}", True, PRIMARY_COLOR)
            high_score_text = shop_font.render(f"High Score: {high_score}", True, SECONDARY_COLOR)
            
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))
            screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, 80))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 115))
            screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 145))
            
            # 段位显示区域（仅在排位模式显示）
            if game_mode == "ranked":
                rank_num, stage_num, progress, needed, rank_name, stage_name, rank_color = get_rank_info()
                rank_display_text = f"{rank_name} {stage_name}"
                rank_text = medium_font.render(rank_display_text, True, BLACK)
                rank_margin = 20
                
                # 段位进度条（右上角，段位名称下方）
                progress_bar_width = 100
                progress_bar_height = 6
                progress_bar_x = SCREEN_WIDTH - progress_bar_width - rank_margin
                progress_bar_y = rank_margin + 28
                
                # 加载并显示段位图标
                icon_size = 48
                icon_y = rank_margin - 2
                try:
                    if rank_name == "Honor":
                        icon_filename = "rankicon/rank7.png"
                    else:
                        rank_data = RANK_CONFIG.get(rank_num, {})
                        icon_filename = rank_data.get("icon", f"rank{rank_num}.png")
                    rank_icon = pygame.image.load(icon_filename).convert_alpha()
                    rank_icon = pygame.transform.scale(rank_icon, (icon_size, icon_size))
                    
                    # 计算图标位置：优先显示在段位文本左侧8px，如果距离小于进度条距离则显示在进度条左侧5px
                    icon_x_text = SCREEN_WIDTH - rank_text.get_width() - rank_margin - icon_size - 8
                    icon_x_bar = progress_bar_x - icon_size - 5
                    icon_x = min(icon_x_text, icon_x_bar)
                    
                    screen.blit(rank_icon, (icon_x, icon_y))
                except:
                    pass
                
                screen.blit(rank_text, (SCREEN_WIDTH - rank_text.get_width() - rank_margin, rank_margin))
                
                # 判断是否达到最高段位
                is_max_rank = (rank_num == 6 and stage_num == 4 and progress >= needed)
                
                if is_max_rank:
                    rank_score = get_rank_score()
                    progress_text = small_font.render(f"{rank_score}", True, rank_color)
                    screen.blit(progress_text, (SCREEN_WIDTH - progress_text.get_width() - rank_margin, progress_bar_y))
                else:
                    pygame.draw.rect(screen, GRAY_DARK, (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height))
                    fill_width = int((progress / needed) * progress_bar_width) if needed > 0 else 0
                    if fill_width > 0:
                        pygame.draw.rect(screen, rank_color, (progress_bar_x, progress_bar_y, fill_width, progress_bar_height))
                    
                    progress_text = small_font.render(f"{progress}/{needed}", True, GRAY_DARK)
                    screen.blit(progress_text, (SCREEN_WIDTH - progress_text.get_width() - rank_margin, progress_bar_y + 8))
                
                # 段位分数变化显示（进度条下方）
                if rank_change_info:
                    if len(rank_change_info) == 4:
                        change_type, change_value, _, _ = rank_change_info
                    elif len(rank_change_info) == 3:
                        change_type, change_value, _ = rank_change_info
                    else:
                        change_type, change_value = rank_change_info
                    if change_type == "add":
                        change_text = small_font.render(f"+{change_value}", True, (0, 255, 0))  # 绿色表示增加
                    else:
                        change_text = small_font.render(f"-{change_value}", True, (255, 100, 100))  # 红色表示扣除
                    screen.blit(change_text, (SCREEN_WIDTH - change_text.get_width() - rank_margin, progress_bar_y + 22))
            
            # Skills lost and rank points details (two columns)
            y_offset = 175
            
            # Calculate column widths
            total_padding = 2 * margin + 60  # Left/right margins + column spacing
            column_width = (SCREEN_WIDTH - total_padding) // 2
            
            # First column: Skills Lost
            first_column_x = margin
            section_title = medium_font.render("Skills Lost", True, PRIMARY_COLOR)
            screen.blit(section_title, (first_column_x, y_offset))
            pygame.draw.line(screen, GRAY_LIGHT, (first_column_x, y_offset + 30), (first_column_x + column_width, y_offset + 30), 2)
            
            # Display cleared skills or None
            if cleared_skills:
                skills_y = y_offset + 45
                for skill in cleared_skills[:5]:  # Show up to 5 skills
                    skill_text = shop_font.render(f"• {skill}", True, SECONDARY_COLOR)
                    screen.blit(skill_text, (first_column_x + 20, skills_y))
                    skills_y += 20
            else:
                # No skills lost
                none_text = shop_font.render("None", True, SECONDARY_COLOR)
                screen.blit(none_text, (first_column_x + 20, y_offset + 45))
            
            # Second column: Rank Points (only show in ranked mode)
            second_column_x = first_column_x + column_width + 60
            if game_mode == "ranked":
                section_title = medium_font.render("Rank Points", True, PRIMARY_COLOR)
                screen.blit(section_title, (second_column_x, y_offset))
                pygame.draw.line(screen, GRAY_LIGHT, (second_column_x, y_offset + 30), (second_column_x + column_width, y_offset + 30), 2)
                
                # Display Rank Points details
                details_y = y_offset + 45
                if rank_change_info and len(rank_change_info) == 4:
                    change_type, change_value, details, rank_change = rank_change_info
                    
                    # Determine text color
                    if score >= MAX_SCORE:
                        text_color = SECONDARY_COLOR  # Blue (Escape ending)
                    elif score < 200:
                        text_color = (255, 100, 100)  # Red (Lost ending)
                    else:
                        text_color = (0, 0, 0)  # Black (Normal ending)
                    
                    # Display details
                    if details.get("low_score_penalty") > 0:
                        # Failure case
                        penalty_text = shop_font.render(f"Game Failed -10 points", True, text_color)
                        screen.blit(penalty_text, (second_column_x + 20, details_y))
                        details_y += 20
                        
                        protection = details.get("protection_amount", 0)
                        # 失败保护得分即使为0也显示
                        protection_text = shop_font.render(f"Failure Protection (Rank {details.get('rank_num')}) +{protection} points", True, text_color)
                        screen.blit(protection_text, (second_column_x + 20, details_y))
                        details_y += 20
                    else:
                        # Success or normal case
                        base_score = details.get("base_score", 0)
                        base_text = shop_font.render(f"Game Score +{base_score} points", True, text_color)
                        screen.blit(base_text, (second_column_x + 20, details_y))
                        details_y += 20
                        
                        win_score = details.get("win_score", 0)
                        # 胜利得分即使为0也显示（胜利结局）
                        if score >= MAX_SCORE:
                            win_text = shop_font.render(f"Game Success (Rank {details.get('rank_num')}) +{win_score} points", True, text_color)
                            screen.blit(win_text, (second_column_x + 20, details_y))
                            details_y += 20
                        
                        # 技能使用额外得分
                        skill_bonus = details.get("skill_usage_bonus", 0)
                        if skill_bonus > 0:
                            skill_text = shop_font.render(f"Skill Usage +{skill_bonus} points", True, text_color)
                            screen.blit(skill_text, (second_column_x + 20, details_y))
                            details_y += 20
                        
                        # 连续失败奖励
                        loss_bonus = details.get("consecutive_loss_bonus", 0)
                        if loss_bonus > 0:
                            if score >= MAX_SCORE:
                                loss_text = shop_font.render(f"End Losing Streak +{loss_bonus} points", True, text_color)
                            else:
                                loss_text = shop_font.render(f"Lucky Survival +{loss_bonus} points", True, text_color)
                            screen.blit(loss_text, (second_column_x + 20, details_y))
                            details_y += 20
                        
                        # 普通保护得分
                        normal_protection = details.get("normal_protection_score", 0)
                        if score < MAX_SCORE and score >= 200:  # 普通结局显示
                            protection_text = shop_font.render(f"Normal Protection (Rank {details.get('rank_num')}) +{normal_protection} points", True, text_color)
                            screen.blit(protection_text, (second_column_x + 20, details_y))
                            details_y += 20
                else:
                    # No information
                    none_text = shop_font.render("None", True, SECONDARY_COLOR)
                    screen.blit(none_text, (second_column_x + 20, details_y))
            else:
                # Practice mode - show practice info
                section_title = medium_font.render("Practice Mode", True, PRIMARY_COLOR)
                screen.blit(section_title, (second_column_x, y_offset))
                pygame.draw.line(screen, GRAY_LIGHT, (second_column_x, y_offset + 30), (second_column_x + column_width, y_offset + 30), 2)
                
                # Display practice mode info
                details_y = y_offset + 45
                practice_text = shop_font.render("Rank points not counted", True, SECONDARY_COLOR)
                screen.blit(practice_text, (second_column_x + 20, details_y))
                details_y += 25
                score_text = shop_font.render(f"Score: {score}", True, PRIMARY_COLOR)
                screen.blit(score_text, (second_column_x + 20, details_y))
                details_y += 25
                shop_points = calculate_score_points(score, game_mode)
                points_text = shop_font.render(f"Score Points: +{shop_points}", True, (0, 200, 0))
                screen.blit(points_text, (second_column_x + 20, details_y))
            
            # 继续按钮（右下角）
            continue_button_width = 200
            continue_button_height = 50
            continue_button_x = SCREEN_WIDTH - margin - continue_button_width
            continue_button_y = SCREEN_HEIGHT - margin - continue_button_height
            continue_button_rect = pygame.Rect(continue_button_x, continue_button_y, continue_button_width, continue_button_height)
            
            # 获取鼠标位置
            mouse_pos = pygame.mouse.get_pos()
            
            # 按钮悬停颜色
            BUTTON_HOVER_COLOR = (56, 151, 190)
            
            # 绘制按钮
            continue_button_color = BUTTON_HOVER_COLOR if continue_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
            pygame.draw.rect(screen, continue_button_color, continue_button_rect)
            pygame.draw.rect(screen, GRAY_LIGHT, continue_button_rect, 2)
            continue_button_text = shop_font.render("Continue", True, WHITE)
            screen.blit(continue_button_text, (continue_button_x + (continue_button_width - continue_button_text.get_width()) // 2, continue_button_y + (continue_button_height - continue_button_text.get_height()) // 2))

            # 更新显示（保留）
        pygame.display.flip()


def open_skill_selection():
    """Skill and Talent Selection Interface"""
    global unlocked_skills
    unlocked_skills = load_unlocked_skills()
    
    # 获取上次使用的技能
    last_used_skills = get_last_used_skills()
    
    # 技能和天赋列表
    skills_list = ["Brave Dash", "Zoom Boost", "Lucky Leap"]
    
    # 准备可选择的技能和天赋
    # 结构: [(name, type, rarity), ...]
    available_items = []
    
    # 添加技能 - 每个品质作为一个独立项
    for skill in skills_list:
        if skill in unlocked_skills and len(unlocked_skills[skill]) > 0:
            # 所有技能都使用嵌套字典结构
            for rarity in unlocked_skills[skill].keys():
                available_items.append((skill, "skill", rarity))
    
    # 添加天赋 - 查询所有已解锁的品质
    # Frenzy 可能解锁了多个品质
    if "Frenzy" in unlocked_skills and len(unlocked_skills["Frenzy"]) > 0:
        for rarity in unlocked_skills["Frenzy"].keys():
            available_items.append(("Frenzy", "talent", rarity))
    
    # Agility 可能解锁了多个品质
    if "Agility" in unlocked_skills and len(unlocked_skills["Agility"]) > 0:
        for rarity in unlocked_skills["Agility"].keys():
            available_items.append(("Agility", "talent", rarity))
    
    selected_items = []
    total_points = 90
    points_per_item = 30
    
    # 提示信息变量
    warning_message = None
    warning_start_time = 0
    WARNING_DURATION = 5000  # 5秒
    
    while True:
        # 绘制界面
        screen.fill(BACKGROUND_COLOR)
        
        # 边距设置
        margin = 20
        icon_size = 44  # 与游戏内容器大小一致 (CONTAINER_SIZE = 44)
        icon_spacing = 60
        
        # 字体设置（与商店风格一致）
        title_font = load_custom_font(32, bold=True)
        medium_font = load_custom_font(24)
        shop_font = load_custom_font(20)
        small_font = load_custom_font(16)
        
        # 标题区域（居中，与商店风格一致）
        title_text = title_font.render("Prepare for Game", True, PRIMARY_COLOR)
        subtitle_text = shop_font.render(f"Remaining Points: {total_points}", True, ACCENT_COLOR)
        selected_count_text = shop_font.render(f"Selected: {len(selected_items)}/3 items", True, GRAY_DARK)
        
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 15))
        screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, 50))
        screen.blit(selected_count_text, (SCREEN_WIDTH // 2 - selected_count_text.get_width() // 2, 75))
        
        # 右上角显示上次使用的技能
        if last_used_skills:
            last_used_title = shop_font.render("Last Used", True, GRAY_DARK)
            screen.blit(last_used_title, (SCREEN_WIDTH - margin - 108, 15))
            
            for i, skill_data in enumerate(last_used_skills[:3]):  # 最多显示3个
                skill_name = skill_data["name"]
                x = SCREEN_WIDTH - margin - 108 + i * 40
                y = 45
                
                # 获取技能类型和稀有度
                # 从 last_used_skills 中获取保存的品质
                last_rarity = skill_data.get("rarity", "rare")
                if skill_name in skills_list:
                    item_type = "skill"
                    if skill_name in unlocked_skills and len(unlocked_skills[skill_name]) > 0:
                        # 使用上次使用的品质
                        border_color = SKILL_RARITY[last_rarity]["color"]
                    else:
                        border_color = (150, 150, 150)
                elif skill_name in ["Frenzy", "Agility"]:
                    item_type = "talent"
                    if skill_name in unlocked_skills and len(unlocked_skills[skill_name]) > 0:
                        # 使用上次使用的品质
                        if skill_name == "Frenzy":
                            border_color = ITEM_RARITY["frenzy"][last_rarity]["color"]
                        elif skill_name == "Agility":
                            border_color = ITEM_RARITY["agility"][last_rarity]["color"]
                    else:
                        border_color = (150, 150, 150)
                else:
                    border_color = (150, 150, 150)
                
                # 绘制小图标
                small_icon_size = 32
                icon_rect = (x, y, small_icon_size, small_icon_size)
                base_color = (230, 230, 230)
                pygame.draw.rect(screen, base_color, icon_rect)
                pygame.draw.rect(screen, border_color, icon_rect, 2)
                
                # 绘制图标内容
                icon_center_x = x + small_icon_size // 2
                icon_center_y = y + small_icon_size // 2
                icon_inner_size = 24
                
                if skill_name == "Brave Dash" and game_resources.get("skill1_icon") != "rect":
                    icon_surface = pygame.transform.scale(game_resources["skill1_icon"], (icon_inner_size, icon_inner_size))
                    screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
                elif skill_name == "Zoom Boost" and game_resources.get("skill2_icon") != "rect":
                    icon_surface = pygame.transform.scale(game_resources["skill2_icon"], (icon_inner_size, icon_inner_size))
                    screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
                elif skill_name == "Lucky Leap" and game_resources.get("skill3_icon") != "rect":
                    icon_surface = pygame.transform.scale(game_resources["skill3_icon"], (icon_inner_size, icon_inner_size))
                    screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
                elif skill_name == "Frenzy" and game_resources.get("frenzy_icon") != "rect":
                    icon_surface = pygame.transform.scale(game_resources["frenzy_icon"], (icon_inner_size, icon_inner_size))
                    screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
                else:
                    # 兜底样式
                    draw_diamond(screen, WHITE, icon_center_x, icon_center_y, 10)
                    item_text = load_custom_font(10).render(skill_name[:2], True, border_color)
                    screen.blit(item_text, (icon_center_x - item_text.get_width() // 2, icon_center_y - item_text.get_height() // 2))
        
        # 已选择的物品区域
        y_offset = 110
        selected_title = medium_font.render("Selected Items", True, PRIMARY_COLOR)
        screen.blit(selected_title, (margin, y_offset))
        pygame.draw.line(screen, GRAY_LIGHT, (margin, y_offset + 30), (SCREEN_WIDTH - margin, y_offset + 30), 2)
        
        # 绘制已选择的物品
        # 新结构: (name, type, rarity)
        for i, (item, item_type, rarity) in enumerate(selected_items):
            x = margin + i * icon_spacing
            y = y_offset + 45
            
            # 获取稀有度颜色 - 使用当前遍历到的rarity，而不是第一个品质
            if item_type == "skill":
                border_color = SKILL_RARITY[rarity]["color"]
            else:  # talent
                if item == "Frenzy":
                    border_color = ITEM_RARITY["frenzy"][rarity]["color"]
                elif item == "Agility":
                    border_color = ITEM_RARITY["agility"][rarity]["color"]
                else:
                    border_color = (255, 255, 255)
            
            # 绘制图标容器（统一底色，边框显示品质）
            container_rect = (x, y, icon_size, icon_size)
            # 底色使用金黄色表示选中
            base_color = (255, 215, 0)
            pygame.draw.rect(screen, base_color, container_rect)
            # 绘制品质边框（3px粗）
            pygame.draw.rect(screen, border_color, container_rect, 3)

            # 绘制图标
            icon_center_x = x + icon_size // 2
            icon_center_y = y + icon_size // 2
            icon_inner_size = 32  # 与游戏内图标大小一致 (ICON_SIZE = 32)

            if item == "Brave Dash" and game_resources.get("skill1_icon") != "rect":
                icon_surface = pygame.transform.scale(game_resources["skill1_icon"], (icon_inner_size, icon_inner_size))
                screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
            elif item == "Zoom Boost" and game_resources.get("skill2_icon") != "rect":
                icon_surface = pygame.transform.scale(game_resources["skill2_icon"], (icon_inner_size, icon_inner_size))
                screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
            elif item == "Lucky Leap" and game_resources.get("skill3_icon") != "rect":
                icon_surface = pygame.transform.scale(game_resources["skill3_icon"], (icon_inner_size, icon_inner_size))
                screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
            elif item == "Frenzy" and game_resources.get("frenzy_icon") != "rect":
                icon_surface = pygame.transform.scale(game_resources["frenzy_icon"], (icon_inner_size, icon_inner_size))
                screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
            else:
                # 兜底样式（与游戏内样式一致）
                draw_diamond(screen, WHITE, icon_center_x, icon_center_y, 15)
                item_text = load_custom_font(10).render(item[:3], True, border_color)
                screen.blit(item_text, (icon_center_x - item_text.get_width() // 2, icon_center_y - item_text.get_height() // 2))

        # 可用的物品区域 - 横向列表展示
        y_offset += 110
        available_title = medium_font.render("Available Skills & Talents", True, PRIMARY_COLOR)
        screen.blit(available_title, (margin, y_offset))
        pygame.draw.line(screen, GRAY_LIGHT, (margin, y_offset + 30), (SCREEN_WIDTH - margin, y_offset + 30), 2)

        # 绘制可用的物品 - 横向排列
        # 新结构: (name, type, rarity)
        for i, (item, item_type, rarity) in enumerate(available_items):
            # 横向排列，所有物品在一行
            x = margin + i * icon_spacing
            y = y_offset + 45

            # 获取稀有度颜色 - 使用当前遍历到的rarity
            if item_type == "skill":
                border_color = SKILL_RARITY[rarity]["color"]
            else:  # talent
                if item == "Frenzy":
                    border_color = ITEM_RARITY["frenzy"][rarity]["color"]
                elif item == "Agility":
                    border_color = ITEM_RARITY["agility"][rarity]["color"]
                else:
                    border_color = (255, 255, 255)

            # 绘制图标容器（统一底色，边框显示品质）
            container_rect = (x, y, icon_size, icon_size)
            # 底色使用金黄色表示选中 - 检查 (item, item_type, rarity) 是否在 selected_items 中
            item_key = (item, item_type, rarity)
            base_color = (255, 215, 0) if item_key in selected_items else (230, 230, 230)
            pygame.draw.rect(screen, base_color, container_rect)
            # 绘制品质边框（3px粗）
            pygame.draw.rect(screen, border_color, container_rect, 3)

            # 绘制图标
            icon_center_x = x + icon_size // 2
            icon_center_y = y + icon_size // 2
            icon_inner_size = 32  # 与游戏内图标大小一致 (ICON_SIZE = 32)

            if item == "Brave Dash" and game_resources.get("skill1_icon") != "rect":
                icon_surface = pygame.transform.scale(game_resources["skill1_icon"], (icon_inner_size, icon_inner_size))
                screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
            elif item == "Zoom Boost" and game_resources.get("skill2_icon") != "rect":
                icon_surface = pygame.transform.scale(game_resources["skill2_icon"], (icon_inner_size, icon_inner_size))
                screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
            elif item == "Lucky Leap" and game_resources.get("skill3_icon") != "rect":
                icon_surface = pygame.transform.scale(game_resources["skill3_icon"], (icon_inner_size, icon_inner_size))
                screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
            elif item == "Frenzy" and game_resources.get("frenzy_icon") != "rect":
                icon_surface = pygame.transform.scale(game_resources["frenzy_icon"], (icon_inner_size, icon_inner_size))
                screen.blit(icon_surface, (icon_center_x - icon_inner_size // 2, icon_center_y - icon_inner_size // 2))
            elif item == "Agility":
                # 矫健天赋使用文字图标
                agility_font = load_custom_font(14, bold=True)
                agility_text = agility_font.render("A", True, border_color)
                screen.blit(agility_text, (icon_center_x - agility_text.get_width() // 2, icon_center_y - agility_text.get_height() // 2))
            else:
                # 兜底样式（与游戏内样式一致）
                draw_diamond(screen, WHITE, icon_center_x, icon_center_y, 15)
                item_text = load_custom_font(10).render(item[:3], True, border_color)
                screen.blit(item_text, (icon_center_x - item_text.get_width() // 2, icon_center_y - item_text.get_height() // 2))

        # 返回按钮（左上角）
        back_button_width = 80
        back_button_height = 36
        back_button_x = margin
        back_button_y = margin
        back_button_rect = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)
        
        # 获取鼠标位置
        mouse_pos = pygame.mouse.get_pos()
        
        # 按钮悬停颜色
        BUTTON_HOVER_COLOR = (56, 151, 190)
        
        # 绘制返回按钮
        back_button_color = BUTTON_HOVER_COLOR if back_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
        pygame.draw.rect(screen, back_button_color, back_button_rect)
        pygame.draw.rect(screen, GRAY_LIGHT, back_button_rect, 2)
        back_button_text = small_font.render("Back", True, WHITE)
        screen.blit(back_button_text, (back_button_x + (back_button_width - back_button_text.get_width()) // 2, back_button_y + (back_button_height - back_button_text.get_height()) // 2))
        
        # 游戏模式按钮（右下角并排显示）
        button_width = 180
        button_height = 50
        button_spacing = 20
        button_y = SCREEN_HEIGHT - margin - button_height
        
        # 排位模式按钮（左侧）
        ranked_button_x = SCREEN_WIDTH - margin - 2 * button_width - button_spacing
        ranked_button_rect = pygame.Rect(ranked_button_x, button_y, button_width, button_height)
        ranked_button_color = BUTTON_HOVER_COLOR if ranked_button_rect.collidepoint(mouse_pos) else SECONDARY_COLOR
        pygame.draw.rect(screen, ranked_button_color, ranked_button_rect)
        pygame.draw.rect(screen, GRAY_LIGHT, ranked_button_rect, 2)
        ranked_button_text = shop_font.render("Ranked Mode", True, WHITE)
        screen.blit(ranked_button_text, (ranked_button_x + (button_width - ranked_button_text.get_width()) // 2, button_y + (button_height - ranked_button_text.get_height()) // 2))
        
        # 练习模式按钮（右侧）
        practice_button_x = SCREEN_WIDTH - margin - button_width
        practice_button_rect = pygame.Rect(practice_button_x, button_y, button_width, button_height)
        practice_button_color = BUTTON_HOVER_COLOR if practice_button_rect.collidepoint(mouse_pos) else (100, 180, 100)
        pygame.draw.rect(screen, practice_button_color, practice_button_rect)
        pygame.draw.rect(screen, GRAY_LIGHT, practice_button_rect, 2)
        practice_button_text = shop_font.render("Practice Mode", True, WHITE)
        screen.blit(practice_button_text, (practice_button_x + (button_width - practice_button_text.get_width()) // 2, button_y + (button_height - practice_button_text.get_height()) // 2))
        
        # 显示警告提示（如果有）- 置于最顶层
        if warning_message:
            current_time = pygame.time.get_ticks()
            if current_time - warning_start_time < WARNING_DURATION:
                # 计算透明度（淡入淡出效果）
                elapsed = current_time - warning_start_time
                if elapsed < 500:  # 淡入
                    alpha = int(255 * (elapsed / 500))
                elif elapsed > WARNING_DURATION - 500:  # 淡出
                    alpha = int(255 * ((WARNING_DURATION - elapsed) / 500))
                else:
                    alpha = 255
                
                # 绘制警告背景
                warning_font = load_custom_font(20, bold=True)
                warning_text = warning_font.render(warning_message, True, ACCENT_COLOR)
                warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
                
                # 绘制半透明背景
                bg_surface = pygame.Surface((warning_text.get_width() + 40, warning_text.get_height() + 20), pygame.SRCALPHA)
                pygame.draw.rect(bg_surface, (255, 255, 255, alpha), bg_surface.get_rect())
                pygame.draw.rect(bg_surface, (ACCENT_COLOR[0], ACCENT_COLOR[1], ACCENT_COLOR[2], alpha), bg_surface.get_rect(), 2)
                screen.blit(bg_surface, (warning_rect.centerx - bg_surface.get_width() // 2, warning_rect.centery - bg_surface.get_height() // 2))
                
                # 绘制文字
                warning_surface = warning_font.render(warning_message, True, ACCENT_COLOR)
                warning_surface.set_alpha(alpha)
                screen.blit(warning_surface, warning_rect)
            else:
                warning_message = None
        
        pygame.display.flip()
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            # 鼠标点击事件
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # 检查是否点击了返回按钮
                if back_button_rect.collidepoint(mouse_pos):
                    return False
                
                # 检查是否点击了排位模式按钮
                if ranked_button_rect.collidepoint(mouse_pos):
                    # 检查是否至少选择了一个物品
                    if len(selected_items) == 0:
                        # 检查商店分数是否足够购买技能/天赋
                        shop_score = get_total_score()
                        has_enough_shop_score = shop_score >= 3600
                        has_available_items = len(available_items) > 0
                        
                        # 如果商店分数足够但没有已解锁的技能/天赋，提示去商店购买
                        if has_enough_shop_score and not has_available_items:
                            warning_message = "Please buy skills or talents from the shop first!"
                            warning_start_time = pygame.time.get_ticks()
                        # 检查是否有可用的物品且没有足够分数购买
                        elif has_available_items and total_points >= points_per_item:
                            # 有可用物品但没选择，显示警告
                            warning_message = "Please select at least 1 skill or talent!"
                            warning_start_time = pygame.time.get_ticks()
                        else:
                            # 没有可用物品或没有足够分数，允许空选进入排位模式
                            return (selected_items, "ranked")
                    else:
                        return (selected_items, "ranked")
                
                # 检查是否点击了练习模式按钮
                if practice_button_rect.collidepoint(mouse_pos):
                    # 检查是否至少选择了一个物品
                    if len(selected_items) == 0:
                        # 检查商店分数是否足够购买技能/天赋
                        shop_score = get_total_score()
                        has_enough_shop_score = shop_score >= 3600
                        has_available_items = len(available_items) > 0
                        
                        # 如果商店分数足够但没有已解锁的技能/天赋，提示去商店购买
                        if has_enough_shop_score and not has_available_items:
                            warning_message = "Please buy skills or talents from the shop first!"
                            warning_start_time = pygame.time.get_ticks()
                        # 检查是否有可用的物品且没有足够分数购买
                        elif has_available_items and total_points >= points_per_item:
                            # 有可用物品但没选择，显示警告
                            warning_message = "Please select at least 1 skill or talent!"
                            warning_start_time = pygame.time.get_ticks()
                        else:
                            # 没有可用物品或没有足够分数，允许空选进入练习模式
                            return (selected_items, "practice")
                    else:
                        return (selected_items, "practice")
                
                # 检查是否点击了右上角的技能图标（一键购买）
                if last_used_skills:
                    for i, skill_data in enumerate(last_used_skills[:3]):
                        skill_name = skill_data["name"]
                        last_rarity = skill_data["rarity"]
                        x = SCREEN_WIDTH - margin - 108 + i * 40
                        y = 45
                        small_icon_size = 32
                        
                        if x <= mouse_pos[0] <= x + small_icon_size and y <= mouse_pos[1] <= y + small_icon_size:
                            # 检查技能是否已解锁
                            if skill_name not in unlocked_skills:
                                # 获取价格
                                price = 0
                                if skill_name in skills_list:
                                    price = SKILL_RARITY[last_rarity]["price"]
                                elif skill_name == "Frenzy":
                                    price = ITEM_RARITY["frenzy"][last_rarity]["price"]
                                elif skill_name == "Agility":
                                    price = ITEM_RARITY["agility"][last_rarity]["price"]
                                
                                # 检查商店分数是否足够
                                shop_score = get_total_score()
                                if shop_score >= price:
                                    # 扣除商店分数
                                    save_total_score_to_db(shop_score - price)
                                    # 显示扣除积分警告
                                    warning_message = f"Spent {price} points to unlock {skill_name}"
                                    warning_start_time = pygame.time.get_ticks()
                                    # 解锁技能
                                    save_unlocked_skill(skill_name, last_rarity)
                                    # 重新加载已解锁技能
                                    unlocked_skills = load_unlocked_skills()
                                    # 重新准备可选择的物品
                                    # 重新生成可用物品列表 - 使用新结构 (name, type, rarity)
                                    available_items = []
                                    for skill in skills_list:
                                        if skill in unlocked_skills and len(unlocked_skills[skill]) > 0:
                                            # 所有技能都使用嵌套字典结构
                                            for rarity in unlocked_skills[skill].keys():
                                                available_items.append((skill, "skill", rarity))
                                    # Frenzy 可能解锁了多个品质
                                    if "Frenzy" in unlocked_skills and len(unlocked_skills["Frenzy"]) > 0:
                                        for rarity in unlocked_skills["Frenzy"].keys():
                                            available_items.append(("Frenzy", "talent", rarity))
                                    # Agility 可能解锁了多个品质
                                    if "Agility" in unlocked_skills and len(unlocked_skills["Agility"]) > 0:
                                        for rarity in unlocked_skills["Agility"].keys():
                                            available_items.append(("Agility", "talent", rarity))
                                else:
                                    # 分数不足，显示警告
                                    warning_message = f"Not enough points! Need {price} points"
                                    warning_start_time = pygame.time.get_ticks()
                
                # 检查是否点击了可用的技能图标 - 横向排列
                available_y_offset = 220
                for i, (item, item_type, rarity) in enumerate(available_items):
                    # 横向排列坐标
                    item_x = margin + i * icon_spacing
                    item_y = available_y_offset + 45
                    
                    if item_x <= mouse_pos[0] <= item_x + icon_size and item_y <= mouse_pos[1] <= item_y + icon_size:
                        item_key = (item, item_type, rarity)
                        
                        if item_key in selected_items:
                            # 取消选择
                            selected_items.remove(item_key)
                            total_points += points_per_item
                        else:
                            # 检查是否已经选择了该技能/天赋的其他品质
                            existing_item = None
                            for selected_item, selected_item_type, selected_rarity in selected_items:
                                if selected_item == item:
                                    existing_item = (selected_item, selected_item_type, selected_rarity)
                                    break
                            
                            if existing_item:
                                # 已经选择了该技能/天赋的其他品质，显示警告
                                warning_message = f"You can only select one quality of {item}!"
                                warning_start_time = pygame.time.get_ticks()
                            else:
                                # 选择物品
                                if total_points >= points_per_item:
                                    selected_items.append(item_key)
                                    total_points -= points_per_item
                                else:
                                    # 点数不足，显示警告
                                    warning_message = "Not enough available points to select this item!"
                                    warning_start_time = pygame.time.get_ticks()

# 启动游戏
if __name__ == "__main__":
    main()
