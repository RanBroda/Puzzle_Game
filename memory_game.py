import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Initialize the mixer module
pygame.mixer.init()

# Load the sound
match_sound = pygame.mixer.Sound("chimes.wav")

# Font initiation
pygame.font.init()  # Initialize font module
font = pygame.font.SysFont(None, 36)  # Create a font object
start_time = pygame.time.get_ticks()  # Capture the start time in milliseconds

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 940, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Memory Game")

# Colors
BG_COLOR = (30, 30, 30)
CARD_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (255, 20, 147), (0, 255, 255),
               (128, 0, 128)]
CARD_BACK_COLOR = (255, 255, 255)
CARD_BORDER_COLOR = (0, 0, 0)

# Timer
TIMEREVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMEREVENT, 1000)

# Cards setup
NUM_PAIRS = 8
CARD_SIZE = (80, 100)
CARDS_PER_ROW = 8
card_positions = [(x * (CARD_SIZE[0] + 10) + 50, y * (CARD_SIZE[1] + 10) + 40) for y in range(2) for x in
                  range(CARDS_PER_ROW)]
cards = []
for color in CARD_COLORS[:NUM_PAIRS]:
    cards.extend([color, color])
random.shuffle(cards)

# Game variables
flipped_cards = []
found_pairs = []


def draw_board():
    screen.fill(BG_COLOR)
    for index, position in enumerate(card_positions):
        card_color = CARD_BACK_COLOR if index not in flipped_cards else cards[index]
        if index in found_pairs:
            continue
        pygame.draw.rect(screen, card_color, (*position, *CARD_SIZE))
        pygame.draw.rect(screen, CARD_BORDER_COLOR, (*position, *CARD_SIZE), 3)

    current_time = pygame.time.get_ticks()  # Get current time in milliseconds
    elapsed_time = (current_time - start_time) // 1000  # Convert to seconds
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    timer_text = f"{minutes:02}:{seconds:02}"  # Format as MM:SS
    timer_surface = font.render(timer_text, True, (255, 255, 255))  # Render the text
    screen.blit(timer_surface, (SCREEN_WIDTH - 100, 10))  # Position the text on screen


def game_logic(mouse_pos):
    global flipped_cards, found_pairs
    for index, position in enumerate(card_positions):
        if position[0] <= mouse_pos[0] <= position[0] + CARD_SIZE[0] and position[1] <= mouse_pos[1] <= position[1] + CARD_SIZE[1]:
            if index in flipped_cards or index in found_pairs:
                return
            flipped_cards.append(index)
            if len(flipped_cards) == 2:
                # Draw the board to show both flipped cards
                draw_board()
                pygame.display.flip()  # Update the screen to show changes

                # Delay added here to allow the player to see the second card
                pygame.time.wait(1000)

                if cards[flipped_cards[0]] == cards[flipped_cards[1]]:
                    found_pairs.extend(flipped_cards)
                    match_sound.play()
                flipped_cards.clear()
                return  # Return immediately after handling the second card flip


def check_game_over():
    return len(found_pairs) == len(cards)


# Game loop
running = True

while running:
    # Game loop start
    # Inside game loop

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            game_logic(pygame.mouse.get_pos())
            if check_game_over():
                print("Game Over! Restarting...")
                start_time = pygame.time.get_ticks()
                flipped_cards.clear()
                found_pairs.clear()
                random.shuffle(cards)

    draw_board()
    pygame.display.flip()

pygame.quit()
sys.exit()
