// ============================================================
//  PromptGen — app.js
//  Client-side JavaScript for the Prompt Generator
//
//  Responsibilities:
//  1. Copy the generated prompt to clipboard (home page)
//  2. Show a loading spinner on the Generate button
//  3. Utility: show the Bootstrap toast notification
// ============================================================


// ============================================================
//  copyPrompt()
//  Called when the "Copy Prompt" button is clicked on index.html.
//  Reads the text from #generatedPrompt and copies it.
// ============================================================
function copyPrompt() {
    // Get the element that holds the prompt text
    var promptEl = document.getElementById('generatedPrompt');
    if (!promptEl) return;

    var text = promptEl.innerText;

    // The Clipboard API is modern and works in all recent browsers
    navigator.clipboard.writeText(text).then(function() {

        // 1. Show the Bootstrap toast (defined in base.html)
        showCopyToast();

        // 2. Visually update the copy button to show success
        var btn = document.getElementById('copyBtn');
        if (btn) {
            var originalHTML = btn.innerHTML;

            // Change button appearance for 2.5 seconds
            btn.innerHTML = '<i class="bi bi-check2-circle me-1"></i>Copied!';
            btn.style.background = 'rgba(34, 197, 94, 0.18)';
            btn.style.borderColor = 'rgba(34, 197, 94, 0.4)';
            btn.style.color = '#4ade80';

            setTimeout(function() {
                btn.innerHTML = originalHTML;
                btn.style.background = '';
                btn.style.borderColor = '';
                btn.style.color = '';
            }, 2500);
        }

    }).catch(function(err) {
        // Fallback: alert the user if clipboard API fails (rare)
        console.error('Clipboard copy failed:', err);
        alert('Could not copy automatically.\nPlease select the text and press Ctrl+C.');
    });
}


// ============================================================
//  showCopyToast()
//  Shows the Bootstrap toast defined in base.html.
//  delay: how long (ms) the toast stays visible.
// ============================================================
function showCopyToast() {
    var toastEl = document.getElementById('copyToast');
    if (!toastEl) return;

    // Bootstrap's Toast API — delay in milliseconds
    var toast = new bootstrap.Toast(toastEl, { delay: 2500 });
    toast.show();
}


// ============================================================
//  DOM Ready — runs after the full page has loaded
// ============================================================
document.addEventListener('DOMContentLoaded', function() {

    // ----------------------------------------------------------
    //  Generate Button Loading State
    //  When the form is submitted, change the button to show
    //  a spinner so the user knows something is happening.
    // ----------------------------------------------------------
    var promptForm = document.getElementById('promptForm');
    var generateBtn = document.getElementById('generateBtn');

    if (promptForm && generateBtn) {
        promptForm.addEventListener('submit', function() {
            // Replace button text with a spinner
            generateBtn.innerHTML =
                '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>' +
                'Generating...';
            generateBtn.disabled = true;

            // Safety: re-enable after 8 seconds in case of error
            setTimeout(function() {
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<i class="bi bi-stars me-2"></i>Generate Prompt';
            }, 8000);
        });
    }

    // ----------------------------------------------------------
    //  Theme Toggle Handler [NEW]
    //  Persists user setting (light/dark) using localStorage
    // ----------------------------------------------------------
    var themeToggleBtn = document.getElementById('themeToggleBtn');
    if (themeToggleBtn) {
        var darkIcon = themeToggleBtn.querySelector('.theme-icon-dark');
        var lightIcon = themeToggleBtn.querySelector('.theme-icon-light');

        // Sync icons with current HTML class list
        if (document.documentElement.classList.contains('light-mode')) {
            if (darkIcon) darkIcon.classList.add('d-none');
            if (lightIcon) lightIcon.classList.remove('d-none');
        }

        themeToggleBtn.addEventListener('click', function() {
            var isLight = document.documentElement.classList.toggle('light-mode');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');

            if (isLight) {
                if (darkIcon) darkIcon.classList.add('d-none');
                if (lightIcon) lightIcon.classList.remove('d-none');
            } else {
                if (lightIcon) lightIcon.classList.add('d-none');
                if (darkIcon) darkIcon.classList.remove('d-none');
            }
        });
    }

});
