import streamlit as st # type: ignore
import pandas as pd # type: ignore
import re
import firebase_admin # type: ignore
from firebase_admin import credentials, firestore # type: ignore

# --- Firebase Init ---
if not firebase_admin._apps:
    cred = credentials.Certificate("latex.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Helpers ---
def extract_dollar_sections(text):
    dollar_sections = re.findall(r'(\$.*?\$)', text)
    modified = text
    latex_map = {}
    for i, section in enumerate(dollar_sections, 1):
        placeholder = f"F{i}"
        modified = modified.replace(section, placeholder, 1)
        latex_map[placeholder] = section[1:-1]
    return latex_map, modified

def replace_placeholders(modified, latex_map):
    for key, val in latex_map.items():
        modified = modified.replace(key, f"${val}$")
    return modified

# --- UI ---
st.title("📘 LaTeX Question Editor")

# Reset via query param
if "reset" in st.query_params:
    st.query_params.clear()

with st.form("question_form"):
    question_input = st.text_input("Question", value="")
    latex_map, modified_text = extract_dollar_sections(question_input)

    st.markdown("**Modified Text with Placeholders:**")
    st.write(modified_text)

    st.markdown("**Edit LaTeX Expressions:**")
    edited_latex = {}
    for ph in latex_map:
        val = st.text_input(f"{ph}:", value=latex_map[ph])
        edited_latex[ph] = val
        st.latex(val)

    st.subheader("Answer Options")
    cols = st.columns(4)
    answers = {}
    for col, label in zip(cols, ["A", "B", "C", "D"]):
        with col:
            val = st.text_input(label, value="")
            answers[label] = val
            st.markdown(f"**Preview {label}:**")
            exps = re.findall(r'\$(.*?)\$', val)
            if exps:
                for e in exps:
                    st.latex(e)
            else:
                st.write(val)

    st.markdown("**Final Reconstructed Question:**")
    final_q = replace_placeholders(modified_text, edited_latex)
    st.write(final_q)
    st.latex(final_q)

    colA, colB = st.columns(2)
    with colA:
        submit = st.form_submit_button("📤 Send to Firebase")
    with colB:
        reset = st.form_submit_button("🔄 Reset Form")

# --- Handlers ---
@firestore.transactional
def add_with_auto_id(transaction):
    counter_ref = db.collection("counters").document("questions")
    counter_doc = counter_ref.get(transaction=transaction)
    current_id = counter_doc.get("current") if counter_doc.exists else 0
    new_id = current_id + 1
    transaction.set(counter_ref, {"current": new_id})
    q_ref = db.collection("questions").document(str(new_id))
    transaction.set(q_ref, {
        "id": new_id,
        "Question": final_q,
        "A": answers["A"],
        "B": answers["B"],
        "C": answers["C"],
        "D": answers["D"]
    })
    return new_id

if submit:
    try:
        transaction = db.transaction()
        new_id = add_with_auto_id(transaction)
        st.success(f"✅ Question saved with ID: {new_id}")
    except Exception as e:
        st.error(f"❌ Failed to send question: {e}")

if reset:
    # Rerun app with query param to force clean form
    st.query_params["reset"] = "1"
    st.rerun()

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
    st.error(f"Failed to load questions: {e}")
