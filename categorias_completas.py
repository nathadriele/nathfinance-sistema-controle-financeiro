"""
Lista completa de categorias do Nathfinance | Sistema de Controle Financeiro v.1
Baseado na regra 50-30-20 com estrutura hierárquica
"""

from models.categories import CategorizadorAutomatico

def exibir_todas_categorias():
    """Exibe todas as categorias organizadas por tipo"""
    categorizador = CategorizadorAutomatico()
    
    print("=" * 80)
    print("NATHFINANCE | SISTEMA DE CONTROLE FINANCEIRO V.1")
    print("CATEGORIAS COMPLETAS - REGRA 50-30-20")
    print("=" * 80)
    
    print("\n[AZUL] GASTOS ESSENCIAIS (até 50% do salário)")
    print("Despesas fixas e necessárias para manter seu padrão de vida básico")
    print("-" * 60)
    
    for categoria_principal, subcategorias in categorizador.categorias_essenciais.items():
        print(f"\n{categoria_principal.upper().replace('_', ' ')}")
        for subcategoria, palavras in subcategorias.items():
            print(f"  • {subcategoria.replace('_', ' ').title()}")
            print(f"    Palavras-chave: {', '.join(palavras)}")
    
    print("\n\n[AMARELO] GASTOS VARIÁVEIS (até 30% do salário)")
    print("Despesas relacionadas ao estilo de vida e lazer")
    print("-" * 60)
    
    for categoria_principal, subcategorias in categorizador.categorias_variaveis.items():
        print(f"\n{categoria_principal.upper().replace('_', ' ')}")
        for subcategoria, palavras in subcategorias.items():
            print(f"  • {subcategoria.replace('_', ' ').title()}")
            print(f"    Palavras-chave: {', '.join(palavras)}")
    
    print("\n\n[VERDE] INVESTIMENTOS E POUPANÇA (mínimo 20% do salário)")
    print("Recursos que contribuem para sua segurança e crescimento financeiro")
    print("-" * 60)
    
    for categoria, palavras in categorizador.categorias_investimentos.items():
        print(f"\n• {categoria.replace('_', ' ').title()}")
        print(f"  Palavras-chave: {', '.join(palavras)}")
    
    print("\n\n[VERMELHO] IMPREVISTOS E EXTRAS (fora do orçamento ideal)")
    print("Gastos que fogem do planejado, mas precisam ser controlados")
    print("-" * 60)
    
    for categoria, palavras in categorizador.categorias_imprevistos.items():
        print(f"\n• {categoria.replace('_', ' ').title()}")
        print(f"  Palavras-chave: {', '.join(palavras)}")
    
    print("\n\n[ROXO] RECEITAS (entradas de dinheiro)")
    print("Classificar os tipos de receita ajuda a entender a origem da renda")
    print("-" * 60)
    
    for categoria, palavras in categorizador.categorias_receitas.items():
        print(f"\n• {categoria.replace('_', ' ').title()}")
        print(f"  Palavras-chave: {', '.join(palavras)}")
    
    print("\n\n" + "=" * 80)
    print("RESUMO ESTATÍSTICO")
    print("=" * 80)
    
    # Contar categorias
    total_essenciais = sum(len(subcats) for subcats in categorizador.categorias_essenciais.values())
    total_variaveis = sum(len(subcats) for subcats in categorizador.categorias_variaveis.values())
    total_investimentos = len(categorizador.categorias_investimentos)
    total_imprevistos = len(categorizador.categorias_imprevistos)
    total_receitas = len(categorizador.categorias_receitas)
    
    print(f"Categorias Essenciais: {total_essenciais}")
    print(f"Categorias Variáveis: {total_variaveis}")
    print(f"Categorias de Investimento: {total_investimentos}")
    print(f"Categorias de Imprevistos: {total_imprevistos}")
    print(f"Categorias de Receitas: {total_receitas}")
    print(f"TOTAL DE CATEGORIAS: {total_essenciais + total_variaveis + total_investimentos + total_imprevistos + total_receitas}")
    
    # Contar palavras-chave
    total_palavras = 0
    for subcats in categorizador.categorias_essenciais.values():
        for palavras in subcats.values():
            total_palavras += len(palavras)
    
    for subcats in categorizador.categorias_variaveis.values():
        for palavras in subcats.values():
            total_palavras += len(palavras)
    
    for palavras in categorizador.categorias_investimentos.values():
        total_palavras += len(palavras)
    
    for palavras in categorizador.categorias_imprevistos.values():
        total_palavras += len(palavras)
    
    for palavras in categorizador.categorias_receitas.values():
        total_palavras += len(palavras)
    
    print(f"Total de palavras-chave: {total_palavras}")
    
    print("\n" + "=" * 80)
    print("DICAS DE USO")
    print("=" * 80)
    print("• O sistema classifica automaticamente baseado nas palavras-chave")
    print("• Você pode usar subcategorias, ex: Transporte > Manutenção")
    print("• Categorias são marcadas como fixas, variáveis ou investimento")
    print("• O sistema segue a regra 50-30-20 automaticamente")
    print("• Inclui campo 'Outros' para casos raros")
    print("• Imprevistos são tratados separadamente do orçamento principal")

def testar_classificacao():
    """Testa a classificação de algumas transações exemplo"""
    categorizador = CategorizadorAutomatico()
    
    print("\n\n" + "=" * 80)
    print("TESTE DE CLASSIFICAÇÃO AUTOMÁTICA")
    print("=" * 80)
    
    exemplos = [
        ("Salário Janeiro", 5000.00),
        ("Aluguel", -1200.00),
        ("Supermercado", -350.00),
        ("Cinema", -50.00),
        ("Poupança", -500.00),
        ("Veterinário", -120.00),
        ("Netflix", -45.00),
        ("Combustível", -200.00),
        ("Dividendos", 150.00),
        ("Multa de trânsito", -180.00)
    ]
    
    for descricao, valor in exemplos:
        tipo, gasto, categoria = categorizador.classificar_transacao(descricao, valor)
        print(f"'{descricao}' (R$ {valor:,.2f}) -> {tipo.value} | {gasto.value if gasto else 'N/A'} | {categoria}")

if __name__ == "__main__":
    exibir_todas_categorias()
    testar_classificacao()
