#!/bin/bash

# AI Research Proposal Evaluation System - Environment Setup Script
# This script helps you set up the required environment variables

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Setting up environment variables for AI Research Proposal Evaluation System${NC}"
echo ""

# Function to set environment variable
set_env_var() {
    local var_name=$1
    local var_description=$2
    local current_value=$(printenv $var_name)
    
    if [ -n "$current_value" ]; then
        echo -e "${GREEN}✅ $var_name is already set: ${current_value:0:20}...${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}📝 $var_description${NC}"
    read -p "Enter $var_name: " var_value
    
    if [ -n "$var_value" ]; then
        export $var_name="$var_value"
        echo -e "${GREEN}✅ $var_name set successfully${NC}"
        
        # Add to bashrc for persistence
        if ! grep -q "export $var_name=" ~/.bashrc; then
            echo "export $var_name=\"$var_value\"" >> ~/.bashrc
            echo -e "${BLUE}💾 Added to ~/.bashrc for persistence${NC}"
        fi
    else
        echo -e "${RED}❌ $var_name not set${NC}"
        return 1
    fi
}

echo -e "${BLUE}🔑 API Configuration${NC}"
echo "You need to set up API credentials. Choose your option:"
echo ""
echo "1. DeepSeek API"
echo "2. OpenAI API"
echo "3. Custom API (e.g., vLLM, Ollama, etc.)"
echo "4. Skip (use web interface settings only)"
echo ""

read -p "Choose option (1-4): " api_option

case $api_option in
    1)
        echo -e "${YELLOW}📋 Setting up DeepSeek API...${NC}"
        echo "Get your API key from: https://platform.deepseek.com/api_keys"
        echo ""
        set_env_var "DEEPSEEK_API_KEY" "DeepSeek API Key"
        set_env_var "DEEPSEEK_BASE_URL" "DeepSeek Base URL (default: https://api.deepseek.com/v1)" "https://api.deepseek.com/v1"
        ;;
    2)
        echo -e "${YELLOW}📋 Setting up OpenAI API...${NC}"
        echo "Get your API key from: https://platform.openai.com/api-keys"
        echo ""
        set_env_var "OPENAI_API_KEY" "OpenAI API Key"
        set_env_var "OPENAI_BASE_URL" "OpenAI Base URL (default: https://api.openai.com/v1)" "https://api.openai.com/v1"
        set_env_var "OPENAI_MODEL_NAME" "Model name (default: gpt-4o-mini)" "gpt-4o-mini"
        ;;
    3)
        echo -e "${YELLOW}📋 Setting up Custom API...${NC}"
        echo "For custom APIs (vLLM, Ollama, etc.), you can set these manually:"
        echo ""
        set_env_var "OPENAI_BASE_URL" "Custom API Base URL (e.g., http://localhost:8000/v1)"
        set_env_var "OPENAI_MODEL_NAME" "Model name for your custom API"
        set_env_var "OPENAI_API_KEY" "API Key (can be empty for local APIs)"
        ;;
    4)
        echo -e "${YELLOW}⏭️ Skipping API setup. You can configure APIs in the web interface.${NC}"
        ;;
    *)
        echo -e "${RED}❌ Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}🌍 Environment Variables Summary${NC}"
echo "=================================="

# Show current environment variables
env_vars=("DEEPSEEK_API_KEY" "DEEPSEEK_BASE_URL" "OPENAI_API_KEY" "OPENAI_BASE_URL" "OPENAI_MODEL_NAME")
for var in "${env_vars[@]}"; do
    value=$(printenv $var)
    if [ -n "$value" ]; then
        if [[ "$var" == *"API_KEY" ]]; then
            echo -e "${GREEN}✅ $var: ${value:0:10}...${NC}"
        else
            echo -e "${GREEN}✅ $var: $value${NC}"
        fi
    else
        echo -e "${RED}❌ $var: Not set${NC}"
    fi
done

echo ""
echo -e "${GREEN}🎉 Environment setup complete!${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Source your bashrc: source ~/.bashrc"
echo "2. Test the configuration: python test_gunicorn.py"
echo "3. Start the server: ./start_gunicorn.sh"
echo ""
echo -e "${BLUE}💡 Tip: You can also set environment variables temporarily:${NC}"
echo "export DEEPSEEK_API_KEY='your_deepseek_key_here'"
echo "export DEEPSEEK_BASE_URL='https://api.deepseek.com/v1'"
echo ""
echo "Or for other APIs:"
echo "export OPENAI_API_KEY='your_openai_key_here'"
echo "export OPENAI_BASE_URL='https://api.openai.com/v1'"
echo "export OPENAI_MODEL_NAME='gpt-4o-mini'"