import pygame 
from config import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, MAP_IMAGE_PATH
from knight1 import Player1
from camera import Camera

from game_object import GameObject  
from plant_target1 import PlantTarget1   
from slime2_target import Slime2
from test01 import Test01
from ui import UI, PauseMenu  # ← Import cả PauseMenu
#================================================================================================
#Vai trò: Lớp chính điều khiển toàn bộ vòng đời của game.
#Quản lý cửa sổ, vòng lặp game, xử lý sự kiện, cập nhật logic, vẽ mọi thứ.
#phát nhạc nền. Kết nối các thành phần: player, camera, map, game object.
#================================================================================================
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
            400, 450
        )
        
        # Tạo camera với kích thước bản đồ (dùng để cắt vùng nhìn)
        self.camera = Camera(MAP_WIDTH, MAP_HEIGHT)
        
        # Tạo surface trung gian có kích thước bằng vùng nhìn của camera (đã có zoom)
        # Camera có thể zoom (view_width, view_height) – đây là kích thước vùng nhìn game
        self.game_surface = pygame.Surface((self.camera.view_width, self.camera.view_height))
        
        # Khởi tạo và phát nhạc nền
        self.setup_music()
        
        self.running = True # Cờ chạy vòng lặp game
        self.game_over = False  # Trạng thái game over
        self.ui = UI()              # Khởi tạo giao diện HUD
        self.pause_menu = PauseMenu()  # Khởi tạo menu tạm dừng

        self.home001_object = GameObject(
            x=900, y= 10, #100, 
            image_path="assets/home/home_001.png",  # Dùng ảnh tĩnh
            animation_folder=None,
            frame_duration=None,
            scale=2.0,
        )
        self.sampleNPC_object = GameObject (
            x = 1100, y = 300,
            image_path=None,  # Không có ảnh tĩnh, chỉ dùng animation
            animation_folder="assets/sample", 
            frame_duration=0.1,    # Mỗi frame hiển thị 0.15 giây
            scale= 1.0,  # Tăng gấp đôi kích thước (có thể chỉnh 1.5, 2.5, 3.0...)
        )

        # với animation từ thư mục
        self.home002_object = GameObject(  # ← SỬA: đúng chính tả
            #Tọa độ x, y trong game
            x= 1500 ,  y= 10,
            image_path= "assets/home2/home2.png",
            animation_folder=None, 
            frame_duration=None,
            scale=2.0 
        )
        self.chimney_home2_object = GameObject(
            x = 1500,  y = 10,
            image_path=None,
            animation_folder = "assets/chimney",
            frame_duration = 0.15,    
            scale = 2.0,
        )

        self.lunebladeNPC_object = GameObject (
            x = 1100, y = 700,
            image_path=None,  # Không có ảnh tĩnh, chỉ dùng animation
            animation_folder="assets/luneblade", 
            frame_duration=0.1,    # Mỗi frame hiển thị 0.15 giây
            scale= 2.0,  # Tăng gấp đôi kích thước (có thể chỉnh 1.5, 2.5, 3.0...)
        )

        #Home 3
        self.home003_object = GameObject(
            x = 950, y  = 410,
            image_path="assets/home3/home3.png",
            animation_folder = None,
            frame_duration = None,
            scale = 2.0,
        )
        self.flag1_object = GameObject (
            x = 950, y = 410,
            image_path = None,
            animation_folder = "assets/flag1",
            frame_duration = 0.6,
            scale = 2.0,
        )

        #NỀN 
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
            (152, 101), (152, 133), (152, 165), (152, 197), (152, 229), (152, 261),
            (152, 293), (152, 325), (152, 357), (152, 389), (152, 421), (152, 453),
            (152, 485), (152, 517), (152, 549), (152, 581), (152, 613), (152, 645),

            (801, 101), (801, 133), (801, 165), (801, 197), (801, 229), (801, 261),
            (801, 293), (801, 325), (801, 357), (801, 389), (801, 421), (801, 453),
            (801, 485), (801, 517), (801, 549), (801, 581), (801, 613), (801, 645),
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
            x = 830 , y = 120,
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
            scale= 2.0,
        )

        self.fruit_pasket_02 = GameObject(
            x = 1330, y  = 190,
            image_path="assets/fruit_basket/fruit_basket_02.png",
            animation_folder= None,
            frame_duration = 2.0,
            scale= 2.0,
        )

        self.fruit_pasket_03 = GameObject (
            x = 1430, y =  200,
            image_path="assets/fruit_basket/fruit_basket_03.png",
            animation_folder= None,
            frame_duration = 2.0,
            scale= 2.0,
        )

        # Tạo plant target
        self.plants = []
        
        # Danh sách tọa độ các plant được thêm vào
        plant_positions = [
            #(700, 800),
            #(760, 600),
            #(700, 600),
            #(800, 1000),
            #(100, 200),
            #(1800, 600),
        ]
        for x, y in plant_positions:
            plant = PlantTarget1(x, y, scale_factor=2.0)
            plant.set_player(self.player)
            self.plants.append(plant)
           
        self.slimes2 = []
        # Danh sách tọa độ các slime 2 được thêm vào
        slime2_positions = [
            #(730, 700), (760, 620), (800, 600),
            #(700, 600),
            #(800, 1000),
            #(100, 200),
            #(1800, 600),
        ]
        for x, y in slime2_positions:
            slime2 = Slime2(x, y, scale_factor=2.0)
            slime2.set_player(self.player)
            self.slimes2.append(slime2)

        self.test01 = []
        # Danh sách tọa độ các test 01 được thêm vào (COMMENT lại nếu chưa muốn có quái)
        test01_positions = [
            (730, 700), (760, 620), (800, 600),  # COMMENT hết
            (700, 600),
            (800, 1000),
            (100, 200),
            (1800, 600),
        ]
        for x, y in test01_positions:
            test01 = Test01(x, y, scale_factor=2.0)
            test01.set_player(self.player)
            self.test01.append(test01)
        
        # Gán danh sách enemy cho player
        self.player.set_enemies(self.slimes2 + self.test01)

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
        # Xử lý các sự kiện cửa sổ (đóng, thoát, phím điều khiển nhạc)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = self.pause_menu.handle_click(event.pos, SCREEN_WIDTH, SCREEN_HEIGHT)
                if action == "quit":
                    self.running = False
                # Click nút Play Again khi game over
                if self.game_over:
                    box_w, box_h = 360, 260
                    box_x = (SCREEN_WIDTH  - box_w) // 2
                    box_y = (SCREEN_HEIGHT - box_h) // 2
                    btn_w, btn_h = 220, 44
                    btn_x = box_x + (box_w - btn_w) // 2
                    #PMD-Thêm đúng 3 dòng ghost_mode, ghost_used, ghost_start_time là xong. 
                    #Lần chơi mới sẽ có ghost mode bình thường trở lại.
                    if pygame.Rect(btn_x, box_y + 140, btn_w, btn_h).collidepoint(event.pos):
                        self.player.health = self.player.max_health
                        self.player.is_dead = False
                        self.player.ghost_mode = False
                        self.player.ghost_used = False
                        self.player.ghost_start_time = 0
                        self.player.x = 400
                        self.player.y = 450
                        self.player.rect.center = (400, 450)
                        self.game_over = False
                        pygame.mixer.music.unpause()
                        #PMD
            elif event.type == pygame.KEYDOWN:
                # Xử lý phím khi Game Over
                if self.game_over:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    continue  # Bỏ qua các phím khác khi game over

                if event.key == pygame.K_ESCAPE:
                    self.pause_menu.toggle()
                    if self.pause_menu.visible:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_m:  # Phím M để tắt/bật nhạc
                    self.toggle_music()
                elif event.key == pygame.K_UP:  # Phím lên để tăng volume
                    self.change_volume(0.1)
                elif event.key == pygame.K_DOWN:  # Phím xuống để giảm volume
                    self.change_volume(-0.1)

        # Không truyền events cho player khi đang pause hoặc game over
        if self.pause_menu.visible or self.game_over:
            return []
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
        # Chỉnh nhạc nền
        pygame.mixer.music.set_volume(new_volume)
        # Chỉnh luôn tất cả SFX (chém, dash, quái...)
        for channel in range(pygame.mixer.get_num_channels()):
            pygame.mixer.Channel(channel).set_volume(new_volume)

    def update(self):
        # LẤY EVENTS VÀ TRUYỀN CHO PLAYER
        events = self.handle_events()

        # Kiểm tra player chết → kích hoạt game over
        if self.player.is_dead and not self.game_over:
            self.game_over = True
            pygame.mixer.music.pause()
            pygame.mixer.stop()  # Dừng toàn bộ SFX

        # Nếu game over hoặc đang pause thì không update gì cả
        if self.game_over or self.pause_menu.visible:
            return

        # Cập nhật player VỚI EVENTS (để xử lý tấn công)
        self.player.update(MAP_WIDTH, MAP_HEIGHT, events)

        # Cập nhật camera để theo dõi player
        self.camera.update(self.player)

        self.home001_object.update(1/60)
        self.home002_object.update(1/60)  # ← SỬA: tên biến đúng
        self.chimney_home2_object.update(1/60)
        self.home003_object.update(1/60)
        self.flag1_object.update(1/60)
        self.lunebladeNPC_object.update(1/60)
        self.dragonHome001_object.update(1/60)
        self.sampleNPC_object.update(1/60)

        for fence in self.fences:
            fence.update(1/60)

        self.tree_01_object.update(1/60)
        self.fruit_pasket_01.update(1/60)
        self.fruit_pasket_02.update(1/60)
        self.fruit_pasket_03.update(1/60)

        # CẬP NHẬT TẤT CẢ PLANT
        for plant in self.plants:
            plant.update(1/60, MAP_WIDTH, MAP_HEIGHT)

        # CẬP NHẬT TẤT CẢ SLIME2
        for slime2 in self.slimes2:
            slime2.update(1/60, MAP_WIDTH, MAP_HEIGHT)

        # CẬP NHẬT TẤT CẢ TEST01
        for test01 in self.test01:
            test01.update(1/60, MAP_WIDTH, MAP_HEIGHT)

        # Xử lý va chạm
        self.check_plant_collisions()
        self.remove_dead_slimes()
        self.remove_dead_tests()

    def check_plant_collisions(self):
        attack_hitbox = self.player.get_attack_hitbox()
        if not attack_hitbox:
            return
        
        for i in range(len(self.plants) - 1, -1, -1):
            plant = self.plants[i]
            cx, cy, radius = plant.get_hitbox()
            
            closest_x = max(attack_hitbox.left, min(cx, attack_hitbox.right))
            closest_y = max(attack_hitbox.top, min(cy, attack_hitbox.bottom))
            dx = closest_x - cx
            dy = closest_y - cy
            
            if dx*dx + dy*dy < radius * radius:
                self.plants.pop(i)
                print(f"Plant bị tiêu diệt! Còn {len(self.plants)} plant")

    def remove_dead_slimes(self):
        before_count = len(self.slimes2)
        self.slimes2 = [slime for slime in self.slimes2 if not slime.fully_dead]
        if before_count != len(self.slimes2):
            print(f"Đã xóa {before_count - len(self.slimes2)} slime2 chết")
            self.player.set_enemies(self.slimes2 + self.test01)

    def remove_dead_tests(self):
        before_count = len(self.test01)
        self.test01 = [test for test in self.test01 if not test.fully_dead]
        if before_count != len(self.test01):
            print(f"Đã xóa {before_count - len(self.test01)} test chết")
            self.player.set_enemies(self.slimes2 + self.test01)

    def draw(self):
        self.game_surface.fill((0,0,0))
        self.game_surface.blit(self.map_image, (-self.camera.x, -self.camera.y))
        
        self.home001_object.draw(self.game_surface, self.camera)
        self.home002_object.draw(self.game_surface, self.camera)  
        self.chimney_home2_object.draw(self.game_surface, self.camera)
        self.home003_object.draw(self.game_surface, self.camera)
        self.flag1_object.draw(self.game_surface, self.camera)
        self.lunebladeNPC_object.draw(self.game_surface, self.camera)
        self.sampleNPC_object.draw(self.game_surface, self.camera)
        self.tree_01_object.draw(self.game_surface, self.camera)
        self.fruit_pasket_01.draw(self.game_surface, self.camera)
        self.fruit_pasket_02.draw(self.game_surface, self.camera)
        self.fruit_pasket_03.draw(self.game_surface, self.camera)
        
        # VẼ TẤT CẢ PLANT 
        for plant in self.plants:
            plant.draw(self.game_surface, self.camera)

        # VẼ TẤT CẢ SLIME2
        for slime2 in self.slimes2:
            slime2.draw(self.game_surface, self.camera)

        # VẼ TẤT CẢ test01
        for test01 in self.test01:
            test01.draw(self.game_surface, self.camera)
                
        self.player.draw(self.game_surface, self.camera)
        
        scaled_surface = pygame.transform.scale(self.game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0,0))
        
        # Vẽ HUD lên screen (sau khi scale để không bị zoom)
        self.ui.draw(self.screen, self.player, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Vẽ Pause Menu lên trên cùng
        self.pause_menu.draw(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Đã xóa: self.pause_menu.draw(...)

        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
            
        # Dừng nhạc khi thoát game
        pygame.mixer.music.stop()
        pygame.quit()