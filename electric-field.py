import math
import pygame
import sys

print(sys.executable)
print("pygame module loaded from:", pygame.__file__)
print("pygame type:", type(pygame))

# Constants
K = 1000.0  # Coulomb's constant (scaled for pixels)
SOFT = 2.0  # Softening parameter
WIDTH, HEIGHT = 1200, 800
GRID_SPACING = 30
ARROW_SCALE = 30  # How long arrows are drawn relative to field

# Colors
BG = (30, 30, 40)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


class Charge:
    def __init__(self, x, y, q):
        self.x = float(x)
        self.y = float(y)
        self.q = float(q)


def compute_field_at(px, py, charges):
    Ex = Ey = 0.0
    for c in charges:
        dx = px - c.x
        dy = py - c.y
        r2 = dx*dx + dy*dy + SOFT*SOFT
        inv_r3 = 1.0 / (r2 * math.sqrt(r2))
        Ex += K * c.q * dx * inv_r3
        Ey += K * c.q * dy * inv_r3
    return Ex, Ey


def magnitude(x, y):
    return math.sqrt(x*x + y*y)


def color_from_mag(mag, max_mag):
    t = max(0.0, min(1.0, mag / max_mag if max_mag > 0 else 0.0))
    r = int(255 * t)
    g = int(255 * (1 - t*0.4))
    b = int(255 * (1 - t))
    return (r, g, b)


def draw_arrow(surface, x, y, Ex, Ey, max_mag):
    mag = magnitude(Ex, Ey)
    if mag == 0:
        return
    # Normalize vector for drawing
    dx = (Ex / mag) * ARROW_SCALE
    dy = (Ey / mag) * ARROW_SCALE
    color = color_from_mag(mag, max_mag)
    end_pos = (int(x + dx), int(y + dy))
    pygame.draw.line(surface, color, (x, y), end_pos, 2)
    # Small arrowhead
    angle = math.atan2(dy, dx)
    arrow_size = 4
    left = (end_pos[0] - arrow_size * math.cos(angle - math.pi/6),
            end_pos[1] - arrow_size * math.sin(angle - math.pi/6))
    right = (end_pos[0] - arrow_size * math.cos(angle + math.pi/6),
             end_pos[1] - arrow_size * math.sin(angle + math.pi/6))
    pygame.draw.polygon(surface, color, [end_pos, left, right])


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Electric Field Visualizer (Arrows)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    charges = []
    active_sign = 1
    dragging = None
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:
                    # Check for dragging existing charge
                    idx = None
                    for i, c in enumerate(charges):
                        if (c.x - mx)**2 + (c.y - my)**2 < 16*16:
                            idx = i
                            break
                    if idx is not None:
                        dragging = idx
                    else:
                        charges.append(Charge(mx, my, active_sign * 1.0))
                elif event.button == 3:
                    # Remove nearest charge within 20 px
                    nearest = None
                    best = 400
                    for i, c in enumerate(charges):
                        d = (c.x - mx)**2 + (c.y - my)**2
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
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Dragging update
        if dragging is not None and charges:
            mx, my = pygame.mouse.get_pos()
            charges[dragging].x = mx
            charges[dragging].y = my

        # Drawing
        screen.fill(BG)

        # Precompute field on grid
        field_grid = []
        max_mag = 0.0
        for gx in range(0, WIDTH, GRID_SPACING):
            for gy in range(0, HEIGHT, GRID_SPACING):
                Ex, Ey = compute_field_at(gx, gy, charges)
                mag = magnitude(Ex, Ey)
                field_grid.append((gx, gy, Ex, Ey, mag))
                if mag > max_mag:
                    max_mag = mag

        # Draw arrows
        for gx, gy, Ex, Ey, mag in field_grid:
            draw_arrow(screen, gx, gy, Ex, Ey, max_mag)

        # Draw charges
        for c in charges:
            color = RED if c.q > 0 else BLUE
            pygame.draw.circle(screen, color, (int(c.x), int(c.y)), 6)

        # HUD
        hud_surf = font.render(
            f"Charges: {len(charges)}  Active sign: {'+' if active_sign >= 0 else '-'}{abs(active_sign)}  Left click: place/drag; Right click: remove; r: reset",
            True, WHITE)
        screen.blit(hud_surf, (5, 5))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
