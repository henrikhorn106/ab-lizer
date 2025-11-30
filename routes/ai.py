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

    system_prompt = \
        f"""You are a Conversion Rate Optimization AI assistant.
        You're working for the following company:
        {company_data}
        
        This is the report for the test:
        {report_data}

        RULES:
        - Always give only the recommendation
        - Explain, why you made the decision
        - Explain the user experience impact
        - Suggest if the test variant should get rolled out or not
        - Use simple language


        EXAMPLE:
        Variant B should get rolled out. Variant B has a higher conversion rate (0.35% vs 0.20%), 
        an absolute uplift of 0.0015 (0.15 percentage points). 
        The two-proportion z-test returns p = 0.0428 (< 0.05), 
        and the 95% confidence interval for the uplift (0.0000486, 0.0029514) 
        is entirely positive, so the result is statistically 
        significant and the effect is estimated to be above zero. 
        The z-statistic (~2.025) and low variability support the 
        reliability of this result. Suggestion: Yes, 
        Variant B should be rolled out.
        """

    user_prompt = \
        f"""Give me a recommendation for the following test:
        {test_data}
        """


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
    system_prompt = \
        f"""You are a Summery AI assistant.

            RULES:
            - Give a short summary of the recommendation
            - 500 characters max
            
            EXAMPLE:
            Variant B showed a 26.6% increase in CTR (6.33% vs 5.0%). The result is statistically significant with p-value = 0.032.
        """

    user_prompt = \
        f"""Generate a summary of the following recommendation:
        {recommendation}"""

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