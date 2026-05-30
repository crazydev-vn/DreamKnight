import pygame
import os

#================================================================================================
#GameObject dùng để biểu diễn một đối tượng trong game,
#Hỗ trợ ảnh tĩnh hoặc có animation (chuỗi ảnh).
#Hỗ trợ scale, cập nhật theo thời gian, vẽ theo camera.
#================================================================================================

class GameObject:
    #Lớp vật thể animation hoặc ảnh tĩnh
    def __init__(self, x, y, image_path=None, animation_folder=None, frame_duration=0.05, scale=1.0):
        self.x = x
        self.y = y
        self.scale = scale  
        
        # LƯU LẠI ĐƯỜNG DẪN ĐỂ DÙNG SAU NÀY (QUAN TRỌNG)
        self.image_path = image_path
        self.animation_folder = animation_folder
        
        #Khởi tạo ảnh tĩnh (nếu có)
        self.static_image = None
        if image_path:
            try:
                #Load ảnh tĩnh với hỗ trợ kênh alpha (trong suốt)
                self.static_image = pygame.image.load(image_path).convert_alpha()
                if scale != 1.0:
                    #Scale ảnh ngay nếu cần
                    self.static_image = self._scale_image(self.static_image)
                #Ảnh hiện tại đang được hiển thị (khởi đầu là ảnh tĩnh)
                self.current_image = self.static_image
            except Exception as e:
                print(f"Không thể load ảnh: {image_path} - Lỗi: {e}")
                self.static_image = None
                self.current_image = None
        else:
            # Nếu không có ảnh tĩnh, current_image sẽ được set khi load animation
            self.current_image = None
        
        #Chuẩn bị cho animation
        self.animation_frames = []  #Danh sách các frame ảnh
        self.is_animating = False   #Trạng thái đang chạy animation hay không
        self.current_frame = 0  #Chỉ số frame hiện tại
        self.timer = 0  #Bộ đếm thời gian để chuyển frame
        self.frame_duration = frame_duration
        
        #Nếu có thư mục animation thì load nó
        if animation_folder:
            self.load_animation(animation_folder)
            
    #Helper method để scale ảnh
    def _scale_image(self, image):
        if self.scale == 1.0:
            return image
        new_width = int(image.get_width() * self.scale)
        new_height = int(image.get_height() * self.scale)
        return pygame.transform.scale(image, (new_width, new_height))
    
    #Load 24 ảnh animation từ folder
    def load_animation(self, folder_path):
        try:
            # Kiểm tra thư mục tồn tại
            if not os.path.exists(folder_path):
                print(f"Thư mục không tồn tại: {folder_path}")
                return
                
            # Lấy danh sách tất cả file ảnh trong thư mục, lọc theo đuôi .png, .jpg, .jpeg
            image_files = sorted([f for f in os.listdir(folder_path) 
                                 if f.endswith(('.png', '.jpg', '.jpeg'))])
            
            # Nếu không có ảnh thì bỏ qua
            if not image_files:
                print(f"Không tìm thấy file ảnh nào trong {folder_path}")
                return
            
            # Chỉ lấy tối đa 24 ảnh (thường dùng cho animation ngắn)
            image_files = image_files[:24]
            
            # Xóa frames cũ trước khi load mới
            self.animation_frames = []
            
            # Duyệt từng file, load và scale
            for image_file in image_files:
                frame_path = os.path.join(folder_path, image_file)
                frame = pygame.image.load(frame_path).convert_alpha()
                #Scale từng frame
                if self.scale != 1.0:
                    frame = self._scale_image(frame)
                self.animation_frames.append(frame)

            #Nếu có ít nhất 1 frame thì kích hoạt animation
            if self.animation_frames:
                self.is_animating = True
                self.current_image = self.animation_frames[0]   #Hiển thị frame đầu tiên
                print(f"Đã load {len(self.animation_frames)} frame animation từ {folder_path}")
            else:
                print(f"Không tìm thấy ảnh animation trong {folder_path}")

        except Exception as e:
            print(f"Lỗi khi load animation: {e}")
    
    #Cập nhật animation theo tgian thực
    def update(self, delta_time):
        # Chỉ cập nhật nếu đang trong chế độ animation và có frames
        if not self.is_animating or not self.animation_frames:
            return
        
        #delta_time: thời gian (giây) đã trôi qua kể từ lần gọi update trước.
        self.timer += delta_time

        #Nếu đã đủ thời gian hiển thị frame hiện tại
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.current_image = self.animation_frames[self.current_frame]
    
    #Vẽ object lên surface
    def draw(self, surface, camera):
        if not self.current_image:
            return
            
        draw_x = self.x - camera.x
        draw_y = self.y - camera.y
        surface.blit(self.current_image, (draw_x, draw_y))

    #Bật animation
    def enable_animation(self):
        if self.animation_frames:
            self.is_animating = True

    #Tắt animation (chỉ hiển thị ảnh tĩnh)         
    def disable_animation(self):
        if self.static_image:
            self.is_animating = False
            self.current_image = self.static_image

    #Reset animation về frame đầu
    def reset_animation(self):
        self.current_frame = 0
        self.timer = 0
        if self.animation_frames:
            self.current_image = self.animation_frames[0]

    #Thay đổi scale sau khi đã khởi tạo
    def set_scale(self, new_scale):
        self.scale = new_scale
        # Reload lại ảnh với scale mới nếu có ảnh tĩnh
        if self.image_path and self.static_image:
            try:
                original = pygame.image.load(self.image_path).convert_alpha()
                self.static_image = self._scale_image(original)
                if not self.is_animating:
                    self.current_image = self.static_image
            except Exception as e:
                print(f"Lỗi khi reload ảnh tĩnh: {e}")
        
        # Reload lại animation với scale mới nếu có animation folder
        if self.animation_folder and self.animation_frames:
            self.load_animation(self.animation_folder)