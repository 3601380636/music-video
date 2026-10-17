"""运行 python -m unittest -v 验证时间轴边界。"""
import tempfile
import unittest
from pathlib import Path
from lyrics import read_lrc, write_ass
from scene import RainScene


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


if __name__ == '__main__':
    unittest.main()
