import pygame
from config import *
from pathlib import Path
from load_functions import *
import random

GAME_DIR=Path(__file__).resolve().parent
ASSETS_DIR=GAME_DIR/"assets"
PLAYER_DIR=ASSETS_DIR/"player"

class Wall:
    def __init__(self, x, y):
        self.rect=pygame.Rect(x*WALL_SIZE, y*WALL_SIZE, WALL_SIZE, WALL_SIZE)
    
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

class Coin:
    def __init__(self, x, y, big=False):
        #Posicion de la moneda:
        self.x=x*WALL_SIZE+WALL_SIZE/2
        self.y=y*WALL_SIZE+WALL_SIZE/2
        self.big=big

        if not big:
            self.rect=pygame.Rect(x*COIN_SIZE, y*COIN_SIZE, COIN_SIZE, COIN_SIZE)
        else:
            self.rect=pygame.Rect(x*B_COIN_SIZE, y*B_COIN_SIZE, B_COIN_SIZE, B_COIN_SIZE)
        self.rect.center=(self.x, self.y)

    def draw(self, screen):
        pygame.draw.rect(screen, NARANJA, self.rect)

class Jugador:
    def __init__(self, x, y):
        self.x=x*WALL_SIZE+WALL_SIZE/2
        self.y=y*WALL_SIZE+WALL_SIZE/2
        self.animacion=[]

        self.is_moving=False
        self.was_moving=False

        self.flip=False

        for i in range(3):
            self.ruta_temp=PLAYER_DIR/f"player{i+1}.png"
            self.image=load_image(self.ruta_temp, 1)
            self.animacion.append(self.image)

        #Crear el rectángulo del personaje:
        self.rect=self.image.get_rect(center=(self.x, self.y))

        #Imagen de la animacion que se está mostrando:
        self.indice_frame=0

        #Almacenamiento de la hora actual (milisegundos) desde que se inicia el juego:
        self.update_time=pygame.time.get_ticks()


    def move(self, walls):
        #Intentar movimiento en x:
        if self.dx!=0:
            #Comprobar colision en x:
            if not self.check_collision(walls, self.dx, 0):
                self.x+=self.dx
            else:
                #Intentar deslizar verticalmente si hay colision:
                if not self.check_collision(walls, self.dx, -SLIDE_SPEED):
                    if not self.check_collision(walls, self.dx, SLIDE_SPEED):
                        self.y+=SLIDE_SPEED
                    else:
                        self.y-=SLIDE_SPEED

        #Intentar movimiento en y:
        if self.dy!=0:
            #Comprobar colision en y:
            if not self.check_collision(walls, 0, self.dy):
                self.y+=self.dy
            else:
                #Intentar deslizar horizontalmente si hay colision:
                if not self.check_collision(walls, -SLIDE_SPEED, self.dy):
                    if not self.check_collision(walls, SLIDE_SPEED, self.dy):
                        self.x+=SLIDE_SPEED
                    else:
                        self.x-=SLIDE_SPEED

        #Actualizar a la nueva posicion:
        self.rect.center=(self.x, self.y)

        #Manejar los límites en pantalla del jugador:
        if self.x>ANCHO_VENT+SCALE_P:
            self.x=0-2*SCALE_P
        if self.x<0-2*SCALE_P:
            self.x=ANCHO_VENT+SCALE_P

        if self.y>ALTO_VENT+SCALE_P:
            self.y=0-2*SCALE_P
        if self.y<0-2*SCALE_P:
            self.y=ALTO_VENT+SCALE_P

        self.rect.center=(self.x, self.y)

        if self.dx!=0 or self.dy!=0:
            self.is_moving=True
        else:
            self.is_moving=False

    def handle_input(self):
        #Reiniciar la velocidad:
        self.dx=0
        self.dy=0

        keys=pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.dx=PLAYER_SPEED
        elif keys[pygame.K_LEFT]:
            self.dx=-PLAYER_SPEED
        elif keys[pygame.K_DOWN]:
            self.dy=PLAYER_SPEED
        elif keys[pygame.K_UP]:
            self.dy=-PLAYER_SPEED

        if self.dx<0:
            self.flip=True
        if self.dx>0:
            self.flip=False
    
    def check_collision(self, walls, dx=0, dy=0):
        #Comprobar si hay colision en un posicion futura:
        #Crea un rectángulo temporal en la posición futura:
        future_rect=self.rect.copy()
        future_rect.x+=dx
        future_rect.y+=dy

        #Comprobar colisión con cada pared:
        for wall in walls:
            if future_rect.colliderect(wall.rect):
                return True
        return False
        
    def update(self, wall):

        self.was_moving=self.is_moving

        self.handle_input()

        cooldown=100
        self.image=self.animacion[self.indice_frame]
        if pygame.time.get_ticks()-self.update_time>=cooldown:
            self.indice_frame+=1
            self.update_time=pygame.time.get_ticks()

        if self.indice_frame>=len(self.animacion):
            self.indice_frame=0

        self.move(wall)

    def draw(self, screen):
        image_flip=pygame.transform.flip(self.image, self.flip, False)
        screen.blit(image_flip, self.rect)

