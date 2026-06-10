from test01 import Test01

from plant1 import Plant1

from slime1 import Slime1
from slime2 import Slime2
from slime3 import Slime3

from gold_drop import GoldDrop

#================================================================================================
# Vai trò: Quản lý toàn bộ quái vật trong game.
# Bao gồm: khởi tạo quái, cập nhật, vẽ, va chạm, xóa quái chết, rơi vàng.
# Tách khỏi game.py để dễ chỉnh vị trí spawn và thêm/bớt loại quái.
#================================================================================================

# ============================================================
#  CẤU HÌNH VỊ TRÍ SPAWN - CHỈNH Ở ĐÂY ĐỂ THÊM/BỚT QUÁI
# ============================================================

TEST01_POSITIONS = [
    #(x, y)
    #(730, 700), (760, 620), (800, 600),
    #(100, 200),
    #(1800, 600),
]

PLANT1_POSITIONS = [
    #(x, y)
    #(730, 700),
    #(800, 1000),
]

SLIME1_POSITIONS = [
    # (x, y)
    #(730, 700), (760, 620), (800, 600),
    #(700, 600),
    #(800, 1000),
    #(100, 200),
    #(1800, 600),
]
SLIME2_POSITIONS = [
    # (x, y)
    # (730, 700), (760, 620), (800, 600),
    # (700, 600),
    # (800, 1000),
]
SLIME3_POSITIONS = [
    # (x, y)
    (730, 700), (760, 620), (800, 600),
    (700, 600),
    (800, 1000),
]

# Giá trị vàng khi quái chết
GOLD_VALUES = {
    "test01": 10,
    "plant1": 8,
    "slime1": 5,
    "slime2": 7,
    "slime3": 7,
}

# Scale mặc định cho tất cả quái
DEFAULT_SCALE = 2.0

# ============================================================


class EnemyManager:
    def __init__(self, player):
        self.player = player
        self.gold_drops = []

        self.test01  = self._spawn(Test01,  TEST01_POSITIONS)
        self.plant1  = self._spawn(Plant1,  PLANT1_POSITIONS)
        self.slime1  = self._spawn(Slime1,  SLIME1_POSITIONS)
        self.slime2  = self._spawn(Slime2,  SLIME2_POSITIONS)
        self.slime3  = self._spawn(Slime3,  SLIME3_POSITIONS)

        self._sync_enemies()

    # ------------------------------------------------------------------
    # Khởi tạo
    # ------------------------------------------------------------------

    def _spawn(self, cls, positions):
        enemies = []
        for x, y in positions:
            e = cls(x, y, scale_factor=DEFAULT_SCALE)
            e.set_player(self.player)
            enemies.append(e)
        return enemies

    def _sync_enemies(self):
        """Đồng bộ danh sách enemy cho player để player biết mục tiêu."""
        all_enemies = self.test01 + self.plant1 + self.slime1 + self.slime2 + self.slime3
        self.player.set_enemies(all_enemies)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt, map_width, map_height):
        for e in self.test01:
            e.update(dt, map_width, map_height)
        for e in self.plant1:
            e.update(dt, map_width, map_height)
        for e in self.slime1:
            e.update(dt, map_width, map_height)
        for e in self.slime2:
            e.update(dt, map_width, map_height)
        for e in self.slime3:
            e.update(dt, map_width, map_height)

        self._check_plant1_collisions()
        self._check_enemy_collisions()
        self._remove_dead()

        # Cập nhật vàng rơi
        self.gold_drops = [g for g in self.gold_drops if not g.collected]
        for gold in self.gold_drops:
            gold.update(self.player)

    # ------------------------------------------------------------------
    # Va chạm
    # ------------------------------------------------------------------

    def _check_plant1_collisions(self):
        attack_hitbox = self.player.get_attack_hitbox()
        if not attack_hitbox:
            return
        for plant1 in self.plant1:
            if plant1.is_dead:
                continue
            cx, cy, radius = plant1.get_hitbox()
            closest_x = max(attack_hitbox.left, min(cx, attack_hitbox.right))
            closest_y = max(attack_hitbox.top,  min(cy, attack_hitbox.bottom))
            dx = closest_x - cx
            dy = closest_y - cy
            if dx*dx + dy*dy < radius * radius:
                plant1.take_damage(self.player.damage)
                print(f"Plant1 bị tấn công! Máu còn: {plant1.health}")

    def _check_enemy_collisions(self):
        attack_hitbox = self.player.get_attack_hitbox()
        if not attack_hitbox:
            return
        for enemy_list in [self.test01, self.slime1, self.slime2, self.slime3]:
            for enemy in enemy_list:
                if enemy.is_dead:
                    continue
                cx, cy, radius = enemy.get_hitbox()
                closest_x = max(attack_hitbox.left, min(cx, attack_hitbox.right))
                closest_y = max(attack_hitbox.top,  min(cy, attack_hitbox.bottom))
                dx = closest_x - cx
                dy = closest_y - cy
                if dx*dx + dy*dy < radius * radius:
                    enemy.take_damage(self.player.damage)

    # ------------------------------------------------------------------
    # Xóa quái chết & rơi vàng
    # ------------------------------------------------------------------

    def _remove_list(self, enemy_list, gold_value):
        alive = []
        for e in enemy_list:
            if e.fully_dead:
                cx = e.x + e.width  // 2
                cy = e.y + e.height // 2
                self.gold_drops.append(GoldDrop(cx, cy, value=gold_value))
            else:
                alive.append(e)
        return alive, len(alive) != len(enemy_list)

    def _remove_dead(self):
        changed = False

        self.test01,  c = self._remove_list(self.test01,  GOLD_VALUES["test01"])
        changed |= c

        self.plant1,  c = self._remove_list(self.plant1,  GOLD_VALUES["plant1"])
        changed |= c

        self.slime1,  c = self._remove_list(self.slime1,  GOLD_VALUES["slime1"])
        changed |= c

        self.slime2,  c = self._remove_list(self.slime2,  GOLD_VALUES["slime2"])
        changed |= c

        self.slime3,  c = self._remove_list(self.slime3,  GOLD_VALUES["slime3"])
        changed |= c

        if changed:
            self._sync_enemies()

    # ------------------------------------------------------------------
    # Vẽ
    # ------------------------------------------------------------------

    def draw(self, surface, camera):
        for e in self.test01:
            e.draw(surface, camera)
        for e in self.plant1:
            e.draw(surface, camera)

        for e in self.slime1:
            e.draw(surface, camera)
        for e in self.slime2:
            e.draw(surface, camera)
        for e in self.slime3:
            e.draw(surface, camera)

        for gold in self.gold_drops:
            gold.draw(surface, camera)