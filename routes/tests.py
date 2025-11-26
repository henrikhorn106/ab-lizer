def tranform_data(test, variants, report):
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
    print(string)

    return string

