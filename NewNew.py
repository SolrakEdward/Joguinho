import pygame
from pygame.locals import *
from sys import exit
import os
import time

pygame.init()

# Configurações da tela
largura_tela = 800
altura_tela = 600
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("RPG game")
fps = pygame.time.Clock()

# Carrega mapas
mapas = [
    pygame.transform.scale(pygame.image.load('mapa_fundo4.png').convert(), (largura_tela, altura_tela)),
    pygame.transform.scale(pygame.image.load('mapa_fundo5.png').convert(), (largura_tela, altura_tela)),
    pygame.transform.scale(pygame.image.load('fundo.png').convert(), (largura_tela, altura_tela)),
]
mapa_atual = 0

#imagem do monstro/slime
slime = pygame.image.load('sprites/slime.png').convert()

estado_jogo = "explore"
mover = True

#Jogador status
vida_player = 100
forca_player = 10
mana_total = 100

#Monstro status
vida_monstro = 50
forca_monstro = 3

#turno
turno = "player"

#Texto
pygame.font.init()
fonte = pygame.font.SysFont("arial", 18)

def desenhar_texto(texto, x, y, cor=(255, 255, 255)):
    img = fonte.render(texto, True, cor)
    tela.blit(img, (x, y))

msm = ""

# Jogador com sprite animada
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.sprites = [
            pygame.image.load(os.path.join('sprites', f'op_{i}.png')).convert_alpha()
            for i in range(1, 5)
        ]
        self.index = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(center=(400, 300))
        self.virado_para_esquerda = False
        self.anim_timer = 0

    def update(self, keys, velocidade):
        dx = dy = 0
        if keys[K_a]:
            dx -= velocidade
            self.virado_para_esquerda = False
        if keys[K_d]:
            dx += velocidade
            self.virado_para_esquerda = True
        if keys[K_w]:
            dy -= velocidade
        if keys[K_s]:
            dy += velocidade

        if dx != 0 or dy != 0:
            self.anim_timer += 1
            if self.anim_timer >= 10:
                self.index = (self.index + 1) % len(self.sprites)
                self.anim_timer = 0
        else:
            self.index = 0

        self.rect.x += dx
        self.rect.y += dy

        self.image = self.sprites[self.index]
        if self.virado_para_esquerda:
            self.image = pygame.transform.flip(self.image, True, False)

        return dx, dy

player = Player()
player_group = pygame.sprite.Group(player)

# -----------------------------
# FUNÇÕES DE COLISÃO POR MAPA
# -----------------------------

def colisao_bloqueia(player, obstaculo, pos_ant):
    player.rect = pos_ant  # impede movimento

def colisao_muda_mapa(player, obstaculo, pos_ant):
    global mapa_atual, lista
    mapa_atual = 2  # troca para mapa 2 (índice 2)
    player.rect.topleft = (100, 100)  # nova posição ao entrar
    lista = obstaculos_por_mapa.get(mapa_atual, [])

def modo_combate():
    global estado_jogo, mover
    estado_jogo = "combate"
    print("Combate iniciado!")
    mover = False

def colisao_inicia_combate(player, obs, pos_ant):
    global mapa_atual, lista
    modo_combate()
    mapa_atual = 2
    player.rect.topleft = (200, 300)
    lista = obstaculos_por_mapa.get(mapa_atual, [])
    

# -----------------------------
# OBSTÁCULOS POR MAPA
# -----------------------------

class Obstaculo:
    def __init__(self, rect, on_colisao):
        self.rect = rect
        self.on_colisao = on_colisao

obstaculos_por_mapa = {
    0: [
        Obstaculo(pygame.Rect(145, 70, 155, 80), colisao_bloqueia),
        Obstaculo(pygame.Rect(125, 412, 155, 80), colisao_bloqueia),
        Obstaculo(pygame.Rect(349, 395, 155, 80), colisao_bloqueia),
        Obstaculo(pygame.Rect(521, 411, 155, 80), colisao_bloqueia),
        Obstaculo(pygame.Rect(350, 70, 250, 120), colisao_bloqueia)

    ],
    1: [
        Obstaculo(pygame.Rect(70, 85, 300, 500), colisao_inicia_combate),
    ],
    2: [
        # Mapa vazio por enquanto
    ],
}

lista = obstaculos_por_mapa[mapa_atual]


# -----------------------------
# LOOP PRINCIPAL
# -----------------------------

while True:
    fps.tick(60)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    keys = pygame.key.get_pressed()
    tela.blit(mapas[mapa_atual], (0, 0))

    pos_ant = player.rect.copy()
    if mover == True:
        dx, dy = player.update(keys, 3.5)


    # Colisões com lógica personalizada
    for obs in lista:
        if player.rect.colliderect(obs.rect):
            obs.on_colisao(player, obs, pos_ant)

    # Troca de mapa ao sair da tela
    mudou_mapa = False
    if player.rect.right < 0:
        mapa_atual = (mapa_atual - 1) % len(mapas)
        player.rect.left = largura_tela
        mudou_mapa = True
    elif player.rect.left > largura_tela:
        mapa_atual = (mapa_atual + 1) % len(mapas)
        player.rect.right = 0
        mudou_mapa = True
    elif player.rect.bottom < 0:
        mapa_atual = (mapa_atual - 1) % len(mapas)
        player.rect.top = altura_tela
        mudou_mapa = True
    elif player.rect.top > altura_tela:
        mapa_atual = (mapa_atual + 1) % len(mapas)
        player.rect.bottom = 0
        mudou_mapa = True

    if mudou_mapa:
        lista = obstaculos_por_mapa.get(mapa_atual, [])

    if mapa_atual == 2 and estado_jogo == "combate":
        tela.blit(slime, (600, 310))

        if vida_monstro <= 0:
            desenhar_texto("O monstro morreu", 500, 460)
            pygame.display.flip()
            time.sleep(2)
            quit()

        #Textos na tela
        desenhar_texto("Modo Combate!", 25, 440, (255,0,0))
        desenhar_texto("Pressione [K] para atacar", 25, 470)
        desenhar_texto("Pressione [ESC] para fugir", 25, 495)
        desenhar_texto(f"Vida: {vida_player}", 25, 520)
        desenhar_texto(f"Vida do monstro: {vida_monstro}", 500, 440)

        if keys[K_k] and turno == "player":
            vida_monstro = vida_monstro - forca_player
            turno = "monstro"
            msm = "Você atacou"
            time.sleep(1)

        if turno == "monstro":
            vida_player = vida_player - forca_monstro
            turno = "player"


        if keys[K_ESCAPE]:
            desenhar_texto("Você fugiu", 25, 540, (255, 255, 0))
            pygame.display.flip()
            time.sleep(2)
            quit()

    if keys[K_l]:
        print(f"{player.rect.x}, {player.rect.y}")

    # Desenho
    player_group.draw(tela)
    #for obs in lista:
        #pygame.draw.rect(tela, (0, 255, 0), obs.rect)  # debug

    pygame.display.flip()
