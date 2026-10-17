"""柔焦雨夜：青蓝与玫瑰色光晕、玻璃雨痕、水面涟漪。"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont


class RainScene:
    def __init__(self, width, height):
        self.w, self.h = width, height
        rng = random.Random(18)
        self.rain = [(rng.random(), rng.random(), rng.uniform(.025,.10), rng.choice([1,2])) for _ in range(65)]
        self.rings = [(rng.uniform(.12,.95),rng.uniform(.79,.97),rng.random()) for _ in range(9)]
        small = Image.new('RGB',(320,180))
        px = small.load()
        lights = [(.86,.32,.24,(93,50,67)),(.18,.55,.32,(15,65,76)),(.68,.66,.17,(141,92,72))]
        for y in range(180):
            for x in range(320):
                c = [7.,14.,25.]
                for cx,cy,r,color in lights:
                    a = math.exp(-((x/320-cx)**2+(y/180-cy)**2)/(r*r))
                    for k in range(3):
                        c[k] += color[k]*a
                px[x,y] = tuple(int(v) for v in c)
        bokeh = Image.new('RGBA',small.size)
        d = ImageDraw.Draw(bokeh)
        for _ in range(48):
            x,y = rng.uniform(170,330),rng.uniform(25,145)
            r = rng.uniform(1.5,7)
            color = rng.choice([(247,174,156,45),(143,198,211,45),(226,199,160,50)])
            d.ellipse((x-r,y-r,x+r,y+r),fill=color)
            d.line((x,y+r+2,x+r*.2,178),fill=(*color[:3],12),width=max(1,int(r)))
        small = Image.alpha_composite(small.convert('RGBA'),bokeh.filter(ImageFilter.GaussianBlur(2)))
        self.base = small.resize((width,height),Image.Resampling.BICUBIC)
        grain = Image.new('RGBA',(320,180))
        grain.putdata([(235,222,212,rng.randrange(0,9)) for _ in range(320*180)])
        self.base = Image.alpha_composite(self.base,grain.resize((width,height)))
        self.glow = Image.new('RGBA',(width,height))
        gd = ImageDraw.Draw(self.glow)
        gd.ellipse((width*.58,height*.08,width*1.12,height*.85),fill=(210,111,133,10))
        self.glow = self.glow.filter(ImageFilter.GaussianBlur(width*.10))

    def frame(self, t, period=8):
        w,h = self.w,self.h
        phase = (t/period)%1
        im = self.base.copy()
        glow = self.glow.copy()
        glow.putalpha(glow.getchannel('A').point(lambda a: int(a*(.65+.35*math.sin(2*math.pi*phase)))))
        im = Image.alpha_composite(im,glow)
        layer = Image.new('RGBA',im.size)
        d = ImageDraw.Draw(layer)
        for x,y,length,speed in self.rain:
            py = (y+phase)%1
            alpha = 33 if .12 < x < .62 else 65
            for wrap in [-1,0,1]:
                yy=(py+wrap)*h
                d.line((x*w,yy,x*w-w*.006,yy+length*h),fill=(191,218,226,alpha),width=max(1,round(w/1280)))
                d.ellipse((x*w-w*.006-1,yy+length*h-2,x*w-w*.006+1,yy+length*h+2),fill=(220,231,230,alpha))
        for x,y,start in self.rings:
            age=(phase+start)%1
            r=w*(.008+.065*age)
            a=int(42*math.sin(math.pi*age)**2)
            d.ellipse((x*w-r,y*h-r*.13,x*w+r,y*h+r*.13),outline=(194,201,210,a),width=1)
        im=Image.alpha_composite(im,layer)
        overlay=Image.new('RGBA',im.size)
        d=ImageDraw.Draw(overlay)
        margin=w*.065
        d.line((margin,h*.13,w-margin,h*.13),fill=(222,219,215,45),width=1)
        d.line((margin,h*.90,w-margin,h*.90),fill=(222,219,215,35),width=1)
        try:
            font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',max(9,round(h*.016)))
        except OSError:
            font=ImageFont.load_default()
        d.text((margin,h*.083),'R A I N   /   A F T E R   H O U R S',font=font,fill=(226,222,217,150))
        d.text((margin,h*.925),'S O U N D   I N   M O T I O N',font=font,fill=(226,222,217,95))
        return Image.alpha_composite(im,overlay).convert('RGB')
