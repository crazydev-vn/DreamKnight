import pygame
import os

#================================================================================================
# knight1_hiteffect.py
# Quản lý hiệu ứng animation khi tấn công trúng kẻ địch.
# - Load 10 frame ảnh từ assets/hit/hit_01.png ... hit_10.png
# - Class HitEffect: phát animation 1 lần tại vị trí kẻ địch bị trúng đòn
# - Class HitEffectManager: quản lý nhiều hiệu ứng đồng thời, cập nhật và vẽ tất cả
#================================================================================================


def load_hit_frames():
    """
    Load 10 frame ảnh hiệu ứng hit từ assets/hit/hit_01.png ... hit_10.png
    Trả về danh sách các Surface.
    """
    frames = []
    for i in range(1, 8):
        path = os.path.join("assets","effect_attack02", f"frame{i:04d}.png")
        try:
            img = pygame.image.load(path).convert_alpha()
            frames.append(img)
        except FileNotFoundError:
            print(f"⚠️ Không tìm thấy file: {path}")
            # Tạo surface placeholder màu vàng để dễ debug nếu thiếu ảnh
            placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.circle(placeholder, (255, 220, 0, 180), (32, 32), 28)
            frames.append(placeholder)
    return frames


# Cache frames để không load lại nhiều lần
_cached_hit_frames = None

def get_hit_frames():
    """Trả về frames đã cache, load lần đầu nếu chưa có."""
    global _cached_hit_frames
    if _cached_hit_frames is None:
        _cached_hit_frames = load_hit_frames()
    return _cached_hit_frames


#================================================================================================
# Class HitEffect
# Đại diện cho 1 hiệu ứng hit đang phát tại 1 vị trí cụ thể.
# Phát animation 1 lần duy nhất rồi tự hủy (không lặp lại).
#================================================================================================

class HitEffect:
    def __init__(self, x, y, frame_duration=40):
        """
        Tạo hiệu ứng hit tại vị trí (x, y) trong tọa độ world.
        
        Args:
            x (float): Tọa độ X tâm hiệu ứng (world coordinates)
            y (float): Tọa độ Y tâm hiệu ứng (world coordinates)
            frame_duration (int): Thời gian mỗi frame (ms), mặc định 40ms → tổng ~400ms
        """
        self.frames = get_hit_frames()
        self.frame_duration = frame_duration
        self.current_frame_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.is_done = False  # True khi đã phát xong toàn bộ animation

        # Vị trí tâm hiệu ứng (world coordinates)
        self.x = x
        self.y = y

    def update(self):
        """Cập nhật frame animation. Tự đánh dấu is_done khi hết frame."""
        if self.is_done:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time >= self.frame_duration:
            self.last_update_time = current_time
            self.current_frame_index += 1
            if self.current_frame_index >= len(self.frames):
                self.is_done = True  # Hết animation, đánh dấu để xóa

    def draw(self, screen, camera):
        """Vẽ frame hiện tại lên screen, căn giữa tại vị trí (x, y)."""
        if self.is_done:
            return

        frame = self.frames[self.current_frame_index]
        frame_w = frame.get_width()
        frame_h = frame.get_height()

        # Căn giữa hiệu ứng tại vị trí world, trừ camera offset
        draw_x = self.x - frame_w // 2 - camera.x
        draw_y = self.y - frame_h // 2 - camera.y

        screen.blit(frame, (draw_x, draw_y))


#================================================================================================
# Class HitEffectManager
# Quản lý tất cả HitEffect đang hoạt động.
# Dùng trong Player1: gọi spawn() khi trúng địch, update() và draw() mỗi frame.
#================================================================================================

class HitEffectManager:
    def __init__(self):
        self.effects = []  # Danh sách HitEffect đang hoạt động

    def spawn(self, x, y, frame_duration=40):
        """
        Tạo hiệu ứng hit mới tại vị trí (x, y).
        
        Args:
            x (float): Tọa độ X tâm hiệu ứng (world coordinates)
            y (float): Tọa độ Y tâm hiệu ứng (world coordinates)
            frame_duration (int): Thời gian mỗi frame (ms)
        """
        effect = HitEffect(x, y, frame_duration)
        self.effects.append(effect)

    def update(self):
        """Cập nhật tất cả hiệu ứng và xóa những cái đã phát xong."""
        for effect in self.effects:
            effect.update()
        # Giữ lại những hiệu ứng chưa xong
        self.effects = [e for e in self.effects if not e.is_done]

    def draw(self, screen, camera):
        """Vẽ tất cả hiệu ứng đang hoạt động."""
        for effect in self.effects:
            effect.draw(screen, camera)