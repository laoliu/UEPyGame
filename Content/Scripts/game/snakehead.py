import unreal_engine as ue
from unreal_engine.classes import Actor, SphereComponent, TextRenderActor

class SnakeHead(Actor):
    def __init__(self):
        super().__init__()
        # Create root component (collision body)
        self.collision = self.root_component
        if not self.root_component:
            self.collision = ue.add_component(self, SphereComponent, 'Collision')
            self.root_component = self.collision
        # Set collision size
        self.collision.set_sphere_radius(50)
        # Movement speed
        self.speed = 10.0
        # Current movement direction (3D vector)
        self.direction = [1,0,0]  # Initial direction is positive X-axis
        # List of snake body parts
        self.body = []

        self.input_forward = 0
        self.input_right = 0
        self.input_up = 0

    def move(self):
        # Move according to current direction
        current_location = self.get_actor_location()
        new_location = (
            current_location.x + self.direction[0] * self.speed,
            current_location.y + self.direction[1] * self.speed,
            current_location.z + self.direction[2] * self.speed
        )
        self.set_actor_location(new_location)

    def add_body_part(self):
        # Create a new snake body part
        body_part = ue.get_editor_world().actor_spawn(ue.load_class('/Game/SnakeBodyPart.SnakeBodyPart'))
        # Set position to the current position of the snake head (or the last body part)
        # And add to the body list
        self.body.append(body_part)

    def set_direction(self, new_direction):
        # Prevent 180-degree turns (direct reversal)
        # Check if new direction is opposite to current direction - if yes, ignore
        # Otherwise set new direction
        # Note: We allow changing multiple directions simultaneously since direction is a 3D vector
        # Example: Current direction [1,0,0] (right) cannot change to [-1,0,0] (left) as it would cause immediate collision
        # But we can allow perpendicular direction changes, hence the check
        # Simplified logic: Only check if directions are opposite (negative dot product)
        if self.direction[0]*new_direction[0] + self.direction[1]*new_direction[1] + self.direction[2]*new_direction[2] < 0:
            return
        self.direction = new_direction

    # Bind inputs during game initialization
    def setup_input():
        ue.bind_axis('MoveForward', move_forward)
        ue.bind_axis('MoveRight', move_right)
        ue.bind_axis('MoveUp', move_up)

    def move_forward(amount):
        if amount != 0:
            snake = ue.find_actor('SnakeHead')
            snake.input_forward = amount
        # Should we use camera-relative directions or fixed world coordinates? Simplified to use world coordinates
        # Convention: Forward/backward = Y-axis, Left/right = X-axis, Up/down = Z-axis
        # Forward = positive Y, Backward = negative Y, Right = positive X, Left = negative X, Up = positive Z, Down = negative Z
        # Note: Snake movement uses a direction vector - we change direction per axis but movement follows single direction
        # Implementation options:
        # 1. Set direction vector to corresponding axis when key pressed (but can't handle multiple directions)
        # 2. Use three variables to track axis directions and combine into final vector (allows diagonal movement)
        # Current approach: Add three variables (forward, right, up) to SnakeHead
        # Then calculate final direction vector in tick() before movement

    def move_up(amount):
        snake = ue.find_actor('SnakeHead')
        snake.input_up = amount