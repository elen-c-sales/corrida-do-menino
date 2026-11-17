"""Ponto de entrada da versao web do Corrida do Menino (Pygbag/WASM).

O jogo continua sendo o mesmo `corrida.py` da versao desktop: aqui apenas
iniciamos o loop assincrono exigido pelo Pygbag. Para a versao desktop use
`python corrida.py`.

Build local:
    python tools/build_web.py

O resultado fica em `build/web/`.
"""
import asyncio

import pygame  # noqa: F401  # o Pygbag detecta dependencias pelo import direto aqui

import corrida


async def main():
    jogo = corrida.Jogo()
    await jogo.executar_async()


if __name__ == "__main__":
    asyncio.run(main())
