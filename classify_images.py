import os
import pandas as pd
from openai import OpenAI
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def classify_image(image_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    # Convert image to base64
    image_base64 = base64.b64encode(image_data).decode("utf-8")

    # Send image to OpenAI for classification
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": "\n"}
                ]
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"}},
                    {"type": "text", "text": "Give me details such as color, style, item type, and other visual attributes extracted from the images."}
                ]
            },
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    # Read the scraped product data
    df = pd.read_csv('products.csv')

    # Ensure images folder exists
    if not os.path.exists('images'):
        os.makedirs('images')

    # Initialize a list to store the attributes
    attributes_list = []

    # Classify images and add attributes
    for index, row in df.iterrows():
        image_path = row['image_path']
        attributes = classify_image(image_path)
        attributes_list.append({
            'product_id': row['product_id'],
            'attributes': attributes
        })
        print(f"Processed {index + 1}/{len(df)}")

    # Convert list to dataframe
    attributes_df = pd.DataFrame(attributes_list)

    # Merge attributes back into the products dataframe
    df = df.merge(attributes_df, on='product_id', how='left')

    # Save the updated dataframe to the same CSV file
    df.to_csv('products.csv', index=False)
    print("Product data with attributes saved to products.csv")
