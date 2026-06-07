import pygame
import math

# ================================================================================================
# CLASS GoldDrop — Đồng vàng rơi ra khi quái chết
# ================================================================================================

class GoldDrop:
    PICKUP_RADIUS  = 60   # Khoảng cách bắt đầu hút vào player
    COLLECT_RADIUS = 15   # Khoảng cách để nhặt luôn
    MAGNET_SPEED   = 5.0  # Tốc độ hút về phía player

    def __init__(self, x, y, value=10):
        self.x      = float(x)
        self.y      = float(y)
        self.value  = value       # Số vàng nhận được khi nhặt
        self.collected = False    # Đã nhặt chưa

        # Hiệu ứng nảy nhỏ lúc mới rơi
        self._bounce_vy  = -3.0   # Vận tốc nảy ban đầu (đi lên)
        self._gravity    = 0.3
        self._on_ground  = False

        # Nhấp nháy
        self._birth_time = pygame.time.get_ticks()

        # Kích thước vẽ
        self.radius = 7

    # ------------------------------------------------------------------
    def update(self, player):
        """Gọi mỗi frame, truyền vào player để kiểm tra nhặt."""
        if self.collected:
            return

        # Hiệu ứng nảy
        if not self._on_ground:
            self._bounce_vy += self._gravity
            self.y += self._bounce_vy
            if self._bounce_vy >= 0 and self._bounce_vy < self._gravity * 2:
                self._on_ground = True
                self._bounce_vy = 0

        # Tọa độ tâm player
        px = player.x + player.width  // 2
        py = player.y + player.height // 2

        dist = math.hypot(self.x - px, self.y - py)

        # Hút về phía player khi đủ gần
        if dist < self.PICKUP_RADIUS and dist > 0:
            ratio    = self.MAGNET_SPEED / dist
            self.x  += (px - self.x) * ratio
            self.y  += (py - self.y) * ratio

        # Nhặt khi chạm
        if dist < self.COLLECT_RADIUS:
            self.collected = True
            player.gold   += self.value
            print(f"[Gold] Nhặt {self.value} vàng! Tổng: {player.gold}")

    # ------------------------------------------------------------------
    def draw(self, screen, camera):
        if self.collected:
            return

        sx = int(self.x - camera.x)
        sy = int(self.y - camera.y)

        # Nhấp nháy theo thời gian
        t     = (pygame.time.get_ticks() - self._birth_time) / 300.0
        alpha = int(180 + 75 * math.sin(t * math.pi * 2))

        # Tạo surface nhỏ để set alpha
        size = self.radius * 2 + 4
        surf = pygame.Surface((size, size), pygame.SRCALPHA)

        # Viền ngoài (nâu)
        pygame.draw.circle(surf, (180, 120, 0, alpha),
                           (size // 2, size // 2), self.radius + 1)
        # Thân vàng
        pygame.draw.circle(surf, (255, 210, 0, alpha),
                           (size // 2, size // 2), self.radius)
        # Điểm sáng nhỏ
        pygame.draw.circle(surf, (255, 245, 150, alpha),
                           (size // 2 - 2, size // 2 - 2), self.radius // 3)

        screen.blit(surf, (sx - size // 2, sy - size // 2))