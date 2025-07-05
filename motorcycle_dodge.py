import pygame
import random
import sys
import os
import json

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 450, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Motorcyclist Dodge")

# Load images
road_img = pygame.image.load(os.path.join(os.path.dirname(__file__), 'road.png')).convert()
road_img = pygame.transform.scale(road_img, (WIDTH, HEIGHT))
motorcycle_img = pygame.image.load(os.path.join(os.path.dirname(__file__), 'motorcycle.png')).convert_alpha()
car_img = pygame.image.load(os.path.join(os.path.dirname(__file__), 'car.png')).convert_alpha()

# Resize images
player_width, player_height = int(75 * 0.75), int(120 * 0.75)  # 56, 90
motorcycle_img = pygame.transform.scale(motorcycle_img, (player_width, player_height))
car_width, car_height = int(90 * 0.75), int(140 * 0.75)  # 67, 105
car_img = pygame.transform.scale(car_img, (car_width, car_height))
road_img = pygame.transform.scale(road_img, (WIDTH, HEIGHT))

# Road scrolling variables
road_y1 = 0
road_y2 = -HEIGHT
base_road_speed = 4
road_speed = base_road_speed

# Player (motorcyclist) settings
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_speed = 5

# Car (obstacle) settings
base_car_speed = 3
car_speed = base_car_speed
cars = []

# Add font for score display
score = 0
font = pygame.font.SysFont(None, 36)
score_counter = 0  # Counter for slower score increment

# High score system
HIGH_SCORE_FILE = "high_score.json"

