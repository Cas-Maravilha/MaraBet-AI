"""
Sistema de Rotação de Chaves - MaraBet AI
Rotação automática e gerenciada de chaves de API
"""

import logging
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .secrets_manager import SecretsManager

logger = logging.getLogger(__name__)

class RotationStatus(Enum):
    """Status da rotação de chave"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class KeyRotationConfig:
    """Configuração de rotação para uma chave"""
    key_name: str
    rotation_interval_days: int
    warning_days: int
    auto_rotate: bool
    validation_callback: Optional[Callable[[str], bool]] = None
    notification_callback: Optional[Callable[[str, str], None]] = None

@dataclass
class KeyRotationRecord:
    """Registro de rotação de chave"""
    key_name: str
    old_value: str
    new_value: str
    rotated_at: datetime
    status: RotationStatus
    error_message: Optional[str] = None

class KeyRotator:
    """
    Sistema de rotação automática de chaves
    Gerencia rotação de chaves de API e credenciais
    """
    
    def __init__(self, secrets_manager: SecretsManager):
        """
        Inicializa o rotador de chaves
        
        Args:
            secrets_manager: Instância do gerenciador de secrets
        """
        self.secrets_manager = secrets_manager
        self.rotation_configs: Dict[str, KeyRotationConfig] = {}
        self.rotation_history: List[KeyRotationRecord] = []
        self.running = False
        self.scheduler_thread = None
        
        # Carregar configurações existentes
        self._load_rotation_configs()
    
    def _load_rotation_configs(self):
        """Carrega configurações de rotação do banco de secrets"""
        try:
            config_data = self.secrets_manager.get_secret("rotation_configs")
            if config_data:
                import json
                configs = json.loads(config_data)
                for key, config in configs.items():
                    self.rotation_configs[key] = KeyRotationConfig(**config)
                logger.info(f"✅ {len(self.rotation_configs)} configurações de rotação carregadas")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configurações de rotação: {e}")
    
    def _save_rotation_configs(self):
        """Salva configurações de rotação no banco de secrets"""
        try:
            configs = {}
            for key, config in self.rotation_configs.items():
                configs[key] = {
                    'key_name': config.key_name,
                    'rotation_interval_days': config.rotation_interval_days,
                    'warning_days': config.warning_days,
                    'auto_rotate': config.auto_rotate
                }
            
            import json
            self.secrets_manager.set_secret("rotation_configs", json.dumps(configs))
            logger.info("✅ Configurações de rotação salvas")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar configurações de rotação: {e}")
    
    def add_key_rotation(self, 
                        key_name: str,
                        rotation_interval_days: int = 90,
                        warning_days: int = 7,
                        auto_rotate: bool = True,
                        validation_callback: Optional[Callable[[str], bool]] = None,
                        notification_callback: Optional[Callable[[str, str], None]] = None) -> bool:
        """
        Adiciona uma chave ao sistema de rotação
        
        Args:
            key_name: Nome da chave
            rotation_interval_days: Intervalo de rotação em dias
            warning_days: Dias de aviso antes da rotação
            auto_rotate: Se deve rotacionar automaticamente
            validation_callback: Função para validar nova chave
            notification_callback: Função para notificações
            
        Returns:
            True se bem-sucedido
        """
        try:
            config = KeyRotationConfig(
                key_name=key_name,
                rotation_interval_days=rotation_interval_days,
                warning_days=warning_days,
                auto_rotate=auto_rotate,
                validation_callback=validation_callback,
                notification_callback=notification_callback
            )
            
            self.rotation_configs[key_name] = config
            self._save_rotation_configs()
            
            logger.info(f"✅ Chave {key_name} adicionada ao sistema de rotação")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar chave {key_name} à rotação: {e}")
            return False
    
    def remove_key_rotation(self, key_name: str) -> bool:
        """
        Remove uma chave do sistema de rotação
        
        Args:
            key_name: Nome da chave
            
        Returns:
            True se bem-sucedido
        """
        try:
            if key_name in self.rotation_configs:
                del self.rotation_configs[key_name]
                self._save_rotation_configs()
                logger.info(f"✅ Chave {key_name} removida do sistema de rotação")
                return True
            else:
                logger.warning(f"⚠️ Chave {key_name} não encontrada no sistema de rotação")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao remover chave {key_name} da rotação: {e}")
            return False
    
    def rotate_key(self, key_name: str, new_value: Optional[str] = None) -> bool:
        """
        Rotaciona uma chave específica
        
        Args:
            key_name: Nome da chave
            new_value: Novo valor (opcional, será gerado se não fornecido)
            
        Returns:
            True se bem-sucedido
        """
        try:
            if key_name not in self.rotation_configs:
                logger.error(f"❌ Chave {key_name} não configurada para rotação")
                return False
            
            config = self.rotation_configs[key_name]
            
            # Obter valor atual
            old_value = self.secrets_manager.get_secret(key_name)
            if not old_value:
                logger.error(f"❌ Chave {key_name} não encontrada")
                return False
            
            # Gerar novo valor se não fornecido
            if not new_value:
                new_value = self._generate_new_key(key_name)
            
            # Validar novo valor se callback fornecido
            if config.validation_callback:
                if not config.validation_callback(new_value):
                    logger.error(f"❌ Novo valor para {key_name} falhou na validação")
                    return False
            
            # Criar registro de rotação
            record = KeyRotationRecord(
                key_name=key_name,
                old_value=old_value,
                new_value=new_value,
                rotated_at=datetime.now(),
                status=RotationStatus.IN_PROGRESS
            )
            
            try:
                # Atualizar secret
                if self.secrets_manager.set_secret(key_name, new_value):
                    record.status = RotationStatus.COMPLETED
                    logger.info(f"✅ Chave {key_name} rotacionada com sucesso")
                    
                    # Notificar se callback fornecido
                    if config.notification_callback:
                        config.notification_callback(key_name, "rotated")
                else:
                    record.status = RotationStatus.FAILED
                    record.error_message = "Falha ao atualizar secret"
                    logger.error(f"❌ Falha ao rotacionar chave {key_name}")
                
            except Exception as e:
                record.status = RotationStatus.FAILED
                record.error_message = str(e)
                logger.error(f"❌ Erro ao rotacionar chave {key_name}: {e}")
            
            # Adicionar ao histórico
            self.rotation_history.append(record)
            
            return record.status == RotationStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"❌ Erro ao rotacionar chave {key_name}: {e}")
            return False
    
    def _generate_new_key(self, key_name: str) -> str:
        """
        Gera uma nova chave baseada no tipo
        
        Args:
            key_name: Nome da chave
            
        Returns:
            Nova chave gerada
        """
        import secrets
        import string
        
        # Gerar chave baseada no tipo
        if "api_key" in key_name.lower():
            # Chave de API: 32 caracteres alfanuméricos
            return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        elif "password" in key_name.lower():
            # Senha: 16 caracteres com símbolos
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            return ''.join(secrets.choice(chars) for _ in range(16))
        elif "token" in key_name.lower():
            # Token: 64 caracteres hexadecimais
            return secrets.token_hex(32)
        else:
            # Padrão: 24 caracteres alfanuméricos
            return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(24))
    
    def check_rotation_schedule(self) -> List[str]:
        """
        Verifica quais chaves precisam ser rotacionadas
        
        Returns:
            Lista de chaves que precisam rotação
        """
        try:
            keys_to_rotate = []
            current_time = datetime.now()
            
            for key_name, config in self.rotation_configs.items():
                if not config.auto_rotate:
                    continue
                
                # Obter última rotação
                last_rotation = self._get_last_rotation(key_name)
                
                if last_rotation:
                    days_since_rotation = (current_time - last_rotation).days
                    if days_since_rotation >= config.rotation_interval_days:
                        keys_to_rotate.append(key_name)
                else:
                    # Primeira rotação
                    keys_to_rotate.append(key_name)
            
            return keys_to_rotate
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar cronograma de rotação: {e}")
            return []
    
    def _get_last_rotation(self, key_name: str) -> Optional[datetime]:
        """Obtém data da última rotação de uma chave"""
        try:
            for record in reversed(self.rotation_history):
                if record.key_name == key_name and record.status == RotationStatus.COMPLETED:
                    return record.rotated_at
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao obter última rotação de {key_name}: {e}")
            return None
    
    def get_rotation_warnings(self) -> List[Dict[str, Any]]:
        """
        Obtém avisos de chaves que precisam ser rotacionadas em breve
        
        Returns:
            Lista de avisos
        """
        try:
            warnings = []
            current_time = datetime.now()
            
            for key_name, config in self.rotation_configs.items():
                if not config.auto_rotate:
                    continue
                
                last_rotation = self._get_last_rotation(key_name)
                if last_rotation:
                    days_since_rotation = (current_time - last_rotation).days
                    days_until_rotation = config.rotation_interval_days - days_since_rotation
                    
                    if 0 < days_until_rotation <= config.warning_days:
                        warnings.append({
                            'key_name': key_name,
                            'days_until_rotation': days_until_rotation,
                            'last_rotation': last_rotation.isoformat(),
                            'next_rotation': (last_rotation + timedelta(days=config.rotation_interval_days)).isoformat()
                        })
            
            return warnings
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter avisos de rotação: {e}")
            return []
    
    def start_auto_rotation(self):
        """Inicia rotação automática em background"""
        try:
            if self.running:
                logger.warning("⚠️ Rotação automática já está em execução")
                return
            
            self.running = True
            
            # Agendar verificação diária
            schedule.every().day.at("02:00").do(self._run_rotation_check)
            
            # Iniciar thread do scheduler
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            
            logger.info("✅ Rotação automática iniciada")
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar rotação automática: {e}")
    
    def stop_auto_rotation(self):
        """Para rotação automática"""
        try:
            self.running = False
            schedule.clear()
            
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=5)
            
            logger.info("✅ Rotação automática parada")
            
        except Exception as e:
            logger.error(f"❌ Erro ao parar rotação automática: {e}")
    
    def _scheduler_loop(self):
        """Loop principal do scheduler"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
            except Exception as e:
                logger.error(f"❌ Erro no scheduler de rotação: {e}")
                time.sleep(60)
    
    def _run_rotation_check(self):
        """Executa verificação de rotação agendada"""
        try:
            logger.info("🔄 Executando verificação de rotação agendada")
            
            # Verificar chaves que precisam rotação
            keys_to_rotate = self.check_rotation_schedule()
            
            for key_name in keys_to_rotate:
                logger.info(f"🔄 Rotacionando chave {key_name}")
                self.rotate_key(key_name)
            
            # Verificar avisos
            warnings = self.get_rotation_warnings()
            for warning in warnings:
                logger.warning(f"⚠️ Chave {warning['key_name']} precisa ser rotacionada em {warning['days_until_rotation']} dias")
            
            logger.info(f"✅ Verificação de rotação concluída: {len(keys_to_rotate)} chaves rotacionadas")
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de rotação: {e}")
    
    def get_rotation_history(self, key_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém histórico de rotações
        
        Args:
            key_name: Nome da chave (opcional, filtra por chave)
            
        Returns:
            Lista de registros de rotação
        """
        try:
            history = []
            
            for record in self.rotation_history:
                if key_name and record.key_name != key_name:
                    continue
                
                history.append({
                    'key_name': record.key_name,
                    'rotated_at': record.rotated_at.isoformat(),
                    'status': record.status.value,
                    'error_message': record.error_message
                })
            
            # Ordenar por data (mais recente primeiro)
            history.sort(key=lambda x: x['rotated_at'], reverse=True)
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter histórico de rotação: {e}")
            return []
    
    def get_rotation_status(self) -> Dict[str, Any]:
        """
        Obtém status geral do sistema de rotação
        
        Returns:
            Dicionário com status
        """
        try:
            total_keys = len(self.rotation_configs)
            auto_rotate_keys = sum(1 for config in self.rotation_configs.values() if config.auto_rotate)
            keys_to_rotate = len(self.check_rotation_schedule())
            warnings = len(self.get_rotation_warnings())
            
            return {
                'total_keys': total_keys,
                'auto_rotate_keys': auto_rotate_keys,
                'keys_to_rotate': keys_to_rotate,
                'warnings': warnings,
                'running': self.running,
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter status de rotação: {e}")
            return {}
