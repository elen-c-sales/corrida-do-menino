"""
Corrida do Menino: Aventura no Sitio (Para)
Versao desktop do jogo feito para o R36S com PICO-8.
Dedicado ao querido filho Sauron e aos nossos amados filhotes.

Personagem: Sauron (menino com cabelo comprido castanho, camisa clara, bermuda e tenis).
Cenario: Sitio no Para com mangueiras, bananeiras, muro de tijolinhos e folhas pelo chao.
Animais no quintal do sitio: Misty (grande), Shelby (grande), Saddam (baixinho) e o jabuti Jabotao.
Gatinhos ajudantes (desbloqueados pegando trequinhos tecnologicos):
  1. Catarino (branco, comprido) -> Pulo mais alto
  2. Coraline (frajola, magrela) -> Ima de trequinhos
  3. Hanna (branca com manchas rajadas, gordinha) -> Escudo que salva de 1 batida
  4. Scar (rajado com peito branco, grande e gordinho) -> Trequinhos em dobro + super pontos
"""
import asyncio
import math
import os
import random
import sys
import pygame

# Configuracoes
LARGURA = 640
ALTURA = 360
CHAO_Y = 294
FPS = 60
ARQUIVO_RECORDE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorde.txt")
CHAVE_RECORDE_WEB = "corrida-do-menino:recorde"

# Paleta do Sitio ao Entardecer / Noite Tropical no Para
COR_CEU_TOPO = (14, 22, 42)
COR_CEU_MEIO = (36, 48, 72)
COR_CEU_HORIZONTE = (110, 68, 58)

COR_LUA = (250, 240, 210)
COR_ESTRELA = (235, 242, 255)

COR_MATA_LONGE = (20, 38, 34)
COR_MATA_MEIO = (28, 52, 38)
COR_MURO = (118, 62, 46)
COR_MURO_ESCURO = (86, 42, 30)
COR_MURO_JUNTA = (68, 34, 24)

COR_TERRA = (76, 56, 42)
COR_TERRA_ESCURA = (54, 38, 28)
COR_GRAMA = (52, 108, 48)
COR_GRAMA_CLARA = (78, 142, 62)
COR_FOLHA_SECA = (210, 165, 45)
COR_FOLHA_MARROM = (145, 95, 40)

# Cores do menino
COR_CABELO_ESCURO = (62, 36, 20)
COR_CABELO = (98, 60, 34)
COR_CABELO_CLARO = (138, 90, 52)
COR_CABELO_BRILHO = (168, 115, 70)

COR_PELE = (240, 188, 148)
COR_PELE_SOMBRA = (208, 152, 114)
COR_BOCHECHA = (235, 130, 125)
COR_OLHO = (22, 20, 32)

COR_CAMISA = (75, 185, 230)
COR_CAMISA_SOMBRA = (48, 138, 182)
COR_CAMISA_DETALHE = (235, 245, 255)

COR_BERMUDAS = (42, 68, 135)
COR_BERMUDAS_SOMBRA = (28, 48, 100)

COR_TENIS = (242, 242, 248)
COR_TENIS_DETALHE = (220, 65, 75)
COR_SOLA = (90, 95, 115)

# Interface
COR_TEXTO = (245, 245, 252)
COR_PONTOS = (120, 240, 175)
COR_RECORDE = (255, 215, 95)
COR_TECH = (80, 235, 255)
COR_ALERTA = (255, 105, 95)

GRAVIDADE = 0.78
PULO_VEL = -13.5

# Dados dos Gatinhos Ajudantes
GATINHOS_INFO = [
    {
        "id": "catarino",
        "nome": "Catarino",
        "req": 3,
        "poder": "Pulo Alto Felino",
        "cor_tag": (160, 220, 255),
    },
    {
        "id": "coraline",
        "nome": "Coraline",
        "req": 7,
        "poder": "Ima de Trequinhos",
        "cor_tag": (140, 245, 170),
    },
    {
        "id": "hanna",
        "nome": "Hanna",
        "req": 12,
        "poder": "Escudo Salva-Vidas",
        "cor_tag": (255, 195, 130),
    },
    {
        "id": "scar",
        "nome": "Scar",
        "req": 18,
        "poder": "Trequinhos x2 + Turbo",
        "cor_tag": (255, 150, 210),
    },
]


def em_navegador():
    """Verdadeiro quando o jogo roda no navegador via Pygbag/Pyodide (WASM)."""
    return sys.platform in ("emscripten", "wasi") or "pyodide" in sys.modules


def _armazenamento_web():
    """Acesso ao localStorage do navegador, quando disponivel.

    O sistema de arquivos do Pygbag vive apenas em memoria (MEMFS), entao o
    recorde precisa ser salvo no localStorage para sobreviver ao recarregamento.
    """
    if not em_navegador():
        return None
    try:
        import platform as plataforma

        return plataforma.window.localStorage
    except Exception:
        return None


def criar_fonte(nome, tamanho, negrito=True):
    """Cria uma fonte adequada ao ambiente atual.

    No navegador nao existem fontes do sistema como o Consolas, portanto usamos
    a fonte embutida no pygame (freesansbold) com um tamanho equivalente.
    """
    if em_navegador():
        return pygame.font.Font(None, tamanho + (3 if negrito else 2))
    return pygame.font.SysFont(nome, tamanho, bold=negrito)


def carregar_recorde():
    armazenamento = _armazenamento_web()
    if armazenamento is not None:
        try:
            valor = armazenamento.getItem(CHAVE_RECORDE_WEB)
            return int(valor) if valor else 0
        except (AttributeError, TypeError, ValueError):
            return 0

    try:
        with open(ARQUIVO_RECORDE, "r", encoding="utf-8") as arquivo:
            return int(arquivo.read().strip())
    except (OSError, ValueError):
        return 0


def salvar_recorde(valor):
    armazenamento = _armazenamento_web()
    if armazenamento is not None:
        try:
            armazenamento.setItem(CHAVE_RECORDE_WEB, str(valor))
        except (AttributeError, TypeError):
            pass
        return

    try:
        with open(ARQUIVO_RECORDE, "w", encoding="utf-8") as arquivo:
            arquivo.write(str(valor))
    except OSError:
        pass


