import streamlit as st
import requests

API_URL="http://127.0.0.1:8001"

st.set_page_config(page_title="AI Resume Analyzer",layout="wide")
st.title("AI Resume Analyzer")
st.caption("Paste your resume and a job description to get an instant AI analysis")

col1,col2=st.columns(2)
with col1:
    resume=st.text_area("Your resume",height=300,
                        placeholder="Paste your full resume here...")
with col2:
    job_desc=st.text_area("Job description",height=300,
                          placeholder="Paste the job description here...")
    
if st.button("Analyze my resume", type="primary"):
    if not resume or not job_desc:
        st.error("Please paste both your resume and the job description.")
    else:
        with st.spinner("Analyzing your resume..."):
            try:
                response=requests.post(f"{API_URL}/analyze",
                                       json={"resume": resume,"job_description":job_desc})
                data=response.json()
                
                if "error" in data:
                    st.error(f"Analysis error: {data['error']}")
                else:
                    score=data.get("match_score",0)
                    label=data.get("score_label","")
                    
                    st.markdown("---")
                    m1,m2,m3=st.columns(3)
                    m1.metric("Match score",f"{score}/100")
                    m2.metric("Likelihood",data.get("interview_likelihood","").title())
                    m3.metric("Verdict",label)
                    
                    st.info(data.get("summary",""))
                    
                    c1,c2=st.columns(2)
                    with c1:
                        st.subheader("Strengths")
                        for s in data.get("strengths",[]):
                            st.success(s)
                        st.subheader("Missing keywords")
                        for k in data.get("missing_keywords",[]):
                            st.code(k)
                    
                    with c2:
                        st.subheader("Gaps")
                        for g in data.get("gaps",[]):
                            st.warning(g)
                        st.subheader("How to improve")
                        for i,tip in enumerate(data.get("improvements",[]),1):
                            st.write(f"{i}. {tip}")
            except Exception as e:
                st.error(f"Could not connect to API: {e}")