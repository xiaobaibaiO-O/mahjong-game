import random
import pygame
import os
from typing import List, Dict, Set
from collections import defaultdict

# 初始化Pygame
pygame.init()

# 常量定义
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
TILE_WIDTH = 40
TILE_HEIGHT = 60
MARGIN = 5

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
GRAY = (128, 128, 128)

class Tile:
    """麻将牌类"""
    # 加载麻将牌图片
    IMAGES = {}
    
    @classmethod
    def load_images(cls):
        """加载所有麻将牌图片"""
        image_dir = "mahjong_tiles"  # 麻将牌图片目录
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
            print(f"请在 {image_dir} 目录下放入麻将牌图片（命名格式：1w.png, 2t.png等）")
            return
            
        loaded_count = 0  # 新增加载计数器
        for suit in ['w', 't', 'b']:
            for value in range(1, 10):
                image_path = os.path.join(image_dir, f"{value}{suit}.png")
                if os.path.exists(image_path):
                    cls.IMAGES[f"{value}{suit}"] = pygame.image.load(image_path)
                    cls.IMAGES[f"{value}{suit}"] = pygame.transform.scale(
                        cls.IMAGES[f"{value}{suit}"], 
                        (TILE_WIDTH, TILE_HEIGHT)
                    )
                    loaded_count += 1
                else:
                    print(f"缺少图片: {image_path}")  # 新增缺失文件提示
        
        print(f"成功加载 {loaded_count}/108 张麻将图片")  # 新增加载结果提示
    
    def __init__(self, suit: str, value: int):
        self.suit = suit    # 花色：万(w)、条(t)、筒(b)
        self.value = value  # 数值：1-9
        self.x = 0  # 新增当前位置
        self.y = 0
        self.target_x = 0  # 新增目标位置
        self.target_y = 0
        self.selected = False  # 新增选中状态
        self.anim_speed = 0.2  # 动画速度
        
    def __str__(self):
        return f"{self.value}{self.suit}"
    
    def __eq__(self, other):
        return self.suit == other.suit and self.value == other.value
    
    def get_image(self):
        """获取麻将牌图片"""
        key = f"{self.value}{self.suit}"
        if key not in self.IMAGES:
            # 创建临时表面作为默认牌面
            surf = pygame.Surface((TILE_WIDTH, TILE_HEIGHT))
            surf.fill(WHITE)
            pygame.draw.rect(surf, BLACK, (0, 0, TILE_WIDTH, TILE_HEIGHT), 2)
            font = pygame.font.Font(None, 24)
            text = font.render(str(self), True, BLACK)
            surf.blit(text, (10, 20))
            return surf
        return self.IMAGES.get(key, None)

