import pygame as pg


pg.init()
screen = pg.display.set_mode((640, 480))
BG_COLOR = pg.Color(30, 30, 50)


def main():
    clock = pg.time.Clock()
    image = pg.Surface((50, 30))
    image.fill(pg.Color('dodgerblue'))
    pg.draw.rect(image, pg.Color(40, 220, 190), (0, 0, 49, 29), 2)
    player_rect = image.get_rect(topleft=(200, 200))
    # This pygame.Rect has the dimensions of the screen and
    # is used to clamp the player_rect to this area.
    screen_rect = screen.get_rect()
    speed = 5

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        pressed = pg.key.get_pressed()
        if pressed[pg.K_UP]:
            player_rect.y -= speed
        if pressed[pg.K_DOWN]:
            player_rect.y += speed
        if pressed[pg.K_LEFT]:
            player_rect.x -= speed
        if pressed[pg.K_RIGHT]:
            player_rect.x += speed
        # Clamp the rect to the dimensions of the screen_rect.
        player_rect.clamp_ip(screen_rect)

        screen.fill(BG_COLOR)
        screen.blit(image, player_rect)

        pg.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
    pg.quit()