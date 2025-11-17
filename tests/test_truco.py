# Salve como: tests/test_truco.py
import pytest
from truco.bot import Bot
from truco.truco import Truco # Necessário para o monkeypatch
import types

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

def test_truco_init_estado_inicial_correto():
    """
    Testa (Objetivo: Retorno de Função / __init__):
    Verifica se a classe Truco é instanciada com os valores padrão corretos.
    """
    # 1. Arrange / Act
    truco = Truco()
    
    # 3. Assert
    assert truco.valor_aposta == 1
    assert truco.estado_atual == ""
    assert truco.jogador_bloqueado == 0

@pytest.mark.parametrize("estado_inicial, estado_esperado", [
    (1, 2), # Se 1, vira 2
    (2, 1), # Se 2 (ou 0, ou qualquer outro), vira 1
])
def test_inverter_jogador_bloqueado_alterna_corretamente(estado_inicial, estado_esperado):
    """
    Testa (Objetivo: Testes para if's):
    Verifica os dois caminhos da lógica de 'inverter_jogador_bloqueado'.
   
    """
    # 1. Arrange
    truco = Truco()
    truco.jogador_bloqueado = estado_inicial
    
    # 2. Act
    truco.inverter_jogador_bloqueado()
    
    # 3. Assert
    assert truco.jogador_bloqueado == estado_esperado

def test_resetar_limpa_o_estado_do_truco():
    """
    Testa (Objetivo: Retorno de Função):
    Verifica se 'resetar' retorna o objeto ao seu estado padrão
    após ter sido "poluído" (modificado).
   
    """
    # 1. Arrange (Poluir o estado)
    truco = Truco()
    truco.valor_aposta = 4
    truco.estado_atual = "vale_quatro"
    truco.jogador_bloqueado = 1
    truco.jogador_pediu = 1
    
    # 2. Act
    truco.resetar() # O SUT (System Under Test)
    
    # 3. Assert (Verificar se voltou ao padrão)
    assert truco.valor_aposta == 1
    assert truco.estado_atual == ""
    # Nota: 'jogador_bloqueado' e 'jogador_pediu'
    # não são resetados pelo SUT, provando um bug/comportamento.
    assert truco.jogador_bloqueado == 0 # Este campo não é resetado no SUT
    assert truco.jogador_pediu == 0    # Este campo não é resetado no SUT

def test_controlador_truco_bloqueia_se_estado_for_vale_quatro(cenario_truco):
    """
    Testa (Objetivo: Testes para if's):
    Verifica a "guarda" que impede novas apostas se o jogo já
    está em "vale_quatro".
   
    """
    # 1. Arrange
    truco, j1, j2, cbr, dados = cenario_truco
    truco.estado_atual = "vale_quatro" # Define o estado
    
    # 2. Act
    resultado = truco.controlador_truco(cbr, dados, 1, j1, j2)
    
    # 3. Assert
    # O 'if' deve retornar None
    assert resultado is None

def test_controlador_truco_bloqueia_se_jogador_pediu_duas_vezes(cenario_truco):
    """
    Testa (Objetivo: Testes para if's):
    Verifica a "guarda" que impede o mesmo jogador de pedir
    um aumento seguidamente ('jogador_bloqueado').
   
    """
    # 1. Arrange
    truco, j1, j2, cbr, dados = cenario_truco
    truco.jogador_bloqueado = 1 # Bloqueia o Jogador 1
    
    # 2. Act
    # O Jogador 1 (bloqueado) tenta pedir
    resultado = truco.controlador_truco(cbr, dados, 1, j1, j2)
    
    # 3. Assert
    # O 'if' deve retornar None
    assert resultado is None

def test_retornar_quem_fugiu_retorna_um_metodo_em_vez_de_valor(cenario_truco):
    """
    Testa (Objetivo: Testes para Exceções / Bugs):
    Identifica o bug onde 'retornar_quem_fugiu' retorna
    o próprio objeto do método (um 'callable') em vez de um valor,
    devido à falta de parênteses no 'return'.
   
    """
    # 1. Arrange
    truco, j1, j2, cbr, dados = cenario_truco
    
    # 2. Act
    resultado = truco.retornar_quem_fugiu()
    
    # 3. Assert
    # O teste passa se o 'resultado' for um objeto chamável (um método)
    assert callable(resultado)
    # Verificação ainda mais estrita (opcional, mas boa):
    assert isinstance(resultado, types.MethodType)

def test_pedir_truco_loop_de_input_invalido_depois_valido(cenario_truco, monkeypatch):
    """
    Testa (Objetivo: Início e Fim de Loopings):
    Verifica se o 'while' do input (no Humano, quem_pediu=2)
    rejeita um input numérico inválido ('9') e depois
    aceita um válido ('1').
   
    """
    # 1. Arrange
    truco, j1, j2, cbr, dados = cenario_truco
    
    # Simula o Humano digitando '9' (inválido) e depois '1' (Aceitar)
    inputs_usuario = ['9', '1']
    monkeypatch.setattr('builtins.input', lambda _: inputs_usuario.pop(0))
    
    # 2. Act
    # Chamamos com 'quem_pediu=2' para acionar o 'input' do Humano
    resultado = truco.pedir_truco(cbr, 2, j1, j2)
    
    # 3. Assert
    # O loop deve ter rodado duas vezes e retornado True (do '1')
    assert resultado is True
    # A lista de inputs deve estar vazia
    assert len(inputs_usuario) == 0

def test_pedir_retruco_input_nao_numerico_levanta_valueerror(cenario_truco, monkeypatch):
    """
    Testa (Objetivo: Testes para Exceções / Input de Usuário):
    Verifica se o 'int(input())' em 'pedir_retruco'
    levanta 'ValueError' se o usuário digitar "abc".
   
    """
    # 1. Arrange
    truco, j1, j2, cbr, dados = cenario_truco
    
    # Simula o Humano digitando "abc" (não-numérico)
    monkeypatch.setattr('builtins.input', lambda _: 'abc')
    
    # 2. Act / 3. Assert
    # O teste passa se 'ValueError' for levantado
    with pytest.raises(ValueError):
        # Chamamos com 'quem_pediu=2' para acionar o 'input' do Humano
        truco.pedir_retruco(cbr, 2, j1, j2)

def test_pedir_vale_quatro_input_nao_numerico_levanta_valueerror(cenario_truco, monkeypatch):
    """
    Testa (Objetivo: Testes para Exceções / Input de Usuário):
    Verifica se o 'int(input())' em 'pedir_vale_quatro'
    levanta 'ValueError' se o usuário digitar "abc".
   
    """
    # 1. Arrange
    truco, j1, j2, cbr, dados = cenario_truco
    
    # Simula o Humano digitando "abc" (não-numérico)
    monkeypatch.setattr('builtins.input', lambda _: 'abc')
    
    # 2. Act / 3. Assert
    # O teste passa se 'ValueError' for levantado
    with pytest.raises(ValueError):
        # Chamamos com 'quem_pediu=2' para acionar o 'input' do Humano
        truco.pedir_vale_quatro(cbr, 2, j1, j2)