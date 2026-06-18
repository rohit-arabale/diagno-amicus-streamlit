import html
import os
import re

API_KEY = os.getenv("GEMINI_API_KEY")

model = None
if API_KEY:
    try:
        import google.generativeai as genai

        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
    except ModuleNotFoundError:
        model = None


DISEASE_GUIDANCE = {
    "Heart Disease": {
        "explanation": "This screening suggests a potential cardiovascular risk based on your inputs, such as cholesterol, blood pressure, or heart rate.",
        "causes": "Risk may be related to high cholesterol, raised blood pressure, diabetes, smoking, obesity, stress, inactivity, age, or family history.",
        "symptoms": "Chest discomfort, breathlessness, unusual sweating, dizziness, palpitations, fatigue, or pain spreading to the arm, jaw, back, or shoulder may occur. Some people have no early symptoms.",
        "precautions": "Avoid high-sodium and high-fat foods, manage stress, stay active as tolerated, avoid smoking, and monitor your blood pressure.",
        "treatment": "Consult a cardiologist for a comprehensive evaluation, which may include an ECG, stress test, or blood work.",
    },
    "Diabetes": {
        "explanation": "This screening indicates possible metabolic markers consistent with diabetes or prediabetes risk.",
        "causes": "Risk may be influenced by insulin resistance, family history, excess body weight, inactivity, diet pattern, age, or previous abnormal glucose readings.",
        "symptoms": "Increased thirst, frequent urination, fatigue, blurred vision, slow wound healing, unexplained weight change, or recurrent infections may occur.",
        "precautions": "Monitor carbohydrate intake, maintain regular physical activity, and track your blood glucose levels.",
        "treatment": "Follow up with an endocrinologist or primary care doctor for an HbA1c test and personalized management plan.",
    },
    "Liver Disease": {
        "explanation": "This assessment highlights potential liver function abnormalities based on your enzyme or bilirubin levels.",
        "causes": "Possible contributors include viral hepatitis, fatty liver disease, alcohol use, medication effects, bile duct problems, metabolic disorders, or other inflammatory conditions.",
        "symptoms": "Fatigue, nausea, abdominal discomfort, dark urine, pale stools, itching, swelling, easy bruising, or yellowing of the skin or eyes may occur.",
        "precautions": "Avoid alcohol consumption, limit processed foods, and avoid medications that stress the liver without a doctor's advice.",
        "treatment": "Consult a hepatologist or gastroenterologist for further tests, such as a liver ultrasound or comprehensive metabolic panel.",
    },
    "Actinic Keratosis": {
        "explanation": "A rough, scaly skin patch caused by repeated sun exposure. It should be reviewed because some lesions may progress over time.",
        "causes": "Long-term ultraviolet exposure, fair skin, older age, outdoor work, tanning-bed use, or reduced immunity can increase risk.",
        "symptoms": "A dry, rough, scaly, pink, red, or brown patch may be felt more easily than seen and can become tender, itchy, or crusted.",
        "precautions": "Use sunscreen, avoid excess sun exposure, do not scratch the area, and monitor for bleeding or rapid change.",
        "treatment": "A dermatologist may recommend cryotherapy, medicated creams, photodynamic therapy, or biopsy when appropriate.",
    },
    "Basal Cell Carcinoma": {
        "explanation": "A common slow-growing skin cancer that often appears on sun-exposed skin.",
        "causes": "Cumulative sun exposure, indoor tanning, fair skin, prior skin cancer, radiation exposure, or reduced immunity may contribute.",
        "symptoms": "It may appear as a pearly bump, shiny patch, non-healing sore, scar-like area, crusting spot, or lesion that bleeds and heals repeatedly.",
        "precautions": "Arrange a dermatology review, protect the area from sunlight, and monitor for crusting, pain, growth, or bleeding.",
        "treatment": "Treatment may include surgical removal, topical treatment, curettage, or another dermatologist-directed procedure.",
    },
    "Benign Keratosis": {
        "explanation": "A usually non-cancerous skin growth that may look waxy, scaly, or raised.",
        "causes": "These lesions are often related to aging, genetics, friction, or previous sun exposure and are commonly benign.",
        "symptoms": "A waxy, stuck-on, rough, tan, brown, or dark lesion may be present and can become itchy or irritated.",
        "precautions": "Avoid picking the lesion, protect the skin from sunlight, and seek review if it changes quickly or becomes symptomatic.",
        "treatment": "Treatment is often unnecessary unless the lesion becomes irritated, uncertain, or cosmetically concerning.",
    },
    "Dermatofibroma": {
        "explanation": "A common benign firm skin nodule that may appear after minor skin trauma.",
        "causes": "It may follow insect bites, minor trauma, folliculitis, or localized skin inflammation.",
        "symptoms": "A small firm bump, often on the legs, may be pink, brown, or dark and can dimple inward when pinched.",
        "precautions": "Avoid repeated irritation and monitor for unusual growth, pain, or color change.",
        "treatment": "Observation is usually enough, although removal or biopsy may be considered if the diagnosis is uncertain.",
    },
    "Melanoma": {
        "explanation": "A serious skin cancer that requires prompt medical attention because it can spread if not treated early.",
        "causes": "Risk may be higher with intense ultraviolet exposure, tanning beds, many moles, atypical moles, fair skin, family history, or reduced immunity.",
        "symptoms": "Warning signs include asymmetry, irregular borders, multiple colors, increasing diameter, evolution, bleeding, itching, pain, or a new unusual lesion.",
        "precautions": "Arrange urgent dermatology review, avoid additional sun exposure, and do not delay biopsy if recommended.",
        "treatment": "Treatment depends on stage and commonly begins with specialist assessment and surgical excision.",
    },
    "Nevi": {
        "explanation": "A mole or melanocytic nevus that is often benign but should be monitored for suspicious changes.",
        "causes": "Moles may be related to genetics, sun exposure, skin type, age, and normal melanocyte growth patterns.",
        "symptoms": "Most are stable brown, tan, or skin-colored spots. Concerning changes include asymmetry, border change, color variation, growth, bleeding, itching, or pain.",
        "precautions": "Use sunscreen and watch for asymmetry, border change, color change, larger diameter, or evolution over time.",
        "treatment": "No treatment is usually required unless the lesion changes, becomes symptomatic, or needs clinical review.",
    },
    "Vascular Lesion": {
        "explanation": "A lesion related to blood vessels that is often benign but can vary in appearance.",
        "causes": "These can be related to dilated or clustered blood vessels, aging, trauma, genetics, hormones, or vascular growth patterns.",
        "symptoms": "A red, purple, blue, or dark spot or bump may be present and can sometimes bleed if injured.",
        "precautions": "Avoid injury to the area and seek review if it grows, bleeds, or changes color.",
        "treatment": "Management depends on the lesion type and symptoms, and may include observation, laser treatment, or removal.",
    },
}

