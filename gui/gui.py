import pygame
import sys
import time
import random

# Initialize Pygame
pygame.init()

# Load images
natural_eye = pygame.image.load('natural.jpg')
surprised_eye = pygame.image.load('surprised.jpg')
sad_eye = pygame.image.load('sad.jpg')
angry_eye = pygame.image.load('angry.jpg')

# Dictionary to store eye states
eye_images = {
    'natural': natural_eye,
    'surprised': surprised_eye,
    'sad': sad_eye,
    'blink': angry_eye
}

# Define state durations
blink_duration = 0.5  # seconds
random_state_duration = 2.0  # seconds
natural_duration = 2.0  # seconds

# Timing setup
state_start_time = time.time()
current_state = 'natural'

def get_random_state():
    return random.choice(['sad', 'surprised'])

# Initialize display
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption('Eye State Display')

def update_display(image):
    # Resize the image to fit the fullscreen
    image = pygame.transform.scale(image, (screen_width, screen_height))
    
    screen.fill((0, 0, 0))
    image_rect = image.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(image, image_rect)
    pygame.display.flip()

# Main loop
running = True
while running:
    current_time = time.time()

    if current_state == 'natural':
        # Check if it's time to switch to blink
        if current_time - state_start_time >= natural_duration:
            current_state = 'blink'
            state_start_time = current_time
    elif current_state == 'blink':
        # Check if it's time to switch to natural
        if current_time - state_start_time >= blink_duration:
            current_state = 'natural'
            state_start_time = current_time
    elif current_state in ['sad', 'surprised']:
        # Check if it's time to switch to natural
        if current_time - state_start_time >= random_state_duration:
            current_state = 'natural'
            state_start_time = current_time

    # Transition to a random state after natural state
    if current_state == 'natural' and current_time - state_start_time >= natural_duration:
        current_state = get_random_state()
        state_start_time = current_time

    # Get the current image based on the state
    current_image = eye_images[current_state]

    # Update the display with the current image
    update_display(current_image)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Clean up
pygame.quit()
sys.exit()
