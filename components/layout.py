"""
Layout principal do FinTrack360
"""

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from components.forms import (
    criar_formulario_transacao, 
    criar_filtros, 
    criar_barra_acoes,
    criar_modal_importacao,
    criar_modal_exportacao
)

def criar_header():
    """Cria o cabeçalho da aplicação"""
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.NavbarBrand([
                        html.I(className="fas fa-chart-line me-2"),
                        "Nathfinance | Sistema de Controle Financeiro v.1"
                    ], className="fs-3 fw-bold text-white")
                ], width="auto"),
                dbc.Col([
                    html.P(
                        "Sistema de Controle Financeiro - Regra 50-30-20",
                        className="text-white-50 mb-0 small"
                    )
                ])
            ], align="center", justify="between")
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4"
    )

def criar_kpi_cards():
    """Cria os cards de KPI"""
    return html.Div(
        id="kpi-cards-container",
        children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("R$", className="text-success"),
                            html.H5("R$ 0,00", id="kpi-renda"),
                            html.P("Renda Mensal", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("-", className="text-danger"),
                            html.H5("R$ 0,00", id="kpi-gastos"),
                            html.P("Total Gastos", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("+", className="text-info"),
                            html.H5("R$ 0,00", id="kpi-investimentos"),
                            html.P("Investimentos", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("=", className="text-primary"),
                            html.H5("R$ 0,00", id="kpi-saldo"),
                            html.P("Saldo Atual", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], width=3)
            ], className="mb-4")
        ]
    )

def criar_area_alertas():
    """Cria área para exibir alertas e recomendações"""
    return html.Div(
        id="alertas-container",
        children=[],
        className="mb-4"
    )

def criar_area_graficos():
    """Cria área principal dos gráficos"""
    return html.Div([
        # Primeira linha de gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id="grafico-pizza",
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id="grafico-barras-metas",
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], width=6)
        ], className="mb-4"),
        
        # Segunda linha de gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id="grafico-evolucao-saldo",
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], width=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id="grafico-gastos-categoria",
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], width=4)
        ], className="mb-4")
    ])

def criar_tabela_transacoes():
    """Cria tabela com as transações recentes"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Transações Recentes", className="mb-0")
        ]),
        dbc.CardBody([
            html.Div(
                id="tabela-transacoes",
                children=[
                    html.P("Nenhuma transação encontrada.", className="text-muted text-center")
                ]
            )
        ])
    ], className="mb-4")

def criar_footer():
    """Cria o rodapé da aplicação"""
    return dbc.Container([
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.P([
                    "Nathfinance | Sistema de Controle Financeiro v.1 | ",
                    html.A("Regra 50-30-20", href="#", className="text-decoration-none"),
                    " | Desenvolvido usando Python & Dash"
                ], className="text-muted text-center mb-0")
            ])
        ])
    ], fluid=True, className="py-3")

def criar_layout_principal():
    """Cria o layout principal da aplicação"""
    return dbc.Container([
        # Stores para dados
        dcc.Store(id='store-transacoes', data=[]),
        dcc.Store(id='store-mes-atual', data=""),
        dcc.Interval(id='interval-component', interval=30*1000, n_intervals=0),  # Atualiza a cada 30s
        
        # Header
        criar_header(),
        
        # Conteúdo principal
        dbc.Container([
            # Barra de ações
            criar_barra_acoes(),
            
            # Formulário de nova transação
            criar_formulario_transacao(),
            
            # Filtros
            criar_filtros(),
            
            # KPI Cards
            criar_kpi_cards(),
            
            # Área de alertas
            criar_area_alertas(),
            
            # Gráficos principais
            criar_area_graficos(),
            
            # Tabela de transações
            criar_tabela_transacoes(),
            
        ], fluid=True),
        
        # Modais
        criar_modal_importacao(),
        criar_modal_exportacao(),
        
        # Footer
        criar_footer(),
        
        # Toast para notificações
        dbc.Toast(
            id="toast-notificacao",
            header="Notificação",
            is_open=False,
            dismissable=True,
            duration=4000,
            icon="info",
            style={"position": "fixed", "top": 66, "right": 10, "width": 350, "z-index": 9999}
        )
        
    ], fluid=True, className="px-0")

def criar_card_alerta(alerta):
    """Cria um card de alerta baseado no tipo"""
    cores_alerta = {
        'success': 'success',
        'warning': 'warning', 
        'info': 'info',
        'danger': 'danger'
    }
    
    icones_alerta = {
        'success': '[OK]',
        'warning': '[!]',
        'info': '[i]',
        'danger': '[X]'
    }
    
    cor = cores_alerta.get(alerta['tipo'], 'info')
    icone = icones_alerta.get(alerta['tipo'], 'ℹ️')
    
    return dbc.Alert([
        html.H6([
            icone, " ", alerta['categoria']
        ], className="alert-heading mb-2"),
        html.P(alerta['mensagem'], className="mb-2"),
        html.Hr(),
        html.P(alerta['recomendacao'], className="mb-0 small")
    ], color=cor, className="mb-2")

def criar_linha_tabela_transacao(transacao):
    """Cria uma linha da tabela de transações"""
    # Definir cor baseada no tipo
    if transacao.get('tipo') == 'entrada':
        cor_badge = 'success'
        icone = '+'
    elif transacao.get('categoria') == 'investimento':
        cor_badge = 'info'
        icone = 'INV'
    else:
        cor_badge = 'danger'
        icone = '-'
    
    return html.Tr([
        html.Td(transacao.get('data', ''), className="small"),
        html.Td([
            dbc.Badge([icone, " ", transacao.get('categoria', '')], color=cor_badge, className="me-1"),
            transacao.get('descricao', '')
        ]),
        html.Td(f"R$ {transacao.get('valor', 0):,.2f}", className="text-end"),
        html.Td(transacao.get('status_meta', ''), className="small")
    ])
