import pygame
import serial
import time

# Initialize Pygame
pygame.init()

# Setup window dimensions
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Water Tank Simulation')

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Water tank dimensions
tank_width = 200
tank_height = 500
tank_x = (WIDTH - tank_width) // 2
tank_y = HEIGHT - tank_height - 50

# Water level variables
max_fsr_value = 64  # Maximum FSR reading
max_water_liters = 2000  # Max water capacity (milliliters)
water_level_l = 0

# Serial port setup
serial_port = 'COM5'  # Update this with your correct COM port
baud_rate = 9600

try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    time.sleep(2)  # Wait for the connection to establish
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    ser = None

def read_fsr_from_arduino():
    """ Read the FSR value from the Arduino. """
    if ser and ser.in_waiting > 0:
        try:
            data = ser.readline().decode('utf-8').strip()
            if data:
                fsr_value = int(data)
                return fsr_value
        except ValueError:
            print(f"Invalid data received: {data}")
    return None

def map_fsr_to_liters(fsr_value):
    """ Map FSR value (0-64) to water capacity in liters (0-2000). """
    if fsr_value > max_fsr_value:
        fsr_value = max_fsr_value  # Cap the value to max FSR reading
    return (fsr_value / max_fsr_value) * max_water_liters

# Main game loop
running = True
clock = pygame.time.Clock()  # Create a clock to manage frame rate
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read FSR value from Arduino only when available
    fsr_value = read_fsr_from_arduino()
    if fsr_value is not None:
        water_level_l = map_fsr_to_liters(fsr_value)

    # Clear the screen
    screen.fill(WHITE)

    # Draw tank border
    pygame.draw.rect(screen, BLACK, (tank_x, tank_y, tank_width, tank_height), 5)

    # Calculate water height based on the current water level
    water_height = int((water_level_l / max_water_liters) * tank_height)

    # Draw water inside the tank
    pygame.draw.rect(screen, BLUE, (tank_x, tank_y + (tank_height - water_height), tank_width, water_height))

    # Display water level in milliliters
    font = pygame.font.SysFont(None, 36)
    text = font.render(f'Water Level: {int(water_level_l)} liters', True, BLACK)
    screen.blit(text, (tank_x + 10, tank_y - 40))

    # Update the display
    pygame.display.flip()

    # Limit the frame rate to 30 FPS
    clock.tick(30)

# Quit Pygame
pygame.quit()

# Close the serial connection
if ser:
    ser.close()
