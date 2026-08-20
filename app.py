import streamlit as st
from google import genai
from PIL import Image, ImageDraw, ImageFont
import io

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & HEADER
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Video Prompt Visualizer",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 AI Video Prompt Visualizer")
st.write("Convert raw script ideas into production-ready AI video prompts and export downloadable concept cards.")

# ---------------------------------------------------------
# 2. SIDEBAR CONFIGURATION
# ---------------------------------------------------------
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Google AI Studio API Key", type="password", help="Paste your Gemini API key here.")

target_tool = st.sidebar.selectbox(
    "Target AI Video Generator:",
    ["Runway Gen-3", "OpenAI Sora", "Luma Dream Machine", "Pika Labs"]
)

aspect_ratio = st.sidebar.selectbox(
    "Aspect Ratio:",
    ["16:9 (Widescreen)", "9:16 (Vertical/Reels)", "1:1 (Square)"]
)

# ---------------------------------------------------------
# 3. HELPER FUNCTION: CREATE CONCEPT CARD IMAGE
# ---------------------------------------------------------
def create_concept_card(prompt_text, tool_name):
    """Generates a downloadable visual preview card containing the prompt details."""
    width, height = 1280, 720
    # Create dark slate canvas
    image = Image.new("RGB", (width, height), color=(18, 24, 38))
    draw = ImageDraw.Draw(image)
    
    # Draw border accent
    draw.rectangle([20, 20, width - 20, height - 20], outline=(0, 210, 255), width=3)
    
    # Render header text
    draw.text((50, 50), f"CONCEPT KEYFRAME PREVIEW | {tool_name.upper()}", fill=(0, 210, 255))
    draw.line([(50, 85), (width - 50, 85)], fill=(50, 60, 80), width=2)
    
    # Wrap text into lines for canvas display
    margin = 50
    offset = 120
    words = prompt_text.split()
    line = ""
    for word in words:
        if len(line + " " + word) < 65:
            line += " " + word
        else:
            draw.text((margin, offset), line, fill=(230, 235, 245))
            offset += 35
            line = word
    draw.text((margin, offset), line, fill=(230, 235, 245))
    
    # Save image to in-memory byte buffer
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# 4. MAIN INPUT & GENERATION LOGIC
# ---------------------------------------------------------
st.subheader("1. Input Scene Script")
scene_input = st.text_area(
    "Paste scene details, action notes, or camera directives:",
    placeholder="EXT. AIRPORT ROAD - DAWN: A white BMW M5 and Nissan Skyline race down a 10-lane highway...",
    height=150
)

if st.button("Generate Prompt & Preview", type="primary"):
    if not api_key:
        st.error("Please enter your Google AI Studio API Key in the sidebar.")
    elif not scene_input.strip():
        st.warning("Please enter a scene script description.")
    else:
        try:
            # Initialize Gemini client
            client = genai.Client(api_key=api_key)
            
            system_instruction = f"""
            You are an expert AI Cinematographer and Prompt Engineer. 
            Convert the user's scene description into a highly detailed, cinematic video generation prompt optimized for {target_tool}.
            Include details on: Camera movement, lighting, subject action, environment, aspect ratio ({aspect_ratio}), and style tags.
            Output ONLY the finalized prompt string without commentary or conversational setup.
            """
            
            with st.spinner("Engineering video prompt..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"System Instruction: {system_instruction}\n\nScene: {scene_input}"
                )
                
                engineered_prompt = response.text.strip()
                
                # Display output
                st.subheader("2. Engineered Video Prompt")
                st.code(engineered_prompt, language="text")
                
                # Generate and display visual keyframe card
                st.subheader("3. Visual Concept Card & Exports")
                concept_card_bytes = create_concept_card(engineered_prompt, target_tool)
                
                # Show image preview in Streamlit
                st.image(concept_card_bytes, caption="Generated Storyboard Concept Card", use_container_width=True)
                
                # Export / Save Options
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="💾 Download Prompt as Text (.txt)",
                        data=engineered_prompt,
                        file_name="video_prompt.txt",
                        mime="text/plain"
                    )
                    
                with col2:
                    st.download_button(
                        label="🖼️ Download Concept Card (.png)",
                        data=concept_card_bytes,
                        file_name="storyboard_concept_card.png",
                        mime="image/png"
                    )
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
