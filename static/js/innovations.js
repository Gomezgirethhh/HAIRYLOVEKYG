/**
 * HAIRY LOVE - Funcionalidades Innovadoras
 * Sistema de Interactividad Dinámico
 */

// ==================== SISTEMA DE FAVORITOS ====================
class FavoriteSystem {
    constructor() {
        this.storageKey = 'hairylove_favorites';
        this.favorites = this.loadFavorites();
        this.init();
    }
    
    init() {
        document.querySelectorAll('.favorite-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.toggleFavorite(e));
            const petId = btn.getAttribute('data-pet-id');
            if (this.favorites.includes(petId)) {
                btn.classList.add('active');
                btn.innerHTML = '<i class="fas fa-heart"></i>';
            }
        });
    }
    
    toggleFavorite(e) {
        const btn = e.currentTarget;
        const petId = btn.getAttribute('data-pet-id');
        
        if (this.favorites.includes(petId)) {
            this.removeFavorite(petId);
            btn.classList.remove('active');
            btn.innerHTML = '<i class="far fa-heart"></i>';
        } else {
            this.addFavorite(petId);
            btn.classList.add('active');
            btn.innerHTML = '<i class="fas fa-heart"></i>';
            this.showNotification('¡Agregado a favoritos!', 'success');
        }
        
        this.saveFavorites();
    }
    
    addFavorite(petId) {
        if (!this.favorites.includes(petId)) {
            this.favorites.push(petId);
        }
    }
    
    removeFavorite(petId) {
        this.favorites = this.favorites.filter(id => id !== petId);
    }
    
    loadFavorites() {
        const stored = localStorage.getItem(this.storageKey);
        return stored ? JSON.parse(stored) : [];
    }
    
    saveFavorites() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.favorites));
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            ${message}
        `;
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: ${type === 'success' ? '#28a745' : '#17a2b8'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 2000;
            animation: slideInFromRight 0.5s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.5s ease';
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    }
}

// ==================== FILTROS DINÁMICOS ====================
class DynamicFilters {
    constructor() {
        this.filters = {};
        this.init();
    }
    
    init() {
        const filterInputs = document.querySelectorAll('[data-filter]');
        filterInputs.forEach(input => {
            input.addEventListener('change', () => this.applyFilters());
        });
    }
    
    applyFilters() {
        const pets = document.querySelectorAll('.mascota-card, .pet-card');
        const activeFilters = this.getActiveFilters();
        
        pets.forEach(pet => {
            if (this.matchesFilters(pet, activeFilters)) {
                pet.style.display = '';
                setTimeout(() => pet.classList.add('fade-in'), 50);
            } else {
                pet.style.display = 'none';
                pet.classList.remove('fade-in');
            }
        });
    }
    
    getActiveFilters() {
        const filters = {};
        document.querySelectorAll('[data-filter]').forEach(input => {
            if (input.value) {
                filters[input.Name] = input.value;
            }
        });
        return filters;
    }
    
    matchesFilters(pet, filters) {
        for (let key in filters) {
            const petValue = pet.getAttribute(`data-${key}`);
            if (petValue && petValue !== filters[key]) {
                return false;
            }
        }
        return true;
    }
}

// ==================== ANIMACIÓN DE SCROLL ====================
class ScrollAnimations {
    constructor() {
        this.observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };
        this.observer = new IntersectionObserver(
            this.handleIntersection.bind(this),
            this.observerOptions
        );
        this.init();
    }
    
    init() {
        document.querySelectorAll('[data-animate]').forEach(el => {
            this.observer.observe(el);
        });
    }
    
    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-on-scroll');
                this.observer.unobserve(entry.target);
            }
        });
    }
}

// ==================== BÚSQUEDA EN TIEMPO REAL ====================
class RealTimeSearch {
    constructor(searchInputId) {
        this.searchInput = document.getElementById(searchInputId);
        if (this.searchInput) {
            this.init();
        }
    }
    
    init() {
        this.searchInput.addEventListener('input', (e) => this.performSearch(e));
    }
    
    performSearch(e) {
        const query = e.target.value.toLowerCase();
        const results = document.querySelectorAll('.mascota-card, .pet-card');
        let visibleCount = 0;
        
        results.forEach(item => {
            const petName = item.getAttribute('data-pet-name')?.toLowerCase() || '';
            const petBreed = item.getAttribute('data-pet-breed')?.toLowerCase() || '';
            
            if (petName.includes(query) || petBreed.includes(query) || query === '') {
                item.style.display = '';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });
        
        // Mostrar mensaje si no hay resultados
        if (visibleCount === 0 && query !== '') {
            this.showNoResults();
        }
    }
    
    showNoResults() {
        let noResults = document.getElementById('noResults');
        if (!noResults) {
            noResults = document.createElement('div');
            noResults.id = 'noResults';
            noResults.style.cssText = `
                text-align: center;
                padding: 2rem;
                grid-column: 1 / -1;
                color: #a8419f;
                font-size: 1.1rem;
            `;
            document.querySelector('.mascotas-grid, .pets-grid')?.appendChild(noResults);
        }
        noResults.innerHTML = '<i class="fas fa-search" style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.5;"></i><p>No se encontraron mascotas con ese criterio</p>';
    }
}

// ==================== CARRUSELES ANIMADOS ====================
class AnimatedCarousel {
    constructor(carouselSelector) {
        this.carousel = document.querySelector(carouselSelector);
        if (this.carousel) {
            this.currentIndex = 0;
            this.items = this.carousel.querySelectorAll('.carousel-item');
            this.init();
        }
    }
    
    init() {
        if (this.items.length === 0) return;
        
        this.showItem(0);
        
        document.querySelector('.carousel-prev')?.addEventListener('click', () => this.prev());
        document.querySelector('.carousel-next')?.addEventListener('click', () => this.next());
        
        // Auto-avance cada 5 segundos
        setInterval(() => this.next(), 5000);
    }
    
    showItem(index) {
        this.items.forEach((item, i) => {
            item.style.display = i === index ? 'block' : 'none';
            if (i === index) {
                item.classList.add('fade-in');
            }
        });
    }
    
    next() {
        this.currentIndex = (this.currentIndex + 1) % this.items.length;
        this.showItem(this.currentIndex);
    }
    
    prev() {
        this.currentIndex = (this.currentIndex - 1 + this.items.length) % this.items.length;
        this.showItem(this.currentIndex);
    }
}

// ==================== CONTADOR ANIMADO ====================
class AnimatedCounter {
    constructor(selector, targetNumber, duration = 2000) {
        this.element = document.querySelector(selector);
        this.targetNumber = targetNumber;
        this.duration = duration;
        this.currentNumber = 0;
        this.init();
    }
    
    init() {
        const increment = this.targetNumber / (this.duration / 50);
        const interval = setInterval(() => {
            this.currentNumber += increment;
            if (this.currentNumber >= this.targetNumber) {
                this.currentNumber = this.targetNumber;
                clearInterval(interval);
            }
            this.element.textContent = Math.floor(this.currentNumber);
        }, 50);
    }
}

// ==================== MODAL INTERACTIVO ====================
class InteractiveModal {
    constructor(triggerId, modalId) {
        this.trigger = document.getElementById(triggerId);
        this.modal = document.getElementById(modalId);
        if (this.trigger && this.modal) {
            this.init();
        }
    }
    
    init() {
        this.trigger.addEventListener('click', () => this.open());
        document.querySelector(`#${this.modal.id} .close`)?.addEventListener('click', () => this.close());
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.close();
        });
    }
    
    open() {
        this.modal.style.display = 'flex';
        this.modal.style.animation = 'zoomIn 0.3s ease';
    }
    
    close() {
        this.modal.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            this.modal.style.display = 'none';
        }, 300);
    }
}

