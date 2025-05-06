from google.cloud import firestore
import streamlit as st


import re

def extract_dollar_sections(text):
    # Find all $...$ sections (using raw string properly)
    dollar_sections = re.findall(r'(\$.*?\$)', text)
    
    # Replace each $...$ section with extract_n
    modified_text = text
    for i, section in enumerate(dollar_sections, 1):
        modified_text = modified_text.replace(section, f"F{i}", 1)
    
    return dollar_sections, modified_text

def extract_between_dollars(text):
    pattern = r'\$(.*?)\$'
    matches = re.findall(pattern, text)
    return matches


# ext = r"$a+\frac{4}{5}=b+\frac{3}{4}=c+\frac{1}{2}$ bo'lsa $a, b, c$ sonlarni o'sish tartibida yozing."

ext = st.text_input("Question")

dollar, modified = extract_dollar_sections(ext)
       
st.write(modified)

for d in dollar:
  for y in extract_between_dollars(d):
    st.latex(y)
    st.write(y)
    


col1, col2, col3,col4 = st.columns(4)

with col1:
    A = st.text_input("A")
    latex_expressionsA = extract_between_dollars(A)
    if latex_expressionsA:
        for expr in latex_expressionsA:
            st.latex(expr)
    else:
        st.write(A)

with col2:
    B = st.text_input("B")
    latex_expressionsB = extract_between_dollars(B)
    if latex_expressionsB:
        for expr in latex_expressionsB:
            st.latex(expr)
    else:
        st.write(B)

with col3:
    C = st.text_input("C")
    latex_expressionsC = extract_between_dollars(C)
    if latex_expressionsC:
        for expr in latex_expressionsC:
            st.latex(expr)
    else:
        st.write(C)

with col4:
    D= st.text_input("D")
    latex_expressionsD = extract_between_dollars(D)
    if latex_expressionsD:
        for expr in latex_expressionsD:
            st.latex(expr)
    else:
        st.write(D)





import streamlit as st
import pandas as pd

# Show Data Editor
st.subheader("Question Data Table")

df = pd.DataFrame({
    "Question": [ext],
    "A": [A],
    "B": [B],
    "C": [C],
    "D": [D]
})

st.data_editor(df, num_rows="dynamic", use_container_width=True)





# # Initialize Firestore client
# db = firestore.Client.from_service_account_json("latex config.json")

# # Streamlit widgets to let a user create a new post
# title = st.text_input("Post title")
# url = st.text_input("Post url")
# submit = st.button("Submit new post")

# # Add new post to Firestore
# if title and url and submit:
#     doc_ref = db.collection("posts").document(title)
#     doc_ref.set({
#         "title": title,
#         "url": url
#     })
#     st.success("Post submitted!")

# # Get only the first document
# posts_ref = db.collection("posts")
# docs = posts_ref.stream()

# # Render the first post
# for doc in docs:
#     post = doc.to_dict()
#     st.subheader(f"Post: {post['title']}")
#     st.write(f":link: [{post['url']}]({post['url']})")
#     st.video(post['youtube'])


# # import firebase_admin
# # from firebase_admin import credentials

# # cred = credentials.Certificate("math.json")
# # firebase_admin.initialize_app(cred)




