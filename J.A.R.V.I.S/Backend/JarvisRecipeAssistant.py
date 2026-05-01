import os
import time
import requests
import openai # type: ignore
from dotenv import load_dotenv
from datetime import datetime
from diskcache import Cache # type: ignore

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
BING_API_KEY = os.getenv("BING_API_KEY")

# Initialize cache
cache = Cache("cache")

# Paths
SAVE_FOLDER = os.path.join("data", "recipes")
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Common recipes for autocomplete
COMMON_RECIPES = [
    "Khichdi", "Dhokla", "Pav Bhaji", "Chole Bhature", "Paneer Butter Masala",
    "Butter Chicken", "Biryani", "Samosa", "Aloo Paratha", "Rajma Chawal"
]

def get_recipe_from_gpt(dish_name=None, ingredients=None, food_type="Veg"):
    cache_key = f"{dish_name}_{ingredients}_{food_type}"
    if cache_key in cache:
        print("🔁 Retrieved recipe from cache.")
        return cache[cache_key]

    if dish_name:
        prompt = f"""
        You are a top chef. Provide a detailed and neat recipe for a {food_type} dish called "{dish_name}".
        Include:
        🍽️ Introduction
        🧂 Ingredients (with quantities)
        🍳 Step-by-step instructions
        Format it cleanly using emojis.
        """
    elif ingredients:
        prompt = f"""
        You are an intelligent chef assistant.
        Suggest a {food_type} Indian dish based on these ingredients: {ingredients}.
        Then provide the full recipe with:
        🍽️ Introduction
        🧂 Ingredients
        🍳 Step-by-step instructions
        Use emojis and format cleanly.
        """
    else:
        return "❌ No input provided for recipe generation."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a recipe assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        recipe = response['choices'][0]['message']['content'].strip()
        cache[cache_key] = recipe
        return recipe
    except Exception as e:
        return f"❌ Error getting recipe: {e}"

def get_dish_image(dish_name):
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": dish_name, "license": "public", "imageType": "photo"}
    try:
        response = requests.get(
            "https://api.bing.microsoft.com/v7.0/images/search",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        results = response.json()
        if results["value"]:
            return results["value"][0]["contentUrl"]
        else:
            return None
    except Exception as e:
        print(f"❌ Error fetching image: {e}")
        return None

def save_recipe(name, content):
    safe_name = name.lower().replace(" ", "_")
    filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(SAVE_FOLDER, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    try:
        os.system(f'notepad "{path}"')
    except:
        pass
    return path

def suggest_recipes(input_text):
    suggestions = [recipe for recipe in COMMON_RECIPES if recipe.lower().startswith(input_text.lower())]
    return suggestions

def main():
    print("\n" + "="*60)
    print("🤖  WELCOME TO J.A.R.V.I.S GPT RECIPE ASSISTANT 🍴")
    print("="*60)

    food_type = ""
    while food_type not in ["Veg", "Non-Veg"]:
        food_type = input("🫕 Are you looking for a Veg or Non-Veg recipe? (Veg/Non-Veg): ").strip().capitalize()

    while True:
        mode = ""
        while mode not in ["1", "2"]:
            mode = input("\n📌 Type '1' to enter a Dish Name OR '2' for Ingredient-based recipe (or 'exit' to quit): ").strip()
            if mode.lower() == 'exit':
                print("👋 Goodbye! Enjoy your cooking!")
                return

        if mode == '1':
            dish = input("\n🍽️ Enter the dish name: ").strip()
            if not dish:
                print("❗ Dish name cannot be empty.")
                continue
            suggestions = suggest_recipes(dish)
            if suggestions:
                print("💡 Did you mean:")
                for s in suggestions:
                    print(f" - {s}")
            print("\n🧠 Generating recipe from GPT...\n")
            recipe = get_recipe_from_gpt(dish_name=dish, food_type=food_type)
            name_to_save = dish
        else:
            ingredients = input("\n🥕 Enter available ingredients (comma-separated): ").strip()
            if not ingredients:
                print("❗ Ingredients cannot be empty.")
                continue
            print("\n🧠 Finding a recipe based on your ingredients...\n")
            recipe = get_recipe_from_gpt(ingredients=ingredients, food_type=food_type)
            name_to_save = ingredients.replace(",", "_").split()[0][:10]

        if recipe.startswith("❌"):
            print(recipe)
            continue

        print("✨ Recipe Generated!\n" + "-" * 60)
        print(recipe)
        print("-" * 60)

        image_url = get_dish_image(name_to_save)
        if image_url:
            print(f"🖼️ Image of the dish: {image_url}")
        else:
            print("🖼️ No image found for this dish.")

        path = save_recipe(name_to_save, recipe)
        print(f"\n✅ Recipe saved and opened in Notepad: {path}\n")

        time.sleep(1)

if __name__ == "__main__":
    main()
