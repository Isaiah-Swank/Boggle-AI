import pygame
import random
import string
import sys
import os
import collections  # For BFS with deque

# -----------------------
# CONSTANTS AND SETTINGS
# -----------------------

BOARD_SIZE = 4         # 4x4 board
TILE_SIZE = 100        # Each tile is 100x100 pixels
MARGIN = 5             # Margin inside each tile for the letter image
TILE_GAP = 10          # Gap between tiles

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

BLUE = (0, 0, 200)
BORDER_COLOR = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow for selected tiles
GRAY = (100, 100, 100)           # Darker gray for the board border
BABY_BLUE = (137, 207, 240)

FPS = 30  # Frames per second

# Button constants
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_COLOR = BLUE
BUTTON_TEXT_COLOR = (255, 255, 255)

def create_board(size=4):
    """Create a board of random uppercase letters."""
    board = []
    for _ in range(size):
        row = [random.choice(string.ascii_uppercase) for _ in range(size)]
        board.append(row)
    return board

def load_letter_images(filename, letter_size):
    """
    Loads the letters from a single sprite sheet (letters.png).
    Assumes 26 letters in one row: A-Z in order.
    Returns a dict mapping each letter 'A'-'Z' to a pygame.Surface.
    The images are scaled to letter_size.
    """
    letters_img = pygame.image.load(filename).convert_alpha()

    total_width = letters_img.get_width()
    total_height = letters_img.get_height()
    letter_width = total_width // 26

    letter_images = {}
    for i, letter in enumerate(string.ascii_uppercase):
        rect = pygame.Rect(i * letter_width, 0, letter_width, total_height)
        letter_surface = letters_img.subsurface(rect)
        letter_surface = pygame.transform.scale(letter_surface, letter_size)
        letter_images[letter] = letter_surface

    return letter_images

def load_dictionary(filename):
    """Load a dictionary file (one word per line) into a set."""
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

def build_prefix_set(dictionary):
    """
    Build a set of all possible prefixes in the dictionary.
    This allows quick checks of whether a partial word can lead to a valid word.
    """
    prefix_set = set()
    for word in dictionary:
        for i in range(len(word)):
            prefix_set.add(word[:i+1])
    return prefix_set

def find_all_words(board, dictionary, prefix_set):
    """
    Use BFS to find all possible words on the board that are in 'dictionary'.
    'prefix_set' is used to prune paths that can't form a valid word.
    Returns a sorted list of unique words.
    """
    found_words = set()
    rows = len(board)
    cols = len(board[0]) if rows else 0

    for r in range(rows):
        for c in range(cols):
            # Each queue entry: ((row, col), current_word, visited_positions)
            queue = collections.deque()
            start_letter = board[r][c]
            queue.append(((r, c), start_letter, {(r, c)}))

            while queue:
                (curr_r, curr_c), current_word, visited = queue.popleft()

                # If current_word is >= 3 letters and in dictionary, record it
                if len(current_word) >= 3 and current_word in dictionary:
                    found_words.add(current_word)

                # Only expand if current_word is still a valid prefix
                if current_word in prefix_set:
                    for nr in range(curr_r - 1, curr_r + 2):
                        for nc in range(curr_c - 1, curr_c + 2):
                            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                                new_word = current_word + board[nr][nc]
                                # Enqueue if the extended word is still a valid prefix
                                if new_word in prefix_set:
                                    new_visited = visited | {(nr, nc)}
                                    queue.append(((nr, nc), new_word, new_visited))

    return sorted(found_words)

def draw_button(screen, rect, text, font):
    """Draws a button with the given rect and text."""
    pygame.draw.rect(screen, BUTTON_COLOR, rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2)  # Black border for button
    text_surf = font.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def is_adjacent(pos1, pos2):
    """
    Check if pos2 is adjacent to pos1.
    Each position is a tuple (row, col). Adjacent means the difference in row
    and col is at most 1, excluding the case where they are the same.
    """
    r1, c1 = pos1
    r2, c2 = pos2
    return abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1 and not (r1 == r2 and c1 == c2)

