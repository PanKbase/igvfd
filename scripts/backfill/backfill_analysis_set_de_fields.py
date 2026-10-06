#!/usr/bin/env python3
"""
Backfill DE fields onto Analysis Sets from an annotated Excel report.

Column → property mapping:
  de_cell_type       → cell_type
  de_comparison_class → de_comparison_class
  de_contrast        → de_contrast
  de_trait           → de_trait
  de_trait_decoded   → de_trait_description
  de_method          → de_method

de_note is curator guidance and is never submitted.

Usage:
  # Dry run (default)
  python scripts/backfill/backfill_analysis_set_de_fields.py \\
    --xlsx scripts/backfill/pankbase_analysis_set_report_2026_10_2_21h_30m_DE_only.xlsx

  # Against local inserts / a specific server
  python scripts/backfill/backfill_analysis_set_de_fields.py \\
    --xlsx path/to/file.xlsx --server http://localhost:8000 --status all --limit 10

  # Apply patches (after Gate 2 approval)
  python scripts/backfill/backfill_analysis_set_de_fields.py \\
    --xlsx path/to/file.xlsx --server https://api.data.pankbase.org --no-dry-run
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
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    print('requests is required', file=sys.stderr)
    sys.exit(1)

try:
    from openpyxl import load_workbook
except ImportError:
    print('openpyxl is required (pip install openpyxl)', file=sys.stderr)
    sys.exit(1)

COLUMN_MAP = {
    'de_cell_type': 'cell_type',
    'de_comparison_class': 'de_comparison_class',
    'de_contrast': 'de_contrast',
    'de_trait': 'de_trait',
    'de_trait_decoded': 'de_trait_description',
    'de_method': 'de_method',
}

ACCESSION_RE = re.compile(r'(PKBDS[A-Z0-9]+|IGVFDS[A-Z0-9]+|TSTDS[A-Z0-9]+)')

HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}


def load_xlsx(path: str) -> List[Dict[str, Any]]:
    """Load sheet 1 with header on row 3; return list of mapped property dicts plus metadata."""
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 3:
        raise SystemExit(f'{path}: expected header on row 3')
    headers = [str(h).strip() if h is not None else f'col{i}' for i, h in enumerate(rows[2])]
    missing = [c for c in COLUMN_MAP if c not in headers]
    if missing:
        raise SystemExit(f'{path}: missing columns {missing}; found {headers}')
    if 'Accession' not in headers and 'ID' not in headers:
        raise SystemExit(f'{path}: need Accession or ID column; found {headers}')

    out: List[Dict[str, Any]] = []
    for r in rows[3:]:
        if all(c is None or str(c).strip() == '' for c in r):
            continue
        raw = {}
        for i in range(min(len(headers), len(r))):
            v = r[i]
            if v is None:
                raw[headers[i]] = None
            else:
                s = str(v).strip()
                raw[headers[i]] = s if s else None

        accession = raw.get('Accession')
        obj_id = raw.get('ID')
        if not accession and obj_id:
            m = ACCESSION_RE.search(obj_id)
            accession = m.group(1) if m else None
        if not accession:
            raise SystemExit(f'Row without accession: {raw}')
        if not obj_id:
            obj_id = f'/analysis-sets/{accession}/'

        fields: Dict[str, str] = {}
        for src, dst in COLUMN_MAP.items():
            val = raw.get(src)
            if val is not None:
                fields[dst] = val

        out.append({
            'accession': accession,
            'id': obj_id if obj_id.startswith('/') else f'/analysis-sets/{accession}/',
            'status': (raw.get('Status') or '').lower() or None,
            'fields': fields,
        })
    return out


def get_auth() -> Optional[Tuple[str, str]]:
    api_key = os.getenv('IGVF_API_KEY')
    secret_key = os.getenv('IGVF_SECRET_KEY')
    if api_key and secret_key:
        return api_key, secret_key
    # Fall back to local insert access key when targeting localhost.
    return None


def get_object(server: str, obj_id: str, auth: Optional[Tuple[str, str]]) -> Optional[Dict[str, Any]]:
    url = f'{server.rstrip("/")}{obj_id}'
    resp = requests.get(url, auth=auth, headers=HEADERS, timeout=60)
    if resp.status_code == 404:
        return None
    if resp.status_code != 200:
        raise RuntimeError(f'GET {obj_id} failed: {resp.status_code} {resp.text[:300]}')
    return resp.json()


def patch_object(server: str, obj_id: str, payload: Dict[str, Any], auth: Optional[Tuple[str, str]]) -> Tuple[bool, str]:
    if auth is None:
        return False, 'auth required for PATCH (set IGVF_API_KEY and IGVF_SECRET_KEY)'
    url = f'{server.rstrip("/")}{obj_id}'
    resp = requests.patch(url, auth=auth, headers=HEADERS, json=payload, timeout=60)
    if resp.status_code in (200, 201, 204):
        return True, ''
    return False, f'{resp.status_code}: {resp.text[:400]}'


def plan_patch(
    existing: Dict[str, Any],
    desired: Dict[str, str],
    overwrite: bool,
) -> Tuple[str, Dict[str, str], str]:
    """
    Return (action, payload, message).
    action: patch | skip | conflict
    """
    ann = existing.get('annotation_type')
    if ann != 'differential_expression':
        return 'skip', {}, f'annotation_type is {ann!r}, expected differential_expression'

    payload: Dict[str, str] = {}
    conflicts: List[str] = []
    unchanged: List[str] = []

    for key, new_val in desired.items():
        old_val = existing.get(key)
        if old_val is None or old_val == '':
            payload[key] = new_val
        elif old_val == new_val:
            unchanged.append(key)
        elif overwrite:
            payload[key] = new_val
        else:
            conflicts.append(f'{key}: existing={old_val!r} desired={new_val!r}')

    if conflicts:
        return 'conflict', {}, '; '.join(conflicts)
    if not payload:
        return 'skip', {}, 'all fields already match' if unchanged else 'no fields to patch'
    msg_parts = []
    if payload:
        msg_parts.append('set ' + ','.join(sorted(payload)))
    if unchanged:
        msg_parts.append('unchanged ' + ','.join(sorted(unchanged)))
    return 'patch', payload, '; '.join(msg_parts)


def main() -> None:
    parser = argparse.ArgumentParser(description='Backfill AnalysisSet DE fields from xlsx')
    parser.add_argument('--xlsx', required=True, help='Annotated DE xlsx (header on row 3)')
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
        '--no-dry-run',
        dest='dry_run',
        action='store_false',
        help='Actually PATCH records',
    )
    parser.add_argument(
        '--status',
        choices=['released', 'all'],
        default='released',
        help='Only process rows with this Status in the xlsx (default: released)',
    )
    parser.add_argument('--limit', type=int, default=None, help='Max records to process')
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing values that differ (default: report conflict, skip)',
    )
    parser.add_argument(
        '--log',
        default=None,
        help='CSV log path (default: scripts/backfill/backfill_analysis_set_de_fields_log.csv)',
    )
    parser.add_argument('--sleep', type=float, default=0.05, help='Seconds between requests')
    args = parser.parse_args()

    rows = load_xlsx(args.xlsx)
    if args.status != 'all':
        rows = [r for r in rows if (r.get('status') or 'released') == args.status]
    if args.limit is not None:
        rows = rows[: args.limit]

    log_path = Path(
        args.log
        or str(Path(__file__).resolve().parent / 'backfill_analysis_set_de_fields_log.csv')
    )
    auth = get_auth()
    counts: Counter = Counter()
    print(f'Server: {args.server}')
    print(f'Dry run: {args.dry_run}')
    print(f'Status filter: {args.status}')
    print(f'Records to process: {len(rows)}')
    print(f'Log: {log_path}')

    with log_path.open('w', newline='') as logf:
        writer = csv.DictWriter(
            logf,
            fieldnames=['accession', 'action', 'fields', 'message'],
        )
        writer.writeheader()

        for row in rows:
            accession = row['accession']
            obj_id = row['id']
            desired = row['fields']
            try:
                existing = get_object(args.server, obj_id, auth)
                if existing is None:
                    action, payload, message = 'error', {}, 'object not found'
                else:
                    action, payload, message = plan_patch(existing, desired, args.overwrite)
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


if __name__ == '__main__':
    main()
