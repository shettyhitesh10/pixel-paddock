"""Collect a pinned historical event into a separate review file. Never changes the released snapshot."""
import argparse,json,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
API='https://api.openf1.org/v1/'
ENDPOINTS=('drivers','laps','pit','stints','team_radio','race_control','session_result','starting_grid')

def get_json(endpoint,key):
 url=API+endpoint+'?'+urlencode({'session_key':key})
 with urlopen(Request(url,headers={'User-Agent':'PixelPaddock/5.0 source-linked local fan POC','Accept':'application/json'}),timeout=15) as r:
  payload=json.loads(r.read(12_000_000))
 if not isinstance(payload,list):raise ValueError('Expected an array from '+endpoint)
 return payload,url

def collect(race_key,qualifying_key,fetch=get_json):
 # Explicit keys avoid silently mixing weekends when `latest` moves.
 out={'schemaVersion':1,'provider':'OpenF1','fetchedAt':datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),'raceSessionKey':race_key,'qualifyingSessionKey':qualifying_key,'records':{},'sources':{},'errors':{},'needsReview':True}
 race,_=fetch('sessions',race_key);quali,_=fetch('sessions',qualifying_key)
 if len(race)!=1 or len(quali)!=1:raise ValueError('Session keys must each resolve to one session')
 if race[0].get('session_name')!='Race' or quali[0].get('session_name')!='Qualifying' or race[0].get('meeting_key')!=quali[0].get('meeting_key'):raise ValueError('Race and qualifying must belong to the same meeting')
 out['sessions']={'race':race[0],'qualifying':quali[0]}
 for endpoint in ENDPOINTS:
  try:
   rows,url=fetch(endpoint,race_key)
   if any(x.get('session_key') not in (None,race_key) for x in rows):raise ValueError('Mismatched session key')
   out['records'][endpoint]=rows;out['sources'][endpoint]=url
  except Exception as exc:out['errors'][endpoint]=str(exc)
 try:
  rows,url=fetch('session_result',qualifying_key);out['records']['qualifying_result']=rows;out['sources']['qualifying_result']=url
 except Exception as exc:out['errors']['qualifying_result']=str(exc)
 # Empty radio is a valid coverage state, not a fabricated transcript.
 out['radioCoverage']='Selected published clips' if out['records'].get('team_radio') else 'No clips supplied by provider'
 return out

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--race-session-key',type=int,required=True);p.add_argument('--qualifying-session-key',type=int,required=True);p.add_argument('--output',type=Path,default=ROOT/'research/openf1-candidate.json');a=p.parse_args()
 if a.output.resolve()==(ROOT/'dist/data/content.json').resolve():p.error('Use a separate candidate file')
 last=[0.0]
 def rate_limited(endpoint,key):
  remaining=.4-(time.monotonic()-last[0])
  if remaining>0:time.sleep(remaining)
  last[0]=time.monotonic();return get_json(endpoint,key)
 data=collect(a.race_session_key,a.qualifying_session_key,rate_limited);a.output.parent.mkdir(parents=True,exist_ok=True);tmp=a.output.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(a.output)
 print(json.dumps({'output':str(a.output),'errors':data['errors'],'radioCoverage':data['radioCoverage'],'releasedSnapshotChanged':False}))
if __name__=='__main__':main()
