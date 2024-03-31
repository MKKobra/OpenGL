import sys
import math
from random import randint
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Window dimensions
width, height = 400, 500

# Score
score = 0
previous_score = None
falling_circle_count = 0
missed_projectile_count = 0  # New variable to track missed projectiles

# Minimum and maximum circle radius
min_radius, max_radius = 7, 21

# Button coordinates and size
button1_x, button1_y, button1_size = 15, height - 15, 15
button2_x, button2_y, button2_size = width // 2, height - 15, 15
button3_x, button3_y, button3_size = width - 15, height - 15, 15

# Circle parameters
circle_radius = 15
circle_center_x = width // 2
circle_center_y = circle_radius

# Projectile parameters
projectile_radius = 4.5
projectile_speed = 0.4  # Adjust speed as needed
projectiles = []  # List to store projectile data (center_x, center_y)

# Falling circle parameters
falling_circle_speed = 0.02  # Adjust speed as needed
falling_circles = []  # List to store circle data (center_x, center_y, radius)

# Game state
game_paused = False


def draw_button(x, y, size, color):
    glColor3f(*color)  # Set color for button
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()


def draw_circle(radius, center_x, center_y, point_size):
    glColor3f(1, 1, 0)  # Yellow color for circle border
    glPointSize(point_size)
    glBegin(GL_POINTS)
    x = radius
    y = 0
    err = 0

    while x >= y:
        # Plot points for each octant
        glVertex2f(x + center_x, y + center_y)
        glVertex2f(y + center_x, x + center_y)
        glVertex2f(-x + center_x, y + center_y)
        glVertex2f(-y + center_x, x + center_y)
        glVertex2f(-x + center_x, -y + center_y)
        glVertex2f(-y + center_x, -x + center_y)
        glVertex2f(x + center_x, -y + center_y)
        glVertex2f(y + center_x, -x + center_y)

        # Midpoint algorithm
        if err <= 0:
            y += 1
            err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1

    glEnd()

def update_projectiles():
    global projectiles, missed_projectile_count, falling_circle_count

    if game_paused:
        return

    projectiles_to_remove = []

    for i in range(len(projectiles)):
        projectile_x, projectile_y = projectiles[i]
        projectile_center_y = projectile_y + projectile_speed
        if projectile_center_y + projectile_radius > height - 20:
            projectiles_to_remove.append(i)  # Mark projectile for removal
            missed_projectile_count += 1  # Increment missed projectile count
        else:
            collision_detected = check_projectile_collision(projectile_x, projectile_center_y)
            if not collision_detected:
                projectiles[i] = (projectile_x, projectile_center_y)  # Update projectile position

    # Remove projectiles marked for removal
    for index in sorted(projectiles_to_remove, reverse=True):
        del projectiles[index]

    # Check for game over due to missed projectiles
    if missed_projectile_count >= 3:
        falling_circle_count = 3  # Disable falling circles
        print("Game Over")
        print("Final Score:", score)
        glutLeaveMainLoop()  # Terminate the game and close the window

def draw_projectiles():
    global projectiles

    for projectile in projectiles:
        center_x, center_y = projectile
        draw_circle(projectile_radius, center_x, center_y, 2)

def update_falling_circles():
    global falling_circles, falling_circle_count
    new_falling_circles = []  # Create a new list to store updated circles

    if game_paused:
        return

    for i in range(len(falling_circles)):  # Loop through each circle index
        center_x, center_y, radius = falling_circles[i]
        center_y -= falling_circle_speed

        # Check if circle goes off-screen
        if center_y + radius < 0:
            pass  # Skip this circle (it will be removed later)
        else:
            if center_y - radius <= 0:  # Check if circle touches the bottom line
                falling_circle_count += 1
                if falling_circle_count >= 3:
                    print("Game Over")
                    print("Final Score:", score)
                    glutLeaveMainLoop()  # Terminate the game and close the window
            else:
                # Check for collision with the shooter circle
                if abs(center_x - circle_center_x - circle_radius) <= radius and abs(center_y - circle_center_y - circle_radius) <= radius:
                    print("Game Over")
                    print("Final Score:", score)
                    glutLeaveMainLoop()  # Terminate the game and close the window
                else:
                    new_falling_circles.append((center_x, center_y, radius))  # Update circle data

    falling_circles = new_falling_circles  # Replace the old list with the updated one

