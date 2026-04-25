import streamlit as st
import json
from resume_parser import pdf_to_text, parse_resume

st.set_page_config(page_title="Resume Parser", page_icon="📄")

st.markdown("""
    <style>
        /* Background */
        body, .stApp { background-color: #ddeeff; }

        /* Title */
        h1 { color: #3b0764 !important; font-weight: 800; }

        /* Caption / small text */
        .stCaptionContainer p, .stMarkdown p { color: #2d1b4e; }

        /* Section headings */
        .section-heading {
            color: #3b0764;
            font-size: 1.1rem;
            font-weight: 700;
            margin: 18px 0 8px 0;
        }

        /* Card boxes */
        .card {
            background-color: #c8e0f8;
            border-left: 5px solid #5b21b6;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 12px;
            color: #1a0533;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        .card b { color: #3b0764; }

        /* Skill pills */
        .pill {
            display: inline-block;
            background-color: #7c3aed;
            color: #ffffff;
            border-radius: 20px;
            padding: 4px 12px;
            margin: 3px;
            font-size: 0.82rem;
            font-weight: 500;
        }

        /* File uploader */
        [data-testid="stFileUploader"] {
            background-color: #c8e0f8;
            border-radius: 10px;
            padding: 10px;
        }

        /* Spinner / info text */
        .stSpinner p { color: #3b0764; }
    </style>
""", unsafe_allow_html=True)

st.title("📄 Resume Parser")
st.caption("Upload a PDF resume and AI will extract the structured details.")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner("Reading PDF..."):
        text = pdf_to_text(uploaded_file)

    if not text.strip():
        st.warning("Could not extract text from this PDF.")
    else:
        with st.spinner("Parsing with AI..."):
            result = parse_resume(text)

        try:
            data = result if isinstance(result, dict) else json.loads(result)

            if "error" in data:
                st.error(f"Parser error: {data['error']}")
                st.text(data.get("raw", ""))
            else:
                # Row 1: Name / Email / Phone
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<div class="card"><b>👤 Name</b><br>' + str(data.get("name") or "—") + '</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="card"><b>📧 Email</b><br>' + str(data.get("email") or "—") + '</div>', unsafe_allow_html=True)
                with col3:
                    st.markdown('<div class="card"><b>📞 Phone</b><br>' + str(data.get("phone") or "—") + '</div>', unsafe_allow_html=True)

                # Skills as pills
                st.markdown('<div class="section-heading">🛠 Skills</div>', unsafe_allow_html=True)
                skills = data.get("skills", [])
                if skills:
                    pills_html = "".join(f'<span class="pill">{s}</span>' for s in skills)
                    st.markdown(f'<div class="card">{pills_html}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="card">—</div>', unsafe_allow_html=True)

                # Education
                st.markdown('<div class="section-heading">🎓 Education</div>', unsafe_allow_html=True)
                for edu in data.get("education", []):
                    st.markdown(
                        f'<div class="card"><b>{edu.get("degree") or "—"}</b><br>'
                        f'{edu.get("institution") or "—"} &nbsp;·&nbsp; {edu.get("year") or "—"}</div>',
                        unsafe_allow_html=True
                    )

                # Experience
                st.markdown('<div class="section-heading">💼 Experience</div>', unsafe_allow_html=True)
                for exp in data.get("experience", []):
                    st.markdown(
                        f'<div class="card"><b>{exp.get("title") or "—"}</b> at {exp.get("company") or "—"}'
                        f'<br>⏱ {exp.get("duration") or "—"}</div>',
                        unsafe_allow_html=True
                    )

                # Summary
                st.markdown('<div class="section-heading">📝 Summary</div>', unsafe_allow_html=True)
                st.markdown('<div class="card">' + str(data.get("summary") or "—") + '</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Could not display results: {e}")
            st.write(result)