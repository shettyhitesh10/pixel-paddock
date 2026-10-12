"""Normalize verified facts and build source-linked driver weekend dossiers."""
import argparse,json
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
def seconds(value):
 if not value:return None
 try:
  parts=value.split(':');return sum(float(p)*60**i for i,p in enumerate(reversed(parts)))
 except (ValueError,AttributeError):return None

def comparison(a,b,qa,qb,fa,fb,sa,sb):
 stage=next((k for k in ['q3','q2','q1'] if qa.get(k) and qb.get(k)),None)
 delta=round(seconds(qa[stage])-seconds(qb[stage]),3) if stage else None
 comparable=a['laps']==b['laps'] and a['time']!='DNF' and b['time']!='DNF'
 def gap(row):
  if row['position']==1:return 0.0
  try:return float(row['time'].strip('+s'))
  except ValueError:return None
 ga,gb=gap(a),gap(b)
 return dict(driverId=b['driverId'],qualifyingStage=stage.upper() if stage else None,qualifyingDeltaSeconds=delta,raceGapSeconds=round(ga-gb,3) if comparable and ga is not None and gb is not None else None,raceGapNote='Same-lap finish gap' if comparable and ga is not None and gb is not None else 'Finish-time gap unavailable: retirement or different laps',racePositions=[a['position'],b['position']],racePoints=[a['points'],b['points']],weekendPoints=[a['points']+sa.get('points',0),b['points']+sb.get('points',0)],fastestLaps=[fa.get('fastestLap',{}).get('time'),fb.get('fastestLap',{}).get('time')],pitStops=[len(fa['pitStops']),len(fb['pitStops'])])

CRITICAL_TAKES={'max_verstappen': 'The strongest conversion on the grid: qualifying advantage translated into the highest race-and-Sprint return. The teammate comparison is limited by Hadjar’s compromised starting position.', 'leclerc': 'A good race return, but pole remained within reach on the timing sheet. The review should separate one-lap precision from an effective race strategy.', 'hamilton': 'The raw qualifying pace was competitive; the race return was weaker. Strategy execution deserves closer scrutiny than the fastest-lap ranking.', 'antonelli': 'The weekend strengthened the title position. His advantage over Russell is convincing in points, but the different starting situations prevent a clean race-pace verdict.', 'russell': 'Recovery matters here, yet it does not erase the cost of starting deep in the field. The teammate deficit needs to be read alongside the grid penalty.', 'norris': 'A better points outcome than the teammate, with a qualifying edge too. That is a positive comparison without proving the car extracted every available position.', 'piastri': 'The race recovered useful points, but the qualifying comparison gives Norris the one-lap advantage. Tyre disruption complicates any judgment of the race gap.', 'lawson': 'The midfield result converted into valuable points. The large gap to Lindblad is worth studying, rather than assuming it is entirely a pace advantage.', 'arvid_lindblad': 'The qualifying-to-race conversion is the concern. Track position and the opening sequence should be examined before assigning the whole deficit to pace.', 'hulkenberg': 'This was a valuable points conversion. Bortoleto’s early retirement means the finish-order comparison cannot serve as a clean measure of relative speed.', 'bortoleto': 'A short race leaves too little evidence for a race-pace verdict. Reliability should be resolved before turning the points deficit into a driver-performance judgment.', 'gasly': 'Qualifying suggested more potential than the race delivered. The priority is understanding the failure to convert track position into points.', 'colapinto': 'Retirement leaves the main performance question open. The qualifying comparison still offers evidence, but there is no representative full-race outcome.', 'bearman': 'The teammate comparison offers a small positive, while the absence of points remains the larger issue. More lap-level detail is needed to distinguish traffic from pace.', 'ocon': 'The race and qualifying comparisons should be reviewed together. A narrow finishing difference alone is a weak basis for judging the weekend.', 'sainz': 'The race ended without a points reward despite a better outcome than the teammate. Albon’s retirement limits how much the intra-team result tells us.', 'albon': 'The retirement makes the finish comparison incomplete. A full account of the car issues is needed before a driving-performance verdict is fair.', 'alonso': 'The pit-lane start makes the recovery context essential. Completing the race provides more evidence than Stroll’s truncated run, but not a like-for-like pace test.', 'stroll': 'The retirement prevents a useful full-race comparison with Alonso. The story should stay focused on verified constraints rather than inventing a driver-error explanation.', 'perez': 'Finishing ahead of Bottas is a positive intra-team outcome. Both cars scoring zero keeps the wider competitiveness question unresolved.', 'bottas': 'A completed race is useful operationally, but the teammate comparison still points to a weaker weekend return in position. Strategy and starting tyres deserve review.'}

