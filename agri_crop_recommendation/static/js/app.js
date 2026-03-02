/**
 * Indian Farmer Crop Recommendation System — Frontend Application
 * 
 * Handles:
 * - Region loading from API
 * - Recommendation form submission
 * - Results rendering (crops, forecast chart, risk, pests, calendar)
 */

// ===== Global State =====
let weatherChart = null;

// ===== Crop Emoji Map =====
const CROP_EMOJIS = {
    'BAJRA_01': '🌾', 'JOWAR_01': '🌾', 'RAGI_01': '🌾',
    'FOXTAIL_01': '🌾', 'MOONG_01': '🫘', 'URAD_01': '🫘',
    'COWPEA_01': '🫘', 'GUAR_01': '🌿', 'SESAME_01': '🌻',
    'SUNFLOWER_01': '🌻', 'SOYBEAN_01': '🫘', 'TOMATO_01': '🍅',
    'BRINJAL_01': '🍆', 'OKRA_01': '🌿', 'BOTTLEGOURD_01': '🥒'
};

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    loadRegions();
    document.getElementById('recommendationForm').addEventListener('submit', handleSubmit);
});

// ===== Load Regions =====
let _allRegions = [];   // module-level cache

async function loadRegions() {
    try {
        const response = await fetch('/regions');
        const data = await response.json();
        _allRegions = data.regions;

        // --- Populate State dropdown ---
        const stateSelect = document.getElementById('state');
        const states = [...new Set(_allRegions.map(r => r.state || 'Other'))].sort();
        stateSelect.innerHTML = '<option value="">Select your state...</option>';
        states.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s;
            opt.textContent = s;
            stateSelect.appendChild(opt);
        });

        // --- Wire state change → populate districts ---
        stateSelect.addEventListener('change', () => {
            const distSelect = document.getElementById('region');
            const chosen = stateSelect.value;
            if (!chosen) {
                distSelect.innerHTML = '<option value="">Select a state first...</option>';
                distSelect.disabled = true;
                return;
            }
            const filtered = _allRegions
                .filter(r => (r.state || 'Other') === chosen)
                .sort((a, b) => a.name.localeCompare(b.name));
            distSelect.innerHTML = '<option value="">Select your district...</option>';
            filtered.forEach(region => {
                const opt = document.createElement('option');
                opt.value = region.region_id;
                opt.textContent = `${region.name} (${region.climate_zone})`;
                distSelect.appendChild(opt);
            });
            distSelect.disabled = false;
        });

    } catch (error) {
        console.error('Failed to load regions:', error);
        document.getElementById('state').innerHTML =
            '<option value="">Failed to load states</option>';
    }
}


// ===== Handle Form Submit =====
async function handleSubmit(e) {
    e.preventDefault();

    const regionId = document.getElementById('region').value;
    if (!regionId) {
        alert('Please select a district');
        return;
    }

    // Build request body
    const body = {
        region_id: regionId,
        irrigation: document.getElementById('irrigation').value,
        planning_days: parseInt(document.getElementById('planning_days').value)
    };

    // Add soil info if provided
    const soilTexture = document.getElementById('soil_texture').value;
    const soilPh = document.getElementById('soil_ph').value;
    if (soilTexture && soilPh) {
        body.soil = {
            texture: soilTexture,
            ph: parseFloat(soilPh),
            organic_matter: document.getElementById('soil_organic').value,
            drainage: document.getElementById('soil_drainage').value
        };
    }

    // Show loading, hide results
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('submitBtn').disabled = true;

    try {
        const response = await fetch('/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Server error');
        }

        const data = await response.json();
        renderResults(data);

    } catch (error) {
        console.error('Recommendation failed:', error);
        alert('Error: ' + error.message);
    } finally {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('submitBtn').disabled = false;
    }
}

