import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Window dimensions
width, height = 600, 450

# Button colors
button_colors = [(0.0, 0.0, 1.0),  # Blue
                 (0.0, 1.0, 0.0),  # Green
                 (1.0, 0.0, 0.0)]  # Red

# Tank top and bottom initial positions
tank_top_x = 280
tank_bottom_x = 280

# Projectile properties
projectile_radius = 5
bottom_projectiles = []
top_projectiles = []

#tank life
bottom_tank_life = 3
top_tank_life = 3

# Array to store button center coordinates
button_centers = []

# Variable to track game pause status
game_paused = False

# Variable to track game over time
game_over_time = None

# Projectile properties
class Projectile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.paused = False  # Initially not paused

bottom_projectiles = []
top_projectiles = []

# Function to draw a circle using midpoint circle algorithm
def draw_circle(center_x, center_y, radius):
    # Midpoint circle algorithm
    x = radius
    y = 0
    error = 1 - radius
    while x >= y:
        glBegin(GL_POINTS)
        glVertex2f(x + center_x, y + center_y)
        glVertex2f(y + center_x, x + center_y)
        glVertex2f(-x + center_x, y + center_y)
        glVertex2f(-y + center_x, x + center_y)
        glVertex2f(-x + center_x, -y + center_y)
        glVertex2f(-y + center_x, -x + center_y)
        glVertex2f(x + center_x, -y + center_y)
        glVertex2f(y + center_x, -x + center_y)
        glEnd()
        y += 1
        if error < 0:
            error += 2 * y + 1
        else:
            x -= 1
            error += 2 * (y - x) + 1

# Function to draw buttons
def draw_buttons():
    global button_centers
    button_radius = 7
    button_spacing = 280
    for i in range(3):
        button_center_x = 20 + i * button_spacing
        button_center_y = height - 20
        button_centers.append((button_center_x, button_center_y))
        glColor3f(*button_colors[i])
        draw_circle(button_center_x, button_center_y, button_radius)

# Function to draw a rectangular shape using midpoint line algorithm
def draw_rectangular(top_left_x, top_left_y, width, height):
    x1, y1 = top_left_x, top_left_y
    x2, y2 = top_left_x + width, top_left_y
    x3, y3 = top_left_x + width, top_left_y - height
    x4, y4 = top_left_x, top_left_y - height

    draw_line(x1, y1, x2, y2)
    draw_line(x2, y2, x3, y3)
    draw_line(x3, y3, x4, y4)
    draw_line(x4, y4, x1, y1)

