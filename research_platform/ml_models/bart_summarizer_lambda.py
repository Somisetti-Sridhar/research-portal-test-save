import requests
import json

# Replace this with your actual API Gateway URL
API_URL = "https://eswopm4jm1.execute-api.ap-south-1.amazonaws.com/default/google-summarizer"

def summarize_text(text, max_words_per_chunk=400):
    payload = {
        "text": text,
        "max_words_per_chunk": max_words_per_chunk
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        return data.get("summary", "")
    except requests.exceptions.RequestException as e:
        print(f"Error calling Lambda API: {e}")
        if e.response is not None:
            print(e.response.text)
        return None
    
    
def summarize_text_from_pdf(pdf_file, max_words_per_chunk=400):
    from apps.papers.utils import extract_text_from_pdf
    text = extract_text_from_pdf(pdf_file)
    
    if not text.strip():
        return "No text could be extracted from the PDF."
    
    payload = {"text": text, "max_words_per_chunk": max_words_per_chunk}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        return data.get("summary", "")
    except requests.exceptions.RequestException as e:
        print(f"Error calling Lambda API: {e}")
        if e.response:
            print(e.response.text)
        return "Error generating summary."

if __name__ == "__main__":
    TEXT = """
    Coronavirus disease 2019 (COVID-19) is a contagious disease caused by the coronavirus SARS-CoV-2.
    In January 2020, the disease spread worldwide, resulting in the COVID-19 pandemic.
    """
    
    summary = summarize_text(TEXT)
    print("Summary:\n", summary)
