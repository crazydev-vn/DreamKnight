import pygame
from config import PLAYER_SPEED, RUN_SPEED, DEBUG_MODE
from knight1_hiteffect import HitEffectManager
from knight1_animation import (
    Animation, load_idle_frames, load_walk_frames, load_run_frames, 
    load_attack_idle_frames, load_attack_walk_frames, load_attack_run_frames,
    load_dash_frames  # THÊM MỚI: Import dash frames
)


#================================================================================================
# Lớp Player1 kế thừa từ pygame.sprite.Sprite để sử dụng hệ thống sprite của Pygame
# Lớp Player1 - Đại diện cho nhân vật chính (hiệp sĩ) trong game.
# Quản lý:
# - Các trạng thái: đứng yên (idle), đi bộ (walk), chạy (run), tấn công (attack), dash (lướt).
# - Animation riêng cho từng trạng thái và từng hướng (lên, xuống, trái, phải).
# - Di chuyển mượt với vector chuẩn hóa, di chuyển = nhấn giữ shift trái
# - Tấn công bằng chuột trái, tạo hitbox tấn công và phát âm thanh luân phiên.
# - Dash bằng chuột phải, lướt nhanh về phía trước với animation và kích thước sprite riêng
# - Gây sát thương lên kẻ địch khi tấn công
# - Giới hạn trong bản đồ, cập nhật camera, vẽ với debug hitbox.
#================================================================================================