// ===== Render All Results =====
function renderResults(data) {
    const results = document.getElementById('results');

    // Overview stats
    renderOverview(data);

    // Season guidance
    renderGuidance(data.season);

    // Weather forecast chart
    renderForecastChart(data.medium_range_forecast);

    // Crop recommendations
    renderCrops(data.recommended_crops);

    // Risk assessment (from top crop)
    renderRiskAssessment(data.recommended_crops);

    // Pest warnings
    renderPestWarnings(data.recommended_crops);

    // Planting calendar
    renderCalendar(data.planting_calendars);

    // Show results
    results.classList.remove('hidden');

    // Scroll to results
    setTimeout(() => {
        document.getElementById('overview').scrollIntoView({ behavior: 'smooth' });
    }, 200);
}

// ===== Overview Stats =====
function renderOverview(data) {
    const nameEl = document.getElementById('result-region');
    if (nameEl) nameEl.textContent = (data.region && data.region.name) || '-';
    const seasonEl = document.getElementById('result-season');
    if (seasonEl) seasonEl.textContent = (data.season && data.season.current) || '-';

    const forecast = data.medium_range_forecast || {};
    const tempEl = document.getElementById('result-temp');
    if (tempEl) tempEl.textContent =
        (forecast.expected_avg_temp || (forecast.ml_summary && forecast.ml_summary.avg_temp) || '-') + '°C';
    const rainEl = document.getElementById('result-rain');
    if (rainEl) rainEl.textContent =
        (forecast.expected_rainfall_mm || (forecast.ml_summary && forecast.ml_summary.total_rainfall) || '-') + ' mm';
    const soilEl = document.getElementById('result-soil');
    if (soilEl) soilEl.textContent =
        data.soil ? data.soil.texture + ' (pH ' + data.soil.ph + ')' : '-';

    const source = forecast.forecast_source || 'climatology';
    const srcEl = document.getElementById('result-forecast-src');
    if (srcEl) srcEl.textContent = source;

    // Update forecast badge
    const badge = document.getElementById('forecast-badge');
    if (badge) {
        if (source.includes('ensemble') || source.includes('LSTM')) {
            badge.textContent = '🤖 ML Ensemble';
            badge.className = 'badge badge-success';
        } else if (source.includes('XGBoost')) {
            badge.textContent = '🤖 ' + source;
            badge.className = 'badge badge-info';
        } else {
            badge.textContent = '📊 Climatology';
            badge.className = 'badge badge-warning';
        }
    }
}

// ===== Season Guidance =====
function renderGuidance(season) {
    const guidance = document.getElementById('season-guidance');
    let text = season.guidance || `Current season: ${season.current}`;
    if (season.is_transition) {
        text += ` Transitioning to ${season.next_season} soon.`;
    }
    guidance.textContent = text;
}

// ===== Weather Forecast Chart =====
function renderForecastChart(forecast) {
    const canvas = document.getElementById('weatherChart');
    if (!canvas) return;

    if (weatherChart) {
        weatherChart.destroy();
        weatherChart = null;
    }

    const monthly = (forecast && forecast.monthly_forecast) || [];
    const dailyPreds = (forecast && forecast.daily_predictions) || [];

    // ── Prefer monthly (Jan–Dec) data from historical zone ──────────────────
    if (monthly.length === 12) {
        _renderMonthlyChart(canvas, monthly, forecast);
        return;
    }

    // ── Fallback: ML daily predictions ─────────────────────────────────────
    if (dailyPreds.length > 0) {
        _renderDailyChart(canvas, dailyPreds);
        return;
    }

    // ── Nothing available — show summary card ───────────────────────────────
    const parent = canvas.parentElement;
    if (parent) {
        const avgTemp = forecast.expected_avg_temp || '-';
        const rain = forecast.expected_rainfall_mm || '-';
        const hum = forecast.expected_humidity || '-';
        parent.innerHTML = `
        <div class="forecast-summary-card">
            <div class="forecast-summary-row">
                <div class="forecast-summary-item">
                    <span class="fsi-icon">🌡️</span>
                    <span class="fsi-val">${avgTemp}°C</span>
                    <span class="fsi-label">Avg Temp</span>
                </div>
                <div class="forecast-summary-item">
                    <span class="fsi-icon">🌧️</span>
                    <span class="fsi-val">${rain} mm</span>
                    <span class="fsi-label">Expected Rain</span>
                </div>
                <div class="forecast-summary-item">
                    <span class="fsi-icon">💧</span>
                    <span class="fsi-val">${hum}%</span>
                    <span class="fsi-label">Avg Humidity</span>
                </div>
            </div>
            <p class="forecast-summary-note">📊 Seasonal summary — train ML models for daily detail</p>
        </div>`;
    }
}

