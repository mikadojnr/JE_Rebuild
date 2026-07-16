/**
 * John & Eniola Consultancy - Main JavaScript
 * AJAX handling and interactive features
 */

// Toast notification utility
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-4 rounded-lg text-white z-[110] shadow-lg transition-all duration-300 translate-x-full opacity-0 ${
        type === 'success' ? 'bg-emerald-500' :
        type === 'error' ? 'bg-red-500' :
        type === 'warning' ? 'bg-amber-500' :
        'bg-[#141495]'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
        toast.classList.add('translate-x-0', 'opacity-100');
    });

    setTimeout(() => {
        toast.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
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

// Custom confirmation modal
function showConfirmModal(options = {}) {
    const {
        title = 'Are you sure?',
        message = 'This action cannot be undone.',
        confirmText = 'Confirm',
        cancelText = 'Cancel',
        type = 'danger'
    } = options;

    return new Promise((resolve) => {
        const modal = document.getElementById('confirmModal');
        const backdrop = document.getElementById('confirmModalBackdrop');
        const content = document.getElementById('confirmModalContent');
        const icon = document.getElementById('confirmModalIcon');
        const titleEl = document.getElementById('confirmModalTitle');
        const messageEl = document.getElementById('confirmModalMessage');
        const cancelBtn = document.getElementById('confirmModalCancel');
        const confirmBtn = document.getElementById('confirmModalConfirm');

        const themes = {
            danger: {
                iconClass: 'fa-solid fa-trash-can',
                iconBg: 'bg-red-100',
                iconColor: 'text-red-600',
                confirmBg: 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
            },
            warning: {
                iconClass: 'fa-solid fa-triangle-exclamation',
                iconBg: 'bg-amber-100',
                iconColor: 'text-amber-600',
                confirmBg: 'bg-amber-600 hover:bg-amber-700 focus:ring-amber-500'
            },
            success: {
                iconClass: 'fa-solid fa-circle-check',
                iconBg: 'bg-emerald-100',
                iconColor: 'text-emerald-600',
                confirmBg: 'bg-emerald-600 hover:bg-emerald-700 focus:ring-emerald-500'
            },
            info: {
                iconClass: 'fa-solid fa-circle-info',
                iconBg: 'bg-[#141495]/10',
                iconColor: 'text-[#141495]',
                confirmBg: 'bg-[#141495] hover:bg-[#0f0f7a] focus:ring-[#141495]'
            }
        };

        const theme = themes[type] || themes.danger;

        icon.className = `mx-auto mb-5 w-16 h-16 rounded-full flex items-center justify-center ${theme.iconBg}`;
        icon.querySelector('i').className = `${theme.iconClass} text-2xl ${theme.iconColor}`;
        titleEl.textContent = title;
        messageEl.textContent = message;
        confirmBtn.textContent = confirmText;
        confirmBtn.className = `flex-1 px-6 py-4 text-sm font-semibold text-white rounded-br-2xl transition focus:outline-none focus:ring-2 focus:ring-offset-2 ${theme.confirmBg}`;
        cancelBtn.textContent = cancelText;

        modal.classList.remove('hidden');
        modal.classList.add('flex');
        requestAnimationFrame(() => {
            backdrop.classList.remove('opacity-0');
            content.classList.remove('scale-95', 'opacity-0');
            content.classList.add('scale-100', 'opacity-100');
        });

        function cleanup(result) {
            backdrop.classList.add('opacity-0');
            content.classList.add('scale-95', 'opacity-0');
            content.classList.remove('scale-100', 'opacity-100');
            setTimeout(() => {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
                cancelBtn.removeEventListener('click', onCancel);
                confirmBtn.removeEventListener('click', onConfirm);
                modal.removeEventListener('click', onBackdrop);
            }, 200);
            resolve(result);
        }

        function onCancel() { cleanup(false); }
        function onConfirm() { cleanup(true); }
        function onBackdrop(e) { if (e.target === modal) cleanup(false); }

        cancelBtn.addEventListener('click', onCancel);
        confirmBtn.addEventListener('click', onConfirm);
        modal.addEventListener('click', onBackdrop);
    });
}

// AJAX delete helper for admin
function deleteViaAjax(url, elementSelector = null) {
    return showConfirmModal({
        title: 'Delete Item',
        message: 'This will permanently delete this item. This action cannot be undone.',
        confirmText: 'Yes, Delete',
        type: 'danger'
    }).then(confirmed => {
        if (!confirmed) return false;

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
                        const removable = element.closest('.card, tr, .item') || element;
                        removable.remove();
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
window.showConfirmModal = showConfirmModal;
window.deleteViaAjax = deleteViaAjax;
window.smoothScroll = smoothScroll;
window.toggleMobileMenu = toggleMobileMenu;
