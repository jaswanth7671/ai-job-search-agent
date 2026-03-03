import streamlit as st
from src.pipeline import run_pipeline

st.title("AI Job Search Agent")

query = st.text_input("Search Jobs", "AI Engineer")

if st.button("Run Agent"):

    results = run_pipeline(query)

    for r in results:

        st.subheader(r["job"]["title"])
        st.write("Company:", r["job"]["company"])
        st.write("Location:", r["job"]["location"])
        st.write("URL:", r["job"]["url"])

        st.write("Tailored Resume:")
        st.write(r["tailored_resume"])
