"""
Glossário e Conceitos - MaraBet AI
Sistema especializado para definições de termos técnicos e conceitos
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConceptDefinition:
    """Definição de conceito"""
    term: str
    acronym: str
    definition: str
    formula: str
    example: str
    importance: str
    category: str
    related_terms: List[str]

@dataclass
class GlossarySection:
    """Seção do glossário"""
    title: str
    concepts: List[ConceptDefinition]
    description: str

@dataclass
class Glossary:
    """Glossário completo"""
    title: str
    sections: List[GlossarySection]
    total_concepts: int
    last_updated: datetime

class GlossaryGenerator:
    """
    Gerador de Glossário e Conceitos
    Sistema completo para definições técnicas e conceitos
    """
    
    def __init__(self):
        self.concept_categories = self._load_concept_categories()
        self.formulas = self._load_formulas()
        self.examples = self._load_examples()
        
    def _load_concept_categories(self) -> Dict[str, str]:
        """Carrega categorias de conceitos"""
        return {
            'mathematical': 'Conceitos Matemáticos',
            'statistical': 'Conceitos Estatísticos',
            'betting': 'Conceitos de Apostas',
            'analysis': 'Conceitos de Análise',
            'risk': 'Conceitos de Risco',
            'performance': 'Conceitos de Performance'
        }
    
    def _load_formulas(self) -> Dict[str, str]:
        """Carrega fórmulas matemáticas"""
        return {
            'ev': 'EV = (Probabilidade × Odd) - 1',
            'kelly': 'Stake % = (f/4) × [(P × O) - 1] / (O - 1)',
            'roi': 'ROI = (Lucro / Investimento) × 100%',
            'yield': 'Yield = (Lucro Total / Stake Total) × 100%',
            'xg': 'xG = Σ(Probabilidade de Gol de cada chance)',
            'sharpe': 'Sharpe Ratio = (ROI - Taxa Livre de Risco) / Volatilidade',
            'drawdown': 'Drawdown = (Pico - Vale) / Pico × 100%',
            'win_rate': 'Taxa de Acerto = (Apostas Vencedoras / Total de Apostas) × 100%'
        }
    
    def _load_examples(self) -> Dict[str, str]:
        """Carrega exemplos práticos"""
        return {
            'ev': 'Se P = 0.68 e Odd = 1.65, então EV = (0.68 × 1.65) - 1 = +0.122 = +12.2%',
            'kelly': 'Se P = 0.68, O = 1.65 e f = 0.25, então Stake = (0.25/4) × [(0.68 × 1.65) - 1] / (1.65 - 1) = 4.7%',
            'roi': 'Se investiu R$ 1.000 e lucrou R$ 150, então ROI = (150/1000) × 100% = 15%',
            'yield': 'Se apostou R$ 5.000 e lucrou R$ 300, então Yield = (300/5000) × 100% = 6%',
            'xg': 'Se uma chance tem 20% de virar gol e outra 15%, então xG = 0.20 + 0.15 = 0.35',
            'sharpe': 'Se ROI = 12%, Taxa Livre = 3% e Volatilidade = 8%, então Sharpe = (12-3)/8 = 1.125',
            'drawdown': 'Se pico foi R$ 1.200 e vale R$ 1.100, então Drawdown = (1200-1100)/1200 = 8.33%',
            'win_rate': 'Se acertou 22 de 30 apostas, então Taxa de Acerto = (22/30) × 100% = 73.3%'
        }
    
    def generate_mathematical_concepts(self) -> List[ConceptDefinition]:
        """Gera conceitos matemáticos"""
        concepts = []
        
        # EV (Expected Value)
        concepts.append(ConceptDefinition(
            term="Expected Value",
            acronym="EV",
            definition="Valor esperado de retorno de uma aposta, calculado como a diferença entre o valor esperado de ganho e o valor apostado.",
            formula=self.formulas['ev'],
            example=self.examples['ev'],
            importance="CRÍTICA - Base para identificar apostas com valor positivo",
            category="mathematical",
            related_terms=["Probabilidade", "Odd", "Valor Positivo", "Kelly Criterion"]
        ))
        
        # Kelly Criterion
        concepts.append(ConceptDefinition(
            term="Kelly Criterion",
            acronym="Kelly",
            definition="Fórmula matemática para otimização do tamanho da aposta, maximizando o crescimento da banca a longo prazo.",
            formula=self.formulas['kelly'],
            example=self.examples['kelly'],
            importance="CRÍTICA - Otimiza o tamanho da aposta para maximizar lucros",
            category="mathematical",
            related_terms=["Expected Value", "Probabilidade", "Odd", "Gestão de Banca"]
        ))
        
        # xG (Expected Goals)
        concepts.append(ConceptDefinition(
            term="Expected Goals",
            acronym="xG",
            definition="Gols esperados baseados na qualidade das chances criadas, considerando posição, ângulo e tipo de finalização.",
            formula=self.formulas['xg'],
            example=self.examples['xg'],
            importance="ALTA - Métrica avançada para análise de performance ofensiva",
            category="mathematical",
            related_terms=["Chances", "Finalização", "Performance Ofensiva", "Análise Estatística"]
        ))
        
        return concepts
    
    def generate_statistical_concepts(self) -> List[ConceptDefinition]:
        """Gera conceitos estatísticos"""
        concepts = []
        
        # H2H (Head to Head)
        concepts.append(ConceptDefinition(
            term="Head to Head",
            acronym="H2H",
            definition="Confrontos diretos entre duas equipes, analisando resultados históricos e padrões de performance.",
            formula="H2H = Σ(Resultados Históricos) / Número de Confrontos",
            example="Manchester City vs Arsenal: 5 vitórias City, 2 vitórias Arsenal, 3 empates em 10 confrontos",
            importance="ALTA - Histórico direto é preditor importante de resultados futuros",
            category="statistical",
            related_terms=["Confrontos Diretos", "Histórico", "Padrões", "Tendências"]
        ))
        
        # Sharpe Ratio
        concepts.append(ConceptDefinition(
            term="Sharpe Ratio",
            acronym="Sharpe",
            definition="Medida de risco-ajustado que compara o retorno de uma estratégia com sua volatilidade.",
            formula=self.formulas['sharpe'],
            example=self.examples['sharpe'],
            importance="MÉDIA - Avalia eficiência da estratégia considerando o risco",
            category="statistical",
            related_terms=["ROI", "Volatilidade", "Risco", "Performance"]
        ))
        
        # Drawdown
        concepts.append(ConceptDefinition(
            term="Drawdown",
            acronym="DD",
            definition="Maior perda consecutiva desde um pico de capital, medindo o risco de perdas em sequência.",
            formula=self.formulas['drawdown'],
            example=self.examples['drawdown'],
            importance="ALTA - Mede o risco de perdas consecutivas",
            category="statistical",
            related_terms=["Risco", "Perdas", "Gestão de Banca", "Volatilidade"]
        ))
        
        return concepts
    
    def generate_betting_concepts(self) -> List[ConceptDefinition]:
        """Gera conceitos de apostas"""
        concepts = []
        
        # ROI (Return on Investment)
        concepts.append(ConceptDefinition(
            term="Return on Investment",
            acronym="ROI",
            definition="Retorno sobre investimento, medindo a lucratividade percentual de um conjunto de apostas.",
            formula=self.formulas['roi'],
            example=self.examples['roi'],
            importance="CRÍTICA - Principal métrica de lucratividade",
            category="betting",
            related_terms=["Lucro", "Investimento", "Rentabilidade", "Performance"]
        ))
        
        # Yield
        concepts.append(ConceptDefinition(
            term="Yield",
            acronym="Yield",
            definition="Rentabilidade percentual média por aposta, calculada como lucro total dividido pelo stake total.",
            formula=self.formulas['yield'],
            example=self.examples['yield'],
            importance="ALTA - Mede eficiência das apostas em relação ao capital investido",
            category="betting",
            related_terms=["Rentabilidade", "Stake", "Eficiência", "ROI"]
        ))
        
        # Win Rate
        concepts.append(ConceptDefinition(
            term="Taxa de Acerto",
            acronym="Win Rate",
            definition="Percentual de apostas vencedoras em relação ao total de apostas realizadas.",
            formula=self.formulas['win_rate'],
            example=self.examples['win_rate'],
            importance="ALTA - Mede precisão das previsões",
            category="betting",
            related_terms=["Precisão", "Apostas Vencedoras", "Previsões", "Acerto"]
        ))
        
        return concepts
    
    def generate_analysis_concepts(self) -> List[ConceptDefinition]:
        """Gera conceitos de análise"""
        concepts = []
        
        # Forma Recente
        concepts.append(ConceptDefinition(
            term="Forma Recente",
            acronym="Form",
            definition="Performance das equipes nos últimos jogos, considerando resultados, gols marcados e sofridos.",
            formula="Forma = Σ(Pontos dos últimos N jogos) / (N × 3)",
            example="Últimos 5 jogos: 3 vitórias, 1 empate, 1 derrota = 10 pontos de 15 possíveis = 66.7%",
            importance="ALTA - Indicador de momentum e tendência atual",
            category="analysis",
            related_terms=["Performance", "Momentum", "Tendência", "Últimos Jogos"]
        ))
        
        # Probabilidade Implícita
        concepts.append(ConceptDefinition(
            term="Probabilidade Implícita",
            acronym="Impl. Prob",
            definition="Probabilidade calculada a partir da odd oferecida pela casa de apostas.",
            formula="Probabilidade Implícita = 1 / Odd",
            example="Odd 1.65 → Probabilidade Implícita = 1/1.65 = 60.6%",
            importance="ALTA - Base para comparação com probabilidade real",
            category="analysis",
            related_terms=["Odd", "Probabilidade", "Casa de Apostas", "Valor"]
        ))
        
        # Over/Under
        concepts.append(ConceptDefinition(
            term="Over/Under",
            acronym="O/U",
            definition="Aposta sobre o número total de gols na partida, comparando com um valor limite estabelecido.",
            formula="Over X.5: Mais de X gols | Under X.5: Menos de X gols",
            example="Over 2.5: Aposta que haverá 3 ou mais gols na partida",
            importance="ALTA - Mercado popular e bem analisável",
            category="analysis",
            related_terms=["Gols", "Total", "Limite", "Mercado"]
        ))
        
        return concepts
    
    def generate_risk_concepts(self) -> List[ConceptDefinition]:
        """Gera conceitos de risco"""
        concepts = []
        
        # Gestão de Banca
        concepts.append(ConceptDefinition(
            term="Gestão de Banca",
            acronym="Bankroll",
            definition="Estratégia para gerenciar o capital disponível, definindo limites de aposta e controles de risco.",
            formula="Stake Máximo = Banca × Percentual Máximo",
            example="Banca de R$ 1.000 com limite de 5% = Stake máximo de R$ 50 por aposta",
            importance="CRÍTICA - Protege o capital e evita perdas excessivas",
            category="risk",
            related_terms=["Capital", "Limites", "Controle", "Proteção"]
        ))
        
        # Diversificação
        concepts.append(ConceptDefinition(
            term="Diversificação",
            acronym="Divers.",
            definition="Estratégia de espalhar o risco entre diferentes tipos de apostas, ligas e mercados.",
            formula="Risco Total = Σ(Risco Individual × Peso)",
            example="Apostar em diferentes ligas, mercados e horários para reduzir correlação",
            importance="ALTA - Reduz risco concentrado e volatilidade",
            category="risk",
            related_terms=["Risco", "Correlação", "Mercados", "Estratégia"]
        ))
        
        # Stop Loss
        concepts.append(ConceptDefinition(
            term="Stop Loss",
            acronym="SL",
            definition="Limite de perda estabelecido para interromper apostas quando atingido.",
            formula="Stop Loss = Banca Inicial × Percentual de Perda Máxima",
            example="Banca de R$ 1.000 com SL de 20% = Parar ao perder R$ 200",
            importance="ALTA - Protege contra perdas excessivas",
            category="risk",
            related_terms=["Limite", "Perda", "Proteção", "Controle"]
        ))
        
        return concepts
    
    def generate_performance_concepts(self) -> List[ConceptDefinition]:
        """Gera conceitos de performance"""
        concepts = []
        
        # Backtesting
        concepts.append(ConceptDefinition(
            term="Backtesting",
            acronym="Backtest",
            definition="Teste de uma estratégia usando dados históricos para avaliar sua performance antes da implementação.",
            formula="Performance = Σ(Resultados Históricos da Estratégia)",
            example="Testar estratégia de Over 2.5 com dados dos últimos 2 anos",
            importance="ALTA - Valida estratégia antes de usar dinheiro real",
            category="performance",
            related_terms=["Validação", "Histórico", "Estratégia", "Teste"]
        ))
        
        # Edge
        concepts.append(ConceptDefinition(
            term="Edge",
            acronym="Edge",
            definition="Vantagem competitiva sobre a casa de apostas, baseada em análise superior ou informações privilegiadas.",
            formula="Edge = Probabilidade Real - Probabilidade Implícita",
            example="Probabilidade real 70% vs implícita 60% = Edge de 10%",
            importance="CRÍTICA - Base para apostas lucrativas a longo prazo",
            category="performance",
            related_terms=["Vantagem", "Competitividade", "Análise", "Lucratividade"]
        ))
        
        # Value Bet
        concepts.append(ConceptDefinition(
            term="Value Bet",
            acronym="Value",
            definition="Aposta com valor positivo, onde a probabilidade real é maior que a implícita na odd.",
            formula="Value = (Probabilidade Real × Odd) - 1 > 0",
            example="Probabilidade real 65% e odd 1.70 = (0.65 × 1.70) - 1 = +10.5% de valor",
            importance="CRÍTICA - Identifica apostas com expectativa positiva",
            category="performance",
            related_terms=["Valor", "Probabilidade", "Odd", "Lucratividade"]
        ))
        
        return concepts
    
    def generate_glossary(self) -> Glossary:
        """Gera glossário completo"""
        
        logger.info("Gerando glossário completo de conceitos")
        
        try:
            sections = []
            
            # Conceitos Matemáticos
            mathematical_concepts = self.generate_mathematical_concepts()
            sections.append(GlossarySection(
                title="Conceitos Matemáticos",
                concepts=mathematical_concepts,
                description="Fórmulas e conceitos matemáticos fundamentais para análise de apostas"
            ))
            
            # Conceitos Estatísticos
            statistical_concepts = self.generate_statistical_concepts()
            sections.append(GlossarySection(
                title="Conceitos Estatísticos",
                concepts=statistical_concepts,
                description="Métricas estatísticas e análises quantitativas"
            ))
            
            # Conceitos de Apostas
            betting_concepts = self.generate_betting_concepts()
            sections.append(GlossarySection(
                title="Conceitos de Apostas",
                concepts=betting_concepts,
                description="Termos específicos do mercado de apostas esportivas"
            ))
            
            # Conceitos de Análise
            analysis_concepts = self.generate_analysis_concepts()
            sections.append(GlossarySection(
                title="Conceitos de Análise",
                concepts=analysis_concepts,
                description="Métodos e técnicas de análise de partidas"
            ))
            
            # Conceitos de Risco
            risk_concepts = self.generate_risk_concepts()
            sections.append(GlossarySection(
                title="Conceitos de Risco",
                concepts=risk_concepts,
                description="Gestão de risco e controle de perdas"
            ))
            
            # Conceitos de Performance
            performance_concepts = self.generate_performance_concepts()
            sections.append(GlossarySection(
                title="Conceitos de Performance",
                concepts=performance_concepts,
                description="Métricas de performance e otimização de estratégias"
            ))
            
            # Calcula total de conceitos
            total_concepts = sum(len(section.concepts) for section in sections)
            
            return Glossary(
                title="Glossário e Conceitos - MaraBet AI",
                sections=sections,
                total_concepts=total_concepts,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro na geração do glossário: {e}")
            return self._create_empty_glossary()
    
    def _create_empty_glossary(self) -> Glossary:
        """Cria glossário vazio em caso de erro"""
        return Glossary(
            title="Glossário e Conceitos - MaraBet AI",
            sections=[],
            total_concepts=0,
            last_updated=datetime.now()
        )
    
    def format_glossary(self, glossary: Glossary) -> str:
        """Formata glossário completo"""
        
        if not glossary or not glossary.sections:
            return "Glossário não disponível."
        
        report_parts = []
        
        # Cabeçalho
        report_parts.append("GLOSSÁRIO E CONCEITOS")
        report_parts.append("=" * 60)
        report_parts.append(f"Total de Conceitos: {glossary.total_concepts}")
        report_parts.append(f"Última Atualização: {glossary.last_updated.strftime('%d/%m/%Y %H:%M:%S')}")
        report_parts.append("")
        
        # Seções do glossário
        for section in glossary.sections:
            report_parts.append(f"📚 {section.title.upper()}")
            report_parts.append("-" * 50)
            report_parts.append(section.description)
            report_parts.append("")
            
            for concept in section.concepts:
                # Termo e sigla
                report_parts.append(f"🔹 {concept.term} ({concept.acronym})")
                
                # Definição
                report_parts.append(f"   Definição: {concept.definition}")
                
                # Fórmula
                if concept.formula:
                    report_parts.append(f"   Fórmula: {concept.formula}")
                
                # Exemplo
                if concept.example:
                    report_parts.append(f"   Exemplo: {concept.example}")
                
                # Importância
                importance_icon = "🔴" if concept.importance == "CRÍTICA" else "🟡" if concept.importance == "ALTA" else "🟢"
                report_parts.append(f"   Importância: {importance_icon} {concept.importance}")
                
                # Termos relacionados
                if concept.related_terms:
                    report_parts.append(f"   Relacionados: {', '.join(concept.related_terms)}")
                
                report_parts.append("")
            
            report_parts.append("")
        
        # Resumo
        report_parts.append("📊 RESUMO DO GLOSSÁRIO")
        report_parts.append("-" * 40)
        for section in glossary.sections:
            report_parts.append(f"• {section.title}: {len(section.concepts)} conceitos")
        
        report_parts.append(f"\nTotal: {glossary.total_concepts} conceitos definidos")
        
        return "\n".join(report_parts)

if __name__ == "__main__":
    # Teste do gerador de glossário
    generator = GlossaryGenerator()
    
    print("=== TESTE DO GERADOR DE GLOSSÁRIO ===")
    
    # Gera glossário completo
    glossary = generator.generate_glossary()
    
    # Formata glossário
    report = generator.format_glossary(glossary)
    
    print(report)
    
    print("\nTeste concluído!")
