import os
import numpy as np
import onnxruntime as ort
from .models import SymptomEntry
from PIL import Image
from typing import List, Optional


MODEL_DIR = os.path.dirname(__file__)
ONNX_MODEL_PATH = os.path.join(MODEL_DIR, "best_model.onnx")
CLASS_NAMES_FILE = os.path.join(MODEL_DIR, "class_names.txt")
IMG_SIZE = (128, 128)


def _load_class_names() -> Optional[List[str]]:
    if os.path.isfile(CLASS_NAMES_FILE):
        try:
            with open(CLASS_NAMES_FILE, "r", encoding="utf-8") as f:
                names = [line.strip() for line in f if line.strip()]
            if names:
                return names
        except Exception as e:
            print("Failed to read class_names.txt:", e)
    return None

CLASS_NAMES = _load_class_names() or [f"class{i}" for i in range(10)]

def analyze_image_from_file(f):
    if not os.path.isfile(ONNX_MODEL_PATH):
        return (
            "ONNX model not available. Place 'best_model.onnx' inside agrobot_app/. Optionally add "
            "'class_names.txt' with one label per line."
        )
    try:
        img = Image.open(f).convert('RGB')
        img = img.resize(IMG_SIZE)
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0).astype(np.float32)

        session = ort.InferenceSession(ONNX_MODEL_PATH)
        input_name = session.get_inputs()[0].name
        preds = session.run(None, {input_name: img_array})[0]
        predicted_class = int(np.argmax(preds[0]))
        confidence = float(np.max(preds[0]))
        
        if predicted_class < len(CLASS_NAMES):
            label = CLASS_NAMES[predicted_class]
        else:
            label = f"class_{predicted_class}"
        entry = SymptomEntry.objects.filter(symptom__iexact=label).first()
        if entry:
            causes = entry.possible_causes
            treatments = entry.treatments.replace("|", "; ")
            return (
                f"Predicted Disease: {label} (Confidence: {confidence:.2f})\n"
                f"Possible Causes: {causes}\n"
                f"Suggested Treatments: {treatments}"
            )
        else:
            return f"Predicted Disease: {label} (Confidence: {confidence:.2f})."
    except Exception as e:
        return f"Error analyzing image: {str(e)}"