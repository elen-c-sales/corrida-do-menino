"""
Corrida do Menino
Versao desktop do jogo feito para o R36S com PICO-8.

Personagem: menino com cabelo comprido castanho, camisa clara, bermuda e tenis.
Inspirado no dino-run-vecna-edition de Elen Camila Sales.
"""
import os
import random
import sys
import pygame

# Configuracoes
LARGURA = 640
ALTURA = 360
CHAO_Y = 290
FPS = 60
ARQUIVO_RECORDE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorde.txt")

# Cores
COR_CEU = (10, 12, 30)
COR_ESTRELA = (220, 230, 255)
COR_MONTANHA_LONGE = (35, 40, 70)
COR_MONTANHA_MEIO = (50, 45, 80)
COR_MONTANHA_PERTO = (70, 55, 90)
COR_CHAO = (28, 26, 40)
COR_LINHA_CHAO = (120, 110, 150)
COR_CABELO = (92, 58, 35)
COR_CABELO_CLARO = (120, 78, 48)
COR_PELE = (232, 180, 140)
COR_OLHO = (20, 20, 30)
COR_CAMISA = (60, 160, 200)
COR_BERMUDAS = (40, 70, 140)
COR_TENIS = (235, 235, 235)
COR_OBSTACULO = (180, 50, 60)
COR_TEXTO = (240, 240, 245)
COR_PONTOS = (120, 220, 180)

GRAVIDADE = 0.8
PULO_VEL = -13.5


def carregar_recorde():
    try:
        with open(ARQUIVO_RECORDE, "r", encoding="utf-8") as arquivo:
            return int(arquivo.read().strip())
    except (OSError, ValueError):
        return 0


def salvar_recorde(valor):
    try:
        with open(ARQUIVO_RECORDE, "w", encoding="utf-8") as arquivo:
            arquivo.write(str(valor))
    except OSError:
        pass


class Estrela:
    def __init__(self):
        self.x = random.uniform(0, LARGURA)
        self.y = random.uniform(0, 180)
        self.prof = random.uniform(0.1, 0.6)
        self.tamanho = 1 if self.prof < 0.4 else 2

    def atualizar(self, velocidade):
        self.x -= velocidade * self.prof * 0.35
        if self.x < 0:
            self.x += LARGURA

    def desenhar(self, tela):
        cor = COR_ESTRELA if self.prof > 0.35 else (120, 140, 190)
        pygame.draw.rect(tela, cor, (int(self.x), int(self.y), self.tamanho, self.tamanho))


class Montanhas:
    def __init__(self, cor, base, altura, fator, largura_pico):
        self.cor = cor
        self.base = base
        self.altura = altura
        self.fator = fator
        self.largura_pico = largura_pico
        self.desloc = 0.0

    def atualizar(self, velocidade):
        self.desloc = (self.desloc + velocidade * self.fator) % self.largura_pico

    def desenhar(self, tela):
        x = -self.largura_pico - self.desloc
        indice = 0
        while x < LARGURA + self.largura_pico:
            pico = self.base - self.altura - (indice % 3) * 10
            meio = x + self.largura_pico / 2
            pontos = [(x, self.base), (meio, pico), (x + self.largura_pico, self.base)]
            pygame.draw.polygon(tela, self.cor, pontos)
            x += self.largura_pico
            indice += 1
        pygame.draw.rect(
            tela, self.cor,
            (0, self.base - 2, LARGURA, ALTURA - self.base + 2)
        )


class Poeira:
    def __init__(self, x, y):
        self.x = x + random.uniform(0, 6)
        self.y = y - random.uniform(0, 4)
        self.vx = -1.5 - random.uniform(0, 2)
        self.vy = -random.uniform(0, 1)
        self.vida = random.randint(12, 24)
        self.max_vida = self.vida

    def atualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 1

    def desenhar(self, tela):
        if self.vida <= 0:
            return
        alpha = int(180 * self.vida / self.max_vida)
        cor = (140, 130, 170, alpha)
        surf = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, cor, (2, 2), 2)
        tela.blit(surf, (int(self.x), int(self.y)))


