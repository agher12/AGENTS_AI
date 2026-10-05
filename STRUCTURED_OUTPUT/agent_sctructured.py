import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import List
from recipe_generator import response

load_dotenv()

class EmailResponse(BaseModel):
 """Response after sending email"""
 recipient: str = Field(description="Email address recipient")
 subject: str = Field(description="Email subject")
 body: str = Field(description="Email body")
 status: str = Field(description="Email status (sent/failed)")
 summary: str = Field(description="Email summary")


def send_email (email_address: str, sender_name: str, subject: str, body: str):
 """Send an email to an email address on behalf of the sender"""
 #Code that sends that mail
 print("Sending email")
 return F"Email sent to: {email_address} in behalf of sender: {sender_name}"

#Initialize the Google Generative AI model
model = init_chat_model(
    model = "gemini-3.1-flash-lite",
    model_provider="google_genai"
)

system_prompt = """
My name is Betiño. You are a Helpful assistant.
YOUR WORKFLOW:
1. You should help the user with various office task.
2.If the user ask you to send an email, use the send_email tool.
3. Create a relevant body and subject for the mail
"""

agent = create_agent(
    model=model,
    tools=[send_email],
    system_prompt = system_prompt,
    response_format= EmailResponse
)

user_query = "Send and email to john at john@example.com telling him that I finished the task"

response = agent.invoke(
    {"messages": [{'role': 'user', 'content': user_query}]},
)

print(response['messages'][-1].content)
print(response['structured_response'])




