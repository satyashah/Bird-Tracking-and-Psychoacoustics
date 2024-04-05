import wave

# Load the two .wav files
sound1_path = "test_sounds/1kHz.wav"
sound2_path = "test_sounds/440Hz.wav"

wf1 = wave.open(sound1_path, 'rb')
wf2 = wave.open(sound2_path, 'rb')

# Ensure both files have the same sample width, channels, and frame rate
print(wf1.getsampwidth(), wf2.getsampwidth())
print(wf1.getnchannels(), wf2.getnchannels(), "==1")
print(wf1.getframerate(), wf2.getframerate())

# Create a new stereo .wav file
output_path = "combined_stereo.wav"
output_wf = wave.open(output_path, 'wb')
output_wf.setnchannels(2) # Stereo
output_wf.setsampwidth(wf1.getsampwidth())
output_wf.setframerate(wf1.getframerate())

# Mix the audio data
while True:
    frame1 = wf1.readframes(1)
    frame2 = wf2.readframes(1)
    if not frame1 or not frame2:
        break
    # Combine frames for left and right channels
    output_wf.writeframes(frame1 + frame2)

# Close the files
wf1.close()
wf2.close()
output_wf.close()
