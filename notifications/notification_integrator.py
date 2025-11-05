import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time

from .notification_manager import (
    NotificationManager, Notification, NotificationType,
    send_prediction_alert, send_system_status, send_error_alert,
    send_performance_report, send_daily_report
)
from settings.settings import (
    NOTIFICATION_ENABLED, NOTIFICATION_PREDICTION_THRESHOLD,
    NOTIFICATION_CONFIDENCE_THRESHOLD, NOTIFICATION_COOLDOWN
)

logger = logging.getLogger(__name__)

class NotificationIntegrator:
    """Integrador de notificações com o sistema MaraBet AI"""
    
    def __init__(self):
        self.manager = NotificationManager()
        self.enabled = NOTIFICATION_ENABLED
        self.last_notifications = {}  # Cache para cooldown
        self.prediction_count = 0
        self.error_count = 0
        
        if self.enabled:
            logger.info("🔔 Sistema de notificações ativado")
        else:
            logger.warning("⚠️  Sistema de notificações desativado - configure as credenciais")
    
    async def notify_prediction(self, prediction_data: Dict, 
                              channels: List[str] = None) -> bool:
        """
        Notifica sobre nova predição encontrada
        
        Args:
            prediction_data: Dados da predição
            channels: Canais de notificação
        
        Returns:
            True se notificação foi enviada
        """
        if not self.enabled:
            return False
        
        try:
            # Verificar se atende critérios
            if not self._should_notify_prediction(prediction_data):
                return False
            
            # Verificar cooldown
            if self._is_in_cooldown('prediction', prediction_data.get('fixture_id')):
                return False
            
            # Enviar notificação
            result = await send_prediction_alert(prediction_data, channels)
            
            if any(result.values()):
                self.prediction_count += 1
                self._update_cooldown('prediction', prediction_data.get('fixture_id'))
                logger.info(f"🔔 Predição notificada: {prediction_data.get('market', 'N/A')}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao notificar predição: {e}")
            return False
    
    async def notify_system_status(self, status_data: Dict, 
                                 channels: List[str] = None) -> bool:
        """
        Notifica sobre mudança de status do sistema
        
        Args:
            status_data: Dados de status
            channels: Canais de notificação
        
        Returns:
            True se notificação foi enviada
        """
        if not self.enabled:
            return False
        
        try:
            # Verificar se houve mudança significativa
            if not self._should_notify_status(status_data):
                return False
            
            # Enviar notificação
            result = await send_system_status(status_data, channels)
            
            if any(result.values()):
                logger.info("🔔 Status do sistema notificado")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao notificar status: {e}")
            return False
    
    async def notify_error(self, error_message: str, error_data: Dict = None,
                         channels: List[str] = None) -> bool:
        """
        Notifica sobre erro no sistema
        
        Args:
            error_message: Mensagem de erro
            error_data: Dados adicionais do erro
            channels: Canais de notificação
        
        Returns:
            True se notificação foi enviada
        """
        if not self.enabled:
            return False
        
        try:
            # Verificar cooldown para erros
            if self._is_in_cooldown('error', error_message):
                return False
            
            # Enviar notificação
            result = await send_error_alert(error_message, error_data, channels)
            
            if any(result.values()):
                self.error_count += 1
                self._update_cooldown('error', error_message)
                logger.info(f"🔔 Erro notificado: {error_message[:50]}...")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao notificar erro: {e}")
            return False
    
    async def notify_performance(self, performance_data: Dict,
                               channels: List[str] = None) -> bool:
        """
        Notifica sobre métricas de performance
        
        Args:
            performance_data: Dados de performance
            channels: Canais de notificação
        
        Returns:
            True se notificação foi enviada
        """
        if not self.enabled:
            return False
        
        try:
            # Enviar notificação
            result = await send_performance_report(performance_data, channels)
            
            if any(result.values()):
                logger.info("🔔 Relatório de performance notificado")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao notificar performance: {e}")
            return False
    
    async def notify_daily_report(self, report_data: Dict,
                                channels: List[str] = None) -> bool:
        """
        Envia relatório diário
        
        Args:
            report_data: Dados do relatório
            channels: Canais de notificação
        
        Returns:
            True se notificação foi enviada
        """
        if not self.enabled:
            return False
        
        try:
            # Enviar notificação
            result = await send_daily_report(report_data, channels)
            
            if any(result.values()):
                logger.info("🔔 Relatório diário notificado")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao notificar relatório diário: {e}")
            return False
    
    def _should_notify_prediction(self, prediction_data: Dict) -> bool:
        """Verifica se deve notificar sobre a predição"""
        # Verificar EV mínimo
        expected_value = prediction_data.get('expected_value', 0)
        if expected_value < NOTIFICATION_PREDICTION_THRESHOLD:
            return False
        
        # Verificar confiança mínima
        confidence = prediction_data.get('confidence', 0)
        if confidence < NOTIFICATION_CONFIDENCE_THRESHOLD:
            return False
        
        # Verificar se é recomendada
        if not prediction_data.get('recommended', False):
            return False
        
        return True
    
    def _should_notify_status(self, status_data: Dict) -> bool:
        """Verifica se deve notificar sobre mudança de status"""
        # Notificar sempre sobre mudanças de status
        return True
    
    def _is_in_cooldown(self, notification_type: str, key: str) -> bool:
        """Verifica se está em período de cooldown"""
        cache_key = f"{notification_type}:{key}"
        
        if cache_key in self.last_notifications:
            last_time = self.last_notifications[cache_key]
            if time.time() - last_time < NOTIFICATION_COOLDOWN:
                return True
        
        return False
    
    def _update_cooldown(self, notification_type: str, key: str):
        """Atualiza o cooldown para uma notificação"""
        cache_key = f"{notification_type}:{key}"
        self.last_notifications[cache_key] = time.time()
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas das notificações"""
        return {
            'enabled': self.enabled,
            'prediction_count': self.prediction_count,
            'error_count': self.error_count,
            'telegram_enabled': self.manager.telegram_enabled,
            'email_enabled': self.manager.email_enabled,
            'cooldown_entries': len(self.last_notifications)
        }
    
    async def test_notifications(self, channels: List[str] = None) -> Dict[str, bool]:
        """Testa o sistema de notificações"""
        logger.info("🧪 Testando sistema de notificações...")
        
        # Dados de teste
        test_prediction = {
            'market': 'h2h',
            'selection': 'Home',
            'expected_value': 0.08,
            'confidence': 0.75,
            'stake_percentage': 0.03,
            'recommended': True,
            'match': {
                'home_team': 'Manchester City',
                'away_team': 'Arsenal',
                'league': 'Premier League'
            }
        }
        
        test_status = {
            'running': True,
            'total_matches': 150,
            'total_predictions': 25,
            'recommended_predictions': 8,
            'next_execution': '2025-10-14 19:00:00'
        }
        
        test_performance = {
            'total_predictions': 25,
            'average_ev': 0.06,
            'average_confidence': 0.78,
            'success_rate': 0.68
        }
        
        # Testar cada tipo de notificação
        results = {}
        
        try:
            results['prediction'] = await self.notify_prediction(test_prediction, channels)
        except Exception as e:
            logger.error(f"Erro no teste de predição: {e}")
            results['prediction'] = False
        
        try:
            results['status'] = await self.notify_system_status(test_status, channels)
        except Exception as e:
            logger.error(f"Erro no teste de status: {e}")
            results['status'] = False
        
        try:
            results['performance'] = await self.notify_performance(test_performance, channels)
        except Exception as e:
            logger.error(f"Erro no teste de performance: {e}")
            results['performance'] = False
        
        # Resultado do teste
        success_count = sum(results.values())
        total_tests = len(results)
        
        logger.info(f"🧪 Teste concluído: {success_count}/{total_tests} notificações enviadas")
        
        return results

# Instância global do integrador
notification_integrator = NotificationIntegrator()

# Funções de conveniência para uso em outros módulos
async def notify_prediction(prediction_data: Dict, channels: List[str] = None) -> bool:
    """Notifica sobre predição"""
    return await notification_integrator.notify_prediction(prediction_data, channels)

async def notify_system_status(status_data: Dict, channels: List[str] = None) -> bool:
    """Notifica sobre status do sistema"""
    return await notification_integrator.notify_system_status(status_data, channels)

async def notify_error(error_message: str, error_data: Dict = None, channels: List[str] = None) -> bool:
    """Notifica sobre erro"""
    return await notification_integrator.notify_error(error_message, error_data, channels)

async def notify_performance(performance_data: Dict, channels: List[str] = None) -> bool:
    """Notifica sobre performance"""
    return await notification_integrator.notify_performance(performance_data, channels)

async def notify_daily_report(report_data: Dict, channels: List[str] = None) -> bool:
    """Notifica relatório diário"""
    return await notification_integrator.notify_daily_report(report_data, channels)

def get_notification_stats() -> Dict:
    """Retorna estatísticas das notificações"""
    return notification_integrator.get_stats()

async def test_notifications(channels: List[str] = None) -> Dict[str, bool]:
    """Testa o sistema de notificações"""
    return await notification_integrator.test_notifications(channels)
