# Rain MV · 雨夜歌词视频

一个适合 Python 项目练习的小工具：选择本地音乐和 LRC 歌词，生成循环雨夜窗景、逐句歌词字幕，并导出 MP4。

当前雨景为《雨爱》设计：青蓝与玫瑰色的柔焦灯光、玻璃雨痕、水面涟漪和细微颗粒。画面每 8 秒循环；字幕根据歌曲时间独立推进。当前版本不自动理解任意歌曲或识别歌词，也不做逐字卡拉 OK 高亮。

字幕采用 Windows 微软雅黑 Light，暖白色、大字距与留白布局。入场上浮并由模糊变清晰，离场轻微放大、模糊淡出；每四条时间记录切换左、中、右构图。长句自动缩小并换行，短句自动缩短进出场动画。可在 `lyrics.py` 的 `write_ass` 中调整字号、配色、位置及动画时长，在 `scene.py` 中调整背景。

## 在 Windows / VS Code 中运行

安装 Python 3.10 或更新版本，用 VS Code 打开本项目文件夹。在终端依次执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

依次选择音频和 LRC，等待生成 `renders/rain_mv.mp4`。编码器随 imageio-ffmpeg 的 Windows 安装包提供，无需另装系统 FFmpeg。默认 1280×720、24 帧，字体为 Windows 微软雅黑。首次安装依赖需要联网，生成视频在本地进行。

先导出 30 秒预览：

```powershell
.\.venv\Scripts\python.exe app.py --audio "media/雨爱.mp3" --lyrics "media/雨爱.lrc" --preview 30 --output "renders/preview.mp4"
```

完整视频去掉 `--preview 30` 即可。字幕比歌声早时加 `--offset 0.5` 让字幕延迟半秒；字幕晚时使用负数。程序也读取 LRC 内的 offset 标签，两者相加。最后一句默认最多显示 8 秒；需要更精确的结束时间，可在 LRC 中加入带时间标记的空行。

## 代码怎么读

1. `lyrics.py`：字符串处理、正则表达式、时间转换。
2. `scene.py`：类、循环、坐标、正弦函数与图像绘制。
3. `app.py`：参数解析、文件选择、子进程及音视频合成。

可以先改背景配色、雨滴数量，再研究字幕时间，最后理解合成流程。本项目不需要训练 PyTorch 模型。

## 上传 GitHub

在 GitHub 创建空仓库，不勾选自动添加 README、许可证或 .gitignore。在本项目目录运行：

```powershell
git init
git add .
git commit -m "Add rainy lyric video generator"
git branch -M main
git remote add origin 你的仓库地址
git push -u origin main
```

提交前用 `git status` 检查列表。`.gitignore` 已排除本地音乐、LRC、视频、虚拟环境和渲染目录；歌曲素材不随代码发布。将自己的素材放进 `media/` 即可。

## 已知边界

支持带行级时间戳的 LRC；同步精度取决于歌词是否对应这版录音，可用 offset 修正整体偏移。视频渲染需要一定时间，终端会显示阶段信息。重新运行会覆盖同名输出视频。该项目输入普通音频，不直接支持 NCM。
