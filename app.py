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

# 2. API KEY SETUP (Only ONE key needed now)
gemini_key = st.secrets.get("GEMINI_API_KEY", "") or st.sidebar.text_input("Google AI Studio API Key", type="password")

# Master prompt for the Abuja trailer
master_prompt = st.text_area(
    "Master Script / Scene Description:",
    value="A 60-second trailer set in Abuja: Dawn highway race on Airport Road; Wuse II showroom key swap; CBD neon workshop Pagani engine discovery; Garki market Lamborghini scene; Midnight Idu drift and Guzape hill pursuit; Sunset vintage Mustang drive at Zuma Rock.",
    height=120
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
            Each shot must be detailed, photorealistic (8k film, cinematic lighting, ultra-wide), and focus on one major action/subject.
            Include specific Abuja atmosphere (dawn, neon, industrial smoke, golden hour Zuma Rock silhouette).
            """
            
            try:
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=f"{breakdown_instruction}\n\nMaster Description: {master_prompt}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=TrailerBreakdown
                    )
                )
                
                # automatically parsed by Pydantic schema
                parsed_data = TrailerBreakdown.model_validate_json(response.text)
                shot_prompts = parsed_data.shots
                
            except Exception as e:
                st.error(f"Error breaking down prompt: {str(e)}")
                st.stop()

        st.subheader("Generated Shot Breakdown & Keyframe Visuals")
        
        # Step B: Visualize each shot as a high-quality image keyframe
        for idx, shot in enumerate(shot_prompts, 1):
            st.markdown(f"### Shot {idx} / 6")
            
            # Create two columns: one for text, one for image
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.info(f"**Visual Prompt for Keyframe:**\n\n{shot}")
            
            with col2:
                with st.spinner(f"Generating Keyframe Visual {idx}..."):
                    # We use Pollinations AI to serve free, key-free visualizations.
                    # It works instantly by embedding a simple URL.
                    # Format: https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&seed={seed}&nologo=true
                    
                    base_url = "https://image.pollinations.ai/prompt/"
                    style_tags = "8k, ultra-photorealistic, cinematic film, highly detailed, "
                    
                    # Encode the prompt for the URL
                    encoded_prompt = urllib.parse.quote(f"{style_tags}{shot}")
                    
                    # Generate the final URL with specific settings
                    final_image_url = f"{base_url}{encoded_prompt}?width=1280&height=720&seed={idx}&nologo=true&private=true&enhance=true"
                    
                    # Display the image instantly
                    st.image(
                        final_image_url, 
                        caption=f"Visual Keyframe Shot {idx} - Cinematic Preview", 
                        use_container_width=True
                    )
            
            st.divider()

        st.success("Storyboard Complete! You have six high-quality cinematic visual concept cards.")
