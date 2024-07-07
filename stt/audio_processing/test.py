import torchaudio
import logging
import os

# 디버깅 로그 활성화
logging.basicConfig(level=logging.DEBUG)

# FFmpeg 경로 확인
ffmpeg_path = os.popen('which ffmpeg').read().strip()
print(f"FFmpeg path: {ffmpeg_path}")

# torchaudio 백엔드 확인
print("Current audio backend:", torchaudio.get_audio_backend())

# 샘플 wav 파일을 로드하여 ffmpeg가 제대로 작동하는지 확인합니다.
try:
    waveform, sample_rate = torchaudio.load("stt/audio_processing/aa.wav")
    print("Waveform shape:", waveform.shape)
    print("Sample rate:", sample_rate)
except Exception as e:
    print(f"Error loading audio file: {e}")
