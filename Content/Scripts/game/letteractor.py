import unreal as ue

#TextRenderActor
class LetterActor():
    def __init__(self, letter):
        super().__init__()
        self.letter = letter
        # Set display text
        self.text_render.set_text(letter)
        # Add collision component
        self.collision = ue.add_component(self, SphereComponent, 'Collision')
        self.collision.set_sphere_radius(50)
        # Bind collision event
        self.collision.on_component_begin_overlap.add(self.on_overlap)

    def on_overlap(self, me, other):
        # When collision occurs, check if it's the snake head
        if other.owner.get_class().get_name() == 'SnakeHead':
            # Notify game manager to verify this letter
            game_manager = ue.find_actor('GameManager')
            game_manager.check_letter(self.letter, self)
            # Destroy self
            self.destroy()