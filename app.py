import os
import json
import streamlit as st

from src.pipeline import run_pipeline

st.set_page_config(page_title="AI Job Search Agent", layout="wide")
st.title("AI Job Search Agent")
st.caption("Search → Filter → Rank → Tailor (Top 3)")

with st.sidebar:
    st.header("Controls")
    query = st.text_input("Job query", "AI Engineer")
    search_location = st.text_input("Search location (for Google Jobs)", "United States")
    location_pref = st.text_input("Preferred location (ranking boost)", "Texas")
    days_recent = st.slider("Recency window (days)", 1, 60, 30)
    max_results = st.slider("Max jobs to pull", 10, 100, 30)

    st.subheader("Filters")
    exclude_faang = st.checkbox("Exclude FAANG (required)", True)
    exclude_startups = st.checkbox("Exclude startups <50 (heuristic)", True)

    st.subheader("Tailoring")
    enable_tailoring = st.checkbox("Generate tailored resume + cover letter", True)

    run_btn = st.button("Run Agent", type="primary")

if run_btn:
    if enable_tailoring and not os.getenv("OPENAI_API_KEY"):
        st.error("Missing OPENAI_API_KEY in environment/secrets.")
        st.stop()
    if not os.getenv("SERPAPI_API_KEY"):
        st.error("Missing SERPAPI_API_KEY in environment/secrets.")
        st.stop()

    with st.spinner("Running pipeline..."):
        result = run_pipeline(
            query=query,
            max_results=max_results,
            location_pref=location_pref,
            days_recent=days_recent,
            exclude_faang=exclude_faang,
            exclude_startups=exclude_startups,
            enable_tailoring=enable_tailoring,
            search_location=search_location
        )

    st.success(f"Run complete: {result['run_id']}")

    t1, t2, t3, t4 = st.tabs(["Top 10 Ranked", "Raw", "Filtered", "Trace/Logs"])

    with t1:
        st.dataframe(result["ranked_top10"], use_container_width=True)

        st.markdown("## Tailored Applications (Top 3)")
        for app in result["applications"]:
            st.markdown(f"### {app['job_title']} — {app['company']}")
            st.write(app["location"])
            st.write(app["url"])

            with st.expander("Resume (Markdown)"):
                st.code(app["resume_md"], language="markdown")
                st.download_button(
                    "Download Resume.md",
                    app["resume_md"].encode("utf-8"),
                    file_name=f"{result['run_id']}_{app['company']}_resume.md".replace(" ", "_"),
                    mime="text/markdown",
                )

            with st.expander("Cover Letter (Markdown)"):
                st.code(app["cover_letter_md"], language="markdown")
                st.download_button(
                    "Download CoverLetter.md",
                    app["cover_letter_md"].encode("utf-8"),
                    file_name=f"{result['run_id']}_{app['company']}_cover_letter.md".replace(" ", "_"),
                    mime="text/markdown",
                )

    with t2:
        st.dataframe(result["raw_jobs"], use_container_width=True)

    with t3:
        st.dataframe(result["filtered_jobs"], use_container_width=True)

    with t4:
        st.json(result["trace"])
        st.download_button(
            "Download trace.json",
            json.dumps(result["trace"], indent=2).encode("utf-8"),
            file_name=f"{result['run_id']}_trace.json",
            mime="application/json",
        )
