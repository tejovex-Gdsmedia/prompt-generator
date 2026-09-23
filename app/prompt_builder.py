# ============================================================
#  app/prompt_builder.py — Prompt Construction & Gemini AI Logic
# ============================================================

import os
import google.generativeai as genai


def generate_prompt(user_task, category):
    """
    Generates a structured, professional AI prompt using Google Gemini API.
    Falls back to deterministic template generation if no API key is set or on error.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        # Fallback to template if no API key
        return generate_template_prompt(user_task, category)
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        category_instructions = {
            "coding": "senior software engineer - clean code, test cases, edge cases, comments",
            "study": "expert educator - key concepts, analogies, summary, 3 quiz questions",
            "resume": "resume coach - action verbs, metrics, ATS keywords, achievements",
            "content": "content strategist - hook, structure, SEO, strong CTA",
            "content writing": "content strategist - hook, structure, SEO, strong CTA",
            "business": "business consultant - executive summary, KPIs, risk analysis",
            "general": "helpful AI assistant - clear, structured, high-quality output"
        }
        
        cat_key = (category or "general").strip().lower()
        role = category_instructions.get(cat_key, category_instructions["general"])
        
        meta_prompt = f"""
You are a {role}.

User's raw idea: "{user_task}"

Transform this into a powerful, structured AI prompt that includes:
1. A clear role/persona for the AI
2. The exact task with full context
3. Expected output format
4. Quality constraints and tone guidelines
5. Any relevant examples or constraints

Return ONLY the final engineered prompt. No explanations. No preamble.
"""
        response = model.generate_content(meta_prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Gemini API error (falling back to template): {e}")
        return generate_template_prompt(user_task, category)


def generate_template_prompt(user_task, category):
    """
    Fallback prompt builder providing high-quality static templates.
    """
    templates = {
        "coding": f"You are a senior software engineer. Task: {user_task}. Provide clean, well-commented code with step-by-step explanation, edge case handling, and test cases.",
        "study": f"You are an expert educator. Explain: {user_task}. Include key concepts, real-world analogy, bullet-point summary, and 3 practice questions.",
        "resume": f"You are a resume expert. Create content for: {user_task}. Use action verbs, quantifiable metrics, and ATS-friendly keywords.",
        "content": f"You are a content strategist. Write about: {user_task}. Include attention hook, clear structure, SEO keywords, and strong CTA.",
        "content writing": f"You are a content strategist. Write about: {user_task}. Include attention hook, clear structure, SEO keywords, and strong CTA.",
        "business": f"You are a business consultant. Analyze: {user_task}. Provide executive summary, key metrics, risks, and recommendations.",
        "general": f"You are a helpful AI assistant. Help with: {user_task}. Be clear, structured, and thorough."
    }
    cat_key = (category or "general").strip().lower()
    return templates.get(cat_key, templates["general"])


# Backwards compatibility alias if called elsewhere
build_prompt = generate_prompt
