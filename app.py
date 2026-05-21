from fpdf import FPDF
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
import nltk
from collections import Counter
import re
import pdfplumber
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import google.generativeai as genai
import os
from dotenv import load_dotenv
import os
load_dotenv()

os.getenv("GOOGLE_API_KEY")
load_dotenv()

genai.configure(api_key="AIzaSyB72B4ukFX67QVPjK6fbZpFv8uSKZixnpw")

# Download tokenizer
nltk.download('punkt')
nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize

# Page settings
st.set_page_config(
    page_title="AI Exam Notes Generator",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)
# Custom CSS
st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.stButton>button {
    background: linear-gradient(
        90deg,
        #4B8BBE,
        #306998
    );

    color: white;

    border-radius: 12px;

    height: 3em;

    width: 100%;

    font-size: 18px;

    border: none;

    transition: 0.3s;
}

.stButton>button:hover {

    transform: scale(1.03);

    background: linear-gradient(
        90deg,
        #306998,
        #4B8BBE
    );
}

.custom-card {

    background-color: white;

    padding: 20px;

    border-radius: 20px;

    box-shadow: 0 4px 12px rgba(
        0,
        0,
        0,
        0.1
    );

    margin-bottom: 20px;
}

h1, h2, h3 {

    color: #306998;
}

@media (max-width: 768px) {

    .custom-card {

        padding: 12px;
    }

    h1 {

        font-size: 28px;
    }
}

</style>
""", unsafe_allow_html=True)
# Title
st.title("📚 AI Exam Notes Generator")
st.write("Upload your PDF notes and generate smart summaries.")
# Sidebar
st.sidebar.title("📌 Features")

st.sidebar.write("✅ PDF Upload")
st.sidebar.write("✅ AI Summary")
st.sidebar.write("✅ Important Keywords")
st.sidebar.write("✅ Quiz Questions")
st.sidebar.write("✅ Quick Revision Notes")

st.sidebar.info(
    "Built using Python & Streamlit 🚀"
)


# Upload PDF
uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)
# Extract PDF text
def extract_text(pdf_file):

    text = ""

    with pdfplumber.open(pdf_file) as pdf:

        for page in pdf.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted

    return text


# Generate summary
def generate_summary(text):

    parser = PlaintextParser.from_string(
        text,
        Tokenizer("english")
    )

    summarizer = LsaSummarizer()

    summary = summarizer(
        parser.document,
        3
    )

    final_summary = ""

    for sentence in summary:
        final_summary += str(sentence) + " "

    return final_summary


# Extract keywords
def extract_keywords(text, num_keywords=10):

    text = re.sub(r'[^a-zA-Z ]', '', text)
    text = text.lower()

    words = word_tokenize(text)

    stop_words = {
        'the', 'is', 'and', 'in',
        'to', 'of', 'a', 'for',
        'on', 'with', 'as', 'by'
    }

    filtered_words = [
        word for word in words
        if word not in stop_words and len(word) > 3
    ]

    word_freq = Counter(filtered_words)

    return word_freq.most_common(num_keywords)

# Generate quiz questions
def generate_quiz_questions(text):

    sentences = text.split('.')

    questions = []

    for sentence in sentences:

        sentence = sentence.strip()

        words = sentence.split()

        if len(words) > 5:

            question = (
                "Explain: " +
                sentence
            )

            questions.append(question)

        if len(questions) >= 5:
            break

    return questions
# Create PDF
def create_pdf(summary, keywords, quiz_questions):

    doc = SimpleDocTemplate("AI_Notes.pdf")

    styles = getSampleStyleSheet()

    content = []

    title = Paragraph(
        "<b>AI Exam Notes Generator</b>",
        styles['Title']
    )

    content.append(title)

    content.append(Spacer(1, 12))

    # Summary
    content.append(
        Paragraph("<b>AI Summary:</b>", styles['Heading2'])
    )

    content.append(
        Paragraph(summary, styles['BodyText'])
    )

    content.append(Spacer(1, 12))

    # Keywords
    content.append(
        Paragraph("<b>Important Keywords:</b>", styles['Heading2'])
    )

    keyword_text = ", ".join(
        [word for word, freq in keywords]
    )

    content.append(
        Paragraph(keyword_text, styles['BodyText'])
    )

    content.append(Spacer(1, 12))

    # Quiz Questions
    content.append(
        Paragraph("<b>Quiz Questions:</b>", styles['Heading2'])
    )

    for q in quiz_questions:

        content.append(
            Paragraph(q, styles['BodyText'])
        )

    doc.build(content)

    return "AI_Notes.pdf"

# Create PDF
def create_pdf(summary, keywords, quiz_questions):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", size=14)

    pdf.cell(
        200,
        10,
        txt="AI Exam Notes",
        ln=True,
        align='C'
    )

    pdf.ln(10)

    # Summary
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(
        0,
        10,
        txt=f"Summary:\n{summary}"
    )

    pdf.ln(5)

    # Keywords
    keyword_text = "\n".join(
        [f"{word} ({freq})" for word, freq in keywords]
    )

    pdf.multi_cell(
        0,
        10,
        txt=f"Keywords:\n{keyword_text}"
    )

    pdf.ln(5)

    # Quiz Questions
    question_text = "\n".join(quiz_questions)

    pdf.multi_cell(
        0,
        10,
        txt=f"Quiz Questions:\n{question_text}"
    )

    pdf.output("AI_Notes.pdf")
    
# Main app
if uploaded_file is not None:

    st.success("PDF uploaded successfully!")

    extracted_text = extract_text(uploaded_file)
        # Generate AI Notes Button
    if st.button("Generate AI Notes"):

        # AI Summary
        st.markdown("""
