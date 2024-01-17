import pygame
import sys
import random

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


class Block:
    def __init__(self, color, width, height, x, y):
        self.color = color
        self.width = width
        self.height = height
        self.x = x
        self.y = y


# Create a variable to keep track of the number of collisions
collision_count = 0


def respawn_blocks(num_blocks, block_size, spacing, color):
    global random_blocks
    global robot

    print(f"Before respawn: {len(random_blocks)} blocks")

    # Check if the robot has collected a multiple of 4 blocks
    if robot.blocks_removed % 4 == 0 and robot.blocks_removed > 0:
        print(f"Creating square with {robot.blocks_removed} blocks!")
        robot.blocks_removed = 0  # Reset the block count

        for _ in range(num_blocks):
            while True:
                new_x = robot.x + (len(random_blocks) % 2) * (
                            block_size + spacing) + block_size * 2  # Adjusted starting position
                new_y = robot.y + (len(random_blocks) // 2) * (block_size + spacing)
                new_block = Block(color, block_size, block_size, new_x, new_y)

                # Check for collisions with existing blocks
                collision = any(
                    pygame.Rect(new_block.x, new_block.y, new_block.width, new_block.height).colliderect(
                        existing_block.x, existing_block.y, existing_block.width, existing_block.height
                    ) for existing_block in random_blocks
                )

                if not collision:
                    random_blocks.append(new_block)
                    break

        # Introduce a small delay to avoid busy waiting
        pygame.time.delay(10)

    print(f"After respawn: {len(random_blocks)} blocks")


def generate_random_blocks(num_blocks, grid_spacing, color):
    random_blocks = []
    for _ in range(num_blocks):
        while True:
            random_x = random.randint(0, width - grid_spacing)
            random_y = random.randint(0, height - grid_spacing)
            new_block = Block(color, 20, 20, random_x, random_y)

            # Check for collisions with existing blocks
            collision = False
            for existing_block in random_blocks:
                if pygame.Rect(new_block.x, new_block.y, new_block.width, new_block.height).colliderect(
                        existing_block.x, existing_block.y, existing_block.width, existing_block.height
                ):
                    collision = True
                    break

            if not collision:
                random_blocks.append(new_block)
                break

    return random_blocks


def clear_respawned_blocks():
    global random_blocks, collision_count
    respawned_blocks = random_blocks[-collision_count:]  # Get the last N blocks (respawned blocks)
    for block in respawned_blocks:
        if block.color == (0, 255, 0):  # Check if the block is green (respawned)
            random_blocks.remove(block)
    collision_count = 0  # Reset collision count


class Robot:
    def __init__(self, color, width, height, x, y, speed):
        self.color = color
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.speed = speed  # Adjust the speed value to increase or decrease the speed
        self.direction = "right"
        self.is_running = False
        self.blocks_removed = 0

    def move(self):
        if self.is_running:
            if self.direction == "right":
                self.x += self.speed
                if self.x >= width - self.width:
                    self.x = 0
                    self.y += 10  # Reduce space between new lines
                    if self.y >= height - self.height:
                        self.y = 0  # Reset to the initial position
                    self.direction = "left"
            elif self.direction == "left":
                self.x -= self.speed
                if self.x <= 0:
                    self.x = 0
                    self.y += 10  # Reduce space between new lines
                    if self.y >= height - self.height:
                        self.y = 0  # Reset to the initial position
                    self.direction = "right"


# Initialize Pygame
pygame.init()

# Set up display
width, height = 600, 400
screen = pygame.display.set_mode((width, height + 50))  # Increased height for the control area
pygame.display.set_caption("Block World Simulation")

# Set up robot
robot = Robot(BLUE, 20, 20, 0, 0, 15)  # Adjust speed value to increase or decrease the speed

# Generate random blocks
num_random_blocks = 10
random_blocks = generate_random_blocks(num_random_blocks, 30, RED)

# Set up fonts
font = pygame.font.Font(None, 36)

# Set up buttons
button_start = pygame.Rect(10, height + 10, 100, 30)
button_stop = pygame.Rect(120, height + 10, 100, 30)
button_reset = pygame.Rect(230, height + 10, 100, 30)
button_create_square = pygame.Rect(340, height + 10, 200, 30)

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Check if the mouse click is on any button
                if button_start.collidepoint(event.pos):
                    print("Start button clicked")
                    robot.is_running = True
                    clear_respawned_blocks()  # Clear the respawned (green) blocks
                elif button_stop.collidepoint(event.pos):
                    print("Stop button clicked")
                    robot.is_running = False
                elif button_reset.collidepoint(event.pos):
                    print("Reset button clicked")
                    robot.x = 0
                    robot.y = 0
                    robot.direction = "right"
                    robot.blocks_removed = 0
                    collision_count = 0  # Reset collision count
                elif button_create_square.collidepoint(event.pos):
                    # Check if the robot has collided with blocks
                    if robot.blocks_removed % 4 == 0 and robot.blocks_removed > 0:
                        print(f"Creating square with {robot.blocks_removed} blocks!")
                        respawn_blocks(4, 20, 5, (0, 255, 0))  # Green color, block size = 20
                    else:
                        print("Cannot create square. Collect 4 blocks first.")

    # Move the robot
    robot.move()

    # Check for collisions between robot and random blocks
    for random_block in random_blocks:
        if pygame.Rect(robot.x, robot.y, robot.width, robot.height).colliderect(
                random_block.x, random_block.y, random_block.width, random_block.height
        ):
            print("Robot found a block")
            random_blocks.remove(random_block)
            robot.blocks_removed += 1
            collision_count += 1

            if robot.blocks_removed % 4 == 0 and robot.blocks_removed > 0:
                print("Robot found another 4 blocks. Stopping.")
                robot.is_running = False

    # Draw background with grid
    screen.fill(WHITE)
    grid_color = (200, 200, 200)
    for x in range(0, width, 30):
        pygame.draw.line(screen, grid_color, (x, 0), (x, height))
    for y in range(0, height, 30):
        pygame.draw.line(screen, grid_color, (0, y), (width, y))

    # Draw random blocks
    for random_block in random_blocks:
        pygame.draw.rect(screen, random_block.color,
                         (random_block.x, random_block.y, random_block.width, random_block.height))

    # Draw robot
    pygame.draw.rect(screen, robot.color, (robot.x, robot.y, robot.width, robot.height))

    # Draw control area
    pygame.draw.rect(screen, (150, 150, 150), (0, height, width, 50))

    # Draw buttons
    pygame.draw.rect(screen, (0, 255, 0), button_start)
    pygame.draw.rect(screen, (255, 0, 0), button_stop)
    pygame.draw.rect(screen, (0, 0, 255), button_reset)
    pygame.draw.rect(screen, (0, 255, 255), button_create_square)

    # Add text to buttons
    text_start = font.render("Start", True, WHITE)
    text_stop = font.render("Stop", True, WHITE)
    text_reset = font.render("Reset", True, WHITE)
    text_create_square = font.render("Create Square", True, WHITE)

    screen.blit(text_start, (30, height + 15))
    screen.blit(text_stop, (140, height + 15))
    screen.blit(text_reset, (250, height + 15))
    screen.blit(text_create_square, (360, height + 15))

    # Update display
    pygame.display.flip()

    # Set the frame rate
    clock.tick(30)
