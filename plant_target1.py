import pygame
import os
import math
from config import PLAYER_SPEED, RUN_SPEED
from knight.animation_knight import Animation, AnimationManager

# ==================== CẤU HÌNH CHO PLANT TARGET ====================
PLANT_ANIMATION_CONFIGS = {
    "idle": {
        "folder": "plant1_idle",
        "directions": {
            "up":    {"prefix": "plant1_idle_ebove", "frames": 4},
            "down":  {"prefix": "plant1_idle_under", "frames": 4},
            "left":  {"prefix": "plant1_idle_left", "frames": 4},
            "right": {"prefix": "plant1_idle_right", "frames": 4}
        }
    },
    "walk": {
        "folder": "plant1_walk",
        "directions": {
            "up":    {"prefix": "plant1_walk_ebove", "frames": 6},
            "down":  {"prefix": "plant1_walk_under", "frames": 6},
            "left":  {"prefix": "plant1_walk_left", "frames": 6},
            "right": {"prefix": "plant1_walk_right", "frames": 6}
        }
    },
    "run": {
        "folder": "plant1_run",
        "directions": {
            "up":    {"prefix": "plant1_run_ebove", "frames": 8},
            "down":  {"prefix": "plant1_run_under", "frames": 8},
            "left":  {"prefix": "plant1_run_left", "frames": 8},
            "right": {"prefix": "plant1_run_right", "frames": 8}
        }
    },
    "attack": {
        "folder": "plant1_attack",
        "directions": {
            "up":    {"prefix": "plant1_attack_ebove", "frames": 7},
            "down":  {"prefix": "plant1_attack_under", "frames": 7},
            "left":  {"prefix": "plant1_attack_left", "frames": 7},
            "right": {"prefix": "plant1_attack_right", "frames": 7}
        }
    }
}

