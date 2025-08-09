import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import dash
from dash import dcc, html, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import locale
import os
from utils.data_manager import DataManager
from categorias_completas import CategorizadorAutomatico
from sistema_cartoes import gerenciador_cartoes
from sistema_metas import gerenciador_metas
from sistema_lembretes import gerenciador_lembretes
from sistema_exportacao import exportador

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
app.title = "Nathfinance | Controle Financeiro Pessoal"

data_manager = DataManager()
df_raw = data_manager.load_data()
categorizador = CategorizadorAutomatico()

if not df_raw.empty:
    df = df_raw.copy()
    mapeamento_colunas = {
        'Descrição': 'Descricao',
        'Valor (R$)': 'Valor'
    }
    df = df.rename(columns=mapeamento_colunas)

    if 'Valor' in df.columns:
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

    if 'Data' in df.columns:
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
else:
    df = pd.DataFrame()

print(f"Carregadas {len(df)} transações")
print("Iniciando Nathfinance | Controle Financeiro Pessoal...")
print("Sistema inspirado no Mobills - Regra 50-30-20")
print("Acesse: http://localhost:8050")

CORES_MOBILLS = {
    'azul_principal': '#4A90E2',
    'azul_escuro': '#2E5BBA',
    'verde': '#7ED321',
    'vermelho': '#D0021B',
    'laranja': '#F5A623',
    'cinza_claro': '#F8F9FA',
    'cinza_medio': '#6C757D',
    'branco': '#FFFFFF'
}

def formatar_moeda(valor):
    try:
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "R$ 0,00"

def formatar_categoria(categoria):
    if not categoria or pd.isna(categoria):
        return "Sem categoria"
    categoria_str = str(categoria).replace("_", " ")
    return categoria_str.title()

def calcular_saldo_atual(df):
    if df.empty:
        return 0
    receitas = df[df['Valor'] > 0]['Valor'].sum()
    despesas = abs(df[df['Valor'] < 0]['Valor'].sum())
    return receitas - despesas

def criar_card_saldo(df):
    saldo = calcular_saldo_atual(df)
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.H6("Agosto ▼", className="text-white mb-2", style={'fontSize': '16px'}),
                html.H2(formatar_moeda(saldo), className="text-white mb-0",
                       style={'fontSize': '32px', 'fontWeight': 'bold'}),
                html.P("Saldo atual em contas", className="text-white-50 mb-0",
                      style={'fontSize': '14px'})
            ], className="text-center")
        ])
    ], style={
        'background': f'linear-gradient(135deg, {CORES_MOBILLS["azul_principal"]}, {CORES_MOBILLS["azul_escuro"]})',
        'border': 'none',
        'borderRadius': '15px',
        'marginBottom': '20px'
    })

def criar_cards_resumo(df):
    if df.empty:
        receitas = despesas = 0
    else:
        receitas = df[df['Valor'] > 0]['Valor'].sum()
        despesas = abs(df[df['Valor'] < 0]['Valor'].sum())

    cartoes = gerenciador_cartoes.calcular_limite_total_usado()
    cards = []
    dados_cards = [
        ("Receitas", receitas, CORES_MOBILLS['verde'], "💰"),
        ("Despesas", despesas, CORES_MOBILLS['vermelho'], "💸"),
        ("Cartões", cartoes, CORES_MOBILLS['laranja'], "💳")
    ]

    for titulo, valor, cor, icone in dados_cards:
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Span(icone, style={'fontSize': '20px', 'marginRight': '8px'}),
                        html.Span(titulo, style={'fontSize': '14px', 'color': CORES_MOBILLS['cinza_medio']})
                    ], className="d-flex align-items-center mb-2"),
                    html.H5(formatar_moeda(valor), className="mb-0",
                           style={'color': cor, 'fontWeight': 'bold'})
                ])
            ], style={'border': 'none', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ], width=4)
        cards.append(card)

    return dbc.Row(cards, className="mb-4")

