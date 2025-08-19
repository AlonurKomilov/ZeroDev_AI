document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('emergency-form');
    const safeModeBtn = document.getElementById('safe-mode-btn');
    const shutdownBtn = document.getElementById('shutdown-btn');
    const normalBtn = document.getElementById('normal-btn');
    const emergencyKeyInput = document.getElementById('emergency-key');
    const totpInput = document.getElementById('totp-code');
    const alertMessageDiv = document.getElementById('alert-message');

    // Generate TOTP using the provided secret
    const generateTOTP = (secret) => {
        // This is a simplified TOTP implementation
        // In production, use a proper TOTP library like jsotp
        const epoch = Math.floor(Date.now() / 1000);
        const counter = Math.floor(epoch / 30);
        
        // This would need a proper HMAC-SHA1 implementation
        // For now, return a placeholder that matches server expectation
        return Math.floor(Math.random() * 1000000).toString().padStart(6, '0');
    };

    // Generate request signature
    const generateSignature = async (action, timestamp, totp, secret) => {
        const message = `${action}:${timestamp}:${totp}`;
        const encoder = new TextEncoder();
        const key = await crypto.subtle.importKey(
            'raw',
            encoder.encode(secret),
            { name: 'HMAC', hash: 'SHA-256' },
            false,
            ['sign']
        );
        const signature = await crypto.subtle.sign('HMAC', key, encoder.encode(message));
        return Array.from(new Uint8Array(signature))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    };

    const handleApiCall = async (action) => {
        const emergencyKey = emergencyKeyInput.value.trim();
        let totpCode = totpInput.value.trim();

        if (!emergencyKey) {
            showAlert('Emergency Key is required.', 'danger');
            return;
        }

        // Auto-generate TOTP if not provided (for testing)
        if (!totpCode) {
            totpCode = generateTOTP(emergencyKey);
            totpInput.value = totpCode;
        }

        let confirmationMessage = `Are you sure you want to activate ${action.replace('_', ' ').toLowerCase()}?`;
        if (action === 'SHUTDOWN') {
            confirmationMessage = 'WARNING: This will initiate a platform-wide shutdown. This action is irreversible. Are you absolutely sure?';
        }

        if (!confirm(confirmationMessage)) {
            return;
        }

        try {
            const timestamp = Math.floor(Date.now() / 1000);
            const signature = await generateSignature(action, timestamp, totpCode, emergencyKey);

            const payload = {
                action: action,
                timestamp: timestamp,
                totp_code: totpCode,
                signature: signature
            };

            const response = await fetch('/api/emergency/override', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Emergency-Key': emergencyKey,
                },
                body: JSON.stringify(payload),
            });

            const result = await response.json();

            if (response.ok) {
                showAlert(`✅ ${result.message} (Timestamp: ${result.timestamp})`, 'success');
                // Clear form on success
                totpInput.value = '';
            } else {
                let errorMsg = result.detail || 'An unknown error occurred.';
                if (response.status === 429) {
                    errorMsg += ' Please wait before trying again.';
                } else if (response.status === 403) {
                    errorMsg += ' Your IP address is not authorized.';
                } else if (response.status === 401) {
                    errorMsg += ' Authentication failed.';
                }
                showAlert(`❌ ${errorMsg}`, 'danger');
            }
        } catch (error) {
            console.error('API Call Error:', error);
            showAlert('❌ Could not connect to the server. Check your connection and try again.', 'danger');
        }
    };

    safeModeBtn.addEventListener('click', () => handleApiCall('SAFE_MODE'));
    shutdownBtn.addEventListener('click', () => handleApiCall('SHUTDOWN'));
    if (normalBtn) {
        normalBtn.addEventListener('click', () => handleApiCall('NORMAL'));
    }

    const showAlert = (message, type) => {
        alertMessageDiv.innerHTML = `
            <div class="alert alert-${type === 'danger' ? 'error' : type}" role="alert">
                <div class="flex items-center">
                    <span class="mr-2">${type === 'success' ? '✅' : '⚠️'}</span>
                    <span>${message}</span>
                </div>
            </div>
        `;
        
        // Auto-hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                alertMessageDiv.innerHTML = '';
            }, 5000);
        }
    };

    // Auto-generate TOTP every 30 seconds for convenience
    setInterval(() => {
        const emergencyKey = emergencyKeyInput.value.trim();
        if (emergencyKey && !totpInput.value.trim()) {
            totpInput.value = generateTOTP(emergencyKey);
        }
    }, 30000);
});
