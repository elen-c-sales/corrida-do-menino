"""Gera GIFs de demonstracao do Corrida do Menino sem abrir janela.

O script usa o modo "dummy" do SDL, joga sozinho (autopiloto) e monta o GIF
com o Pillow. O recorde do jogador nunca e alterado.

Exemplos:
    python tools/captura_gif.py
    python tools/captura_gif.py --escala 480x270 --saida captura-480.gif
    python tools/captura_gif.py --sim
    python tools/captura_gif.py --seed 10 --duracao 12
"""
import argparse
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pygame
from PIL import Image

import corrida

corrida.salvar_recorde = lambda valor: None  # preserva o recorde do jogador

FPS = corrida.FPS
PASSO = FPS // 20  # o GIF roda a 20 fps


class TeclasFalsas:
    """Estado de teclado usado por pygame.key.get_pressed() durante a demo."""

    def __init__(self):
        self.agachar = False

    def __getitem__(self, tecla):
        if tecla in (pygame.K_DOWN, pygame.K_s):
            return self.agachar
        return False


teclas = TeclasFalsas()
pygame.key.get_pressed = lambda: teclas


def postar_tecla(key):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))


def decidir(jogo):
    """Autopiloto: pula obstaculos, agacha em galhos e calcula saltos p/ trequinhos."""
    if jogo.estado != "jogando":
        return False, False

    m = jogo.menino
    vel = max(1.0, jogo.velocidade)
    pular = False
    agachar = False

    for o in jogo.obstaculos:
        d = o.x - m.x
        if o.tipo == "galho_mangueira":
            if -80 < d < 100 + vel * 2:
                agachar = True
        elif 0 < d < 30 + vel * 19 and m.no_chao:
            pular = True

    if not pular and not agachar and m.no_chao:
        for t in jogo.trequinhos:
            d = t.x - m.x
            if d < 0:
                continue
            queda = corrida.CHAO_Y - t.y
            quadros_ate = d / vel
            if queda > 95:  # item alto: pular antes
                if 7 <= quadros_ate <= 11:
                    pular = True
                    break
            elif queda > 70:  # item na altura media: pular em cima da hora
                if 2 <= quadros_ate <= 5:
                    pular = True
                    break

    return pular, agachar


def novo_jogo(seed):
    random.seed(seed)
    return corrida.Jogo()


def redimensionar(img, escala):
    if escala == (corrida.LARGURA, corrida.ALTURA):
        return img
    return img.resize(escala, Image.LANCZOS)


def rodar(jogo, escala, capturar=False, quadros_jogo=0, titulo_segundos=0.0):
    """Roda a demo; devolve (quadros, info)."""
    quadros = []
    frame_total = 0

    if titulo_segundos > 0:
        quadros_titulo = int(titulo_segundos * FPS)
        for i in range(quadros_titulo):
            if i == quadros_titulo - int(0.5 * FPS):
                postar_tecla(pygame.K_SPACE)
            jogo.eventos()
            jogo.atualizar()
            if capturar:
                jogo.desenhar()
                if i % PASSO == 0:
                    dados = pygame.image.tobytes(jogo.tela, "RGB")
                    img = Image.frombytes("RGB", (corrida.LARGURA, corrida.ALTURA), dados)
                    quadros.append(redimensionar(img, escala))
        frame_total += quadros_titulo

    frame = 0
    fim_timer = 0
    while True:
        jogando = jogo.estado == "jogando"
        if jogando and frame < quadros_jogo:
            pular, agachar = decidir(jogo)
            teclas.agachar = agachar
            if pular and jogo.menino.no_chao:
                postar_tecla(pygame.K_UP)
        else:
            teclas.agachar = False

        jogo.eventos()
        jogo.atualizar()
        if capturar:
            jogo.desenhar()
            if frame % PASSO == 0:
                dados = pygame.image.tobytes(jogo.tela, "RGB")
                img = Image.frombytes("RGB", (corrida.LARGURA, corrida.ALTURA), dados)
                quadros.append(redimensionar(img, escala))

        if jogo.estado == "game_over":
            fim_timer += 1
            if fim_timer > 60 or not capturar:
                break
        elif frame >= quadros_jogo + 180:
            break

        frame += 1

    return quadros, {
        "pontos": jogo.pontos,
        "trequinhos": jogo.trequinhos_total,
        "gatos": len(jogo.gatinhos_desbloqueados),
        "estado": jogo.estado,
        "quadros": frame + frame_total,
    }


def simular(duracao):
    jogo = corrida.Jogo()
    resultados = []
    for seed in range(1, 31):
        random.seed(seed)
        jogo.reiniciar(iniciar_jogando=True)
        _, info = rodar(jogo, (corrida.LARGURA, corrida.ALTURA), quadros_jogo=int(duracao * FPS))
        info["seed"] = seed
        resultados.append(info)
        print(
            f"seed {seed:2d}: pontos {info['pontos']:4d}  trequinhos {info['trequinhos']:2d}  "
            f"gatos {info['gatos']}  estado {info['estado']}"
        )

    resultados.sort(
        key=lambda r: (r["estado"] == "game_over", r["trequinhos"], r["pontos"]),
        reverse=True,
    )
    print("\nMelhores:")
    for r in resultados[:5]:
        print(r)


def capturar(seed, escala, saida, cores, duracao, titulo):
    jogo = novo_jogo(seed)
    quadros, info = rodar(
        jogo,
        escala,
        capturar=True,
        quadros_jogo=int(duracao * FPS),
        titulo_segundos=titulo,
    )
    print("Resultado:", info)
    if not quadros:
        raise SystemExit("Nenhum quadro capturado")

    base = quadros[0].quantize(colors=cores, method=Image.MEDIANCUT)
    quantizados = [base] + [f.quantize(palette=base, dither=Image.NONE) for f in quadros[1:]]
    destino = saida if saida.is_absolute() else RAIZ / saida
    quantizados[0].save(
        destino,
        save_all=True,
        append_images=quantizados[1:],
        duration=int(1000 / 20),
        loop=0,
        optimize=True,
        disposal=1,
    )
    print("GIF salvo em", destino, os.path.getsize(destino) // 1024, "KB")
    return destino


def analisar_escala(texto):
    try:
        largura, altura = texto.lower().split("x")
        return int(largura), int(altura)
    except ValueError as erro:
        raise argparse.ArgumentTypeError("Use o formato LARGURAxALTURA, ex.: 640x360") from erro


def main():
    parser = argparse.ArgumentParser(description="Gera um GIF de demonstracao do jogo.")
    parser.add_argument("--sim", action="store_true", help="testa sementes e ranqueia as melhores")
    parser.add_argument("--seed", type=int, default=4, help="semente da partida (padrao: 4)")
    parser.add_argument("--escala", type=analisar_escala, default="640x360")
    parser.add_argument("--saida", default="captura.gif", help="caminho do GIF gerado")
    parser.add_argument("--cores", type=int, default=128, help="cores da paleta do GIF")
    parser.add_argument("--duracao", type=float, default=8.5, help="segundos de gameplay")
    parser.add_argument("--titulo", type=float, default=1.6, help="segundos da tela de titulo")
    args = parser.parse_args()

    if args.sim:
        simular(args.duracao)
    else:
        capturar(args.seed, args.escala, Path(args.saida), args.cores, args.duracao, args.titulo)
    pygame.quit()


if __name__ == "__main__":
    main()
