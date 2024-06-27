import streamlit as st

# import qa_bot function from rag.py
from rag import qa_bot

st.title("Question Answering Bot")

user_question = st.text_input("Ask a question:")

if st.button("Get Answer"):
    with st.spinner("Thinking..."):
        answer = qa_bot(user_question)
        st.success("Done!")
        st.write(answer)