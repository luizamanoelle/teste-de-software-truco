# Salve como: tests/test_truco.py
import pytest
from truco.bot import Bot
from truco.truco import Truco # Necessário para o monkeypatch

# --- Testes de Casos de Uso e Apostas (UC-02) ---

@pytest.mark.xfail(reason="BUG: truco.py (linha 78, 'pedir_truco') não atualiza self.valor_aposta para 2 quando o truco é aceito. [RN08]")
def test_truco_aceito_aumenta_valor_aposta_RN08(cenario_truco, monkeypatch):
    """
    Testa (UC-02 / RN08): Pedir Truco e o oponente (Bot) aceitar.
    A mão deve valer 2 tentos.
    """
    truco, j1, j2, cbr, dados = cenario_truco
    
    # Simula o Bot (j2) aceitando o truco
    monkeypatch.setattr(Bot, 'avaliar_truco', lambda *args: 1) # 1 = Aceitar
    
    resultado_aceite = truco.controlador_truco(cbr, dados, 1, j1, j2)
    
    assert resultado_aceite is True
    assert truco.estado_atual == "truco"
    
    # Este assert falha (1 == 2), provando o bug.
    assert truco.retornar_valor_aposta() == 2

def test_truco_recusado_da_1_ponto_ao_desafiante_UC02(cenario_truco, monkeypatch):
    """
    Testa (UC-02 / RF14): Pedir Truco e o oponente (Bot) recusar.
    O desafiante (j1) deve ganhar 1 tento.
    """
    truco, j1, j2, cbr, dados = cenario_truco

    # Simula o Bot (j2) recusando o truco
    monkeypatch.setattr(Bot, 'avaliar_truco', lambda *args: 0) # 0 = Recusar

    resultado_aceite = truco.controlador_truco(cbr, dados, 1, j1, j2)

    assert resultado_aceite is False
    assert j1.pontos == 1 # j1 (desafiante) ganha 1 ponto
    assert j2.pontos == 0

def test_escalonamento_truco_aceito_retruco_recusado_UC02(cenario_truco, monkeypatch):
    """
    Testa (UC-02): Truco (aceito) -> Retruco (recusado).
    O desafiante do Retruco (j2) deve ganhar 2 tentos.
    """
    truco, j1, j2, cbr, dados = cenario_truco

    # 1. J1 pede Truco.
    # 2. Bot (j2) avalia e decide AUMENTAR (2 = Retruco)
    monkeypatch.setattr(Bot, 'avaliar_truco', lambda *args: 2) # 2 = Aumentar
    
    # 3. Humano (j1) decide RECUSAR (0)
    monkeypatch.setattr('builtins.input', lambda _: '0') # 0 = Recusar

    resultado_aceite = truco.controlador_truco(cbr, dados, 1, j1, j2)

    assert resultado_aceite is False
    assert j1.pontos == 0
    # O código em truco.py (linha 105) dá 2 pontos ao j2.
    assert j2.pontos == 2
    assert truco.estado_atual == "retruco"
    # Verifica se o valor da aposta foi corretamente definido para 3
    # pela função 'pedir_retruco'
    assert truco.retornar_valor_aposta() == 3

@pytest.mark.xfail(reason="BUG: truco.py (linha 149, 'pedir_vale_quatro') não atualiza self.estado_atual para 'vale_quatro'.")
def test_escalonamento_completo_aceito_UC02(cenario_truco, monkeypatch):
    """
    Testa (UC-02): Truco -> Retruco -> Vale-Quatro (todos aceitos).
    O valor da mão deve ser 4 e o estado "vale_quatro".
    """
    truco, j1, j2, cbr, dados = cenario_truco

    # Simulação de respostas:
    respostas_bot = [
        2,  # 1. Bot ouve "Truco" -> responde "Aumentar" (Retruco)
        1   # 3. Bot ouve "Vale Quatro" -> responde "Aceitar"
    ]
    respostas_humano = [
        '2' # 2. Humano ouve "Retruco" -> responde "Aumentar" (Vale Quatro)
    ]

    monkeypatch.setattr(Bot, 'avaliar_truco', lambda *args: respostas_bot.pop(0))
    monkeypatch.setattr('builtins.input', lambda _: respostas_humano.pop(0))

    resultado_aceite = truco.controlador_truco(cbr, dados, 1, j1, j2)

    assert resultado_aceite is True
    # A aposta final deve ser 4
    assert truco.retornar_valor_aposta() == 4
    # Ninguém ganha pontos ainda
    assert j1.pontos == 0 and j2.pontos == 0
    
    # Este assert falha ("retruco" == "vale_quatro"), provando o bug.
    assert truco.estado_atual == "vale_quatro"

def test_escalonamento_vale_quatro_recusado_da_3_pontos_UC02(cenario_truco, monkeypatch):
    """
    Testa (UC-02): Cobre a lacuna: Truco -> Retruco -> Vale-Quatro (Recusado).
    O desafiante do Vale-Quatro (J1) deve ganhar 3 tentos.
    """
    truco, j1, j2, cbr, dados = cenario_truco

    # Simulação da escalonada:
    # J1 pede Truco
    # J2 (Bot) responde "Aumentar" (Retruco)
    # J1 (Humano) responde "Aumentar" (Vale-Quatro)
    # J2 (Bot) responde "Recusar"
    
    respostas_bot_mock = [
        2,  # J2 ouve "Truco" -> responde "Aumentar" (Retruco)
        0   # J2 ouve "Vale-Quatro" -> responde "Recusar"
    ]
    respostas_humano_mock = [
        '2' # J1 ouve "Retruco" -> responde "Aumentar" (Vale-Quatro)
    ]

    monkeypatch.setattr(Bot, 'avaliar_truco', lambda *args: respostas_bot_mock.pop(0))
    monkeypatch.setattr('builtins.input', lambda _: respostas_humano_mock.pop(0))

    # 2. Act
    resultado_aceite = truco.controlador_truco(cbr, dados, 1, j1, j2)

    # 3. Assert
    assert resultado_aceite is False # Aposta foi recusada
    
    # J1 (que pediu o Vale-Quatro) ganha 3 pontos
    assert j1.pontos == 3
    assert j2.pontos == 0
    
    # O valor da aposta foi definido para 4 antes da recusa
    assert truco.retornar_valor_aposta() == 4