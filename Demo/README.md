<h1 align="center"> 🚀 AI Research Proposal Evaluation System 🎓 </h1>

<h3 align="center">
    <p>An intelligent system for evaluating research proposals using AI models with structured assessment criteria.</p>
</h3>
<p align="center">
    <a href="LICENSE">
        <img alt="License: Apache2" src="https://img.shields.io/badge/License-Apache_2.0-green.svg">
    </a>
    <a href="https://www.python.org/downloads/release/python-3916/">
        <img alt="Python Version" src="https://img.shields.io/badge/python-3.9+-blue.svg">
    </a>
</p>

https://ratemyproposal.ai

## Features

- **Structured Evaluation**: 8-dimensional assessment framework with detailed scoring criteria
- **Batch Processing**: Process multiple proposals from directories efficiently
- **Web Interface**: User-friendly web application for individual proposal evaluation
- **Ensemble Review**: Multiple AI reviewers for robust evaluation
- **Self-Reflection**: Iterative improvement through AI self-reflection
- **Meta-Review**: Synthesis of multiple reviews into final assessment
- **CFP-Matching**: Call for Proposal Compatibility Assessment

## Project Structure

```
AI-Scientist-research-plan-eval/
├── app.py                    # Main Flask application
├── templates/
│   └── index_generalcriteria.html     # Web interface
├── ai_scientist/                      # Core evaluation module
│   ├── __init__.py
│   ├── perform_review.py              # Main review engine
│   ├── llm.py                         # LLM interface
│   └── fewshot_examples/              # Example data
├── requirements.txt                   # Python dependencies
├── logs/                             # Logs directory (auto-created)
│   ├── evaluations.jsonl             # Evaluation results
│   └── feedback.jsonl                # User feedback
└── README.md              						# This file
```

 Web Application (`app.py`)

Deploy a web interface for individual proposal evaluation:

```bash
python app.py
```

**Access:**

- Local: `http://localhost:4090`
- HTTPS: `https://localhost:4090` (with SSL)

## Local Model Deployment

### vLLM e.g. with Qwen3-32B

#### Step 1: Install vLLM

```bash
pip install vllm
```

#### Step 2: Start vLLM Server

```bash
# Start vLLM server with Qwen3-32B
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-32B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 2 \
    --gpu-memory-utilization 0.9
```

**Note:** Adjust `--tensor-parallel-size` based on your GPU count (2 for 2 GPUs, 4 for 4 GPUs, etc.)

#### Step 3: Start Your Flask Service

```bash
# In a new terminal, start the Flask application
python app_8criteria.py
```

#### Step 4: Configure Web Application

1. **Open your browser** and go to `http://localhost:4090`
2. **Click "Show Settings"** in the API Settings section
3. **Configure the following**:
   - **API Base URL**: `http://localhost:8000/v1`
   - **Model Name**: `Qwen/Qwen2.5-32B-Instruct`
   - **API Key**: `EMPTY` (leave blank)
   - **Temperature**: `0.1` (recommended for evaluation tasks)
4. **Click "Save Settings"**

#### Step 5: Test the Complete Setup

1. **Paste a research proposal** in the text area
2. **Click "Evaluate Proposal"**
3. **The system will now**:
   - Send the request from Flask service (port 4090)
   - Forward to vLLM server (port 8000) for AI inference
   - Return results back to Flask service
   - Display the evaluation on the webpage

1. - Use the largest model that fits in VRAM
   - Enable tensor parallelism for multiple GPUs
   - Use mixed precision (FP16)

2. **For production**:
   - Use vLLM for best performance
   - Implement caching for repeated evaluations
   - Use load balancing for multiple instances

## Monitoring and Logging

The system automatically logs:

- **Evaluations**: Complete results in `logs/evaluations.jsonl`
- **Feedback**: User feedback in `logs/feedback.jsonl`

## Evaluation Framework

The system evaluates research proposals across 8 core dimensions, each scored from 1.0 to 10.0:

### 1. Novelty (1-10)

**Definition**: Assesses the originality and paradigm-modifying potential of the research idea.

### 2. Workability (1-10)

**Definition**: Evaluates the feasibility and implementability of the proposed research plan.

### 3. Relevance (1-10)

**Definition**: Assesses how well the proposal applies to the stated research problem.

### 4. Specificity (1-10)

**Definition**: Evaluates the clarity and thoroughness of the proposal articulation.

### 5. Integration Depth (1-10)

**Definition**: Assesses how well diverse concepts and methodologies are integrated.

### 6. Strategic Vision (1-10)

**Definition**: Evaluates long-term potential and forward-looking perspective.

### 7. Methodological Rigor (1-10)

**Definition**: Assesses the soundness and appropriateness of research methods.

### 8. Argumentative Cohesion (1-10)

**Definition**: Evaluates logical flow and coherence of the argument.

### Overall Quality (1-10)

**Definition**: Synthesizes all eight dimensions to evaluate overall proposal quality and potential impact.

## Output Format

Each evaluation produces a structured JSON response:

```json
{
  "Novelty": "8.5/10",
  "Workability": "7.2/10",
  "Relevance": "9.1/10",
  "Specificity": "8.8/10",
  "Integration_Depth": "7.9/10",
  "Strategic_Vision": "8.3/10",
  "Methodological_Rigor": "8.7/10",
  "Argumentative_Cohesion": "8.0/10",
  "Overall_Quality": "8.3/10",
  "Decision": "Accept",
  "Weaknesses": [
    "Limited discussion of potential ethical concerns",
    "Could benefit from more detailed timeline"
  ],
  "Justifications": {
    "Novelty": "Proposes a novel approach to...",
    "Workability": "The methodology is well-defined...",
    // ... other justifications
  }
}
```

## Installation and Setup

### Prerequisites

- Python 3.9+
- OpenAI API access
- Required Python packages (see requirements.txt)

### Installation

```bash
git clone <repository-url>
cd Demo
pip install -r requirements.txt
```

### Configuration

1. Set up your OpenAI API credentials in the respective scripts
2. Configure model parameters as needed
3. Prepare input directories for batch processing

## Acknowledgments

This project builds upon advanced AI evaluation techniques and research proposal assessment frameworks.

# Citations

```
@misc{chen2025brainstorm,
      title={Beyond Brainstorming: What Drives High-Quality Scientific Ideas? Lessons from Multi-Agent Collaboration}, 
      author={Nuo Chen and Yicheng Tong and Jiaying Wu and Minh Duc Duong and Qian Wang and Qingyun Zou and Bryan Hooi and Bingsheng He},
      year={2025},
      eprint={2508.04575},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2508.04575}, 
}
```