from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def add_text_to_video(video_path, texts):
    # Load the video clip
    video = VideoFileClip(video_path)
    
    # Create a list to hold clips
    clips = [video]
    
    # Loop through each text entry and create a text clip
    for text, start, end in texts:
        # Create a text clip (customize with your preferences)
        text = "<span background='black'>This is highlighted</span> text"
        txt_clip = (TextClip(text, fontsize=70, color='white', method="pango", font="Amiri-Bold")
                    .set_position('center')
                    .set_duration(end - start)
                    .set_start(start)
                    .set_opacity(0.5))  # Set opacity to 50%

        # Overlay the text clip on the video
        clips.append(txt_clip)
    
    # Overlay text clips on the original video clip
    final_clip = CompositeVideoClip(clips)
    
    # Return the final clip
    return final_clip

texts = [
    ("Hello", 0.5, 2),
    ("World", 3, 5),
    ("This is an example", 6, 10)
]

input_file = "songs/cat.mp4"
output_file = "outputs/output.mp4" 

output_clip = add_text_to_video(input_file, texts)
output_clip.write_videofile(output_file, codec='libx264')