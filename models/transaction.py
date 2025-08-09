"""
Modelo de transações financeiras para FinTrack360
"""

from datetime import datetime, date
from dataclasses import dataclass, field
from typing import Optional, List
import pandas as pd
from .categories import CategorizadorAutomatico, TipoTransacao, TipoGasto

@dataclass
class Transacao:
    """Classe que representa uma transação financeira"""
    data: date
    descricao: str
    valor: float
    tipo_transacao: TipoTransacao = field(init=False)
    tipo_gasto: Optional[TipoGasto] = field(init=False)
    categoria: str = field(init=False)
    recorrente: bool = False
    mes: int = field(init=False)
    semana: int = field(init=False)
    saldo_acumulado: float = field(init=False, default=0.0)
    percentual_salario: float = field(init=False, default=0.0)
    status_meta: str = field(init=False, default="")
    
    def __post_init__(self):
        """Inicialização automática após criação do objeto"""
        self.mes = self.data.month
        self.semana = self._calcular_semana()
        
        # Classificação automática
        categorizador = CategorizadorAutomatico()
        self.tipo_transacao, self.tipo_gasto, self.categoria = categorizador.classificar_transacao(
            self.descricao, self.valor
        )
    
    def _calcular_semana(self) -> int:
        """Calcula a semana do mês baseada na data"""
        primeiro_dia = self.data.replace(day=1)
        dias_diferenca = (self.data - primeiro_dia).days
        return (dias_diferenca // 7) + 1
    
    def atualizar_percentual_salario(self, salario_mensal: float):
        """Atualiza o percentual em relação ao salário mensal"""
        if salario_mensal > 0:
            self.percentual_salario = (abs(self.valor) / salario_mensal) * 100
    
    def atualizar_status_meta(self, gasto_atual_categoria: float, limite_categoria: float):
        """Atualiza o status em relação à meta 50-30-20"""
        if self.tipo_transacao == TipoTransacao.ENTRADA:
            self.status_meta = "Entrada"
        elif gasto_atual_categoria <= limite_categoria:
            self.status_meta = "OK"
        elif gasto_atual_categoria <= limite_categoria * 0.9:  # Abaixo de 90% do limite
            self.status_meta = "Abaixo da meta"
        else:
            self.status_meta = "Acima do limite"

class GerenciadorTransacoes:
    """Classe para gerenciar todas as transações"""
    
    def __init__(self):
        self.transacoes: List[Transacao] = []
        self.categorizador = CategorizadorAutomatico()
    
    def adicionar_transacao(self, data: date, descricao: str, valor: float, recorrente: bool = False) -> Transacao:
        """Adiciona uma nova transação"""
        transacao = Transacao(
            data=data,
            descricao=descricao,
            valor=valor,
            recorrente=recorrente
        )
        
        self.transacoes.append(transacao)
        self._recalcular_saldos()
        self._atualizar_metas()
        
        return transacao
    
    def obter_transacoes_mes(self, mes: int, ano: int) -> List[Transacao]:
        """Retorna transações de um mês específico"""
        return [t for t in self.transacoes 
                if t.data.month == mes and t.data.year == ano]
    
    def obter_renda_mensal(self, mes: int, ano: int) -> float:
        """Calcula a renda total do mês"""
        transacoes_mes = self.obter_transacoes_mes(mes, ano)
        renda = sum(abs(t.valor) for t in transacoes_mes
                   if t.tipo_transacao == TipoTransacao.ENTRADA)
        return float(renda)
    
    def obter_gastos_por_tipo(self, mes: int, ano: int) -> dict:
        """Retorna gastos agrupados por tipo (essencial, variável, investimento)"""
        transacoes_mes = self.obter_transacoes_mes(mes, ano)
        gastos = {
            TipoGasto.ESSENCIAL: 0.0,
            TipoGasto.VARIAVEL: 0.0,
            TipoGasto.INVESTIMENTO: 0.0
        }
        
        for transacao in transacoes_mes:
            if transacao.tipo_gasto and transacao.tipo_transacao != TipoTransacao.ENTRADA:
                gastos[transacao.tipo_gasto] += abs(transacao.valor)
        
        return gastos
    
    def obter_saldo_atual(self, mes: int, ano: int) -> float:
        """Calcula o saldo atual do mês"""
        transacoes_mes = self.obter_transacoes_mes(mes, ano)
        if not transacoes_mes:
            return 0.0
        
        # Ordenar por data para pegar o último saldo
        transacoes_ordenadas = sorted(transacoes_mes, key=lambda t: t.data)
        return transacoes_ordenadas[-1].saldo_acumulado
    
    def _recalcular_saldos(self):
        """Recalcula os saldos acumulados de todas as transações"""
        # Ordenar transações por data
        self.transacoes.sort(key=lambda t: t.data)
        
        saldo = 0.0
        for transacao in self.transacoes:
            if transacao.tipo_transacao == TipoTransacao.ENTRADA:
                saldo += transacao.valor
            else:
                saldo -= abs(transacao.valor)
            transacao.saldo_acumulado = saldo
    
    def _atualizar_metas(self):
        """Atualiza o status das metas para todas as transações"""
        # Agrupar por mês/ano
        meses = {}
        for transacao in self.transacoes:
            chave_mes = (transacao.data.year, transacao.data.month)
            if chave_mes not in meses:
                meses[chave_mes] = []
            meses[chave_mes].append(transacao)
        
        # Atualizar cada mês
        for (ano, mes), transacoes_mes in meses.items():
            renda_mensal = self.obter_renda_mensal(mes, ano)
            gastos_por_tipo = self.obter_gastos_por_tipo(mes, ano)
            
            for transacao in transacoes_mes:
                transacao.atualizar_percentual_salario(renda_mensal)
                
                if transacao.tipo_gasto:
                    limite = self.categorizador.obter_limite_categoria(transacao.tipo_gasto, renda_mensal)
                    gasto_atual = gastos_por_tipo[transacao.tipo_gasto]
                    transacao.atualizar_status_meta(gasto_atual, limite)
    
    def exportar_para_dataframe(self) -> pd.DataFrame:
        """Exporta transações para DataFrame do pandas"""
        dados = []
        for t in self.transacoes:
            dados.append({
                'Data': t.data,
                'Tipo': t.tipo_transacao.value if t.tipo_transacao else '',
                'Categoria': t.categoria,
                'Descrição': t.descricao,
                'Valor (R$)': t.valor,
                'Recorrente': 'Sim' if t.recorrente else 'Não',
                'Semana': t.semana,
                'Saldo Acumulado': t.saldo_acumulado,
                '% do Salário': f"{t.percentual_salario:.1f}%",
                'Meta 50-30-20': t.status_meta
            })
        
        return pd.DataFrame(dados)
