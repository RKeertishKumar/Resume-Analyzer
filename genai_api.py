import google.generativeai as genai
import os

def gemini_api_response(resume_info,path_info):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    model = genai.GenerativeModel('gemini-1.5-flash')

    response = model.generate_content(f"Roadmap for {path_info} role in 5 points based on weakness in {resume_info}")
    suggesetion = response.text
    return suggesetion