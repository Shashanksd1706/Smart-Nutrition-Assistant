import tempfile
import shutil

def convert_audio(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
        shutil.copyfileobj(file, temp)
        return temp.name
