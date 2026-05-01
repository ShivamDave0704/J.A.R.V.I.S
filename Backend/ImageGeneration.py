from diffusers import StableDiffusionPipeline # type: ignore
import torch # type: ignore
import os

# Prompt input
prompt = input("Enter your image prompt: ")

# Load the model
print("🔄 Loading model (only first time)...")
pipe = StableDiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    use_safetensors=True
).to("cuda")  # Change to "cpu" if you don’t have a GPU

# Generate image
print("🎨 Generating image...")
image = pipe(prompt, num_inference_steps=30, guidance_scale=7.5).images[0]

# Save the image
filename = prompt.replace(" ", "_") + ".png"
os.makedirs("GeneratedImages", exist_ok=True)
image_path = os.path.join("GeneratedImages", filename)
image.save(image_path)

print(f"✅ Image saved at: {image_path}")
