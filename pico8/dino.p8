pico-8 cartridge // http://www.pico-8.com
version 41
__lua__

-- CORRIDA DO MENINO: AVENTURA NO SITIO
-- Versao PICO-8 para R36S / TreeFrogUI
-- Baseada na versao pygame de Sauron (cabelo comprido, fones, bolsa)
-- Cenario: sitio no Para ao entardecer, cachorros, gatinhos e trequinhos

local W = 128
local H = 128
local CHAO = 104
local G = 0.42
local PULO_VEL = -5.4

-- paleta
local C_CEU1 = 1
local C_CEU2 = 2
local C_CEU3 = 8
local C_LUA = 10
local C_MATA1 = 3
local C_MATA2 = 5
local C_MURO = 4
local C_TERRA = 4
local C_FOLHA = 9
local C_CABELO = 4
local C_PELE = 14
local C_CAMISA = 12
local C_BERMUDAS = 1
local C_TENIS = 7
local C_FONE = 5
local C_OLHO = 0
local C_TECH = 11
local C_PERIGO = 8
local C_TEXTO = 7
local C_VAGA = 10

-- estado
local estado = "titulo"
local pontos = 0
local recorde = 0
local techs = 0
local vel = 1.2
local intervalo = 70
local t_obs = 0
local t_tech = 0
local gatos_desbloq = {}
local gato_idx = 0
local escudo_pronto = false
local aviso = ""
local aviso_t = 0

local estrelas = {}
local folhas = {}
local vagalumes = {}
local menino = {}
local obstaculos = {}
local coletaveis = {}
local particulas = {}
local cachorros = {}
local frame = 0

local GATOS = {
  { id="catarino", nome="CATARINO", req=3,  poder="PULO ALTO" },
  { id="coraline", nome="CORALINE", req=7,  poder="IMA TECH" },
  { id="hanna",    nome="HANNA",    req=12, poder="ESCUDO" },
  { id="scar",     nome="SCAR",     req=18, poder="TECH X2" }
}

function _init()
  recorde = dget(0) or 0
  iniciar_cenario()
  iniciar_menino()
  estado = "titulo"
end

function iniciar_cenario()
  estrelas = {}
  for i = 1, 30 do
    add(estrelas, { x=rnd(W), y=rnd(60), p=0.1+rnd(0.5) })
  end
  folhas = {}
  for i = 1, 14 do
    add(folhas, { x=rnd(W), y=CHAO+rnd(20), v=0.2+rnd(0.5), c=rnd(1)<0.5 and 9 or 4 })
  end
  vagalumes = {}
  for i = 1, 10 do
    add(vagalumes, { x=rnd(W), y=60+rnd(40), f=rnd(6.28) })
  end
  cachorros = {
    { tipo=1, x=rnd(W), nome="MISTY" },
    { tipo=2, x=rnd(W), nome="SHELBY" },
    { tipo=3, x=rnd(W), nome="SADDAM" },
    { tipo=4, x=rnd(W), nome="JABOTAO" }
  }
end

function iniciar_menino()
  menino = { x=20, y=CHAO, vy=0, chao=true, agachado=false, passo=0, piscar=0 }
end

function reiniciar()
  pontos = 0
  techs = 0
  vel = 1.2
  intervalo = 70
  t_obs = 0
  t_tech = 0
  gatos_desbloq = {}
  gato_idx = 0
  escudo_pronto = false
  aviso = ""
  aviso_t = 0
  obstaculos = {}
  coletaveis = {}
  particulas = {}
  iniciar_cenario()
  iniciar_menino()
  estado = "jogando"
end

function gato_ativo()
  if gato_idx < 1 or gato_idx > #gatos_desbloq then return "" end
  return gatos_desbloq[gato_idx]
end

function verificar_desbloqueios()
  for g in all(GATOS) do
    if techs >= g.req then
      local ja = false
      for d in all(gatos_desbloq) do
        if d == g.id then ja = true end
      end
      if not ja then
        add(gatos_desbloq, g.id)
        gato_idx = #gatos_desbloq
        aviso = g.nome .. " NA EQUIPE"
        aviso_t = 90
      end
    end
  end
end

