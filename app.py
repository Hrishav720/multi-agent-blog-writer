from __future__ import annotations

import json
import os
import re
import zipfile
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional, List, Iterator, Tuple

import pandas as pd
import streamlit as st

# 🔥 LangSmith Auto Tracing

from blog_backend import app


# -----------------------------
# PDF GENERATOR
# -----------------------------
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.lib.pagesizes import A4

def generate_pdf(md_text: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    for line in md_text.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            elements.append(Paragraph(f"<b>{line[2:]}</b>", styles["Heading1"]))
        elif line.startswith("## "):
            elements.append(Paragraph(f"<b>{line[3:]}</b>", styles["Heading2"]))
        elif line.startswith("!["):
            match = re.search(r"\((.*?)\)", line)
            if match:
                try:
                    elements.append(RLImage(match.group(1), width=400))
                except:
                    pass
        elif line:
            elements.append(Paragraph(line, styles["BodyText"]))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Multi-Agent Blog Writer",
    layout="wide",
)

# -----------------------------
# HERO HEADER
# -----------------------------
st.markdown("""
# 🧠 AI Multi-Agent Blog Writer  
Generate research-backed, image-rich, production-ready blogs.
""")

# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
with st.sidebar:
    st.header("⚙️ Blog Settings")

    topic = st.text_area("Blog Topic", height=120)

    col1, col2 = st.columns(2)
    with col1:
        as_of = st.date_input("As-of date", value=date.today())
    with col2:
        temperature = st.slider("Creativity", 0.0, 1.0, 0.3)

    show_logs = st.toggle("Show Debug Logs", value=False)

    run_btn = st.button("🚀 Generate Blog", type="primary")

# -----------------------------
# STATE
# -----------------------------
if "last_out" not in st.session_state:
    st.session_state["last_out"] = None

# -----------------------------
# TABS
# -----------------------------
tab_plan, tab_preview, tab_assets, tab_logs = st.tabs(
    ["🧩 Plan", "📝 Blog Preview", "📦 Assets", "📊 Logs"]
)

# -----------------------------
# RUN GRAPH
# -----------------------------
if run_btn:
    if not topic.strip():
        st.warning("Enter a topic.")
        st.stop()

    inputs: Dict[str, Any] = {
        "topic": topic.strip(),
        "mode": "",
        "needs_research": False,
        "queries": [],
        "evidence": [],
        "plan": None,
        "as_of": as_of.isoformat(),
        "recency_days": 7,
        "sections": [],
        "merged_md": "",
        "md_with_placeholders": "",
        "image_specs": [],
        "final": "",
    }

    with st.status("Running Multi-Agent Graph...", expanded=True) as status:

        progress = st.empty()
        current_state: Dict[str, Any] = {}

        for step in app.stream(inputs, stream_mode="updates"):
            progress.json(step)

        out = app.invoke(inputs)
        st.session_state["last_out"] = out

        status.update(label="✅ Blog Generated", state="complete")

# -----------------------------
# DISPLAY OUTPUT
# -----------------------------
out = st.session_state.get("last_out")

if out:

    final_md = out.get("final", "")
    plan = out.get("plan")
    image_specs = out.get("image_specs", [])

    # ---------------- PLAN TAB ----------------
    with tab_plan:
        if plan:
            if hasattr(plan, "model_dump"):
                plan = plan.model_dump()
            st.write("### Blog Title")
            st.success(plan.get("blog_title", ""))

            st.write("### Structure")
            df = pd.DataFrame(plan.get("tasks", []))
            st.dataframe(df, use_container_width=True)

    # ---------------- PREVIEW TAB ----------------
    with tab_preview:
        if final_md:
            st.markdown(final_md)

            blog_title = (
                plan.get("blog_title")
                if isinstance(plan, dict)
                else "blog"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.download_button(
                    "⬇️ Markdown",
                    data=final_md.encode(),
                    file_name=f"{blog_title}.md",
                    mime="text/markdown",
                )

            with col2:
                pdf_bytes = generate_pdf(final_md)
                st.download_button(
                    "📄 Download PDF",
                    data=pdf_bytes,
                    file_name=f"{blog_title}.pdf",
                    mime="application/pdf",
                )

            with col3:
                st.metric("Sections", len(plan.get("tasks", [])) if plan else 0)

    # ---------------- ASSETS TAB ----------------
    with tab_assets:
        if image_specs:
            st.write("### Generated Images")
            for spec in image_specs:
                filename = spec.get("filename")
                img_path = Path("images") / filename
                if img_path.exists():
                    st.image(str(img_path), use_container_width=True)

    # ---------------- LOGS TAB ----------------
    with tab_logs:
        if show_logs:
            st.json(out)
        else:
            st.info("Enable 'Show Debug Logs' in sidebar.")