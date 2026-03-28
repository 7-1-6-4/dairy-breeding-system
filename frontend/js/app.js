// API Configuration
const API_BASE_URL = 'http://127.0.0.1:5000';

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

// Create recommendation card
function createRecommendationCard(rec, isPrimary) {
    const card = document.createElement('div');
    card.className = `recommendation-card ${isPrimary ? 'primary' : ''}`;
    
    // Create stars for traits
    const heatStars = '★'.repeat(Math.round(rec.heat_tolerance_score)) + '☆'.repeat(10 - Math.round(rec.heat_tolerance_score));
    const diseaseStars = '★'.repeat(Math.round(rec.disease_resistance_score)) + '☆'.repeat(10 - Math.round(rec.disease_resistance_score));
    const feedStars = '★'.repeat(Math.round(rec.feed_efficiency_score)) + '☆'.repeat(10 - Math.round(rec.feed_efficiency_score));
    
    card.innerHTML = `
        <div class="rank-badge">#${rec.rank} ${isPrimary ? 'Best Match' : 'Alternative'}</div>
        <div class="breed-name">${rec.breed_name}</div>
        <div class="breed-type">${rec.breed_type}</div>
        
        <div class="suitability-meter">
            <div class="meter-header">
                <span>Suitability</span>
                <span class="meter-value">${rec.suitability_score.toFixed(1)}%</span>
            </div>
            <div class="meter-bar">
                <div class="meter-fill" style="width: ${rec.suitability_score}%"></div>
            </div>
        </div>
        
        <div class="traits-grid">
            <div class="trait-item">
                <span class="trait-label">Milk Yield</span>
                <span class="trait-value">${rec.milk_score.toFixed(0)}%</span>
            </div>
            <div class="trait-item">
                <span class="trait-label">Heat Tolerance</span>
                <span class="trait-stars">${heatStars}</span>
            </div>
            <div class="trait-item">
                <span class="trait-label">Health</span>
                <span class="trait-value">${rec.health_score.toFixed(0)}%</span>
            </div>
        </div>
        
        <div class="explanation-box">
            ${rec.explanation}
        </div>
    `;
    
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
    // You can enhance this with a toast notification
    alert(message);
}

// Make functions globally available for HTML buttons
window.resetForm = resetForm;
window.printResults = printResults;