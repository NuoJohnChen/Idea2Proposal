# Research Proposal Evaluator Web Application

A Flask-based web application for automated research proposal evaluation.

## Features

- 🎯 **Intelligent Evaluation**: Comprehensive assessment of research proposals using AI models
- 📊 **Detailed Metrics**: In-depth analysis across 5 key evaluation dimensions
- 💡 **Scoring Criteria**: Detailed scoring standards for each metric
- 🎨 **Beautiful Interface**: Modern responsive web interface
- ⚡ **Real-time Processing**: Online processing without complex local environment setup

## Evaluation Metrics

### Core Metrics (1-10 Scale)

1. **Overall Quality** - Comprehensive quality and potential impact of the research idea
2. **Argumentative Cohesion** - Logical completeness and persuasiveness
3. **Intellectual Depth** - Significance and originality of core insights
4. **Execution Credibility** - Feasibility and risk awareness of the execution plan
5. **Scientific Rigor** - Objectivity and completeness of validation plans

### Additional Information

- Proposal summary
- Strengths and weaknesses analysis
- Suggested questions
- Limitations analysis
- Final decision (Accept/Reject)

## Usage Instructions

### 1. Start the Application

```bash
python app.py
```

### 2. Access the Web Interface

Open your browser and navigate to: `http://localhost:5000`

### 3. Usage Steps

1. Paste your research proposal in the text box
2. Click the "Evaluate Proposal" button
3. Wait for AI analysis to complete (typically 1-3 minutes)
4. Review the detailed evaluation results

## Recommended Proposal Format

Your research proposal should include the following sections:

```
Title: Your Research Title

Problem Statement: 
Describe the problem you aim to solve...

Motivation & Hypothesis: 
Explain your research motivation and core hypotheses...

Proposed Method: 
Detail your proposed solution...

Step-by-Step Experiment Plan: 
Specific experimental steps and validation methods...
```

## Technical Architecture

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap + JavaScript
- **AI Model**: DeepSeek-v3
- **Evaluation Engine**: Custom evaluation framework

## Important Notes

1. 🔒 **Privacy Protection**: Your proposal text is used only for evaluation and will not be stored
2. ⏱️ **Processing Time**: Evaluation may take 1-3 minutes, please be patient
3. 🌐 **Network Requirements**: Stable internet connection required for AI service access
4. 📝 **Text Length**: Recommended proposal length between 1000-5000 words

## Troubleshooting

If you encounter issues:

1. Ensure port 5000 is not occupied by other programs
2. Check if your network connection is stable
3. Verify that AI service credentials are properly configured

## Support and Feedback

For questions or suggestions, please contact the development team.

---

**Enjoy your research proposal evaluation experience!** 🚀 