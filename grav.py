import math
import pygame as pg
from pygame import gfxdraw


def draw_circle(surface, x, y, radius, color):
    if x > 3000 or y > 3000:
        return
    try:
        gfxdraw.aacircle(surface, x, y, radius, color)
        gfxdraw.filled_circle(surface, x, y, radius, color)
    except Exception:
        pass  # truly evil


pg.init()

font = pg.font.SysFont("monospace", 30)


def draw_rect_alpha(surface, color, rect):
    shape_surf = pg.Surface(pg.Rect(rect).size, pg.SRCALPHA)
    pg.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)


class Body:
    def __init__(self, name, mass, posx, posy, colour, radius, velx=0, vely=0) -> None:
        self.mass = mass
        self.position = pg.Vector2(posx, posy)
        self.velocity = pg.Vector2(velx, vely)
        self.acceleration = pg.Vector2(0, 0)
        self.radius = radius
        self.colour = colour
        self.name = name

    def update_position(self, delta_time):
        self.position += self.velocity * delta_time

    def get_gravity(self, bodies) -> pg.Vector2:
        G = 1
        total = pg.Vector2(0, 0)
        for body in bodies:
            if self.colour == body.colour:
                continue
            rhat = (body.position - self.position).normalize()
            sdist = (self.position - body.position).length()

            total += rhat * (self.mass * body.mass * G / (sdist*sdist))
        return total

    def update_velocity(self, delta_time, bodies):
        force = self.get_gravity(bodies)
        self.acceleration = force/self.mass
        self.velocity += self.acceleration * delta_time


class App:
    def __init__(self, width, height) -> None:
        self.surface = pg.display.set_mode((width, height))
        self.bodies = []
        self.clock = pg.time.Clock()
        self.focus = 0
        self.scale = 1

    def drawHud(self):
        focus = self.bodies[self.focus-1]
        if self.focus != 0:
            text = font.render(focus.name, True, focus.colour)
            text2 = font.render(
                f"Speed : {round(focus.velocity.magnitude(), 2)}", True, focus.colour)
            text3 = font.render(
                f"Altitude : {round((focus.position - self.bodies[0].position).magnitude(), 2)}", True, focus.colour)
            textRect2 = text2.get_rect()
            textRect3 = text3.get_rect()
            pg.draw.rect(self.surface, (0, 0, 0), (960-textRect2.centerx, 40,
                                                   textRect2.width, textRect2.height))
            self.surface.blit(text2, (960-textRect2.centerx, 40,
                                      textRect2.width, textRect2.height))
            pg.draw.rect(self.surface, (0, 0, 0), (960-textRect3.centerx, 70,
                                                   textRect3.width, textRect3.height))
            self.surface.blit(text3, (960-textRect3.centerx, 70,
                                      textRect3.width, textRect3.height))

        else:
            text = font.render("Space", True, focus.colour)

        textRect = text.get_rect()
        self.surface.blit(text, (960-textRect.centerx, 10,
                          textRect.width, textRect.height))

    def drawBody(self, body: Body) -> None:
        focused = pg.Vector2(0, 0)
        if (self.focus > 0):
            focused = self.bodies[self.focus-1].position

        pos = (body.position -
               focused) * self.scale + pg.Vector2(960, 540)
        draw_circle(self.surface, int(pos.x), int(pos.y),
                    int(body.radius*self.scale), body.colour)

    def draw(self, dt):
        self.drawHud()
        for body in self.bodies:
            body.update_velocity(dt, self.bodies)
        for body in self.bodies:
            body.update_position(dt)
        for body in self.bodies:
            self.drawBody(body)

    def run(self):
        running = True
        speed = 1
        self.surface.fill((20, 20, 20))

        while running:
            draw_rect_alpha(self.surface, (0, 0, 0, 5),
                            (0, 0, 1920, 1080))

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        self.focus = (self.focus-1) % (len(self.bodies)+1)
                    if event.key == pg.K_RIGHT:
                        self.focus = (self.focus+1) % (len(self.bodies)+1)
                    if event.key == pg.K_DOWN:
                        self.scale /= 2
                    if event.key == pg.K_UP:
                        self.scale *= 2
                    if event.key == pg.K_COMMA:
                        speed /= 2
                    if event.key == pg.K_PERIOD:
                        speed *= 2
                    if event.key == pg.K_SLASH:
                        speed *= -1

            if event.type == pg.QUIT:
                running = False
            ms = self.clock.tick(120)
            self.draw(ms/1000*speed)
            pg.display.flip()


a = App(1920, 1080)
a.bodies.append(Body("Lumen", 450000, 0, 0, (255, 255, 200), 50))
a.bodies.append(Body("Nisse", 45, -500, 0,
                (0x35, 0x1E, 0x29), 10, 0, math.sqrt(450000/500)))


a.run()
