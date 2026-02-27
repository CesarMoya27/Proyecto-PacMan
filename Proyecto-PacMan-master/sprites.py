import pygame
from config import *
from pathlib import Path
from load_functions import *
import random

#Paredes del juego:
class Wall:
    def __init__(self, x, y):
        self.rect=pygame.Rect(x*WALL_SIZE_WIDTH, y*WALL_SIZE_HEIGHT, WALL_SIZE_WIDTH, WALL_SIZE_HEIGHT)
    
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

#Monedas:
class Coin:
    def __init__(self, x, y, big=False):
        #Posicion de la moneda:
        self.x=x*WALL_SIZE_WIDTH+WALL_SIZE_WIDTH/2
        self.y=y*WALL_SIZE_HEIGHT+WALL_SIZE_HEIGHT/2
        self.big=big

        if not big:
            self.rect=pygame.Rect(x*COIN_SIZE, y*COIN_SIZE, COIN_SIZE, COIN_SIZE)
        else:
            self.rect=pygame.Rect(x*B_COIN_SIZE, y*B_COIN_SIZE, B_COIN_SIZE, B_COIN_SIZE)
        self.rect.center=(self.x, self.y)

    def draw(self, screen):
        pygame.draw.rect(screen, ORANGE, self.rect)

#Pac-Man:
class Jugador:
    def __init__(self, x, y):
        self.initial_x=x*WALL_SIZE_WIDTH+WALL_SIZE_WIDTH/2
        self.initial_y=y*WALL_SIZE_HEIGHT+WALL_SIZE_HEIGHT/2
        self.x=self.initial_x
        self.y=self.initial_y

        self.animacion=[]

        self.is_moving=False
        self.was_moving=False

        self.flip=False
        self.life=PLAYER_LIFES

        self.can_move=True
        self.respawn_timer=0

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

    def respawn(self):
        self.x=self.initial_x
        self.y=self.initial_y
        self.rect.center=(self.x, self.y)
        self.can_move=False
        self.respawn_timer=pygame.time.get_ticks()

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
        if self.x>BASE_WIDTH+SCALE_P:
            self.x=0-2*SCALE_P
        if self.x<0-2*SCALE_P:
            self.x=BASE_WIDTH+SCALE_P

        if self.y>BASE_HEIGHT+SCALE_P:
            self.y=0-2*SCALE_P
        if self.y<0-2*SCALE_P:
            self.y=BASE_HEIGHT+SCALE_P

        self.rect.center=(self.x, self.y)

        if self.dx!=0 or self.dy!=0:
            self.is_moving=True
        else:
            self.is_moving=False

    def handle_input(self):
        #Reiniciar la velocidad:
        self.dx=0
        self.dy=0
        if self.can_move:
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
        
        if not self.can_move:
            current_time=pygame.time.get_ticks()
            if current_time-self.respawn_timer>PLAYER_RESPAWN_TIME:
                self.can_move=True

        self.move(wall)
    
    def draw_lifes(self, screen):
        for i in range (self.life):
            if self.life>=1:
                screen.blit(LIFE, (5+i*40, BASE_HEIGHT-25))

    def draw(self, screen):
        image_flip=pygame.transform.flip(self.image, self.flip, False)
        screen.blit(image_flip, self.rect)

#Fantasmas:
class Ghost:
    def __init__(self, x, y, type=0):
        self.initial_x=x*WALL_SIZE_WIDTH+WALL_SIZE_WIDTH/2
        self.initial_y=y*WALL_SIZE_HEIGHT+WALL_SIZE_HEIGHT/2
        self.x=self.initial_x
        self.y=self.initial_y

        self.animacion_normal=[]
        self.animacion_vulnerable=[]

        self.visible=True
        self.flip=False
        self.vulnerable=False
        self.can_move=True
        self.dead=False

        self.respawn_timer=0

        for i in range(2):
            if type==1:
                self.ruta_temp=ASSETS_DIR/"blinky"/f"blinky{i+1}.png"
                self.image=load_image(self.ruta_temp)
                self.animacion_normal.append(self.image)
            elif type==2:
                self.ruta_temp=ASSETS_DIR/"pinky"/f"pinky{i+1}.png"
                self.image=load_image(self.ruta_temp)
                self.animacion_normal.append(self.image)
            elif type==3:
                self.ruta_temp=ASSETS_DIR/"inky"/f"inky{i+1}.png"
                self.image=load_image(self.ruta_temp)
                self.animacion_normal.append(self.image)
            elif type==4:
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
        self.direction=random.randint(0,3)
        self.dir_timer=pygame.time.get_ticks()
    
    def vulnerable_state(self, vulnerable):
        #Cambiar el estado de vulnerabilidad del fantasma:
        self.vulnerable=vulnerable
    
    #Ocultar al fantasma temporalmente:
    def hide(self):
        self.visible=False
        self.rect.center=(1000, 1000)
        self.respawn_timer=pygame.time.get_ticks()
    
    def respawn(self):
        self.x=self.initial_x
        self.y=self.initial_y
        self.rect.center=(self.x, self.y)

        self.respawn_timer=pygame.time.get_ticks()

        self.can_move=False
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
        #Calcular el movimiento segun la dirección:
        self.dx=0
        self.dy=0

        if self.can_move:
            if not self.vulnerable:
                if self.direction==RIGHT:
                    self.dx=GHOST_SPEED
                elif self.direction==LEFT:
                    self.dx=-GHOST_SPEED
                elif self.direction==UP:
                    self.dy=-GHOST_SPEED
                elif self.direction==DOWN:
                    self.dy=GHOST_SPEED
            else:
                if self.direction==RIGHT:
                    self.dx=GHOST_SPEED_V
                elif self.direction==LEFT:
                    self.dx=-GHOST_SPEED_V
                elif self.direction==UP:
                    self.dy=-GHOST_SPEED_V
                elif self.direction==DOWN:
                    self.dy=GHOST_SPEED_V

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
        if self.x>BASE_WIDTH-SCALE_G:
            self.x=0
        if self.x<0:
            self.x=BASE_WIDTH-SCALE_G
        if self.y>BASE_HEIGHT-SCALE_G:
            self.y=0
        if self.y<0:
            self.y=BASE_HEIGHT-SCALE_G

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

        if not self.can_move and self.dead:
            self.can_move=True
            self.dead=False
        elif not self.can_move:
            current_time=pygame.time.get_ticks()
            if current_time-self.respawn_timer>=PLAYER_RESPAWN_TIME:
                self.can_move=True

    def draw(self, screen):
        image_flip=pygame.transform.flip(self.image, self.flip, False)
        screen.blit(image_flip, self.rect)