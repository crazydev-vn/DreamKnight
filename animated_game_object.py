import pygame
import os
 
# Lớp AnimatedObject - đại diện cho một vật thể trong game có thể hiển thị ảnh tĩnh
# Chạy animation từ một thư mục chứa nhiều frame ảnh.
# Hỗ trợ bật/tắt animation, cập nhật theo thời gian, vẽ theo camera.

class AnimatedObject:
    """Lớp vật thể có animation"""
    def __init__(self, x, y, static_image_path, animation_folder, frame_duration=0.05):
        self.x = x
        self.y = y
        
        # Load ảnh tĩnh
        self.static_image = pygame.image.load(static_image_path).convert_alpha()
        
         # ----- Load animation frames -----
        self.animation_frames = []  # Danh sách chứa các Surface ảnh của từng frame
        self.load_animation_frames(animation_folder)    # Gọi phương thức load frame từ thư mục
        
        # ----- Các biến điều khiển animation -----
        self.current_frame = 0  # Chỉ số frame hiện tại (0 -> n-1)
        self.frame_duration = frame_duration  # Thời gian mỗi frame (giây)
        self.timer = 0  # Bộ đếm thời gian để chuyển frame
        self.animation_enabled = True  # Cờ: True = đang chạy animation, False = dùng ảnh tĩnh
        self.current_image = self.static_image  # Ảnh đang được hiển thị (khởi tạo là ảnh tĩnh)
        
    def load_animation_frames(self, folder_path):
        """Load tất cả ảnh animation từ folder"""
        try:
            # Lấy danh sách tên file ảnh trong thư mục, lọc theo đuôi mở rộng
            image_files = sorted([f for f in os.listdir(folder_path) 
                                 if f.endswith(('.png', '.jpg', '.jpeg'))])
            
            # Chỉ lấy tối đa 24 frame đầu tiên (thường đủ cho animation ngắn)
            image_files = image_files[:24]
            
            # Duyệt từng file, load ảnh và thêm vào danh sách frame
            for image_file in image_files:
                frame = pygame.image.load(os.path.join(folder_path, image_file)).convert_alpha()
                self.animation_frames.append(frame)
            
            print(f"Đã load {len(self.animation_frames)} frame animation từ {folder_path}")
        except Exception as e:
            print(f"Lỗi khi load animation: {e}")
    
    def update(self, delta_time):
        """Cập nhật animation""" 
        # Nếu animation bị tắt HOẶC không có frame nào -> hiển thị ảnh tĩnh
        if not self.animation_enabled or not self.animation_frames:
            self.current_image = self.static_image
            return
        
        # Tăng bộ đếm thời gian
        self.timer += delta_time
        
        # Khi đã đủ thời gian cho frame hiện tại, chuyển sang frame tiếp theo
        if self.timer >= self.frame_duration:
            self.timer = 0
            # Tăng chỉ số frame, quay vòng về 0 khi hết danh sách
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            # Cập nhật ảnh hiện tại là frame mới
            self.current_image = self.animation_frames[self.current_frame]
    
    def draw(self, surface, camera):
        """Vẽ object"""
        # Tính tọa độ vẽ trên surface = tọa độ thế giới - tọa độ camera
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