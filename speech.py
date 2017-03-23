import os
from pocketsphinx import *
import time

class LiveSpeech(Pocketsphinx):

    def __init__(self, **kwargs):
        signal.signal(signal.SIGINT, self.stop)

        self.audio_device = kwargs.pop('audio_device', None)
        self.sampling_rate = kwargs.pop('sampling_rate', 16000)
        self.buffer_size = kwargs.pop('buffer_size', 2048)
        self.no_search = kwargs.pop('no_search', False)
        self.full_utt = kwargs.pop('full_utt', False)

        self.keyphrase = kwargs.get('keyphrase')

        self.in_speech = False
        self.buf = bytearray(self.buffer_size)
        self.ad = Ad(self.audio_device, self.sampling_rate)

        super(LiveSpeech, self).__init__(**kwargs)
        self.listen_countdown = (5 * self.sampling_rate ) / 1024
        print(self.listen_countdown)

    def __iter__(self):
        with self.ad:
            with self.start_utterance():
                countdown = self.listen_countdown
                while self.ad.readinto(self.buf) >= 0:
                    self.process_raw(self.buf, self.no_search, self.full_utt)
                    countdown -= 1
                    if countdown <= 0:
                        print('restart count', time.strftime('%H:%M:%S',time.localtime(time.time())))
                        countdown = self.listen_countdown
                        with self.end_utterance():
                            yield self
                        
                    if self.keyphrase and self.hyp():
                        with self.end_utterance():
                            yield self
                    elif self.in_speech != self.get_in_speech():
                        self.in_speech = self.get_in_speech()
                        if not self.in_speech and self.hyp():
                            with self.end_utterance():
                                yield self

    def stop(self, *args, **kwargs):
        raise StopIteration



path = os.path.dirname(os.path.realpath(__file__))
pocketsphinx_data = os.getenv('POCKETSPHINX_DATA', os.path.join(path, ''))
hmmpath= os.getenv('POCKETSPHINX_HMM', os.path.join(pocketsphinx_data, 'tdt_sc_8k'))
dictpath = os.getenv('POCKETSPHINX_DIC', os.path.join(pocketsphinx_data, 'keywords.dic'))
lmpath = os.getenv('POCKETSPHINX_LM', os.path.join(pocketsphinx_data, 'keywords.lm'))



speech = LiveSpeech(
    verbose=False,
    sampling_rate=16000,
    buffer_size=2048,
    no_search=False,
    full_utt=False,
    hmm=hmmpath,
    lm=lmpath,
    dic=dictpath
)


for phrase in speech:
    print(phrase)