class PlantTarget1(pygame.sprite.Sprite):
    """Lớp PlantTarget1 - kẻ địch thực vật có AI đơn giản"""
    
    def __init__(self, x, y, scale_factor=2.0):
        super().__init__()
        
        # ---------- VỊ TRÍ VÀ HITBOX CƠ BẢN ----------
        self.x = float(x)
        self.y = float(y)
        self.home_x = float(x)    # lưu vị trí nhà để quay về
        self.home_y = float(y)
        
        # Khởi tạo các dictionary chứa Animation
        self.idle_anims = {}
        self.walk_anims = {}
        self.run_anims = {}
        self.attack_anims = {}
        
        # Load tất cả animation
        self._load_all_animations(scale_factor)
        
        # ---------- TRẠNG THÁI HIỆN TẠI ----------
        self.direction = "down"              # SỬA: "under" -> "down"
        self.state = "idle"                  # idle, walk, run, attack, return_home
        self.is_attacking = False
        
        # ---------- THÔNG SỐ DI CHUYỂN ----------
        self.speed = 0.0
        self.dx = 0.0
        self.dy = 0.0
        
        # ---------- AI PARAMETERS ----------
        self.home_chase_radius = 200         # vùng phát hiện cố định (hitbox 2) - TĂNG LÊN 200
        self.home_leave_radius = 400         # vùng rời cố định (hitbox 3) - GẤP ĐÔI chase
        self.walk_duration = 1000            # thời gian đi bộ trước khi chạy (ms)

        self.walk_start_time = 0
        self.is_running = False
        
        # Lưu player reference
        self.player = None
        
        # ---------- HITBOX ----------
        self.body_radius = 20
        
        # ---------- HÌNH ẢNH VÀ RECT ----------
        # SỬA: Kiểm tra an toàn khi lấy frame
        if "down" in self.idle_anims:
            self.image = self.idle_anims["down"].current_frame
        else:
            # Fallback: tạo surface trắng nếu không có animation
            self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
            self.image.fill((0, 255, 0))  # màu xanh tạm thời
            
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.body_radius = max(self.width, self.height) // 2
        
        # Debug
        self.debug = True
        
    def _load_all_animations(self, scale_factor):
        """Load tất cả các frame animation từ thư mục assets/plant_target/plant1"""
        # SỬA: đường dẫn đúng
        base_path = os.path.join("assets", "plant_target", "plant1")
        
        # Kiểm tra thư mục tồn tại
        if not os.path.exists(base_path):
            print(f"Thư mục không tồn tại: {base_path}")
            return
            
        def load_anim_type(anim_type, frame_duration=90):
            anims = {}
            config = PLANT_ANIMATION_CONFIGS.get(anim_type)
            if not config:
                return anims
            folder = config["folder"]
            for direction, dir_cfg in config["directions"].items():
                prefix = dir_cfg["prefix"]
                frame_count = dir_cfg["frames"]
                frames = []
                for i in range(1, frame_count + 1):
                    filename = f"{prefix}{i}.png"
                    filepath = os.path.join(base_path, folder, filename)
                    try:
                        if os.path.exists(filepath):
                            img = pygame.image.load(filepath).convert_alpha()
                            if scale_factor != 1.0:
                                new_size = (int(img.get_width() * scale_factor),
                                           int(img.get_height() * scale_factor))
                                img = pygame.transform.scale(img, new_size)
                            frames.append(img)
                        else:
                            print(f"Không tìm thấy file: {filepath}")
                            # Tạo frame giả
                            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
                            surf.fill((0, 255, 0))
                            frames.append(surf)
                    except Exception as e:
                        print(f"Lỗi load ảnh {filepath}: {e}")
                        surf = pygame.Surface((64, 64), pygame.SRCALPHA)
                        surf.fill((0, 255, 0))
                        frames.append(surf)
                if frames:
                    anims[direction] = Animation(frames, frame_duration)
                    print(f"Loaded {len(frames)} frames for {anim_type} {direction}")
            return anims
        
        self.idle_anims = load_anim_type("idle", frame_duration=200)
        self.walk_anims = load_anim_type("walk", frame_duration=90)
        self.run_anims = load_anim_type("run", frame_duration=80)
        self.attack_anims = load_anim_type("attack", frame_duration=60)
        
        # Nếu không load được animation nào, tạo animation mặc định
        if not self.idle_anims:
            print("Tạo animation mặc định cho plant")
            default_frames = [pygame.Surface((64, 64), pygame.SRCALPHA)]
            default_frames[0].fill((0, 255, 0))
            self.idle_anims["down"] = Animation(default_frames, 200)
            self.idle_anims["up"] = Animation(default_frames, 200)
            self.idle_anims["left"] = Animation(default_frames, 200)
            self.idle_anims["right"] = Animation(default_frames, 200)
    
    def set_player(self, player):
        """Gán tham chiếu đến player"""
        self.player = player
        
    def update(self, delta_time, map_width, map_height):
        """Cập nhật trạng thái, AI và di chuyển - DÙNG HITBOX CỐ ĐỊNH TẠI NHÀ"""
        if self.player is None:
            return
        
        # === QUAN TRỌNG: Tính khoảng cách từ PLAYER đến HOME (vị trí nhà cố định) ===
        px = self.player.x + self.player.width // 2
        py = self.player.y + self.player.height // 2
        
        home_center_x = self.home_x + self.width // 2
        home_center_y = self.home_y + self.height // 2
        
        # Khoảng cách từ player đến nhà (dùng để kiểm tra hitbox cố định)
        dist_player_to_home = math.hypot(px - home_center_x, py - home_center_y)
        
        # Cập nhật hướng nhìn về phía player (nếu đang đuổi)
        if self.state in ("walk", "run", "attack") and self.player:
            angle = math.atan2(py - (self.y + self.height // 2), 
                              px - (self.x + self.width // 2))
            if abs(angle) < math.pi/4:
                self.direction = "right"
            elif abs(angle - math.pi) < math.pi/4:
                self.direction = "left"
            elif angle > math.pi/4 and angle < 3*math.pi/4:
                self.direction = "down"
            else:
                self.direction = "up"
        
        # === XỬ LÝ TRẠNG THÁI AI DỰA TRÊN HITBOX CỐ ĐỊNH ===
        current_time = pygame.time.get_ticks()
        
        # Kiểm tra player có ở trong vùng chase_range CỐ ĐỊNH không
        if dist_player_to_home <= self.home_chase_radius:
            # Player đang ở trong vùng đuổi theo (cố định tại nhà)
            if self.state == "idle":
                self.state = "walk"
                self.walk_start_time = current_time
                self.is_running = False
                print(f"Phát hiện player trong vùng {self.home_chase_radius}px - Bắt đầu đuổi")
            elif self.state == "walk":
                if current_time - self.walk_start_time >= self.walk_duration:
                    self.state = "run"
                    self.is_running = True
                    print("Chuyển sang chạy!")
            elif self.state == "return_home":
                # Đang quay về nhưng player lại vào vùng -> đuổi tiếp
                self.state = "walk"
                self.walk_start_time = current_time
                self.is_running = False
                print("Player quay lại vùng - Tiếp tục đuổi")
                
        elif dist_player_to_home > self.home_leave_radius:
            # Player ra khỏi vùng leave_range CỐ ĐỊNH -> quay về nhà
            if self.state != "return_home" and self.state != "idle":
                self.state = "return_home"
                self.is_running = False
                print(f"Player ra khỏi vùng {self.home_leave_radius}px - QUAY VỀ NHÀ")
        
        # === XỬ LÝ TRẠNG THÁI "return_home" (quay về vị trí nhà) ===
        if self.state == "return_home":
            # Tính vector từ vị trí hiện tại về HOME
            dx_home = home_center_x - (self.x + self.width // 2)
            dy_home = home_center_y - (self.y + self.height // 2)
            dist_to_home = math.hypot(dx_home, dy_home)
            
            if dist_to_home < 10:
                # Đã về đến nhà
                self.state = "idle"
                self.dx = 0
                self.dy = 0
                # Đặt chính xác về vị trí home
                self.x = self.home_x
                self.y = self.home_y
                self.rect.x = self.x
                self.rect.y = self.y
                print("Đã về đến NHÀ!")
            else:
                # Di chuyển về nhà với tốc độ walk
                if dist_to_home > 0:
                    length = max(abs(dx_home), abs(dy_home), 0.1)
                    speed = PLAYER_SPEED * 0.6  # Tốc độ về nhà (chậm hơn)
                    self.dx = (dx_home / length) * speed
                    self.dy = (dy_home / length) * speed
                    
                    # Cập nhật hướng
                    if abs(dx_home) > abs(dy_home):
                        self.direction = "right" if dx_home > 0 else "left"
                    else:
                        self.direction = "down" if dy_home > 0 else "up"
        
        # === XỬ LÝ ĐUỔI THEO (khi đang walk hoặc run) ===
        if self.state in ("walk", "run"):
            # Tính vector từ Plant đến Player
            target_x = self.player.x + self.player.width // 2
            target_y = self.player.y + self.player.height // 2
            dx_target = target_x - (self.x + self.width // 2)
            dy_target = target_y - (self.y + self.height // 2)
            distance = math.hypot(dx_target, dy_target)
            
            if distance > 5:  # Chỉ di chuyển nếu còn xa
                length = max(distance, 0.1)
                if self.state == "run":
                    speed = RUN_SPEED * 0.7  # Plant chạy chậm hơn player
                else:
                    speed = PLAYER_SPEED * 0.5  # Plant đi chậm hơn player
                self.dx = (dx_target / length) * speed
                self.dy = (dy_target / length) * speed
            else:
                self.dx = 0
                self.dy = 0
                if self.state == "run":
                    self.state = "walk"  # Chuyển sang walk khi đến gần
        
        # Dừng lại khi idle
        if self.state == "idle":
            self.dx = 0
            self.dy = 0
        
        # CẬP NHẬT VỊ TRÍ (có giới hạn map)
        new_x = self.x + self.dx
        new_y = self.y + self.dy
        if 0 <= new_x <= map_width - self.width:
            self.x = new_x
        if 0 <= new_y <= map_height - self.height:
            self.y = new_y
        self.rect.x = self.x
        self.rect.y = self.y
        
        # CẬP NHẬT ANIMATION
        self._update_animation(delta_time)
        
    def _update_animation(self, delta_time):
        """Chọn và cập nhật animation"""
        # Chọn dictionary animation
        if self.state == "idle":
            anim_dict = self.idle_anims
        elif self.state == "walk":
            anim_dict = self.walk_anims
        elif self.state == "run":
            anim_dict = self.run_anims
        elif self.state == "attack":
            anim_dict = self.attack_anims
        else:
            anim_dict = self.walk_anims if self.state == "return_home" else self.idle_anims
        
        # Lấy animation theo hướng (SỬA: fallback an toàn)
        anim = anim_dict.get(self.direction)
        if not anim and "down" in anim_dict:
            anim = anim_dict["down"]
        elif not anim and anim_dict:
            anim = list(anim_dict.values())[0]
            
        if anim:
            anim.update()
            self.image = anim.current_frame
            # Cập nhật rect giữ nguyên tâm
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            self.body_radius = max(self.width, self.height) // 2
    
    def draw(self, screen, camera):
        """Vẽ Plant và hitbox CỐ ĐỊNH tại nhà"""
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        screen.blit(self.image, (screen_x, screen_y))
        
        if self.debug:
            # === HITBOX DI ĐỘNG (thân plant) - màu xanh lá ===
            center_x = self.x + self.width // 2 - camera.x
            center_y = self.y + self.height // 2 - camera.y
            pygame.draw.circle(screen, (0, 255, 0), (center_x, center_y), self.body_radius, 2)
            
            # === HITBOX CỐ ĐỊNH TẠI VỊ TRÍ NHÀ ===
            home_center_x = self.home_x + self.width // 2 - camera.x
            home_center_y = self.home_y + self.height // 2 - camera.y
            
            # Hitbox 2: Vùng đuổi theo (màu vàng) - CỐ ĐỊNH
            pygame.draw.circle(screen, (255, 255, 0), (home_center_x, home_center_y), self.home_chase_radius, 2)
            
            # Hitbox 3: Vùng rời (màu đỏ) - CỐ ĐỊNH
            pygame.draw.circle(screen, (255, 0, 0), (home_center_x, home_center_y), self.home_leave_radius, 2)
            
            # Vẽ điểm nhà (hình vuông trắng)
            pygame.draw.rect(screen, (255, 255, 255), 
                            (home_center_x - 5, home_center_y - 5, 10, 10), 2)
            
            # Vẽ đường từ plant đến nhà
            pygame.draw.line(screen, (200, 200, 200), 
                            (center_x, center_y), 
                            (home_center_x, home_center_y), 1)
            
            # === HIỂN THỊ THÔNG TIN DEBUG ===
            font = pygame.font.Font(None, 20)
            dist_to_home = math.hypot(
                (self.home_x + self.width//2) - (self.x + self.width//2),
                (self.home_y + self.height//2) - (self.y + self.height//2)
            )
            dist_text = font.render(f"Dist to home: {dist_to_home:.0f}", True, (255, 255, 255))
            screen.blit(dist_text, (screen_x, screen_y - 25))
            
            state_text = font.render(f"State: {self.state}", True, (255, 255, 0))
            screen.blit(state_text, (screen_x, screen_y - 45))
    
    def get_hitbox(self):
        """Trả về hitbox thân (hình tròn)"""
        return (self.x + self.width//2, self.y + self.height//2, self.body_radius)
    
    def get_chase_hitbox(self):
        """Trả về vùng phát hiện đuổi theo"""
        return (self.x + self.width//2, self.y + self.height//2, self.chase_radius)
    
    def get_leave_hitbox(self):
        """Trả về vùng rời khỏi"""
        return (self.x + self.width//2, self.y + self.height//2, self.leave_radius)