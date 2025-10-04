# app.py (Make sure this file is running your model)

from flask import Flask, render_template, request, jsonify
import math
from typing import Dict, Any

app = Flask(__name__)

# --- Constants & MOCK DATA (As previously established) ---
DENSITIES = {
    "C-type (Carbonaceous)": 1300,
    "S-type (Stony)": 2700,
    "M-type (Metallic)": 5000,
    "Rocky": 3000
}
DEFAULT_DENSITY = DENSITIES["Rocky"]
JOULES_PER_MEGATON = 4.184e15

MOCK_ASTEROID_DATA = {
    'name': '99942 Apophis',
    'neo_reference_id': '2000042',
    'is_potentially_hazardous_asteroid': True,
    'estimated_diameter': {'meters': {'estimated_diameter_min': '320.0', 'estimated_diameter_max': '400.0'}},
    'close_approach_data': [{'relative_velocity': {'kilometers_per_second': '7.42',}, 'miss_distance': {'kilometers': '31000.0'}}]
}

MOCK_TOP_5_NEAREST = [
    ("2023 NT1", 60000.0),
    ("99942 Apophis", 31000.0),
    ("2024 MK", 90000.0),
    ("(2002 AZ1)", 125000.0),
    ("433 Eros", 150000.0)
]

# --- Calculation Functions (find_mock_asteroid_data and calculate_impact_energy) ---
# Ensure these functions exist in your app.py file exactly as written previously.

def find_mock_asteroid_data(asteroid_name: str) -> Dict[str, Any] | None:
    # ... (Your existing function to find the mock data) ...
    normalized_name = asteroid_name.strip().upper().replace('(', '').replace(')', '').replace('-', ' ')
    mock_name_normalized = MOCK_ASTEROID_DATA['name'].upper()
    mock_id = MOCK_ASTEROID_DATA['neo_reference_id']
    
    if normalized_name == mock_name_normalized or normalized_name == mock_id:
        return MOCK_ASTEROID_DATA
    return None

def calculate_impact_energy(asteroid_data: Dict[str, Any], density: float) -> Dict[str, Any]:
    # ... (Your existing function to calculate energy) ...
    # This function should return the detailed dictionary including 'interpretation'.
    try:
        estimated_diameter = asteroid_data['estimated_diameter']['meters']
        min_d = float(estimated_diameter['estimated_diameter_min'])
        max_d = float(estimated_diameter['estimated_diameter_max'])
        avg_diameter = (min_d + max_d) / 2
        avg_radius = avg_diameter / 2

        close_approach = asteroid_data['close_approach_data'][-1]
        relative_velocity_km_s = float(close_approach['relative_velocity']['kilometers_per_second'])
        V_m_s = relative_velocity_km_s * 1000

        mass_kg = density * (4/3) * math.pi * (avg_radius ** 3)
        kinetic_energy_joules = 0.5 * mass_kg * (V_m_s ** 2)
        energy_megatons = kinetic_energy_joules / JOULES_PER_MEGATON

        if energy_megatons > 100:
            interpretation = "Devastating impact event, comparable to large scale nuclear war scenarios. Mitigation is critical."
        elif energy_megatons > 10:
            interpretation = "Major regional impact event, capable of causing widespread destruction and global climate effects."
        elif energy_megatons > 1:
            interpretation = "Powerful impact, capable of leveling a major metropolitan area (like the Tunguska event)."
        else:
            interpretation = "Smaller impact, likely resulting in localized damage or an atmospheric explosion (airburst)."

        return {
            "name": asteroid_data.get('name', 'N/A'),
            "average_diameter_m": f"{avg_diameter:.2f} meters",
            "relative_velocity_km_s": f"{relative_velocity_km_s:.3f} km/s",
            "assumed_density_kg_m3": f"{density:,} kg/m³",
            "calculated_mass_kg": f"{mass_kg:.2e} kg",
            "kinetic_energy_joules": f"{kinetic_energy_joules:.2e}",
            "impact_energy_megatons_tnt": f"{energy_megatons:.2e} MT",
            "is_potentially_hazardous": asteroid_data.get('is_potentially_hazardous_asteroid', False),
            "interpretation": interpretation
        }

    except Exception as e:
        return {"error": f"An unexpected error occurred during calculation: {e}"}


# --- Flask Routes ---
@app.route('/')
def index():
    """Renders the main HTML page and passes data to the Jinja2 template."""
    return render_template('index.html', 
                           densities=DENSITIES, 
                           top_asteroids=MOCK_TOP_5_NEAREST)

@app.route('/calculate_impact', methods=['POST'])
def calculate_impact_route():
    """Receives POST data from the website, runs the model, and returns JSON."""
    asteroid_name = request.form.get('asteroid_name')
    density_value = request.form.get('density_value')

    try:
        selected_density = float(density_value)
    except (TypeError, ValueError):
        selected_density = DEFAULT_DENSITY

    asteroid_data = find_mock_asteroid_data(asteroid_name)

    if not asteroid_data:
        return jsonify({"error": f"Asteroid '{asteroid_name}' not found. Try '99942 Apophis'."})

    results = calculate_impact_energy(asteroid_data, selected_density)
    
    # jsonify converts the Python dictionary output into the JSON format needed by the JavaScript frontend
    return jsonify(results)

if __name__ == '__main__':
    # Ensure you have Flask installed: pip install Flask
    app.run(debug=True)
