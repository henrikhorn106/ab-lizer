from openai import OpenAI
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access API key and start client
api_keys = os.environ.get('OPENAI_API_KEY')
client = OpenAI()


# noinspection PyTypeChecker
def generate_ai_recommendation(data):
    response = client.responses.parse(
        model="gpt-5-mini",
        input=[
            {
                "role": "system",
                "content": """You are a Conversion Rate Optimization AI assistant.
                
                RULES:
                1. Always give only the recommendation
                2. Explain, why you made the decision
                3. Suggest if the test variant should get rolled out or not
                4. Use simple language
                
                EXAMPLE:
                Variant B should get rolled out.
                Variant B has a higher conversion rate (0.35% vs 0.20%), 
                an absolute uplift of 0.0015 (0.15 percentage points). 
                The two-proportion z-test returns p = 0.0428 (< 0.05), 
                and the 95% confidence interval for the uplift (0.0000486, 0.0029514) 
                is entirely positive, so the result is statistically 
                significant and the effect is estimated to be above zero. 
                The z-statistic (~2.025) and low variability support the 
                reliability of this result. Suggestion: Yes, 
                Variant B should be rolled out.
                """,
            },
            {
                "role": "user",
                "content": f"""Give me a recommendation fot the following test:
                {data}
                """
            },
        ]
    )
    return response.output_text