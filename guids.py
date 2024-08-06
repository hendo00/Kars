import pygame

# Initialize Pygame
pygame.init()

# The GUID you want to connect to (example GUID, replace with actual GUID)
xbox_guid = "050082795e040000fd02000003090000"
ps4_guid = "05009b514c050000cc09000000810000"
# Flag to check if the joystick is found
xbox_found = False
ps4_found = False

# Iterate through the joysticks and connect to the one with the specific GUID

while not xbox_found:
    pygame.joystick.quit()
    pygame.joystick.init()
    num_joysticks = pygame.joystick.get_count()
    for i in range(num_joysticks):
        xbox = pygame.joystick.Joystick(i)
        xbox.init()
        guid = xbox.get_guid()
        #print(f"Joystick {i} GUID: {guid}")
        if guid == xbox_guid:
            print(f"Joystick with target GUID {xbox_guid} found and initialized.")
            xbox_found = True
            break

while not ps4_found:
    pygame.joystick.quit()
    pygame.joystick.init()
    num_joysticks = pygame.joystick.get_count()
    for i in range(num_joysticks):
        ps4 = pygame.joystick.Joystick(i)
        ps4.init()
        guid = ps4.get_guid()
        #print(f"Joystick {i} GUID: {guid}")
        if guid == ps4_guid:

            print(f"Joystick with target GUID {ps4_guid} found and initialized.")
            ps4_found = True
            break


# Your joystick handling code here

# Quit Pygame
pygame.quit()
