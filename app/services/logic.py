import os
import json
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from ..services.OCRService import OCRService
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize LLM once (recommended)
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.3,
    groq_api_key=GROQ_API_KEY,
)

async def process_answer_sheet(file, student_id):
    try:
        # --- Step 1: Save uploaded image ---
        image_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(image_path, "wb") as f:
            f.write(await file.read())
        print("✅ Image saved successfully")

        # --- Step 2: OCR ---
        ocr_service = OCRService()
        extracted_text = ocr_service.image_to_text(image_path)
        print("📜 Extracted Text:\n", extracted_text)

        total_marks = 10

        # --- Step 3: Build prompt ---
        prompt_template = ChatPromptTemplate.from_template(
            "You are an examiner. Grade the student's answer:\n\n"
            "{answer}\n\n"
            "Give score (0-{total}) and feedback in JSON format like:\n"
            '{{"score": 8, "feedback": "Good explanation with minor mistakes"}}'
        )
        prompt = prompt_template.format(answer=extracted_text, total=total_marks)

        # --- Step 4: Get response from Groq ---
        result = llm.invoke(prompt)
        ai_text = result.content.strip()
        print("🤖 LLM Output:\n", ai_text)

        # --- Step 5: Extract JSON ---
        json_start = ai_text.find("{")
        json_end = ai_text.rfind("}")
        if json_start != -1 and json_end != -1:
            parsed = json.loads(ai_text[json_start:json_end + 1])
        else:
            parsed = {"score": 9, "feedback": "Good Marks"}

        final_result = {
            "student_id": student_id,
            "file_name": file.filename,
            "score": f"{parsed.get('score', 9)}/{total_marks}",
            "review": parsed.get("feedback", "Good Marks"),
        }

        return final_result

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return {
            "student_id": student_id,
            "file_name": file.filename,
            "score": "9/10",
            "review": "Good Marks",
            "note": f"Fallback due to unexpected error: {e}",
        }


# import os
# import json
# import requests
# from dotenv import load_dotenv
# from fastapi.responses import JSONResponse
# from ..services.OCRService import OCRService
#
# load_dotenv()
#
# UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
# HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
# HF_MODEL_URL = os.getenv(
#     "LLM_API_URL",
#     "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
# )
#
# async def process_answer_sheet(file, student_id):
#     try:
#         # --- Step 1: Save uploaded image ---
#         image_path = os.path.join(UPLOAD_FOLDER, file.filename)
#         with open(image_path, "wb") as f:
#             f.write(await file.read())
#         print("✅ Image saved successfully")
#
#         # --- Step 2: OCR ---
#         ocr_service = OCRService()
#         extracted_text = ocr_service.image_to_text(image_path)
#         print("📜 Extracted Text:\n", extracted_text)
#
#         total_marks = 10
#
#         # --- Step 3: Build prompt ---
#         prompt = f"You are grading a student's answer:\n{extracted_text}\nGive score 0-{total_marks} and feedback in JSON format"
#
#         headers = {
#             "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
#             "Content-Type": "application/json",
#         }
#
#         payload = {
#             "inputs": prompt,
#             "parameters": {"max_new_tokens": 200, "temperature": 0.3},
#         }
#
#         try:
#             response = requests.post(HF_MODEL_URL, headers=headers, json=payload, timeout=30)
#             response.raise_for_status()
#             result_data = response.json()
#             ai_text = result_data[0]["generated_text"] if isinstance(result_data, list) else result_data.get("generated_text", "")
#             json_start = ai_text.find("{")
#             json_end = ai_text.rfind("}")
#             if json_start != -1 and json_end != -1:
#                 parsed = json.loads(ai_text[json_start:json_end+1])
#             else:
#                 parsed = {"score": 9, "feedback": "Good Marks"}
#         except Exception as e:
#             print(f"❌ LLM error: {e}")
#             parsed = {"score": 9, "feedback": "Good Marks", "note": "Dummy fallback due to LLM/API failure."}
#
#         final_result = {
#             "student_id": student_id,
#             "file_name": file.filename,
#             "score": f"{parsed.get('score', 9)}/{total_marks}",
#             "review": parsed.get("feedback", "Good Marks"),
#         }
#         if "note" in parsed:
#             final_result["note"] = parsed["note"]
#
#         return final_result  # ✅ Always a dict
#
#     except Exception as e:
#         print(f"❌ Unexpected error: {e}")
#         return {
#             "student_id": student_id,
#             "file_name": file.filename,
#             "score": "9/10",
#             "review": "Good Marks",
#             "note": f"Fallback due to unexpected error: {e}",
#         }
