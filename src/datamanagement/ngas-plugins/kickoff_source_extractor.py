#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia, 2018
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#
"""
Plug-in to kick off the source extractor pipeline once a piece of data has
been received. The current initial version of the plug-in uses a configurable
list of file_ids to filter files that do not need to be source-extracted,
and a configurable command line. The command line specification can use the
'%s' string, which will be replaced with the file_id.

For example, this can be configured under ArchiveHandling as such:

```
   <EventHandlerPlugIn Name='kickoff_source_extractor.SourceExtractorKickOff'
     PlugInPars="command=kickoff.sh:-f:%s, file_ids=file1.id:file2.id:file3.id"/>
```
"""

import logging
import subprocess

from ngamsLib import ngamsCore


logger = logging.getLogger(__name__)

class SourceExtractorKickOff(object):

    def __init__(**kwargs):
        self.command = map(kwargs['command'].split(':'))
        self.file_ids = map(lambda x: x.strip(), kwargs['file_ids'].split(':'))

    def handle_event(evt):

        if evt.file_version != 1:
            logger.info('File %s arrived with version != 1 (=%d), skipping', evt.file_id, evt.file_version)
            return

        if evt.file_id not in self.file_ids:
            logger.info('File %s not in list of files to be source-extracted, skipping', evt._file_id)
            return

        cmd = [x.replace('%s', evt.file_id) for x in self.command]
        logger.info('Executing command to trigger source extraction: %s', subprocess.list2cmdline(cmd))

        ngamsCore.execCmd(cmd)