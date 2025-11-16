# Salve este código como: tests/test_envido.py

import pytest
from truco.jogador import Jogador
from truco.bot import Bot
from truco.carta import Carta  # <--- IMPORTAÇÃO ADICIONADA
from truco.envido import Envido
from truco.interface import Interface # <--- IMPORTAÇÃO ADICIONADA
from truco.flor import Flor

# --- Testes de Cálculo de Envido (RN10) ---

def test_calculo_envido_33_pontos():
    """
    Testa (RN10): 7 de ouros + 6 de ouros = 20 + 7 + 6 = 33 pontos.
    """
    # 1. Arrange
    jogador = Jogador("Teste")
    mao = [
        Carta(7, "OUROS"),
        Carta(6, "OUROS"),
        Carta(1, "ESPADAS") # Carta de outro naipe
    ]
    
    # 2. Act
    pontos_envido = jogador.calcula_envido(mao) #
    
    # 3. Assert
    assert pontos_envido == 33

def test_calculo_envido_figuras_valem_zero():
    """
    Testa (RN10): Figuras (10, 11, 12) valem 0 para o cálculo.
    Ex: 12 de copas + 11 de copas = 20 + 0 + 0 = 20 pontos.
    """
    # 1. Arrange
    jogador = Jogador("Teste")
    mao = [
        Carta(12, "COPAS"),
        Carta(11, "COPAS"),
        Carta(5, "ESPADAS") # Carta de outro naipe
    ]
    
    # 2. Act
    pontos_envido = jogador.calcula_envido(mao) #
    
    # 3. Assert
    assert pontos_envido == 20

def test_calculo_envido_naipes_diferentes_pega_maior():
    """
    Testa (RN10): Se não há cartas do mesmo naipe, vale a mais alta.
    Ex: 7 de ouros + 5 de espadas + 2 de bastos = 7 pontos.
    """
    # 1. Arrange
    jogador = Jogador("Teste")
    mao = [
        Carta(7, "OUROS"), # Carta mais alta (vale 7)
        Carta(5, "ESPADAS"),
        Carta(2, "BASTOS")
    ]
    
    # 2. Act
    pontos_envido = jogador.calcula_envido(mao) #
    
    # 3. Assert
    assert pontos_envido == 7

# --- Fixture para Cenário de Apostas (Envido) ---

@pytest.fixture
def cenario_envido():
    """Prepara instâncias limpas para testar o fluxo de apostas de envido."""
    envido = Envido()
    jogador1 = Jogador("Humano")
    jogador2 = Bot("Robô")
    
    cbr_mock = None
    dados_mock = None
    # CORREÇÃO 1: Usar um objeto Interface real em vez de None
    interface_mock = Interface() #
    
    # Cenário: J1 (Humano) tem 33 de envido. J2 (Bot) tem 25.
    jogador1.mao = [Carta(7, "OUROS"), Carta(6, "OUROS"), Carta(1, "ESPADAS")]
    jogador1.envido = jogador1.calcula_envido(jogador1.mao) # 33
    
    jogador2.mao = [Carta(5, "COPAS"), Carta(1, "COPAS"), Carta(3, "BASTOS")]
    jogador2.envido = jogador2.calcula_envido(jogador2.mao) # 25
    
    # Define o J1 como "mão"
    jogador1.primeiro = True
    jogador2.primeiro = False
    
    return envido, jogador1, jogador2, cbr_mock, dados_mock, interface_mock

# --- Testes de Fluxo de Envido (UC-03) ---

def test_envido_aceito_da_pontos_ao_vencedor(cenario_envido, monkeypatch):
    """
    Testa (UC-03 / RF15): Chamar Envido e oponente (Bot) aceitar.
    J1 tem 33, J2 tem 25. J1 deve ganhar 2 tentos.
    """
    # 1. Arrange
    envido, j1, j2, cbr, dados, iface = cenario_envido
    
    # Simula o Bot (j2) aceitando o envido
    monkeypatch.setattr(Bot, 'avaliar_envido', lambda *args: 1) # 1 = Aceitar

    # 2. Act
    # J1 (Humano) pede Envido (tipo 6)
    envido.controlador_envido(cbr, dados, 6, 1, j1, j2, iface) #

    # 3. Assert
    # O J1 (Humano) venceu o envido
    assert envido.quem_venceu_envido == 1 #
    # O J1 (Humano) deve ganhar 2 pontos (valor_envido padrão)
    assert j1.pontos == 2
    assert j2.pontos == 0

