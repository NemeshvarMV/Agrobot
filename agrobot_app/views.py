from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
import json
import os
import random
from .utils import generate_response_from_text, translate_to_en, translate_from_en, detect_language
from .image_analysis import analyze_image_from_file

SUPPORTED_LANGS = ["en", "ta", "hi", "kn", "te", "ml"]

TEMPLATES = [
    "Based on my knowledge, {answer}",
    "Here’s what I found: {answer}",
    "After analyzing, I think: {answer}",
    "From my experience: {answer}",
    "I believe this might help: {answer}",
    "Looking into it, I found this: {answer}",
    "According to the data I have, {answer}",
    "After some research, it appears: {answer}",
    "In my analysis, the following is relevant:\n{answer}",
    "Here’s an insight I can share:\n{answer}",
    "Considering the information available, {answer}",
    "My recommendation is as follows:\n{answer}",
    "Here’s what seems likely:\n{answer}",
    "From what I can tell: {answer}",
    "Analyzing your query, I suggest:\n{answer}",
    "Here’s a detailed explanation:\n{answer}",
    "Based on current knowledge, {answer}",
    "After reviewing, I think the answer is:\n{answer}",
    "Here’s something that might help:\n{answer}",
    "From my perspective: {answer}",
    "Looking at the details, I find:\n{answer}",
    "My interpretation is:\n{answer}",
    "Here’s a summary of what I found:\n{answer}",
    "Upon evaluation, it seems: {answer}",
    "Here’s a closer look:\n{answer}",
    "After careful consideration: {answer}",
    "This might be useful:\n{answer}",
    "Based on my research, {answer}",
    "From my analysis, it appears:\n{answer}",
    "Let me explain:\n{answer}",
    "Here’s an observation:\n{answer}",
    "This is what I can share:\n{answer}",
    "According to my understanding:\n{answer}",
    "Here’s an answer you can consider:\n{answer}",
    "Upon reviewing your query, {answer}",
    "This information might help:\n{answer}",
    "After examining the data, {answer}",
    "Here’s my insight:\n{answer}",
    "From the information at hand, {answer}",
    "I’ve analyzed it and found:\n{answer}",
    "Here’s a practical tip:\n{answer}",
    "Based on my assessment, {answer}",
    "From what I understand: {answer}",
    "Here’s a suggestion:\n{answer}",
    "After evaluating, I recommend:\n{answer}",
    "This could be relevant:\n{answer}",
    "From my findings, {answer}",
    "Here’s the explanation:\n{answer}",
    "Considering the context, {answer}",
    "Here’s the information I gathered:\n{answer}",
    "Based on observations, {answer}",
    "After careful analysis:\n{answer}"
]
TAGS = {
    "predicted": {
        "en": "Predicted Disease:",
        "ta": "முன்னறிவிக்கப்பட்ட நோய்:",
        "hi": "अनुमानित रोग:",
        "kn": "ಅನುಮಾನಿತ ರೋಗ:",
        "te": "అంచనా వేసిన వ్యాధి:",
        "ml": "പ്രവചിച്ച രോഗം:"
    },
    "causes": {
        "en": "Possible Causes:",
        "ta": "சாத்தியமான காரணங்கள்:",
        "hi": "संभावित कारण:",
        "kn": "ಸಂಭಾವ್ಯ ಕಾರಣಗಳು:",
        "te": "సంభవించే కారణాలు:",
        "ml": "സാധ്യമായ കാരണങ്ങൾ:"
    },
    "treatment": {
        "en": "Suggested Treatments:",
        "ta": "பரிந்துரைக்கப்பட்ட சிகிச்சைகள்:",
        "hi": "सुझाए गए उपचार:",
        "kn": "ಸೂಚಿಸಲಾದ ಚಿಕಿತ್ಸೆ:",
        "te": "సూచించిన చికిత్సలు:",
        "ml": "ശുപാർശ ചെയ്ത ചികിത്സകൾ:"
    }
}

def home(request):
    return render(request, "index.html")

@csrf_exempt
def process_text(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            user_text = data.get("text", "")
            ui_lang = data.get("lang", "en")

            if ui_lang not in SUPPORTED_LANGS:
                ui_lang = "en"

            detected_lang = detect_language(user_text)
            en_text = translate_to_en(user_text, detected_lang)
            response_en = generate_response_from_text(en_text)

            response_with_template = random.choice(TEMPLATES).format(answer=response_en)
            response_final = translate_from_en(response_with_template, ui_lang)

            return JsonResponse({"answer": response_final})
        except Exception as e:
            return JsonResponse({"error": f"Processing error: {str(e)}"}, status=500)
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
@require_POST
def predict_disease(request):
    image_file = request.FILES.get('image')
    ui_lang = request.POST.get('lang', 'en')  
    if ui_lang not in SUPPORTED_LANGS:
        ui_lang = "en"
    if not image_file:
        return JsonResponse({'error': 'No image uploaded.'}, status=400)   

    temp_path = default_storage.save('temp_upload.jpg', image_file)
    temp_full_path = default_storage.path(temp_path)

    try:
        result_text = analyze_image_from_file(temp_full_path)
        lines = result_text.split('\n')
        predicted_val = lines[0].split(":", 1)[1].strip() if len(lines) > 0 else ""
        causes_val = lines[1].split(":", 1)[1].strip() if len(lines) > 1 else ""
        treatment_val = lines[2].split(":", 1)[1].strip() if len(lines) > 2 else ""
        predicted_translated_val = translate_from_en(predicted_val, ui_lang)
        causes_translated_val = translate_from_en(causes_val, ui_lang)
        treatment_translated_val = translate_from_en(treatment_val, ui_lang)

        structured_result = (
            f"{TAGS['predicted'][ui_lang]} {predicted_translated_val}\n"
            f"{TAGS['causes'][ui_lang]} {causes_translated_val}\n"
            f"{TAGS['treatment'][ui_lang]} {treatment_translated_val}"
        )

        template_en = random.choice(TEMPLATES)
        full_text_en = template_en.format(answer=structured_result)
        full_text_translated = translate_from_en(full_text_en, ui_lang)
        result = {'disease': full_text_translated}

    except Exception as e:
        result = {'error': f"Prediction error: {str(e)}"}

    if os.path.exists(temp_full_path):
        os.remove(temp_full_path)
        
    return JsonResponse(result)
