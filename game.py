import pygame
from config import *
from sprites import *

class Game:
    def __init__(self):

        #Creando la ventana:
        self.screen=pygame.display.set_mode((ANCHO_VENT, ALTO_VENT))
        pygame.display.set_caption("Pac-Man")

        #Reloj para el juego:
        self.clock=pygame.time.Clock()

        #Controlar la ejecución del juego:
        self.running=True
        self.game_state=INTRO

        #Cargar los sonidos:
        self.music=load_sound(SOUNDS_DIR, 1)
        self.sound=load_sound(SOUNDS_DIR)
        self.dies=load_sound(SOUNDS_DIR,2)
        self.dead=False

        #Ajustar el volumen:
        self.music.set_volume(MUSIC_VOL)
        self.sound.set_volume(SOUND_VOL)
        self.dies.set_volume(SOUND_VOL)

        #Crear al jugador:
        self.coins=[]
        self.walls=[]
        self.score=0
        self.create_level()

        #Fuente para el texto:
        self.font=pygame.font.Font(None, 36)
        self.font_big=pygame.font.Font(None, 74)

        #Iniciar la música:
        self.music.play(-1)

    #Pantalla de inicio:
    def show_intro_screen(self):
        title_text=load_image(str(TITLE_DIR))
        title_text=escalar_img(title_text, 0.4)
        start_text=self.font.render('Presiona ESPACIO para Comenzar', True, WHITE)
        controls_text=self.font.render('Usa las FLECHAS para moverte', True, WHITE)

        title_rect=title_text.get_rect(center=(ANCHO_VENT/2, ALTO_VENT/3))
        start_rect=start_text.get_rect(center=(ANCHO_VENT/2, ALTO_VENT/2))
        controls_rect=controls_text.get_rect(center=(ANCHO_VENT/2, 2*ALTO_VENT/3))

        self.screen.fill(BLACK)
        self.screen.blit(title_text, title_rect)
        self.screen.blit(start_text, start_rect)
        self.screen.blit(controls_text, controls_rect)
    
    #Pantalla de game over:
    def show_game_over_screen(self):
        game_over_text=self.font_big.render('JUEGO TERMINADO', True, RED)
        score_text=self.font_big.render(f'Puntaje: {self.score}', True, WHITE)
        restart_text=self.font.render('Presione ESPACIO para jugar de nuevo', True, WHITE)

        game_over_rect=game_over_text.get_rect(center=(ANCHO_VENT/2, ALTO_VENT/3))
        score_rect=score_text.get_rect(center=(ANCHO_VENT/2, ALTO_VENT/2))
        restart_rect=restart_text.get_rect(center=(ANCHO_VENT/2, 2*ALTO_VENT/3))   

        self.screen.fill(BLACK)
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)  

    #Pantalla de victoria:
    def show_victory_screen(self):
        victory_text=self.font_big.render('VICTORIA', True, COLOR_P)
        score_text=self.font_big.render(f'Puntaje: {self.score}', True, WHITE)
        restart_text=self.font.render('Presione ESPACIO para jugar de nuevo', True, WHITE)

        victory_rect=victory_text.get_rect(center=(ANCHO_VENT/2, ALTO_VENT/3))
        score_rect=score_text.get_rect(center=(ANCHO_VENT/2, ALTO_VENT/2))
        restart_rect=restart_text.get_rect(center=(ANCHO_VENT/2, 2*ALTO_VENT/3))   

        self.screen.fill(BLACK)
        self.screen.blit(victory_text, victory_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)  
          

    #Crear el nivel:
    def create_level(self):
        for i_fila, fila in enumerate(NIVEL):
            for i_col, col in enumerate(fila):
                if col=="1":
                    self.walls.append(Wall(i_col, i_fila))
                elif col=="P":
                    self.player=Jugador(i_col, i_fila)
                elif col=="0":
                    self.coins.append(Coin(i_col, i_fila))
                elif col=="B":
                    self.blinky=Blinky(i_col, i_fila)
                elif col=="R":
                    self.pinky=Pinky(i_col, i_fila)
                elif col=="I":
                    self.inky=Inky(i_col, i_fila)                                  
                elif col=="C":
                    self.clyde=Clyde(i_col, i_fila)

    #Manejar los eventos del juego:
    def handle_events(self):
        for event in pygame.event.get():
            #Cerrar el juego:
            if event.type==pygame.QUIT:
                self.running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_SPACE:
                    if self.game_state==INTRO:
                        self.game_state=PLAYING
                    elif self.game_state in [GAME_OVER, VICTORY]:
                        self.create_level()
                        self.score=0
                        self.game_state=PLAYING
    
    #Actualizar el estado del juego:
    def update(self):
        if self.game_state in [GAME_OVER, VICTORY]:
            self.sound.stop()

        if self.game_state==PLAYING:
            self.player.update(self.walls)
            self.music.stop()
            self.dies.stop()
            self.dead=False

            #Manejar sonidos de movimiento:
            if self.player.is_moving and not self.player.was_moving:
                self.sound.play(-1)
            elif not self.player.is_moving and self.player.was_moving:
                self.sound.stop()

            for coin in self.coins[:]:
                if self.player.rect.colliderect(coin.rect):
                    self.coins.remove(coin)
                    self.score+=COIN_SCORE
                    if len(self.coins)==0:
                        self.game_state=VICTORY

        self.blinky.update(self.walls)
        self.pinky.update(self.walls)
        self.inky.update(self.walls)
        self.clyde.update(self.walls)

        if self.player.rect.colliderect(self.blinky.rect) or self.player.rect.colliderect(self.pinky.rect) or self.player.rect.colliderect(self.inky.rect) or self.player.rect.colliderect(self.clyde.rect):
            self.game_state=GAME_OVER
            if not self.dead:
                self.dies.play()
                self.dead=True

    def draw(self):
        #Llenar de negro el fondo:
        self.screen.fill(BLACK)

        #Dibujar la pantalla de intro:
        if self.game_state==INTRO:
            self.show_intro_screen()
        elif self.game_state==GAME_OVER:
            self.show_game_over_screen()
        elif self.game_state==VICTORY:
            self.show_victory_screen()
        elif self.game_state==PLAYING:
            #Dibujar las paredes:
            for wall in self.walls:
                wall.draw(self.screen)
            
            #Dibujar las monedas:
            for coin in self.coins:
                coin.draw(self.screen)

            #Dibujar el puntaje en pantalla:
            score_text=self.font.render(f'Puntaje: {self.score}', True, WHITE)
            self.screen.blit(score_text, (10, 10))

            #Dibujar al jugador:
            self.player.draw(self.screen)
            self.blinky.draw(self.screen)
            self.pinky.draw(self.screen)
            self.inky.draw(self.screen)
            self.clyde.draw(self.screen)

        #Acutializar la pantalla:
        pygame.display.flip()

    #Bucle principal del juego:
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
