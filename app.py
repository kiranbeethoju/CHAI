from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'demo.html')

@app.route('/get_patients')
def get_patients():
    with open('sample_data.json', 'r') as f:
        patients = json.load(f)
    return jsonify(patients)

@app.route("/api/update_grid", methods=["POST"])
def update_grid():
    data = request.json
    grid = data.get("grid", {})
    account = data.get("account", "unknown")
    justifications = data.get("justifications", {})

    em_level = derive_em_level(grid)
    return jsonify(
        account=account,
        e_m_level=em_level,
        grid=grid,
        justifications=justifications
    )

@app.route("/api/set_selections", methods=["POST"])
def set_selections():
    data = request.json
    account = data.get("account", "unknown")
    selections = data.get("selections", [])
    
    # Convert selections array to grid format
    grid = {}
    justifications = {}
    
    for selection in selections:
        checkbox_id = selection.get("id")
        is_checked = selection.get("checked", False)
        justification = selection.get("justification", "")
        
        if checkbox_id:
            grid[checkbox_id] = is_checked
            if justification:
                justifications[checkbox_id] = justification
    
    em_level = derive_em_level(grid)
    
    return jsonify(
        account=account,
        e_m_level=em_level,
        grid=grid,
        justifications=justifications
    )

def calculate_problem_level(grid):
    # High level problems
    if any([
        grid.get("problems-high-1", False),  # Chronic illness with severe exacerbation
        grid.get("problems-high-2", False)   # Acute/chronic illness that poses threat to life
    ]):
        return "High"
    
    # Moderate level problems
    if any([
        grid.get("problems-moderate-1", False),  # Chronic illness with exacerbation
        grid.get("problems-moderate-2", False),  # 2+ stable chronic illnesses
        grid.get("problems-moderate-3", False),  # Undiagnosed new problem
        grid.get("problems-moderate-4", False),  # Acute illness with systemic symptoms
        grid.get("problems-moderate-5", False)   # Acute complicated injury
    ]):
        return "Moderate"
    
    # Low level problems
    if any([
        grid.get("problems-low-1", False),  # 2+ self-limited problems
        grid.get("problems-low-2", False),  # 1 stable chronic illness
        grid.get("problems-low-3", False)   # 1 acute uncomplicated illness
    ]):
        return "Low"
    
    # Straightforward level problems
    if grid.get("problems-minimal-1", False):  # 1 self-limited problem
        return "Straightforward"
    
    # N/A level
    if grid.get("problems-na-1", False):
        return "N/A"
    
    return "Straightforward"  # Default level

def calculate_data_level(grid):
    # High level data
    category1_count = sum([
        grid.get("data-high-1", False)
    ])
    category2_independent = grid.get("data-high-2", False)
    category3_discussion = grid.get("data-high-3", False)
    
    if (category1_count >= 3) or (category2_independent and category3_discussion):
        return "High"
    
    # Moderate level data
    moderate_count = sum([
        grid.get("data-moderate-1", False),  # 3 from Category 1
        grid.get("data-moderate-2", False),  # Independent interpretation
        grid.get("data-moderate-3", False)   # Discussion of management
    ])
    if moderate_count >= 1:
        return "Moderate"
    
    # Low level data
    low_count = sum([
        grid.get("data-low-1", False),  # Review of external notes
        grid.get("data-low-2", False),  # Review of test results
        grid.get("data-low-3", False),  # Ordering of tests
        grid.get("data-low-4", False)   # Assessment with historian
    ])
    if low_count >= 1:
        return "Low"
    
    # Minimal level data
    if grid.get("data-minimal-1", False):
        return "Straightforward"
    
    # N/A level
    if grid.get("data-na-1", False):
        return "N/A"
    
    return "Straightforward"  # Default level

def calculate_risk_level(grid):
    # High level risk
    if any([
        grid.get("risk-high-1", False),  # Drug therapy with intensive monitoring
        grid.get("risk-high-2", False),  # Major surgery with risk factors
        grid.get("risk-high-3", False),  # Emergency major surgery
        grid.get("risk-high-4", False),  # Decision regarding hospitalization
        grid.get("risk-high-5", False)   # DNR/de-escalation decision
    ]):
        return "High"
    
    # Moderate level risk
    if any([
        grid.get("risk-moderate-1", False),  # Prescription drug management
        grid.get("risk-moderate-2", False),  # Minor surgery with risk factors
        grid.get("risk-moderate-3", False),  # Major surgery without risk factors
        grid.get("risk-moderate-4", False)   # Social determinants limiting treatment
    ]):
        return "Moderate"
    
    # Low level risk
    if grid.get("risk-low-1", False):  # Low risk of morbidity
        return "Low"
    
    # Minimal level risk
    if grid.get("risk-minimal-1", False):
        return "Straightforward"
    
    # N/A level
    if grid.get("risk-na-1", False):
        return "N/A"
    
    return "Straightforward"  # Default level

def derive_em_level(grid):
    # Calculate levels for each component
    problem_level = calculate_problem_level(grid)
    data_level = calculate_data_level(grid)
    risk_level = calculate_risk_level(grid)
    
    # Define the hierarchy of levels
    level_hierarchy = {
        "N/A": 0,
        "Straightforward": 1,
        "Low": 2,
        "Moderate": 3,
        "High": 4
    }
    
    # Convert levels to numerical values
    levels = [
        level_hierarchy[problem_level],
        level_hierarchy[data_level],
        level_hierarchy[risk_level]
    ]
    
    # Sort levels in descending order
    levels.sort(reverse=True)
    
    # Get the second highest level (2 out of 3 elements must meet or exceed)
    second_highest = levels[1]
    
    # Convert back to string
    level_names = {v: k for k, v in level_hierarchy.items()}
    return level_names[second_highest]

if __name__ == "__main__":
    app.run(debug=True) 