# Function to draw a line using the midpoint line algorithm
def draw_line(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = -1 if x1 > x2 else 1
    sy = -1 if y1 > y2 else 1
    if dx > dy:
        err = dx / 2.0
        while x1 != x2:
            glBegin(GL_POINTS)
            glVertex2f(x1, y1)
            glEnd()
            err -= dy
            if err < 0:
                y1 += sy
                err += dx
            x1 += sx
    else:
        err = dy / 2.0
        while y1 != y2:
            glBegin(GL_POINTS)
            glVertex2f(x1, y1)
            glEnd()
            err -= dx
            if err < 0:
                x1 += sx
                err += dy
            y1 += sy
    glBegin(GL_POINTS)
    glVertex2f(x2, y2)
    glEnd()

# Function to draw the tank top rectangle
def draw_tank_top():
    # First rectangle
    glColor3f(1.0, 1.0, 1.0)
    draw_rectangular(tank_top_x, height - 35, 40, 30)
    
    # Second rectangle centered horizontally
    draw_rectangular(tank_top_x + 17, height - 65, 8, 20)

# Function to draw the tank bottom rectangle
def draw_tank_bottom():
    # First rectangle
    glColor3f(1.0, 1.0, 1.0)
    draw_rectangular(tank_bottom_x, height - 419, 40, 30)
    
    # Second rectangle centered horizontally
    draw_rectangular(tank_bottom_x + 17, height - 399, 8, 20)

# Function to draw projectiles
def draw_projectiles(projectiles, color):
    glColor3f(*color)
    for projectile in projectiles:
        draw_circle(projectile.x, projectile.y, projectile_radius)
        
# Function to handle when top projectile hits bottom tank
def top_hits_bottom():
    global bottom_tank_life
    for projectile in top_projectiles:
        # Check if projectile hits the bottom tank
        if (tank_bottom_x - 10 <= projectile.x <= tank_bottom_x + 45) and (height - 419 >= projectile.y <= height - 389):
            if 0 < bottom_tank_life <= 3:
                bottom_tank_life -= 1
                print("Bottom Tank life =", bottom_tank_life)
                top_projectiles.remove(projectile)
                if bottom_tank_life == 0:
                    print("Bottom Tank Distroyed")
                    print("Top Tank Wins")
                break

# Function to handle when bottom projectile hits top tank
def bottom_hits_top():
    global top_tank_life
    for projectile in bottom_projectiles:
        if (tank_top_x - 10 <= projectile.x <= tank_top_x + 45) and (height - 66 <= projectile.y <= height - 29):
            if 0 < top_tank_life <= 3:
                top_tank_life -= 1
                print("Top Tank life =", top_tank_life)
                bottom_projectiles.remove(projectile)
                if top_tank_life == 0:
                    print("Top Tank Distroyed")
                    print("Bottom Tank Wins")
                break

# Function to update projectile positions
def update_projectiles():
    global bottom_projectiles, top_projectiles
    if not game_paused:
        update_bottom_projectiles()
        update_top_projectiles()
        top_hits_bottom()
        bottom_hits_top()
    glutPostRedisplay()

# Function to update bottom projectiles
def update_bottom_projectiles():
    global bottom_projectiles
    new_projectiles = []
    for projectile in bottom_projectiles:
        if not projectile.paused:
            projectile.y += 0.5
        if projectile.y < height - 30:
            new_projectiles.append(projectile)
    bottom_projectiles = new_projectiles

# Function to update top projectiles
def update_top_projectiles():
    global top_projectiles
    new_top_projectiles = []
    for projectile in top_projectiles:
        if not projectile.paused:
            projectile.y -= 0.5
        if projectile.y > 5:
            new_top_projectiles.append(projectile)
    top_projectiles = new_top_projectiles

# Function to handle keyboard input for bottom tank
def key_pressed_bottom(key, x, y):
    global tank_bottom_x, game_paused
    if not game_paused:
        if key == GLUT_KEY_LEFT:
            tank_bottom_x = max(0, tank_bottom_x - 11)  # Ensure tank stays within left boundary
        elif key == GLUT_KEY_RIGHT:
            tank_bottom_x = min(width - 40, tank_bottom_x + 11)  # Ensure tank stays within right boundary
        glutPostRedisplay()

# Function to handle keyboard input for top tank
def key_pressed_top(key, x, y):
    global tank_top_x, game_paused
    if not game_paused:
        if key == b'a':
            tank_top_x = max(0, tank_top_x - 11)  # Ensure tank stays within left boundary
        elif key == b'd':
            tank_top_x = min(width - 40, tank_top_x + 11)  # Ensure tank stays within right boundary
        elif key == b'f':
            fire_top_projectile()
        elif key == b' ':
            fire_bottom_projectile()
        glutPostRedisplay()

def mouse_click(button, state, x, y):
    global button_centers, game_paused, bottom_tank_life, top_tank_life, tank_top_x, tank_bottom_x

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not game_paused:
            for i in range(len(button_centers)):
                button_x, button_y = button_centers[i]
                if button_x - 7 <= x <= button_x + 7 and height - y - 7 <= button_y <= height - y + 7:
                    if i == 0:
                        print("Game Restarted\n")
                        print("Top Tank life = 3")
                        print("Bottom Tank life = 3")
                        print("----------------------\n")
                        bottom_tank_life = 3
                        top_tank_life = 3
                        tank_top_x = 280
                        tank_bottom_x = 280
                        game_paused = False
                        glutPostRedisplay()
                        return  # Exit the function after restart

                    elif i == 1:
                        if not game_paused:
                            print("Game Paused")
                            game_paused = True
                            for projectile in bottom_projectiles + top_projectiles:
                                projectile.paused = True

                    elif i == 2:
                        glutLeaveMainLoop()
                        
        else:
            for i in range(len(button_centers)):
                button_x, button_y = button_centers[i]
                if button_x - 7 <= x <= button_x + 7 and height - y - 7 <= button_y <= height - y + 7 and i == 1:
                    print("Game Resumed")
                    game_paused = False
                    for projectile in bottom_projectiles + top_projectiles:
                        projectile.paused = False  # Resume projectiles
                    return
                        
# Function to fire projectile from the bottom tank
def fire_bottom_projectile():
    global bottom_projectiles, game_paused
    if not game_paused and bottom_tank_life > 0:
        bottom_projectiles.append(Projectile(tank_bottom_x + 20, height - 397))
# Function to fire projectile from the top tank
def fire_top_projectile():
    global top_projectiles, game_paused
    if not game_paused and top_tank_life > 0:
        top_projectiles.append(Projectile(tank_top_x + 20, height - 88))

def draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    draw_buttons()
    if top_tank_life > 0:
        draw_tank_top()
        draw_projectiles(bottom_projectiles, (1.0, 0.0, 0.0))
    if bottom_tank_life > 0:
        draw_tank_bottom()
        draw_projectiles(top_projectiles, (0.0, 1.0, 1.0))
    
    # Check for winning condition and display winning text if applicable
    if top_tank_life <= 0:
        draw_winning_text("Bottom Tank Wins")
    elif bottom_tank_life <= 0:
        draw_winning_text("Top Tank Wins")
    
    glutSwapBuffers()

# Function to draw winning text
def draw_winning_text(text):
    global game_over_time
    glColor3f(0.0, 1.0, 1.0)
    glRasterPos2i(width // 2 - 60, height // 2)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))
    
    if top_tank_life <= 0 or bottom_tank_life <= 0:
        if game_over_time is None:
            game_over_time = time.time()

        if time.time() - game_over_time >= 3:  # Check if 3 seconds have passed since game over
            glutLeaveMainLoop()

def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)

def main():
    print("Top Tank life = 3")
    print("Bottom Tank life = 3")
    print("----------------------\n")
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"OpenGL Window")
    glutDisplayFunc(draw)
    glutReshapeFunc(reshape)
    glutSpecialFunc(key_pressed_bottom)
    glutKeyboardFunc(key_pressed_top)
    glutMouseFunc(mouse_click)
    glutIdleFunc(update_projectiles)
    glutMainLoop()

if __name__ == "__main__":
    main()