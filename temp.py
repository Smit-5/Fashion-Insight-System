import streamlit as st
import wikipedia
import os
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import result
import model
from PIL import Image

def fetch_wikipedia_description(label):
    """Fetches the summary description from Wikipedia.
    """
    try:
        summary = wikipedia.summary(label, sentences=2)  # Fetch the first few sentences
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple Wikipedia entries found. Please be more specific. Options: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found for this label."
    


def get_google_search_results(query, num_results=5):

    ua = UserAgent()
    user_agent = ua.random


    base_url = "https://www.google.com/search"
    params = {
        "q": query,
        "num": num_results
    }
    headers = {
        "User-Agent": user_agent
    }
    response = requests.get(base_url, params=params, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        search_results = soup.find_all("div", class_="tF2Cxc")
        urls = [result.find("a")['href'] for result in search_results]
        return urls
    else:
        print("Failed to fetch search results.")
        return []

# --- Streamlit App --- (Same as before) 

st.title("Label Information Fetcher")

# label = st.text_input("Enter a label:")
uploaded_image = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_image is not None:
    img = Image.open(uploaded_image)
    img = model.input_img_embedding(img)

    label = result.search_similar_vectors_text(img, 1)
    st.write(label)

    if st.button("Fetch Information"):
        try:
            info = fetch_wikipedia_description(label)
            # print(info)
            st.write(info)

            urls = get_google_search_results(label, 5)
        
            if urls:
                st.write(f"Top {3} URLs related to '{label}':")
            for idx, url in enumerate(urls, start=1):
                st.write(f"{idx}. {url}")
                print(f"{idx}. {url}")
            else:
                pass

        except Exception as e:
            st.error(f"An error occurred: {e}")