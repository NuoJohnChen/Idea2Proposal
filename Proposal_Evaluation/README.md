# AI Research Proposal Evaluation System

An intelligent system for evaluating research proposals using advanced AI models with structured assessment criteria.

## Overview

This project provides a comprehensive framework for evaluating research proposals through automated AI-driven analysis. It offers both batch processing capabilities for multiple proposals and a web-based interface for individual proposal evaluation.

## Features

- **Structured Evaluation**: 8-dimensional assessment framework with detailed scoring criteria
- **Batch Processing**: Process multiple proposals from directories efficiently
- **Web Interface**: User-friendly web application for individual proposal evaluation
- **Ensemble Review**: Multiple AI reviewers for robust evaluation
- **Self-Reflection**: Iterative improvement through AI self-reflection
- **Meta-Review**: Synthesis of multiple reviews into final assessment

## Project Structure

```
├── app.py                    # Web application for individual proposal evaluation
├── predict_proposal.py       # Batch processing script for multiple proposals
├── ai_scientist/            # Core evaluation modules
├── examples_*/              # Input directories for batch processing
├── results_*/               # Output directories for batch results
└── templates/               # Web interface templates
```

## Core Components

### 1. Batch Processing (`predict_proposal.py`)

Process multiple research proposals from directories:

```bash
python predict_proposal.py
```

**Features:**

- Processes all `.txt` files in specified example directories
- Supports multiple input formats (triple-quoted blocks, Python lists)
- Generates detailed JSON reviews and summary files
- Multi-threaded processing for efficiency

**Input Directories:**

- `examples/`

**Output:**

- JSON review files with detailed scores and justifications
- Summary text files with key metrics
- Comprehensive logging

### 2. Web Application (`app.py`)

Deploy a web interface for individual proposal evaluation:

```bash
python app.py
```

**Features:**

- Real-time proposal evaluation
- Interactive scoring display
- Detailed criteria explanations
- HTTPS support for secure access

**Access:**

- Local: `http://localhost:4090`
- HTTPS: `https://localhost:4090` (with SSL)

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

- Python 3.8+
- OpenAI API access
- Required Python packages (see requirements.txt)

### Installation

```bash
git clone <repository-url>
cd AI-Scientist-research-plan-eval
pip install -r requirements.txt
```

### Configuration

1. Set up your OpenAI API credentials in the respective scripts
2. Configure model parameters as needed
3. Prepare input directories for batch processing

## Usage Examples

### Batch Processing

```bash
# Process all proposals in example directories
python predict_proposal.py
```

### Web Interface

```bash
# Start the web application
python app.py
```

### Individual Evaluation

```python
from predict_proposal import perform_structured_review

review = perform_structured_review(
    proposal_text,
    model="deepseek-v3",
    client=openai_client,
    temperature=0.1,
    num_reviews_ensemble=3,
    num_reflections=3
)
```

## Advanced Features

### Ensemble Review Process

1. **Multiple Independent Reviews**: Generate 3 independent evaluations
2. **Meta-Review**: Synthesize reviews into comprehensive assessment
3. **Self-Reflection**: Iterative improvement through AI self-reflection
4. **Final Synthesis**: Weighted average of ensemble scores

### Context-Aware Evaluation

The system considers the proposal's origin context:

- **Leader-guided**: Highly curated, expected highest quality
- **Multi-Person**: Broad consensus approach
- **Single-Person**: Individual perspective

## Acknowledgments

This project builds upon advanced AI evaluation techniques and research proposal assessment frameworks.