class Player1(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # KHỞI TẠO CÁC BỘ ANIMATION
        self.idle_animations = {
            "up": Animation(load_idle_frames("up"), frame_duration=500),
            "down": Animation(load_idle_frames("down"), frame_duration=200), 
            "left": Animation(load_idle_frames("left"), frame_duration=200),
            "right": Animation(load_idle_frames("right"), frame_duration=500),
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
        
        # THÊM MỚI: Animation tấn công khi đi bộ
        self.attack_walk_animations = {
            "up": Animation(load_attack_walk_frames("up"), frame_duration=60),
            "down": Animation(load_attack_walk_frames("down"), frame_duration=60), 
            "left": Animation(load_attack_walk_frames("left"), frame_duration=60),
            "right": Animation(load_attack_walk_frames("right"), frame_duration=60),
        }
        
        self.attack_run_animations = {
            "up": Animation(load_attack_run_frames("up"), frame_duration=50),
            "down": Animation(load_attack_run_frames("down"), frame_duration=50), 
            "left": Animation(load_attack_run_frames("left"), frame_duration=50),
            "right": Animation(load_attack_run_frames("right"), frame_duration=50),
        }
        
        #DASH ANIMATION
        # Dash: kỹ năng lướt nhanh với animation riêng
        self.dash_animations = {
            "up": Animation(load_dash_frames("up"), frame_duration=40),
            "down": Animation(load_dash_frames("down"), frame_duration=40),
            "left": Animation(load_dash_frames("left"), frame_duration=40),
            "right": Animation(load_dash_frames("right"), frame_duration=40),
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

        #ÂM THANH DASH =====
        # Âm thanh khi thực hiện dash
        self.dash_sound = pygame.mixer.Sound("03_sounds/dash/dash03.mp3")  # Đảm bảo file tồn tại
        # Có thể thay bằng sound khác hoặc comment nếu chưa có file

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
        
        # DASH VARIABLES 
        self.is_dashing = False         # Đang trong trạng thái dash
        self.dash_start_time = 0        # Thời điểm bắt đầu dash
        self.dash_duration = 150        # Thời gian dash x(ms) - lướt trong x(ms)
        self.dash_distance = 100        # Khoảng cách dash (pixels) - lướt x(px)
        self.dash_start_x = 0           # Vị trí X bắt đầu dash
        self.dash_start_y = 0           # Vị trí Y bắt đầu dash
        self.dash_target_x = 0          # Vị trí X đích đến
        self.dash_target_y = 0          # Vị trí Y đích đến
        self.dash_cooldown = 500        # Thời gian hồi chiêu dash x00 -> 0.x(ms)
        self.last_dash_time = 0         # Thời điểm dash gần nhất
        self.dash_direction = "down"    # Hướng dash
        
        # Kích thước sprite dash khác nhau cho từng hướng
        # Left/Right: 63x32 (rộng hơn, thấp hơn - tạo cảm giác lao ngang)
        # Up/Down: 32x63 (hẹp hơn, cao hơn - tạo cảm giác lao dọc)
        self.dash_sprite_sizes = {
            "left": (63, 32),
            "right": (63, 32),
            "up": (32, 63),
            "down": (32, 63)
        }
        
        #  Xóa các biến liên quan đến thời gian chạy tự động
        
        # HÌNH ẢNH VÀ VỊ TRÍ
        self.image = self.idle_animations[self.direction].current_frame
        self.rect = self.image.get_rect(center=(x, y))

        self.x = x
        self.y = y

        self.width =  self.image.get_width()
        self.height = self.image.get_height()

        self.hitbox_width = 30   # Chiều rộng hitbox mong muốn
        self.hitbox_height = 50  # Chiều cao hitbox mong muốn

        # Tùy chọn: Offset để dịch hitbox so với ảnh
        self.hitbox_offset_x = 45  # Dịch ngang (dương = sang phải)
        self.hitbox_offset_y = 40  # Dịch dọc (dương = xuống dưới)

        self.dx = 0
        self.dy = 0
        
        self.debug = DEBUG_MODE
        self.attack_hitbox = None 

        # HỆ THỐNG SÁT THƯƠNG =====
        #PMD-Bất tử khi HP <= 30% với hiệu ứng mờ dần
        self.health = 100
        self.max_health = 100
        self.is_dead = False
        # GHOST MODE: khi HP <= 30% thì mờ và bất tử 2 giây
        self.ghost_mode = False
        self.ghost_start_time = 0
        self.ghost_duration = 2000
        self.ghost_used = False     # Chỉ dùng 1 lần duy nhất     # 2 giây bất tử
        self.ghost_alpha = 80           # độ mờ (0=trong suốt, 255=bình thường)
        #PMD

        self.damage = 50                  # Sát thương mỗi đòn đánh
        self.has_dealt_damage = False       # Đã gây sát thương trong đòn tấn công này chưa
        self.damage_cooldown = 200          # Thời gian delay giữa các lần gây sát thương (ms)
        self.last_damage_time = 0           # Thời điểm gây sát thương lần cuối
        self.enemies = None                 # Danh sách kẻ địch (sẽ được gán từ game chính)
        # HIT EFFECT MANAGER
        self.hit_effect_manager = HitEffectManager()
    # THAY ĐỔI 2: Sửa handle_input để kiểm tra phím Shift với chế độ toggle
    # ===== THAY ĐỔI: Thêm xử lý dash bằng chuột phải =====
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
        
        # ===== THÊM MỚI: XỬ LÝ DASH =====
        # Xử lý dash cho dù đang attack hay không (dash có thể ngắt attack)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Chuột phải
                current_time = pygame.time.get_ticks()
                # Kiểm tra cooldown dash
                if current_time - self.last_dash_time >= self.dash_cooldown:
                    self.start_dash()
        
        # Nếu đang dash, không xử lý input di chuyển
        if self.is_dashing:
            return
        
        if not self.is_attacking:
            dx_raw = (keys[pygame.K_d] - keys[pygame.K_a])
            dy_raw = (keys[pygame.K_s] - keys[pygame.K_w])

            if dx_raw != 0 or dy_raw != 0:
                length = max((dx_raw**2 + dy_raw**2) ** 0.5, 0.1)
                
                # Kiểm tra run_mode nhấn Shift
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
                if not self.is_attacking and not self.is_dashing:  # Không attack khi đang dash
                    self.start_attack()
    
    def play_next_attack_sound(self):
        self.attack_sounds[self.current_attack_sound_index].play()
        self.current_attack_sound_index += 1
        if self.current_attack_sound_index >= len(self.attack_sounds):
            self.current_attack_sound_index = 0

    #KHỞI TẠO DASH 

    #Bắt đầu dash theo hướng hiện tại - lướt nhanh về phía trước
    def start_dash(self):
        self.is_dashing = True
        self.is_attacking = False
        self.dash_start_time = pygame.time.get_ticks()
        self.last_dash_time = self.dash_start_time
        self.dash_direction = self.direction
        
        # ===== QUAN TRỌNG: Cập nhật image NGAY =====
        self.dash_animations[self.direction].reset()
        self.image = self.dash_animations[self.direction].current_frame
        
        # Phát âm thanh
        try:
            self.dash_sound.play()
        except:
            pass
        
        # Lưu vị trí
        self.dash_start_x = self.x
        self.dash_start_y = self.y
        
        # Tính vị trí đích
        dash_vec = self.get_dash_vector()
        self.dash_target_x = self.x + dash_vec[0] * self.dash_distance
        self.dash_target_y = self.y + dash_vec[1] * self.dash_distance
        
        self.create_dash_effect()

        
    #Lấy vector đơn vị cho hướng dash
    def get_dash_vector(self):
        vectors = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0)
        }
        return vectors.get(self.dash_direction, (0, 1))
    
    def create_dash_effect(self):
        """Tạo hiệu ứng dash - có thể mở rộng để thêm particle system"""
        # TODO: Thêm particle effect, motion trail khi dash
        # Hiện tại để trống, có thể implement sau
        pass
    
     #Cập nhật dash: di chuyển nội suy và kiểm tra kết thúc
    def update_dash(self, map_width, map_height):
      
        if not self.is_dashing:
            return
        
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.dash_start_time
        progress = min(1.0, elapsed / self.dash_duration)
        
        # Sử dụng easing function ease_out_cubic để dash mượt mà
        # Bắt đầu nhanh, kết thúc chậm - tạo cảm giác lướt tự nhiên
        eased_progress = 1 - (1 - progress) ** 3
        
        # Nội suy vị trí từ start đến target
        new_x = self.dash_start_x + (self.dash_target_x - self.dash_start_x) * eased_progress
        new_y = self.dash_start_y + (self.dash_target_y - self.dash_start_y) * eased_progress
        
        # Giới hạn trong map (không cho dash ra ngoài)
        self.x = max(0, min(new_x, map_width - self.width))
        self.y = max(0, min(new_y, map_height - self.height))
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Cập nhật animation dash
        self.dash_animations[self.dash_direction].update()
        
        # Kết thúc dash khi hoàn thành 100% thời gian
        if progress >= 1.0:
            self.is_dashing = False
            # Reset kích thước về bình thường sau dash
            self.reset_sprite_size()
    
    def reset_sprite_size(self):
        """Reset kích thước sprite về bình thường sau dash"""
        # Kích thước sẽ được cập nhật lại ở frame tiếp theo khi chọn animation mới
        pass

    # Cập nhật start_attack để hỗ trợ attack_walk và kiểm tra dash
    def start_attack(self):
        self.is_attacking = True
        self.attack_start_time = pygame.time.get_ticks()
        self.sound_played_for_this_attack = False
        self.has_dealt_damage = False  # Reset trạng thái gây sát thương
        
        # Chọn animation dựa trên trạng thái di chuyển
        if self.is_running:
            # Đang chạy - dùng animation attack_run
            self.attack_run_animations[self.direction].reset()
        elif self.dx != 0 or self.dy != 0:
            # Đang di chuyển (đi bộ) - dùng animation attack_walk
            self.attack_walk_animations[self.direction].reset()
        else:
            # Đang đứng yên - dùng animation attack_idle
            self.attack_idle_animations[self.direction].reset()
        
        self.create_attack_hitbox()

    def create_attack_hitbox(self):
        # ===== CÁC THAM SỐ DỄ ĐIỀU CHỈNH =====
        # Kích thước hitbox
        hitbox_width = 60      # Độ rộng hitbox (cho hướng trái/phải)
        hitbox_height = 60     # Chiều cao hitbox (cho hướng lên/xuống)
        
        # Điều chỉnh vị trí cho từng hướng (đơn vị: pixels)
        # Giá trị dương = dịch sang phải/xuống dưới, âm = dịch sang trái/lên trên
        offset_config = {
            "up": {
                "offset_x": 0,      # Dịch ngang (so với tâm)
                "offset_y": -25,    # Dịch dọc (âm = lên trên, dương = xuống dưới)
                "width": 80,        # Độ rộng hitbox khi đánh lên
                "height": 20        # Chiều cao hitbox khi đánh lên
            },
            "down": {
                "offset_x": 0,
                "offset_y": 45,     # Dịch xuống dưới
                "width": 80,
                "height": 20
            },
            "left": {
                "offset_x": -35,    # Dịch sang trái
                "offset_y": 0,
                "width": 20,
                "height": 70
            },
            "right": {
                "offset_x": 40,     # Dịch sang phải
                "offset_y": 0,
                "width": 20,
                "height": 70
            }
        }
        
        # Lấy cấu hình cho hướng hiện tại
        config = offset_config[self.direction]
        
        # Tính tâm của player
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Tính vị trí hitbox dựa trên tâm player
        hitbox_x = center_x + config["offset_x"] - config["width"] // 2
        hitbox_y = center_y + config["offset_y"] - config["height"] // 2
        
        # Tạo hitbox
        self.attack_hitbox = pygame.Rect(
            hitbox_x,
            hitbox_y,
            config["width"],
            config["height"]
        )
    
    # ===== HÀM MỚI: Gây sát thương lên kẻ địch =====
    
    def deal_damage_to_enemies(self):
        """Gây sát thương lên tất cả kẻ địch trong vùng attack_hitbox"""
        if not self.is_attacking or self.attack_hitbox is None:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Kiểm tra cooldown
        if current_time - self.last_damage_time < self.damage_cooldown:
            return
        
        # Kiểm tra nếu đã có danh sách enemy
        if self.enemies is None:
            return
        
        # Duyệt từng enemy và kiểm tra va chạm
        for enemy in self.enemies:
            # Bỏ qua nếu enemy đã chết
            if hasattr(enemy, 'is_dead') and enemy.is_dead:
                continue
            
            # ===== QUAN TRỌNG: Dùng get_hitbox() thay vì rect =====
            if hasattr(enemy, 'get_hitbox'):
                # Lấy hitbox tròn của enemy
                enemy_hx, enemy_hy, enemy_hr = enemy.get_hitbox()
                
                # Tạo rect từ hitbox tròn (để kiểm tra va chạm với attack_hitbox)
                enemy_hitbox_rect = pygame.Rect(
                    enemy_hx - enemy_hr, 
                    enemy_hy - enemy_hr, 
                    enemy_hr * 2, 
                    enemy_hr * 2
                )
                
                # Kiểm tra va chạm với attack_hitbox
                if self.attack_hitbox.colliderect(enemy_hitbox_rect):  # ← đổi từ enemy_rect thành enemy_hitbox_rect
                    if hasattr(enemy, 'take_damage'):
                        enemy.take_damage(self.damage)
                        self.last_damage_time = current_time
                        print(f"⚔️ Player gây {self.damage} sát thương lên {enemy.__class__.__name__}!")
                        
                        # Tính vị trí va chạm
                        intersection = self.attack_hitbox.clip(enemy_hitbox_rect)  # ← đổi từ enemy_rect
                        self.hit_effect_manager.spawn(intersection.centerx, intersection.centery)
                        break
            else:
                # Fallback: nếu enemy không có get_hitbox, dùng rect cũ
                if hasattr(enemy, 'rect'):
                    if self.attack_hitbox.colliderect(enemy.rect):
                        if hasattr(enemy, 'take_damage'):
                            enemy.take_damage(self.damage)
                            self.last_damage_time = current_time
                            print(f"⚔️ Player gây {self.damage} sát thương lên {enemy.__class__.__name__}!")
                            self.hit_effect_manager.spawn(enemy.rect.centerx, enemy.rect.centery)
                            break
    """Gây sát thương lên tất cả kẻ địch trong vùng attack_hitbox"""                        
    """
    def deal_damage_to_enemies():
        
        if not self.is_attacking or self.attack_hitbox is None:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Kiểm tra cooldown
        if current_time - self.last_damage_time < self.damage_cooldown:
            return
        
        # Kiểm tra nếu đã có danh sách enemy
        if self.enemies is None:
            return
        
        # Duyệt từng enemy và kiểm tra va chạm
        for enemy in self.enemies:
            # Bỏ qua nếu enemy đã chết
            if hasattr(enemy, 'is_dead') and enemy.is_dead:
                continue
            
            # Lấy rect của enemy
            if hasattr(enemy, 'get_rect'):
                enemy_rect = enemy.get_rect()
            elif hasattr(enemy, 'rect'):
                enemy_rect = enemy.rect
            else:
                continue
            
            # Nếu attack_hitbox chạm vào enemy
            if self.attack_hitbox.colliderect(enemy_rect):
                # Gây sát thương nếu enemy có phương thức take_damage
                if hasattr(enemy, 'take_damage'):
                    enemy.take_damage(self.damage)
                    self.last_damage_time = current_time
                    print(f"⚔️ Player gây {self.damage} sát thương lên {enemy.__class__.__name__}!")
                    # SPAWN HIT EFFECT tại tâm enemy
                    #self.hit_effect_manager.spawn(enemy_rect.centerx, enemy_rect.centery)
                    intersection = self.attack_hitbox.clip(enemy_rect)
                    self.hit_effect_manager.spawn(intersection.centerx, intersection.centery)
                    break  # Chỉ gây damage cho 1 enemy mỗi lần (tránh đánh nhiều cùng lúc)
            
            # Nếu attack_hitbox chạm vào enemy
            if self.attack_hitbox.colliderect(enemy_rect):
                # Gây sát thương nếu enemy có phương thức take_damage
                if hasattr(enemy, 'take_damage'):
                    enemy.take_damage(self.damage)
                    self.last_damage_time = current_time
                    print(f"⚔️ Player gây {self.damage} sát thương lên {enemy.__class__.__name__}!")
                    # SPAWN HIT EFFECT tại tâm enemy
                    self.hit_effect_manager.spawn(enemy_rect.centerx, enemy_rect.centery)
                    break     


    """    
    # ===== HÀM MỚI: Gán danh sách enemy từ game chính =====
    def set_enemies(self, enemies):
        self.enemies = enemies
#PMD-Bất tử khi HP <= 30% với hiệu ứng mờ dần
    def take_damage(self, damage):
        if self.is_dead:
            return
        # Nếu đang ghost mode thì không nhận damage
        if self.ghost_mode:
            current_time = pygame.time.get_ticks()
            if current_time - self.ghost_start_time < self.ghost_duration:
                print("Player đang ghost mode - miễn sát thương!")
                return
            else:
                self.ghost_mode = False  # Hết 2 giây, tắt ghost
        # Trừ máu bình thường
        self.health = max(0, self.health - damage)
        print(f"Player nhận {damage} sát thương! Máu còn: {self.health}/{self.max_health}")
        if self.health <= 0:
            self.is_dead = True
            print("Player đã chết!")
            return
        # Kích hoạt ghost mode nếu HP <= 30% và chưa từng dùng
        if self.health <= self.max_health * 0.3 and not self.ghost_used:
            self.ghost_mode = True
            self.ghost_used = True
            self.ghost_start_time = pygame.time.get_ticks()
            print("⚠️ HP thấp! Ghost mode 2 giây!")
    
    # Cập nhật update_attack để hỗ trợ attack_walk
    def update_attack(self):
        # Không xử lý attack khi đang dash
        if self.is_dashing:
            return
            
        if self.is_attacking:
            current_time = pygame.time.get_ticks()
            
            if not self.sound_played_for_this_attack:
                self.play_next_attack_sound()
                self.sound_played_for_this_attack = True
            
            # Cập nhật animation phù hợp với trạng thái
            if self.is_running:
                self.attack_run_animations[self.direction].update()
            elif self.dx != 0 or self.dy != 0:
                self.attack_walk_animations[self.direction].update()
            else:
                self.attack_idle_animations[self.direction].update()
            
            # THÊM MỚI: Kiểm tra thời điểm gây sát thương (giữa chừng animation)
            attack_progress = current_time - self.attack_start_time
            if not self.has_dealt_damage and attack_progress > 100:  # Gây sát thương sau 100ms
                self.has_dealt_damage = True
                self.deal_damage_to_enemies()  # Gọi hàm gây sát thương
            
            if current_time - self.attack_start_time >= self.attack_duration:
                self.is_attacking = False
                self.attack_hitbox = None
                self.has_dealt_damage = False  # Reset cho lần tấn công sau

    # Xóa giản hóa update_running_state
    def update_running_state(self):
        # Không cần hàm này nữa vì trạng thái chạy được điều khiển hoàn toàn bằng toggle Shift
        # Giữ lại hàm rỗng để không ảnh hưởng đến code gọi nó
        pass

    def move(self, dx, dy, map_width, map_height):
        # Không di chuyển bằng input thường khi đang dash
        if self.is_dashing:
            return
            
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

    # Cập nhật phương thức update để hỗ trợ dash và attack_walk
    def update(self, map_width, map_height, events):
        # ===== QUAN TRỌNG: Xử lý input TRƯỚC để bắt dash ngay =====
        self.handle_input(events)
        
        # Sau đó mới cập nhật dash
        self.update_dash(map_width, map_height)
        
        # Nếu đang dash, chỉ cập nhật animation và thoát
        if self.is_dashing:
            self.dash_animations[self.dash_direction].update()
            self.image = self.dash_animations[self.dash_direction].current_frame
            return  # Thoát ngay, không xử lý gì thêm
        
        # Phần còn lại cho state bình thường (giữ nguyên)
        self.update_running_state()
        self.update_attack()
        self.move(self.dx, self.dy, map_width, map_height)
        self.hit_effect_manager.update()  

        # Chọn animation bình thường
        if self.is_attacking:
            if self.is_running:
                self.image = self.attack_run_animations[self.direction].current_frame
            elif self.dx != 0 or self.dy != 0:
                self.image = self.attack_walk_animations[self.direction].current_frame
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
        # ===== THÊM MỚI: Vẽ dash với kích thước sprite đặc biệt =====
        if self.is_dashing:
            # Lấy kích thước dash sprite
            dash_width, dash_height = self.dash_sprite_sizes.get(self.dash_direction, (self.width, self.height))
            
            # ===== THÊM OFFSET ĐỂ CANH CHỈNH ANIMATION BỊ LỆCH =====
            # Điều chỉnh các giá trị này để sprite dash khớp với vị trí nhân vật
            dash_sprite_offset = {
                "left": {"offset_x": 5, "offset_y": 30},   # Left: dịch XUỐNG 30px
                "right": {"offset_x": -70, "offset_y": 30}, # Right: dịch XUỐNG 30px
                "up": {"offset_x": 30, "offset_y": 0},     # Up: dịch SANG PHẢI 30px
                "down": {"offset_x": 30, "offset_y": -50}   # Down: dịch SANG PHẢI 30px
            }
            
            offset = dash_sprite_offset.get(self.dash_direction, {"offset_x": 0, "offset_y": 0})
            
            # Vẽ sprite dash với offset đã điều chỉnh
            if self.dash_direction in ["left", "right"]:
                offset_x = (self.width - dash_width) // 2
                screen_x = self.x - camera.x + offset_x + offset["offset_x"]
                screen_y = self.y - camera.y + offset["offset_y"]
            else:
                offset_y = (self.height - dash_height) // 2
                screen_x = self.x - camera.x + offset["offset_x"]
                screen_y = self.y - camera.y + offset_y + offset["offset_y"]
            #PMD-BT
            # Vẽ sprite với hiệu ứng mờ nếu đang ghost mode
            screen.blit(self.image, (screen_x, screen_y))
            #PMD-BT
            # ===== VẼ HITBOX DASH NỘI SUY GIỮA START VÀ TARGET =====
            if DEBUG_MODE:
                # Tính tiến độ dash (0 -> 1)
                current_time = pygame.time.get_ticks()
                elapsed = current_time - self.dash_start_time
                progress = min(1.0, elapsed / self.dash_duration)
                
                # ===== TÍNH VỊ TRÍ HITBOX DASH THEO NỘI SUY =====
                # Hitbox bắt đầu
                start_hitbox_x = self.dash_start_x + self.hitbox_offset_x
                start_hitbox_y = self.dash_start_y + self.hitbox_offset_y
                
                # Hitbox đích
                target_hitbox_x = self.dash_target_x + self.hitbox_offset_x
                target_hitbox_y = self.dash_target_y + self.hitbox_offset_y
                
                # Nội suy vị trí hitbox hiện tại
                current_hitbox_x = start_hitbox_x + (target_hitbox_x - start_hitbox_x) * progress
                current_hitbox_y = start_hitbox_y + (target_hitbox_y - start_hitbox_y) * progress
                
                # Vẽ hitbox xanh (hitbox thường tại vị trí hiện tại của player)
                green_hitbox_x = self.x + self.hitbox_offset_x - camera.x
                green_hitbox_y = self.y + self.hitbox_offset_y - camera.y
                pygame.draw.rect(screen, (0, 255, 0), 
                            (green_hitbox_x, green_hitbox_y, 
                                self.hitbox_width, self.hitbox_height), 2)
                

                # Vẽ hitbox vàng (hitbox dash nội suy)
                pygame.draw.rect(screen, (255, 255, 0), 
                            (current_hitbox_x - camera.x, 
                                current_hitbox_y - camera.y, 
                                self.hitbox_width, 
                                self.hitbox_height), 2)
                
                # Vẽ đường kẻ từ start đến target (debug)
                start_screen_x = start_hitbox_x - camera.x
                start_screen_y = start_hitbox_y - camera.y
                target_screen_x = target_hitbox_x - camera.x
                target_screen_y = target_hitbox_y - camera.y
                pygame.draw.line(screen, (255, 0, 255), 
                            (start_screen_x, start_screen_y), 
                            (target_screen_x, target_screen_y), 1)
        else:
            # ===== KHÔNG DASH: Vẽ sprite nhân vật =====
            screen_x = self.x - camera.x
            screen_y = self.y - camera.y
            screen.blit(self.image, (screen_x, screen_y))
            
            # ===== VẼ HITBOX NHÂN VẬT (DEBUG) =====
            if DEBUG_MODE:
                # Vẽ attack hitbox nếu đang tấn công
                if self.is_attacking and self.attack_hitbox:
                    hitbox_screen_x = self.attack_hitbox.x - camera.x
                    hitbox_screen_y = self.attack_hitbox.y - camera.y
                    pygame.draw.rect(screen, (255, 0, 0), 
                                (hitbox_screen_x, hitbox_screen_y, 
                                    self.attack_hitbox.width, self.attack_hitbox.height), 2)
                
                # Vẽ hitbox thường của nhân vật
                pygame.draw.rect(screen, (0, 255, 0), 
                            (screen_x + self.hitbox_offset_x, 
                            screen_y + self.hitbox_offset_y, 
                            self.hitbox_width, 
                            self.hitbox_height), 2)

        # VẼ HIT EFFECTS (luôn vẽ sau sprite để hiện lên trên)
        self.hit_effect_manager.draw(screen, camera)

    def get_rect(self):
        # Trả về hitbox của nhân vật (dùng cho va chạm)
        return pygame.Rect(
            self.x + self.hitbox_offset_x, 
            self.y + self.hitbox_offset_y, 
            self.hitbox_width, 
            self.hitbox_height
        )
    
    def get_attack_hitbox(self):
        return self.attack_hitbox if self.is_attacking else None
    
    # ===== THÊM MỚI: Hàm lấy trạng thái dash =====
    def is_dashing_state(self):
        """Trả về trạng thái dash hiện tại"""
        return self.is_dashing
    
    # ===== THÊM MỚI: Hàm lấy thông tin dash cooldown =====
    def get_dash_cooldown_remaining(self):
        """Lấy thời gian còn lại của cooldown dash (ms)"""
        if self.is_dashing:
            return 0
        current_time = pygame.time.get_ticks()
        remaining = self.dash_cooldown - (current_time - self.last_dash_time)
        return max(0, remaining)