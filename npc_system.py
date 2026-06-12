import pygame
import math
import os
from config import SCREEN_WIDTH, SCREEN_HEIGHT

#================================================================================================
# CLASS NPCSYSTEM - Hệ thống NPC, hội thoại và cửa hàng
#================================================================================================
class NPCSystem:
    
    def __init__(self):
        # Trạng thái giao diện
        self.is_showing_dialogue = False
        self.is_showing_shop = False
        self.shop_type = None
        
        self.active_npc_id = None
        self.current_step = 0
        self.selected_option = 0
        
        # Hệ thống thông báo
        self.shop_message = ""
        self.shop_message_timer = 0
        self.button_rects = []

        # Cache icon
        self.shop_icons = {}

        # Kịch bản hội thoại NPC
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

        # KHO HÀNG HÓA - ĐÃ XÓA basket_id KHÔNG CẦN THIẾT
        self.shop_goods = {
            "vat pham": [
                {"name": "Minor Health Potion", "desc": "+20 HP", "price": 15, "type": "heal", "value": 20, "quantity": 1, "icon": "fc266.png"},
                {"name": "Health Potion", "desc": "+50 HP", "price": 39, "type": "heal", "value": 50, "quantity": 1, "icon": "fc268.png"},
                {"name": "Greater Health Potion", "desc": "+MAX HP", "price": 81, "type": "heal", "value": 100, "quantity": 1, "icon": "fc272.png"}
            ],
            "ky nang": [
                {"name": "Upgrade sword", "desc": "Tang Sat Thuong Kiem (+15)", "price": 150, "type": "damage", "value": 15, "quantity": 1, "icon": "fc730.png"},
                {"name": "Dashmaster", "desc": "Giam Cooldown Dash (-0.2s)", "price": 200, "type": "dash_cd", "value": 0.2, "quantity": 1, "icon": "fc790.png"},
            ]
        }

    # ------------------------------------------------------------------
    # LOAD ICON
    # ------------------------------------------------------------------
    def load_shop_icon(self, icon_path, size=(64, 64)):
        """Load icon từ thư mục assets/icon_item"""
        if icon_path in self.shop_icons:
            return self.shop_icons[icon_path]
        
        full_path = f"assets/icon_item/{icon_path}"
        if os.path.exists(full_path):
            try:
                icon = pygame.image.load(full_path).convert_alpha()
                self.shop_icons[icon_path] = pygame.transform.scale(icon, size)
                return self.shop_icons[icon_path]
            except:
                return None
        return None

    # ------------------------------------------------------------------
    # CẬP NHẬT
    # ------------------------------------------------------------------
    def update(self, player, game_instance):
        if self.is_showing_dialogue or self.is_showing_shop:
            if self.shop_message_timer > 0:
                self.shop_message_timer -= 1
            return

        npc_objects = {
            1: game_instance.sampleNPC_object,
            2: game_instance.lunebladeNPC_object
        }

        player_cx = player.x + player.width // 2
        player_cy = player.y + player.height // 2

        for npc_id, npc_obj in npc_objects.items():
            if npc_obj:
                img_w = npc_obj.current_image.get_width() if npc_obj.current_image else 32
                img_h = npc_obj.current_image.get_height() if npc_obj.current_image else 48
                
                npc_cx = npc_obj.x + img_w // 2
                npc_cy = npc_obj.y + img_h // 2
                
                distance = math.hypot(npc_cx - player_cx, npc_cy - player_cy)
                
                if distance <= 80: 
                    self.active_npc_id = npc_id
                    return
                
        self.active_npc_id = None

    # ------------------------------------------------------------------
    # XỬ LÝ CLICK CHUỘT
    # ------------------------------------------------------------------
    def handle_click(self, mouse_pos, player):
        if not self.is_showing_shop:
            return

        for btn in self.button_rects:
            if btn["rect"].collidepoint(mouse_pos):
                
                if btn["action"] == "change_tab":
                    self.shop_type = btn["tab_target"]
                    self.shop_message = ""
                    return

                goods_list = self.shop_goods[self.shop_type]
                idx = btn["item_index"]
                
                if btn["action"] == "close":
                    self.is_showing_shop = False
                    self.shop_type = None
                    return
                    
                elif btn["action"] == "buy":
                    item = goods_list[idx]
                    total_cost = item["price"] * item["quantity"]
                    
                    if player.gold >= total_cost:
                        player.gold -= total_cost
                        
                        for _ in range(item["quantity"]):
                            if item["type"] == "heal":
                                player.health = min(player.max_health, player.health + item["value"])
                            elif item["type"] == "damage":
                                if hasattr(player, 'damage'): 
                                    player.damage += item["value"]
                                elif hasattr(player, 'attack_damage'): 
                                    player.attack_damage += item["value"]
                            elif item["type"] == "dash_cd":
                                if hasattr(player, 'dash_cooldown'):
                                    player.dash_cooldown = max(100, player.dash_cooldown - (item["value"] * 1000))
                        
                        self.shop_message = f"Mua thanh cong {item['quantity']}x {item['name']}!"
                        item["quantity"] = 1
                        self.shop_message_timer = 90
                    else:
                        self.shop_message = "Khong du tien Vang de mua!"
                        self.shop_message_timer = 90
                    return

    # ------------------------------------------------------------------
    # XỬ LÝ PHÍM
    # ------------------------------------------------------------------
    def handle_keydown(self, key):
        if self.is_showing_shop:
            if key == pygame.K_f: 
                self.is_showing_shop = False
                self.shop_type = None
            return

        if not self.is_showing_dialogue:
            if key == pygame.K_f and self.active_npc_id is not None:
                self.is_showing_dialogue = True
                self.current_step = 0
                self.selected_option = 0
            return

        if self.is_showing_dialogue and self.active_npc_id:
            npc = self.npc_data[self.active_npc_id]
            total_dialogues = len(npc["dialogues"])

            if self.active_npc_id == 1 and self.current_step == total_dialogues - 1:
                if key == pygame.K_LEFT or key == pygame.K_RIGHT:
                    self.selected_option = 1 - self.selected_option
                elif key == pygame.K_f:
                    self.is_showing_dialogue = False 
                    self.is_showing_shop = True     
                    self.shop_type = "vat pham" if self.selected_option == 0 else "ky nang"
                return

            if key == pygame.K_f:
                self.current_step += 1
                if self.current_step >= total_dialogues:
                    self.is_showing_dialogue = False
                    self.active_npc_id = None

    # ------------------------------------------------------------------
    # VẼ GIAO DIỆN
    # ------------------------------------------------------------------
    def draw(self, surface, camera, game_instance):
        font_small = pygame.font.SysFont("Arial", 18)
        font_bold = pygame.font.SysFont("Arial", 22, bold=True)
        player = game_instance.player

        # 1. Vẽ icon [F] trên đầu NPC
        if self.active_npc_id and not self.is_showing_dialogue and not self.is_showing_shop:
            target_object = game_instance.sampleNPC_object if self.active_npc_id == 1 else game_instance.lunebladeNPC_object
            if target_object and target_object.current_image:
                img_width = target_object.current_image.get_width()
                draw_x = int(target_object.x - camera.x)
                draw_y = int(target_object.y - camera.y)
                
                excl_x = draw_x + (img_width // 2) - 4
                excl_y = draw_y - 22  
                
                excl_surf = font_bold.render("!", True, (255, 215, 0))
                surface.blit(excl_surf, (excl_x, excl_y))
                hint_surf = font_small.render("[F]", True, (255, 255, 255))
                surface.blit(hint_surf, (excl_x + 12, excl_y + 4))

        # 2. Vẽ hộp thoại
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

        # 3. Vẽ cửa hàng
        if self.is_showing_shop:
            self.button_rects = []

            shop_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 8, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.4)
            pygame.draw.rect(surface, (35, 30, 25), shop_rect, border_radius=12)
            pygame.draw.rect(surface, (255, 215, 0), shop_rect, 3, border_radius=12)
            
            # Tiêu đề
            title_text = f"CUA HANG {self.shop_type.upper()}"
            title_surf = font_bold.render(title_text, True, (255, 215, 0))
            surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, shop_rect.y + 15))
            
            # Tab chuyển đổi
            tab_width = 130
            tab_height = 30
            tab_item_rect = pygame.Rect(shop_rect.x + 30, shop_rect.y + 50, tab_width, tab_height)
            tab_skill_rect = pygame.Rect(shop_rect.x + 40 + tab_width, shop_rect.y + 50, tab_width, tab_height)
            
            bg_tab_item = (70, 55, 45) if self.shop_type == "vat pham" else (30, 25, 20)
            bg_tab_skill = (70, 55, 45) if self.shop_type == "ky nang" else (30, 25, 20)
            border_tab_item = (255, 215, 0) if self.shop_type == "vat pham" else (100, 100, 100)
            border_tab_skill = (255, 215, 0) if self.shop_type == "ky nang" else (100, 100, 100)
            
            pygame.draw.rect(surface, bg_tab_item, tab_item_rect, border_radius=6)
            pygame.draw.rect(surface, border_tab_item, tab_item_rect, 2, border_radius=6)
            txt_tab_i = font_bold.render("Vat Pham", True, (255, 255, 255) if self.shop_type == "vat pham" else (160, 160, 160))
            surface.blit(txt_tab_i, (tab_item_rect.x + (tab_width - txt_tab_i.get_width()) // 2, tab_item_rect.y + 3))
            self.button_rects.append({"rect": tab_item_rect, "action": "change_tab", "tab_target": "vat pham", "item_index": -1})
            
            pygame.draw.rect(surface, bg_tab_skill, tab_skill_rect, border_radius=6)
            pygame.draw.rect(surface, border_tab_skill, tab_skill_rect, 2, border_radius=6)
            txt_tab_s = font_bold.render("Ky Nang", True, (255, 255, 255) if self.shop_type == "ky nang" else (160, 160, 160))
            surface.blit(txt_tab_s, (tab_skill_rect.x + (tab_width - txt_tab_s.get_width()) // 2, tab_skill_rect.y + 3))
            self.button_rects.append({"rect": tab_skill_rect, "action": "change_tab", "tab_target": "ky nang", "item_index": -1})
            
            # Hiển thị vàng
            gold_surf = font_bold.render(f"Vang: {player.gold}", True, (255, 255, 0))
            surface.blit(gold_surf, (shop_rect.right - gold_surf.get_width() - 30, shop_rect.y + 50))
            
            # Danh sách vật phẩm
            goods = self.shop_goods[self.shop_type]
            start_y = shop_rect.y + 95
            
            for i, item in enumerate(goods):
                row_rect = pygame.Rect(shop_rect.x + 30, start_y + (i * 80), shop_rect.width - 60, 70)
                pygame.draw.rect(surface, (50, 40, 35), row_rect, border_radius=8)
                
                # Vẽ icon
                icon_file = item.get("icon", None)
                if icon_file:
                    item_surface = self.load_shop_icon(icon_file, (64, 64))
                    if item_surface:
                        surface.blit(item_surface, (row_rect.x + 5, row_rect.y + 3))
                        name_surf = font_bold.render(item["name"], True, (255, 255, 255))
                        desc_surf = font_small.render(item["desc"], True, (170, 170, 170))
                        surface.blit(name_surf, (row_rect.x + 75, row_rect.y + 12))
                        surface.blit(desc_surf, (row_rect.x + 75, row_rect.y + 38))
                    else:
                        name_surf = font_bold.render(item["name"], True, (255, 255, 255))
                        desc_surf = font_small.render(item["desc"], True, (170, 170, 170))
                        surface.blit(name_surf, (row_rect.x + 65, row_rect.y + 10))
                        surface.blit(desc_surf, (row_rect.x + 65, row_rect.y + 35))
                else:
                    name_surf = font_bold.render(item["name"], True, (255, 255, 255))
                    desc_surf = font_small.render(item["desc"], True, (170, 170, 170))
                    surface.blit(name_surf, (row_rect.x + 65, row_rect.y + 10))
                    surface.blit(desc_surf, (row_rect.x + 65, row_rect.y + 35))
                
                # Nút mua
                total_item_price = item["price"] * item["quantity"]
                btn_buy = pygame.Rect(row_rect.right - 145, row_rect.y + 18, 130, 35)
                pygame.draw.rect(surface, (218, 165, 32), btn_buy, border_radius=6)
                buy_str = f"Mua: {total_item_price}G"
                buy_surf = font_small.render(buy_str, True, (25, 25, 25))
                surface.blit(buy_surf, (btn_buy.x + (btn_buy.width - buy_surf.get_width()) // 2, btn_buy.y + 7))
                self.button_rects.append({"rect": btn_buy, "action": "buy", "item_index": i})

            # Thông báo
            if self.shop_message_timer > 0:
                text_color = (100, 255, 100) if "thanh cong" in self.shop_message else (255, 100, 100)
                msg_surf = font_bold.render(self.shop_message, True, text_color)
                surface.blit(msg_surf, (SCREEN_WIDTH // 2 - msg_surf.get_width() // 2, shop_rect.bottom - 75))

            # Hướng dẫn
            hint_str = "Nhan phim [F] de Dong Cua Hang  |  click de tuong tac"
            close_surf = font_small.render(hint_str, True, (200, 200, 200))
            surface.blit(close_surf, (SCREEN_WIDTH // 2 - close_surf.get_width() // 2, shop_rect.bottom - 35))