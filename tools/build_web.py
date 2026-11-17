"""Gera a versao web do Corrida do Menino com Pygbag.

Uso:
    python tools/build_web.py            # gera build/web/
    python tools/build_web.py --serve    # gera e abre o servidor local do Pygbag

Requisitos: `pip install -r requirements-web.txt`.
"""
import argparse
import functools
import http.server
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA_BUILD = RAIZ / "build" / "web"

# O template padrao do Pygbag nao foca o canvas automaticamente; sem isso, as
# teclas so passam a funcionar depois que o jogador clica na tela. Tambem
# trocamos o visual da tela de carregamento pelo tema noturno do sitio.
AJUSTES_HTML = """
    <style>
        :root {
            /* Ajuste este valor para deixar a tela do jogo maior ou menor. */
            --largura-max-jogo: 960px;
        }
        html, body {
            background-color: #0e162a !important;
        }
        body {
            background-image: radial-gradient(circle at 50% 35%, #1a2740 0%, #0e162a 55%, #070c16 100%) !important;
            background-attachment: fixed;
            margin: 0;
        }
        /* O Pygbag estica o canvas para a janela inteira. Aqui limitamos o
           tamanho, mantemos os 16:9 e deixamos a tela centralizada. */
        canvas.emscripten#canvas {
            --jogo-largura: min(94vw, var(--largura-max-jogo), calc(88vh * 16 / 9));
            width: var(--jogo-largura) !important;
            height: calc(var(--jogo-largura) * 9 / 16) !important;
            border: 2px solid #2f5a7a;
            border-radius: 10px;
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.65), 0 0 45px rgba(80, 235, 255, 0.12);
            background-color: #0e162a;
        }
        #infobox {
            background: #101a2e;
            color: #7df0af;
            border: 2px solid #50ebff;
            border-radius: 8px;
            font-family: Consolas, "DejaVu Sans Mono", monospace;
            padding: 12px 24px;
        }
    </style>
    <script>
        (function () {
            function focarCanvas() {
                var canvas = document.getElementById("canvas");
                var ativo = document.activeElement;
                if (canvas && (!ativo || ativo === document.body)) {
                    canvas.focus({ preventScroll: true });
                }
            }
            window.addEventListener("load", function () { setTimeout(focarCanvas, 0); });
            document.addEventListener("pointerdown", focarCanvas, { passive: true });
            var timer = setInterval(focarCanvas, 1000);
            setTimeout(function () { clearInterval(timer); }, 15000);
        })();
    </script>
"""


def personalizar_index():
    """Acrescenta foco de teclado e tema visual ao index.html gerado."""
    caminho = PASTA_BUILD / "index.html"
    html = caminho.read_text(encoding="utf-8")
    if "corrida-do-menino:ajustes" in html:
        return
    extras = AJUSTES_HTML.replace("<script>", '<script id="corrida-do-menino:ajustes">', 1)
    html = html.replace("</body>", extras + "\n</body>")
    caminho.write_text(html, encoding="utf-8")


def pygbag_disponivel():
    try:
        __import__("pygbag")
        return True
    except ImportError:
        return False


def limpar_build():
    """Remove apenas o resultado publicado, preservando o cache do CDN."""
    if PASTA_BUILD.is_dir():
        shutil.rmtree(PASTA_BUILD)
    PASTA_BUILD.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Gera a versao web do jogo com Pygbag.")
    parser.add_argument(
        "--serve",
        action="store_true",
        help="serve o build localmente em http://127.0.0.1:8080 apos gerar",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="porta do servidor local usado com --serve (padrao: 8080)",
    )
    args = parser.parse_args()

    if not pygbag_disponivel():
        print(
            "Pygbag nao encontrado. Instale as dependencias da versao web com:\n"
            "    pip install -r requirements-web.txt",
            file=sys.stderr,
        )
        return 1

    limpar_build()

    comando = [
        sys.executable,
        "-m",
        "pygbag",
        "--build",
        "--width",
        "640",
        "--height",
        "360",
        "--title",
        "Corrida do Menino",
        "--app_name",
        "Corrida do Menino",
        "--package",
        "corrida-do-menino",
        # O jogo nao usa audio: nao espera o clique de "media engagement".
        "--ume_block",
        "0",
        ".",
    ]

    print("Gerando versao web em", PASTA_BUILD)
    resultado = subprocess.run(comando, cwd=RAIZ)
    if resultado.returncode != 0:
        return resultado.returncode

    if not (PASTA_BUILD / "index.html").is_file():
        print("Build concluido, mas build/web/index.html nao foi gerado.", file=sys.stderr)
        return 1

    personalizar_index()

    print("\nPronto! Arquivos gerados em:", PASTA_BUILD)
    if args.serve:
        endereco = ("127.0.0.1", args.port)
        handler = functools.partial(
            http.server.SimpleHTTPRequestHandler, directory=str(PASTA_BUILD)
        )
        servidor = http.server.ThreadingHTTPServer(endereco, handler)
        print(f"Servindo em http://127.0.0.1:{args.port}/ (Ctrl+C para sair)")
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")
        finally:
            servidor.server_close()
    else:
        print("Para testar localmente:")
        print(f"    python -m http.server {args.port} --directory build/web")
        print(f"Depois abra http://127.0.0.1:{args.port}/")
        print(
            "Evite a porta 8000: o Pygbag a reserva para o proxy de desenvolvimento "
            "e o jogo tentaria buscar as dependencias nela."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
