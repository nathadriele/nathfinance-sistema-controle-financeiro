"""
Sistema de Exportação para Nathfinance
Exportação de relatórios em PDF, CSV e OFX
"""

import pandas as pd
import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional
import base64
import io

class ExportadorRelatorios:
    """Classe para exportar relatórios financeiros"""
    
    def __init__(self, data_dir: str = "data/exports"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def exportar_csv_transacoes(self, df: pd.DataFrame, nome_arquivo: str = None) -> str:
        """Exporta transações para CSV"""
        try:
            if nome_arquivo is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"transacoes_{timestamp}.csv"
            
            caminho_arquivo = os.path.join(self.data_dir, nome_arquivo)
            df.to_csv(caminho_arquivo, index=False, encoding='utf-8-sig')
            
            return caminho_arquivo
            
        except Exception as e:
            print(f"Erro ao exportar CSV: {e}")
            return None
    
    def exportar_excel_completo(self, dados_completos: Dict, nome_arquivo: str = None) -> str:
        """Exporta relatório completo em Excel com múltiplas abas"""
        try:
            if nome_arquivo is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"relatorio_completo_{timestamp}.xlsx"
            
            caminho_arquivo = os.path.join(self.data_dir, nome_arquivo)
            
            with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
                if 'transacoes' in dados_completos:
                    df_transacoes = pd.DataFrame(dados_completos['transacoes'])
                    df_transacoes.to_excel(writer, sheet_name='Transações', index=False)
                
                if 'cartoes' in dados_completos:
                    df_cartoes = pd.DataFrame(dados_completos['cartoes'])
                    df_cartoes.to_excel(writer, sheet_name='Cartões', index=False)
                
                if 'metas' in dados_completos:
                    df_metas = pd.DataFrame(dados_completos['metas'])
                    df_metas.to_excel(writer, sheet_name='Metas', index=False)
                
                if 'lembretes' in dados_completos:
                    df_lembretes = pd.DataFrame(dados_completos['lembretes'])
                    df_lembretes.to_excel(writer, sheet_name='Lembretes', index=False)
                
                if 'orcamentos' in dados_completos:
                    df_orcamentos = pd.DataFrame(dados_completos['orcamentos'])
                    df_orcamentos.to_excel(writer, sheet_name='Orçamentos', index=False)
            
            return caminho_arquivo
            
        except Exception as e:
            print(f"Erro ao exportar Excel: {e}")
            return None
    
    def gerar_ofx_transacoes(self, df: pd.DataFrame, conta_id: str = "123456789") -> str:
        """Gera arquivo OFX das transações"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"transacoes_{timestamp}.ofx"
            caminho_arquivo = os.path.join(self.data_dir, nome_arquivo)
            
            ofx_content = """OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX>
<SIGNONMSGSRSV1>
<SONRS>
<STATUS>
<CODE>0
<SEVERITY>INFO
</STATUS>
<DTSERVER>""" + datetime.now().strftime("%Y%m%d%H%M%S") + """
<LANGUAGE>POR
</SONRS>
</SIGNONMSGSRSV1>
<BANKMSGSRSV1>
<STMTTRNRS>
<TRNUID>1
<STATUS>
<CODE>0
<SEVERITY>INFO
</STATUS>
<STMTRS>
<CURDEF>BRL
<BANKACCTFROM>
<BANKID>001
<ACCTID>""" + conta_id + """
<ACCTTYPE>CHECKING
</BANKACCTFROM>
<BANKTRANLIST>
<DTSTART>""" + df['Data'].min().strftime("%Y%m%d") if not df.empty else datetime.now().strftime("%Y%m%d") + """
<DTEND>""" + df['Data'].max().strftime("%Y%m%d") if not df.empty else datetime.now().strftime("%Y%m%d") + """
"""
            
            for _, transacao in df.iterrows():
                data_transacao = pd.to_datetime(transacao['Data']).strftime("%Y%m%d")
                valor = transacao['Valor']
                tipo_transacao = "CREDIT" if valor > 0 else "DEBIT"
                
                ofx_content += f"""<STMTTRN>
<TRNTYPE>{tipo_transacao}
<DTPOSTED>{data_transacao}
<TRNAMT>{valor:.2f}
<FITID>{hash(str(transacao['Data']) + str(transacao['Descricao']) + str(valor))}
<MEMO>{transacao['Descricao']}
</STMTTRN>
"""
            
            ofx_content += """</BANKTRANLIST>
</STMTRS>
</STMTTRNRS>
</BANKMSGSRSV1>
</OFX>"""
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(ofx_content)
            
            return caminho_arquivo
            
        except Exception as e:
            print(f"Erro ao gerar OFX: {e}")
            return None
    
    def gerar_relatorio_pdf_texto(self, dados_completos: Dict) -> str:
        """Gera relatório em formato texto (simulando PDF)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"relatorio_{timestamp}.txt"
            caminho_arquivo = os.path.join(self.data_dir, nome_arquivo)
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("NATHFINANCE - RELATÓRIO FINANCEIRO COMPLETO\n")
                f.write("=" * 60 + "\n")
                f.write(f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                
                f.write("RESUMO GERAL\n")
                f.write("-" * 20 + "\n")
                
                if 'transacoes' in dados_completos:
                    df_trans = pd.DataFrame(dados_completos['transacoes'])
                    if not df_trans.empty:
                        receitas = df_trans[df_trans['Valor'] > 0]['Valor'].sum()
                        despesas = abs(df_trans[df_trans['Valor'] < 0]['Valor'].sum())
                        saldo = receitas - despesas
                        
                        f.write(f"Total de Receitas: R$ {receitas:,.2f}\n")
                        f.write(f"Total de Despesas: R$ {despesas:,.2f}\n")
                        f.write(f"Saldo Atual: R$ {saldo:,.2f}\n\n")
                
                if 'cartoes' in dados_completos:
                    f.write("CARTÕES DE CRÉDITO\n")
                    f.write("-" * 20 + "\n")
                    
                    for cartao in dados_completos['cartoes']:
                        f.write(f"• {cartao['nome']} ({cartao['bandeira'].upper()})\n")
                        f.write(f"  Limite Total: R$ {cartao['limite_total']:,.2f}\n")
                        f.write(f"  Limite Usado: R$ {cartao['limite_usado']:,.2f}\n")
                        f.write(f"  Disponível: R$ {cartao['limite_disponivel']:,.2f}\n")
                        f.write(f"  Uso: {cartao['percentual_usado']:.1f}%\n\n")
                
                if 'metas' in dados_completos:
                    f.write("METAS FINANCEIRAS\n")
                    f.write("-" * 20 + "\n")
                    
                    for meta in dados_completos['metas']:
                        f.write(f"• {meta['nome']}\n")
                        f.write(f"  Meta: R$ {meta['valor_meta']:,.2f}\n")
                        f.write(f"  Atual: R$ {meta['valor_atual']:,.2f}\n")
                        f.write(f"  Progresso: {meta['percentual_concluido']:.1f}%\n")
                        f.write(f"  Dias Restantes: {meta['dias_restantes']}\n\n")
                
                if 'lembretes' in dados_completos:
                    f.write("LEMBRETES PENDENTES\n")
                    f.write("-" * 20 + "\n")
                    
                    lembretes_pendentes = [l for l in dados_completos['lembretes'] if l['status'] == 'pendente']
                    for lembrete in lembretes_pendentes:
                        f.write(f"• {lembrete['titulo']}\n")
                        f.write(f"  Valor: R$ {lembrete['valor']:,.2f}\n")
                        f.write(f"  Vencimento: {lembrete['data_vencimento']}\n")
                        f.write(f"  Prioridade: {lembrete['prioridade'].title()}\n\n")
                
                f.write("=" * 60 + "\n")
                f.write("Relatório gerado pelo Nathfinance\n")
                f.write("Sistema de Controle Financeiro Pessoal\n")
                f.write("=" * 60 + "\n")
            
            return caminho_arquivo
            
        except Exception as e:
            print(f"Erro ao gerar relatório: {e}")
            return None
    
    def gerar_backup_completo(self, dados_completos: Dict) -> str:
        """Gera backup completo em JSON"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"backup_completo_{timestamp}.json"
            caminho_arquivo = os.path.join(self.data_dir, nome_arquivo)
            
            backup_data = {
                'metadata': {
                    'data_backup': datetime.now().isoformat(),
                    'versao_sistema': '1.0',
                    'tipo_backup': 'completo'
                },
                'dados': dados_completos
            }
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
            
            return caminho_arquivo
            
        except Exception as e:
            print(f"Erro ao gerar backup: {e}")
            return None
    
    def listar_arquivos_exportados(self) -> List[Dict]:
        """Lista arquivos exportados"""
        try:
            arquivos = []
            for arquivo in os.listdir(self.data_dir):
                caminho_completo = os.path.join(self.data_dir, arquivo)
                if os.path.isfile(caminho_completo):
                    stat = os.stat(caminho_completo)
                    arquivos.append({
                        'nome': arquivo,
                        'tamanho': stat.st_size,
                        'data_modificacao': datetime.fromtimestamp(stat.st_mtime),
                        'caminho': caminho_completo
                    })
            
            return sorted(arquivos, key=lambda x: x['data_modificacao'], reverse=True)
            
        except Exception as e:
            print(f"Erro ao listar arquivos: {e}")
            return []

exportador = ExportadorRelatorios()

if __name__ == "__main__":
    print("=== Sistema de Exportação Nathfinance ===")
    
    dados_teste = {
        'transacoes': [
            {'Data': '2024-07-01', 'Descricao': 'Salário', 'Valor': 5000.00, 'Categoria': 'Renda'},
            {'Data': '2024-07-02', 'Descricao': 'Aluguel', 'Valor': -1200.00, 'Categoria': 'Moradia'},
            {'Data': '2024-07-03', 'Descricao': 'Supermercado', 'Valor': -350.00, 'Categoria': 'Alimentação'}
        ]
    }
    
    df_teste = pd.DataFrame(dados_teste['transacoes'])
    df_teste['Data'] = pd.to_datetime(df_teste['Data'])
    
    print("Testando exportações...")
    
    arquivo_csv = exportador.exportar_csv_transacoes(df_teste)
    if arquivo_csv:
        print(f"✓ CSV exportado: {arquivo_csv}")
    
    arquivo_relatorio = exportador.gerar_relatorio_pdf_texto(dados_teste)
    if arquivo_relatorio:
        print(f"✓ Relatório exportado: {arquivo_relatorio}")
    
    arquivo_backup = exportador.gerar_backup_completo(dados_teste)
    if arquivo_backup:
        print(f"✓ Backup exportado: {arquivo_backup}")
    
    arquivos = exportador.listar_arquivos_exportados()
    print(f"\nArquivos exportados: {len(arquivos)}")
    for arquivo in arquivos[:3]:  # Mostrar apenas os 3 mais recentes
        print(f"- {arquivo['nome']} ({arquivo['tamanho']} bytes)")
