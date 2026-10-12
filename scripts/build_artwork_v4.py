"""Package original sprite sheets without cropping or changing their composition."""
from pathlib import Path
from PIL import Image
import json
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'dist/assets/art';ART.mkdir(parents=True,exist_ok=True)
SHEETS=[
('drivers-a','exec-f62e92d4-800c-4f93-a5df-8eb97fe538b1.png',['hamilton','norris','max_verstappen']),
('drivers-b','exec-e7ac02e6-c3a2-4769-8d20-f152723ff858.png',['russell','leclerc','alonso']),
('drivers-c','exec-107b66ff-924e-4ffa-995d-8077caf0981b.png',['antonelli','piastri','sainz']),
('drivers-d','exec-f48222e5-8351-4c2d-b95d-0c93212cf081.png',['albon','gasly','ocon']),
('drivers-e','exec-bf2d0674-cad5-481a-bc1e-4fc72f3ff861.png',['bottas','perez','hulkenberg']),
('drivers-f','exec-4af1877a-7dcd-4efd-a3d8-effe1e4bbe26.png',['hadjar','lawson','arvid_lindblad']),
('drivers-g','exec-c6a16340-d92d-427e-973f-d51b53b58ec1.png',['colapinto','bearman','bortoleto']),
('drivers-h','exec-8e675850-cc3c-412c-a34d-4e7661fee0c7.png',['stroll','tsunoda']),
('leaders-a','exec-90089c9c-b3a8-476b-8553-5e0d9754d367.png',['toto-wolff','fred-vasseur','andrea-stella']),
('leaders-b','exec-9beb4b3c-c651-4d67-a790-c69d8ad5aa7f.png',['laurent-mekies','alan-permane','flavio-briatore']),
('leaders-c','exec-63773bfa-012f-4f93-8045-26cfcdff01d0.png',['ayao-komatsu','mattia-binotto','james-vowles']),
('leaders-d','exec-4d7023ff-f373-4d60-b9c3-efff21aae67b.png',['adrian-newey','marcin-budkowski','steve-nielsen']),
]
extra=ROOT/'assets-work/release4-final-sheet.json'
if extra.exists():
 x=json.loads(extra.read_text());SHEETS.append(('leaders-e',Path(x['path']).name,['allan-mcnish']))
manifest={'scene':'assets/art/singapore-dusk.webp','people':{},'format':'6 columns × 3 rows / 6 animation frames per person','attribution':'Original AI-assisted pixel illustrations created for this fan project.'}
provenance=[]
for name,file,people in SHEETS:
 source=Path('/workspace/generated_images')/file;im=Image.open(source)
 assert im.width/im.height==1.5,(name,im.size)
 out=ART/(name+'.webp')
 im.save(out,'WEBP',quality=95,method=6)
 for row,id in enumerate(people):manifest['people'][id]={'src':'assets/art/'+out.name,'row':row,'frames':6,'width':im.width,'height':im.height}
 provenance.append({'asset':name,'source':str(source),'output':str(out.relative_to(ROOT)),'people':people,'columns':6,'rows':3,'frames':6,'encoding':'WebP quality 95; original dimensions and composition retained'})
source=Path('/workspace/generated_images/exec-fd578ca0-f987-4cea-b4ab-258ce2c3efb9.png');out=ART/'singapore-dusk.webp'
Image.open(source).save(out,'WEBP',quality=95,method=6)
(ROOT/'dist/artwork.js').write_text('window.PADDOCK_ART='+json.dumps(manifest,separators=(',',':'))+';\nif(window.PADDOCK_ASSET_URLS){window.PADDOCK_ART.scene=window.PADDOCK_ASSET_URLS[window.PADDOCK_ART.scene]||window.PADDOCK_ART.scene;Object.values(window.PADDOCK_ART.people).forEach(p=>{p.src=window.PADDOCK_ASSET_URLS[p.src]||p.src;});}\n')
(ROOT/'research/artwork-v4-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print(json.dumps({'people':len(manifest['people']),'assets':len(SHEETS)+1,'imageBytes':sum(p.stat().st_size for p in ART.glob('*.webp'))}))
