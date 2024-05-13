# pip install faster-whisper
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import math

THRESHOLD_TIMER = 1
COUNT_DOWN_NUM = 2

def add_text_to_video(video_path, texts):
    # Load the video clip
    video = VideoFileClip(video_path)
    
    # Create a list to hold clips
    clips = [video]
    
    # Loop through each text entry and create a text clip
    for text, start, end in texts:
        # Create a text clip (customize with your preferences)
        txt_clip = (TextClip(text, fontsize=15, color='Blue', font="Amiri-Bold")
                    .set_position((0.1, 0.7), relative=True)
                    .set_duration(end - start)
                    .set_start(start)
                    .set_opacity(1))

        # Overlay the text clip on the video
        clips.append(txt_clip)
    # Overlay text clips on the original video clip
    final_clip = CompositeVideoClip(clips)
    
    # Return the final clip
    return final_clip

# given an end time make a clip with the duration - 2, duration - 1, duration for 2 1 0
def append_countdown_clip(end_time, clips, count_n):
    for i in range(count_n, -1, -1):
        num_clip = (TextClip(str(i), fontsize=50, color='Red', font="Amiri-Bold")
                    .set_position('center')
                    .set_duration(1)
                    .set_start(end_time - i)
                    .set_opacity(1)) 
        clips.append(num_clip)
def add_countdown(clip, countdown_threshhold, texts):
    cur_time = 0
    clips = [clip]
    for (word, start, end) in texts:
        if (start - cur_time) > countdown_threshhold:
            append_countdown_clip(start, clips, math.floor(start - cur_time))
            print("added countdown at: ", start)
        cur_time = end
    final_clip = CompositeVideoClip(clips)
    return final_clip

def chunk_text(texts, chunk_size):
    # chunk text together based on the word's end time stamp
    max_time = texts[-1][2]
    print(max_time)
    pointer = 0
    chunked_texts = []
    for chunk_start_time in range(0, math.ceil(max_time), chunk_size):
        chunk_end_time = chunk_start_time + chunk_size
        cur_chunk = []
        while (pointer < len(texts) and texts[pointer][2] <= chunk_end_time):
            (text, start, end) = texts[pointer]
            cur_chunk.append(text)
            pointer += 1
        if len(cur_chunk) > 0:
            chunked_texts.append((" ".join(cur_chunk).strip() , chunk_start_time, chunk_end_time))
    # make sure text is not longer than the original clip
    last_chunk = chunked_texts[-1]
    last_chunk_modified = (last_chunk[0], last_chunk[1], math.floor(max_time))
    chunked_texts[-1] = last_chunk_modified
    return chunked_texts


model_size = "large-v3"

# Run on GPU with FP16
model = WhisperModel(model_size, device="cuda", compute_type="float16")
# or run on GPU with INT8
#model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
#model = WhisperModel(model_size, device="cpu", compute_type="int8")
input_file = "songs/karma.mp4"
output_file = "outputs/output.mp4" 
segments, info = model.transcribe(input_file, beam_size=5, word_timestamps=True)

# Prepare the filter complex string for adding text
texts = []

for segment in segments:
    for word in segment.words:
        print("[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word))
        texts.append((word.word, word.start, word.end))
chunked_texts = chunk_text(texts, 5)
print(chunked_texts)

output_clip = add_text_to_video(input_file, chunked_texts)
output_clip = add_countdown(output_clip, THRESHOLD_TIMER, texts)
output_clip.write_videofile(output_file, codec='libx264')