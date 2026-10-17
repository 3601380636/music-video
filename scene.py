"""用简单图形绘制雨夜窗景。所有运动按整周期计算，便于无缝循环。"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter


class RainScene:
    def __init__(self, width, height):
        self.w, self.h = width, height
        rng = random.Random(18)
        self.rain = [(rng.random(), rng.random(), rng.uniform(.015,.05), rng.choice([1,2,3])) for _ in range(140)]
        base = Image.new('RGB', (width,height))
        d = ImageDraw.Draw(base)
        for y in range(height):
            k = y/height
            d.line((0,y,width,y), fill=(int(13-5*k),int(29-13*k),int(44-18*k)))
        glow = Image.new('RGB',(width,height),(0,0,0))
        g = ImageDraw.Draw(glow)
        g.ellipse((width*.38,-height*.35,width*1.1,height*.7),fill=(19,53,65))
        base = Image.blend(base,glow.filter(ImageFilter.GaussianBlur(width*.15)),.35)
        city = Image.new('RGBA',(width,height))
        c = ImageDraw.Draw(city)
        for x in range(-30,width,round(width*.055)):
            top = rng.randint(int(height*.33),int(height*.57))
            bw = rng.randint(int(width*.035),int(width*.065))
            c.rectangle((x,top,x+bw,height*.76), fill=(10,22,30,255))
            for wx in range(x+7,x+bw-3,10):
                for wy in range(top+12,int(height*.72),17):
                    if rng.random()<.32:
                        c.rectangle((wx,wy,wx+2,wy+4),fill=rng.choice([(181,151,104,180),(99,160,174,160)]))
        base = Image.alpha_composite(base.convert('RGBA'),city.filter(ImageFilter.GaussianBlur(1.4)))
        self.base = base

    def frame(self, t, period=8):
        w,h = self.w,self.h
        im = self.base.copy()
        layer = Image.new('RGBA', im.size)
        d = ImageDraw.Draw(layer)
        phase = t/period
        for x,y,length,speed in self.rain:
            py = (y+phase*speed)%1
            px = x + .002*math.sin(2*math.pi*phase)
            for wrap in [-1,0,1]:
                yy = (py+wrap)*h
                d.line((px*w,yy,px*w-3,yy+length*h),fill=(155,198,208,65),width=1)
                d.ellipse((px*w-1,yy+length*h-2,px*w+1,yy+length*h+2),fill=(175,213,220,85))
        im = Image.alpha_composite(im,layer)
        d = ImageDraw.Draw(im)
        # 窗框、窗台、杯子：保持克制的前景剪影。
        d.rectangle((0,0,w*.035,h),fill=(7,14,21))
        d.rectangle((w*.965,0,w,h),fill=(7,14,21))
        d.rectangle((w*.29,0,w*.303,h*.77),fill=(8,17,24))
        d.line((w*.304,0,w*.304,h*.77),fill=(37,54,62),width=2)
        d.rectangle((0,h*.76,w,h*.785),fill=(30,39,44))
        d.rectangle((0,h*.785,w,h),fill=(9,17,24))
        x,y=w*.78,h*.70
        d.ellipse((x+w*.043,y+h*.01,x+w*.067,y+h*.052),outline=(122,115,99),width=3)
        d.rounded_rectangle((x,y,x+w*.05,h*.76),radius=5,fill=(135,126,108))
        d.ellipse((x,y-3,x+w*.05,y+5),fill=(49,43,38))
        steam = Image.new('RGBA',im.size)
        sd = ImageDraw.Draw(steam)
        for j in range(2):
            pts=[]
            for n in range(35):
                u=n/34
                pts.append((x+w*(.018+j*.017)+math.sin(u*7+phase*2*math.pi+j)*w*.003,y-u*h*.075))
            sd.line(pts,fill=(205,210,201,45),width=2)
        return Image.alpha_composite(im,steam.filter(ImageFilter.GaussianBlur(1))).convert('RGB')