class Player:
    """玩家类"""
    def __init__(self, name: str, is_bot: bool = True, position: str = "bottom"):
        self.name = name
        self.is_bot = is_bot
        self.position = position  # 玩家位置：bottom, top, left, right
        self.hand: List[Tile] = []
        self.shown_melds: List[List[Tile]] = []
        self.discarded: List[Tile] = []
        self.score = 0
        self.waiting = False  # 是否处于听牌状态
        self.can_peng_now = False  # 新增碰牌状态

    def arrange_hand(self):
        """整理手牌"""
        self.hand.sort(key=lambda x: (x.suit, x.value))

    def can_peng(self, tile: Tile) -> bool:
        """判断是否可以碰牌"""
        count = sum(1 for t in self.hand if t.suit == tile.suit and t.value == tile.value)
        return count >= 2

    def calculate_score(self, is_self_drawn: bool = False) -> int:
        """计算胡牌分数"""
        score = 1  # 基础分
        
        if is_self_drawn:
            score += 1
            
        # 检查清一色
        all_tiles = self.hand + [tile for meld in self.shown_melds for tile in meld]
        if all(tile.suit == all_tiles[0].suit for tile in all_tiles):
            score += 1
            
        # 检查碰碰胡
        if not any(self._is_sequence(meld) for meld in self._get_all_melds()):
            score += 1
            
        return score

    def _is_sequence(self, meld: List[Tile]) -> bool:
        """判断是否为顺子"""
        if len(meld) != 3:
            return False
        sorted_meld = sorted(meld, key=lambda x: x.value)
        return (all(t.suit == sorted_meld[0].suit for t in sorted_meld) and
                sorted_meld[0].value + 1 == sorted_meld[1].value and
                sorted_meld[1].value + 1 == sorted_meld[2].value)
    
    def _get_all_melds(self) -> List[List[Tile]]:
        """获取所有的面子（包括手牌中的）"""
        melds = self.shown_melds.copy()
        # 这里需要复杂的算法来识别手牌中的面子，简化处理
        return melds

    def can_hu(self) -> bool:
        """判断是否可以胡牌"""
        tile_count = defaultdict(int)
        for tile in self.hand:
            tile_count[f"{tile.value}{tile.suit}"] += 1
            
        pairs = [k for k, v in tile_count.items() if v >= 2]
        for pair in pairs:
            temp_count = tile_count.copy()
            temp_count[pair] -= 2
            
            if self._check_remaining_tiles(temp_count):
                return True
        return False
    
    def _check_remaining_tiles(self, tile_count: Dict) -> bool:
        """检查剩余牌是否可以组成顺子或刻子"""
        if not any(tile_count.values()):
            return True
                
        for tile_name, count in tile_count.items():
            if count == 0:
                continue
                
            # 修复解析牌面值的问题
            suit = tile_name[-1]  # 取最后一个字符作为花色
            value = int(tile_name[:-1])  # 取除最后一个字符外的所有字符作为数值
                
            # 尝试组成刻子
            if count >= 3:
                tile_count[tile_name] -= 3
                if self._check_remaining_tiles(tile_count):
                    return True
                tile_count[tile_name] += 3
                    
            # 尝试组成顺子
            if suit in 'wtb' and value <= 7:
                next_tile = f"{value+1}{suit}"
                next_next_tile = f"{value+2}{suit}"
                if (tile_count.get(next_tile, 0) > 0 and 
                    tile_count.get(next_next_tile, 0) > 0):
                    tile_count[tile_name] -= 1
                    tile_count[next_tile] -= 1
                    tile_count[next_next_tile] -= 1
                    if self._check_remaining_tiles(tile_count):
                        return True
                    tile_count[tile_name] += 1
                    tile_count[next_tile] += 1
                    tile_count[next_next_tile] += 1
                
            break
        return False

