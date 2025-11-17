import pytest
import pandas as pd
import numpy as np
from unittest import mock
from truco.dados import Dados
from truco.cbr import Cbr
from sklearn.neighbors import NearestNeighbors
import sklearn.neighbors._unsupervised 


# Mock do Dataset (garantindo colunas e indices para os filtros)
DATASET_MOCK = pd.DataFrame({
    'col1': [1, 2], 'col2': [3, 4],
    'quemGanhouTruco': [2, 1], 'quemRetruco': [2, 1], 'qualidadeMaoHumano': [100.0, 150.0],
    'pontosEnvidoRobo': [33, 25], 'pontosEnvidoHumano': [25, 33], 'quemGanhouEnvido': [2, 1],
    'quemPediuRealEnvido': [1, 1], 'quemPediuFaltaEnvido': [1, 1],
    'ganhadorPrimeiraRodada': [2, 1], 'ganhadorSegundaRodada': [2, 2], 'ganhadorTerceiraRodada': [1, 2],
    'terceiraCartaRobo': [10, 5], 'segundaCartaRobo': [5, 15], 'primeiraCartaRobo': [1, 1]
}).set_index(pd.Index([0, 1], name='idMao'))

# simula a classe dados (lida c  a leitura de arquivos e registros do jogo)
class MockDados:
    def retornar_casos(self):
        #nao le arquivos reais, retorna o mock
        return DATASET_MOCK.copy()
    def retornar_registro(self):
        return pd.Series([0] * len(DATASET_MOCK.columns), index=DATASET_MOCK.columns)

# simula a classe nbrs (vizinhos proximos)
class MockNbrs:
    def fit(self, X):
        return self
    def kneighbors(self, X):
        #nao faz calculos reais, retorna indices fixos
        #ignora a matematica real, só pra testar a logica do cbr
        return np.array([[0.0, 0.0]]), np.array([[0, 1]])


@pytest.fixture
# substitui dados reais pelo mock
def cbr(monkeypatch):
    """injeta os mocks antes de ele ser criado"""
    
    with mock.patch('truco.cbr.Dados', MockDados):
        # Mock do vizinhos_proximos para injetar MockNbrs
        monkeypatch.setattr('truco.cbr.Cbr.vizinhos_proximos', lambda self, df=None: MockNbrs())
        return Cbr()

@pytest.fixture
def dados():
    """Retorna uma instância de Dados (original)."""
    return Dados()


def test_vizinhos_proximos(cbr, dados):
    """
    ao chamar vizinhos_proximos, retorna o essencial. contrato de interface entra cbr e as dependencias.

    """

    #verifica se o retorno possui um metodo o uatributo esperado
    assert hasattr(cbr.vizinhos_proximos(None), 'kneighbors') #dados historicos
    assert hasattr(cbr.vizinhos_proximos(None), 'fit') #treinamento

def test_cbr(cbr, dados):
    """
    apos criar o cbr, seus atributos estao corretos.
    
    """

    #foi inicializado corretamente com 0
    assert cbr.indice == 0
    # dataset corretos como pandas dataframe, ve se o carregamento funcionou
    assert isinstance(cbr.dataset, pd.core.frame.DataFrame)
    #confirma que vizinhos proximos foi chamado e o atributo nbrs foi criado
    assert hasattr(cbr.nbrs, 'kneighbors') 

def test_carregar_dataset(cbr, dados, monkeypatch):
    """Verifica se carregar_dataset limpa e formata o DataFrame corretamente."""
    
    #(Arrange: Cria df_raw e mock_read_csv)
    df_raw = pd.DataFrame({
        'idMao': [1], 'naipeCartaRobo': ['ESPADAS'], 'naipeCartaHumano': ['OURO'], 'outra_col': ['NULL']
    }).set_index('idMao')
    
    def mock_read_csv(*args, **kwargs):
        return df_raw.copy()
    
    #substitui a função real pelo mock, forçando o uso do df_raw que tem dados sujos
    monkeypatch.setattr('truco.cbr.pd.read_csv', mock_read_csv)
    
    #Act: chama o metodo que carrega e limpa o dataset
    df = cbr.carregar_dataset()
    
    #Assert: verifica se o df retornado esta limpo e formatado
    #espadas que vale 1 e ouro que vale 2
    #garante que as strings originais não estão mais no df
    assert isinstance(df, pd.core.frame.DataFrame)
    assert df.index.name == "idMao"
    
    assert 1 in df['naipeCartaRobo'].values
    assert 2 in df['naipeCartaHumano'].values
    assert "ESPADAS" not in df.values
    assert "OURO" not in df.values
    assert "BASTOS" not in df.values
    assert "COPAS" not in df.values


def test_truco(cbr):
    """
    valida a lofica de tomada de decisao do cbr ao receber truco.
    """
    # Qualidade 200.0 >> Humano 150/100. Deve retornar 2 (Aumentar)
    #assume que que a mao forte e o historico são favoraveis vencidas > perdidas e qualidade bot>
    assert cbr.truco(1, 2, 200.0) == 2 
    
    # Bot tem qualidade 3.0 < Humano. Deve retornar 0 (Fugir)
    #cai no else final de return 0
    assert cbr.truco(1, 2, 3.0) == 0 
    
    # Testando outros dois caminhos (não agressivos)
    assert cbr.truco(2, 1, 0) == 0
    assert cbr.truco(2, 2, 3.0) == 0

@pytest.mark.xfail(reason="BUG de LÓGICA: Cbr.jogar_carta falha em encontrar o índice da carta mais próxima. Retorna o índice 0 em vez do correto (índice 4 ou 1).")
def test_jogar_carta(cbr):
 # o bot deve usar min(pontuacao_cartas, key=lambda x:abs(x-valor_referencia))
 #pra encontrar a carta q mais se aproxima do valor referencia

    """
    Verifica a decisão do CBR ao jogar carta.
    """

    #o valor referencia do mock é 10, a carta mais proxima eh 5 (indice 4)
    # Esperado 4, mas retorna 0.
    assert cbr.jogar_carta(3, [1, 2, 3, 4, 5]) == 4 
    
    # Estes devem passar pois retorna 0
    assert cbr.jogar_carta(1, [1, 2, 3]) == 0
    assert cbr.jogar_carta(1, [1, 2, 3, 4, 5]) == 0
    
    # Esperado 1, mas retorna 0.
    assert cbr.jogar_carta(2, [1, 2, 3, 4, 5]) == 1

@pytest.mark.xfail(reason="BUG de LÓGICA: Cbr.envido retorna 6 em cenários agressivos devido à comparação de IDs, pulando o IF do 'return 7'.")
def test_envido(cbr):
    """
    Verifica a decisão do CBR ao receber Envido.
    """
    #O Bot tem mão boa E está perdendo o jogo (robo_perdendo=True). Deve ser o mais agressivo.
    assert cbr.envido(0, 2, 6, True) == 8 
    #O Bot (quem_pediu=2) tem 6 pontos de Envido (uma mão "boa"). Ele deve ser agressivo.
    assert cbr.envido(0, 2, 6, False) == 7 
    
    #O Bot está respondendo a um Envido (tipo=6).
    assert cbr.envido(6, 1, 0, True) == 1 
    assert cbr.envido(6, 1, -3, True) == 1
    assert cbr.envido(6, 1, 100, True) == 1
    
    #O Bot tem uma mão excelente (pontos=100) e deve aceitar um Real Envido (tipo=7).
    assert cbr.envido(7, 1, 0, False) == 0 
    assert cbr.envido(7, 1, 100, False) == 1