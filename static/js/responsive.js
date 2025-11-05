/**
 * MaraBet AI - JavaScript Responsivo
 * Funcionalidades mobile-first e interações touch-friendly
 * @version 1.0.0
 */

// ============================================
// INICIALIZAÇÃO
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('MaraBet AI - Sistema Responsivo Inicializado');
    
    initNavigation();
    initResponsiveFeatures();
    initTouchGestures();
    initLazyLoading();
    initPWA();
    detectDevice();
});

// ============================================
// NAVEGAÇÃO RESPONSIVA
// ============================================

function initNavigation() {
    const navbarToggle = document.getElementById('navbarToggle');
    const navbarMenu = document.getElementById('navbarMenu');
    
    if (navbarToggle && navbarMenu) {
        // Toggle menu mobile
        navbarToggle.addEventListener('click', () => {
            const isExpanded = navbarToggle.getAttribute('aria-expanded') === 'true';
            
            navbarToggle.classList.toggle('active');
            navbarMenu.classList.toggle('active');
            navbarToggle.setAttribute('aria-expanded', !isExpanded);
            
            // Prevenir scroll quando menu aberto
            document.body.style.overflow = navbarMenu.classList.contains('active') ? 'hidden' : '';
        });
        
        // Fechar menu ao clicar em link
        const menuLinks = navbarMenu.querySelectorAll('a');
        menuLinks.forEach(link => {
            link.addEventListener('click', () => {
                navbarToggle.classList.remove('active');
                navbarMenu.classList.remove('active');
                navbarToggle.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            });
        });
        
        // Fechar menu ao clicar fora
        document.addEventListener('click', (e) => {
            if (!navbarToggle.contains(e.target) && !navbarMenu.contains(e.target)) {
                if (navbarMenu.classList.contains('active')) {
                    navbarToggle.classList.remove('active');
                    navbarMenu.classList.remove('active');
                    navbarToggle.setAttribute('aria-expanded', 'false');
                    document.body.style.overflow = '';
                }
            }
        });
    }
    
    // Bottom navigation active state
    updateBottomNavigation();
}

function updateBottomNavigation() {
    const currentPath = window.location.pathname;
    const bottomNavItems = document.querySelectorAll('.bottom-nav-item');
    
    bottomNavItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// ============================================
// RECURSOS RESPONSIVOS
// ============================================

function initResponsiveFeatures() {
    // Detectar orientação
    window.addEventListener('orientationchange', handleOrientationChange);
    handleOrientationChange();
    
    // Resize adaptativo
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleResize, 250);
    });
    
    // Scroll adaptativo
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(handleScroll, 100);
    });
}

function handleOrientationChange() {
    const orientation = window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
    document.body.setAttribute('data-orientation', orientation);
    
    console.log(`Orientação: ${orientation}`);
}

function handleResize() {
    const width = window.innerWidth;
    let device;
    
    if (width < 768) {
        device = 'mobile';
    } else if (width < 1024) {
        device = 'tablet';
    } else {
        device = 'desktop';
    }
    
    document.body.setAttribute('data-device', device);
    console.log(`Dispositivo: ${device}, Largura: ${width}px`);
}

function handleScroll() {
    const navbar = document.querySelector('.navbar');
    
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }
}

// ============================================
// GESTOS TOUCH
// ============================================

function initTouchGestures() {
    // Swipe para navegação
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;
    
    document.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    });
    
    document.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleGesture();
    });
    
    function handleGesture() {
        const diffX = touchEndX - touchStartX;
        const diffY = touchEndY - touchStartY;
        
        // Detectar swipe horizontal
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
            if (diffX > 0) {
                console.log('Swipe Right');
                // Ação personalizada
            } else {
                console.log('Swipe Left');
                // Ação personalizada
            }
        }
        
        // Detectar swipe vertical
        if (Math.abs(diffY) > Math.abs(diffX) && Math.abs(diffY) > 50) {
            if (diffY > 0) {
                console.log('Swipe Down');
            } else {
                console.log('Swipe Up');
            }
        }
    }
    
    // Pull to refresh
    let touchStartYPull = 0;
    const pullThreshold = 80;
    
    document.addEventListener('touchstart', (e) => {
        if (window.scrollY === 0) {
            touchStartYPull = e.touches[0].clientY;
        }
    });
    
    document.addEventListener('touchmove', (e) => {
        if (window.scrollY === 0) {
            const touchY = e.touches[0].clientY;
            const diff = touchY - touchStartYPull;
            
            if (diff > pullThreshold) {
                // Mostrar indicador de refresh
                console.log('Pull to refresh ativado');
            }
        }
    });
}

// ============================================
// LAZY LOADING
// ============================================

function initLazyLoading() {
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback: carregar todas as imagens
        lazyImages.forEach(img => img.classList.add('loaded'));
    }
}

// ============================================
// PWA
// ============================================