<div class="custom-card">
<h3>🧠 AI Summary</h3>
</div>
""", unsafe_allow_html=True)

        summary = generate_summary(
            extracted_text[:2000]
        )

        st.write(summary)
        st.markdown("---")

        # Keywords
        st.markdown("""
<div class="custom-card">
<h3>🔑 Important Keywords</h3>
</div>
""", unsafe_allow_html=True)
        keywords = extract_keywords(
            extracted_text
        )

        for word, freq in keywords:

            st.write(
                f"• {word} ({freq} times)"
            )
            st.markdown("---")

        # Quiz Questions
        st.markdown("""
<div class="custom-card">
<h3>❓ Quiz Questions</h3>
</div>
""", unsafe_allow_html=True)

        quiz_questions = generate_quiz_questions(
            extracted_text
        )

        for i, question in enumerate(
            quiz_questions,
            start=1
        ):

            st.write(
                f"Q{i}. {question}?"
            )
            st.markdown("---")
        # Create downloadable PDF
        create_pdf(
            summary,
            keywords,
            quiz_questions
        )

        with open(
            "AI_Notes.pdf",
            "rb"
        ) as pdf_file:

            st.download_button(
                label="⬇ Download AI Notes PDF",
                data=pdf_file,
                file_name="AI_Notes.pdf",
                mime="application/pdf"
            )

        # Quick Revision Notes
        st.markdown("""
<div class="custom-card">
<h3>📝 Quick Revision Notes</h3>
</div>
""", unsafe_allow_html=True)

        sentences = extracted_text.split('.')

        for sentence in sentences[:5]:

            if len(sentence.strip()) > 20:

                st.write(
                    f"✅ {sentence.strip()}"
                )
                st.markdown("---")

    st.subheader("📄 Extracted Text")

    st.text_area(
        "Text",
        extracted_text[:3000],
        height=250
    )

    # Chat With PDF
st.markdown("""
<div class="custom-card">
<h3>💬 Chat With PDF</h3>
</div>
""", unsafe_allow_html=True)

user_question = st.text_input(
    "Ask a question from PDF"
)

if user_question:

    gemini_model = genai.GenerativeModel(
        "models/gemini-2.5-flash"
    )

    prompt = f"""
    Answer the question only from this PDF text.

    PDF Text:
    {extracted_text[:5000]}

    Question:
    {user_question}
    """

    try:

        response = gemini_model.generate_content(
            prompt
        )

        st.success(response.text)

    except Exception as e:

        st.error(f"Error: {e}")