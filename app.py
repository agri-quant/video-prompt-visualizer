import os
import requests
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel
import replicate
from moviepy import VideoFileClip, concatenate_videoclips

# Page Setup
st.set_page_config(page_title="AI Movie Trailer Generator", page_icon="🎬", layout="wide")
st.title("🎬 Multi-Shot AI Video Pipeline")
st.write("Automatically breaks multi-scene prompts into individual clips, renders them via AI, and stitches them into a final trailer.")

# API Keys Setup
gemini_key = st.secrets.get("GEMINI_API_KEY", "") or st.sidebar.text_input("Gemini API Key", type="password")
replicate_token = st.secrets.get("REPLICATE_API_TOKEN", "") or st.sidebar.text_input("Replicate API Token", type="password")

master_prompt = st.text_area(
    "Master Trailer Script / Outline:",
    value="A 60-second trailer set in Abuja: Dawn highway race on Airport Road; Wuse II showroom key swap; CBD neon workshop Pagani engine discovery; Garki market Lamborghini scene; Midnight Idu drift and Guzape hill pursuit; Sunset vintage Mustang drive at Zuma Rock.",
    height=120
)

class TrailerBreakdown(BaseModel):
    shots: list[str]

if st.button("Generate & Stitch Full Trailer", type="primary"):
    if not gemini_key or not replicate_token:
        st.error("Please provide both Gemini and Replicate API Keys.")
    else:
        # Direct Token Assignment
        clean_replicate_token = replicate_token.strip().replace('"', '').replace("'", "")
        os.environ["REPLICATE_API_TOKEN"] = clean_replicate_token
        
        # Initialize Replicate Client explicitly with token
        rep_client = replicate.Client(api_token=clean_replicate_token)
        genai_client = genai.Client(api_key=gemini_key)
        
        # Step 1: Break master prompt into shot prompts
        with st.spinner("Deconstructing script into individual shot prompts..."):
            breakdown_instruction = """
            Take the user's master trailer description and convert it into 6 distinct, short video generation prompts (one for each 5-second scene).
            Each shot must be detailed, cinematic, and focused on a single visual action.
            """
            try:
                response = genai_client.models.generate_content(
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
                st.error(f"Failed to break down prompt: {str(e)}")
                st.stop()

        st.subheader("Generated Shot List")
        for i, shot in enumerate(shot_prompts, 1):
            st.text(f"Shot {i}: {shot}")

        # Step 2: Render individual clips using explicitly authenticated client
        clip_files = []
        progress_bar = st.progress(0)
        
        for idx, shot in enumerate(shot_prompts):
            with st.spinner(f"Rendering Shot {idx+1} of {len(shot_prompts)} via Video API..."):
                try:
                    # Run model using authenticated rep_client instance
                    output = rep_client.run(
                        "minimax/video-01",
                        input={"prompt": shot}
                    )
                    
                    video_url = str(output)
                    res = requests.get(video_url)
                    file_path = f"clip_{idx+1}.mp4"
                    with open(file_path, "wb") as f:
                        f.write(res.content)
                    clip_files.append(file_path)
                except Exception as clip_err:
                    st.error(f"Error rendering Shot {idx+1}: {str(clip_err)}")
                    st.stop()
                
            progress_bar.progress((idx + 1) / len(shot_prompts))

        # Step 3: Stitch clips using MoviePy
        with st.spinner("Stitching shot clips into final combined trailer..."):
            try:
                loaded_clips = [VideoFileClip(c) for c in clip_files]
                final_clip = concatenate_videoclips(loaded_clips)
                final_output_path = "final_abuja_trailer.mp4"
                final_clip.write_videofile(final_output_path, codec="libx264")

                st.success("Trailer Complete!")
                st.video(final_output_path)
                
                with open(final_output_path, "rb") as f:
                    st.download_button(
                        label="🎥 Download 60-Second Stitched Trailer (.mp4)",
                        data=f,
                        file_name="Gidan_Gudu_Trailer.mp4",
                        mime="video/mp4"
                    )
            except Exception as stitch_err:
                st.error(f"Error stitching video files: {str(stitch_err)}")
