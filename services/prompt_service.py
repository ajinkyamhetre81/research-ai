# services/prompt_service.py

from typing import Dict, Any


class PromptService:
    """Service class for creating structured prompts for LLM processing."""
    
 
    @staticmethod
    def create_test_prompt() -> str:
        """Create simple test prompt for connection testing."""
        return "Hello! Please respond with 'API connection successful!'"

    @staticmethod
    def create_college_faculty_extraction_prompt(raw_data: str) -> str:
        return f"""
    You are a STRICT INFORMATION EXTRACTION ENGINE.

    Your task:
    Extract ONLY explicitly stated academic institution and faculty information from the provided text.

    CRITICAL RULES:
    1. DO NOT infer or guess any information.
    2. DO NOT complete partial emails.
    3. DO NOT assume subjects from department names.
    4. If information is not explicitly written in the text, return "NA".
    5. Do NOT hallucinate missing contact details.
    6. Only extract information that appears clearly and directly in the text.
    7. If uncertain, return "NA".
    8. Return ONLY valid raw JSON.
    9. Do NOT include explanations or markdown.
    10. If no faculty information is found, return empty arrays.

    Text Content:
    {raw_data}

    Return JSON in this EXACT structure:

    {{
    "institution": {{
        "college_name": "string or NA",
        "website": "string or NA",
        "address": "string or NA",
        "contact_email": "string or NA",
        "contact_phone": "string or NA"
    }},
    "departments": [
        {{
        "department_name": "string or NA",
        "department_email": "string or NA",
        "department_phone": "string or NA",
        "faculty_members": [
            {{
            "full_name": "string or NA",
            "designation": "string or NA",
            "subjects_taught": ["subject1", "subject2"] or [],
            "email": "string or NA",
            "phone": "string or NA",
            "office_address": "string or NA",
            "profile_url": "string or NA"
            }}
        ]
        }}
    ],
    "extraction_metadata": {{
        "faculty_count": integer,
        "department_count": integer,
        "confidence_level": "high/medium/low"
    }}
    }}

    Confidence Rules:
    - HIGH: Information clearly structured and explicitly listed.
    - MEDIUM: Information found but scattered.
    - LOW: Very limited or unclear information.

    Return ONLY raw JSON.
    """
