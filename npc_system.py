from multiprocessing.resource_sharer import stop

import pygame
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT

#================================================================================================
# CLASS NPCSYSTEM
# Quản lý toàn bộ hệ thống tương tác với các nhân vật máy (NPC) trong trò chơi.
# Xử lý tính toán khoảng cách thực tế, kích hoạt biểu tượng cảm xúc, điều khiển kịch bản hội thoại
# phân nhánh bằng phím F và quản lý trạng thái hiển thị giao diện các cửa hàng (Shop).
#================================================================================================
class NPCSystem:
    
    # ------------------------------------------------------------------
    # KHỞI TẠO HỆ THỐNG NPC
    # ------------------------------------------------------------------
    def __init__(self):
        # Các cờ trạng thái điều khiển vòng lặp và giao diện của trò chơi
        self.is_showing_dialogue = False  # Cờ bật/tắt hiển thị hộp thoại nói chuyện
        self.is_showing_shop = False      # Cờ bật/tắt hiển thị bảng giao diện cửa hàng
        self.shop_type = None              # Lưu loại shop đang mở: "vat pham" hoặc "ky nang"
        
        self.active_npc_id = None          # ID của NPC mà người chơi đang đứng ở gần (1 hoặc 2)
        self.current_step = 0              # Tiến trình câu thoại hiện tại đang đọc (Bắt đầu từ 0)
        self.selected_option = 0           # Lựa chọn shop tại câu cuối: 0 là Vật Phẩm, 1 là Kỹ Năng
       
        # ===== DỮ LIỆU SHOP =====
        self.shop_selected_index = 0  # Chỉ số lựa chọn hiện tại trong cửa hàng (Dùng để điều khiển di chuyển lên xuống giữa các mục)                                               
        self.item_shop = [
            {
                "name": "Apple",
                "price": 20,
                "heal": 20,
                "image": "assets/shop/apple.png"
            },
            {
                "name": "Orange",
                "price": 40,
                "heal": 40,
                "image": "assets/shop/orange.png"
            },
            {
                "name": "Watermelon",
                "price": 80,
                "heal": 80,
                "image": "assets/shop/watermelon.png"
            },
            {
                "name": "Golden Fruit",
                "price": 150,
                "heal": 150,
                "image": "assets/shop/golden_fruit.png"
            }
        ]

        self.skill_shop = [
            {
                "name": "Fast Slash",
                "price": 100
            },
            {
                "name": "Quick Dash",
                "price": 150
            },
            {
                "name": "Long Slash",
                "price": 200
            },
            {
                "name": "Power Slash",
                "price": 250
            }
        ]

        # Kịch bản kịch tính phù hợp với ngoại hình nhân vật (Chữ hiển thị trong game bắt buộc KHÔNG DẤU)
        self.npc_data = {
            1: {
                "name": "Lilith (Thuong Nhan Toc Quy) Xin Chao Hanh Gia!",
                "dialogues": {
                    0: "Lilith: Su dung cam cua nguoi lam ta thay rat thu vi day, chang hanh gia tre...",
                    1: "Lilith: Lu Slime ngoai kia dang khao khat linh hon cua nguoi. Nguoi khong the di tay khong.",
                    2: "Lilith: Hay doi trac voi ta! Nguoi muon on dinh sinh menh bang Vat Pham, hay muon hoc Ky Nang phap thuat de thieu rui chung?" 
                }
            },
            2: {
                "name": "Kaelen (Truong Lao Guild Hall) Xin Chao Hanh Gia!",
                "dialogues": {
                    0: "Kaelen: Ta giu trong trach quan ly Guild Hall de dan dat cac hiep si tre tuoi nhu nguoi.",
                    1: "Kaelen: Hay chuan bi day du trang bi tu Lilith truoc khi buoc vao vung dat cua lu Slime.",
                    2: "Kaelen: Tieu diet lu quai vat se giup nguoi co vang de giao dich. Chuc may man!"
                }
            }
        }

    # ------------------------------------------------------------------
    # CẬP NHẬT TRẠNG THÁI (KHOẢNG CÁCH NPC ĐỘNG)
    # ------------------------------------------------------------------
    def update(self, player, game_instance):
        """Tính toán khoảng cách giữa người chơi và tọa độ thực tế của NPC lấy từ game.py"""
        # Nếu đang mở hộp thoại hoặc đang xem Shop thì đóng băng hệ thống quét khoảng cách
        if self.is_showing_dialogue or self.is_showing_shop:
            return

        # Lấy trực tiếp đối tượng thực thể động đang chạy hoạt ảnh xoay từ game.py
        npc_objects = {
            1: game_instance.sampleNPC_object,
            2: game_instance.lunebladeNPC_object
        }

        # Lấy tâm vị trí thực tế của nhân vật người chơi (Player)
        player_cx = player.x + player.width // 2
        player_cy = player.y + player.height // 2

        # Vòng lặp kiểm tra khoảng cách thực của từng NPC đang đứng trên bản đồ
        for npc_id, npc_obj in npc_objects.items():
            if npc_obj:
                # Tính toán tâm của NPC dựa theo kích thước khung hình ảnh thực tế đang hiển thị
                img_w = npc_obj.current_image.get_width() if npc_obj.current_image else 32
                img_h = npc_obj.current_image.get_height() if npc_obj.current_image else 48
                
                npc_cx = npc_obj.x + img_w // 2
                npc_cy = npc_obj.y + img_h // 2
                
                # Công thức Pythagore tính khoảng cách giữa người chơi và thực thể NPC thô
                distance = math.hypot(npc_cx - player_cx, npc_cy - player_cy)
                
                # Nếu đứng gần trong phạm vi 80 pixel, khóa mục tiêu tương tác để chuẩn bị hiện chữ ! [F]
                if distance <= 80: 
                    self.active_npc_id = npc_id
                    return
                
        # Nếu đi ra xa khỏi tất cả phạm vi của các NPC thì hủy mục tiêu tương tác về rỗng
        self.active_npc_id = None

    # ------------------------------------------------------------------
    # XỬ LÝ SỰ KIỆN PHÍM BẤM (BÀN PHÍM)
    # ------------------------------------------------------------------
    def handle_keydown(self, key):
        """Hành động xử lý khi người chơi ấn các phím điều khiển từ bàn phím"""
       # THỬ THÁCH 1:ĐANG Ở TRONG SHOP

        if self.is_showing_shop:

            # Chọn lên
            if key == pygame.K_UP:
                self.shop_selected_index -= 1

            # Chọn xuống
            elif key == pygame.K_DOWN:
                self.shop_selected_index += 1

            # Giới hạn chỉ số
            if self.shop_type == "vat pham":
                max_index = len(self.item_shop) - 1
            else:
                max_index = len(self.skill_shop) - 1

            self.shop_selected_index = max(
                0,
                min(self.shop_selected_index, max_index)
            )

            # Mua bằng F
            if key == pygame.K_f:
                self.buy_selected_item()

            return
        # THỬ THÁCH 2: Logic chuyển câu thoại hoặc chọn nhánh khi đang mở bảng hộp thoại hội thoại
        if self.is_showing_dialogue and self.active_npc_id:
            npc = self.npc_data[self.active_npc_id]
            total_dialogues = len(npc["dialogues"])

            # ĐIỀU KIỆN ĐẶC BIỆT: Nếu là Lilith (NPC 1) và đang đứng ở câu thoại cuối cùng (Xuất hiện lựa chọn)
            if self.active_npc_id == 1 and self.current_step == total_dialogues - 1:
                if key == pygame.K_LEFT or key == pygame.K_RIGHT:
                    # Nhấn nút mũi tên Trái/Phải để đổi qua đổi lại giữa 2 khung lựa chọn Shop
                    self.selected_option = 1 - self.selected_option
                elif key == pygame.K_f:
                    # Nhấn F để chốt lựa chọn phương án, tự động tắt hộp thoại nói và bật bảng Shop lên
                    self.is_showing_dialogue = False 
                    self.is_showing_shop = True   
                    self.shop_selected_index = 0 # Reset chỉ số lựa chọn trong shop về 0 mỗi khi mở shop mới 
                    if self.selected_option == 0:
                        self.shop_type = "vat pham"
                    else:
                        self.shop_type = "ky nang"
                return

            # Các câu thoại bình thường, ấn phím F để nhảy sang câu thoại tiếp theo
            if key == pygame.K_f:
                self.current_step += 1
                # Nếu đã đọc hết tất cả các câu thoại trong danh sách thì tự động đóng hộp thoại
                if self.current_step >= total_dialogues:
                    self.is_showing_dialogue = False
                    self.active_npc_id = None

    # ------------------------------------------------------------------
    # VẼ GIAO DIỆN (HỘP THOẠI, CHỮ ! [F], CỬA HÀNG)
    # ------------------------------------------------------------------
    def draw(self, surface, camera, game_instance):
        """Vẽ toàn bộ giao diện chữ, dấu tương tác, khung nền hộp thoại và bảng shop lên màn hình chính"""
        font_small = pygame.font.SysFont("Arial", 18)
        font_bold = pygame.font.SysFont("Arial", 22, bold=True)

        # 1. ĐƠN GIẢN HÓA: Vẽ chữ ! [F] trực tiếp lên trên sát khung ảnh thật của NPC theo Camera
        if self.active_npc_id and not self.is_showing_dialogue and not self.is_showing_shop:
            if self.active_npc_id == 1:
                target_object = game_instance.sampleNPC_object
            else:
                target_object = game_instance.lunebladeNPC_object

            if target_object and target_object.current_image:
                img_width = target_object.current_image.get_width()
                
                # Tính toán tọa độ hiển thị thực tế trên màn hình sau khi đã trừ đi Camera cuộn bản đồ
                draw_x = int(target_object.x - camera.x)
                draw_y = int(target_object.y - camera.y)
                
                # Căn lề tự động: Đặt chữ nằm chính giữa và sát ngay phía trên khung ảnh của NPC
                excl_x = draw_x + (img_width // 2) - 4
                excl_y = draw_y - 22  # Sát ngay phía trên đầu khung ảnh (22 pixel cực kỳ vừa vặn)
                
                # Tiến hành vẽ chữ lên trên màn hình game surface
                excl_surf = font_bold.render("!", True, (255, 215, 0))
                surface.blit(excl_surf, (excl_x, excl_y))
                
                hint_surf = font_small.render("[F]", True, (255, 255, 255))
                surface.blit(hint_surf, (excl_x + 12, excl_y + 4))

        # 2. VẼ HỘP THOẠI DIALOGUE BOX (Nằm đè ở cạnh đáy màn hình hiển thị chính)
        if self.is_showing_dialogue and self.active_npc_id:
            npc = self.npc_data[self.active_npc_id]
            
            # Vẽ một hình chữ nhật lớn màu xám đen bo tròn góc làm nền cho hộp chữ thoại
            box_rect = pygame.Rect(50, SCREEN_HEIGHT - 160, SCREEN_WIDTH - 100, 130)
            pygame.draw.rect(surface, (25, 25, 25), box_rect, border_radius=10)
            pygame.draw.rect(surface, (255, 215, 0), box_rect, 2, border_radius=10) # Tạo đường viền màu vàng Gold
            
            # Vẽ tên định danh của đối tượng NPC đang nói chuyện lên góc trên hộp thoại
            name_surf = font_bold.render(npc["name"], True, (255, 165, 0))
            surface.blit(name_surf, (70, SCREEN_HEIGHT - 150))
            
            # Vẽ văn bản nội dung câu thoại không dấu hiện tại
            msg = npc["dialogues"].get(self.current_step, "")
            msg_surf = font_small.render(msg, True, (255, 255, 255))
            surface.blit(msg_surf, (70, SCREEN_HEIGHT - 110))
            
            # ĐIỀU KIỆN PHÂN NHÁNH: Nếu là câu cuối của Lilith, tiến hành vẽ thêm 2 nút hộp lựa chọn shop
            total_dialogues = len(npc["dialogues"])
            if self.active_npc_id == 1 and self.current_step == total_dialogues - 1:
                rect_item = pygame.Rect(70, SCREEN_HEIGHT - 75, 180, 35)
                rect_skill = pygame.Rect(270, SCREEN_HEIGHT - 75, 180, 35)
                
                # Thay đổi màu sắc viền sáng dựa theo phím bấm mũi tên người chơi trỏ vào (Bên nào chọn viền sẽ vàng)
                color_item = (255, 215, 0) if self.selected_option == 0 else (100, 100, 100)
                color_skill = (255, 215, 0) if self.selected_option == 1 else (100, 100, 100)
                
                # Vẽ 2 khung hình chữ nhật nhỏ đại diện cho hai danh mục shop
                pygame.draw.rect(surface, (40, 40, 40), rect_item, border_radius=5)
                pygame.draw.rect(surface, color_item, rect_item, 2, border_radius=5)
                
                pygame.draw.rect(surface, (40, 40, 40), rect_skill, border_radius=5)
                pygame.draw.rect(surface, color_skill, rect_skill, 2, border_radius=5)
                
                # Viết tiêu đề chữ tương ứng lồng vào trong khung lựa chọn
                txt_item = font_small.render("Shop Vat Pham", True, (255, 255, 255) if self.selected_option == 0 else (180, 180, 180))
                txt_skill = font_small.render("Shop Ky Nang", True, (255, 255, 255) if self.selected_option == 1 else (180, 180, 180))
                
                surface.blit(txt_item, (rect_item.x + 30, rect_item.y + 6))
                surface.blit(txt_skill, (rect_skill.x + 35, rect_skill.y + 6))
                
                # Gợi ý phím bấm điều khiển cho người chơi dễ thao tác chọn shop
                hint = font_small.render("[Mui ten Trai/Phai de chon - Nhan F de mo]", True, (0, 255, 255))
                surface.blit(hint, (SCREEN_WIDTH - 380, SCREEN_HEIGHT - 60))
            else:
                # Gợi ý nhấn phím F thông thường đối với các câu thoại hội thoại chạy chữ khác
                hint = font_small.render("[Nhan F de tiep tuc...]", True, (160, 160, 160))
                surface.blit(hint, (SCREEN_WIDTH - 220, SCREEN_HEIGHT - 60))

        # 3. V VẼ KHUNG NỀN MÀN HÌNH GIAO DIỆN CỬA HÀNG MẪU (Khi đã chọn xong và ấn F kích hoạt)
        if self.is_showing_shop:
            # Tạo một bảng chữ nhật lớn che giữa màn hình đại diện cho Menu Shop
            shop_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 6, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5)
            pygame.draw.rect(surface, (40, 30, 20), shop_rect, border_radius=12) # Tạo nền màu nâu gỗ cổ kính
            pygame.draw.rect(surface, (255, 215, 0), shop_rect, 3, border_radius=12)
            
            # Tự động đồng bộ tiêu đề chữ hiển thị dựa theo biến danh mục shop_type người chơi vừa chọn
            title_text = f"CUA HANG {self.shop_type.upper()}"
            title_surf = font_bold.render(title_text, True, (255, 215, 0))
            surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, SCREEN_HEIGHT // 6 + 20))
            
            # Văn bản hướng dẫn người chơi nhấn phím ESC để quay trở ra trò chơi tự do
            close_surf = font_small.render("Nhan [ESC] de roi khoi cua hang", True, (255, 100, 100))
            close_surf_x = SCREEN_WIDTH // 2 - close_surf.get_width() // 2
            surface.blit(close_surf, (close_surf_x, SCREEN_HEIGHT - 90))

def buy_selected_item(self):

    if self.shop_type == "vat pham":

        item = self.item_shop[self.shop_selected_index]

        print(
            f"Mua {item['name']} - "
            f"{item['price']} Gold - "
            f"+{item['heal']} HP"
        )

    elif self.shop_type == "ky nang":

        skill = self.skill_shop[self.shop_selected_index]

        print(
            f"Mua ky nang {skill['name']} - "
            f"{skill['price']} Gold"
        )