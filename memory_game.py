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

# Define the button dimensions and position
reset_button_color = (70, 130, 180)  # SteelBlue color
reset_button_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, 140, 40)  # Position and size
reset_button_text = "Reset Game"

# Play Again button setup
play_again_button_color = (34, 139, 34)  # Forest Green color
play_again_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2, 140, 40)  # Position and size
play_again_button_text = "Play Again"

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

    # Draw timer on the screen
    current_time = pygame.time.get_ticks()  # Get current time in milliseconds
    elapsed_time = (current_time - start_time) // 1000  # Convert to seconds
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    timer_text = f"{minutes:02}:{seconds:02}"  # Format as MM:SS
    timer_surface = font.render(timer_text, True, (255, 255, 255))  # Render the text
    screen.blit(timer_surface, (SCREEN_WIDTH - 100, 10))  # Position the text on screen

    # Draw reset button the screen
    pygame.draw.rect(screen, reset_button_color, reset_button_rect)
    text_surface = font.render(reset_button_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=reset_button_rect.center)
    screen.blit(text_surface, text_rect)


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
    if len(found_pairs) == len(cards):
        draw_end_game()
        return True
    return False


def draw_end_game():
    # Draw "Well done!" message
    message_text = "Well done!"
    message_surface = font.render(message_text, True, (255, 215, 0))  # Gold color
    message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
    screen.blit(message_surface, message_rect)

    # Draw "Play Again" button
    pygame.draw.rect(screen, play_again_button_color, play_again_button_rect)
    text_surface = font.render(play_again_button_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=play_again_button_rect.center)
    screen.blit(text_surface, text_rect)

# Game loop
running = True
game_over = False
while running:
    # Game loop start
    # Inside game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if check_game_over():
                if play_again_button_rect.collidepoint(mouse_pos):
                #Reset game logic for playing again
                    start_time = pygame.time.get_ticks()
                    flipped_cards.clear()
                    found_pairs.clear()
                    random.shuffle(cards)
                    game_over = False  # Reset game over status
            elif reset_button_rect.collidepoint(mouse_pos):
                # Reset game logic
                start_time = pygame.time.get_ticks()  # Reset start time for new game
                flipped_cards.clear()
                found_pairs.clear()
                random.shuffle(cards)
            else:
                game_logic(mouse_pos)

    if not game_over:
        draw_board()
    pygame.display.flip()
    game_over = check_game_over() # Update game_over status after drawing

pygame.quit()
sys.exit()
