"""
Serviço de coleta de dados para o sistema MaraBet AI
"""
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from config.settings import settings
from utils.logger import get_logger, log_performance

logger = get_logger(__name__)

class CollectorService:
    """Serviço de coleta de dados de apostas esportivas"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.api_football_key = settings.api_football_key
        self.odds_api_key = settings.odds_api_key
        self.base_url_football = settings.api_football_base_url
        self.base_url_odds = settings.odds_api_base_url
        
    async def __aenter__(self):
        """Context manager entry"""
        await self.start_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close_session()
    
    async def start_session(self):
        """Iniciar sessão HTTP"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=settings.request_timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.info("🌐 Sessão HTTP iniciada")
    
    async def close_session(self):
        """Fechar sessão HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("🌐 Sessão HTTP fechada")
    
    @log_performance("Coleta de jogos")
    async def collect_matches(self, league_id: int, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coletar jogos de uma liga específica"""
        try:
            if not self.session:
                await self.start_session()
            
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            url = f"{self.base_url_football}/fixtures"
            params = {
                "league": league_id,
                "date": date,
                "season": 2024
            }
            headers = {
                "X-RapidAPI-Key": self.api_football_key,
                "X-RapidAPI-Host": "v3.football.api-sports.io"
            }
            
            logger.info(f"📊 Coletando jogos da liga {league_id} para {date}")
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    matches = data.get("response", [])
                    logger.info(f"✅ {len(matches)} jogos coletados da liga {league_id}")
                    return matches
                else:
                    logger.error(f"❌ Erro na API Football: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Erro ao coletar jogos: {e}")
            return []
    
    @log_performance("Coleta de odds")
    async def collect_odds(self, match_id: int, bookmaker: str = "elephant") -> List[Dict[str, Any]]:
        """Coletar odds de um jogo específico"""
        try:
            if not self.session:
                await self.start_session()
            
            url = f"{self.base_url_odds}/sports/soccer/odds"
            params = {
                "apiKey": self.odds_api_key,
                "sport": "soccer",
                "regions": "us,uk,eu",
                "markets": "h2h,spreads,totals",
                "oddsFormat": "decimal",
                "dateFormat": "iso"
            }
            
            logger.info(f"💰 Coletando odds do jogo {match_id} da {bookmaker}")
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    odds = data.get("data", [])
                    
                    # Filtrar por bookmaker específico
                    filtered_odds = [
                        odd for odd in odds 
                        if odd.get("bookmakers", [{}])[0].get("title", "").lower() == bookmaker.lower()
                    ]
                    
                    logger.info(f"✅ {len(filtered_odds)} odds coletadas da {bookmaker}")
                    return filtered_odds
                else:
                    logger.error(f"❌ Erro na API Odds: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Erro ao coletar odds: {e}")
            return []
    
    @log_performance("Coleta de estatísticas")
    async def collect_statistics(self, match_id: int) -> Dict[str, Any]:
        """Coletar estatísticas de um jogo"""
        try:
            if not self.session:
                await self.start_session()
            
            url = f"{self.base_url_football}/fixtures/statistics"
            params = {"fixture": match_id}
            headers = {
                "X-RapidAPI-Key": self.api_football_key,
                "X-RapidAPI-Host": "v3.football.api-sports.io"
            }
            
            logger.info(f"📈 Coletando estatísticas do jogo {match_id}")
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    stats = data.get("response", [])
                    logger.info(f"✅ Estatísticas coletadas do jogo {match_id}")
                    return stats
                else:
                    logger.error(f"❌ Erro na API Football: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Erro ao coletar estatísticas: {e}")
            return {}
    
    @log_performance("Coleta de dados históricos")
    async def collect_historical_data(self, team_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Coletar dados históricos de um time"""
        try:
            if not self.session:
                await self.start_session()
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            url = f"{self.base_url_football}/fixtures"
            params = {
                "team": team_id,
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
                "status": "finished"
            }
            headers = {
                "X-RapidAPI-Key": self.api_football_key,
                "X-RapidAPI-Host": "v3.football.api-sports.io"
            }
            
            logger.info(f"📚 Coletando dados históricos do time {team_id} ({days} dias)")
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    matches = data.get("response", [])
                    logger.info(f"✅ {len(matches)} jogos históricos coletados")
                    return matches
                else:
                    logger.error(f"❌ Erro na API Football: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados históricos: {e}")
            return []
    
    async def collect_all_data(self, league_ids: List[int]) -> Dict[str, Any]:
        """Coletar todos os dados de uma lista de ligas"""
        try:
            logger.info(f"🔄 Iniciando coleta completa de {len(league_ids)} ligas")
            
            all_data = {
                "matches": [],
                "odds": [],
                "statistics": [],
                "timestamp": datetime.now().isoformat()
            }
            
            for league_id in league_ids:
                # Coletar jogos
                matches = await self.collect_matches(league_id)
                all_data["matches"].extend(matches)
                
                # Coletar odds dos jogos
                for match in matches[:5]:  # Limitar a 5 jogos por liga
                    match_id = match.get("fixture", {}).get("id")
                    if match_id:
                        odds = await self.collect_odds(match_id)
                        all_data["odds"].extend(odds)
                        
                        # Coletar estatísticas
                        stats = await self.collect_statistics(match_id)
                        if stats:
                            all_data["statistics"].append({
                                "match_id": match_id,
                                "statistics": stats
                            })
            
            logger.info(f"✅ Coleta completa finalizada - {len(all_data['matches'])} jogos, {len(all_data['odds'])} odds")
            return all_data
            
        except Exception as e:
            logger.error(f"❌ Erro na coleta completa: {e}")
            return {"error": str(e)}
    
    def get_supported_bookmakers(self) -> List[str]:
        """Obter lista de casas de apostas suportadas"""
        return [
            "elephant", "kwanza", "premier", 
            "bantu", "1xbet", "mobet"
        ]
    
    def get_supported_leagues(self) -> List[Dict[str, Any]]:
        """Obter lista de ligas suportadas"""
        return [
            {"id": 39, "name": "Premier League", "country": "England"},
            {"id": 140, "name": "La Liga", "country": "Spain"},
            {"id": 78, "name": "Bundesliga", "country": "Germany"},
            {"id": 135, "name": "Serie A", "country": "Italy"},
            {"id": 61, "name": "Ligue 1", "country": "France"},
            {"id": 71, "name": "Brasileirão", "country": "Brazil"}
        ]
