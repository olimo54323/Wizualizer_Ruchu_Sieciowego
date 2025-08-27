from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from config import Config, allowed_file
from database import Database
from pcap_analyzer import PcapAnalyzer
from stats_generator import StatsGenerator
from report_generator import ReportGenerator
from packet_filter import PacketFilter

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

db = Database(Config.DATABASE_PATH)
analyzer = PcapAnalyzer()
stats_gen = StatsGenerator()
report_gen = ReportGenerator()
filter_handler = PacketFilter()

@app.route('/')
def index():
    analyses = db.get_all_analyses()
    return render_template('index.html', analyses=analyses)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Obsługa przesłanego pliku
    if 'file' in request.files and request.files['file'].filename:
        file = request.files['file']
        
        if not allowed_file(file.filename):
            flash('Invalid file format. Allowed: .pcap, .pcapng, .cap')
            return redirect(url_for('index'))
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
    # Obsługa ścieżki do pliku
    elif 'file_path' in request.form and request.form['file_path'].strip():
        file_path = request.form['file_path'].strip()
        
        if not os.path.exists(file_path):
            flash(f'File does not exist: {file_path}')
            return redirect(url_for('index'))
        
        if not allowed_file(file_path):
            flash('Invalid file format. Allowed: .pcap, .pcapng, .cap')
            return redirect(url_for('index'))
        
        # Użyj oryginalnej ścieżki
        filepath = file_path
        filename = os.path.basename(file_path)
        
    else:
        flash('No file selected or path provided')
        return redirect(url_for('index'))
    
    try:
        print(f"Analyzing file: {filepath}")
        packets = analyzer.analyze_file(filepath)
        print(f"Found {len(packets)} packets")
        
        stats = stats_gen.generate_stats(packets)
        print("Generated stats")
        
        analysis_id = db.save_analysis(filename, packets, stats)
        print(f"Saved analysis with ID: {analysis_id}")
        
        flash(f'Successfully analyzed file: {filename}')
        return redirect(url_for('view_analysis', analysis_id=analysis_id))
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        flash(f'Error processing file: {str(e)}')
        return redirect(url_for('index'))
    finally:
        # Usuń plik tylko jeśli był przesłany, nie jeśli był podana ścieżka
        if 'file' in request.files and request.files['file'].filename:
            if os.path.exists(filepath):
                os.remove(filepath)

@app.route('/view/<int:analysis_id>')
def view_analysis(analysis_id):
    analysis = db.get_analysis(analysis_id)
    
    if not analysis:
        flash('Analysis not found')
        return redirect(url_for('index'))
    
    return render_template('view.html', 
                         filename=analysis['filename'],
                         data=analysis['packets'],
                         stats=analysis['stats'],
                         analysis_id=analysis_id)

@app.route('/generate_report/<int:analysis_id>')
def generate_report(analysis_id):
    analysis = db.get_analysis(analysis_id)
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    options = request.args.getlist('options[]')
    if not options:
        options = ['summary', 'protocols', 'ports', 'mac_addresses']
    
    report_path = report_gen.generate_pdf(
        analysis['filename'],
        analysis['packets'],
        analysis['stats'],
        options
    )
    
    return send_file(report_path, as_attachment=True)

@app.route('/export_csv/<int:analysis_id>')
def export_csv(analysis_id):
    analysis = db.get_analysis(analysis_id)
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    csv_path = report_gen.export_csv(analysis['packets'])
    return send_file(csv_path, as_attachment=True)

@app.route('/generate_filtered_report/<int:analysis_id>', methods=['POST'])
def generate_filtered_report(analysis_id):
    analysis = db.get_analysis(analysis_id)
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    filters = request.json
    filtered_packets = filter_handler.filter_packets(analysis['packets'], filters)
    
    report_path = report_gen.generate_filtered_pdf(
        analysis['filename'],
        filtered_packets,
        filters
    )
    
    return jsonify({
        'success': True,
        'report_url': url_for('download_report', filename=os.path.basename(report_path))
    })

@app.route('/download_report/<filename>')
def download_report(filename):
    return send_file(os.path.join(Config.UPLOAD_FOLDER, filename), as_attachment=True)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)