# Salve este código como: tests/test_flor.py

import pytest
from truco.jogador import Jogador
from truco.bot import Bot
from truco.carta import Carta
from truco.flor import Flor
from truco.interface import Interface

# --- Testes de Lógica de Detecção (RN09) ---
# Estes testes validam a lógica pura do 'checa_flor' na classe Jogador.

def test_jogador_checa_flor_detecta_corretamente():
    """
    Testa (RF16): Se um jogador com 3 cartas do mesmo naipe pode cantar Flor.
    A função checa_flor() deve retornar True.
    """
    # 1. Arrange
    jogador = Jogador("Teste")
    # Mão com 3 cartas de Copas
    jogador.mao = [
        Carta(1, "COPAS"),
        Carta(5, "COPAS"),
        Carta(12, "COPAS")
    ]
    
    # 2. Act
    resultado = jogador.checa_flor()
    
    # 3. Assert
    assert resultado is True

def test_jogador_checa_flor_nao_detecta_incorretamente():
    """
    Testa (RN09): Se um jogador sem 3 cartas do mesmo naipe, não pode cantar Flor.
    A função checa_flor() deve retornar False.
    """
    # 1. Arrange
    jogador = Jogador("Teste")
    # Mão mista
    jogador.mao = [
        Carta(1, "COPAS"),
        Carta(5, "COPAS"),
        Carta(12, "ESPADAS") # Naipe diferente
    ]
    
    # 2. Act
    resultado = jogador.checa_flor()
    
    # 3. Assert
    assert resultado is False

# --- Fixture para Cenário de Apostas (Flor) ---

@pytest.fixture
def cenario_flor():
    """Prepara instâncias limpas para testar o fluxo de apostas de flor."""
    flor = Flor()
    jogador1 = Jogador("Humano")
    jogador2 = Bot("Robô")
    interface_mock = Interface()
    
    return flor, jogador1, jogador2, interface_mock

# --- Testes de Fluxo de Flor (UC-03) ---

def test_flor_simples_da_3_pontos(cenario_flor):
    """
    Testa (RN09): Cantar Flor (quando o oponente não tem) vale 3 tentos.
    """
    # 1. Arrange
    flor, j1, j2, iface = cenario_flor
    
    # J1 (Humano) tem Flor
    j1.mao = [Carta(1, "COPAS"), Carta(2, "COPAS"), Carta(3, "COPAS")]
    j1.flor = j1.checa_flor() # True
    
    # J2 (Bot) não tem Flor
    j2.mao = [Carta(1, "ESPADAS"), Carta(2, "OUROS"), Carta(3, "BASTOS")]
    j2.flor = j2.checa_flor() # False

    # 2. Act
    # J1 (Humano) canta Flor
    flor.pedir_flor(1, j1, j2, iface)

    # 3. Assert
    # J1 ganha 3 pontos
    assert j1.pontos == 3
    assert j2.pontos == 0
    assert flor.quem_venceu_flor == 1
    assert flor.estado_atual == "Flor"

def test_flor_contraflor_aceita_da_6_pontos(cenario_flor, monkeypatch):
    """
    Testa (RN09): J1 canta Flor, J2 tem Flor (canta Contraflor), J1 aceita.
    O vencedor (maior envido) ganha 6 tentos.
    """
    # 1. Arrange
    flor, j1, j2, iface = cenario_flor

    # J1 (Humano) tem Flor (Pontos de envido: 20 + 7 + 6 = 33)
    j1.mao = [Carta(7, "COPAS"), Carta(6, "COPAS"), Carta(1, "COPAS")]
    j1.envido = j1.calcula_envido(j1.mao)
    j1.flor = j1.checa_flor() # True
    
    # J2 (Bot) tem Flor (Pontos de envido: 20 + 5 + 4 = 29)
    j2.mao = [Carta(5, "ESPADAS"), Carta(4, "ESPADAS"), Carta(1, "ESPADAS")]
    j2.envido = j2.calcula_envido(j2.mao)
    j2.flor = j2.checa_flor() # True
    
    # Simula o J1 (Humano) aceitando a Contraflor
    # 'decisao_jogador' é chamado para o J1 decidir
    monkeypatch.setattr('builtins.input', lambda _: '1') # 1 = Aceitar

    # 2. Act
    # J1 (Humano) canta Flor
    flor.pedir_flor(1, j1, j2, iface)

    # 3. Assert
    # A aposta subiu para 6
    assert flor.valor_flor == 6
    # J1 venceu a contraflor (33 > 29)
    assert j1.pontos == 6
    assert j2.pontos == 0
    assert flor.quem_venceu_flor == 1
    assert flor.estado_atual == "Contraflor"

def test_flor_contraflor_recusada_da_3_pontos_ao_bot(cenario_flor, monkeypatch):
    """
    Testa (RN09): J1 canta Flor, J2 tem Flor (canta Contraflor), J1 recusa.
    O Bot (J2) ganha os 3 pontos da Flor original.
    """
    # 1. Arrange
    flor, j1, j2, iface = cenario_flor

    j1.mao = [Carta(7, "COPAS"), Carta(6, "COPAS"), Carta(1, "COPAS")]
    j1.flor = j1.checa_flor() # True
    
    j2.mao = [Carta(5, "ESPADAS"), Carta(4, "ESPADAS"), Carta(1, "ESPADAS")]
    j2.flor = j2.checa_flor() # True
    
    # Simula o J1 (Humano) recusando a Contraflor
    monkeypatch.setattr('builtins.input', lambda _: '0') # 0 = Recusar

    # 2. Act
    # J1 (Humano) canta Flor
    flor.pedir_flor(1, j1, j2, iface)

    # 3. Assert
    # O código em flor.py (linha 45) dá 3 pontos ao J2 se J1 recusa a contraflor.
    assert j1.pontos == 0
    assert j2.pontos == 3
    assert flor.quem_venceu_flor == 0 # Disputa não foi até o fim
    assert flor.estado_atual == "Contraflor"

def test_nao_pode_cantar_flor_sem_flor_na_mao(cenario_flor):
    """
    Testa (RN09): Se um jogador sem flor canta flor (e o oponente também não tem).
    O código do jogo parece permitir isso, mas nenhum ponto deve ser dado.
    """
    # 1. Arrange
    flor, j1, j2, iface = cenario_flor
    
    # J1 (Humano) não tem Flor
    j1.mao = [Carta(1, "COPAS"), Carta(2, "ESPADAS"), Carta(3, "COPAS")]
    j1.flor = j1.checa_flor() # False
    
    # J2 (Bot) não tem Flor
    j2.mao = [Carta(1, "ESPADAS"), Carta(2, "OUROS"), Carta(3, "BASTOS")]
    j2.flor = j2.checa_flor() # False

    # 2. Act
    # J1 (Humano) canta Flor
    flor.pedir_flor(1, j1, j2, iface)

    # 3. Assert
    # O método 'pedir_flor' não faz nada se nenhum dos casos 
    # (j1.flor, j2.flor, ou ambos) for verdadeiro.
    assert j1.pontos == 0
    assert j2.pontos == 0
    assert flor.quem_venceu_flor == 0
    assert flor.estado_atual == "Flor" # O estado é setado, mas nada acontece.

    # (No topo do arquivo, adicione as importações que faltam)
# from truco.flor import Flor
# from truco.carta import Carta
