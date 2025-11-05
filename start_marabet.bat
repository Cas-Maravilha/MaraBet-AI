@echo off
echo 🚀 INICIANDO MARABET AI...
echo.

echo 📦 Construindo containers...
docker-compose -f docker-compose.production.yml build
echo.

echo 🚀 Iniciando serviços...
docker-compose -f docker-compose.production.yml up -d
echo.

echo 📊 Status dos containers:
docker-compose -f docker-compose.production.yml ps
echo.

echo ✅ MaraBet AI iniciado!
echo 🌐 Acesse: http://localhost:8000
echo 📊 Dashboard: http://localhost:8000/dashboard
echo.
pause
