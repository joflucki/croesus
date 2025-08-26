from typing import Any, Dict, List
from numpy import ndarray
import pygame
import pymunk
import imageio

# Settings
WIDTH, HEIGHT = 1088, 1920
FPS = 144
DURATION_SECONDS = 10
VIDEO_NAME = "output.mp4"


def main():
    # Setup pygame
    pygame.init()
    screen = pygame.Surface((WIDTH, HEIGHT))  # offscreen surface (no window)
    clock = pygame.time.Clock()

    # Setup pymunk space
    space = pymunk.Space()
    space.gravity = (0, 981)  # gravity downward

    # Create floor multiple floors
    floors: List[pymunk.Segment] = []

    for i in range(3):
        floor = pymunk.Segment(
            space.static_body,
            (0, HEIGHT - (i + 1) * 50),
            (WIDTH, HEIGHT - (i + 1) * 50),
            5,
        )
        floor.elasticity = 1
        space.add(floor)
        floors.append(floor)

    # Create ball
    radius = 25
    mass = 1
    moment = pymunk.moment_for_circle(mass, 0, radius)
    ball_body = pymunk.Body(mass, moment)
    ball_body.position = (WIDTH // 2, 100)
    ball_shape = pymunk.Circle(ball_body, radius)
    ball_shape.elasticity = 0.8
    space.add(ball_body, ball_shape)

    # Create collision handler
    def on_shape_collide(
        arbiter: pymunk.Arbiter, space: pymunk.Space, data: Dict[str, Any]
    ):
        shape_a, shape_b = arbiter.shapes
        if isinstance(shape_a, pymunk.Segment) and shape_a in floors:
            floors.remove(shape_a)
            space.remove(shape_a)

        if isinstance(shape_b, pymunk.Segment) and shape_b in floors:
            floors.remove(shape_b)
            space.remove(shape_b)

    space.on_collision(
        separate=on_shape_collide,
    )

    # Prepare video frame storage
    frames: List[ndarray] = []

    # Simulation loop
    total_frames = FPS * DURATION_SECONDS
    for _ in range(total_frames):
        # Step simulation
        space.step(1 / FPS)

        # Clear screen
        screen.fill((0, 0, 0))

        # Draw floor
        for floor in floors:
            pygame.draw.line(screen, (255, 255, 255), floor.a, floor.b, 5)

        # Draw ball
        pos = int(ball_body.position[0]), int(ball_body.position[1])
        pygame.draw.circle(screen, (255, 0, 0), pos, radius)

        # Convert pygame surface to numpy array
        frame_image = pygame.surfarray.array3d(screen)
        frame_image = frame_image.swapaxes(0, 1)  # Pygame has different axis order

        frames.append(frame_image)

        clock.tick(FPS)

    # Save to video using imageio
    print("Exporting video...")
    imageio.mimsave(uri=VIDEO_NAME, ims=frames, fps=FPS)  # type: ignore
    print(f"Video saved as {VIDEO_NAME}")


if __name__ == "__main__":
    main()
