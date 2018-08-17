import os

# Simple example
bashcommand = "echo 'Hello World' | festival --tts"
os.system(bashcommand)

# This bash command takes the entered phrase and returns an audio .wav file and a text file of the visemes

while True:
    phrase = input("Enter phrase:")

    bashcommand = "festival -b '(set! mytext (Utterance Text " + '"' + phrase + '"))' + \
                      "' '(utt.synth mytext)' '(utt.save.wave mytext " + '"my_wav.wav")' + "' '(utt.save.segs mytext " + '"textfile"' + ")'"

    os.system(bashcommand)
