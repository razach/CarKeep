"""
Frontend routes for CarKeep web application.
Handles template rendering and user interface.
"""

from flask import (
    Blueprint, render_template, request, make_response, 
    current_app, redirect, url_for
)
from pathlib import Path
import time

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    """Homepage with scenario list."""
    try:
        current_app.logger.debug(f"API URL: {current_app.config['API_BASE_URL']}")
        # Make API call to get scenarios
        response = current_app.api_client.get('/api/scenarios')
        current_app.logger.debug(f"API Response: {response.text}")
        data = response.json()
        
        response = make_response(render_template('index.html', 
                             baseline=data['baseline'], 
                             scenarios=data['scenarios'],
                             timestamp=int(time.time())))
        
        # Add cache control headers to prevent browser caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@frontend_bp.route('/scenario/<scenario_name>')
def view_scenario(scenario_name):
    """View individual scenario results."""
    try:
        # Make API call to get scenario details
        response = current_app.api_client.get(f'/api/scenario/{scenario_name}')
        results = response.json()
        
        return render_template('scenario.html', 
                             scenario_name=scenario_name, 
                             results=results)
    except Exception as e:
        return render_template('error.html', error=str(e)), 400

@frontend_bp.route('/comparison')
def comparison():
    """Simple scenario comparison view."""
    try:
        # Make API call to get comparison data
        response = current_app.api_client.get('/api/comparison-results')
        data = response.json()
        
        return render_template('comparison.html', 
                             scenarios=data.get('scenarios'), 
                             baseline=data.get('baseline'))
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@frontend_bp.route('/create')
def create_scenario():
    """Create new scenario form."""
    return render_template('create.html')

@frontend_bp.route('/edit-baseline', methods=['GET', 'POST'])
def edit_baseline():
    """Edit baseline scenario."""
    try:
        if request.method == 'POST':
            # Make API call to update baseline
            response = current_app.api_client.put('/api/baseline', data=request.form)
            if response.status_code == 200:
                return redirect(url_for('frontend.index'))
            else:
                raise Exception(response.json().get('error', 'Unknown error'))
        
        # GET request - show form
        response = current_app.api_client.get('/api/scenarios')
        data = response.json()
        return render_template('edit_baseline.html', baseline=data.get('baseline'))
        
    except Exception as e:
        return render_template('error.html', error=str(e)), 400

@frontend_bp.route('/state-taxes', methods=['GET'])
def state_taxes():
    """State tax configuration management."""
    try:
        # Make API call to get state tax configurations
        response = current_app.api_client.get('/api/state-taxes')
        states = response.json()
        
        return render_template('state_taxes.html', states=states)
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@frontend_bp.route('/scenario/<scenario_name>/edit', methods=['GET', 'POST'])
def edit_scenario(scenario_name):
    """Edit an existing scenario."""
    try:
        if request.method == 'POST':
            # Make API call to update the scenario
            response = current_app.api_client.put(f'/api/scenarios/{scenario_name}', 
                                                json=request.form)
            if response.status_code == 200:
                return redirect(url_for('frontend.view_scenario', scenario_name=scenario_name))
            else:
                raise Exception(response.json().get('error', 'Unknown error'))
        
        # GET request - show form
        response = current_app.api_client.get(f'/api/scenarios/{scenario_name}')
        data = response.json()
        
        return render_template('edit.html', 
                             scenario_name=scenario_name, 
                             scenario=data)
    except Exception as e:
        return render_template('error.html', error=str(e)), 400

@frontend_bp.route('/cost-analysis')
def cost_analysis():
    """Detailed cost analysis view."""
    try:
        # Make API call to get cost analysis data
        response = current_app.api_client.get('/api/cost-analysis')
        data = response.json()
        
        return render_template('cost_analysis.html', 
                             analysis_data=data)
    except Exception as e:
        return render_template('error.html', error=str(e)), 500