SECTION_ORDER = [
    "Clinical Summary",
    "Possible Causes",
    "Common Symptoms",
    "Precautions",
    "Suggested Next Step",
    "Lifestyle Guidance",
    "When to Seek Medical Care",
]

SECTION_ALIASES = {
    "clinical summary": "Clinical Summary",
    "summary": "Clinical Summary",
    "possible causes": "Possible Causes",
    "possible cause": "Possible Causes",
    "common symptoms": "Common Symptoms",
    "common symptom": "Common Symptoms",
    "symptoms": "Common Symptoms",
    "precautions": "Precautions",
    "precaution": "Precautions",
    "suggested next step": "Suggested Next Step",
    "suggested next steps": "Suggested Next Step",
    "next step": "Suggested Next Step",
    "next steps": "Suggested Next Step",
    "lifestyle guidance": "Lifestyle Guidance",
    "lifestyle advice": "Lifestyle Guidance",
    "lifestyle recommendations": "Lifestyle Guidance",
    "when to seek medical care": "When to Seek Medical Care",
    "when to seek care": "When to Seek Medical Care",
    "when to get medical care": "When to Seek Medical Care",
    "important note": "Important Note",
}

METADATA_ALIASES = {
    "patient name": "Patient Name",
    "condition": "Condition",
    "disease name": "Condition",
    "model confidence": "Model Confidence",
    "confidence": "Model Confidence",
}


def _strip_markup(line):
    cleaned = html.unescape(line.strip())
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned)
    cleaned = cleaned.strip()
    while len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in "*_`":
        cleaned = cleaned[1:-1].strip()
    return re.sub(r"\s+", " ", cleaned).strip()


def _match_metadata(line):
    cleaned = _strip_markup(line)
    match = re.match(
        r"^(Patient Name|Condition|Disease Name|Model Confidence|Confidence)\s*[:\-]\s*(.+)$",
        cleaned,
        re.IGNORECASE,
    )
    if not match:
        return None, None
    key = METADATA_ALIASES.get(match.group(1).strip().casefold())
    value = match.group(2).strip()
    return key, value


def _match_section_heading(line):
    cleaned = _strip_markup(line)
    cleaned = re.sub(r"^\d+[\.\)]\s*", "", cleaned).strip()
    cleaned = cleaned.strip("*_` ").strip()
    lowered = cleaned.casefold()

    for alias in sorted(SECTION_ALIASES, key=len, reverse=True):
        if lowered == alias:
            return SECTION_ALIASES[alias], ""
        if lowered.startswith(f"{alias}:"):
            inline = cleaned[len(alias):].lstrip(" :.-")
            return SECTION_ALIASES[alias], inline

    return None, None


