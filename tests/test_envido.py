# Salve como: tests/test_envido.py
import pytest
from truco.jogador import Jogador
from truco.bot import Bot
from truco.carta import Carta
from truco.envido import Envido
from truco.interface import Interface
from truco.flor import Flor

# --- Testes de Fluxo de Envido (UC-03) ---

def test_envido_aceito_da_pontos_ao_vencedor_UC03(cenario_envido, monkeypatch):
    """
    Testa (UC-03 / RF15): Chamar Envido e oponente (Bot) aceitar.
    J1 (33) ganha de J2 (25). J1 deve ganhar 2 tentos.
    """
    envido, j1, j2, cbr, dados, iface = cenario_envido
    
    # Simula o Bot (j2) aceitando o envido
    monkeypatch.setattr(Bot, 'avaliar_envido', lambda *args: 1) # 1 = Aceitar

    # J1 (Humano) pede Envido (tipo 6)
    envido.controlador_envido(cbr, dados, 6, 1, j1, j2, iface)

    assert envido.quem_venceu_envido == 1
    assert j1.pontos == 2 # Ganhou 2 pontos (valor_envido padrão)
    assert j2.pontos == 0

def test_envido_recusado_da_1_ponto_ao_desafiante_UC03(cenario_envido, monkeypatch):
    """
    Testa (UC-03 / RF17): Chamar Envido e oponente (Bot) recusar.
    J1 pede. J1 deve ganhar 1 tento.
    """
    envido, j1, j2, cbr, dados, iface = cenario_envido
    
    # Simula o Bot (j2) recusando o envido
    monkeypatch.setattr(Bot, 'avaliar_envido', lambda *args: 0) # 0 = Recusar

    envido.controlador_envido(cbr, dados, 6, 1, j1, j2, iface)

    assert envido.quem_venceu_envido == 0 # Ninguém "venceu"
    assert envido.quem_fugiu == 2 # J2 "fugiu"
    assert j1.pontos == 1 # J1 (desafiante) ganha 1 ponto
    assert j2.pontos == 0

def test_envido_empate_ganha_o_mao_RN10(cenario_envido, monkeypatch):
    """
    Testa (RN10): Em um empate de pontos de Envido, o jogador "Mão" (J1) ganha.
    """
    envido, j1, j2, cbr, dados, iface = cenario_envido
    
    # Força o J2 a também ter 33 pontos
    j2.mao = [Carta(7, "COPAS"), Carta(6, "COPAS"), Carta(1, "BASTOS")]
    j2.envido = j2.calcula_envido(j2.mao) # 33
    
    assert j1.primeiro is True # J1 é o "mão"
    assert j1.envido == 33 and j2.envido == 33
    
    monkeypatch.setattr(Bot, 'avaliar_envido', lambda *args: 1) # 1 = Aceitar

    envido.controlador_envido(cbr, dados, 6, 1, j1, j2, iface)

    # O J1 (Humano) venceu por ser "mão"
    assert envido.quem_venceu_envido == 1
    assert j1.pontos == 2 # Ganha os 2 pontos da aposta
    assert j2.pontos == 0

# --- Testes de Bugs de Interação (Envido vs Flor) ---

@pytest.mark.xfail(reason="BUG: envido.py não checa o estado de 'flor' antes de rodar. [RN09]")
def test_flor_anula_envido_em_andamento_RN09(cenario_envido, monkeypatch):
    """
    Testa (RN09): Se a Flor foi cantada, o Envido deve ser anulado.
    """
    envido, j1, j2, cbr, dados, iface = cenario_envido
    flor = Flor()
    
    # J2 (Bot) tem Flor e canta
    j2.mao = [Carta(1, "COPAS"), Carta(2, "COPAS"), Carta(3, "COPAS")]
    j2.flor = j2.checa_flor() # True
    flor.pedir_flor(2, j1, j2, iface)
    
    # Pré-condição: J2 ganhou 3 pontos pela Flor
    assert j2.pontos == 3
    assert j1.pontos == 0
    
    # 2. Act
    # J1 (Humano), ignora a Flor e tenta chamar Envido (ilegal)
    resultado = envido.controlador_envido(cbr, dados, 6, 1, j1, j2, iface)
    
    # 3. Assert
    # O Envido não deveria rodar
    assert resultado is None 
    # J1 não deve ganhar pontos de Envido
    assert j1.pontos == 0
    # Pontos de J2 devem ser apenas os 3 da Flor
    assert j2.pontos == 3

