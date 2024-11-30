const express = require('express');
const ytdl = require('yt-dlp-exec');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 8080;

// Middleware
app.use(cors());
app.use(express.json());

// Root endpoint
app.get('/', (req, res) => {
    res.json({
        message: "YouTube Stream Extraction API",
        status: "Running",
        version: "1.0.0"
    });
});

// Stream extraction endpoint
app.get('/streams/:videoId', async (req, res) => {
    const { videoId } = req.params;

    try {
        // Construct full YouTube URL
        const youtubeUrl = `https://youtu.be/${videoId}`;

        // Extract video information using yt-dlp
        const videoInfo = await ytdl(youtubeUrl, {
            dumpJson: true,
            noWarnings: true,
            noColor: true,
            format: 'bestaudio/best'
        });

        // Prepare stream information
        const streams = {
            title: videoInfo.title || 'Unknown Title',
            uploader: videoInfo.uploader || 'Unknown Uploader',
            thumbnail: videoInfo.thumbnail || '',
            duration: videoInfo.duration || 0,
            audio_streams: []
        };

        // Extract audio streams
        const audioFormats = videoInfo.formats.filter(format => 
            format.acodec !== 'none' && format.url
        );

        streams.audio_streams = audioFormats.map(format => ({
            format_id: format.format_id || '',
            ext: format.ext || '',
            abr: format.abr || 0,
            acodec: format.acodec || '',
            filesize: format.filesize || 0,
            url: format.url || ''
        }));

        res.json(streams);
    } catch (error) {
        console.error('Error extracting video info:', error);
        res.status(404).json({ 
            detail: "Video not found or extraction failed",
            error: error.message 
        });
    }
});

// Start the server
app.listen(port, '0.0.0.0', () => {
    console.log(`Server running on port ${port}`);
});
