"""读取 LRC，并生成 FFmpeg 可以烧录到视频里的 ASS 字幕。"""
import re
from pathlib import Path


def read_lrc(path, offset=0):
    raw = Path(path).read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('gb18030')
    tag = re.search(r'\[offset:([+-]?\d+)\]', text, re.I)
    shift = offset + (int(tag[1]) / 1000 if tag else 0)
    rows = {}
    for line in text.splitlines():
        stamps = re.findall(r'\[(\d+):(\d+(?:\.\d+)?)\]', line)
        words = re.sub(r'\[[^\]]*\]', '', line).strip()
        for minute, second in stamps:
            rows[max(0, int(minute)*60 + float(second) + shift)] = words
    if not rows:
        raise ValueError('歌词里没有时间标记，请使用 LRC 文件。')
    return sorted(rows.items())


def stamp(t):
    cs = max(0, round(t*100))
    return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'


def write_ass(rows, path, duration, width, height):
    size = round(height * .047)
    header = f'''[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei,{size},&H00F7F4EF,&H00FFFFFF,&H00201812,&H80000000,0,0,0,0,100,100,1,0,1,1.2,0,2,60,60,{round(height*.10)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    events = []
    for i, (start, words) in enumerate(rows):
        end = min(duration, rows[i+1][0] if i+1 < len(rows) else start+8)
        if not words or end <= start:
            continue
        # 禁用歌词中的 ASS 控制字符，保留普通可见文本。
        words = words.replace('\\', '＼').replace('{', '｛').replace('}', '｝')
        events.append(f'Dialogue: 0,{stamp(start)},{stamp(end)},Default,,0,0,0,,{{\\fad(150,150)}}{words}')
    Path(path).write_text(header + '\n'.join(events), encoding='utf-8-sig')
