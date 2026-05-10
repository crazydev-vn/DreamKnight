import pygame
import os

class GameObject:
    """Lớp vật thể animation hoặc ảnh tĩnh"""
    def __init__(self, x, y, image_path, animation_folder=None, frame_duration=0.05, scale=1.0):
        self.x = x
        self.y = y
        self.scale = scale  
        
        # Load ảnh tĩnh
        try:
            self.static_image = pygame.image.load(image_path).convert_alpha()
            if scale != 1.0:
                self.static_image = self._scale_image(self.static_image)
            self.current_image = self.static_image
        except:
            print(f"Không thể load ảnh: {image_path}")
            self.static_image = None
            self.current_image = None
        
        # Load animation nếu có
        self.animation_frames = []
        self.is_animating = False
        self.current_frame = 0
        self.timer = 0
        self.frame_duration = frame_duration
        
        if animation_folder:
            self.load_animation(animation_folder)
    
    def _scale_image(self, image):
        """Helper method để scale ảnh"""
        if self.scale == 1.0:
            return image
        new_width = int(image.get_width() * self.scale)
        new_height = int(image.get_height() * self.scale)
        return pygame.transform.scale(image, (new_width, new_height))
    
    def load_animation(self, folder_path):
        """Load 24 ảnh animation từ folder"""
        try:
            # Lấy tất cả file ảnh trong folder và sắp xếp
            image_files = sorted([f for f in os.listdir(folder_path) 
                                 if f.endswith(('.png', '.jpg', '.jpeg'))])
            
            # Lấy 24 ảnh đầu tiên (hoặc tất cả nếu ít hơn)
            image_files = image_files[:24]
            
            for image_file in image_files:
                frame = pygame.image.load(os.path.join(folder_path, image_file)).convert_alpha()
                # Scale từng frame
                if self.scale != 1.0:
                    frame = self._scale_image(frame)
                self.animation_frames.append(frame)
            
            if self.animation_frames:
                self.is_animating = True
                self.current_image = self.animation_frames[0]
                print(f"Đã load {len(self.animation_frames)} frame animation từ {folder_path}")
            else:
                print(f"Không tìm thấy ảnh animation trong {folder_path}")
                
        except Exception as e:
            print(f"Lỗi khi load animation: {e}")
    
    def update(self, delta_time):
        """Cập nhật animation"""
        if not self.is_animating or not self.animation_frames:
            return
        
        self.timer += delta_time
        
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.current_image = self.animation_frames[self.current_frame]
    
    def draw(self, surface, camera):
        """Vẽ object lên surface"""
        if not self.current_image:
            return
            
        draw_x = self.x - camera.x
        draw_y = self.y - camera.y
        surface.blit(self.current_image, (draw_x, draw_y))
    
    def enable_animation(self):
        """Bật animation"""
        if self.animation_frames:
            self.is_animating = True
            
    def disable_animation(self):
        """Tắt animation (chỉ hiển thị ảnh tĩnh)"""
        self.is_animating = False
        self.current_image = self.static_image
    
    def reset_animation(self):
        """Reset animation về frame đầu"""
        self.current_frame = 0
        self.timer = 0
        if self.animation_frames:
            self.current_image = self.animation_frames[0]
    
    def set_scale(self, new_scale):
        """Thay đổi scale sau khi đã khởi tạo"""
        self.scale = new_scale
        # Reload lại ảnh với scale mới
        if self.static_image:
            original = pygame.image.load(self.image_path).convert_alpha()
            self.static_image = self._scale_image(original)
        if self.animation_frames:
            # Reload lại animation với scale mới
            self.load_animation(self.animation_folder)