import pygame
import sys

# Inicializar pygame
pygame.init()

# Configuración de ventana
ANCHO = 800
ALTO = 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("CLUE: Archivo Noir")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (20, 20, 30)
AZUL = (50, 90, 150)

# Jugador
jugador_x = 100
jugador_y = 100
velocidad = 5
tamaño = 20

# Reloj
clock = pygame.time.Clock()

# Loop principal
while True:
    pantalla.fill(NEGRO)

    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Teclas presionadas
    teclas = pygame.key.get_pressed()

    if teclas[pygame.K_LEFT]:
        jugador_x -= velocidad
    if teclas[pygame.K_RIGHT]:
        jugador_x += velocidad
    if teclas[pygame.K_UP]:
        jugador_y -= velocidad
    if teclas[pygame.K_DOWN]:
        jugador_y += velocidad

    # Dibujar jugador
    pygame.draw.rect(pantalla, AZUL, (jugador_x, jugador_y, tamaño, tamaño))

    pygame.display.flip()
    clock.tick(60)