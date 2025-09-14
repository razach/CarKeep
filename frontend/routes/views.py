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
from flask import Response

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
        # Fetch scenarios metadata (baseline + examples)
        sc_response = current_app.api_client.get('/api/scenarios')
        sc_data = sc_response.json()
        baseline_raw = sc_data.get('baseline', {})
        scenarios_meta = sc_data.get('scenarios', {})

        # Normalize baseline for template compatibility
        baseline = {
            'vehicle_name': baseline_raw.get('vehicle', {}).get('name', 'Current Vehicle'),
            'current_value': baseline_raw.get('vehicle', {}).get('current_value', 0),
            'monthly_payment': baseline_raw.get('current_loan', {}).get('monthly_payment', 0),
            'state': baseline_raw.get('state', 'VA'),
            'description': baseline_raw.get('description', '')
        }

        # Fetch comparison results (may return a flat mapping of scenario_name -> results)
        comp_response = current_app.api_client.get('/api/comparison-results')
        comp_data = comp_response.json()

        # Determine comp_items
        if isinstance(comp_data, dict) and 'scenarios' in comp_data:
            comp_items = comp_data.get('scenarios', {})
        else:
            comp_items = comp_data if isinstance(comp_data, dict) else {}

        scenarios_list = []
        for name, comp_entry in comp_items.items():
            meta = scenarios_meta.get(name, {})

            # Build a normalized scenario payload the template expects
            scenario_payload = {
                'vehicle': meta.get('scenario', {}).get('vehicle', {}) if meta else (comp_entry.get('scenario', {}).get('vehicle', {}) if isinstance(comp_entry, dict) else {}),
                'financing': meta.get('scenario', {}).get('financing', {}) if meta else (comp_entry.get('scenario', {}).get('financing', {}) if isinstance(comp_entry, dict) else {})
            }

            scenarios_list.append({
                'scenario_name': name,
                'description': meta.get('description') or (comp_entry.get('description') if isinstance(comp_entry, dict) else name),
                'scenario': scenario_payload,
                'state': meta.get('state') or (comp_entry.get('state') if isinstance(comp_entry, dict) else baseline.get('state', 'VA')),
                'results': comp_entry.get('results') if isinstance(comp_entry, dict) else None
            })

        return render_template('comparison.html', 
                             scenarios=scenarios_list, 
                             baseline=baseline)
    except Exception as e:
        current_app.logger.exception('Error rendering comparison page')
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

@frontend_bp.route('/_state-taxes/<state_code>/row', methods=['GET'])
def state_tax_row(state_code):
    """Return a single state row/card partial (for htmx swaps)."""
    try:
        response = current_app.api_client.get('/api/state-taxes')
        states = response.json()
        config = states.get(state_code)
        if not config:
            return Response('Not found', status=404)
        html = render_template('components/state_tax_row.html', state_code=state_code, config=config)
        return html
    except Exception:
        return Response('Error', status=500)

@frontend_bp.route('/_state-taxes/<state_code>/save', methods=['POST'])
def save_state_tax(state_code):
    """Save edits for a state (proxy to API) and return updated row + toast."""
    try:
        # Accept form data (percent values) and forward as JSON to API
        form = request.form
        payload = {
            'property_tax_rate': form.get('property_tax_rate'),
            'pptra_relief': form.get('pptra_relief', 0),
            'relief_cap': form.get('relief_cap', 0),
            'state_name': form.get('state_name', state_code)
        }
        api_resp = current_app.api_client.put(f'/api/state-taxes/{state_code}', json=payload)
        if api_resp.status_code >= 400:
            msg = api_resp.json().get('error', 'Failed to save state')
            resp = Response(status=400)
            resp.headers['HX-Trigger'] = f'{{"toast":{{"type":"error","message":"{msg}"}}}}'
            return resp

        # Re-fetch and render updated row
        sc_response = current_app.api_client.get('/api/state-taxes')
        states = sc_response.json()
        config = states.get(state_code)
        html = render_template('components/state_tax_row.html', state_code=state_code, config=config)
        resp = make_response(html, 200)
        resp.headers['HX-Trigger'] = '{"toast":{"type":"success","message":"State tax saved"}}'
        return resp
    except Exception:
        resp = Response(status=500)
        resp.headers['HX-Trigger'] = '{"toast":{"type":"error","message":"Error saving state"}}'
        return resp

@frontend_bp.route('/_state-taxes/<state_code>/delete', methods=['POST'])
def delete_state_tax_action(state_code):
    """Delete a state via API; return 204 + toast (caller removes element)."""
    try:
        api_resp = current_app.api_client.delete(f'/api/state-taxes/{state_code}')
        payload = api_resp.json()
        if payload.get('success'):
            # Return 200 with empty body so hx-swap="outerHTML" will remove the element
            resp = make_response('', 200)
            resp.headers['HX-Trigger'] = '{"toast":{"type":"success","message":"State deleted"}}'
            return resp
        else:
            msg = payload.get('error', 'Failed to delete state')
            resp = Response(status=400)
            resp.headers['HX-Trigger'] = f'{{"toast":{{"type":"error","message":"{msg}"}}}}'
            return resp
    except Exception:
        resp = Response(status=500)
        resp.headers['HX-Trigger'] = '{"toast":{"type":"error","message":"Error deleting state"}}'
        return resp

