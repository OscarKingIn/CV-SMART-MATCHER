import streamlit as st
from dotenv import load_dotenv
from app.analyzer import analyze_multiple_cv
from app.parser import extract_text 
from app import config

load_dotenv()

st.set_page_config(page_title="AI SMART MATCHER", layout="wide")
st.title("📄 SMART CV MATCHER - POWERED BY AI)")
deployment = config.AZURE_OPENAI_DEPLOYMENT or config.MODEL or "N/A"
st.caption(f"Provider: {config.PROVIDER} | Model/Deployment: {deployment}")

st.markdown(
    "Upload your **CV(s)** and a **job description**. "
    "The app will parse documents, identify missing keywords, calculate fit score, and ask an LLM to analyze each resume.."
)

col1, col2 = st.columns(2)
with col1:
    candidate_doc = st.file_uploader(
        "Upload CV(s) (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"], accept_multiple_files=True
    )
with col2:
    job_d = st.file_uploader(
        "Upload Job Description (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"]
    )

api_ready = bool(config.OPENAI_API_KEY)
if not api_ready:
    st.warning("⚠️ API key not set. Only parsing and keyword analysis will be available..")

if st.button("Analyze"):
    if not (candidate_doc and job_d):
        st.error("Please upload at least one cv and a job description.")
        st.stop()

    j_ext, jd_text = extract_text(job_d.name, job_d.read())
    st.write(f":green[Job Description parsed as {j_ext}]")

    cv_text = []
    for r_file in candidate_doc:
        r_ext, r_text = extract_text(r_file.name, r_file.read())
        st.write(f":blue[Resume '{r_file.name}' parsed as {r_ext}]")
        cv_text.append(r_text)

    if api_ready:
        with st.spinner("Analyzing resumes with LLM..."):
            results = analyze_multiple_cv(cv_text, jd_text)

        st.success("Analysis complete!")

        for idx, res in enumerate(results, start=1):
            st.subheader(f"Candidate {idx} (Fit Score: {res['fit_score']}/100)")
            st.subheader("Missing JD Keywords")
            if res["missing_keywords"]:
                st.code(", ".join(res["missing_keywords"]))
            else:
                st.write("✅ All Job Description keywords found in the CV!")

            st.subheader("LLM Analysis")
            st.markdown(res["analysis"])
            st.markdown("---")
    else:
        st.info("LLM not configured. Showing missing Job Description keywords only.")
        for idx, r_text in enumerate(cv_text, start=1):
            missing_keywords = analyze_multiple_cv([r_text], jd_text)[0]["missing_keywords"]
            st.subheader(f"Resume {idx}")
            if missing_keywords:
                st.code(", ".join(missing_keywords))
            else:
                st.write("✅ All Job Description keywords found in resume!")

