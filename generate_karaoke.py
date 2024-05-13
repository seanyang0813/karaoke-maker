# pip install faster-whisper
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import math

THRESHOLD_TIMER = 1
COUNT_DOWN_NUM = 2
HIGHLIGHT_START_WORD = True
HIGHLIGHT_DELAY = 0.1
input_file = "songs/karma-high.mp4"
output_file = "output.mp4" 

def add_text_to_video(video_path, texts, pre_lyrics):
    # Load the video clip
    video = VideoFileClip(video_path)
    
    # Create a list to hold clips
    clips = [video]
    
    # Loop through each text entry and create a text clip
    for text, start, end in texts:
        # Create a text clip (customize with your preferences)
        txt_clip = (TextClip(text, fontsize=10, color='Yellow', method="pango", font="Amiri-Bold")
                    .set_position((0.1, 0.7), relative=True)
                    .set_duration(end - start)
                    .set_start(start)
                    .set_opacity(1))

        # Overlay the text clip on the video
        clips.append(txt_clip)
    for text, start, end in pre_lyrics:
        # Create a text clip (customize with your preferences)
        txt_clip = (TextClip(text, fontsize=10, color='Yellow', method="pango", font="Amiri-Bold")
                    .set_position((0.1, 0.8), relative=True)
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
    # second lyric line storage
    pre_lyrics = []
    for chunk_start_time in range(0, math.ceil(max_time), chunk_size):
        chunk_end_time = chunk_start_time + chunk_size
        cur_chunk = []
        while (pointer < len(texts) and texts[pointer][2] <= chunk_end_time):
            # use next element's start instead of current element's end
            (text, start, end) = texts[pointer]
            if (pointer < len(texts) - 1):
                next_start = texts[pointer + 1][1]
            else:
                next_start = end
            cur_chunk.append((text, start, next_start))
            pointer += 1
        # go through them but only highlight a portion for duration of start to end
        if len(cur_chunk) > 0:
            for i in range(len(cur_chunk)):
                (text, start, end) = cur_chunk[i]
                if HIGHLIGHT_START_WORD:
                    pangoed_text = "<span background='blue'>" + " ".join([cur_chunk[x][0] for x in range(i + 1)]) + "</span>" + " ".join([cur_chunk[x][0] for x in range(i + 1, len(cur_chunk))])
                    chunked_texts.append((pangoed_text, start + HIGHLIGHT_DELAY, end + HIGHLIGHT_DELAY))
                else:
                    if (i != 0):
                        pangoed_text = "<span background='blue'>" + " ".join([cur_chunk[x][0] for x in range(i)]) + "</span>" + " ".join([cur_chunk[x][0] for x in range(i, len(cur_chunk))])
                    else:
                        pangoed_text = " ".join([cur_chunk[x][0] for x in range(i, len(cur_chunk))])
                    chunked_texts.append((pangoed_text, start, end))
        # pre display the next line if it's available
        pre_lyrics.append((" ".join([x[0] for x in cur_chunk]), chunk_start_time, chunk_end_time))   
    # make sure text is not longer than the original clip
    last_chunk = chunked_texts[-1]
    last_chunk_modified = (last_chunk[0], last_chunk[1], math.floor(max_time))
    chunked_texts[-1] = last_chunk_modified
    pre_lyrics_chunked_texts = []
    # add some more chunks for the prelyrics
    for i in range(len(pre_lyrics) - 1):
        # look ahead for timestamp
        if (len(pre_lyrics[i + 1][0])) > 0:
            pre_lyrics_chunked_texts.append((pre_lyrics[i + 1][0], pre_lyrics[i][1], pre_lyrics[i + 1][1]))
    return (chunked_texts, pre_lyrics_chunked_texts)


model_size = "large-v3"

# Run on GPU with FP16
model = WhisperModel(model_size, device="cuda", compute_type="float16")
# or run on GPU with INT8
#model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
#model = WhisperModel(model_size, device="cpu", compute_type="int8")
segments, info = model.transcribe(input_file, beam_size=5, word_timestamps=True)

# Prepare the filter complex string for adding text
texts = []

for segment in segments:
    for word in segment.words:
        print("[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word))
        texts.append((word.word, word.start, word.end))
(chunked_texts, pre_lyrics_chunked_texts) = chunk_text(texts, 5)
print(chunked_texts)

output_clip = add_text_to_video(input_file, chunked_texts, pre_lyrics_chunked_texts)
output_clip = add_countdown(output_clip, THRESHOLD_TIMER, texts)
output_clip.write_videofile(output_file, codec='libx264')