from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import logging
from datetime import datetime
from agent.meal_agent import run_agent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Swiggy AI Food Recommendation Engine",
    description="AI-powered food recommendation API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/agent")
def meal_agent(query: str, session_id: str = None):
    if not query or not query.strip():
        logger.warning("Empty query received")
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )
    
    # Generate session ID if not provided (for isolation)
    if not session_id:
        session_id = str(uuid.uuid4())
    
    logger.info(f"Processing query: '{query}' for session: {session_id}")
    
    try:
        # Run agent with session isolation
        response = run_agent(query, session_id=session_id)
        
        # Check for errors
        if response.get("error"):
            logger.error(f"Agent error: {response.get('output')}")
            raise HTTPException(
                status_code=500,
                detail=response.get("output", "Unknown error")
            )
        
        logger.info(f"Query processed successfully for session: {session_id}")
        
        return {
            "status": "success",
            "session_id": session_id,
            "query": query,
            "response": response.get("output", "No recommendations found"),
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )

@app.get("/")
def root():
    """Root endpoint with API info."""
    return {
        "name": "Swiggy AI Food Recommendation Engine",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "recommendation": "/agent?query=YOUR_QUERY",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )