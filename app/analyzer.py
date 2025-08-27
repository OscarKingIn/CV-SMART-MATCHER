import re
import time
from openai import OpenAI, OpenAIError
from app import config

# LAUNCH OPENAI CLIENT

client = OpenAI(api_key=config.OPENAI_API_KEY)

# ---------------------------------------
# MAKE LLM REQUEST WITH AUTOMATIC RETRIES
# ---------------------------------------


def llm_request(system_prompt, user_prompt, retries=5, backoff=5):
    for attempt in range(1, retries + 1):
        try:
            resp = client.chat.completions.create(
                model=config.MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return resp
        except OpenAIError as e:
            # RETRY EXCLUSIVELY ON RATE LIMIT ERRORS
            if "Rate limit" in str(e):
                time.sleep(backoff)
                backoff *= 2
            else:
                return {"error": str(e)}
    return {"error": "Rate limit exceeded after retries."}

# ----------------------------------------
# EXTRACT MISSING JOB DESCRIPTION KEYWORDS
# ----------------------------------------
def extract_missing_keywords(cv_text, jd_text):
    jd_words = set(re.findall(r"\b\w+\b", jd_text.lower()))
    resume_words = set(re.findall(r"\b\w+\b", cv_text.lower()))
    missing = jd_words - resume_words
    return sorted(list(missing))

# -------------------------
# FIT SCORE CALCULATION
# -------------------------
def calculate_fit_score(cv_text, jd_text):
    jd_words = set(re.findall(r"\b\w+\b", jd_text.lower()))
    resume_words = set(re.findall(r"\b\w+\b", cv_text.lower()))
    if not jd_words:
        return 0
    matched = jd_words & resume_words
    return int(len(matched) / len(jd_words) * 100)

# -------------------------
# ANALYZE SINGLE CV
# -------------------------
def analyze_resume_against_jd(cv_text, jd_text):
    missing_keywords = extract_missing_keywords(cv_text, jd_text)
    fit_score = calculate_fit_score(cv_text, jd_text)

    SYSTEM_PROMPT = "You are an expert HR AI. Analyze resumes objectively."
    user_prompt = f"""Resume:
{cv_text}

Job Description:
{jd_text}

Provide a summary of fit, strengths, weaknesses, and suggestions for improvement."""

    llm_result = llm_request(SYSTEM_PROMPT, user_prompt)

    if "error" in llm_result:
        analysis_text = f"Error: {llm_result['error']}"
    else:
        try:
            analysis_text = llm_result.choices[0].message.content
        except (KeyError, IndexError, AttributeError):
            analysis_text = "Error: Unexpected response from LLM."

    return {
        "missing_keywords": missing_keywords,
        "fit_score": fit_score,
        "analysis": analysis_text
    }

# -------------------------
# ANALYZE MULTIPLE RESUMES & RANK
# -------------------------
def analyze_multiple_cv(resume_list, jd_text):
    results = []
    for idx, resume_text in enumerate(resume_list, start=1):
        result = analyze_resume_against_jd(resume_text, jd_text)
        result["resume_index"] = idx
        results.append(result)
    # SORT BY FIT SCORE DESCENDING
    results.sort(key=lambda x: x["fit_score"], reverse=True)
    return results
