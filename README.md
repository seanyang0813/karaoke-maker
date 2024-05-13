
# Karaoke box - Never miss a beat

  

## Project Description

Joint work with @kevinjzhang . This is a project to take in any music video and generate a karaoke version for it. The output includes both word level highlighting and countdown for pauses in the middle.
It uses whisper large v3 to generate the text and create options. Then with some processing, it generates a lot of timestamped texts to be displayed for pymovie clip.
Demo + explanation video: https://youtu.be/2AUswYhcplQ
Demo songs for
Love story: https://youtu.be/Y09obyya8KI
Karma: https://youtu.be/OWphfiGsipA
Youtube is saying it contains copyright content even it's unlisted so you might have access issue but it seems to be fine in the US

## project setups/ dependencies

```

pip install faster-whisper
pip install moviepy
pip install moviepy[optional]

```
Image magic is needed for rendering the text: see https://github.com/Zulko/moviepy?tab=readme-ov-file#optional-but-useful-dependencies
If you have issues with generation it be potentially related to imagemagick permissions, see:
https://github.com/Zulko/moviepy/issues/693
## How to run
```
python3 generate_karaoke.py 
```
The input and outputs directory are specified at the top of the generate_karaoke.py file. 
By default it uses cuda gpu option. However, you can use cpu by commenting the correct line next to use cpu instead
```
model  = WhisperModel(model_size, device="cuda", compute_type="float16")
#model = WhisperModel(model_size, device="cpu", compute_type="int8")
```