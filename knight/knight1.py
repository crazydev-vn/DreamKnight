import pygame
from config import PLAYER_SPEED, RUN_SPEED, DEBUG_MODE
from knight.animation_knight import Animation, load_idle_frames, load_walk_frames, load_run_frames, load_attack_idle_frames, load_attack_run_frames

# Lớp Player kế thừa từ pygame.sprite.Sprite để sử dụng hệ thống sprite của Pygame
class Player1(pygame.sprite.Sprite):
    def __init__(self, x, y):
        # Gọi constructor của lớp cha (Sprite)
        super().__init__()

        # KHỞI TẠO CÁC BỘ ANIMATION
        
        # Animation đứng yên (idle) - mỗi frame hiển thị 200ms
        self.idle_animations = {
            "up": Animation(load_idle_frames("up"), frame_duration=200),
            "down": Animation(load_idle_frames("down"), frame_duration=200), 
            "left": Animation(load_idle_frames("left"), frame_duration=200),
            "right": Animation(load_idle_frames("right"), frame_duration=200),
        }
        
        # Animation đi bộ (walk) - mặc định 90ms/frame
        self.walk_animations = {
            "up": Animation(load_walk_frames("up")),
            "down": Animation(load_walk_frames("down")), 
            "left": Animation(load_walk_frames("left")),
            "right": Animation(load_walk_frames("right")),
        }
        
        # Animation chạy (run) - nhanh hơn, 80ms/frame
        self.run_animations = {
            "up": Animation(load_run_frames("up"), frame_duration=80),
            "down": Animation(load_run_frames("down"), frame_duration=80), 
            "left": Animation(load_run_frames("left"), frame_duration=80),
            "right": Animation(load_run_frames("right"), frame_duration=80),
        }
        
        # ANIMATIONS TẤN CÔNG HOÀN TOÀN RIÊNG BIỆT
        # Tấn công khi đứng yên - 60ms/frame cho animation nhanh
        self.attack_idle_animations = {
            "up": Animation(load_attack_idle_frames("up"), frame_duration=60),
            "down": Animation(load_attack_idle_frames("down"), frame_duration=60), 
            "left": Animation(load_attack_idle_frames("left"), frame_duration=60),
            "right": Animation(load_attack_idle_frames("right"), frame_duration=60),
        }
        
        # Tấn công khi đang chạy - 50ms/frame, nhanh nhất
        self.attack_run_animations = {
            "up": Animation(load_attack_run_frames("up"), frame_duration=50),
            "down": Animation(load_attack_run_frames("down"), frame_duration=50), 
            "left": Animation(load_attack_run_frames("left"), frame_duration=50),
            "right": Animation(load_attack_run_frames("right"), frame_duration=50),
        }

        # =============================
        # KHỞI TẠO ÂM THANH TẤN CÔNG
        # =============================
        pygame.mixer.init()
        
        # Load 5 âm thanh tấn công
        self.attack_sound_1 = pygame.mixer.Sound("sounds/attack/Sword1.mp3")
        self.attack_sound_2 = pygame.mixer.Sound("sounds/attack/Sword2.mp3")
        self.attack_sound_3 = pygame.mixer.Sound("sounds/attack/Sword3.mp3")
        self.attack_sound_4 = pygame.mixer.Sound("sounds/attack/Sword4.mp3")
        
        # Danh sách âm thanh để dễ quản lý
        self.attack_sounds = [
            self.attack_sound_1,
            self.attack_sound_2,
            self.attack_sound_3,
            self.attack_sound_4,
        ]
        
        # Chỉ số âm thanh hiện tại (bắt đầu từ 0)
        self.current_attack_sound_index = 0

        # =============================
        # BIẾN TRẠNG THÁI CỦA PLAYER
        # =============================
        self.direction = "down"  # Hướng nhìn mặc định
        self.is_running = False  # Có đang chạy không?
        self.is_attacking = False  # Có đang tấn công không?
        self.attack_start_time = 0  # Thời điểm bắt đầu tấn công
        self.attack_duration = 300  # 0.3 giây cho mỗi lần tấn công
        self.walk_start_time = 0  # Thời điểm bắt đầu đi bộ
        self.running_transition_time = 900  # 0.9 giây cần đi bộ để chuyển sang chạy
        
        # BIẾN KIỂM SOÁT PHÁT ÂM THANH
        self.sound_played_for_this_attack = False  # Đã phát âm thanh cho lần tấn công này chưa
        
        # =============================
        # HÌNH ẢNH VÀ VỊ TRÍ
        # =============================
        # Lấy frame đầu tiên của animation idle hướng down
        self.image = self.idle_animations[self.direction].current_frame
        # Tạo rectangle (hình chữ nhật) để đại diện cho player
        self.rect = self.image.get_rect(center=(x, y))

        # VỊ TRÍ THỰC CHO CAMERA (lưu số thực để di chuyển mượt)
        self.x = x  # Tọa độ X thực
        self.y = y  # Tọa độ Y thực
        self.width = self.image.get_width()  # Chiều rộng player
        self.height = self.image.get_height()  # Chiều cao player

        # VẬN TỐC
        self.dx = 0  # Vận tốc theo trục X
        self.dy = 0  # Vận tốc theo trục Y
        
        # HITBOX TẤN CÔNG
        self.debug = DEBUG_MODE  # Lấy giá trị debug từ config
        self.attack_hitbox = None  # Hitbox để phát hiện va chạm khi tấn công

    def handle_input(self, events):
        """Xử lý input từ bàn phím - WASD + Chuột"""
        # Lấy trạng thái của tất cả phím
        keys = pygame.key.get_pressed()
        
        # Xử lý di chuyển (chỉ khi không đang tấn công)
        if not self.is_attacking:
            # Tính vector di chuyển thô từ phím WASD
            dx_raw = (keys[pygame.K_d] - keys[pygame.K_a])
            dy_raw = (keys[pygame.K_s] - keys[pygame.K_w])

            # Chuẩn hóa vector (normalize) để di chuyển với tốc độ ổn định
            if dx_raw != 0 or dy_raw != 0:
                # Tính độ dài vector
                length = max((dx_raw**2 + dy_raw**2) ** 0.5, 0.1)
                # Chia cho độ dài để chuẩn hóa, nhân với tốc độ
                self.dx = (dx_raw / length) * PLAYER_SPEED
                self.dy = (dy_raw / length) * PLAYER_SPEED

                # CẬP NHẬT HƯỚNG KHI ĐANG DI CHUYỂN
                if dx_raw != 0:
                    self.direction = "right" if dx_raw > 0 else "left"
                else:
                    self.direction = "down" if dy_raw > 0 else "up"
            else:
                # Khi đứng yên, reset tốc độ
                self.dx = 0
                self.dy = 0

        # Xử lý tấn công bằng chuột trái
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.is_attacking:
                    self.start_attack()

                    
    # PHƯƠNG THỨC ÂM THANH
    def play_next_attack_sound(self):
        """Phát âm thanh tấn công tiếp theo trong danh sách (lần lượt)"""
        # Phát âm thanh hiện tại
        self.attack_sounds[self.current_attack_sound_index].play()
        
        # Tăng chỉ số lên 1 cho lần tấn công tiếp theo
        self.current_attack_sound_index += 1
        
        # Nếu đã qua âm thanh thứ 5 thì quay lại âm thanh đầu tiên
        if self.current_attack_sound_index >= len(self.attack_sounds):
            self.current_attack_sound_index = 0


    def start_attack(self):
        """Bắt đầu tấn công"""
        self.is_attacking = True
        self.attack_start_time = pygame.time.get_ticks()  # Ghi lại thời điểm bắt đầu
        self.sound_played_for_this_attack = False  # Reset cờ phát âm thanh
        
        # Reset animation tấn công - CHỌN ĐÚNG BỘ ANIMATION
        if self.is_running:
            # Nếu đang chạy, dùng animation tấn công khi chạy
            self.attack_run_animations[self.direction].reset()
        else:
            # Nếu đang đứng yên, dùng animation tấn công khi đứng yên
            self.attack_idle_animations[self.direction].reset()
        
        # Tạo hitbox tấn công để phát hiện va chạm
        self.create_attack_hitbox()

    #Hit box
    def create_attack_hitbox(self):
        """Tạo hitbox cho tấn công dựa trên hướng"""
        attack_range = 50  # Phạm vi tấn công (pixel)
        hitbox_size = 40   # Kích thước hitbox (pixel)
        
        # Tạo hitbox ở phía trước player tùy theo hướng
        if self.direction == "up":
            # Hitbox phía trên player
            self.attack_hitbox = pygame.Rect(
                self.x + self.width // 2 - hitbox_size // 2,  # Căn giữa theo chiều ngang
                self.y - attack_range,  # Phía trên player
                hitbox_size,
                attack_range
            )
        elif self.direction == "down":
            # Hitbox phía dưới player
            self.attack_hitbox = pygame.Rect(
                self.x + self.width // 2 - hitbox_size // 2,  # Căn giữa
                self.y + self.height,  # Phía dưới player
                hitbox_size,
                attack_range
            )
        elif self.direction == "left":
            # Hitbox phía trái player
            self.attack_hitbox = pygame.Rect(
                self.x - attack_range,  # Phía trái player
                self.y + self.height // 2 - hitbox_size // 2,  # Căn giữa theo chiều dọc
                attack_range,
                hitbox_size
            )
        elif self.direction == "right":
            # Hitbox phía phải player
            self.attack_hitbox = pygame.Rect(
                self.x + self.width,  # Phía phải player
                self.y + self.height // 2 - hitbox_size // 2,  # Căn giữa
                attack_range,
                hitbox_size
            )
    
    

    def update_attack(self):
        """Cập nhật trạng thái tấn công"""
        if self.is_attacking:
            current_time = pygame.time.get_ticks()
            
            # Phát âm thanh lần lượt khi bắt đầu tấn công (chỉ phát 1 lần)
            if not self.sound_played_for_this_attack:
                self.play_next_attack_sound()  # Phát âm thanh tiếp theo
                self.sound_played_for_this_attack = True
            
            # Cập nhật animation tấn công - CHỌN ĐÚNG BỘ ANIMATION
            if self.is_running:
                # Update animation tấn công khi chạy
                self.attack_run_animations[self.direction].update()
            else:
                # Update animation tấn công khi đứng yên
                self.attack_idle_animations[self.direction].update()
            
            # Kết thúc tấn công sau thời gian quy định
            if current_time - self.attack_start_time >= self.attack_duration:
                self.is_attacking = False
                self.attack_hitbox = None  # Xóa hitbox

    def update_running_state(self):
        """Cập nhật trạng thái chạy dựa trên thời gian di chuyển"""
        if self.is_attacking:
            return  # Không cập nhật trạng thái chạy khi đang tấn công
            
        current_time = pygame.time.get_ticks()
        
        if self.dx != 0 or self.dy != 0:
            # ĐANG DI CHUYỂN
            if not self.is_running:
                if self.walk_start_time == 0:
                    # BẮT ĐẦU TÍNH THỜI GIAN ĐI BỘ
                    self.walk_start_time = current_time
                elif current_time - self.walk_start_time >= self.running_transition_time:
                    # ĐỦ 0.9s - CHUYỂN SANG CHẠY
                    self.is_running = True
        else:
            # ĐỨNG YÊN - RESET TRẠNG THÁI
            self.is_running = False
            self.walk_start_time = 0

    def move(self, dx, dy, map_width, map_height):
        """Di chuyển và kiểm tra biên map"""
        # GIẢM TỐC ĐỘ KHI ĐANG TẤN CÔNG
        if self.is_attacking:
            # Nếu đang chạy thì giảm còn 30%, đứng yên giảm còn 10%
            speed_multiplier = 0.3 if self.is_running else 0.1
        else:
            # TỐC ĐỘ BÌNH THƯỜNG
            # Nếu đang chạy thì nhân với tỷ lệ RUN_SPEED/PLAYER_SPEED
            # Nếu đi bộ thì giữ nguyên tốc độ (1.0)
            speed_multiplier = RUN_SPEED / PLAYER_SPEED if self.is_running else 1.0
            
        # Tính vận tốc thực tế
        current_dx = dx * speed_multiplier
        current_dy = dy * speed_multiplier
        
        # TÍNH VỊ TRÍ MỚI
        new_x = self.x + current_dx
        new_y = self.y + current_dy
        
        # KIỂM TRA BIÊN MAP - không cho player đi ra ngoài map
        # Giới hạn X: từ 0 đến (chiều rộng map - chiều rộng player)
        if 0 <= new_x <= map_width - self.width:
            self.x = new_x
        # Giới hạn Y: từ 0 đến (chiều cao map - chiều cao player)
        if 0 <= new_y <= map_height - self.height:
            self.y = new_y
            
        # ĐỒNG BỘ RECT với vị trí thực
        self.rect.x = self.x
        self.rect.y = self.y
        
        # CẬP NHẬT HITBOX TẤN CÔNG NẾU ĐANG TẤN CÔNG
        if self.is_attacking:
            self.create_attack_hitbox()

    def update(self, map_width, map_height, events):
        """Cập nhật player mỗi frame"""
        # Xử lý input từ người chơi
        self.handle_input(events)
        # Cập nhật trạng thái chạy/đi bộ
        self.update_running_state()
        # Cập nhật trạng thái tấn công
        self.update_attack()
        # Di chuyển player
        self.move(self.dx, self.dy, map_width, map_height)

        # CHỌN VÀ CẬP NHẬT ANIMATION PHÙ HỢP
        if self.is_attacking:
            # ANIMATION TẤN CÔNG RIÊNG BIỆT
            if self.is_running:
                # Đã update trong update_attack(), chỉ cần lấy frame hiện tại
                self.image = self.attack_run_animations[self.direction].current_frame
            else:
                self.image = self.attack_idle_animations[self.direction].current_frame
        elif self.dx == 0 and self.dy == 0:
            # ĐỨNG YÊN - IDLE ANIMATION
            self.idle_animations[self.direction].update()
            self.image = self.idle_animations[self.direction].current_frame
        else:
            # ĐANG DI CHUYỂN
            if self.is_running:
                # CHẠY - Run animation
                self.run_animations[self.direction].update()
                self.image = self.run_animations[self.direction].current_frame
            else:
                # ĐI BỘ - Walk animation
                self.walk_animations[self.direction].update()
                self.image = self.walk_animations[self.direction].current_frame
    def update_debug_mode(self):
        """Cập nhật trạng thái debug từ config"""
        from config import DEBUG_MODE
        self.debug = DEBUG_MODE

    def draw(self, screen, camera):
        """Vẽ player lên screen với camera offset"""
        # Tính vị trí trên màn hình dựa vào camera
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        # Vẽ player
        screen.blit(self.image, (screen_x, screen_y))

        #"""
        # ===== DEBUG: CHỈ HIỂN THỊ HITBOX =====
        if DEBUG_MODE:  # Dùng trực tiếp từ config
            # Vẽ attack hitbox (màu đỏ)
            if self.is_attacking and self.attack_hitbox:
                hitbox_screen_x = self.attack_hitbox.x - camera.x
                hitbox_screen_y = self.attack_hitbox.y - camera.y
                pygame.draw.rect(screen, (255, 0, 0), 
                            (hitbox_screen_x, hitbox_screen_y, 
                                self.attack_hitbox.width, self.attack_hitbox.height), 2)
            
            # Vẽ player hitbox (màu xanh lá)
            pygame.draw.rect(screen, (0, 255, 0), 
                        (screen_x, screen_y, self.width, self.height), 2)
            
            #"""

    def get_rect(self):
        """Trả về hitbox của player"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    
    def get_attack_hitbox(self):
        """Trả về hitbox tấn công (nếu đang tấn công)"""
        return self.attack_hitbox if self.is_attacking else None