function _renderMonthlyChart(canvas, monthly, forecast) {
    const currentMonth = new Date().getMonth(); // 0-indexed

    // ── 3-month window: current month + next 2 ───────────────────────────────
    const indices = [0, 1, 2].map(offset => (currentMonth + offset) % 12);
    const window3 = indices.map(i => monthly[i]);

    const labels = window3.map(m => m.month);
    const temps = window3.map(m => m.temperature);
    const rainfall = window3.map(m => m.rainfall);
    const humidity = window3.map(m => m.humidity);

    // Current month (idx 0) gets brighter colour
    const barBg = ['rgba(0,200,100,0.88)', 'rgba(0,230,118,0.52)', 'rgba(0,230,118,0.32)'];
    const barBorder = ['#00c864', 'rgba(0,180,80,0.65)', 'rgba(0,180,80,0.40)'];
    const ptBg = ['#ff8c42', 'rgba(229,57,53,0.75)', 'rgba(229,57,53,0.55)'];
    const ptR = [8, 5, 5];

    weatherChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                {
                    label: 'Rainfall (mm)',
                    data: rainfall,
                    type: 'bar',
                    backgroundColor: barBg,
                    borderColor: barBorder,
                    borderWidth: 1.5,
                    borderRadius: 6,
                    yAxisID: 'yRain',
                    order: 2,
                },
                {
                    label: 'Avg Temperature (°C)',
                    data: temps,
                    type: 'line',
                    borderColor: '#e53935',
                    backgroundColor: 'rgba(229,57,53,0.08)',
                    borderWidth: 2.5,
                    tension: 0.3,
                    fill: false,
                    pointBackgroundColor: ptBg,
                    pointRadius: ptR,
                    pointHoverRadius: 9,
                    yAxisID: 'yTemp',
                    order: 1,
                },
                {
                    label: 'Humidity (%)',
                    data: humidity,
                    type: 'line',
                    borderColor: '#1565c0',
                    backgroundColor: 'transparent',
                    borderWidth: 1.8,
                    borderDash: [5, 4],
                    tension: 0.3,
                    fill: false,
                    pointRadius: 4,
                    pointHoverRadius: 7,
                    yAxisID: 'yHum',
                    order: 1,
                },
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: {
                legend: {
                    labels: {
                        color: '#2c3e50',
                        font: { family: 'Inter', size: 12 },
                        usePointStyle: true,
                        pointStyleWidth: 10,
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(255,255,255,0.97)',
                    titleColor: '#2d5016',
                    bodyColor: '#2c3e50',
                    borderColor: 'rgba(74,124,44,0.35)',
                    borderWidth: 1,
                    padding: 10,
                    callbacks: {
                        title: (items) => {
                            const idx = items[0].dataIndex;
                            return labels[idx] + (idx === 0 ? '  ← This Month' : '');
                        },
                        label: (item) => {
                            const units = { 'Rainfall (mm)': 'mm', 'Avg Temperature (°C)': '°C', 'Humidity (%)': '%' };
                            const u = units[item.dataset.label] || '';
                            return ` ${item.dataset.label}: ${item.parsed.y}${u}`;
                        }
                    }
                },
            },
            scales: {
                x: {
                    ticks: {
                        color: (ctx) => ctx.index === 0 ? '#e65100' : '#555',
                        font: (ctx) => ctx.index === 0
                            ? { family: 'Inter', weight: '700', size: 13 }
                            : { family: 'Inter', size: 12 },
                    },
                    grid: { color: 'rgba(0,0,0,0.05)' }
                },
                yRain: {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: 'Rainfall (mm)', color: '#2e7d32', font: { size: 11 } },
                    ticks: { color: '#2e7d32' },
                    grid: { display: false },
                    beginAtZero: true,
                },
                yTemp: {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Temperature (°C)', color: '#c62828', font: { size: 11 } },
                    ticks: { color: '#c62828' },
                    grid: { color: 'rgba(0,0,0,0.06)' },
                },
                yHum: {
                    type: 'linear',
                    position: 'left',
                    display: false,
                    min: 0,
                    max: 110,
                    grid: { display: false },
                },
            }
        }
    });
}

