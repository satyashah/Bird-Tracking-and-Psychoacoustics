import wave
import numpy as np

sound1_path = "test_sounds/StarWars60.wav"
sound2_path = "test_sounds/PinkPanther60.wav"

def merge_wav_files(wav_file1, wav_file2, output_file):
    # Open the first WAV file
    wav1 = wave.open(wav_file1, 'rb')
    params1 = wav1.getparams()

    # Open the second WAV file
    wav2 = wave.open(wav_file2, 'rb')
    params2 = wav2.getparams()

    # Ensure both files have the same number of channels and sample width
    assert params1.nchannels == params2.nchannels, "Number of channels must be the same"
    assert params1.sampwidth == params2.sampwidth, "Sample width must be the same"

    # Read the audio data from both files
    frames1 = wav1.readframes(params1.nframes)
    frames2 = wav2.readframes(params2.nframes)

    # Convert the audio data to numpy arrays
    audio_data1 = np.frombuffer(frames1, dtype=np.int16)
    audio_data2 = np.frombuffer(frames2, dtype=np.int16)

    # Reshape audio_data2 to match the length of audio_data1
    audio_data2 = np.resize(audio_data2, len(audio_data1))

    # Interleave the audio data to create stereo audio
    stereo_audio = np.vstack((audio_data1, audio_data2)).T

    # Write the interleaved audio data to a new WAV file
    with wave.open(output_file, 'wb') as wav_out:
        wav_out.setparams(params1)  # Use parameters from the first file
        wav_out.writeframes(stereo_audio.tobytes())

    # Close the input files
    wav1.close()
    wav2.close()

# Usage example:
merge_wav_files(sound1_path, sound2_path, "stereo_output.wav")
