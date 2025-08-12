document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('emergency-form');
    const safeModeBtn = document.getElementById('safe-mode-btn');
    const shutdownBtn = document.getElementById('shutdown-btn');
    const emergencyKeyInput = document.getElementById('emergency-key');
    const alertMessageDiv = document.getElementById('alert-message');

    const handleApiCall = async (action) => {
        const emergencyKey = emergencyKeyInput.value;

        if (!emergencyKey) {
            showAlert('Emergency Key is required.', 'danger');
            return;
        }

        let confirmationMessage = `Are you sure you want to activate ${action.replace('_', ' ').toLowerCase()}?`;
        if (action === 'SHUTDOWN') {
            confirmationMessage = 'WARNING: This will initiate a platform-wide shutdown. This action is irreversible. Are you absolutely sure?';
        }

        if (!confirm(confirmationMessage)) {
            return;
        }

        try {
            const response = await fetch('/api/emergency/override', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Emergency-Key': emergencyKey,
                },
                body: JSON.stringify({ action: action }),
            });

            const result = await response.json();

            if (response.ok) {
                showAlert(result.message, 'success');
            } else {
                showAlert(result.detail || 'An unknown error occurred.', 'danger');
            }
        } catch (error) {
            console.error('API Call Error:', error);
            showAlert('Could not connect to the server.', 'danger');
        }
    };

    safeModeBtn.addEventListener('click', () => handleApiCall('SAFE_MODE'));
    shutdownBtn.addEventListener('click', () => handleApiCall('SHUTDOWN'));

    const showAlert = (message, type) => {
        alertMessageDiv.textContent = message;
        alertMessageDiv.className = `alert alert-${type}`;
        alertMessageDiv.style.display = 'block';

        setTimeout(() => {
            alertMessageDiv.style.display = 'none';
        }, 5000);
    };
});
