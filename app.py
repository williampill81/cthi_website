import re
from pathlib import Path

from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# Resource directory
RESOURCE_ROOT = Path(app.root_path) / 'static' / 'resources'

# Health card categories
HEALTH_CATEGORIES = [
    {'id': 'cancer', 'name': 'Cancer', 'name_zh': '癌症資料卡'},
    {'id': 'cardiovascular', 'name': 'Cardiovascular Health', 'name_zh': '心臟健康卡'},
    {'id': 'chronic-illness', 'name': 'Chronic Illness', 'name_zh': '慢性病健康卡'},
    {'id': 'dental', 'name': 'Dental Health', 'name_zh': '牙科健康卡'},
    {'id': 'infections', 'name': 'Infections and Virus', 'name_zh': '感染和病毒健康卡'},
    {'id': 'mental-health', 'name': 'Mental Health', 'name_zh': '心理健康卡'},
    {'id': 'preventative', 'name': 'Preventative Care', 'name_zh': '預防保健卡'},
    {'id': 'respiratory', 'name': 'Respiratory Health', 'name_zh': '呼吸系統健康卡'},
    {'id': 'sexual-health', 'name': 'Sexual Health', 'name_zh': '性健康卡'},
]


def format_resource_title(filename):
    """Generate a human-friendly title from a resource filename."""
    name = Path(filename).stem
    name = name.replace('_', ' ').replace('-', ' ')
    name = re.sub(r'\s+', ' ', name)
    return name.strip()


def infer_language_labels(filename):
    """Infer language labels for display based on the filename."""
    upper_name = filename.upper()

    if 'COMBINED' in upper_name or 'BILINGUAL' in upper_name or ('ENG' in upper_name and 'CHN' in upper_name):
        return 'English & Chinese', '中英文'
    if 'CHN' in upper_name or 'CHINESE' in upper_name or '中文' in filename:
        return 'Chinese', '中文'
    if 'ENG' in upper_name or 'ENGLISH' in upper_name:
        return 'English', '英文'
    return None, None


def get_resources_for_category(category_id):
    """Return a list of resource metadata dictionaries for a category."""
    category_path = RESOURCE_ROOT / category_id
    if not category_path.exists() or not category_path.is_dir():
        return []

    resources = []
    for file_path in sorted(category_path.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() == '.pdf':
            language_en, language_zh = infer_language_labels(file_path.name)
            resources.append({
                'title': format_resource_title(file_path.name),
                'path': f'resources/{category_id}/{file_path.name}',
                'language_label_en': language_en,
                'language_label_zh': language_zh
            })
    return resources

def get_current_language():
    """Get the current language from session or default to English"""
    return session.get('language', 'en')

def set_language(lang):
    """Set the language in session"""
    session['language'] = lang

@app.route('/set-language/<lang>')
def set_language_route(lang):
    """Set language and redirect back"""
    if lang in ['en', 'zh']:
        set_language(lang)
    return redirect(request.referrer or '/')

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/team')
def team():
    """Meet the Team page"""
    return render_template('team.html')

@app.route('/health-cards')
def health_cards():
    """All Health Education Cards"""
    return render_template('health_cards.html', categories=HEALTH_CATEGORIES)

@app.route('/health-cards/<category>')
def health_card_category(category):
    """Individual health card category"""
    # Find the category info
    cat_info = next((c for c in HEALTH_CATEGORIES if c['id'] == category), None)
    if not cat_info:
        return "Category not found", 404
    resources = get_resources_for_category(category)
    return render_template('health_card_detail.html', category=cat_info, resources=resources)

@app.route('/resources-zh')
def resources_zh():
    """Chinese Health Resources"""
    return render_template('resources_zh.html', categories=HEALTH_CATEGORIES)

@app.route('/resources-zh/<category>')
def resources_zh_category(category):
    """Individual Chinese health resource category"""
    cat_info = next((c for c in HEALTH_CATEGORIES if c['id'] == category), None)
    if not cat_info:
        return "Category not found", 404
    resources = get_resources_for_category(category)
    return render_template('resources_zh_detail.html', category=cat_info, resources=resources)

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

