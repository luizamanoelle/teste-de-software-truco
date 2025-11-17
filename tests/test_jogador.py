# Salve como: tests/test_jogador.py
import pytest
from truco.jogador import Jogador
from truco.carta import Carta

def test_jogador_tem_3_cartas_RF03(cenario_distribuicao):
    """Testa se o jogador humano recebe 3 cartas (RF03)."""
    # A fixture cenario_distribuicao vem do conftest.py
    baralho, j1, bot = cenario_distribuicao
    
    # Ação: Jogador (j1) cria sua mão
    j1.criar_mao(baralho) 
    
    # Verifica se o jogador tem 3 cartas na mão
    assert len(j1.mao) == 3

# --- Testes de Pontuação (RN02 / RF25) ---

def test_vitoria_implementada_com_12_pontos_RF25():
    """
    Testa (RF25): Valida a condição de término (12 pontos)
    conforme implementado no __main__.py,
    embora o requisito RN02 peça 24.
    """
    jogador = Jogador("Vencedor")
    jogador.adicionar_pontos(10)
    assert jogador.retorna_pontos_totais() < 12
    
    jogador.adicionar_pontos(2)
    assert jogador.retorna_pontos_totais() == 12
    # Esta é a verificação exata que o __main__.py faz:
    assert jogador.retorna_pontos_totais() >= 12

def test_vitoria_requisito_com_24_pontos_RN02():
    """
    Testa (RN02): Valida se o jogador pode acumular 24 pontos
    (conforme o requisito), mesmo que o jogo termine antes.
    """
    jogador = Jogador("Vencedor")
    jogador.adicionar_pontos(12)
    jogador.adicionar_pontos(10)
    assert jogador.retorna_pontos_totais() == 22
    
    jogador.adicionar_pontos(2)
    assert jogador.retorna_pontos_totais() == 24
    assert jogador.retorna_pontos_totais() >= 24

# --- Testes de Cálculo de Envido (RN10) ---

@pytest.mark.parametrize("mao, pontos_esperados", [
    # (RN10) - 7 de ouros + 6 de ouros = 33 pontos
    ([Carta(7, "OUROS"), Carta(6, "OUROS"), Carta(1, "ESPADAS")], 33),
    
    # (RN10) - Figuras (10, 11, 12) valem 0
    ([Carta(12, "COPAS"), Carta(11, "COPAS"), Carta(5, "ESPADAS")], 20),
    
    # (RN10) - Sem mesmo naipe, vale a mais alta
    ([Carta(7, "OUROS"), Carta(5, "ESPADAS"), Carta(2, "BASTOS")], 7),
    
    # Caso com 3 do mesmo naipe (calcula as 2 mais altas)
    ([Carta(7, "BASTOS"), Carta(6, "BASTOS"), Carta(1, "BASTOS")], 33), # 20 + 7 + 6
])
def test_calculo_envido_RN10(mao, pontos_esperados):
    """Testa o cálculo de pontos de Envido (RN10) com vários cenários."""
    jogador = Jogador("Teste")
    pontos_envido = jogador.calcula_envido(mao)
    assert pontos_envido == pontos_esperados

# --- Testes de Detecção de Flor (RN09 / RF16) ---

def test_jogador_checa_flor_detecta_corretamente_RF16():
    """Testa (RF16): 3 cartas do mesmo naipe == True."""
    jogador = Jogador("Teste")
    jogador.mao = [Carta(1, "COPAS"), Carta(5, "COPAS"), Carta(12, "COPAS")]
    assert jogador.checa_flor() is True

def test_jogador_checa_flor_nao_detecta_incorretamente_RN09():
    """Testa (RN09): Cartas de naipes mistos == False."""
    jogador = Jogador("Teste")
    jogador.mao = [Carta(1, "COPAS"), Carta(5, "COPAS"), Carta(12, "ESPADAS")]
    assert jogador.checa_flor() is False

# --- Testes de Exceção ---

def test_jogar_carta_que_nao_esta_na_mao_levanta_excecao():
    """
    Testa (Exceção): Jogar uma carta por um índice
    que não existe na mão levanta um IndexError.
    """
    jogador = Jogador("Teste")
    jogador.mao = [Carta(1, "COPAS"), Carta(2, "OUROS"), Carta(3, "ESPADAS")]
    
    # Verifica se o código levanta 'IndexError'
    # ao tentar jogar a carta no índice 10 (que não existe)
    with pytest.raises(IndexError):
        jogador.jogar_carta(10)