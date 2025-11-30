import math
from scipy.stats import norm, fisher_exact, chi2_contingency

def two_proportion_z_test(imp_a, conv_a, imp_b, conv_b, alpha=0.05):
    # conversion rates
    conv_rate_a = conv_a / imp_a
    conv_rate_b = conv_b / imp_b

    # quick check for small counts -> uvariability Fisher's exact test
    if min(conv_a, conv_b, imp_a-conv_a, imp_b-conv_b) < 5:
        # build contingency table for Fisher's exact test
        table = [[conv_a, imp_a - conv_a],
                 [conv_b, imp_b - conv_b]]
        oddsratio, p = fisher_exact(table, alternative='two-sided')
        return {
            "conv_rate_a": conv_rate_a,
            "conv_rate_b": conv_rate_b,
            "sample_size_a": imp_a,
            "sample_size_b": imp_b,
            "conversions_a": conv_a,
            "conversions_b": conv_b,
            "p_value": p,
            "method": "fisher_exact",
            "significant": p < alpha,
            "difference": conv_rate_b - conv_rate_a
        }

    # pooled proportion
    p_pool = (conv_a + conv_b) / (imp_a + imp_b)
    variability = math.sqrt(p_pool * (1 - p_pool) * (1 / imp_a + 1 / imp_b))
    standard_deviation = (conv_rate_b - conv_rate_a) / variability
    p_value = 2 * (1 - norm.cdf(abs(standard_deviation)))

    # non-pooled variability for CI
    variability_diff = math.sqrt(conv_rate_a * (1 - conv_rate_a) / imp_a + conv_rate_b * (1 - conv_rate_b) / imp_b)
    standard_deviation975 = norm.ppf(0.975)
    ci_low = (conv_rate_b - conv_rate_a) - standard_deviation975 * variability_diff
    ci_high = (conv_rate_b - conv_rate_a) + standard_deviation975 * variability_diff

    return {
        "conv_rate_a": conv_rate_a,
        "conv_rate_b": conv_rate_b,
        "sample_size_a": imp_a,
        "sample_size_b": imp_b,
        "conversions_a": conv_a,
        "conversions_b": conv_b,
        "difference": conv_rate_b - conv_rate_a,
        "p_value": float(p_value),
        "standard_deviation": standard_deviation,
        "variability": variability,
        "ci_95": (float(ci_low), float(ci_high)),
        "method": "two_proportion_z_test",
        "significant": float(p_value) < alpha
    }


def calculate_increase_percent(conv_rate_a, conv_rate_b):
    """
    Calculate the percentage increase from variant A to variant B.

    Args:
        conv_rate_a: Conversion rate of variant A (as a decimal, e.g., 0.05 for 5%)
        conv_rate_b: Conversion rate of variant B (as a decimal, e.g., 0.06 for 6%)

    Returns:
        The percentage increase (or decrease if negative) as a float.
        Returns 0 if conv_rate_a is 0 to avoid division by zero.
    """
    if conv_rate_a == 0:
        return 0.0

    increase = ((conv_rate_b - conv_rate_a) / conv_rate_a) * 100
    return round(increase, 2)


def transform_test_data(test, variants, report):
    """
    Transform test data into a formatted string representation.

    Args:
        test: The AB test object
        variants: List of variant objects (should have exactly 2 variants)
        report: The statistical report data dictionary

    Returns:
        Formatted string with test details, variant data, and statistical report
    """
    if len(variants) < 2:
        return "Error: Test must have at least 2 variants"

    # Extract variant data
    variant_a = variants[0]
    variant_b = variants[1]

    # Build formatted string with proper alignment
    string = f"""
TEST DETAILS:
Name: {test.name}
Description: {test.description if test.description else 'No description provided'}
Primary Metric: {test.metric}

VARIANT A (Control):
- Sample Size: {variant_a.impressions:,}
- Conversions: {variant_a.conversions:,}
- Conversion Rate: {variant_a.conversion_rate:.2%}

VARIANT B (Treatment):
- Sample Size: {variant_b.impressions:,}
- Conversions: {variant_b.conversions:,}
- Conversion Rate: {variant_b.conversion_rate:.2%}

STATISTICAL REPORT:
{report}
"""

    return string
