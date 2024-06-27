import os

from elasticsearch import Elasticsearch
from openai import AzureOpenAI

es = Elasticsearch("http://localhost:9200")

index_name = "course-questions"

def retrieve_documents(query, index_name="course-questions", max_results=5):
    es = Elasticsearch("http://localhost:9200")
    
    search_query = {
        "size": max_results,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": "data-engineering-zoomcamp"
                    }
                }
            }
        }
    }
    
    response = es.search(index=index_name, body=search_query)
    documents = [hit['_source'] for hit in response['hits']['hits']]
    return documents

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment_name = "Demo"

context_template = """
Section: {section}
Question: {question}
Answer: {text}
""".strip()

prompt_template = """
QUESTION: {user_question}

CONTEXT:

{context}
""".strip()

system_prompt = "You're a course teaching assistant. Answer the user QUESTION from students based on the provided CONTEXT."

def build_context(documents):
    context_result = ""
    
    for doc in documents:
        doc_str = context_template.format(**doc)
        context_result += ("\n\n" + doc_str)
    
    return context_result.strip()

def build_prompt(user_question, documents):
    context = build_context(documents)
    prompt = prompt_template.format(
        user_question=user_question,
        context=context
    )
    return prompt

def ask_openai(system_prompt, prompt):
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "system", "content": system_prompt},{"role": "user", "content": prompt}],
        temperature=0.7
    )
    answer = response.choices[0].message.content
    return answer

def qa_bot(user_question):
    context_docs = retrieve_documents(user_question)
    prompt = build_prompt(user_question, context_docs)
    answer = ask_openai(system_prompt, prompt)
    return answer