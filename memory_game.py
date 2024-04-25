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

# Initialize time attack variables
time_attack_mode = False
time_left = 60  # Start with 60 seconds


# Define the reset button dimensions and position
reset_button_color = (70, 130, 180)  # SteelBlue color
reset_button_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, 140, 40)  # Position and size
reset_button_text = "Reset Game"

# Play Again button setup
play_again_button_color = (34, 139, 34)  # Forest Green color
play_again_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2, 140, 40)  # Position and size
play_again_button_text = "Play Again"

# Game mode and turn tracking
num_players = 1  # Default to 1 player
current_player = 1  # Start with player 1

# Define buttons for choosing game mode
mode_buttons = {
    '1 Player': pygame.Rect(50, SCREEN_HEIGHT // 2, 140, 40),
    '2 Players': pygame.Rect(250, SCREEN_HEIGHT // 2, 140, 40),
    'Time Attack': pygame.Rect(450, SCREEN_HEIGHT // 2, 140, 40)
}

# Cards setup
NUM_PAIRS = 8
CARD_SIZE = (80, 100)
CARDS_PER_ROW = 8
card_positions = [(x * (CARD_SIZE[0] + 10) + 50, y * (CARD_SIZE[1] + 10) + 40) for y in range(2) for x in
                  range(CARDS_PER_ROW)]
cards = []
for color in CARD_COLORS[:NUM_PAIRS]:
    cards.append({'color': color, 'flipped': False, 'animating': False, 'width': CARD_SIZE[0], 'front': True})
    cards.append({'color': color, 'flipped': False, 'animating': False, 'width': CARD_SIZE[0], 'front': True})
random.shuffle(cards)

# Game variables
flipped_cards = []
found_pairs = []
consecutive_matches = 0


def draw_mode_selection():
    for text, rect in mode_buttons.items():
        pygame.draw.rect(screen, (0, 0, 255), rect)  # Blue button
        text_surface = font.render(text, True, (255, 255, 255))  # White text
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)


total_time = 60


def draw_board():
    screen.fill(BG_COLOR)
    for index, position in enumerate(card_positions):
        card = cards[index]
        if card['flipped'] or not card['front']:
            color_card = card['color']
        else:
            color_card = CARD_BACK_COLOR

        pos_x = position[0] + (CARD_SIZE[0] - card['width']) // 2
        pygame.draw.rect(screen, color_card, (pos_x, position[1], card['width'], CARD_SIZE[1]))

        if card['animating']:
            animate_card(index)

    if not time_attack_mode:
        # Draw timer on the screen
        current_time = pygame.time.get_ticks()  # Get current time in milliseconds
        elapsed_time = (current_time - start_time) // 1000  # Convert to seconds
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        timer_text = f"{minutes:02}:{seconds:02}"  # Format as MM:SS
        timer_surface = font.render(timer_text, True, (255, 255, 255))  # Render the text
        screen.blit(timer_surface, (SCREEN_WIDTH - 100, 10))  # Position the text on screen

    if time_attack_mode:
        global time_left
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000  # Time elapsed in seconds
        time_left = max(0, total_time - elapsed_time)
        minutes = time_left // 60
        seconds = time_left % 60
        timer_text = f"{minutes:02}:{seconds:02}"  # Format as MM:SS
        # Render and display the countdown timer
        timer_surface = font.render(timer_text, True, (255, 255, 255))
        screen.blit(timer_surface, (SCREEN_WIDTH - 100, 10))  # Position the text on screen

    # Draw reset button the screen
    pygame.draw.rect(screen, reset_button_color, reset_button_rect)
    text_surface = font.render(reset_button_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=reset_button_rect.center)
    screen.blit(text_surface, text_rect)


def handle_game_over():
    global game_over
    game_over = True
    print("Time's up! Game Over!")  # This is just a placeholder. Update it according to your game's design.


def animate_card(index):
    card = cards[index]
    if card['animating']:
        if not card['flipped']:
            if card['width'] > 0 and card['front']:
                card['width'] -= 2.5  # Speed of animation
            elif card['width'] <= 0:
                card['front'] = not card['front']
                card['width'] += 2.5
            else:
                card['width'] += 2.5
                if card['width'] == CARD_SIZE[0]:
                    card['animating'] = False
                    card['flipped'] = True
        else:
            if card['width'] > 0 and not card['front']:
                card['width'] -= 2.5  # Speed of animation
            elif card['width'] <= 0:
                card['front'] = not card['front']
                card['width'] += 2.5
            else:
                card['width'] += 2.5
                if card['width'] == CARD_SIZE[0]:
                    card['animating'] = False
                    card['flipped'] = False


def game_logic(mouse_pos):
    global flipped_cards, found_pairs, consecutive_matches, current_player
    for index, position in enumerate(card_positions):
        card = cards[index]
        rect = pygame.Rect(*position, card['width'], CARD_SIZE[1])
        if rect.collidepoint(mouse_pos) and not card['flipped'] and not card['animating']:
            card['animating'] = True
            flipped_cards.append(index)
            while not card['flipped']:
                draw_board()
            if len(flipped_cards) == 2 and cards[flipped_cards[0]]['flipped'] and cards[flipped_cards[1]]['flipped']:
                # Draw the board to show both flipped cards
                draw_board()
                pygame.display.flip()  # Update the screen to show changes

                # Delay added here to allow the player to see the second card
                pygame.time.wait(500)

                if cards[flipped_cards[0]]['color'] == cards[flipped_cards[1]]['color']:
                    found_pairs.extend(flipped_cards)
                    consecutive_matches += 1
                    if consecutive_matches == 2:
                        display_fire_message()
                        consecutive_matches = 0
                    match_sound.play()
                else:  # No streak
                    cards[flipped_cards[0]]['animating'] = True
                    cards[flipped_cards[1]]['animating'] = True
                    pygame.time.wait(250)
                    draw_board()
                    pygame.display.flip()
                    consecutive_matches = 0
                    if num_players == 2:
                        current_player = 2 if current_player == 1 else 1
                flipped_cards.clear()
                return  # Return immediately after handling the second card flip


def display_fire_message():
    fire_message = "You are on fire!"
    fire_surface = font.render(fire_message, True, (255, 69, 0))  # Using Red-Orange color
    fire_rect = fire_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5))
    screen.blit(fire_surface, fire_rect)
    pygame.display.flip()
    pygame.time.wait(500)  # Show the message for 1.5 seconds


