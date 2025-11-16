import pytest
from truco.jogador import Jogador
from truco.bot import Bot
from truco.baralho import Baralho

# Esta fixture prepara o cenário de distribuição
@pytest.fixture
def cenario_distribuicao():
    baralho_teste = Baralho()
    jogador_teste = Jogador("Humano")
    bot_teste = Bot("Robô")
    
    # Ação: Jogador e Bot criam suas mãos
    jogador_teste.criar_mao(baralho_teste) #
    bot_teste.criar_mao(baralho_teste)     #
    
    return baralho_teste, jogador_teste, bot_teste

# Teste de Distribuição (RF03)
def test_jogador_tem_3_cartas(cenario_distribuicao):
    _, jogador, _ = cenario_distribuicao
    
    # Verifica se o jogador tem 3 cartas na mão
    assert len(jogador.mao) == 3

# Teste de Distribuição (RF03)
def test_baralho_fica_com_34_cartas_apos_distribuicao(cenario_distribuicao):
    baralho, _, _ = cenario_distribuicao
    
    # 40 cartas iniciais - 3 (jogador) - 3 (bot) = 34
    assert len(baralho.cartas) == 34

# (Adicione ao final de test_jogador.py, 
#  lembre de importar Jogador se ainda não o fez no topo)
# from truco.jogador import Jogador 

# --- Testes de Vitória e Pontuação (RN04) ---

def test_jogo_termina_com_24_pontos():
    # [ ] Testar se o jogo termina (verifica vitória, RF25) 
    #     quando um jogador atinge 24 pontos.
    jogador = Jogador("Vencedor")
    
    # 1. Arrange: Adiciona pontos em partes
    jogador.adicionar_pontos(12)
    jogador.adicionar_pontos(10)
    
    # 2. Act: Verifica antes de atingir o limite
    assert jogador.retorna_pontos_totais() == 22
    assert jogador.retorna_pontos_totais() < 24
    
    # Adiciona os pontos finais para chegar a 24
    jogador.adicionar_pontos(2) #
    
    # 3. Assert: Verifica a condição de término
    total_pontos = jogador.retorna_pontos_totais() #
    assert total_pontos == 24
    assert total_pontos >= 24

from truco.jogador import Jogador 

# (Coloque perto de outros testes do Jogador, se houver, 
#  ou adicione o import do Jogador no topo do arquivo)

def test_jogador_atinge_12_pontos_para_vitoria():
    # Este teste valida a condição de término (RF25)
    # conforme implementado no __main__.py (12 pontos).
    
    # 1. Arrange (Preparar)
    jogador = Jogador("Vencedor")
    
    # Adiciona 10 pontos
    jogador.adicionar_pontos(10) #
    
    # 2. Act (Executar)
    # Verifica o estado antes de atingir o limite
    assert jogador.retorna_pontos_totais() < 12 #
    
    # Adiciona os pontos finais para cruzar o limite
    jogador.adicionar_pontos(2)
    
    # 3. Assert (Verificar)
    # Verifica se o total de pontos é 12
    assert jogador.retorna_pontos_totais() == 12
    
    # Esta é a verificação exata que o __main__.py faz:
    assert jogador.retorna_pontos_totais() >= 12