"""
FileName : electric-field.py
Author : Chanin Timbal
Date: March 2026
Description: A 2D electric field visualizer using Pygame, for PHY 222 at OIT
Code belongs to Chanin Timbal, all rights reserved. For educational use only.
"""

import math
import pygame
import sys


print(sys.executable)
print("pygame module loaded from:", pygame.__file__)
print("pygame type:", type(pygame))

# Constants
K = 1000.0                      # Coulomb's constant (scaled for visualization)
SOFT = 100.0                    # Softening factor to prevent singularities
WIDTH, HEIGHT = 1200, 800       # Window dimensions
GRID_SPACING = 25               # Distance between field sample points
ARROW_SCALE = 25                # Scaling factor for arrow lengths

# Colors for visualization
BG = (30, 30, 40)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
BLUE = (60, 120, 255)

# Charge Class


class Charge:
    def __init__(self, x, y, q):
        self.x = float(x)        # horizontal position
        self.y = float(y)        # vertical position
        self.q = float(q)        # charge magnitude (positive or negative)

# Field Computation


def compute_field_at(px, py, charges):
    # Initialize electric field components
    Ex = 0.0
    Ey = 0.0
    # Loop through each charge to compute its contribution to the field at (px, py)
    for c in charges:
        dx = px - c.x                               # horizontal distance from charge to point
        dy = py - c.y                               # vertical distance from charge to point
        # squared distance with softening to prevent singularities
        r2 = dx * dx + dy * dy + SOFT * SOFT
        # Compute the contribution of this charge to the electric field using Coulomb's law
        inv_r3 = 1.0 / (r2 * math.sqrt(r2))
        # Update the horizontal component of the electric field
        Ex += K * c.q * dx * inv_r3
        # Update the vertical component of the electric field
        Ey += K * c.q * dy * inv_r3
    return Ex, Ey


def magnitude(x, y):
    return math.sqrt(x * x + y * y)                 # maginude of a vector


# Color Mapping
def color_from_mag(mag, max_mag):
    if max_mag <= 0:                                # Avoid division by zero, return blue for zero field
        return (0, 0, 255)                          # blue for zero field

    # Slight power curve for better contrast
    # Normalize magnitude to [0, 1] with a power curve for better contrast
    t = (mag / max_mag) ** 0.4
    t = max(0.0, min(1.0, t))                       # limit t to [0, 1]

    # Blue → Cyan → Yellow → Red
    if t < 0.33:
        r = 0
        g = int(255 * (t / 0.33))
        b = 255
    elif t < 0.66:
        r = int(255 * ((t - 0.33) / 0.33))
        g = 255
        b = int(255 * (1 - (t - 0.33) / 0.33))
    else:
        r = 255
        g = int(255 * (1 - (t - 0.66) / 0.34))
        b = 0

    return (r, g, b)


# Arrow Drawing
def draw_arrow(surface, x, y, Ex, Ey, max_mag):
    mag = magnitude(Ex, Ey)
    if mag == 0:
        return

    # Normalize the electric field vector and scale it for visualization
    dx = (Ex / mag) * ARROW_SCALE
    dy = (Ey / mag) * ARROW_SCALE

    # Get color based on magnitude for visual feedback
    color = color_from_mag(mag, max_mag)
    # Calculate the end position of the arrow based on the electric field vector
    end_pos = (int(x + dx), int(y + dy))

    # Draw the main line of the arrow
    pygame.draw.line(surface, color, (x, y), end_pos, 2)

    # Calculate the angle of the arrow for drawing the arrowhead
    angle = math.atan2(dy, dx)
    arrow_size = 5
    left = (
        end_pos[0] - arrow_size * math.cos(angle - math.pi / 6),
        end_pos[1] - arrow_size * math.sin(angle - math.pi / 6),
    )
    right = (
        end_pos[0] - arrow_size * math.cos(angle + math.pi / 6),
        end_pos[1] - arrow_size * math.sin(angle + math.pi / 6),
    )
    pygame.draw.polygon(surface, color, [end_pos, left, right])


