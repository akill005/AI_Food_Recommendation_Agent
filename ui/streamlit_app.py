import streamlit as st
import requests
import uuid
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:8000/agent"
st.set_page_config(
    page_title="AI Food Search Engine",
    page_icon="🍛",
    layout="centered",
    initial_sidebar_state="expanded"
)
st.markdown(
    """
    <style>

    /* Entire App */
    html, body, [class*="css"] {
        background-color: #0E1117;
        color: white;
    }

    .stApp {
        background-color: #0E1117;
    }

    /* Remove Streamlit default header/footer/menu */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    /* Main Container */
    .block-container {
        padding-top: 2rem;
        max-width: 900px;
    }

    /* Title */
    h1 {
        text-align: center;
        font-size: 60px !important;
        font-weight: 800 !important;
        color: white !important;
        margin-bottom: 0.3rem !important;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #9CA3AF;
        font-size: 20px;
        margin-bottom: 35px;
    }

    /* User + Assistant Chat Containers */
    [data-testid="stChatMessage"] {
        background-color: #1A1D24;
        border: 1px solid #2D3748;
        border-radius: 18px;
        padding: 14px;
        margin-bottom: 15px;
    }

    /* Chat Input Container */
    .stChatInputContainer {
        background-color: #1F2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 18px !important;
    }

    /* User + assistant message text */
[data-testid="stChatMessageContent"] p {
    color: white !important;
    font-size: 17px;
    line-height: 1.7;
}

/* User query text */
[data-testid="stChatMessageContent"] {
    color: white !important;
}

/* Input box typed text */
textarea {
    color: black !important;
    font-size: 17px !important;
}

/* Placeholder text */
textarea::placeholder {
    color: #6B7280 !important;
}

    /* Spinner Text */
    .stSpinner > div {
        color: white !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.title("🍛 AI Food Search Engine")
st.markdown(
    """
    <div class="subtitle">
        Smart hybrid retrieval powered food recommendation system
    </div>
    """,
    unsafe_allow_html=True
)
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "api_available" not in st.session_state:
    st.session_state.api_available = True

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("What do you want to eat?", key="user_input")

if prompt:
    # Add user message to history
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process with backend
    with st.chat_message("assistant"):
        with st.spinner("🔍 Finding recommendations..."):
            try:
                # Validate API is reachable
                if not st.session_state.api_available:
                    st.error("❌ Backend API is not available. Please start the FastAPI server.")
                    reply = "Backend service is unavailable. Please ensure the API is running on http://127.0.0.1:8000"
                
                else:
                    # Make API request
                    response = requests.get(
                        API_URL,
                        params={
                            "query": prompt,
                            "session_id": st.session_state.session_id
                        },
                        timeout=30
                    )
                    
                    # Handle response
                    if response.status_code == 200:
                        data = response.json()
                        reply = data.get("response", "No recommendations found.")
                        st.session_state.api_available = True
                    
                    elif response.status_code == 400:
                        reply = "❌ Invalid query. Please provide a clear food preference."
                    
                    elif response.status_code == 500:
                        data = response.json()
                        reply = f"❌ Backend error: {data.get('detail', 'Unknown error')}"
                    
                    else:
                        reply = f"❌ Unexpected error (Status {response.status_code})"
            
            except requests.exceptions.ConnectionError:
                logger.error("Failed to connect to API")
                st.session_state.api_available = False
                reply = (
                    "❌ Cannot connect to the backend API.\n\n"
                    "Please ensure:\n"
                    "1. FastAPI server is running (`python app.py`)\n"
                    "2. Server is accessible at http://127.0.0.1:8000"
                )
            
            except requests.exceptions.Timeout:
                logger.error("API request timeout")
                reply = "⏱️ Request timed out. The server took too long to respond. Please try again."
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {str(e)}")
                reply = f"❌ Network error: {str(e)}"
            
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                reply = f"❌ Unexpected error: {str(e)}"
            
            st.markdown(reply)
    
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply
        }
    )
# import streamlit as st
# import requests
# import uuid

# API_URL = "http://127.0.0.1:8000/agent"

# st.set_page_config(
#     page_title="Swiggy AI Search",
#     page_icon="🍛",
#     layout="centered"
# )

# # ---------------- UI HEADER ----------------
# st.markdown("""
# # 🍛 Swiggy AI Search Engine
# ### Find food instantly with smart retrieval + filters
# """)

# # ---------------- SESSION ----------------
# if "session_id" not in st.session_state:
#     st.session_state.session_id = str(uuid.uuid4())

# # ---------------- QUICK SUGGESTIONS ----------------
# st.markdown("### 🔥 Quick Searches")

# col1, col2, col3, col4 = st.columns(4)

# if col1.button("🍗 Chicken"):
#     st.session_state.query = "chicken biryani under 200"

# if col2.button("🥩 Mutton"):
#     st.session_state.query = "mutton dishes"

# if col3.button("🍳 Egg"):
#     st.session_state.query = "egg fried rice"

# if col4.button("🌱 Veg"):
#     st.session_state.query = "veg dishes under 150"

# # ---------------- SEARCH BAR ----------------
# query = st.text_input(
#     "Search food items",
#     value=st.session_state.get("query", ""),
#     placeholder="e.g. chicken biryani under 200"
# )

# # ---------------- SEARCH BUTTON ----------------
# search = st.button("🔍 Search")

# # ---------------- RESULT SECTION ----------------
# if search and query:

#     with st.spinner("Finding best matches... 🍛"):

#         try:
#             response = requests.get(
#                 API_URL,
#                 params={
#                     "query": query,
#                     "session_id": st.session_state.session_id
#                 },
#                 timeout=30
#             ).json()

#             result_text = response.get("response", "")

#             st.markdown("## 🍽️ Results")

#             blocks = result_text.strip().split("\n\n")

#             for block in blocks:
#                 if not block.strip():
#                     continue

#                 html_card = f"""
#                 <div style="
#                     background-color:#111827;
#                     padding:16px;
#                     border-radius:14px;
#                     margin-bottom:12px;
#                     border:1px solid #2D3748;
#                     box-shadow:0 2px 8px rgba(0,0,0,0.25);
#                     color:#F9FAFB;
#                     font-family: Arial, sans-serif;
#                     white-space: pre-line;
#                     font-size:15px;
#                     line-height:1.5;
#                 ">
#                     {block}
#                 </div>
#                 """

#                 st.markdown(html_card, unsafe_allow_html=True)

#         except Exception as e:
#             st.error(f"Error connecting to backend: {e}")