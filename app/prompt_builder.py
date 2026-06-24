# ============================================================
#  app/prompt_builder.py — Prompt Construction Logic
#
#  This file is the brain of the application.
#  It takes the user's input + category and returns a
#  professional, structured AI prompt string.
#
#  FUTURE (Phase 2): This file will be updated to send the
#  prompt to the Gemini API and return a real AI response.
# ============================================================


def build_prompt(user_input, category):
    """
    Builds a professional AI prompt based on user input and category.

    Parameters:
        user_input (str) → the goal/task the user entered
        category   (str) → one of: Coding, Study, Resume,
                            Content Writing, Business, General

    Returns:
        str → a ready-to-use AI prompt
    """

    # Each category has a professional template.
    # {user_input} is replaced with the actual user text.
    templates = {

        'Coding': (
            f"Act as a senior software engineer and expert programmer. "
            f"Help me with the following task:\n\n\"{user_input}\"\n\n"
            f"Please provide:\n"
            f"1. Clean, well-commented code\n"
            f"2. A step-by-step explanation of how the code works\n"
            f"3. Best practices and potential improvements\n"
            f"4. How to test the solution"
        ),

        'Study': (
            f"Act as an expert tutor and educator. "
            f"Help me understand the following topic:\n\n\"{user_input}\"\n\n"
            f"Please provide:\n"
            f"1. A clear, simple explanation using plain language\n"
            f"2. Real-world examples and analogies\n"
            f"3. Common misconceptions to avoid\n"
            f"4. A concise summary\n"
            f"5. Three practice questions to test understanding"
        ),

        'Resume': (
            f"Act as a professional resume coach and HR expert. "
            f"Help me with the following:\n\n\"{user_input}\"\n\n"
            f"Please ensure:\n"
            f"1. ATS-friendly formatting and keywords\n"
            f"2. Strong action verbs (e.g., Led, Built, Increased, Designed)\n"
            f"3. Quantified achievements where possible (e.g., Reduced load time by 40%)\n"
            f"4. Clear, concise, and professional language\n"
            f"5. Tailored to the target role or industry"
        ),

        'Content Writing': (
            f"Act as a professional content writer and SEO strategist. "
            f"Help me create the following:\n\n\"{user_input}\"\n\n"
            f"Please ensure the content:\n"
            f"1. Starts with a compelling hook or headline\n"
            f"2. Is well-structured with clear headings and subheadings\n"
            f"3. Is SEO-optimized with natural keyword usage\n"
            f"4. Maintains an engaging and appropriate tone\n"
            f"5. Ends with a strong call-to-action"
        ),

        'Business': (
            f"Act as a senior business strategist and consultant. "
            f"Help me with the following business challenge:\n\n\"{user_input}\"\n\n"
            f"Please provide:\n"
            f"1. A clear analysis of the situation\n"
            f"2. Actionable, step-by-step recommendations\n"
            f"3. Key risks to consider and how to mitigate them\n"
            f"4. Suggested KPIs to measure success\n"
            f"5. Professional, concise language suitable for stakeholders"
        ),

        'General': (
            f"You are a highly knowledgeable and helpful AI assistant. "
            f"Please help me with the following:\n\n\"{user_input}\"\n\n"
            f"Please:\n"
            f"1. Be clear, thorough, and well-organized\n"
            f"2. Break down complex points into simple steps\n"
            f"3. Provide practical, actionable insights\n"
            f"4. Use examples where helpful\n"
            f"5. Summarize the key points at the end"
        ),
    }

    # Look up the template for the given category.
    # If the category is not found, fall back to 'General'.
    return templates.get(category, templates['General'])
