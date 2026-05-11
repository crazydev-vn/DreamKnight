# ==================== CẤU HÌNH GAME ====================
SCREEN_WIDTH = 800  #Độ rộng cửa sổ game (pixel)
SCREEN_HEIGHT = 520  #Độ cao cửa sổ game (pixel) #400
VIEW_WIDTH = 600   # Độ cao cửa sổ game (pixel)
VIEW_HEIGHT = 400  # Vùng nhìn của camera - HIỆN TẠI CHỈ 1 PIXEL! 
MAP_WIDTH = 1920
MAP_HEIGHT = 1080

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40

FPS = 10000

PLAYER_SPEED = 3  # THÊM DÒNG NÀY
RUN_SPEED = 6  # Tốc độ chạy nhanh hơn

# ==================== ĐƯỜNG DẪN ẢNH ====================
MAP_IMAGE_PATH = "assets/map/MAP002.png"  # Đường dẫn đến file ảnh map của bạn

# Thư mục chứa ảnh animation nhân vật (đảm bảo tồn tại)
PLAYER_ASSET_DIR = "assets/knight_lv3"

# Tên ảnh theo mẫu: walk_<dir>_<idx>.png
# dir in ["up","down","left","right"], idx from 0..5
PLAYER_ANIM_PREFIX = "walk"   # kết hợp: f"{PLAYER_ASSET_DIR}/{PLAYER_ANIM_PREFIX}_{dir}_{i}.png"

DEBUG_MODE = True