def criar_formulario_transacao():
    return dbc.Card([
        dbc.CardHeader([
            html.H5("💰 Nova Transação", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Data"),
                    dbc.Input(
                        id="input-data",
                        type="date",
                        value=date.today().strftime('%Y-%m-%d')
                    )
                ], width=3),
                dbc.Col([
                    dbc.Label("Tipo"),
                    dcc.Dropdown(
                        id="input-tipo",
                        options=[
                            {"label": "💰 Receita", "value": "entrada"},
                            {"label": "💸 Despesa", "value": "saida"}
                        ],
                        value="saida",
                        clearable=False
                    )
                ], width=2),
                dbc.Col([
                    dbc.Label("Descrição"),
                    dbc.Input(
                        id="input-descricao",
                        type="text",
                        placeholder="Ex: Supermercado, Salário..."
                    )
                ], width=4),
                dbc.Col([
                    dbc.Label("Valor (R$)"),
                    dbc.Input(
                        id="input-valor",
                        type="number",
                        step="0.01",
                        placeholder="0,00"
                    )
                ], width=2),
                dbc.Col([
                    dbc.Label(" "),
                    dbc.Button(
                        "Adicionar",
                        id="btn-adicionar",
                        color="primary",
                        className="w-100"
                    )
                ], width=1)
            ])
        ])
    ], className="mb-4")

def criar_grafico_despesas_categoria(df):
    if df.empty:
        return go.Figure()

    despesas = df[df['Valor'] < 0].copy()
    if despesas.empty:
        return go.Figure()

    despesas['Valor_Abs'] = abs(despesas['Valor'])
    despesas_por_categoria = despesas.groupby('Categoria')['Valor_Abs'].sum().reset_index()
    despesas_por_categoria['Categoria_Formatada'] = despesas_por_categoria['Categoria'].apply(formatar_categoria)

    cores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']

    fig = px.pie(despesas_por_categoria,
                 values='Valor_Abs',
                 names='Categoria_Formatada',
                 title="DESPESAS POR CATEGORIA",
                 color_discrete_sequence=cores)

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=12),
        title_font_size=14,
        title_x=0.5
    )

    return fig

def criar_secao_orcamento():
    mes_atual = date.today().month
    ano_atual = date.today().year

    total_orcado = gerenciador_metas.calcular_total_orcado(mes_atual, ano_atual)
    total_gasto = gerenciador_metas.calcular_total_gasto_orcamento(mes_atual, ano_atual)

    return dbc.Card([
        dbc.CardBody([
            html.H6("ORÇAMENTO", className="mb-3", style={'fontSize': '14px', 'fontWeight': 'bold'}),
            html.Div([
                html.Div([
                    html.Span("Meta", style={'fontSize': '14px'}),
                    html.Span(formatar_moeda(total_orcado), className="float-end", style={'fontSize': '14px'})
                ], className="d-flex justify-content-between mb-1"),
                html.Div([
                    html.Span("Valor gasto", style={'fontSize': '14px'}),
                    html.Span(formatar_moeda(total_gasto), className="float-end",
                             style={'fontSize': '14px', 'color': CORES_MOBILLS['vermelho']})
                ], className="d-flex justify-content-between mb-1"),
                html.Div([
                    html.Span("Disponível", style={'fontSize': '14px'}),
                    html.Span(formatar_moeda(total_orcado - total_gasto), className="float-end",
                             style={'fontSize': '14px', 'color': CORES_MOBILLS['verde']})
                ], className="d-flex justify-content-between")
            ])
        ])
    ], style={'border': 'none', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})

def criar_ultimas_transacoes(df):
    if df.empty:
        transacoes_recentes = pd.DataFrame()
    else:
        transacoes_recentes = df.head(5)

    linhas = []
    for _, transacao in transacoes_recentes.iterrows():
        # Verificar se as colunas existem e obter valores seguros
        valor = transacao.get('Valor', 0) if 'Valor' in transacao else 0
        descricao = transacao.get('Descricao', transacao.get('Descrição', 'Transação'))
        categoria = formatar_categoria(transacao.get('Categoria', 'Sem categoria'))
        data = transacao.get('Data', '')

        cor_valor = CORES_MOBILLS['verde'] if valor > 0 else CORES_MOBILLS['vermelho']
        sinal = "" if valor > 0 else "- "

        # Formatar data
        if hasattr(data, 'strftime'):
            data_formatada = data.strftime('%d/%m')
        elif isinstance(data, str) and data:
            try:
                data_obj = pd.to_datetime(data)
                data_formatada = data_obj.strftime('%d/%m')
            except:
                data_formatada = str(data)[:5]  # Primeiros 5 caracteres
        else:
            data_formatada = "N/A"

        linha = html.Div([
            html.Div([
                html.Strong(str(descricao), style={'fontSize': '14px'}),
                html.Br(),
                html.Small(str(categoria), style={'color': CORES_MOBILLS['cinza_medio']})
            ], className="flex-grow-1"),
            html.Div([
                html.Span(f"{sinal}{formatar_moeda(abs(valor))}",
                         style={'color': cor_valor, 'fontWeight': 'bold', 'fontSize': '14px'}),
                html.Br(),
                html.Small(data_formatada, style={'color': CORES_MOBILLS['cinza_medio']})
            ], className="text-end")
        ], className="d-flex align-items-center py-2 border-bottom")
        linhas.append(linha)

    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.H6("ÚLTIMAS TRANSAÇÕES", className="mb-3", style={'fontSize': '14px', 'fontWeight': 'bold'}),
                html.A("Ver extrato completo →", href="#", className="text-primary", style={'fontSize': '12px'})
            ], className="d-flex justify-content-between align-items-center"),
            html.Div(linhas)
        ])
    ], style={'border': 'none', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})

