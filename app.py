from flask import Flask, render_template, request, jsonify
from collections import deque
import re
import base64
import io

app = Flask(__name__)

# Store last 5 analyses for history
history = deque(maxlen=5)

# ========== IMAGE PROCESSING FUNCTION (Simple Version - No OpenCV) ==========
def analyze_wound_image(image_base64):
    """
    Simple image analysis for wound/burn detection
    Uses basic color analysis without heavy dependencies
    """
    try:
        # Remove data:image prefix if present
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        # Decode base64 to image
        image_bytes = base64.b64decode(image_base64)
        
        # Try to import PIL (optional - agar installed hai to use karo)
        try:
            from PIL import Image
            import numpy as np
            
            image = Image.open(io.BytesIO(image_bytes))
            # Convert to RGB
            image = image.convert('RGB')
            # Resize for faster processing
            image.thumbnail((200, 200))
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Calculate average redness
            if len(img_array.shape) == 3:
                red_channel = img_array[:, :, 0]
                avg_red = np.mean(red_channel)
                
                # Simple redness detection
                if avg_red > 180:
                    return {
                        "severity": "🔴 HIGH SEVERITY",
                        "color": "red",
                        "analysis": "High inflammation detected! This appears to be a significant burn or infected wound.",
                        "advice": "🚨 Consult a doctor immediately. Do not apply home remedies.",
                        "firstaid": "Keep area clean, cover with sterile cloth, seek medical help."
                    }
                elif avg_red > 120:
                    return {
                        "severity": "🟡 MEDIUM SEVERITY",
                        "color": "yellow",
                        "analysis": "Moderate redness detected. This could be a minor burn or healing wound.",
                        "advice": "Apply antiseptic cream and keep covered. Monitor for infection.",
                        "firstaid": "Clean with mild soap, apply burn cream, cover with bandage."
                    }
                elif avg_red > 80:
                    return {
                        "severity": "🟢 LOW SEVERITY",
                        "color": "green",
                        "analysis": "Mild redness detected. This appears to be a minor irritation.",
                        "advice": "Home care is sufficient. Keep the area clean.",
                        "firstaid": "Wash with water, apply moisturizer, avoid scratching."
                    }
                else:
                    return {
                        "severity": "⚪ NORMAL",
                        "color": "gray",
                        "analysis": "No significant redness detected. Image appears normal.",
                        "advice": "Continue regular hygiene. No immediate concern.",
                        "firstaid": "Keep area clean and dry."
                    }
            else:
                return {
                    "severity": "⚠️ CANNOT ANALYZE",
                    "color": "gray",
                    "analysis": "Could not process image properly. Please upload a clear photo.",
                    "advice": "Make sure image is clear and well-lit.",
                    "firstaid": "For any wound, clean with water and consult doctor if concerned."
                }
        except ImportError:
            # Agar PIL installed nahi hai to basic response
            return {
                "severity": "🟡 IMAGE ANALYSIS (BASIC)",
                "color": "yellow",
                "analysis": "Image received but advanced analysis requires PIL library.",
                "advice": "For wound/burn, clean with water and apply antiseptic.",
                "firstaid": "Keep area clean, cover with bandage, consult doctor if severe."
            }
            
    except Exception as e:
        return {
            "severity": "⚠️ ERROR",
            "color": "gray",
            "analysis": f"Error analyzing image.",
            "advice": "Please try uploading again with a clearer image.",
            "firstaid": "For medical emergencies, call 108 immediately."
        }

