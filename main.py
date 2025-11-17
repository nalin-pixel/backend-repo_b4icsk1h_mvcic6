import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from schemas import ContactMessage
from database import create_document

app = FastAPI(title="Nieuwe Vloer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

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
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else (os.getenv("DATABASE_NAME") or "❌ Not Set")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Public data for services
class ServiceItem(BaseModel):
    id: str
    title: str
    description: str
    icon: str

@app.get("/services", response_model=List[ServiceItem])
def get_services():
    return [
        ServiceItem(id="vlakke-chape", title="Chape & Uitvlakwerken", description="Perfect vlakke ondergrond voor elke vloer.", icon="Layers"),
        ServiceItem(id="vloerisolatie", title="Vloerisolatie", description="Warme voeten en lagere energiefactuur.", icon="Thermometer"),
        ServiceItem(id="vloerverwarming", title="Vloerverwarming", description="Comfort door gelijkmatige warmteverdeling.", icon="Flame"),
        ServiceItem(id="gietvloeren", title="Giet- & Ploegvloeren", description="Strakke, naadloze afwerking voor modern interieur.", icon="Droplet"),
        ServiceItem(id="tegelwerken", title="Tegelwerken", description="Vakkundige plaatsing van tegels en natuursteen.", icon="Square"),
    ]

# Contact form endpoint
@app.post("/contact")
def submit_contact(message: ContactMessage):
    try:
        doc_id = create_document("contactmessage", message)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