def create_falling_circle():
    global falling_circles

    if game_paused:
        return

    # Generate random radius within the specified range
    radius = randint(min_radius, max_radius)
    # Randomize horizontal position within the screen width
    center_x = randint(radius, width - radius)

    # Start the circle from the top of the screen
    center_y = height - 35

    falling_circles.append((center_x, center_y, radius))

def draw_falling_circles():
    global falling_circles

    for center_x, center_y, radius in falling_circles:
        draw_circle(radius, center_x, center_y, 2)  # Point size for falling circles

def idle():
    update_projectiles()
    update_falling_circles()
    # Add a new falling circle occasionally (adjust frequency as needed)
    if not game_paused and randint(0, 2500) == 0:  # Create a new circle every 2500th frame (adjust as desired)
        create_falling_circle()
    glutPostRedisplay()

def check_projectile_collision(projectile_x, projectile_y):
    global falling_circles, projectiles, score

    for i in range(len(falling_circles) - 1, -1, -1):  # Loop backwards for efficient removal
        center_x, center_y, radius = falling_circles[i]

        distance_centers = math.sqrt((projectile_x - center_x) ** 2 + (projectile_y - center_y) ** 2)
        combined_radius = radius + projectile_radius

        # Check for collision (considering combined radii)
        if distance_centers <= combined_radius:
            del falling_circles[i]  # Remove collided circle
            # Avoid removing from an empty list
            if projectiles:
                del projectiles[0]  # Remove the colliding projectile (index 0)
                score += 1
            return True  # Indicate collision occurred
    return False  # No collision detected

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def keyboard(key, x, y):
    global circle_center_x, projectiles

    if not game_paused:  # Only allow movement when the game is not paused
        if key == b'a':
            circle_center_x = max(circle_center_x - 4, circle_radius)
        elif key == b'd':
            circle_center_x = min(circle_center_x + 4, width - circle_radius)
        elif key == b' ':  # Spacebar pressed
            projectiles.append((circle_center_x, circle_center_y + circle_radius))  # Launch projectile

    glutPostRedisplay()

def mouse_click(button, state, x, y):
    global falling_circle_count, score, missed_projectile_count, falling_circles, projectiles, game_paused

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if button1_x <= x <= button1_x + button1_size and height - button1_y <= y <= height - button1_y + button1_size:
            # Reset game variables
            score = 0
            missed_projectile_count = 0
            falling_circles = []
            projectiles = []
            falling_circle_count = 0
            print("Starting Over")
        elif button2_x <= x <= button2_x + button2_size and height - button2_y <= y <= height - button2_y + button2_size:
            game_paused = not game_paused
        elif button3_x <= x <= button3_x + button3_size and height - button3_y <= y <= height - button3_y + button3_size:
            print("Goodbye")
            print("Final Score:", score)
            glutLeaveMainLoop()  # Exit the game

def display():
    global score, previous_score, falling_circle_count

    glClear(GL_COLOR_BUFFER_BIT)

    # Draw buttons with different colors and sizes
    draw_button(button1_x, button1_y, button1_size, (0, 0, 1))  # Blue button
    draw_button(button2_x, button2_y, button1_size, (0, 1, 0))  # Green button
    draw_button(button3_x, button3_y, button1_size, (1, 0, 0))  # Red button

    # Draw falling circles
    draw_falling_circles()

    # Draw the circle for launching projectiles
    draw_circle(circle_radius, circle_center_x, circle_center_y, 2)

    # Draw projectiles
    draw_projectiles()

    # Display current score only when it changes
    if previous_score != score:
        print("Score:", score)
        previous_score = score

    glutSwapBuffers()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"Circle Shooting Game")
    glClearColor(0, 0, 0, 1)  # Black background color
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse_click)  # Register mouse click function
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
