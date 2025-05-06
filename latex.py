import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import re
import pandas as pd

# --- Firebase Initialization ---
try:
    if not firebase_admin._apps:
        # Load Firebase credentials from Streamlit secrets
        firebase_creds = json.loads(st.secrets["firebase_credentials"])  # Get credentials from secrets
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
    db = firestore.client()  # Create Firestore client
    st.success("✅ Firebase Initialized Successfully!")
except Exception as e:
    st.error(f"❌ Failed to initialize Firebase: {e}")
    st.stop()

# --- Clear Form Early if Flagged ---
if st.session_state.get("clear_form_flag", False):
    for key in list(st.session_state.keys()):
        if key.startswith("latex_") or key.startswith("ans_") or key == "Question":
            st.session_state[key] = ""
    st.session_state["clear_form_flag"] = False  # Reset the flag

# --- Helper Functions ---
def extract_latex_sections(text):
    """Extract LaTeX sections (enclosed in $...$) from the question text."""
    dollar_sections = re.findall(r'(\$.*?\$)', text)
    modified_text = text
    latex_map = {}
    for i, section in enumerate(dollar_sections, 1):
        placeholder = f"F{i}"
        modified_text = modified_text.replace(section, placeholder, 1)
        latex_map[placeholder] = section[1:-1]  # Remove $ from LaTeX sections
    return latex_map, modified_text

def replace_placeholders_with_latex(modified_text, latex_map):
    """Replace placeholders with actual LaTeX values."""
    for placeholder, latex in latex_map.items():
        modified_text = modified_text.replace(placeholder, f"${latex}$")
    return modified_text

# --- UI Components ---
st.title("📘 LaTeX Question Editor")

# Question Input Field
question_input = st.text_input("Question", key="Question")

# Extract LaTeX sections and display modified text
latex_map, modified_text = extract_latex_sections(question_input)
st.write(modified_text)

# LaTeX Editing Section
edited_latex_map = {}
for placeholder, latex in latex_map.items():
    val = st.text_input(f"{placeholder}:", value=latex, key=f"latex_{placeholder}")
    edited_latex_map[placeholder] = val
    st.latex(val)

# Answer Options (A, B, C, D)
answer_inputs = {}
col1, col2, col3, col4 = st.columns(4)
for col, label in zip([col1, col2, col3, col4], ["A", "B", "C", "D"]):
    with col:
        val = st.text_input(label, key=f"ans_{label}")
        answer_inputs[label] = val
        # Check for LaTeX expressions in the answer
        exps = re.findall(r'\$(.*?)\$', val)
        if exps:
            for exp in exps:
                st.latex(exp)
        else:
            st.write(val)

# Final Reconstructed Question
final_question = replace_placeholders_with_latex(modified_text, edited_latex_map)
st.write(final_question)
st.latex(final_question)

# --- Firestore Functions ---
@firestore.transactional
def add_question_to_firestore(transaction, question, answers):
    """Add a new question to Firestore and increment the question ID."""
    counter_ref = db.collection("counters").document("questions")
    counter_doc = counter_ref.get(transaction=transaction)
    current_id = counter_doc.get("current") if counter_doc.exists else 0
    new_id = current_id + 1
    transaction.set(counter_ref, {"current": new_id})
    q_ref = db.collection("questions").document(str(new_id))
    transaction.set(q_ref, {
        "id": new_id,
        "Question": question,
        "A": answers["A"],
        "B": answers["B"],
        "C": answers["C"],
        "D": answers["D"]
    })
    return new_id

# --- Buttons ---
colA, colB = st.columns(2)
with colA:
    submitted = st.button("📤 Send to Firebase")
with colB:
    st.button("🔄 Reset Form", on_click=lambda: st.session_state.update({"clear_form_flag": True}))

# --- Form Submission Logic ---
if submitted:
    # Validate Required Fields
    if not question_input.strip():
        st.warning("⚠️ Question cannot be empty.")
    elif any(not answer.strip() for answer in answer_inputs.values()):
        st.warning("⚠️ All answers (A, B, C, D) must be filled out.")
    else:
        try:
            transaction = db.transaction()
            new_id = add_question_to_firestore(transaction, final_question, answer_inputs)
            st.session_state["clear_form_flag"] = True  # Will trigger form reset on next run
            st.success(f"✅ Question saved with ID: {new_id}")
        except Exception as e:
            st.error(f"❌ Failed to send question to Firestore: {e}")

# --- View All Questions ---
st.subheader("📋 All Questions in Firestore")
try:
    docs = db.collection("questions").stream()
    rows = [{"ID": doc.id, **doc.to_dict()} for doc in docs]
    if rows:
        df = pd.DataFrame(rows)
        st.data_editor(df, use_container_width=True, num_rows="dynamic")
    else:
        st.info("No questions found in Firestore.")
except Exception as e:
    st.error(f"❌ Failed to load questions: {e}")
