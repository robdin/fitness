"""Generate the editable Blender scenes and transparent animation loops.
blender -b --python tools/blender/build_scene.py -- --out .local/blender-mvp
All geometry, materials, lights and keyframes are authored procedurally.
"""
import argparse, math, sys
from pathlib import Path
import bpy
from mathutils import Vector
p=argparse.ArgumentParser()
p.add_argument('--out',default='.local/blender-mvp')
p.add_argument('--frames',type=int,default=48)
p.add_argument('--size',type=int,default=720)
p.add_argument('--samples',type=int,default=16)
p.add_argument('--stills',action='store_true')
p.add_argument('--scene',choices=['clock','dumbbell','ring','tiles'])
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
def color(h):
    c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(((v+.055)/1.055)**2.4 if v>.04045 else v/12.92 for v in c)
materials={}
for name,h,metal,rough in [('lime','B9F227',.25,.25),('cream','F7F4EA',.05,.3),('navy','10233E',.45,.3),('dark','182331',.1,.4),('coral','FF6B4A',.18,.3),('blue','74B9FF',.3,.3),('steel','ABB6C3',.85,.26)]:
    m=bpy.data.materials.new(name);m.use_nodes=True
    node=m.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value=(*color(h),1)
    node.inputs['Metallic'].default_value=metal;node.inputs['Roughness'].default_value=rough
    materials[name]=m
def finish(ob,name,material,r=.04):
    ob.name=name;ob.data.materials.append(materials[material])
    if r:
        m=ob.modifiers.new('Rounded edges','BEVEL');m.width=r;m.segments=3
        ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    for f in ob.data.polygons:f.use_smooth=True
    return ob
def cube(name,pos,dims,mat,r=.07):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos);ob=bpy.context.object;ob.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(ob,name,mat,r)
def cyl(name,pos,r,depth,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=r,depth=depth,location=pos)
    return finish(bpy.context.object,name,mat)
def torus(name,pos,r,minor,mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=16,major_radius=r,minor_radius=minor,location=pos)
    return finish(bpy.context.object,name,mat,0)
def empty(name):
    ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);return ob
def aim(ob,target=(0,0,0)):
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def setup(name):
    s=bpy.data.scenes.new(name);bpy.context.window.scene=s
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=a.samples;s.cycles.use_denoising=True
    s.cycles.max_bounces=4;s.cycles.diffuse_bounces=2;s.cycles.glossy_bounces=2
    s.render.threads_mode='FIXED';s.render.threads=8
    s.render.resolution_x=s.render.resolution_y=a.size;s.render.resolution_percentage=100
    s.render.fps=24;s.render.film_transparent=True
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.compression=15
    s.world=bpy.data.worlds.new(name+' world');s.world.use_nodes=True
    s.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.27,.36,1)
    s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
    s.view_settings.view_transform='AgX';s.frame_start=1;s.frame_end=a.frames
    cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam)
    cam.location=(4,-7,10);cam.data.type='ORTHO';cam.data.ortho_scale=6.8;aim(cam);s.camera=cam
    for name,pos,power,size,col in [('Softbox',(-3,-4,8),900,5,(1,.92,.8)),('Cool rim',(4,2,5),1100,4,(.6,.76,1)),('Bounce',(-4,2,3),450,4,(.79,1,.61))]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=col
        light=bpy.data.objects.new(name,data);s.collection.objects.link(light);light.location=pos;aim(light)
    return s
def animate(root,amplitude=.12):
    for f in range(1,a.frames+2):
        t=(f-1)/a.frames*2*math.pi
        root.rotation_euler=(.06*math.sin(t),amplitude*math.sin(t),.1*math.sin(t));root.location.z=.07*math.sin(t)
        root.keyframe_insert('rotation_euler',frame=f);root.keyframe_insert('location',frame=f)
scenes=[]
s=setup('clock');root=empty('Stopwatch assembly');parts=[]
parts.extend([cyl('Watch body',(0,0,0),2.05,.52,'steel'),cyl('Lime bezel',(0,0,.29),1.97,.16,'lime'),cyl('Dark dial',(0,0,.39),1.79,.1,'navy'),torus('Inner ring',(0,0,.46),1.70,.018,'lime')])
for i in range(60):
    angle=i*2*math.pi/60
    ob=cube('Minute marker %02d'%i,(1.51*math.sin(angle),1.51*math.cos(angle),.48),(.045 if i%5 else .07,.11 if i%5 else .22,.015),'cream',0)
    ob.rotation_euler.z=-angle;parts.append(ob)