def check_game_over():
    if len(found_pairs) == len(cards):
        if time_attack_mode:
            global total_time
            total_time = max(10, total_time - 5)  # Reduce time by 5 seconds, minimum of 10 seconds
            reset_game()
        else:
            draw_end_game()
        return True
    elif time_left <= 0:
        draw_end_game_lost()
        return True
    return False


def reset_game():
    global start_time, flipped_cards, found_pairs, current_player, time_left
    start_time = pygame.time.get_ticks()
    flipped_cards.clear()
    found_pairs.clear()
    cards.clear()
    for color in CARD_COLORS[:NUM_PAIRS]:
        cards.append({'color': color, 'flipped': False, 'animating': False, 'width': CARD_SIZE[0], 'front': True})
        cards.append({'color': color, 'flipped': False, 'animating': False, 'width': CARD_SIZE[0], 'front': True})
    random.shuffle(cards)
    draw_board()
    current_player = 1
    if not time_attack_mode:
        time_left = 60  # Reset to default 60 seconds for time attack mode


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


def draw_end_game_lost():
    # Draw "Well done!" message
    message_text = "You Lost!!!"
    message_surface = font.render(message_text, True, (255, 0, 0))  # Red color
    message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
    screen.blit(message_surface, message_rect)

    # Draw "Play Again" button
    pygame.draw.rect(screen, play_again_button_color, play_again_button_rect)
    text_surface = font.render(play_again_button_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=play_again_button_rect.center)
    screen.blit(text_surface, text_rect)


def draw_turn_indicator():
    player_text = f"Player {current_player}'s Turn"
    text_surface = font.render(player_text, True, (255, 215, 0))  # Gold color
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 20))
    screen.blit(text_surface, text_rect)


mode_selected = False
while not mode_selected:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            start_time = pygame.time.get_ticks()  # Capture the start time in milliseconds
            mouse_pos = pygame.mouse.get_pos()
            for text, rect in mode_buttons.items():
                if rect.collidepoint(mouse_pos):
                    if text == '1 Player': num_players = 1
                    elif text == '2 Players': num_players = 2
                    elif text == 'Time Attack':
                        num_players = 1
                        time_attack_mode = True
                    mode_selected = True
                    break

    screen.fill(BG_COLOR)
    draw_mode_selection()
    pygame.display.flip()

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
                    # Reset game logic for playing again
                    reset_game()
                    game_over = False  # Reset game over status
            elif reset_button_rect.collidepoint(mouse_pos):
                # Reset game logic
                reset_game()
            else:
                game_logic(mouse_pos)

    if not game_over:
        draw_board()
        if num_players == 2:
            draw_turn_indicator()
    pygame.display.flip()
    game_over = check_game_over()  # Update game_over status after drawing

pygame.quit()
sys.exit()
