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

## Web Application Deployment

### Development Mode

Deploy a web interface for individual proposal evaluation:

```bash
python app.py
```

**Access:**
- Local: `http://localhost:4090`
- HTTPS: `https://localhost:4090` (with SSL)

### Production Mode with Gunicorn

For production deployment, use Gunicorn WSGI server:

#### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Start with Gunicorn
gunicorn --config gunicorn.conf.py wsgi:app
```

#### Using the Startup Script

For easier deployment, use the provided startup script:

```bash
# Make script executable (first time only)
chmod +x start_gunicorn.sh

# Start the application
./start_gunicorn.sh
```

The startup script will:
- ✅ Check all dependencies
- 📁 Create necessary directories
- 🔧 Install gunicorn if missing
- 🚀 Start the server with optimal settings

#### Environment Setup

Before starting the server, set up your API credentials:

```bash
# Run the environment setup script
./setup_env.sh
```

This will guide you through setting up:
- **DeepSeek API** (recommended default)
- **OpenAI API** (alternative)
- **Custom APIs** (vLLM, Ollama, etc.)

Or set environment variables manually:

```bash
# For DeepSeek (recommended)
export DEEPSEEK_API_KEY='your_deepseek_api_key'
export DEEPSEEK_BASE_URL='https://api.deepseek.com/v1'

# For OpenAI
export OPENAI_API_KEY='your_openai_api_key'
export OPENAI_BASE_URL='https://api.openai.com/v1'
export OPENAI_MODEL_NAME='gpt-4o-mini'
```

#### Testing Gunicorn Configuration

Before deploying, you can test your gunicorn setup:

```bash
# Test gunicorn configuration
python test_gunicorn.py
```

This will verify:
- ✅ App imports correctly
- ✅ WSGI configuration is valid
- ✅ Gunicorn can start with your config

#### Advanced Gunicorn Options

```bash
# Basic gunicorn command
gunicorn -w 4 -b 0.0.0.0:4090 wsgi:app

# With custom configuration file
gunicorn --config gunicorn.conf.py wsgi:app

# With SSL support
gunicorn --config gunicorn.conf.py --certfile=path/to/cert.pem --keyfile=path/to/key.pem wsgi:app

# With systemd service (recommended for production)
sudo systemctl start idea2proposal
sudo systemctl enable idea2proposal
```

#### Gunicorn Configuration

The `gunicorn.conf.py` file includes optimized settings for production:

- **Workers**: Automatically set to `CPU_COUNT * 2 + 1`
- **Timeout**: 300 seconds for long-running AI evaluations
- **Logging**: Structured logging to `logs/` directory
- **Memory Management**: Automatic worker recycling to prevent memory leaks
- **Security**: Production-ready security settings

#### Systemd Service (Optional)

Create `/etc/systemd/system/idea2proposal.service`:

```ini
[Unit]
Description=AI Research Proposal Evaluation System
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/Demo
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/gunicorn --config gunicorn.conf.py wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable idea2proposal
sudo systemctl start idea2proposal
```

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

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- API access (DeepSeek, OpenAI, or custom API)
- Required Python packages (see requirements.txt)

### Installation

```bash
git clone <repository-url>
cd Demo
pip install -r requirements.txt
```

### 1. Set up API Keys

**Method 1: Use setup script (recommended)**
```bash
chmod +x setup_env.sh
./setup_env.sh
```

**Method 2: Set environment variables manually**
```bash
# DeepSeek API
export DEEPSEEK_API_KEY='your_deepseek_api_key_here'
export DEEPSEEK_BASE_URL='https://api.deepseek.com/v1'

# OpenAI API
export OPENAI_API_KEY='your_openai_api_key_here'
export OPENAI_BASE_URL='https://api.openai.com/v1'
export OPENAI_MODEL_NAME='gpt-4o-mini'

# Custom API (vLLM for self-deployment)
export OPENAI_BASE_URL='http://localhost:8000/v1'
export OPENAI_MODEL_NAME='your_model_name'
export OPENAI_API_KEY=''
```

### 2. Start the Service

```bash
# Test configuration
python test_gunicorn.py

# Start the service
./start_gunicorn.sh
```

### 3. Access the Application

Open your browser and visit: `http://localhost:4090`

## 🔑 API Key Setup

### DeepSeek API
1. Visit: https://platform.deepseek.com/api_keys
2. Register/Login to your account
3. Create a new API key
4. Copy the key and set environment variables

### OpenAI API
1. Visit: https://platform.openai.com/api-keys
2. Register/Login to your account
3. Create a new API key
4. Copy the key and set environment variables

## 🛠️ Troubleshooting

### Common Issues

**Issue 1: `name 'client' is not defined`**
- Solution: Set environment variables or use web interface API settings

**Issue 2: `API key not configured`**
- Solution: Run `./setup_env.sh` or set environment variables manually

**Issue 3: Port already in use**
```bash
# Find process using the port
lsof -i :4090
# Kill the process
kill -9 <PID>
```

**Issue 4: Permission denied**
```bash
chmod +x *.sh
```

## 📝 Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `DEEPSEEK_API_KEY` | DeepSeek API key | None |
| `DEEPSEEK_BASE_URL` | DeepSeek API URL | https://api.deepseek.com/v1 |
| `OPENAI_API_KEY` | OpenAI API key | None |
| `OPENAI_BASE_URL` | OpenAI API URL | https://api.openai.com/v1 |
| `OPENAI_MODEL_NAME` | OpenAI model name | gpt-4o-mini |

## 🎯 Usage Workflow

1. **Set up API keys** → Run `./setup_env.sh` or configure in web interface
2. **Test configuration** → Run `python test_gunicorn.py`
3. **Start the service** → Run `./start_gunicorn.sh`
4. **Access the application** → Open `http://localhost:4090`
5. **Evaluate proposals** → Enter research proposal text in the web interface

## 💡 Tips

- Supports multiple API providers (DeepSeek, OpenAI, vLLM, Ollama, etc.)
- Can switch between different API settings in the web interface
- All evaluation results are saved in the `logs/` directory
- Supports PDF file upload and URL input

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