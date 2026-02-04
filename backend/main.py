from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

from cnn_model import predict_image
from models import ChatRequest, ChatResponse
from database import knowledge_base

app = FastAPI(title="AgriAssist API", version="3.0")

# -------------------------------------------------
# CORS
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow all origins (mobile / web)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Gemini Configuration
# -------------------------------------------------
# Uses env variable if set, else your existing key string
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    "---------"  # your current fallback
)

if GEMINI_API_KEY != "YOUR_API_KEY":
    genai.configure(api_key=GEMINI_API_KEY)


# -------------------------------------------------
# CNN Prediction Endpoint
# -------------------------------------------------
@app.post("/predict-cnn")
async def predict_cnn(file: UploadFile = File(...)):
    """
    1. Receive leaf image from frontend.
    2. Use shared CNN model (cnn_model.py) to predict.
    3. Return numeric prediction + confidence.
       - For now: 0 = Healthy leaf, 1 = Apple Scab
       - Frontend converts to text like "Apple Scab detected".
    """
    try:
        img_bytes = await file.read()
        result = predict_image(img_bytes)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        # result: { "prediction": 0/1, "confidence": float }
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------
# Chat Endpoint (RAG + Gemini)
# -------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Conversational RAG + LLM:
    - Uses user question
    - Uses CNN prediction when available
    - Uses FAISS vector DB for disease info
    - If DB has no info, Gemini still answers using general agriculture knowledge
    - If question is not about agriculture, reply:
      "Please ask something related to agriculture."
    """
    user_msg = request.message
    lang = request.language or "English"
    cnn_pred = request.cnn_prediction  # can be None, 0, or 1 (for now)

    # 1) RAG Search (may return empty list)
    rag_results = knowledge_base.search_diseases(user_msg, n_results=3)

    # 2) Build short context text from retrieved diseases
    context_parts = []
    for d in rag_results:
        context_parts.append(
            f"Crop: {d.crop}. Disease: {d.disease_name}. "
            f"Symptoms: {d.symptoms}. Solution: {d.solution}. Prevention: {d.prevention}."
        )
    context_text = " ".join(context_parts)

    if not context_text:
        context_text = (
            "No specific disease information was found in the database for this query. "
            "You must still answer using your general agriculture knowledge."
        )

    # 3) CNN hint based on image result (binary for now)
    if cnn_pred == 1:
        cnn_text = (
            "The leaf image suggests Apple Scab disease. "
            "Focus on Apple Scab treatment and prevention for the answer."
        )
    elif cnn_pred == 0:
        cnn_text = (
            "The leaf image suggests a healthy plant. "
            "Explain general good practices and early prevention tips."
        )
    else:
        cnn_text = (
            "No image analysis was used. Answer using only the question and database information."
        )

    # 4) Prompt for Gemini
    prompt = f"""
You are AgriAssist, an agriculture assistant for farmers.

User language: {lang}
Image analysis: {cnn_text}
Database information: {context_text}

User question: {user_msg}

VERY IMPORTANT RULES:

1. DOMAIN LIMIT:
   - Only answer questions related to agriculture, crops, soil, water for farming, plant diseases, pesticides, fertilizers, weather for crops, and farm practices.
   - If the question is NOT about agriculture or farming, reply exactly:
     "Please ask something related to agriculture."
   - Do NOT answer about politics, movies, coding, gossip, finance, or any other non-agriculture topic.

2. USE DATABASE AND IMAGE:
   - If database information mentions a disease, use it as the main reference.
   - If image analysis says Apple Scab, assume the plant has Apple Scab unless the question is clearly different.
   - If database information is empty, still answer using your general agriculture knowledge.

3. ANSWER STYLE:
   - Reply in {lang}.
   - Use very simple words suitable for farmers.
   - Use 3 to 5 short sentences only.
   - No technical or scientific jargon.
   - Give direct, practical steps (what to do now, what to avoid, how to prevent).
   - If you are not fully sure, write one sentence like:
     "For exact advice, please also ask a local agriculture expert."

Now give your final answer for the farmer.
"""

    # 5) Gemini Response
    try:
        if GEMINI_API_KEY != "YOUR_API_KEY":
            gemini_model = genai.GenerativeModel("gemini-2.5-flash")
            res = gemini_model.generate_content(prompt)
            reply = res.text
        else:
            reply = "Please setup Gemini API key."

        return ChatResponse(
            response=reply,
            source_diseases=rag_results,
            language=lang,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------
# Health Check (used by frontend if needed)
# -------------------------------------------------
@app.get("/")
def home():
    """
    Simple health endpoint.
    Can also be used by frontend to show 'Online' status.
    """
    return {"status": "healthy"}
