import os

class Config:
    SECRET_KEY = 'umpalumpa'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    DATABASE_PATH = 'analyses.db'
    
    # Dozwolone rozszerzenia
    ALLOWED_EXTENSIONS = {'pcap', 'pcapng', 'cap'}
    
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs('static/img', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS