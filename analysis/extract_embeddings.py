import json
from pathlib import Path
import torch
import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
from transformers import AutoProcessor, ClapModel
import librosa

MODEL_NAME = "laion/clap-htsat-unfused"
processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = ClapModel.from_pretrained(MODEL_NAME)

BASE_DIR = Path(__file__).resolve().parent
TEST_DIR = BASE_DIR.parent / "test"
DATA_DIR = BASE_DIR / "data"

def get_clap_embedding(file_path, num_samples=5, sample_duration=7):
    full_duration = librosa.get_duration(path=file_path)
    max_start = max(0.0, full_duration - sample_duration)
    offsets = np.linspace(0.0, max_start, num=num_samples) if max_start > 0 else [0.0]
    
    embeddings = []
    for offset in offsets:
        audio_data, sr = librosa.load(file_path, sr=48000, offset=offset, duration=sample_duration)
        inputs = processor(audio=audio_data, sampling_rate=sr, return_tensors="pt")
        
        with torch.no_grad():
            audio_features = model.get_audio_features(**inputs)
            if hasattr(audio_features, "audio_embeds"):
                audio_features = audio_features.audio_embeds
            elif hasattr(audio_features, "pooler_output"):
                audio_features = audio_features.pooler_output
        
        emb = audio_features.squeeze().numpy()
        embeddings.append(emb)
    
    mean_embedding = np.mean(embeddings, axis=0)
    norm = np.linalg.norm(mean_embedding)
    if norm > 0:
        mean_embedding = mean_embedding / norm
        
    return mean_embedding

def get_mfcc_embedding(file_path, duration=30):
    full_duration = librosa.get_duration(path=file_path)
    offset = 0.0 if full_duration <= duration else full_duration * 0.1
    
    audio_data, sr = librosa.load(file_path, sr=None, offset=offset, duration=duration)
    mfcc = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=20)
    
    mfcc_mean = np.mean(mfcc.T, axis=0)
    mfcc_scaled = (mfcc_mean - np.mean(mfcc_mean)) / (np.std(mfcc_mean) + 1e-8)
    return mfcc_scaled

def compute_similarity(vec1, vec2):
    """Oblicza podobieństwo cosinusowe (1 - Cosine Distance)."""
    return float(1 - cosine(vec1, vec2))

if __name__ == "__main__":
    config_path = TEST_DIR / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    unique_rel_paths = set()
    for sc in cfg["scenarios"]:
        unique_rel_paths.add(sc["reference"])
        for s in sc["samples"]:
            unique_rel_paths.add(s["url"])

    print(f"Generowanie wektorów cech ({MODEL_NAME}) dla {len(unique_rel_paths)} unikalnych plików")
    clap_vecs = {}
    mfcc_vecs = {}
    for rel_path in sorted(unique_rel_paths):
        full_path = TEST_DIR / rel_path
        if not full_path.exists():
            raise FileNotFoundError(f"Brak pliku audio: {full_path}")
        clap_vecs[rel_path] = get_clap_embedding(str(full_path))
        mfcc_vecs[rel_path] = get_mfcc_embedding(str(full_path))

    results = []
    for sc in cfg["scenarios"]:
        ref_rel = sc["reference"]
        ref_filename = Path(ref_rel).name  # Zwraca np. "blues.00000.wav" (identycznie jak w Google Sheets)

        for s in sc["samples"]:
            sample_rel = s["url"]
            
            if ref_rel == sample_rel:
                sim_clap, sim_mfcc = 1.0, 1.0
            else:
                sim_clap = compute_similarity(clap_vecs[ref_rel], clap_vecs[sample_rel])
                sim_mfcc = compute_similarity(mfcc_vecs[ref_rel], mfcc_vecs[sample_rel])

            results.append({
                "scenario": sc["name"],
                "reference": ref_filename,
                "sample_id": s["id"],
                "sample_label": s["label"],
                "sample_url": sample_rel,
                "clap_sim": round(sim_clap, 4),
                "mfcc_sim": round(sim_mfcc, 4)
            })

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = DATA_DIR / "model_similarities.csv"
    df_results = pd.DataFrame(results)
    df_results.to_csv(out_csv, index=False)

    print("\n=== PORÓWNANIE PODOBIEŃSTWA DLA PAR Z TESTU ===")
    print(df_results[["scenario", "reference", "sample_id", "sample_label", "clap_sim", "mfcc_sim"]].to_string(index=False))
    print(f"\nZapisano wyniki do: {out_csv}")