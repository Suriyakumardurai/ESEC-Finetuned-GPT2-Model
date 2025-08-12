# chat/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from transformers import pipeline, AutoTokenizer
import markdown2
import json
import os

# --- This part is correct and loads the model on startup ---
try:
    BASE_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_PROJECT_DIR)
    
    print("🚀 Initializing ESEC Chatbot model (CPU)...")
    print(f"Attempting to load model from: {MODEL_PATH}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    esec_bot = pipeline("text-generation", model=MODEL_PATH, tokenizer=tokenizer, device=-1)
    print("✅ ESEC Chatbot model loaded successfully!")

except Exception as e:
    print(f"❌ Failed to load model: {e}")
    esec_bot = None
    tokenizer = None

def index(request):
    html_response = ""
    prompt = ""

    if request.method == 'POST':
        if not esec_bot:
             html_response = "<p><strong>Error:</strong> The AI model is not loaded. Please check the server logs.</p>"
             return render(request, "chat/index.html", {"response": html_response, "prompt": prompt})

        user_question = request.POST.get("prompt", "").strip()
        prompt = user_question

        # --- Use the essential prompt format the model was trained on ---
        formatted_prompt = f"[QUESTION]: {user_question} [ANSWER]:"

        try:
            # --- SIMPLIFIED GENERATOR CALL ---
            # All complex parameters have been removed to let the model respond freely.
            result = esec_bot(
                formatted_prompt,
                max_new_tokens=90,
                num_return_sequences=1,
                pad_token_id=tokenizer.eos_token_id
            )

            full_text = result[0]["generated_text"]
            answer_part = full_text.split("[ANSWER]:")[1].strip()
            answer_part = answer_part.split("QUESTION]:")[0].strip()

            # Render the response using markdown
            html_response = markdown2.markdown(answer_part, extras=["fenced-code-blocks", "tables"])

        except Exception as e:
            html_response = f"<p><strong>Error during generation:</strong> {e}</p>"

    return render(request, "chat/index.html", {"response": html_response, "prompt": prompt})
