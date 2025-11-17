# Salve como: tests/test_dados.py

import pytest
import pandas as pd
from truco.dados import Dados
from truco.jogador import Jogador
from truco.bot import Bot
import os

@pytest.fixture
def cenario_dados(monkeypatch):
    """Prepara um cenário para testar a classe Dados."""
    
    TEST_CSV = "test_jogadas.csv"
    dados = Dados()
    j1 = Jogador("Humano")
    j2 = Bot("Robô")
    
    # --- ESTA É A CORREÇÃO ---
    # 1. Salva a função original 'to_csv'
    original_to_csv = pd.DataFrame.to_csv
    
    # 2. Cria uma "espiã" que salva no nosso TEST_CSV
    def mock_to_csv(df_self, path_or_buf, *args, **kwargs):
        # Se o código tentar salvar em "jogadas.csv",
        # nós o interceptamos e salvamos em "test_jogadas.csv"
        if path_or_buf == "jogadas.csv":
            # Chama a função original, mas com o nome do arquivo trocado
            original_to_csv(df_self, TEST_CSV, *args, **kwargs)
        else:
            # Senão, apenas chama a função original
            original_to_csv(df_self, path_or_buf, *args, **kwargs)

    # 3. Substitui a função 'to_csv' do pandas pela nossa "espiã"
    monkeypatch.setattr(pd.DataFrame, 'to_csv', mock_to_csv)
    # -------------------------

    # Garante que o arquivo de teste esteja limpo antes
    if os.path.exists(TEST_CSV):
        os.remove(TEST_CSV)
    
    yield dados, j1, j2, TEST_CSV
    
    # Limpeza: Remove o arquivo de teste depois
    if os.path.exists(TEST_CSV):
        os.remove(TEST_CSV)

def test_registrar_resultado_salva_pontuacao_final_RF26(cenario_dados):
    """
    Testa (RF26): Se a pontuação final e o vencedor são salvos.
    
    Este teste FALHA (xfail) porque o autor confirmou
    que o __main__ não atualiza a classe Dados
    antes de salvar.
    """
    # 1. Arrange
    dados, j1, j2, TEST_CSV = cenario_dados
    j1.pontos = 12
    j2.pontos = 5
    
    # 2. Act
    # O 'mock_to_csv' intercepta esta chamada
    dados.finalizar_partida() #

    # 3. Assert (Provando o Bug)
    assert os.path.exists(TEST_CSV)
    df = pd.read_csv(TEST_CSV)

    # --- CORREÇÃO DO TESTE ---
    # O IndexError acontece se o CSV estiver vazio.
    # Vamos verificar se o DataFrame está vazio.
    if df.empty:
        # Se estiver vazio, forçamos a falha no assert que queremos (RF26)
        # "O DataFrame está vazio, mas deveria ter uma linha com 12 pontos."
        # Usamos '0' como o 'valor real' que veio do CSV vazio.
        assert 0 == 12, "O DataFrame 'df' está vazio. O __main__ não salvou dados."

    # Se o DataFrame não estiver vazio (ex: salvou a linha padrão com 0s):
    last_row = df.iloc[-1]
    
    # O que DEVERIA acontecer (Requisito RF26):
    # (Estes asserts vão falhar, provando o bug)
    assert last_row["pontosHumano"] == 12
    assert last_row["pontosRobo"] == 5