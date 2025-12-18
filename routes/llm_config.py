"""
LLM Configuration Module

Provides unified interface for managing multiple LLM providers (OpenAI, Anthropic, Google).
"""
from typing import Dict, Tuple
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

# Model configuration: model_id -> (provider_class, display_name, description, config)
MODEL_CONFIGS = {
    # OpenAI models
    'openai-gpt-4o': (
        ChatOpenAI,
        'GPT-4o (OpenAI)',
        'Most capable OpenAI model, best for complex analysis',
        {'model': 'gpt-4o', 'temperature': 0.7}
    ),
    'openai-gpt-4o-mini': (
        ChatOpenAI,
        'GPT-4o Mini (OpenAI)',
        'Fast and cost-effective, good for most tasks',
        {'model': 'gpt-4o-mini', 'temperature': 0.7}
    ),
    'openai-gpt-4-turbo': (
        ChatOpenAI,
        'GPT-4 Turbo (OpenAI)',
        'Powerful model with extended context',
        {'model': 'gpt-4-turbo', 'temperature': 0.7}
    ),

    # Anthropic Claude models
    'anthropic-claude-opus-4-5': (
        ChatAnthropic,
        'Claude Opus 4.5 (Anthropic)',
        'Most powerful Claude model, excellent reasoning',
        {'model': 'claude-opus-4-5-20251101', 'temperature': 0.7}
    ),
    'anthropic-claude-sonnet-4-5': (
        ChatAnthropic,
        'Claude Sonnet 4.5 (Anthropic)',
        'Balanced performance and speed',
        {'model': 'claude-sonnet-4-5-20250929', 'temperature': 0.7}
    ),
    'anthropic-claude-sonnet-3-7': (
        ChatAnthropic,
        'Claude Sonnet 3.7 (Anthropic)',
        'Fast and efficient for standard tasks',
        {'model': 'claude-sonnet-3-7-20250219', 'temperature': 0.7}
    ),

    # Google Gemini models
    'google-gemini-2-0-flash': (
        ChatGoogleGenerativeAI,
        'Gemini 2.0 Flash (Google)',
        'Fast multimodal model with good performance',
        {'model': 'gemini-2.0-flash-exp', 'temperature': 0.7}
    ),
    'google-gemini-1-5-pro': (
        ChatGoogleGenerativeAI,
        'Gemini 1.5 Pro (Google)',
        'Powerful model with large context window',
        {'model': 'gemini-1.5-pro', 'temperature': 0.7}
    ),
    'google-gemini-1-5-flash': (
        ChatGoogleGenerativeAI,
        'Gemini 1.5 Flash (Google)',
        'Fast and efficient for standard tasks',
        {'model': 'gemini-1.5-flash', 'temperature': 0.7}
    ),
}

# Provider API key requirements
PROVIDER_API_KEYS = {
    'openai': 'OPENAI_API_KEY',
    'anthropic': 'ANTHROPIC_API_KEY',
    'google': 'GOOGLE_API_KEY',
}


def get_llm_instance(model_id: str):
    """
    Get initialized LLM instance for the specified model.

    Args:
        model_id: Model identifier (e.g., 'openai-gpt-4o-mini')

    Returns:
        Initialized LangChain chat model instance

    Raises:
        ValueError: If model_id is invalid or API key is missing
    """
    if model_id not in MODEL_CONFIGS:
        raise ValueError(f"Invalid model_id: {model_id}")

    provider_class, display_name, description, config = MODEL_CONFIGS[model_id]
    provider = model_id.split('-')[0]  # Extract provider from model_id

    # Check for required API key
    api_key_name = PROVIDER_API_KEYS.get(provider)
    if not api_key_name:
        raise ValueError(f"Unknown provider: {provider}")

    api_key = os.environ.get(api_key_name)
    if not api_key:
        raise ValueError(
            f"Missing API key: {api_key_name}. "
            f"Please add it to your .env file to use {display_name}."
        )

    # Initialize and return the LLM instance
    return provider_class(**config)


def get_available_models() -> Dict[str, Tuple[str, str]]:
    """
    Get list of available models based on configured API keys.

    Returns:
        Dict mapping model_id to (display_name, description)
        Only includes models whose API keys are configured.
    """
    available_models = {}

    for model_id, (provider_class, display_name, description, config) in MODEL_CONFIGS.items():
        provider = model_id.split('-')[0]
        api_key_name = PROVIDER_API_KEYS.get(provider)

        # Only include models whose API keys are configured
        if api_key_name and os.environ.get(api_key_name):
            available_models[model_id] = (display_name, description)

    return available_models


def get_default_model() -> str:
    """
    Get default model ID based on available API keys.
    Preference order: OpenAI > Anthropic > Google

    Returns:
        Default model_id
    """
    # Try OpenAI first
    if os.environ.get('OPENAI_API_KEY'):
        return 'openai-gpt-4o-mini'

    # Try Anthropic
    if os.environ.get('ANTHROPIC_API_KEY'):
        return 'anthropic-claude-sonnet-3-7'

    # Try Google
    if os.environ.get('GOOGLE_API_KEY'):
        return 'google-gemini-1-5-flash'

    # Fallback (will raise error when used if key not configured)
    return 'openai-gpt-4o-mini'
