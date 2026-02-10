import pygame
import sys
from game import Game

def main():
    try:
        #Inicializar pygame:
        pygame.init()
        pygame.mixer.init()

        #Crear y ejecutar el juego:
        game=Game()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        pygame.quit()
        sys.exit()
    
if __name__=="__main__":
    main()
