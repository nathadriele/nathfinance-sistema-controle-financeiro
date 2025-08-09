"""
Gerenciador de persistência de dados para FinTrack360
"""

import pandas as pd
import json
import os
from datetime import datetime, date
from typing import List, Dict, Optional
from models.transaction import GerenciadorTransacoes, Transacao
from models.categories import TipoTransacao, TipoGasto

class DataManager:
    """Classe responsável por salvar e carregar dados"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.csv_file = os.path.join(data_dir, "transactions.csv")
        self.backup_dir = os.path.join(data_dir, "backups")
        
        # Criar diretórios se não existirem
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def salvar_transacoes(self, gerenciador: GerenciadorTransacoes) -> bool:
        """Salva todas as transações em CSV"""
        try:
            # Criar backup antes de salvar
            self._criar_backup()
            
            # Converter transações para DataFrame
            df = gerenciador.exportar_para_dataframe()
            
            # Salvar CSV
            df.to_csv(self.csv_file, index=False, encoding='utf-8')
            
            print(f"Dados salvos com sucesso em {self.csv_file}")
            return True
            
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
            return False
    
    def load_data(self) -> pd.DataFrame:
        """Carrega dados como DataFrame para compatibilidade"""
        try:
            if not os.path.exists(self.csv_file):
                print("Arquivo de dados não encontrado. Retornando DataFrame vazio.")
                return pd.DataFrame()

            df = pd.read_csv(self.csv_file)
            return df

        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return pd.DataFrame()

    def carregar_transacoes(self) -> Optional[GerenciadorTransacoes]:
        """Carrega transações do CSV"""
        try:
            if not os.path.exists(self.csv_file):
                print("Arquivo de dados não encontrado. Criando novo gerenciador.")
                return GerenciadorTransacoes()
            
            # Ler CSV
            df = pd.read_csv(self.csv_file, encoding='utf-8')
            
            # Criar gerenciador
            gerenciador = GerenciadorTransacoes()
            
            # Converter DataFrame para transações
            for _, row in df.iterrows():
                try:
                    # Converter data
                    data_transacao = pd.to_datetime(row['Data']).date()
                    
                    # Extrair valores
                    descricao = str(row['Descrição'])
                    valor = float(row['Valor (R$)'])
                    recorrente = row['Recorrente'] == 'Sim' if 'Recorrente' in row else False
                    
                    # Adicionar transação
                    gerenciador.adicionar_transacao(
                        data=data_transacao,
                        descricao=descricao,
                        valor=valor,
                        recorrente=recorrente
                    )
                    
                except Exception as e:
                    print(f"Erro ao processar linha: {e}")
                    continue
            
            print(f"Carregadas {len(gerenciador.transacoes)} transações")
            return gerenciador
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return GerenciadorTransacoes()
    
    def _criar_backup(self):
        """Cria backup do arquivo atual"""
        if os.path.exists(self.csv_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"transactions_backup_{timestamp}.csv")
            
            try:
                import shutil
                shutil.copy2(self.csv_file, backup_file)
                print(f"Backup criado: {backup_file}")
            except Exception as e:
                print(f"Erro ao criar backup: {e}")
    
    def exportar_excel(self, gerenciador: GerenciadorTransacoes, filename: Optional[str] = None) -> bool:
        """Exporta dados para Excel com múltiplas abas"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(self.data_dir, f"fintrack360_export_{timestamp}.xlsx")
            
            # Criar DataFrame principal
            df_principal = gerenciador.exportar_para_dataframe()
            
            # Criar análises por mês
            meses_anos = set((t.data.year, t.data.month) for t in gerenciador.transacoes)
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Aba principal com todas as transações
                df_principal.to_excel(writer, sheet_name='Todas_Transações', index=False)
                
                # Aba para cada mês
                for ano, mes in sorted(meses_anos):
                    transacoes_mes = gerenciador.obter_transacoes_mes(mes, ano)
                    if transacoes_mes:
                        # Criar DataFrame do mês
                        dados_mes = []
                        for t in transacoes_mes:
                            dados_mes.append({
                                'Data': t.data,
                                'Descrição': t.descricao,
                                'Valor': t.valor,
                                'Categoria': t.categoria,
                                'Tipo': t.tipo_transacao.value,
                                'Saldo': t.saldo_acumulado
                            })
                        
                        df_mes = pd.DataFrame(dados_mes)
                        sheet_name = f"{ano}_{mes:02d}"
                        df_mes.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Aba de resumo
                self._criar_aba_resumo(writer, gerenciador)
            
            print(f"Dados exportados para Excel: {filename}")
            return True
            
        except Exception as e:
            print(f"Erro ao exportar para Excel: {e}")
            return False
    
    def _criar_aba_resumo(self, writer, gerenciador: GerenciadorTransacoes):
        """Cria aba de resumo com estatísticas"""
        from utils.calculations import CalculadoraFinanceira
        
        calc = CalculadoraFinanceira(gerenciador)
        
        # Obter meses únicos
        meses_anos = set((t.data.year, t.data.month) for t in gerenciador.transacoes)
        
        resumo_dados = []
        for ano, mes in sorted(meses_anos):
            kpis = calc.calcular_kpis_mensais(mes, ano)
            distribuicao = calc.calcular_distribuicao_50_30_20(mes, ano)
            
            resumo_dados.append({
                'Ano': ano,
                'Mês': mes,
                'Renda': kpis['renda_mensal'],
                'Gastos Essenciais': kpis['gastos_essenciais'],
                'Gastos Variáveis': kpis['gastos_variaveis'],
                'Investimentos': kpis['investimentos'],
                'Total Gastos': kpis['total_gastos'],
                'Saldo Final': kpis['saldo_atual'],
                '% Essenciais': distribuicao['essencial']['percentual_real'],
                '% Variáveis': distribuicao['variavel']['percentual_real'],
                '% Investimentos': distribuicao['investimento']['percentual_real']
            })
        
        if resumo_dados:
            df_resumo = pd.DataFrame(resumo_dados)
            df_resumo.to_excel(writer, sheet_name='Resumo_Mensal', index=False)
    
    def importar_csv_externo(self, arquivo_csv: str, mapeamento_colunas: Dict[str, str]) -> Optional[GerenciadorTransacoes]:
        """
        Importa dados de CSV externo com mapeamento de colunas
        
        Args:
            arquivo_csv: Caminho para o arquivo CSV
            mapeamento_colunas: Dict mapeando colunas do CSV para campos esperados
                                Ex: {'data': 'Data', 'descricao': 'Histórico', 'valor': 'Valor'}
        """
        try:
            df = pd.read_csv(arquivo_csv, encoding='utf-8')
            gerenciador = GerenciadorTransacoes()
            
            for _, row in df.iterrows():
                try:
                    # Mapear colunas
                    data_str = row[mapeamento_colunas['data']]
                    descricao = str(row[mapeamento_colunas['descricao']])
                    valor = float(str(row[mapeamento_colunas['valor']]).replace(',', '.'))
                    
                    # Converter data
                    data_transacao = pd.to_datetime(data_str).date()
                    
                    # Adicionar transação
                    gerenciador.adicionar_transacao(
                        data=data_transacao,
                        descricao=descricao,
                        valor=valor
                    )
                    
                except Exception as e:
                    print(f"Erro ao processar linha: {e}")
                    continue
            
            print(f"Importadas {len(gerenciador.transacoes)} transações do arquivo externo")
            return gerenciador
            
        except Exception as e:
            print(f"Erro ao importar CSV externo: {e}")
            return None
    
    def limpar_dados_antigos(self, dias_manter: int = 365):
        """Remove backups antigos para economizar espaço"""
        try:
            import time
            agora = time.time()
            limite = agora - (dias_manter * 24 * 60 * 60)
            
            for arquivo in os.listdir(self.backup_dir):
                caminho_arquivo = os.path.join(self.backup_dir, arquivo)
                if os.path.isfile(caminho_arquivo):
                    if os.path.getmtime(caminho_arquivo) < limite:
                        os.remove(caminho_arquivo)
                        print(f"Backup antigo removido: {arquivo}")
                        
        except Exception as e:
            print(f"Erro ao limpar dados antigos: {e}")
