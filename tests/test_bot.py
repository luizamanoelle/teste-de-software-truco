# Salve como: tests/test_bot.py
import pytest
from truco.carta import Carta

# Teste de Distribuição (RF03)
def test_bot_tem_3_cartas_RF03(cenario_distribuicao):
    baralho, j1, bot = cenario_distribuicao
    
    # Ação: Bot cria sua mão
    bot.criar_mao(baralho) 
    
    # Verifica se o bot tem 3 cartas na mão
    assert len(bot.mao) == 3

# Adicione estes testes ao seu arquivo tests/test_bot.py
# (Lembre de importar 'Carta' no topo: from truco.carta import Carta)

# Adicione estes testes ao seu arquivo tests/test_bot.py
# (Lembre de importar 'Carta' no topo: from truco.carta import Carta)

def test_bot_avalia_envido_passa_pontos_corretos_ao_cbr_RF20(cenario_main, monkeypatch):
    """
    Testa (RF20): Se o Bot (avaliar_envido)
    corretamente passa seus próprios pontos de envido para o CBR.
    """
    # 1. Arrange
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # Damos ao Bot (j2) uma mão conhecida
    j2.mao = [Carta(7, "OUROS"), Carta(6, "OUROS"), Carta(1, "ESPADAS")]
    j2.envido = j2.calcula_envido(j2.mao) # 33 pontos
    
    assert j2.envido == 33 # Garante que a pontuação é 33

    # 2. Act
    # Criamos um "Espião" (Spy) para capturar os argumentos
    # enviados para a função 'cbr.envido'
    captured_args = {}
    def spy_cbr_envido(tipo, quem_pediu, pontos_bot, perdendo):
        captured_args['tipo'] = tipo
        captured_args['quem_pediu'] = quem_pediu
        captured_args['pontos_bot'] = pontos_bot
        return 1 # Retorna "Aceitar"
            
    # Substituímos a função 'cbr.envido' pelo nosso "Espião"
    monkeypatch.setattr(cbr, 'envido', spy_cbr_envido)
    
    # O Bot (j2) avalia uma chamada de Envido (tipo 6)
    j2.avaliar_envido(cbr, 6, 1, 0) 
    
    # 3. Assert
    # O Bot passou seus 33 pontos para o CBR?
    assert captured_args['pontos_bot'] == 33


def test_bot_avalia_truco_passa_qualidade_mao_ao_cbr_RF20(cenario_main, monkeypatch):
    """
    Testa (RF20): Se o Bot (avaliar_truco)
    corretamente passa a 'qualidade_mao' para o CBR.
    """
    # 1. Arrange
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # Definimos um valor conhecido para a qualidade da mão
    j2.qualidade_mao = 123.45
    
    # 2. Act
    # Criamos um "Espião" (Spy) para capturar os argumentos
    # enviados para a função 'cbr.truco'
    captured_args = {}
    def spy_cbr_truco(tipo, quem_pediu, qualidade):
        captured_args['tipo'] = tipo
        captured_args['qualidade'] = qualidade
        return 1 # Retorna "Aceitar"
    
    monkeypatch.setattr(cbr, 'truco', spy_cbr_truco)

    # O Bot (j2) avalia uma chamada de Truco
    j2.avaliar_truco(cbr, "truco", 1)

    # 3. Assert
    # O Bot passou a qualidade da mão correta para o CBR?
    assert captured_args['qualidade'] == 123.45