# plant3.py
import pygame
import os
import math
from config import PLAYER_SPEED
from plant3_animation import Plant3AnimationLoader

# ================================================================================================
# CLASS PLANT3 — Kẻ địch Plant 3 (đứng yên, mạnh nhất)
# ================================================================================================

class Plant3(pygame.sprite.Sprite):

    def __init__(self, x, y, scale_factor=2.0):
        super().__init__()

        self.x = float(x)
        self.y = float(y)
        self.home_x = float(x)
        self.home_y = float(y)

        all_anims = Plant3AnimationLoader.load_all(scale_factor)
        self.idle_anims   = all_anims["idle"]
        self.attack_anims = all_anims["attack"]
        self.hit_anims    = all_anims["hit"]
        self.death_anims  = all_anims["death"]

        self.direction = "down"
        self.state = "idle"
        self.is_attacking = False

        self.speed = 0.0
        self.dx = 0.0
        self.dy = 0.0

        self.attack_range    = 60
        self.attack_duration = 700

        self.attack_start_time  = 0
        self.attack_sound_index = 0

        self.health = 500
        self.contact_damage = 15
        self.max_health = 500

        self.hit_start_time = 0
        self.hit_duration = 300
        self.death_start_time = 0
        self.death_frame_duration = 85
        self.death_frames_count = 6
        self.death_duration = self.death_frame_duration * self.death_frames_count

        self.is_dead = False
        self.fully_dead = False
        self.is_invincible = False
        self.invincible_duration = 500
        self.invincible_start_time = 0

        self.player = None

        start_frame = self.idle_anims["down"].current_frame
        self.image = start_frame
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.body_radius = 30

        self.debug = False

        self.attack_sounds = []
        self.hit_sound = None
        self.death_sound = None
        self._load_sounds()

    def _load_sounds(self):
        sound_path = os.path.join("03_sounds", "plant3")
        try:
            for i in range(1, 3):
                path = os.path.join(sound_path, f"Attack{i}.mp3")
                if os.path.exists(path):
                    self.attack_sounds.append(pygame.mixer.Sound(path))
            hit_path = os.path.join(sound_path, "hit.mp3")
            if os.path.exists(hit_path):
                self.hit_sound = pygame.mixer.Sound(hit_path)
            death_path = os.path.join(sound_path, "Death.mp3")
            if os.path.exists(death_path):
                self.death_sound = pygame.mixer.Sound(death_path)
        except Exception as e:
            print(f"[Plant3] Lỗi load âm thanh: {e}")

    def set_player(self, player):
        self.player = player

    def take_damage(self, damage) -> bool:
        if self.is_dead or self.is_invincible:
            return False

        self.health -= damage
        print(f"[Plant3] Nhận {damage} sát thương! Máu còn: {self.health}/{self.max_health}")

        if self.health <= 0:
            self.health = 0
            self.die()
        else:
            self._start_hit()

        return True

    def die(self):
        if self.is_dead:
            return
        self.is_dead = True
        self.state = "death"
        self.death_start_time = pygame.time.get_ticks()
        self.dx = self.dy = 0
        self.is_attacking = False
        if self.death_sound:
            self.death_sound.play()
        if self.direction in self.death_anims:
            self.death_anims[self.direction].reset()

    def get_hitbox(self):
        return (self.rect.centerx, self.rect.centery, self.body_radius)

    def update(self, delta_time, map_width, map_height):
        if self.player is None:
            return

        current_time = pygame.time.get_ticks()
        self._update_invincible(current_time)

        if self.state == "death":
            self._update_animation(delta_time)
            if current_time - self.death_start_time >= self.death_duration:
                self.fully_dead = True
            return

        if self.state == "hit":
            if current_time - self.hit_start_time >= self.hit_duration:
                self.state = "idle"
            else:
                self._update_animation(delta_time)
                return

        if self.state == "attack":
            if current_time - self.attack_start_time >= self.attack_duration:
                self._end_attack()
            else:
                self._update_animation(delta_time)
                return

        if self.player and not self.player.is_dead:
            px, py = self._player_center()
            slime_cx = self.x + self.width // 2
            slime_cy = self.y + self.height // 2
            dist_to_player = math.hypot(slime_cx - px, slime_cy - py)

            self._update_direction(px, py)

            if dist_to_player <= self.attack_range and self.state != "attack":
                self._start_attack(current_time)
                return

        self.dx = self.dy = 0
        self._update_animation(delta_time)

    def _player_center(self):
        return (
            self.player.x + self.player.width // 2,
            self.player.y + self.player.height // 2,
        )

    def _update_direction(self, px, py):
        angle = math.atan2(py - (self.y + self.height // 2),
                           px - (self.x + self.width // 2))
        if abs(angle) < math.pi / 4:
            self.direction = "right"
        elif abs(angle - math.pi) < math.pi / 4 or abs(angle + math.pi) < math.pi / 4:
            self.direction = "left"
        elif math.pi / 4 <= angle <= 3 * math.pi / 4:
            self.direction = "down"
        else:
            self.direction = "up"

    def _start_hit(self):
        self.state = "hit"
        self.hit_start_time = pygame.time.get_ticks()
        self.dx = self.dy = 0
        self.is_invincible = True
        self.invincible_start_time = self.hit_start_time
        if self.hit_sound:
            self.hit_sound.play()
        if self.direction in self.hit_anims:
            self.hit_anims[self.direction].reset()

    def _start_attack(self, current_time):
        self.state = "attack"
        self.is_attacking = True
        self.attack_start_time = current_time
        if self.direction in self.attack_anims:
            self.attack_anims[self.direction].reset()
        if self.attack_sounds:
            self.attack_sounds[self.attack_sound_index].play()
            self.attack_sound_index = (self.attack_sound_index + 1) % len(self.attack_sounds)
        print(f"[Plant3] Bắt đầu tấn công")

    def _end_attack(self):
        self.state = "idle"
        self.is_attacking = False
        if self.direction in self.attack_anims:
            self.attack_anims[self.direction].reset()
        if self.player and not self.player.is_dead:
            slime_cx = self.x + self.width // 2
            slime_cy = self.y + self.height // 2
            px = self.player.x + self.player.width // 2
            py = self.player.y + self.player.height // 2
            if math.hypot(slime_cx - px, slime_cy - py) <= self.attack_range * 1.3:
                self.player.take_damage(15)

    def _update_invincible(self, current_time):
        if self.is_invincible:
            if current_time - self.invincible_start_time >= self.invincible_duration:
                self.is_invincible = False

    def _update_animation(self, delta_time):
        anim_map = {
            "idle": self.idle_anims,
            "attack": self.attack_anims,
            "hit": self.hit_anims,
            "death": self.death_anims,
        }
        anim_dict = anim_map.get(self.state, self.idle_anims)
        anim = anim_dict.get(self.direction) \
               or anim_dict.get("down") \
               or (next(iter(anim_dict.values())) if anim_dict else None)

        if not anim:
            return

        anim.update()
        self.image = anim.current_frame

        if self.is_invincible and not self.is_dead:
            alpha = 128 + int(127 * math.sin(pygame.time.get_ticks() * 0.015))
            self.image.set_alpha(max(128, alpha))
        else:
            self.image.set_alpha(255)

        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        screen.blit(self.image, (screen_x, screen_y))

        if not self.debug:
            return

        cx = int(self.x + self.width // 2 - camera.x)
        cy = int(self.y + self.height // 2 - camera.y)

        bar_w, bar_h = 40, 6
        bar_x = int(screen_x + (self.width - bar_w) // 2)
        bar_y = int(screen_y - 15)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(screen, (0, 255, 0),
                         (bar_x, bar_y, int(bar_w * self.health / self.max_health), bar_h))

        pygame.draw.circle(screen, (0, 255, 0), (cx, cy), self.body_radius, 2)
        pygame.draw.circle(screen, (255, 165, 0), (cx, cy), self.attack_range, 2)

        font = pygame.font.Font(None, 20)
        for i, text in enumerate([
            f"HP: {self.health}/{self.max_health}",
            f"State: {self.state}",
        ]):
            surf = font.render(text, True, (255, 255, 0))
            screen.blit(surf, (screen_x, screen_y - 45 + i * 20))