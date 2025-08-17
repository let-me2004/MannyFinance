# ai_core.py
# The definitive, final version that solves both the API error and the prompt bleed.

import os
import streamlit as st
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface.chat_models import ChatHuggingFace
from langchain_core.messages import HumanMessage, SystemMessage

def get_ai_response(data, question):
    """Generates a clean AI response using the correct conversational task."""
    if not data:
        return "Could not generate a response as data fetching failed."
    if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
        return "Hugging Face API Token is not set. Please enter it in the sidebar."

    repo_id = "HuggingFaceH4/zephyr-7b-beta"
    
    # Step 1: Define the connection to the Hugging Face model endpoint.
    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        max_new_tokens=256,
        temperature=0.1,
    )
    
    # Step 2: Wrap the endpoint in the ChatHuggingFace class. This is ESSENTIAL.
    # It ensures the request is sent as a 'conversational' task.
    chat_model = ChatHuggingFace(llm=llm)

    # Step 3: Use a clean, direct prompt within the required message structure.
    # This prompt is strict and concise to prevent the AI from "thinking out loud".
    system_prompt = """You are a factual data extraction AI named Manny.
- Your sole task is to directly and concisely answer the user's question using ONLY the provided context.
- Do not add any commentary, introductions, or explanations.
- If the information required is not in the context, you MUST respond with the exact phrase: "The information required to answer this question is not available in the provided data."
"""
    
    human_prompt = f"CONTEXT:\n{str(data)}\n\nQUESTION:\n{question}"
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt),
    ]

    try:
        # Step 4: Invoke the chat model with the list of messages.
        result = chat_model.invoke(messages)
        return result.content
    except Exception as e:
        # The error message from the screenshot came from this block.
        st.error(f"An error occurred while communicating with the AI model: {e}")
        return "Sorry, I was unable to generate a response. This could be a temporary issue with the AI service. Please try again."