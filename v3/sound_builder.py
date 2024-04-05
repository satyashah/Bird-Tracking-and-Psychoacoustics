import wave

# Load the two .wav files
sound1_path = "test_sounds/440Hz.wav"
sound2_path = "test_sounds/1kHz.wav"

with wave.open(sound1_path, 'rb') as wf1, wave.open(sound2_path, 'rb') as wf2:
    # Ensure both files have the same sample width, channels, and frame rate
    assert wf1.getsampwidth() == wf2.getsampwidth(), "Sample widths must be the same"
    assert wf1.getnchannels() == wf2.getnchannels() == 1, "Both files must have 1 channel"
    assert wf1.getframerate() == wf2.getframerate(), "Frame rates must be the same"

    # Create a new stereo .wav file
    output_path = "cs.wav"
    with wave.open(output_path, 'wb') as output_wf:
        output_wf.setnchannels(2) # Stereo
        output_wf.setsampwidth(wf1.getsampwidth())
        output_wf.setframerate(wf1.getframerate())

        # Define chunk size for reading frames
        chunk_size = 4096 # Adjust based on your needs

        # Read and interleave frames in chunks
        while True:
            chunk1 = wf1.readframes(chunk_size)
            chunk2 = wf2.readframes(chunk_size)
            if not chunk1 or not chunk2:
                break
            # Interleave frames for left and right channels
            interleaved_chunk = b''.join([chunk1[i:i+2] + chunk2[i:i+2] for i in range(0, len(chunk1), 2)])
            output_wf.writeframes(interleaved_chunk)