// ==================== VALIDACIÓN DE FORMULARIOS ====================
class FormValidator {
    constructor() {
        this.forms = document.querySelectorAll('form[data-validate]');
        this.init();
    }
    
    init() {
        this.forms.forEach(form => {
            form.addEventListener('submit', (e) => this.validateForm(e));
        });
    }
    
    validateForm(e) {
        const form = e.target;
        const inputs = form.querySelectorAll('[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.markInvalid(input);
                isValid = false;
            } else {
                this.markValid(input);
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            this.showError('Por favor completa todos los campos requeridos');
        }
    }
    
    markInvalid(input) {
        input.classList.add('error');
        input.style.animation = 'shake 0.3s ease';
    }
    
    markValid(input) {
        input.classList.remove('error');
    }
    
    showError(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger';
        alertDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        document.querySelector('main').prepend(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

// ==================== TEMA OSCURO/CLARO ====================
class ThemeToggler {
    constructor() {
        this.storageKey = 'hairylove_theme';
        this.init();
    }
    
    init() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggle());
        }
        this.loadTheme();
    }
    
    toggle() {
        const currentTheme = localStorage.getItem(this.storageKey) || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }
    
    applyTheme(theme) {
        if (theme === 'dark') {
            document.body.classList.add('dark-theme');
            localStorage.setItem(this.storageKey, 'dark');
        } else {
            document.body.classList.remove('dark-theme');
            localStorage.setItem(this.storageKey, 'light');
        }
    }
    
    loadTheme() {
        const theme = localStorage.getItem(this.storageKey) || 'light';
        this.applyTheme(theme);
    }
}

// ==================== INICIALIZACIÓN ====================
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar todos los sistemas
    new FavoriteSystem();
    new DynamicFilters();
    new ScrollAnimations();
    new RealTimeSearch('quickSearch');
    new FormValidator();
    new ThemeToggler();
    
    // Inicializar carruseles si existen
    if (document.querySelector('.carousel')) {
        new AnimatedCarousel('.carousel');
    }
    
    console.log('✨ Hairy Love - Funcionalidades innovadoras cargadas exitosamente');
});
