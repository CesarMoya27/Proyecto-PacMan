import pygame
import config

#Cargar imágenes:
def load_image(IMAGE_PATH, type=0):
    if type==1:
        img=pygame.image.load(str(IMAGE_PATH))
        img=escalar_img(img, config.SCALE_P)
        return img
    else:
        img=pygame.image.load(str(IMAGE_PATH))
        img=escalar_img(img, config.SCALE_G)
        return img
    
#Cargar sonidos:
def load_sound(SOUND_PATH, type=0):
    if type==1:
        SOUND_PATH=SOUND_PATH/config.MUSIC
        return pygame.mixer.Sound(str(SOUND_PATH))
    elif type==0:
        SOUND_PATH=SOUND_PATH/config.SOUND
        return pygame.mixer.Sound(str(SOUND_PATH))
    elif type==2:
        SOUND_PATH=SOUND_PATH/config.DIES
        return pygame.mixer.Sound(str(SOUND_PATH))

#Funcion para escalar imagenes:
def escalar_img(imagen, escala):
    w=imagen.get_width()
    h=imagen.get_height()
    nueva_imagen=pygame.transform.scale(imagen, (w*escala, h*escala))
    return nueva_imagen
    