class SichuanMahjong:
    def __init__(self):
        self.screen = pygame.display.set_mode((1024, 768), pygame.RESIZABLE)
        self.actual_width = 1024
        self.actual_height = 768
        self.base_tile_width = 40
        self.base_tile_height = 60
        self.margin = 3  # 更紧凑的间距
        pygame.display.set_caption("四川麻将")
        
        self.players = [
            Player("玩家", is_bot=False, position="bottom"),
            Player("电脑1", position="right"),
            Player("电脑2", position="top"),
            Player("电脑3", position="left")
        ]
        self.tiles = []
        self.current_player = 0
        self.last_discarded = None
        self.round = 1
        self.max_rounds = 8
        self.show_peng_button = False  # 新增碰牌按钮状态
        self.peng_button_rect = pygame.Rect(0, 0, 100, 50)  # 碰牌按钮位置
        self.confirm_button_rect = pygame.Rect(0, 0, 0, 0)  # 初始化为空矩形
        
        # 加载麻将牌图片
        Tile.load_images()

    def initialize_game(self):
        """初始化游戏"""
        self.tiles = []
        # 生成所有牌
        suits = ['w', 't', 'b']  # 万、条、筒
        for suit in suits:
            for value in range(1, 10):
                for _ in range(4):
                    self.tiles.append(Tile(suit, value))
        
        random.shuffle(self.tiles)
        
        # 清空玩家手牌和明牌
        for player in self.players:
            player.hand = []
            player.shown_melds = []
            player.discarded = []
        
        # 发牌
        for _ in range(13):
            for player in self.players:
                player.hand.append(self.tiles.pop())
                
        for player in self.players:
            player.arrange_hand()

    def bot_action(self, player: Player) -> Tile:
        """机器人行为"""
        # 简单的策略：丢弃最后一张牌
        discard_tile = player.hand[-1]
        player.hand.remove(discard_tile)
        return discard_tile

    def _handle_peng(self, player: Player, tile: Tile):
        """处理碰牌"""
        print(f"{player.name}碰牌")
        matching_tiles = [t for t in player.hand 
                         if t.suit == tile.suit and t.value == tile.value][:2]
        for t in matching_tiles:
            player.hand.remove(t)
        player.shown_melds.append(matching_tiles + [tile])
        self.current_player = self.players.index(player)

    def _process_discard(self, player: Player):
        """处理出牌逻辑"""
        # 获取选中的牌
        selected_tiles = [t for t in player.hand if t.selected]
        if not selected_tiles:
            return
            
        discard_tile = selected_tiles[0]
        player.hand.remove(discard_tile)
        self.last_discarded = discard_tile
        player.discarded.append(discard_tile)
        
        # 清除选中状态
        for t in player.hand:
            t.selected = False
            
        # 切换到下家
        self.current_player = (self.current_player + 1) % 4
        print(f"{player.name}打出了 {discard_tile}")

    def draw_game(self):
        """绘制游戏界面"""
        # 渐变背景
        self.screen.fill((34, 139, 34))  # 深绿色背景
        # 添加木质纹理
        wood_texture = pygame.Surface((self.actual_width, self.actual_height))
        wood_texture.set_alpha(50)
        wood_texture.fill((139, 69, 19))  # 棕色纹理
        self.screen.blit(wood_texture, (0,0))
        
        # 添加牌桌装饰
        pygame.draw.rect(self.screen, (139, 69, 19), 
                        (0, self.actual_height//3, 
                         self.actual_width, self.actual_height//3))
        
        # 绘制所有玩家的牌
        for player in self.players:
            self.draw_player_hand(player, hidden=player.is_bot)
        
        # 绘制弃牌区
        self.draw_discarded_tiles()
        
        # 绘制当前玩家提示
        font = pygame.font.Font(None, 36)
        text = font.render(f"当前玩家: {self.players[self.current_player].name}", True, BLACK)
        self.screen.blit(text, (10, 10))
        
        # 绘制碰牌按钮（如果显示）
        if self.show_peng_button:
            pygame.draw.rect(self.screen, (0, 200, 0), self.peng_button_rect)
            text = font.render("碰", True, WHITE)
            self.screen.blit(text, (self.peng_button_rect.x + 30, self.peng_button_rect.y + 10))
        
        # 绘制确认出牌按钮
        if any(t.selected for t in self.players[0].hand):
            btn_width = 120
            btn_height = 50
            self.confirm_button_rect = pygame.Rect(
                self.actual_width - btn_width - 20, 
                self.actual_height - btn_height - 20,  # 增加底部间距
                btn_width, btn_height
            )
            pygame.draw.rect(self.screen, (200, 0, 0), self.confirm_button_rect)
            font = pygame.font.Font(None, 36)
            text = font.render("出牌", True, WHITE)
            self.screen.blit(text, (self.confirm_button_rect.x + 30, 
                                   self.confirm_button_rect.y + 10))
        
        pygame.display.flip()
        
    def draw_player_hand(self, player: Player, hidden: bool = False):
        """动态计算布局"""
        hand_length = len(player.hand)
        if hand_length == 0:
            return

        # 根据窗口大小计算缩放比例
        scale = min(self.actual_width/1024, self.actual_height/768)
        tile_width = int(self.base_tile_width * scale)
        tile_height = int(self.base_tile_height * scale)
        margin = int(self.margin * scale)

        if player.position == "bottom":
            total_width = hand_length * (tile_width + margin)
            start_x = (self.actual_width - total_width) // 2
            y = self.actual_height - tile_height - margin*2
            
            for i, tile in enumerate(player.hand):
                tile.target_x = start_x + i * (tile_width + margin)
                tile.target_y = y - 20 if tile.selected else y
                self._draw_tile(tile, tile.x, tile.y, hidden, tile_width, tile_height)

        elif player.position == "top":
            x = (self.actual_width - (hand_length * (tile_width + margin))) // 2
            y = self.margin
            for tile in player.hand:
                img = pygame.transform.rotate(tile.get_image(), 180) if not hidden else None
                self._draw_tile(tile, x, y, hidden, tile_width, tile_height, rotated=True)
                x += tile_width + margin
                
        elif player.position == "left":
            x = self.margin
            y = (self.actual_height - (hand_length * (tile_height + margin))) // 2
            for tile in player.hand:
                img = pygame.transform.rotate(tile.get_image(), 90) if not hidden else None
                self._draw_tile(tile, x, y, hidden, tile_width, tile_height, vertical=True)
                y += tile_height + margin
                
        elif player.position == "right":
            x = self.actual_width - tile_width - margin
            y = (self.actual_height - (hand_length * (tile_height + margin))) // 2
            for tile in player.hand:
                img = pygame.transform.rotate(tile.get_image(), -90) if not hidden else None
                self._draw_tile(tile, x, y, hidden, tile_width, tile_height, vertical=True)
                y += tile_height + margin

    def _draw_tile(self, tile, x, y, hidden, tile_width, tile_height, rotated=False, vertical=False):
        """通用牌面绘制方法"""
        try:
            if not hidden:
                img = tile.get_image()
                if rotated:
                    img = pygame.transform.rotate(img, 180)
                if vertical:
                    img = pygame.transform.rotate(img, 90)
                self.screen.blit(img, (x, y))
            else:
                # 修复变量名错误
                if vertical:
                    # 垂直方向时交换宽高
                    pygame.draw.rect(self.screen, GRAY, (x, y, tile_height, tile_width))
                else:
                    pygame.draw.rect(self.screen, GRAY, (x, y, tile_width, tile_height))
        except Exception as e:
            print(f"绘制牌{tile}时出错: {str(e)}")

    def draw_discarded_tiles(self):
        """绘制弃牌区"""
        # 在界面中央绘制一个区域显示打出的牌
        center_x = self.actual_width // 2
        center_y = self.actual_height // 2
        
        if self.last_discarded:
            if self.last_discarded.get_image():
                self.screen.blit(self.last_discarded.get_image(), 
                               (center_x - self.base_tile_width//2, center_y - self.base_tile_height//2))
            else:
                pygame.draw.rect(self.screen, WHITE,
                               (center_x - self.base_tile_width//2, center_y - self.base_tile_height//2,
                                self.base_tile_width, self.base_tile_height))
                font = pygame.font.Font(None, 24)
                text = font.render(str(self.last_discarded), True, BLACK)
                self.screen.blit(text, (center_x - 10, center_y - 10))
    
    def handle_player_click(self, pos):
        current = self.players[self.current_player]
        if current.is_bot:
            return

        # 检查手牌点击
        selected_tile = None
        for tile in current.hand:
            tile_rect = pygame.Rect(tile.x, tile.y, 
                                  self.base_tile_width, self.base_tile_height)
            if tile_rect.collidepoint(pos):
                selected_tile = tile
                break

        if selected_tile:
            # 切换选中状态
            selected_tile.selected = not selected_tile.selected
            # 取消其他牌的选中
            for t in current.hand:
                if t != selected_tile:
                    t.selected = False
        else:
            # 检查确认出牌按钮
            if self.confirm_button_rect.collidepoint(pos):
                self._process_discard(current)

    def update_game(self):
        """更新游戏状态"""
        current = self.players[self.current_player]
        
        # 检查碰牌机会
        if not current.is_bot and self.last_discarded:
            current.can_peng_now = current.can_peng(self.last_discarded)
            self.show_peng_button = current.can_peng_now
            self.peng_button_rect = pygame.Rect(
                self.actual_width - 120, self.actual_height - 70, 100, 50
            )
        
        if current.is_bot:
            # AI行为
            pygame.time.wait(1000)  # 等待一秒
            discarded = self.bot_action(current)
            self.last_discarded = discarded
            current.discarded.append(discarded)
            self.current_player = (self.current_player + 1) % 4

    def play_game(self):
        """开始游戏"""
        self.initialize_game()
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 处理鼠标点击事件
                    if not self.players[self.current_player].is_bot:
                        self.handle_player_click(event.pos)
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event)
            
            # 更新游戏状态
            self.update_game()
            
            # 绘制游戏界面
            self.draw_game()
            
            clock.tick(30)
        
        pygame.quit()

    def handle_resize(self, event):
        self.actual_width = event.w
        self.actual_height = event.h
        self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    def update_animations(self):
        """更新所有动画效果"""
        for player in self.players:
            for tile in player.hand:
                # 位置插值
                dx = tile.target_x - tile.x
                dy = tile.target_y - tile.y
                tile.x += dx * tile.anim_speed
                tile.y += dy * tile.anim_speed
                
                # 选中状态偏移
                if tile.selected:
                    tile.target_y -= 20  # 选中时上浮
                else:
                    tile.target_y = tile.y

# 开始游戏
if __name__ == "__main__":
    game = SichuanMahjong()
    game.play_game()
    