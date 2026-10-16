"""Renderização final: cada trecho em um processo, cada quadro com 3 subamostras (obturador de 180°)."""
import os, sys, subprocess, time, importlib
from multiprocessing import Pool
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "render")
os.makedirs(OUT, exist_ok=True)

MODS = {"s1_fragmentacao": "sc_abertura", "s2_transformacao": "sc_abertura", "s3a_edital": "sc_edital",
        "s3b_inscricao": "sc_inscricao", "s3c_comissao": "sc_comissao", "s3d_convocacao": "sc_convocacao",
        "s4_diferenciais": "sc_diferenciais", "s5_climax": "sc_final", "s6_encerramento": "sc_final"}

def chunks(max_frames=420):
    """Trechos uniformes sobre o filme inteiro; film.draw resolve seção e inserção por quadro."""
    from timeline import FILM_TOTAL
    from engine import FPS
    total = int(round(FILM_TOTAL * FPS))
    return [("filme", k, min(total, k + max_frames)) for k in range(0, total, max_frames)]

def work(job):
    name, f0, f1 = job
    import skia
    from engine import W, H, FPS, surface, finish
    import film as mod
    path = os.path.join(OUT, f"{f0:06d}.mp4")
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return path, 0.0
    t_start = time.time()
    tmp = path + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p",
                           "-tune", "film", "-x264-params", "keyint=60", tmp], stdin=subprocess.PIPE)
    s = surface()
    SUB = 3
    for k in range(f0, f1):
        T = k / FPS
        acc = None
        for j in range(SUB):
            tt = T + (j / SUB - 0.5 + 0.5 / SUB) * (0.5 / FPS)
            c = s.getCanvas()
            mod.draw(c, tt)
            a = s.toarray(colorType=skia.kRGBA_8888_ColorType).astype(np.float32)
            acc = a if acc is None else acc + a
        arr = (acc / SUB + 0.5).astype(np.uint8)
        arr = finish(arr, k)
        ff.stdin.write(arr.tobytes())
    ff.stdin.close(); ff.wait()
    os.replace(tmp, path)
    return path, time.time() - t_start

if __name__ == "__main__":
    jobs = chunks()
    if len(sys.argv) == 3:  # opcional: refazer só o intervalo [t0, t1) do filme, em segundos
        from engine import FPS
        a, z = float(sys.argv[1]) * FPS, float(sys.argv[2]) * FPS
        for j in jobs:
            if j[2] > a and j[1] < z:
                p = os.path.join(OUT, f"{j[1]:06d}.mp4")
                if os.path.exists(p): os.remove(p)
    print(len(jobs), "trechos", flush=True)
    t0 = time.time()
    with Pool(int(os.environ.get("PROCS", "7"))) as pool:
        for path, dt in pool.imap_unordered(work, jobs):
            print(f"{os.path.basename(path)} {dt:.0f}s  ({time.time() - t0:.0f}s)", flush=True)
    allj = chunks()
    with open(os.path.join(OUT, "list.txt"), "w") as f:
        for j in allj:
            f.write(f"file '{j[1]:06d}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "list.txt"),
                    "-c", "copy", os.path.join(ROOT, "video.mp4")], check=True)
    print("video.mp4 pronto", time.time() - t0, flush=True)
