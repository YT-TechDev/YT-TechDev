#!/usr/bin/env python3
"""Exercise selection and unauthorized writes/staging against a real Git index."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from section_guard import allowed_assets, check, main, select, snapshot, without_tools


class SelectionTests(unittest.TestCase):
    def test_explicit_and_legacy_both(self):
        self.assertEqual(allowed_assets('both'), {
            'assets/constellation-languages.gif', 'assets/constellation-languages.png',
            'assets/constellation-frameworks.gif', 'assets/constellation-frameworks.png'})
        for section in ('languages', 'frameworks', 'tools', 'both'):
            self.assertEqual(select(set(), section), section)
        with self.assertRaises(ValueError):
            select(set(), 'all')

    def test_isolated_detection(self):
        for section, path in [('languages', 'scripts/verify_languages.py'),
                              ('frameworks', 'scripts/framework_orbits.py'),
                              ('tools', 'scripts/tools_observatory.py'),
                              ('tools', 'scripts/tools_particles.json'),
                              ('tools', 'scripts/verify_tools.py')]:
            self.assertEqual(select({path}), section)
        self.assertEqual(select({'scripts/verify_languages.py', 'scripts/verify_frameworks.py'}), 'both')
        for changed in ({'scripts/render_sections.py'}, {'scripts/requirements.txt'},
                        {'scripts/verify_tools.py', 'scripts/verify_frameworks.py'},
                        {'scripts/unknown_renderer.py', 'assets/constellation-tools-centered.gif'}):
            with self.assertRaises(ValueError):
                select(changed)

    def test_non_render_diffs_are_validation_only(self):
        # PR #4's actual production merge included these exact paths.
        preview = {
            'README.md', 'docs/centered-constellation-preview.md',
            '.github/workflows/profile-centered-preview.yml',
            'scripts/render_centered_constellation.py',
            'assets/constellation-languages-centered.gif',
            'assets/constellation-frameworks-centered.gif',
            'assets/constellation-tools-centered.gif',
        }
        self.assertEqual(select(preview), 'none')
        self.assertEqual(select(set()), 'none')
        self.assertEqual(select({'assets/constellation-tools-centered.gif'}), 'none')
        self.assertEqual(select({
            'scripts/section_guard.py', 'scripts/test_section_guard.py',
            '.github/workflows/render-constellation.yml',
        }), 'none')
        self.assertEqual(select(preview | {'assets/constellation-languages.gif'}), 'languages')
        self.assertEqual(select(preview | {'scripts/tools_observatory.py'}), 'tools')
        self.assertEqual(select({
            'assets/constellation-frameworks.png',
            'assets/constellation-languages.gif',
        }), 'both')

    def test_non_render_scope_fails_closed(self):
        for unsafe in (
            {'scripts/render_sections.py'}, {'scripts/render_constellation.py'},
            {'scripts/requirements.txt'}, {'scripts/unknown_renderer.py'},
            {'assets/constellation-tools-extra.gif'},
            {'scripts/test_section_guard.py', 'scripts/requirements.txt'},
            {'assets/constellation-languages-centered.gif', 'scripts/requirements.txt'},
            {'assets/constellation-languages.gif', 'assets/constellation-tools.gif'},
        ):
            with self.subTest(unsafe=unsafe), self.assertRaises(ValueError):
                select(unsafe)
        self.assertEqual(select({'scripts/requirements.txt'}, requested='tools'), 'tools')

    def test_cli_non_render_does_not_read_missing_historical_renderer(self):
        with patch('sys.argv', ['section_guard.py', 'select', '--before', 'parent']), \
             patch('section_guard.git', return_value=[
                 'assets/constellation-languages-centered.gif',
                 'scripts/section_guard.py',
             ]), \
             patch('section_guard.subprocess.check_output') as read_old, \
             patch.dict(os.environ, {'GITHUB_OUTPUT': ''}), \
             patch('builtins.print') as printed:
            main()
        read_old.assert_not_called()
        printed.assert_called_once_with('No rendering required; validation only')

    def test_shared_tools_entrypoint_is_bounded(self):
        old = "SECTIONS = {'tools': {'height':810}, 'languages': {'height':780}}\n"
        new = "SECTIONS = {'tools': {'height':900}, 'languages': {'height':780}}\n"
        changed = {'scripts/render_sections.py', 'scripts/tools_observatory.py'}
        self.assertEqual(select(changed, before_source=old, after_source=new), 'tools')
        for bad in (new.replace('780', '900'), new + 'print(123)\n'):
            with self.assertRaises(ValueError):
                select(changed, before_source=old, after_source=bad)
        self.assertNotEqual(without_tools(old), without_tools(old + 'import random\n'))


class WriteGuardTests(unittest.TestCase):
    def test_real_index_protection_and_negative_controls(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            os.chdir(directory)
            try:
                subprocess.run(['git', 'init', '-q'], check=True)
                subprocess.run(['git', 'config', 'user.name', 'Test'], check=True)
                subprocess.run(['git', 'config', 'user.email', 'test@example.invalid'], check=True)
                paths = ['scripts/source.py'] + [f'assets/constellation-{s}.{ext}'
                        for s in ('languages', 'frameworks', 'tools') for ext in ('gif', 'png')]
                for p in paths:
                    Path(p).parent.mkdir(parents=True, exist_ok=True)
                    Path(p).write_text(p)
                subprocess.run(['git', 'add', '.'], check=True)
                subprocess.run(['git', 'commit', '-qm', 'fixture'], check=True)
                guard = snapshot('tools')
                Path('assets/constellation-tools.png').write_text('selected update')
                check(guard)
                subprocess.run(['git', 'add', 'assets/constellation-tools.png'], check=True)
                check(guard)  # Selected images may be staged.
                for p in ('assets/constellation-languages.png', 'assets/constellation-frameworks.gif', 'scripts/source.py'):
                    original = Path(p).read_bytes()
                    Path(p).write_text('unauthorized')
                    with self.assertRaises(AssertionError):
                        check(guard)
                    subprocess.run(['git', 'add', p], check=True)
                    Path(p).write_bytes(original)  # Also reject index-only violations.
                    with self.assertRaises(AssertionError):
                        check(guard)
                    subprocess.run(['git', 'reset', '-q', 'HEAD', '--', p], check=True)
                Path('unexpected.tmp').write_text('unexpected')
                with self.assertRaises(AssertionError):
                    check(guard)
                Path('unexpected.tmp').unlink()
                bad = json.loads(json.dumps(guard))
                bad['allowed'].append('scripts/source.py')
                with self.assertRaises(AssertionError):
                    check(bad)
                check(guard)
            finally:
                os.chdir(previous)


if __name__ == '__main__':
    unittest.main()
