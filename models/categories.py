"""
Sistema de categorização automática para Nathfinance
Baseado na regra 50-30-20
"""

from enum import Enum
from typing import Dict, List, Optional
import unicodedata

class TipoGasto(Enum):
    ESSENCIAL = "essencial"      # 50%
    VARIAVEL = "variavel"        # 30%
    INVESTIMENTO = "investimento" # 20%

class TipoTransacao(Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"
    INVESTIMENTO = "investimento"

class CategorizadorAutomatico:
    """Classe responsável pela categorização automática de transações"""

    def __init__(self):
        # Estrutura completa de categorias essenciais (50%)
        self.categorias_essenciais = {
            'moradia': {
                'aluguel': ['aluguel'],
                'condominio': ['condominio'],
                'iptu': ['iptu', 'imposto predial'],
                'financiamento': ['financiamento imobiliario', 'financiamento casa', 'financiamento'],
                'contas_domesticas': ['energia eletrica', 'luz', 'agua', 'esgoto', 'gas', 'internet', 'celular', 'plano celular', 'telefone']
            },
            'alimentacao': {
                'supermercado': ['supermercado', 'mercado'],
                'feiras': ['feira', 'hortifruti'],
                'mercearia': ['mercearia', 'padaria', 'acougue']
            },
            'transporte': {
                'combustivel': ['combustivel', 'gasolina', 'etanol', 'diesel'],
                'transporte_publico': ['onibus', 'metro', 'trem', 'transporte publico'],
                'estacionamento': ['estacionamento', 'zona azul'],
                'impostos_veiculo': ['ipva', 'licenciamento'],
                'seguro_veiculo': ['seguro carro', 'seguro veiculo'],
                'manutencao_veiculo': ['manutencao carro', 'oficina', 'pneu', 'oleo', 'revisao']
            },
            'saude': {
                'plano_saude': ['plano saude', 'convenio medico'],
                'consultas': ['medico', 'dentista', 'consulta'],
                'medicamentos': ['farmacia', 'medicamento', 'remedio'],
                'exames': ['exame', 'laboratorio']
            },
            'educacao_essencial': {
                'mensalidade': ['escola', 'faculdade', 'universidade', 'mensalidade'],
                'material_escolar': ['material escolar', 'livro didatico'],
                'transporte_escolar': ['transporte escolar', 'van escolar']
            },
            'filhos': {
                'fraldas': ['fralda', 'fraldas'],
                'escola_infantil': ['creche', 'berçario'],
                'pediatra': ['pediatra', 'medico crianca']
            }
        }
        
        # Estrutura completa de categorias variáveis (30%)
        self.categorias_variaveis = {
            'lazer_entretenimento': {
                'cinema_teatro': ['cinema', 'teatro', 'show', 'espetaculo'],
                'viagens': ['viagem', 'hotel', 'passagem', 'turismo'],
                'restaurantes': ['restaurante', 'delivery', 'ifood', 'lanche'],
                'bares': ['bar', 'balada', 'pub'],
                'assinaturas': ['netflix', 'spotify', 'amazon prime', 'youtube premium', 'disney plus', 'assinatura']
            },
            'compras_pessoais': {
                'roupas_calcados': ['roupa', 'sapato', 'tenis', 'calcado', 'vestuario'],
                'eletronicos': ['celular', 'notebook', 'tablet', 'eletronico', 'gadget'],
                'cosmeticos': ['cosmetico', 'perfume', 'maquiagem', 'creme']
            },
            'pets': {
                'racao': ['racao', 'comida pet'],
                'veterinario': ['veterinario', 'vet'],
                'vacinas': ['vacina pet', 'vacina animal'],
                'petshop': ['petshop', 'banho tosa', 'tosa']
            },
            'cuidados_pessoais': {
                'academia': ['academia', 'musculacao', 'personal'],
                'cabelo': ['cabelo', 'cabeleireiro', 'barbearia', 'salao'],
                'estetica': ['estetica', 'manicure', 'pedicure', 'massagem']
            },
            'educacao_opcional': {
                'cursos_livres': ['curso livre', 'workshop', 'seminario'],
                'livros_extras': ['livro', 'revista', 'jornal']
            },
            'presentes_datas': {
                'aniversarios': ['aniversario', 'festa aniversario'],
                'natal': ['natal', 'ceia natal'],
                'presentes_gerais': ['presente', 'gift', 'lembranca']
            },
            'casa_manutencao': {
                'utensilios': ['utensilio', 'panela', 'copo', 'prato'],
                'decoracao': ['decoracao', 'quadro', 'vaso', 'enfeite'],
                'reparos_menores': ['reparo', 'conserto menor', 'manutencao casa']
            }
        }
        
        # Estrutura completa de investimentos (20%)
        self.categorias_investimentos = {
            'poupanca': ['poupanca', 'conta poupanca'],
            'tesouro_direto': ['tesouro direto', 'tesouro', 'titulo publico'],
            'renda_fixa': ['cdb', 'lci', 'lca', 'renda fixa'],
            'acoes': ['acoes', 'acao', 'bolsa', 'bovespa', 'b3'],
            'criptomoedas': ['bitcoin', 'crypto', 'criptomoeda', 'btc', 'ethereum'],
            'previdencia_privada': ['previdencia privada', 'vgbl', 'pgbl', 'previdencia'],
            'fundos_imobiliarios': ['fii', 'fundos imobiliarios', 'fundo imobiliario'],
            'cofrinho_digital': ['cofrinho', 'picpay', 'nubank cofrinho'],
            'reserva_emergencia': ['reserva emergencia', 'emergencia', 'reserva'],
            'cursos_profissionalizantes': ['mba', 'pos graduacao', 'curso profissionalizante'],
            'dividendos': ['dividendo', 'reinvestimento', 'jcp']
        }

        # Categorias de imprevistos (fora do orçamento)
        self.categorias_imprevistos = {
            'multas': ['multa', 'infracao', 'multa transito'],
            'reparos_inesperados': ['reparo inesperado', 'conserto urgente', 'emergencia casa', 'emergencia carro'],
            'despesas_juridicas': ['advogado', 'juridico', 'processo'],
            'perdas_furtos': ['furto', 'roubo', 'perda'],
            'emergencias_medicas': ['emergencia medica', 'hospital urgencia', 'uti'],
            'juros_multas': ['juro', 'multa atraso', 'atraso pagamento']
        }
        
        # Categorias de receitas (entradas)
        self.categorias_receitas = {
            'salario_fixo': ['salario', 'salario clt', 'ordenado'],
            'renda_variavel': ['freelance', 'freela', 'comissao', 'bonus'],
            'renda_passiva': ['aluguel recebido', 'dividendo recebido', 'renda passiva'],
            'auxilios_beneficios': ['auxilio', 'beneficio', 'inss', 'aposentadoria'],
            'restituicao': ['restituicao', 'reembolso', 'devolucao'],
            'vendas_avulsas': ['venda', 'marketplace', 'brecho', 'venda avulsa'],
            'premiacoes': ['premiacao', 'premio', 'sorteio'],
            'decimo_terceiro': ['13 salario', '13º', 'decimo terceiro'],
            'ferias': ['ferias', 'terco ferias']
        }

        # Palavras-chave para entradas (compatibilidade)
        self.palavras_entrada = ['salario', 'freelance', 'bonus', 'renda extra', 'venda', 'receita', 'entrada', 'dividendo recebido', 'aluguel recebido']
    
    def _normalizar_texto(self, texto: str) -> str:
        """Remove acentos e normaliza texto para comparação"""
        texto_normalizado = unicodedata.normalize('NFD', texto.lower())
        return ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')

    def classificar_transacao(self, descricao: str, valor: float) -> tuple[TipoTransacao, TipoGasto, str]:
        """
        Classifica uma transação baseada na descrição usando estrutura hierárquica

        Returns:
            tuple: (tipo_transacao, tipo_gasto, categoria_especifica)
        """
        descricao_normalizada = self._normalizar_texto(descricao)

        # Verificar se é entrada (valor positivo indica entrada)
        if valor > 0:
            categoria_receita = self._encontrar_categoria_receita(descricao_normalizada)
            return TipoTransacao.ENTRADA, None, categoria_receita

        # Verificar se é entrada baseada em palavras-chave (mesmo com valor negativo em alguns casos)
        if any(self._normalizar_texto(palavra) in descricao_normalizada for palavra in self.palavras_entrada):
            categoria_receita = self._encontrar_categoria_receita(descricao_normalizada)
            return TipoTransacao.ENTRADA, None, categoria_receita

        # Verificar investimentos primeiro (prioridade alta)
        categoria_investimento = self._encontrar_categoria_investimento(descricao_normalizada)
        if categoria_investimento:
            if valor < 0:  # Saída para investimento
                return TipoTransacao.INVESTIMENTO, TipoGasto.INVESTIMENTO, categoria_investimento
            else:  # Entrada de investimento (resgate)
                return TipoTransacao.ENTRADA, None, categoria_investimento

        # Verificar imprevistos
        categoria_imprevisto = self._encontrar_categoria_imprevisto(descricao_normalizada)
        if categoria_imprevisto:
            return TipoTransacao.SAIDA, TipoGasto.VARIAVEL, f"imprevisto_{categoria_imprevisto}"

        # Verificar gastos essenciais
        categoria_essencial = self._encontrar_categoria_essencial(descricao_normalizada)
        if categoria_essencial:
            return TipoTransacao.SAIDA, TipoGasto.ESSENCIAL, categoria_essencial

        # Verificar gastos variáveis
        categoria_variavel = self._encontrar_categoria_variavel(descricao_normalizada)
        if categoria_variavel:
            return TipoTransacao.SAIDA, TipoGasto.VARIAVEL, categoria_variavel

        # Se não encontrou categoria específica, classificar como variável por padrão
        return TipoTransacao.SAIDA, TipoGasto.VARIAVEL, 'outros'
    
    def obter_limite_categoria(self, tipo_gasto: TipoGasto, renda_mensal: float) -> float:
        """Retorna o limite recomendado para cada tipo de gasto"""
        if tipo_gasto == TipoGasto.ESSENCIAL:
            return renda_mensal * 0.50
        elif tipo_gasto == TipoGasto.VARIAVEL:
            return renda_mensal * 0.30
        elif tipo_gasto == TipoGasto.INVESTIMENTO:
            return renda_mensal * 0.20
        return 0.0
    
    def _encontrar_categoria_receita(self, descricao_normalizada: str) -> str:
        """Encontra categoria específica de receita"""
        for categoria, palavras in self.categorias_receitas.items():
            if any(self._normalizar_texto(palavra) in descricao_normalizada for palavra in palavras):
                return categoria
        return 'renda_geral'

    def _encontrar_categoria_investimento(self, descricao_normalizada: str) -> str:
        """Encontra categoria específica de investimento"""
        for categoria, palavras in self.categorias_investimentos.items():
            if any(self._normalizar_texto(palavra) in descricao_normalizada for palavra in palavras):
                return categoria
        return None

    def _encontrar_categoria_imprevisto(self, descricao_normalizada: str) -> str:
        """Encontra categoria específica de imprevisto"""
        for categoria, palavras in self.categorias_imprevistos.items():
            if any(self._normalizar_texto(palavra) in descricao_normalizada for palavra in palavras):
                return categoria
        return None

    def _encontrar_categoria_essencial(self, descricao_normalizada: str) -> str:
        """Encontra categoria específica essencial"""
        for categoria_principal, subcategorias in self.categorias_essenciais.items():
            for subcategoria, palavras in subcategorias.items():
                if any(self._normalizar_texto(palavra) in descricao_normalizada for palavra in palavras):
                    return f"{categoria_principal}_{subcategoria}"
        return None

    def _encontrar_categoria_variavel(self, descricao_normalizada: str) -> str:
        """Encontra categoria específica variável"""
        for categoria_principal, subcategorias in self.categorias_variaveis.items():
            for subcategoria, palavras in subcategorias.items():
                if any(self._normalizar_texto(palavra) in descricao_normalizada for palavra in palavras):
                    return f"{categoria_principal}_{subcategoria}"
        return None

    def obter_todas_categorias(self) -> Dict[str, List[str]]:
        """Retorna todas as categorias organizadas por tipo"""
        categorias = {
            'essenciais': [],
            'variaveis': [],
            'investimentos': [],
            'receitas': [],
            'imprevistos': []
        }

        # Categorias essenciais
        for cat_principal, subcats in self.categorias_essenciais.items():
            for subcat in subcats.keys():
                categorias['essenciais'].append(f"{cat_principal}_{subcat}")

        # Categorias variáveis
        for cat_principal, subcats in self.categorias_variaveis.items():
            for subcat in subcats.keys():
                categorias['variaveis'].append(f"{cat_principal}_{subcat}")

        # Investimentos
        categorias['investimentos'] = list(self.categorias_investimentos.keys())

        # Receitas
        categorias['receitas'] = list(self.categorias_receitas.keys())

        # Imprevistos
        categorias['imprevistos'] = list(self.categorias_imprevistos.keys())

        return categorias

    def adicionar_categoria_personalizada(self, tipo_gasto: TipoGasto, categoria: str, palavras_chave: List[str]):
        """Permite adicionar categorias personalizadas"""
        if tipo_gasto == TipoGasto.ESSENCIAL:
            # Para essenciais, adicionar como nova subcategoria em 'outros'
            if 'outros' not in self.categorias_essenciais:
                self.categorias_essenciais['outros'] = {}
            self.categorias_essenciais['outros'][categoria] = palavras_chave
        elif tipo_gasto == TipoGasto.VARIAVEL:
            # Para variáveis, adicionar como nova subcategoria em 'outros'
            if 'outros' not in self.categorias_variaveis:
                self.categorias_variaveis['outros'] = {}
            self.categorias_variaveis['outros'][categoria] = palavras_chave
        elif tipo_gasto == TipoGasto.INVESTIMENTO:
            self.categorias_investimentos[categoria] = palavras_chave
