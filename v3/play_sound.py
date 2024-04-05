from pydub import AudioSegment
from pydub.playback import play
from multiprocessing import Process
import time

some_audio = AudioSegment.from_file('cs.wav', format='wav')
process = Process(target=play, args=(some_audio,))

if __name__ == '__main__':
    process.start()
    time.sleep(5) # do some stuff inbetween
    process.terminate()