def _default_report_parts(disease, confidence, patient_name="Patient"):
    guidance = DISEASE_GUIDANCE.get(
        disease,
        {
            "explanation": f"This screening suggests an increased likelihood of {disease}.",
            "precautions": "Monitor symptoms, review the result with a qualified clinician, and avoid self-diagnosis.",
            "treatment": "Management depends on a proper medical evaluation and confirmatory testing.",
        },
    )
    metadata = {
        "Patient Name": patient_name,
        "Condition": disease,
        "Model Confidence": f"{confidence:.2f}%",
    }
    sections = {
        "Clinical Summary": guidance["explanation"],
        "Possible Causes": guidance.get("causes", "This result may be influenced by biomarker abnormalities, lifestyle factors, family history, or an underlying health condition."),
        "Common Symptoms": guidance.get("symptoms", "Symptoms vary by condition, and some people may not notice obvious symptoms in the early stage."),
        "Precautions": guidance["precautions"],
        "Suggested Next Step": guidance["treatment"],
        "Lifestyle Guidance": "Maintain a balanced diet, stay physically active, sleep well, and follow up on abnormal health trends.",
        "When to Seek Medical Care": "Arrange medical review promptly if symptoms are severe, worsening, persistent, or clinically concerning.",
    }
    note = "This AI-generated report is for educational screening support only and is not a final medical diagnosis."
    return metadata, sections, note


def _parse_report_parts(report_text):
    metadata = {}
    sections = {}
    note = ""
    current_title = None
    current_lines = []

    def flush_section():
        nonlocal note, current_title, current_lines
        if not current_title:
            return
        body = "\n".join(line for line in current_lines if line).strip()
        if current_title == "Important Note":
            if body:
                note = body
        elif body:
            sections[current_title] = body
        current_title = None
        current_lines = []

    for raw_line in report_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        meta_key, meta_value = _match_metadata(line)
        if meta_key and current_title is None:
            metadata[meta_key] = meta_value
            continue

        section_title, inline_value = _match_section_heading(line)
        if section_title:
            flush_section()
            current_title = section_title
            if inline_value:
                current_lines.append(inline_value)
            continue

        cleaned = _strip_markup(line)
        if current_title:
            current_lines.append(cleaned)

    flush_section()
    return metadata, sections, note


def _compose_report(metadata, sections, note):
    lines = [
        f"Patient Name: {metadata['Patient Name']}",
        f"Condition: {metadata['Condition']}",
        f"Model Confidence: {metadata['Model Confidence']}",
        "",
    ]

    for index, title in enumerate(SECTION_ORDER, start=1):
        lines.append(f"{index}. {title}")
        lines.append(sections[title])
        lines.append("")

    lines.append("Important Note")
    lines.append(note)
    return "\n".join(lines).strip()


def _normalize_report(report_text, disease, confidence, patient_name="Patient"):
    default_metadata, default_sections, default_note = _default_report_parts(
        disease,
        confidence,
        patient_name,
    )
    parsed_metadata, parsed_sections, parsed_note = _parse_report_parts(report_text)

    metadata = {**default_metadata, **{k: v for k, v in parsed_metadata.items() if v}}
    sections = default_sections.copy()
    for title, body in parsed_sections.items():
        if body:
            sections[title] = body
    note = parsed_note or default_note

    return _compose_report(metadata, sections, note)


def _fallback_report(disease, confidence, patient_name="Patient"):
    metadata, sections, note = _default_report_parts(disease, confidence, patient_name)
    return _compose_report(metadata, sections, note)


def generate_medical_report(disease, confidence, patient_name="Patient"):
    if model is None:
        return _fallback_report(disease, confidence, patient_name)

    try:
        prompt = f"""
You are a professional medical writing assistant.

Create a clear, readable, patient-friendly medical screening report using the details below.

Patient Name: {patient_name}
Condition: {disease}
Confidence: {confidence:.2f}%

Use this structure:
Patient Name
Condition
Model Confidence
1. Clinical Summary
2. Possible Causes
3. Common Symptoms
4. Precautions
5. Suggested Next Step
6. Lifestyle Guidance
7. When to Seek Medical Care
Important Note

For each numbered section, write 1 to 3 concise sentences.
Do not invent medication names, doses, dates of birth, clinician names, hospital names, claim numbers, or confirmed diagnoses.
Keep the wording professional, simple, medically cautious, and suitable for a patient to read.
The final note must say that this is educational screening support and not a final diagnosis.
"""

        response = model.generate_content(prompt)
        return _normalize_report(response.text, disease, confidence, patient_name)
    except Exception as e:
        return _normalize_report(
            f"AI report generation error: {e}\n\n{_fallback_report(disease, confidence, patient_name)}",
            disease,
            confidence,
            patient_name,
        )
