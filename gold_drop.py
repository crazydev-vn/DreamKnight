import pygame
import math

class GoldDrop:
    PICKUP_RADIUS  = 60
    COLLECT_RADIUS = 15
    MAGNET_SPEED   = 5.0

    def __init__(self, x, y, value=10):
        self.x = float(x)
        self.y = float(y)
        self.value = value
        self.collected = False
        
        self.state = "falling"
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_duration = 50
        
        self.scale_falling = 2.0   # Scale cho gold01
        self.scale_collect = 3.0   # Scale cho gold02 (hiệu ứng nhặt)
        
        self.falling_frames = []
        self.collect_frames = []
        self._load_frames()
        
        self.current_sprite = self.falling_frames[0] if self.falling_frames else None
        
        self._bounce_vy = -3.0
        self._gravity = 0.3
        self._on_ground = False
        
        # THÊM: lưu vị trí player lúc nhặt để hiệu ứng bám
        self.target_player = None
        self.offset_x = 0
        self.offset_y = 0

    def _load_frames(self):
        for i in range(1, 11):
            img = pygame.image.load(f"assets/gold/gold01/gold{i}.png").convert_alpha()
            new_width = int(img.get_width() * self.scale_falling)
            new_height = int(img.get_height() * self.scale_falling)
            img = pygame.transform.scale(img, (new_width, new_height))
            self.falling_frames.append(img)
        
        for i in range(1, 6):
            img = pygame.image.load(f"assets/gold/gold02/gold_efect{i}.png").convert_alpha()
            new_width = int(img.get_width() * self.scale_collect)
            new_height = int(img.get_height() * self.scale_collect)
            img = pygame.transform.scale(img, (new_width, new_height))
            self.collect_frames.append(img)

    def _update_animation(self):
        if not self.current_sprite:
            return False
        current_time = pygame.time.get_ticks()
        if self.state == "falling":
            if current_time - self.frame_timer >= self.frame_duration:
                self.frame_timer = current_time
                self.current_frame = (self.current_frame + 1) % len(self.falling_frames)
                self.current_sprite = self.falling_frames[self.current_frame]
                self.offset_y += 50

        elif self.state == "collecting":
            if current_time - self.frame_timer >= self.frame_duration:
                self.frame_timer = current_time
                self.current_frame += 1
                if self.current_frame < len(self.collect_frames):
                    self.current_sprite = self.collect_frames[self.current_frame]
                else:
                    self.collected = True
                    return True
        return False

    def update(self, player):
        if self.collected:
            return
        if self._update_animation():
            return
        
        if self.state == "falling":
            if not self._on_ground:
                self._bounce_vy += self._gravity
                self.y += self._bounce_vy
                if self._bounce_vy >= 0 and self._bounce_vy < self._gravity * 2:
                    self._on_ground = True
                    self._bounce_vy = 0
            px = player.x + player.width // 2
            py = player.y + player.height // 2
            dist = math.hypot(self.x - px, self.y - py)
            if dist < self.PICKUP_RADIUS and dist > 0:
                ratio = self.MAGNET_SPEED / dist
                self.x += (px - self.x) * ratio
                self.y += (py - self.y) * ratio
            if dist < self.COLLECT_RADIUS:
                self.state = "collecting"
                self.current_frame = -1
                self.frame_timer = pygame.time.get_ticks()
                player.gold += self.value
                # LƯU VỊ TRÍ PLAYER LÚC NHẶT
                self.target_player = player
                self.offset_x = self.x - (player.x + player.width // 2)
                self.offset_y = self.y - (player.y + player.height // 2)
        
        elif self.state == "collecting" and self.target_player:
            # Bám theo player khi đang hiệu ứng nhặt
            px = self.target_player.x + self.target_player.width // 2
            py = self.target_player.y + self.target_player.height // 2
            self.x = px + self.offset_x
            self.y = py + self.offset_y

    def draw(self, screen, camera):
        if self.collected and self.state != "collecting":
            return
        if not self.current_sprite:
            return
        sx = int(self.x - camera.x - self.current_sprite.get_width() // 2)
        sy = int(self.y - camera.y - self.current_sprite.get_height() // 2)
        screen.blit(self.current_sprite, (sx, sy))