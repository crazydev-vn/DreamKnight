import pygame
import os
from config import PLAYER_SPEED, RUN_SPEED

# Lớp Animation quản lý chuỗi các frame
class Animation:
    def __init__(self, frames, frame_duration=90):
        self.frames = frames
        self.frame_count = len(frames)
        self.frame_duration = frame_duration
        self.current_frame_index = 0
        self.last_update_time = 0
        self.current_frame = frames[0]
        
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
        "folder": "knight1_lv1_idle",
        "directions": {
            "up": {"prefix": "knight1_lv1_idle_ebove", "frames": 4},
            "down": {"prefix": "knight1_lv1_idle_under", "frames": 12},
            "left": {"prefix": "knight1_lv1_idle_left", "frames": 12},
            "right": {"prefix": "knight1_lv1_idle_right", "frames": 12}
        }
    },
    "walk": {
        "folder": "knight1_lv1_walk",
        "directions": {
            "up": {"prefix": "knight1_lv1_walk_ebove", "frames": 6},
            "down": {"prefix": "knight1_lv1_walk_under", "frames": 6},
            "left": {"prefix": "knight1_lv1_walk_left", "frames": 6},
            "right": {"prefix": "knight1_lv1_walk_right", "frames": 6}
        }
    },
    "run": {
        "folder": "knight1_lv1_run",
        "directions": {
            "up": {"prefix": "knight1_lv1_run_ebove", "frames": 8},
            "down": {"prefix": "knight1_lv1_run_under", "frames": 8},
            "left": {"prefix": "knight1_lv1_run_left", "frames": 8},
            "right": {"prefix": "knight1_lv1_run_right", "frames": 8}
        }
    },
    "attack_idle": {
        "folder": "knight1_lv1_idle_attack",
        "directions": {
            "up": {"prefix": "knight1_lv1_idle_attack_ebove", "frames": 8},
            "down": {"prefix": "knight1_lv1_idle_attack_under", "frames": 8},
            "left": {"prefix": "knight1_lv1_idle_attack_left", "frames": 8},
            "right": {"prefix": "knight1_lv1_idle_attack_right", "frames": 8}
        }
    },
    "attack_run": {
        "folder": "knight1_lv1_run_attack",
        "directions": {
            "up": {"prefix": "knight1_lv1_run_attack_ebove", "frames": 8},
            "down": {"prefix": "knight1_lv1_run_attack_under", "frames": 8},
            "left": {"prefix": "knight1_lv1_run_attack_left", "frames": 8},
            "right": {"prefix": "knight1_lv1_run_attack_right", "frames": 8}
        }
    }
}

class AnimationManager:
    """Quản lý tất cả animations của player"""
    
    def __init__(self, scale_factor=2.0):
        self.scale_factor = scale_factor
        self.animations_cache = {}  # Cache để tránh load lại ảnh nhiều lần
        
    def _load_and_scale_image(self, filepath):
        """Load và scale ảnh"""
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
    
    def load_animation(self, animation_type, direction):
        """Load animation dựa trên type và direction"""
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
            filepath = os.path.join("assets", "knight_lv1", folder, filename)
            scaled_img = self._load_and_scale_image(filepath)
            frames.append(scaled_img)
        
        # Cache kết quả
        self.animations_cache[cache_key] = frames
        return frames
    
    def create_animation(self, animation_type, direction, frame_duration=90):
        """Tạo đối tượng Animation từ type và direction"""
        frames = self.load_animation(animation_type, direction)
        return Animation(frames, frame_duration)

# Các hàm cũ (giữ lại cho tương thích)
def load_idle_frames(direction):
    """Load frames đứng yên"""
    manager = AnimationManager()
    return manager.load_animation("idle", direction)

def load_walk_frames(direction):
    """Load frames đi bộ"""
    manager = AnimationManager()
    return manager.load_animation("walk", direction)

def load_run_frames(direction):
    """Load frames chạy nhanh"""
    manager = AnimationManager()
    return manager.load_animation("run", direction)

def load_attack_idle_frames(direction):
    """Load frames tấn công khi ĐỨNG YÊN"""
    manager = AnimationManager()
    return manager.load_animation("attack_idle", direction)

def load_attack_run_frames(direction):
    """Load frames tấn công khi ĐANG CHẠY"""
    manager = AnimationManager()
    return manager.load_animation("attack_run", direction)