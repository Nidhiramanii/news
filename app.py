import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ---------------------------
# CONFIGURATION
# ---------------------------
API_KEY = "a3f417b116fa4104b3c547e8ee9d32e1"
BASE_URL = "https://newsapi.org/v2/top-headlines"

st.set_page_config(
    page_title="Advanced News Dashboard",
    page_icon="📰",
    layout="wide"
)

# ---------------------------
# HEADER
# ---------------------------
st.title("📰 Advanced News Dashboard")
st.markdown("Search and filter the latest headlines worldwide.")

# ---------------------------
# SIDEBAR FILTERS
# ---------------------------
st.sidebar.header("News Filters")

country = st.sidebar.selectbox(
    "Select Country",
    {
        "United States": "us",
        "India": "in",
        "United Kingdom": "gb",
        "Australia": "au",
        "Canada": "ca",
        "Germany": "de",
        "France": "fr",
        "Japan": "jp"
    }
)

category = st.sidebar.selectbox(
    "Select Category",
    [
        "general",
        "business",
        "entertainment",
        "health",
        "science",
        "sports",
        "technology"
    ]
)

keyword = st.sidebar.text_input(
    "Search Keyword",
    placeholder="e.g. AI, Tesla, Cricket"
)

num_articles = st.sidebar.slider(
    "Number of Articles",
    min_value=5,
    max_value=100,
    value=20
)

refresh = st.sidebar.button("🔄 Refresh News")

# ---------------------------
# NEWS FETCH FUNCTION
# ---------------------------
@st.cache_data(ttl=300)
def fetch_news(country_code, category_name, query, page_size):
    params = {
        "apiKey": API_KEY,
        "country": country_code,
        "category": category_name,
        "pageSize": page_size
    }

    # If keyword entered, switch to query search
    if query:
        params["q"] = query

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "status": "error",
            "message": f"Error {response.status_code}"
        }

# ---------------------------
# FETCH DATA
# ---------------------------
data = fetch_news(
    country,
    category,
    keyword,
    num_articles
)

# ---------------------------
# DISPLAY RESULTS
# ---------------------------
if data.get("status") == "ok":

    articles = data.get("articles", [])

    st.success(f"Found {len(articles)} articles")

    for article in articles:

        with st.container():

            col1, col2 = st.columns([1, 3])

            with col1:
                image_url = article.get("urlToImage")

                if image_url:
                    st.image(image_url, use_container_width=True)

            with col2:
                st.subheader(article.get("title", "No Title"))

                source = article.get("source", {}).get("name", "Unknown")

                published = article.get("publishedAt")

                try:
                    published = datetime.strptime(
                        published,
                        "%Y-%m-%dT%H:%M:%SZ"
                    ).strftime("%d %b %Y %H:%M")
                except:
                    published = "Unknown"

                st.markdown(
                    f"""
                    **Source:** {source}  
                    **Published:** {published}
                    """
                )

                description = article.get("description")

                if description:
                    st.write(description)

                st.markdown(
                    f"[🔗 Read Full Article]({article.get('url')})"
                )

            st.divider()

    # -----------------------
    # DOWNLOAD DATA
    # -----------------------
    news_df = pd.DataFrame([
        {
            "Title": a.get("title"),
            "Source": a.get("source", {}).get("name"),
            "Published": a.get("publishedAt"),
            "URL": a.get("url")
        }
        for a in articles
    ])

    csv = news_df.to_csv(index=False)

    st.download_button(
        label="📥 Download Headlines CSV",
        data=csv,
        file_name="news_headlines.csv",
        mime="text/csv"
    )

else:
    st.error(
        data.get(
            "message",
            "Unable to fetch news."
        )
    )