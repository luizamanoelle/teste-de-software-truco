from truco.baralho import Baralho

def test_baralho_tem_40_cartas():
    # Testa o RF02 e RN06
    meu_baralho = Baralho()
    assert len(meu_baralho.cartas) == 40

def test_baralho_nao_tem_8_ou_9():
    # Testa o RN06
    meu_baralho = Baralho()
    for carta in meu_baralho.cartas:
        assert carta.numero != 8
        assert carta.numero != 9

def test_embaralhar_muda_a_ordem():
    # Testa o RF02
    baralho1 = Baralho()
    cartas_antes = list(baralho1.cartas) # Copia a lista

    baralho1.embaralhar()
    cartas_depois = baralho1.cartas

    # É estatisticamente improvável que sejam iguais após embaralhar
    assert cartas_antes != cartas_depois