# ========== ORIGINAL ANALYZE FUNCTION ==========
def analyze(text):
    original_text = text.lower()
    
    # Hindi to English mapping
    hindi_words = {
        'dil': 'heart', 'seenay mein dard': 'chest pain', 'dard': 'pain',
        'bukhar': 'fever', 'tapman': 'temperature', 'khansi': 'cough',
        'sardi': 'cold', 'chakkar': 'dizziness', 'ultiyaan': 'vomiting',
        'dast': 'diarrhea', 'pet dard': 'stomach pain', 'katna': 'bite',
        'jalaan': 'burn', 'khoon': 'bleeding', 'saans': 'breath',
        'gala band': 'choking', 'accident': 'accident', 'girna': 'fall'
    }
    
    # Convert Hindi words to English
    for hindi, eng in hindi_words.items():
        if hindi in original_text:
            original_text = original_text.replace(hindi, eng)
    
    text = original_text
    
    # HEART ATTACK
    if any(w in text for w in ["heart", "chest pain", "attack", "heart attack", "cardiac"]):
        return {
            "condition": "Heart Emergency",
            "level": "🔴 HIGH",
            "level_color": "red",
            "analysis": "Possible cardiac issue detected - This needs immediate medical attention!",
            "steps": ["📞 Call emergency 108 IMMEDIATELY", "💆 Keep patient calm and seated", "🚫 Do not let them move or walk", "💊 If aspirin is available and not allergic, chew one", "🫀 Loosen tight clothing"],
            "emergency_contact": "108 - Ambulance"
        }

    # ACCIDENT / TRAUMA
    elif any(w in text for w in ["accident", "injury", "crash", "fall", "hurt badly", "blood"]):
        return {
            "condition": "Accident / Trauma",
            "level": "🔴 HIGH",
            "level_color": "red",
            "analysis": "Physical injury detected - Check for bleeding and consciousness",
            "steps": ["🩸 Apply pressure to stop bleeding", "🚑 Call ambulance immediately (108)", "🛑 Do not move patient if back/neck injury suspected", "❄️ Apply ice pack on swelling", "🏥 Take to nearest hospital"],
            "emergency_contact": "108 - Ambulance"
        }

    # BREATHING / CHOKING
    elif any(w in text for w in ["choke", "breath", "suffocation", "not breathing", "saans", "gala"]):
        return {
            "condition": "Breathing Emergency",
            "level": "🔴 HIGH",
            "level_color": "red",
            "analysis": "Airway obstruction or breathing problem detected",
            "steps": ["🫁 Check if person is breathing", "🆘 Call emergency immediately (108)", "💪 Perform Heimlich maneuver if choking", "🫀 Start CPR if not breathing", "📞 Ask someone to bring AED if available"],
            "emergency_contact": "108 - Ambulance"
        }

    # ANIMAL BITE
    elif any(w in text for w in ["dog bite", "animal bite", "bite", "cat bite", "snake bite", "katna"]):
        return {
            "condition": "Animal Bite Injury",
            "level": "🔴 HIGH",
            "level_color": "red",
            "analysis": "Risk of rabies or venomous bite - URGENT medical care needed",
            "steps": ["🧼 Wash wound with soap and water for 15 minutes", "🩹 Apply antiseptic (betadine)", "🏥 Go to hospital URGENTLY", "💉 Take anti-rabies vaccine immediately", "📝 Note animal description if possible"],
            "emergency_contact": "108 - Ambulance"
        }

    # SEVERE BURNS
    elif any(w in text for w in ["burn", "jalaan", "fire", "hot water", "scald"]):
        return {
            "condition": "Burn Injury",
            "level": "🔴 HIGH",
            "level_color": "red",
            "analysis": "Thermal injury detected - Immediate cooling required",
            "steps": ["💧 Cool under running water for 15-20 minutes", "🧴 Do NOT apply ice, butter, or toothpaste", "🩹 Cover with clean, non-stick cloth", "💊 Take pain killer if needed", "🏥 Seek medical help for severe burns"],
            "emergency_contact": "108 - Ambulance"
        }

    # FEVER
    elif any(w in text for w in ["fever", "temperature", "high fever", "bukhar", "tapman", "102", "103", "104"]):
        return {
            "condition": "Fever / Viral Infection",
            "level": "🟡 MEDIUM",
            "level_color": "yellow",
            "analysis": "Possible infection or viral fever - Monitor temperature",
            "steps": ["🌡️ Check temperature every 4 hours", "💧 Drink plenty of water and ORS", "😴 Take complete rest", "💊 Take paracetamol if fever > 101°F", "👨‍⚕️ Consult doctor if fever persists beyond 3 days"],
            "emergency_contact": "Call doctor or 108 if very high"
        }

    # COUGH
    elif any(w in text for w in ["cough", "khasi", "dry cough", "wet cough", "cold cough"]):
        return {
            "condition": "Cough / Respiratory Issue",
            "level": "🟡 MEDIUM",
            "level_color": "yellow",
            "analysis": "Respiratory irritation detected - Likely viral or allergic",
            "steps": ["🍵 Drink warm water with honey and ginger", "💨 Steam inhalation 2-3 times daily", "🌙 Use extra pillow while sleeping", "🚫 Avoid cold drinks and ice cream", "👨‍⚕️ Consult doctor if persists > 1 week"],
            "emergency_contact": "Consult local physician"
        }

    # COLD
    elif any(w in text for w in ["cold", "sardi", "sinus", "runny nose", "blocked nose"]):
        return {
            "condition": "Cold / Sinus Congestion",
            "level": "🟢 LOW",
            "level_color": "green",
            "analysis": "Common cold or sinus congestion - Usually resolves with home care",
            "steps": ["💨 Take steam inhalation with menthol", "🧂 Use saline nasal spray", "🛌 Take adequate rest", "🥣 Eat warm soup and fluids", "🧴 Use vaporub on chest and nose"],
            "emergency_contact": "Home care, consult if severe"
        }

    # VOMITING
    elif any(w in text for w in ["vomiting", "nausea", "ultiyaan", "matli"]):
        return {
            "condition": "Vomiting / Nausea",
            "level": "🟡 MEDIUM",
            "level_color": "yellow",
            "analysis": "Stomach upset or food poisoning possible",
            "steps": ["💧 Sip water or ORS slowly", "🍪 Eat small amounts of dry crackers", "😴 Rest completely", "🚫 Avoid solid food for 4-6 hours", "👨‍⚕️ Consult doctor if blood in vomit"],
            "emergency_contact": "108 if severe dehydration"
        }

    # DIZZINESS
    elif any(w in text for w in ["dizziness", "chakkar", "fainting", "unconscious", "weakness"]):
        return {
            "condition": "Dizziness / Weakness",
            "level": "🟡 MEDIUM",
            "level_color": "yellow",
            "analysis": "Possible low BP, dehydration, or anemia",
            "steps": ["🪑 Sit or lie down immediately", "💧 Drink water or glucose drink", "🍬 Eat something sweet", "👨‍⚕️ Consult doctor if recurrent"],
            "emergency_contact": "108 if unconscious"
        }

    # DEFAULT
    else:
        return {
            "condition": "General Health Query",
            "level": "🟢 LOW",
            "level_color": "green",
            "analysis": "Symptoms not clearly recognized. Please provide more specific symptoms.",
            "steps": ["📝 Describe your symptoms clearly", "🌡️ Check temperature", "📞 Call 108 for emergency", "👨‍⚕️ Consult doctor"],
            "emergency_contact": "108 for emergencies"
        }