@frontend_bp.route('/_state-taxes/create', methods=['POST'])
def create_state_tax_action():
    """Create a new state via API and return the new row to insert into the grid."""
    try:
        form = request.form
        # Expect raw percent inputs from the form; API expects numbers as strings
        payload = {
            'state_code': form.get('state_code', '').upper(),
            'state_name': form.get('state_name', ''),
            'property_tax_rate': form.get('property_tax_rate', '0'),
            'pptra_relief': form.get('pptra_relief', '0'),
            'relief_cap': form.get('relief_cap', '0')
        }

        # Basic validation
        if not payload['state_code'] or not payload['state_name']:
            resp = Response(status=400)
            resp.headers['HX-Trigger'] = '{"toast":{"type":"error","message":"State Code and Name are required"}}'
            return resp

        api_resp = current_app.api_client.post('/api/state-taxes', json=payload)
        if api_resp.status_code >= 400:
            msg = api_resp.json().get('error', 'Failed to add state')
            resp = Response(status=400)
            resp.headers['HX-Trigger'] = f'{{"toast":{{"type":"error","message":"{msg}"}}}}'
            return resp

        # Re-fetch the states and render the new row
        sc_response = current_app.api_client.get('/api/state-taxes')
        states = sc_response.json()
        code = payload['state_code']
        config = states.get(code)
        if not config:
            # Fallback: nothing to render
            resp = Response(status=204)
            resp.headers['HX-Trigger'] = '{"toast":{"type":"success","message":"State added"}}'
            return resp

        row_html = render_template('components/state_tax_row.html', state_code=code, config=config)
        # Include a small OOB script to reset the form
        oob = '<script hx-swap-oob="true">(function(){try{document.getElementById("addStateForm").reset()}catch(e){}})();</script>'
        resp = make_response(row_html + oob, 201)
        resp.headers['HX-Trigger'] = '{"toast":{"type":"success","message":"State added"}}'
        return resp
    except Exception:
        resp = Response(status=500)
        resp.headers['HX-Trigger'] = '{"toast":{"type":"error","message":"Error adding state"}}'
        return resp

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

        # API returns {'analysis': {...}} on success
        analysis = data.get('analysis') if isinstance(data, dict) else None

        return render_template('cost_analysis.html', 
                             analysis=analysis)
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@frontend_bp.route('/_scenarios/<scenario_name>/delete', methods=['POST'])
def delete_scenario_action(scenario_name):
    """Proxy deletion to API and return htmx-friendly response."""
    try:
        api_resp = current_app.api_client.delete(f'/api/scenarios/{scenario_name}')
        payload = api_resp.json()
        if payload.get('success'):
            # Re-fetch scenarios and return OOB count updates so stats refresh
            sc_response = current_app.api_client.get('/api/scenarios')
            sc_data = sc_response.json()
            scenarios = sc_data.get('scenarios', {})
            counts_oob = render_template('components/scenario_counts_oob.html', scenarios=scenarios)
            resp = make_response(counts_oob, 200)
            resp.headers['HX-Trigger'] = '{"toast":{"type":"success","message":"Scenario deleted"}}'
            return resp
        else:
            resp = Response(status=400)
            resp.headers['HX-Trigger'] = '{"toast":{"type":"error","message":"Failed to delete scenario"}}'
            return resp
    except Exception as e:
        resp = Response(status=500)
        resp.headers['HX-Trigger'] = '{"toast":{"type":"error","message":"Error deleting scenario"}}'
        return resp

@frontend_bp.route('/_scenarios/<scenario_name>/duplicate', methods=['POST'])
def duplicate_scenario_action(scenario_name):
    """Proxy duplication to API and return updated grid partial."""
    try:
        api_resp = current_app.api_client.post(f'/api/scenarios/{scenario_name}/duplicate')
        payload = api_resp.json()
        if payload.get('success'):
            # Re-fetch scenarios to render the new grid
            sc_response = current_app.api_client.get('/api/scenarios')
            sc_data = sc_response.json()
            scenarios = sc_data.get('scenarios', {})
            grid_html = render_template('components/scenarios_grid.html', scenarios=scenarios)
            counts_oob = render_template('components/scenario_counts_oob.html', scenarios=scenarios)
            # Return grid + counts OOB together
            resp = make_response(grid_html + counts_oob, 200)
            resp.headers['HX-Trigger'] = '{"toast":{"type":"success","message":"Scenario duplicated"}}'
            return resp
        else:
            resp = Response(status=400)
            resp.headers['HX-Trigger'] = '{"toast":{"type":"error","message":"Failed to duplicate scenario"}}'
            return resp
    except Exception as e:
        resp = Response(status=500)
        resp.headers['HX-Trigger'] = '{"toast":{"type":"error","message":"Error duplicating scenario"}}'
        return resp