function alternar_gato()
  if #gatos_desbloq == 0 then return end
  gato_idx = (gato_idx % #gatos_desbloq) + 1
  aviso = GATOS[gato_idx].nome
  aviso_t = 60
end

function spawn_obstaculo()
  local tipo = flr(rnd(3))
  if tipo == 0 then
    add(obstaculos, { t="toco", x=W+8, alt=8 })
  elseif tipo == 1 then
    add(obstaculos, { t="galho", x=W+8, alt=10 })
  else
    add(obstaculos, { t="banana", x=W+8, alt=17 })
  end
end

function spawn_trequinho()
  local tipos = {"mp3", "cyber", "fita", "placa"}
  local t = tipos[flr(rnd(#tipos))+1]
  add(coletaveis, {
    t=t,
    x=W+8,
    y=58+flr(rnd(34)),
    p=0
  })
end

function estourar(x, y, cor, n)
  for i = 1, n do
    local a = rnd(6.28)
    local v = 0.3+rnd(0.9)
    add(particulas, {
      x=x, y=y,
      vx=math.cos(a)*v,
      vy=math.sin(a)*v,
      vida=12+flr(rnd(10)),
      c=cor
    })
  end
end

function pular()
  local forca = PULO_VEL
  if gato_ativo() == "catarino" then forca = PULO_VEL*1.25 end
  if menino.chao and not menino.agachado then
    menino.vy = forca
    menino.chao = false
  end
end

function atualizar_jogo()
  if btnp(4) or btnp(2) then pular() end
  if btnp(5) then alternar_gato() end
  menino.agachado = btn(3) and menino.chao

  menino.vy += G
  menino.y += menino.vy
  if not menino.chao and btn(3) and menino.vy < 0 then
    menino.vy += G*0.8
  end
  if menino.y >= CHAO then
    menino.y = CHAO
    menino.vy = 0
    menino.chao = true
  end
  menino.passo += vel*0.14
  if menino.piscar > 0 then menino.piscar -= 1 end

  for s in all(estrelas) do
    s.x -= vel*s.p*0.2
    if s.x < 0 then s.x += W end
  end
  for f in all(folhas) do
    f.x -= vel*f.v
    if f.x < 0 then f.x += W; f.y = CHAO+rnd(20) end
  end
  for v in all(vagalumes) do
    v.f += 0.05
    v.x -= vel*0.15
    if v.x < 0 then v.x += W end
  end
  for c in all(cachorros) do
    c.x -= vel*0.25
    if c.x < -10 then c.x += W+20 end
  end

  for p in all(particulas) do
    p.x += p.vx
    p.y += p.vy
    p.vida -= 1
    if p.vida <= 0 then del(particulas, p) end
  end

  for o in all(obstaculos) do
    o.x -= vel
    if o.x < -16 then del(obstaculos, o) end
  end

  for c in all(coletaveis) do
    c.x -= vel
    c.p += 0.08
    if gato_ativo() == "coraline" and c.x < menino.x+36 and c.x > menino.x then
      c.y += (menino.y-10-c.y)*0.05
    end
    if c.x < -10 then del(coletaveis, c) end
  end

  t_obs += 1
  if t_obs >= intervalo then
    spawn_obstaculo()
    t_obs = 0
    vel += 0.015
    intervalo = max(36, intervalo-1)
  end

  t_tech += 1
  if t_tech >= 100 then
    spawn_trequinho()
    t_tech = 0
  end

  pontos += 1
  if aviso_t > 0 then aviso_t -= 1 end

  -- coleta de trequinhos
  for c in all(coletaveis) do
    local dx = c.x-(menino.x+5)
    local dy = c.y-(menino.y-10)
    if dx*dx+dy*dy < 100 then
      local ganho = 1
      if gato_ativo() == "scar" then ganho = 2 end
      techs += ganho
      pontos += 25*ganho
      estourar(c.x, c.y, C_TECH, 6)
      del(coletaveis, c)
      if gato_ativo() == "hanna" then escudo_pronto = true end
      verificar_desbloqueios()
    end
  end

  -- colisao com obstaculos
  local mx = menino.x+5
  local my = menino.y-(menino.agachado and 6 or 15)
  local mh = menino.agachado and 6 or 15
  for o in all(obstaculos) do
    local oy = CHAO-o.alt
    if o.t == "galho" then oy = CHAO-20 end
    if mx+4 > o.x and mx-4 < o.x+8 then
      if o.t == "galho" then
        if menino.y-6 < oy+o.alt then bater(o) end
      else
        if my+mh > oy then bater(o) end
      end
    end
  end
end

function bater(o)
  if escudo_pronto then
    escudo_pronto = false
    aviso = "ESCUDO SALVOU!"
    aviso_t = 80
    estourar(o.x, CHAO-8, 10, 12)
    del(obstaculos, o)
    return
  end
  estourar(menino.x+5, menino.y-10, 8, 18)
  if pontos > recorde then
    recorde = pontos
    dset(0, recorde)
  end
  estado = "game_over"
end

function desenhar_ceu()
  rectfill(0, 0, W, 30, C_CEU1)
  rectfill(0, 30, W, 58, C_CEU2)
  rectfill(0, 58, W, 78, C_CEU3)
  for s in all(estrelas) do
    pset(s.x, s.y, 6)
  end
  circfill(104, 18, 7, C_LUA)
  circfill(101, 16, 2, 7)
end

function desenhar_mata()
  -- camada longe
  local x = -((frame*vel*0.1)%20)
  while x < W+20 do
    rectfill(x, 70, x+10, 82, C_MATA1)
    rectfill(x+3, 64, x+7, 76, C_MATA1)
    x += 20
  end
  -- camada meio
  x = -((frame*vel*0.25)%16)
  while x < W+16 do
    rectfill(x, 78, x+9, 90, C_MATA2)
    rectfill(x+2, 71, x+6, 84, C_MATA2)
    x += 16
  end
  -- muro de tijolinhos
  rectfill(0, 88, W, 96, C_MURO)
  for x = 0, W, 8 do
    line(x, 88, x, 96, 7)
  end
  line(0, 92, W, 92, 7)
end

function desenhar_chao()
  rectfill(0, CHAO, W, H, C_TERRA)
  local d = -((frame*vel*0.8)%10)
  for x = d, W, 10 do
    line(x, CHAO+4, x+3, CHAO+4, 5)
  end
  for f in all(folhas) do
    pset(f.x, f.y, f.c)
  end
end

function desenhar_vagalumes()
  for v in all(vagalumes) do
    local brilho = math.sin(v.f) > 0.3
    if brilho then
      pset(v.x, v.y+math.sin(v.f)*2, C_VAGA)
    end
  end
end

function desenhar_cachorro(c)
  local x = flr(c.x)
  local y = 88
  if c.tipo == 4 then
    -- jabuti
    circfill(x, y, 4, 3)
    circfill(x, y, 3, 4)
    pset(x-1, y-1, 9)
    pset(x+1, y, 9)
    rectfill(x+3, y+1, x+5, y+2, 4)
  else
    -- cachorros
    local cor = 6
    if c.tipo == 2 then cor = 9 end
    if c.tipo == 3 then cor = 10 end
    rectfill(x-4, y-4, x+3, y+1, cor)
    rectfill(x+2, y-6, x+6, y-3, cor)
    pset(x+5, y-5, 0)
    if c.tipo == 1 then
      rectfill(x-3, y-5, x-1, y-3, 0)
    end
    local p = flr(frame/6)%2
    rectfill(x-3, y+1, x-2, y+3+p, cor)
    rectfill(x+1, y+1, x+2, y+3-p, cor)
  end
end

function desenhar_obstaculos()
  for o in all(obstaculos) do
    local x = flr(o.x)
    if o.t == "toco" then
      rectfill(x, CHAO-8, x+7, CHAO, 4)
      line(x+1, CHAO-6, x+6, CHAO-6, 5)
      line(x+2, CHAO-3, x+6, CHAO-3, 5)
    elseif o.t == "galho" then
      rectfill(x, CHAO-30, x+7, CHAO-20, 4)
      line(x+1, CHAO-20, x+1, CHAO-16, 3)
      line(x+5, CHAO-20, x+6, CHAO-15, 3)
      circfill(x+2, CHAO-19, 2, 11)
    else
      rectfill(x+2, CHAO-17, x+5, CHAO, 4)
      rectfill(x, CHAO-17, x+8, CHAO-14, 11)
      rectfill(x-3, CHAO-15, x+2, CHAO-13, 3)
      rectfill(x+6, CHAO-16, x+11, CHAO-14, 3)
    end
  end
end

function desenhar_trequinho(c)
  local x = flr(c.x)
  local y = flr(c.y+math.sin(c.p)*2)
  if c.t == "mp3" then
    rectfill(x-3, y-3, x+3, y+3, 5)
    rectfill(x-2, y-2, x+2, y+1, 11)
  elseif c.t == "cyber" then
    rectfill(x-4, y-3, x+4, y+3, 5)
    rectfill(x-3, y-2, x+2, y+1, 11)
    line(x+3, y-5, x+3, y-3, 7)
  elseif c.t == "fita" then
    rectfill(x-4, y-2, x+4, y+2, 0)
    circfill(x-2, y, 1, 5)
    circfill(x+2, y, 1, 5)
  else
    rectfill(x-3, y-3, x+3, y+3, 3)
    pset(x-1, y-1, 10)
    pset(x+1, y+1, 10)
  end
end

function desenhar_cabeca(cx, cy)
  rectfill(cx-4, cy-12, cx+3, cy-4, C_CABELO)
  rectfill(cx-5, cy-8, cx-4, cy+2, C_CABELO)
  rectfill(cx+3, cy-8, cx+4, cy+1, C_CABELO)
  rectfill(cx-3, cy-10, cx+2, cy-5, C_PELE)
  pset(cx+1, cy-8, C_OLHO)
  -- fone no pescoco
  rectfill(cx-4, cy-3, cx+3, cy-2, C_FONE)
  -- cabelo na testa
  rectfill(cx-4, cy-12, cx+2, cy-10, C_CABELO)
end

function desenhar_menino()
  local x = flr(menino.x)
  local base = flr(menino.y)
  if menino.piscar > 0 and flr(menino.piscar/2)%2 == 0 then return end
  if not menino.chao then
    line(x-5, base-16, x-9, base-12, C_CABELO)
  end
  if menino.agachado then
    desenhar_cabeca(x-2, base-8)
    rectfill(x-5, base-5, x+4, base-3, C_CAMISA)
    rectfill(x-4, base-2, x+2, base, C_BERMUDAS)
    rectfill(x+2, base-2, x+5, base, C_TENIS)
    return
  end
  desenhar_cabeca(x, base-18)
  -- bolsa com antena
  rectfill(x-6, base-13, x-3, base-8, 4)
  line(x-5, base-13, x-7, base-19, 7)
  pset(x-7, base-19, C_TECH)
  -- camisa
  rectfill(x-3, base-11, x+2, base-6, C_CAMISA)
  local braco = flr(menino.passo)%2 == 0 and -2 or 2
  line(x+2, base-10, x+5, base-6+braco, C_PELE)
  -- bermuda
  rectfill(x-3, base-6, x+2, base-3, C_BERMUDAS)
  -- pernas
  local f = flr(menino.passo)%4
  if f < 2 then
    line(x-1, base-3, x-3, base, C_PELE)
    line(x+1, base-3, x+3, base, C_PELE)
  else
    line(x-1, base-3, x+1, base, C_PELE)
    line(x+1, base-3, x-1, base, C_PELE)
  end
  -- tenis
  rectfill(x-4, base-1, x-1, base, C_TENIS)
  rectfill(x+1, base-1, x+4, base, C_TENIS)
end

function desenhar_particulas()
  for p in all(particulas) do
    pset(p.x, p.y, p.c)
  end
end

function desenhar_gatinhos()
  if #gatos_desbloq == 0 then return end
  for i = 1, #gatos_desbloq do
    local id = gatos_desbloq[i]
    local cx = menino.x-10-i*7
    local cy = CHAO-4
    local cor = 6
    if id == "catarino" then cor = 7 end
    if id == "coraline" then cor = 0 end
    if id == "hanna" then cor = 7 end
    if id == "scar" then cor = 5 end
    rectfill(cx-2, cy-4, cx+2, cy, cor)
    rectfill(cx+1, cy-6, cx+3, cy-4, cor)
    pset(cx+2, cy-5, 10)
    line(cx-2, cy, cx-3, cy-4, cor)
    if i == gato_idx then
      pset(cx, cy-8, 10)
    end
  end
end

function desenhar_hud()
  print("PONTOS "..pontos, 2, 2, C_TEXTO)
  print("TECH "..techs, 84, 2, C_TECH)
  print("REC "..recorde, 84, 10, 10)
  if escudo_pronto then
    print("ESCUDO", 2, 10, 10)
  end
  local g = gato_ativo()
  if g ~= "" then
    for a in all(GATOS) do
      if a.id == g then
        print(a.nome.." "..a.poder, 2, 18, 9)
      end
    end
  end
  if aviso_t > 0 then
    print(aviso, 30, 112, 10)
  end
end

function desenhar_titulo()
  print("CORRIDA DO MENINO", 12, 24, 7)
  print("AVENTURA NO SITIO", 30, 34, 10)
  desenhar_menino()
  if flr(t()*2)%2 == 0 then
    print("A PARA COMECAR", 38, 116, 7)
  end
end

function desenhar_fim()
  rectfill(20, 36, 108, 88, 0)
  print("OPS! CAIU!", 42, 42, 8)
  print("PONTOS "..pontos, 38, 56, 7)
  print("TECHS "..techs, 44, 66, 11)
  print("RECORDE "..recorde, 36, 76, 10)
  if flr(t()*2)%2 == 0 then
    print("A PARA RECOMECAR", 24, 96, 7)
  end
end

function _update()
  frame += 1
  if estado == "titulo" then
    if btnp(4) or btnp(5) then reiniciar() end
  elseif estado == "jogando" then
    atualizar_jogo()
  elseif estado == "game_over" then
    if btnp(4) or btnp(5) then reiniciar() end
  end
end

function _draw()
  desenhar_ceu()
  desenhar_mata()
  desenhar_vagalumes()
  for c in all(cachorros) do desenhar_cachorro(c) end
  desenhar_chao()
  desenhar_obstaculos()
  for c in all(coletaveis) do desenhar_trequinho(c) end
  desenhar_particulas()
  if estado == "titulo" then
    desenhar_menino()
    desenhar_titulo()
  else
    desenhar_gatinhos()
    desenhar_menino()
    desenhar_hud()
    if estado == "game_over" then desenhar_fim() end
  end
end
