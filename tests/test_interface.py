# Salve como: tests/test_interface.py

import pytest
from truco.jogador import Jogador
from truco.carta import Carta
from truco.interface import Interface

@pytest.fixture
def iface_e_jogadores():
    """Fornece uma interface limpa e jogadores para testes de placar."""
    iface = Interface()
    
    # Usamos classes genéricas, pois não precisamos da lógica do Jogo/Bot
    class MockJogador:
        def __init__(self, nome):
            self.nome = nome
            
    j1 = MockJogador("Humano")
    j2 = MockJogador("Robô")
    return iface, j1, j2

def test_jogador_mostra_mao_RF04(capsys):
    """
    Testa (RF04): Se as cartas do jogador são exibidas corretamente.
    
    Este teste chama 'jogador.mostrar_mao()', que é a função
    usada pelo '__main__.py' para mostrar as opções ao humano
   .
    """
    # 1. Arrange
    j1 = Jogador("Humano")
    iface = Interface()
    # Damos ao J1 uma mão conhecida
    j1.mao = [Carta(7, "OUROS"), Carta(1, "ESPADAS")]

    # 2. Act
    # O método 'mostrar_mao'
    # chama 'carta.exibir_carta'
    j1.mostrar_mao(iface) 

    # 3. Assert
    captured = capsys.readouterr() # Captura o print()
    
    # Verifica se a saída do console contém as cartas
    assert "[0] 7 de OUROS" in captured.out
    assert "[1] 1 de ESPADAS" in captured.out

def test_interface_mostrar_carta_jogada(capsys):
    """Testa se a carta jogada é exibida."""
    iface = Interface()
    carta = Carta(7, "ESPADAS")
    iface.mostrar_carta_jogada("Humano", carta)
    captured = capsys.readouterr()
    assert "Humano jogou a carta: 7 de ESPADAS" in captured.out

def test_interface_placar_envido_RF24(iface_e_jogadores, capsys):
    """Testa (RF24): Exibição do placar do Envido."""
    iface, j1, j2 = iface_e_jogadores
    
    # Testa a vitória do J1
    iface.mostrar_vencedor_envido(1, j1.nome, 33, j2.nome, 25)
    captured_j1 = capsys.readouterr()
    assert "Venceu o envido com 33 pontos" in captured_j1.out
    assert "PERDEU o envido com 25 pontos" in captured_j1.out
    
    # Testa a vitória do J2
    iface.mostrar_vencedor_envido(2, j1.nome, 25, j2.nome, 33)
    captured_j2 = capsys.readouterr()
    assert "Venceu o envido com 33 pontos" in captured_j2.out
    assert "PERDEU o envido com 25 pontos" in captured_j2.out

def test_interface_placar_flor_RF24(iface_e_jogadores, capsys):
    """Testa (RF24): Exibição do placar da Flor."""
    iface, j1, j2 = iface_e_jogadores
    
    iface.mostrar_vencedor_flor(1, j1.nome, j2.nome, 3)
    captured = capsys.readouterr()
    assert "Jogador 1 - Humano: Venceu a flor e ganhou 3 pontos" in captured.out

def test_interface_placar_rodadas(iface_e_jogadores, capsys):
    """Testa a exibição do placar de vazas/rodadas."""
    iface, j1, j2 = iface_e_jogadores
    
    iface.mostrar_placar_rodadas(j1.nome, 2, j2.nome, 1)
    captured = capsys.readouterr()
    assert "Humano: Venceu 2 Rodada(s)" in captured.out
    assert "Robô: Venceu 1 Rodada(s)" in captured.out

def test_interface_placar_total(iface_e_jogadores, capsys):
    """Testa (RF24): Exibição do placar total (mão)."""
    iface, j1, j2 = iface_e_jogadores
    
    iface.mostrar_placar_total(j1.nome, 10, j2.nome, 4)
    captured = capsys.readouterr()
    assert "Humano: 10 Pontos Acumulados" in captured.out
    assert "Robô: 4 Pontos Acumulados" in captured.out

def test_interface_placar_desistencia_RF09(iface_e_jogadores, capsys):
    """Testa (RF09): Exibição da desistência ('Ir ao Monte')."""
    iface, j1, j2 = iface_e_jogadores
    
    iface.mostrar_placar_total_jogador_fugiu(j1, j1.nome, 10, j2.nome, 12)
    captured = capsys.readouterr()
    
    # Testa a mensagem de desistência
    assert "Jogador Humano fugiu!" in captured.out
    
    # O código original em 'interface.py' (linha 50)
    # comenta a exibição do placar total, então testamos se 
    # o placar NÃO foi exibido.
    assert "Pontos Acumulados" not in captured.out

# Em: tests/test_interface.py
# (Adicione este teste no final do arquivo)

def test_interface_mensagem_erro_truco_repetido(iface_e_jogadores, capsys):
    """
    Testa (Mensagem de Erro): Se a interface exibe a mensagem
    correta quando o jogador tenta pedir truco novamente.
    [Requisito: Testes para mensagens de erro]
    """
    # 1. Arrange
    iface, j1, j2 = iface_e_jogadores

    # 2. Act
    # Chama a função específica da interface
    iface.mostrar_pediu_truco(j1.nome)

    # 3. Assert
    captured = capsys.readouterr()
    
    # Verifica se a mensagem de erro correta foi impressa
    assert "Humano pediu truco e o pedido já foi aceito, escolha outra jogada!" in captured.out