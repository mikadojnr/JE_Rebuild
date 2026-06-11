/**
 * John & Eniola Consultancy - Main JavaScript
 * AJAX handling and interactive features
 */

// Toast notification utility
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-4 rounded-lg text-white z-50 ${
        type === 'success' ? 'bg-green-500' :
        type === 'error' ? 'bg-red-500' :
        'bg-blue-500'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.remove(), 3000);
}

// AJAX form submission helper
function submitFormViaAjax(formId, onSuccess = null) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Loading...';
        submitBtn.disabled = true;
        
        fetch(this.action || window.location.href, {
            method: this.method || 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                if (onSuccess) onSuccess(data);
            } else {
                showToast(data.message || 'An error occurred', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('An error occurred. Please try again.', 'error');
        })
        .finally(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    });
}

// Delete confirmation
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// AJAX delete helper for admin
function deleteViaAjax(url, elementSelector = null) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            if (elementSelector) {
                const element = document.querySelector(elementSelector);
                if (element) {
                    element.closest('.card, tr, .item').remove();
                }
            }
            return true;
        } else {
            showToast(data.message || 'Error deleting', 'error');
            return false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred', 'error');
        return false;
    });
}

// Smooth scroll to element
function smoothScroll(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// Toggle mobile menu
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

// Initialize tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(el => {
        el.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute bg-gray-900 text-white px-3 py-1 rounded text-sm whitespace-nowrap';
            tooltip.textContent = this.getAttribute('data-tooltip');
            this.appendChild(tooltip);
            
            setTimeout(() => tooltip.remove(), 3000);
        });
    });
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Dynamic table row deletion
function setupDeleteButtons() {
    document.querySelectorAll('[data-delete-url]').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            if (!confirmDelete()) return;
            
            const url = this.getAttribute('data-delete-url');
            const row = this.closest('tr') || this.closest('.card');
            
            if (await deleteViaAjax(url)) {
                row && row.remove();
            }
        });
    });
}

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    setupDeleteButtons();
});

// Export functions for global use
window.showToast = showToast;
window.submitFormViaAjax = submitFormViaAjax;
window.confirmDelete = confirmDelete;
window.deleteViaAjax = deleteViaAjax;
window.smoothScroll = smoothScroll;
window.toggleMobileMenu = toggleMobileMenu;