class Menino:
    def __init__(self):
        self.x = 90
        self.y = CHAO_Y
        self.vy = 0.0
        self.no_chao = True
        self.agachado = False
        self.corrindo = 0.0

    def pular(self):
        if self.no_chao and not self.agachado:
            self.vy = PULO_VEL
            self.no_chao = False

    def atualizar(self, velocidade, agachar):
        self.agachado = agachar and self.no_chao
        self.vy += GRAVIDADE
        self.y += self.vy
        if self.y >= CHAO_Y:
            self.y = CHAO_Y
            self.vy = 0
            self.no_chao = True
        self.corrindo += velocidade * 0.25

    def hitbox(self):
        if self.agachado:
            return pygame.Rect(int(self.x) + 4, int(self.y) - 22, 30, 22)
        return pygame.Rect(int(self.x) + 4, int(self.y) - 42, 28, 42)

    def desenhar_cabeca(self, tela, cx, cy):
        # cabelo comprido castanho (parte de tras)
        pygame.draw.rect(tela, COR_CABELO, (cx - 12, cy - 22, 24, 30))
        pygame.draw.rect(tela, COR_CABELO, (cx - 16, cy - 12, 6, 22))
        pygame.draw.rect(tela, COR_CABELO, (cx + 10, cy - 12, 6, 22))
        # mechas claras
        pygame.draw.rect(tela, COR_CABELO_CLARO, (cx - 10, cy - 20, 4, 22))
        pygame.draw.rect(tela, COR_CABELO_CLARO, (cx + 8, cy - 18, 3, 18))
        # rosto
        pygame.draw.rect(tela, COR_PELE, (cx - 9, cy - 18, 18, 20))
        # olho
        pygame.draw.circle(tela, COR_OLHO, (cx + 4, cy - 9), 2)
        # cabelo cobrindo a testa
        pygame.draw.rect(tela, COR_CABELO, (cx - 11, cy - 22, 21, 7))
        pygame.draw.rect(tela, COR_CABELO, (cx - 13, cy - 18, 5, 8))

    def desenhar(self, tela):
        cx = int(self.x) + 16
        base = int(self.y)

        if not self.no_chao:
            # cabelo balanca quando pula
            pygame.draw.line(
                tela, COR_CABELO,
                (cx - 15, base - 58), (cx - 26, base - 48), 4
            )

        if self.agachado:
            self.desenhar_cabeca(tela, cx - 8, base - 14)
            pygame.draw.rect(tela, COR_CAMISA, (cx - 14, base - 12, 36, 9))
            pygame.draw.rect(tela, COR_BERMUDAS, (cx - 12, base - 4, 22, 5))
            pygame.draw.rect(tela, COR_TENIS, (cx + 6, base - 5, 16, 6))
            return

        self.desenhar_cabeca(tela, cx, base - 52)

        # camisa
        pygame.draw.rect(tela, COR_CAMISA, (cx - 10, base - 34, 22, 20))

        # braco balancando
        braco = -6 if int(self.corrindo) % 2 == 0 else 6
        pygame.draw.line(
            tela, COR_PELE,
            (cx + 10, base - 30), (cx + 18, base - 16 + braco), 5
        )

        # bermuda
        pygame.draw.rect(tela, COR_BERMUDAS, (cx - 10, base - 16, 22, 12))

        # pernas correndo
        fase = int(self.corrindo) % 4
        if fase < 2:
            pygame.draw.line(tela, COR_PELE, (cx - 4, base - 5), (cx - 10, base), 5)
            pygame.draw.line(tela, COR_PELE, (cx + 5, base - 5), (cx + 11, base), 5)
        else:
            pygame.draw.line(tela, COR_PELE, (cx - 4, base - 5), (cx + 5, base), 5)
            pygame.draw.line(tela, COR_PELE, (cx + 5, base - 5), (cx - 4, base), 5)

        # tenis
        pygame.draw.rect(tela, COR_TENIS, (cx - 16, base - 5, 16, 6))
        pygame.draw.rect(tela, COR_TENIS, (cx + 3, base - 5, 16, 6))


