from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import uuid

app = FastAPI(title="Thrift Matchmaker API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= MODELS =============
class ClothingItem(BaseModel):
    id: str
    user_id: str
    image_url: str
    category: str  # shirt, pants, shoes, etc.
    color_primary: str
    color_secondary: Optional[str]
    season: List[str]  # winter, summer, all
    created_at: datetime

class ThriftMatch(BaseModel):
    thrift_item_id: str
    thrift_image_url: str
    compatibility_score: float
    matching_items: List[str]  # IDs of wardrobe items
    outfit_suggestion: str

# ============= AZURE SETUP =============
AZURE_CV_ENDPOINT = os.getenv("AZURE_CV_ENDPOINT")
AZURE_CV_KEY = os.getenv("AZURE_CV_KEY")
BLOB_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION")

# In-memory store (replace with Azure SQL)
wardrobe_db = {}

# ============= ENDPOINTS =============

@app.get("/")
def root():
    return {"message": "Thrift Matchmaker API", "version": "1.0"}

@app.post("/wardrobe/upload")
async def upload_wardrobe_item(
    file: UploadFile = File(...),
    user_id: str = "default_user"
):
    """Upload clothing item to user's wardrobe"""
    
    # Generate unique ID
    item_id = str(uuid.uuid4())
    
    # Read image
    contents = await file.read()
    
    # TODO: Upload to Azure Blob Storage
    # blob_url = upload_to_blob(contents, item_id)
    blob_url = f"https://placeholder.blob/{item_id}.jpg"
    
    # TODO: Analyze with Azure Computer Vision
    # analysis = analyze_clothing(blob_url)
    analysis = {
        "category": "shirt",
        "color_primary": "blue",
        "color_secondary": "white",
        "season": ["all"]
    }
    
    # Create item
    item = ClothingItem(
        id=item_id,
        user_id=user_id,
        image_url=blob_url,
        category=analysis["category"],
        color_primary=analysis["color_primary"],
        color_secondary=analysis.get("color_secondary"),
        season=analysis["season"],
        created_at=datetime.now()
    )
    
    # Store
    if user_id not in wardrobe_db:
        wardrobe_db[user_id] = []
    wardrobe_db[user_id].append(item.dict())
    
    return {"success": True, "item": item}

@app.get("/wardrobe/{user_id}")
def get_wardrobe(user_id: str):
    """Get all wardrobe items for user"""
    items = wardrobe_db.get(user_id, [])
    return {"items": items, "count": len(items)}

@app.post("/match/thrift")
async def match_thrift_item(
    file: UploadFile = File(...),
    user_id: str = "default_user"
):
    """Find matching wardrobe items for a thrift piece"""
    
    # Read thrift item image
    contents = await file.read()
    
    # TODO: Analyze thrift item
    thrift_analysis = {
        "category": "pants",
        "color_primary": "black",
        "season": ["all"]
    }
    
    # Get user wardrobe
    wardrobe = wardrobe_db.get(user_id, [])
    
    if not wardrobe:
        raise HTTPException(400, "No wardrobe items found. Upload clothes first!")
    
    # TODO: Match logic (simplified)
    matches = []
    for item in wardrobe:
        score = calculate_compatibility(thrift_analysis, item)
        if score > 0.5:
            matches.append({
                "item_id": item["id"],
                "item_url": item["image_url"],
                "score": score
            })
    
    # Sort by score
    matches.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "thrift_item": thrift_analysis,
        "matches": matches[:5],  # Top 5
        "outfit_ideas": generate_outfit_ideas(matches, wardrobe)
    }

# ============= HELPER FUNCTIONS =============

def calculate_compatibility(thrift_item: dict, wardrobe_item: dict) -> float:
    """Calculate how well items match (0-1 score)"""
    score = 0.0
    
    # Category compatibility
    if is_compatible_category(thrift_item["category"], wardrobe_item["category"]):
        score += 0.4
    
    # Color compatibility
    if is_compatible_color(thrift_item["color_primary"], wardrobe_item["color_primary"]):
        score += 0.4
    
    # Season compatibility
    if any(s in wardrobe_item["season"] for s in thrift_item["season"]):
        score += 0.2
    
    return min(score, 1.0)

def is_compatible_category(cat1: str, cat2: str) -> bool:
    """Check if clothing categories work together"""
    compatible = {
        "shirt": ["pants", "skirt", "shorts"],
        "pants": ["shirt", "jacket", "sweater"],
        "shoes": ["pants", "skirt", "shorts"]
    }
    return cat2 in compatible.get(cat1, [])

def is_compatible_color(color1: str, color2: str) -> bool:
    """Simple color matching (expand with color theory)"""
    neutral = ["black", "white", "gray", "beige"]
    
    # Neutrals match everything
    if color1 in neutral or color2 in neutral:
        return True
    
    # Same color matches
    if color1 == color2:
        return True
    
    # Add color wheel logic here
    complementary = {
        "blue": ["orange", "yellow"],
        "red": ["green"],
        "purple": ["yellow"]
    }
    
    return color2 in complementary.get(color1, [])

def generate_outfit_ideas(matches: List[dict], wardrobe: List[dict]) -> List[str]:
    """Generate text outfit suggestions"""
    if not matches:
        return ["No matches found. Try different items!"]
    
    ideas = [
        f"Pair with {matches[0]['item_id']} for a casual look",
        "Add a neutral jacket to complete the outfit",
        "Perfect for a weekend outing"
    ]
    return ideas

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)