import pygame

_sfx_sounds   = []
_music_volume = 0.5
_sfx_volume   = 0.5

def register_sound(sound):
    _sfx_sounds.append(sound)
    sound.set_volume(_sfx_volume)
    print(f"[SoundManager] Đăng ký sound #{len(_sfx_sounds)}, volume={_sfx_volume}, id={id(sound)}")

def set_music_volume(volume):
    global _music_volume
    _music_volume = max(0.0, min(1.0, volume))
    pygame.mixer.music.set_volume(_music_volume)

def set_sfx_volume(volume):
    global _sfx_volume
    _sfx_volume = max(0.0, min(1.0, volume))
    print(f"[SoundManager] set_sfx_volume={_sfx_volume}, tổng sound={len(_sfx_sounds)}")
    for sound in _sfx_sounds:
        try:
            sound.set_volume(_sfx_volume)
        except:
            pass

def get_music_volume():
    return _music_volume

def get_sfx_volume():
    return _sfx_volume