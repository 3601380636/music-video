"""运行 python app.py 弹出文件选择；也支持命令行参数。"""
import argparse
import re
import subprocess
import tempfile
from pathlib import Path
import imageio_ffmpeg
from lyrics import read_lrc, write_ass
from scene import RainScene


def choose_file(title, kinds):
    import tkinter as tk
    from tkinter.filedialog import askopenfilename
    root = tk.Tk()
    root.withdraw()
    try:
        return askopenfilename(title=title, filetypes=kinds)
    finally:
        root.destroy()


def main():
    p = argparse.ArgumentParser(description='雨夜循环背景 + LRC 同步字幕 → MP4')
    p.add_argument('--audio', help='MP3 / WAV / FLAC 音频路径')
    p.add_argument('--lyrics', help='LRC 歌词路径')
    p.add_argument('--output', default='renders/rain_mv.mp4')
    p.add_argument('--offset', type=float, default=0, help='字幕延迟秒数，负数为提前')
    p.add_argument('--preview', type=float, help='只导出前 N 秒用于预览')
    p.add_argument('--width', type=int, default=1280)
    p.add_argument('--height', type=int, default=720)
    args = p.parse_args()
    audio = args.audio or choose_file('选择音乐', [('音频','*.mp3 *.wav *.flac *.m4a')])
    if not audio:
        return
    lyrics = args.lyrics or choose_file('选择同步歌词', [('LRC 歌词','*.lrc')])
    if not lyrics:
        return
    audio, lyrics = Path(audio).resolve(), Path(lyrics).resolve()
    output = Path(args.output).resolve()
    if output in (audio,lyrics):
        raise ValueError('输出路径不能覆盖输入文件。')
    if args.width < 320 or args.height < 180 or args.width%2 or args.height%2:
        raise ValueError('画面宽高必须是偶数，且至少为 320×180。')
    if args.preview is not None and args.preview <= 0:
        raise ValueError('预览秒数必须大于零。')
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    info = subprocess.run([ffmpeg,'-hide_banner','-i',str(audio)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',info.stderr)
    if not match:
        raise ValueError('无法读取音频时长，请检查音频格式。')
    duration = int(match[1])*3600 + int(match[2])*60 + float(match[3])
    if args.preview:
        duration = min(duration,args.preview)
    rows = read_lrc(lyrics,args.offset)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.rain-mv-', dir=output.parent) as tmp:
        tmp = Path(tmp)
        write_ass(rows,tmp/'lyrics.ass',duration,args.width,args.height)
        scene = RainScene(args.width,args.height)
        fps,period = 24,8
        cmd = [ffmpeg,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{args.width}x{args.height}','-r',str(fps),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p',str(tmp/'loop.mp4')]
        print('正在绘制 8 秒循环雨景……',flush=True)
        proc = subprocess.Popen(cmd,stdin=subprocess.PIPE)
        try:
            for frame in range(fps*period):
                proc.stdin.write(scene.frame(frame/fps,period).tobytes())
        finally:
            proc.stdin.close()
            code = proc.wait()
        if code:
            raise RuntimeError('背景编码失败。')
        print(f'正在合成字幕和音频，时长 {duration:.1f} 秒……',flush=True)
        # 在临时目录运行，避免 Windows 路径冒号影响字幕滤镜。
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-stream_loop','-1','-i','loop.mp4','-i',str(audio),'-vf','ass=lyrics.ass','-map','0:v:0','-map','1:a:0','-t',str(duration),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(output)],cwd=tmp,check=True)
    print(f'完成：{output}',flush=True)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as e:
        raise SystemExit(f'生成失败：{e}')