# Field Line Tracing
# trace a field line starting from (x, y) in both directions, return list of points
def trace_field_line(x, y, charges, step=4, max_steps=1500):
    points = [(x, y)]

    # trace in both directions (away from and towards the charge)
    for direction in (1, -1):
        px, py = x, y

        for _ in range(max_steps):
            # compute the electric field at the current point
            Ex, Ey = compute_field_at(px, py, charges)
            # compute the magnitude of the electric field
            mag = magnitude(Ex, Ey)
            if mag == 0:
                break

            # normalize the electric field vectors
            Ex /= mag
            Ey /= mag

            # move the point in the direction of the electric field (or opposite for negative direction)
            px += direction * Ex * step
            py += direction * Ey * step

            if px < 0 or px > WIDTH or py < 0 or py > HEIGHT:  # stop tracing if we go out of bounds
                break

            points.append((px, py))

    return points


# Main Loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Electric Field Visualizer - Chanin Timbal")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    charges = []
    active_sign = 1
    dragging = None
    field_line_mode = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if event.button == 1:
                    idx = None
                    for i, c in enumerate(charges):
                        if (c.x - mx) ** 2 + (c.y - my) ** 2 < 16 * 16:
                            idx = i
                            break
                    if idx is not None:
                        dragging = idx
                    else:
                        charges.append(Charge(mx, my, active_sign))

                elif event.button == 3:
                    nearest = None
                    best = 400
                    for i, c in enumerate(charges):
                        d = (c.x - mx) ** 2 + (c.y - my) ** 2
                        if d < best:
                            best = d
                            nearest = i
                    if nearest is not None:
                        charges.pop(nearest)

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = None

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    active_sign = max(-10, min(10, active_sign + 1))
                elif event.key == pygame.K_MINUS:
                    active_sign = max(-10, min(10, active_sign - 1))
                elif event.key == pygame.K_r:
                    charges.clear()
                elif event.key == pygame.K_f:
                    field_line_mode = not field_line_mode
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if dragging is not None and charges:
            mx, my = pygame.mouse.get_pos()
            charges[dragging].x = mx
            charges[dragging].y = my

        screen.fill(BG)

        # Precompute field grid (for arrow mode)
        field_grid = []
        max_mag = 0.0

        for gx in range(0, WIDTH, GRID_SPACING):
            for gy in range(0, HEIGHT, GRID_SPACING):
                Ex, Ey = compute_field_at(gx, gy, charges)
                mag = magnitude(Ex, Ey)
                field_grid.append((gx, gy, Ex, Ey, mag))
                if mag > max_mag:
                    max_mag = mag

        if not field_line_mode:
            # Draw arrows
            for gx, gy, Ex, Ey, mag in field_grid:
                draw_arrow(screen, gx, gy, Ex, Ey, max_mag)
        else:
            # Draw field lines
            for c in charges:
                num_lines = int(10 + abs(c.q) * 4)

                for i in range(num_lines):
                    angle = 2 * math.pi * i / num_lines
                    start_x = c.x + 12 * math.cos(angle)
                    start_y = c.y + 12 * math.sin(angle)

                    line = trace_field_line(start_x, start_y, charges)

                    if len(line) > 1:
                        Ex, Ey = compute_field_at(start_x, start_y, charges)
                        mag = magnitude(Ex, Ey)
                        color = color_from_mag(mag, max_mag)
                        pygame.draw.lines(screen, color, False, line, 1)

        # Draw charges
        for c in charges:
            color = RED if c.q > 0 else BLUE
            pygame.draw.circle(screen, color, (int(c.x), int(c.y)), 7)

        mode_text = "Field Lines" if field_line_mode else "Arrows"
        hud = font.render(
            f"Mode: {mode_text} | Charges: {len(charges)} | Active: {'+' if active_sign >= 0 else '-'}{abs(active_sign)} | F: toggle | R: reset",
            True,
            WHITE,
        )
        screen.blit(hud, (5, 5))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
