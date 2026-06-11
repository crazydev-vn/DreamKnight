import math
import random

from test01 import Test01
from plant1 import Plant1
from plant2 import Plant2
from plant3 import Plant3
from slime1 import Slime1
from slime2 import Slime2
from slime3 import Slime3
from gold_drop import GoldDrop
from config import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT

# ============================================================
#  CẤU HÌNH WAVE SYSTEM
# ============================================================

# Thứ tự các đợt quái — chỉnh ở đây để thay đổi thứ tự
WAVE_ORDER = [
    "slime1",
    "slime2",
    "slime3",
    "plant1",
    "plant2",
    "plant3",
]

ENEMIES_PER_WAVE = 30       # số con mỗi đợt — chỉnh số này
SPAWN_INTERVAL   = 2        # giây giữa mỗi lần spawn 1 con
SPAWN_OFFSET     = 80       # px ngoài rìa camera — quái spawn ngoài tầm nhìn

# Giá trị vàng khi quái chết
GOLD_VALUES = {
    "slime1": 5,  "slime2": 7,  "slime3": 9,
    "plant1": 8,  "plant2": 10, "plant3": 12,
}


ENEMY_CLASSES = {
    "slime1": Slime1, "slime2": Slime2, "slime3": Slime3,
    "plant1": Plant1, "plant2": Plant2, "plant3": Plant3,
}

# Scale mặc định cho tất cả quái
DEFAULT_SCALE = 2.0



