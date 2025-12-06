# fire a request at the RunComfy deployed API to generate a background image using the input image as a controlnet mask

import requests
import base64
import sys

if len(sys.argv) != 3:
    print("usage: fire-api.py <image_path> <api_key>")
    sys.exit(1)

image_path = sys.argv[1]
api_key = sys.argv[2]

with open(image_path, 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

image_extension = image_path.split('.')[-1].lower()

# comfyui for some reason accepts PNGs but only if you *say* it's a jpeg
image_uri = f"data:image/jpeg;base64,{image_data}"


url = 'https://api.runcomfy.net/prod/v1/deployments/83bde595-975f-4ac6-84a1-5248c8db6866/inference'
headers = {
  'Authorization': f'Bearer {api_key}',
  'Content-Type': 'application/json'
}
payload = { 'overrides': {
  "6": {
    "inputs": {
      "text": "Expansive surreal mountainous dreamscape dissolving into fractal geometry, neon-lit ridgelines with iridescent spectral reflections, abstract polygonal rock formations blending into flowing liquid-light gradients, shimmering atmospheric haze in electric magenta and ultraviolet blues, hyper-saturated volumetric fog drifting between impossible crystalline peaks, dynamic aurora-like ribbons weaving through the skyline, luminous particulate dust drifting in nonlinear trails, high-frequency psychedelic texture patterns reminiscent of glitch-art and laser-projection mapping; undulating contours with subtle topographic echoes, shimmering interference colors, refractive crystalline shards embedded in cliff faces, reflective surfaces bending the horizon in non-Euclidean ways; cinematic wide-angle composition, immersive environmental scale, ultrafine detail with smooth painterly energy; radiant backlighting casting neon rim highlights across abstract terrain, deep contrast gradients, fog-scattered strobes, atmospheric distortion waves; 8k festival-visual quality, high dynamic range, emotionally euphoric palette, subtle fractal recursion, aesthetic halfway between digital matte painting and VJ reactive visuals; vibrant, club-centric, hypnotic, infinitely looping energy, surreal but grounded enough to read as mountainous terrain, visually coherent yet delightfully chaotic."
    }
  },
  "100": {
    "inputs": {
      "image": image_uri
    }
  }
} }
requests.post(url, headers=headers, json=payload)