class Blinky:
    def __init__(self, x, y):
        self.initial_x=x*WALL_SIZE+WALL_SIZE/2
        self.initial_y=y*WALL_SIZE+WALL_SIZE/2
        self.x=self.initial_x
        self.y=self.initial_y

        self.animacion_normal=[]
        self.animacion_vulnerable=[]

        self.visible=True
        self.flip=False
        self.vulnerable=False
        self.respawn_timer=0

        for i in range(2):
            self.ruta_temp=ASSETS_DIR/"blinky"/f"blinky{i+1}.png"
            self.image=load_image(self.ruta_temp)
            self.animacion_normal.append(self.image)

        for i in range(2):
            self.ruta_temp=ASSETS_DIR/"blue"/f"blue{i+1}.png"
            self.image=load_image(self.ruta_temp)
            self.animacion_vulnerable.append(self.image)       

        self.rect=self.image.get_rect(center=(self.x, self.y))

        #Imagen de la animacion que se está mostrando:
        self.indice_frame=0

        #Almacenamiento de la hora actual (milisegundos) desde que se inicia el juego:
        self.update_time=pygame.time.get_ticks()

        #Variables de movimiento:
        self.direction=random.randint(0,3)
        self.dir_timer=pygame.time.get_ticks()
    
    def vulnerable_state(self, vulnerable):
        #Cambiar el estado de vulnerabilidad del fantasma:
        self.vulnerable=vulnerable
    
    #Ocultar al fantasma temporalmente:
    def hide(self):
        self.visible=False
        self.respawn_timer=pygame.time.get_ticks()
    
    def respawn(self):
        self.x=self.initial_x
        self.y=self.initial_y
        self.rect.center=(self.x, self.y)
        self.visible=True
        self.vulnerable=False

    def change_dir(self):
        #Cambiar la direccion del fantasma aleatoriamente:
        self.direction=random.randint(0,3)
        self.dir_timer=pygame.time.get_ticks()

    def move(self, walls):
        if not self.visible:
            current_time=pygame.time.get_ticks()
            if current_time-self.respawn_timer>GHOST_RESPAWN_TIME:
                self.respawn()
            return

        #Mover fantasma y manejar las colisiones:
        #Cambiar dirección después de cierto tiempo:
        current_time=pygame.time.get_ticks()
        if current_time-self.dir_timer>3000:
            self.change_dir()
        
        #Calcular el movimiento segun la dirección:
        self.dx=0
        self.dy=0

        if self.direction==RIGHT:
            self.dx=GHOST_SPEED
        elif self.direction==LEFT:
            self.dx=-GHOST_SPEED
        elif self.direction==UP:
            self.dy=-GHOST_SPEED
        elif self.direction==DOWN:
            self.dy=GHOST_SPEED

        #Comprobar la colision en la posicion:
        new_rect=self.rect.copy()
        new_rect.x+=self.dx
        new_rect.y+=self.dy

        for wall in walls:
            if new_rect.colliderect(wall.rect):
                self.change_dir()

        #Intentar movimiento en x:
        if self.dx!=0:
            #Comprobar colision en x:
            if not self.check_collision(walls, self.dx, 0):
                self.x+=self.dx
            else:
                #Intentar deslizar verticalmente si hay colision:
                if not self.check_collision(walls, self.dx, -SLIDE_SPEED):
                    if not self.check_collision(walls, self.dx, SLIDE_SPEED):
                        self.y+=SLIDE_SPEED
                    else:
                        self.y-=SLIDE_SPEED
                        self.change_dir()

        #Intentar movimiento en y:
        if self.dy!=0:
            #Comprobar colision en y:
            if not self.check_collision(walls, 0, self.dy):
                self.y+=self.dy
            else:
                #Intentar deslizar horizontalmente si hay colision:
                if not self.check_collision(walls, -SLIDE_SPEED, self.dy):
                    if not self.check_collision(walls, SLIDE_SPEED, self.dy):
                        self.x+=SLIDE_SPEED
                    else:
                        self.x-=SLIDE_SPEED
                        self.change_dir()

        #Actualizar a la nueva posicion:
        self.rect.center=(self.x, self.y)

        #Manejar los límites del enemigo en la pantalla:
        if self.x>ANCHO_VENT-SCALE_G:
            self.x=0
        if self.x<0:
            self.x=ANCHO_VENT-SCALE_G
        if self.y>ALTO_VENT-SCALE_G:
            self.y=0
        if self.y<0:
            self.y=ALTO_VENT-SCALE_G

    def check_collision(self, walls, dx=0, dy=0):
        #Comprobar si hay colision en un posicion futura:
        #Crea un rectángulo temporal en la posición futura:
        future_rect=self.rect.copy()
        future_rect.x+=dx
        future_rect.y+=dy

        #Comprobar colisión con cada pared:
        for wall in walls:
            if future_rect.colliderect(wall.rect):
                return True
        return False

    def update(self, walls):
        cooldown=100
        if not self.vulnerable:
            self.image=self.animacion_normal[self.indice_frame]
        else:
            self.image=self.animacion_vulnerable[self.indice_frame]

        if pygame.time.get_ticks()-self.update_time>=cooldown:
            self.indice_frame+=1
            self.update_time=pygame.time.get_ticks()

        if self.indice_frame>=len(self.animacion_normal):
            self.indice_frame=0

        self.move(walls)

    def draw(self, screen):
        image_flip=pygame.transform.flip(self.image, self.flip, False)
        if self.visible:
            screen.blit(image_flip, self.rect)

