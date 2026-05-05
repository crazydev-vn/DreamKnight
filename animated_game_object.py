import pygame
import os

class AnimatedObject:
    """Lớp vật thể có animation"""
    def __init__(self, x, y, static_image_path, animation_folder, frame_duration=0.05):
        self.x = x
        self.y = y
        
        # Load ảnh tĩnh
        self.static_image = pygame.image.load(static_image_path).convert_alpha()
        
        # Load animation frames
        self.animation_frames = []
        self.load_animation_frames(animation_folder)
        
        self.current_frame = 0
        self.frame_duration = frame_duration  # Thời gian mỗi frame (giây)
        self.timer = 0
        self.animation_enabled = True  # Bật/tắt animation
        self.current_image = self.static_image
        
    def load_animation_frames(self, folder_path):
        """Load tất cả ảnh animation từ folder"""
        try:
            # Lấy tất cả file ảnh trong folder và sắp xếp
            image_files = sorted([f for f in os.listdir(folder_path) 
                                 if f.endswith(('.png', '.jpg', '.jpeg'))])
            
            # Giới hạn 24 ảnh đầu tiên
            image_files = image_files[:24]
            
            for image_file in image_files:
                frame = pygame.image.load(os.path.join(folder_path, image_file)).convert_alpha()
                self.animation_frames.append(frame)
            
            print(f"Đã load {len(self.animation_frames)} frame animation từ {folder_path}")
        except Exception as e:
            print(f"Lỗi khi load animation: {e}")
    
    def update(self, delta_time):
        """Cập nhật animation"""
        if not self.animation_enabled or not self.animation_frames:
            self.current_image = self.static_image
            return
        
        self.timer += delta_time
        
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.current_image = self.animation_frames[self.current_frame]
    
    def draw(self, surface, camera):
        """Vẽ object"""
        draw_x = self.x - camera.x
        draw_y = self.y - camera.y
        surface.blit(self.current_image, (draw_x, draw_y))
    
    def enable_animation(self):
        """Bật animation"""
        self.animation_enabled = True
        
    def disable_animation(self):
        """Tắt animation (chỉ hiển thị ảnh tĩnh)"""
        self.animation_enabled = False
        self.current_image = self.static_image