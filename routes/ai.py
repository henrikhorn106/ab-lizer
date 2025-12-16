from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI


# Load .env file
load_dotenv()

# Access API key and start client
api_keys = os.environ.get('OPENAI_API_KEY')
client = OpenAI()

# Initialize LangChain OpenAI client for structured outputs
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


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
        description="Exactly 5 topics covering different aspects of the recommendation",
        min_items=5,
        max_items=5
    )

    class Config:
        json_schema_extra = {
            "example": {
                "decision": "Roll out Variant B",
                "topics": [
                    {
                        "title": "Statistical Significance & Confidence",
                        "content": "The test achieved statistical significance with p=0.023..."
                    }
                ]
            }
        }


# ================================================================
# LANGGRAPH STATE AND WORKFLOW
# ================================================================

class RecommendationState(TypedDict):
    """State for the recommendation generation workflow"""
    test_data: dict
    report_data: dict
    company_data: dict
    system_prompt: str
    user_prompt: str
    recommendation: dict | None
    error: str | None


def prepare_prompts(state: RecommendationState) -> RecommendationState:
    """Node: Prepare system and user prompts"""
    company_data = state["company_data"]
    test_data = state["test_data"]
    report_data = state["report_data"]

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
P-value: {report_data.get('p_value', 'N/A'):.4f}
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

    state["system_prompt"] = system_prompt
    state["user_prompt"] = user_prompt
    return state


def generate_recommendation(state: RecommendationState) -> RecommendationState:
    """Node: Generate AI recommendation using structured output"""
    try:
        print("Generating AI recommendation with LangGraph...")

        # Use structured output with Pydantic model
        llm_with_structure = llm.with_structured_output(AIRecommendation)

        # Generate recommendation
        response = llm_with_structure.invoke([
            {"role": "system", "content": state["system_prompt"]},
            {"role": "user", "content": state["user_prompt"]}
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

        state["recommendation"] = recommendation_dict
        state["error"] = None
        print("AI recommendation generated successfully!")

    except Exception as e:
        print(f"Error generating recommendation: {str(e)}")
        state["error"] = str(e)
        # Fallback recommendation
        state["recommendation"] = {
            "decision": "Error generating recommendation",
            "topics": [
                {
                    "title": "Error",
                    "content": f"Failed to generate recommendation: {str(e)}"
                }
            ]
        }

    return state


def validate_recommendation(state: RecommendationState) -> RecommendationState:
    """Node: Validate that recommendation has required structure"""
    recommendation = state.get("recommendation")

    if not recommendation:
        state["error"] = "No recommendation generated"
        return state

    # Validate structure
    if "decision" not in recommendation:
        state["error"] = "Missing decision field"
    elif "topics" not in recommendation:
        state["error"] = "Missing topics field"
    elif len(recommendation.get("topics", [])) != 5:
        # If we don't have exactly 5 topics, pad or trim
        topics = recommendation.get("topics", [])
        if len(topics) < 5:
            # Pad with empty topics
            default_titles = [
                "Statistical Significance & Confidence",
                "Business Impact Assessment",
                "Sample Size & Data Quality",
                "Risk Factors & Considerations",
                "Next Steps & Action Items"
            ]
            while len(topics) < 5:
                topics.append({
                    "title": default_titles[len(topics)] if len(topics) < len(default_titles) else "Additional Analysis",
                    "content": "Analysis pending."
                })
        else:
            # Trim to 5
            topics = topics[:5]
        recommendation["topics"] = topics

    return state


# Build the LangGraph workflow
workflow = StateGraph(RecommendationState)

# Add nodes
workflow.add_node("prepare_prompts", prepare_prompts)
workflow.add_node("generate_recommendation", generate_recommendation)
workflow.add_node("validate_recommendation", validate_recommendation)

# Add edges
workflow.set_entry_point("prepare_prompts")
workflow.add_edge("prepare_prompts", "generate_recommendation")
workflow.add_edge("generate_recommendation", "validate_recommendation")
workflow.add_edge("validate_recommendation", END)

# Compile the graph
recommendation_graph = workflow.compile()


# ================================================================
# MAIN FUNCTION (Updated with LangGraph)
# ================================================================

def generate_ai_recommendation(test_data, report_data, company_data):
    """
    Generate AI recommendation using LangGraph workflow and structured outputs.

    Args:
        test_data: AB test data object
        report_data: Statistical report data dict
        company_data: Company context data dict

    Returns:
        dict: Structured recommendation with decision and 5 topics
    """
    # Prepare initial state
    initial_state = {
        "test_data": test_data,
        "report_data": report_data,
        "company_data": company_data,
        "system_prompt": "",
        "user_prompt": "",
        "recommendation": None,
        "error": None
    }

    # Run the workflow
    final_state = recommendation_graph.invoke(initial_state)

    # Return the recommendation
    return final_state["recommendation"]


# ================================================================
# HELPER FUNCTIONS (Unchanged)
# ================================================================

def generate_ai_summary(recommendation):
    """
    Generate a concise executive summary from the AI recommendation.

    Args:
        recommendation: Either a dict with structured recommendation or plain text

    Returns:
        str: Concise executive summary (max 200 characters)
    """
    print("Generating AI summary...")

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

    response = client.responses.parse(
        model="gpt-5-mini",
        input=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt
            },
        ]
    )

    print("AI summary generated!")

    return response.output_text


def generate_test_description(test_name):
    """
    Generate an AB test description based on the test name using AI.

    Args:
        test_name: The name of the AB test

    Returns:
        A concise description of the test
    """
    print(f"Generating description for test: {test_name}")

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

    response = client.responses.parse(
        model="gpt-5-mini",
        input=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt
            },
        ]
    )

    print("Test description generated!")

    return response.output_text
