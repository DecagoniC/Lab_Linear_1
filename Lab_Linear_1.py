import pygame
import math
import sys

pygame.init()
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WHITE = (255, 255, 255)
alpha = 0.05
beta = 0.05
u_min, u_max = 0.0, 10.0 * math.pi
v_min, v_max = -1.0, 1.0
u_steps, v_steps = 120, 75
rotation_y = 0.0
rotation_x = 0.0
is_dragging = False
last_x, last_y = 0, 0
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("SPIRALKA")


surface_points = []
du = (u_max - u_min) / (u_steps - 1)
dv = (v_max - v_min) / (v_steps - 1)
for i in range(u_steps):
    u = u_min + i * du
    row = []
    for j in range(v_steps):
        v = v_min + j * dv
        x = alpha * u * math.cos(u)
        y = beta * u * math.sin(u)
        z = v
        row.append([x, y, z])
    surface_points.append(row)

# Функция проекции 3D -> 2D
def project(point):
    z = point[2] + 4.0
    if z == 0:
        z = 0.1
    x = (point[0] * 4.0)/z* 100 + WINDOW_WIDTH / 2
    y = (point[1] * 4.0)/z* 100 + WINDOW_HEIGHT / 2
    return (int(x), int(y))

# Основной цикл
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                is_dragging = True
                last_x, last_y = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if is_dragging:
                current_x, current_y = pygame.mouse.get_pos()
                rotation_y += -(current_x - last_x) * 0.01
                rotation_x += (current_y - last_y) * 0.01
                last_x, last_y = current_x, current_y

    # Очистка экрана
    screen.fill(WHITE)

    # Проецирование и вращение точек
    rotated_points = [[None for _ in range(v_steps)] for _ in range(u_steps)]
    for i in range(u_steps):
        for j in range(v_steps):
            point = surface_points[i][j]
            x = point[0]
            y = point[1] * math.cos(rotation_x) - point[2] * math.sin(rotation_x)
            z = point[1] * math.sin(rotation_x) + point[2] * math.cos(rotation_x)
            x2 = x * math.cos(rotation_y) + z * math.sin(rotation_y)
            y2 = y
            z2 = -x * math.sin(rotation_y) + z * math.cos(rotation_y)
            rotated_points[i][j] = [x2, y2, z2]

    # Создание списка полигонов
    polygons = []
    for i in range(u_steps - 1):
        for j in range(v_steps - 1):
            p1 = rotated_points[i][j]
            p2 = rotated_points[i + 1][j]
            p3 = rotated_points[i + 1][j + 1]
            p4 = rotated_points[i][j + 1]
            avg_z = (p1[2] + p2[2] + p3[2] + p4[2]) / 4

            # Комбинированный градиент по u и v
            u_factor = i / (u_steps - 1)  # От 0 до 1 по u
            v_factor = (j + 0.5) / (v_steps - 1)  # От 0 до 1 по v
            red = int(255 * u_factor)  # Зависит от u
            green = int(255 * v_factor)  # Зависит от v
            blue = int(255 * (1 - u_factor * v_factor))  # Зависит от комбинации
            color = (red, green, blue)

            proj_p1 = project(p1)
            proj_p2 = project(p2)
            proj_p3 = project(p3)
            proj_p4 = project(p4)
            polygons.append((avg_z, [proj_p1, proj_p2, proj_p3, proj_p4], color))

    # Сортировка полигонов по глубине
    polygons.sort(key=lambda x: x[0], reverse=1)

    # Рисование полигонов
    for _, points, color in polygons:
        pygame.draw.polygon(screen, color, points)

    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)
