"""
Table: ab_tests

Field	Type	Description
id	int	Primary key
name	string	Test name
description	text	Summary
metric	string	e.g. “CTR”
created_at	datetime	Timestamp

Table: variants

Field	Type	Description
id	int	Primary key
test_id	FK	Related A/B test
name	string	“Variant A”, “Variant B”
impressions	int	Views
conversions	int	Conversions
conversion_rate	float	Computed

Table: reports

Field	Type	Description
id	int	Primary key
test_id	FK	Related A/B test
summary	text	AI insight
significance	float	p-value
ai_recommendation	text	Generated recommendation
"""