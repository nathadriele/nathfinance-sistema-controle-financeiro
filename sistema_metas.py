from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Dict, Optional
from enum import Enum
import json

class TipoMeta(Enum):
    ECONOMIA = "economia"
    GASTO_CATEGORIA = "gasto_categoria"
    RENDA = "renda"
    INVESTIMENTO = "investimento"
    DIVIDA = "divida"

class StatusMeta(Enum):
    ATIVA = "ativa"
    PAUSADA = "pausada"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"

@dataclass
class Meta:
    """Classe para representar uma meta financeira"""
    id: str
    nome: str
    tipo: TipoMeta
    valor_meta: float
    valor_atual: float
    data_inicio: date
    data_fim: date
    categoria: str = ""
    descricao: str = ""
    status: StatusMeta = StatusMeta.ATIVA
    cor: str = "#4A90E2"
    
    @property
    def percentual_concluido(self) -> float:
        if self.valor_meta == 0:
            return 0
        return min((self.valor_atual / self.valor_meta) * 100, 100)
    
    @property
    def valor_restante(self) -> float:
        return max(self.valor_meta - self.valor_atual, 0)
    
    @property
    def dias_restantes(self) -> int:
        return (self.data_fim - date.today()).days
    
    @property
    def esta_no_prazo(self) -> bool:
        return self.dias_restantes >= 0
    
    @property
    def valor_diario_necessario(self) -> float:
        if self.dias_restantes <= 0:
            return 0
        return self.valor_restante / self.dias_restantes

@dataclass
class OrcamentoCategoria:
    """Orçamento para uma categoria específica"""
    categoria: str
    valor_orcado: float
    valor_gasto: float
    mes: int
    ano: int
    
    @property
    def valor_disponivel(self) -> float:
        return max(self.valor_orcado - self.valor_gasto, 0)
    
    @property
    def percentual_usado(self) -> float:
        if self.valor_orcado == 0:
            return 0
        return (self.valor_gasto / self.valor_orcado) * 100
    
    @property
    def status(self) -> str:
        perc = self.percentual_usado
        if perc <= 70:
            return "ok"
        elif perc <= 90:
            return "atencao"
        else:
            return "excedido"

