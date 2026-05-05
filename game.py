import pygame 
from config import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, MAP_IMAGE_PATH
from knight.knight1 import Player1
from camera import Camera

from game_object import GameObject  # Import object đơn giản

class Game:
    def __init__(self):
        pygame.init()
        
        # Khởi tạo mixer cho âm thanh
        pygame.mixer.init()
        
        # Tạo cửa sổ game
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("DREAM KNIGHT")
        self.clock = pygame.time.Clock()
        
        # Load map
        self.map_image = pygame.image.load(MAP_IMAGE_PATH).convert()
        
        # Tạo player
        self.player = Player1(MAP_WIDTH // 2, MAP_HEIGHT // 2)
        
        # Tạo camera
        self.camera = Camera(MAP_WIDTH, MAP_HEIGHT)
        
        # Tạo game surface với kích thước ĐÃ ZOOM của camera
        self.game_surface = pygame.Surface((self.camera.view_width, self.camera.view_height))
        
        # Khởi tạo và phát nhạc nền
        self.setup_music()
        
        self.running = True

        self.dragonHome001_object = GameObject(
            x=140,
            y=20,
            image_path=None,  # Có thể để None nếu dùng animation
            animation_folder="do_assets/Dragon_Home001",
            frame_duration=0.15,
            scale=2.0  # Tăng gấp đôi kích thước (có thể chỉnh 1.5, 2.5, 3.0...)
        )
        
    def setup_music(self): 
        """Khởi tạo và phát nhạc nền"""
        try:
            # Load nhạc nền
            pygame.mixer.music.load("sounds/map/001_Greenpath.mp3")
            
            # Cài đặt volume nhạc (0.0 đến 1.0)
            pygame.mixer.music.set_volume(0.5)  # 50% volume
            
            # Phát nhạc lặp vô hạn (-1 là lặp mãi mãi)
            pygame.mixer.music.play(-1)
            
            print("Đang phát nhạc nền...")
        except FileNotFoundError:
            print("Không tìm thấy file nhạc nền! Bỏ qua phát nhạc.")
        except pygame.error as e:
            print(f"Lỗi khi phát nhạc: {e}")

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # Thêm phím tắt điều khiển nhạc
                elif event.key == pygame.K_m:  # Phím M để tắt/bật nhạc
                    self.toggle_music()
                elif event.key == pygame.K_UP:  # Phím lên để tăng volume
                    self.change_volume(0.1)
                elif event.key == pygame.K_DOWN:  # Phím xuống để giảm volume
                    self.change_volume(-0.1)
        
        # TRẢ VỀ EVENTS ĐỂ PLAYER XỬ LÝ TẤN CÔNG
        return events
    
    def toggle_music(self):
        """Tắt/bật nhạc nền"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            print("Đã tạm dừng nhạc")
        else:
            pygame.mixer.music.unpause()
            print("Đã tiếp tục nhạc")

    def change_volume(self, delta):
        """Thay đổi volume nhạc nền"""
        current_volume = pygame.mixer.music.get_volume()
        new_volume = current_volume + delta
        # Giới hạn volume trong khoảng 0.0 đến 1.0
        new_volume = max(0.0, min(1.0, new_volume))
        pygame.mixer.music.set_volume(new_volume)
        print(f"Volume nhạc: {new_volume:.1f}")

    def update(self):
        # LẤY EVENTS VÀ TRUYỀN CHO PLAYER
        events = self.handle_events()
        
        # Cập nhật player VỚI EVENTS (để xử lý tấn công)
        self.player.update(MAP_WIDTH, MAP_HEIGHT, events)
        
        # Cập nhật camera để theo dõi player
        self.camera.update(self.player)

        self.dragonHome001_object.update(1/60)
    
    def draw(self):
        # Vẽ lên game_surface (vùng nhìn đã ZOOM)
        self.game_surface.fill((0, 0, 0))  # Nền đen
        
        # Vẽ map với camera offset
        map_x = -self.camera.x
        map_y = -self.camera.y
        self.game_surface.blit(self.map_image, (map_x, map_y))
        
        #self.my_object.draw(self.game_surface, self.camera)

        self.dragonHome001_object.draw(self.game_surface, self.camera)
        
        # Vẽ player với camera offset
        self.player.draw(self.game_surface, self.camera)
        
        # Scale game_surface lên toàn bộ màn hình
        scaled_surface = pygame.transform.scale(self.game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
            
        # Dừng nhạc khi thoát game
        pygame.mixer.music.stop()
        pygame.quit()