@echo off
echo 🛑 PARANDO MARABET AI...
echo.

echo 📦 Parando containers...
docker-compose -f docker-compose.production.yml down
echo.

echo 🧹 Limpando containers órfãos...
docker system prune -f
echo.

echo ✅ MaraBet AI parado!
pause
