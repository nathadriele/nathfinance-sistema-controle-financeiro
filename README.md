# Nathfinance - Controle Financeiro Pessoal (Em Andamento | v.1)

<img width="1451" height="399" alt="capa" src="https://github.com/user-attachments/assets/e56926c1-631b-4ce8-88a9-40f37e747fcc" />

NathFinance é um sistema de controle financeiro pessoal desenvolvido em Dash/Plotly, projetado para oferecer uma visualização clara e interativa das suas finanças, auxiliando no gerenciamento de gastos, metas e planejamento financeiro.

<img width="1909" height="812" alt="image" src="https://github.com/user-attachments/assets/157205fa-00b7-46f1-85a4-faf9b63aa9e7" />

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```
3. Execute a aplicação:
```bash
python app.py
```
4. Acesse: http://localhost:8050

## Funcionalidades

- Dashboard com saldo atual e resumos
- Controle de transações com categorização automática
- Sistema de cartões de crédito
- Metas financeiras
- Lembretes de contas
- Exportação de dados
- Gráficos interativos

## Estrutura

```
nathfinance/
├── app.py                 # Aplicação principal
├── data/transactions.csv  # Dados das transações
├── utils/                 # Utilitários
├── models/                # Modelos de dados
├── components/            # Componentes da interface
└── sistema_*.py           # Sistemas auxiliares
```

## Interface

Design moderno com cores modernas e layout responsivo.

## Formato dos Dados

CSV com colunas: Data, Tipo, Categoria, Descrição, Valor (R$), Recorrente, Semana, Saldo Acumulado, % do Salário, Meta 50-30-20
