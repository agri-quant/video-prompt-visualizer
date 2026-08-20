import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel
import urllib.parse

# 1. PAGE SETUP
st.set_page_config(
    page_title="Gidan Gudu - AI Storyboard Engine",
    page_icon="🎨",
    layout="wide"
)

st.title("🎬 Gidan Gudu - Shot Storyboard Engine")
st.write("Converts master scripts into cinematic multi-shot breakdowns and visualizes keyframes using strictly **Google Gemini**.")

# 2. API KEY SETUP
gemini_key = st.secrets.get("GEMINI_API_KEY", "") or st.sidebar.text_input("Google AI Studio API Key", type="password")

# Optimized Master Prompt tailored specifically for Storyboard Visuals
master_prompt = st.text_area(
    "Master Script / Scene Description:",
    value="TITLE: Gidan Gudu (The Escape House). A high-octane automotive crime thriller set in Abuja.\n\n"
          "SCENE BREAKDOWN:\n"
          "1. [Dawn Race]: Low-angle tracking shot of a BMW M5 F90 and Nissan Skyline GT-R R34 racing side-by-side on a misty Airport Road, Abuja highway at sunrise.\n"
          "2. [The Swap]: Close-up of a Hausa businessman in a crisp white kaftan swapping a Mercedes-Brabus key fob and encrypted folder across a polished marble desk in a luxury Wuse II showroom.\n"
          "3. [The Find]: Interior of a dark neon-lit underground garage in CBD Abuja, mechanics examining a twin-turbo V12 engine inside a Pagani Huayra with glowing blue diagnostic screens.\n"
          "4. [Culture Meets Speed]: A wide daylight shot of a bright yellow Lamborghini Huracán parked in the middle of vibrant, bustling Garki Market surrounded by colourful fabric stalls and traders.\n"
          "5. [Midnight Mayhem]: Night action shot of tuned street cars drifting in formation surrounded by tire smoke in an industrial warehouse district in Idu, high-speed energy.\n"
          "6. [Abuja Icon Finish]: Wide golden-hour cinematic view of a classic red 1969 Mustang Fastback parked on a hill along Kuje Road with the majestic, towering silhouette of Zuma Rock lit by the setting sun.",
    height=220
)

# 3. SCHEMA DEFINITION for Gemini Structured Output
class TrailerBreakdown(BaseModel):
    shots: list[str]

# 4. GENERATION PIPELINE
if st.button("Generate Shot List & Keyframes", type="primary"):
    if not gemini_key:
        st.error("Please provide your Google AI Studio API Key in the sidebar or secrets.")
    else:
        # Initialize Gemini Client
        client = genai.Client(api_key=gemini_key)
        
        # Step A: Deconstruct script into modular shot prompts
        with st.spinner("Breaking script into cinematic shot list..."):
            breakdown_instruction = """
            Take the user's master trailer description and convert it into exactly 6 distinct, highly cinematic keyframe visual prompts (one for each key shot).
            Each shot prompt must be detailed, photorealistic (8k film, cinematic lighting, ultra-wide 16:9), focusing on subject, atmospheric lighting, and Abuja environment.
            Do not include video motion terms like 'panning' or 'zooming'; phrase them purely as high-impact still photograph composition prompts.
            """
            
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"{breakdown_instruction}\n\nMaster Description: {master_prompt}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=TrailerBreakdown
                    )
                )
                
                parsed_data = TrailerBreakdown.model_validate_json(response.text)
                shot_prompts = parsed_data.shots
                
            except Exception as e:
                st.error(f"Error breaking down prompt: {str(e)}")
                st.stop()

        st.subheader("Generated Storyboard Breakdown & Visual Keyframes")
        
        # Step B: Visualize each shot as a high-quality image keyframe
        for idx, shot in enumerate(shot_prompts, 1):
            st.markdown(f"### Keyframe Shot {idx} / 6")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.info(f"**Visual Composition Prompt:**\n\n{shot}")
            
            with col2:
                with st.spinner(f"Rendering Keyframe Visual {idx}..."):
                    base_url = "https://image.pollinations.ai/prompt/"
                    style_tags = "cinematic film still, 8k resolution, highly detailed, photorealistic photography, "
                    
                    encoded_prompt = urllib.parse.quote(f"{style_tags}{shot}")
                    final_image_url = f"{base_url}{encoded_prompt}?width=1280&height=720&seed={idx}&nologo=true&private=true&enhance=true"
                    
                    st.image(
                        final_image_url, 
                        caption=f"Visual Keyframe {idx} - Gidan Gudu Storyboard", 
                        use_container_width=True
                    )
            
            st.divider()

        st.success("Storyboard Complete! Your Gidan Gudu concept cards are ready.")
