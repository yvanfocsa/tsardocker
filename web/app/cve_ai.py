# web/app/cve_ai.py

from flask import Blueprint, current_app, request, jsonify

bp_cve = Blueprint('cve_ai', __name__)

@bp_cve.route('/cve/analyze', methods=['POST'])
def analyze_cve():
    # Lazy-load du pipeline au premier appel
    if not hasattr(current_app, 'cve_pipeline'):
        from transformers import pipeline
        current_app.cve_pipeline = pipeline(
            'text2text-generation',
            model='google/flan-t5-small',
            device=-1
        )

    data = request.get_json() or {}
    cve_id = data.get('cve', '')

    prompt = (
        f"Explique la vulnérabilité {cve_id} : résumé, PoC simplifié et mesures de mitigation."
    )

    # Exécution du pipeline IA
    response = current_app.cve_pipeline(
        prompt,
        max_length=256,
        do_sample=False
    )

    analysis = response[0].get('generated_text', '')
    return jsonify({'analysis': analysis})