class Obstaculo:
    def __init__(self, tipo):
        self.tipo = tipo
        self.x = float(LARGURA + 40)
        if tipo == "espinho":
            self.largura = 36
            self.altura = 46
            self.y = CHAO_Y
        else:
            self.largura = 48
            self.altura = 34
            self.y = CHAO_Y - 52

    def atualizar(self, velocidade):
        self.x -= velocidade

    def hitbox(self):
        return pygame.Rect(int(self.x), int(self.y) - self.altura, self.largura, self.altura)

    def desenhar(self, tela):
        if self.tipo == "espinho":
            for i in range(3):
                x = int(self.x) + i * 12
                pontos = [
                    (x, self.y),
                    (x + 6, self.y - self.altura),
                    (x + 12, self.y),
                ]
                pygame.draw.polygon(tela, COR_OBSTACULO, pontos)
            pygame.draw.rect(tela, COR_OBSTACULO, (int(self.x), self.y - 6, self.largura, 6))
        else:
            pygame.draw.rect(
                tela, COR_OBSTACULO,
                (int(self.x), int(self.y) - self.altura, self.largura, self.altura),
                border_radius=8
            )
            pygame.draw.circle(
                tela, COR_OBSTACULO,
                (int(self.x) + 14, int(self.y) - self.altura), 12
            )
            pygame.draw.circle(
                tela, COR_OBSTACULO,
                (int(self.x) + 32, int(self.y) - self.altura + 4), 10
            )


