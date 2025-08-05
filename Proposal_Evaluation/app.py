from flask import Flask, render_template, request, jsonify
import json
from openai import OpenAI
from ai_scientist.perform_review import perform_review

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(base_url="",
                api_key="")

model = "deepseek-v3"

# Define scoring criteria for display
SCORING_CRITERIA = {
    "Overall_Quality": {
        "name": "Overall Quality of Idea",
        "description": "This metric evaluates the overall quality and potential impact of a research idea as presented in a proposal. It synthesizes the four key dimensions above and assesses the proposal's potential to make a significant and lasting contribution to the field.",
        "scale": {
            10: "Landmark Potential: A truly exceptional idea that is visionary, fundamentally sound, and meticulously planned. Clear potential to define a new research paradigm.",
            9: "Clear Breakthrough: An outstanding idea that is highly ambitious, deeply insightful, and backed by a highly credible and rigorous plan.",
            8: "Strong Contender: A very strong and well-crafted idea with significant novelty, persuasive narrative, credible execution plan, and rigorous validation strategy.",
            7: "Solid Contribution: A solid, well-rounded research proposal that represents a clear contribution to the field.",
            6: "Competent but Lacks Spark: A competent proposal that is technically sound but may lack significant ambition or novelty.",
            5: "Has Potential but Flawed: Contains a kernel of a good idea but is undermined by significant flaws in key areas.",
            4: "Weak and Unconvincing: The idea is either unoriginal, poorly motivated, or its proposed execution is not credible.",
            3: "Fatally Flawed: The proposal suffers from critical flaws such as naive problem understanding or technically infeasible plans.",
            2: "Vague and Insubstantial: Too vague to be properly evaluated, lacks clear research question or concrete method.",
            1: "No Merit: Incoherent, unoriginal, and demonstrates complete lack of understanding of the research process."
        }
    },
    "Novelty": {
        "name": "Novelty",
        "description": "This metric assesses the degree to which the research proposal introduces an original idea that modifies existing paradigms in the field. It evaluates originality and paradigm relatedness.",
        "scale": {
            10: "Field-Defining: Proposes a highly original and paradigm-modifying idea that could fundamentally reshape the field or create a new subfield.",
            9: "Paradigm-Shifting: The idea is extremely rare and imaginative, challenging core paradigms with transformative potential.",
            8: "Highly Original: The core insight is profoundly novel and paradigm-modifying, offering a surprising new perspective on a key problem.",
            7: "Significant Novelty: Introduces a rare and ingenious approach that meaningfully modifies existing paradigms.",
            6: "Clever: Presents a non-obvious, imaginative idea that partially modifies paradigms within the current framework.",
            5: "Solid Originality: Offers meaningful novelty but leans more toward paradigm-preserving improvements.",
            4: "Minimally Novel: Slightly original, with just enough rarity or ingenuity to qualify as non-derivative, but mostly paradigm-preserving.",
            3: "Derivative: Mostly paradigm-preserving with minimal originality, resembling common approaches.",
            2: "Trivial: Lacks rarity and ingenuity, feeling mundane and non-transformational.",
            1: "Not Novel: Completely repeats existing paradigms without any original or modifying elements."
        }
    },
    "Workability": {
        "name": "Workability",
        "description": "This metric evaluates the feasibility of the proposed research plan, assessing whether it can be easily implemented without violating known constraints. It considers acceptability and implementability.",
        "scale": {
            10: "Bulletproof: Extremely feasible, with all constraints addressed innovatively; acceptability and implementability are exemplary.",
            9: "Expert-Level: Highly workable, identifying and resolving constraints with clever, efficient strategies showing deep knowledge.",
            8: "Highly Credible: Key constraints are addressed with specific, acceptable, and implementable solutions.",
            7: "Credible: Major feasibility issues are identified, with plausible paths to acceptability and implementation.",
            6: "Plausible: Overall workable, but some constraints or implementation details are not fully explored.",
            5: "Feasible but Vague: Macro-level feasibility is present, but acceptability or implementability lacks detail.",
            4: "Minimally Feasible: Just barely implementable, acknowledging key constraints with minimal but adequate mitigation; acceptability is marginal.",
            3: "Overly Optimistic: Acknowledges constraints but proposes simplistic or unproven paths to implementation.",
            2: "Ignores Fatal Flaws: Obvious constraints are overlooked, making acceptability or implementability doubtful.",
            1: "Pure Fantasy: Violates known constraints entirely, with no feasible path to implementation."
        }
    },
    "Relevance": {
        "name": "Relevance",
        "description": "This metric assesses how well the proposal applies to the stated research problem and its potential effectiveness in solving it. It evaluates applicability and effectiveness.",
        "scale": {
            10: "Exemplary: Perfectly applicable and highly effective, reshaping understanding of the problem with inevitable impact.",
            9: "Outstanding: Seamlessly applicable to the problem, with strong evidence of effectiveness in solving it.",
            8: "Highly Relevant: Tightly fits the problem and demonstrates clear, superior effectiveness.",
            7: "Relevant: Clearly applies to the problem with logical expectation of effectiveness.",
            6: "Applicable: Fits the problem basically, with plausible but not deeply convincing effectiveness.",
            5: "Understandable: Core relevance is graspable, but applicability or effectiveness has gaps.",
            4: "Minimally Relevant: Slightly applicable to the problem with just enough evidence of potential effectiveness to be considered on-topic.",
            3: "Disconnected: Feels loosely applicable, with questionable effectiveness in addressing the problem.",
            2: "Contradictory: Internal inconsistencies reduce applicability and effectiveness.",
            1: "Irrelevant: Does not apply to the stated problem or offer any effective solution."
        }
    },
    "Specificity": {
        "name": "Specificity",
        "description": "This metric evaluates how clearly and thoroughly the proposal is articulated, assessing whether it is worked out in detail. It considers implicational explicitness, completeness, and clarity.",
        "scale": {
            10: "Gold Standard: Extremely specific, with explicit implications, full completeness, and flawless clarity; sets a benchmark.",
            9: "Insightful: Highly detailed, with explicit causal links, comprehensive coverage, and clear communication.",
            8: "Critical: Strong specificity, including detailed breakdowns and clear, complete articulation.",
            7: "Rigorous: Thoroughly specified, with good explicitness, completeness, and clarity.",
            6: "Sufficient: Basically specific, covering key details but with some vagueness in implications or completeness.",
            5: "Basic: Core elements are specified, but lacks depth in explicitness, completeness, or clarity.",
            4: "Minimally Specific: Just enough detail to convey the main ideas, with minimal explicitness, completeness, and clarity to be understandable.",
            3: "Insufficient: Fails to detail key aspects, reducing explicitness and completeness.",
            2: "Vague: Relies on ambiguous descriptions, lacking clarity and thoroughness.",
            1: "Incoherent: Completely lacks specificity, with no clear details or explicit connections."
        }
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.json
        proposal_text = data.get('proposal_text', '')
        
        if not proposal_text.strip():
            return jsonify({'error': 'Please provide a research proposal text'}), 400
        
        # Perform the review
        review = perform_review(
            proposal_text,
            model,
            client,
            num_reflections=3,
            num_fs_examples=0,
            num_reviews_ensemble=3,
            temperature=0.1,
        )
        
        # Add scoring criteria to the response
        for key in SCORING_CRITERIA:
            if key in review:
                review[f"{key}_criteria"] = SCORING_CRITERIA[key]
        
        return jsonify({
            'success': True,
            'review': review,
            'scoring_criteria': SCORING_CRITERIA
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # # For HTTP only (default)
    # app.run(debug=True, host='0.0.0.0', port=4090)
    
    # For HTTPS support, replace the above line with:
    app.run(debug=True, host='0.0.0.0', port=4090, ssl_context='adhoc') 