def criar_navegacao_abas():
    """Criar navegação por abas (estilo Mobills)"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Tabs([
                dbc.Tab(label="Resumo", tab_id="resumo", active_tab_style={'backgroundColor': CORES_MOBILLS['azul_principal'], 'color': 'white'}),
                dbc.Tab(label="Extrato", tab_id="extrato"),
                dbc.Tab(label="Cartões", tab_id="cartoes"),
                dbc.Tab(label="Metas", tab_id="metas"),
                dbc.Tab(label="Lembretes", tab_id="lembretes"),
                dbc.Tab(label="Gráficos", tab_id="graficos")
            ], id="tabs-navegacao", active_tab="resumo")
        ])
    ], style={'border': 'none', 'marginBottom': '20px'})

# Layout principal da aplicação
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H3("Nathfinance", className="text-primary mb-0", style={'fontWeight': 'bold'}),
            html.P("Controle Financeiro Pessoal", className="text-muted mb-0", style={'fontSize': '14px'})
        ], width=8),
        dbc.Col([
            dbc.Button("📊 Exportar", id="btn-exportar", color="outline-primary", size="sm", className="float-end")
        ], width=4)
    ], className="mb-4 pt-3"),

    # Card do saldo principal
    dbc.Row([
        dbc.Col([
            html.Div(id="card-saldo")
        ])
    ]),

    # Cards de resumo
    html.Div(id="cards-resumo"),

    # Alertas
    html.Div(id="alertas-container"),

    # Navegação por abas
    criar_navegacao_abas(),

    # Conteúdo das abas
    html.Div(id="conteudo-abas"),

    # Store para dados
    dcc.Store(id='store-dados', data=df.to_dict('records') if not df.empty else []),

    # Modal de exportação
    dbc.Modal([
        dbc.ModalHeader("Exportar Relatórios"),
        dbc.ModalBody([
            html.P("Selecione o formato de exportação:"),
            dbc.RadioItems(
                id="formato-exportacao",
                options=[
                    {"label": "📄 Relatório Completo (Excel)", "value": "excel"},
                    {"label": "📊 Transações (CSV)", "value": "csv"},
                    {"label": "💾 Backup Completo (JSON)", "value": "backup"},
                    {"label": "📋 Relatório Texto", "value": "texto"}
                ],
                value="excel"
            )
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancelar", id="btn-cancelar-export", color="secondary", className="me-2"),
            dbc.Button("Exportar", id="btn-confirmar-export", color="primary")
        ])
    ], id="modal-exportacao", is_open=False),

    # Área de notificações de exportação
    html.Div(id="notificacao-exportacao"),

    # Botão flutuante para adicionar transação
    html.Div([
        dbc.Button("➕", id="btn-adicionar-flutuante",
                  style={
                      'position': 'fixed',
                      'bottom': '20px',
                      'right': '20px',
                      'borderRadius': '50%',
                      'width': '60px',
                      'height': '60px',
                      'fontSize': '24px',
                      'backgroundColor': CORES_MOBILLS['azul_principal'],
                      'border': 'none',
                      'boxShadow': '0 4px 8px rgba(0,0,0,0.3)',
                      'zIndex': '1000'
                  })
    ])
], fluid=True, style={'backgroundColor': CORES_MOBILLS['cinza_claro'], 'minHeight': '100vh'})

# Callback para atualizar o card do saldo
@app.callback(
    Output('card-saldo', 'children'),
    Input('store-dados', 'data')
)
def atualizar_card_saldo(dados):
    df = pd.DataFrame(dados) if dados else pd.DataFrame()
    return criar_card_saldo(df)

# Callback para atualizar cards de resumo
@app.callback(
    Output('cards-resumo', 'children'),
    Input('store-dados', 'data')
)
def atualizar_cards_resumo(dados):
    df = pd.DataFrame(dados) if dados else pd.DataFrame()
    return criar_cards_resumo(df)

# Callback para alertas
@app.callback(
    Output('alertas-container', 'children'),
    Input('store-dados', 'data')
)
def atualizar_alertas(dados):
    alertas = gerenciador_lembretes.gerar_alertas()

    if not alertas:
        return []

    cards_alertas = []
    for alerta in alertas:
        cor_mapa = {
            'danger': 'danger',
            'warning': 'warning',
            'info': 'info',
            'success': 'success'
        }

        card = dbc.Alert([
            html.Div([
                html.Span(alerta['icone'], style={'fontSize': '20px', 'marginRight': '10px'}),
                html.Strong(alerta['titulo'], style={'marginRight': '10px'}),
                html.Span(alerta['descricao'])
            ])
        ], color=cor_mapa.get(alerta['tipo'], 'info'), dismissable=True, className="mb-2")
        cards_alertas.append(card)

    return cards_alertas

# Callback para conteúdo das abas
@app.callback(
    Output('conteudo-abas', 'children'),
    [Input('tabs-navegacao', 'active_tab'),
     Input('store-dados', 'data')]
)
def atualizar_conteudo_abas(aba_ativa, dados):
    df = pd.DataFrame(dados) if dados else pd.DataFrame()

    if aba_ativa == "resumo":
        return [
            # Primeira linha - Gráfico e Orçamento
            dbc.Row([
                # Coluna esquerda - Gráfico de despesas
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(
                                figure=criar_grafico_despesas_categoria(df),
                                style={'height': '300px'}
                            )
                        ])
                    ], style={'border': 'none', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
                ], width=6),

                # Coluna direita - Orçamento
                dbc.Col([
                    criar_secao_orcamento()
                ], width=6)
            ], className="mb-4"),

            # Segunda linha - Últimas transações (largura total)
            dbc.Row([
                dbc.Col([
                    criar_ultimas_transacoes(df)
                ])
            ])
        ]

    elif aba_ativa == "extrato":
        return criar_aba_extrato(df)

    elif aba_ativa == "cartoes":
        return criar_aba_cartoes()

    elif aba_ativa == "metas":
        return criar_aba_metas()

    elif aba_ativa == "lembretes":
        return criar_aba_lembretes()

    elif aba_ativa == "graficos":
        return criar_aba_graficos(df)

    return html.Div("Selecione uma aba")

def criar_aba_extrato(df):
    conteudo = [criar_formulario_transacao()]

    if df.empty:
        conteudo.append(html.Div("Nenhuma transação encontrada", className="text-center py-5"))
        return conteudo

    # Preparar dados para a tabela
    df_extrato = df.copy()

    # Verificar e mapear colunas existentes
    if 'Valor' in df_extrato.columns:
        df_extrato['Valor_Formatado'] = df_extrato['Valor'].apply(lambda x: formatar_moeda(x) if pd.notna(x) else "R$ 0,00")
    else:
        df_extrato['Valor_Formatado'] = "R$ 0,00"

    # Formatar data
    if 'Data' in df_extrato.columns:
        df_extrato['Data_Formatada'] = pd.to_datetime(df_extrato['Data'], errors='coerce').dt.strftime('%d/%m/%Y')
    else:
        df_extrato['Data_Formatada'] = "N/A"

    # Verificar colunas de descrição e categoria
    descricao_col = 'Descricao' if 'Descricao' in df_extrato.columns else 'Descrição' if 'Descrição' in df_extrato.columns else None
    categoria_col = 'Categoria' if 'Categoria' in df_extrato.columns else None

    # Formatar categoria se existir
    if categoria_col:
        df_extrato['Categoria_Formatada'] = df_extrato[categoria_col].apply(formatar_categoria)

    # Preparar dados para exibição
    if descricao_col and categoria_col:
        colunas_dados = ['Data_Formatada', descricao_col, 'Categoria_Formatada', 'Valor_Formatado']
        colunas_tabela = [
            {'name': 'Data', 'id': 'Data_Formatada'},
            {'name': 'Descrição', 'id': descricao_col},
            {'name': 'Categoria', 'id': 'Categoria_Formatada'},
            {'name': 'Valor', 'id': 'Valor_Formatado'}
        ]
    else:
        # Fallback se não encontrar as colunas
        colunas_dados = ['Data_Formatada', 'Valor_Formatado']
        colunas_tabela = [
            {'name': 'Data', 'id': 'Data_Formatada'},
            {'name': 'Valor', 'id': 'Valor_Formatado'}
        ]

    conteudo.append(dbc.Card([
        dbc.CardBody([
            html.H5("Extrato Completo", className="mb-3"),
            dash_table.DataTable(
                data=df_extrato[colunas_dados].to_dict('records'),
                columns=colunas_tabela,
                style_cell={'textAlign': 'left', 'fontSize': '14px', 'padding': '10px'},
                style_header={'backgroundColor': CORES_MOBILLS['azul_principal'], 'color': 'white', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': CORES_MOBILLS['cinza_claro']
                    }
                ],
                page_size=10
            )
        ])
    ], style={'border': 'none', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}))

    return conteudo

def criar_aba_graficos(df):
    """Criar conteúdo da aba Gráficos"""
    if df.empty:
        return html.Div("Nenhum dado para exibir gráficos", className="text-center py-5")

    return dbc.Row([
        # Gráfico de pizza das despesas
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Gastos do Mês", className="mb-3"),
                    dcc.Graph(
                        figure=criar_grafico_despesas_categoria(df),
                        style={'height': '400px'}
                    )
                ])
            ], style={'border': 'none', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ], width=6),

        # Gráfico de renda e gastos
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Renda e Gastos", className="mb-3"),
                    criar_grafico_renda_gastos(df)
                ])
            ], style={'border': 'none', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ], width=6)
    ])

def criar_grafico_renda_gastos(df):
    """Criar gráfico de barras para renda e gastos"""
    if df.empty:
        return html.Div("Sem dados")

    receitas = df[df['Valor'] > 0]['Valor'].sum()
    despesas = abs(df[df['Valor'] < 0]['Valor'].sum())

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Renda',
        x=['Agosto'],
        y=[receitas],
        marker_color=CORES_MOBILLS['verde'],
        text=[formatar_moeda(receitas)],
        textposition='auto'
    ))

    fig.add_trace(go.Bar(
        name='Gastos',
        x=['Agosto'],
        y=[despesas],
        marker_color=CORES_MOBILLS['vermelho'],
        text=[formatar_moeda(despesas)],
        textposition='auto'
    ))

    fig.update_layout(
        title="RENDA E GASTOS",
        xaxis_title="",
        yaxis_title="Valor (R$)",
        barmode='group',
        showlegend=True,
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return dcc.Graph(figure=fig)

def criar_aba_cartoes():
    """Criar conteúdo da aba Cartões"""
    cartoes = gerenciador_cartoes.obter_cartoes_ativos()

    if not cartoes:
        return html.Div("Nenhum cartão cadastrado", className="text-center py-5")

    cards_cartoes = []
    for cartao in cartoes:
        # Determinar cor da barra de progresso
        cor_barra = CORES_MOBILLS['verde']
        if cartao.percentual_usado > 70:
            cor_barra = CORES_MOBILLS['laranja']
        if cartao.percentual_usado > 90:
            cor_barra = CORES_MOBILLS['vermelho']

        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H6(cartao.nome, className="mb-1", style={'fontWeight': 'bold'}),
                        html.Small(f"{cartao.bandeira.value.upper()}", className="text-muted")
                    ]),
                    html.Hr(),
                    html.Div([
                        html.P(f"Limite: {formatar_moeda(cartao.limite_total)}", className="mb-1", style={'fontSize': '14px'}),
                        html.P(f"Usado: {formatar_moeda(cartao.limite_usado)}", className="mb-1", style={'fontSize': '14px'}),
                        html.P(f"Disponível: {formatar_moeda(cartao.limite_disponivel)}", className="mb-2",
                              style={'fontSize': '14px', 'color': CORES_MOBILLS['verde'], 'fontWeight': 'bold'})
                    ]),
                    dbc.Progress(value=cartao.percentual_usado, color="primary", className="mb-2",
                               style={'height': '8px'}),
                    html.Small(f"{cartao.percentual_usado:.1f}% utilizado", className="text-muted"),
                    html.Hr(),
                    html.Small(f"Vence em: {cartao.proxima_fatura.strftime('%d/%m/%Y')}", className="text-muted")
                ])
            ], style={'border': f'3px solid {cartao.cor}', 'borderRadius': '10px'})
        ], width=4, className="mb-3")
        cards_cartoes.append(card)

    # Resumo dos cartões
    total_limite = sum(c.limite_total for c in cartoes)
    total_usado = sum(c.limite_usado for c in cartoes)
    total_disponivel = sum(c.limite_disponivel for c in cartoes)

    resumo = dbc.Card([
        dbc.CardBody([
            html.H5("Resumo dos Cartões", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.H6("Limite Total", className="text-muted"),
                    html.H4(formatar_moeda(total_limite), className="text-primary")
                ], width=4),
                dbc.Col([
                    html.H6("Total Usado", className="text-muted"),
                    html.H4(formatar_moeda(total_usado), className="text-danger")
                ], width=4),
                dbc.Col([
                    html.H6("Disponível", className="text-muted"),
                    html.H4(formatar_moeda(total_disponivel), className="text-success")
                ], width=4)
            ])
        ])
    ], style={'border': 'none', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'})

    return [resumo] + [dbc.Row(cards_cartoes)]

def criar_aba_metas():
    """Criar conteúdo da aba Metas"""
    metas = gerenciador_metas.obter_metas_ativas()

    if not metas:
        return html.Div("Nenhuma meta cadastrada", className="text-center py-5")

    cards_metas = []
    for meta in metas:
        # Determinar cor da barra de progresso
        cor_barra = "success"
        if meta.percentual_concluido < 30:
            cor_barra = "danger"
        elif meta.percentual_concluido < 70:
            cor_barra = "warning"

        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H6(meta.nome, className="mb-1", style={'fontWeight': 'bold'}),
                        html.Small(meta.tipo.value.replace('_', ' ').title(), className="text-muted")
                    ]),
                    html.Hr(),
                    html.Div([
                        html.P(f"Meta: {formatar_moeda(meta.valor_meta)}", className="mb-1", style={'fontSize': '14px'}),
                        html.P(f"Atual: {formatar_moeda(meta.valor_atual)}", className="mb-1", style={'fontSize': '14px'}),
                        html.P(f"Restante: {formatar_moeda(meta.valor_restante)}", className="mb-2",
                              style={'fontSize': '14px', 'color': CORES_MOBILLS['laranja'], 'fontWeight': 'bold'})
                    ]),
                    dbc.Progress(value=meta.percentual_concluido, color=cor_barra, className="mb-2",
                               style={'height': '8px'}),
                    html.Small(f"{meta.percentual_concluido:.1f}% concluído", className="text-muted"),
                    html.Hr(),
                    html.Small(f"Restam: {meta.dias_restantes} dias", className="text-muted")
                ])
            ], style={'border': f'3px solid {meta.cor}', 'borderRadius': '10px'})
        ], width=4, className="mb-3")
        cards_metas.append(card)

    # Resumo das metas
    relatorio = gerenciador_metas.gerar_relatorio_metas()

    resumo = dbc.Card([
        dbc.CardBody([
            html.H5("Resumo das Metas", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.H6("Total de Metas", className="text-muted"),
                    html.H4(str(relatorio['total_metas']), className="text-primary")
                ], width=3),
                dbc.Col([
                    html.H6("Metas Ativas", className="text-muted"),
                    html.H4(str(relatorio['metas_ativas']), className="text-info")
                ], width=3),
                dbc.Col([
                    html.H6("Economia Total", className="text-muted"),
                    html.H4(formatar_moeda(relatorio['economia_total']), className="text-success")
                ], width=3),
                dbc.Col([
                    html.H6("Progresso Médio", className="text-muted"),
                    html.H4(f"{relatorio['percentual_medio']:.1f}%", className="text-warning")
                ], width=3)
            ])
        ])
    ], style={'border': 'none', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'})

    return [resumo] + [dbc.Row(cards_metas)]

def criar_aba_lembretes():
    """Criar conteúdo da aba Lembretes"""
    lembretes_pendentes = gerenciador_lembretes.obter_lembretes_pendentes()

    if not lembretes_pendentes:
        return html.Div("Nenhum lembrete pendente", className="text-center py-5")

    # Separar lembretes por urgência
    vencidos = [l for l in lembretes_pendentes if l.esta_vencido]
    hoje = [l for l in lembretes_pendentes if l.vence_hoje]
    proximos = [l for l in lembretes_pendentes if l.dias_restantes > 0 and l.dias_restantes <= 7]
    futuros = [l for l in lembretes_pendentes if l.dias_restantes > 7]

    def criar_card_lembrete(lembrete):
        # Determinar cor baseada na urgência
        if lembrete.esta_vencido:
            cor_borda = CORES_MOBILLS['vermelho']
            badge_cor = "danger"
            badge_texto = "VENCIDO"
        elif lembrete.vence_hoje:
            cor_borda = CORES_MOBILLS['laranja']
            badge_cor = "warning"
            badge_texto = "HOJE"
        elif lembrete.dias_restantes <= 3:
            cor_borda = CORES_MOBILLS['laranja']
            badge_cor = "warning"
            badge_texto = f"{lembrete.dias_restantes} DIAS"
        else:
            cor_borda = CORES_MOBILLS['azul_principal']
            badge_cor = "info"
            badge_texto = f"{lembrete.dias_restantes} DIAS"

        return dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.Div([
                        html.H6(lembrete.titulo, className="mb-1", style={'fontWeight': 'bold'}),
                        dbc.Badge(badge_texto, color=badge_cor, className="mb-2")
                    ], className="d-flex justify-content-between align-items-start"),
                    html.P(lembrete.descricao, className="text-muted mb-2", style={'fontSize': '14px'}),
                    html.Div([
                        html.Strong(formatar_moeda(lembrete.valor), style={'color': cor_borda}),
                        html.Span(f" • {lembrete.categoria}", className="text-muted ms-2")
                    ]),
                    html.Hr(),
                    html.Div([
                        html.Small(f"Vencimento: {lembrete.data_vencimento.strftime('%d/%m/%Y')}", className="text-muted"),
                        html.Small(f"Prioridade: {lembrete.prioridade.value.title()}",
                                 className="text-muted ms-3")
                    ])
                ])
            ])
        ], style={'border': f'2px solid {cor_borda}', 'borderRadius': '8px', 'marginBottom': '10px'})

    secoes = []

    # Seção de vencidos
    if vencidos:
        secoes.append(html.Div([
            html.H5("🔴 Vencidos", className="text-danger mb-3"),
            html.Div([criar_card_lembrete(l) for l in vencidos])
        ], className="mb-4"))

    # Seção de hoje
    if hoje:
        secoes.append(html.Div([
            html.H5("🟡 Vencem Hoje", className="text-warning mb-3"),
            html.Div([criar_card_lembrete(l) for l in hoje])
        ], className="mb-4"))

    # Seção próximos 7 dias
    if proximos:
        secoes.append(html.Div([
            html.H5("📅 Próximos 7 Dias", className="text-info mb-3"),
            html.Div([criar_card_lembrete(l) for l in proximos])
        ], className="mb-4"))

    # Seção futuros
    if futuros:
        secoes.append(html.Div([
            html.H5("📋 Futuros", className="text-secondary mb-3"),
            html.Div([criar_card_lembrete(l) for l in futuros[:5]])  # Mostrar apenas os 5 próximos
        ], className="mb-4"))

    # Resumo dos lembretes
    total_valor = gerenciador_lembretes.calcular_valor_total_pendente()

    resumo = dbc.Card([
        dbc.CardBody([
            html.H5("Resumo dos Lembretes", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.H6("Total Pendente", className="text-muted"),
                    html.H4(str(len(lembretes_pendentes)), className="text-primary")
                ], width=3),
                dbc.Col([
                    html.H6("Vencidos", className="text-muted"),
                    html.H4(str(len(vencidos)), className="text-danger")
                ], width=3),
                dbc.Col([
                    html.H6("Hoje", className="text-muted"),
                    html.H4(str(len(hoje)), className="text-warning")
                ], width=3),
                dbc.Col([
                    html.H6("Valor Total", className="text-muted"),
                    html.H4(formatar_moeda(total_valor), className="text-success")
                ], width=3)
            ])
        ])
    ], style={'border': 'none', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'})

    return [resumo] + secoes

# Callback para abrir modal de exportação
@app.callback(
    Output('modal-exportacao', 'is_open'),
    [Input('btn-exportar', 'n_clicks'),
     Input('btn-cancelar-export', 'n_clicks'),
     Input('btn-confirmar-export', 'n_clicks')],
    [State('modal-exportacao', 'is_open')]
)
def toggle_modal_exportacao(btn_exportar, btn_cancelar, btn_confirmar, is_open):
    if btn_exportar or btn_cancelar:
        return not is_open
    if btn_confirmar:
        return False
    return is_open

# Callback para processar exportação
@app.callback(
    Output('notificacao-exportacao', 'children'),
    [Input('btn-confirmar-export', 'n_clicks')],
    [State('formato-exportacao', 'value'),
     State('store-dados', 'data')]
)
def processar_exportacao(n_clicks, formato, dados):
    if not n_clicks:
        return []

    try:
        # Preparar dados completos
        df_transacoes = pd.DataFrame(dados) if dados else pd.DataFrame()

        dados_completos = {
            'transacoes': dados if dados else [],
            'cartoes': gerenciador_cartoes.exportar_para_dict()['cartoes'],
            'metas': gerenciador_metas.exportar_para_dict()['metas'],
            'orcamentos': gerenciador_metas.exportar_para_dict()['orcamentos'],
            'lembretes': gerenciador_lembretes.exportar_para_dict()['lembretes']
        }

        arquivo_gerado = None

        if formato == "excel":
            arquivo_gerado = exportador.exportar_excel_completo(dados_completos)
            tipo_arquivo = "Excel"
        elif formato == "csv":
            arquivo_gerado = exportador.exportar_csv_transacoes(df_transacoes)
            tipo_arquivo = "CSV"
        elif formato == "backup":
            arquivo_gerado = exportador.gerar_backup_completo(dados_completos)
            tipo_arquivo = "Backup JSON"
        elif formato == "texto":
            arquivo_gerado = exportador.gerar_relatorio_pdf_texto(dados_completos)
            tipo_arquivo = "Relatório Texto"

        if arquivo_gerado:
            nome_arquivo = os.path.basename(arquivo_gerado)
            return dbc.Alert([
                html.Strong("✅ Exportação realizada com sucesso!"),
                html.Br(),
                f"Arquivo {tipo_arquivo} gerado: {nome_arquivo}",
                html.Br(),
                html.Small(f"Salvo em: {arquivo_gerado}")
            ], color="success", dismissable=True, duration=5000)
        else:
            return dbc.Alert("❌ Erro ao exportar arquivo", color="danger", dismissable=True, duration=3000)

    except Exception as e:
        return dbc.Alert(f"❌ Erro na exportação: {str(e)}", color="danger", dismissable=True, duration=3000)

# Callback para adicionar transação
@app.callback(
    Output('store-dados', 'data', allow_duplicate=True),
    Input('btn-adicionar', 'n_clicks'),
    [State('input-data', 'value'),
     State('input-tipo', 'value'),
     State('input-descricao', 'value'),
     State('input-valor', 'value'),
     State('store-dados', 'data')],
    prevent_initial_call=True
)
def adicionar_transacao(n_clicks, data_input, tipo, descricao, valor, dados_atuais):
    if not n_clicks:
        return dados_atuais or []

    if not descricao or not valor:
        print("Descrição ou valor não fornecidos")
        return dados_atuais or []

    try:
        # Preparar nova transação
        nova_transacao = {
            'Data': data_input,
            'Tipo': tipo,
            'Categoria': categorizador.categorizar_transacao(descricao),
            'Descrição': descricao,
            'Valor (R$)': float(valor) if tipo == 'entrada' else -float(valor),
            'Recorrente': 'Não',
            'Semana': 1,
            'Saldo Acumulado': 0,
            '% do Salário': '',
            'Meta 50-30-20': ''
        }

        # Adicionar aos dados existentes
        if dados_atuais:
            dados_atuais.append(nova_transacao)
        else:
            dados_atuais = [nova_transacao]

        # Salvar no CSV
        df_novo = pd.DataFrame(dados_atuais)
        data_manager.save_data(df_novo)

        print(f"Transação adicionada: {descricao} - R$ {valor}")
        return dados_atuais

    except Exception as e:
        print(f"Erro ao adicionar transação: {str(e)}")
        return dados_atuais or []



# Executar aplicação
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