@pytest.mark.xfail(reason="BUG: envido.py não dá ao Humano a opção de 'Flor' ao receber um Envido. [RN09]")
def test_bot_chama_envido_mas_humano_tem_flor_RN09(cenario_envido, monkeypatch):
    """
    Testa (RN09): Bot chama Envido, mas Humano (J1) tem Flor.
    O Humano deveria poder cantar Flor, anulando o Envido.
    """
    envido, j1, j2, cbr, dados, iface = cenario_envido
    
    # Damos ao J1 (Humano) uma Flor
    j1.mao = [Carta(1, "COPAS"), Carta(2, "COPAS"), Carta(3, "COPAS")]
    j1.flor = j1.checa_flor() # True
    j1.envido = j1.calcula_envido(j1.mao) # 25
    
    # Damos ao J2 (Bot) um Envido alto (sem flor)
    j2.mao = [Carta(7, "OUROS"), Carta(6, "OUROS"), Carta(1, "ESPADAS")]
    j2.flor = j2.checa_flor() # False
    j2.envido = j2.calcula_envido(j2.mao) # 33
    
    # Simula o J1 "Aceitando" o Envido (opção '1'),
    # pois o código não oferece a opção de "Flor".
    monkeypatch.setattr('builtins.input', lambda _: '1') # 1 = Aceitar

    # O Bot (quem_pediu=2) chama Envido (tipo 6)
    envido.controlador_envido(cbr, dados, 6, 2, j1, j2, iface)

    # Assert (Provando o Comportamento Incorreto)
    # O J2 ganhou 2 pontos de Envido ILEGALMENTE.
    assert j2.pontos == 2
    assert j1.pontos == 0
    assert envido.quem_venceu_envido == 2

# Em: tests/test_envido.py
# (Adicione estes dois testes no final do arquivo)

@pytest.mark.xfail(reason="BUG: RN10 diz que Real Envido vale 3, mas envido.py (linha 105) implementa 5.")
def test_real_envido_aceito_vale_3_pontos_RN10(cenario_envido, monkeypatch):
    """
    Testa (RN10): Se chamar Real Envido (tipo 7) e for aceito,
    o vencedor (J1) deve ganhar 3 pontos.
    """
    envido, j1, j2, cbr, dados, iface = cenario_envido
    
    # Simula o Bot (j2) aceitando (1)
    monkeypatch.setattr(Bot, 'avaliar_envido', lambda *args: 1)

    # J1 (Humano) pede Real Envido (tipo 7)
    envido.controlador_envido(cbr, dados, 7, 1, j1, j2, iface)

    # O código do jogo (envido.py, linha 105)
    # define self.valor_envido = 5 (ERRADO).
    # O requisito (RN10) diz que é 3.
    
    # O teste verifica o requisito (3) e vai falhar (XFAIL).
    assert j1.pontos == 3
    assert j2.pontos == 0
    assert envido.quem_venceu_envido == 1
    # O assert que provaria o bug (se não fosse xfail):
    # assert j1.pontos == 5 


def test_falta_envido_aceito_calcula_pontos_da_meta_RN10(cenario_envido, monkeypatch):
    """
    Testa (RN10): Se chamar Falta Envido (tipo 8) calcula os
    pontos restantes até a meta (12).
    """
    envido, j1, j2, cbr, dados, iface = cenario_envido
    
    # J1 tem 0 pontos. J2 tem 0 pontos. Meta é 12.
    # J1 pede Falta Envido.
    # O valor da aposta deve ser 12 - j2.pontos = 12.
    #
    
    # Simula o Bot (j2) aceitando (1)
    monkeypatch.setattr(Bot, 'avaliar_envido', lambda *args: 1)

    # J1 (Humano) pede Falta Envido (tipo 8)
    envido.controlador_envido(cbr, dados, 8, 1, j1, j2, iface)

    # J1 vence (33 > 25) e deve ganhar os 12 pontos.
    assert j1.pontos == 12
    assert j2.pontos == 0
    assert envido.quem_venceu_envido == 1
    