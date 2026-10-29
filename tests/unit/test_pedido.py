import pytest
from unittest.mock import MagicMock
from pedido.pedido import Item, Pedido, contar_frete_gratis


# =============================================================
# EXEMPLO — um teste pronto, para você copiar o formato
# =============================================================

def test_exemplo_quantidade_total(pedido_pequeno):
    # 1 café + 2 pães de queijo = 3 unidades
    assert pedido_pequeno.quantidade_total() == 3


# =============================================================
# PARTE 1 — Encontre os bugs
# Escreva um teste para cada bug. Cada teste deve FALHAR
# no código original. Não altere src/pedido/pedido.py ainda.
# =============================================================

def test_bug1_subtotal_considera_quantidade(pedido_pequeno):
    # 1 café (6,00) + 2 pães de queijo (2 x 4,50) = 15,00
    assert pedido_pequeno.subtotal() == 15.0


def test_bug2_item_mais_barato_retorna_menor_preco(pedido_pequeno):
    # café custa 6,00 e o pão de queijo 4,50 → o mais barato é o pão de queijo
    assert pedido_pequeno.item_mais_barato().nome == "Pão de queijo"


def test_bug3_total_com_desconto_subtrai_o_desconto():
    # quantidade 1 para o bug do subtotal não interferir
    # 100,00 com 10% de desconto = 90,00
    pedido = Pedido("Carla", [Item("Combo", 100.0, 1)])
    assert pedido.total_com_desconto(10) == 90.0


def test_bug4_frete_gratis_com_subtotal_exatamente_50():
    # valor-limite: a partir de 50,00 (inclusive) o frete é grátis
    pedido = Pedido("Carla", [Item("Combo", 50.0, 1)])
    assert pedido.tem_frete_gratis() is True



# =============================================================
# PARTE 2 — Implemente com TDD
# Siga o ciclo: 🔴 escreva o teste → 🟢 implemente → 🟡 refatore
# =============================================================

# Requisito 1 — contar_frete_gratis(pedidos) -> int
# Escreva os testes ANTES de implementar a função

def test_contar_frete_gratis_todos_com_frete_gratis(pedido_grande):
    # pedido_grande: 73,00 / combo: exatamente 50,00 → os 2 têm frete grátis
    pedido_50 = Pedido("Carla", [Item("Combo", 50.0, 1)])
    assert contar_frete_gratis([pedido_grande, pedido_50]) == 2


def test_contar_frete_gratis_nenhum_com_frete_gratis(pedido_pequeno):
    # pedido_pequeno: 15,00 / combo: 49,99 (logo abaixo do limite) → nenhum tem frete grátis
    pedido_49 = Pedido("Carla", [Item("Combo", 49.99, 1)])
    assert contar_frete_gratis([pedido_pequeno, pedido_49]) == 0


def test_contar_frete_gratis_lista_mista(pedido_pequeno, pedido_grande):
    # pedido_grande (73,00) e combo (50,00) têm frete grátis; pedido_pequeno (15,00) não
    pedido_50 = Pedido("Carla", [Item("Combo", 50.0, 1)])
    assert contar_frete_gratis([pedido_pequeno, pedido_grande, pedido_50]) == 2


def test_contar_frete_gratis_lista_vazia():
    assert contar_frete_gratis([]) == 0



# Requisito 2 — situacao(unidades_indisponiveis) -> str
# Escreva os testes ANTES de implementar o método

def test_situacao_cancelado_mesmo_com_frete_gratis(pedido_grande):
    # pedido_grande: 5 unidades, 73,00 (frete grátis); 2 indisponíveis = 40% > 25%
    assert pedido_grande.situacao(2) == "Cancelado por falta de estoque"


def test_situacao_confirmado_com_frete_gratis(pedido_grande):
    # pedido_grande: 73,00 (frete grátis) e nenhuma unidade indisponível
    assert pedido_grande.situacao(0) == "Confirmado com frete grátis"


def test_situacao_confirmado_sem_frete_gratis(pedido_pequeno):
    # pedido_pequeno: 15,00 (sem frete grátis) e nenhuma unidade indisponível
    assert pedido_pequeno.situacao(0) == "Confirmado"


def test_situacao_exatamente_25_porcento_segue_para_o_frete():
    # 4 unidades, 60,00 (frete grátis); 1 indisponível = exatamente 25% → não cancela
    pedido = Pedido("Carla", [Item("Combo", 15.0, 4)])
    assert pedido.situacao(1) == "Confirmado com frete grátis"


def test_situacao_pouco_acima_de_25_porcento_cancela():
    # 7 unidades, 70,00 (frete grátis); 2 indisponíveis ≈ 28,6% > 25% → cancela
    pedido = Pedido("Carla", [Item("Combo", 10.0, 7)])
    assert pedido.situacao(2) == "Cancelado por falta de estoque"



# Requisito 3 — sugerir_frete_gratis(sms_service) -> None
# Use MagicMock para simular o serviço de SMS
# Escreva os testes ANTES de implementar o método

def test_sugerir_frete_gratis_abaixo_de_50_envia_sms(pedido_pequeno):
    # pedido_pequeno: 15,00 → faltam 35,00 para o frete grátis
    sms_service = MagicMock()

    pedido_pequeno.sugerir_frete_gratis(sms_service)

    sms_service.enviar.assert_called_once_with("Bruno", 35.0)
