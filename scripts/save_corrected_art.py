"""Persist a reviewed imagegen correction and retire its preceding image hash."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]/'backend'
payload=json.load(sys.stdin)
pro_path=root/'artwork_provenance.json'
pro=json.loads(pro_path.read_text())
policy_path=root/'art_direction.json'
policy=json.loads(policy_path.read_text())
for item in payload:
 tid=item['token_id'];src=Path(item['source'])
 old=next((root/'generated'/f'{tid}.{ext}' for ext in ('webp','png','jpg','jpeg') if (root/'generated'/f'{tid}.{ext}').exists()),None)
 old_sha=hashlib.sha256(old.read_bytes()).hexdigest() if old else None
 with Image.open(src) as im:im.verify()
 with Image.open(src) as im:
  if min(im.size)<512:raise ValueError('Artwork too small')
  out=root/'generated'/f'{tid}.webp';tmp=out.with_suffix('.tmp.webp');im.save(tmp,'WEBP',quality=94,method=6)
 tmp.replace(out)
 if old and old!=out:old.unlink()
 sha=hashlib.sha256(out.read_bytes()).hexdigest()
 if old_sha and old_sha!=sha and not any(x['sha256']==old_sha for x in policy['blocked_artwork']):policy['blocked_artwork'].append({'token_id':tid,'sha256':old_sha,'reason':item['reason']})
 pro[str(tid)]={'created_at':datetime.now(timezone.utc).isoformat(),'method':'OpenAI built-in image generation/editing','state':'candidate','creator_approved':False,'art_direction_version':policy['version'],'sha256':sha,'retired_sha256':old_sha,'visual_review':item.get('visual_review', 'candidate generated under intact-skin and original-Grim rules; visual approval pending')}
 print(json.dumps({'token_id':tid,'sha256':sha}))
pro_path.write_text(json.dumps(pro,indent=2)+'\n')
policy_path.write_text(json.dumps(policy,indent=2)+'\n')
