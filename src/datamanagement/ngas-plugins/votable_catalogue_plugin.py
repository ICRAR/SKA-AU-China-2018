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
"""Registers a VOTable catalogue file into the CASDA metadata tables"""
import contextlib
import os

from ngamsLib import ngamsPlugInApi
import psycopg2

def insert_catalogue_dataproduct(dsn, fid):
    with contextlib.closing(psycopg2.connect(dsn)) as db:
        with contextlib.closing(db.cursor()) as cursor:
            cursor.execute("INSERT INTO data_product(file_id, dataproduct_type, deposit_state) VALUES (%s, 'CATALOGUE', 'DEPOSITED')", (fid,))
            cursor.execute('COMMIT')

def votable_catalogue_plugin(srv, request):

    mime = request.getMimeType()
    parDic = ngamsPlugInApi.parseDapiPlugInPars(srv.cfg, mime)

    options = ('host', 'user', 'password', 'dbname')
    for option in options:
        if option not in parDic:
            raise Exception('%s option not specified for votable_catalogue_plugin, please provide one' % option)

    host, user, password, dbname = [parDic[option] for option in options]
    dsn = 'host=%s user=%s password=%s dbname=%s' % (host, user, password, dbname)
    stageFilename = request.getStagingFilename()
    uncomprSize = ngamsPlugInApi.getFileSize(stageFilename)
    file_id = os.path.basename(request.getFileUri())
    diskInfo = request.getTargDiskInfo()
    fileVersion, relPath, relFilename, complFilename, fileExists = \
        ngamsPlugInApi.genFileInfo(srv.db, srv.cfg, request, diskInfo,
                                   request.getStagingFilename(), file_id, file_id,
                                   [], [])

    insert_catalogue_dataproduct(dsn, file_id)

    return ngamsPlugInApi.genDapiSuccessStat(
        diskInfo.getDiskId(), relFilename, file_id, fileVersion, mime,
        uncomprSize, uncomprSize, '', relPath, diskInfo.getSlotId(), fileExists,
        complFilename)