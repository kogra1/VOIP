import video as v
import rec_sound as s
import threading
import time
import os
import subprocess

def merge_av(video_file, audio_file, output_file):
    subprocess.run(['ffmpeg', '-i', video_file, '-i', audio_file, '-c:v', 'copy', '-c:a', 'aac', output_file])

def main():

    print(s.__file__)
    print(dir(s))
    sampling_rate = 44100
    duration = 5

    video_thread = threading.Thread(target=v.record_video, args=(duration,))
    audio_thread = threading.Thread(target=s.record_audio, args=(duration, sampling_rate))

    video_thread.start()
    audio_thread.start()
 
    video_thread.join()
    audio_thread.join()

    merge_av("output.avi", "output.wav", "final_output.mp4")
    print("Merged video and audio into final_output.mp4")

if __name__ == "__main__":
    main()


