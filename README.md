# Nathfinance - Controle Financeiro Pessoal (Em Andamento | v.1)

<img width="1451" height="399" alt="capa" src="https://github.com/user-attachments/assets/e56926c1-631b-4ce8-88a9-40f37e747fcc" />

NathFinance é um sistema de controle financeiro pessoal desenvolvido em Dash/Plotly, projetado para oferecer uma visualização clara e interativa das suas finanças, auxiliando no gerenciamento de gastos, metas e planejamento financeiro.

<img width="1909" height="812" alt="image" src="https://github.com/user-attachments/assets/157205fa-00b7-46f1-85a4-faf9b63aa9e7" />

## Requisitos Básicos

```
- Python 3.9
- pip instalado
- Navegador web moderno
```

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

## Estrutura Atual

```
nathfinance/
├── app.py                 # Aplicação principal
├── data/transactions.csv  # Dados das transações
├── utils/                 # Utilitários
├── models/                # Modelos de dados
├── components/            # Componentes da interface
└── sistema_*.py           # Sistemas auxiliares
```

## Roadmap

```
- [x] Dashboard com saldo e gráficos
- [x] Categorização automática de transações
- [ ] Integração com APIs bancárias
- [ ] Relatórios PDF
- [ ] Modo mobile otimizado
```

## Interface

Design moderno com cores modernas e layout responsivo.

## Formato dos Dados

**CSV com colunas:**
- Data
- Tipo
- Categoria
- Descrição
- Valor (R$)
- Recorrente
- Semana
- Saldo Acumulado
- % do Salário
- Meta 50-30-20

## Contribuição

**Contribuições são bem-vindas!**

1. Faça um fork do repositório  
2. Crie uma branch para sua funcionalidade (`git checkout -b feature/nova-funcionalidade`)  
3. Commit suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)  
4. Envie para o seu fork (`git push origin feature/nova-funcionalidade`)  
5. Abra um Pull Request
6. E, seja feliz.

