let barChart, lineChart;

async function uploadAndAnalyze(event) {
    event.preventDefault(); // Stop the refresh!

    const fileInput = document.getElementById('fileInput');
    const status = document.getElementById('status');
    const dashboard = document.getElementById('dashboard');

    if (!fileInput.files[0]) return alert("Select a file.");

    console.log("Starting analysis...");
    status.innerText = "Processing... (This takes ~45s for 500k rows)";

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('/analyze', { // Note: relative path works now!
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error(`Server Error: ${response.status}`);

        const data = await response.json();
        console.log("Data Received:", data);

        renderDashboard(data);
        status.innerText = "Analysis Complete.";
        dashboard.style.display = "block";

    } catch (error) {
        console.error("Error Detail:", error);
        status.innerText = "Error: " + error.message;
    }
}

function renderDashboard(data) {
    const visualData = data.charts || data.visuals;
    const ctxBar = document.getElementById('barChart').getContext('2d');
    const ctxLine = document.getElementById('lineChart').getContext('2d');

    if (barChart) barChart.destroy();
    if (lineChart) lineChart.destroy();

    barChart = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: visualData.bar_chart.labels,
            datasets: [{
                label: visualData.bar_chart.title,
                data: visualData.bar_chart.values,
                backgroundColor: '#3498db'
            }]
        }
    });

    lineChart = new Chart(ctxLine, {
        type: 'line',
        data: {
            labels: visualData.line_chart.labels,
            datasets: [{
                label: visualData.line_chart.title,
                data: visualData.line_chart.values,
                borderColor: '#e74c3c'
            }]
        }
    });
}