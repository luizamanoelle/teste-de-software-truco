import pytest
from truco.bot import Bot
from truco.baralho import Baralho

@pytest.fixture
def cenario_bot_distribuicao():
    baralho_teste = Baralho()
    bot_teste = Bot("Robô")
    
    # Ação: Bot cria sua mão
    bot_teste.criar_mao(baralho_teste) #
    
    return bot_teste

# Teste de Distribuição (RF03)
def test_bot_tem_3_cartas(cenario_bot_distribuicao):
    bot = cenario_bot_distribuicao
    
    # Verifica se o bot tem 3 cartas na mão
    assert len(bot.mao) == 3