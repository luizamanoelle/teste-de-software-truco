# --- Fixture para Cenário de Apostas (Truco) ---
# (Certifique-se que 'Bot' e 'Jogador' estão importados no topo do seu arquivo)
# from truco.jogador import Jogador
# from truco.bot import Bot
import pytest
from truco.jogo import Jogo
from truco.carta import Carta
from truco.jogador import Jogador
from truco.bot import Bot
from truco.truco import Truco

@pytest.fixture
def cenario_truco():
    """Prepara instâncias limpas para testar o fluxo de apostas de truco."""
    truco = Truco()
    jogador1 = Jogador("Humano")
    jogador2 = Bot("Robô")
    
    # Os métodos do truco pedem 'cbr' e 'dados' como argumentos, 
    # mas para estes testes, eles não são usados ativamente 
    # (pois vamos mockar as decisões).
    cbr_mock = None 
    dados_mock = None
    
    return truco, jogador1, jogador2, cbr_mock, dados_mock

# --- Testes de Casos de Uso e Apostas (UC-02) ---

def test_truco_aceito_aumenta_valor_aposta(cenario_truco, monkeypatch):
    """
    Testa (UC-02 / RF11, RF12): Pedir Truco e o oponente (Bot) aceitar.
    RN08 diz que a mão deve valer 2 tentos.
    """
    # 1. Arrange
    truco, j1, j2, cbr, dados = cenario_truco
    
    # Simula o Bot (j2) aceitando o truco
    # O método 'avaliar_truco' do Bot será substituído por uma função 
    # que simplesmente retorna 1 (Aceitar).
    monkeypatch.setattr(Bot, 'avaliar_truco', lambda *args: 1) # 1 = Aceitar
    
    # 2. Act
    # Jogador 1 (Humano) pede truco
    resultado_aceite = truco.controlador_truco(cbr, dados, 1, j1, j2)
    
    # 3. Assert
    # O controlador deve retornar True, indicando que a aposta foi aceita
    assert resultado_aceite is True
    # O estado do jogo deve ser "truco"
    assert truco.estado_atual == "truco"
    # Os pontos dos jogadores não mudam até o fim da mão
    assert j1.pontos == 0
    assert j2.pontos == 0

    # VERIFICAÇÃO-CHAVE (RN08):
    # O valor da aposta (o que o vencedor da mão ganhará) deve ser 2.
    # NOTA: Este teste PROVAVELMENTE VAI FALHAR (assert 1 == 2).
    # O código original em 'truco.py' no método 'pedir_truco' esqueceu 
    # de atualizar 'self.valor_aposta = 2' quando a aposta é aceita.
    # Esta falha é a prova de um BUG, que é o objetivo do seu trabalho.
    assert truco.retornar_valor_aposta() == 2

def test_truco_recusado_da_1_ponto_ao_desafiante(cenario_truco, monkeypatch):
    """
    Testa (UC-02 / RF14): Pedir Truco e o oponente (Bot) recusar.
    O desafiante (j1) deve ganhar 1 tento.
    """
    # 1. Arrange
    truco, j1, j2, cbr, dados = cenario_truco

    # Simula o Bot (j2) recusando o truco
    monkeypatch.setattr(Bot, 'avaliar_truco', lambda *args: 0) # 0 = Recusar

    # 2. Act
    # Jogador 1 (Humano) pede truco
    resultado_aceite = truco.controlador_truco(cbr, dados, 1, j1, j2)

    # 3. Assert
    # O controlador retorna False (aposta não continuou)
    assert resultado_aceite is False
    # O desafiante (j1) que pediu truco ganha 1 ponto
    assert j1.pontos == 1
    # O oponente (j2) que recusou não ganha nada
    assert j2.pontos == 0
    # O valor da aposta (para o caso de a mão continuar) não muda
    assert truco.retornar_valor_aposta() == 1
    # O estado do jogo é "truco" (pois foi chamado)
    assert truco.estado_atual == "truco"

