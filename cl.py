import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

# Load environment variables
load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Assistant",
    page_icon="🎓",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root variables ── */
:root {
    --bg:        #0d1117;
    --surface:   #161b22;
    --surface2:  #21262d;
    --accent:    #58a6ff;
    --accent2:   #3fb950;
    --text:      #e6edf3;
    --muted:     #8b949e;
    --user-bg:   #1f3a5f;
    --ai-bg:     #1a2d1c;
    --border:    #30363d;
    --radius:    14px;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 1rem 6rem !important; max-width: 780px; }

/* ── Header ── */
.app-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 28px 0 18px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
}
.header-icon {
    width: 48px; height: 48px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
}
.header-text h1 {
    margin: 0; font-size: 1.45rem; font-weight: 700;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.header-text p {
    margin: 2px 0 0; font-size: 0.78rem; color: var(--muted); font-weight: 300;
}

/* ── Chat bubbles ── */
.chat-row {
    display: flex;
    gap: 12px;
    margin-bottom: 18px;
    animation: fadeUp .3s ease;
}
.chat-row.user  { flex-direction: row-reverse; }
.chat-row.user  .bubble { background: var(--user-bg); border-bottom-right-radius: 4px; }
.chat-row.ai    .bubble { background: var(--ai-bg);   border-bottom-left-radius:  4px; }

.avatar {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0; margin-top: 2px;
}
.avatar.user { background: var(--user-bg); border: 1px solid var(--accent); }
.avatar.ai   { background: var(--ai-bg);   border: 1px solid var(--accent2); }

.bubble {
    max-width: 72%;
    padding: 12px 16px;
    border-radius: var(--radius);
    font-size: 0.88rem;
    line-height: 1.65;
    color: var(--text);
    border: 1px solid var(--border);
    word-wrap: break-word;
}
.bubble code {
    font-family: 'JetBrains Mono', monospace;
    background: var(--surface2);
    padding: 1px 5px; border-radius: 4px;
    font-size: 0.82rem; color: var(--accent);
}
.bubble pre {
    background: var(--surface2);
    padding: 10px 14px; border-radius: 8px;
    overflow-x: auto; margin: 8px 0;
    border: 1px solid var(--border);
}
.bubble pre code { background: none; padding: 0; color: var(--accent2); }

.timestamp {
    font-size: 0.68rem; color: var(--muted);
    margin-top: 6px; text-align: right;
}
.chat-row.ai .timestamp { text-align: left; }

/* ── Welcome card ── */
.welcome-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px 24px;
    text-align: center;
    margin: 40px 0;
}
.welcome-card h2 { font-size: 1.2rem; font-weight: 600; margin-bottom: 10px; }
.welcome-card p  { color: var(--muted); font-size: 0.85rem; line-height: 1.7; }
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 18px; }
.chip {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 5px 14px;
    font-size: 0.78rem; color: var(--muted);
}

/* ── Input bar ── */
.stChatInput { background: transparent !important; }
section[data-testid="stBottom"] {
    background: var(--bg) !important;
    border-top: 1px solid var(--border);
    padding: 10px 0 !important;
}
textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.9rem !important;
}
textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(88,166,255,.15) !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Buttons ── */
.stButton > button {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.82rem !important;
    transition: border-color .2s, background .2s !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    background: var(--user-bg) !important;
}

/* ── Animation ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="header-icon">🎓</div>
    <div class="header-text">
        <h1>Student Assistant</h1>
        <p>Powered by Groq & Tanish Londhe· Your AI study companion</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content=(
            "You are a helpful Student AI assistant. You help students with their studies, "
            "explain concepts clearly, help with homework, suggest study strategies, and answer "
            "academic questions across all subjects. Be encouraging, patient, and educational."
        ))
    ]
if "display_msgs" not in st.session_state:
    st.session_state.display_msgs = []   # list of {"role": "user"|"ai", "content": str}

# ── Sidebar ───────────────────────────────────────────────────────────────────
api_key = os.getenv("GROQ_API_KEY", "")

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    model_choice = st.selectbox(
        "Model",
        ["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma2-9b-it"],
        index=0
    )
    st.markdown("---")
    st.markdown("### 📚 Suggested topics")
    topics = ["Explain a concept", "Solve a math problem", "Summarise an article",
              "Help with essay", "Study plan", "Quiz me"]
    for t in topics:
        st.markdown(f"<div class='chip'>{t}</div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑️ Clear chat"):
        st.session_state.display_msgs = []
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:.75rem;color:#8b949e;'>Built with LangChain + Groq</p>",
        unsafe_allow_html=True
    )

# ── Model init ────────────────────────────────────────────────────────────────
@st.cache_resource
def get_model(key, model_id):
    return ChatGroq(model=model_id, groq_api_key=key)

# ── Chat display ──────────────────────────────────────────────────────────────
if not st.session_state.display_msgs:
    st.markdown("""
    <div class="welcome-card">
        <h2>👋 Hello, I'm your Student Assistant!</h2>
        <p>I'm here to help you understand concepts, solve problems,<br>
        plan your studies, and ace your exams. What shall we tackle today?</p>
        <div class="chip-row">
            <span class="chip">📐 Mathematics</span>
            <span class="chip">🔬 Science</span>
            <span class="chip">📖 Literature</span>
            <span class="chip">🌍 History</span>
            <span class="chip">💻 Coding</span>
            <span class="chip">✏️ Essay writing</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.display_msgs:
        role_class = "user" if msg["role"] == "user" else "ai"
        avatar = "🧑‍🎓" if msg["role"] == "user" else "🤖"
        content = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
        st.markdown(f"""
        <div class="chat-row {role_class}">
            <div class="avatar {role_class}">{avatar}</div>
            <div>
                <div class="bubble">{content}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
prompt = st.chat_input("Ask me anything about your studies…")

if prompt:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not found. Please set it in your .env file.")
    else:
        # Show user message immediately
        st.session_state.display_msgs.append({"role": "user", "content": prompt})
        st.session_state.messages.append(HumanMessage(content=prompt))

        # Get AI response
        try:
            llm = get_model(api_key, model_choice)
            with st.spinner("Thinking…"):
                response = llm.invoke(st.session_state.messages)
            ai_text = response.content
        except Exception as e:
            ai_text = f"❌ Error: {e}"

        st.session_state.messages.append(AIMessage(content=ai_text))
        st.session_state.display_msgs.append({"role": "ai", "content": ai_text})
        st.rerun()
   