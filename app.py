import streamlit as st
from google import genai
import replicate
import os
import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Page Setup
st.set_page_config(page_title="AI Movie Trailer Generator", page_icon="🎬", layout="wide")
st.title("🎬 Multi-Shot AI Video Pipeline")
st.write("Automatically breaks multi-scene prompts into individual clips, renders them via AI, and stitches them into a final trailer.")

# API Keys
gemini_key = st.secrets.get("GEMINI_API_KEY", "") or st.sidebar.text_input("Gemini API Key", type="password")
replicate_token = st.secrets.get("REPLICATE_API_TOKEN", "") or st.sidebar.text_input("Replicate API Token", type="password")

master_prompt = st.text_area(
    "Master Trailer Script / Outline:",
    value="A 60-second trailer set in Abuja: Dawn highway race on Airport Road; Wuse II showroom key swap; CBD neon workshop Pagani engine discovery; Garki market Lamborghini scene; Midnight Idu drift and Guzape hill pursuit; Sunset vintage Mustang drive at Zuma Rock.",
    height=120
)

if st.button("Generate & Stitch Full Trailer", type="primary"):
    if not gemini_key or not replicate_token:
        st.error("Please provide both Gemini and Replicate API Keys.")
    else:
        os.environ["REPLICATE_API_TOKEN"] = replicate_token
        client = genai.Client(api_key=gemini_key)
        
        # Step 1: Break master prompt into 5-second shot prompts
        with st.spinner("Deconstructing script into individual 5-second shot prompts..."):
            breakdown_instruction = """
            Take the user's master trailer description and output exactly 6 distinct, short video generation prompts (one for each 5-second scene).
            Format the output strictly as a JSON list of strings, like this:
            ["Shot 1 prompt...", "Shot 2 prompt...", "Shot 3 prompt...", "Shot 4 prompt...", "Shot 5 prompt...", "Shot 6 prompt..."]
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"{breakdown_instruction}\n\nMaster Description: {master_prompt}"
            )
            
            # Simple list parsing
            import json
            try:
                shot_prompts = json.loads(response.text.strip())
            except:
                st.error("Failed to parse shot breakdown. Try clicking generate again.")
                st.stop()

        st.subheader("Generated Shot List")
        for i, shot in enumerate(shot_prompts, 1):
            st.text(f"Shot {i}: {shot}")

        # Step 2: Render individual clips and download locally
        clip_files = []
        progress_bar = st.progress(0)
        
        for idx, shot in enumerate(shot_prompts):
            with st.spinner(f"Rendering Shot {idx+1} of {len(shot_prompts)} via Video API..."):
                output = replicate.run(
                    "minimax/video-01",
                    input={"prompt": shot}
                )
                
                # Download MP4 file
                video_url = str(output)
                res = requests.get(video_url)
                file_path = f"clip_{idx+1}.mp4"
                with open(file_path, "wb") as f:
                    f.write(res.content)
                clip_files.append(file_path)
                
            progress_bar.progress((idx + 1) / len(shot_prompts))

        # Step 3: Stitch clips using MoviePy
        with st.spinner("Stitching shot clips into final combined trailer..."):
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
