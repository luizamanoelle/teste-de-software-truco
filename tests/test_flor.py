# Salve como: tests/test_flor.py
import pytest
from truco.carta import Carta

# --- Testes de Fluxo de Flor (UC-03 / RN09) ---

def test_flor_simples_da_3_pontos_RN09(cenario_flor):
    """
    Testa (RN09): Cantar Flor (oponente não tem) vale 3 tentos.
    """
    flor, j1, j2, iface = cenario_flor
    
    # J1 (Humano) tem Flor
    j1.mao = [Carta(1, "COPAS"), Carta(2, "COPAS"), Carta(3, "COPAS")]
    j1.flor = j1.checa_flor() # True
    
    # J2 (Bot) não tem Flor
    j2.mao = [Carta(1, "ESPADAS"), Carta(2, "OUROS"), Carta(3, "BASTOS")]
    j2.flor = j2.checa_flor() # False

    # J1 (Humano) canta Flor
    flor.pedir_flor(1, j1, j2, iface)

    assert j1.pontos == 3
    assert j2.pontos == 0
    assert flor.quem_venceu_flor == 1
    assert flor.estado_atual == "Flor"

def test_flor_contraflor_aceita_da_6_pontos_RN09(cenario_flor, monkeypatch):
    """
    Testa (RN09): J1 canta Flor, J2 (Bot) tem Flor (canta Contraflor), J1 aceita.
    O vencedor (maior envido) ganha 6 tentos.
    """
    flor, j1, j2, iface = cenario_flor

    # J1 (Humano) tem Flor (Envido: 33)
    j1.mao = [Carta(7, "COPAS"), Carta(6, "COPAS"), Carta(1, "COPAS")]
    j1.envido = j1.calcula_envido(j1.mao)
    j1.flor = j1.checa_flor() # True
    
    # J2 (Bot) tem Flor (Envido: 29)
    j2.mao = [Carta(5, "ESPADAS"), Carta(4, "ESPADAS"), Carta(1, "ESPADAS")]
    j2.envido = j2.calcula_envido(j2.mao)
    j2.flor = j2.checa_flor() # True
    
    # Simula o J1 (Humano) aceitando a Contraflor
    monkeypatch.setattr('builtins.input', lambda _: '1') # 1 = Aceitar

    # J1 (Humano) canta Flor
    flor.pedir_flor(1, j1, j2, iface)

    assert flor.valor_flor == 6
    assert j1.pontos == 6 # J1 venceu (33 > 29)
    assert j2.pontos == 0
    assert flor.quem_venceu_flor == 1
    assert flor.estado_atual == "Contraflor"

def test_flor_contraflor_recusada_da_3_pontos_ao_bot_RN09(cenario_flor, monkeypatch):
    """
    Testa (RN09): J1 canta Flor, J2 (Bot) tem Flor (canta Contraflor), J1 recusa.
    O Bot (J2) ganha os 3 pontos da Flor original.
    """
    flor, j1, j2, iface = cenario_flor

    j1.mao = [Carta(7, "COPAS"), Carta(6, "COPAS"), Carta(1, "COPAS")]
    j1.flor = j1.checa_flor() # True
    
    j2.mao = [Carta(5, "ESPADAS"), Carta(4, "ESPADAS"), Carta(1, "ESPADAS")]
    j2.flor = j2.checa_flor() # True
    
    # Simula o J1 (Humano) recusando a Contraflor
    monkeypatch.setattr('builtins.input', lambda _: '0') # 0 = Recusar

    # J1 (Humano) canta Flor
    flor.pedir_flor(1, j1, j2, iface)

    # O código em flor.py (linha 45) dá 3 pontos ao J2 se J1 recusa.
    assert j1.pontos == 0
    assert j2.pontos == 3
    assert flor.quem_venceu_flor == 0
    assert flor.estado_atual == "Contraflor"

def test_nao_pode_cantar_flor_sem_flor_na_mao_RN09(cenario_flor):
    """
    Testa (RN09): Se um jogador sem flor canta flor (e o oponente não tem).
    Nenhum ponto deve ser dado.
    """
    flor, j1, j2, iface = cenario_flor
    
    j1.mao = [Carta(1, "COPAS"), Carta(2, "ESPADAS"), Carta(3, "COPAS")]
    j1.flor = j1.checa_flor() # False
    
    j2.mao = [Carta(1, "ESPADAS"), Carta(2, "OUROS"), Carta(3, "BASTOS")]
    j2.flor = j2.checa_flor() # False

    # J1 (Humano) canta Flor
    flor.pedir_flor(1, j1, j2, iface)

    # O método 'pedir_flor' não faz nada se nenhum jogador tiver flor.
    assert j1.pontos == 0
    assert j2.pontos == 0
    assert flor.quem_venceu_flor == 0