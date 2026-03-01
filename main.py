from game import Game
from arcade_machine_sdk import GameMeta
import pygame

if not pygame.get_init():
    pygame.init()

metadata = (GameMeta()
            .with_title("Pac Man")
            .with_description("Juego de prueba")
            .with_release_date("05/03/2026")
            .with_group_number(2)
            .add_tag("Laberinto")
            .add_author("Cesar Moya")
            .add_author("Isabela Paraqueimo"))

game = Game(metadata)

if __name__ == "__main__":
    game.run_independently()
