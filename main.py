import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel

from database import db, create_document
from schemas import Inquiry

app = FastAPI(title="Embrovia API", description="Backend for Embrovia website")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Embrovia API running"}

@app.post("/api/inquiry")
async def create_inquiry(
    name: str = Form(...),
    email: str = Form(...),
    service: str = Form(...),
    message: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    whatsapp: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    quantity: Optional[int] = Form(None),
    turnaround: Optional[str] = Form(None),
    files: List[UploadFile] = File(default_factory=list)
):
    """Accept quote/contact inquiries with optional file uploads."""
    # Save files to a temp uploads directory (names only stored in DB)
    saved_names: List[str] = []
    upload_dir = os.path.join("uploads")
    os.makedirs(upload_dir, exist_ok=True)

    for f in files or []:
        filename = f.filename
        if not filename:
            continue
        # store with a unique name to avoid collisions
        safe_name = filename.replace("/", "_").replace("\\", "_")
        target_path = os.path.join(upload_dir, safe_name)
        content = await f.read()
        with open(target_path, "wb") as out:
            out.write(content)
        saved_names.append(safe_name)

    data = Inquiry(
        name=name,
        email=email,
        service=service,
        message=message,
        company=company,
        whatsapp=whatsapp,
        country=country,
        quantity=quantity,
        turnaround=turnaround,
        file_names=saved_names or None,
    )

    try:
        inserted_id = create_document("inquiry", data)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health():
    has_db = db is not None
    return {"status": "ok", "database": has_db}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db as _db
        if _db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = _db.name if hasattr(_db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = _db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
