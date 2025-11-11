from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import subprocess
import os
import uuid
import shutil

app = FastAPI(title="Raseed Financial Advisor API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Raseed Financial Advisor API is running", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "endpoints": ["/chat", "/api/categorize"]}

@app.post("/api/categorize")
async def categorize(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    input_path = f"uploads/{file_id}_input.csv"
    output_path = f"uploads/{file_id}_output.csv"
    
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Save uploaded file temporarily
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Run your existing LLM script
        cmd = ["python", "main.py", input_path]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Check if the default output file was created
        default_output = "Bank_transaction_categorized.csv"
        if os.path.exists(default_output):
            # Move it to our unique output path
            shutil.move(default_output, output_path)
        elif not os.path.exists(output_path):
            # If main.py didn't create the file, try to read it from the same directory
            raise HTTPException(status_code=500, detail=f"Categorization failed. Error: {result.stderr}")

        # Return categorized CSV file
        return FileResponse(
            output_path, 
            media_type="text/csv", 
            filename="Bank_transaction_categorized.csv",
            headers={"Content-Disposition": "attachment; filename=Bank_transaction_categorized.csv"}
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Categorization failed: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        # Clean up input file
        if os.path.exists(input_path):
            os.remove(input_path)
        # Note: output file will be cleaned up after download or can be cleaned up periodically


from dotenv import load_dotenv
import google.generativeai as genai
from geminichatbot.app.chat_brain import (
    build_context_block, craft_parts, enforce_note, update_memory_summary
)
from geminichatbot.app.data_model import (
    load_expense_csv, normalize_expenses, summarize
)
from pydantic import BaseModel
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))

SYSTEM = (
    "You are a friendly personal finance copilot for India-focused users.\n"
    "The user uploads a CSV that contains only OUTGOING transactions (expenses).\n"
    "Keep responses short, structured, and practical.\n"
    "Strictly avoid naming specific investment products or giving buy/sell calls.\n"
    "Always end with this NOTE:\n"
    "Educational only. Not financial advice. Please research before investing."
)


class ChatRequest(BaseModel):
    message: str
    file_id: str = "latest"  # file_id to identify the categorized CSV file
    history: list | None = None
    profile: dict | None = None
    income: float | None = None
    memory: str | None = ""


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        # Validate API key
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="Gemini API key not found. Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable."
            )
        
        # Handle "latest" file_id by finding the most recent output file
        if req.file_id == "latest":
            uploads_dir = "uploads"
            if not os.path.exists(uploads_dir):
                raise HTTPException(
                    status_code=404, 
                    detail="No categorized files found. Please upload and categorize a CSV file first using the CSV upload feature."
                )
            
            # Find all output CSV files
            try:
                output_files = [f for f in os.listdir(uploads_dir) if f.endswith("_output.csv")]
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error reading uploads directory: {str(e)}"
                )
            
            if not output_files:
                raise HTTPException(
                    status_code=404, 
                    detail="No categorized files found. Please upload and categorize a CSV file first using the CSV upload feature."
                )
            
            # Get the most recently modified file
            file_paths = [os.path.join(uploads_dir, f) for f in output_files]
            file_path = max(file_paths, key=os.path.getmtime)
            print(f"Using latest file: {file_path}")  # Debug log
        else:
            file_path = f"uploads/{req.file_id}_output.csv"
            if not os.path.exists(file_path):
                raise HTTPException(
                    status_code=404, 
                    detail=f"Categorized file not found for file_id: {req.file_id}. Please upload and categorize a CSV file first."
                )

        # Load and summarize
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            df = load_expense_csv(file_bytes)
            if df.empty:
                raise HTTPException(status_code=400, detail="The CSV file is empty or could not be parsed.")
            dfn, cols = normalize_expenses(df)
            profile = summarize(dfn, cols)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing CSV file: {str(e)}")

        # Build context + query
        ctx_block = build_context_block(profile, req.income)
        memory = update_memory_summary(req.memory or "", req.history or [], max_chars=900)

        parts = craft_parts(
            history=req.history or [],
            ctx_block=ctx_block,
            query=req.message,
            mem_summary=memory
        )

        # Generate response from Gemini
        try:
            # Try to use gemini-1.5-pro, fallback to gemini-1.5-flash if needed
            model_name = "gemini-2.5-pro"
            try:
                model = genai.GenerativeModel(model_name=model_name, system_instruction=SYSTEM)
                resp = model.generate_content(parts)
            except Exception as model_error:
                # If model doesn't exist, try flash model
                if "not found" in str(model_error).lower() or "404" in str(model_error):
                    model_name = "gemini-2.5-flash"
                    model = genai.GenerativeModel(model_name=model_name, system_instruction=SYSTEM)
                    resp = model.generate_content(parts)
                else:
                    raise
            
            # Extract text from response
            answer = ""
            if hasattr(resp, 'text') and resp.text:
                answer = resp.text
            elif hasattr(resp, 'candidates') and resp.candidates:
                # Try to get text from candidates
                candidate = resp.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    answer = "".join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
            
            if not answer or not answer.strip():
                # Check if response was blocked
                if hasattr(resp, 'prompt_feedback'):
                    block_reason = getattr(resp.prompt_feedback, 'block_reason', None)
                    if block_reason:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Response was blocked: {block_reason}. Please try rephrasing your question."
                        )
                raise HTTPException(
                    status_code=500, 
                    detail="Gemini API returned an empty response. Please check your API key and try again."
                )
            
            answer = enforce_note(answer.strip())
        except HTTPException:
            raise
        except Exception as e:
            error_msg = str(e)
            if "API key" in error_msg or "authentication" in error_msg.lower() or "403" in error_msg:
                raise HTTPException(
                    status_code=401, 
                    detail=f"Gemini API authentication failed: {error_msg}. Please check your API key."
                )
            if "429" in error_msg or "quota" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Gemini API quota exceeded. Please try again later."
                )
            raise HTTPException(
                status_code=500, 
                detail=f"Error calling Gemini API: {error_msg}"
            )

        return {"response": answer, "memory": memory}

    except HTTPException:
        # Re-raise HTTP exceptions (like 404) as-is
        raise
    except Exception as e:
        # Log full error for debugging, but return user-friendly message
        import traceback
        error_trace = traceback.format_exc()
        print(f"Unexpected error in chat endpoint: {error_trace}")  # Log to console
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}. Please check server logs for details."
        )
