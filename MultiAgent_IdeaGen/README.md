<h1 align="center"> 🤝 Idea Geneation by Multi-Agent Collaboration 🎓 </h1>

<h3 align="center">
    <p>A Framework for AI-Powered Academic Discussion and Research Collaboration</p>
</h3>
<p align="center">
    <a href="LICENSE">
        <img alt="License: Apache2" src="https://img.shields.io/badge/License-Apache_2.0-green.svg">
    </a>
    <a href="https://www.python.org/downloads/release/python-3916/">
        <img alt="Python Version" src="https://img.shields.io/badge/python-3.9+-blue.svg">
    </a>
</p>

**Multi-Agent Collaboration** is designed to facilitate AI-powered academic discussions and research collaboration using Large Language Models (LLMs). This framework enables researchers to simulate realistic academic conversations between AI agents with different expertise levels and generate structured research proposals from collaborative discussions.

---

# 🚀 Features

- **🎓 Multi-Agent Academic Discussions**: Simulate realistic conversations between AI researchers with different expertise levels
- **📝 Research Proposal Generation**: Automatically synthesize discussions into structured, citable research proposals
- **📚 Literature Integration**: Built-in Semantic Scholar API integration for real paper citations and analysis
- **🤖 Flexible LLM Support**: DeepSeek V3, OpenAI GPT-4, O1-mini, and custom model integration
- **⚙️ YAML-Based Configuration**: Easy-to-customize discussion scenarios and agent behaviors
- **🤝 Multiple Collaboration Patterns**: Horizontal, Vertical, Interdisciplinary, and Leader-led discussion types
- **🧠 Advanced Memory Management**: Sophisticated chat history and context-aware memory systems
- **🔧 Extensible Tool System**: Integrated paper search, analysis, and research tools

---

# Contents

