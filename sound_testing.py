import pyaudio
import wave
import time

def play_sound(file_path, device_index=None):
    # Open the WAV file
    wf = wave.open(file_path, 'rb')

    # Instantiate PyAudio
    p = pyaudio.PyAudio()

    # Open stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=2,
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=device_index)

    # Read data
    data = wf.readframes(1024)

    # Play stream
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    # Stop stream
    stream.stop_stream()
    stream.close()

    # Close PyAudio
    p.terminate()

# Example usage
if __name__ == "__main__":
    # Set the file paths for the two sounds
    sound1_path = "stereo_output.wav"

    # Set the device indices for the two speakers
    speaker1_index = 2  # Index of the first speaker


    
    # # Play sound from the first speaker
    play_sound(sound1_path, device_index=speaker1_index)

    # # Wait for some time (e.g., 5 seconds)
    # time.sleep(5)

    # # Play sound from the second speaker
    # play_sound(sound2_path, device_index=speaker2_index)
