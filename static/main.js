document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar on mobile
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // Update timeseries chart when symbol changes
    const symbolSelector = document.getElementById('symbol-selector');
    const timeseriesChart = document.getElementById('timeseries-chart');
    
    if (symbolSelector && timeseriesChart) {
        symbolSelector.addEventListener('change', function() {
            const symbol = this.value;
            
            // Show loading state
            timeseriesChart.src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';
            timeseriesChart.alt = 'Loading...';
            
            // Fetch new chart data
            fetch(`/update_plot/${symbol}`)
                .then(response => response.json())
                .then(data => {
                    timeseriesChart.src = `data:image/png;base64,${data.plot}`;
                    timeseriesChart.alt = `Price Trend for ${symbol}`;
                })
                .catch(error => {
                    console.error('Error updating chart:', error);
                });
        });
    }
    
    // Toggle time period buttons
    const timeButtons = document.querySelectorAll('.btn-control');
    timeButtons.forEach(button => {
        button.addEventListener('click', function() {
            timeButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            // Here you would typically fetch new data for the selected time period
        });
    });
    
    // Simulate loading time for better UX
    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 500);
});