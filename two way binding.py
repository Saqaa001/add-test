import streamlit as st
import pandas as pd
import re

# --- Session State Initialization ---
if "LatexMap" not in st.session_state:
    st.session_state["LatexMap"] = {}
if "ModifiedText" not in st.session_state:
    st.session_state["ModifiedText"] = ""
if "FinalQuestion" not in st.session_state:
    st.session_state["FinalQuestion"] = ""

for key in ["Question", "A", "B", "C", "D"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# --- Helper Functions ---
def extract_dollar_sections(text):
    dollar_sections = re.findall(r'(\$.*?\$)', text)
    modified_text = text
    st.session_state["LatexMap"] = {}  # reset on new input
    for i, section in enumerate(dollar_sections, 1):
        placeholder = f"F{i}"
        modified_text = modified_text.replace(section, placeholder, 1)
        st.session_state["LatexMap"][placeholder] = section[1:-1]  # strip $
    st.session_state["ModifiedText"] = modified_text
    return list(st.session_state["LatexMap"].keys()), modified_text

def replace_placeholders_with_latex(modified_text, latex_map):
    for key, val in latex_map.items():
        modified_text = modified_text.replace(key, f"${val}$")
    return modified_text

# --- Input Question ---
st.subheader("Enter Question")

# Create a form for input and submission
with st.form(key="question_form"):
    # Step 1: Display raw input and update session state immediately on typing
    question_input = st.text_input("Question", value=st.session_state["Question"])

    # Step 2: Extract LaTeX sections
    placeholders, modified_text = extract_dollar_sections(question_input)

    # Step 3: Show modified with placeholders
    st.markdown("**Modified Text with Placeholders:**")
    st.write(modified_text)

    # Step 4: Editable LaTeX expressions
    st.markdown("**Edit LaTeX Expressions:**")
    for placeholder in placeholders:
        new_val = st.text_input(f"{placeholder}:", value=st.session_state["LatexMap"][placeholder], key=placeholder)
        st.session_state["LatexMap"][placeholder] = new_val
        st.latex(new_val)

    # --- Answer Options Input and Preview ---
    st.subheader("Answer Options")
    col1, col2, col3, col4 = st.columns(4)
    for col, label in zip([col1, col2, col3, col4], ["A", "B", "C", "D"]):
        with col:
            value = st.text_input(label, value=st.session_state[label])
            st.session_state[label] = value
            st.markdown(f"**Preview {label}:**")
            expressions = re.findall(r'\$(.*?)\$', value)
            if expressions:
                for expr in expressions:
                    st.latex(expr)
            else:
                st.write(value)

    # Step 5: Show Final Reconstructed Question
    st.markdown("**Final Reconstructed Question:**")
    preview_question = replace_placeholders_with_latex(modified_text, st.session_state["LatexMap"])
    st.write(preview_question)
    st.latex(preview_question)

    # Apply Changes Button
    submit_button = st.form_submit_button(label="✅ Apply Changes")

if submit_button:
    # Apply the changes only once when the button is clicked
    final_question = replace_placeholders_with_latex(modified_text, st.session_state["LatexMap"])
    st.session_state["Question"] = final_question  # Update session state
    st.session_state["FinalQuestion"] = final_question  # Store final question for later use
    st.success("Changes applied to session state!")

# --- Data Table Editor ---
st.subheader("Edit or View as Table")
df = pd.DataFrame({
    "Question": [st.session_state["Question"]],
    "A": [st.session_state["A"]],
    "B": [st.session_state["B"]],
    "C": [st.session_state["C"]],
    "D": [st.session_state["D"]],
})
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- Sync Back if Edited ---
if not edited_df.equals(df):
    for key in ["Question", "A", "B", "C", "D"]:
        st.session_state[key] = edited_df.at[0, key]
