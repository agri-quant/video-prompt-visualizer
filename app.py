import streamlit as st
from google import genai
import time

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="AI Video Prompt Visualizer",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 AI Video Prompt Visualizer & Generator")
st.write("Convert raw script ideas into production-ready prompts and render video outputs.")

# 2. API KEY SETUP
api_key = st.secrets.get("GEMINI_API_KEY", "") or st.sidebar.text_input("Google AI Studio API Key", type="password")

target_tool = st.sidebar.selectbox(
    "Target AI Video Generator:",
    ["Runway Gen-3", "OpenAI Sora", "Luma Dream Machine", "Pika Labs"]
)

# 3. INPUT SCENE
st.subheader("1. Input Scene Script")
scene_input = st.text_area(
    "Paste scene details, action notes, or camera directives:",
    placeholder="EXT. AIRPORT ROAD - DAWN: A white BMW M5 and Nissan Skyline race down a 10-lane highway...",
    height=150
)

if st.button("Generate Video Prompt & Render", type="primary"):
    if not api_key:
        st.error("Please provide your Google AI Studio API Key in the sidebar or Streamlit Secrets.")
    elif not scene_input.strip():
        st.warning("Please enter a scene script description.")
    else:
        try:
            # Step A: Engineering the Prompt using Gemini
            client = genai.Client(api_key=api_key)
            
            system_instruction = f"""
            You are an expert AI Cinematographer and Prompt Engineer. 
            Convert the user's scene description into a highly detailed, cinematic video generation prompt optimized for {target_tool}.
            Include details on: Camera movement, lighting, subject action, environment, and style tags.
            Output ONLY the finalized prompt string without commentary.
            """
            
            with st.spinner("Step 1/2: Engineering cinematic video prompt..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"System Instruction: {system_instruction}\n\nScene: {scene_input}"
                )
                engineered_prompt = response.text.strip()
                
            st.subheader("2. Engineered Video Prompt")
            st.code(engineered_prompt, language="text")
            
            # Step B: Video Generation Section
            st.subheader("3. Generated Video Output")
            
            with st.spinner("Step 2/2: Rendering AI Video... (This may take a moment)"):
                # Note: Replace sample_video_url with your Video API call (e.g. Replicate / Runway API)
                # For demo playback, using a public MP4 placeholder video stream:
                sample_video_url = "https://www.w3schools.com/html/mov_bbb.mp4" 
                
                # Render video player
                st.video(sample_video_url)
                
                # Video Download Option
                st.download_button(
                    label="🎥 Download Generated Video (.mp4)",
                    data=sample_video_url,
                    file_name="generated_scene.mp4",
                    mime="video/mp4"
                )
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
