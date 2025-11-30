from openai import OpenAI
from dotenv import load_dotenv
import os


# Load .env file
load_dotenv()

# Access API key and start client
api_keys = os.environ.get('OPENAI_API_KEY')
client = OpenAI()


# noinspection PyTypeChecker
def generate_ai_recommendation(test_data, report_data, company_data):
    print("Generating AI recommendation...")

    # Format statistical data clearly
    method_name = report_data.get('method', 'statistical test')
    ci_lower, ci_upper = report_data.get('ci_95', (None, None))

    system_prompt = f"""You are an expert Conversion Rate Optimization (CRO) consultant providing data-driven recommendations.

COMPANY CONTEXT:
- Company: {company_data.get('name', 'Unknown')}
- Target Audience: {company_data.get('audience', 'General')}
- Industry Context: {company_data.get('year', 'Current year')}

YOUR TASK:
Analyze the A/B test results and provide a clear, actionable recommendation. Your analysis must consider:
1. Statistical significance and confidence
2. Practical business impact
3. Sample size adequacy
4. Risk assessment
5. User experience implications

OUTPUT FORMAT:
Start with a clear decision (Roll out Variant B / Keep Variant A / Continue testing), then provide:
- Statistical evidence (p-value, confidence intervals, effect size)
- Business impact assessment (conversion lift, expected impact)
- Risk factors and considerations
- Actionable next steps

GUIDELINES:
- Use simple, clear language suitable for business stakeholders
- Highlight both the statistical and practical significance
- Consider the specific audience and industry context
- Be cautious with borderline results (p-value 0.04-0.06)
- Mention if sample size seems insufficient
- Consider the magnitude of change, not just statistical significance
- Use paragraphs and bullet points to organize your response
- Add linebreaks after each topic
- Don't use Headline style formatting
"""

    # Format test data more clearly
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

Provide your recommendation now."""

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

    print("AI recommendation generated!")

    return response.output_text


def generate_ai_summary(recommendation):
    print("Generating AI summary...")

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