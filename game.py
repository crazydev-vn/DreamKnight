import pygame 
from config import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, MAP_IMAGE_PATH
from knight.knight1 import Player1
from camera import Camera

from game_object import GameObject  # Import object đơn giản
from plant_target1 import PlantTarget1   # import enemy

#Vai trò: Lớp chính điều khiển toàn bộ vòng đời của game.
#Quản lý cửa sổ, vòng lặp game, xử lý sự kiện, cập nhật logic, vẽ mọi thứ.
#phát nhạc nền. Kết nối các thành phần: player, camera, map, game object.

class Game:
    def __init__(self):
        pygame.init()
        
        # Khởi tạo mixer cho âm thanh
        pygame.mixer.init()
        
        # Tạo cửa sổ game với kích thước lấy từ config
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("DREAM KNIGHT")
        self.clock = pygame.time.Clock()    # Đồng hồ để điều khiển FPS
        
        # Load map
        self.map_image = pygame.image.load(MAP_IMAGE_PATH).convert()
        
        # Tạo player tại trung tâm bản đồ (Chỉnh ở đây để chọn vị trí chỉ định)
        self.player = Player1(
            140, 20
        )
        
        # Tạo camera với kích thước bản đồ (dùng để cắt vùng nhìn)
        self.camera = Camera(MAP_WIDTH, MAP_HEIGHT)
        
        # Tạo surface trung gian có kích thước bằng vùng nhìn của camera (đã có zoom)
        # Camera có thể zoom (view_width, view_height) – đây là kích thước vùng nhìn game
        self.game_surface = pygame.Surface((self.camera.view_width, self.camera.view_height))
        
        # Khởi tạo và phát nhạc nền
        self.setup_music()
        
        self.running = True # Cờ chạy vòng lặp game

        self.home001_object = GameObject(
            x=900, y= 10, #100, 
            image_path="assets/home/home_001.png",  # Dùng ảnh tĩnh
            animation_folder=None,
            frame_duration=None,
            scale=2.0  
        )

        # với animation từ thư mục
        self.home002_objcect = GameObject(
            #Tọa độ x, y trong game
            x= 1500 ,  y= 10,
            image_path= "assets/home2/home2.png",  # Không có ảnh tĩnh, chỉ dùng animation
            animation_folder=None, 
            frame_duration=None,    # Mỗi frame hiển thị 0.15 giây
            scale=2.0  # Tăng gấp đôi kích thước (có thể chỉnh 1.5, 2.5, 3.0...)
        )

        self.chimney_home2_object = GameObject(
            x = 1500,  y = 10,
            image_path=None,
            animation_folder= "assets/chimney",
            frame_duration=0.15,    
            scale=2.0
        )
        

        self.home_base01_object = GameObject(
            x = 200, y  = 101,
            image_path="assets/home_base/home_base01.png",
            animation_folder= None,
            frame_duration = 2.0,
            scale= 2.0,
        )
        self.dragonHome001_object = GameObject(
            #Tọa độ x, y trong game
            x= 200 ,  y= 100,
            image_path=None,  # Không có ảnh tĩnh, chỉ dùng animation
            animation_folder="assets/dragon_home", 
            frame_duration=0.15,    # Mỗi frame hiển thị 0.15 giây
            scale=2.0  # Tăng gấp đôi kích thước (có thể chỉnh 1.5, 2.5, 3.0...)
        )


        self.fences = []
        
        # Tạo nhiều hàng rào bằng vòng lặp
        fence_positions = [
            (152, 101),
            (152, 133),
            (152, 165),
            (152, 197),
            (152, 229),
            (152, 261),
            (152, 293),
            (152, 325),
            (152, 357),
            (152, 389),
            (152, 421),
            (152, 453),
            (152, 485),
            (152, 517),
            (152, 549),
            (152, 581),
            (152, 613),
            (152, 645),


            (801, 101),
            (801, 133),
            (801, 165),
            (801, 197),
            (801, 229),
            (801, 261),
            (801, 293),
            (801, 325),
            (801, 357),
            (801, 389),
            (801, 421),
            (801, 453),
            (801, 485),
            (801, 517),
            (801, 549),
            (801, 581),
            (801, 613),
            (801, 645),
            (801, 677),
            (801, 709),
            (801, 741),
            (801, 773),
            (801, 805),
            (801, 837),
            (801, 869),
            (801, 901),
            (801, 933),
            (801, 965),
            (801, 997),
            (801, 1029),
       
         
        ]
        
        for x, y in fence_positions:
            fence = GameObject(
                x=x, y=y,
                image_path="assets/fence/fence2.png",
                animation_folder=None,
                frame_duration=2.0,
                scale=2.0,
            )
            self.fences.append(fence)



    

        

        self.tree_01_object = GameObject (
            x = 800 , y = 120,
            image_path = None,
            animation_folder = "assets/tree_01",
            frame_duration = 2.0,
            scale=2.0,
        )

        self.fruit_pasket_01 = GameObject(
            x = 1225, y  = 190,
            image_path="assets/fruit_basket/fruit_basket_01.png",
            animation_folder= None,
            frame_duration = 2.0,
            scale= 1.9,
        )
        self.fruit_pasket_02 = GameObject(
            x = 1330, y  = 190,
            image_path="assets/fruit_basket/fruit_basket_02.png",
            animation_folder= None,
            frame_duration = 2.0,
            scale= 1.9,
        )

        self.fruit_pasket_03 = GameObject (
            x = 1430, y =  200,
            image_path="assets/fruit_basket/fruit_basket_03.png",
            animation_folder= None,
            frame_duration = 2.0,
            scale= 1.9,
        )

        


        # Tạo plant target
        
        self.plants = []
        
        # Danh sách tọa độ các plant được thêm vào
        plant_positions = [
            (700, 800),
            #(730, 700),
            #(760, 600),
            #(700, 600),
    
            #(800, 1000),
            #(100, 200),    # Thêm tọa độ tùy ý
            #(1800, 600),   # Thêm tọa độ tùy ý
        ]
        
        for x, y in plant_positions:
            plant = PlantTarget1(x, y, scale_factor=2.0)
            plant.set_player(self.player)
            self.plants.append(plant)

        
        #self.plant.set_player(self.player)

    #Khởi tạo và phát nhạc nền
    def setup_music(self): 
        try:
            # Load nhạc nền
            pygame.mixer.music.load("03_sounds/map/H101-62 ASPID REVISED.mp3")
            
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
        # Vai trò: xử lý các sự kiện cửa sổ (đóng, thoát, phím điều khiển nhạc).
        # Trả về danh sách events để player xử lý thêm (tấn công, di chuyển...).
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
    
    #Tắt/bật nhạc nền
    def toggle_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            print("Đã tạm dừng nhạc")
        else:
            pygame.mixer.music.unpause()
            print("Đã tiếp tục nhạc")
            
    #Thay đổi volume nhạc nền
    def change_volume(self, delta):
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

        self.home001_object.update(1/60)
        self.home002_objcect.update(1/60)
        self.chimney_home2_object.update(1/60)

        self.home001_object.update(1/60)
        self.dragonHome001_object.update(1/60)

        for fence in self.fences:
            fence.update(1/60)

        self.tree_01_object.update(1/60)
        self.fruit_pasket_01.update(1/60)
        self.fruit_pasket_02.update(1/60)
        self.fruit_pasket_03.update(1/60)

        
        


        # ========== CẬP NHẬT TẤT CẢ PLANT ==========
        for plant in self.plants:
            plant.update(1/60, MAP_WIDTH, MAP_HEIGHT)
        
        # Kiểm tra va chạm tấn công với tất cả plant
        self.check_attack_collisions()

    #Kiểm tra va chạm tấn công giữa player và tất cả plant
    def check_attack_collisions(self):
        attack_hitbox = self.player.get_attack_hitbox()
        if not attack_hitbox:
            return
        
        # Duyệt ngược để xóa an toàn
        for i in range(len(self.plants) - 1, -1, -1):
            plant = self.plants[i]
            cx, cy, radius = plant.get_hitbox()
            
            # Tìm điểm gần nhất trên attack_hitbox đến tâm plant
            closest_x = max(attack_hitbox.left, min(cx, attack_hitbox.right))
            closest_y = max(attack_hitbox.top, min(cy, attack_hitbox.bottom))
            dx = closest_x - cx
            dy = closest_y - cy
            
            if dx*dx + dy*dy < radius * radius:
                self.plants.pop(i)  # Xóa plant khi bị đánh trúng
                print(f"Plant bị tiêu diệt! Còn {len(self.plants)} plant")
    
    def draw(self):
        self.game_surface.fill((0,0,0))
        self.game_surface.blit(self.map_image, (-self.camera.x, -self.camera.y))
        
       
        self.home001_object.draw(self.game_surface, self.camera)
        
        
        self.home002_objcect.draw(self.game_surface, self.camera)
        self.chimney_home2_object.draw(self.game_surface, self.camera)




        self.home_base01_object.draw(self.game_surface, self.camera) #2
        self.dragonHome001_object.draw(self.game_surface, self.camera) #3
        
        for fence in self.fences:
            fence.draw(self.game_surface, self.camera)

        self.tree_01_object.draw(self.game_surface, self.camera)
        self.fruit_pasket_01.draw(self.game_surface, self.camera)
        self.fruit_pasket_02.draw(self.game_surface, self.camera)
        self.fruit_pasket_03.draw(self.game_surface, self.camera)

       
        
        
        # ========== VẼ TẤT CẢ PLANT ==========
        for plant in self.plants:
            plant.draw(self.game_surface, self.camera)
        
        self.player.draw(self.game_surface, self.camera)
        
        scaled_surface = pygame.transform.scale(self.game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0,0))
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
            
        # Dừng nhạc khi thoát game
        pygame.mixer.music.stop()
        pygame.quit()