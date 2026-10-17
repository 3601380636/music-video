"""无需下载素材的抽象动态画面；颜色与运动由歌词主题和音频强弱决定。"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont


PALETTES = {
    'solace': ((8,15,30), (29,42,65), (219,139,110), 'S O F T   L I G H T'),
    'dream': ((8,14,38), (40,35,88), (141,171,223), 'B E Y O N D   T H E   N I G H T'),
    'warmth': ((37,24,36), (120,69,65), (237,177,121), 'G O L D E N   H O U R'),
}


class AdaptiveScene:
    def __init__(self, width, height, theme, energy):
        self.w, self.h, self.theme = width, height, theme
        self.energy = min(1., max(0., energy))
        dark, mid, accent, self.caption = PALETTES.get(theme, PALETTES['dream'])
        self.accent = accent
        rng = random.Random(83 + sum(map(ord, theme)))
        self.particles = [(rng.random(),rng.random(),rng.uniform(.002,.008)) for _ in range(42+int(energy*40))]
        small = Image.new('RGB',(320,180))
        pix = small.load()
        for y in range(180):
            for x in range(320):
                vertical = y/180
                halo = math.exp(-((x/320-.75)**2/.16+(vertical-.48)**2/.24))
                pix[x,y] = tuple(min(255,round(dark[k]*(1-vertical*.2)+mid[k]*vertical*.38+accent[k]*halo*.37)) for k in range(3))
        self.base = small.resize((width,height),Image.Resampling.BICUBIC).convert('RGBA')
        mist = Image.new('RGBA',(width,height))
        d = ImageDraw.Draw(mist)
        for j in range(5):
            x=width*(.45+j*.11)
            y=height*(.37+.055*math.sin(j*2))
            r=height*(.12+j*.025)
            d.ellipse((x-r,y-r,x+r,y+r),fill=(*accent,15))
        self.base = Image.alpha_composite(self.base,mist.filter(ImageFilter.GaussianBlur(height*.12)))
        grain = Image.new('RGBA',(320,180))
        grain.putdata([(255,245,235,rng.randrange(0,7)) for _ in range(320*180)])
        self.base = Image.alpha_composite(self.base,grain.resize((width,height)))
        try:
            self.font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',max(9,round(height*.016)))
        except OSError:
            self.font = ImageFont.load_default()

    def frame(self, t, period=8):
        w,h = self.w,self.h
        phase = (t/period)%1
        im = self.base.copy()
        fx = Image.new('RGBA', im.size)
        d = ImageDraw.Draw(fx)
        accent = self.accent
        if self.theme == 'solace':
            # 克制的光圈像呼吸；痛苦主题保持安静，不使用跳跃的亮色颗粒。
            for n in range(5):
                age=(phase+n/5)%1
                r=w*(.06+age*.30)
                x,y=w*.72,h*.49
                alpha=int((1-age)**2*(50+self.energy*45))
                d.ellipse((x-r,y-r*.62,x+r,y+r*.62),outline=(*accent,alpha),width=max(1,round(w/1100)))
            d.line((w*.08,h*.77,w*.92,h*.77),fill=(*accent,65),width=1)
        elif self.theme == 'warmth':
            for n in range(4):
                age=(phase+n/4)%1
                y=h*(.72-.62*age)
                x=w*(.66+.13*math.sin(2*math.pi*(age+n/4)))
                r=w*(.012+.025*age)
                d.ellipse((x-r,y-r,x+r,y+r),fill=(*accent,int((1-age)*18)))
        else:
            for n in range(6):
                a=2*math.pi*(phase+n/6)
                x=w*(.73+.21*math.cos(a))
                y=h*(.49+.30*math.sin(a))
                r=w*(.018+.008*math.sin(a)**2)
                d.ellipse((x-r,y-r,x+r,y+r),outline=(*accent,22),width=1)
        for x,y,size in self.particles:
            px=x+(.04+self.energy*.04)*(math.sin(2*math.pi*(phase+y))-math.sin(2*math.pi*y))
            py=y+.01*math.sin(2*math.pi*(phase+x))
            r=max(1,w*size*.45)
            d.ellipse((px*w-r,py*h-r,px*w+r,py*h+r),fill=(*accent,24+int(self.energy*22)))
        im = Image.alpha_composite(im,fx.filter(ImageFilter.GaussianBlur(max(1,w*.0015))))
        overlay = Image.new('RGBA', im.size)
        d=ImageDraw.Draw(overlay)
        left=w*.065
        d.line((left,h*.13,w-left,h*.13),fill=(230,224,217,42))
        d.line((left,h*.90,w-left,h*.90),fill=(230,224,217,31))
        d.text((left,h*.083),self.caption,font=self.font,fill=(233,226,217,135))
        d.text((left,h*.925),'S O U N D   I N   M O T I O N',font=self.font,fill=(233,226,217,90))
        return Image.alpha_composite(im,overlay).convert('RGB')
