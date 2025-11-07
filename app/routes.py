from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import JSONResponse
from app.services.logic import process_answer_sheet
from app.services.db import insert_result, fetch_all_results

router = APIRouter()

from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import JSONResponse

from app.services.db import insert_result, fetch_all_results


router = APIRouter()
from bson import ObjectId

def convert_objectid_to_str(data):
    """Recursively convert MongoDB ObjectIds to strings."""
    if isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

@router.post("/evaluate")
async def evaluate_answer(file: UploadFile, student_id: str = Form(...)):
        try:
            result = await process_answer_sheet(file, student_id)
            print("Results from controller:", result)

            try:
                inserted = insert_result(result)  # or await insert_result(result)
                print("✅ Insert into DB passed")

                # Convert any ObjectId in the inserted result or result
                result = convert_objectid_to_str(result)
                if inserted:
                    inserted = convert_objectid_to_str(inserted)

            except Exception as db_err:
                print(f"⚠️ Failed to insert into DB: {db_err}")
                result["note"] = result.get("note", "") + " | DB insertion failed."

            return JSONResponse(
                content={"status": "success", "result": result},
                status_code=200
            )

        except Exception as e:
            import traceback
            print("❌ Unexpected controller error:", traceback.format_exc())
            return JSONResponse(
                content={
                    "status": "error",
                    "message": str(e),
                    "trace": traceback.format_exc()
                },
                status_code=200
            )

@router.get("/results")
def get_results():
    try:
        return fetch_all_results()
    except Exception as e:
        print(f"⚠️ Failed to fetch results: {e}")
        return JSONResponse(content={"status": "error", "message": "Cannot fetch results"}, status_code=200)
