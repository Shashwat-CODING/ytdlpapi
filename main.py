import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Stream Extraction API",
    description="API for extracting audio streams from YouTube videos",
    version="1.0.0"
)

# Add CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/streams/{video_id}")
async def get_video_streams(video_id: str):
    """
    Extract audio streams for a given YouTube video ID
    
    :param video_id: YouTube video ID
    :return: Dictionary of stream information
    """
    try:
        # Enhanced yt-dlp options
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'no_color': True,
            'format': 'bestaudio/best',
        }
        
        # Construct full YouTube URL
        youtube_url = f'https://youtu.be/{video_id}'
        
        # Extract video information
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(youtube_url, download=False)
            except Exception as extract_error:
                logger.error(f"Error extracting video info: {extract_error}")
                raise HTTPException(status_code=404, detail="Video not found or extraction failed")
            
            # Prepare stream information
            streams = {
                'title': info_dict.get('title', 'Unknown Title'),
                'uploader': info_dict.get('uploader', 'Unknown Uploader'),
                'thumbnail': info_dict.get('thumbnail', ''),
                'duration': info_dict.get('duration', 0),
                'audio_streams': []
            }
            
            # Extract audio streams
            for format in info_dict.get('formats', []):
                if format.get('acodec') != 'none' and format.get('url'):
                    stream_info = {
                        'format_id': format.get('format_id', ''),
                        'ext': format.get('ext', ''),
                        'abr': format.get('abr', 0),
                        'acodec': format.get('acodec', ''),
                        'filesize': format.get('filesize', 0),
                        'url': format.get('url', '')
                    }
                    streams['audio_streams'].append(stream_info)
            
            # Log successful extraction
            logger.info(f"Successfully extracted streams for video: {video_id}")
            
            return streams
    
    except Exception as e:
        # Catch-all error handling
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    """
    Root endpoint to verify API is running
    """
    return {
        "message": "YouTube Stream Extraction API",
        "status": "Running",
        "version": "1.0.0"
    }

# Dynamic port binding for cloud platforms
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
