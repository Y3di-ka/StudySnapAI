import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google import genai


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="StudySnap AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# COLORS
# =========================================================

ROYAL_BLUE = "#1E3A8A"
GOLD = "#F4C542"
WHITE = "#FFFFFF"
DARK_NAVY = "#0F172A"


# =========================================================
# GEMINI MODEL
# =========================================================

MODEL_NAME = "gemini-3.8-flash"


@st.cache_resource
def get_gemini_client():
    return genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )


client = get_gemini_client()


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "started" not in st.session_state:
    st.session_state.started = False

if "student_name" not in st.session_state:
    st.session_state.student_name = ""

if "language" not in st.session_state:
    st.session_state.language = "English"

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

if "uploaded_mime_type" not in st.session_state:
    st.session_state.uploaded_mime_type = "image/jpeg"


# =========================================================
# GLOBAL CSS
# =========================================================

st.html(
    f"""
    <style>

    /* =====================================================
       CLEAR BOOKSHELF BACKGROUND
       ===================================================== */

    html, body, [data-testid="stAppViewContainer"] {{
        background:
            linear-gradient(
                rgba(15, 23, 42, 0.35),
                rgba(15, 23, 42, 0.35)
            ),
            url("https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=2200&q=85")
            center center / cover fixed no-repeat;
    }}

    [data-testid="stAppViewContainer"] {{
        background-color: transparent;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}


    /* =====================================================
       MAIN CONTENT
       ===================================================== */

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }}


    /* =====================================================
       SIDEBAR
       ===================================================== */

    [data-testid="stSidebar"] {{
        background: rgba(15, 23, 42, 0.95);
        border-right: 2px solid rgba(244, 197, 66, 0.5);
    }}


    /* =====================================================
       TEXT
       ===================================================== */

    h1, h2, h3, p, label {{
        color: {WHITE} !important;
    }}


    /* =====================================================
       HERO
       ===================================================== */

    .hero {{
        background: rgba(15, 23, 42, 0.82);
        border: 2px solid rgba(244, 197, 66, 0.7);
        border-radius: 25px;
        padding: 35px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }}

    .hero-title {{
        font-size: 46px;
        font-weight: 800;
        color: {WHITE};
        margin-bottom: 8px;
    }}

    .hero-title span {{
        color: {GOLD};
    }}

    .hero-subtitle {{
        font-size: 20px;
        color: #E2E8F0;
    }}


    /* =====================================================
       FEATURE CARDS
       ===================================================== */

    .feature-card {{
        background: rgba(30, 58, 138, 0.92);
        border-radius: 20px;
        padding: 25px;
        min-height: 150px;
        border: 1px solid rgba(244, 197, 66, 0.6);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
        margin-bottom: 15px;
    }}

    .feature-icon {{
        font-size: 35px;
        margin-bottom: 10px;
    }}

    .feature-title {{
        font-size: 20px;
        font-weight: 700;
        color: {WHITE};
        margin-bottom: 7px;
    }}

    .feature-text {{
        color: #E2E8F0;
        font-size: 15px;
    }}


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {{
        background: {ROYAL_BLUE};
        color: {WHITE};
        border: 2px solid {GOLD};
        border-radius: 12px;
        font-weight: 700;
        padding: 10px 22px;
        transition: 0.2s;
    }}

    .stButton > button:hover {{
        background: {GOLD};
        color: {DARK_NAVY};
        border-color: {WHITE};
    }}


    /* =====================================================
       FILE UPLOADER
       ===================================================== */

    [data-testid="stFileUploader"] {{
        background: rgba(15, 23, 42, 0.88);
        border: 2px dashed {GOLD};
        border-radius: 18px;
        padding: 10px;
    }}


    /* =====================================================
       CHAT MESSAGES
       ===================================================== */

    [data-testid="stChatMessage"] {{
        background: rgba(15, 23, 42, 0.90);
        border-radius: 18px;
        border: 1px solid rgba(244, 197, 66, 0.35);
        margin-bottom: 10px;
        padding: 10px;
    }}


    /* =====================================================
       CHAT INPUT BOX
       ===================================================== */

    [data-testid="stChatInput"] {{
        background: rgba(15, 23, 42, 0.96) !important;
        border: 2px solid {GOLD} !important;
        border-radius: 18px !important;
        padding: 4px !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.40) !important;
    }}

    [data-testid="stChatInput"] textarea {{
        background: transparent !important;
        color: {WHITE} !important;
        font-size: 16px !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: #CBD5E1 !important;
        opacity: 1 !important;
    }}

    [data-testid="stChatInput"] button {{
        background: {ROYAL_BLUE} !important;
        border-radius: 12px !important;
        border: 1px solid {GOLD} !important;
    }}

    [data-testid="stChatInput"] button:hover {{
        background: {GOLD} !important;
    }}

    [data-testid="stChatInput"] button svg {{
        color: {WHITE} !important;
    }}


    /* =====================================================
       NORMAL INPUTS
       ===================================================== */

    input, textarea {{
        background: rgba(255, 255, 255, 0.95) !important;
        color: {DARK_NAVY} !important;
        border-radius: 10px !important;
    }}


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {{
        text-align: center;
        padding: 25px;
        margin-top: 40px;
        color: #CBD5E1;
        font-size: 14px;
    }}

    .gold {{
        color: {GOLD};
        font-weight: 700;
    }}

    </style>
    """
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown(
    """
    <div style="
        text-align:center;
        padding:20px 5px;
        font-size:42px;
    ">
        📚
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("StudySnap AI")

st.sidebar.markdown(
    """
    <p style="color:#CBD5E1;">
    Snap it. Understand it. Learn it.
    </p>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()

st.sidebar.markdown(
    """
    ### ✨ Features

    📸 Upload study material  
    🤖 AI explanation  
    💬 Ask follow-up questions  
    🌍 Multiple languages  
    📧 Send notes to email
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()

st.sidebar.markdown(
    """
    **Supported languages**

    🇬🇧 English  
    🇮🇳 Hindi  
    🇮🇳 Marathi  
    🗣️ Hinglish
    """,
    unsafe_allow_html=True
)


# =========================================================
# WELCOME / ONBOARDING
# =========================================================

if not st.session_state.started:

    st.html(
        f"""
        <div class="hero">

            <div style="font-size:60px;">
                📚🤖
            </div>

            <div class="hero-title">
                Study<span>Snap AI</span>
            </div>

            <div class="hero-subtitle">
                Snap it. Understand it. Learn it.
            </div>

            <p style="
                color:#CBD5E1;
                font-size:17px;
                margin-top:15px;
            ">
                Turn your textbook pages, handwritten notes,
                diagrams and questions into simple explanations.
            </p>

        </div>
        """
    )

    st.markdown("### 🚀 What can StudySnap AI do?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.html(
            """
            <div class="feature-card">
                <div class="feature-icon">📸</div>
                <div class="feature-title">Snap & Upload</div>
                <div class="feature-text">
                    Upload a photo of your textbook,
                    notes, diagram or question.
                </div>
            </div>
            """
        )

    with col2:
        st.html(
            """
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">AI Explanation</div>
                <div class="feature-text">
                    Gemini AI explains difficult topics
                    in simple student-friendly language.
                </div>
            </div>
            """
        )

    with col3:
        st.html(
            """
            <div class="feature-card">
                <div class="feature-icon">💬</div>
                <div class="feature-title">Ask Questions</div>
                <div class="feature-text">
                    Continue the conversation and
                    ask follow-up questions.
                </div>
            </div>
            """
        )

    st.divider()

    st.markdown("### 👋 Let's get started!")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "Your Name",
            placeholder="Enter your name"
        )

    with col2:
        language = st.selectbox(
            "Preferred Language",
            [
                "English",
                "Hindi",
                "Marathi",
                "Hinglish"
            ]
        )

    if st.button(
        "🚀 Start Learning",
        use_container_width=True
    ):

        if name.strip():

            st.session_state.student_name = name.strip()
            st.session_state.language = language
            st.session_state.started = True

            st.rerun()

        else:
            st.warning("Please enter your name first.")

    st.stop()


# =========================================================
# MAIN HERO
# =========================================================

st.html(
    f"""
    <div class="hero">

        <div style="font-size:55px;">
            📚✨
        </div>

        <div class="hero-title">
            Hello, <span>{st.session_state.student_name}</span>!
        </div>

        <div class="hero-subtitle">
            Ready to understand something new?
        </div>

        <p style="
            color:#CBD5E1;
            font-size:16px;
        ">
            Language:
            <span class="gold">
                {st.session_state.language}
            </span>
        </p>

    </div>
    """
)


# =========================================================
# IMAGE UPLOAD
# =========================================================

st.markdown("### 📸 Upload Your Study Material")

uploaded_file = st.file_uploader(
    "Upload a textbook page, handwritten note, diagram or question",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="visible"
)

if uploaded_file:

    image_bytes = uploaded_file.getvalue()

    st.session_state.uploaded_image = image_bytes
    st.session_state.uploaded_mime_type = uploaded_file.type

    st.image(
        image_bytes,
        caption="Your uploaded study material",
        use_container_width=True
    )

    st.success(
        "Image uploaded successfully! 🎉 "
        "You can now ask StudySnap AI about it."
    )


# =========================================================
# CHAT HISTORY
# =========================================================

if st.session_state.messages:

    st.markdown("### 💬 Study Conversation")

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# =========================================================
# CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "Ask me anything about your study material..."
)


if prompt:

    if not st.session_state.uploaded_image:

        st.warning(
            "📸 Please upload a study image first."
        )

    else:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner(
                "🤖 StudySnap AI is thinking..."
            ):

                try:

                    system_instruction = f"""
You are StudySnap AI, a friendly AI study assistant.

Student name:
{st.session_state.student_name}

Preferred language:
{st.session_state.language}

Your job is to help the student understand
the uploaded study material.

Rules:

1. Explain in very simple language.
2. Use examples whenever helpful.
3. Break difficult topics into small steps.
4. If the question is mathematical,
   show the solution step by step.
5. If the image contains a diagram,
   explain the important parts.
6. Keep the answer student-friendly.
7. Avoid unnecessarily complicated terminology.
8. Respect the student's preferred language.
"""

                    contents = [
                        system_instruction,

                        genai.types.Part.from_bytes(
                            data=st.session_state.uploaded_image,
                            mime_type=st.session_state.uploaded_mime_type
                        ),

                        prompt
                    ]

                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=contents
                    )

                    answer = response.text

                    st.markdown(answer)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

                except Exception as e:

                    error_text = str(e)

                    # =====================================
                    # QUOTA ERROR
                    # =====================================

                    if (
                        "429" in error_text
                        or "RESOURCE_EXHAUSTED" in error_text
                    ):

                        st.warning(
                            "⚠️ Today's AI usage limit has "
                            "been reached. Please try again "
                            "after the Gemini quota resets."
                        )

                    # =====================================
                    # SERVER BUSY
                    # =====================================

                    elif "503" in error_text:

                        st.warning(
                            "⚠️ Gemini is currently busy. "
                            "Please try again later."
                        )

                    # =====================================
                    # API KEY ERROR
                    # =====================================

                    elif (
                        "API key" in error_text
                        or "INVALID_ARGUMENT" in error_text
                    ):

                        st.error(
                            "❌ Gemini API key problem. "
                            "Please check your Streamlit secrets."
                        )

                    # =====================================
                    # OTHER ERROR
                    # =====================================

                    else:

                        st.error(
                            "❌ Something went wrong. "
                            "Please try again later."
                        )


# =========================================================
# EMAIL NOTES FUNCTION
# =========================================================

def send_email(
    recipient_email,
    student_name,
    messages
):

    sender_email = st.secrets["EMAIL_ADDRESS"]
    app_password = st.secrets["EMAIL_APP_PASSWORD"]

    body = f"""
StudySnap AI - Study Notes
==========================

Student: {student_name}

"""

    for message in messages:

        role = message["role"].upper()

        body += f"""

{role}:
{message["content"]}

----------------------------------------
"""

    msg = MIMEMultipart()

    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = "📚 StudySnap AI - Your Study Notes"

    msg.attach(
        MIMEText(body, "plain")
    )

    with smtplib.SMTP(
        "smtp.gmail.com",
        587
    ) as server:

        server.starttls()

        server.login(
            sender_email,
            app_password
        )

        server.send_message(msg)


# =========================================================
# EMAIL SECTION
# =========================================================

if st.session_state.messages:

    st.divider()

    st.markdown("### 📧 Save Your Study Notes")

    email = st.text_input(
        "Enter your email address",
        placeholder="example@gmail.com"
    )

    if st.button(
        "📨 Send Study Notes to Email",
        use_container_width=True
    ):

        if not email.strip():

            st.warning(
                "Please enter your email address."
            )

        else:

            try:

                send_email(
                    email.strip(),
                    st.session_state.student_name,
                    st.session_state.messages
                )

                st.success(
                    "📚 Your study notes have been sent successfully!"
                )

            except Exception:

                st.error(
                    "❌ Email could not be sent. "
                    "Please check your email settings."
                )


# =========================================================
# RESET BUTTON
# =========================================================

st.divider()

if st.button(
    "🔄 Start New Study Session",
    use_container_width=True
):

    st.session_state.messages = []
    st.session_state.uploaded_image = None
    st.session_state.uploaded_mime_type = "image/jpeg"

    st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.html(
    """
    <div class="footer">

        <div style="
            font-size:25px;
            margin-bottom:8px;
        ">
            📚🤖✨
        </div>

        <b>StudySnap AI</b>

        <br>

        <span>
            Snap it. Understand it. Learn it.
        </span>

        <br><br>

        Made with ❤️ using Gemini AI + Streamlit

    </div>
    """
)