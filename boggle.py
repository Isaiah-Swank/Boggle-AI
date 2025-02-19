# Import the necessary Python libraries and modules for game development, randomization,
# string operations, system operations, and file path operations.
import pygame
import random
import string
import sys
import os

# -----------------------
# CONSTANTS AND SETTINGS
# -----------------------

# Board constants (for a 4x4 board).
# BOARD_SIZE determines the number of rows and columns (4).
# TILE_SIZE is the dimension of each tile in pixels (width and height).
# MARGIN is the margin used inside each tile for placing the letter image.
# TILE_GAP is the space between each tile.
BOARD_SIZE = 4         
TILE_SIZE = 100        
MARGIN = 5             
TILE_GAP = 10          

# Window (game screen) dimensions.
# WINDOW_WIDTH and WINDOW_HEIGHT set the size of the game screen.
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

# Color definitions in RGB format.
# BLUE, BORDER_COLOR, HIGHLIGHT_COLOR, GRAY, and BABY_BLUE are used for drawing.
BLUE = (0, 0, 200)
BORDER_COLOR = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow for selected tiles
GRAY = (100, 100, 100)           # Darker gray for the board border
BABY_BLUE = (137, 207, 240)

# Frames per second setting for the game loop.
FPS = 30  

# Button constants.
# BUTTON_WIDTH and BUTTON_HEIGHT define the dimensions.
# BUTTON_COLOR and BUTTON_TEXT_COLOR define the button's background and text colors.
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_COLOR = BLUE
BUTTON_TEXT_COLOR = (255, 255, 255)

def create_board(size=4):
    """
    Create a board (list of lists) filled with random uppercase letters 
    (size x size).
    """
    board = []
    for _ in range(size):
        row = [random.choice(string.ascii_uppercase) for _ in range(size)]
        board.append(row)
    return board

def load_letter_images(filename, letter_size):
    """
    Load the letters from a sprite sheet (filename) that contains A-Z in a single row.
    Returns a dictionary mapping each letter 'A'-'Z' to its corresponding pygame.Surface
    scaled to letter_size.
    """
    # Load the full sprite sheet (which has all letters).
    letters_img = pygame.image.load(filename).convert_alpha()

    # Determine the width and height of the entire sprite sheet.
    total_width = letters_img.get_width()
    total_height = letters_img.get_height()

    # Each letter is assumed to have the same width. 
    # Since there are 26 letters, we divide total width by 26.
    letter_width = total_width // 26

    letter_images = {}
    for i, letter in enumerate(string.ascii_uppercase):
        # Define the rectangle area for a single letter.
        rect = pygame.Rect(i * letter_width, 0, letter_width, total_height)

        # Extract that portion of the sprite sheet.
        letter_surface = letters_img.subsurface(rect)

        # Scale the letter to the specified size.
        letter_surface = pygame.transform.scale(letter_surface, letter_size)

        # Store in the dictionary with the letter as the key.
        letter_images[letter] = letter_surface

    return letter_images

def load_dictionary(filename):
    """
    Load a dictionary file (one word per line) into a set.
    If the file doesn't exist, prints an error message and returns an empty set.
    """
    dictionary = set()
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                word = line.strip().upper()
                if word:
                    dictionary.add(word)
    else:
        print(f"Dictionary file '{filename}' not found.")
    return dictionary

def draw_button(screen, rect, text, font):
    """
    Draw a rectangular button on the screen at the given rect, 
    using the given text and font.
    """
    # Draw the button background.
    pygame.draw.rect(screen, BUTTON_COLOR, rect)
    # Draw a black border around the button.
    pygame.draw.rect(screen, (0, 0, 0), rect, 2)
    # Render the text surface.
    text_surf = font.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    # Blit (copy) the text onto the button.
    screen.blit(text_surf, text_rect)

def is_adjacent(pos1, pos2):
    """
    Check if pos2 is adjacent to pos1 on the board.
    Adjacency means the difference in row and column is at most 1,
    excluding the case where they are the same tile.
    """
    r1, c1 = pos1
    r2, c2 = pos2
    return abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1 and not (r1 == r2 and c1 == c2)