function _renderDailyChart(canvas, dailyPreds) {
    const labels = dailyPreds.map(p => `Day ${p.day}`);
    const tempMax = dailyPreds.map(p => p.temp_max);
    const tempMin = dailyPreds.map(p => p.temp_min);
    const rainfall = dailyPreds.map(p => p.rainfall);

    weatherChart = new Chart(canvas, {
        type: 'line',
        data: {
            labels,
            datasets: [
                { label: 'Max Temp (°C)', data: tempMax, borderColor: '#ff5252', backgroundColor: 'rgba(255,82,82,0.1)', borderWidth: 2, tension: 0.4, fill: false, yAxisID: 'y' },
                { label: 'Min Temp (°C)', data: tempMin, borderColor: '#40c4ff', backgroundColor: 'rgba(64,196,255,0.1)', borderWidth: 2, tension: 0.4, fill: false, yAxisID: 'y' },
                { label: 'Rainfall (mm)', data: rainfall, borderColor: '#00e676', backgroundColor: 'rgba(0,230,118,0.2)', borderWidth: 2, tension: 0.4, fill: true, type: 'bar', yAxisID: 'y1' }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: { legend: { labels: { color: '#2c3e50', font: { family: 'Inter', size: 12 } } } },
            scales: {
                x: { ticks: { color: '#555' }, grid: { color: 'rgba(0,0,0,0.06)' } },
                y: { type: 'linear', position: 'left', title: { display: true, text: 'Temperature (°C)', color: '#555' }, ticks: { color: '#555' }, grid: { color: 'rgba(0,0,0,0.06)' } },
                y1: { type: 'linear', position: 'right', title: { display: true, text: 'Rainfall (mm)', color: '#555' }, ticks: { color: '#555' }, grid: { display: false } }
            }
        }
    });
}

// ===== Crop Cards =====
function renderCrops(crops) {
    const grid = document.getElementById('cropsGrid');
    const count = document.getElementById('crops-count');

    count.textContent = `${crops.length} crops analyzed and ranked`;

    grid.innerHTML = crops.map((crop, index) => {
        const emoji = CROP_EMOJIS[crop.crop_id] || '🌱';
        const score = crop.suitability_score;
        const scoreClass = score >= 70 ? '' : score >= 45 ? 'medium' : 'low';
        const scoreColor = score >= 70 ? '#00e676' : score >= 45 ? '#ffab40' : '#ff5252';

        // Duration display — use range if available, else single value
        const durRange = crop.duration_range && crop.duration_range.length === 2
            ? `${crop.duration_range[0]}–${crop.duration_range[1]} days growth cycle`
            : `${crop.growth_duration_days} days growth cycle`;

        // Risk badge
        let riskClass = 'risk-low';
        let riskLabel = 'Low Risk';
        if (crop.risk_assessment) {
            const level = crop.risk_assessment.overall_risk_level;
            riskClass = `risk-${level.toLowerCase()}`;
            riskLabel = `${level} Risk`;
        } else if (crop.risk_note) {
            if (crop.risk_note.includes('High')) riskClass = 'risk-high';
            else if (crop.risk_note.includes('Moderate')) riskClass = 'risk-medium';
            riskLabel = crop.risk_note;
        }

        // Pest mini badges
        let pestBadges = '';
        if (crop.pest_warnings && crop.pest_warnings.length > 0) {
            pestBadges = `<div class="pest-mini-badges">
                ${crop.pest_warnings.map(p =>
                `<span class="pest-mini-badge">🐛 ${p.name}</span>`
            ).join('')}
            </div>`;
        }

        // Growing tip
        const tipHtml = crop.growing_tip
            ? `<div class="growing-tip">💡 <strong>Tip:</strong> ${crop.growing_tip}</div>`
            : '';

        return `
            <div class="crop-card" style="animation-delay: ${index * 0.08}s">
                <div class="crop-card-rank">#${index + 1}</div>
                <div class="crop-card-header">
                    <div class="crop-card-image">${emoji}</div>
                    <div>
                        <div class="crop-card-title">${crop.crop}</div>
                        <div class="crop-card-duration">${durRange}</div>
                    </div>
                </div>
                
                <div class="score-bar-container">
                    <div class="score-bar-label">
                        <span>Suitability</span>
                        <span style="color: ${scoreColor}">${score.toFixed(1)}%</span>
                    </div>
                    <div class="score-bar">
                        <div class="score-bar-fill ${scoreClass}" style="width: ${score}%"></div>
                    </div>
                </div>
                
                <div class="crop-details">
                    <div class="crop-detail-item">
                        <span class="label">Water Need</span>
                        <span class="value">${crop.water_required_mm} mm</span>
                    </div>
                    <div class="crop-detail-item">
                        <span class="label">Irrigation</span>
                        <span class="value">${crop.irrigation_needed_mm} mm</span>
                    </div>
                    <div class="crop-detail-item">
                        <span class="label">Drought Tol.</span>
                        <span class="value">${crop.drought_tolerance}</span>
                    </div>
                    <div class="crop-detail-item">
                        <span class="label">Reg. Score</span>
                        <span class="value">${(crop.regional_suitability * 100).toFixed(0)}%</span>
                    </div>
                </div>
                
                <span class="crop-risk-badge ${riskClass}">${riskLabel}</span>
                ${pestBadges}
                ${tipHtml}
            </div>
        `;
    }).join('');
}


// ===== Risk Assessment =====
function renderRiskAssessment(crops) {
    const container = document.getElementById('riskContent');

    // Get risk from top crop
    const topCrop = crops.find(c => c.risk_assessment);
    if (!topCrop || !topCrop.risk_assessment) {
        container.innerHTML = `
            < div class="empty-state" >
                <div class="empty-state-icon">✅</div>
                <p>No detailed risk assessment available</p>
            </div > `;
        return;
    }

    const risk = topCrop.risk_assessment;

    const riskItems = [
        {
            title: '💧 Drought Risk',
            data: risk.drought_risk,
            detail: `Water deficit: ${risk.drought_risk.water_deficit_mm || 0} mm(${risk.drought_risk.water_deficit_pct || 0} %)`
        },
        {
            title: '🌡️ Temperature Stress',
            data: risk.temperature_stress,
            detail: `Heat stress: ${risk.temperature_stress.heat_stress_days || 0} days, Cold: ${risk.temperature_stress.cold_stress_days || 0} days`
        },
        {
            title: '⛈️ Extreme Weather',
            data: risk.extreme_weather,
            detail: `Heavy rain: ${risk.extreme_weather.heavy_rain_days || 0} days, Heatwave: ${risk.extreme_weather.heatwave_days || 0} days`
        }
    ];

    container.innerHTML = `
            < p style = "margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted)" >
                Risk analysis for top crop: <strong style="color: var(--accent)">${topCrop.crop}</strong>
        </p >
        <div class="risk-grid">
            ${riskItems.map(item => {
        const level = (item.data.level || 'Low').toLowerCase();
        return `
                    <div class="risk-item risk-item-${level}">
                        <div class="risk-item-header">
                            <span class="risk-item-title">${item.title}</span>
                            <span class="risk-item-score crop-risk-badge risk-${level}">
                                ${item.data.score || 0}
                            </span>
                        </div>
                        <p class="risk-item-detail">${item.detail}</p>
                        ${item.data.warning ? `<p class="risk-item-detail" style="color: var(--accent-warm); margin-top: 4px">${item.data.warning}</p>` : ''}
                    </div>
                `;
    }).join('')}
        </div>
        <div class="risk-recommendation">
            <strong>📋 Recommendation:</strong> ${risk.recommendation || 'Monitor conditions regularly.'}
        </div>
        `;
}

// ===== Pest Warnings =====
function renderPestWarnings(crops) {
    const container = document.getElementById('pestContent');

    // Collect unique warnings from all crops
    const allWarnings = [];
    const seen = new Set();

    crops.forEach(crop => {
        if (crop.pest_warnings) {
            crop.pest_warnings.forEach(warning => {
                if (!seen.has(warning.id)) {
                    seen.add(warning.id);
                    allWarnings.push({ ...warning, crop_name: crop.crop });
                }
            });
        }
    });

    if (allWarnings.length === 0) {
        container.innerHTML = `
            < div class="empty-state" >
                <div class="empty-state-icon">✅</div>
                <p>No pest or disease warnings for current conditions</p>
            </div > `;
        return;
    }

    container.innerHTML = `
            < div class="pest-list" >
                ${allWarnings.slice(0, 6).map(w => {
        const isHigh = w.severity === 'High' || w.severity === 'Critical';
        return `
                    <div class="pest-item ${isHigh ? 'severity-high' : ''}">
                        <div class="pest-item-header">
                            <span class="pest-item-name">${w.type === 'pest' ? '🐛' : '🦠'} ${w.name}</span>
                            <span class="crop-risk-badge risk-${w.severity.toLowerCase()}">${w.severity}</span>
                        </div>
                        <p class="pest-item-type">${w.type} • Affects: ${w.crop_name}</p>
                        <p class="pest-item-desc">${w.description}</p>
                        <div class="pest-item-prevention">
                            <strong>Prevention:</strong> ${w.prevention}
                        </div>
                    </div>
                `;
    }).join('')
        }
        </div >
            `;
}

// ===== Planting Calendar =====
function renderCalendar(calendars) {
    const container = document.getElementById('calendarContent');

    if (!calendars || calendars.length === 0) {
        container.innerHTML = `
            < div class="empty-state" >
                <div class="empty-state-icon">📅</div>
                <p>No planting calendar data available</p>
            </div > `;
        return;
    }

    const phaseColors = ['#a5d6a7', '#66bb6a', '#43a047', '#2e7d32'];

    container.innerHTML = `
            < div class="calendar-list" >
                ${calendars.slice(0, 5).map(cal => {
        const phases = cal.phases || [];

        return `
                    <div class="calendar-item">
                        <div class="calendar-item-header">
                            <span class="calendar-item-crop">${CROP_EMOJIS[cal.crop_id] || '🌱'} ${cal.crop_name}</span>
                            <span class="calendar-item-dates">${cal.sowing_date} → ${cal.harvest_date} (${cal.total_duration_days} days)</span>
                        </div>
                        <div class="calendar-phases">
                            ${phases.map((phase, i) => `
                                <div class="calendar-phase" 
                                     style="flex: ${phase.progress_pct}; background: ${phaseColors[i] || phaseColors[0]}"
                                     title="${phase.name}: ${phase.duration_days} days">
                                    ${phase.progress_pct > 15 ? phase.name : ''}
                                </div>
                            `).join('')}
                        </div>
                        <div class="calendar-legend">
                            ${phases.map((phase, i) => `
                                <span class="calendar-legend-item">
                                    <span class="calendar-legend-dot" style="background: ${phaseColors[i]}"></span>
                                    ${phase.name} (${phase.duration_days}d)
                                </span>
                            `).join('')}
                        </div>
                    </div>
                `;
    }).join('')
        }
        </div >
            `;
}