class Pinky:
    def __init__(self, x, y):
        self.initial_x=x*WALL_SIZE+WALL_SIZE/2
        self.initial_y=y*WALL_SIZE+WALL_SIZE/2
        self.x=self.initial_x
        self.y=self.initial_y

        self.animacion_normal=[]
        self.animacion_vulnerable=[]

        self.flip=False
        self.vulnerable=False
        self.visible=True
        self.respawn_timer=0

        for i in range(2):
            self.ruta_temp=ASSETS_DIR/"pinky"/f"pinky{i+1}.png"
            self.image=load_image(self.ruta_temp)
            self.animacion_normal.append(self.image)

        for i in range(2):
            self.ruta_temp=ASSETS_DIR/"blue"/f"blue{i+1}.png"
            self.image=load_image(self.ruta_temp)
            self.animacion_vulnerable.append(self.image)

        self.rect=self.image.get_rect(center=(self.x, self.y))

        #Imagen de la animacion que se está mostrando:
        self.indice_frame=0

        #Almacenamiento de la hora actual (milisegundos) desde que se inicia el juego:
        self.update_time=pygame.time.get_ticks()

        #Variables de movimiento:
        self.direction=(random.randint(0,3)-1)%4
        self.dir_timer=pygame.time.get_ticks()
    
    def vulnerable_state(self, vulnerable):
        self.vulnerable=vulnerable

    def hide(self):
        self.visible=False
        self.respawn_timer=pygame.time.get_ticks()
    
    def respawn(self):
        self.x=self.initial_x
        self.y=self.initial_y
        self.rect.center=(self.x, self.y)
        self.visible=True
        self.vulnerable=False

    def change_dir(self):
        #Cambiar la direccion del fantasma aleatoriamente:
        self.direction=(random.randint(0,3)-1)%4
        self.dir_timer=pygame.time.get_ticks()

    def move(self, walls):
        if not self.visible:
            current_time=pygame.time.get_ticks()
            if current_time-self.respawn_timer>GHOST_RESPAWN_TIME:
                self.respawn()
            return
 
        #Mover fantasma y manejar las colisiones:
        #Cambiar dirección después de cierto tiempo:
        current_time=pygame.time.get_ticks()
        if current_time-self.dir_timer>5000:
            self.change_dir()
        
        #Calcular el movimiento segun la dirección:
        self.dx=0
        self.dy=0

        if self.direction==RIGHT:
            self.dx=GHOST_SPEED
        elif self.direction==LEFT:
            self.dx=-GHOST_SPEED
        elif self.direction==UP:
            self.dy=-GHOST_SPEED
        elif self.direction==DOWN:
            self.dy=GHOST_SPEED

        #Comprobar la colision en la posicion:
        new_rect=self.rect.copy()
        new_rect.x+=self.dx
        new_rect.y+=self.dy

        for wall in walls:
            if new_rect.colliderect(wall.rect):
                self.change_dir()

        #Intentar movimiento en x:
        if self.dx!=0:
            #Comprobar colision en x:
            if not self.check_collision(walls, self.dx, 0):
                self.x+=self.dx
            else:
                #Intentar deslizar verticalmente si hay colision:
                if not self.check_collision(walls, self.dx, -SLIDE_SPEED):
                    if not self.check_collision(walls, self.dx, SLIDE_SPEED):
                        self.y+=SLIDE_SPEED
                    else:
                        self.y-=SLIDE_SPEED
                        self.change_dir()

        #Intentar movimiento en y:
        if self.dy!=0:
            #Comprobar colision en y:
            if not self.check_collision(walls, 0, self.dy):
                self.y+=self.dy
            else:
                #Intentar deslizar horizontalmente si hay colision:
                if not self.check_collision(walls, -SLIDE_SPEED, self.dy):
                    if not self.check_collision(walls, SLIDE_SPEED, self.dy):
                        self.x+=SLIDE_SPEED
                    else:
                        self.x-=SLIDE_SPEED
                        self.change_dir()

        #Actualizar a la nueva posicion:
        self.rect.center=(self.x, self.y)

        #Manejar los límites del enemigo en la pantalla:
        if self.x>ANCHO_VENT-SCALE_G:
            self.x=0
        if self.x<0:
            self.x=ANCHO_VENT-SCALE_G
        if self.y>ALTO_VENT-SCALE_G:
            self.y=0
        if self.y<0:
            self.y=ALTO_VENT-SCALE_G

    def check_collision(self, walls, dx=0, dy=0):
        #Comprobar si hay colision en un posicion futura:
        #Crea un rectángulo temporal en la posición futura:
        future_rect=self.rect.copy()
        future_rect.x+=dx
        future_rect.y+=dy

        #Comprobar colisión con cada pared:
        for wall in walls:
            if future_rect.colliderect(wall.rect):
                return True
        return False

    def update(self, walls):
        cooldown=100
        if not self.vulnerable:
            self.image=self.animacion_normal[self.indice_frame]
        else:
            self.image=self.animacion_vulnerable[self.indice_frame]

        if pygame.time.get_ticks()-self.update_time>=cooldown:
            self.indice_frame+=1
            self.update_time=pygame.time.get_ticks()

        if self.indice_frame>=len(self.animacion_normal):
            self.indice_frame=0

        self.move(walls)

    def draw(self, screen):
        image_flip=pygame.transform.flip(self.image, self.flip, False)
        if self.visible:
            screen.blit(image_flip, self.rect)