class EnemyManager:
    def __init__(self, player):
        self.player     = player
        self.gold_drops = []

        # Danh sách quái đang sống trên màn hình
        self.enemies    = []

        # Đợt hiện tại (0 = slime1, 1 = slime2, ...)
        self.current_wave       = 0
        self.wave_name_current  = ""
        self.remaining_to_spawn = 0  # số con còn phải spawn trong đợt này
        self.spawn_timer        = 0.0

        # Spawn đợt đầu tiên ngay khi khởi tạo
        self._spawn_wave(self.current_wave)

    # ------------------------------------------------------------------
    # Chuẩn bị đợt mới — chưa spawn ngay, spawn từ từ qua update
    # ------------------------------------------------------------------

    def _spawn_wave(self, wave_index):
        wave_name = WAVE_ORDER[wave_index]
        print(f"[Wave {wave_index + 1}] Bắt đầu đợt: {wave_name} x{ENEMIES_PER_WAVE}")

        self.wave_name_current  = wave_name
        self.remaining_to_spawn = ENEMIES_PER_WAVE
        self.spawn_timer        = 0.0

    # ------------------------------------------------------------------
    # Spawn 1 con ở rìa ngoài camera của player
    # ------------------------------------------------------------------

    def _spawn_one_enemy(self):
        cls = ENEMY_CLASSES[self.wave_name_current]

        # Tính góc trên trái của camera dựa theo vị trí player
        cam_x = self.player.x - SCREEN_WIDTH  // 2
        cam_y = self.player.y - SCREEN_HEIGHT // 2

        # Chọn ngẫu nhiên 1 trong 4 rìa: top, bottom, left, right
        side = random.choice(["top", "bottom", "left", "right"])

        if side == "top":
            x = random.uniform(cam_x - SPAWN_OFFSET, cam_x + SCREEN_WIDTH + SPAWN_OFFSET)
            y = cam_y - SPAWN_OFFSET
        elif side == "bottom":
            x = random.uniform(cam_x - SPAWN_OFFSET, cam_x + SCREEN_WIDTH + SPAWN_OFFSET)
            y = cam_y + SCREEN_HEIGHT + SPAWN_OFFSET
        elif side == "left":
            x = cam_x - SPAWN_OFFSET
            y = random.uniform(cam_y - SPAWN_OFFSET, cam_y + SCREEN_HEIGHT + SPAWN_OFFSET)
        else:  # right
            x = cam_x + SCREEN_WIDTH  + SPAWN_OFFSET
            y = random.uniform(cam_y - SPAWN_OFFSET, cam_y + SCREEN_HEIGHT + SPAWN_OFFSET)

        # Giữ trong giới hạn map, không spawn quá sát rìa
        MARGIN = 200
        x = max(MARGIN, min(x, MAP_WIDTH  - MARGIN))
        y = max(MARGIN, min(y, MAP_HEIGHT - MARGIN))

        e = cls(x, y, scale_factor=DEFAULT_SCALE)
        e.set_player(self.player)
        self.enemies.append(e)
        self._sync_enemies()

    # ------------------------------------------------------------------
    # Đồng bộ danh sách enemy cho player
    # ------------------------------------------------------------------

    def _sync_enemies(self):
        self.player.set_enemies(self.enemies)

    # ------------------------------------------------------------------
    # Update mỗi frame
    # ------------------------------------------------------------------

    def update(self, dt, map_width, map_height):
        # Spawn từng con theo thời gian
        if self.remaining_to_spawn > 0:
            self.spawn_timer += dt
            if self.spawn_timer >= SPAWN_INTERVAL:
                self.spawn_timer -= SPAWN_INTERVAL
                self._spawn_one_enemy()
                self.remaining_to_spawn -= 1

        # Cập nhật tất cả quái còn sống
        for e in self.enemies:
            e.update(dt, map_width, map_height)

        self._check_enemy_collisions()
        self._remove_dead()

        # Hết spawn VÀ hết quái trên màn → sang đợt tiếp
        if self.remaining_to_spawn == 0 and len(self.enemies) == 0:
            next_wave = self.current_wave + 1
            if next_wave < len(WAVE_ORDER):
                self.current_wave = next_wave
                self._spawn_wave(self.current_wave)
            else:
                # Hết tất cả đợt — có thể thêm logic win ở đây sau
                print("[Wave] Đã hoàn thành tất cả các đợt!")

        # Cập nhật vàng rơi
        self.gold_drops = [g for g in self.gold_drops if not g.collected]
        for gold in self.gold_drops:
            gold.update(self.player)

    # ------------------------------------------------------------------
    # Va chạm tấn công của player
    # ------------------------------------------------------------------

    def _check_enemy_collisions(self):
        attack_hitbox = self.player.get_attack_hitbox()
        if not attack_hitbox:
            return
        for enemy in self.enemies:
            if enemy.is_dead:
                continue
            cx, cy, radius = enemy.get_hitbox()
            closest_x = max(attack_hitbox.left,  min(cx, attack_hitbox.right))
            closest_y = max(attack_hitbox.top,   min(cy, attack_hitbox.bottom))
            dx = closest_x - cx
            dy = closest_y - cy
            if dx * dx + dy * dy < radius * radius:
                enemy.take_damage(self.player.damage)

    # ------------------------------------------------------------------
    # Xóa quái chết và rơi vàng
    # ------------------------------------------------------------------

    def _remove_dead(self):
        alive   = []
        changed = False
        for e in self.enemies:
            if e.fully_dead:
                # Rơi vàng tại vị trí quái chết
                gold_value = self._get_gold_value(e)
                cx = e.x + e.width  // 2
                cy = e.y + e.height // 2
                self.gold_drops.append(GoldDrop(cx, cy, value=gold_value))
                changed = True
            else:
                alive.append(e)
        if changed:
            self.enemies = alive
            self._sync_enemies()

    def _get_gold_value(self, enemy):
        """Trả về giá trị vàng dựa theo class của quái."""
        class_to_name = {v: k for k, v in ENEMY_CLASSES.items()}
        name = class_to_name.get(type(enemy), "slime1")
        return GOLD_VALUES.get(name, 5)

    # ------------------------------------------------------------------
    # Thuộc tính tiện ích (để game.py hoặc UI đọc nếu cần)
    # ------------------------------------------------------------------

    @property
    def wave_number(self):
        """Số đợt hiện tại (bắt đầu từ 1)."""
        return self.current_wave + 1

    @property
    def wave_name(self):
        """Tên loại quái đang spawn trong đợt này."""
        return WAVE_ORDER[self.current_wave]

    # ------------------------------------------------------------------
    # Vẽ
    # ------------------------------------------------------------------

    def draw(self, surface, camera):
        for e in self.enemies:
            e.draw(surface, camera)
        for gold in self.gold_drops:
            gold.draw(surface, camera)