def criar_ceu_sitio():
    surf = pygame.Surface((LARGURA, CHAO_Y))
    meio = int(CHAO_Y * 0.58)
    for y in range(CHAO_Y):
        if y < meio:
            t = y / max(1, meio)
            r = int(COR_CEU_TOPO[0] + (COR_CEU_MEIO[0] - COR_CEU_TOPO[0]) * t)
            g = int(COR_CEU_TOPO[1] + (COR_CEU_MEIO[1] - COR_CEU_TOPO[1]) * t)
            b = int(COR_CEU_TOPO[2] + (COR_CEU_MEIO[2] - COR_CEU_TOPO[2]) * t)
        else:
            t = (y - meio) / max(1, CHAO_Y - meio)
            r = int(COR_CEU_MEIO[0] + (COR_CEU_HORIZONTE[0] - COR_CEU_MEIO[0]) * t)
            g = int(COR_CEU_MEIO[1] + (COR_CEU_HORIZONTE[1] - COR_CEU_MEIO[1]) * t)
            b = int(COR_CEU_MEIO[2] + (COR_CEU_HORIZONTE[2] - COR_CEU_MEIO[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (LARGURA, y))

    # Lua sob o ceu do Para
    lua_x, lua_y = 540, 58
    halo = pygame.Surface((110, 110), pygame.SRCALPHA)
    for raio, alpha in ((50, 16), (36, 30), (24, 50)):
        pygame.draw.circle(halo, (250, 220, 190, alpha), (55, 55), raio)
    surf.blit(halo, (lua_x - 55, lua_y - 55))
    pygame.draw.circle(surf, COR_LUA, (lua_x, lua_y), 17)
    pygame.draw.circle(surf, (22, 30, 52), (lua_x + 6, lua_y - 4), 14)
    return surf


class Estrela:
    def __init__(self):
        self.x = random.uniform(0, LARGURA)
        self.y = random.uniform(6, 150)
        self.prof = random.uniform(0.1, 0.5)
        self.fase = random.uniform(0, math.tau)

    def atualizar(self, velocidade):
        self.x -= velocidade * self.prof * 0.2
        self.fase += 0.05
        if self.x < 0:
            self.x += LARGURA

    def desenhar(self, tela):
        brilho = 0.6 + 0.4 * math.sin(self.fase)
        c = int(240 * brilho)
        pygame.draw.rect(tela, (c, c, min(255, c + 15)), (int(self.x), int(self.y), 2, 2))


class Vagalume:
    def __init__(self):
        self.x = random.uniform(0, LARGURA)
        self.y = random.uniform(120, CHAO_Y - 16)
        self.vel = random.uniform(0.2, 0.5)
        self.fase = random.uniform(0, math.tau)

    def atualizar(self, velocidade):
        self.x -= velocidade * self.vel
        self.fase += 0.08
        self.y += math.sin(self.fase) * 0.3
        if self.x < -6:
            self.x = LARGURA + random.uniform(5, 40)
            self.y = random.uniform(120, CHAO_Y - 16)

    def desenhar(self, tela):
        pulso = 0.5 + 0.5 * math.sin(self.fase * 1.5)
        alpha = int(60 + 160 * pulso)
        surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(surf, (190, 255, 90, alpha // 3), (4, 4), 4)
        pygame.draw.circle(surf, (230, 255, 140, alpha), (4, 4), 2)
        tela.blit(surf, (int(self.x) - 4, int(self.y) - 4))


class FundoSitio:
    """Desenha as mangueiras ao fundo, o muro de tijolinhos e as bananeiras."""
    def __init__(self):
        self.desloc_mata = 0.0
        self.desloc_muro = 0.0
        self.desloc_bananeiras = 0.0

    def atualizar(self, velocidade):
        self.desloc_mata = (self.desloc_mata + velocidade * 0.18) % 160
        self.desloc_muro = (self.desloc_muro + velocidade * 0.42) % 32
        self.desloc_bananeiras = (self.desloc_bananeiras + velocidade * 0.42) % 180

    def _desenhar_bananeira(self, tela, x, base_y):
        ix = int(x)
        # Tronco pseudocaule
        pygame.draw.line(tela, (95, 115, 58), (ix, base_y), (ix - 2, base_y - 52), 7)
        pygame.draw.line(tela, (125, 95, 55), (ix + 3, base_y - 12), (ix + 7, base_y - 34), 3)
        # Folhas secas penduradas (igual na foto da Misty!)
        pygame.draw.polygon(
            tela,
            (155, 120, 68),
            [(ix - 3, base_y - 36), (ix - 12, base_y - 16), (ix - 6, base_y - 14)],
        )
        pygame.draw.polygon(
            tela,
            (140, 105, 55),
            [(ix + 3, base_y - 34), (ix + 11, base_y - 14), (ix + 5, base_y - 12)],
        )
        # Folhas verdes largas no topo
        folhas = [
            (-28, -14, (62, 138, 52)),
            (-22, -26, (78, 160, 60)),
            (26, -16, (62, 138, 52)),
            (22, -28, (85, 168, 65)),
            (0, -32, (95, 178, 72)),
        ]
        topo_y = base_y - 50
        for dx, dy, cor in folhas:
            meio_x = ix + dx // 2
            meio_y = topo_y + dy - 6
            pygame.draw.polygon(
                tela,
                cor,
                [(ix, topo_y), (meio_x, meio_y), (ix + dx, topo_y + dy), (meio_x, meio_y + 7)],
            )

    def desenhar(self, tela):
        # 1. Silhueta de mangueiras frondosas ao fundo
        x = -160 - int(self.desloc_mata)
        idx = 0
        while x < LARGURA + 160:
            copa_y = 188 + (idx % 3) * 8
            # Tronco da mangueira
            pygame.draw.line(tela, (48, 34, 26), (x + 70, 255), (x + 70, copa_y + 15), 10)
            pygame.draw.line(tela, (48, 34, 26), (x + 70, copa_y + 25), (x + 52, copa_y + 8), 5)
            pygame.draw.line(tela, (48, 34, 26), (x + 70, copa_y + 22), (x + 90, copa_y + 6), 5)
            # Copa frondosa
            pygame.draw.circle(tela, COR_MATA_LONGE, (x + 48, copa_y + 10), 34)
            pygame.draw.circle(tela, COR_MATA_LONGE, (x + 92, copa_y + 12), 32)
            pygame.draw.circle(tela, COR_MATA_MEIO, (x + 70, copa_y), 38)
            pygame.draw.circle(tela, (38, 68, 44), (x + 66, copa_y - 6), 26)
            x += 160
            idx += 1

        # 2. Muro de tijolinhos do sitio (como nas fotos da Misty e do Saddam)
        muro_topo = 238
        muro_altura = CHAO_Y - muro_topo
        pygame.draw.rect(tela, COR_MURO, (0, muro_topo, LARGURA, muro_altura))
        pygame.draw.line(tela, COR_MURO_ESCURO, (0, muro_topo), (LARGURA, muro_topo), 3)

        for linha in range(0, muro_altura, 11):
            y = muro_topo + linha
            pygame.draw.line(tela, COR_MURO_JUNTA, (0, y), (LARGURA, y), 1)
            offset = 16 if (linha // 11) % 2 == 1 else 0
            x_tijolo = -32 - int(self.desloc_muro) + offset
            while x_tijolo < LARGURA + 32:
                pygame.draw.line(tela, COR_MURO_JUNTA, (x_tijolo, y), (x_tijolo, y + 11), 1)
                x_tijolo += 32

        # Pilares do muro
        x_pilar = -180 - int(self.desloc_bananeiras)
        while x_pilar < LARGURA + 180:
            pygame.draw.rect(tela, COR_MURO_ESCURO, (x_pilar, muro_topo - 3, 12, muro_altura + 3))
            # Touceira de bananeiras perto do muro
            self._desenhar_bananeira(tela, x_pilar + 55, CHAO_Y - 2)
            self._desenhar_bananeira(tela, x_pilar + 76, CHAO_Y)
            x_pilar += 180


class CachorroSitio:
    """Misty (grande), Shelby (grande), Saddam (baixinho) e o jabuti Jabotao no quintal do sitio."""
    def __init__(self, nome, x_inicial):
        self.nome = nome
        self.x = float(x_inicial)
        self.y = CHAO_Y - 3
        self.fase = random.uniform(0, math.tau)

    def atualizar(self, velocidade):
        fator_vel = 0.56 if self.nome == "Jabotao" else 0.48
        self.x -= velocidade * fator_vel
        self.fase += 0.07 if self.nome == "Jabotao" else 0.14
        if self.x < -120:
            self.x = LARGURA + random.uniform(140, 320)

    def desenhar(self, tela, fonte_mini):
        ix = int(self.x)
        iy = int(self.y)
        abano = int(math.sin(self.fase * 2.0) * 4)

        if self.nome == "Jabotao":
            # JABOTAO: Jabuti amazonico robusto, casco abaulado escuro com placas amarelas/ocre e detalhes vermelhos nas patas
            passo = int(math.sin(self.fase * 2.0) * 2)
            # Sombra do casco
            pygame.draw.ellipse(tela, (28, 20, 16), (ix - 2, iy - 3, 30, 5))
            # Patinhas grossas com escamas alaranjadas/avermelhadas (jabuti-piranga)
            pygame.draw.rect(tela, (85, 68, 52), (ix + 3 + passo, iy - 6, 5, 6), border_radius=2)
            pygame.draw.rect(tela, (85, 68, 52), (ix + 17 - passo, iy - 6, 5, 6), border_radius=2)
            pygame.draw.circle(tela, (215, 95, 55), (ix + 6 + passo, iy - 3), 1)
            pygame.draw.circle(tela, (215, 95, 55), (ix + 20 - passo, iy - 3), 1)
            # Pescoco e cabeca saindo da frente do casco
            pygame.draw.rect(tela, (95, 76, 58), (ix + 21, iy - 12, 9, 6), border_radius=3)
            pygame.draw.circle(tela, (225, 165, 70), (ix + 26, iy - 11), 2)
            pygame.draw.circle(tela, (20, 18, 18), (ix + 27, iy - 10), 1)
            # Casco abaulado (domo)
            pygame.draw.ellipse(tela, (52, 38, 26), (ix, iy - 19, 25, 16))
            pygame.draw.rect(tela, (76, 56, 42), (ix, iy - 6, 25, 3))
            # Placas geometricas do casco com centro amarelo-ocre
            for px, py, r in ((ix + 7, iy - 13, 3), (ix + 13, iy - 15, 3), (ix + 19, iy - 13, 3), (ix + 10, iy - 9, 2), (ix + 16, iy - 9, 2)):
                pygame.draw.circle(tela, (95, 68, 42), (px, py), r + 1)
                pygame.draw.circle(tela, (220, 175, 75), (px, py), r - 1)
            # Base da borda do casco
            pygame.draw.line(tela, (125, 92, 54), (ix + 1, iy - 6), (ix + 23, iy - 6), 2)
            txt = fonte_mini.render("Jabotao", True, (235, 230, 210))
            tela.blit(txt, (ix + 13 - txt.get_width() // 2, iy - 31))
            return

        # Sombra dos cachorros
        pygame.draw.ellipse(tela, (28, 20, 16), (ix - 4, iy - 3, 46, 6))

        if self.nome == "Misty":
            # MISTY: Bem grande, branca com cabeca preta, ponta do focinho branca e manchas pretas nas costas
            # Rabo
            pygame.draw.line(tela, (25, 25, 30), (ix, iy - 22), (ix - 9, iy - 28 + abano), 3)
            # Pernas compridas brancas
            pygame.draw.rect(tela, (230, 230, 236), (ix + 3, iy - 14, 5, 14))
            pygame.draw.rect(tela, (245, 245, 250), (ix + 9, iy - 14, 5, 14))
            pygame.draw.rect(tela, (230, 230, 236), (ix + 25, iy - 14, 5, 14))
            pygame.draw.rect(tela, (245, 245, 250), (ix + 31, iy - 14, 5, 14))
            # Corpo grande branco com manchas pretas no dorso/anca
            pygame.draw.rect(tela, (245, 245, 250), (ix, iy - 27, 36, 15), border_radius=6)
            pygame.draw.ellipse(tela, (28, 28, 34), (ix + 2, iy - 27, 15, 11))
            pygame.draw.ellipse(tela, (28, 28, 34), (ix + 19, iy - 26, 8, 8))
            # Pescoco branco e cabeca preta com focinho branco
            pygame.draw.rect(tela, (245, 245, 250), (ix + 28, iy - 33, 10, 12), border_radius=3)
            pygame.draw.rect(tela, (28, 28, 34), (ix + 30, iy - 39, 13, 12), border_radius=4)
            # Focinho branco e nariz preto
            pygame.draw.rect(tela, (245, 245, 250), (ix + 40, iy - 35, 7, 6), border_radius=2)
            pygame.draw.circle(tela, (20, 20, 24), (ix + 46, iy - 34), 2)
            # Orelha caidinha preta e lingua rosa
            pygame.draw.polygon(tela, (18, 18, 22), [(ix + 31, iy - 38), (ix + 26, iy - 31), (ix + 33, iy - 32)])
            pygame.draw.rect(tela, (235, 110, 130), (ix + 42, iy - 29, 4, 2))
            altura_tag = 48

        elif self.nome == "Shelby":
            # SHELBY: Bem grande e forte, todo ruivo/ferrugem (red nose), focinho rosado, olhos mel
            cor_ruivo = (178, 92, 42)
            cor_ruivo_esc = (142, 68, 28)
            # Rabo
            pygame.draw.line(tela, cor_ruivo_esc, (ix, iy - 23), (ix - 8, iy - 29 + abano), 3)
            # Pernas fortes
            pygame.draw.rect(tela, cor_ruivo_esc, (ix + 3, iy - 14, 5, 14))
            pygame.draw.rect(tela, cor_ruivo, (ix + 9, iy - 14, 5, 14))
            pygame.draw.rect(tela, cor_ruivo_esc, (ix + 26, iy - 14, 5, 14))
            pygame.draw.rect(tela, cor_ruivo, (ix + 32, iy - 14, 5, 14))
            # Corpo grande e musculoso
            pygame.draw.rect(tela, cor_ruivo, (ix, iy - 28, 38, 16), border_radius=6)
            # Detalhe discreto claro no peito
            pygame.draw.ellipse(tela, (215, 155, 110), (ix + 31, iy - 24, 7, 8))
            # Cabeca grande red nose
            pygame.draw.rect(tela, cor_ruivo, (ix + 29, iy - 39, 15, 14), border_radius=4)
            pygame.draw.rect(tela, (195, 110, 58), (ix + 40, iy - 35, 7, 7), border_radius=2)
            # Nariz rosado/vermelho tipico da foto!
            pygame.draw.circle(tela, (215, 115, 115), (ix + 46, iy - 33), 2)
            # Olho cor de mel
            pygame.draw.circle(tela, (230, 165, 50), (ix + 39, iy - 35), 2)
            pygame.draw.circle(tela, (30, 20, 15), (ix + 39, iy - 35), 1)
            # Orelha
            pygame.draw.polygon(tela, cor_ruivo_esc, [(ix + 31, iy - 38), (ix + 27, iy - 31), (ix + 33, iy - 32)])
            altura_tag = 48

        else:
            # SADDAM: Mais baixinho e parrudo! Caramelo/dourado, peito branco, focinho escuro, linguinha rosa
            cor_caramelo = (208, 142, 74)
            cor_caramelo_esc = (172, 110, 50)
            # Rabo
            pygame.draw.line(tela, cor_caramelo_esc, (ix + 2, iy - 16), (ix - 6, iy - 21 + abano), 3)
            # Perninhas mais baixas e fortes
            pygame.draw.rect(tela, cor_caramelo_esc, (ix + 4, iy - 9, 5, 9))
            pygame.draw.rect(tela, cor_caramelo, (ix + 10, iy - 9, 5, 9))
            pygame.draw.rect(tela, cor_caramelo_esc, (ix + 23, iy - 9, 5, 9))
            pygame.draw.rect(tela, cor_caramelo, (ix + 29, iy - 9, 5, 9))
            # Patinhas com pontinha branca
            pygame.draw.rect(tela, (245, 245, 250), (ix + 29, iy - 3, 6, 3))
            # Corpo parrudo baixinho
            pygame.draw.rect(tela, cor_caramelo, (ix + 2, iy - 21, 33, 13), border_radius=5)
            # Peito branco bem visivel (como na foto da varanda!)
            pygame.draw.ellipse(tela, (245, 245, 250), (ix + 26, iy - 20, 10, 11))
            # Cabeca larga com focinho escuro e lingua rosa
            pygame.draw.rect(tela, cor_caramelo, (ix + 27, iy - 30, 14, 12), border_radius=4)
            pygame.draw.rect(tela, (65, 52, 48), (ix + 37, iy - 26, 7, 5), border_radius=2)
            pygame.draw.ellipse(tela, (245, 120, 145), (ix + 39, iy - 22, 5, 4))
            pygame.draw.circle(tela, (30, 22, 18), (ix + 36, iy - 27), 2)
            # Orelha
            pygame.draw.polygon(tela, cor_caramelo_esc, [(ix + 29, iy - 30), (ix + 26, iy - 34), (ix + 33, iy - 29)])
            altura_tag = 39

        # Nome discreto acima do cachorro
        txt = fonte_mini.render(self.nome, True, (235, 230, 210))
        tela.blit(txt, (ix + 18 - txt.get_width() // 2, iy - altura_tag))


class GatinhoAjudante:
    """
    Desenha e anima o gatinho ajudante ativo atras do menino, respeitando o porte real:
    - Catarino: branco, olhos azuis, mais novo mas COMPRIDO.
    - Coraline: frajola preta e branca, MAGRELA.
    - Hanna: branca com manchas redondas rajadas, GORDINHA.
    - Scar: manto rajado com peito/focinho brancos, GRANDE E GORDINHO.
    """
    def __init__(self):
        self.x = 46.0
        self.y = float(CHAO_Y)
        self.historico_y = [float(CHAO_Y)] * 14
        self.fase = 0.0

    def atualizar(self, menino_x, menino_y, velocidade):
        self.historico_y.append(menino_y)
        if len(self.historico_y) > 10:
            self.historico_y.pop(0)
        alvo_y = self.historico_y[0]
        self.y += (alvo_y - self.y) * 0.35
        self.x = menino_x - 38
        self.fase += 0.06 + velocidade * 0.032

    def desenhar(self, tela, id_gato, escudo_pronto=False):
        if not id_gato:
            return

        ix = int(self.x)
        iy = int(self.y)
        pulo_bob = int(abs(math.sin(self.fase)) * 2.5) if iy >= CHAO_Y - 2 else 0
        cy = iy - pulo_bob
        osc = int(math.sin(self.fase) * 4)
        rabo_osc = int(math.cos(self.fase * 0.8) * 4)

        # Sombra no chao
        pygame.draw.ellipse(tela, (25, 18, 14), (ix - 2, CHAO_Y - 3, 28, 5))

        if id_gato == "catarino":
            # CATARINO: Todo branco, olhos azuis, nariz/orelhas rosa, corpo COMPRIDO
            cor_pelo = (248, 248, 252)
            cor_sombra = (220, 222, 232)
            # Rabo comprido branco
            pygame.draw.lines(
                tela, cor_pelo, False, [(ix, cy - 11), (ix - 8, cy - 17), (ix - 12, cy - 23 + rabo_osc)], 3
            )
            # Pernas
            pygame.draw.line(tela, cor_sombra, (ix + 4, cy - 7), (ix + 4 - osc, cy), 3)
            pygame.draw.line(tela, cor_pelo, (ix + 8, cy - 7), (ix + 8 + osc, cy), 3)
            pygame.draw.line(tela, cor_sombra, (ix + 22, cy - 7), (ix + 22 + osc, cy), 3)
            pygame.draw.line(tela, cor_pelo, (ix + 26, cy - 7), (ix + 26 - osc, cy), 3)
            # Corpo esguio e COMPRIDO (28px)
            pygame.draw.rect(tela, cor_pelo, (ix, cy - 14, 28, 8), border_radius=4)
            # Cabeca branca com orelhas rosadas e olhos azuis
            pygame.draw.circle(tela, cor_pelo, (ix + 28, cy - 15), 6)
            pygame.draw.polygon(tela, cor_pelo, [(ix + 24, cy - 19), (ix + 26, cy - 25), (ix + 29, cy - 20)])
            pygame.draw.polygon(tela, (245, 175, 185), [(ix + 25, cy - 20), (ix + 26, cy - 24), (ix + 28, cy - 20)])
            pygame.draw.polygon(tela, cor_pelo, [(ix + 29, cy - 19), (ix + 32, cy - 25), (ix + 33, cy - 19)])
            pygame.draw.circle(tela, (70, 155, 245), (ix + 30, cy - 16), 2)
            pygame.draw.circle(tela, (245, 150, 165), (ix + 34, cy - 14), 1)

        elif id_gato == "coraline":
            # CORALINE: Frajola preta e branca, MAGRELA, olhos verdes
            cor_preto = (26, 26, 34)
            cor_branco = (248, 248, 252)
            # Rabo fino preto
            pygame.draw.lines(
                tela, cor_preto, False, [(ix + 2, cy - 11), (ix - 6, cy - 18), (ix - 9, cy - 24 + rabo_osc)], 2
            )
            # Pernas fininhas com patinhas brancas
            pygame.draw.line(tela, cor_branco, (ix + 5, cy - 7), (ix + 5 - osc, cy), 2)
            pygame.draw.line(tela, cor_branco, (ix + 18, cy - 7), (ix + 18 + osc, cy), 2)
            # Corpo magrelinho (mais curto e fininho: 19x6)
            pygame.draw.rect(tela, cor_preto, (ix + 2, cy - 13, 19, 6), border_radius=3)
            pygame.draw.rect(tela, cor_branco, (ix + 6, cy - 9, 13, 3), border_radius=1)
            # Cabeca preta com listra branca no focinho e olhao verde
            pygame.draw.circle(tela, cor_preto, (ix + 21, cy - 15), 6)
            pygame.draw.polygon(tela, cor_branco, [(ix + 21, cy - 15), (ix + 27, cy - 13), (ix + 21, cy - 10)])
            pygame.draw.polygon(tela, cor_preto, [(ix + 17, cy - 19), (ix + 19, cy - 25), (ix + 22, cy - 20)])
            pygame.draw.polygon(tela, cor_preto, [(ix + 22, cy - 19), (ix + 25, cy - 25), (ix + 26, cy - 19)])
            pygame.draw.circle(tela, (125, 220, 95), (ix + 23, cy - 16), 2)

        elif id_gato == "hanna":
            # HANNA: Branca, GORDINHA, manchas redondas rajadas nas costas e capuz rajado
            cor_branco = (248, 248, 252)
            cor_rajado = (105, 88, 70)
            cor_rajado_esc = (68, 54, 42)
            # Rabo rajado
            pygame.draw.lines(
                tela, cor_rajado, False, [(ix + 1, cy - 12), (ix - 6, cy - 17), (ix - 9, cy - 21 + rabo_osc)], 3
            )
            # Pernas brancas
            pygame.draw.line(tela, (220, 220, 230), (ix + 5, cy - 7), (ix + 5 - osc, cy), 3)
            pygame.draw.line(tela, cor_branco, (ix + 9, cy - 7), (ix + 9 + osc, cy), 3)
            pygame.draw.line(tela, (220, 220, 230), (ix + 19, cy - 7), (ix + 19 + osc, cy), 3)
            pygame.draw.line(tela, cor_branco, (ix + 22, cy - 7), (ix + 22 - osc, cy), 3)
            # Corpo redondinho/gordinho!
            pygame.draw.ellipse(tela, cor_branco, (ix, cy - 18, 25, 14))
            # Manchas redondas rajadas nas costas (iguais a foto!)
            pygame.draw.circle(tela, cor_rajado, (ix + 9, cy - 13), 4)
            pygame.draw.circle(tela, cor_rajado_esc, (ix + 9, cy - 13), 2)
            pygame.draw.circle(tela, cor_rajado, (ix + 16, cy - 12), 4)
            pygame.draw.circle(tela, cor_rajado_esc, (ix + 16, cy - 12), 2)
            # Cabeca branca com topo/orelhas rajadas
            pygame.draw.circle(tela, cor_branco, (ix + 25, cy - 15), 6)
            pygame.draw.arc(tela, cor_rajado, (ix + 19, cy - 22, 12, 10), 0.3, 2.9, 4)
            pygame.draw.polygon(tela, cor_rajado, [(ix + 21, cy - 19), (ix + 23, cy - 25), (ix + 26, cy - 20)])
            pygame.draw.polygon(tela, cor_rajado, [(ix + 26, cy - 19), (ix + 29, cy - 25), (ix + 30, cy - 19)])
            pygame.draw.circle(tela, (125, 200, 95), (ix + 27, cy - 16), 2)

            # Se o escudo da Hanna estiver pronto, desenha uma aurinha dourada suave
            if escudo_pronto:
                aura = pygame.Surface((38, 30), pygame.SRCALPHA)
                pygame.draw.ellipse(aura, (255, 215, 100, 75), (0, 0, 38, 30), 2)
                tela.blit(aura, (ix - 3, cy - 24))

        elif id_gato == "scar":
            # SCAR: GRANDE E GORDINHO, manto rajado cinza/marrom, peito e focinho brancos, olhos verdes
            cor_rajado = (112, 102, 92)
            cor_listra = (64, 56, 50)
            cor_branco = (248, 248, 252)
            # Rabo grosso rajado
            pygame.draw.lines(
                tela, cor_rajado, False, [(ix - 1, cy - 14), (ix - 9, cy - 20), (ix - 12, cy - 25 + rabo_osc)], 4
            )
            # Pernas fortes brancas
            pygame.draw.line(tela, (220, 220, 230), (ix + 5, cy - 8), (ix + 5 - osc, cy), 4)
            pygame.draw.line(tela, cor_branco, (ix + 10, cy - 8), (ix + 10 + osc, cy), 4)
            pygame.draw.line(tela, (220, 220, 230), (ix + 22, cy - 8), (ix + 22 + osc, cy), 4)
            pygame.draw.line(tela, cor_branco, (ix + 26, cy - 8), (ix + 26 - osc, cy), 4)
            # Corpo GRANDAO e GORDINHO (30x16)
            pygame.draw.ellipse(tela, cor_rajado, (ix - 1, cy - 21, 30, 16))
            # Barriga e peito brancos
            pygame.draw.ellipse(tela, cor_branco, (ix + 4, cy - 12, 24, 7))
            pygame.draw.ellipse(tela, cor_branco, (ix + 20, cy - 18, 10, 12))
            # Listras de tigre no manto
            for lx in (ix + 6, ix + 11, ix + 16):
                pygame.draw.line(tela, cor_listra, (lx, cy - 20), (lx - 1, cy - 13), 2)
            # Cabeca grande rajada com focinho branco e nariz rosa
            pygame.draw.circle(tela, cor_rajado, (ix + 28, cy - 18), 7)
            pygame.draw.polygon(tela, cor_branco, [(ix + 28, cy - 18), (ix + 35, cy - 15), (ix + 27, cy - 11)])
            pygame.draw.polygon(tela, cor_rajado, [(ix + 23, cy - 23), (ix + 26, cy - 29), (ix + 29, cy - 23)])
            pygame.draw.polygon(tela, cor_rajado, [(ix + 29, cy - 23), (ix + 33, cy - 29), (ix + 34, cy - 22)])
            pygame.draw.circle(tela, (110, 215, 115), (ix + 30, cy - 19), 2)
            pygame.draw.circle(tela, (245, 145, 160), (ix + 34, cy - 15), 2)


class TrequinhoTech:
    """
    Premios tecnologicos de gambiarra para o menino pular e pegar:
    - mp3: MP3 Player antigo estilo pen-drive com tela iluminada e fone
    - cyberdeck: Maletinha hacker com tela verde, teclado colorido e antena
    - cassete: Fita cassete retro
    - placa: Placa de circuito impresso verde com chip e LED vermelho piscando
    """
    def __init__(self):
        self.tipo = random.choice(["mp3", "cyberdeck", "cassete", "placa"])
        self.x = float(LARGURA + 40)
        self.y_base = random.choice([CHAO_Y - 82, CHAO_Y - 108, CHAO_Y - 56])
        self.y = float(self.y_base)
        self.fase = random.uniform(0, math.tau)
        self.largura = 26
        self.altura = 22

    def atualizar(self, velocidade, menino, ima_ativo=False):
        self.x -= velocidade
        self.fase += 0.12
        self.y = self.y_base + math.sin(self.fase) * 4.5

        # Se a Coraline estiver ajudando, puxa o trequinho quando chega perto!
        if ima_ativo:
            alvo_x = menino.x + 18
            alvo_y = menino.y - 26
            dist = math.hypot(alvo_x - self.x, alvo_y - self.y)
            if dist < 155:
                self.x += (alvo_x - self.x) * 0.16
                self.y_base += (alvo_y - self.y_base) * 0.16
                self.y = self.y_base

    def hitbox(self):
        return pygame.Rect(int(self.x) - 4, int(self.y) - 4, self.largura + 8, self.altura + 8)

    def desenhar(self, tela):
        ix = int(self.x)
        iy = int(self.y)

        # Halo tecnologico brilhante
        halo = pygame.Surface((40, 40), pygame.SRCALPHA)
        pulso = int(50 + 25 * math.sin(self.fase * 2))
        pygame.draw.circle(halo, (80, 235, 255, pulso), (20, 20), 17)
        tela.blit(halo, (ix - 8, iy - 9))

        if self.tipo == "mp3":
            # MP3 Player antigo com telinha LCD azul e roda de botoes
            pygame.draw.rect(tela, (45, 52, 68), (ix, iy + 2, 24, 14), border_radius=4)
            pygame.draw.rect(tela, (180, 190, 210), (ix, iy + 2, 24, 14), 1, border_radius=4)
            pygame.draw.rect(tela, (90, 235, 255), (ix + 3, iy + 5, 11, 8), border_radius=1)
            pygame.draw.circle(tela, (230, 235, 245), (ix + 19, iy + 9), 3)
            pygame.draw.circle(tela, (50, 55, 70), (ix + 19, iy + 9), 1)
            # Fiozinho do fone
            pygame.draw.lines(tela, (220, 220, 235), False, [(ix + 24, iy + 8), (ix + 28, iy + 4), (ix + 26, iy - 1)], 1)

        elif self.tipo == "cyberdeck":
            # Cyberdeck de gambiarra: base cinza, tela terminal verde, antena com LED
            pygame.draw.line(tela, (180, 180, 195), (ix + 20, iy + 2), (ix + 23, iy - 6), 2)
            cor_led = (255, 60, 70) if int(self.fase * 2) % 2 == 0 else (255, 180, 60)
            pygame.draw.circle(tela, cor_led, (ix + 23, iy - 6), 2)
            # Tampa com tela verde fosforescente
            pygame.draw.rect(tela, (65, 70, 82), (ix + 2, iy, 20, 12), border_radius=2)
            pygame.draw.rect(tela, (20, 55, 32), (ix + 4, iy + 2, 16, 8))
            pygame.draw.line(tela, (90, 255, 130), (ix + 6, iy + 4), (ix + 15, iy + 4), 1)
            pygame.draw.line(tela, (90, 255, 130), (ix + 6, iy + 7), (ix + 12, iy + 7), 1)
            # Base com teclas coloridas
            pygame.draw.rect(tela, (95, 100, 115), (ix, iy + 11, 24, 7), border_radius=2)
            pygame.draw.rect(tela, (255, 90, 80), (ix + 3, iy + 13, 3, 2))
            pygame.draw.rect(tela, (90, 210, 255), (ix + 8, iy + 13, 8, 2))
            pygame.draw.rect(tela, (250, 215, 70), (ix + 18, iy + 13, 3, 2))

        elif self.tipo == "cassete":
            # Fita Cassete retro
            pygame.draw.rect(tela, (40, 42, 54), (ix, iy + 2, 24, 15), border_radius=2)
            pygame.draw.rect(tela, (235, 145, 55), (ix + 2, iy + 4, 20, 7))
            pygame.draw.circle(tela, (240, 240, 245), (ix + 8, iy + 8), 2)
            pygame.draw.circle(tela, (240, 240, 245), (ix + 16, iy + 8), 2)
            pygame.draw.polygon(tela, (75, 78, 95), [(ix + 5, iy + 17), (ix + 19, iy + 17), (ix + 17, iy + 13), (ix + 7, iy + 13)])

        else:
            # Placa de circuito verde (Arduino/Gambiarra) com trilhas douradas e LED
            pygame.draw.rect(tela, (28, 135, 75), (ix, iy + 2, 24, 16), border_radius=2)
            pygame.draw.rect(tela, (40, 40, 48), (ix + 7, iy + 6, 10, 8))
            for px in range(ix + 8, ix + 17, 3):
                pygame.draw.line(tela, (220, 195, 90), (px, iy + 4), (px, iy + 15), 1)
            cor_led = (255, 50, 50) if int(self.fase * 3) % 2 == 0 else (120, 255, 90)
            pygame.draw.circle(tela, cor_led, (ix + 20, iy + 6), 2)


class Particula:
    def __init__(self, x, y, cor=None, nota=False):
        self.x = x + random.uniform(-4, 6)
        self.y = y + random.uniform(-4, 2)
        self.vx = random.uniform(-2.6, 1.5)
        self.vy = random.uniform(-2.4, -0.4)
        self.vida = random.randint(16, 28)
        self.max_vida = self.vida
        self.cor = cor or random.choice([COR_FOLHA_SECA, COR_FOLHA_MARROM, (125, 95, 65)])
        self.nota = nota

    def atualizar(self):
        self.x += self.vx
        self.y += self.vy
        if not self.nota:
            self.vy += 0.06
        self.vida -= 1

    def desenhar(self, tela):
        if self.vida <= 0:
            return
        ix, iy = int(self.x), int(self.y)
        if self.nota:
            # Desenha notinha musical / faisca tech
            pygame.draw.circle(tela, self.cor, (ix, iy), 2)
            pygame.draw.line(tela, self.cor, (ix + 2, iy), (ix + 2, iy - 6), 1)
            pygame.draw.line(tela, self.cor, (ix + 2, iy - 6), (ix + 5, iy - 5), 2)
        else:
            pygame.draw.ellipse(tela, self.cor, (ix, iy, 5, 3))


class Menino:
    def __init__(self):
        self.x = 98
        self.y = float(CHAO_Y)
        self.vy = 0.0
        self.no_chao = True
        self.agachado = False
        self.corrindo = 0.0
        self.acabou_de_pousar = False

    def pular(self, bonus_pulo=1.0):
        if self.no_chao and not self.agachado:
            self.vy = PULO_VEL * bonus_pulo
            self.no_chao = False
            return True
        return False

    def atualizar(self, velocidade, agachar):
        self.acabou_de_pousar = False
        estava_no_ar = not self.no_chao
        self.agachado = agachar and self.no_chao

        if not self.no_chao and agachar:
            self.vy += GRAVIDADE * 1.9
        else:
            self.vy += GRAVIDADE

        self.y += self.vy
        if self.y >= CHAO_Y:
            self.y = float(CHAO_Y)
            self.vy = 0.0
            self.no_chao = True
            if estava_no_ar:
                self.acabou_de_pousar = True

        # Cadencia do ciclo de corrida: ~2,6 ciclos por segundo no inicio e
        # ~4,2 no maximo, em vez de acelerar junto com a dificuldade.
        self.corrindo += 0.15 + velocidade * 0.042

    def hitbox(self):
        if self.agachado:
            return pygame.Rect(int(self.x) + 6, int(self.y) - 24, 26, 24)
        return pygame.Rect(int(self.x) + 8, int(self.y) - 44, 20, 44)

    def _desenhar_cabelo_tras(self, tela, cx, cy, vento_y):
        onda = math.sin(self.corrindo * 0.9) * 2.5
        onda2 = math.cos(self.corrindo * 0.9) * 2.5

        pygame.draw.rect(
            tela, COR_CABELO_ESCURO, (cx - 14, cy - 19, 24, 26), border_radius=6
        )
        for i in range(4):
            desloc_y = cy - 10 + i * 5
            comprimento = 14 - i * 1.5
            balanco = int(onda if i % 2 == 0 else onda2) + int(vento_y)
            ponto_ini = (cx - 10, desloc_y)
            ponto_meio = (cx - 16, desloc_y + 3 + balanco // 2)
            ponto_fim = (int(cx - 12 - comprimento), desloc_y + 5 + balanco)
            cor_mecha = COR_CABELO if i % 2 == 0 else COR_CABELO_ESCURO
            pygame.draw.lines(tela, cor_mecha, False, [ponto_ini, ponto_meio, ponto_fim], 5)

        pygame.draw.line(
            tela,
            COR_CABELO_CLARO,
            (cx - 11, cy - 8),
            (cx - 22, cy - 3 + int(onda) + int(vento_y)),
            3,
        )

    def _desenhar_cabeca(self, tela, cx, cy, caido=False):
        vento_y = max(-5, min(6, self.vy * 0.45)) if not self.no_chao else 0
        self._desenhar_cabelo_tras(tela, cx, cy, vento_y)

        pygame.draw.rect(tela, COR_PELE_SOMBRA, (cx - 4, cy + 1, 8, 6))
        pygame.draw.rect(tela, COR_PELE, (cx - 9, cy - 17, 20, 20), border_radius=5)
        pygame.draw.rect(tela, COR_PELE_SOMBRA, (cx - 9, cy - 2, 18, 4), border_radius=2)

        pygame.draw.circle(tela, COR_PELE, (cx - 7, cy - 6), 3)
        pygame.draw.circle(tela, COR_PELE_SOMBRA, (cx - 7, cy - 6), 1)

        if caido:
            pygame.draw.line(tela, COR_OLHO, (cx + 2, cy - 10), (cx + 7, cy - 5), 2)
            pygame.draw.line(tela, COR_OLHO, (cx + 7, cy - 10), (cx + 2, cy - 5), 2)
            pygame.draw.circle(tela, COR_OLHO, (cx + 5, cy - 1), 2)
        else:
            pygame.draw.line(tela, COR_CABELO_ESCURO, (cx + 2, cy - 12), (cx + 8, cy - 11), 2)
            pygame.draw.rect(tela, COR_OLHO, (cx + 3, cy - 9, 4, 5), border_radius=2)
            pygame.draw.rect(tela, (255, 255, 255), (cx + 5, cy - 9, 2, 2))
            pygame.draw.circle(tela, COR_BOCHECHA, (cx + 2, cy - 3), 2)
            pygame.draw.line(tela, COR_PELE_SOMBRA, (cx + 5, cy - 2), (cx + 8, cy - 3), 2)

        # Topo do cabelo e franja comprida castanha
        pygame.draw.rect(tela, COR_CABELO, (cx - 13, cy - 22, 25, 9), border_radius=5)
        pygame.draw.line(tela, COR_CABELO_BRILHO, (cx - 7, cy - 20), (cx + 5, cy - 20), 2)
        pygame.draw.line(tela, COR_CABELO_CLARO, (cx - 9, cy - 18), (cx + 7, cy - 18), 2)

        onda_franja = int(math.sin(self.corrindo * 0.9) * 1.5)
        pygame.draw.polygon(
            tela,
            COR_CABELO,
            [
                (cx - 13, cy - 17),
                (cx - 4, cy - 16),
                (cx - 6, cy + 7 + onda_franja),
                (cx - 14, cy + 5 + onda_franja),
            ],
        )
        pygame.draw.line(
            tela,
            COR_CABELO_CLARO,
            (cx - 9, cy - 15),
            (cx - 10, cy + 4 + onda_franja),
            2,
        )
        pygame.draw.polygon(
            tela,
            COR_CABELO,
            [(cx - 4, cy - 16), (cx + 11, cy - 15), (cx + 8, cy - 11), (cx - 2, cy - 12)],
        )

        # Headphone retro / Walkman no pescoco/orelha
        pygame.draw.arc(tela, (70, 75, 90), (cx - 11, cy - 23, 18, 18), 0.4, 2.6, 2)
        pygame.draw.circle(tela, (50, 55, 70), (cx - 6, cy - 6), 4)
        pygame.draw.circle(tela, COR_TECH, (cx - 6, cy - 6), 2)

    def _desenhar_tenis(self, tela, x, y):
        px, py = int(x), int(y)
        pygame.draw.rect(tela, COR_TENIS, (px - 5, py - 6, 15, 5), border_radius=2)
        pygame.draw.rect(tela, COR_TENIS_DETALHE, (px - 2, py - 4, 6, 2))
        pygame.draw.rect(tela, COR_SOLA, (px - 5, py - 2, 16, 2), border_radius=1)

    def desenhar(self, tela, caido=False, escudo_ativo=False):
        cx = int(self.x) + 18
        base = int(self.y)

        altura_ar = max(0.0, CHAO_Y - self.y)
        fator_sombra = max(0.35, 1.0 - altura_ar / 150.0)
        larg_sombra = int(34 * fator_sombra)
        sombra = pygame.Surface((larg_sombra, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(
            sombra, (20, 14, 10, int(135 * fator_sombra)), (0, 0, larg_sombra, 8)
        )
        tela.blit(sombra, (cx - larg_sombra // 2, CHAO_Y - 3))

        if escudo_ativo:
            bolha = pygame.Surface((60, 64), pygame.SRCALPHA)
            pygame.draw.ellipse(bolha, (255, 220, 110, 45), (0, 0, 60, 64))
            pygame.draw.ellipse(bolha, (255, 220, 110, 140), (0, 0, 60, 64), 2)
            tela.blit(bolha, (cx - 30, base - 58))

        if self.agachado:
            pygame.draw.line(tela, COR_PELE_SOMBRA, (cx - 6, base - 7), (cx - 12, base - 3), 5)
            self._desenhar_tenis(tela, cx - 15, base)
            pygame.draw.rect(tela, COR_BERMUDAS, (cx - 12, base - 12, 18, 8), border_radius=3)
            pygame.draw.rect(tela, COR_CAMISA, (cx - 8, base - 19, 24, 11), border_radius=4)
            pygame.draw.line(tela, COR_CAMISA_DETALHE, (cx - 4, base - 14), (cx + 12, base - 14), 2)
            pygame.draw.line(tela, COR_PELE, (cx + 2, base - 7), (cx + 10, base - 3), 5)
            self._desenhar_tenis(tela, cx + 8, base)
            pygame.draw.line(tela, COR_PELE, (cx + 6, base - 14), (cx + 17, base - 9), 4)
            self._desenhar_cabeca(tela, cx + 8, base - 21, caido=caido)
            return

        fase_rad = self.corrindo * 0.75
        bob = int(abs(math.sin(fase_rad)) * 2.5) if self.no_chao else 0
        cy_corpo = base - bob
        osc = math.sin(fase_rad) if self.no_chao else 0.75
        osc_oposto = -osc

        # Braco de tras
        braco_tras_x = cx + int(osc_oposto * 9)
        braco_tras_y = cy_corpo - 18 + int(abs(osc_oposto) * 3)
        pygame.draw.line(
            tela, COR_CAMISA_SOMBRA, (cx, cy_corpo - 31), (cx + int(osc_oposto * 4), cy_corpo - 25), 5
        )
        pygame.draw.line(
            tela, COR_PELE_SOMBRA, (cx + int(osc_oposto * 4), cy_corpo - 25), (braco_tras_x, braco_tras_y), 4
        )

        # Perna de tras
        pe_tras_x = cx + int(osc * 10)
        pe_tras_y = base - (3 if osc < 0 or not self.no_chao else 0)
        joelho_tras_x = cx + int(osc * 5) + 2
        joelho_tras_y = cy_corpo - 10
        pygame.draw.line(tela, COR_BERMUDAS_SOMBRA, (cx - 2, cy_corpo - 16), (joelho_tras_x, joelho_tras_y), 6)
        pygame.draw.line(tela, COR_PELE_SOMBRA, (joelho_tras_x, joelho_tras_y), (pe_tras_x, pe_tras_y - 3), 5)
        self._desenhar_tenis(tela, pe_tras_x - 2, pe_tras_y)

        # Mochilinha tiracolo de gambiarra nas costas com antena
        pygame.draw.rect(tela, (90, 75, 55), (cx - 15, cy_corpo - 33, 7, 13), border_radius=2)
        pygame.draw.line(tela, (160, 165, 175), (cx - 13, cy_corpo - 33), (cx - 16, cy_corpo - 41), 1)
        pygame.draw.circle(tela, (90, 255, 120), (cx - 16, cy_corpo - 41), 2)

        # Bermuda e Camisa
        pygame.draw.rect(tela, COR_BERMUDAS, (cx - 9, cy_corpo - 19, 18, 9), border_radius=3)
        pygame.draw.rect(tela, COR_CAMISA, (cx - 10, cy_corpo - 35, 20, 18), border_radius=4)
        pygame.draw.rect(tela, COR_CAMISA_SOMBRA, (cx - 10, cy_corpo - 35, 5, 18), border_radius=2)
        pygame.draw.line(tela, COR_CAMISA_DETALHE, (cx - 7, cy_corpo - 26), (cx + 8, cy_corpo - 26), 2)
        pygame.draw.line(tela, COR_TENIS_DETALHE, (cx - 7, cy_corpo - 24), (cx + 8, cy_corpo - 24), 1)

        # Perna da frente
        pe_frente_x = cx + int(osc_oposto * 10)
        pe_frente_y = base - (3 if osc_oposto < 0 or not self.no_chao else 0)
        joelho_frente_x = cx + int(osc_oposto * 5) + 2
        joelho_frente_y = cy_corpo - 10
        pygame.draw.line(tela, COR_BERMUDAS, (cx + 1, cy_corpo - 16), (joelho_frente_x, joelho_frente_y), 6)
        pygame.draw.line(tela, COR_PELE, (joelho_frente_x, joelho_frente_y), (pe_frente_x, pe_frente_y - 3), 5)
        self._desenhar_tenis(tela, pe_frente_x - 2, pe_frente_y)

        # Cabeca
        self._desenhar_cabeca(tela, cx + 1, cy_corpo - 39, caido=caido)

        # Braco da frente
        ombro_x, ombro_y = cx - 1, cy_corpo - 31
        cotovelo_x = ombro_x + int(osc * 5)
        cotovelo_y = ombro_y + 7
        mao_x = cotovelo_x + int(osc * 6) + 3
        mao_y = cotovelo_y + 4 - int(max(0, osc) * 4)
        pygame.draw.line(tela, COR_CAMISA, (ombro_x, ombro_y), (cotovelo_x, cotovelo_y), 6)
        pygame.draw.line(tela, COR_PELE, (cotovelo_x, cotovelo_y), (mao_x, mao_y), 4)
        pygame.draw.circle(tela, COR_PELE, (mao_x, mao_y), 2)


class ObstaculoArvore:
    """
    Obstaculos naturais do sitio que ficam mais desafiadores conforme o nivel dos ajudantes:
    - tronco: Toco/raizes de arvore para pular
    - bananeira_alta: Touceira de planta/bananeira mais alta (aparece do nivel 1 em diante)
    - galho_mangueira: Galho baixo com folhas e cipo para agachar por baixo
    - tronco_duplo: Tronco largo caido com samambaia (nivel 2+)
    """
    def __init__(self, nivel_ajudante):
        opcoes = ["tronco", "galho_mangueira"]
        if nivel_ajudante >= 1:
            opcoes.append("bananeira_alta")
        if nivel_ajudante >= 2:
            opcoes.append("tronco_duplo")
        self.tipo = random.choice(opcoes)
        self.x = float(LARGURA + 40)

        if self.tipo == "tronco":
            self.largura = 34
            self.altura = 42
            self.y = CHAO_Y
        elif self.tipo == "bananeira_alta":
            self.largura = 36
            self.altura = 56
            self.y = CHAO_Y
        elif self.tipo == "tronco_duplo":
            self.largura = 54
            self.altura = 46
            self.y = CHAO_Y
        else:  # galho_mangueira (no alto, para agachar)
            self.largura = 54
            self.altura = 36
            self.y = CHAO_Y - 32

    def atualizar(self, velocidade):
        self.x -= velocidade

    def hitbox(self):
        return pygame.Rect(
            int(self.x) + 5, int(self.y) - self.altura + 5, self.largura - 10, self.altura - 6
        )

    def desenhar(self, tela):
        ix = int(self.x)
        iy = int(self.y)

        # Sombra no chao
        pygame.draw.ellipse(tela, (32, 22, 16), (ix, CHAO_Y - 3, self.largura, 6))

        if self.tipo == "tronco":
            # Toco de arvore com raizes e brotinho verde
            pygame.draw.polygon(
                tela,
                (92, 58, 34),
                [(ix, iy), (ix + 6, iy - self.altura), (ix + 28, iy - self.altura), (ix + 34, iy)],
            )
            pygame.draw.line(tela, (65, 38, 22), (ix + 14, iy - 4), (ix + 14, iy - self.altura + 4), 2)
            pygame.draw.line(tela, (65, 38, 22), (ix + 22, iy - 6), (ix + 20, iy - self.altura + 8), 2)
            pygame.draw.ellipse(tela, (135, 92, 56), (ix + 6, iy - self.altura - 3, 22, 7))
            # Folhinhas brotando ao lado
            pygame.draw.ellipse(tela, (75, 165, 58), (ix + 24, iy - 28, 12, 7))
            pygame.draw.ellipse(tela, (95, 185, 68), (ix - 4, iy - 20, 11, 6))

        elif self.tipo == "bananeira_alta":
            # Muda de bananeira / planta tropical alta
            pygame.draw.rect(tela, (82, 122, 48), (ix + 13, iy - 38, 10, 38), border_radius=3)
            folhas = [
                (ix - 4, iy - 46, 22, 10),
                (ix + 16, iy - 48, 22, 10),
                (ix + 6, iy - 58, 14, 22),
                (ix - 2, iy - 34, 18, 9),
                (ix + 18, iy - 34, 18, 9),
            ]
            for fx, fy, fw, fh in folhas:
                pygame.draw.ellipse(tela, (68, 152, 52), (fx, fy, fw, fh))
                pygame.draw.ellipse(tela, (98, 185, 72), (fx + 2, fy + 2, fw - 4, fh - 4))

        elif self.tipo == "tronco_duplo":
            # Dois troncos caidos com arbusto espinhoso
            pygame.draw.ellipse(tela, (48, 115, 42), (ix + 2, iy - 44, 50, 32))
            pygame.draw.ellipse(tela, (72, 148, 55), (ix + 8, iy - 48, 38, 26))
            for tx in (ix + 6, ix + 28):
                pygame.draw.rect(tela, (95, 60, 35), (tx, iy - 26, 18, 26), border_radius=4)
                pygame.draw.circle(tela, (140, 98, 62), (tx + 9, iy - 18), 6)
            # Frutinhas amarelas/vermelhas
            pygame.draw.circle(tela, (245, 190, 50), (ix + 16, iy - 36), 3)
            pygame.draw.circle(tela, (245, 90, 65), (ix + 36, iy - 38), 3)

        else:
            # Galho baixo de mangueira com folhas e mangas penduradas (para agachar!)
            topo_galho = iy - self.altura
            pygame.draw.line(
                tela, (82, 52, 32), (ix + self.largura, topo_galho - 14), (ix + 4, topo_galho + 12), 7
            )
            # Copa de folhas verdes do galho
            pygame.draw.ellipse(tela, (38, 98, 38), (ix - 4, topo_galho - 12, 62, 28))
            pygame.draw.ellipse(tela, (58, 132, 48), (ix + 2, topo_galho - 8, 50, 22))
            pygame.draw.ellipse(tela, (82, 158, 58), (ix + 10, topo_galho - 4, 34, 15))
            # Cipo e manguinha pendurada!
            pygame.draw.line(tela, (65, 115, 45), (ix + 16, topo_galho + 14), (ix + 16, iy - 2), 2)
            pygame.draw.line(tela, (65, 115, 45), (ix + 38, topo_galho + 12), (ix + 38, iy - 8), 2)
            pygame.draw.ellipse(tela, (235, 165, 45), (ix + 34, iy - 10, 8, 10))
            pygame.draw.ellipse(tela, (220, 85, 55), (ix + 35, iy - 10, 6, 5))


class Jogo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Corrida do Menino - Sitio & Gambiarra Tech")
        self.clock = pygame.time.Clock()
        self.fonte_mini = criar_fonte("consolas", 13)
        self.fonte = criar_fonte("consolas", 16)
        self.fonte_grande = criar_fonte("consolas", 30)
        self.recorde = carregar_recorde()
        self.rodando = True

        self.ceu_surf = criar_ceu_sitio()
        self.estrelas = [Estrela() for _ in range(38)]
        self.vagalumes = [Vagalume() for _ in range(18)]
        self.fundo_sitio = FundoSitio()

        # Os 3 cachorros e o jabuti Jabotao no quintal do sitio
        self.cachorros = [
            CachorroSitio("Misty", 170),
            CachorroSitio("Jabotao", 310),
            CachorroSitio("Saddam", 450),
            CachorroSitio("Shelby", 610),
        ]

        # Folhas amarelas/secas de mangueira espalhadas no chao
        self.folhas_chao = [
            (
                random.randint(0, LARGURA),
                random.randint(CHAO_Y + 6, ALTURA - 8),
                random.choice([COR_FOLHA_SECA, COR_FOLHA_MARROM, (185, 135, 42)]),
            )
            for _ in range(34)
        ]

        self.reiniciar(iniciar_jogando=False)

    def reiniciar(self, iniciar_jogando=True):
        self.pontos = 0
        self.trequinhos_total = 0
        self.velocidade = 5.0
        self.intervalo_obstaculo = 92
        self.tempo_obstaculo = 0
        self.tempo_trequinho = 35
        self.obstaculos = []
        self.trequinhos = []
        self.particulas = []
        self.menino = Menino()
        self.gatinho = GatinhoAjudante()

        # Controle dos gatinhos desbloqueados
        self.gatinhos_desbloqueados = []
        self.indice_gato_ativo = -1
        self.escudo_hanna_pronto = False
        self.contador_recarga_hanna = 0
        self.aviso_texto = ""
        self.aviso_timer = 0

        self.estado = "jogando" if iniciar_jogando else "titulo"

    def gato_ativo_info(self):
        if 0 <= self.indice_gato_ativo < len(self.gatinhos_desbloqueados):
            id_ativo = self.gatinhos_desbloqueados[self.indice_gato_ativo]
            for info in GATINHOS_INFO:
                if info["id"] == id_ativo:
                    return info
        return None

    def _mostrar_aviso(self, texto, duracao=140):
        self.aviso_texto = texto
        self.aviso_timer = duracao

    def _verificar_desbloqueio_gatinhos(self):
        for info in GATINHOS_INFO:
            if self.trequinhos_total >= info["req"] and info["id"] not in self.gatinhos_desbloqueados:
                self.gatinhos_desbloqueados.append(info["id"])
                self.indice_gato_ativo = len(self.gatinhos_desbloqueados) - 1
                if info["id"] == "hanna":
                    self.escudo_hanna_pronto = True
                    self.contador_recarga_hanna = 0
                self._mostrar_aviso(
                    f"NOVO AJUDANTE: {info['nome'].upper()} ({info['poder']})! [C/1-4 troca]",
                    duracao=180,
                )

    def _trocar_gatinho(self, indice_especifico=None):
        if not self.gatinhos_desbloqueados:
            return
        if indice_especifico is not None:
            if indice_especifico < len(self.gatinhos_desbloqueados):
                self.indice_gato_ativo = indice_especifico
            else:
                return
        else:
            self.indice_gato_ativo = (self.indice_gato_ativo + 1) % len(self.gatinhos_desbloqueados)

        info = self.gato_ativo_info()
        if info:
            self._mostrar_aviso(f"Ajudante: {info['nome']} -> {info['poder']}", duracao=100)

    def _desenhar_texto(self, texto, fonte, cor, x, y, centralizado=False):
        sombra = fonte.render(texto, True, (14, 10, 8))
        superficie = fonte.render(texto, True, cor)
        if centralizado:
            x = x - superficie.get_width() // 2
        self.tela.blit(sombra, (x + 2, y + 2))
        self.tela.blit(superficie, (x, y))

    def eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
                return
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if em_navegador():
                        # No navegador ESC nao deve fechar a aba: apenas ignora.
                        continue
                    self.rodando = False
                    return
                if self.estado == "titulo":
                    if evento.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_RETURN, pygame.K_w):
                        self.reiniciar(iniciar_jogando=True)
                elif self.estado == "jogando":
                    if evento.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        info_gato = self.gato_ativo_info()
                        bonus = 1.13 if (info_gato and info_gato["id"] == "catarino") else 1.0
                        if self.menino.pular(bonus_pulo=bonus):
                            for _ in range(5):
                                self.particulas.append(Particula(self.menino.x + 14, CHAO_Y))
                    elif evento.key in (pygame.K_c, pygame.K_TAB, pygame.K_e):
                        self._trocar_gatinho()
                    elif evento.key == pygame.K_1:
                        self._trocar_gatinho(0)
                    elif evento.key == pygame.K_2:
                        self._trocar_gatinho(1)
                    elif evento.key == pygame.K_3:
                        self._trocar_gatinho(2)
                    elif evento.key == pygame.K_4:
                        self._trocar_gatinho(3)
                elif self.estado == "game_over":
                    if evento.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                        self.reiniciar(iniciar_jogando=True)

    def _atualizar_cenario(self, vel):
        for estrela in self.estrelas:
            estrela.atualizar(vel)
        for vagalume in self.vagalumes:
            vagalume.atualizar(vel)
        self.fundo_sitio.atualizar(vel)
        for cao in self.cachorros:
            cao.atualizar(vel)
        self.folhas_chao = [
            ((fx - vel) % LARGURA, fy, cor) for (fx, fy, cor) in self.folhas_chao
        ]

    def atualizar(self):
        if self.aviso_timer > 0:
            self.aviso_timer -= 1

        if self.estado == "titulo":
            self._atualizar_cenario(2.2)
            self.menino.atualizar(2.8, False)
            self.gatinho.atualizar(self.menino.x, self.menino.y, 2.8)
            return

        if self.estado != "jogando":
            for p in self.particulas[:]:
                p.atualizar()
                if p.vida <= 0:
                    self.particulas.remove(p)
            return

        teclas = pygame.key.get_pressed()
        agachar = teclas[pygame.K_DOWN] or teclas[pygame.K_s]
        self.menino.atualizar(self.velocidade, agachar)
        self.gatinho.atualizar(self.menino.x, self.menino.y, self.velocidade)

        if self.menino.acabou_de_pousar:
            for _ in range(6):
                self.particulas.append(Particula(self.menino.x + 16, CHAO_Y))
        elif self.menino.no_chao and pygame.time.get_ticks() % 85 < 16:
            self.particulas.append(Particula(self.menino.x + 10, self.menino.y))

        self._atualizar_cenario(self.velocidade)

        for p in self.particulas[:]:
            p.atualizar()
            if p.vida <= 0:
                self.particulas.remove(p)

        info_gato = self.gato_ativo_info()
        id_gato = info_gato["id"] if info_gato else None

        # Atualiza trequinhos tecnologicos
        hit_menino = self.menino.hitbox()
        for t in self.trequinhos[:]:
            t.atualizar(self.velocidade, self.menino, ima_ativo=(id_gato == "coraline"))
            if t.x + t.largura < -10:
                self.trequinhos.remove(t)
            elif hit_menino.colliderect(t.hitbox()):
                self.trequinhos.remove(t)
                ganho = 2 if id_gato == "scar" else 1
                self.trequinhos_total += ganho
                self.pontos += 60 * ganho
                # Recarrega escudo da Hanna a cada 5 trequinhos
                if "hanna" in self.gatinhos_desbloqueados and not self.escudo_hanna_pronto:
                    self.contador_recarga_hanna += 1
                    if self.contador_recarga_hanna >= 5:
                        self.escudo_hanna_pronto = True
                        self.contador_recarga_hanna = 0
                        self._mostrar_aviso("Hanna recarregou o Escudo Salva-Vidas!", 110)

                for _ in range(7):
                    self.particulas.append(
                        Particula(t.x + 10, t.y + 8, cor=COR_TECH, nota=True)
                    )
                self._verificar_desbloqueio_gatinhos()

        # Geracao de trequinhos
        self.tempo_trequinho -= 1
        if self.tempo_trequinho <= 0:
            self.trequinhos.append(TrequinhoTech())
            self.tempo_trequinho = random.randint(65, 115)

        # Atualiza obstaculos (arvores/galhos)
        for o in self.obstaculos[:]:
            o.atualizar(self.velocidade)
            if o.x + o.largura < -10:
                self.obstaculos.remove(o)

        nivel_ajudantes = len(self.gatinhos_desbloqueados)
        self.tempo_obstaculo += 1
        if self.tempo_obstaculo >= self.intervalo_obstaculo:
            self.obstaculos.append(ObstaculoArvore(nivel_ajudantes))
            self.tempo_obstaculo = 0
            # Dificuldade sobe gradualmente e acompanha o nivel dos ajudantes
            alvo_min = max(42, 74 - nivel_ajudantes * 7)
            self.intervalo_obstaculo = max(alvo_min, self.intervalo_obstaculo - 2)
            self.velocidade = min(10.5, 5.0 + nivel_ajudantes * 0.65 + self.pontos * 0.0012)

        self.pontos += 1

        # Colisao com obstaculos (Hanna pode salvar o menino!)
        for o in self.obstaculos[:]:
            if hit_menino.colliderect(o.hitbox()):
                if id_gato == "hanna" and self.escudo_hanna_pronto:
                    self.escudo_hanna_pronto = False
                    self.contador_recarga_hanna = 0
                    self.obstaculos.remove(o)
                    for _ in range(12):
                        self.particulas.append(
                            Particula(o.x + 16, o.y - 20, cor=(255, 210, 110))
                        )
                    self._mostrar_aviso("MIAU! Hanna quebrou o obstaculo e te salvou!", 130)
                    continue

                if self.pontos > self.recorde:
                    self.recorde = self.pontos
                    salvar_recorde(self.recorde)
                self.estado = "game_over"
                break

    def _desenhar_chao(self):
        pygame.draw.rect(self.tela, COR_TERRA, (0, CHAO_Y, LARGURA, ALTURA - CHAO_Y))
        pygame.draw.rect(
            self.tela, COR_TERRA_ESCURA, (0, CHAO_Y + 28, LARGURA, ALTURA - CHAO_Y - 28)
        )
        pygame.draw.line(self.tela, COR_GRAMA, (0, CHAO_Y + 2), (LARGURA, CHAO_Y + 2), 4)
        pygame.draw.line(self.tela, COR_GRAMA_CLARA, (0, CHAO_Y), (LARGURA, CHAO_Y), 2)

        # Folhas amarelas de mangueira no chao do sitio
        for fx, fy, cor in self.folhas_chao:
            pygame.draw.ellipse(self.tela, cor, (int(fx), fy, 6, 3))

    def _desenhar_hud(self):
        # Placar superior
        self._desenhar_texto(f"PONTOS {self.pontos:04d}", self.fonte, COR_PONTOS, 12, 8)
        self._desenhar_texto(
            f"TREQUINHOS {self.trequinhos_total:02d}", self.fonte, COR_TECH, 165, 8
        )
        self._desenhar_texto(
            f"RECORDE {self.recorde:04d}", self.fonte, COR_RECORDE, LARGURA - 138, 8
        )

        # Barra de Gatinhos Ajudantes no topo
        info_ativo = self.gato_ativo_info()
        x_card = 12
        y_card = 30
        for idx, g in enumerate(GATINHOS_INFO):
            desbloq = g["id"] in self.gatinhos_desbloqueados
            ativo = info_ativo and info_ativo["id"] == g["id"]
            larg = 118
            alt = 20
            surf = pygame.Surface((larg, alt), pygame.SRCALPHA)
            if ativo:
                pygame.draw.rect(surf, (25, 45, 38, 220), (0, 0, larg, alt), border_radius=5)
                pygame.draw.rect(surf, g["cor_tag"], (0, 0, larg, alt), 2, border_radius=5)
                label = f"[{idx+1}]{g['nome']}*"
                cor_txt = g["cor_tag"]
            elif desbloq:
                pygame.draw.rect(surf, (20, 24, 34, 180), (0, 0, larg, alt), border_radius=5)
                pygame.draw.rect(surf, (110, 120, 140), (0, 0, larg, alt), 1, border_radius=5)
                label = f"[{idx+1}]{g['nome']}"
                cor_txt = (200, 205, 215)
            else:
                pygame.draw.rect(surf, (15, 15, 22, 140), (0, 0, larg, alt), border_radius=5)
                label = f"{g['nome']} ({g['req']}T)"
                cor_txt = (115, 115, 130)

            self.tela.blit(surf, (x_card, y_card))
            txt = self.fonte_mini.render(label, True, cor_txt)
            self.tela.blit(txt, (x_card + 6, y_card + 3))
            x_card += larg + 6

        if info_ativo:
            extra = ""
            if info_ativo["id"] == "hanna":
                extra = " [ESCUDO PRONTO!]" if self.escudo_hanna_pronto else f" [Recarga {self.contador_recarga_hanna}/5]"
            dica_poder = f"Ajudante: {info_ativo['nome']} - {info_ativo['poder']}{extra} (Tecla C troca)"
            self._desenhar_texto(dica_poder, self.fonte_mini, info_ativo["cor_tag"], 14, 53)

        if self.aviso_timer > 0 and self.aviso_texto:
            painel_aviso = pygame.Surface((480, 24), pygame.SRCALPHA)
            pygame.draw.rect(painel_aviso, (16, 22, 34, 210), (0, 0, 480, 24), border_radius=6)
            self.tela.blit(painel_aviso, (LARGURA // 2 - 240, 72))
            self._desenhar_texto(
                self.aviso_texto, self.fonte_mini, COR_RECORDE, LARGURA // 2, 76, centralizado=True
            )

    def desenhar(self):
        self.tela.blit(self.ceu_surf, (0, 0))
        for estrela in self.estrelas:
            estrela.desenhar(self.tela)
        self.fundo_sitio.desenhar(self.tela)

        # Cachorros passeando no quintal do sitio
        for cao in self.cachorros:
            cao.desenhar(self.tela, self.fonte_mini)

        for vagalume in self.vagalumes:
            vagalume.desenhar(self.tela)

        self._desenhar_chao()

        for t in self.trequinhos:
            t.desenhar(self.tela)
        for o in self.obstaculos:
            o.desenhar(self.tela)
        for p in self.particulas:
            p.desenhar(self.tela)

        info_ativo = self.gato_ativo_info()
        id_gato = info_ativo["id"] if info_ativo else ("catarino" if self.estado == "titulo" else None)
        escudo_visivel = (id_gato == "hanna" and self.escudo_hanna_pronto)

        self.gatinho.desenhar(self.tela, id_gato, escudo_pronto=escudo_visivel)
        self.menino.desenhar(
            self.tela, caido=(self.estado == "game_over"), escudo_ativo=escudo_visivel
        )

        self._desenhar_hud()

        if self.estado == "titulo":
            painel = pygame.Surface((470, 165), pygame.SRCALPHA)
            pygame.draw.rect(painel, (16, 24, 28, 210), (0, 0, 470, 165), border_radius=12)
            pygame.draw.rect(painel, COR_TECH, (0, 0, 470, 165), 2, border_radius=12)
            self.tela.blit(painel, (LARGURA // 2 - 235, 62))

            self._desenhar_texto(
                "CORRIDA DO MENINO", self.fonte_grande, COR_TEXTO, LARGURA // 2, 76, centralizado=True
            )
            self._desenhar_texto(
                "AVENTURA NO SITIO & GAMBIARRA TECH",
                self.fonte,
                COR_RECORDE,
                LARGURA // 2,
                114,
                centralizado=True,
            )
            self._desenhar_texto(
                "Pegue MP3 e Cyberdecks para chamar Catarino, Coraline, Hanna e Scar!",
                self.fonte_mini,
                COR_TECH,
                LARGURA // 2,
                142,
                centralizado=True,
            )
            if (pygame.time.get_ticks() // 450) % 2 == 0:
                self._desenhar_texto(
                    "ESPACO PARA COMECAR", self.fonte, COR_PONTOS, LARGURA // 2, 188, centralizado=True
                )

        elif self.estado == "game_over":
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((10, 12, 18, 165))
            self.tela.blit(overlay, (0, 0))

            painel = pygame.Surface((400, 190), pygame.SRCALPHA)
            pygame.draw.rect(painel, (20, 24, 34, 230), (0, 0, 400, 190), border_radius=12)
            pygame.draw.rect(painel, COR_ALERTA, (0, 0, 400, 190), 2, border_radius=12)
            self.tela.blit(painel, (LARGURA // 2 - 200, 78))

            self._desenhar_texto(
                "OPS! TROPECOU NO SITIO!", self.fonte, COR_ALERTA, LARGURA // 2, 94, centralizado=True
            )
            self._desenhar_texto(
                f"PONTOS: {self.pontos}   |   TREQUINHOS: {self.trequinhos_total}",
                self.fonte,
                COR_TEXTO,
                LARGURA // 2,
                132,
                centralizado=True,
            )
            self._desenhar_texto(
                f"GATINHOS NA EQUIPE: {len(self.gatinhos_desbloqueados)}/4",
                self.fonte_mini,
                COR_TECH,
                LARGURA // 2,
                160,
                centralizado=True,
            )
            self._desenhar_texto(
                f"RECORDE: {self.recorde}", self.fonte, COR_RECORDE, LARGURA // 2, 184, centralizado=True
            )
            self._desenhar_texto(
                "R OU ESPACO PARA RECOMECAR", self.fonte, COR_PONTOS, LARGURA // 2, 224, centralizado=True
            )

        pygame.display.flip()

    def executar(self):
        while self.rodando:
            self.eventos()
            self.atualizar()
            self.desenhar()
            self.clock.tick(FPS)
        pygame.quit()

    async def executar_async(self):
        """Loop usado no navegador (Pygbag/WASM).

        O `clock.tick(FPS)` antes do `await asyncio.sleep(0)` e o padrao
        recomendado pelo Pygbag: ele limita o jogo a 60 quadros por segundo
        mesmo em monitores de 120/144 Hz.
        """
        while self.rodando:
            self.eventos()
            self.atualizar()
            self.desenhar()
            self.clock.tick(FPS)
            await asyncio.sleep(0)
        pygame.quit()


def main():
    Jogo().executar()


if __name__ == "__main__":
    main()
