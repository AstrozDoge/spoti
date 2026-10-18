import os
import shutil
import subprocess
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

# Complete standalone web design and download trigger
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotisaver</title>
    <link rel="stylesheet" href="https://cloudflare.com">
</head>
<body class="bg-black text-gray-100 flex items-center justify-center min-h-screen font-sans">

    <div class="w-full max-w-md p-8 bg-gray-900 border border-gray-800 rounded-2xl shadow-xl text-center">
        <h1 class="text-3xl font-black text-green-400 mb-2 tracking-tight">Spotisaver</h1>
        <p class="text-gray-400 text-sm mb-6">Enter a public playlist link to generate your download pack</p>
        
        <form action="/download" method="POST" onsubmit="showLoading()" class="space-y-4">
            <input type="text" name="url" placeholder="Paste Spotify link here..." required
                   class="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl focus:outline-none focus:border-green-500 text-sm text-white">
            
            <button type="submit" id="btn"
                    class="w-full py-3 bg-green-500 hover:bg-green-600 text-black font-semibold rounded-xl shadow-lg transition-all active:scale-[0.98]">
                Extract & Download ZIP
            </button>
        </form>

        <div id="status" class="hidden mt-6 text-sm text-green-400 animate-pulse font-medium">
            ⏳ Processing tracks and compiling your ZIP archive... Please wait.
        </div>
    </div>

    <script>
        function showLoading() {
            document.getElementById('status').classList.remove('hidden');
            document.getElementById('btn').disabled = true;
            document.getElementById('btn').innerText = "Processing Tracks...";
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_INTERFACE)

@app.route('/download', methods=['POST'])
def download():
    playlist_url = request.form.get('url')
    download_dir = "temp_tracks"
    zip_name = "spotify_tracks"
    
    if os.path.exists(download_dir):
        shutil.rmtree(download_dir)
    os.makedirs(download_dir)

    try:
        # Download songs using spotdl public scraping directly on the host server instance
        subprocess.run(["spotdl", "download", playlist_url, "--output", f"{download_dir}/{{title}} - {{artist}}.{{output-ext}}"], check=True)
        
        # Zip everything up automatically on the cloud box
        shutil.make_archive(zip_name, 'zip', download_dir)
        
        # Send the file straight to your web browser window
        return send_file(f"{zip_name}.zip", as_attachment=True)
    except Exception as e:
        return f"Extraction Error: {str(e)}", 500
    finally:
        # Keep cloud runtime storage fresh
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)
        if os.path.exists(f"{zip_name}.zip"):
            os.remove(f"{zip_name}.zip")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
