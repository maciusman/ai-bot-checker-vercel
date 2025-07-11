// script.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('check-form');
    const urlInput = document.getElementById('url-input');
    const submitButton = document.getElementById('submit-button');
    const loader = document.getElementById('loader');
    const resultsOutput = document.getElementById('results-output');
    const resultsContainer = document.getElementById('results-container');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = urlInput.value.trim();
        if (!url) return;

        submitButton.disabled = true;
        submitButton.textContent = 'Testowanie...';
        loader.style.display = 'block';
        resultsContainer.style.display = 'none';
        resultsOutput.textContent = '';

        try {
            // WAŻNA ZMIANA: Używamy adresu API z Vercela
            const response = await fetch('/api/bot_checker', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Błąd serwera: ${response.status}`);
            }

            const data = await response.json();
            
            resultsOutput.textContent = data.report;
            resultsContainer.style.display = 'block';

        } catch (error) {
            resultsOutput.textContent = `Wystąpił błąd: ${error.message}\n\nSprawdź, czy wpisany URL jest poprawny i spróbuj ponownie.`;
            resultsContainer.style.display = 'block';
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Uruchom Test';
            loader.style.display = 'none';
        }
    });
});