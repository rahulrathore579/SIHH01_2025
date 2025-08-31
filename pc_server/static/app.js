// Plant Disease Detection & Sprinkler Control - PC Master Controller
// JavaScript for web interface

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const captureBtn = document.getElementById('captureBtn');
    const startCameraBtn = document.getElementById('startCameraBtn');
    const stopCameraBtn = document.getElementById('stopCameraBtn');
    const testPiBtn = document.getElementById('testPiBtn');
    const statusSpan = document.getElementById('status');
    const cameraStatus = document.getElementById('cameraStatus');
    const piStatus = document.getElementById('piStatus');
	const detectionStatus = document.getElementById('detectionStatus');
    const lastResult = document.getElementById('lastResult');
    const piConnectionStatus = document.getElementById('piConnectionStatus');

    // Initialize
    updateStatus('System ready');
    checkPiConnection();

    // Event listeners
    captureBtn.addEventListener('click', captureAndDetect);
    startCameraBtn.addEventListener('click', startCamera);
    stopCameraBtn.addEventListener('click', stopCamera);
    testPiBtn.addEventListener('click', testPiConnection);

    // Capture, detect disease, and control Pi
    async function captureAndDetect() {
        try {
            updateStatus('Capturing image and detecting disease...');
            captureBtn.disabled = true;

            const response = await fetch('/api/capture_and_detect', {
					method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.status === 'success') {
                updateStatus(`Detection complete: ${result.result}`);
                displayResult(result);
                updateTables();
            } else {
                updateStatus(`Error: ${result.error}`);
            }

        } catch (error) {
            updateStatus(`Error: ${error.message}`);
        } finally {
            captureBtn.disabled = false;
        }
    }

    // Start camera
    async function startCamera() {
        try {
            updateStatus('Starting camera...');
            startCameraBtn.disabled = true;

            const response = await fetch('/api/start_camera', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.status === 'success') {
                updateStatus('Camera started successfully');
                cameraStatus.textContent = 'Camera: Running';
                cameraStatus.className = 'camera-running';
            } else {
                updateStatus(`Camera error: ${result.message}`);
                cameraStatus.textContent = 'Camera: Error';
                cameraStatus.className = 'camera-error';
            }

        } catch (error) {
            updateStatus(`Camera error: ${error.message}`);
            cameraStatus.textContent = 'Camera: Error';
            cameraStatus.className = 'camera-error';
        } finally {
            startCameraBtn.disabled = false;
        }
    }

    // Stop camera
    async function stopCamera() {
        try {
            updateStatus('Stopping camera...');
            stopCameraBtn.disabled = true;

            const response = await fetch('/api/stop_camera', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.status === 'success') {
                updateStatus('Camera stopped successfully');
                cameraStatus.textContent = 'Camera: Stopped';
                cameraStatus.className = 'camera-stopped';
            } else {
                updateStatus(`Camera error: ${result.message}`);
            }

        } catch (error) {
            updateStatus(`Camera error: ${error.message}`);
        } finally {
            stopCameraBtn.disabled = false;
        }
    }

    // Test Pi connection
    async function testPiConnection() {
        try {
            updateStatus('Testing Pi connection...');
            testPiBtn.disabled = true;

            const response = await fetch('/api/test_pi_connection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.status === 'success') {
                updateStatus('Pi connection successful');
                piStatus.textContent = 'Pi connection: Connected';
                piStatus.className = 'pi-connected';
                piConnectionStatus.textContent = 'Connected';
                piConnectionStatus.className = 'connected';
			} else {
                updateStatus(`Pi connection failed: ${result.message}`);
                piStatus.textContent = 'Pi connection: Failed';
                piStatus.className = 'pi-failed';
                piConnectionStatus.textContent = 'Failed';
                piConnectionStatus.className = 'failed';
            }

        } catch (error) {
            updateStatus(`Pi connection error: ${error.message}`);
            piStatus.textContent = 'Pi connection: Error';
            piStatus.className = 'pi-error';
            piConnectionStatus.textContent = 'Error';
            piConnectionStatus.className = 'error';
        } finally {
            testPiBtn.disabled = false;
        }
    }

    // Check Pi connection on load
    async function checkPiConnection() {
        try {
            const response = await fetch('/api/test_pi_connection', {
				method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.status === 'success') {
                piStatus.textContent = 'Pi connection: Connected';
                piStatus.className = 'pi-connected';
                piConnectionStatus.textContent = 'Connected';
                piConnectionStatus.className = 'connected';
			} else {
                piStatus.textContent = 'Pi connection: Failed';
                piStatus.className = 'pi-failed';
                piConnectionStatus.textContent = 'Failed';
                piConnectionStatus.className = 'failed';
            }

        } catch (error) {
            piStatus.textContent = 'Pi connection: Error';
            piStatus.className = 'pi-error';
            piConnectionStatus.textContent = 'Error';
            piConnectionStatus.className = 'error';
        }
    }

    // Display detection result
    function displayResult(result) {
        const severityClass = result.severity > 70 ? 'high-severity' : 
                             result.severity > 30 ? 'medium-severity' : 'low-severity';
        
        const actionClass = result.action === 'on' ? 'action-on' : 'action-off';

        lastResult.innerHTML = `
            <div class="result-card ${severityClass}">
                <h4>🌱 Detection Result</h4>
                <p><strong>Disease:</strong> ${result.disease}</p>
                <p><strong>Severity:</strong> <span class="severity">${result.severity}%</span></p>
                <p><strong>Result:</strong> ${result.result}</p>
                <p><strong>Action:</strong> <span class="action-badge ${actionClass}">${result.action.toUpperCase()}</span></p>
                <p><strong>Duration:</strong> ${result.duration_ms}ms</p>
                <p><strong>Pi Response:</strong> ${result.pi_response.status}</p>
                <p><strong>Time:</strong> ${new Date(result.timestamp).toLocaleString()}</p>
            </div>
        `;
    }

    // Update status
    function updateStatus(message) {
        statusSpan.textContent = message;
        console.log(message);
    }

    // Update tables (refresh page for now)
    function updateTables() {
        // Refresh the page to show updated data
        setTimeout(() => {
            window.location.reload();
        }, 2000);
    }

    // Auto-refresh results every 30 seconds
    setInterval(() => {
        updateTables();
    }, 30000);
}); 