# ========== IMAGE UPLOAD ROUTE ==========
@app.route("/analyze_image", methods=["POST"])
def analyze_image():
    """Handle image upload and return analysis"""
    try:
        data = request.get_json()
        image_data = data.get("image_data", "")
        
        if not image_data:
            return jsonify({"success": False, "error": "No image received"})
        
        result = analyze_wound_image(image_data)
        return jsonify({"success": True, "result": result})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ========== MAIN HOME ROUTE ==========
@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    current_query = None
    
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        current_query = text
        
        if not text:
            result = {
                "condition": "No Input Received",
                "level": "⚪",
                "level_color": "gray",
                "analysis": "Please describe your symptoms or emergency situation",
                "steps": ["📝 Type your symptoms in the box above", "💬 Be specific about what you're feeling", "📞 Or call 108 directly for medical emergencies"],
                "emergency_contact": "108 - Emergency Helpline"
            }
        elif len(text) < 3:
            result = {
                "condition": "Insufficient Information",
                "level": "⚪",
                "level_color": "gray",
                "analysis": "Please provide more details about your symptoms",
                "steps": ["📝 Add more details (minimum 3 characters)", "🔄 Try again with more information"],
                "emergency_contact": "108 - Emergency Helpline"
            }
        else:
            result = analyze(text)
            history.appendleft({
                "symptoms": text[:50] + "..." if len(text) > 50 else text,
                "condition": result["condition"],
                "level": result["level"]
            })
    
    return render_template("index.html", result=result, history=list(history), query=current_query)


if __name__ == "__main__":
    app.run(debug=True)