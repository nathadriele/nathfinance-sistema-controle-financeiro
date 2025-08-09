"""
Componentes de gráficos e visualizações para FinTrack360
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List
from models.categories import TipoGasto
from utils.calculations import CalculadoraFinanceira

class GeradorGraficos:
    """Classe responsável por gerar todos os gráficos do dashboard"""
    
    def __init__(self):
        # Cores do tema
        self.cores = {
            'essencial': '#FF6B6B',    # Vermelho suave
            'variavel': '#4ECDC4',     # Verde água
            'investimento': '#45B7D1', # Azul
            'entrada': '#96CEB4',      # Verde claro
            'fundo': '#F8F9FA',        # Cinza claro
            'texto': '#2C3E50'         # Azul escuro
        }
    
    def criar_grafico_pizza_distribuicao(self, distribuicao: Dict) -> go.Figure:
        """Cria gráfico de pizza com distribuição 50-30-20"""
        
        valores = [
            distribuicao['essencial']['real'],
            distribuicao['variavel']['real'],
            distribuicao['investimento']['real']
        ]
        
        labels = ['Essenciais (50%)', 'Variáveis (30%)', 'Investimentos (20%)']
        cores = [self.cores['essencial'], self.cores['variavel'], self.cores['investimento']]
        
        # Calcular percentuais reais
        total = sum(valores)
        percentuais = [f"{(v/total*100):.1f}%" if total > 0 else "0%" for v in valores]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=valores,
            hole=0.4,
            marker_colors=cores,
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>' +
                         'Valor: R$ %{value:,.2f}<br>' +
                         'Percentual: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': 'Distribuição de Gastos - Regra 50-30-20',
                'x': 0.5,
                'font': {'size': 18, 'color': self.cores['texto']}
            },
            font={'size': 12},
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=60, b=60, l=20, r=20),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        return fig
    
    def criar_grafico_barras_metas(self, distribuicao: Dict) -> go.Figure:
        """Cria gráfico de barras comparando metas vs realizado"""
        
        categorias = ['Essenciais', 'Variáveis', 'Investimentos']
        valores_ideais = [
            distribuicao['essencial']['ideal'],
            distribuicao['variavel']['ideal'],
            distribuicao['investimento']['ideal']
        ]
        valores_reais = [
            distribuicao['essencial']['real'],
            distribuicao['variavel']['real'],
            distribuicao['investimento']['real']
        ]
        
        fig = go.Figure()
        
        # Barras dos valores ideais
        fig.add_trace(go.Bar(
            name='Meta (50-30-20)',
            x=categorias,
            y=valores_ideais,
            marker_color='lightgray',
            opacity=0.7,
            hovertemplate='<b>%{x}</b><br>Meta: R$ %{y:,.2f}<extra></extra>'
        ))
        
        # Barras dos valores reais
        cores_barras = [self.cores['essencial'], self.cores['variavel'], self.cores['investimento']]
        fig.add_trace(go.Bar(
            name='Realizado',
            x=categorias,
            y=valores_reais,
            marker_color=cores_barras,
            hovertemplate='<b>%{x}</b><br>Realizado: R$ %{y:,.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': 'Metas vs Realizado',
                'x': 0.5,
                'font': {'size': 18, 'color': self.cores['texto']}
            },
            xaxis_title='Categorias',
            yaxis_title='Valor (R$)',
            barmode='group',
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=60, b=80, l=60, r=20),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        return fig
    
    def criar_grafico_evolucao_saldo(self, evolucao: List[Dict]) -> go.Figure:
        """Cria gráfico de linha com evolução do saldo"""
        
        if not evolucao:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum dado disponível",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            return fig
        
        datas = [item['data'] for item in evolucao]
        saldos = [item['saldo'] for item in evolucao]
        
        # Criar cores baseadas no saldo (verde para positivo, vermelho para negativo)
        cores_linha = ['green' if s >= 0 else 'red' for s in saldos]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=datas,
            y=saldos,
            mode='lines+markers',
            name='Saldo',
            line=dict(color=self.cores['investimento'], width=3),
            marker=dict(size=6, color=self.cores['investimento']),
            hovertemplate='<b>Data:</b> %{x}<br>' +
                         '<b>Saldo:</b> R$ %{y:,.2f}<br>' +
                         '<extra></extra>'
        ))
        
        # Adicionar linha zero
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title={
                'text': 'Evolução do Saldo Mensal',
                'x': 0.5,
                'font': {'size': 18, 'color': self.cores['texto']}
            },
            xaxis_title='Data',
            yaxis_title='Saldo (R$)',
            margin=dict(t=60, b=60, l=60, r=20),
            paper_bgcolor='white',
            plot_bgcolor='white',
            hovermode='x unified'
        )
        
        return fig
    
    def criar_grafico_gastos_categoria(self, gastos_categoria: Dict[str, float]) -> go.Figure:
        """Cria gráfico de barras horizontais com gastos por categoria"""
        
        if not gastos_categoria:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum gasto registrado",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            return fig
        
        # Ordenar categorias por valor
        categorias_ordenadas = sorted(gastos_categoria.items(), key=lambda x: x[1], reverse=True)
        categorias = [item[0] for item in categorias_ordenadas]
        valores = [item[1] for item in categorias_ordenadas]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=valores,
            y=categorias,
            orientation='h',
            marker_color=self.cores['variavel'],
            hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': 'Gastos por Categoria',
                'x': 0.5,
                'font': {'size': 18, 'color': self.cores['texto']}
            },
            xaxis_title='Valor (R$)',
            yaxis_title='Categorias',
            margin=dict(t=60, b=60, l=120, r=20),
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=max(400, len(categorias) * 30)  # Altura dinâmica
        )
        
        return fig
    
    def criar_kpi_cards(self, kpis: Dict[str, float]) -> List[Dict]:
        """Cria dados para os cards de KPI"""
        
        cards_data = [
            {
                'titulo': 'Renda Mensal',
                'valor': f"R$ {kpis['renda_mensal']:,.2f}",
                'cor': 'success',
                'icone': 'R$'
            },
            {
                'titulo': 'Total Gastos',
                'valor': f"R$ {kpis['total_gastos']:,.2f}",
                'cor': 'danger',
                'icone': '-'
            },
            {
                'titulo': 'Investimentos',
                'valor': f"R$ {kpis['investimentos']:,.2f}",
                'cor': 'info',
                'icone': '+'
            },
            {
                'titulo': 'Saldo Atual',
                'valor': f"R$ {kpis['saldo_atual']:,.2f}",
                'cor': 'success' if kpis['saldo_atual'] >= 0 else 'danger',
                'icone': '='
            }
        ]
        
        return cards_data
    
    def criar_grafico_comparativo_mensal(self, dados_mensais: List[Dict]) -> go.Figure:
        """Cria gráfico comparativo entre meses"""
        
        if not dados_mensais:
            fig = go.Figure()
            fig.add_annotation(
                text="Dados insuficientes para comparação",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            return fig
        
        meses = [f"{d['ano']}-{d['mes']:02d}" for d in dados_mensais]
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Receitas vs Gastos', 'Distribuição por Tipo'),
            vertical_spacing=0.1
        )
        
        # Gráfico 1: Receitas vs Gastos
        receitas = [d['renda'] for d in dados_mensais]
        gastos = [d['total_gastos'] for d in dados_mensais]
        
        fig.add_trace(
            go.Bar(name='Receitas', x=meses, y=receitas, marker_color=self.cores['entrada']),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name='Gastos', x=meses, y=gastos, marker_color=self.cores['essencial']),
            row=1, col=1
        )
        
        # Gráfico 2: Distribuição por tipo
        essenciais = [d['essenciais'] for d in dados_mensais]
        variaveis = [d['variaveis'] for d in dados_mensais]
        investimentos = [d['investimentos'] for d in dados_mensais]
        
        fig.add_trace(
            go.Bar(name='Essenciais', x=meses, y=essenciais, marker_color=self.cores['essencial']),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(name='Variáveis', x=meses, y=variaveis, marker_color=self.cores['variavel']),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(name='Investimentos', x=meses, y=investimentos, marker_color=self.cores['investimento']),
            row=2, col=1
        )
        
        fig.update_layout(
            title={
                'text': 'Comparativo Mensal',
                'x': 0.5,
                'font': {'size': 18, 'color': self.cores['texto']}
            },
            height=600,
            showlegend=True,
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        return fig
