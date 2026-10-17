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
    size = round(height * .065)
    header = f'''[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei Light,{size},&H00E8F0F6,&H00FFFFFF,&H0030221B,&H90000000,0,0,0,0,100,100,3,0,1,0,1,5,60,60,40,1

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
        # 每四句调整构图；长句缩小并换行。动画时长随短句收缩。
        layout = (i // 4) % 3
        x, y, align = [(width*.12,height*.45,4), (width*.50,height*.50,5), (width*.87,height*.43,6)][layout]
        font_size = round(size * (.80 if len(words) > 18 else 1))
        spacing = max(1,round(width*.0024))
        limit = max(8, int(width*.72/(font_size+spacing)))
        words = r'\N'.join(words[n:n+limit] for n in range(0,len(words),limit))
        ms = max(1,round((end-start)*1000))
        enter, leave = min(650,ms//3), min(450,ms//3)
        tags = (f'\\an{align}\\fs{font_size}\\fsp{spacing}'
                f'\\move({x:.1f},{y+height*.025:.1f},{x:.1f},{y:.1f},0,{enter})'
                f'\\fad({enter},{leave})\\blur4\\fscx98\\fscy98'
                f'\\t(0,{enter},\\blur0\\fscx100\\fscy100)'
                f'\\t({ms-leave},{ms},\\blur5\\fscx102\\fscy102)')
        events.append(f'Dialogue: 0,{stamp(start)},{stamp(end)},Default,,0,0,0,,{{{tags}}}{words}')
    Path(path).write_text(header + '\n'.join(events), encoding='utf-8-sig')
