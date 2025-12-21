// voyager.js
// Client-side JavaScript for The Voyager application
// Handles AJAX-based day regeneration without page reload

(function() {
    'use strict';
    
    console.log('Voyager.js loaded');
    
    // ========================================================================
    // CSRF TOKEN SETUP
    // ========================================================================
    
    /**
     * Retrieve CSRF token from meta tag in base.html
     * This token is required for all POST requests to Flask
     */
    const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
    
    if (!csrfTokenMeta) {
        console.warn('CSRF token meta tag not found. AJAX requests may fail.');
        return;
    }
    
    const csrfToken = csrfTokenMeta.getAttribute('content');
    
    
    // ========================================================================
    // REGENERATE DAY FUNCTIONALITY
    // ========================================================================
    
    /**
     * Get the trip ID from the itinerary container
     * This is stored once per page as data attribute
     */
    const itineraryContainer = document.getElementById('itinerary');
    
    // Only proceed if we're on a page with an itinerary
    if (!itineraryContainer) {
        console.log('No itinerary found on this page. Skipping regeneration setup.');
        return;
    }
    
    const tripId = itineraryContainer.getAttribute('data-tripid');
    
    if (!tripId) {
        console.error('Trip ID not found in itinerary container');
        return;
    }
    
    console.log(`Itinerary page detected for trip ID: ${tripId}`);
    
    
    /**
     * Attach event listeners to all regenerate buttons
     */
    const regenButtons = document.querySelectorAll('.regen-btn');
    
    if (regenButtons.length === 0) {
        console.log('No regenerate buttons found on this page.');
        return;
    }
    
    console.log(`Found ${regenButtons.length} regenerate button(s)`);
    
    
    regenButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Get the day number from the button's data attribute
            const dayNum = this.getAttribute('data-day');
            
            if (!dayNum) {
                console.error('Day number not found on button');
                alert('Error: Unable to determine which day to regenerate.');
                return;
            }
            
            console.log(`Regenerating Day ${dayNum} for Trip ${tripId}`);
            
            // Store reference to button and original text
            const btn = this;
            const originalText = btn.innerHTML;
            
            // Disable button and show loading state
            btn.disabled = true;
            btn.innerHTML = '<span class="regen-icon">⏳</span> Regenerating...';
            
            // Construct the API endpoint URL
            const url = `/trip/${tripId}/day/${dayNum}/regenerate`;
            
            // Send AJAX POST request
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken  // Flask-WTF expects this header
                },
                body: JSON.stringify({})  // Empty body; data is in URL
            })
            .then(function(response) {
                // Check if response is OK (status 200-299)
                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(function(data) {
                // Validate response data
                if (!data || !data.content) {
                    throw new Error('Invalid response: missing content field');
                }
                
                // Verify day number matches (optional but good practice)
                if (data.day && data.day != dayNum) {
                    console.warn(`Day number mismatch: expected ${dayNum}, got ${data.day}`);
                }
                
                // Find the content paragraph for this specific day
                const contentElement = document.querySelector(`#day-${dayNum} .day-content`);
                
                if (!contentElement) {
                    throw new Error(`Content element not found for Day ${dayNum}`);
                }
                
                // Update the content with the new itinerary
                contentElement.textContent = data.content;
                
                // Visual feedback: briefly highlight the updated day
                highlightDay(dayNum);
                
                console.log(`Successfully regenerated Day ${dayNum}`);
                
                // Optional: Show success message
                showTemporaryMessage(`Day ${dayNum} regenerated successfully!`, 'success');
            })
            .catch(function(error) {
                // Handle errors gracefully
                console.error('Error during regeneration:', error);
                
                // User-friendly error message
                alert(`Failed to regenerate Day ${dayNum}. ${error.message}\n\nPlease try again.`);
            })
            .finally(function() {
                // Always re-enable button and restore original text
                btn.disabled = false;
                btn.innerHTML = originalText;
            });
        });
    });
    
    
    // ========================================================================
    // HELPER FUNCTIONS
    // ========================================================================
    
    /**
     * Briefly highlight a day block to show it was updated
     * @param {string|number} dayNum - The day number to highlight
     */
    function highlightDay(dayNum) {
        const dayBlock = document.getElementById(`day-${dayNum}`);
        
        if (!dayBlock) {
            return;
        }
        
        // Add highlight class
        dayBlock.style.transition = 'background-color 0.3s ease';
        dayBlock.style.backgroundColor = '#fff3cd';
        
        // Remove highlight after 2 seconds
        setTimeout(function() {
            dayBlock.style.backgroundColor = '';
        }, 2000);
        
        // Scroll to the updated day (smooth scroll)
        dayBlock.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'nearest' 
        });
    }
    
    
    /**
     * Show a temporary success/info message
     * @param {string} message - Message to display
     * @param {string} type - Message type (success, error, info)
     */
    function showTemporaryMessage(message, type = 'info') {
        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type}`;
        messageDiv.textContent = message;
        messageDiv.style.position = 'fixed';
        messageDiv.style.top = '80px';
        messageDiv.style.right = '20px';
        messageDiv.style.zIndex = '1000';
        messageDiv.style.minWidth = '250px';
        messageDiv.style.animation = 'slideIn 0.3s ease';
        
        // Add to page
        document.body.appendChild(messageDiv);
        
        // Remove after 3 seconds
        setTimeout(function() {
            messageDiv.style.animation = 'slideOut 0.3s ease';
            setTimeout(function() {
                document.body.removeChild(messageDiv);
            }, 300);
        }, 3000);
    }
    
    
    // ========================================================================
    // INITIALIZE
    // ========================================================================
    
    console.log('Regeneration handlers attached successfully');
    
})();


// Simple CSS animations for temporary messages (inline for simplicity)
// These could also be added to style.css if preferred
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);