"""
Componentes de formulários para FinTrack360
"""

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from datetime import datetime, date

def criar_formulario_transacao():
    """Cria o formulário para adicionar nova transação"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Registrar Lançamento Financeiro", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Data:", html_for="input-data"),
                    dcc.DatePickerSingle(
                        id='input-data',
                        date=date.today(),
                        display_format='DD/MM/YYYY',
                        style={'width': '100%'}
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Valor (R$):", html_for="input-valor"),
                    dbc.Input(
                        id="input-valor",
                        type="number",
                        step=0.01,
                        placeholder="0.00",
                        value=""
                    )
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Descrição:", html_for="input-descricao"),
                    dbc.Input(
                        id="input-descricao",
                        type="text",
                        placeholder="Ex: Supermercado, Salário, Investimento...",
                        value=""
                    )
                ], width=8),
                dbc.Col([
                    dbc.Label("Recorrente:", html_for="input-recorrente"),
                    dbc.RadioItems(
                        id="input-recorrente",
                        options=[
                            {"label": "Sim", "value": True},
                            {"label": "Não", "value": False}
                        ],
                        value=False,
                        inline=True
                    )
                ], width=4)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Adicionar Lançamento",
                        id="btn-adicionar",
                        color="primary",
                        size="lg",
                        className="w-100"
                    )
                ])
            ])
        ])
    ], className="mb-4")

def criar_filtros():
    """Cria os filtros para visualização dos dados"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Filtros", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Mês/Ano:", html_for="filtro-mes"),
                    dcc.Dropdown(
                        id='filtro-mes',
                        options=[],  # Será preenchido dinamicamente
                        value=f"{date.today().year}-{date.today().month:02d}",
                        placeholder="Selecione o mês"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Categoria:", html_for="filtro-categoria"),
                    dcc.Dropdown(
                        id='filtro-categoria',
                        options=[
                            {'label': 'Todas', 'value': 'todas'},
                            {'label': 'Essenciais (50%)', 'value': 'essencial'},
                            {'label': 'Variáveis (30%)', 'value': 'variavel'},
                            {'label': 'Investimentos (20%)', 'value': 'investimento'}
                        ],
                        value='todas',
                        placeholder="Selecione a categoria"
                    )
                ], width=6)
            ])
        ])
    ], className="mb-4")

def criar_modal_importacao():
    """Cria modal para importação de dados"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Importar Dados")),
        dbc.ModalBody([
            html.P("Selecione um arquivo CSV para importar suas transações:"),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Arraste e solte ou ',
                    html.A('selecione um arquivo CSV')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
            ),
            html.Div(id='upload-status'),
            
            html.Hr(),
            
            html.H6("Mapeamento de Colunas:"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Coluna Data:"),
                    dbc.Input(id="map-data", placeholder="Data", value="Data")
                ], width=4),
                dbc.Col([
                    dbc.Label("Coluna Descrição:"),
                    dbc.Input(id="map-descricao", placeholder="Descrição", value="Descrição")
                ], width=4),
                dbc.Col([
                    dbc.Label("Coluna Valor:"),
                    dbc.Input(id="map-valor", placeholder="Valor", value="Valor")
                ], width=4)
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancelar", id="btn-cancelar-import", className="ms-auto", n_clicks=0),
            dbc.Button("Importar", id="btn-confirmar-import", color="primary", n_clicks=0)
        ]),
    ], id="modal-importacao", is_open=False, size="lg")

def criar_modal_exportacao():
    """Cria modal para exportação de dados"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Exportar Dados")),
        dbc.ModalBody([
            html.P("Escolha o formato para exportar seus dados:"),
            dbc.RadioItems(
                id="formato-export",
                options=[
                    {"label": "Excel (.xlsx) - Recomendado", "value": "excel"},
                    {"label": "CSV (.csv)", "value": "csv"}
                ],
                value="excel",
                inline=False
            ),
            html.Hr(),
            html.P("O arquivo será salvo na pasta 'data' do projeto."),
            html.Div(id='export-status')
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancelar", id="btn-cancelar-export", className="ms-auto", n_clicks=0),
            dbc.Button("Exportar", id="btn-confirmar-export", color="success", n_clicks=0)
        ]),
    ], id="modal-exportacao", is_open=False)

def criar_barra_acoes():
    """Cria barra com ações principais"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("Importar", id="btn-abrir-import", color="info", outline=True),
                        dbc.Button("Exportar", id="btn-abrir-export", color="success", outline=True),
                        dbc.Button("Atualizar", id="btn-atualizar", color="secondary", outline=True)
                    ])
                ], width="auto"),
                dbc.Col([
                    html.Div(id="status-dados", className="text-end")
                ])
            ], justify="between", align="center")
        ])
    ], className="mb-4")

# Callbacks para os modais
@callback(
    Output("modal-importacao", "is_open"),
    [Input("btn-abrir-import", "n_clicks"), Input("btn-cancelar-import", "n_clicks")],
    [State("modal-importacao", "is_open")],
)
def toggle_modal_importacao(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@callback(
    Output("modal-exportacao", "is_open"),
    [Input("btn-abrir-export", "n_clicks"), Input("btn-cancelar-export", "n_clicks")],
    [State("modal-exportacao", "is_open")],
)
def toggle_modal_exportacao(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
