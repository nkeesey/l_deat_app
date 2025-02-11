from flask import Blueprint, jsonify, request, render_template
import pandas as pd
from app.services.s3_service import S3Service
from app.services.data_service import DataService

from werkzeug.exceptions import NotFound, InternalServerError

main = Blueprint('main', __name__)
s3_service = S3Service(use_local=True, data_dir='data')
data_service = DataService(csv_path='data/comparison_bonsai_df.csv')

@main.route('/api/files/', methods=['GET'])
def list_available_files():
    try:
        files = s3_service.list_files()
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/data', methods=['GET'])
def get_data():
    try:
        page = request.args.get('page')
        if page:
            # Handle paginated data request
            page = int(page)
            page_size = int(request.args.get('page_size', 50))
            filters = {k: v for k, v in request.args.items() 
                      if k not in ['page', 'page_size']}
            return jsonify(data_service.get_filtered_data(filters, page, page_size))
        
        # Handle original S3/file-based request
        filename = request.args.get('filename')
        if filename:
            raw_data = s3_service.get_file(filename)
            processed_data = data_service.process_data(raw_data)
            return jsonify(processed_data)
            
        return jsonify({'error': 'No valid parameters provided'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/')
def display_csv():
    try:
        # Read your CSV file
        df = pd.read_csv('data/comparison_bonsai_df.csv')
        
        # Convert DataFrame to HTML table
        table_html = df.head(50).to_html(classes='table table-striped', index=False)
        
        return render_template('display.html', table=table_html)
    except Exception as e:
        return f"Error: {str(e)}"

@main.route('/api/summary')
def get_summary():
    """Get overall dataset summary."""
    try:
        return jsonify(data_service.get_summary())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/columns/<column_name>/stats')
def get_column_stats(column_name):
    """Get statistics for a specific column."""
    try:
        stats = data_service.get_column_stats(column_name)
        return jsonify(stats)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/health')
def health_check():
    """Simple health check endpoint."""
    return jsonify({'status': 'healthy'})

@main.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@main.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@main.errorhandler(Exception)
def handle_exception(error):
    return jsonify({'error': str(error)}), 500