import pygame
import os
from config import PLAYER_SPEED, RUN_SPEED

# Lớp Animation quản lý chuỗi các frame
# Lớp Animation: quản lý một chuỗi các frame ảnh để tạo hiệu ứng chuyển động.
# Tự động cập nhật frame theo thời gian dựa trên frame_duration (ms)
# Hỗ trợ reset về frame đầu tiên.
class Animation:
    def __init__(self, frames, frame_duration=90):
        self.frames = frames    # Danh sách các frame ảnh
        self.frame_count = len(frames)  # Tổng số frame
        self.frame_duration = frame_duration   # Thời gian mỗi frame (ms)
        self.current_frame_index = 0    # Chỉ số frame hiện tại
        self.last_update_time = 0   # Thời điểm cập nhật frame gần nhất (ms)
        self.current_frame = frames[0]  # Frame đang hiển thị (bắt đầu từ frame đầu)
        
    def update(self):
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_update_time > self.frame_duration:
            self.current_frame_index = (self.current_frame_index + 1) % self.frame_count
            self.current_frame = self.frames[self.current_frame_index]
            self.last_update_time = current_time
    
    def reset(self):
        self.current_frame_index = 0
        self.current_frame = self.frames[0]
        self.last_update_time = 0

# Định nghĩa cấu trúc thư mục và file cho từng animation
ANIMATION_CONFIGS = {
    "idle": {
        "folder": "knight_lv3_idle",
        "directions": {
            "up": {"prefix": "knight_lv3_idle_up", "frames": 4},
            "down": {"prefix": "knight_lv3_idle_down", "frames": 12},
            "left": {"prefix": "knight_lv3_idle_left", "frames": 12},
            "right": {"prefix": "knight_lv3_idle_right", "frames": 12}
        }
    },
    "walk": {
        "folder": "knight_lv3_walk",
        "directions": {
            "up": {"prefix": "knight_lv3_walk_up", "frames": 6},
            "down": {"prefix": "knight_lv3_walk_down", "frames": 6},
            "left": {"prefix": "knight_lv3_walk_left", "frames": 6},
            "right": {"prefix": "knight_lv3_walk_right", "frames": 6}
        }
    },
    "run": {
        "folder": "knight_lv3_run",
        "directions": {
            "up": {"prefix": "knight_lv3_run_up", "frames": 8},
            "down": {"prefix": "knight_lv3_run_down", "frames": 8},
            "left": {"prefix": "knight_lv3_run_left", "frames": 8},
            "right": {"prefix": "knight_lv3_run_right", "frames": 8}
        }
    },
    "attack_idle": {
        "folder": "knight_lv3_idle_attack",
        "directions": {
            "up": {"prefix": "knight_lv3_idle_attack_up", "frames": 8},
            "down": {"prefix": "knight_lv3_idle_attack_down", "frames": 8},
            "left": {"prefix": "knight_lv3_idle_attack_left", "frames": 8},
            "right": {"prefix": "knight_lv3_idle_attack_right", "frames": 8}
        }
    },
    "attack_walk": {  # THÊM MỚI: Tấn công khi đi bộ
        "folder": "knight_lv3_walk_attack",  # Tên thư mục chứa ảnh attack khi đi bộ
        "directions": {
            "up": {"prefix": "knight_lv3_walk_attack_up", "frames": 8},
            "down": {"prefix": "knight_lv3_walk_attack_down", "frames": 8},
            "left": {"prefix": "knight_lv3_walk_attack_left", "frames": 8},
            "right": {"prefix": "knight_lv3_walk_attack_right", "frames": 8}
        }
    },
    "attack_run": {
        "folder": "knight_lv3_run_attack",
        "directions": {
            "up": {"prefix": "knight_lv3_run_attack_up", "frames": 8},
            "down": {"prefix": "knight_lv3_run_attack_down", "frames": 8},
            "left": {"prefix": "knight_lv3_run_attack_left", "frames": 8},
            "right": {"prefix": "knight_lv3_run_attack_right", "frames": 8}
        }
    }
}

#Quản lý tất cả animations của player
class AnimationManager:
    def __init__(self, scale_factor=2.0):
        self.scale_factor = scale_factor
        self.animations_cache = {}  # Cache để tránh load lại ảnh nhiều lần
        
    #Load và scale ảnh
    def _load_and_scale_image(self, filepath):
        try:
            img = pygame.image.load(filepath).convert_alpha()
            original_size = img.get_size()
            new_size = (int(original_size[0] * self.scale_factor), 
                       int(original_size[1] * self.scale_factor))
            return pygame.transform.scale(img, new_size)
        except Exception as e:
            print(f"Error loading image {filepath}: {e}")
            # Trả về surface trắng nếu không load được
            return pygame.Surface((32, 32), pygame.SRCALPHA)
    
    #Load animation dựa trên type và direction
    def load_animation(self, animation_type, direction):
        cache_key = f"{animation_type}_{direction}"
        
        # Kiểm tra cache trước
        if cache_key in self.animations_cache:
            return self.animations_cache[cache_key]
        
        # Lấy config từ ANIMATION_CONFIGS
        config = ANIMATION_CONFIGS.get(animation_type)
        if not config:
            raise ValueError(f"Unknown animation type: {animation_type}")
        
        direction_config = config["directions"].get(direction)
        if not direction_config:
            raise ValueError(f"Unknown direction: {direction} for animation type: {animation_type}")
        
        # Load frames
        frames = []
        folder = config["folder"]
        prefix = direction_config["prefix"]
        frame_count = direction_config["frames"]
        
        for i in range(1, frame_count + 1):
            filename = f"{prefix}{i}.png"
            filepath = os.path.join("assets", "knight_lv3", folder, filename)
            scaled_img = self._load_and_scale_image(filepath)
            frames.append(scaled_img)
        
        # Cache kết quả
        self.animations_cache[cache_key] = frames
        return frames
    
    #Tạo đối tượng Animation từ type và direction
    def create_animation(self, animation_type, direction, frame_duration=90):
        frames = self.load_animation(animation_type, direction)
        return Animation(frames, frame_duration)

# Các hàm cũ (giữ lại cho tương thích)
#Load frames đứng yên
def load_idle_frames(direction):
    manager = AnimationManager()
    return manager.load_animation("idle", direction)

#Load frames đi bộ
def load_walk_frames(direction): 
    manager = AnimationManager()
    return manager.load_animation("walk", direction)

#Load frames chạy nhanh
def load_run_frames(direction):
    manager = AnimationManager()
    return manager.load_animation("run", direction)

#Load frames tấn công khi ĐỨNG YÊN
def load_attack_idle_frames(direction):
    manager = AnimationManager()
    return manager.load_animation("attack_idle", direction)

# THÊM MỚI: Load frames tấn công khi ĐI BỘ
def load_attack_walk_frames(direction):
    manager = AnimationManager()
    return manager.load_animation("attack_walk", direction)

#Load frames tấn công khi ĐANG CHẠY
def load_attack_run_frames(direction):
    manager = AnimationManager()
    return manager.load_animation("attack_run", direction)