from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

class Recipe(BaseModel):
    name: str = Field(description='Name of the recipe')
    description: str = Field(description='Description of the recipe')
    prep_time: str = Field(description='Prep time of the recipe')

class Response(BaseModel):
    """A single recipe"""
    ingredients: List[str] = Field(description='Ingredients of the recipe')
    recipe: List[Recipe] = Field(description='List of 3 recipe suggestions')

#Initialize the Google Generative AI model
model = init_chat_model(
    model = "gemini-3.1-flash-lite",
    model_provider= "google_genai"
)
structured_model = model.with_structured_output(Response)

system_prompt = """
"You are a helpful chef. Identify the main ingredients. Suggest 3 recipes based those ingredients."
"""
# Create message
message = [{"role": "system", "content": system_prompt},
           {"role": "user", "content": "I have broccoli, butter, and eggs."}]

#Get and print the response
response = structured_model.invoke(message)
print(response.model_dump())
