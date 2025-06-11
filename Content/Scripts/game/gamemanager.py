import random
from unreal_engine.classes import Actor
import unreal as ue
from letteractor import LetterActor

class GameManager(Actor):
    def __init__(self):
        #super().__init__()
        self.target_word = "ORANGE"
        self.current_index = 0  # Index of the next letter to collect in the target word
        self.letters = []       # Stores spawned letter Actors
        self.time_left = 120    # 120-second time limit
        self.game_over = False
        self.generate_letters()

    def generate_letters(self):
        # Spawn each letter of the target word at random positions in the scene
        for letter in self.target_word:
            letter_actor = ue.get_editor_world().actor_spawn(LetterActor, letter)
            # Set random position within specified bounds
            letter_actor.set_actor_location( (random.uniform(-500,500), random.uniform(-500,500), random.uniform(0,200)) )
            self.letters.append(letter_actor)

    def check_letter(self, letter, letter_actor):
        # Verify if collected letter matches current target letter
        if letter == self.target_word[self.current_index]:
            # Correct letter - grow snake body
            snake_head = ue.find_actor('SnakeHead')
            snake_head.add_body_part()
            self.current_index += 1
            # Check if all letters are collected
            if self.current_index >= len(self.target_word):
                self.game_over = True
                ue.log("Congratulations! You win!")
        else:
            # Wrong letter - penalize time
            self.time_left -= 10
            if self.time_left <= 0:
                self.game_over = True
                ue.log("Game Over! Time out!")

    def tick(self, delta_time):
        if self.game_over:
            return
        # Update timer every frame
        self.time_left -= delta_time
        if self.time_left <= 0:
            self.game_over = True
            ue.log("Game Over! Time out!")