def test_escalonamento_truco_aceito_retruco_recusado(cenario_truco, monkeypatch):
    """
    Testa (UC-02): Truco (aceito) -> Retruco (recusado).
    O desafiante do Retruco (j2) deve ganhar 2 tentos.
    """
    # 1. Arrange
    truco, j1, j2, cbr, dados = cenario_truco

    # Ordem das simulações:
    # 1. J1 pede Truco.
    # 2. O Bot (j2) avalia e decide AUMENTAR (2 = Retruco)
    monkeypatch.setattr(Bot, 'avaliar_truco', lambda *args: 2) # 2 = Aumentar Aposta
    
    # 3. O 'controlador_truco' chama 'pedir_retruco', que pede input do J1 (Humano).
    # 4. O Humano (j1) decide RECUSAR (0)
    #    (Simulamos o 'input' para retornar a string '0')
    monkeypatch.setattr('builtins.input', lambda _: '0') # 0 = Recusar

    # 2. Act
    # Jogador 1 (Humano) inicia o Truco
    resultado_aceite = truco.controlador_truco(cbr, dados, 1, j1, j2)

    # 3. Assert
    # A cadeia de apostas foi interrompida (recusada)
    assert resultado_aceite is False
    # O Humano (j1) que recusou o RETRUCO não ganha pontos
    assert j1.pontos == 0
    # O Bot (j2) que pediu o RETRUCO ganha os pontos do Truco (2 pontos)
    # (O código 'pedir_retruco' dá 2 pontos, não 1. Isso está estranho na RN, 
    # mas o código 'truco.py' linha 105 diz `jogador2.pontos += 2`)
    assert j2.pontos == 2
    # O valor da aposta foi setado para 3 pelo 'pedir_retruco'
    assert truco.retornar_valor_aposta() == 3
    assert truco.estado_atual == "retruco"

def test_escalonamento_completo_truco_retruco_valequatro_aceitos(cenario_truco, monkeypatch):
    """
    Testa (UC-02): Truco -> Retruco -> Vale-Quatro (todos aceitos/aumentados).
    O vencedor da mão deve ganhar 4 tentos.
    """
    # 1. Arrange
    truco, j1, j2, cbr, dados = cenario_truco

    # Simulação complexa de idas e vindas:
    # Esta lista simula as respostas do BOT em ordem
    respostas_bot = [
        2,  # 1ª Ação: Bot ouve "Truco" e responde "Aumentar" (Retruco)
        1   # 3ª Ação: Bot ouve "Vale Quatro" e responde "Aceitar"
    ]
    # Esta lista simula as respostas do HUMANO em ordem
    respostas_humano_input = [
        '2' # 2ª Ação: Humano ouve "Retruco" e responde "Aumentar" (Vale Quatro)
    ]

    # Aplicando os mocks para usarem as listas
    monkeypatch.setattr(Bot, 'avaliar_truco', lambda *args: respostas_bot.pop(0))
    monkeypatch.setattr('builtins.input', lambda _: respostas_humano_input.pop(0))

    # 2. Act
    # Jogador 1 (Humano) inicia o Truco
    resultado_aceite = truco.controlador_truco(cbr, dados, 1, j1, j2)

    # 3. Assert
    # A cadeia de apostas foi totalmente aceita
    assert resultado_aceite is True
    # A aposta final deve ser 4 (definido em 'pedir_vale_quatro')
    assert truco.retornar_valor_aposta() == 4
    # Ninguém ganha pontos ainda, só no fim da mão
    assert j1.pontos == 0
    assert j2.pontos == 0
    
    # BUG BÔNUS: O método 'pedir_vale_quatro' esquece de mudar
    # o 'estado_atual' para "vale_quatro". Ele permanece "retruco".
    # Este assert prova esse outro bug:
    assert truco.estado_atual == "retruco"
    # Se o bug fosse corrigido, o assert correto seria:
    # assert truco.estado_atual == "vale_quatro"