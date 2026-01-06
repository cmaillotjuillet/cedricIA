// JavaScript principal pour CedricIA

// Auto-dismiss des messages flash après 5 secondes
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Confirmation avant suppression
function confirmDelete(message) {
    return confirm(message || 'Êtes-vous sûr de vouloir supprimer cet élément ?');
}

// Formatage automatique des numéros de téléphone
document.addEventListener('DOMContentLoaded', function() {
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 10) value = value.substring(0, 10);
            e.target.value = value.replace(/(\d{2})(?=\d)/g, '$1 ').trim();
        });
    });
});

// Recherche de créneaux disponibles (pour le formulaire de rendez-vous)
async function checkAvailableSlots(date) {
    try {
        const response = await fetch(`/appointments/available-slots?date=${date}`);
        const data = await response.json();
        return data.available_slots;
    } catch (error) {
        console.error('Erreur lors de la récupération des créneaux:', error);
        return [];
    }
}