- [🚀 Features](#-features)
- [🔧 Installation](#-installation)
- [🌐 Environment Variables](#-environment-variables)
- [🎯 Quick Start](#-quick-start)
- [📖 Available Configurations](#-available-configurations)
- [⚙️ Configuration System](#️-configuration-system)
- [🛠️ Advanced Usage](#️-advanced-usage)
- [📊 Output Structure](#-output-structure)
- [🔍 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)

# 🔧 Installation

**Make sure you have Python >= 3.9**

```bash
git clone <your-repository-url>
cd Multi-Agent-Collaboration
pip install -r requirements.txt
```

If you want to use local models or additional features:

```bash
pip install -r requirements_local.txt
```

# 🌐 Environment Variables

You need to export your API keys as follows:

```bash
# For DeepSeek (Recommended)
export DEEPSEEK_API_KEY="your_deepseek_api_key_here"
export DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"

# For OpenAI (Optional)
export OPENAI_API_KEY="your_openai_api_key_here"

# For Semantic Scholar Literature Search (Optional)
export SEMANTIC_SCHOLAR_API_KEY="your_semantic_scholar_key_here"
```

# 🎯 Quick Start

Choose any configuration and run a discussion on your topic:

```bash
# Horizontal collaboration (peer-level researchers)
cd agentverse/tasks/simulation/Horizontal_Collaboration
python run_dynamic_topic.py --topic "machine learning interpretability"

# Vertical collaboration (mixed hierarchy levels)
cd agentverse/tasks/simulation/Vertical_Collaboration  
python run_dynamic_topic.py --topic "quantum computing applications"

# Interdisciplinary collaboration (cross-domain experts)
cd agentverse/tasks/simulation/Interdisciplinary_Collaboration
python run_dynamic_topic.py --topic "AI for healthcare"

# Leader-led collaboration (senior-guided discussion)
cd agentverse/tasks/simulation/Leader_Led_Collaboration
python run_dynamic_topic.py --topic "federated learning privacy"

# Multi-agent collaboration (general framework)
cd agentverse/tasks/simulation/Multi_Collaboration
python run_dynamic_topic.py --topic "neural architecture search"

# Individual reflection with DeepSeek
cd agentverse/tasks/simulation/Solitary_Ideation_deepseek_v3
python run_dynamic_topic.py --topic "AI ethics"

# Individual reflection with O1-mini
cd agentverse/tasks/simulation/Solitary_Ideation_o1_mini
python run_dynamic_topic.py --topic "transformer architectures"
```

# 📖 Available Configurations

The `agentverse/tasks/simulation/` directory contains various pre-configured discussion scenarios:

## Collaboration Patterns

| Configuration                                 | Description                                     | Best Use Case                                            |
| --------------------------------------------- | ----------------------------------------------- | -------------------------------------------------------- |
| **`Horizontal_Collaboration`**        | Peer-level researchers with equal expertise     | Equal-level expert discussions, peer reviews             |
| **`Vertical_Collaboration`**          | Mixed hierarchy with different seniority levels | Academic mentoring, student-supervisor interactions      |
| **`Interdisciplinary_Collaboration`** | Cross-domain experts from different fields      | Multi-domain problem solving, interdisciplinary research |
| **`Leader_Led_Collaboration`**        | Senior researcher guiding junior participants   | Research leadership, guided team discussions             |
| **`Multi_Collaboration`**             | General multi-agent discussion framework        | Flexible group discussions, custom scenarios             |

## Individual Reflection

| Configuration                               | Description                       | Model Used     |
| ------------------------------------------- | --------------------------------- | -------------- |
| **`Solitary_Ideation_deepseek_v3`** | Single researcher self-reflection | DeepSeek V3    |
| **`Solitary_Ideation_o1_mini`**     | Single researcher self-reflection | OpenAI O1-mini |

# ⚙️ Configuration System

The framework uses YAML configuration files to define discussion scenarios. Each configuration contains:

```yaml
prompts:              # Role definitions and behavioral guidelines
environment:          # Discussion rules and turn management  
agents:              # Participant configurations and LLM settings
tools:               # Research tools (Semantic Scholar, etc.)
ai_researcher_config: # Literature search parameters
```

## Key Configuration Parameters

| Section               | Purpose                                         | Key Settings                             |
| --------------------- | ----------------------------------------------- | ---------------------------------------- |
| **Prompts**     | Define agent personalities and expertise levels | Role descriptions, behavioral guidelines |
| **Environment** | Control discussion flow                         | Max turns, order type, visibility rules  |
| **Agents**      | Configure participants                          | LLM type, temperature, memory settings   |
| **Tools**       | Enable research capabilities                    | Paper search, citation analysis          |

## Customizing Configurations

1. **Copy an existing configuration:**

```bash
cp Horizontal_Collaboration/config.yaml my_custom_config.yaml
```

2. **Modify key parameters:**

   - Change `max_turns` for discussion length
   - Adjust `temperature` for creativity levels
   - Modify prompts for different expertise
   - Add/remove tools as needed
3. **Test your configuration:**

```bash
python run_dynamic_topic.py --config my_custom_config.yaml --topic "test topic"
```

# 🛠️ Advanced Usage

## Batch Processing

```bash
# Compare different collaboration types on the same topic
topic="federated learning privacy"
for config in Horizontal_Collaboration Vertical_Collaboration Leader_Led_Collaboration; do
    cd agentverse/tasks/simulation/$config
    python run_dynamic_topic.py --topic "$topic"
    cd ../../../..
done

# Test multiple topics with the same configuration
for topic in "NLP transformers" "Computer Vision" "Robotics control"; do
    python run_dynamic_topic.py --topic "$topic"
done

# Compare different LLMs on the same topic  
topic="quantum machine learning"
cd agentverse/tasks/simulation/
cd Solitary_Ideation_deepseek_v3 && python run_dynamic_topic.py --topic "$topic" && cd ..
cd Solitary_Ideation_o1_mini && python run_dynamic_topic.py --topic "$topic" && cd ..
```

# 📊 Output Structure

Each discussion generates structured outputs:

```
outputs/
├── {topic}_run{n}_{timestamp}.txt        # Complete conversation log
├── logs/
│   └── {topic}_run{n}_{timestamp}.log    # Debug and execution info
└── research_proposals/
    └── {topic}_proposal.txt              # Synthesized research proposal
```

## Generated Research Proposals

The framework automatically synthesizes discussions into structured proposals containing:

1. **Title** - Research question formulation
2. **Problem Statement** - Current limitations and knowledge gaps
3. **Motivation & Hypothesis** - Research rationale and expected outcomes
4. **Proposed Method** - Technical approach and methodology
5. **Experiment Plan** - Step-by-step experimental design
6. **References** - Verified citations from Semantic Scholar integration

## Common Issues

- **API Key Errors**: Ensure environment variables are properly set
- **Import Errors**: Install missing dependencies with `pip install semanticscholar`
- **Memory Issues**: Reduce `max_tokens` or `max_turns` in configuration
- **Network Issues**: Check internet connectivity for Semantic Scholar API

# 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

**Note**: This framework is designed for academic research simulation and collaboration. Ensure proper attribution when using generated content for actual research purposes.