class Inky:
    def __init__(self, x, y):
        self.initial_x=x*WALL_SIZE+WALL_SIZE/2
        self.initial_y=y*WALL_SIZE+WALL_SIZE/2
        self.x=self.initial_x
        self.y=self.initial_y

        self.animacion_normal=[]
        self.animacion_vulnerable=[]

        self.flip=False
        self.vulnerable=False
        self.visible=True
        self.respawn_timer=0

        for i in range(2):
            self.ruta_temp=ASSETS_DIR/"inky"/f"inky{i+1}.png"
            self.image=load_image(self.ruta_temp)
            self.animacion_normal.append(self.image)
        
        for i in range(2):
            self.ruta_temp=ASSETS_DIR/"blue"/f"blue{i+1}.png"
            self.image=load_image(self.ruta_temp)
            self.animacion_vulnerable.append(self.image)

        self.rect=self.image.get_rect(center=(self.x, self.y))

        #Imagen de la animacion que se está mostrando:
        self.indice_frame=0

        #Almacenamiento de la hora actual (milisegundos) desde que se inicia el juego:
        self.update_time=pygame.time.get_ticks()

        #Variables de movimiento:
        self.direction=random.randint(0,3)
        self.dir_timer=pygame.time.get_ticks()

    def vulnerable_state(self, vulnerable):
        self.vulnerable=vulnerable

    def hide(self):
        self.visible=False
        self.respawn_timer=pygame.time.get_ticks()
    
    def respawn(self):
        self.x=self.initial_x
        self.y=self.initial_y
        self.rect.center=(self.x, self.y)
        self.visible=True
        self.vulnerable=False

    def change_dir(self):
        #Cambiar la direccion del fantasma aleatoriamente:
        if self.direction in [RIGHT, LEFT]:
            self.direction=random.choice([UP, DOWN])
        else:
            self.direction=random.choice([RIGHT, LEFT])
        self.dir_timer=pygame.time.get_ticks()

    def move(self, walls):
        if not self.visible:
            current_time=pygame.time.get_ticks()
            if current_time-self.respawn_timer>GHOST_RESPAWN_TIME:
                self.respawn()
            return

        #Mover fantasma y manejar las colisiones:
        #Cambiar dirección después de cierto tiempo:
        current_time=pygame.time.get_ticks()
        if current_time-self.dir_timer>4500:
            self.change_dir()
        
        #Calcular el movimiento segun la dirección:
        self.dx=0
        self.dy=0

        if self.direction==RIGHT:
            self.dx=GHOST_SPEED
        elif self.direction==LEFT:
            self.dx=-GHOST_SPEED
        elif self.direction==UP:
            self.dy=-GHOST_SPEED
        elif self.direction==DOWN:
            self.dy=GHOST_SPEED

        #Comprobar la colision en la posicion:
        new_rect=self.rect.copy()
        new_rect.x+=self.dx
        new_rect.y+=self.dy

        for wall in walls:
            if new_rect.colliderect(wall.rect):
                self.change_dir()

        #Intentar movimiento en x:
        if self.dx!=0:
            #Comprobar colision en x:
            if not self.check_collision(walls, self.dx, 0):
                self.x+=self.dx
            else:
                #Intentar deslizar verticalmente si hay colision:
                if not self.check_collision(walls, self.dx, -SLIDE_SPEED):
                    if not self.check_collision(walls, self.dx, SLIDE_SPEED):
                        self.y+=SLIDE_SPEED
                    else:
                        self.y-=SLIDE_SPEED
                        self.change_dir()

        #Intentar movimiento en y:
        if self.dy!=0:
            #Comprobar colision en y:
            if not self.check_collision(walls, 0, self.dy):
                self.y+=self.dy
            else:
                #Intentar deslizar horizontalmente si hay colision:
                if not self.check_collision(walls, -SLIDE_SPEED, self.dy):
                    if not self.check_collision(walls, SLIDE_SPEED, self.dy):
                        self.x+=SLIDE_SPEED
                    else:
                        self.x-=SLIDE_SPEED
                        self.change_dir()

        #Actualizar a la nueva posicion:
        self.rect.center=(self.x, self.y)

        #Manejar los límites del enemigo en la pantalla:
        if self.x>ANCHO_VENT-SCALE_G:
            self.x=0
        if self.x<0:
            self.x=ANCHO_VENT-SCALE_G
        if self.y>ALTO_VENT-SCALE_G:
            self.y=0
        if self.y<0:
            self.y=ALTO_VENT-SCALE_G

    def check_collision(self, walls, dx=0, dy=0):
        #Comprobar si hay colision en un posicion futura:
        #Crea un rectángulo temporal en la posición futura:
        future_rect=self.rect.copy()
        future_rect.x+=dx
        future_rect.y+=dy

        #Comprobar colisión con cada pared:
        for wall in walls:
            if future_rect.colliderect(wall.rect):
                return True
        return False

    def update(self, walls):
        cooldown=100
        if not self.vulnerable:
            self.image=self.animacion_normal[self.indice_frame]
        else:
            self.image=self.animacion_vulnerable[self.indice_frame]
        if pygame.time.get_ticks()-self.update_time>=cooldown:
            self.indice_frame+=1
            self.update_time=pygame.time.get_ticks()

        if self.indice_frame>=len(self.animacion_normal):
            self.indice_frame=0

        self.move(walls)

    def draw(self, screen):
        image_flip=pygame.transform.flip(self.image, self.flip, False)
        if self.visible:
            screen.blit(image_flip, self.rect)

