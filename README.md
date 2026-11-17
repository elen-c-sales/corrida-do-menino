# Corrida do Menino

Jogo de corrida infinita em 2D desenvolvido em Python com Pygame, concebido como versão de computador e bancada de testes para o console portátil R36S (via PICO-8 e TreeFrogUI).

O projeto retrata o cotidiano e o imaginário de Sauron no sítio da família no estado do Pará, reunindo vegetação amazônica e de quintal, aparelhos de tecnologia retrô e gambiarra eletrônica, além dos animais da casa.

## Dedicatória

Este jogo é dedicado ao querido filho Sauron e aos nossos amados filhotes: Misty, Saddam, Shelby, Catarino, Coraline, Hanna, Scar e Jabotão.

## Ambientação e Mecânica

O protagonista é Sauron, representado como um menino de cabelo comprido castanho que ondula com o movimento da corrida, usando fones de ouvido antigos no pescoço e uma bolsa tiracolo com antena de rádio nas costas.

A partida acontece no quintal do sítio ao entardecer. Ao fundo, aparecem mangueiras frondosas, o muro de tijolinhos da propriedade, touceiras de bananeiras com folhas verdes e secas, vaga-lumes e folhas amarelas caídas sobre a terra batida.

Enquanto corre pelo terreno, os moradores do quintal acompanham a movimentação em segundo plano:

* **Misty**: cadela de porte grande, pelagem branca com cabeça preta, ponta do focinho branca e manchas pretas no dorso.
* **Shelby**: cachorro de porte grande e musculoso, pelagem ruiva avermelhada (red nose), focinho rosado e olhos cor de mel.
* **Saddam**: cachorro de porte mais baixo e robusto, pelagem caramelo dourada com peito branco e língua à mostra.
* **Jabotão**: jabuti amazônico de casco abaulado escuro com placas geométricas amarelo-ocre e escamas alaranjadas nas patas, caminhando no seu próprio ritmo pelo terreno.

### Prêmios Tecnológicos (Trequinhos)

Pelo caminho surgem dispositivos eletrônicos antigos e peças de bancada flutuando em diferentes alturas. O jogador deve saltar para coletar:

1. **Aparelhos MP3**: reprodutores portáteis clássicos com visor LCD iluminado e fone de ouvido.
2. **Cyberdecks**: terminais portáteis montados artesanalmente com tela de fósforo verde, teclado compacto colorido e antena com LED.
3. **Fitas Cassete**: mídias magnéticas clássicas de áudio.
4. **Placas de Circuito**: placas verdes perfuradas com trilhas metálicas, microcontrolador e LED indicador.

### Sistema de Ajudantes (Gatinhos) e Progressão de Dificuldade

À medida que o jogador acumula trequinhos tecnológicos durante a partida, os quatro gatos da família são recrutados como ajudantes. Cada novo ajudante desbloqueado eleva o nível da corrida, introduzindo obstáculos naturais mais complexos no terreno:

1. **Catarino** (desbloqueado com 3 trequinhos): gato branco de olhos azuis e orelhas rosadas, mais jovem e de corpo comprido. Concede impulso extra nos saltos, facilitando a passagem por mudas altas de bananeira.
2. **Coraline** (desbloqueada com 7 trequinhos): gata frajola preta e branca de olhos verdes e corpo magro. Ativa um campo magnético que atrai os trequinhos tecnológicos próximos automaticamente.
3. **Hanna** (desbloqueada com 12 trequinhos): gata branca e gordinha com capuz e manchas redondas rajadas nas costas. Cria um escudo protetor capaz de quebrar um obstáculo caso o jogador tropece. O escudo é recarregado a cada 5 trequinhos coletados.
4. **Scar** (desbloqueado com 18 trequinhos): gato grande e gordinho, com manto rajado nas costas e peito e focinho brancos. Multiplica por dois a contagem de trequinhos coletados e dobra a pontuação de cada item.

O jogador pode alternar livremente entre os gatos já desbloqueados durante a corrida para adaptar a habilidade ativa ao tipo de obstáculo que se aproxima (tocos com raízes, galhos baixos de mangueira com mangas e cipós que exigem agachamento, bananeiras altas e troncos duplos caídos).

## Requisitos e Instalação

* Python 3.7 ou superior
* Biblioteca Pygame 2.0 ou superior

Para instalar a dependência necessária, execute no terminal:

```bash
pip install pygame
```

Para iniciar o jogo:

```bash
python corrida.py
```

## Controles

* **ESPAÇO**, **SETA PARA CIMA** ou **W**: pular
* **SETA PARA BAIXO** ou **S**: agachar (para passar sob galhos de mangueira) ou acelerar a descida durante o pulo
* **C**, **TAB** ou **E**: alternar entre os gatinhos ajudantes desbloqueados
* **1**, **2**, **3**, **4**: selecionar diretamente Catarino, Coraline, Hanna ou Scar (quando desbloqueados)
* **R** ou **ESPAÇO**: reiniciar a partida na tela de fim de jogo
* **ESC**: encerrar o programa

## Estrutura do Repositório

* `corrida.py`: código-fonte completo do jogo, incluindo renderização procedural em pixel art, física, sistema de partículas e lógica de progressão.
* `recorde.txt`: arquivo de texto gerado e atualizado automaticamente para armazenar a maior pontuação atingida.
* `README.md`: documentação geral do projeto.
* `LICENSE`: texto integral da licença livre MIT.

## Integração com o Portátil R36S

A edição correspondente para o sistema PICO-8 localiza-se em `C:\Users\usuario\dev\r36s\roms\pico8\dino.p8` e deve ser copiada para o diretório `roms/pico8/` no cartão de memória com o ambiente TreeFrogUI configurado.

## Licença

Este projeto é distribuído sob a Licença MIT (software livre e de código aberto). Você tem liberdade para usar, copiar, modificar, mesclar, publicar e distribuir este código. Consulte o arquivo `LICENSE` para ler os termos completos.
