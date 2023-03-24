import pygame
def init_window(size=[400, 400]):
    # initializing pygame
    pygame.init()

    clock = pygame.time.Clock()

    # Set the window screen size
    display_screen = pygame.display.set_mode(size)

    # add font style and size
    base_font = pygame.font.Font(None, 40)

    # stores text taken by keyboard
    user_text = ''

    # set left, top, width, height in
    # Pygame.Rect()
    input_rect = pygame.Rect(200, 200, 140, 32)
    color_active = pygame.Color("lightskyblue")
    color_passive = pygame.Color("gray15")
    color = color_passive

    active = False

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # when mouse collides with the rectangle
            # make active as true
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True

            # if the key is physically pressed down
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:

                    # stores text except last letter
                    user_text = user_text[0:-1]
                else:
                    user_text += event.unicode
                if event.key == 13:  # enter pressed
                    user_text = user_text[0:-1]
                    global message_pool
                    message_pool.append(user_text)
                    user_text = ''

        display_screen.fill((0, 0, 0))

        if active:
            color = color_active
        else:
            color = color_passive

        pygame.draw.rect(display_screen, color, input_rect)

        # render the text
        text_surface = base_font.render(user_text, True, (255, 255, 255))
        display_screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        input_rect.w = max(100, text_surface.get_width() + 10)
        pygame.display.flip()
        clock.tick(60)