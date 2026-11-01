"""Render skeleton diagnostics from the generated native KH1 MSET, not a game capture."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image,ImageDraw
from kh1_motion_source import read_model,read_mset,pose
from render_aqua_diagnostics import font,pose as draw_pose

ROLES={'center':0,'koshi':3,'hara':76,'mune':78,'kubi':147,'atama':151,
       'R_kata':89,'R_ude1':93,'R_ude2':94,'R_te':101,
       'L_kata':194,'L_ude1':198,'L_ude2':199,'L_te':206,
       'R_momo':17,'R_sune':18,'R_ashi1':19,'R_ashi2':23,
       'L_momo':43,'L_sune':44,'L_ashi1':45,'L_ashi2':49}
SKELETON={'bones':[{'name':name,'index':index} for name,index in ROLES.items()]}


def render(workspace):
    package=workspace/'KH1FM_Aqua_Motion_Test_v1';out=package/'preview';out.mkdir(exist_ok=True)
    model=read_model((workspace/'sora_source/Custom Movesets KH1/xa_ex_0010.mdls').read_bytes())
    bank=read_mset((package/'assets/xa_ex_0010.mset').read_bytes())
    report=json.loads((package/'validation.json').read_text())
    records=[r for r in report['motions'] if r['action'] not in ['Guard startup','Guard recovery']]
    image=Image.new('RGB',(1420,125+len(records)*180),'#111926');draw=ImageDraw.Draw(image)
    draw.text((24,18),'AQUA / KH1 NATIVE MOTION TEST',font=font(25),fill='#ecf0fa')
    draw.text((24,56),'Offline Sora skeleton playback. Orange: right limbs. Blue: left limbs.',font=font(17),fill='#acb9ce')
    draw.text((24,83),'No character mesh, particles, hitboxes, camera, or game runtime is shown.',font=font(16),fill='#acb9ce')
    for row,record in enumerate(records):
        top=125+row*180;motion=bank['motions'][record['native_slot']]
        draw.line((20,top,1400,top),fill='#354254')
        draw.text((24,top+12),record['action'],font=font(18),fill='#ecf0fa')
        draw.text((24,top+41),f"Donor {record['donor']} / {motion.frames} KH1 frames",font=font(14),fill='#acb9ce')
        for col,t in enumerate(np.linspace(0,motion.frames-1,6)):
            body=pose(model,motion,float(t))[:,:3,3]
            draw_pose(draw,body,SKELETON,(340+col*192,top+144),scale=.78)
            draw.text((290+col*192,top+155),f'{t:.1f}',font=font(12),fill='#acb9ce')
    image.save(out/'motion_sheet.png')
    selected=[('Ground combo','ground first'),('Air combo','air first'),('Guard body','Guard startup'),('Cartwheel','Dodge Roll / Cartwheel')]
    frames=[]
    for progress in np.linspace(0,1,40):
        img=Image.new('RGB',(1120,410),'#111926');d=ImageDraw.Draw(img)
        d.text((22,16),'Native MSET skeleton playback / offline diagnostic',font=font(23),fill='#ecf0fa')
        d.text((22,50),'Clips share one preview length for comparison. Not a game capture.',font=font(16),fill='#acb9ce')
        for col,(title,action) in enumerate(selected):
            record=next(r for r in report['motions'] if r['action']==action)
            motion=bank['motions'][record['native_slot']]
            body=pose(model,motion,float(progress*(motion.frames-1)))[:,:3,3]
            draw_pose(d,body,SKELETON,(140+col*280,330),scale=1.12)
            d.text((28+col*280,94),title,font=font(18),fill='#ecf0fa')
        frames.append(img)
    frames[0].save(out/'motion_diagnostic.gif',save_all=True,append_images=frames[1:],duration=45,loop=0,disposal=2)
    print(out)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',type=Path,default=Path(__file__).resolve().parents[1])
    render(parser.parse_args().workspace.resolve())
