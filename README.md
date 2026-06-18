# 🩺 Diagno-Amicus

**AI-Powered Clinical Decision Support and Health Risk Assessment Platform**

Diagno-Amicus is an intelligent healthcare assistant designed to provide comprehensive health risk analysis using machine learning, clinical reasoning, and medical knowledge systems. The platform combines multiple diagnostic modules including skin abnormality detection, heart disease risk assessment, diabetes prediction, and liver disease evaluation within a unified Streamlit-based application.

---

## Features

### 🔍 Comprehensive Health Analysis

* Multi-factor health evaluation
* Clinical reasoning engine
* AI-assisted interpretation of results
* Personalized risk assessment

### 🧴 Skin Abnormality Detection

* Deep learning-based skin image analysis
* Automated abnormality detection
* Image preprocessing and classification
* Risk estimation and diagnostic insights

### ❤️ Heart Disease Risk Prediction

* Cardiovascular risk assessment
* Clinical parameter evaluation
* Risk categorization and recommendations

### 🩸 Diabetes Risk Assessment

* Diabetes prediction using patient health metrics
* Risk stratification
* Clinical interpretation support

### 🫀 Liver Disease Risk Analysis

* Liver health assessment
* Biomarker-based prediction
* Risk evaluation and recommendations

### 📊 Dashboard & History

* Patient analysis history
* Interactive dashboard
* Visualized results and reports

### 🔐 Authentication & Data Management

* Firebase Authentication
* Secure user management
* Cloud-based storage integration

### 🤖 AI-Powered Clinical Reasoning

* Medical knowledge base integration
* Clinical interpretation engine
* Intelligent recommendation generation

---

## Technology Stack

### Frontend

* Streamlit

### Machine Learning & AI

* TensorFlow
* Keras
* Google Gemini AI

### Data Processing

* Pandas
* Pillow

### Visualization

* Plotly

### Backend Services

* Firebase Admin SDK

---

## Project Structure

```text
diagno-amicus/
│
├── app.py                         # Main Streamlit application
├── engine.py                      # Core diagnostic engine
├── run_prediction.py              # Prediction pipeline
├── abnormality_detector.py        # Skin abnormality detection
├── clinical_reasoner.py           # Clinical reasoning module
├── evaluator.py                   # Evaluation logic
├── medical_knowledge.py           # Medical knowledge base
├── probability_mapper.py          # Risk probability mapping
├── risk_models.py                 # Disease risk models
│
├── assets/                        # UI assets and styling
├── components/                    # Reusable Streamlit components
├── pages/                         # Application pages
├── config/                        # Configuration files
├── database/                      # Database utilities
├── dataset/                       # Training and testing datasets
├── skin_model/                    # Skin disease model files
├── training/                      # Model training scripts
└── Diagrams/                      # Architecture diagrams
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/your-username/diagno-amicus.git
cd diagno-amicus
```

### Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Required Dependencies

```text
streamlit>=1.31.0
pandas>=2.1.4
plotly>=5.18.0
firebase-admin>=6.5.0
google-generativeai>=0.8.0
keras>=3.0.0
pillow>=10.0.0
python-dotenv>=1.0.0
tensorflow>=2.19.0
```

---

## Firebase Configuration

Create a Firebase project and place your service account credentials file in the project root:

```text
serviceAccountKey.json
```

Configure Firebase settings according to your project requirements.

---

## Running the Application

```bash
streamlit run app.py
```

Application will be available at:

```text
http://localhost:8501
```

---

## Workflow

1. User logs into the platform.
2. Health metrics and patient information are provided.
3. Optional skin image is uploaded for analysis.
4. Diagnostic engine processes all available information.
5. Clinical reasoning module generates interpretations.
6. Risk models calculate disease probabilities.
7. Results are displayed through the dashboard.
8. Reports are stored in user history.

---

## Future Enhancements

* Additional disease prediction models
* Explainable AI (XAI) support
* PDF report generation
* Doctor recommendation system
* Multi-language support
* Real-time telemedicine integration
* EHR/EMR interoperability

---

## Disclaimer

This project is intended for educational, research, and decision-support purposes only. It does not replace professional medical diagnosis, treatment, or consultation. Users should always seek advice from qualified healthcare professionals.

---

## Authors

Developed as part of an AI-powered healthcare diagnostic assistance project.
Developer by Rohit Arabale,Soham Pawar,Arnav Nandanwar for college mini project

---

## License

This project is licensed under the MIT License.
