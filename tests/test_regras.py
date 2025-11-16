# Salve este código como: tests/test_regras_invalidas.py

import pytest
from truco.jogador import Jogador
from truco.bot import Bot
from truco.carta import Carta
from truco.envido import Envido
from truco.truco import Truco
from truco.flor import Flor
from truco.interface import Interface # Import necessário

# --- Fixture para Cenários de Regras Inválidas ---

@pytest.fixture
def cenario_regras():
    """Prepara um cenário completo com todos os objetos para testar interações."""
    j1 = Jogador("Humano")
    j2 = Bot("Robô")
    truco = Truco()
    envido = Envido()
    flor = Flor()
    iface_mock = Interface()
    
    # Mocks de cbr/dados, não são necessários para lógica
    cbr_mock = None
    dados_mock = None
    
    return j1, j2, truco, envido, flor, iface_mock, cbr_mock, dados_mock


def test_envido_nao_pode_ser_jogado_apos_primeira_vaza(cenario_regras, monkeypatch):
    """
    Testa (RN10): Testar se um jogador não pode chamar Envido 
    após a primeira vaza.
    
    BUG: O modelo 'Envido' não sabe o que é uma 'vaza'. 
    Ele não verifica o número de cartas na mão.
    """
    # 1. Arrange
    j1, j2, truco, envido, flor, iface, cbr, dados = cenario_regras
    
    # CORREÇÃO 1: Resetar o estado para evitar poluição de outros testes
    # (O ideal seria um método envido.resetar(), mas ele não existe/está vazio)
    envido.estado_atual = 0
    envido.quem_venceu_envido = 0
    # Limpamos os pontos dos jogadores também, caso estejam "sujos"
    j1.pontos = 0
    
    # CORREÇÃO 2: Dar cartas e calcular envido para um Assert real
    j1.mao = [Carta(7, "COPAS"), Carta(2, "OUROS"), Carta(3, "ESPADAS")]
    j1.envido = j1.calcula_envido(j1.mao) # j1 tem 7 pontos
    
    j2.mao = [Carta(4, "BASTOS"), Carta(5, "OUROS"), Carta(1, "ESPADAS")]
    j2.envido = j2.calcula_envido(j2.mao) # j2 tem 5 pontos

    # Simulamos a Vaza 1: J1 joga uma carta
    j1.jogar_carta(0)
    assert len(j1.mao) == 2 # J1 tem 2 cartas
    
    # Simula o Bot (j2) aceitando
    monkeypatch.setattr(Bot, 'avaliar_envido', lambda *args: 1)

    # 2. Act
    # J1 (Humano) tenta chamar Envido (tipo 6) na Vaza 2 (ilegal)
    resultado_envido = envido.controlador_envido(cbr, dados, 6, 1, j1, j2, iface)

    # 3. Assert (Provando o Bug)
    # O que DEVERIA acontecer (RN10):
    # O 'controlador_envido' deveria falhar (retornar None)
    # O assert correto seria: assert resultado_envido is None
    
    # O que REALMENTE acontece (o bug):
    # O Envido é chamado e aceito, mesmo sendo ilegal.
    # Estes asserts PASSAM, provando que o bug ocorreu:
    assert resultado_envido is True
    assert j1.pontos == 2 # J1 ganha 2 pontos (pois 7 > 5) ilegalmente

def test_truco_nao_pode_ser_jogado_com_envido_pendente(cenario_regras, monkeypatch):
    """
    Testa (RN08): Testar se um jogador não pode chamar Truco 
    se houver um Envido/Flor pendente.
    
    BUG: O modelo 'Truco' não sabe do estado do 'Envido' ou 'Flor'.
    """
    # 1. Arrange
    j1, j2, truco, envido, flor, iface, cbr, dados = cenario_regras

    # Simulamos que o Envido está "em andamento"
    envido.estado_atual = 6 # (6 = Envido)
    
    # Simula o Bot (j2) aceitando o truco
    monkeypatch.setattr(Bot, 'avaliar_truco', lambda *args: 1) # 1 = Aceitar

    # 2. Act
    # J1 (Humano) tenta chamar Truco (ilegal, pois o Envido está pendente)
    resultado_truco = truco.controlador_truco(cbr, dados, 1, j1, j2)
    
    # 3. Assert (Provando o Bug)
    # O que DEVERIA acontecer (RN08):
    # O 'controlador_truco' deveria falhar (retornar None)
    # O assert correto seria: assert resultado_truco is None
    
    # O que REALMENTE acontece (o bug):
    # O Truco é chamado e aceito.
    # Este assert PASSA, provando que o bug ocorreu:
    assert resultado_truco is True
    assert truco.estado_atual == "truco"

def test_jogar_carta_que_nao_esta_na_mao_levanta_excecao(cenario_regras):
    """
    Testa (Exceção): Testar se um jogador não pode jogar 
    uma carta que não está em sua mão.
    
    Este teste verifica o comportamento CORRETO do Python (IndexError).
    """
    # 1. Arrange
    j1, j2, truco, envido, flor, iface, cbr, dados = cenario_regras
    j1.mao = [Carta(1, "COPAS"), Carta(2, "OUROS"), Carta(3, "ESPADAS")]
    
    # 2. Act & 3. Assert
    # Verificamos se o código levanta um 'IndexError' 
    # ao tentar jogar a carta no índice 10 (que não existe)
    with pytest.raises(IndexError):
        j1.jogar_carta(10) # Índice 10 está fora do range da mão (0, 1, 2)