import pygame 

class Camera:
    """Lớp quản lý camera - theo dõi nhân vật và xác định vùng hiển thị"""
    def __init__(self, map_width, map_height):
        from config import VIEW_WIDTH, VIEW_HEIGHT
        
        # Vị trí góc trên bên trái của camera trong hệ tọa độ bản đồ (pixel)
        # Đây là điểm bắt đầu của vùng nhìn thấy trên bản đồ
        self.x = 0  # Tọa độ X của camera trên bản đồ
        self.y = 0  # Tọa độ Y của camera trên bản đồ
        
        # Kích thước toàn bộ bản đồ (pixel)
        # Dùng để tính toán giới hạn di chuyển camera
        self.map_width = map_width    # Chiều rộng toàn bộ bản đồ (px)
        self.map_height = map_height  # Chiều cao toàn bộ bản đồ (px)
        
        # Kích thước vùng nhìn thấy trên màn hình (viewport) (pixel)
        # Đây là phần bản đồ được hiển thị lên màn hình người chơi
        self.view_width = VIEW_WIDTH    # VIEW_WIDTH từ config (thường 800-1200px)
        self.view_height = VIEW_HEIGHT  # VIEW_HEIGHT từ config (thường 600-800px)
    
    #Cập nhật vị trí camera để theo dõi nhân vật
    def update(self, target):
        
        # Tính tâm của đối tượng mục tiêu (nhân vật) (pixel)
        target_center_x = target.x + target.width // 2      # Tâm X của nhân vật
        target_center_y = target.y + target.height // 2     # Tâm Y của nhân vật
        
        # Đặt vị trí camera sao cho nhân vật ở giữa màn hình (pixel)
        self.x = target_center_x - self.view_width // 2     # Camera X = tâm nhân vật - nửa chiều rộng màn hình
        self.y = target_center_y - self.view_height // 2    # Camera Y = tâm nhân vật - nửa chiều cao màn hình
        
        # Giới hạn camera trong phạm vi bản đồ, không cho ra khỏi biên (pixel)
        # Đảm bảo camera không hiển thị vùng ngoài bản đồ
        self.x = max(0, min(self.x, self.map_width - self.view_width))      # Giới hạn X: từ 0 đến (map_width - view_width)
        self.y = max(0, min(self.y, self.map_height - self.view_height))    # Giới hạn Y: từ 0 đến (map_height - view_height)
    
    #Cập nhật kích thước tầm nhìn khi màn hình thay đổi   
    def update_view_size(self, width, height):
        # Phương thức này cho phép thay đổi kích thước viewport động
        # Hữu ích khi resize cửa sổ game hoặc thay đổi độ phân giải
        self.view_width = width     # Chiều rộng mới của viewport (px)
        self.view_height = height   # Chiều cao mới của viewport (px) 