def compute_points(word):
    """
    Compute points for a valid word:
      - 3 or 4 letter words: 1 point
      - 5 letter words: 2 points
      - 6 letter words: 3 points
      - Longer than 6: 5 points
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

def reset_game_state(dictionary, prefix_set):
    """
    Resets the entire board and other game-related variables.
    Returns a tuple of all the relevant items for a fresh start.
    """
    new_board = create_board(BOARD_SIZE)

    # Create letter images (scaled)
    letter_size = (TILE_SIZE - 2 * MARGIN, TILE_SIZE - 2 * MARGIN)
    new_letter_images = load_letter_images("letters.png", letter_size)

    # Score-related and word tracking variables
    new_current_word = ""
    new_result_message = ""
    new_selected_positions = []
    new_words_found_count = 0
    new_words_found_list = []
    new_score = 0

    # BFS results for the "Give Up" feature
    give_up = False
    all_possible_words = []
    word_display_index = 0  # Which BFS word is currently being displayed (and added)
    last_word_switch_time = 0
    display_interval = 1000  # 1 second per word
    time_give_up_completed = None  # track when we've shown all words
    completed_adding_all = False   # track if we've actually displayed/added all words

    return (new_board, new_letter_images, new_current_word, new_result_message,
            new_selected_positions, new_words_found_count, new_words_found_list,
            new_score, give_up, all_possible_words, word_display_index,
            last_word_switch_time, display_interval, time_give_up_completed,
            completed_adding_all)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Boggle Game - Gradual Reveal of Possible Words")
    clock = pygame.time.Clock()

    # Load dictionary and build prefix set
    dictionary = load_dictionary("dictionary.txt")
    prefix_set = build_prefix_set(dictionary)

    # ----------------------------
    # INITIALIZE / RESET GAME
    # ----------------------------
    (board, letter_images, current_word, result_message,
     selected_positions, words_found_count, words_found_list,
     score, give_up, all_possible_words, word_display_index,
     last_word_switch_time, display_interval, time_give_up_completed,
     completed_adding_all
     ) = reset_game_state(dictionary, prefix_set)

    # Precompute board positions
    board_pixel_width = BOARD_SIZE * TILE_SIZE + (BOARD_SIZE - 1) * TILE_GAP
    board_pixel_height = BOARD_SIZE * TILE_SIZE + (BOARD_SIZE - 1) * TILE_GAP
    board_offset_x = (WINDOW_WIDTH - board_pixel_width) // 2
    board_offset_y = (WINDOW_HEIGHT - board_pixel_height) // 2

    border_padding = 5
    board_rect = pygame.Rect(
        board_offset_x - border_padding,
        board_offset_y - border_padding,
        board_pixel_width + 2 * border_padding,
        board_pixel_height + 2 * border_padding
    )

    # Set up fonts
    font = pygame.font.SysFont(None, 36)
    result_font = pygame.font.SysFont(None, 28)
    small_font = pygame.font.SysFont(None, 24)

    # Define the "Check Word" button (bottom center)
    check_button_rect = pygame.Rect(
        (WINDOW_WIDTH - BUTTON_WIDTH) // 2 - 100,  # Shift left for space
        WINDOW_HEIGHT - BUTTON_HEIGHT - 30,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    # Define the "Give Up" button (placed next to "Check Word")
    give_up_button_rect = pygame.Rect(
        (WINDOW_WIDTH - BUTTON_WIDTH) // 2 + 100,  # Shift right for space
        WINDOW_HEIGHT - BUTTON_HEIGHT - 30,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                # Only allow tile selection if the player hasn't given up yet
                if not give_up:
                    # Check if click is on any tile
                    for row_index, row in enumerate(board):
                        for col_index, letter in enumerate(row):
                            x_pos = board_offset_x + col_index * (TILE_SIZE + TILE_GAP)
                            y_pos = board_offset_y + row_index * (TILE_SIZE + TILE_GAP)
                            tile_rect = pygame.Rect(x_pos, y_pos, TILE_SIZE, TILE_SIZE)
                            if tile_rect.collidepoint(mouse_pos):
                                # Make sure we either have no selected tiles
                                # or the new tile is adjacent to the last selected tile
                                if (row_index, col_index) not in selected_positions:
                                    if (not selected_positions or
                                            is_adjacent(selected_positions[-1], (row_index, col_index))):
                                        current_word += letter
                                        selected_positions.append((row_index, col_index))
                                        result_message = ""
                                break  # stop checking after one tile is clicked

                # Check if click is on the "Check Word" button (only if not given up)
                if check_button_rect.collidepoint(mouse_pos) and not give_up:
                    if current_word:
                        word_upper = current_word.upper()
                        if word_upper in dictionary:
                            result_message = f"'{current_word}' is a valid word!"
                            words_found_count += 1
                            words_found_list.append(word_upper)
                            score += compute_points(word_upper)
                        else:
                            result_message = f"'{current_word}' is NOT valid."
                    else:
                        result_message = "No word entered."
                    # Reset current word
                    current_word = ""
                    selected_positions = []

                # Check if click is on the "Give Up" button
                if give_up_button_rect.collidepoint(mouse_pos) and not give_up:
                    give_up = True
                    # Find all possible words via BFS
                    all_possible_words = find_all_words(board, dictionary, prefix_set)

                    # Prepare to display these words one-by-one
                    word_display_index = 0
                    last_word_switch_time = current_time
                    time_give_up_completed = None
                    completed_adding_all = False

        # ------------------------------
        # RENDER THE GAME EVERY FRAME
        # ------------------------------
        screen.fill(BABY_BLUE)

        # Board background and border
        pygame.draw.rect(screen, GRAY, board_rect)
        pygame.draw.rect(screen, GRAY, board_rect, 30)

        # Draw all tiles
        for row_index, row in enumerate(board):
            for col_index, letter in enumerate(row):
                x_pos = board_offset_x + col_index * (TILE_SIZE + TILE_GAP)
                y_pos = board_offset_y + row_index * (TILE_SIZE + TILE_GAP)
                tile_rect = pygame.Rect(x_pos, y_pos, TILE_SIZE, TILE_SIZE)

                # Highlight if selected
                if (row_index, col_index) in selected_positions:
                    pygame.draw.rect(screen, HIGHLIGHT_COLOR, tile_rect)
                else:
                    pygame.draw.rect(screen, BLUE, tile_rect)
                pygame.draw.rect(screen, BORDER_COLOR, tile_rect, 3)

                # Draw the letter
                letter_image = letter_images[letter]
                letter_rect = letter_image.get_rect(center=tile_rect.center)
                screen.blit(letter_image, letter_rect)

        # Display the current word
        word_surf = font.render("Current Word: " + current_word, True, (0, 0, 0))
        word_rect = word_surf.get_rect(center=(WINDOW_WIDTH // 2, 30))
        screen.blit(word_surf, word_rect)

        # Display how many words have been found
        count_surf = font.render("Words Found: " + str(words_found_count), True, (0, 0, 0))
        count_rect = count_surf.get_rect(topright=(WINDOW_WIDTH - 20, 20))
        screen.blit(count_surf, count_rect)

        # List the found words on the right
        y_offset = count_rect.bottom + 10
        for w in words_found_list:
            w_item = small_font.render(w, True, (0, 0, 0))
            screen.blit(w_item, (WINDOW_WIDTH - 200, y_offset))
            y_offset += w_item.get_height() + 5

        # Display the score on the top-left
        score_surf = font.render("Score: " + str(score), True, (0, 0, 0))
        score_rect = score_surf.get_rect(topleft=(20, 20))
        screen.blit(score_surf, score_rect)

        # Draw the buttons
        draw_button(screen, check_button_rect, "Check Word", font)
        draw_button(screen, give_up_button_rect, "Give Up", font)

        # Display result message if any
        if result_message:
            result_surf = result_font.render(result_message, True, (0, 0, 0))
            result_rect = result_surf.get_rect(center=(WINDOW_WIDTH // 2, 70))
            screen.blit(result_surf, result_rect)

        # -----------------------------
        # HANDLE "GIVE UP" WORD ROTATION
        # -----------------------------
        if give_up and all_possible_words:
            # If we still have words left to "reveal"...
            if word_display_index < len(all_possible_words):
                # Wait for 'display_interval' to add the next word
                if current_time - last_word_switch_time > display_interval:
                    displayed_word = all_possible_words[word_display_index]

                    # Add this word to the list (if not already present)
                    if displayed_word not in words_found_list:
                        words_found_list.append(displayed_word)
                        words_found_count += 1
                        score += compute_points(displayed_word)
                        # Sort the list just to keep it tidy
                        words_found_list.sort()

                    # Move to the next word
                    word_display_index += 1
                    last_word_switch_time = current_time

            else:
                # We've finished adding ALL possible words
                if not completed_adding_all:
                    completed_adding_all = True
                    time_give_up_completed = current_time  # mark the finish time

                # After 5 seconds, reset the game
                if current_time - time_give_up_completed > 5000:
                    (board, letter_images, current_word, result_message,
                     selected_positions, words_found_count, words_found_list,
                     score, give_up, all_possible_words, word_display_index,
                     last_word_switch_time, display_interval, time_give_up_completed,
                     completed_adding_all
                     ) = reset_game_state(dictionary, prefix_set)

                    # Recompute board area for the new board (if needed)
                    board_pixel_width = BOARD_SIZE * TILE_SIZE + (BOARD_SIZE - 1) * TILE_GAP
                    board_pixel_height = BOARD_SIZE * TILE_SIZE + (BOARD_SIZE - 1) * TILE_GAP
                    board_offset_x = (WINDOW_WIDTH - board_pixel_width) // 2
                    board_offset_y = (WINDOW_HEIGHT - board_pixel_height) // 2

                    board_rect = pygame.Rect(
                        board_offset_x - 5,
                        board_offset_y - 5,
                        board_pixel_width + 2 * 5,
                        board_pixel_height + 2 * 5
                    )

            # Show the currently "rotating" word if there's one in progress 
            if word_display_index < len(all_possible_words):
                displayed_word = all_possible_words[word_display_index]
                give_up_surf = font.render("Possible Word: " + displayed_word, True, (255, 0, 0))
                give_up_rect = give_up_surf.get_rect(center=(WINDOW_WIDTH // 2, 120))
                screen.blit(give_up_surf, give_up_rect)
            else:
                # Show a final message
                if completed_adding_all:
                    final_surf = font.render("All possible words displayed!", True, (255, 0, 0))
                    final_rect = final_surf.get_rect(center=(WINDOW_WIDTH // 2, 120))
                    screen.blit(final_surf, final_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