function initPWA() {
    // Detectar se é PWA standalone
    if (window.matchMedia('(display-mode: standalone)').matches) {
        console.log('Rodando como PWA');
        document.body.classList.add('pwa-mode');
    }
    
    // Prompt de instalação
    let deferredPrompt;
    
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        // Mostrar botão de instalação
        showInstallPrompt();
    });
    
    window.addEventListener('appinstalled', () => {
        console.log('PWA instalado com sucesso');
        showToast('✅ App instalado! Pode acessar pelo ícone na tela inicial', 'success');
        deferredPrompt = null;
    });
    
    function showInstallPrompt() {
        const installBanner = document.createElement('div');
        installBanner.className = 'install-banner';
        installBanner.innerHTML = `
            <div class="install-banner-content">
                <div>
                    <strong>Instalar MaraBet AI</strong>
                    <p>Adicione à tela inicial para acesso rápido</p>
                </div>
                <button class="btn btn-primary" id="installBtn">Instalar</button>
                <button class="btn btn-outline" id="dismissBtn">Agora não</button>
            </div>
        `;
        
        document.body.appendChild(installBanner);
        
        document.getElementById('installBtn').addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                
                if (outcome === 'accepted') {
                    console.log('Usuário aceitou instalação');
                }
                
                deferredPrompt = null;
                installBanner.remove();
            }
        });
        
        document.getElementById('dismissBtn').addEventListener('click', () => {
            installBanner.remove();
        });
    }
}

// ============================================
// DETECÇÃO DE DISPOSITIVO
// ============================================

function detectDevice() {
    const userAgent = navigator.userAgent.toLowerCase();
    const isMobile = /mobile|android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent);
    const isTablet = /ipad|android(?!.*mobile)|tablet/i.test(userAgent);
    const isIOS = /iphone|ipad|ipod/i.test(userAgent);
    const isAndroid = /android/i.test(userAgent);
    
    const deviceInfo = {
        isMobile,
        isTablet,
        isDesktop: !isMobile && !isTablet,
        isIOS,
        isAndroid,
        isTouchDevice: 'ontouchstart' in window,
        screenWidth: window.innerWidth,
        screenHeight: window.innerHeight,
        pixelRatio: window.devicePixelRatio || 1
    };
    
    console.log('Dispositivo:', deviceInfo);
    
    // Adicionar classes ao body
    if (deviceInfo.isMobile) document.body.classList.add('is-mobile');
    if (deviceInfo.isTablet) document.body.classList.add('is-tablet');
    if (deviceInfo.isDesktop) document.body.classList.add('is-desktop');
    if (deviceInfo.isIOS) document.body.classList.add('is-ios');
    if (deviceInfo.isAndroid) document.body.classList.add('is-android');
    
    return deviceInfo;
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================

function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    
    if (!container) {
        console.warn('Toast container não encontrado');
        return;
    }
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'polite');
    
    container.appendChild(toast);
    
    // Animação de entrada
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remover após duração
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ============================================
// MODAL
// ============================================

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    const backdrop = document.querySelector('.modal-backdrop');
    
    if (modal && backdrop) {
        modal.classList.add('active');
        backdrop.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    const backdrop = document.querySelector('.modal-backdrop');
    
    if (modal && backdrop) {
        modal.classList.remove('active');
        backdrop.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Fechar modal ao clicar no backdrop
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-backdrop')) {
        const activeModal = document.querySelector('.modal.active');
        if (activeModal) {
            closeModal(activeModal.id);
        }
    }
});

// Fechar modal com ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const activeModal = document.querySelector('.modal.active');
        if (activeModal) {
            closeModal(activeModal.id);
        }
    }
});

// ============================================
// LOADING
// ============================================

function showLoading(message = 'A carregar...') {
    const overlay = document.getElementById('loading-overlay');
    
    if (overlay) {
        overlay.querySelector('p').textContent = message;
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// ============================================
// NETWORK STATUS
// ============================================

window.addEventListener('online', () => {
    console.log('Online');
    showToast('✅ Conexão restaurada', 'success');
    // Sincronizar dados pendentes
    syncOfflineData();
});

window.addEventListener('offline', () => {
    console.log('Offline');
    showToast('⚠️ Sem conexão à internet. Modo offline ativado.', 'warning', 5000);
});

function syncOfflineData() {
    // Sincronizar dados que foram salvos offline
    if ('serviceWorker' in navigator && 'sync' in ServiceWorkerRegistration.prototype) {
        navigator.serviceWorker.ready.then(registration => {
            return registration.sync.register('sync-predictions');
        });
    }
}

// ============================================
// PERFORMANCE
// ============================================

// Observar performance
if ('PerformanceObserver' in window) {
    const perfObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
            if (entry.entryType === 'navigation') {
                console.log('Tempo de carregamento:', entry.loadEventEnd - entry.fetchStart, 'ms');
            }
        });
    });
    
    perfObserver.observe({ entryTypes: ['navigation'] });
}

// ============================================
// UTILITÁRIOS
// ============================================

// Debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Format currency
function formatCurrency(value, currency = 'EUR') {
    return new Intl.NumberFormat('pt-AO', {
        style: 'currency',
        currency: currency
    }).format(value);
}

// Format date
function formatDate(date, options = {}) {
    return new Intl.DateTimeFormat('pt-AO', {
        dateStyle: 'medium',
        timeStyle: 'short',
        ...options
    }).format(new Date(date));
}

// ============================================
// EXPORT
// ============================================

// Tornar funções disponíveis globalmente
window.MaraBetAI = {
    showToast,
    openModal,
    closeModal,
    showLoading,
    hideLoading,
    formatCurrency,
    formatDate,
    debounce,
    throttle,
    detectDevice
};

console.log('MaraBet AI - JavaScript carregado com sucesso! ✅');

