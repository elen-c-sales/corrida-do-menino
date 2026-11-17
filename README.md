# Corrida do Menino

Versão para computador do jogo criado para o R36S com TreeFrogUI.

O personagem é um menino com cabelo comprido castanho, camisa clara, bermuda e tênis. O jogo tem parallax de profundidade com várias camadas, obstáculos, pontuação e recorde salvo em arquivo.

Este repositório é a versão desktop, feita para testar a mecânica aqui no computador antes de levar o cartucho PICO-8 para o portátil.

## Como jogar

Requisitos:

- Python 3.7 ou superior
- pygame 2.0 ou superior

Instalação do pygame:

```
pip install pygame
```

Execução:

```
python corrida.py
```

## Controles

- ESPAÇO ou SETA PARA CIMA: pular
- SETA PARA BAIXO: agachar
- R: recomeçar após o game over
- ESC: sair

## Arquivos

- corrida.py: código principal do jogo
- recorde.txt: arquivo onde o recorde é salvo automaticamente
- README.md: este arquivo

## Versão para o portátil

A versão PICO-8 está em `C:\Users\usuario\dev\r36s\roms\pico8\dino.p8` e deve ser copiada para `roms/pico8/` no cartão com o TreeFrogUI instalado.
