"""运行 python -m unittest -v 验证时间轴边界。"""
import tempfile
import unittest
from pathlib import Path
from lyrics import read_lrc, write_ass
from scene import RainScene
from adaptive_scene import AdaptiveScene
from theme import choose_theme


class TimingTests(unittest.TestCase):
    def test_multiple_timestamps_offset_and_blank_clear(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            path = Path(tmp)/'sample.lrc'
            path.write_text('[offset:200]\n[00:01.00][00:03.00]重复\n[00:04.00]\n',encoding='utf-8')
            self.assertEqual(read_lrc(path, .3), [(1.5,'重复'),(3.5,'重复'),(4.5,'')])
            ass = Path(tmp)/'sample.ass'
            write_ass(read_lrc(path,.3),ass,4,960,540)
            content = ass.read_text(encoding='utf-8-sig')
            self.assertIn('0:00:03.50,0:00:04.00',content)
            self.assertEqual(content.count('Dialogue:'),2)

    def test_loop_end_matches_start(self):
        scene = RainScene(320,180)
        self.assertEqual(scene.frame(0).tobytes(),scene.frame(8).tobytes())

    def test_short_line_and_long_line_animation(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            path = Path(tmp)/'animated.ass'
            write_ass([(0,'短句'),(.3,'很长的测试句子'*10),(4,'')],path,5,1280,720)
            content = path.read_text(encoding='utf-8-sig')
            self.assertIn(r'\fad(100,100)',content)
            self.assertIn(r'\N',content)
            self.assertIn(r'\move(',content)
            self.assertIn('0:00:00.30,0:00:04.00',content)

    def test_different_lyrics_select_different_art(self):
        rain = [(1,'雨在窗前下个不停')]
        solace = [(1,'我听见你的痛苦，给你一个拥抱')]
        self.assertEqual(choose_theme(rain),'rain')
        self.assertEqual(choose_theme(solace),'solace')
        art = AdaptiveScene(320,180,'solace',.5)
        self.assertEqual(art.frame(0).tobytes(),art.frame(8).tobytes())


if __name__ == '__main__':
    unittest.main()
