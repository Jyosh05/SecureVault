import re
def input_validation(*input_strings):
    # malicious patterns
    sql_injection_patterns = [
        r"\b(SELECT|INSERT|DELETE|UPDATE|DROP|ALTER|CREATE|TRUNCATE|EXEC|UNION|--|;)\b",
        r"\b(OR|AND)\b\s*?[^\s]*?="
    ]
    javascript_pattern = r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>"
    python_script_pattern = r"\b(import|from|exec|eval|os|sys|subprocess)\b"

    # patterns combined into 1
    combined_pattern = "|".join(sql_injection_patterns) + "|" + javascript_pattern + "|" + python_script_pattern

    # compile regex patterns
    combined_regex = re.compile(combined_pattern, re.IGNORECASE)

    # for loop to iterate through the inputs and check for injection patterns
    for input_string in input_strings:
        if combined_regex.search(input_string):
            raise ValueError("Invalid input: Harmful input detected")
    return True

