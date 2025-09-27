from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import json
import requests
from openai import OpenAI
from ai_scientist.perform_review import perform_review
import PyPDF2
import io
import os
from datetime import datetime
import uuid
from threading import Thread
from queue import Queue
import time

app = Flask(__name__)

# No default API configuration - users must configure their own API
# Check for common environment variables but don't set defaults
deepseek_key = os.getenv('DEEPSEEK_API_KEY')
openai_key = os.getenv('OPENAI_API_KEY')

if deepseek_key:
    print("DeepSeek API key found in environment variables")
    client = OpenAI(api_key=deepseek_key, base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1'))
    model = "deepseek-chat"
elif openai_key:
    print("OpenAI API key found in environment variables")
    client = OpenAI(api_key=openai_key, base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'))
    model = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')
else:
    print("No API keys found in environment variables. Users must configure API settings in the web interface.")
    client = None
    model = None

# Logs directory
LOGS_DIR = "logs"

def log_feedback(payload: dict):
    try:
        os.makedirs(LOGS_DIR, exist_ok=True)
        log_file = os.path.join(LOGS_DIR, "feedback.jsonl")
        payload_with_ts = dict(payload)
        payload_with_ts["timestamp"] = datetime.now().isoformat()
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload_with_ts, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Error logging feedback: {str(e)}")

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.json or {}
        # expected: { feature: 'evaluate'|'extract_pdf'|..., action: 'up'|'down', evaluation_id?, extraction_id?, details? }
        feature = data.get('feature')
        action = data.get('action')
        if feature not in ['evaluate', 'extract_pdf']:
            return jsonify({'error': 'Invalid feature'}), 400
        if action not in ['up', 'down']:
            return jsonify({'error': 'Invalid action'}), 400
        feedback_entry = {
            'feature': feature,
            'action': action,
            'evaluation_id': data.get('evaluation_id'),
            'extraction_id': data.get('extraction_id'),
            'details': data.get('details')
        }
        log_feedback(feedback_entry)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def log_evaluation(proposal_text, review_result, msg_history, call_for_proposal=""):
    """Log evaluation results to JSONL file"""
    try:
        # Ensure logs directory exists
        os.makedirs(LOGS_DIR, exist_ok=True)
        
        # Create log entry
        evaluation_id = str(uuid.uuid4())
        log_entry = {
            "evaluation_id": evaluation_id,
            "timestamp": datetime.now().isoformat(),
            "proposal_text": proposal_text,
            "call_for_proposal": call_for_proposal,
            "review_result": review_result,
            "thinking_process": msg_history
        }
        
        # Write to JSONL file
        log_file = os.path.join(LOGS_DIR, "evaluations.jsonl")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        return evaluation_id
            
    except Exception as e:
        print(f"Error logging evaluation: {str(e)}")

# Define scoring criteria for display
SCORING_CRITERIA = {
    "Overall_Quality": {
        "name": "Overall Quality of Idea",
        "description": "This metric synthesizes all eight dimensions to evaluate the proposal's overall quality and potential impact. It assesses how well the proposal balances creativity, feasibility, and impact across all dimensions."
    },
    "Novelty": {
        "name": "Novelty",
        "description": "This metric assesses the degree to which the research proposal introduces an original idea that modifies existing paradigms in the field. It evaluates originality (how rare, ingenious, imaginative, or surprising the core insight is) and paradigm relatedness (whether the idea preserves the current paradigm or modifies it in a radical, transformational way). High novelty indicates a proposal that challenges fundamental assumptions or opens new avenues of research, rather than incremental tweaks."
    },
    "Workability": {
        "name": "Workability",
        "description": "This metric evaluates the feasibility of the proposed research plan, assessing whether it can be easily implemented without violating known constraints (e.g., technical, ethical, or resource limitations). It considers acceptability (social, legal, or political feasibility) and implementability (ease of execution, including awareness of risks and mitigation strategies). High workability indicates a practical, grounded blueprint rather than speculative ideas."
    },
    "Relevance": {
        "name": "Relevance",
        "description": "This metric assesses how well the proposal applies to the stated research problem and its potential effectiveness in solving it. It evaluates applicability (direct fit to the problem) and effectiveness (likelihood of achieving meaningful results or impact). High relevance ensures the proposal addresses a genuine gap in a compelling, targeted manner, forming a cohesive narrative from problem to solution."
    },
    "Specificity": {
        "name": "Specificity",
        "description": "This metric evaluates how clearly and thoroughly the proposal is articulated, assessing whether it is worked out in detail. It considers implicational explicitness (clear links between actions and outcomes), completeness (breadth of coverage across who, what, where, when, why, and how), and clarity (grammatical and communicative precision). High specificity distinguishes detailed, rigorous plans from vague or incomplete ones."
    },
    "Integration_Depth": {
        "name": "Integration Depth",
        "description": "This metric assesses how well the proposal integrates diverse concepts, methodologies, or data sources into a cohesive and synergistic framework. It evaluates the ability to connect disparate elements, creating a whole that is greater than the sum of its parts. High integration depth indicates a sophisticated, interdisciplinary approach, rather than a siloed or fragmented one."
    },
    "Strategic_Vision": {
        "name": "Strategic Vision",
        "description": "This metric evaluates the long-term potential and forward-looking perspective of the proposal. It assesses whether the research addresses not just an immediate gap but also anticipates future trends, sets the stage for subsequent work, and has a clear vision for its broader impact on the field or society. High strategic vision indicates a proposal that is not just a single project, but a foundational step in a larger, ambitious research agenda."
    },
    "Methodological_Rigor": {
        "name": "Methodological Rigor",
        "description": "This metric assesses the soundness and appropriateness of the proposed research methods. It evaluates the quality of the experimental design, data collection procedures, analytical techniques, and validation strategies. High methodological rigor ensures that the research outcomes will be reliable, valid, and reproducible."
    },
    "Argumentative_Cohesion": {
        "name": "Argumentative Cohesion",
        "description": "This metric assesses the logical flow and coherence of the argument presented in the proposal. It evaluates how well different sections connect to form a unified narrative, the consistency of reasoning throughout, and the strength of the logical connections between claims and evidence. High argumentative cohesion indicates a proposal where all parts work together to build a compelling, logically sound case."
    },
    "Call_Response": {
        "name": "Call for Proposal Response",
        "description": "This metric evaluates how well the proposal addresses and responds to the specific requirements, themes, and objectives outlined in the call for proposal. It assesses alignment with the call's focus areas, adherence to specified guidelines, and the degree to which the proposal directly tackles the challenges or opportunities highlighted in the call. High call response indicates a proposal that is precisely tailored to the call's requirements and demonstrates clear understanding of the expected outcomes."
    }
}

@app.route('/')
def index():
    return render_template('index_generalcriteria.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.json or {}
        proposal_text = data.get('proposal_text', '')
        call_for_proposal = data.get('call_for_proposal', '')
        api_settings = data.get('api_settings', {})

        if not proposal_text.strip():
            return jsonify({'error': 'Please provide a research proposal text'}), 400

        # Decide client/model first (outside worker to fail fast)
        if api_settings.get('apiKey') and api_settings.get('apiBase'):
            if not api_settings.get('modelName'):
                return jsonify({'error': 'Model name is required when using custom API settings'}), 400
            try:
                chosen_client = OpenAI(
                    base_url=api_settings.get('apiBase'),
                    api_key=api_settings.get('apiKey')
                )
                chosen_model = api_settings.get('modelName')
                chosen_temperature = float(api_settings.get('temperature', 0.1))
                if not (0 <= chosen_temperature <= 2):
                    return jsonify({'error': 'Temperature must be between 0 and 2'}), 400
                print(f"Using custom API with model {chosen_model}")
            except Exception as e:
                return jsonify({'error': f'Invalid API configuration: {str(e)}'}), 400
        else:
            if client is None:
                return jsonify({'error': 'No API configured. Please set environment variables (DEEPSEEK_API_KEY or OPENAI_API_KEY) or use custom API settings in the web interface.'}), 400
            chosen_client = client
            chosen_model = model
            chosen_temperature = 0.1
            print("Using environment variable API settings")

        result_queue: Queue = Queue(maxsize=1)

        def worker():
            try:
                review, msg_history = perform_review(
                    proposal_text,
                    chosen_model,
                    chosen_client,
                    num_reflections=3,
                    num_fs_examples=0,
                    num_reviews_ensemble=3,
                    temperature=chosen_temperature,
                    return_msg_history=True,
                    call_for_proposal=call_for_proposal
                )

                print("=== Review Debug Info ===")
                print(f"Review type: {type(review)}")
                print(f"Review keys: {list(review.keys()) if isinstance(review, dict) else 'Not a dict'}")
                print(f"Review content: {review}")
                print("=== End Debug Info ===")

                for key in SCORING_CRITERIA:
                    if isinstance(review, dict) and key in review:
                        review[f"{key}_criteria"] = SCORING_CRITERIA[key]

                if not isinstance(review, dict):
                    print(f"Warning: Review is not a dictionary, type: {type(review)}")
                    review_dict = {}
                else:
                    review_dict = review

                if not isinstance(msg_history, list):
                    print(f"Warning: msg_history is not a list, type: {type(msg_history)}")
                    msg_list = []
                else:
                    msg_list = msg_history

                evaluation_id = log_evaluation(proposal_text, review_dict, msg_list, call_for_proposal)
                payload = {
                    'success': True,
                    'review': review_dict,
                    'scoring_criteria': SCORING_CRITERIA,
                    'thinking_process': msg_list,
                    'evaluation_id': evaluation_id
                }
                result_queue.put(payload)
            except Exception as ex:
                result_queue.put({'error': str(ex)})

        t = Thread(target=worker, daemon=True)
        t.start()

        def generate():
            # send early bytes to avoid 524 before first byte
            yield b' '\
                
            # periodic heartbeats until worker finishes
            while t.is_alive():
                time.sleep(3)
                yield b' '

            payload = result_queue.get()
            yield json.dumps(payload, ensure_ascii=False).encode('utf-8')

        return Response(stream_with_context(generate()), mimetype='application/json')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/extract_pdf', methods=['POST'])
def extract_pdf():
    try:
        pdf_url = ""
        pdf_file = None
        
        # Check if it's a JSON request (for URL) or form data (for file upload)
        if request.content_type and 'application/json' in request.content_type:
            data = request.json
            pdf_url = data.get('pdf_url', '')
        else:
            # Handle form data for file upload
            pdf_file = request.files.get('pdf_file')
            # Also check for URL in form data
            pdf_url = request.form.get('pdf_url', '')
        
        if not pdf_url and not pdf_file:
            return jsonify({'error': 'Please provide either a PDF URL or upload a PDF file'}), 400
        
        text = ""
        
        if pdf_file:
            # Handle uploaded file
            if pdf_file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not pdf_file.filename.lower().endswith('.pdf'):
                return jsonify({'error': 'Please upload a PDF file'}), 400
            
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            except Exception as e:
                return jsonify({'error': f'Error reading PDF file: {str(e)}'}), 400
        
        elif pdf_url:
            # Handle URL
            try:
                response = requests.get(pdf_url, timeout=30)
                response.raise_for_status()
                
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(response.content))
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            except Exception as e:
                return jsonify({'error': f'Error downloading or reading PDF from URL: {str(e)}'}), 400
        
        if not text.strip():
            return jsonify({'error': 'No text could be extracted from the PDF'}), 400
        
        extraction_id = str(uuid.uuid4())
        return jsonify({
            'success': True,
            'text': text.strip(),
            'extraction_id': extraction_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # # For HTTP only (default)
    app.run(debug=True, host='0.0.0.0', port=4090)
    
    # For HTTPS support, replace the above line with:
    # app.run(debug=True, host='0.0.0.0', port=4090, ssl_context='adhoc') 
