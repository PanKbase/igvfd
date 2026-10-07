#!/usr/bin/env python3
"""
Link DE AnalysisSet input_file_sets (and optional donors/samples) from a CSV mapping.

Input CSV columns:
  analysis_set_accession   (required)
  input_file_sets          (required for patch; semicolon- or comma-separated paths/accessions)
  donors                   (optional; same delimiter rules)
  samples                  (optional; same delimiter rules)

Other columns (e.g. current_*, annotation_type, summary) are ignored.

Never overwrites non-empty existing values without --overwrite.
Default is dry-run; --apply requires IGVF_API_KEY + IGVF_SECRET_KEY.

Usage:
  # Dry run (default)
  python scripts/backfill/link_de_inputs.py \\
    --csv scripts/backfill/de_lineage_template.csv

  # Smoke a couple of rows
  python scripts/backfill/link_de_inputs.py --csv path/to.csv --limit 2

  # Apply (non-production / after Gate approval only)
  python scripts/backfill/link_de_inputs.py \\
    --csv path/to.csv --server http://localhost:8000 --apply
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    import requests
except ImportError:
    print('requests is required', file=sys.stderr)
    sys.exit(1)

HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}

# Bare accessions or absolute @id paths.
ACCESSION_RE = re.compile(r'^(PKB|IGVF|TST)[A-Z]{2}[A-Z0-9]+$')
PATH_RE = re.compile(r'^/[a-z0-9-]+/.+/$')
SPLIT_RE = re.compile(r'[;,]+')

PATCHABLE = ('input_file_sets', 'donors', 'samples')


def get_auth() -> Optional[Tuple[str, str]]:
    api_key = os.getenv('IGVF_API_KEY')
    secret_key = os.getenv('IGVF_SECRET_KEY')
    if api_key and secret_key:
        return api_key, secret_key
    return None


def split_refs(raw: Optional[str]) -> List[str]:
    """Split semicolon/comma-separated paths or accessions; drop empties."""
    if raw is None:
        return []
    s = str(raw).strip()
    if not s:
        return []
    parts = [p.strip() for p in SPLIT_RE.split(s)]
    return [p for p in parts if p]


def normalize_ref_token(token: str) -> str:
    """Return a lookup key: absolute path if given, else bare accession."""
    t = token.strip()
    if PATH_RE.match(t):
        return t
    # Allow path without trailing slash
    if t.startswith('/') and not t.endswith('/'):
        return t + '/'
    # Strip accidental @id wrappers
    if t.startswith('/') and PATH_RE.match(t if t.endswith('/') else t + '/'):
        return t if t.endswith('/') else t + '/'
    m = ACCESSION_RE.match(t)
    if m:
        return t
    # Embedded "accession=..." or full URL — take last path segment if it looks like accession
    if '/' in t:
        seg = t.rstrip('/').split('/')[-1]
        if ACCESSION_RE.match(seg):
            return seg
    raise ValueError(f'unrecognized ref (want path or accession): {token!r}')


def resolve_ref(server: str, token: str, auth: Optional[Tuple[str, str]], cache: Dict[str, str]) -> str:
    """
    Resolve path or accession to canonical @id via GET.
    Caches successful resolutions.
    """
    key = normalize_ref_token(token)
    if key in cache:
        return cache[key]

    if key.startswith('/'):
        url = f'{server.rstrip("/")}{key}'
    else:
        url = f'{server.rstrip("/")}/{key}/'

    resp = requests.get(url, auth=auth, headers=HEADERS, timeout=60, allow_redirects=True)
    if resp.status_code == 404:
        raise LookupError(f'not found: {token}')
    if resp.status_code != 200:
        raise RuntimeError(f'GET {token} failed: {resp.status_code} {resp.text[:300]}')
    data = resp.json()
    obj_id = data.get('@id')
    if not obj_id:
        raise RuntimeError(f'GET {token}: response missing @id')
    cache[key] = obj_id
    # Also cache by accession if present
    acc = data.get('accession')
    if acc:
        cache[acc] = obj_id
    return obj_id


def extract_ids(value: Any) -> List[str]:
    """Normalize API array (paths or embedded objects) to sorted unique @id list."""
    if value is None or value == '':
        return []
    if not isinstance(value, list):
        value = [value]
    out: List[str] = []
    for item in value:
        if item is None or item == '':
            continue
        if isinstance(item, str):
            out.append(item if item.endswith('/') else item + '/')
        elif isinstance(item, dict):
            oid = item.get('@id') or item.get('accession')
            if not oid:
                continue
            if isinstance(oid, str) and not oid.startswith('/'):
                # bare accession — leave for caller to resolve if needed; keep as-is for compare display
                out.append(oid)
            else:
                out.append(oid if oid.endswith('/') else oid + '/')
        else:
            out.append(str(item))
    # unique preserve order then sort for stable compare
    seen = set()
    uniq: List[str] = []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return sorted(uniq)


def ids_equal(a: Sequence[str], b: Sequence[str]) -> bool:
    return sorted(a) == sorted(b)


def load_csv(path: str) -> List[Dict[str, Any]]:
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit(f'{path}: empty or missing header')
        fields_lower = {h.lower(): h for h in reader.fieldnames if h}
        acc_col = fields_lower.get('analysis_set_accession') or fields_lower.get('accession')
        if not acc_col:
            raise SystemExit(
                f'{path}: need analysis_set_accession (or accession) column; found {reader.fieldnames}'
            )
        rows: List[Dict[str, Any]] = []
        for i, raw in enumerate(reader, start=2):
            if all(not (v or '').strip() for v in raw.values()):
                continue
            accession = (raw.get(acc_col) or '').strip()
            if not accession:
                raise SystemExit(f'{path}:{i}: missing analysis_set_accession')
            row: Dict[str, Any] = {
                'accession': accession,
                'id': f'/analysis-sets/{accession}/',
                'line': i,
            }
            for prop in PATCHABLE:
                # Prefer fill columns over current_* 
                col = fields_lower.get(prop)
                if col and (raw.get(col) or '').strip():
                    row[prop] = raw.get(col)
                else:
                    row[prop] = None
            rows.append(row)
        return rows


def get_object(server: str, obj_id: str, auth: Optional[Tuple[str, str]]) -> Optional[Dict[str, Any]]:
    url = f'{server.rstrip("/")}{obj_id}'
    resp = requests.get(url, auth=auth, headers=HEADERS, timeout=60)
    if resp.status_code == 404:
        return None
    if resp.status_code != 200:
        raise RuntimeError(f'GET {obj_id} failed: {resp.status_code} {resp.text[:300]}')
    return resp.json()


def patch_object(
    server: str,
    obj_id: str,
    payload: Dict[str, Any],
    auth: Optional[Tuple[str, str]],
) -> Tuple[bool, str]:
    if auth is None:
        return False, 'auth required for PATCH (set IGVF_API_KEY and IGVF_SECRET_KEY)'
    url = f'{server.rstrip("/")}{obj_id}'
    resp = requests.patch(url, auth=auth, headers=HEADERS, json=payload, timeout=60)
    if resp.status_code in (200, 201, 204):
        return True, ''
    return False, f'{resp.status_code}: {resp.text[:400]}'


def plan_patch(
    existing: Dict[str, Any],
    desired: Dict[str, List[str]],
    overwrite: bool,
) -> Tuple[str, Dict[str, List[str]], str]:
    """
    Return (action, payload, message).
    action: patch | skip | conflict
    desired values are already resolved @id lists.
    """
    ann = existing.get('annotation_type')
    if ann != 'differential_expression':
        return 'skip', {}, f'annotation_type is {ann!r}, expected differential_expression'

    payload: Dict[str, List[str]] = {}
    conflicts: List[str] = []
    unchanged: List[str] = []

    for key, new_ids in desired.items():
        if not new_ids:
            continue
        old_ids = extract_ids(existing.get(key))
        # Normalize old bare accessions for compare only when they look like paths already
        if not old_ids:
            payload[key] = new_ids
        elif ids_equal(old_ids, new_ids):
            unchanged.append(key)
        elif overwrite:
            payload[key] = new_ids
        else:
            conflicts.append(
                f'{key}: existing={old_ids!r} desired={new_ids!r}'
            )

    if conflicts:
        return 'conflict', {}, '; '.join(conflicts)
    if not payload:
        return 'skip', {}, 'all fields already match' if unchanged else 'no fields to patch'
    msg_parts = []
    if payload:
        msg_parts.append('set ' + ','.join(f'{k}={v}' for k, v in sorted(payload.items())))
    if unchanged:
        msg_parts.append('unchanged ' + ','.join(sorted(unchanged)))
    return 'patch', payload, '; '.join(msg_parts)


def build_desired(
    row: Dict[str, Any],
    server: str,
    auth: Optional[Tuple[str, str]],
    cache: Dict[str, str],
) -> Dict[str, List[str]]:
    desired: Dict[str, List[str]] = {}
    for prop in PATCHABLE:
        raw = row.get(prop)
        if raw is None or str(raw).strip() == '':
            continue
        tokens = split_refs(str(raw))
        resolved: List[str] = []
        for tok in tokens:
            resolved.append(resolve_ref(server, tok, auth, cache))
        # unique sorted
        desired[prop] = sorted(set(resolved))
    return desired


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Link DE AnalysisSet input_file_sets / donors / samples from CSV',
    )
    parser.add_argument('--csv', required=True, help='Mapping CSV (see module docstring)')
    parser.add_argument(
        '--server',
        default=os.getenv('IGVF_URL_BASE', 'https://api.data.pankbase.org'),
        help='API base URL (default: IGVF_URL_BASE or https://api.data.pankbase.org)',
    )
    parser.add_argument(
        '--dry-run',
        dest='dry_run',
        action='store_true',
        default=True,
        help='Do not PATCH (default)',
    )
    parser.add_argument(
        '--apply',
        dest='dry_run',
        action='store_false',
        help='Actually PATCH records (requires auth; do not use on production without approval)',
    )
    parser.add_argument(
        '--no-dry-run',
        dest='dry_run',
        action='store_false',
        help=argparse.SUPPRESS,  # alias for --apply (matches sibling backfill script)
    )
    parser.add_argument('--limit', type=int, default=None, help='Max records to process')
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing non-empty values that differ (default: report conflict, skip)',
    )
    parser.add_argument(
        '--log',
        default=None,
        help='CSV log path (default: scripts/backfill/link_de_inputs_log.csv)',
    )
    parser.add_argument('--sleep', type=float, default=0.05, help='Seconds between requests')
    args = parser.parse_args()

    if not args.dry_run:
        auth_check = get_auth()
        if auth_check is None:
            raise SystemExit(
                '--apply requires IGVF_API_KEY and IGVF_SECRET_KEY environment variables'
            )
        # Soft guard: remind operators not to apply against production casually
        if 'api.data.pankbase.org' in args.server.rstrip('/').lower():
            print(
                'WARNING: --apply against production API. Abort unless you have Gate approval.',
                file=sys.stderr,
            )

    rows = load_csv(args.csv)
    # Only rows that have at least one fill column
    actionable = [
        r for r in rows
        if any((r.get(p) or '').strip() for p in PATCHABLE)
    ]
    skipped_empty = len(rows) - len(actionable)
    if args.limit is not None:
        actionable = actionable[: args.limit]

    log_path = Path(
        args.log
        or str(Path(__file__).resolve().parent / 'link_de_inputs_log.csv')
    )
    auth = get_auth()
    cache: Dict[str, str] = {}
    counts: Counter = Counter()

    print(f'Server: {args.server}')
    print(f'Dry run: {args.dry_run}')
    print(f'CSV rows: {len(rows)} ({skipped_empty} with empty fill columns skipped)')
    print(f'Records to process: {len(actionable)}')
    print(f'Overwrite: {args.overwrite}')
    print(f'Log: {log_path}')

    with log_path.open('w', newline='') as logf:
        writer = csv.DictWriter(
            logf,
            fieldnames=['accession', 'action', 'fields', 'message'],
        )
        writer.writeheader()

        for row in actionable:
            accession = row['accession']
            obj_id = row['id']
            payload: Dict[str, List[str]] = {}
            try:
                desired = build_desired(row, args.server, auth, cache)
                if not desired:
                    action, message = 'skip', 'no fields to patch'
                else:
                    existing = get_object(args.server, obj_id, auth)
                    if existing is None:
                        action, message = 'error', 'analysis set not found'
                    else:
                        action, payload, message = plan_patch(
                            existing, desired, args.overwrite,
                        )
                        if action == 'patch' and not args.dry_run:
                            ok, err = patch_object(args.server, obj_id, payload, auth)
                            if not ok:
                                action, message = 'error', err
                            else:
                                message = f'patched; {message}'
                        elif action == 'patch' and args.dry_run:
                            message = f'would patch; {message}'
            except Exception as exc:  # noqa: BLE001
                action, payload, message = 'error', {}, str(exc)[:400]

            counts[action] += 1
            writer.writerow({
                'accession': accession,
                'action': action,
                'fields': ','.join(sorted(payload)) if payload else '',
                'message': message,
            })
            print(f'{accession}\t{action}\t{message}')
            if args.sleep:
                time.sleep(args.sleep)

    print('\n===== SUMMARY =====')
    for k, v in sorted(counts.items()):
        print(f'  {k}: {v}')
    print(f'  total: {sum(counts.values())}')
    if skipped_empty:
        print(f'  csv_empty_fill_skipped: {skipped_empty}')


if __name__ == '__main__':
    main()
