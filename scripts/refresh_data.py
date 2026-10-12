#!/usr/bin/env python3
"""Fetch a review candidate. Never deploy an unreviewed candidate.

Uses the environment's normal urllib proxy configuration. Each failed source keeps
its last successful data; nothing depends on a browser API or embedded credential.
Editorial roster/leadership records remain source reviewed; race data and RSS news
refresh automatically. Public Reddit comments refresh only with --community.
"""
import argparse
import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

BASE = Path(__file__).resolve().parent.parent


def fetch(url, timeout):
    req = Request(url, headers={'User-Agent': 'PixelPaddock/1.0 (source-linked fan dashboard)', 'Accept': 'application/json, application/xml, text/xml;q=0.9'})
    with urlopen(req, timeout=timeout) as response:
        return response.read(4_000_000)


def atomic_write(path, obj):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--season', type=int, default=2026)
    parser.add_argument('--timeout', type=int, default=15)
    parser.add_argument('--community', action='store_true', help='Also refresh comments from the saved public Reddit threads')
    parser.add_argument('--snapshot', type=Path, default=BASE / 'dist/data/content.json')
    parser.add_argument('--output', type=Path, default=BASE / 'research/refresh-candidate.json', help='Review candidate only; integrate into the game screens after checking session context')
    args = parser.parse_args()
    if args.output.resolve() == args.snapshot.resolve():
        parser.error('Write a separate candidate; the reviewed release must not be overwritten by a partial refresh.')
    if not 1950 <= args.season <= datetime.now(timezone.utc).year + 1:
        parser.error('Season must be between 1950 and next year')
    data = json.loads(args.snapshot.read_text())
    if args.season != int(data['meta']['season']):
        parser.error('The reviewed roster belongs to a different season. Review roster and leadership before changing season.')
    original = copy.deepcopy(data)
    root = f'https://api.jolpi.ca/ergast/f1/{args.season}'
    endpoints = {
        'drivers': root + '/driverstandings.json?limit=100',
        'teams': root + '/constructorstandings.json?limit=100',
        'calendar': root + '.json?limit=100',
        'results': root + '/last/results.json?limit=100',
        'news': 'https://feeds.bbci.co.uk/sport/formula1/rss.xml',
    }
    if args.community:
        for i, thread in enumerate(data.get('communityThreads', [])[:3]):
            if thread.get('url', '').startswith('https://www.reddit.com/r/formula1/comments/'):
                endpoints[f'community-{i}'] = thread['url'].rstrip('/') + '.json?limit=30&raw_json=1'
    now = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    known_drivers = {d['id'] for d in data['drivers'] + data.get('formerDrivers', [])}
    known_teams = {t['id'] for t in data['teams']}
    issues, successes, raw_cache = {}, [], {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs = {key: pool.submit(fetch, url, args.timeout) for key, url in endpoints.items()}
        for key, job in jobs.items():
            try:
                raw = job.result()
                if key == 'news':
                    feed = ET.fromstring(raw)
                    added = []
                    for item in feed.findall('./channel/item')[:20]:
                        title, url = item.findtext('title', ''), item.findtext('link', '')
                        if not title or not url.startswith('https://'): continue
                        published = parsedate_to_datetime(item.findtext('pubDate')).astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
                        description = html.unescape(re.sub('<[^>]+>', '', item.findtext('description', '')))
                        text = (title + ' ' + description).lower()
                        tags = [e['id'] for group in ('drivers', 'teams', 'principals') for e in data[group] if e['name'].lower() in text]
                        added.append(dict(id=url, title=title, summary=description[:600], url=url, source='BBC Sport', publishedAt=published, tags=tags))
                    if not added: raise ValueError('RSS contains no valid dated articles')
                    merged = {n['url']: n for n in data['news']}
                    merged.update({n['url']: n for n in added})
                    data['news'] = sorted(merged.values(), key=lambda n: n.get('publishedAt', ''), reverse=True)[:40]
                    raw_cache[key] = {'url': endpoints[key], 'fetchedAt': now, 'items': added}
                elif key.startswith('community-'):
                    payload = json.loads(raw)
                    comments = []
                    thread = data['communityThreads'][int(key.split('-')[1])]
                    def visit(children):
                        for child in children:
                            if child.get('kind') != 't1': continue
                            c = child['data']
                            if c.get('body') not in (None, '[removed]', '[deleted]') and c.get('author') not in (None, '[deleted]', 'AutoModerator'):
                                comments.append(dict(id=c['id'], author=c['author'], text=c['body'][:1200], source='Reddit · r/formula1', url='https://www.reddit.com' + c['permalink'], publishedAt=datetime.fromtimestamp(c['created_utc'], timezone.utc).isoformat().replace('+00:00', 'Z'), tags=thread.get('tags', [])))
                            if isinstance(c.get('replies'), dict): visit(c['replies']['data']['children'])
                    visit(payload[1]['data']['children'])
                    if not comments: raise ValueError('No public comments returned')
                    merged = {c['id']: c for c in data.get('comments', [])}
                    merged.update({c['id']: c for c in comments[:15]})
                    data['comments'] = list(merged.values())[-50:]
                    raw_cache[key] = {'url': endpoints[key], 'fetchedAt': now, 'comments': comments[:15]}
                else:
                    payload = json.loads(raw)
                    mr = payload['MRData']
                    if key in ('drivers', 'teams'):
                        lists = mr['StandingsTable']['StandingsLists']
                        if not lists: raise ValueError('No standings returned')
                        table = lists[-1]
                        if int(table['season']) != args.season or int(table['round']) < int(original['meta']['standingsRound']):
                            raise ValueError('Rejected older championship table')
                        entries = table['DriverStandings' if key == 'drivers' else 'ConstructorStandings']
                        rows = []
                        for entry in entries:
                            ident = entry['Driver']['driverId'] if key == 'drivers' else entry['Constructor']['constructorId']
                            if ident not in (known_drivers if key == 'drivers' else known_teams):
                                raise ValueError('Unreviewed roster ID: ' + ident)
                            rows.append({('driverId' if key == 'drivers' else 'teamId'): ident, 'position': int(entry['position']), 'points': float(entry['points']), 'wins': int(entry['wins'])})
                        if not rows: raise ValueError('No standings match reviewed roster')
                        data['standings'][key] = rows
                        data['meta']['standingsRound'] = int(table['round'])
                        data['meta']['standingsSeason'] = int(table['season'])
                    else:
                        races = mr['RaceTable']['Races']
                        if not races: raise ValueError('No races returned')
                        if key == 'calendar':
                            data['calendar'] = [dict(round=int(r['round']), name=r['raceName'], date=r['date'], time=r.get('time'), circuit=r['Circuit']['circuitName'], location=r['Circuit']['Location']['locality'], country=r['Circuit']['Location']['country'], url=r['url']) for r in races]
                        else:
                            race = races[-1]
                            if not race.get('Results'): raise ValueError('Race has no classification')
                            data['lastRace'] = dict(name=race['raceName'], date=race['date'], round=int(race['round']), url=race['url'])
                            data['results'] = [dict(driverId=r['Driver']['driverId'], position=r.get('positionText', r['position']), points=float(r['points']), time=r.get('Time', {}).get('time', r.get('status', '')), status=r.get('status')) for r in race['Results']]
                    raw_cache[key] = {'url': endpoints[key], 'fetchedAt': now, 'response': payload}
                successes.append(key)
            except Exception as exc:
                issues[key] = f'{type(exc).__name__}: {exc}'
                print(f'{key}: retained prior snapshot ({exc})', file=sys.stderr)
    if not successes:
        print('No source refreshed; snapshot and its timestamp remain unchanged.', file=sys.stderr)
        return 1
    data['meta']['updatedAt'] = now
    data['meta']['sourceFetchedAt'] = {**data['meta'].get('sourceFetchedAt', {}), **{key: now for key in successes}}
    data['meta']['refreshIssues'] = issues
    data['meta']['status'] = f"2026 verified source snapshot. Refreshed {', '.join(successes)}; " + (f'{len(issues)} unavailable sources retain their previous data.' if issues else 'all requested sources returned successfully.')
    cache_path = BASE / 'scripts/refresh_cache.json'
    previous_cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    atomic_write(cache_path, {**previous_cache, **raw_cache})
    data['meta']['candidateNeedsReview'] = True
    data['meta']['candidateWarning'] = 'Partial API candidate. Review section freshness, session context, calendar fields, biographies and game labels before integrating.'
    atomic_write(args.output, data)
    print(f'Refreshed {len(successes)} sources; preserved {len(issues)} unavailable sources.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
