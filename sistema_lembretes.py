from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from enum import Enum

class TipoLembrete(Enum):
    CONTA_FIXA = "conta_fixa"
    FATURA_CARTAO = "fatura_cartao"
    INVESTIMENTO = "investimento"
    META = "meta"
    PAGAMENTO = "pagamento"
    RECEBIMENTO = "recebimento"

class PrioridadeLembrete(Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"

class StatusLembrete(Enum):
    PENDENTE = "pendente"
    CONCLUIDO = "concluido"
    ATRASADO = "atrasado"
    CANCELADO = "cancelado"

@dataclass
class Lembrete:
    """Classe para representar um lembrete financeiro"""
    id: str
    titulo: str
    descricao: str
    tipo: TipoLembrete
    data_vencimento: date
    valor: float
    prioridade: PrioridadeLembrete
    status: StatusLembrete
    recorrente: bool = False
    categoria: str = ""
    observacoes: str = ""
    
    @property
    def dias_restantes(self) -> int:
        return (self.data_vencimento - date.today()).days
    
    @property
    def esta_vencido(self) -> bool:
        return self.data_vencimento < date.today()
    
    @property
    def vence_hoje(self) -> bool:
        return self.data_vencimento == date.today()
    
    @property
    def vence_amanha(self) -> bool:
        return self.data_vencimento == date.today() + timedelta(days=1)
    
    @property
    def cor_prioridade(self) -> str:
        cores = {
            PrioridadeLembrete.BAIXA: "#28a745",
            PrioridadeLembrete.MEDIA: "#ffc107", 
            PrioridadeLembrete.ALTA: "#fd7e14",
            PrioridadeLembrete.URGENTE: "#dc3545"
        }
        return cores.get(self.prioridade, "#6c757d")

class GerenciadorLembretes:
    """Gerenciador de lembretes financeiros"""
    
    def __init__(self):
        self.lembretes: List[Lembrete] = []
    

    
    def adicionar_lembrete(self, lembrete: Lembrete) -> bool:
        """Adiciona um novo lembrete"""
        try:
            self.lembretes.append(lembrete)
            return True
        except Exception as e:
            print(f"Erro ao adicionar lembrete: {e}")
            return False
    
    def marcar_como_concluido(self, lembrete_id: str) -> bool:
        """Marca um lembrete como concluído"""
        try:
            lembrete = self.obter_lembrete(lembrete_id)
            if lembrete:
                lembrete.status = StatusLembrete.CONCLUIDO
                return True
            return False
        except Exception as e:
            print(f"Erro ao marcar lembrete: {e}")
            return False
    
    def obter_lembrete(self, lembrete_id: str) -> Optional[Lembrete]:
        """Obtém um lembrete pelo ID"""
        for lembrete in self.lembretes:
            if lembrete.id == lembrete_id:
                return lembrete
        return None
    
    def obter_lembretes_pendentes(self) -> List[Lembrete]:
        """Retorna lembretes pendentes"""
        return [l for l in self.lembretes if l.status == StatusLembrete.PENDENTE]
    
    def obter_lembretes_vencidos(self) -> List[Lembrete]:
        """Retorna lembretes vencidos"""
        pendentes = self.obter_lembretes_pendentes()
        return [l for l in pendentes if l.esta_vencido]
    
    def obter_lembretes_hoje(self) -> List[Lembrete]:
        """Retorna lembretes que vencem hoje"""
        pendentes = self.obter_lembretes_pendentes()
        return [l for l in pendentes if l.vence_hoje]
    
    def obter_lembretes_proximos(self, dias: int = 7) -> List[Lembrete]:
        """Retorna lembretes dos próximos X dias"""
        pendentes = self.obter_lembretes_pendentes()
        return [l for l in pendentes if 0 <= l.dias_restantes <= dias]
    
    def obter_lembretes_por_tipo(self, tipo: TipoLembrete) -> List[Lembrete]:
        """Obtém lembretes por tipo"""
        return [l for l in self.lembretes if l.tipo == tipo]
    
    def obter_lembretes_por_prioridade(self, prioridade: PrioridadeLembrete) -> List[Lembrete]:
        """Obtém lembretes por prioridade"""
        return [l for l in self.lembretes if l.prioridade == prioridade]
    
    def calcular_valor_total_pendente(self) -> float:
        """Calcula valor total dos lembretes pendentes"""
        pendentes = self.obter_lembretes_pendentes()
        return sum(l.valor for l in pendentes if l.tipo in [TipoLembrete.CONTA_FIXA, TipoLembrete.FATURA_CARTAO, TipoLembrete.PAGAMENTO])
    
    def gerar_alertas(self) -> List[Dict]:
        """Gera alertas baseados nos lembretes"""
        alertas = []
        
        vencidos = self.obter_lembretes_vencidos()
        if vencidos:
            alertas.append({
                'tipo': 'danger',
                'titulo': f'{len(vencidos)} lembrete(s) vencido(s)',
                'descricao': f'Você tem {len(vencidos)} lembrete(s) em atraso',
                'icone': '⚠️'
            })
        
        hoje = self.obter_lembretes_hoje()
        if hoje:
            alertas.append({
                'tipo': 'warning',
                'titulo': f'{len(hoje)} lembrete(s) para hoje',
                'descricao': f'Você tem {len(hoje)} compromisso(s) para hoje',
                'icone': '📅'
            })
        
        urgentes = [l for l in self.obter_lembretes_proximos(3) if l.prioridade == PrioridadeLembrete.URGENTE]
        if urgentes:
            alertas.append({
                'tipo': 'info',
                'titulo': f'{len(urgentes)} lembrete(s) urgente(s)',
                'descricao': f'Você tem {len(urgentes)} lembrete(s) urgente(s) nos próximos 3 dias',
                'icone': '🚨'
            })
        
        return alertas
    
    def exportar_para_dict(self) -> Dict:
        """Exporta lembretes para dicionário"""
        return {
            'lembretes': [
                {
                    'id': l.id,
                    'titulo': l.titulo,
                    'descricao': l.descricao,
                    'tipo': l.tipo.value,
                    'data_vencimento': l.data_vencimento.isoformat(),
                    'valor': l.valor,
                    'prioridade': l.prioridade.value,
                    'status': l.status.value,
                    'recorrente': l.recorrente,
                    'categoria': l.categoria,
                    'observacoes': l.observacoes,
                    'dias_restantes': l.dias_restantes,
                    'esta_vencido': l.esta_vencido,
                    'cor_prioridade': l.cor_prioridade
                }
                for l in self.lembretes
            ]
        }

gerenciador_lembretes = GerenciadorLembretes()

if __name__ == "__main__":
    print("=== Sistema de Lembretes Nathfinance ===")
    
    print("\nLembretes Pendentes:")
    for lembrete in gerenciador_lembretes.obter_lembretes_pendentes():
        status_emoji = "🔴" if lembrete.esta_vencido else "🟡" if lembrete.vence_hoje else "🟢"
        print(f"{status_emoji} {lembrete.titulo} - R$ {lembrete.valor:,.2f}")
        print(f"   Vence em: {lembrete.dias_restantes} dias ({lembrete.data_vencimento})")
        print(f"   Prioridade: {lembrete.prioridade.value}")
    
    print(f"\nTotal pendente: R$ {gerenciador_lembretes.calcular_valor_total_pendente():,.2f}")
    
    alertas = gerenciador_lembretes.gerar_alertas()
    if alertas:
        print("\nAlertas:")
        for alerta in alertas:
            print(f"{alerta['icone']} {alerta['titulo']}: {alerta['descricao']}")
