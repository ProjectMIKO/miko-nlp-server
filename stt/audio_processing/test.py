import torchaudio

# torchaudio 백엔드를 설정하지 않아도 기본적으로 작동하는지 확인
torchaudio.set_audio_backend("sox_io")
print(torchaudio.get_audio_backend())

# 샘플 wav 파일을 로드하여 ffmpeg가 제대로 작동하는지 확인합니다.
waveform, sample_rate = torchaudio.load("stt/audio_processing/aa.wav")
print(waveform.shape, sample_rate)
