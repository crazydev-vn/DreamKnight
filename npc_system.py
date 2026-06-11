import pygame
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT

#================================================================================================
# CLASS NPCSYSTEM
# Quản lý hệ thống hội thoại phím F và Hệ thống Cửa hàng (Shop) tích hợp cơ chế CHUYỂN TAB.
# Vật phẩm giữ nguyên dữ liệu gốc (Apple, Orange, Watermelon), Kỹ năng giữ 2 món lõi.
# Hỗ trợ click chuột chọn Tab Vật Phẩm / Kỹ Năng, tăng giảm số lượng và MUA bằng Vàng.
# Ấn duy nhất phím F để đóng Shop nhanh chóng, có đầy đủ chú thích tiếng Việt có dấu.
#================================================================================================
class NPCSystem:
    
    # ------------------------------------------------------------------
    # KHỞI TẠO HỆ THỐNG NPC VÀ KHO HÀNG HÓA CHUYỂN TAB
    # ------------------------------------------------------------------
    def __init__(self):
        # Các cờ trạng thái điều khiển vòng lặp chính của giao diện
        self.is_showing_dialogue = False  # Cờ bật/tắt hiển thị bảng chữ thoại nói chuyện
        self.is_showing_shop = False      # Cờ bật/tắt hiển thị bảng giao diện cửa hàng Shop
        self.shop_type = None              # Lưu Tab hiện tại đang mở: "vat pham" hoặc "ky nang"
        
        self.active_npc_id = None          # ID của NPC người chơi đang đứng ở gần để tương tác (1 hoặc 2)[cite: 20]
        self.current_step = 0              # Tiến trình câu thoại hiện tại đang hiển thị (bắt đầu từ 0)[cite: 20]
        self.selected_option = 0           # Nhánh lựa chọn Shop tại câu thoại cuối: 0 là Vật Phẩm, 1 là Kỹ Năng[cite: 20]
        
        # Quản lý hệ thống thông báo trạng thái giao dịch mua hàng
        self.shop_message = ""             # Dòng chữ thông báo kết quả: Thành công hoặc Thất bại
        self.shop_message_timer = 0        # Bộ đếm thời gian (frame) để tự động làm ẩn thông báo
        self.button_rects = []             # Mảng chứa tọa độ vùng ảo của các nút bấm để bắt click chuột trái

        # Kịch bản hội thoại kịch tính phù hợp ngoại hình NPC (Chữ hiển thị trong game bắt buộc KHÔNG DẤU)[cite: 20]
        self.npc_data = {
            1: {
                "name": "Lilith (Thuong Nhan Toc Quy) Xin Chao Hanh Gia!",
                "dialogues": {
                    0: "Lilith: Su dung cam cua nguoi lam ta thay rat thu vi day, chang hanh gia tre...",
                    1: "Lilith: Lu Slime ngoai kia dang khao khat linh hon cua nguoi. Nguoi khong the di tay khong.",
                    2: "Lilith: Hay doi trac voi ta! Nguoi muon on dinh sinh menh bang Vat Pham, hay muon hoc Ky Nang?" 
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

       # KHO HÀNG HÓA SHOP CẬP NHẬT: Chia nhỏ các loại trái cây công dụng khác nhau thành 3 món riêng biệt, mỗi món có giá trị hồi máu khác nhau              
        self.shop_goods = {
            "vat pham": [
                {"name": "Qua Tao Pixel", "desc": "Hoi 20 Mau Nho Le", "price": 15, "type": "heal", "value": 20, "quantity": 1, "basket_id": 1},
                {"name": "Qua Cam Ma Thuat", "desc": "Hoi 50 Mau Sinh Menh", "price": 39, "type": "heal", "value": 50, "quantity": 1, "basket_id": 2},
                {"name": "Nguyen Gio Trai Cay", "desc": "Hoi Phuc Hoan Toan 100% Mau", "price": 81, "type": "heal", "value": 100, "quantity": 1, "basket_id": 3}
            ],
            "ky nang": [
                {"name": "Bi Kip Kiem Sat", "desc": "Tang Sat Thuong Kiem (+15)", "price": 150, "type": "damage", "value": 15, "quantity": 1, "basket_id": None},
                {"name": "Thien Linh Giay", "desc": "Giam Cooldown Dash (-0.2s)", "price": 200, "type": "dash_cd", "value": 0.2, "quantity": 1, "basket_id": None},
            ]
        }

    # ------------------------------------------------------------------
    # CẬP NHẬT TIMER THÔNG BÁO VÀ PHẠM VI QUÉT KHOẢNG CÁCH NPC
    # ------------------------------------------------------------------
    def update(self, player, game_instance):
        """Giảm trừ thời gian thông báo và liên tục quét vị trí thực tế của các NPC động trên bản đồ"""
        # Nếu đang mở hội thoại hoặc đang xem cửa hàng thì đóng băng hệ thống quét để giữ ổn định game
        if self.is_showing_dialogue or self.is_showing_shop:
            if self.shop_message_timer > 0:
                self.shop_message_timer -= 1
            return

        # Lấy trực tiếp đối tượng thực thể động đang chạy hoạt ảnh từ file game.py chính
        npc_objects = {
            1: game_instance.sampleNPC_object,
            2: game_instance.lunebladeNPC_object
        }

        # Tính tâm vị trí hiện tại của nhân vật người chơi
        player_cx = player.x + player.width // 2
        player_cy = player.y + player.height // 2

        # Vòng lặp quét khoảng cách hình học thực tế
        for npc_id, npc_obj in npc_objects.items():
            if npc_obj:
                # Tính tâm NPC dựa theo kích thước khung hình ảnh thực tế đang blit lên bản đồ
                img_w = npc_obj.current_image.get_width() if npc_obj.current_image else 32
                img_h = npc_obj.current_image.get_height() if npc_obj.current_image else 48
                
                npc_cx = npc_obj.x + img_w // 2
                npc_cy = npc_obj.y + img_h // 2
                
                # Công thức toán học Pythagore đo khoảng cách pixel thực giữa hai thực thể
                distance = math.hypot(npc_cx - player_cx, npc_cy - player_cy)
                
                # Nếu đứng trong bán kính 80 pixel, khóa mục tiêu tương tác để chuẩn bị hiện phím F
                if distance <= 80: 
                    self.active_npc_id = npc_id
                    return
                
        # Nếu chạy ra xa khỏi tất cả NPC, trả trạng thái ID mục tiêu về rỗng
        self.active_npc_id = None

    # ------------------------------------------------------------------
    # XỬ LÝ CLICK CHUỘT TRÁI (TƯƠNG TÁC NÚT +, -, MUA & CHUYỂN TAB)
    # ------------------------------------------------------------------
    def handle_click(self, mouse_pos, player):
        """Phân tích tọa độ click chuột trái của người chơi để thực hiện chuyển đổi Tab hoặc thanh toán hàng"""
        if not self.is_showing_shop:
            return

        # Duyệt qua danh sách các vùng nút bấm ảo vừa được tính toán ở frame hiện tại
        for btn in self.button_rects:
            if btn["rect"].collidepoint(mouse_pos):
                
                # CHỨC NĂNG CLICK CHUỘT CHUYỂN ĐỔI TAB ĐỘNG Ở ĐỈNH ĐẦU SHOP
                if btn["action"] == "change_tab":
                    self.shop_type = btn["tab_target"] # Đổi dữ liệu hiển thị sang Tab đích ngay lập tức
                    self.shop_message = ""             # Xóa sạch thông báo cũ để tránh hiểu lầm chỉ số
                    return

                # LOGIC MUA BÁN, TĂNG GIẢM SỐ LƯỢNG SẢN PHẨM TRÊN HÀNG NGANG
                goods_list = self.shop_goods[self.shop_type]
                idx = btn["item_index"]
                
                # Nhấn nút thoát bằng chuột trái
                if btn["action"] == "close":
                    self.is_showing_shop = False
                    self.shop_type = None
                    return
                # Nhấn nút MUA để tiến hành khấu trừ Vàng và gia tăng vĩnh viễn thuộc tính nhân vật
                elif btn["action"] == "buy":
                    item = goods_list[idx]
                    total_cost = item["price"] * item["quantity"]
                    
                    # Kiểm tra điều kiện tài sản tiền vàng hiện tại của Hiệp sĩ
                    if player.gold >= total_cost:
                        player.gold -= total_cost # Trừ tiền vàng trực tiếp công khai trên thanh HUD ui.py
                        
                        # Vòng lặp chạy cộng dồn chỉ số theo cấp số lượng đặt mua
                        for _ in range(item["quantity"]):
                            if item["type"] == "heal":
                                player.health = min(player.max_health, player.health + item["value"])
                            elif item["type"] == "damage":
                                if hasattr(player, 'damage'): player.damage += item["value"]
                                elif hasattr(player, 'attack_damage'): player.attack_damage += item["value"]
                            elif item["type"] == "dash_cd":
                                if hasattr(player, 'dash_cooldown'):
                                    player.dash_cooldown = max(100, player.dash_cooldown - (item["value"] * 1000))
                        
                        self.shop_message = f"Mua thanh cong {item['quantity']}x {item['name']}!"
                        item["quantity"] = 1 # Reset con số hiển thị đặt mua của ô hàng quay về 1 mặc định
                        self.shop_message_timer = 90 # Xuất hiện dòng chữ xanh lá thông báo trong 1.5 giây
                    else:
                        self.shop_message = "Khong du tien Vang de mua!"
                        self.shop_message_timer = 90 # Xuất hiện dòng chữ đỏ báo lỗi trong 1.5 giây
                    return

    # ------------------------------------------------------------------
    # XỬ LÝ PHÍM NHẤN BÀN PHÍM (HỘI THOẠI & PHÍM F ĐỂ TẮT SHOP NHANH)
    # ------------------------------------------------------------------
    def handle_keydown(self, key):
        """Ấn duy nhất phím F khi mở Shop để đóng nhanh chóng theo yêu cầu, bỏ hoàn toàn ESC"""
        # CHỈ GIỮ LẠI DUY NHẤT PHÍM F ĐỂ ĐÓNG BẢNG SHOP KHÔNG BỊ TRÙNG THÓI QUEN NÚT
        if self.is_showing_shop:
            if key == pygame.K_f: 
                self.is_showing_shop = False
                self.shop_type = None
            return

        # CHỐNG XUNG ĐỘT PHÍM F: Nếu chưa mở bảng thoại, ấn F frame này chỉ kích hoạt mở nền hộp chữ
        if not self.is_showing_dialogue:
            if key == pygame.K_f and self.active_npc_id is not None:
                self.is_showing_dialogue = True
                self.current_step = 0
                self.selected_option = 0
            return # Ngắt hàm ngay lập tức để phím F không bị ăn lặp lướt xuống khối lệnh dưới trong cùng frame

        # Di chuyển lật trang câu thoại thông thường bằng phím F công khai
        if self.is_showing_dialogue and self.active_npc_id:
            npc = self.npc_data[self.active_npc_id]
            total_dialogues = len(npc["dialogues"])

            # Nếu là câu thoại cuối cùng của thương nhân tộc quỷ Lilith, kích hoạt cụm phím chọn nhánh Shop
            if self.active_npc_id == 1 and self.current_step == total_dialogues - 1:
                if key == pygame.K_LEFT or key == pygame.K_RIGHT:
                    self.selected_option = 1 - self.selected_option
                elif key == pygame.K_f:
                    self.is_showing_dialogue = False 
                    self.is_showing_shop = True     
                    # Tự động gán mở đầu màn hình Shop rơi trúng ngay Tab bồ vừa lựa chọn ở bảng thoại
                    self.shop_type = "vat pham" if self.selected_option == 0 else "ky nang"
                return

            # Nhấn F nhảy sang câu tiếp theo
            if key == pygame.K_f:
                self.current_step += 1
                if self.current_step >= total_dialogues:
                    self.is_showing_dialogue = False
                    self.active_npc_id = None

    # ------------------------------------------------------------------
    # VẼ TOÀN BỘ GIAO DIỆN (CHỮ CHỮ CỬA HÀNG, TAB CON VÀ ẢNH PIXEL)
    # ------------------------------------------------------------------
    def draw(self, surface, camera, game_instance):
        """Vẽ biểu tượng cảm xúc ! [F], vẽ hộp chạy chữ đáy màn hình và vẽ bảng Shop đa Tab bằng ảnh tĩnh thật"""
        font_small = pygame.font.SysFont("Arial", 18)
        font_bold = pygame.font.SysFont("Arial", 22, bold=True)
        player = game_instance.player

        # 1. Vẽ chữ ! [F] màu vàng Gold tự động bám dính khít trên đỉnh đầu thực thể NPC thật
        if self.active_npc_id and not self.is_showing_dialogue and not self.is_showing_shop:
            target_object = game_instance.sampleNPC_object if self.active_npc_id == 1 else game_instance.lunebladeNPC_object
            if target_object and target_object.current_image:
                img_width = target_object.current_image.get_width()
                draw_x = int(target_object.x - camera.x)
                draw_y = int(target_object.y - camera.y)
                
                # Căn giữa theo bề rộng ảnh và nhấc cao 22 pixel chuẩn chỉ
                excl_x = draw_x + (img_width // 2) - 4
                excl_y = draw_y - 22  
                
                excl_surf = font_bold.render("!", True, (255, 215, 0))
                surface.blit(excl_surf, (excl_x, excl_y))
                hint_surf = font_small.render("[F]", True, (255, 255, 255))
                surface.blit(hint_surf, (excl_x + 12, excl_y + 4))

        # 2. Vẽ Hộp thoại nói chuyện đáy màn hình nền xám đen bo góc viền vàng bóng loáng
        if self.is_showing_dialogue and self.active_npc_id:
            npc = self.npc_data[self.active_npc_id]
            box_rect = pygame.Rect(50, SCREEN_HEIGHT - 160, SCREEN_WIDTH - 100, 130)
            pygame.draw.rect(surface, (25, 25, 25), box_rect, border_radius=10)
            pygame.draw.rect(surface, (255, 215, 0), box_rect, 2, border_radius=10) 
            
            name_surf = font_bold.render(npc["name"], True, (255, 165, 0))
            surface.blit(name_surf, (70, SCREEN_HEIGHT - 150))
            msg = npc["dialogues"].get(self.current_step, "")
            msg_surf = font_small.render(msg, True, (255, 255, 255))
            surface.blit(msg_surf, (70, SCREEN_HEIGHT - 110))
            
            total_dialogues = len(npc["dialogues"])
            if self.active_npc_id == 1 and self.current_step == total_dialogues - 1:
                rect_item = pygame.Rect(70, SCREEN_HEIGHT - 75, 180, 35)
                rect_skill = pygame.Rect(270, SCREEN_HEIGHT - 75, 180, 35)
                color_item = (255, 215, 0) if self.selected_option == 0 else (100, 100, 100)
                color_skill = (255, 215, 0) if self.selected_option == 1 else (100, 100, 100)
                
                pygame.draw.rect(surface, (40, 40, 40), rect_item, border_radius=5)
                pygame.draw.rect(surface, color_item, rect_item, 2, border_radius=5)
                pygame.draw.rect(surface, (40, 40, 40), rect_skill, border_radius=5)
                pygame.draw.rect(surface, color_skill, rect_skill, 2, border_radius=5)
                
                txt_item = font_small.render("Shop Vat Pham", True, (255, 255, 255) if self.selected_option == 0 else (180, 180, 180))
                txt_skill = font_small.render("Shop Ky Nang", True, (255, 255, 255) if self.selected_option == 1 else (180, 180, 180))
                surface.blit(txt_item, (rect_item.x + 30, rect_item.y + 6))
                surface.blit(txt_skill, (rect_skill.x + 35, rect_skill.y + 6))
                
                hint = font_small.render("[Mui ten Trai/Phai de chon - Nhan F de mo]", True, (0, 255, 255))
                surface.blit(hint, (SCREEN_WIDTH - 380, SCREEN_HEIGHT - 60))
            else:
                hint = font_small.render("[Nhan F de tiep tuc...]", True, (160, 160, 160))
                surface.blit(hint, (SCREEN_WIDTH - 220, SCREEN_HEIGHT - 60))

        # 3. V V VẼ KHUNG GIAO DIỆN CỬA HÀNG SHOP CHUNG TÍCH HỢP HỆ THỐNG ĐA TAB
        if self.is_showing_shop:
            self.button_rects = [] # Làm rỗng mảng nút bấm ảo ở đầu mỗi frame để tính toán tọa độ click mới tinh

            # Khung sảnh Shop lớn nằm đè chính giữa màn hình
            shop_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 8, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.4)
            pygame.draw.rect(surface, (35, 30, 25), shop_rect, border_radius=12) # Nền bảng màu nâu gỗ cổ kính
            pygame.draw.rect(surface, (255, 215, 0), shop_rect, 3, border_radius=12) # Viền kim loại mạ vàng Gold
            
            # --- ĐƯA CHỮ CỬA HÀNG TO BỰ TRỞ LẠI ĐỈNH ĐẦU BẢNG ---
            title_text = f"CUA HANG {self.shop_type.upper()}"
            title_surf = font_bold.render(title_text, True, (255, 215, 0))
            surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, shop_rect.y + 15))
            
            # --- THIẾT KẾ 2 NÚT NẤM CHUYỂN TAB (Dịch xuống dưới tiêu đề chính một chút) ---
            tab_width = 130
            tab_height = 30
            tab_item_rect = pygame.Rect(shop_rect.x + 30, shop_rect.y + 50, tab_width, tab_height)
            tab_skill_rect = pygame.Rect(shop_rect.x + 40 + tab_width, shop_rect.y + 50, tab_width, tab_height)
            
            # Thay đổi sắc độ màu nền Tab dựa theo trạng thái Tab đang xem thực tế
            bg_tab_item = (70, 55, 45) if self.shop_type == "vat pham" else (30, 25, 20)
            bg_tab_skill = (70, 55, 45) if self.shop_type == "ky nang" else (30, 25, 20)
            
            # Thay đổi sắc độ màu viền sáng Tab để người chơi nhận biết
            border_tab_item = (255, 215, 0) if self.shop_type == "vat pham" else (100, 100, 100)
            border_tab_skill = (255, 215, 0) if self.shop_type == "ky nang" else (100, 100, 100)
            
            # Tiến hành vẽ khối hộp của Tab Vật Phẩm
            pygame.draw.rect(surface, bg_tab_item, tab_item_rect, border_radius=6)
            pygame.draw.rect(surface, border_tab_item, tab_item_rect, 2, border_radius=6)
            txt_tab_i = font_bold.render("Vat Pham", True, (255, 255, 255) if self.shop_type == "vat pham" else (160, 160, 160))
            surface.blit(txt_tab_i, (tab_item_rect.x + (tab_width - txt_tab_i.get_width()) // 2, tab_item_rect.y + 3))
            self.button_rects.append({"rect": tab_item_rect, "action": "change_tab", "tab_target": "vat pham", "item_index": -1})
            
            # Tiến hành vẽ khối hộp của Tab Kỹ Năng
            pygame.draw.rect(surface, bg_tab_skill, tab_skill_rect, border_radius=6)
            pygame.draw.rect(surface, border_tab_skill, tab_skill_rect, 2, border_radius=6)
            txt_tab_s = font_bold.render("Ky Nang", True, (255, 255, 255) if self.shop_type == "ky nang" else (160, 160, 160))
            surface.blit(txt_tab_s, (tab_skill_rect.x + (tab_width - txt_tab_s.get_width()) // 2, tab_skill_rect.y + 3))
            self.button_rects.append({"rect": tab_skill_rect, "action": "change_tab", "tab_target": "ky nang", "item_index": -1})
            
            # Vẽ tổng số tiền Vàng thực tế hiện có của nhân vật lên góc phải bảng gỗ
            gold_surf = font_bold.render(f"Vang: {player.gold}", True, (255, 255, 0))
            surface.blit(gold_surf, (shop_rect.right - gold_surf.get_width() - 30, shop_rect.y + 50))
            
            # Trích xuất danh sách kho hàng hóa chuẩn dựa theo Tab đang active
            goods = self.shop_goods[self.shop_type]
            start_y = shop_rect.y + 95
            
            for i, item in enumerate(goods):
                # Thiết lập phân bổ khoảng cách các ô hàng ngang cách nhau đều đặn (i * 75)
                row_rect = pygame.Rect(shop_rect.x + 30, start_y + (i * 75), shop_rect.width - 60, 65)
                pygame.draw.rect(surface, (50, 40, 35), row_rect, border_radius=8)
                
                # --- NẠP BIỂU TƯỢNG ẢNH TĨNH PIXEL THỰC TẾ LẤY TỪ GAME.PY ---
                item_surface = None
                if self.shop_type == "vat pham":
                    # Lấy chính xác static_image gốc của giỏ trái cây bồ khai báo ở game.py sang làm đại diện ô chứa hình pixel
                    if item["basket_id"] == 1 and game_instance.fruit_pasket_01:
                        item_surface = game_instance.fruit_pasket_01.static_image
                    elif item["basket_id"] == 2 and game_instance.fruit_pasket_02:
                        item_surface = game_instance.fruit_pasket_02.static_image
                    elif item["basket_id"] == 3 and game_instance.fruit_pasket_03:
                        item_surface = game_instance.fruit_pasket_03.static_image
                else:
                    # Nếu thuộc bên Tab kỹ năng, mượn tạm ảnh tĩnh ngôi nhà/hàng rào pixel có sẵn để blit làm biểu tượng đẹp mắt
                    if i == 0: item_surface = game_instance.home001_object.static_image
                    elif i == 1: item_surface = game_instance.flag1_object.static_image

                # Tiến hành scale nhỏ ảnh tĩnh pixel về cỡ tiêu chuẩn vuông 32x32 và blit lên ô chứa hàng
                if item_surface:
                    scaled_icon = pygame.transform.scale(item_surface, (32, 32))
                    surface.blit(scaled_icon, (row_rect.x + 15, row_rect.y + 16))
                
                # Viết văn bản hiển thị Tên sản phẩm chính thức và công dụng đi kèm không dấu
                name_surf = font_bold.render(item["name"], True, (255, 255, 255))
                desc_surf = font_small.render(item["desc"], True, (170, 170, 170))
                surface.blit(name_surf, (row_rect.x + 65, row_rect.y + 10))
                surface.blit(desc_surf, (row_rect.x + 65, row_rect.y + 35))
                               
                # ---- THIẾT KẾ KHỐI Ô NÚT BẤM MUA THANH TOÁN TỔNG TIỀN VÀNG ----
                total_item_price = item["price"] * item["quantity"]
                btn_buy = pygame.Rect(row_rect.right - 145, row_rect.y + 15, 130, 35)
                pygame.draw.rect(surface, (218, 165, 32), btn_buy, border_radius=6) # Hộp nút màu vàng đậm ánh kim cổ kính
                
                buy_str = f"Mua: {total_item_price}G"
                buy_surf = font_small.render(buy_str, True, (25, 25, 25))
                surface.blit(buy_surf, (btn_buy.x + (btn_buy.width - buy_surf.get_width()) // 2, btn_buy.y + 7))
                self.button_rects.append({"rect": btn_buy, "action": "buy", "item_index": i})

            # In dòng thông điệp thông báo trạng thái giao dịch mua hàng (Thành công xanh lá, thất bại màu đỏ)
            if self.shop_message_timer > 0:
                text_color = (100, 255, 100) if "thanh cong" in self.shop_message else (255, 100, 100)
                msg_surf = font_bold.render(self.shop_message, True, text_color)
                surface.blit(msg_surf, (SCREEN_WIDTH // 2 - msg_surf.get_width() // 2, shop_rect.bottom - 75))

            # Dòng chữ hướng dẫn phím bấm đóng nhanh gọn lẹ bằng một nút duy nhất
            hint_str = "Nhan phim [F] de Dong Cua Hang  |  click de tuong tac"
            close_surf = font_small.render(hint_str, True, (200, 200, 200))
            surface.blit(close_surf, (SCREEN_WIDTH // 2 - close_surf.get_width() // 2, shop_rect.bottom - 35))