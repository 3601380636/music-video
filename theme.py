"""离线读取歌词关键词与音频强弱，为整首歌选一个可循环的画面。"""
from array import array
import math
import subprocess


KEYWORDS = {
    'rain': ('雨', '下雨', '雨滴', '潮湿', '淋湿', '雨伞'),
    'solace': ('痛苦', '疼', '伤', '难过', '悲伤', '安慰', '温柔', '拥抱', '治愈', '哭', '泪'),
    'dream': ('梦', '星', '月', '宇宙', '天空', '飞', '自由', '光'),
    'warmth': ('阳光', '晴', '夏', '微笑', '快乐', '希望', '明天', '花'),
}


def choose_theme(rows):
    """只看歌词正文，不把 LRC 开头的作词/编曲署名算进去。"""
    words = '\n'.join(text for _, text in rows if not any(k in text for k in ('作词', '作曲', '编曲', '制作人')))
    scores = {name: sum(words.count(word) for word in terms) for name, terms in KEYWORDS.items()}
    theme = max(scores, key=scores.get)
    return theme if scores[theme] else 'dream'


def audio_energy(ffmpeg, path):
    """只抽取开头 45 秒的低采样率单声道 PCM，估算音乐整体强弱。"""
    result = subprocess.run(
        [ffmpeg, '-v', 'error', '-i', str(path), '-t', '45', '-ac', '1', '-ar', '8000',
         '-f', 's16le', '-'], capture_output=True, check=True
    )
    pcm = array('h')
    pcm.frombytes(result.stdout[:len(result.stdout)//2*2])
    if not pcm:
        return .5
    # 以每 0.25 秒一个窗口计算 RMS，再取较响窗口的均值，避免前奏静音误判。
    window = 2000
    levels = []
    for i in range(0, len(pcm)-window+1, window):
        rms = math.sqrt(sum(sample*sample for sample in pcm[i:i+window])/window)/32768
        levels.append(rms)
    levels.sort()
    top = levels[len(levels)//2:]
    return min(1., max(.15, sum(top)/len(top)*2.5)) if top else .5
