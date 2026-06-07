import pygame
import math

class UI:
    """Lớp quản lý giao diện người dùng (thanh máu, thanh cooldown dash, animation, game over)"""
    
    def __init__(self):
        """Khởi tạo các thành phần UI và load tài nguyên"""
        pygame.font.init()
        self.font       = pygame.font.SysFont("Arial", 16, bold=True)  # Font nhỏ cho text UI
        self.font_big   = pygame.font.SysFont("Arial", 60, bold=True)  # Font lớn cho GAME OVER
        self.tick       = 0  # Biến đếm frame, dùng để tạo hiệu ứng nhấp nháy cho thanh máu khi thấp
        
        # Load ảnh dash
        self.dash_frames = []  # Mảng chứa 5 khung hình animation của dash
        self.load_dash_frames()
        
        # ===== BIẾN ANIMATION =====
        self.dash_animation_progress = 0.0   # Tiến độ animation (0.0 → 1.0)
        self.is_dashing_anim = False        # Cờ báo hiệu đang chạy animation dash
        self.dash_animation_speed = 0.04    # Tốc độ chạy animation (mỗi frame tăng 0.04)
        self.has_played_dash_anim = False   # THÊM: đánh dấu đã chạy animation cho lần dash này
        
    def load_dash_frames(self):
        """Load 5 ảnh dash từ thư mục assets/dash_UI/ và scale gấp đôi kích thước"""
        for i in range(5):  # Duyệt từ 0 đến 4 tương ứng dashUI00.png → dashUI04.png
            try:
                frame = pygame.image.load(f"assets/dash_UI/dashUI0{i}.png").convert_alpha()
                w, h = frame.get_width(), frame.get_height()
                frame = pygame.transform.scale(frame, (w * 2, h * 2))  # Scale gấp đôi để rõ nét hơn
                self.dash_frames.append(frame)
            except Exception as e:
                print(f"LỖI: Không load được dashUI0{i}.png - {e}")
                pygame.quit()
                exit()
    
    def start_dash_animation(self):
        """Bắt đầu animation dash (chỉ gọi 1 lần mỗi lần dash)"""
        self.is_dashing_anim = True
        self.dash_animation_progress = 0.0
        self.has_played_dash_anim = True  # Đánh dấu đã chạy animation cho lần dash này
    
    def reset_dash_animation_flag(self):
        """Reset flag khi dash kết thúc, cho phép lần dash sau có thể chạy animation lại"""
        self.has_played_dash_anim = False
    
    def update_dash_animation(self):
        """Cập nhật animation dash ở mỗi frame (tăng progress, kết thúc khi đạt 1.0)"""
        if self.is_dashing_anim:
            self.dash_animation_progress += self.dash_animation_speed
            if self.dash_animation_progress >= 1.0:
                self.is_dashing_anim = False  # Kết thúc animation
                self.dash_animation_progress = 0.0
                self.reset_dash_animation_flag()  # Reset flag để lần dash sau có thể chạy lại

    def draw_rounded_rect(self, surface, color, rect, radius=8):
        """Vẽ hình chữ nhật bo góc (tay thủ công vì pygame không có sẵn hàm vẽ bo góc)
        
        Args:
            surface: Surface để vẽ lên
            color: Màu sắc (tuple RGB)
            rect: Tuple (x, y, width, height)
            radius: Bán kính bo góc
        """
        x, y, w, h = rect
        # Vẽ phần thân (hình chữ nhật không có góc)
        pygame.draw.rect(surface, color, (x + radius, y, w - 2*radius, h))
        pygame.draw.rect(surface, color, (x, y + radius, w, h - 2*radius))
        # Vẽ 4 góc tròn
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)

    def draw_health_bar(self, surface, player):
        """Vẽ thanh máu với hiệu ứng đổi màu theo % máu và nhấp nháy khi máu thấp"""
        self.tick += 1  # Tăng biến đếm frame để tạo hiệu ứng nhấp nháy
        health_percent = max(0, player.health / player.max_health)  # Tính % máu (0.0 → 1.0)

        # Thông số thanh máu: vị trí và kích thước
        PAD    = 14      # Khoảng cách từ mép màn hình
        BW     = 220     # Chiều rộng thanh (Bar Width)
        BH     = 22      # Chiều cao thanh (Bar Height)
        BAR_X  = PAD + 96
        BAR_Y  = PAD + 35

        # Vẽ nền thanh máu (màu đỏ)
        self.draw_rounded_rect(surface, (255, 0, 0), (BAR_X, BAR_Y, BW, BH), radius=6)

        # Tính chiều rộng phần máu còn lại
        fill_w = max(0, int(BW * health_percent))
        if fill_w > 8:  # Chỉ vẽ nếu còn đủ rộng (tránh lỗi khi fill_w quá nhỏ)
            # Chọn màu dựa trên % máu
            if health_percent > 0.5:
                # Máu > 50%: Màu đỏ cam sáng
                bar_color = (210, 55, 55)
                shine     = (255, 100, 100)  # Màu ánh sáng phản chiếu
            elif health_percent > 0.25:
                # Máu 25-50%: Màu cam
                bar_color = (210, 130, 30)
                shine     = (255, 190, 60)
            else:
                # Máu < 25%: Màu đỏ nhấp nháy
                pulse = int(abs(math.sin(self.tick * 0.06)) * 40)  # Tạo dao động từ 0-40
                bar_color = (200 + pulse, 30, 30)  # Màu đỏ dao động
                shine     = (255, 80 + pulse, 80)

            # Vẽ phần máu còn lại
            self.draw_rounded_rect(surface, bar_color, (BAR_X, BAR_Y, fill_w, BH), radius=6)
            
            # Vẽ hiệu ứng ánh sáng (phản chiếu ở nửa trên thanh máu)
            shine_surf = pygame.Surface((fill_w, BH // 2), pygame.SRCALPHA)
            shine_surf.fill((*shine, 60))  # Màu với độ trong suốt 60/255
            surface.blit(shine_surf, (BAR_X, BAR_Y))

        # Vẽ viền thanh máu (màu vàng)
        pygame.draw.rect(surface, (255, 210, 100), (BAR_X, BAR_Y, BW, BH), 2, border_radius=6)
        
        # Vẽ text hiển thị số máu (vd: "75 / 100")
        hp_text = self.font.render(f"{player.health} / {player.max_health}", True, (255, 255, 255))
        tx = BAR_X + (BW - hp_text.get_width()) // 2  # Căn giữa theo chiều ngang
        ty = BAR_Y + (BH - hp_text.get_height()) // 2  # Căn giữa theo chiều dọc
        surface.blit(hp_text, (tx, ty))

    def draw_dash_cooldown(self, surface, player):
        """Vẽ thanh dash - chỉ chạy animation 1 lần mỗi lần dash"""
        
        # ===== CHỈ GỌI ANIMATION NẾU CHƯA CHẠY CHO LẦN DASH NÀY =====
        # Nếu player đang dash và animation chưa được chạy thì bắt đầu
        if player.is_dashing and not self.has_played_dash_anim:
            self.start_dash_animation()
        
        # Cập nhật animation (tăng progress, kết thúc khi cần)
        self.update_dash_animation()
        
        # Tính thời gian cooldown còn lại của dash
        remaining = player.get_dash_cooldown_remaining()
        ready_pct = 1.0 - (remaining / player.dash_cooldown)  # 0 = đang cooldown, 1 = sẵn sàng
        ready_pct = max(0.0, min(1.0, ready_pct))

        # Vị trí thanh dash (ngay dưới thanh máu)
        PAD   = 14
        BAR_X = PAD + 96
        BAR_Y = PAD + 35 + 28

        # ===== CHỌN FRAME HIỂN THỊ =====
        if self.is_dashing_anim:
            # ĐANG CHẠY ANIMATION: chọn frame dựa trên progress (0 → 4)
            frame_index = int(self.dash_animation_progress * 5)
            frame_index = min(4, frame_index)
        else:
            # BÌNH THƯỜNG: hiển thị theo cooldown (frame càng cao khi sẵn sàng)
            frame_index = int(ready_pct * 5)
            frame_index = min(4, frame_index)
        
        # Giới hạn frame_index trong khoảng hợp lệ
        frame_index = max(0, min(frame_index, len(self.dash_frames) - 1))
        
        # Vẽ frame dash
        current_frame = self.dash_frames[frame_index]
        frame_width = current_frame.get_width()
        frame_height = current_frame.get_height()
        
        surface.blit(current_frame, (BAR_X, BAR_Y))
        
        # Vẽ chữ "DASH" bên cạnh
        if self.is_dashing_anim:
            label_color = (255, 200, 50)  # Màu vàng sáng khi đang dash
        else:
            # Màu xanh sáng nếu sẵn sàng, xanh nhạt nếu đang cooldown
            label_color = (80, 220, 255) if ready_pct >= 1.0 else (150, 180, 210)
        
        label = self.font.render("DASH", True, label_color)
        surface.blit(label, (BAR_X + frame_width + 8, BAR_Y + (frame_height // 2) - 8))

    def draw_game_over(self, surface, screen_width, screen_height):
        """Vẽ màn hình Game Over với hiệu ứng mờ và hướng dẫn restart"""
        # Tạo lớp phủ mờ đen với độ trong suốt 160/255
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # Vẽ chữ GAME OVER lớn màu đỏ ở giữa màn hình
        text = self.font_big.render("GAME OVER", True, (220, 50, 50))
        x = (screen_width - text.get_width()) // 2
        y = (screen_height - text.get_height()) // 2
        surface.blit(text, (x, y))

        # Vẽ hướng dẫn phía dưới
        hint = self.font.render("Nhấn R để chơi lại  |  ESC để thoát", True, (255, 255, 255))
        surface.blit(hint, ((screen_width - hint.get_width()) // 2, y + 80))

    def draw(self, surface, player, screen_width, screen_height):
        """Vẽ toàn bộ UI (hàm chính gọi từ game loop)"""
        # Vẽ thanh máu
        self.draw_health_bar(surface, player)
        
        # Vẽ thanh cooldown dash
        self.draw_dash_cooldown(surface, player)

        # Nếu player đã chết, vẽ màn hình Game Over
        if hasattr(player, 'is_dead') and player.is_dead:
            self.draw_game_over(surface, screen_width, screen_height)