def compute_points(word):
    """
    Compute the point value of a valid word based on its length:
      - 3 or 4 letters: 1 point
      - 5 letters: 2 points
      - 6 letters: 3 points
      - More than 6 letters: 5 points
      - Otherwise (less than 3 letters): 0 points
    """
    length = len(word)
    if length in (3, 4):
        return 1
    elif length == 5:
        return 2
    elif length == 6:
        return 3
    elif length > 6:
        return 5
    else:
        return 0

def main():
    # Initialize all imported pygame modules.
    pygame.init()

    # Create a game screen (window) with the specified width and height.
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    # Set the caption of the game window.
    pygame.display.set_caption("Boggle Game - Enhanced Board")

    # Create a clock object to help control the frame rate.
    clock = pygame.time.Clock()

    # Load a dictionary from a text file.
    dictionary = load_dictionary("dictionary.txt")

    # Create a 4x4 board filled with random letters.
    board = create_board(BOARD_SIZE)

    # Define the size for the letter images (slightly smaller than the tile,
    # allowing for margins).
    letter_size = (TILE_SIZE - 2 * MARGIN, TILE_SIZE - 2 * MARGIN)

    # Load the letter images from a sprite sheet "letters.png".
    letter_images = load_letter_images("letters.png", letter_size)

    # Calculate the total pixel dimensions of the board including the gaps.
    board_pixel_width = BOARD_SIZE * TILE_SIZE + (BOARD_SIZE - 1) * TILE_GAP
    board_pixel_height = BOARD_SIZE * TILE_SIZE + (BOARD_SIZE - 1) * TILE_GAP

    # Center the board on the screen by calculating offset values.
    board_offset_x = (WINDOW_WIDTH - board_pixel_width) // 2
    board_offset_y = (WINDOW_HEIGHT - board_pixel_height) // 2

    # Define a rectangle that represents the board area, extended slightly
    # for a border around it.
    border_padding = 5
    board_rect = pygame.Rect(
        board_offset_x - border_padding,
        board_offset_y - border_padding,
        board_pixel_width + 2 * border_padding,
        board_pixel_height + 2 * border_padding
    )

    # Set up fonts of different sizes for displaying text in the game.
    font = pygame.font.SysFont(None, 36)       # Main font for text
    result_font = pygame.font.SysFont(None, 28)# Font for result messages
    small_font = pygame.font.SysFont(None, 24) # Font for listing found words

    # Define a rectangle for the "Check Word" button near the bottom of the screen.
    button_rect = pygame.Rect(
        (WINDOW_WIDTH - BUTTON_WIDTH) // 2,
        WINDOW_HEIGHT - BUTTON_HEIGHT - 30,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    # Variables to keep track of the current word, result messages, 
    # selected positions of tiles, words found, and the score.
    current_word = ""
    result_message = ""
    selected_positions = []  # List of (row, col) indicating which tiles are selected
    words_found_count = 0    # How many valid words have been found
    words_found_list = []    # A list of valid words found
    score = 0                # Running total of points

    # Main game loop control variable.
    running = True
    while running:
        # Process events (keyboard, mouse, etc.).
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # If the user closes the window, exit the loop.
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Capture left mouse click position.
                mouse_pos = pygame.mouse.get_pos()

                # Check if the click is on any tile within the board.
                for row_index, row in enumerate(board):
                    for col_index, letter in enumerate(row):
                        x_pos = board_offset_x + col_index * (TILE_SIZE + TILE_GAP)
                        y_pos = board_offset_y + row_index * (TILE_SIZE + TILE_GAP)
                        tile_rect = pygame.Rect(x_pos, y_pos, TILE_SIZE, TILE_SIZE)

                        # If the tile is clicked...
                        if tile_rect.collidepoint(mouse_pos):
                            # Ensure we don't select the same tile again and 
                            # that it is adjacent to the previously selected tile (if any).
                            if (row_index, col_index) not in selected_positions:
                                if not selected_positions or is_adjacent(selected_positions[-1], (row_index, col_index)):
                                    # Add the letter to the current word and track its position.
                                    current_word += letter
                                    selected_positions.append((row_index, col_index))
                                    result_message = ""
                            break  # Stop checking further tiles once one is clicked

                # Check if the click is on the "Check Word" button.
                if button_rect.collidepoint(mouse_pos):
                    # If we have a current word, validate it.
                    if current_word:
                        word_upper = current_word.upper()
                        if word_upper in dictionary:
                            result_message = f"'{current_word}' is a valid word!"
                            words_found_count += 1
                            words_found_list.append(word_upper)

                            # Compute points for this word and add to total score.
                            points = compute_points(word_upper)
                            score += points
                        else:
                            result_message = f"'{current_word}' is NOT valid."
                    else:
                        result_message = "No word entered."
                    
                    # Reset the current word and selected tiles after checking.
                    current_word = ""
                    selected_positions = []

        # Fill the background with a baby blue color.
        screen.fill(BABY_BLUE)

        # Fill the entire board area with a gray color (including gap area).
        pygame.draw.rect(screen, GRAY, board_rect)

        # Draw a thicker gray border around the board area.
        pygame.draw.rect(screen, GRAY, board_rect, 30)

        # Draw each tile on the board.
        for row_index, row in enumerate(board):
            for col_index, letter in enumerate(row):
                x_pos = board_offset_x + col_index * (TILE_SIZE + TILE_GAP)
                y_pos = board_offset_y + row_index * (TILE_SIZE + TILE_GAP)
                tile_rect = pygame.Rect(x_pos, y_pos, TILE_SIZE, TILE_SIZE)

                # If a tile is selected, highlight it, otherwise fill it with blue.
                if (row_index, col_index) in selected_positions:
                    pygame.draw.rect(screen, HIGHLIGHT_COLOR, tile_rect)
                else:
                    pygame.draw.rect(screen, BLUE, tile_rect)

                # Draw a black border around each tile.
                pygame.draw.rect(screen, BORDER_COLOR, tile_rect, 3)

                # Get the corresponding letter image and center it on the tile.
                letter_image = letter_images[letter]
                letter_rect = letter_image.get_rect(center=tile_rect.center)
                screen.blit(letter_image, letter_rect)

        # Display the current word at the top center of the screen.
        word_surf = font.render("Current Word: " + current_word, True, (0, 0, 0))
        word_rect = word_surf.get_rect(center=(WINDOW_WIDTH // 2, 30))
        screen.blit(word_surf, word_rect)

        # Display the number of words found so far in the top-right corner.
        count_surf = font.render("Words Found: " + str(words_found_count), True, (0, 0, 0))
        count_rect = count_surf.get_rect(topright=(WINDOW_WIDTH - 20, 20))
        screen.blit(count_surf, count_rect)

        # List out the words found below the "Words Found" count.
        y_offset = count_rect.bottom + 10
        for word in words_found_list:
            word_item = small_font.render(word, True, (0, 0, 0))
            screen.blit(word_item, (WINDOW_WIDTH - 200, y_offset))
            y_offset += word_item.get_height() + 5

        # Display the current score in the top-left corner.
        score_surf = font.render("Score: " + str(score), True, (0, 0, 0))
        score_rect = score_surf.get_rect(topleft=(20, 20))
        screen.blit(score_surf, score_rect)

        # Draw the "Check Word" button at the bottom center.
        draw_button(screen, button_rect, "Check Word", font)

        # If there's a result message (e.g., valid/invalid word), display it below the current word text.
        if result_message:
            result_surf = result_font.render(result_message, True, (0, 0, 0))
            result_rect = result_surf.get_rect(center=(WINDOW_WIDTH // 2, 70))
            screen.blit(result_surf, result_rect)

        # Update the full display surface to the screen.
        pygame.display.flip()

        # Limit the loop to run at the specified FPS.
        clock.tick(FPS)

    # Once the loop ends, quit pygame and exit the system.
    pygame.quit()
    sys.exit()

# If this file is run directly, call the main function to start the game.
if __name__ == "__main__":
    main()
