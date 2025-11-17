# Salve como: tests/test_baralho.py
import pytest
from truco.baralho import Baralho
from truco.carta import Carta

@pytest.fixture
def baralho():
    """Fornece um baralho novo para cada teste."""
    return Baralho()

def test_baralho_tem_40_cartas_RN06(baralho: Baralho):
    # Testa o RF02 e RN06
    assert len(baralho.cartas) == 40

def test_baralho_nao_tem_8_ou_9_RN06(baralho: Baralho):
    # Testa o RN06
    for carta in baralho.cartas:
        assert carta.numero != 8
        assert carta.numero != 9

def test_embaralhar_muda_a_ordem_RF02(baralho: Baralho):
    # Testa o RF02
    cartas_antes = [f"{c.numero}{c.naipe}" for c in baralho.cartas] # Copia a lista

    baralho.embaralhar()
    cartas_depois = [f"{c.numero}{c.naipe}" for c in baralho.cartas]

    # Garante que os baralhos contêm as mesmas cartas
    assert set(cartas_antes) == set(cartas_depois)
    # Garante que a ordem mudou (estatisticamente muito provável)
    assert cartas_antes != cartas_depois

def test_garantir_que_cartas_nao_se_repetem_RNF04(baralho):
    """
    Testa (RNF04): Garante que as cartas não se repetem.
    Verifica se as 40 cartas no baralho são únicas.
    """
    
    # 1. Arrange
    # A fixture 'baralho' já vem com 
    # as 40 cartas criadas pela função 'criar_baralho'
    
    # 2. Act
    # Criamos uma representação em string de cada carta (ex: "7-OUROS")
    # (Os objetos 'Carta'
    # em si não são 'hashable' para um 'set')
    representacao_cartas = [f"{c.numero}-{c.naipe}" for c in baralho.cartas]
    
    # 3. Assert
    # Verificamos se o número total de cartas é 40
    assert len(representacao_cartas) == 40
    
    # Verificamos se o número de cartas ÚNICAS (usando um 'set') também é 40
    assert len(set(representacao_cartas)) == 40