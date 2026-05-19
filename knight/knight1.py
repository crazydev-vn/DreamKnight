import pygame
from config import PLAYER_SPEED, RUN_SPEED, DEBUG_MODE
from knight.animation_knight import Animation, load_idle_frames, load_walk_frames, load_run_frames, load_attack_idle_frames, load_attack_run_frames

# Lớp Player1 kế thừa từ pygame.sprite.Sprite để sử dụng hệ thống sprite của Pygame

# Lớp Player1 - Đại diện cho nhân vật chính (hiệp sĩ) trong game.
# Quản lý:
# - Các trạng thái: đứng yên (idle), đi bộ (walk), chạy (run), tấn công (attack).
# - Animation riêng cho từng trạng thái và từng hướng (lên, xuống, trái, phải).
# - Di chuyển mượt với vector chuẩn hóa, di chuyển = nhấn giữ shift trái
# - Tấn công bằng chuột trái, tạo hitbox tấn công và phát âm thanh luân phiên.
# - Giới hạn trong bản đồ, cập nhật camera, vẽ với debug hitbox.

class Player1(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # KHỞI TẠO CÁC BỘ ANIMATION
        self.idle_animations = {
            "up": Animation(load_idle_frames("up"), frame_duration=200),
            "down": Animation(load_idle_frames("down"), frame_duration=200), 
            "left": Animation(load_idle_frames("left"), frame_duration=200),
            "right": Animation(load_idle_frames("right"), frame_duration=200),
        }
        
        self.walk_animations = {
            "up": Animation(load_walk_frames("up")),
            "down": Animation(load_walk_frames("down")), 
            "left": Animation(load_walk_frames("left")),
            "right": Animation(load_walk_frames("right")),
        }
        
        self.run_animations = {
            "up": Animation(load_run_frames("up"), frame_duration=80),
            "down": Animation(load_run_frames("down"), frame_duration=80), 
            "left": Animation(load_run_frames("left"), frame_duration=80),
            "right": Animation(load_run_frames("right"), frame_duration=80),
        }
        
        self.attack_idle_animations = {
            "up": Animation(load_attack_idle_frames("up"), frame_duration=60),
            "down": Animation(load_attack_idle_frames("down"), frame_duration=60), 
            "left": Animation(load_attack_idle_frames("left"), frame_duration=60),
            "right": Animation(load_attack_idle_frames("right"), frame_duration=60),
        }
        
        self.attack_run_animations = {
            "up": Animation(load_attack_run_frames("up"), frame_duration=50),
            "down": Animation(load_attack_run_frames("down"), frame_duration=50), 
            "left": Animation(load_attack_run_frames("left"), frame_duration=50),
            "right": Animation(load_attack_run_frames("right"), frame_duration=50),
        }

        # KHỞI TẠO ÂM THANH TẤN CÔNG
        pygame.mixer.init()
        self.attack_sound_1 = pygame.mixer.Sound("03_sounds/attack/Sword1.mp3")
        self.attack_sound_2 = pygame.mixer.Sound("03_sounds/attack/Sword2.mp3")
        self.attack_sound_3 = pygame.mixer.Sound("03_sounds/attack/Sword3.mp3")
        self.attack_sound_4 = pygame.mixer.Sound("03_sounds/attack/Sword4.mp3")
        
        self.attack_sounds = [
            self.attack_sound_1,
            self.attack_sound_2,
            self.attack_sound_3,
            self.attack_sound_4,
        ]
        
        self.current_attack_sound_index = 0

        # BIẾN TRẠNG THÁI CỦA PLAYER
        self.direction = "down"
        self.is_running = False
        self.is_attacking = False
        self.attack_start_time = 0
        self.attack_duration = 300
        self.sound_played_for_this_attack = False  
        
        # THÊM BIẾN TOGGLE RUN (nhấn Shift 1 lần để chạy, nhấn lại để đi bộ)
        self.run_mode = False  # Chế độ chạy nhanh (toggle)
        self.shift_just_pressed = False  # Đánh dấu Shift vừa được nhấn trong frame này
        
        # THAY ĐỔI 1: Xóa các biến liên quan đến thời gian chạy tự động
        # (không cần walk_start_time và running_transition_time nữa)

        # HÌNH ẢNH VÀ VỊ TRÍ
        self.image = self.idle_animations[self.direction].current_frame
        self.rect = self.image.get_rect(center=(x, y))

        self.x = x
        self.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.dx = 0
        self.dy = 0
        
        self.debug = DEBUG_MODE
        self.attack_hitbox = None

    # THAY ĐỔI 2: Sửa handle_input để kiểm tra phím Shift với chế độ toggle
    def handle_input(self, events):
        keys = pygame.key.get_pressed()
        
        # XỬ LÝ TOGGLE RUN (nhấn Shift 1 lần để chuyển đổi chế độ chạy/đi bộ)
        # Kiểm tra nếu đang nhấn Shift
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if not self.shift_just_pressed:  # Chỉ xử lý 1 lần khi mới nhấn
                self.run_mode = not self.run_mode  # Đảo trạng thái chế độ chạy
                self.shift_just_pressed = True
        else:
            self.shift_just_pressed = False  # Reset khi thả Shift
        
        if not self.is_attacking:
            dx_raw = (keys[pygame.K_d] - keys[pygame.K_a])
            dy_raw = (keys[pygame.K_s] - keys[pygame.K_w])

            if dx_raw != 0 or dy_raw != 0:
                length = max((dx_raw**2 + dy_raw**2) ** 0.5, 0.1)
                
                # THAY ĐỔI QUAN TRỌNG: Kiểm tra run_mode thay vì nhấn giữ Shift
                # Nếu đang ở chế độ chạy thì chạy nhanh, nếu không thì đi bộ
                if self.run_mode:
                    # Đang chạy - dùng tốc độ chạy
                    self.dx = (dx_raw / length) * RUN_SPEED
                    self.dy = (dy_raw / length) * RUN_SPEED
                    self.is_running = True
                else:
                    # Đang đi bộ - dùng tốc độ đi bộ
                    self.dx = (dx_raw / length) * PLAYER_SPEED
                    self.dy = (dy_raw / length) * PLAYER_SPEED
                    self.is_running = False

                # CẬP NHẬT HƯỚNG
                if dx_raw != 0:
                    self.direction = "right" if dx_raw > 0 else "left"
                else:
                    self.direction = "down" if dy_raw > 0 else "up"
            else:
                self.dx = 0
                self.dy = 0
                self.is_running = False  # Reset trạng thái chạy khi đứng yên

        # Xử lý tấn công
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.is_attacking:
                    self.start_attack()
    
    def play_next_attack_sound(self):
        self.attack_sounds[self.current_attack_sound_index].play()
        self.current_attack_sound_index += 1
        if self.current_attack_sound_index >= len(self.attack_sounds):
            self.current_attack_sound_index = 0

    def start_attack(self):
        self.is_attacking = True
        self.attack_start_time = pygame.time.get_ticks()
        self.sound_played_for_this_attack = False
        
        if self.is_running:
            self.attack_run_animations[self.direction].reset()
        else:
            self.attack_idle_animations[self.direction].reset()
        
        self.create_attack_hitbox()

    def create_attack_hitbox(self):
        attack_range = 50
        hitbox_size = 40
        
        if self.direction == "up":
            self.attack_hitbox = pygame.Rect(
                self.x + self.width // 2 - hitbox_size // 2,
                self.y - attack_range,
                hitbox_size,
                attack_range
            )
        elif self.direction == "down":
            self.attack_hitbox = pygame.Rect(
                self.x + self.width // 2 - hitbox_size // 2,
                self.y + self.height,
                hitbox_size,
                attack_range
            )
        elif self.direction == "left":
            self.attack_hitbox = pygame.Rect(
                self.x - attack_range,
                self.y + self.height // 2 - hitbox_size // 2,
                attack_range,
                hitbox_size
            )
        elif self.direction == "right":
            self.attack_hitbox = pygame.Rect(
                self.x + self.width,
                self.y + self.height // 2 - hitbox_size // 2,
                attack_range,
                hitbox_size
            )
    
    def update_attack(self):
        if self.is_attacking:
            current_time = pygame.time.get_ticks()
            
            if not self.sound_played_for_this_attack:
                self.play_next_attack_sound()
                self.sound_played_for_this_attack = True
            
            if self.is_running:
                self.attack_run_animations[self.direction].update()
            else:
                self.attack_idle_animations[self.direction].update()
            
            if current_time - self.attack_start_time >= self.attack_duration:
                self.is_attacking = False
                self.attack_hitbox = None

    # THAY ĐỔI 3: Xóa hoặc đơn giản hóa update_running_state
    def update_running_state(self):
        # Không cần hàm này nữa vì trạng thái chạy được điều khiển hoàn toàn bằng toggle Shift
        # Giữ lại hàm rỗng để không ảnh hưởng đến code gọi nó
        pass

    def move(self, dx, dy, map_width, map_height):
        if self.is_attacking:
            speed_multiplier = 0.3 if self.is_running else 0.1
        else:
            speed_multiplier = 1.0
            
        current_dx = dx * speed_multiplier
        current_dy = dy * speed_multiplier
        
        new_x = self.x + current_dx
        new_y = self.y + current_dy
        
        if 0 <= new_x <= map_width - self.width:
            self.x = new_x
        if 0 <= new_y <= map_height - self.height:
            self.y = new_y
            
        self.rect.x = self.x
        self.rect.y = self.y
        
        if self.is_attacking:
            self.create_attack_hitbox()

    def update(self, map_width, map_height, events):
        self.handle_input(events)
        self.update_running_state()  # Hàm này giờ không làm gì cả
        self.update_attack()
        self.move(self.dx, self.dy, map_width, map_height)

        if self.is_attacking:
            if self.is_running:
                self.image = self.attack_run_animations[self.direction].current_frame
            else:
                self.image = self.attack_idle_animations[self.direction].current_frame
        elif self.dx == 0 and self.dy == 0:
            self.idle_animations[self.direction].update()
            self.image = self.idle_animations[self.direction].current_frame
        else:
            if self.is_running:
                self.run_animations[self.direction].update()
                self.image = self.run_animations[self.direction].current_frame
            else:
                self.walk_animations[self.direction].update()
                self.image = self.walk_animations[self.direction].current_frame
                
    def update_debug_mode(self):
        from config import DEBUG_MODE
        self.debug = DEBUG_MODE

    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        screen.blit(self.image, (screen_x, screen_y))
    """
        if DEBUG_MODE:
            if self.is_attacking and self.attack_hitbox:
                hitbox_screen_x = self.attack_hitbox.x - camera.x
                hitbox_screen_y = self.attack_hitbox.y - camera.y
                pygame.draw.rect(screen, (255, 0, 0), 
                            (hitbox_screen_x, hitbox_screen_y, 
                                self.attack_hitbox.width, self.attack_hitbox.height), 2)
            
            pygame.draw.rect(screen, (0, 255, 0), 
                        (screen_x, screen_y, self.width, self.height), 2)
    """
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_attack_hitbox(self):
        return self.attack_hitbox if self.is_attacking else None