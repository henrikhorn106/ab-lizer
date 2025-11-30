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
        "difference": conv_rate_b - conv_rate_a,
        "p_value": float(p_value),
        "standard_deviation": standard_deviation,
        "variability": variability,
        "ci_95": (float(ci_low), float(ci_high)),
        "method": "two_proportion_z_test",
        "significant": float(p_value) < alpha
    }


def transform_test_data(test, variants, report):
    string = f"""
    Test Name: {test.name}
    Test Description: {test.description}
    Metric: {test.metric}

    Vartiant A:
    Impressions: {variants[0].impressions}
    Conversions: {variants[0].conversions}
    Conversion Rate: {variants[0].conversion_rate}

    Vartiant B:
    Impressions: {variants[1].impressions}
    Conversions: {variants[1].conversions}
    Conversion Rate: {variants[1].conversion_rate}

    Report:
    {report}
"""

    return string