class Jogo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Corrida do Menino")
        self.clock = pygame.time.Clock()
        self.fonte = pygame.font.SysFont("consolas", 18, bold=True)
        self.fonte_grande = pygame.font.SysFont("consolas", 34, bold=True)
        self.recorde = carregar_recorde()
        self.estado = "titulo"

        self.estrelas = [Estrela() for _ in range(50)]
        self.montanhas_longe = Montanhas(COR_MONTANHA_LONGE, 240, 70, 0.10, 120)
        self.montanhas_meio = Montanhas(COR_MONTANHA_MEIO, 270, 50, 0.28, 90)
        self.montanhas_perto = Montanhas(COR_MONTANHA_PERTO, CHAO_Y, 34, 0.55, 70)
        self.reiniciar()

    def reiniciar(self):
        self.pontos = 0
        self.velocidade = 5.0
        self.intervalo_obstaculo = 90
        self.tempo_obstaculo = 0
        self.obstaculos = []
        self.poeira = []
        self.menino = Menino()
        self.estado = "jogando"

    def eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.estado == "titulo":
                    if evento.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_RETURN):
                        self.reiniciar()
                elif self.estado == "jogando":
                    if evento.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        self.menino.pular()
                elif self.estado == "game_over":
                    if evento.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                        self.reiniciar()

    def atualizar(self):
        if self.estado != "jogando":
            return

        teclas = pygame.key.get_pressed()
        agachar = teclas[pygame.K_DOWN] or teclas[pygame.K_s]
        self.menino.atualizar(self.velocidade, agachar)

        if self.menino.no_chao and pygame.time.get_ticks() % 90 < 16:
            self.poeira.append(Poeira(self.menino.x + 8, self.menino.y))

        for estrela in self.estrelas:
            estrela.atualizar(self.velocidade)
        self.montanhas_longe.atualizar(self.velocidade)
        self.montanhas_meio.atualizar(self.velocidade)
        self.montanhas_perto.atualizar(self.velocidade)

        for p in self.poeira[:]:
            p.atualizar()
            if p.vida <= 0:
                self.poeira.remove(p)

        for o in self.obstaculos[:]:
            o.atualizar(self.velocidade)
            if o.x + o.largura < 0:
                self.obstaculos.remove(o)

        self.tempo_obstaculo += 1
        if self.tempo_obstaculo >= self.intervalo_obstaculo:
            tipo = "espinho" if random.random() < 0.7 else "nuvem"
            self.obstaculos.append(Obstaculo(tipo))
            self.tempo_obstaculo = 0
            self.velocidade += 0.12
            self.intervalo_obstaculo = max(45, self.intervalo_obstaculo - 3)

        self.pontos += 1
        if self.pontos % 200 == 0:
            self.velocidade += 0.25

        hit = self.menino.hitbox()
        for o in self.obstaculos:
            if hit.colliderect(o.hitbox()):
                if self.pontos > self.recorde:
                    self.recorde = self.pontos
                    salvar_recorde(self.recorde)
                self.estado = "game_over"
                break

    def desenhar(self):
        self.tela.fill(COR_CEU)
        for estrela in self.estrelas:
            estrela.desenhar(self.tela)
        self.montanhas_longe.desenhar(self.tela)
        self.montanhas_meio.desenhar(self.tela)
        self.montanhas_perto.desenhar(self.tela)

        pygame.draw.rect(self.tela, COR_CHAO, (0, CHAO_Y, LARGURA, ALTURA - CHAO_Y))
        pygame.draw.line(self.tela, COR_LINHA_CHAO, (0, CHAO_Y), (LARGURA, CHAO_Y), 2)
        desloc = int(pygame.time.get_ticks() * self.velocidade * 0.08) % 24
        for x in range(-24 + desloc, LARGURA, 24):
            pygame.draw.line(self.tela, COR_LINHA_CHAO, (x, CHAO_Y + 10), (x + 10, CHAO_Y + 10), 1)

        for p in self.poeira:
            p.desenhar(self.tela)
        for o in self.obstaculos:
            o.desenhar(self.tela)
        if self.estado != "titulo":
            self.menino.desenhar(self.tela)

        texto_pontos = self.fonte.render("PONTOS " + str(self.pontos), True, COR_PONTOS)
        texto_recorde = self.fonte.render("REC " + str(self.recorde), True, COR_TEXTO)
        self.tela.blit(texto_pontos, (12, 10))
        self.tela.blit(texto_recorde, (LARGURA - 110, 10))

        if self.estado == "titulo":
            titulo = self.fonte_grande.render("CORRIDA DO MENINO", True, COR_TEXTO)
            subtitulo = self.fonte.render("O MUNDO INVERTIDO", True, COR_OBSTACULO)
            self.tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 60))
            self.tela.blit(subtitulo, (LARGURA // 2 - subtitulo.get_width() // 2, 100))
            dica = self.fonte.render("ESPACO PARA COMECAR", True, COR_PONTOS)
            self.tela.blit(dica, (LARGURA // 2 - dica.get_width() // 2, 200))
        elif self.estado == "game_over":
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.tela.blit(overlay, (0, 0))
            fim = self.fonte_grande.render("OPS! CAIU!", True, COR_OBSTACULO)
            pont = self.fonte.render("PONTOS: " + str(self.pontos), True, COR_TEXTO)
            rec = self.fonte.render("RECORDE: " + str(self.recorde), True, COR_PONTOS)
            dica = self.fonte.render("R OU ESPACO PARA RECOMECAR", True, COR_TEXTO)
            self.tela.blit(fim, (LARGURA // 2 - fim.get_width() // 2, 100))
            self.tela.blit(pont, (LARGURA // 2 - pont.get_width() // 2, 160))
            self.tela.blit(rec, (LARGURA // 2 - rec.get_width() // 2, 190))
            self.tela.blit(dica, (LARGURA // 2 - dica.get_width() // 2, 240))

        pygame.display.flip()

    def executar(self):
        while True:
            self.eventos()
            self.atualizar()
            self.desenhar()
            self.clock.tick(FPS)


def main():
    Jogo().executar()


if __name__ == "__main__":
    main()
