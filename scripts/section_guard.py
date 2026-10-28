#!/usr/bin/env python3
"""Section selection and complete write/staging isolation for the render job."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
from pathlib import Path

SECTIONS = ('languages', 'frameworks', 'tools')
FRAMEWORK_SOURCES = {
    'framework_orbits.py', 'framework_contours.json', 'framework_expansion_contours.json',
    'framework_refinement_contours.json', 'framework_polish_contours.json',
    'framework_polish_preserved_rgb.json', 'framework_bootstrap_preserved_rgb.json',
    'bootstrap_outline_contours.json', 'build_bootstrap_outline.py',
    'framework_preserved_rgb.json', 'build_framework_refinement.py',
    'build_framework_polish.py', 'verify_frameworks.py',
}
SHARED = {'scripts/render_sections.py', 'scripts/render_constellation.py',
          'scripts/requirements.txt', 'data/icon-paths.json', 'data/supplemental-icons.json'}


# Only reviewed presentation/CI files may request validation without
# regenerating canonical artwork. Unknown and shared inputs remain fail-closed.
NON_RENDER_CHANGES = {
    'README.md', 'docs/constellation.md',
    'docs/centered-constellation-preview.md',
    '.github/workflows/profile-centered-preview.yml',
    '.github/workflows/render-constellation.yml',
    'scripts/render_centered_constellation.py',
    'scripts/section_guard.py', 'scripts/test_section_guard.py',
} | {f'assets/constellation-{section}-centered.gif' for section in SECTIONS}


def git(*args):
    return subprocess.check_output(['git', *args], text=True).splitlines()


def selected_sections(selection):
    if selection == 'both':
        return ('languages', 'frameworks')  # Historical meaning, deliberately unchanged.
    if selection not in SECTIONS:
        raise ValueError(f'Unknown section: {selection}')
    return (selection,)


def allowed_assets(selection):
    return {f'assets/constellation-{section}.{ext}'
            for section in selected_sections(selection) for ext in ('gif', 'png')}


def without_tools(source):
    """Prove a shared entrypoint change affects only Tools config/dispatch/defaults.

    Any other AST change fails automatic selection, including shared functions,
    Languages/Frameworks configuration and extra statements in the entrypoint.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in
                                               ('SECTIONS', 'defaults') for t in node.targets):
            if isinstance(node.value, ast.Dict):
                entries = [(k, v) for k, v in zip(node.value.keys, node.value.values)
                           if not (isinstance(k, ast.Constant) and k.value == 'tools')]
                node.value.keys = [k for k, _ in entries]
                node.value.values = [v for _, v in entries]
        if isinstance(node, ast.FunctionDef) and node.name == 'render_section':
            target = ast.dump(ast.parse("section_id == 'tools'", mode='eval').body)
            node.body = [s for s in node.body if not
                         (isinstance(s, ast.If) and ast.dump(s.test) == target)]
    return ast.dump(tree, include_attributes=False)


def select(changed, requested=None, before_source=None, after_source=None):
    if requested:
        selected_sections(requested)
        return requested
    identified = set()
    for path in changed:
        for section in SECTIONS:
            if path in {f'assets/constellation-{section}.gif', f'assets/constellation-{section}.png'}:
                identified.add(section)
        if path in {'scripts/verify_languages.py', 'assets/moonbit-official.png'}:
            identified.add('languages')
        if path.removeprefix('scripts/') in FRAMEWORK_SOURCES or path.startswith('scripts/framework_brand_sources/'):
            identified.add('frameworks')
        if path in {'scripts/tools_observatory.py', 'scripts/tools_particles.json',
                    'scripts/tools_station_reference.png', 'scripts/tools_motion_v1.json',
                    'scripts/tools_review.py', 'scripts/verify_tools.py'} or path.startswith('scripts/tools_fonts/'):
            identified.add('tools')
    shared = changed & SHARED
    if shared:
        narrow_tools = (identified == {'tools'} and shared == {'scripts/render_sections.py'}
                        and before_source is not None and after_source is not None
                        and without_tools(before_source) == without_tools(after_source))
        if not narrow_tools:
            raise ValueError('Ambiguous shared-source change; explicit workflow_dispatch section is required')
    if identified == {'languages', 'frameworks'}:
        return 'both'
    if len(identified) == 1:
        return identified.pop()
    # A presentation-only update needs verification, not a new renderer run.
    # Never silently accept an unknown file or multi-section change.
    if not identified and changed <= NON_RENDER_CHANGES:
        return 'none'
    raise ValueError('Ambiguous/no selected section; dispatch an explicit isolated section')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def snapshot(selection):
    assert not git('diff', '--cached', '--name-only'), 'Unexpected staged input'
    paths = git('ls-files')
    allowed = allowed_assets(selection)
    return {'selection': selection, 'allowed': sorted(allowed), 'tracked': paths,
            'sha256': {p: digest(p) for p in paths if p not in allowed}}


def check(guard):
    assert guard['allowed'] == sorted(allowed_assets(guard['selection'])), 'Guard authorization changed'
    assert git('ls-files') == guard['tracked'], 'Tracked inventory changed'
    for path, expected in guard['sha256'].items():
        assert digest(path) == expected, f'Unselected tracked file changed: {path}'
    allowed = set(guard['allowed'])
    changed = set(git('diff', '--name-only', 'HEAD'))
    staged = set(git('diff', '--cached', '--name-only'))
    assert changed <= allowed, f'Unauthorized output: {changed - allowed}'
    assert staged <= allowed, f'Unauthorized staging: {staged - allowed}'
    assert not git('ls-files', '--others', '--exclude-standard'), 'Unexpected untracked output'
    return {'selection': guard['selection'], 'allowed': sorted(allowed),
            'checked_unselected_files': len(guard['sha256']), 'staged': sorted(staged)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('select')
    p.add_argument('--before')
    p.add_argument('--requested')
    for command in ('snapshot', 'check'):
        p = sub.add_parser(command)
        p.add_argument('--guard', type=Path, required=True)
        if command == 'snapshot':
            p.add_argument('--section', required=True)
    args = parser.parse_args()
    if args.command == 'select':
        before = args.before or 'HEAD^'
        if set(before) == {'0'}:
            before = 'HEAD^'
        changed = set(git('diff', '--name-only', before, 'HEAD'))
        if 'scripts/render_sections.py' in changed:
            # Only compare historical renderer code when that entrypoint
            # actually changed. It may not exist in an older parent commit.
            old = subprocess.check_output(
                ['git', 'show', f'{before}:scripts/render_sections.py'], text=True)
            new = Path('scripts/render_sections.py').read_text()
        else:
            old, new = None, None
        selected = select(changed, args.requested, old, new)
        print('No rendering required; validation only' if selected == 'none'
              else f'Regenerating: {selected}')
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
                output.write(f'section={selected}\n')
    elif args.command == 'snapshot':
        args.guard.write_text(json.dumps(snapshot(args.section), indent=2) + '\n')
    else:
        print(json.dumps(check(json.loads(args.guard.read_text())), indent=2))


if __name__ == '__main__':
    main()
