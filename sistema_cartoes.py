from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Dict, Optional
from enum import Enum

class StatusCartao(Enum):
    ATIVO = "ativo"
    BLOQUEADO = "bloqueado"
    CANCELADO = "cancelado"

class BandeiraCartao(Enum):
    VISA = "visa"
    MASTERCARD = "mastercard"
    ELO = "elo"
    AMERICAN_EXPRESS = "amex"
    HIPERCARD = "hipercard"

@dataclass
class Cartao:
    id: str
    nome: str
    bandeira: BandeiraCartao
    limite_total: float
    limite_usado: float
    dia_vencimento: int
    dia_fechamento: int
    status: StatusCartao
    cor: str = "#4A90E2"

    @property
    def limite_disponivel(self) -> float:
        return self.limite_total - self.limite_usado

    @property
    def percentual_usado(self) -> float:
        if self.limite_total == 0:
            return 0
        return (self.limite_usado / self.limite_total) * 100

    @property
    def proxima_fatura(self) -> date:
        hoje = date.today()
        if hoje.day <= self.dia_vencimento:
            return date(hoje.year, hoje.month, self.dia_vencimento)
        else:
            if hoje.month == 12:
                return date(hoje.year + 1, 1, self.dia_vencimento)
            else:
                return date(hoje.year, hoje.month + 1, self.dia_vencimento)

@dataclass
class TransacaoCartao:
    """Transação específica de cartão"""
    id: str
    cartao_id: str
    data: date
    descricao: str
    valor: float
    categoria: str
    parcelas: int = 1
    parcela_atual: int = 1
    estabelecimento: str = ""

class GerenciadorCartoes:
    """Gerenciador de cartões de crédito"""
    
    def __init__(self):
        self.cartoes: List[Cartao] = []
        self.transacoes: List[TransacaoCartao] = []
        self._carregar_cartoes_demo()
    
    def _carregar_cartoes_demo(self):
        self.cartoes = []
    
    def adicionar_cartao(self, cartao: Cartao) -> bool:
        """Adiciona um novo cartão"""
        try:
            self.cartoes.append(cartao)
            return True
        except Exception as e:
            print(f"Erro ao adicionar cartão: {e}")
            return False
    
    def obter_cartao(self, cartao_id: str) -> Optional[Cartao]:
        """Obtém um cartão pelo ID"""
        for cartao in self.cartoes:
            if cartao.id == cartao_id:
                return cartao
        return None
    
    def calcular_limite_total_usado(self) -> float:
        """Calcula o total usado em todos os cartões"""
        return sum(cartao.limite_usado for cartao in self.cartoes if cartao.status == StatusCartao.ATIVO)
    
    def calcular_limite_total_disponivel(self) -> float:
        """Calcula o limite total disponível"""
        return sum(cartao.limite_disponivel for cartao in self.cartoes if cartao.status == StatusCartao.ATIVO)
    
    def obter_cartoes_ativos(self) -> List[Cartao]:
        """Retorna apenas cartões ativos"""
        return [cartao for cartao in self.cartoes if cartao.status == StatusCartao.ATIVO]
    
    def obter_faturas_proximas(self, dias: int = 7) -> List[Dict]:
        """Obtém faturas que vencem nos próximos X dias"""
        faturas_proximas = []
        hoje = date.today()
        
        for cartao in self.obter_cartoes_ativos():
            proxima_fatura = cartao.proxima_fatura
            dias_restantes = (proxima_fatura - hoje).days
            
            if 0 <= dias_restantes <= dias:
                faturas_proximas.append({
                    'cartao': cartao,
                    'data_vencimento': proxima_fatura,
                    'dias_restantes': dias_restantes,
                    'valor': cartao.limite_usado
                })
        
        return sorted(faturas_proximas, key=lambda x: x['dias_restantes'])
    
    def adicionar_transacao_cartao(self, transacao: TransacaoCartao) -> bool:
        """Adiciona uma transação ao cartão"""
        try:
            cartao = self.obter_cartao(transacao.cartao_id)
            if not cartao:
                return False
            
            # Atualizar limite usado
            cartao.limite_usado += transacao.valor
            
            # Adicionar transação
            self.transacoes.append(transacao)
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar transação: {e}")
            return False
    
    def obter_transacoes_cartao(self, cartao_id: str) -> List[TransacaoCartao]:
        """Obtém transações de um cartão específico"""
        return [t for t in self.transacoes if t.cartao_id == cartao_id]
    
    def calcular_gastos_por_categoria_cartao(self, cartao_id: str) -> Dict[str, float]:
        """Calcula gastos por categoria para um cartão"""
        transacoes = self.obter_transacoes_cartao(cartao_id)
        gastos = {}
        
        for transacao in transacoes:
            categoria = transacao.categoria
            if categoria in gastos:
                gastos[categoria] += transacao.valor
            else:
                gastos[categoria] = transacao.valor
        
        return gastos
    
    def exportar_para_dict(self) -> Dict:
        """Exporta dados dos cartões para dicionário"""
        return {
            'cartoes': [
                {
                    'id': c.id,
                    'nome': c.nome,
                    'bandeira': c.bandeira.value,
                    'limite_total': c.limite_total,
                    'limite_usado': c.limite_usado,
                    'limite_disponivel': c.limite_disponivel,
                    'percentual_usado': c.percentual_usado,
                    'dia_vencimento': c.dia_vencimento,
                    'dia_fechamento': c.dia_fechamento,
                    'status': c.status.value,
                    'cor': c.cor,
                    'proxima_fatura': c.proxima_fatura.isoformat()
                }
                for c in self.cartoes
            ],
            'transacoes': [
                {
                    'id': t.id,
                    'cartao_id': t.cartao_id,
                    'data': t.data.isoformat(),
                    'descricao': t.descricao,
                    'valor': t.valor,
                    'categoria': t.categoria,
                    'parcelas': t.parcelas,
                    'parcela_atual': t.parcela_atual,
                    'estabelecimento': t.estabelecimento
                }
                for t in self.transacoes
            ]
        }

# Instância global do gerenciador
gerenciador_cartoes = GerenciadorCartoes()

if __name__ == "__main__":
    # Teste do sistema
    print("=== Sistema de Cartões Nathfinance ===")
    
    for cartao in gerenciador_cartoes.obter_cartoes_ativos():
        print(f"\n{cartao.nome} ({cartao.bandeira.value.upper()})")
        print(f"Limite: {cartao.limite_usado:,.2f} / {cartao.limite_total:,.2f}")
        print(f"Disponível: R$ {cartao.limite_disponivel:,.2f}")
        print(f"Uso: {cartao.percentual_usado:.1f}%")
        print(f"Próxima fatura: {cartao.proxima_fatura}")
    
    print(f"\nTotal usado: R$ {gerenciador_cartoes.calcular_limite_total_usado():,.2f}")
    print(f"Total disponível: R$ {gerenciador_cartoes.calcular_limite_total_disponivel():,.2f}")
    
    faturas = gerenciador_cartoes.obter_faturas_proximas(30)
    if faturas:
        print("\nFaturas próximas:")
        for fatura in faturas:
            print(f"- {fatura['cartao'].nome}: R$ {fatura['valor']:,.2f} em {fatura['dias_restantes']} dias")
