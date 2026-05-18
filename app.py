import streamlit as st
from PyPDF2 import PdfReader
import nltk
from collections import Counter
import re
import pdfplumber
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# Download tokenizer
nltk.download('punkt')
nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize

# Page settings
st.set_page_config(
    page_title="AI Exam Notes Generator",
    page_icon="📚",
    layout="wide"
)

# Title
st.title("📚 AI Exam Notes Generator")
st.write("Upload your PDF notes and generate smart summaries.")



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

# Main app
if uploaded_file is not None:

    st.success("PDF uploaded successfully!")

    with st.spinner("Extracting text..."):

        extracted_text = extract_text(uploaded_file)

    st.subheader("📄 Extracted Text")

    st.text_area(
        "Text",
        extracted_text[:3000],
        height=250
    )
if st.button("Generate AI Notes"):

        with st.spinner("Generating summary..."):

            input_text = extracted_text[:2000]

            summary = generate_summary(input_text)

            st.subheader("🧠 AI Summary")
            st.success(summary)

            st.subheader("🔑 Important Keywords")

            keywords = extract_keywords(extracted_text)

            for word, freq in keywords:
                st.write(f"• {word} ({freq} times)")

            st.subheader("❓ Quiz Questions")

            quiz_questions = generate_quiz_questions(
                extracted_text
            )

            for i, question in enumerate(
                quiz_questions,
                start=1
            ):
                st.write(f"Q{i}. {question}?")

            st.subheader("📝 Quick Revision Points")

            sentences = extracted_text.split('.')

            valid_sentences = []

            for sentence in sentences:

                if len(sentence.strip()) > 20:
                    valid_sentences.append(sentence)

            for sentence in valid_sentences[:5]:

                st.write(
                    f"✅ {sentence.strip()}"
                )