class Clyde:
    def __init__(self, x, y):
        self.initial_x=x*WALL_SIZE+WALL_SIZE/2
        self.initial_y=y*WALL_SIZE+WALL_SIZE/2
        self.x=self.initial_x
        self.y=self.initial_y

        self.animacion_normal=[]
        self.animacion_vulnerable=[]

        self.flip=False
        self.vulnerable=False
        self.visible=True
        self.respawn_timer=0

        for i in range(2):
            self.ruta_temp=ASSETS_DIR/"clyde"/f"clyde{i+1}.png"
            self.image=load_image(self.ruta_temp)
            self.animacion_normal.append(self.image)
        
        for i in range(2):
            self.ruta_temp=ASSETS_DIR/"blue"/f"blue{i+1}.png"
            self.image=load_image(self.ruta_temp)
            self.animacion_vulnerable.append(self.image)

        self.rect=self.image.get_rect(center=(self.x, self.y))

        #Imagen de la animacion que se está mostrando:
        self.indice_frame=0

        #Almacenamiento de la hora actual (milisegundos) desde que se inicia el juego:
        self.update_time=pygame.time.get_ticks()

        #Variables de movimiento:
        self.direction=(random.randint(0,3)-1)%4
        self.dir_timer=pygame.time.get_ticks()

    def vulnerable_state(self, vulnerable):
        self.vulnerable=vulnerable

    def hide(self):
        self.visible=False
        self.respawn_timer=pygame.time.get_ticks()
    
    def respawn(self):
        self.x=self.initial_x
        self.y=self.initial_y
        self.rect.center=(self.x, self.y)
        self.visible=True
        self.vulnerable=False

    def change_dir(self):
        #Cambiar la direccion del fantasma aleatoriamente:
        self.direction=(random.randint(0,3)-1)%4
        self.dir_timer=pygame.time.get_ticks()

    def move(self, walls): 
        if not self.visible:
            current_time=pygame.time.get_ticks()
            if current_time-self.respawn_timer>GHOST_RESPAWN_TIME:
                self.respawn()
            return

        #Mover fantasma y manejar las colisiones:
        #Cambiar dirección después de cierto tiempo:
        current_time=pygame.time.get_ticks()
        if current_time-self.dir_timer>2500:
            self.change_dir()
        
        #Calcular el movimiento segun la dirección:
        self.dx=0
        self.dy=0

        if self.direction==RIGHT:
            self.dx=GHOST_SPEED
        elif self.direction==LEFT:
            self.dx=-GHOST_SPEED
        elif self.direction==UP:
            self.dy=-GHOST_SPEED
        elif self.direction==DOWN:
            self.dy=GHOST_SPEED

        #Comprobar la colision en la posicion:
        new_rect=self.rect.copy()
        new_rect.x+=self.dx
        new_rect.y+=self.dy

        for wall in walls:
            if new_rect.colliderect(wall.rect):
                self.change_dir()

        #Intentar movimiento en x:
        if self.dx!=0:
            #Comprobar colision en x:
            if not self.check_collision(walls, self.dx, 0):
                self.x+=self.dx
            else:
                #Intentar deslizar verticalmente si hay colision:
                if not self.check_collision(walls, self.dx, -SLIDE_SPEED):
                    if not self.check_collision(walls, self.dx, SLIDE_SPEED):
                        self.y+=SLIDE_SPEED
                    else:
                        self.y-=SLIDE_SPEED
                        self.change_dir()

        #Intentar movimiento en y:
        if self.dy!=0:
            #Comprobar colision en y:
            if not self.check_collision(walls, 0, self.dy):
                self.y+=self.dy
            else:
                #Intentar deslizar horizontalmente si hay colision:
                if not self.check_collision(walls, -SLIDE_SPEED, self.dy):
                    if not self.check_collision(walls, SLIDE_SPEED, self.dy):
                        self.x+=SLIDE_SPEED
                    else:
                        self.x-=SLIDE_SPEED
                        self.change_dir()

        #Actualizar a la nueva posicion:
        self.rect.center=(self.x, self.y)

        #Manejar los límites del enemigo en la pantalla:
        if self.x>ANCHO_VENT-SCALE_G:
            self.x=0
        if self.x<0:
            self.x=ANCHO_VENT-SCALE_G
        if self.y>ALTO_VENT-SCALE_G:
            self.y=0
        if self.y<0:
            self.y=ALTO_VENT-SCALE_G

    def check_collision(self, walls, dx=0, dy=0):
        #Comprobar si hay colision en un posicion futura:
        #Crea un rectángulo temporal en la posición futura:
        future_rect=self.rect.copy()
        future_rect.x+=dx
        future_rect.y+=dy

        #Comprobar colisión con cada pared:
        for wall in walls:
            if future_rect.colliderect(wall.rect):
                return True
        return False

    def update(self, walls):
        cooldown=100
        if not self.vulnerable:
            self.image=self.animacion_normal[self.indice_frame]
        else:
            self.image=self.animacion_vulnerable[self.indice_frame]

        if pygame.time.get_ticks()-self.update_time>=cooldown:
            self.indice_frame+=1
            self.update_time=pygame.time.get_ticks()

        if self.indice_frame>=len(self.animacion_normal):
            self.indice_frame=0
        
        self.move(walls)

    def draw(self, screen):
        image_flip=pygame.transform.flip(self.image, self.flip, False)
        if self.visible:
            screen.blit(image_flip, self.rect)