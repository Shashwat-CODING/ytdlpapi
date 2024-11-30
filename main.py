from fastapi import FastAPI, HTTPException
import yt_dlp
import uvicorn

app = FastAPI()

@app.get("/streams/{video_id}")
async def get_video_streams(video_id: str):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(f'https://youtu.be/{video_id}', download=False)
            
            # Prepare stream information
            streams = {
                'title': info_dict.get('title', 'Unknown Title'),
                'thumbnail': info_dict.get('thumbnail', ''),
                'audio_streams': []
            }
            
            # Extract audio streams
            for format in info_dict.get('formats', []):
                if format.get('acodec') != 'none':
                    stream_info = {
                        'format_id': format.get('format_id', ''),
                        'ext': format.get('ext', ''),
                        'abr': format.get('abr', 0),
                        'url': format.get('url', '')
                    }
                    streams['audio_streams'].append(stream_info)
            
            return streams
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