def test_envido_recusado_da_1_ponto_ao_desafiante(cenario_envido, monkeypatch):
    """
    Testa (UC-03 / RF17): Chamar Envido e oponente (Bot) recusar.
    J1 pede. J1 deve ganhar 1 tento.
    """
    # 1. Arrange
    envido, j1, j2, cbr, dados, iface = cenario_envido
    
    # Simula o Bot (j2) recusando o envido
    monkeypatch.setattr(Bot, 'avaliar_envido', lambda *args: 0) # 0 = Recusar

    # 2. Act
    # J1 (Humano) pede Envido (tipo 6)
    envido.controlador_envido(cbr, dados, 6, 1, j1, j2, iface) #

    # 3. Assert
    # Ninguém "venceu" a contagem
    assert envido.quem_venceu_envido == 0 #
    # O J2 (Bot) "fugiu"
    assert envido.quem_fugiu == 2 #
    # O J1 (Humano) que pediu ganha 1 ponto
    assert j1.pontos == 1
    assert j2.pontos == 0

def test_envido_empate_ganha_o_mao(cenario_envido, monkeypatch):
    """
    Testa (RN10): Em um empate de pontos de Envido, o jogador "Mão" ganha.
    """
    # 1. Arrange
    envido, j1, j2, cbr, dados, iface = cenario_envido
    
    # CORREÇÃO 2: Usar 'j2' em vez de 'jogador2'
    # Sobrescreve a mão do J2 para também ter 33 pontos
    j2.mao = [Carta(7, "COPAS"), Carta(6, "COPAS"), Carta(1, "BASTOS")]
    j2.envido = j2.calcula_envido(j2.mao) # 33
    
    # J1 é o "mão" (definido na fixture)
    assert j1.primeiro is True
    assert j1.envido == 33
    assert j2.envido == 33
    
    # Simula o Bot (j2) aceitando o envido
    monkeypatch.setattr(Bot, 'avaliar_envido', lambda *args: 1) # 1 = Aceitar

    # 2. Act
    # J1 (Humano) pede Envido (tipo 6)
    envido.controlador_envido(cbr, dados, 6, 1, j1, j2, iface) #

    # 3. Assert
    # O J1 (Humano) venceu por ser "mão"
    # O código em envido.py (avaliar_vencedor_envido) dá a vitória 
    # ao j1 se 'jogador1_pontos >= jogador2_pontos'
    assert envido.quem_venceu_envido == 1 #
    assert j1.pontos == 2 # Ganha os 2 pontos da aposta
    assert j2.pontos == 0


def test_flor_anula_envido_em_andamento(cenario_envido, monkeypatch):
    # 1. Arrange
    envido, j1, j2, cbr, dados, iface = cenario_envido
    
    # Criamos uma instância de Flor para gerenciar o estado da Flor
    flor = Flor()
    
    # Damos ao J2 (Bot) uma flor e simulamos ele cantando
    j2.mao = [Carta(1, "COPAS"), Carta(2, "COPAS"), Carta(3, "COPAS")]
    j2.flor = j2.checa_flor() # True
    
    # J2 (Bot) canta Flor primeiro
    flor.pedir_flor(2, j1, j2, iface)
    
    # Pré-condição: Verificamos se o Bot realmente cantou flor
    assert j2.pediu_flor is True
    assert j1.pontos == 0
    # (J2 ganha 3 pontos por cantar flor sozinho)
    assert j2.pontos == 3
    
    # Agora, simulamos o Bot (j2) aceitando qualquer Envido
    # (embora isso nem devesse ser chamado)
    monkeypatch.setattr(Bot, 'avaliar_envido', lambda *args: 1) # 1 = Aceitar

    # 2. Act
    # O J1 (Humano), ignora a Flor e tenta chamar Envido (tipo 6)
    resultado = envido.controlador_envido(cbr, dados, 6, 1, j1, j2, iface)
    
    # 3. Assert (O que DEVERIA acontecer - RN09)
    #
    # A RN09 diz que a Flor anula o Envido. Portanto, o 'controlador_envido' 
    # não deveria ter sido executado.
    # O 'resultado' deveria ser None (indicando falha na chamada), 
    # e os pontos do J1 não deveriam mudar.
    
    # Este assert VAI FALHAR, provando o bug:
    assert resultado is None 
    assert j1.pontos == 0 # J1 não deve ganhar pontos de Envido
    
    # O que realmente acontece (o bug):
    # 1. 'controlador_envido' roda.
    # 2. 'j2.avaliar_envido' (mockado) retorna 1 (Aceitar).
    # 3. 'avaliar_vencedor_envido' roda. J1 tem 33, J2 tem 21 (20+1+0).
    # 4. J1 ganha 2 pontos de Envido.
    # 5. O assert 'assert resultado is None' falha (pois resultado=True)
    # 6. O assert 'assert j1.pontos == 0' falha (pois j1.pontos=2)

    # (Adicione esta importação no topo do seu arquivo tests/test_envido.py)