def load_high_scores():
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            data = json.load(f)
            # Handle both old format (just scores) and new format (scores with names)
            scores_data = data.get('scores', [])
            if scores_data and isinstance(scores_data[0], dict):
                # New format: list of dictionaries with 'score' and 'name'
                return scores_data
            else:
                # Old format: just list of scores, convert to new format
                return [{'score': score, 'name': 'Player'} for score in scores_data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_high_scores(scores):
    with open(HIGH_SCORE_FILE, 'w') as f:
        json.dump({'scores': scores}, f)

def get_player_name(score):
    """Get player name input for top 3 scores"""
    # Create a simple text input screen
    input_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Enter Your Name")
    
    name = ""
    input_active = True
    clock = pygame.time.Clock()
    
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Player"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name.strip():  # Only accept if name is not empty
                        return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    return "Player"
                elif len(name) < 12:  # Limit name length
                    # Only allow letters, numbers, and spaces
                    if event.unicode.isalnum() or event.unicode == ' ':
                        name += event.unicode
        
        # Draw input screen
        input_screen.fill((0, 0, 0))
        
        # Draw background road
        input_screen.blit(road_img, (0, 0))
        
        # Draw title
        title_font = pygame.font.SysFont(None, 48)
        title_surface = title_font.render("NEW HIGH SCORE!", True, (255, 255, 0))
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        input_screen.blit(title_surface, title_rect)
        
        # Draw score
        score_font = pygame.font.SysFont(None, 36)
        score_surface = score_font.render(f"Score: {score}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        input_screen.blit(score_surface, score_rect)
        
        # Draw input prompt
        prompt_font = pygame.font.SysFont(None, 32)
        prompt_surface = prompt_font.render("Enter your name:", True, (255, 255, 255))
        prompt_rect = prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        input_screen.blit(prompt_surface, prompt_rect)
        
        # Draw name input box
        input_font = pygame.font.SysFont(None, 40)
        input_surface = input_font.render(name + "|", True, (255, 255, 255))
        input_rect = input_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        input_screen.blit(input_surface, input_rect)
        
        # Draw instructions
        instruction_font = pygame.font.SysFont(None, 24)
        instruction1 = instruction_font.render("Press ENTER to save", True, (200, 200, 200))
        instruction2 = instruction_font.render("Press ESC to skip", True, (200, 200, 200))
        inst1_rect = instruction1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        inst2_rect = instruction2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        input_screen.blit(instruction1, inst1_rect)
        input_screen.blit(instruction2, inst2_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    return "Player"

def add_score_to_leaderboard(score):
    scores = load_high_scores()
    
    # Check if this score qualifies for top 3
    score_values = [entry['score'] for entry in scores]
    is_top_3 = len(scores) < 3 or score > min(score_values)
    
    if is_top_3:
        # Get player name
        player_name = get_player_name(score)
        # Add new score
        scores.append({'score': score, 'name': player_name})
        # Sort by score (descending)
        scores.sort(key=lambda x: x['score'], reverse=True)
        # Keep only top 3
        scores = scores[:3]
        save_high_scores(scores)
    
    return scores

# Load existing high scores
high_scores = load_high_scores()
high_score = high_scores[0]['score'] if high_scores else 0

# Load sounds
crash_sound = pygame.mixer.Sound('crash.wav')
pygame.mixer.music.load('background.wav')
pygame.mixer.music.play(-1)  # Loop forever

def spawn_car():
    x = random.randint(0, WIDTH - car_width)
    y = -car_height
    cars.append(pygame.Rect(x, y, car_width, car_height))

clock = pygame.time.Clock()
spawn_timer = 0

# Main game loop
running = True
while running:
    clock.tick(60)  # 60 FPS

    # Move and draw road
    road_y1 += road_speed
    road_y2 += road_speed
    if road_y1 >= HEIGHT:
        road_y1 = -HEIGHT
    if road_y2 >= HEIGHT:
        road_y2 = -HEIGHT
    screen.blit(road_img, (0, road_y1))
    screen.blit(road_img, (0, road_y2))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed

    # Spawn cars
    spawn_timer += 1
    if spawn_timer > 40:
        spawn_car()
        spawn_timer = 0

    # Move cars
    for car in cars:
        car.y += car_speed

    # Remove cars that are off screen
    cars = [car for car in cars if car.y < HEIGHT]

    # Draw player
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    screen.blit(motorcycle_img, (player_x, player_y))

    # Make the player hitbox 80% smaller and centered
    hitbox_width = int(player_width * 0.8)
    hitbox_height = int(player_height * 0.8)
    hitbox_x = player_x + (player_width - hitbox_width) // 2
    hitbox_y = player_y + (player_height - hitbox_height) // 2
    player_hitbox = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)

    # Draw cars and create smaller hitboxes for them
    car_hitboxes = []
    for car in cars:
        screen.blit(car_img, (car.x, car.y))
        car_hitbox_width = int(car_width * 0.8)
        car_hitbox_height = int(car_height * 0.8)
        car_hitbox_x = car.x + (car_width - car_hitbox_width) // 2
        car_hitbox_y = car.y + (car_height - car_hitbox_height) // 2
        car_hitboxes.append(pygame.Rect(car_hitbox_x, car_hitbox_y, car_hitbox_width, car_hitbox_height))

    # Collision detection
    collision = False
    for car_hitbox in car_hitboxes:
        if player_hitbox.colliderect(car_hitbox):
            collision = True
            break

    # Update and display score
    if not collision:
        score_counter += 1
        if score_counter >= 8:
            score += 1  # Increase score every 8 frames
            score_counter = 0
            # Increase speed every 50 points
            if score % 50 == 0:
                road_speed += 1
                car_speed += 1
    score_surface = font.render(f"Score: {score}", True, (255, 0, 0))
    high_score_surface = font.render(f"High Score: {high_score}", True, (255, 255, 0))
    screen.blit(high_score_surface, (10, 10))
    screen.blit(score_surface, (10, 50))

    if collision:
        crash_sound.play()
        pygame.mixer.music.stop()
        print("Game Over!")
        
        # Check and update high scores
        old_high_score = high_score
        high_scores = add_score_to_leaderboard(score)
        high_score = high_scores[0]['score'] if high_scores else 0
        
        # Check if this is a new high score
        if score > old_high_score:
            new_high_score = True
        else:
            new_high_score = False
            
        # Game Over screen
        game_over = True
        flash = True
        flash_timer = 0
        while game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = False
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Exit with ESC key
                        game_over = False
                        running = False
                    elif event.key == pygame.K_r:  # Restart with R key
                        # Reset game state
                        score = 0
                        score_counter = 0
                        road_speed = base_road_speed
                        car_speed = base_car_speed
                        cars = []
                        spawn_timer = 0
                        player_x = WIDTH // 2 - player_width // 2
                        player_y = HEIGHT - player_height - 10
                        road_y1 = 0
                        road_y2 = -HEIGHT
                        # Restart music
                        pygame.mixer.music.play(-1)
                        game_over = False
                        break
            # Redraw the last frame
            screen.blit(road_img, (0, road_y1))
            screen.blit(road_img, (0, road_y2))
            for car in cars:
                screen.blit(car_img, (car.x, car.y))
            screen.blit(motorcycle_img, (player_x, player_y))
            # Don't show the score/high score in top left during game over screen
            # Flashing GAME OVER text
            flash_timer += 1
            game_over_font = pygame.font.SysFont(None, 72)
            final_score_font = pygame.font.SysFont(None, 48)
            restart_font = pygame.font.SysFont(None, 36)
            # Draw GAME OVER (flashing) - moved higher
            if (flash_timer // 30) % 2 == 0:
                game_over_font_large = pygame.font.SysFont(None, 96)  # Increased from 72 to 96
                game_over_surface = game_over_font_large.render("GAME OVER", True, (255, 0, 0))
                game_over_rect = game_over_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
                screen.blit(game_over_surface, game_over_rect)
            
            # Draw the score (always visible) - moved higher
            final_score_surface = final_score_font.render(f"Score: {score}", True, (255, 0, 0))
            final_score_rect = final_score_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
            screen.blit(final_score_surface, final_score_rect)
            
            # Draw HIGH SCORE sign under the score if new high score
            if new_high_score:
                high_score_surface = final_score_font.render("HIGH SCORE!", True, (255, 255, 0))  # Yellow
                high_score_rect = high_score_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
                screen.blit(high_score_surface, high_score_rect)
            
            # Draw top 3 leaderboard - bigger font and moved higher
            leaderboard_font = pygame.font.SysFont(None, 36)  # Increased from 28 to 36
            leaderboard_title = leaderboard_font.render("TOP 3 RECORDS", True, (255, 255, 255))
            title_rect = leaderboard_title.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            screen.blit(leaderboard_title, title_rect)
            
            # Display top 3 scores with medal colors - bigger spacing
            current_position = -1  # Track which position the current score is in
            score_font_large = pygame.font.SysFont(None, 48)  # Larger font for scores
            for i in range(3):
                if i < len(high_scores):
                    # Show actual score with medal colors
                    if high_scores[i]['score'] == score:
                        current_position = i  # Remember the position
                        color = (255, 215, 0) if i == 0 else (192, 192, 192) if i == 1 else (205, 127, 50)  # Use medal color
                    elif i == 0:
                        color = (255, 215, 0)  # Gold for 1st place
                    elif i == 1:
                        color = (192, 192, 192)  # Silver for 2nd place
                    elif i == 2:
                        color = (205, 127, 50)  # Bronze for 3rd place
                    score_text = f"{i+1}. {high_scores[i]['name']} - {high_scores[i]['score']}"
                else:
                    # Show blank for missing score
                    color = (100, 100, 100)  # Gray color for blanks
                    score_text = f"{i+1}. ---"
                
                score_surface = score_font_large.render(score_text, True, color)
                score_rect = score_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80 + i * 45))  # Increased spacing from 35 to 45
                screen.blit(score_surface, score_rect)
            
            # Draw flashing red arrow pointing to current position
            if current_position >= 0 and (flash_timer // 15) % 2 == 0:  # Flash every 15 frames (faster than GAME OVER)
                # Calculate arrow position based on the actual text width
                current_score_text = f"{current_position+1}. {high_scores[current_position]['name']} - {high_scores[current_position]['score']}"
                text_surface = score_font_large.render(current_score_text, True, (255, 255, 255))
                text_width = text_surface.get_width()
                
                # Position arrow to the left of the text, with some spacing
                arrow_x = WIDTH // 2 - text_width // 2 - 40  # 40 pixels to the left of text start
                arrow_y = HEIGHT // 2 + 80 + current_position * 45  # Updated to match new spacing
                
                # Draw arrow as a triangle pointing right, size of one line
                arrow_size = 30  # Increased size to match larger score text
                arrow_points = [
                    (arrow_x, arrow_y),                    # tip
                    (arrow_x - arrow_size, arrow_y - 12),  # upper back (increased from 8 to 12)
                    (arrow_x - arrow_size + 8, arrow_y),   # middle back (increased from 5 to 8)
                    (arrow_x - arrow_size, arrow_y + 12)   # lower back (increased from 8 to 12)
                ]
                pygame.draw.polygon(screen, (255, 0, 0), arrow_points)
            
            # Draw restart instruction (always visible) - larger and moved higher
            restart_font_large = pygame.font.SysFont(None, 48)  # Increased from 36 to 48
            restart_surface = restart_font_large.render("Press R to Restart", True, (255, 255, 255))
            restart_rect = restart_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 250))
            screen.blit(restart_surface, restart_rect)
            
            # Draw exit instruction
            exit_surface = restart_font_large.render("ESC to Exit", True, (255, 255, 255))
            exit_rect = exit_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 300))
            screen.blit(exit_surface, exit_rect)
            pygame.display.flip()
            pygame.time.delay(33)  # ~30 FPS for flashing
        if game_over:  # If we didn't restart, break out of main loop
            break

    pygame.display.flip()

pygame.quit()
sys.exit() 