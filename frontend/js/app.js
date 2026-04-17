// API Configuration
 const API_BASE_URL = 'https://dairy-breeding-system-production.up.railway.app';
//const API_BASE_URL = 'http://127.0.0.1:5000';

// DOM Elements
const form = document.getElementById('recommendation-form');
const countySelect = document.getElementById('county');
const breedSelect = document.getElementById('current-breed');
const loadingDiv = document.getElementById('loading');
const resultsDiv = document.getElementById('results');
const locationBadge = document.getElementById('location-badge');
const recommendationsGrid = document.getElementById('recommendations-grid');
const improvementBox = document.getElementById('improvement-box');
const comparisonBox = document.getElementById('comparison-box');

// Store current THI for display
let currentThi = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadCounties();
    await loadBreeds();
    setupEventListeners();
});

// Load counties from API
async function loadCounties() {
    try {
        const response = await fetch(`${API_BASE_URL}/counties`);
        const counties = await response.json();
        
        countySelect.innerHTML = '<option value="">-- Choose county --</option>';
        counties.forEach(county => {
            const option = document.createElement('option');
            option.value = county.county_id;
            option.textContent = county.county_name;
            countySelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading counties:', error);
        showError('Failed to load counties. Is the backend running?');
    }
}

// Load breeds from API
async function loadBreeds() {
    try {
        const response = await fetch(`${API_BASE_URL}/breeds`);
        const breeds = await response.json();
        
        breedSelect.innerHTML = '<option value="">-- I don\'t have a cow yet --</option>';
        breeds.forEach(breed => {
            const option = document.createElement('option');
            option.value = breed.breed_id;
            option.textContent = `${breed.breed_name} (${breed.breed_type})`;
            breedSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading breeds:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    form.addEventListener('submit', handleSubmit);
}

// Handle form submission
async function handleSubmit(e) {
    e.preventDefault();
    
    const countyId = countySelect.value;
    const currentBreed = breedSelect.value || null;
    
    if (!countyId) {
        alert('Please select a county');
        return;
    }
    
    // Show loading, hide results
    loadingDiv.classList.remove('hidden');
    resultsDiv.classList.add('hidden');
    
    try {
        const response = await fetch(`${API_BASE_URL}/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                county_id: parseInt(countyId),
                current_breed: currentBreed
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            showError(data.error || 'An error occurred');
            loadingDiv.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to connect to the server. Is the backend running?');
        loadingDiv.classList.add('hidden');
    }
}

// Display results
function displayResults(data) {
    // Store THI for tooltip
    currentThi = data.county.avg_thi;
    
    // Hide loading
    loadingDiv.classList.add('hidden');
    
    // Show results
    resultsDiv.classList.remove('hidden');
    
    // Update location badge
    locationBadge.innerHTML = `
        <span>📍</span>
        ${data.county.name} County
    `;
    
    // Display recommendations
    recommendationsGrid.innerHTML = '';
    data.recommendations.forEach((rec, index) => {
        const card = createRecommendationCard(rec, index === 0);
        recommendationsGrid.appendChild(card);
    });
    
    // Display improvement potential
    if (data.improvement_potential !== null && data.improvement_potential > 0) {
        improvementBox.classList.remove('hidden');
        improvementBox.innerHTML = `
            <strong>📈 Improvement Potential:</strong> Switching to ${data.recommendations[0].breed_name} could improve suitability by ${data.improvement_potential.toFixed(1)}%!
        `;
    } else {
        improvementBox.classList.add('hidden');
    }
    
    // Display comparison
    if (data.comparison) {
        comparisonBox.classList.remove('hidden');
        comparisonBox.innerHTML = `
            <h4>🔄 Breed Comparison</h4>
            ${data.comparison.replace(/\n/g, '<br>')}
        `;
    } else {
        comparisonBox.classList.add('hidden');
    }
}

// Helper functions for explanations
function getSuitabilityExplanation(score) {
    if (score >= 90) return "✅ Excellent match - This breed will thrive here";
    if (score >= 75) return "👍 Good match - Strong potential for success";
    if (score >= 60) return "⚠️ Fair match - May need some management adjustments";
    return "⚠️ Challenging - Not ideal for this area without significant management";
}

function getMilkExplanation(breedType, score) {
    if (breedType === 'Pure Exotic') {
        if (score >= 80) return "High production potential in your area";
        if (score >= 60) return "Moderate production - could be better with cooler conditions";
        return "Production limited by local heat stress";
    } else if (breedType === 'Pure Indigenous') {
        if (score >= 80) return "Good production for an adapted breed";
        return "Moderate production but very reliable";
    } else {
        if (score >= 80) return "Excellent balance of production and adaptation";
        return "Good production with solid resilience";
    }
}

function getHeatExplanation(score) {
    if (score >= 8) return "🔥 Excellent heat tolerance - ideal for hot areas";
    if (score >= 6) return "🌤️ Good heat tolerance - suitable for most regions";
    if (score >= 4) return "☀️ Moderate - needs shade and water in hot weather";
    return "❄️ Prefers cool highlands - needs cooling in hot areas";
}

function getHealthExplanation(score) {
    if (score >= 80) return "🛡️ Excellent disease resistance";
    if (score >= 60) return "👍 Good natural immunity";
    if (score >= 40) return "⚠️ Moderate - requires regular veterinary care";
    return "⚠️ High risk - needs intensive disease management";
}

// Create recommendation card with tooltips
function createRecommendationCard(rec, isPrimary) {
    const card = document.createElement('div');
    card.className = `recommendation-card ${isPrimary ? 'primary' : ''}`;
    
    // Get heat tolerance score (1-10)
    const heatScore = rec.heat_tolerance_score || 5;
    const heatStars = '★'.repeat(heatScore) + '☆'.repeat(10 - heatScore);
    
    // Get milk yield percentage
    const milkPct = rec.milk_score || 0;
    
    // Get health score
    const healthScore = rec.health_score || 0;
    
    // Get suitability score
    const suitability = rec.suitability_score || 0;
    
    card.innerHTML = `
        <div class="rank-badge">#${rec.rank} ${isPrimary ? 'Best Match' : 'Alternative'}</div>
        <div class="breed-name">${rec.breed_name}</div>
        <div class="breed-type">${rec.breed_type}</div>
        
        <!-- Suitability Meter with Tooltip -->
        <div class="suitability-meter">
            <div class="meter-header">
                <div class="metric-label">
                    <span>Suitability</span>
                    <span class="help-icon" data-tooltip="How well this breed matches your county's environmental conditions. Calculated using Temperature-Humidity Index (THI), altitude, rainfall, and disease prevalence. Higher percentage = better match.">?</span>
                </div>
                <span class="meter-value">${suitability.toFixed(1)}%</span>
            </div>
            <div class="meter-bar">
                <div class="meter-fill" style="width: ${suitability}%"></div>
            </div>
            <div style="font-size: 11px; color: #6c757d; margin-top: 5px;">
                ${getSuitabilityExplanation(suitability)}
            </div>
        </div>
        
        <div class="traits-grid">
            <!-- Milk Yield with Tooltip -->
            <div class="trait-item">
                <div class="metric-label">
                    <span class="trait-label">Milk Yield</span>
                    <span class="help-icon" data-tooltip="Expected milk production in your area. The percentage shows how close this breed's yield is to its maximum genetic potential (100% = 25-30 L/day for exotic breeds, 12-15 L/day for indigenous).">?</span>
                </div>
                <span class="trait-value">${milkPct.toFixed(0)}%</span>
                <div style="font-size: 10px; color: #6c757d; margin-top: 3px;">
                    ${getMilkExplanation(rec.breed_type, milkPct)}
                </div>
            </div>
            
            <!-- Heat Tolerance with Tooltip -->
            <div class="trait-item">
                <div class="metric-label">
                    <span class="trait-label">Heat Tolerance</span>
                    <span class="help-icon" data-tooltip="Ability to handle high temperatures and humidity. Measured by Temperature-Humidity Index (THI). 10 stars = excellent heat tolerance (can thrive above THI 80), 1 star = poor heat tolerance (stressed above THI 68).">?</span>
                </div>
                <span class="trait-stars">${heatStars}</span>
                <div style="font-size: 10px; color: #6c757d; margin-top: 3px;">
                    ${getHeatExplanation(heatScore)}
                </div>
            </div>
            
            <!-- Health with Tooltip -->
            <div class="trait-item">
                <div class="metric-label">
                    <span class="trait-label">Health</span>
                    <span class="help-icon" data-tooltip="Disease resistance rating. Higher percentage means better resistance to endemic diseases like East Coast Fever, Anaplasmosis, and Mastitis.">?</span>
                </div>
                <span class="trait-value">${healthScore.toFixed(0)}%</span>
                <div style="font-size: 10px; color: #6c757d; margin-top: 3px;">
                    ${getHealthExplanation(healthScore)}
                </div>
            </div>
        </div>
        
        <!-- THI Explanation Box -->
        <details class="thi-info">
            <summary>🌡️ What is Temperature-Humidity Index (THI)?</summary>
            <p>THI measures heat stress in cattle. It combines temperature and humidity:</p>
            <ul style="margin: 8px 0 0 20px; padding-left: 0;">
                <li><strong>THI &lt; 68</strong>: Comfortable - No stress</li>
                <li><strong>THI 68-72</strong>: Mild stress - Milk begins to drop</li>
                <li><strong>THI 72-78</strong>: Moderate stress - Significant production loss</li>
                <li><strong>THI > 78</strong>: Severe stress - High risk of health issues</li>
            </ul>
            <p style="margin-top: 8px;">Your county's THI: <strong>${currentThi || 'N/A'}</strong></p>
        </details>
        
        <div class="explanation-box">
            ${rec.explanation}
        </div>
    `;
    
    // Add tooltip behavior
    const helpIcons = card.querySelectorAll('.help-icon');
    helpIcons.forEach(icon => {
        icon.addEventListener('mouseenter', function(e) {
            const tooltip = this.getAttribute('data-tooltip');
            // Create or update title attribute for native tooltip
            this.setAttribute('title', tooltip);
        });
    });
    
    return card;
}

// Reset form
function resetForm() {
    form.reset();
    resultsDiv.classList.add('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Print results
function printResults() {
    window.print();
}

// Show error
function showError(message) {
    alert(message);
}

// Make functions globally available for HTML buttons
window.resetForm = resetForm;
window.printResults = printResults;