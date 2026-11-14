"""Generates the game's voice clips with Kokoro (open-source TTS, Apache-2.0).
Usage: python3 tools/make_voice.py <model_dir> <assets_dir>
model_dir holds kokoro-v1.0.onnx and voices-v1.0.bin. Two accents: us (af_heart), uk (bf_emma)."""
import sys, os, json, subprocess, tempfile
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
mdir, out = sys.argv[1:3]
only = sys.argv[3:] 
lines = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voice_lines.json')))
k = Kokoro(os.path.join(mdir, 'kokoro-v1.0.onnx'), os.path.join(mdir, 'voices-v1.0.bin'))
VO = {'us': ('af_heart', 'en-us', 0.92), 'uk': ('bf_emma', 'en-gb', 0.95)}
for acc, (voice, lang, speed) in VO.items():
    os.makedirs(f'{out}/voice/{acc}', exist_ok=True)
    for key, text in lines.items():
        if only and key not in only: continue
        if acc == 'us': text = text.replace('colour', 'color')
        s, sr = k.create(text, voice=voice, speed=speed, lang=lang)
        s = np.concatenate([np.zeros(int(sr*.04), dtype=s.dtype), s / max(1e-6, np.abs(s).max()) * .9, np.zeros(int(sr*.12), dtype=s.dtype)])
        with tempfile.NamedTemporaryFile(suffix='.wav') as t:
            sf.write(t.name, s, sr)
            subprocess.run(['ffmpeg','-v','error','-y','-i',t.name,'-ac','1','-ar','24000','-c:a','libmp3lame','-b:a','40k',f'{out}/voice/{acc}/{key}.mp3'], check=True)
    print(acc, voice, 'done')