parts.extend([cube('Crown stem',(0,2.1,0),(.3,.55,.3),'steel'),cube('Start button',(0,2.38,.01),(.65,.25,.4),'lime'),cube('Side button',(1.5,1.5,.02),(.48,.32,.35),'coral'),cyl('Center pin',(0,0,.55),.14,.1,'cream')])
hand=cube('Moving hand',(0,.55,.54),(.075,1.2,.045),'coral',.035);pivot=empty('Hand pivot');hand.parent=pivot;pivot.parent=root
for f in range(1,a.frames+2):
    pivot.rotation_euler.z=-(f-1)/a.frames*2*math.pi;pivot.keyframe_insert('rotation_euler',frame=f)
for ob in parts:ob.parent=root
animate(root,.08);scenes.append(s)
s=setup('dumbbell');s.camera.data.ortho_scale=7.2;root=empty('Dumbbell assembly');parts=[]
bar=cyl('Handle',(0,0,0),.19,4,'steel');bar.rotation_euler.y=math.pi/2;parts.append(bar)
for side in [-1,1]:
    for i,(r,mat) in enumerate([(1.05,'navy'),(1.25,'lime'),(1.05,'navy')]):
        ob=cyl('Plate %s %s'%(side,i),(side*(1.3+.29*i),0,0),r,.26,mat);ob.rotation_euler.y=math.pi/2;parts.append(ob)
    ob=cyl('End cap',(side*2.06,0,0),.38,.13,'steel');ob.rotation_euler.y=math.pi/2;parts.append(ob)
for i in range(13):
    ob=torus('Grip %s'%i,(-.6+.1*i,0,0),.198,.014,'dark');ob.rotation_euler.y=math.pi/2;parts.append(ob)
for ob in parts:ob.parent=root
animate(root,.15);scenes.append(s)
def wedge(name,start,end,mat):
    steps=max(12,int((end-start)*30));n=steps+1;verts=[]
    for z in [-.19,.19]:
        for r in [2.25,1.42]:
            for i in range(n):
                angle=start+(end-start)*i/steps;verts.append((r*math.cos(angle),r*math.sin(angle),z))
    faces=[]
    for i in range(steps):faces.extend([(i,i+1,2*n+i+1,2*n+i),(n+i,3*n+i,3*n+i+1,n+i+1),(2*n+i,2*n+i+1,3*n+i+1,3*n+i),(i,n+i,n+i+1,i+1)])
    faces.extend([(0,2*n,3*n,n),(n-1,2*n-1,4*n-1,3*n-1)])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);return finish(ob,name,mat)
s=setup('ring');root=empty('Sixty minute breakdown');angle=math.pi/2
for label,value,mat in [('Lifting',15,'lime'),('Rest',25,'cream'),('Setup',8,'blue'),('Waiting',12,'coral')]:
    width=value/60*2*math.pi;ob=wedge(label+': '+str(value)+' illustrative minutes',angle+.015,angle+width-.015,mat);ob.parent=root;mid=angle+width/2
    for f in range(1,a.frames+2):
        t=(f-1)/a.frames*2*math.pi;e=.12+.055*math.sin(t);ob.location=(e*math.cos(mid),e*math.sin(mid),.025*math.sin(t+mid));ob.keyframe_insert('location',frame=f)
    angle+=width
animate(root,.045);s['example']='Invented minutes: 15 + 25 + 8 + 12 = 60';scenes.append(s)
s=setup('tiles');root=empty('Four audit buckets')
for i,(x,y,mat) in enumerate([(-1.13,1.13,'lime'),(1.13,1.13,'cream'),(-1.13,-1.13,'blue'),(1.13,-1.13,'coral')]):
    tile=cube('Audit tile '+str(i),(x,y,0),(1.95,1.95,.32),mat,.16);tile.parent=root
    for f in range(1,a.frames+2):
        t=(f-1)/a.frames*2*math.pi;tile.location.z=.13*math.sin(t+i*.7);tile.keyframe_insert('location',frame=f)
    short=cube('Tick short',(-.15,-.10,.22),(.15,.42,.055),'navy',.04);short.rotation_euler.z=math.radians(40);short.parent=tile
    long=cube('Tick long',(.13,.04,.22),(.15,.75,.055),'navy',.04);long.rotation_euler.z=math.radians(-40);long.parent=tile
animate(root,.08);scenes.append(s)
bpy.context.window.scene=scenes[0]
bpy.ops.wm.save_as_mainfile(filepath=str(out/'time-audit.blend'),compress=True)
for s in scenes:
    if a.scene and s.name!=a.scene:continue
    bpy.context.window.scene=s;dest=out/s.name;dest.mkdir(exist_ok=True)
    if a.stills:
        s.frame_set(1);s.render.filepath=str(dest/'preview.png');bpy.ops.render.render(write_still=True)
    else:
        s.render.filepath=str(dest/'frame-');bpy.ops.render.render(animation=True)
    print('ASSET_COMPLETE',s.name,flush=True)
