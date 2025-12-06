import requests
import base64
import sys
import os
import time
import glob
import threading
import signal
import random
from queue import Queue

if len(sys.argv) not in [2, 3]:
    print("usage: process_frames.py <api_key> [parallelism]")
    sys.exit(1)

api_key = sys.argv[1]
parallelism = int(sys.argv[2]) if len(sys.argv) == 3 else 1

out_dir = "out"
in_dir = "in"

os.makedirs(in_dir, exist_ok=True)

image_paths = sorted(glob.glob(f"{out_dir}/*.png"))

if not image_paths:
    print(f"no images found in {out_dir}/")
    sys.exit(1)

print(f"found {len(image_paths)} images, using {parallelism} workers")

url = 'https://api.runcomfy.net/prod/v1/deployments/83bde595-975f-4ac6-84a1-5248c8db6866/inference'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

print_lock = threading.Lock()
active_jobs = {}
active_jobs_lock = threading.Lock()
shutting_down = False

def cancel_all_jobs():
    global shutting_down
    shutting_down = True
    with active_jobs_lock:
        if active_jobs:
            print("\ncanceling active jobs...")
            for cancel_url in active_jobs.values():
                print(f"Canceling {cancel_url}")
                try:
                    requests.post(cancel_url, headers={'Authorization': f'Bearer {api_key}'})
                except:
                    print(f"Couldn't cancel {cancel_url}")

def signal_handler(sig, frame):
    cancel_all_jobs()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def process_image(i, image_path, total):
    if shutting_down:
        return
        
    filename = os.path.basename(image_path)
    output_path = os.path.join(in_dir, filename)
    
    if os.path.exists(output_path):
        with print_lock:
            print(f"[{i}/{total}] {filename} (skipped)")
        return
    
    with print_lock:
        print(f"[{i}/{total}] processing {filename}")
    
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    image_uri = f"data:image/jpeg;base64,{image_data}"
    
    payload = {
        'overrides': {
            "6": {
                "inputs": {
                    "text": "Expansive surreal mountainous dreamscape dissolving into fractal geometry, neon-lit ridgelines with iridescent spectral reflections, abstract polygonal rock formations blending into flowing liquid-light gradients, shimmering atmospheric haze in electric magenta and ultraviolet blues, hyper-saturated volumetric fog drifting between impossible crystalline peaks, dynamic aurora-like ribbons weaving through the skyline, luminous particulate dust drifting in nonlinear trails, high-frequency psychedelic texture patterns reminiscent of glitch-art and laser-projection mapping; undulating contours with subtle topographic echoes, shimmering interference colors, refractive crystalline shards embedded in cliff faces, reflective surfaces bending the horizon in non-Euclidean ways; cinematic wide-angle composition, immersive environmental scale, ultrafine detail with smooth painterly energy; radiant backlighting casting neon rim highlights across abstract terrain, deep contrast gradients, fog-scattered strobes, atmospheric distortion waves; 8k festival-visual quality, high dynamic range, emotionally euphoric palette, subtle fractal recursion, aesthetic halfway between digital matte painting and VJ reactive visuals; vibrant, club-centric, hypnotic, infinitely looping energy, surreal but grounded enough to read as mountainous terrain, visually coherent yet delightfully chaotic."
                }
            },
            "100": {
                "inputs": {
                    "image": image_uri
                }
            },
            "104": {
                "inputs": {
                    "value": random.randint(0, 2**32 - 1)
                }
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    result_url = response_data['result_url']
    cancel_url = response_data['cancel_url']
    
    thread_id = threading.get_ident()
    with active_jobs_lock:
        active_jobs[thread_id] = cancel_url
    
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    spin_idx = 0
    wait_time = 0
    
    try:
        while not shutting_down:
            response = requests.get(result_url, headers={'Authorization': f'Bearer {api_key}'})
            result = response.json()
            status = result['status']
            
            if status == 'succeeded':
                output_url = result['outputs']['60']['images'][0]['url']
                image_response = requests.get(output_url)
                with open(output_path, 'wb') as f:
                    f.write(image_response.content)
                with print_lock:
                    print(f"[{i}/{total}] {filename} ✓ ({wait_time}s)")
                break
            elif status == 'failed' or status == 'canceled':
                with print_lock:
                    print(f"[{i}/{total}] {filename} ✗ {status}")
                break
            
            time.sleep(5)
            wait_time += 5
            spin_idx = (spin_idx + 1) % len(spinner)
    finally:
        with active_jobs_lock:
            active_jobs.pop(thread_id, None)

def worker(queue):
    while True:
        item = queue.get()
        if item is None:
            break
        i, image_path, total = item
        process_image(i, image_path, total)
        queue.task_done()

queue = Queue()
threads = []

for _ in range(parallelism):
    t = threading.Thread(target=worker, args=(queue,))
    t.start()
    threads.append(t)

for i, image_path in enumerate(image_paths, 1):
    queue.put((i, image_path, len(image_paths)))

queue.join()

for _ in range(parallelism):
    queue.put(None)

for t in threads:
    t.join()

print(f"\ndone, images saved to {in_dir}/")
