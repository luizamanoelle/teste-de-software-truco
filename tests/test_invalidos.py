import pytest
from truco.jogador import Jogador
from truco.bot import Bot
from truco.carta import Carta
from truco.envido import Envido
from truco.truco import Truco
from truco.flor import Flor
from truco.interface import Interface

@pytest.mark.xfail(reason="BUG: envido.py não checa o número de cartas na mão. [RN10]")
def test_envido_nao_pode_ser_jogado_apos_primeira_vaza_RN10(cenario_regras_invalidas, monkeypatch):
    """
    Testa (RN10): Não pode chamar Envido após a primeira vaza.
    O modelo 'Envido' não sabe o que é uma 'vaza'.
    """
    j1, j2, truco, envido, flor, iface, cbr, dados = cenario_regras_invalidas
    
    # Prepara mãos para um Envido real
    j1.mao = [Carta(7, "COPAS"), Carta(2, "OUROS"), Carta(3, "ESPADAS")]
    j1.envido = j1.calcula_envido(j1.mao) # j1 tem 7
    j2.mao = [Carta(4, "BASTOS"), Carta(5, "OUROS"), Carta(1, "ESPADAS")]
    j2.envido = j2.calcula_envido(j2.mao) # j2 tem 5

    # Simula a Vaza 1: J1 joga uma carta
    j1.jogar_carta(0)
    assert len(j1.mao) == 2 # J1 só tem 2 cartas
    
    monkeypatch.setattr(Bot, 'avaliar_envido', lambda *args: 1) # Bot aceita

    # J1 (Humano) tenta chamar Envido (ilegal)
    resultado_envido = envido.controlador_envido(cbr, dados, 6, 1, j1, j2, iface)

    # O Envido não deveria rodar (resultado == None)
    assert resultado_envido is None
    
    # O assert que prova o (o código roda e dá pontos):
    # assert resultado_envido is True
    # assert j1.pontos == 2

@pytest.mark.xfail(reason="BUG: truco.py não checa o estado de 'envido' ou 'flor' antes de rodar. [RN08]")
def test_truco_nao_pode_ser_jogado_com_envido_pendente_RN08(cenario_regras_invalidas, monkeypatch):
    """
    Testa (RN08): Não pode chamar Truco com Envido/Flor pendente.
    BUG: O modelo 'Truco' não sabe do estado do 'Envido'.
    """
    j1, j2, truco, envido, flor, iface, cbr, dados = cenario_regras_invalidas

    # Simula que o Envido está "em andamento"
    envido.estado_atual = 6 # (6 = Envido)
    
    monkeypatch.setattr(Bot, 'avaliar_truco', lambda *args: 1) # Bot aceita

    # J1 (Humano) tenta chamar Truco (ilegal)
    resultado_truco = truco.controlador_truco(cbr, dados, 1, j1, j2)
    
    # O Truco não deveria rodar (resultado == None)
    assert resultado_truco is None

    # (o código roda):
    # assert resultado_truco is True
    # assert truco.estado_atual == "truco"

@pytest.mark.xfail(reason="BUG: flor.py não checa o número de cartas na mão (Vaza 1). [RN09]")
def test_flor_nao_pode_ser_jogada_apos_primeira_vaza_RN09(cenario_regras_invalidas, monkeypatch):
    """
    Testa (RN09): Não pode chamar Flor após a primeira vaza.
     O modelo 'Flor' não sabe o que é uma 'vaza'
    (ele não checa o len(mao)).
    """
    # 1. Arrange
    j1, j2, truco, envido, flor, iface, cbr, dados = cenario_regras_invalidas
    
    # J1 (Humano) tem Flor
    j1.mao = [Carta(1, "COPAS"), Carta(2, "COPAS"), Carta(3, "COPAS")]
    j1.flor = j1.checa_flor() # True
    
    # J2 (Bot) não tem Flor
    j2.mao = [Carta(1, "ESPADAS"), Carta(2, "OUROS"), Carta(3, "BASTOS")]
    j2.flor = j2.checa_flor() # False

    # Simula a Vaza 1: J1 joga uma carta
    j1.jogar_carta(0)
    assert len(j1.mao) == 2 # J1 só tem 2 cartas

    # 2. Act
    # J1 (Humano) tenta chamar Flor (tipo 5) na Vaza 2 (ilegal)
    flor.pedir_flor(1, j1, j2, iface)

    # 3. Assert (Provando o Bug)
    
    # O que DEVERIA acontecer (RN09):
    # O 'pedir_flor' deveria falhar (não dar pontos).
    # O assert correto (que vai falhar) é:
    assert j1.pontos == 0
    
    # O que REALMENTE acontece (o bug):
    # A classe Flor ignora a vaza, vê a flor e dá 3 pontos.
    # O assert que prova o bug é:
    # assert j1.pontos == 3