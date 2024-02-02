from pytube import YouTube
from moviepy.editor import VideoFileClip
import moviepy.video.fx.crop as crop_vid
from moviepy.editor import TextClip, CompositeVideoClip


import os

# def download_youtube_video(url, output_path):
#     yt = YouTube(url)
#     stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
#     stream.download(output_path=output_path)
#     return stream.default_filename


def download_youtube_video(url, output_path):
    yt = YouTube(url)

    # Try to get the stream in 1080p
    stream = yt.streams.filter(
        progressive=True, file_extension='mp4', res='1080p').first()
    if stream is not None:
        print("Processing with 1080p stream.")
        stream.download(output_path=output_path)
        return stream.default_filename

    # If 1080p is not available, try 720p
    stream = yt.streams.filter(
        progressive=True, file_extension='mp4', res='720p').first()
    if stream is not None:
        print("Processing with 720p stream.")
        stream.download(output_path=output_path)
        return stream.default_filename

    # If neither 1080p nor 720p is available, download any available quality
    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
    if stream is not None:
        print("No 1080p or 720p stream found. Downloading any available quality.")
        stream.download(output_path=output_path)
        return stream.default_filename

    # Return None if no suitable stream is found
    return None


def split_video(input_video, output_prefix):
    clip = VideoFileClip(input_video)
    total_duration = clip.duration
    segment_duration = 60  # Duration of each segment in seconds
    num_segments = int(total_duration // segment_duration)

    # Create output directory if it doesn't exist
    output_directory = "output_videos"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = min((i + 1) * segment_duration, total_duration)

        final_clip = clip.subclip(start_time, end_time)
        w, h = final_clip.size
        target_ratio = 1080 / 1920
        current_ratio = w / h

        if current_ratio > target_ratio:
            # The video is wider than the desired aspect ratio, crop the width
            new_width = int(h * target_ratio)
            x_center = w / 2
            y_center = h / 2
            final_clip = crop_vid.crop(final_clip, width=new_width, height=h, x_center=x_center, y_center=y_center)
        else:
            # The video is taller than the desired aspect ratio, crop the height
            new_height = int(w / target_ratio)
            x_center = w / 2
            y_center = h / 2
            final_clip = crop_vid.crop(final_clip, width=w, height=new_height, x_center=x_center, y_center=y_center)

        # Add stylish caption
        caption_text = f"Segment {i+1}"
        caption_clip = TextClip(caption_text, fontsize=50, color='white', bg_color='black', stroke_color='red',stroke_width=2, method='caption', align='center', size=(final_clip.w, None), font='Ubuntu-Bold')
        caption_clip = caption_clip.set_position(('center', 'bottom')).set_duration(final_clip.duration)
        final_clip = CompositeVideoClip([final_clip, caption_clip])

        output_path = os.path.join(output_directory, f"{output_prefix}_{i+1}.mp4")
        final_clip.write_videofile(output_path, codec="libx264", threads=4,audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True)

    clip.close()


def main():
    youtube_url = input("Enter the YouTube video URL: ")
    output_directory = "output_folder"
    output_prefix = "output_segment"
    segment_duration = 60  # Duration of each segment in seconds

    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Download YouTube video
    video_filename = download_youtube_video(youtube_url, output_directory)
    input_video = os.path.join(output_directory, video_filename)

    # Ask user if they want to create short videos
    create_short_video = input(
        "Do you want to create short videos (9:16 aspect ratio)? (yes/no): ").lower()

    if create_short_video == 'yes':
        aspect_ratio = '9:16'
    else:
        aspect_ratio = '16:9'

    # Split and store segments
    split_video(input_video, output_prefix)


if __name__ == "__main__":
    main()
