from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel, Field

# Import LLM configuration
from routes.llm_config import get_llm_instance, get_default_model
from data.db_manager import DBManager

# Load .env file
load_dotenv()

# Initialize DB manager for user lookups
db_manager = DBManager()


# ================================================================
# PYDANTIC MODELS FOR STRUCTURED OUTPUT
# ================================================================

class RecommendationTopic(BaseModel):
    """A single topic in the AI recommendation"""
    title: str = Field(description="The title of this recommendation topic")
    content: str = Field(description="2-3 sentences analyzing this aspect of the A/B test")


class AIRecommendation(BaseModel):
    """Structured AI recommendation for an A/B test"""
    decision: str = Field(
        description="Clear decision: 'Roll out Variant B', 'Keep Variant A', or 'Continue testing'"
    )
    topics: list[RecommendationTopic] = Field(
        description="Exactly 5 topics covering different aspects of the recommendation"
    )

    class Config:
        # Additional validation
        validate_assignment = True


# ================================================================
# HELPER FUNCTION TO GET USER'S LLM
# ================================================================

def _get_user_llm(user_id: int):
    """
    Get the LLM instance for a specific user based on their settings.

    Args:
        user_id: User ID

    Returns:
        Initialized LangChain chat model instance

    Raises:
        ValueError: If user not found or LLM initialization fails
    """
    try:
        user = db_manager.get_user(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        model_id = user.llm_model or get_default_model()
        return get_llm_instance(model_id)

    except Exception as e:
        print(f"Error getting user LLM: {str(e)}")
        # Fallback to default model
        print("Falling back to default model")
        default_model = get_default_model()
        return get_llm_instance(default_model)


# ================================================================
# MAIN FUNCTION WITH STRUCTURED OUTPUT
# ================================================================

def generate_ai_recommendation(test_data, report_data, company_data, user_id):
    """
    Generate AI recommendation using structured outputs.

    Args:
        test_data: AB test data object
        report_data: Statistical report data dict
        company_data: Company context data dict
        user_id: User ID for model selection

    Returns:
        dict: Structured recommendation with decision and 5 topics
    """
    print(f"Generating AI recommendation for user {user_id}...")

    # Get user's selected LLM
    llm = _get_user_llm(user_id)

    # Format statistical data
    method_name = report_data.get('method', 'statistical test')
    ci_lower, ci_upper = report_data.get('ci_95', (None, None))

    system_prompt = f"""You are an expert Conversion Rate Optimization (CRO) consultant providing data-driven recommendations.

COMPANY CONTEXT:
- Company: {company_data.get('name', 'Unknown')}
- Target Audience: {company_data.get('audience', 'General')}
- Industry Context: {company_data.get('year', 'Current year')}

YOUR TASK:
Analyze the A/B test results and provide a clear, actionable recommendation structured into exactly 5 distinct topics.

THE 5 REQUIRED TOPICS ARE:
1. Statistical Significance & Confidence
2. Business Impact Assessment
3. Sample Size & Data Quality
4. Risk Factors & Considerations
5. Next Steps & Action Items

GUIDELINES:
- Use simple, clear language suitable for business stakeholders
- Each topic content should be 2-3 sentences maximum
- Highlight both statistical and practical significance
- Consider the specific audience and industry context
- Be cautious with borderline results (p-value 0.04-0.06)
- Mention if sample size seems insufficient
- Consider the magnitude of change, not just statistical significance
- Provide a clear decision: Roll out Variant B, Keep Variant A, or Continue testing
"""

    user_prompt = f"""Analyze this A/B test and provide your recommendation:

TEST DETAILS:
Test Name: {test_data.name}
Description: {test_data.description if test_data.description else 'No description provided'}
Primary Metric: {test_data.metric}

STATISTICAL RESULTS:
Method: {method_name}
Statistical Significance: {'Yes (p < 0.05)' if report_data.get('significant') else 'No (p ≥ 0.05)'}
P-value: {report_data.get('p_value', 0) if isinstance(report_data.get('p_value'), (int, float)) else 'N/A'}
Confidence Interval (95%): {f'[{ci_lower:.6f}, {ci_upper:.6f}]' if ci_lower is not None and ci_upper is not None else 'N/A'}
Effect Size: {report_data.get('difference', 0):.6f} ({(report_data.get('difference', 0) * 100):.2f} percentage points)
Z-statistic: {report_data.get('standard_deviation', 'N/A')}

VARIANT PERFORMANCE:
Variant A (Control):
- Sample Size: {report_data.get('sample_size_a', 'N/A'):,}
- Conversions: {report_data.get('conversions_a', 'N/A'):,}
- Conversion Rate: {report_data.get('conv_rate_a', 0):.4%}

Variant B (Treatment):
- Sample Size: {report_data.get('sample_size_b', 'N/A'):,}
- Conversions: {report_data.get('conversions_b', 'N/A'):,}
- Conversion Rate: {report_data.get('conv_rate_b', 0):.4%}
- Relative Change: {((report_data.get('conv_rate_b', 0) - report_data.get('conv_rate_a', 0)) / report_data.get('conv_rate_a', 1) * 100):.2f}%

Provide your structured recommendation with exactly 5 topics."""

    try:
        # Use LangChain's structured output
        llm_with_structure = llm.with_structured_output(AIRecommendation)

        # Generate recommendation
        response = llm_with_structure.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        # Convert Pydantic model to dict
        recommendation_dict = {
            "decision": response.decision,
            "topics": [
                {
                    "title": topic.title,
                    "content": topic.content
                }
                for topic in response.topics
            ]
        }

        # Validate we have exactly 5 topics
        if len(recommendation_dict["topics"]) != 5:
            recommendation_dict["topics"] = _ensure_five_topics(recommendation_dict["topics"])

        print("AI recommendation generated successfully!")
        return recommendation_dict

    except Exception as e:
        print(f"Error generating recommendation: {str(e)}")
        # Fallback recommendation with safe attribute access
        test_name = getattr(test_data, 'name', 'Unknown Test')
        sample_a = report_data.get('sample_size_a', 0)
        sample_b = report_data.get('sample_size_b', 0)
        p_val = report_data.get('p_value', 'N/A')
        significance = 'Yes' if report_data.get('significant') else 'No'

        return {
            "decision": "Error generating recommendation",
            "topics": [
                {
                    "title": "Error",
                    "content": f"Failed to generate recommendation: {str(e)[:100]}"
                },
                {
                    "title": "Fallback Analysis",
                    "content": "Please review the test results manually or try regenerating the report."
                },
                {
                    "title": "Data Available",
                    "content": f"Test '{test_name}' comparing {sample_a:,} vs {sample_b:,} samples."
                },
                {
                    "title": "Statistical Result",
                    "content": f"P-value: {p_val}, Statistical Significance: {significance}"
                },
                {
                    "title": "Next Steps",
                    "content": "Contact support if this error persists or check your API configuration."
                }
            ]
        }


def _ensure_five_topics(topics: list) -> list:
    """Ensure exactly 5 topics by padding or trimming"""
    default_titles = [
        "Statistical Significance & Confidence",
        "Business Impact Assessment",
        "Sample Size & Data Quality",
        "Risk Factors & Considerations",
        "Next Steps & Action Items"
    ]

    if len(topics) < 5:
        # Pad with default topics
        while len(topics) < 5:
            topics.append({
                "title": default_titles[len(topics)] if len(topics) < len(default_titles) else "Additional Analysis",
                "content": "Analysis pending due to insufficient data."
            })
    elif len(topics) > 5:
        # Trim to 5
        topics = topics[:5]

    return topics


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def generate_ai_summary(recommendation, user_id):
    """
    Generate a concise executive summary from the AI recommendation.

    Args:
        recommendation: Either a dict with structured recommendation or plain text
        user_id: User ID for model selection

    Returns:
        str: Concise executive summary (max 200 characters)
    """
    print(f"Generating AI summary for user {user_id}...")

    try:
        # Get user's selected LLM
        llm = _get_user_llm(user_id)

        # Format recommendation for summary generation
        if isinstance(recommendation, dict):
            # Convert structured recommendation to readable text
            recommendation_text = f"{recommendation.get('decision', '')}\n\n"
            for topic in recommendation.get('topics', []):
                recommendation_text += f"{topic.get('title', '')}: {topic.get('content', '')}\n"
            recommendation = recommendation_text

        system_prompt = """You are an expert at creating concise, actionable executive summaries for A/B test results.

YOUR TASK:
Extract and summarize the most critical information from the detailed recommendation into a brief, scannable format.

OUTPUT REQUIREMENTS:
- Maximum 200 characters
- Start with the clear decision (Roll out / Keep / Continue testing)
- Include the key metric and percentage change
- Mention statistical significance status
- Use clear, direct language
- No fluff or filler words

FORMAT PATTERN:
"[Decision]: [Metric] [changed by X%] ([old] → [new]). [Significance status with p-value]."

EXAMPLES:
"Roll out Variant B: Conversion rate increased by 15.3% (3.2% → 3.7%). Statistically significant (p=0.012)."
"Keep Variant A: No significant difference detected (p=0.324). Variant B showed only 2.1% improvement."
"Continue testing: Early positive signal (+8.7%) but not yet significant (p=0.089). Need more data."
"""

        user_prompt = f"""Create a concise executive summary from this recommendation:

{recommendation}

Summary:"""

        # Use unified LangChain interface
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        print("AI summary generated!")
        return response.content

    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return "Error generating summary. Please try again."


def generate_test_description(test_name, user_id):
    """
    Generate an AB test description based on the test name using AI.

    Args:
        test_name: The name of the AB test
        user_id: User ID for model selection

    Returns:
        A concise description of the test
    """
    print(f"Generating description for test: {test_name} (user {user_id})")

    try:
        # Get user's selected LLM
        llm = _get_user_llm(user_id)

        system_prompt = """You are an AB Testing assistant that helps create clear and concise test descriptions.

    RULES:
    - Generate a 1-2 sentence description based on the test name
    - Focus on what is being tested and why
    - Keep it professional and actionable
    - Maximum 200 characters
    - Do not include special formatting or quotes

    EXAMPLE:
    Test Name: "Checkout Button Color"
    Description: Testing the impact of button color on checkout completion rates. Comparing blue vs green CTA button to optimize conversions.
    """

        user_prompt = f"""Generate a clear description for an AB test with this name: {test_name}"""

        # Use unified LangChain interface
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        print("Test description generated!")
        return response.content

    except Exception as e:
        print(f"Error generating description: {str(e)}")
        return f"Testing {test_name} to optimize conversion rates."
