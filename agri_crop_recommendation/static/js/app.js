// Farmer Crop Recommendation App

// API Base URL
const API_BASE = window.location.origin;

// Load regions on page load
document.addEventListener('DOMContentLoaded', () => {
    loadRegions();
    setupFormHandlers();
});

// Load regions from API
async function loadRegions() {
    try {
        const response = await fetch(`${API_BASE}/regions`);
        const data = await response.json();
        
        const regionSelect = document.getElementById('region');
        regionSelect.innerHTML = '<option value="">-- अपना जिला चुनें / Select Your District --</option>';
        
        data.regions.forEach(region => {
            const option = document.createElement('option');
            option.value = region.region_id;
            option.textContent = `${region.name} (${region.climate_zone})`;
            regionSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading regions:', error);
        showAlert('Error loading regions. Please refresh the page.', 'error');
    }
}

// Setup form handlers
function setupFormHandlers() {
    const form = document.getElementById('recommendationForm');
    form.addEventListener('submit', handleFormSubmit);
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // Get form data
    const formData = {
        region_id: document.getElementById('region').value,
        irrigation: document.getElementById('irrigation').value,
        planning_days: parseInt(document.getElementById('planning_days').value)
    };
    
    // Add soil data if provided
    const soilTexture = document.getElementById('soil_texture').value;
    const soilPh = document.getElementById('soil_ph').value;
    
    if (soilTexture && soilPh) {
        formData.soil = {
            texture: soilTexture,
            ph: parseFloat(soilPh),
            organic_matter: document.getElementById('soil_organic').value,
            drainage: document.getElementById('soil_drainage').value
        };
    }
    
    // Validate
    if (!formData.region_id) {
        showAlert('कृपया अपना जिला चुनें / Please select your district', 'error');
        return;
    }
    
    // Show loading
    showLoading(true);
    hideResults();
    
    try {
        const response = await fetch(`${API_BASE}/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to get recommendations');
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        showAlert('त्रुटि: सिफारिशें प्राप्त करने में विफल / Error: Failed to get recommendations', 'error');
    } finally {
        showLoading(false);
    }
}

// Display results
function displayResults(data) {
    // Update results header
    document.getElementById('result-region').textContent = data.region.name;
    document.getElementById('result-season').textContent = data.season.current;
    document.getElementById('result-climate').textContent = data.region.climate_zone;
    document.getElementById('result-soil').textContent = 
        `${data.soil.texture}, pH ${data.soil.ph}`;
    document.getElementById('result-irrigation').textContent = data.irrigation;
    document.getElementById('result-forecast-temp').textContent = 
        `${data.medium_range_forecast.expected_avg_temp}°C`;
    document.getElementById('result-forecast-rain').textContent = 
        `${data.medium_range_forecast.expected_rainfall_mm}mm`;
    
    // Display season guidance
    if (data.season.guidance) {
        document.getElementById('season-guidance').textContent = data.season.guidance;
    }
    
    // Display crops
    const cropsGrid = document.getElementById('cropsGrid');
    cropsGrid.innerHTML = '';
    
    data.recommended_crops.forEach((crop, index) => {
        const cropCard = createCropCard(crop, index + 1);
        cropsGrid.appendChild(cropCard);
    });
    
    // Show results
    showResults();
    
    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

// Create crop card
function createCropCard(crop, rank) {
    const card = document.createElement('div');
    card.className = 'crop-card';
    
    // Determine score class
    let scoreClass = 'high';
    if (crop.suitability_score < 50) scoreClass = 'low';
    else if (crop.suitability_score < 70) scoreClass = 'medium';
    
    // Determine risk class
    let riskClass = 'risk-low';
    let riskText = 'Low Risk';
    if (crop.risk_note.includes('High') || crop.risk_note.includes('Multiple')) {
        riskClass = 'risk-high';
        riskText = 'High Risk';
    } else if (crop.risk_note.includes('Moderate') || crop.risk_note.includes('deficit')) {
        riskClass = 'risk-moderate';
        riskText = 'Moderate Risk';
    }
    
    card.innerHTML = `
        <div class="crop-header">
            <div class="crop-rank">${rank}</div>
            <div class="crop-name">
                <h3>${crop.crop}</h3>
                <span class="crop-id">${crop.crop_id}</span>
            </div>
        </div>
        
        <div class="score-section">
            <div class="score-label">
                <span>उपयुक्तता स्कोर / Suitability Score</span>
                <span><strong>${crop.suitability_score.toFixed(1)}/100</strong></span>
            </div>
            <div class="score-bar">
                <div class="score-fill ${scoreClass}" style="width: ${crop.suitability_score}%"></div>
            </div>
        </div>
        
        <div class="crop-details">
            <div class="detail-item">
                <span class="icon">⏱️</span>
                <span><strong>${crop.growth_duration_days}</strong> दिन / days</span>
            </div>
            <div class="detail-item">
                <span class="icon">💧</span>
                <span><strong>${crop.water_required_mm}</strong>mm पानी / water</span>
            </div>
            <div class="detail-item">
                <span class="icon">🌧️</span>
                <span><strong>${crop.expected_rainfall_mm.toFixed(0)}</strong>mm बारिश / rain</span>
            </div>
            <div class="detail-item">
                <span class="icon">💦</span>
                <span><strong>${crop.irrigation_needed_mm.toFixed(0)}</strong>mm सिंचाई / irrigation</span>
            </div>
        </div>
        
        <div class="risk-badge ${riskClass}">
            ${riskText}: ${crop.risk_note}
        </div>
        
        <button class="expand-btn" onclick="toggleExtra(this)">
            अधिक जानकारी / More Details ▼
        </button>
        
        <div class="crop-extra">
            <div class="detail-item">
                <span class="icon">🌵</span>
                <span>सूखा सहनशीलता / Drought Tolerance: <strong>${crop.drought_tolerance}</strong></span>
            </div>
            <div class="detail-item">
                <span class="icon">📍</span>
                <span>क्षेत्रीय उपयुक्तता / Regional Suitability: <strong>${(crop.regional_suitability * 100).toFixed(0)}%</strong></span>
            </div>
        </div>
    `;
    
    return card;
}

// Toggle extra details
function toggleExtra(button) {
    const extra = button.nextElementSibling;
    extra.classList.toggle('active');
    
    if (extra.classList.contains('active')) {
        button.innerHTML = 'कम दिखाएं / Show Less ▲';
    } else {
        button.innerHTML = 'अधिक जानकारी / More Details ▼';
    }
}

// Show/hide loading
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.add('active');
    } else {
        loading.classList.remove('active');
    }
}

// Show/hide results
function showResults() {
    document.getElementById('results').classList.add('active');
}

function hideResults() {
    document.getElementById('results').classList.remove('active');
}

// Show alert
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}
