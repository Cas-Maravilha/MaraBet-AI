/**
 * MaraBet AI - Service Worker
 * Progressive Web App (PWA) Service Worker para cache offline
 * @version 1.0.0
 */

const CACHE_NAME = 'marabet-ai-v1.0.0';
const RUNTIME_CACHE = 'marabet-runtime-v1.0.0';

// Assets para cache imediato (instalação)
const STATIC_ASSETS = [
    '/',
    '/static/css/responsive.css',
    '/static/js/responsive.js',
    '/static/manifest.json',
    '/static/images/logo.svg',
    '/static/images/icon-192x192.png',
    '/static/images/icon-512x512.png',
    '/offline.html'
];

// Instalar Service Worker e fazer cache dos assets estáticos
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Instalando...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[Service Worker] Fazendo cache dos assets estáticos');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('[Service Worker] Instalação concluída');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('[Service Worker] Erro na instalação:', error);
            })
    );
});

// Ativar Service Worker e limpar caches antigos
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Ativando...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((cacheName) => {
                            return cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE;
                        })
                        .map((cacheName) => {
                            console.log('[Service Worker] Removendo cache antigo:', cacheName);
                            return caches.delete(cacheName);
                        })
                );
            })
            .then(() => {
                console.log('[Service Worker] Ativação concluída');
                return self.clients.claim();
            })
    );
});

// Interceptar requisições (estratégia Network First com fallback para Cache)
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Ignorar requisições não HTTP/HTTPS
    if (!request.url.startsWith('http')) {
        return;
    }
    
    // Estratégia para APIs: Network First
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            networkFirst(request)
        );
        return;
    }
    
    // Estratégia para assets estáticos: Cache First
    if (
        url.pathname.startsWith('/static/') ||
        request.destination === 'image' ||
        request.destination === 'style' ||
        request.destination === 'script'
    ) {
        event.respondWith(
            cacheFirst(request)
        );
        return;
    }
    
    // Estratégia padrão para páginas: Network First
    event.respondWith(
        networkFirst(request)
    );
});

/**
 * Estratégia Cache First
 * Busca primeiro no cache, se não encontrar busca na rede
 */
async function cacheFirst(request) {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
        console.log('[Service Worker] Servindo do cache:', request.url);
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        
        // Cache apenas respostas válidas
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('[Service Worker] Erro na rede:', error);
        
        // Retornar imagem placeholder para imagens
        if (request.destination === 'image') {
            return new Response(
                '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100" height="100" fill="#f0f0f0"/><text x="50" y="50" text-anchor="middle" dy=".3em" fill="#999">Sem imagem</text></svg>',
                { headers: { 'Content-Type': 'image/svg+xml' } }
            );
        }
        
        return new Response('Offline', { status: 503 });
    }
}

/**
 * Estratégia Network First
 * Tenta buscar na rede primeiro, se falhar usa cache
 */
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        
        // Cache a resposta se for válida
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('[Service Worker] Rede falhou, tentando cache:', request.url);
        
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Se for uma navegação, retornar página offline
        if (request.mode === 'navigate') {
            const offlinePage = await caches.match('/offline.html');
            if (offlinePage) {
                return offlinePage;
            }
        }
        
        return new Response('Offline - Sem conexão com internet', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
                'Content-Type': 'text/plain'
            })
        });
    }
}

// Push Notifications
self.addEventListener('push', (event) => {
    console.log('[Service Worker] Push recebido:', event);
    
    const options = {
        body: event.data ? event.data.text() : 'Nova notificação do MaraBet AI',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/badge-72x72.png',
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Ver',
                icon: '/static/images/checkmark.png'
            },
            {
                action: 'close',
                title: 'Fechar',
                icon: '/static/images/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('MaraBet AI', options)
    );
});

// Notification Click
self.addEventListener('notificationclick', (event) => {
    console.log('[Service Worker] Notificação clicada:', event);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Background Sync (sincronizar dados quando voltar online)
self.addEventListener('sync', (event) => {
    console.log('[Service Worker] Background sync:', event.tag);
    
    if (event.tag === 'sync-predictions') {
        event.waitUntil(syncPredictions());
    }
});

async function syncPredictions() {
    try {
        const response = await fetch('/api/sync-predictions', {
            method: 'POST'
        });
        
        if (response.ok) {
            console.log('[Service Worker] Sincronização concluída');
        }
    } catch (error) {
        console.error('[Service Worker] Erro na sincronização:', error);
        throw error; // Retry
    }
}

// Periodic Background Sync (atualizar dados periodicamente)
self.addEventListener('periodicsync', (event) => {
    if (event.tag === 'update-predictions') {
        event.waitUntil(updatePredictions());
    }
});

async function updatePredictions() {
    try {
        const response = await fetch('/api/predictions/today');
        const data = await response.json();
        
        // Notificar usuários sobre novas previsões
        if (data.new_predictions > 0) {
            self.registration.showNotification('MaraBet AI', {
                body: `${data.new_predictions} novas previsões disponíveis!`,
                icon: '/static/images/icon-192x192.png',
                badge: '/static/images/badge-72x72.png'
            });
        }
    } catch (error) {
        console.error('[Service Worker] Erro ao atualizar previsões:', error);
    }
}

// Message (comunicação com o app)
self.addEventListener('message', (event) => {
    console.log('[Service Worker] Mensagem recebida:', event.data);
    
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            caches.open(RUNTIME_CACHE)
                .then((cache) => cache.addAll(event.data.urls))
        );
    }
    
    if (event.data.type === 'CLEAR_CACHE') {
        event.waitUntil(
            caches.keys()
                .then((cacheNames) => {
                    return Promise.all(
                        cacheNames.map((cacheName) => caches.delete(cacheName))
                    );
                })
        );
    }
});

// Log de erro
self.addEventListener('error', (event) => {
    console.error('[Service Worker] Erro:', event.error);
});

// Log de erro não tratado
self.addEventListener('unhandledrejection', (event) => {
    console.error('[Service Worker] Promise rejeitada:', event.reason);
});

console.log('[Service Worker] Carregado e pronto!');

