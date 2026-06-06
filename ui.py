import pygame
import math

class UI:
    def __init__(self):
        pygame.font.init()
        self.font       = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_big   = pygame.font.SysFont("Arial", 60, bold=True)
        self.tick       = 0
        
        # Load ảnh dash
        self.dash_frames = []
        self.load_dash_frames()
        
        # ===== BIẾN ANIMATION =====
        self.dash_animation_progress = 0.0
        self.is_dashing_anim = False
        self.dash_animation_speed = 0.02
        self.has_played_dash_anim = False  # ← THÊM: đánh dấu đã chạy animation cho lần dash này
        
    def load_dash_frames(self):
        """Load 5 ảnh dash và scale gấp đôi"""
        for i in range(5):
            try:
                frame = pygame.image.load(f"assets/dash_UI/dashUI0{i}.png").convert_alpha()
                w, h = frame.get_width(), frame.get_height()
                frame = pygame.transform.scale(frame, (w * 2, h * 2))
                self.dash_frames.append(frame)
            except Exception as e:
                print(f"LỖI: Không load được dashUI0{i}.png - {e}")
                pygame.quit()
                exit()
    
    def start_dash_animation(self):
        """Bắt đầu animation dash (chỉ gọi 1 lần mỗi lần dash)"""
        self.is_dashing_anim = True
        self.dash_animation_progress = 0.0
        self.has_played_dash_anim = True  # ← Đánh dấu đã chạy
    
    def reset_dash_animation_flag(self):
        """Reset flag khi dash kết thúc"""
        self.has_played_dash_anim = False
    
    def update_dash_animation(self):
        """Cập nhật animation dash"""
        if self.is_dashing_anim:
            self.dash_animation_progress += self.dash_animation_speed
            if self.dash_animation_progress >= 1.0:
                self.is_dashing_anim = False
                self.dash_animation_progress = 0.0
                self.reset_dash_animation_flag()  # ← Reset khi hoàn thành

    def draw_rounded_rect(self, surface, color, rect, radius=8):
        x, y, w, h = rect
        pygame.draw.rect(surface, color, (x + radius, y, w - 2*radius, h))
        pygame.draw.rect(surface, color, (x, y + radius, w, h - 2*radius))
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)

    def draw_health_bar(self, surface, player):
        self.tick += 1
        health_percent = max(0, player.health / player.max_health)

        PAD    = 14
        BW     = 220
        BH     = 22
        BAR_X  = PAD + 96
        BAR_Y  = PAD + 35

        self.draw_rounded_rect(surface, (255, 0, 0), (BAR_X, BAR_Y, BW, BH), radius=6)

        fill_w = max(0, int(BW * health_percent))
        if fill_w > 8:
            if health_percent > 0.5:
                bar_color = (210, 55, 55)
                shine     = (255, 100, 100)
            elif health_percent > 0.25:
                bar_color = (210, 130, 30)
                shine     = (255, 190, 60)
            else:
                pulse = int(abs(math.sin(self.tick * 0.06)) * 40)
                bar_color = (200 + pulse, 30, 30)
                shine     = (255, 80 + pulse, 80)

            self.draw_rounded_rect(surface, bar_color, (BAR_X, BAR_Y, fill_w, BH), radius=6)
            shine_surf = pygame.Surface((fill_w, BH // 2), pygame.SRCALPHA)
            shine_surf.fill((*shine, 60))
            surface.blit(shine_surf, (BAR_X, BAR_Y))

        pygame.draw.rect(surface, (255, 210, 100), (BAR_X, BAR_Y, BW, BH), 2, border_radius=6)
        
        hp_text = self.font.render(f"{player.health} / {player.max_health}", True, (255, 255, 255))
        tx = BAR_X + (BW - hp_text.get_width()) // 2
        ty = BAR_Y + (BH - hp_text.get_height()) // 2
        surface.blit(hp_text, (tx, ty))

    def draw_dash_cooldown(self, surface, player):
        """Vẽ thanh dash - chỉ chạy animation 1 lần mỗi lần dash"""
        
        # ===== CHỈ GỌI ANIMATION NẾU CHƯA CHẠY CHO LẦN DASH NÀY =====
        if player.is_dashing and not self.has_played_dash_anim:
            self.start_dash_animation()
        
        # Cập nhật animation
        self.update_dash_animation()
        
        # Tính cooldown
        remaining = player.get_dash_cooldown_remaining()
        ready_pct = 1.0 - (remaining / player.dash_cooldown)
        ready_pct = max(0.0, min(1.0, ready_pct))

        PAD   = 14
        BAR_X = PAD + 96
        BAR_Y = PAD + 35 + 28

        # ===== CHỌN FRAME =====
        if self.is_dashing_anim:
            # ĐANG CHẠY ANIMATION: từ 0 -> 4
            frame_index = int(self.dash_animation_progress * 5)
            frame_index = min(4, frame_index)
        else:
            # BÌNH THƯỜNG: hiển thị theo cooldown
            frame_index = int(ready_pct * 5)
            frame_index = min(4, frame_index)
        
        frame_index = max(0, min(frame_index, len(self.dash_frames) - 1))
        
        # Vẽ frame
        current_frame = self.dash_frames[frame_index]
        frame_width = current_frame.get_width()
        frame_height = current_frame.get_height()
        
        surface.blit(current_frame, (BAR_X, BAR_Y))
        
        # Label DASH
        if self.is_dashing_anim:
            label_color = (255, 200, 50)
        else:
            label_color = (80, 220, 255) if ready_pct >= 1.0 else (150, 180, 210)
        
        label = self.font.render("DASH", True, label_color)
        surface.blit(label, (BAR_X + frame_width + 8, BAR_Y + (frame_height // 2) - 8))

    def draw_game_over(self, surface, screen_width, screen_height):
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        text = self.font_big.render("GAME OVER", True, (220, 50, 50))
        x = (screen_width - text.get_width()) // 2
        y = (screen_height - text.get_height()) // 2
        surface.blit(text, (x, y))

        hint = self.font.render("Nhấn R để chơi lại  |  ESC để thoát", True, (255, 255, 255))
        surface.blit(hint, ((screen_width - hint.get_width()) // 2, y + 80))

    def draw(self, surface, player, screen_width, screen_height):
        """Vẽ toàn bộ UI"""
        self.draw_health_bar(surface, player)
        self.draw_dash_cooldown(surface, player)

        if hasattr(player, 'is_dead') and player.is_dead:
            self.draw_game_over(surface, screen_width, screen_height)