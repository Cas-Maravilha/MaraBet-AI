@echo off
echo 🔍 VERIFICANDO DOCKER...
echo.

echo 📊 Versão do Docker:
docker --version
echo.

echo 📊 Versão do Docker Compose:
docker-compose --version
echo.

echo 📊 Status do Docker:
docker info
echo.

echo 📊 Containers em execução:
docker ps
echo.

echo 📊 Imagens disponíveis:
docker images
echo.

echo ✅ Verificação concluída!
pause
