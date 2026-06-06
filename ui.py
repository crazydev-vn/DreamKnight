import pygame
import math

#================================================================================================
# Vai trò: Quản lý toàn bộ giao diện người dùng (HUD) hiển thị trên màn hình.
# Bao gồm: thanh máu player, thanh dash cooldown, thông báo game over.
#================================================================================================

class UI:
    def __init__(self):
        pygame.font.init()
        self.font       = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_big   = pygame.font.SysFont("Arial", 60, bold=True)
        self.tick       = 0   # dùng để tạo hiệu ứng pulse

    # ── Vẽ hình chữ nhật bo góc ──────────────────────────────────────────────
    def draw_rounded_rect(self, surface, color, rect, radius=8):
        x, y, w, h = rect
        pygame.draw.rect(surface, color, (x + radius, y, w - 2*radius, h))
        pygame.draw.rect(surface, color, (x, y + radius, w, h - 2*radius))
        pygame.draw.circle(surface, color, (x + radius,     y + radius),     radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + radius),     radius)
        pygame.draw.circle(surface, color, (x + radius,     y + h - radius), radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)

    # ── Vẽ thanh máu ─────────────────────────────────────────────────────────
    def draw_health_bar(self, surface, player):
        self.tick += 1
        health_percent = max(0, player.health / player.max_health)

        PAD    = 14          # khoảng cách từ mép màn hình
        BW     = 220         # chiều rộng thanh
        BH     = 22          # chiều cao thanh
        BAR_X  = PAD + 96    # dịch sang phải để icon trái tim không đè
        BAR_Y  = PAD + 35

        # ── Nền thanh (xám đậm) ──
        self.draw_rounded_rect(surface, (255, 0, 0), (BAR_X, BAR_Y, BW, BH), radius=6)

        # ── Phần máu hiện tại ──
        fill_w = max(0, int(BW * health_percent))
        if fill_w > 8:
            if health_percent > 0.5:
                bar_color = (210, 55, 55)       # đỏ bình thường
                shine     = (255, 100, 100)
            elif health_percent > 0.25:
                bar_color = (210, 130, 30)      # vàng cam khi máu vừa
                shine     = (255, 190, 60)
            else:
                # pulse đỏ nhấp nháy khi máu thấp
                pulse = int(abs(math.sin(self.tick * 0.06)) * 40)
                bar_color = (200 + pulse, 30, 30)
                shine     = (255, 80 + pulse, 80)

            self.draw_rounded_rect(surface, bar_color, (BAR_X, BAR_Y, fill_w, BH), radius=6)

            # Sọc sáng phía trên (hiệu ứng bóng)
            shine_surf = pygame.Surface((fill_w, BH // 2), pygame.SRCALPHA)
            shine_surf.fill((*shine, 60))
            surface.blit(shine_surf, (BAR_X, BAR_Y))

        # ── Viền ngoài ──
        pygame.draw.rect(surface, (255, 210, 100),
                         (BAR_X, BAR_Y, BW, BH), 2, border_radius=6)

        
        # ── Số máu ──
        hp_text = self.font.render(f"{player.health} / {player.max_health}", True, (255, 255, 255))
        tx = BAR_X + (BW - hp_text.get_width()) // 2
        ty = BAR_Y + (BH - hp_text.get_height()) // 2
        surface.blit(hp_text, (tx, ty))

    # ── Vẽ thanh dash ────────────────────────────────────────────────────────
    def draw_dash_cooldown(self, surface, player):
        remaining    = player.get_dash_cooldown_remaining()
        ready_pct    = 1.0 - (remaining / player.dash_cooldown)
        ready_pct    = max(0.0, min(1.0, ready_pct))

        PAD   = 14
        BW    = 220
        BH    = 10
        BAR_X = PAD + 96
        BAR_Y = PAD + 35 + 28     # ngay dưới thanh máu

        # Nền
        self.draw_rounded_rect(surface, (30, 30, 60), (BAR_X, BAR_Y, BW, BH), radius=4)

        # Phần đã hồi
        fill_w = max(0, int(BW * ready_pct))
        if fill_w > 4:
            color = (80, 220, 255) if ready_pct >= 1.0 else (40, 130, 210)
            self.draw_rounded_rect(surface, color, (BAR_X, BAR_Y, fill_w, BH), radius=4)

        # Viền
        pygame.draw.rect(surface, (100, 180, 255),
                         (BAR_X, BAR_Y, BW, BH), 1, border_radius=4)

        # Label
        label_color = (80, 220, 255) if ready_pct >= 1.0 else (150, 180, 210)
        label = self.font.render("DASH", True, label_color)
        surface.blit(label, (BAR_X + BW + 8, BAR_Y - 3))

    # ── Game Over ─────────────────────────────────────────────────────────────
    def draw_game_over(self, surface, screen_width, screen_height):
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        text = self.font_big.render("GAME OVER", True, (220, 50, 50))
        x = (screen_width  - text.get_width())  // 2
        y = (screen_height - text.get_height()) // 2
        surface.blit(text, (x, y))

        hint = self.font.render("Nhấn R để chơi lại  |  ESC để thoát", True, (255, 255, 255))
        surface.blit(hint, ((screen_width - hint.get_width()) // 2, y + 80))

    # ── Hàm chính ─────────────────────────────────────────────────────────────
    def draw(self, surface, player, screen_width, screen_height):
        self.draw_health_bar(surface, player)
        self.draw_dash_cooldown(surface, player)

        if hasattr(player, 'is_dead') and player.is_dead:
            self.draw_game_over(surface, screen_width, screen_height)

class PauseMenu:
    def __init__(self):
        pygame.font.init()
        self.font_title  = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_btn    = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_small  = pygame.font.SysFont("Arial", 18)
        self.visible     = False

        # Các nút: (label, action)
        self.buttons = ["Resume", "Volume", "Quit"]
        self.hovered = -1  # nút đang hover

    def toggle(self):
        self.visible = not self.visible

    def draw(self, surface, screen_width, screen_height, volume):
        if not self.visible:
            return

        # Nền mờ
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        # Khung menu
        box_w, box_h = 320, 280
        box_x = (screen_width  - box_w) // 2
        box_y = (screen_height - box_h) // 2
        pygame.draw.rect(surface, (30, 20, 50),   (box_x, box_y, box_w, box_h), border_radius=16)
        pygame.draw.rect(surface, (255, 210, 100), (box_x, box_y, box_w, box_h), 2, border_radius=16)

        # Tiêu đề
        title = self.font_title.render("PAUSE", True, (255, 210, 100))
        surface.blit(title, (box_x + (box_w - title.get_width()) // 2, box_y + 24))

        btn_w, btn_h = 220, 44
        btn_x = box_x + (box_w - btn_w) // 2
        mouse_pos = pygame.mouse.get_pos()

        # Nút Resume
        resume_rect = pygame.Rect(btn_x, box_y + 110, btn_w, btn_h)
        if resume_rect.collidepoint(mouse_pos):
            color_bg, color_txt = (255, 210, 100), (30, 20, 50)
        else:
            color_bg, color_txt = (60, 45, 90), (255, 255, 255)
        pygame.draw.rect(surface, color_bg,        resume_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 210, 100), resume_rect, 2, border_radius=10)
        t = self.font_btn.render("Resume", True, color_txt)
        surface.blit(t, (btn_x + (btn_w - t.get_width()) // 2, box_y + 110 + (btn_h - t.get_height()) // 2))

        # Nút Quit
        quit_rect = pygame.Rect(btn_x, box_y + 172, btn_w, btn_h)
        if quit_rect.collidepoint(mouse_pos):
            color_bg, color_txt = (200, 50, 50), (255, 255, 255)
        else:
            color_bg, color_txt = (100, 30, 30), (255, 180, 180)
        pygame.draw.rect(surface, color_bg,      quit_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 80, 80), quit_rect, 2, border_radius=10)
        t = self.font_btn.render("Quit", True, color_txt)
        surface.blit(t, (btn_x + (btn_w - t.get_width()) // 2, box_y + 172 + (btn_h - t.get_height()) // 2))

    def handle_click(self, pos, screen_width, screen_height):
        if not self.visible:
            return None

        box_w, box_h = 320, 280
        box_x = (screen_width  - box_w) // 2
        box_y = (screen_height - box_h) // 2
        btn_w, btn_h = 220, 44
        btn_x = box_x + (box_w - btn_w) // 2

        if pygame.Rect(btn_x, box_y + 110, btn_w, btn_h).collidepoint(pos):
            self.visible = False
            return "resume"
        if pygame.Rect(btn_x, box_y + 172, btn_w, btn_h).collidepoint(pos):
            return "quit"
        return None