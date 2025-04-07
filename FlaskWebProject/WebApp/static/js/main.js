// Main JavaScript file for HotelGuru

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Date range picker for booking form
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    if (startDateInput && endDateInput) {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        startDateInput.min = today;
        
        // Update end date minimum when start date changes
        startDateInput.addEventListener('change', function() {
            if (startDateInput.value) {
                // Set minimum end date to start date
                endDateInput.min = startDateInput.value;
                
                // If end date is before start date, update it
                if (endDateInput.value && endDateInput.value < startDateInput.value) {
                    endDateInput.value = startDateInput.value;
                }
            }
        });
    }
    
    // Enable room filtering on rooms page
    const roomTypeFilter = document.getElementById('roomTypeFilter');
    if (roomTypeFilter) {
        // Room filtering logic would go here
    }
});
