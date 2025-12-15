import streamlit as st
from backend import analyze_image, analyze_farming_data, search_google
from PIL import Image

# --- Page Configuration ---
st.set_page_config(
    page_title="Smart Farming Chatbot",
    page_icon="🌾",
    layout="centered"
)

# --- UI Styling ---
st.title("🌾 Smart Farming Chatbot")
st.markdown("Upload a clear photo of your farm or crop, and the AI will provide smart farming insights.")

# --- Image Uploader ---
uploaded_file = st.file_uploader(
    "Choose an image...",
    type=["jpg", "jpeg", "png", "webp", "bmp"],
    help="Upload a clear, well-lit photo for the best results."
)

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Uploaded Image", use_container_width=True)
    
    # Add a button to trigger the analysis
    if st.button("🔍 Analyze Farm Data", use_container_width=True):
        with st.spinner("Analyzing your farming data... This may take a moment."):
            try:
                # Get bytes from the uploaded file
                image_bytes = uploaded_file.getvalue()

                # --- Step 1: Analyze the image ---
                image_description = analyze_image(image_bytes)

                # --- Step 2: Analyze the farming data ---
                farming_info = analyze_farming_data(image_description)

                if farming_info and not farming_info.get("error"):
                    st.success("🌾 Farming Insights Generated!")

                    # Display results in a structured way
                    with st.expander("🌱 Crop Prediction", expanded=True):
                        st.write(farming_info.get('crop_prediction', 'No crop prediction available.'))

                    with st.expander("💧 Smart Irrigation", expanded=True):
                        st.write(farming_info.get('smart_irrigation', 'No irrigation recommendations available.'))

                    with st.expander("🐛 Pest Detection", expanded=True):
                        st.write(farming_info.get('pest_detection', 'No pest detection information available.'))

                    with st.expander("📈 Yield Optimization", expanded=True):
                        st.write(farming_info.get('yield_optimization', 'No yield optimization suggestions available.'))

                    # --- Step 2: Search Google ---
                    st.subheader("📚 Learn More Online")
                    with st.spinner("Finding helpful links..."):
                        search_results = search_google(farming_info['crop_prediction'])
                        if search_results:
                            for link in search_results:
                                st.markdown(f"- [{link}]({link})")
                        else:
                            st.info("Could not find any additional links.")

                else:
                    # Handle errors from the backend
                    error_message = farming_info.get("message", "An unknown error occurred.")
                    st.error(f"⚠️ Analysis Failed: {error_message}")

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
