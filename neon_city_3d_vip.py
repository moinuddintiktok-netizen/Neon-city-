"""NEON CITY: SURVIVAL — VIP 3D Edition
Created by Chishti Bro Computers & Developers | Founder: Moinuddin Chishti
Python 3.11 + Panda3D. WASD move, mouse aim, left-click fire, E vehicle, F medkit,
SPACE dash, TAB stats, P/ESC pause, ENTER start/redeploy.
"""
import math, random, json
from pathlib import Path
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame, DirectButton
from direct.task import Task
from panda3d.core import (AmbientLight, DirectionalLight, Vec3, Vec4, TextNode,
                          Fog, WindowProperties, loadPrcFileData)

loadPrcFileData('', 'window-title Neon City: Survival — VIP 3D Edition')
loadPrcFileData('', 'win-size 1280 720')
loadPrcFileData('', 'sync-video true')

CYAN=(.05,.85,1,1); PINK=(1,.08,.48,1); PURPLE=(.55,.15,1,1)
GOLD=(1,.68,.08,1); GREEN=(.15,1,.48,1); RED=(1,.12,.12,1); WHITE=(.9,.97,1,1)
WORLD=120

def clamp(x,a,b): return max(a,min(b,x))

class NeonCityVIP(ShowBase):
    def __init__(self):
        super().__init__(); self.disableMouse(); self.setBackgroundColor(.008,.012,.035,1)
        self.rng=random.Random(22); self.state='menu'; self.paused=False; self.elapsed=0
        self.keys={k:False for k in ('w','a','s','d','arrow_up','arrow_down','arrow_left','arrow_right')}
        self.hp=100; self.max_hp=100; self.armor=40; self.ammo=240; self.medkits=3
        self.score=0; self.best=self._load_best(); self.kills=0; self.level=1; self.xp=0; self.next_xp=100
        self.credits=0; self.crystals=0; self.weapon=1; self.shot_cd=0; self.spawn_cd=1; self.boss_cd=40
        self.dash_cd=0; self.invuln=0; self.message_cd=0; self.enemies=[]; self.shots=[]; self.hostile=[]
        self.pickups=[]; self.particles=[]; self.cars=[]; self.vehicle=None
        self._lighting(); self._city(); self._player(); self._cars(); self._hud(); self._controls(); self._menu()
        self.taskMgr.add(self.update,'game-update'); self.taskMgr.add(self.camera_update,'camera-update')

    def _load_best(self):
        try: return int(json.loads((Path.home()/'.neon_city_vip.json').read_text()).get('best',0))
        except Exception: return 0
    def _save(self):
        try: (Path.home()/'.neon_city_vip.json').write_text(json.dumps({'best':max(self.best,self.score)}))
        except Exception: pass
    def _lighting(self):
        a=AmbientLight('ambient'); a.setColor(Vec4(.32,.35,.5,1)); self.render.setLight(self.render.attachNewNode(a))
        d=DirectionalLight('moon'); d.setColor(Vec4(.65,.75,1,1)); d.setDirection(Vec3(-1,-2,-3)); self.render.setLight(self.render.attachNewNode(d))
        f=Fog('neon-fog'); f.setColor(.008,.012,.035); f.setExpDensity(.007); self.render.setFog(f)
    def _box(self,parent,pos,scale,col,name='box',glow=False):
        n=self.loader.loadModel('models/box'); n.reparentTo(parent); n.setPos(*pos); n.setScale(*scale); n.setColor(*col); n.setName(name)
        if glow: n.setLightOff(1)
        return n
    def _ball(self,parent,pos,scale,col,name='orb',glow=False):
        n=self.loader.loadModel('models/misc/sphere'); n.reparentTo(parent); n.setPos(*pos); n.setScale(*scale); n.setColor(*col); n.setName(name)
        if glow:n.setLightOff(1)
        return n
    def _city(self):
        self._box(self.render,(0,0,-.65),(WORLD*2,WORLD*2,.5),(.018,.032,.07,1),'asphalt')
        for x in range(-WORLD,WORLD+1,12): self._box(self.render,(x,0,-.36),(.035,WORLD*2,.025),(.03,.22,.3,1),'neon-grid',True)
        for y in range(-WORLD,WORLD+1,12): self._box(self.render,(0,y,-.35),(WORLD*2,.035,.025),(.03,.12,.22,1),'neon-grid',True)
        palette=[(.04,.07,.14,1),(.07,.04,.14,1),(.03,.09,.13,1),(.1,.04,.1,1)]
        neon=[CYAN,PINK,PURPLE,GOLD]
        for gx in range(-108,109,24):
            for gy in range(-108,109,24):
                if abs(gx)<18 and abs(gy)<18 or self.rng.random()<.12: continue
                w=self.rng.uniform(7,12); dep=self.rng.uniform(7,12); h=self.rng.uniform(9,31)
                x=gx+self.rng.uniform(-3,3); y=gy+self.rng.uniform(-3,3); c=self.rng.choice(neon)
                self._box(self.render,(x,y,h/2),(w,dep,h),self.rng.choice(palette),'tower')
                self._box(self.render,(x,y,h+.1),(w+.25,dep+.25,.14),c,'roof-neon',True)
                self._box(self.render,(x-w/2-.04,y,h/2),(.09,dep,.1),c,'tower-edge',True)
                self._box(self.render,(x+w/2+.04,y,h/2),(.09,dep,.1),c,'tower-edge',True)
                for z in range(2,int(h)-1,3):
                    for wx in (-w*.28,0,w*.28):
                        if self.rng.random()<.7:self._box(self.render,(x+wx,y-dep/2-.06,z),(.65,.08,.5),self.rng.choice(neon),'window',True)
                if self.rng.random()<.3:
                    self._box(self.render,(x,y,h+1),(.12,.12,2),CYAN,'antenna',True)
        # Central energy reactor and hologram signs
        self._ball(self.render,(0,0,5),(3,3,3),PURPLE,'neon-core',True)
        self._ball(self.render,(0,0,5),(1.7,1.7,1.7),CYAN,'core-inner',True)
        for i in range(30):
            x=self.rng.uniform(-WORLD+8,WORLD-8); y=self.rng.uniform(-WORLD+8,WORLD-8); z=self.rng.uniform(5,18); c=self.rng.choice(neon)
            self._box(self.render,(x,y,z),(self.rng.uniform(2,4),.13,self.rng.uniform(1,2)),c,'holo-sign',True)
    def _player(self):
        self.player=self.render.attachNewNode('player'); self.player.setPos(0,0,0)
        self._box(self.player,(0,0,1.15),(.8,.65,1.35),CYAN,'armored-suit',True)
        self._ball(self.player,(0,0,2),(.4,.4,.4),WHITE,'helmet')
        self._box(self.player,(0,.48,1.35),(.85,.16,.18),GOLD,'plasma-rifle',True)
        self._box(self.player,(0,.37,2),(.5,.1,.13),PINK,'visor',True)
    def _cars(self):
        for i in range(12):
            x=self.rng.uniform(-105,105); y=self.rng.uniform(-105,105)
            if abs(x)<12 and abs(y)<12:continue
            root=self.render.attachNewNode('hovercar'); root.setPos(x,y,.55); c=self.rng.choice([CYAN,PINK,PURPLE,GOLD])
            self._box(root,(0,0,0),(3.3,5,.65),c,'car-body',True); self._box(root,(0,.1,.48),(2.1,2,.55),(.025,.05,.12,1),'cockpit')
            for sx in (-1.45,1.45):
                self._ball(root,(sx,1.7,-.08),(.2,.2,.13),GOLD,'headlight',True); self._ball(root,(sx,-2.2,-.08),(.2,.2,.13),PINK,'tail-light',True)
            self.cars.append({'node':root,'x':x,'y':y,'occupied':False})
    def _hud(self):
        self.hud=OnscreenText(text='',pos=(-1.3,.92),scale=.043,fg=CYAN,align=TextNode.ALeft,mayChange=True,shadow=(0,0,0,1))
        self.hudr=OnscreenText(text='',pos=(1.29,.92),scale=.043,fg=GOLD,align=TextNode.ARight,mayChange=True,shadow=(0,0,0,1))
        self.msg=OnscreenText(text='',pos=(0,.76),scale=.055,fg=PINK,align=TextNode.ACenter,mayChange=True,shadow=(0,0,0,1))
        self.controls=OnscreenText(text='WASD MOVE  •  MOUSE AIM  •  CLICK FIRE  •  E CAR  •  F MEDKIT  •  SPACE DASH  •  TAB STATS  •  P PAUSE',pos=(0,-.94),scale=.029,fg=(.55,.75,.9,1),align=TextNode.ACenter)
        self.stats=OnscreenText(text='',pos=(0,.25),scale=.045,fg=WHITE,align=TextNode.ACenter,mayChange=True); self.stats.hide()
    def _controls(self):
        for k in self.keys:self.accept(k,self._key,[k,True]); self.accept(k+'-up',self._key,[k,False])
        self.accept('mouse1',self.shoot); self.accept('e',self.vehicle_toggle); self.accept('f',self.medkit); self.accept('space',self.dash)
        self.accept('tab',self.stats_toggle); self.accept('p',self.pause); self.accept('escape',self.pause); self.accept('enter',self.start); self.accept('r',self.start)
    def _key(self,k,v):self.keys[k]=v
    def _menu(self):
        self.panel=DirectFrame(frameColor=(.01,.02,.08,.94),frameSize=(-.78,.78,-.55,.55),pos=(0,0,.05))
        self.title=OnscreenText(text='NEON CITY',pos=(0,.28),scale=.12,fg=CYAN,align=TextNode.ACenter,shadow=(.5,0,1,1))
        self.sub=OnscreenText(text='SURVIVAL  //  VIP 3D EDITION',pos=(0,.13),scale=.045,fg=PINK,align=TextNode.ACenter)
        self.info=OnscreenText(text='OPEN-WORLD CYBERPUNK SURVIVAL\nBosses • Hovercars • Loot • Upgrades • Neon City\n\nPRESS ENTER OR CLICK START',pos=(0,-.08),scale=.04,fg=WHITE,align=TextNode.ACenter)
        self.startbtn=DirectButton(text='START MISSION',scale=.065,pos=(0,0,-.34),command=self.start,frameColor=(.02,.42,.65,.95),text_fg=(1,1,1,1))
        self.foot=OnscreenText(text='CREATED BY CHISHTI BRO COMPUTERS & DEVELOPERS',pos=(0,-.48),scale=.026,fg=GOLD,align=TextNode.ACenter)
    def _clear_menu(self):
        for n in ('panel','title','sub','info','startbtn','foot'):
            o=getattr(self,n,None)
            if o:
                try:o.destroy()
                except Exception:pass
                setattr(self,n,None)
    def start(self):
        if self.state in ('menu','gameover'):
            if self.state=='gameover':self._reset()
            self._clear_menu(); self.state='playing'; self.paused=False; self.say('MISSION START — SURVIVE THE NEON DISTRICT',CYAN)
            self._cursor(True)
    def _cursor(self,hidden):
        p=WindowProperties();p.setCursorHidden(hidden);self.win.requestProperties(p)
    def _reset(self):
        for group in (self.enemies,self.shots,self.hostile,self.pickups,self.particles):
            for o in group:
                try:o['node'].removeNode()
                except Exception:pass
            group.clear()
        self.hp=self.max_hp=100;self.armor=40;self.ammo=240;self.medkits=3;self.score=0;self.kills=0;self.level=1;self.xp=0;self.next_xp=100;self.credits=0;self.crystals=0;self.weapon=1
        self.player.setPos(0,0,0)
        if self.vehicle: self.vehicle['occupied'] = False
        self.vehicle=None;self.spawn_cd=1;self.boss_cd=40;self.shot_cd=0;self.dash_cd=0;self.invuln=0
    def say(self,t,c=CYAN):self.msg.setText(t);self.msg.setFg(c);self.message_cd=2.2
    def spawn_enemy(self,boss=False):
        a=self.rng.random()*math.tau; rad=self.rng.uniform(32,50); p=self.player.getPos()
        x=clamp(p.x+math.cos(a)*rad,-WORLD+5,WORLD-5);y=clamp(p.y+math.sin(a)*rad,-WORLD+5,WORLD-5)
        kinds=[('Street thug',RED,3,6),('Runner',GOLD,2,11),('Heavy',PURPLE,7,4),('Hunter drone',CYAN,4,7)]
        name,c,hp,spd=('DISTRICT BOSS',PINK,42,4.5) if boss else self.rng.choice(kinds)
        root=self.render.attachNewNode('enemy');root.setPos(x,y,0)
        if 'drone' in name.lower():
            self._ball(root,(0,0,1),(.8,.8,.45),c,'drone',True)
            for i in range(4):self._box(root,(math.cos(i*math.pi/2),math.sin(i*math.pi/2),1),(.6,.14,.13),WHITE,'drone-wing',True)
        else:
            self._box(root,(0,0,.9),(.95,.75,1.5),c,'enemy-armor',True);self._ball(root,(0,0,1.9),(.38,.38,.38),WHITE,'enemy-head')
        if boss:self._ball(root,(0,0,2.65),(1.1,1.1,1.1),PINK,'boss-aura',True)
        self.enemies.append({'node':root,'hp':hp+self.level//2,'speed':spd,'kind':name,'boss':boss,'fire':1.2,'reward':160 if boss else 25})
    def shoot(self):
        if self.state!='playing' or self.paused or self.shot_cd>0 or self.ammo<=0:return
        self.ammo-=1;self.shot_cd=.16 if self.weapon<4 else .1
        p=self.player.getPos(); m=self.mouseWatcherNode.getMouse(); near=Vec3();far=Vec3();self.camLens.extrude(m,near,far)
        near=self.render.getRelativePoint(self.camera,near);far=self.render.getRelativePoint(self.camera,far);v=far-near
        if abs(v.z)<.001:dx,dy=1,0
        else:
            t=(p.z+1.3-near.z)/v.z; target=near+v*t; dx,dy=target.x-p.x,target.y-p.y;d=max(.01,math.hypot(dx,dy));dx/=d;dy/=d
        count=1 if self.weapon<2 else (3 if self.weapon<4 else 5)
        for i in range(count):
            ang=(i-(count-1)/2)*.055;vx=(dx*math.cos(ang)-dy*math.sin(ang))*62;vy=(dx*math.sin(ang)+dy*math.cos(ang))*62
            n=self._ball(self.render,(p.x,p.y,1.7),(.11,.11,.11),CYAN,'plasma',True);self.shots.append({'node':n,'vx':vx,'vy':vy,'life':1.5,'damage':2 if self.weapon>=3 else 1})
    def enemy_shot(self,e):
        p=self.player.getPos();q=e['node'].getPos();dx,dy=p.x-q.x,p.y-q.y;d=max(.01,math.hypot(dx,dy));n=self._ball(self.render,(q.x,q.y,1.5),(.15,.15,.15),PINK,'hostile-plasma',True)
        self.hostile.append({'node':n,'vx':dx/d*22,'vy':dy/d*22,'life':3,'damage':13 if e['boss'] else 7})
    def burst(self,pos,c,n=8):
        for _ in range(n):
            o=self._ball(self.render,pos,(.08,.08,.08),c,'particle',True);a=self.rng.random()*math.tau;v=self.rng.uniform(3,9)
            self.particles.append({'node':o,'vx':math.cos(a)*v,'vy':math.sin(a)*v,'vz':self.rng.uniform(1,6),'life':.55})
    def _pickup(self, x, y):
        """Spawn a collectible drop after an enemy is defeated."""
        kind = self.rng.choices(
            ['credits', 'medkit', 'ammo', 'crystal'],
            weights=[42, 18, 30, 10], k=1
        )[0]
        colors = {'credits': GOLD, 'medkit': GREEN, 'ammo': CYAN, 'crystal': PURPLE}
        node = self._ball(self.render, (x, y, .8), (.42, .42, .42), colors[kind],
                          f'pickup-{kind}', True)
        if kind == 'medkit':
            self._box(node, (0, 0, 0), (.12, .12, 1.5), WHITE, 'medkit-cross', True)
        self.pickups.append({'node': node, 'kind': kind, 'phase': self.rng.random() * math.tau})

    def hurt(self,damage):
        if self.invuln>0:return
        absorbed=min(self.armor,damage*.5);self.armor-=absorbed;self.hp-=damage-absorbed;self.invuln=.5;self.burst(self.player.getPos()+Vec3(0,0,1),RED,10)
        if self.hp<=0:
            self.hp=0;self.state='gameover';self.best=max(self.best,self.score);self._save();self._gameover()
    def _gameover(self):
        self.panel=DirectFrame(frameColor=(.02,.01,.07,.95),frameSize=(-.75,.75,-.5,.5),pos=(0,0,.05))
        self.title=OnscreenText(text='MISSION FAILED',pos=(0,.22),scale=.09,fg=PINK,align=TextNode.ACenter)
        self.info=OnscreenText(text=f'SCORE {self.score}  •  LEVEL {self.level}  •  KILLS {self.kills}\nHIGH SCORE {self.best}\n\nPRESS ENTER OR R TO REDEPLOY',pos=(0,-.02),scale=.043,fg=WHITE,align=TextNode.ACenter)
        self.startbtn=DirectButton(text='REDEPLOY',scale=.065,pos=(0,0,-.3),command=self.start,frameColor=(.5,.03,.18,.95),text_fg=(1,1,1,1))
    def vehicle_toggle(self):
        if self.state!='playing':return
        if self.vehicle:self.vehicle['occupied']=False;self.vehicle=None;self.say('HOVER CAR EXITED',GOLD);return
        p=self.player.getPos();near=[c for c in self.cars if not c['occupied'] and math.hypot(c['x']-p.x,c['y']-p.y)<7]
        if near:self.vehicle=min(near,key=lambda c:math.hypot(c['x']-p.x,c['y']-p.y));self.vehicle['occupied']=True;self.say('HOVER CAR BOOST ENGAGED',GOLD)
        else:self.say('MOVE CLOSER TO A HOVER CAR',GOLD)
    def medkit(self):
        if self.state=='playing' and self.medkits and self.hp<self.max_hp:self.medkits-=1;self.hp=min(self.max_hp,self.hp+40);self.say('MEDKIT +40 HP',GREEN)
        else:self.say('NO MEDKIT NEEDED / AVAILABLE',RED)
    def dash(self):
        if self.state=='playing' and self.dash_cd<=0:self.dash_cd=2;self.invuln=.3;self.say('NEON DASH ACTIVATED',CYAN)
    def stats_toggle(self):
        if self.stats.isHidden():self.stats.show()
        else:self.stats.hide()
    def pause(self):
        if self.state=='playing':self.paused=not self.paused;self.say('PAUSED' if self.paused else 'MISSION RESUMED',GOLD)
    def camera_update(self,task):
        p=self.player.getPos(self.render);target=Vec3(p.x,p.y-25,p.z+23);self.camera.setPos(self.camera.getPos()+(target-self.camera.getPos())*.09);self.camera.lookAt(p+Vec3(0,0,1));return Task.cont
    def update(self,task):
        dt=min(globalClock.getDt(),.04);self.elapsed+=dt;self.shot_cd=max(0,self.shot_cd-dt);self.dash_cd=max(0,self.dash_cd-dt);self.invuln=max(0,self.invuln-dt);self.message_cd=max(0,self.message_cd-dt)
        if self.message_cd<=0:self.msg.setText('')
        if self.state=='playing' and not self.paused:
            p=self.player.getPos();dx=int(self.keys['d'] or self.keys['arrow_right'])-int(self.keys['a'] or self.keys['arrow_left']);dy=int(self.keys['w'] or self.keys['arrow_up'])-int(self.keys['s'] or self.keys['arrow_down']);mag=max(1,math.hypot(dx,dy));dx/=mag;dy/=mag
            speed=14*(2 if self.dash_cd>1.7 else 1)*(1.7 if self.vehicle else 1);p.x=clamp(p.x+dx*speed*dt,-WORLD+4,WORLD-4);p.y=clamp(p.y+dy*speed*dt,-WORLD+4,WORLD-4);self.player.setPos(p)
            if self.vehicle:self.vehicle['x']=p.x;self.vehicle['y']=p.y;self.vehicle['node'].setPos(p.x,p.y,.55)
            if abs(dx)+abs(dy)>.1:self.player.setH(math.degrees(math.atan2(dx,dy)))
            self.spawn_cd-=dt;self.boss_cd-=dt
            if self.spawn_cd<=0:
                if len(self.enemies) < 24: self.spawn_enemy()
                self.spawn_cd=max(.6,1.8-self.level*.04)
            if self.boss_cd<=0:self.spawn_enemy(True);self.boss_cd=max(38,65-self.level);self.say('WARNING — DISTRICT BOSS INCOMING',PINK)
            for e in self.enemies[:]:
                ep=e['node'].getPos();pp=self.player.getPos();vx,vy=pp.x-ep.x,pp.y-ep.y;dist=max(.01,math.hypot(vx,vy))
                if dist>2:e['node'].setX(ep.x+vx/dist*e['speed']*dt);e['node'].setY(ep.y+vy/dist*e['speed']*dt)
                e['node'].setH(e['node'].getH()+55*dt);e['fire']-=dt
                if e['fire']<=0 and dist<42 and (e['boss'] or e['kind'] in ('Heavy','Hunter drone')):self.enemy_shot(e);e['fire']=.85 if e['boss'] else 1.7
                if dist<2:self.hurt(16 if e['boss'] else 7)
            for group,hostile in ((self.shots,False),(self.hostile,True)):
                for b in group[:]:
                    n=b['node'];q=n.getPos();n.setX(q.x+b['vx']*dt);n.setY(q.y+b['vy']*dt);b['life']-=dt;hit=None
                    if not hostile:
                        for e in self.enemies:
                            ep=e['node'].getPos()
                            if math.hypot(ep.x-q.x,ep.y-q.y)<1.7:hit=e;break
                    else:
                        pp=self.player.getPos()
                        if math.hypot(pp.x-q.x,pp.y-q.y)<1.4:self.hurt(b['damage']);b['life']=-1
                    if hit:
                        hit['hp']-=b['damage'];self.burst(q,CYAN,2);b['life']=-1
                        if hit['hp']<=0:
                            ep=hit['node'].getPos();self.burst(ep,PINK if hit['boss'] else PURPLE,18 if hit['boss'] else 7);hit['node'].removeNode();self.enemies.remove(hit);self.score+=hit['reward'];self.kills+=1;self.xp+=35 if hit['boss'] else 18
                            if hit['boss']:self.crystals+=1;self.credits+=100;self.say('BOSS DEFEATED + DATA CRYSTAL',GOLD)
                            elif self.rng.random()<.3:self._pickup(ep.x,ep.y)
                            if self.kills and self.kills%10==0:self.credits+=250;self.say('MISSION COMPLETE +250 CREDITS',GOLD)
                            while self.xp>=self.next_xp:self.xp-=self.next_xp;self.level+=1;self.next_xp=int(self.next_xp*1.35);self.max_hp+=10;self.hp=min(self.max_hp,self.hp+25);self.weapon=min(5,self.weapon+1);self.say(f'LEVEL UP — {self.level}',GREEN)
                    if b['life']<=0:n.removeNode();group.remove(b)
            for it in self.pickups[:]:
                it['phase']+=dt*2.5;n=it['node'];n.setZ(.8+math.sin(it['phase'])*.2);n.setH(n.getH()+75*dt);q=n.getPos();p=self.player.getPos()
                if math.hypot(q.x-p.x,q.y-p.y)<2:
                    k=it['kind']
                    if k=='credits':v=self.rng.randint(20,80);self.credits+=v;self.say(f'+{v} CREDITS',GOLD)
                    elif k=='medkit':self.medkits+=1;self.say('MEDKIT COLLECTED',GREEN)
                    elif k=='ammo':self.ammo+=45;self.say('+45 PLASMA AMMO',CYAN)
                    else:self.crystals+=1;self.credits+=100;self.say('DATA CRYSTAL +100 CREDITS',PURPLE)
                    n.removeNode();self.pickups.remove(it)
            for part in self.particles[:]:
                n=part['node'];q=n.getPos();n.setPos(q.x+part['vx']*dt,q.y+part['vy']*dt,q.z+part['vz']*dt);part['vz']-=11*dt;part['life']-=dt
                if part['life']<=0:n.removeNode();self.particles.remove(part)
        self.hud.setText(f'NEON CITY // VIP 3D\nLV {self.level}  XP {self.xp}/{self.next_xp}\nHP {int(self.hp)}/{self.max_hp}  ARMOR {int(self.armor)}\nAMMO {self.ammo}  MEDKITS {self.medkits}\nKILLS {self.kills}  DATA {self.crystals}')
        self.hudr.setText(f'SCORE {self.score:07d}\nBEST {max(self.best,self.score):07d}\nCREDITS ${self.credits}\nWEAPON TIER {self.weapon}')
        self.stats.setText(f'OPERATIVE STATUS\nLevel: {self.level}  Weapon: Tier {self.weapon}\nCredits: ${self.credits}  Data crystals: {self.crystals}\nAmmo: {self.ammo}  Medkits: {self.medkits}\nKills: {self.kills}\nTAB to hide')
        return Task.cont

if __name__=='__main__': NeonCityVIP().run()
