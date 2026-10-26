# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The voice note body, for the main chat and a side chat."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SESSION = '6f1c2d4e-0b7a-4c3e-9f5d-2a8b1e0c7d93'

PROGRAM = r'''
#include <stdio.h>
#include "muse_chat_priv.h"
int main(void) {
    puts(MUSE_HATCH_NOTE_HEAD "AAAA" MUSE_HATCH_NOTE_TAIL);
    return 0;
}
'''


def bodies(*defines):
    with tempfile.TemporaryDirectory() as tmp:
        src, exe = os.path.join(tmp, 'side_chat.c'), os.path.join(tmp, 'side_chat')
        Path(src).write_text(PROGRAM)
        cc = os.environ.get('CC', 'cc').split()
        subprocess.run(cc + ['-Wall', '-Werror', '-I', str(ROOT / 'components/muse'), *defines, src, '-o', exe],
                       check=True, capture_output=True, text=True)
        out = subprocess.run([exe], check=True, capture_output=True, text=True).stdout.splitlines()
    return json.loads(out[0])


class SideChat(unittest.TestCase):
    def test_main_chat_by_default(self):
        note = bodies()
        self.assertNotIn('session_id', note)
        self.assertEqual(note['message'], '')
        self.assertEqual(note['output_modality'], 'text')
        self.assertEqual(note['items'][0]['data_base64'], 'AAAA')

    def test_side_chat(self):
        note = bodies('-DCONFIG_MUSE_CHAT_SIDE_CHAT=1',
                     f'-DCONFIG_MUSE_CHAT_SESSION_ID="{SESSION}"',
                     '-DCONFIG_MUSE_CHAT_SIDE_CHAT_PROMPT="Journal entry"')
        self.assertEqual(note['session_id'], SESSION)
        self.assertEqual(note['message'], 'Journal entry')
        self.assertEqual(note['output_modality'], 'text')
        self.assertEqual(note['items'][0]['mime_type'], 'audio/wav')
        self.assertEqual(note['items'][0]['data_base64'], 'AAAA')


if __name__ == '__main__':
    unittest.main()
