import pygame
import sys
from game import Game
from arcade_machine_sdk import GameMeta

metadata=(GameMeta()
          .with_title("Pac-Man")
          .with_description("Esquiva a los fantasmas, come todas las esferas y domina el laberinto en esta recreación fiel del arcade original. ")
          .with_release_date("02/03/2026")
          .with_group_number(2)
          .add_tag("Género:Retro, Laberinto,")
          .add_author("Isabela Paraqueimo, Cesar Moya"))

def main():
    try:
        #Inicializar pygame:
        pygame.init()
        pygame.mixer.init()

        #Crear y ejecutar el juego:
        game=Game(metadata)
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        pygame.quit()
        sys.exit()