class GerenciadorMetas:
    """Gerenciador de metas e orçamentos"""
    
    def __init__(self):
        self.metas: List[Meta] = []
        self.orcamentos: List[OrcamentoCategoria] = []
    

    
    def adicionar_meta(self, meta: Meta) -> bool:
        """Adiciona uma nova meta"""
        try:
            self.metas.append(meta)
            return True
        except Exception as e:
            print(f"Erro ao adicionar meta: {e}")
            return False
    
    def atualizar_progresso_meta(self, meta_id: str, novo_valor: float) -> bool:
        """Atualiza o progresso de uma meta"""
        try:
            meta = self.obter_meta(meta_id)
            if meta:
                meta.valor_atual = novo_valor
                if meta.valor_atual >= meta.valor_meta:
                    meta.status = StatusMeta.CONCLUIDA
                return True
            return False
        except Exception as e:
            print(f"Erro ao atualizar meta: {e}")
            return False
    
    def obter_meta(self, meta_id: str) -> Optional[Meta]:
        """Obtém uma meta pelo ID"""
        for meta in self.metas:
            if meta.id == meta_id:
                return meta
        return None
    
    def obter_metas_ativas(self) -> List[Meta]:
        """Retorna apenas metas ativas"""
        return [meta for meta in self.metas if meta.status == StatusMeta.ATIVA]
    
    def obter_metas_por_tipo(self, tipo: TipoMeta) -> List[Meta]:
        """Obtém metas por tipo"""
        return [meta for meta in self.metas if meta.tipo == tipo]
    
    def calcular_economia_total_metas(self) -> float:
        """Calcula o total economizado em todas as metas de economia"""
        metas_economia = self.obter_metas_por_tipo(TipoMeta.ECONOMIA)
        return sum(meta.valor_atual for meta in metas_economia)
    
    def obter_metas_vencendo(self, dias: int = 30) -> List[Meta]:
        """Obtém metas que vencem nos próximos X dias"""
        metas_vencendo = []
        for meta in self.obter_metas_ativas():
            if 0 <= meta.dias_restantes <= dias:
                metas_vencendo.append(meta)
        return sorted(metas_vencendo, key=lambda x: x.dias_restantes)
    
    def adicionar_orcamento(self, orcamento: OrcamentoCategoria) -> bool:
        """Adiciona um orçamento para categoria"""
        try:
            self.orcamentos = [o for o in self.orcamentos 
                             if not (o.categoria == orcamento.categoria and 
                                   o.mes == orcamento.mes and 
                                   o.ano == orcamento.ano)]
            self.orcamentos.append(orcamento)
            return True
        except Exception as e:
            print(f"Erro ao adicionar orçamento: {e}")
            return False
    
    def obter_orcamento_categoria(self, categoria: str, mes: int, ano: int) -> Optional[OrcamentoCategoria]:
        """Obtém orçamento de uma categoria específica"""
        for orcamento in self.orcamentos:
            if (orcamento.categoria == categoria and 
                orcamento.mes == mes and 
                orcamento.ano == ano):
                return orcamento
        return None
    
    def obter_orcamentos_mes(self, mes: int, ano: int) -> List[OrcamentoCategoria]:
        """Obtém todos os orçamentos de um mês"""
        return [o for o in self.orcamentos if o.mes == mes and o.ano == ano]
    
    def calcular_total_orcado(self, mes: int, ano: int) -> float:
        """Calcula o total orçado para um mês"""
        orcamentos = self.obter_orcamentos_mes(mes, ano)
        return sum(o.valor_orcado for o in orcamentos)
    
    def calcular_total_gasto_orcamento(self, mes: int, ano: int) -> float:
        """Calcula o total gasto no orçamento de um mês"""
        orcamentos = self.obter_orcamentos_mes(mes, ano)
        return sum(o.valor_gasto for o in orcamentos)
    
    def obter_categorias_excedidas(self, mes: int, ano: int) -> List[OrcamentoCategoria]:
        """Obtém categorias que excederam o orçamento"""
        orcamentos = self.obter_orcamentos_mes(mes, ano)
        return [o for o in orcamentos if o.status == "excedido"]
    
    def gerar_relatorio_metas(self) -> Dict:
        """Gera relatório completo das metas"""
        metas_ativas = self.obter_metas_ativas()
        
        return {
            'total_metas': len(self.metas),
            'metas_ativas': len(metas_ativas),
            'metas_concluidas': len([m for m in self.metas if m.status == StatusMeta.CONCLUIDA]),
            'economia_total': self.calcular_economia_total_metas(),
            'metas_vencendo': len(self.obter_metas_vencendo()),
            'percentual_medio': sum(m.percentual_concluido for m in metas_ativas) / len(metas_ativas) if metas_ativas else 0
        }
    
    def exportar_para_dict(self) -> Dict:
        """Exporta dados para dicionário"""
        return {
            'metas': [
                {
                    'id': m.id,
                    'nome': m.nome,
                    'tipo': m.tipo.value,
                    'valor_meta': m.valor_meta,
                    'valor_atual': m.valor_atual,
                    'percentual_concluido': m.percentual_concluido,
                    'valor_restante': m.valor_restante,
                    'dias_restantes': m.dias_restantes,
                    'data_inicio': m.data_inicio.isoformat(),
                    'data_fim': m.data_fim.isoformat(),
                    'categoria': m.categoria,
                    'descricao': m.descricao,
                    'status': m.status.value,
                    'cor': m.cor
                }
                for m in self.metas
            ],
            'orcamentos': [
                {
                    'categoria': o.categoria,
                    'valor_orcado': o.valor_orcado,
                    'valor_gasto': o.valor_gasto,
                    'valor_disponivel': o.valor_disponivel,
                    'percentual_usado': o.percentual_usado,
                    'status': o.status,
                    'mes': o.mes,
                    'ano': o.ano
                }
                for o in self.orcamentos
            ]
        }

# Instância global do gerenciador
gerenciador_metas = GerenciadorMetas()

if __name__ == "__main__":
    # Teste do sistema
    print("=== Sistema de Metas Nathfinance ===")
    
    for meta in gerenciador_metas.obter_metas_ativas():
        print(f"\n{meta.nome}")
        print(f"Progresso: R$ {meta.valor_atual:,.2f} / R$ {meta.valor_meta:,.2f}")
        print(f"Concluído: {meta.percentual_concluido:.1f}%")
        print(f"Restam: {meta.dias_restantes} dias")
        if meta.dias_restantes > 0:
            print(f"Necessário por dia: R$ {meta.valor_diario_necessario:.2f}")
    
    print("\n=== Orçamentos ===")
    mes_atual = date.today().month
    ano_atual = date.today().year
    
    for orcamento in gerenciador_metas.obter_orcamentos_mes(mes_atual, ano_atual):
        print(f"\n{orcamento.categoria}")
        print(f"Orçado: R$ {orcamento.valor_orcado:,.2f}")
        print(f"Gasto: R$ {orcamento.valor_gasto:,.2f}")
        print(f"Disponível: R$ {orcamento.valor_disponivel:,.2f}")
        print(f"Status: {orcamento.status} ({orcamento.percentual_usado:.1f}%)")
