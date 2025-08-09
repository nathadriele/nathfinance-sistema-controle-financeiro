"""
Utilitários para cálculos financeiros do FinTrack360
"""

from datetime import datetime, date
from typing import Dict, List, Tuple
from models.categories import TipoGasto, TipoTransacao
from models.transaction import GerenciadorTransacoes, Transacao

class CalculadoraFinanceira:
    """Classe responsável pelos cálculos financeiros e análises"""
    
    def __init__(self, gerenciador: GerenciadorTransacoes):
        self.gerenciador = gerenciador
    
    def calcular_distribuicao_50_30_20(self, mes: int, ano: int) -> Dict[str, Dict[str, float]]:
        """
        Calcula a distribuição atual vs ideal da regra 50-30-20
        
        Returns:
            Dict com valores ideais, reais e diferenças
        """
        renda_mensal = self.gerenciador.obter_renda_mensal(mes, ano)
        gastos_por_tipo = self.gerenciador.obter_gastos_por_tipo(mes, ano)
        
        # Valores ideais
        ideal_essencial = renda_mensal * 0.50
        ideal_variavel = renda_mensal * 0.30
        ideal_investimento = renda_mensal * 0.20
        
        # Valores reais
        real_essencial = gastos_por_tipo[TipoGasto.ESSENCIAL]
        real_variavel = gastos_por_tipo[TipoGasto.VARIAVEL]
        real_investimento = gastos_por_tipo[TipoGasto.INVESTIMENTO]
        
        return {
            'essencial': {
                'ideal': ideal_essencial,
                'real': real_essencial,
                'diferenca': ideal_essencial - real_essencial,
                'percentual_ideal': 50.0,
                'percentual_real': (real_essencial / renda_mensal * 100) if renda_mensal > 0 else 0
            },
            'variavel': {
                'ideal': ideal_variavel,
                'real': real_variavel,
                'diferenca': ideal_variavel - real_variavel,
                'percentual_ideal': 30.0,
                'percentual_real': (real_variavel / renda_mensal * 100) if renda_mensal > 0 else 0
            },
            'investimento': {
                'ideal': ideal_investimento,
                'real': real_investimento,
                'diferenca': ideal_investimento - real_investimento,
                'percentual_ideal': 20.0,
                'percentual_real': (real_investimento / renda_mensal * 100) if renda_mensal > 0 else 0
            },
            'renda_total': renda_mensal
        }
    
    def gerar_alertas(self, mes: int, ano: int) -> List[Dict[str, str]]:
        """Gera alertas baseados nas metas 50-30-20"""
        distribuicao = self.calcular_distribuicao_50_30_20(mes, ano)
        alertas = []
        
        # Verificar gastos essenciais
        if distribuicao['essencial']['real'] > distribuicao['essencial']['ideal']:
            excesso = distribuicao['essencial']['real'] - distribuicao['essencial']['ideal']
            alertas.append({
                'tipo': 'warning',
                'categoria': 'Gastos Essenciais',
                'mensagem': f"Você está gastando R$ {excesso:.2f} a mais que o recomendado (50%) em gastos essenciais.",
                'recomendacao': "Revise seus gastos fixos e procure alternativas mais econômicas."
            })
        
        # Verificar gastos variáveis
        if distribuicao['variavel']['real'] > distribuicao['variavel']['ideal']:
            excesso = distribuicao['variavel']['real'] - distribuicao['variavel']['ideal']
            alertas.append({
                'tipo': 'warning',
                'categoria': 'Gastos Variáveis',
                'mensagem': f"Você está gastando R$ {excesso:.2f} a mais que o recomendado (30%) em gastos variáveis.",
                'recomendacao': "Reduza gastos com lazer, compras e outros itens não essenciais."
            })
        
        # Verificar investimentos
        if distribuicao['investimento']['real'] < distribuicao['investimento']['ideal']:
            falta = distribuicao['investimento']['ideal'] - distribuicao['investimento']['real']
            alertas.append({
                'tipo': 'info',
                'categoria': 'Investimentos',
                'mensagem': f"Você ainda precisa investir R$ {falta:.2f} para atingir a meta de 20%.",
                'recomendacao': "Considere automatizar seus investimentos ou aumentar o valor mensal."
            })
        
        # Verificar se está no caminho certo
        if (distribuicao['essencial']['real'] <= distribuicao['essencial']['ideal'] and
            distribuicao['variavel']['real'] <= distribuicao['variavel']['ideal'] and
            distribuicao['investimento']['real'] >= distribuicao['investimento']['ideal']):
            alertas.append({
                'tipo': 'success',
                'categoria': 'Parabéns!',
                'mensagem': "Você está seguindo perfeitamente a regra 50-30-20!",
                'recomendacao': "Continue assim e mantenha o controle dos seus gastos."
            })
        
        return alertas
    
    def calcular_evolucao_saldo(self, mes: int, ano: int) -> List[Dict[str, any]]:
        """Calcula a evolução do saldo ao longo do mês"""
        transacoes_mes = self.gerenciador.obter_transacoes_mes(mes, ano)
        transacoes_ordenadas = sorted(transacoes_mes, key=lambda t: t.data)
        
        evolucao = []
        for transacao in transacoes_ordenadas:
            evolucao.append({
                'data': transacao.data,
                'saldo': transacao.saldo_acumulado,
                'descricao': transacao.descricao,
                'valor': transacao.valor,
                'tipo': transacao.tipo_transacao.value
            })
        
        return evolucao
    
    def calcular_gastos_por_categoria(self, mes: int, ano: int) -> Dict[str, float]:
        """Calcula gastos detalhados por categoria específica"""
        transacoes_mes = self.gerenciador.obter_transacoes_mes(mes, ano)
        gastos_categoria = {}
        
        for transacao in transacoes_mes:
            if transacao.tipo_transacao != TipoTransacao.ENTRADA:
                categoria = transacao.categoria
                if categoria not in gastos_categoria:
                    gastos_categoria[categoria] = 0.0
                gastos_categoria[categoria] += abs(transacao.valor)
        
        return gastos_categoria
    
    def calcular_kpis_mensais(self, mes: int, ano: int) -> Dict[str, float]:
        """Calcula os principais KPIs do mês"""
        renda_mensal = self.gerenciador.obter_renda_mensal(mes, ano)
        gastos_por_tipo = self.gerenciador.obter_gastos_por_tipo(mes, ano)
        saldo_atual = self.gerenciador.obter_saldo_atual(mes, ano)

        total_gastos = sum(gastos_por_tipo.values())
        economia_mensal = renda_mensal - total_gastos

        return {
            'renda_mensal': float(renda_mensal),
            'total_gastos': float(total_gastos),
            'saldo_atual': float(saldo_atual),
            'economia_mensal': float(economia_mensal),
            'gastos_essenciais': float(gastos_por_tipo[TipoGasto.ESSENCIAL]),
            'gastos_variaveis': float(gastos_por_tipo[TipoGasto.VARIAVEL]),
            'investimentos': float(gastos_por_tipo[TipoGasto.INVESTIMENTO]),
            'percentual_gasto': float((total_gastos / renda_mensal * 100) if renda_mensal > 0 else 0)
        }
    
    def detectar_transacoes_recorrentes(self) -> List[Tuple[str, List[Transacao]]]:
        """Detecta padrões de transações recorrentes"""
        # Agrupar por descrição similar
        grupos_descricao = {}
        
        for transacao in self.gerenciador.transacoes:
            # Simplificar descrição para detectar padrões
            descricao_simples = self._simplificar_descricao(transacao.descricao)
            
            if descricao_simples not in grupos_descricao:
                grupos_descricao[descricao_simples] = []
            grupos_descricao[descricao_simples].append(transacao)
        
        # Identificar grupos com múltiplas ocorrências
        recorrentes = []
        for descricao, transacoes in grupos_descricao.items():
            if len(transacoes) >= 2:  # Pelo menos 2 ocorrências
                # Verificar se ocorrem em meses diferentes
                meses = set((t.data.year, t.data.month) for t in transacoes)
                if len(meses) >= 2:
                    recorrentes.append((descricao, transacoes))
        
        return recorrentes
    
    def _simplificar_descricao(self, descricao: str) -> str:
        """Simplifica descrição para detectar padrões"""
        # Remover números, datas e caracteres especiais
        import re
        descricao_limpa = re.sub(r'\d+', '', descricao.lower())
        descricao_limpa = re.sub(r'[^\w\s]', '', descricao_limpa)
        return descricao_limpa.strip()