def build(data,facts):
 assert facts['event']['round']==data['lastRace']['round'] and facts['event']['season']==data['meta']['season'],'Event mismatch; keep the previous release'
 results={x['driverId']:x for x in data['results']};quali={x['driverId']:x for x in data['qualifyingResults']};sprint={x['driverId']:x for x in data['sprintResults']}
 assert set(results)==set(facts['drivers']),'Incomplete driver facts'
 dossiers={}
 for d in data['drivers']:
  id=d['id'];f=facts['drivers'][id];r=results[id];q=quali[id];s=sprint[id]
  mate=next(x for x in data['drivers'] if x['teamId']==d['teamId'] and x['id']!=id);mid=mate['id']
  cmp=comparison(r,results[mid],q,quali[mid],f,facts['drivers'][mid],s,sprint[mid])
  total=r['points']+s['points'];finish='not classified' if r['position']=='NC' else 'P'+str(r['position'])
  start='pit lane' if f['startType']=='pit lane' else 'P'+str(f['gridPosition'])
  overview=f"{d['name']} started from {start} and was {finish} in the Grand Prix, completing {r['laps']} of {facts['event']['laps']} laps. The race and Sprint yielded {total} points; {mate['name']} scored {cmp['weekendPoints'][1]} across those sessions."
  delta=cmp['qualifyingDeltaSeconds'];assessment=[]
  if delta is not None:assessment.append(f"The comparable {cmp['qualifyingStage']} lap was {abs(delta):.3f}s {'quicker' if delta<0 else 'slower'} than the teammate. That measures one-lap execution, not race pace.")
  else:assessment.append('A like-for-like qualifying time comparison is unavailable. A missing timed lap should not be treated as a pace deficit.')
  difference=cmp['weekendPoints'][0]-cmp['weekendPoints'][1]
  if r['time']=='DNF' or results[mid]['time']=='DNF':assessment.append('Retirement distorts the points comparison. The finishing order alone cannot establish which driver had better underlying race pace.')
  elif difference>0:assessment.append(f"The {difference}-point advantage over the teammate is a positive weekend outcome. It does not isolate the effects of tyres, traffic, strategy or starting position.")
  elif difference<0:assessment.append(f"The {abs(difference)}-point deficit to the teammate makes conversion the main review topic. Lap-by-lap context is needed before attributing that deficit to a driving mistake.")
  else:assessment.append('The teammates scored equally across the race and Sprint. Finishing position and comparable qualifying times provide more useful separation than points alone.')
  key='Recovery to the points' if f['startType']=='pit lane' and r['points'] else 'Race-day conversion' if r['points'] else 'A weekend to review'
  if r['position']==1:key='Pole converted into victory'
  if r['time']=='DNF':key='Retirement limits the verdict'
  stops=sorted(f['pitStops'],key=lambda x:x['lap']);assert all(0<x['lap']<=facts['event']['laps'] for x in stops)
  boundaries=[0]+[x['lap'] for x in stops]+[r['laps']]
  stints=[dict(startLap=boundaries[i]+1,endLap=boundaries[i+1],compound=f['compounds'][i],sourceUrl=facts['sources']['teamReport']) for i in range(len(boundaries)-1) if boundaries[i+1]>boundaries[i]]
  dossiers[id]=dict(eventId=facts['eventId'],event=facts['event'],fetchedAt=facts['fetchedAt'],status='captured',qualifying=q,race=r,sprint=s,grid=dict(position=f['gridPosition'],type=f['startType'],sourceUrl=facts['sources']['grid']),fastestLap=f['fastestLap'],strategy=dict(pitStops=stops,stints=stints,pitLaneTotalSeconds=round(sum(x['pitLaneSeconds'] for x in stops),3),reportedNote=f['reportedNote'],compoundCoverage='Partial: unknown compounds are left blank',lapConvention='Stint boundaries follow the official pit-entry lap records; they are derived, not telemetry.'),radio=dict(items=f['radio'],coverage=f['radioCoverage'],complete=False),teammate=cmp,story=dict(label='AI race story',method='AI-authored assessment of verified classification and reported context; computed timing/points comparisons.',headline=key,overview=overview,criticalTake=CRITICAL_TAKES.get(id,''),assessment=assessment,reportedContext=f['reportedNote'],limitations='No full lap-by-lap telemetry or complete radio archive in this capture. Assessments are subjective; incidents do not automatically imply driver fault.',generatedAt=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),sourceUrls=list(facts['sources'].values())))
 for d in data.get('formerDrivers',[]):dossiers[d['id']]=dict(eventId=facts['eventId'],event=facts['event'],status='not entered',fetchedAt=facts['fetchedAt'])
 data['driverWeekends']=dossiers;data['meta']['schemaVersion']=2
 data['meta']['updatedAt']=max(data['meta']['updatedAt'],facts['fetchedAt'])
 data['meta']['sectionFreshness']['driverWeekends']=dict(fetchedAt=facts['fetchedAt'],sourcePublishedAt=None,session=facts['event']['name']+' · driver dossiers',sourceUrls=list(facts['sources'].values()),note='Official timing, starting grid and pit-lane records; brief reported context and radio excerpts. Teammate comparisons and AI assessment are derived and labelled.')
 return data

def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path,default=R/'dist/data/content.json');p.add_argument('--facts',type=Path,default=R/'data/sources/2026-singapore.json');p.add_argument('--output',type=Path);args=p.parse_args()
 data=build(json.loads(args.snapshot.read_text()),json.loads(args.facts.read_text()));out=args.output or args.snapshot
 temp=out.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');temp.replace(out)
 print(json.dumps({'driverDossiers':len(data['driverWeekends']),'output':str(out)}))
if __name__=='__main__':main()
