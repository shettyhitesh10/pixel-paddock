"""Offline tests for meaningful timing semantics, missing coverage and ingestion failures."""
import copy,json,unittest
from pathlib import Path
from build_driver_weekends import build,comparison
from collect_openf1 import collect
R=Path(__file__).resolve().parents[1]
class WeekendTests(unittest.TestCase):
 def setUp(self):
  self.data=json.loads((R/'dist/data/content.json').read_text());self.facts=json.loads((R/'data/sources/2026-singapore.json').read_text())
 def test_comparable_qualifying_stage_and_race_gap(self):
  d=build(self.data,self.facts)['driverWeekends'];c=d['lawson']['teammate']
  self.assertEqual(c['qualifyingStage'],'Q3');self.assertAlmostEqual(c['qualifyingDeltaSeconds'],-.412)
  # Hadjar has no timed qualifying lap. Treating it as zero would manufacture a deficit.
  self.assertIsNone(d['max_verstappen']['teammate']['qualifyingDeltaSeconds'])
  self.assertAlmostEqual(d['hamilton']['teammate']['raceGapSeconds'],45.853)
 def test_retirement_is_not_a_same_lap_finish(self):
  d=build(self.data,self.facts)['driverWeekends'];self.assertEqual(d['albon']['race']['position'],18)
  self.assertEqual(d['albon']['race']['time'],'DNF');self.assertIsNone(d['albon']['teammate']['raceGapSeconds'])
  self.assertIsNone(d['alonso']['teammate']['raceGapSeconds']);self.assertEqual(d['tsunoda']['status'],'not entered')
 def test_unknown_tyres_and_radio_are_preserved(self):
  d=build(self.data,self.facts)['driverWeekends'];self.assertEqual(d['gasly']['strategy']['stints'][0]['compound'],'UNKNOWN')
  self.assertEqual(d['gasly']['radio']['items'],[]);self.assertFalse(d['hamilton']['radio']['complete'])
  self.assertEqual(d['hamilton']['strategy']['pitLaneTotalSeconds'],24.048)
 def test_mismatched_event_does_not_mutate_snapshot(self):
  original=copy.deepcopy(self.data);self.facts['event']['round']=18
  with self.assertRaises(AssertionError):build(self.data,self.facts)
  self.assertEqual(self.data,original)
 def test_provider_partial_failure_and_empty_radio(self):
  def fetch(endpoint,key):
   if endpoint=='sessions':return [dict(session_key=key,meeting_key=100,session_name='Race' if key==1 else 'Qualifying')],'https://api.openf1.org/v1/sessions'
   if endpoint=='pit':raise OSError('Source unavailable')
   return [],'https://api.openf1.org/v1/'+endpoint
  d=collect(1,2,fetch);self.assertIn('pit',d['errors']);self.assertEqual(d['records']['team_radio'],[])
  self.assertEqual(d['radioCoverage'],'No clips supplied by provider');self.assertTrue(d['needsReview'])
 def test_provider_rejects_two_different_meetings(self):
  def fetch(endpoint,key):return [dict(meeting_key=key,session_name='Race' if key==1 else 'Qualifying')],'url'
  with self.assertRaises(ValueError):collect(1,2,fetch)
if __name__=='__main__':unittest.main()
