import pygame

# Initialize Pygame and the mixer with 2 channels
pygame.init()
pygame.mixer.init(channels=2)

# Load the sounds
blank_sound_path = "test_sounds/blank_300.wav"
sound_left_path = "test_sounds/440Hz.wav"
sound_right_path = "test_sounds/1kHz.wav"
sound_tone_path = "test_sounds/3kHz.wav"
canary_sound_path = "test_sounds/CanaryAB.wav"

sound_left = pygame.mixer.Sound(sound_tone_path)
sound_right = pygame.mixer.Sound(canary_sound_path)

# Play the left sound on the left channel (Channel(0))
pygame.mixer.Channel(0).play(sound_left, loops=-1) # -1 for infinite loop
# pygame.mixer.Channel(0).stop() # Stop the sound

# Play the right sound on the right channel (Channel(1))
pygame.mixer.Channel(1).play(sound_right, loops=-1) # -1 for infinite loop

# Optionally, adjust the volume to ensure only one speaker plays the sound
# This step might not be necessary if your speakers are already configured correctly
pygame.mixer.Channel(0).set_volume(1.0, 0.0) # Full volume on left, mute on right
pygame.mixer.Channel(1).set_volume(0.0, 1.0) # Mute on left, full volume on right

# Keep the program running to allow the sounds to play
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