# from truco.flor import Flor
# from truco.carta import Carta

def test_bot_chama_envido_mas_humano_tem_flor_e_nao_tem_opcao(cenario_envido, monkeypatch):
    """
    Testa (RN09): Bot chama Envido, mas Humano (J1) tem Flor.
    O Humano deveria poder cantar Flor, anulando o Envido.
    
    Este teste PROVA O BUG: O módulo 'envido' não dá a opção de 'Flor'
    para o humano, processando o 'Envido' ilegalmente.
    """
    # 1. Arrange
    envido, j1, j2, cbr, dados, iface = cenario_envido
    # (Não precisamos do cbr ou dados)
    
    # Damos ao J1 (Humano) uma Flor.
    # (Pontos de envido da Flor: 20 + 3 + 2 = 25)
    j1.mao = [Carta(1, "COPAS"), Carta(2, "COPAS"), Carta(3, "COPAS")]
    j1.flor = j1.checa_flor() # True
    j1.envido = j1.calcula_envido(j1.mao) # 25
    
    # Damos ao J2 (Bot) um Envido alto (mas sem flor)
    # (Pontos de envido: 20 + 7 + 6 = 33)
    j2.mao = [Carta(7, "OUROS"), Carta(6, "OUROS"), Carta(1, "ESPADAS")]
    j2.flor = j2.checa_flor() # False
    j2.envido = j2.calcula_envido(j2.mao) # 33
    
    # Simula o J1 (Humano) "Aceitando" o Envido (opção '1')
    # Esta é a única coisa que o J1 PODE fazer, pois o código
    # não oferece a opção de "Flor".
    monkeypatch.setattr('builtins.input', lambda _: '1') # 1 = Aceitar

    # 2. Act
    # O Bot (quem_pediu=2) chama Envido (tipo 6)
    envido.controlador_envido(cbr, dados, 6, 2, j1, j2, iface)

    # 3. Assert (Provando o Comportamento Incorreto)
    
    # O que DEVERIA acontecer:
    # 1. O código deveria detectar a flor de J1.
    # 2. O Envido de J2 seria anulado.
    # 3. J1 ganharia 3 pontos pela Flor.
    # (O teste correto seria: assert j1.pontos == 3 e assert j2.pontos == 0)
    
    # O que REALMENTE acontece (o bug):
    # 1. O código ignora a flor de J1.
    # 2. O 'input' (mockado para '1') faz J1 aceitar o Envido.
    # 3. O 'avaliar_vencedor_envido' é chamado.
    # 4. J2 ganha, pois 33 (Bot) > 25 (Humano).
    
    # Este assert falha (pois J1 não ganha pontos), provando o bug:
    # assert j1.pontos == 3
    
    # Este assert PASSA, provando que o bug ocorreu:
    assert j1.pontos == 0
    assert j2.pontos == 2 # J2 ganhou 2 pontos de Envido ILEGALMENTE
    assert envido.quem_venceu_envido == 2