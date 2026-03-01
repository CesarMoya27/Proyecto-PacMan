import pygame
from config import *
from sprites import *
from arcade_machine_sdk import GameBase

class Game(GameBase):
    def __init__(self, metadata):
        self.metadata=metadata
        
        #Nombre de la ventana:
        pygame.display.set_caption("Pac-Man")

        #Controlar la ejecución del juego:
        self.game_state=INTRO

        #Cargar los sonidos:
        self.sound=load_sound(SOUNDS_DIR)
        self.music=load_sound(SOUNDS_DIR, 1)
        self.dies=load_sound(SOUNDS_DIR, 2)
        self.dead=False
        self.music_is_playing=False

        #Ajustar el volumen:
        self.music.set_volume(MUSIC_VOL)
        self.sound.set_volume(SOUND_VOL)
        self.dies.set_volume(SOUND_VOL)

        #Crear al jugador:
        self.coins=[]
        self.walls=[]
        self.ghosts=[]
        self.score=0
        self.create_level()

        #Variables para el power-up:
        self.power_up_timer=0.0
        self.power_up_dur=10.0
        self.power_up_active=False

        #Fuente para el texto:
        self.font=pygame.font.Font(None, 36)
        self.font_big=pygame.font.Font(None, 73)
    
    def start(self, surface):
        super().start(surface)
        #self.music.play(-1)

    #Pantalla de inicio:
    def show_intro_screen(self, surface):
        title_text=load_image(str(TITLE_DIR))
        title_text=pygame.transform.scale(title_text, (BASE_WIDTH, BASE_HEIGHT))
        start_text=self.font.render('Presiona ESPACIO para Comenzar', True, WHITE)
        controls_text=self.font.render('Usa las FLECHAS para moverte', True, WHITE)

        title_rect=title_text.get_rect(center=(BASE_WIDTH/2, BASE_HEIGHT/2))
        start_rect=start_text.get_rect(center=(BASE_WIDTH/2, BASE_HEIGHT/4.5))
        controls_rect=controls_text.get_rect(center=(BASE_WIDTH/2, 2*BASE_HEIGHT/7))

        surface.fill(BLACK)
        surface.blit(title_text, title_rect)
        surface.blit(start_text, start_rect)
        surface.blit(controls_text, controls_rect)
    
    #Pantalla de game over:
    def show_game_over_screen(self, surface):
        game_over_text=load_image(str(LOSE_DIR))
        game_over_text=pygame.transform.scale(game_over_text, (BASE_WIDTH, BASE_HEIGHT))
        score_text=self.font_big.render(f'Puntaje: {self.score}', True, WHITE)
        restart_text=self.font.render('Presione ESPACIO para jugar de nuevo', True, WHITE)

        game_over_rect=game_over_text.get_rect(center=(BASE_WIDTH/2, BASE_HEIGHT/2))
        score_rect=score_text.get_rect(center=(BASE_WIDTH/2, BASE_HEIGHT/4.8))
        restart_rect=restart_text.get_rect(center=(BASE_WIDTH/2, 2*BASE_HEIGHT/7))   

        surface.fill(BLACK)
        surface.blit(game_over_text, game_over_rect)
        surface.blit(score_text, score_rect)
        surface.blit(restart_text, restart_rect)  

    #Pantalla de victoria:
    def show_victory_screen(self, surface):
        victory_text=load_image(str(WIN_DIR))
        victory_text=pygame.transform.scale(victory_text, (BASE_WIDTH, BASE_HEIGHT))
        score_text=self.font_big.render(f'Puntaje: {self.score}', True, WHITE)
        restart_text=self.font.render('Presione ESPACIO para jugar de nuevo', True, WHITE)

        victory_rect=victory_text.get_rect(center=(BASE_WIDTH/2, BASE_HEIGHT/2))
        score_rect=score_text.get_rect(center=(BASE_WIDTH/2, BASE_HEIGHT/4.6))
        restart_rect=restart_text.get_rect(center=(BASE_WIDTH/2, 2*BASE_HEIGHT/7))   

        surface.fill(BLACK)
        surface.blit(victory_text, victory_rect)
        surface.blit(score_text, score_rect)
        surface.blit(restart_text, restart_rect)  
          
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
                    self.blinky=Ghost(i_col, i_fila, 1)
                elif col=="R":
                    self.pinky=Ghost(i_col, i_fila, 2)
                elif col=="I":
                    self.inky=Ghost(i_col, i_fila, 3)                                  
                elif col=="C":
                    self.clyde=Ghost(i_col, i_fila, 4)
                elif col=="M":
                    self.coins.append(Coin(i_col, i_fila, True))

        self.ghosts.append(self.blinky)
        self.ghosts.append(self.pinky)
        self.ghosts.append(self.inky)
        self.ghosts.append(self.clyde)

    #Para activar el power-up:
    def activate_power_up(self):
        self.power_up_active=True
        self.power_up_timer=self.power_up_dur
        for ghost in self.ghosts:
            ghost.vulnerable_state(True)

    #Actualizar el estado del power_up:
    def update_power_up(self, dt):
        if self.power_up_active:
            self.power_up_timer-=dt
            if self.power_up_timer<=0:
                self.power_up_active=False
                for ghost in self.ghosts:
                    ghost.vulnerable_state(False)

    #Manejar los eventos del juego:
    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_SPACE:
                    if self.game_state==INTRO:
                        self.game_state=PLAYING
                    elif self.game_state in [GAME_OVER, VICTORY]:
                        self.create_level()
                        self.score=0
                        self.game_state=PLAYING
    
    #Actualizar el estado del juego:
    def update(self, dt: float):
        #Control para la música del menú:
        if self.game_state==INTRO:
            if not self.music_is_playing:
                self.music.play(-1)
                self.music_is_playing=True
        else:
            if self.music_is_playing:
                self.music.stop()
                self.music_is_playing=False

        if self.game_state in [GAME_OVER, VICTORY]:
            self.sound.stop()
            self.ghosts=[]
            self.coins=[]

        if self.game_state==PLAYING:
            self.player.update(self.walls, dt)
            for ghost in self.ghosts:
                ghost.update(self.walls, dt)
            self.dies.stop()
            self.dead=False
        
            #Actualizar el power-up:
            self.update_power_up(dt)

            #Manejar sonidos de movimiento:
            if self.player.is_moving and not self.player.was_moving:
                self.sound.play(-1)
            elif not self.player.is_moving and self.player.was_moving:
                self.sound.stop()

            for coin in self.coins[:]:
                if self.player.rect.colliderect(coin.rect):
                    if isinstance(coin, Coin) and coin.big:
                        self.activate_power_up()
                    self.coins.remove(coin)
                    self.score+=COIN_SCORE
                    if len(self.coins)==0:
                        self.game_state=VICTORY

        for ghost in self.ghosts:
            if self.player.rect.colliderect(ghost.rect):
                if ghost.vulnerable:
                    ghost.hide()
                    ghost.dead=True
                else:
                    if self.player.life:
                        self.player.life-=1
                        self.player.respawn()
                        for ghost in self.ghosts:
                            ghost.respawn()

        if self.player.life==0:
            self.game_state=GAME_OVER
            if not self.dead:
                self.dies.play()
                self.dead=True       

    def render(self):
        #Llenar de negro el fondo:
        self.surface.fill(BLACK)

        #Dibujar las pantallas:
        if self.game_state==INTRO:
            self.show_intro_screen(self.surface)
        elif self.game_state==GAME_OVER:
            self.show_game_over_screen(self.surface)
        elif self.game_state==VICTORY:
            self.show_victory_screen(self.surface)
        elif self.game_state==PLAYING:
            #Dibujar las paredes:
            for wall in self.walls:
                wall.draw(self.surface)
            
            #Dibujar las monedas:
            for coin in self.coins:
                coin.draw(self.surface)

            #Dibujar el puntaje en pantalla:
            score_text=self.font.render(f'Puntaje: {self.score}', True, WHITE)
            self.surface.blit(score_text, (10, 10))

            #Dibujar la vida en pantalla:
            self.player.draw_lifes(self.surface)

            #Dibujar el tiempo restante del power-up:
            if self.power_up_active:
                remaining_time=max(0, int(self.power_up_timer))
                power_up_text=self.font.render(f'Power-up:{remaining_time}s', True, YELLOW)
                self.surface.blit(power_up_text, (BASE_WIDTH-150, 10))

            #Dibujar los personajes:
            self.player.draw(self.surface)
            for ghost in self.ghosts:
                ghost.draw(self.surface)
                
    def run_independently(self):
        return super().run_independently()
