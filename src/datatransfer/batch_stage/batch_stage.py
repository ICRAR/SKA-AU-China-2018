#!/usr/bin/env python
#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia, 2015
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

#
#    This script is designed to take in a file of carriage return separated
#    obsid's and then call the DMF daemon to stage the observations.
#

import os
import sys
import base64
import socket
import struct
import random
import errno
import shutil
import logging
import logging.handlers
import threading 
import time
import datetime 
import signal
import subprocess
import zipfile
import urlparse
import json
import psycopg2
import psycopg2.pool
import httplib
from ConfigParser import SafeConfigParser
from threading import Condition, Thread, Lock
from collections import deque
from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from multiprocessing.pool import ThreadPool
from functools import partial

APP_PATH = os.path.dirname(os.path.realpath(__file__))
path = APP_PATH + '/log/'

if not os.path.exists(path):
   os.makedirs(path)

logger = logging.getLogger('processor')
logger.setLevel(logging.DEBUG)
logger.propagate = False

logfilename = 'batch_stage.log'
rot = logging.handlers.TimedRotatingFileHandler(path + logfilename, 'midnight', 1, 0)
rot.setLevel(logging.DEBUG)
rot.setFormatter(logging.Formatter('%(asctime)s, %(levelname)s, %(message)s'))
logger.addHandler(rot)

sec_const = 315964784

def GPSNow():
   return int(time.time()) - sec_const


class BatchStageProcessor(object):
  
   def __init__(self):
      self.fp = None

      self.config = SafeConfigParser()
      self.config.readfp(open(APP_PATH + '/' + 'config.cfg', "r"))
      
      self.LOG = '/home/ngas/mwaops/uvfits/log/cotter'

   def _pawseyStageFiles(self, fileList, host, port, retries = 3, backoff = 10, timeout = 4500):
      """
      issue a dmget which will do a bulk staging of files for a complete observation;
      this function will block until all files are staged or there is a timeout

      filename:    filename to be staged (string)
      host:        host running the pawseydmget daemon (string)
      port:        port of the pawsey / mwadmget daemon (int)
      timeout:     socket timeout in seconds
      retries:     number of times to retry (timeout is halved each retry)
      backoff:     number of seconds to wait before retrying
      """

      while True:
         sock = None
         try:
            files = {'files' : fileList}
            jsonoutput = json.dumps(files)

            val = struct.pack('>I', len(jsonoutput))
            val = val + jsonoutput

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.sendall(val)
            sock.settimeout(timeout)

            exitcode = struct.unpack('!H', sock.recv(2))[0]
            if exitcode != 0:
               raise Exception('_pawseyStageFiles error with exitcode %s' % (str(exitcode)))

            # success so exit retry loop
            break

         except Exception as e:
            if retries > 0:
               retries -= 1
               timeout /= 2
               errMsg = '_pawseyStageFiles raised an error: %s, retrying...' % (str(e))
               logger.info(errMsg)
               time.sleep(backoff)
            else:
               errMsg = '_pawseyStageFiles raised an error: %s, no more retries, raising exception!' % (str(e))
               logger.info(errMsg)
               raise e

         finally:
            if sock:
               sock.close()
   
   
   def _retrieveMWAFiles(self, obsid):
      con = None
      cursor = None
   
      try:
         con = self.fp.dbp.getconn()
         cursor = con.cursor()
         cursor.execute("select filename from data_files where observation_num = %s", [str(obsid)])
         
         files = []
         results = cursor.fetchall()
         for i in results:
            files.append(i[0])
         
         return files
      
      finally:
         if cursor:
            cursor.close()
         
         if con:
            self.fp.dbp.putconn(conn=con)
   
   
   def _retrieveNGASFilePaths(self, obsid):
      files = []
      con = None
      cursor = None
   
      try:
         con = self.fp.ngasdb.getconn()
         cursor = con.cursor()
         cursor.execute(("select distinct on (file_id) mount_point || '/' || file_name as path from ngas_files "
                         "inner join ngas_disks on ngas_disks.disk_id = ngas_files.disk_id where file_id like %s "
                         " and ngas_disks.disk_id in ('35ecaa0a7c65795635087af61c3ce903', '54ab8af6c805f956c804ee1e4de92ca4', "
                         "'921d259d7bc2a0ae7d9a532bccd049c7', 'e3d87c5bc9fa1f17a84491d03b732afd') order by file_id, file_version desc"), 
                        [str(obsid) + '%'])
         
         results = cursor.fetchall()
         for r in results:
            files.append(r[0])

         return files
      
      finally:
         if cursor:
            cursor.close()
         
         if con:
            self.fp.ngasdb.putconn(conn = con)


   def processObs(self, obsid):
      logger.info('Staging observation: %s' % (str(obsid)))

      mwa_files = self._retrieveMWAFiles(obsid)
      logger.info('Retrieved %s mwa files for: %s' % (len(mwa_files), str(obsid)))

      # get file locations and then stage them
      files = self._retrieveNGASFilePaths(obsid)
      logger.info('Retrieved %s ngas files for: %s' % (len(files), str(obsid)))
      
      if len(files) != len(mwa_files):
         raise Exception('MWA (%s) and NGAS (%s) file number mismatch; ignoring: %s' % (len(mwa_files), len(files), str(obsid)))
      
      logger.info('Staging observation: %s' % (str(obsid)))
      self._pawseyStageFiles(files, 'fe1.pawsey.org.au', 9898)

      logger.info('Staging success: %s' % (str(obsid)))


class MyHTTPServer(HTTPServer):
   def __init__(self, *args, **kw):
      HTTPServer.__init__(self, *args, **kw)
      self.context = None


class HTTPGetHandler(BaseHTTPRequestHandler):

   def do_GET(self):
      
      parsed_path = urlparse.urlparse(self.path)
      
      try:
         if parsed_path.path.lower() == '/status'.lower():
            
            statustext = 'running'
            data = { 'status': statustext, 'queue': len(self.server.context._q), 'processing': self.server.context._processq }
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(data))
         
         elif parsed_path.path.lower() == '/kill'.lower():
            self.server.context.stop()
            self.send_response(200)
            self.end_headers()
             
         elif parsed_path.path.lower() == '/rescan'.lower():
            self.server.context.processRecentObs()
            self.send_response(200)
            self.end_headers()
            self.wfile.write('OK')

      except Exception as e:
         logger.error('do_GET: %s' % (str(e)))
         self.send_response(400)
         self.end_headers()


class ProductProcessor(object):
   
   def __init__(self, handler, concurrent = 8):
      self._q = deque()
      self._qLock = Lock()
      self._sem = threading.Semaphore(concurrent)
      self._threads = []
      self._processq = []
      
      self._stop = False

      self.handler = handler
      self.handler.fp = self

      config = SafeConfigParser()
      config.readfp(open(APP_PATH + '/' + 'config.cfg', "r"))
      
      self.dbp = psycopg2.pool.ThreadedConnectionPool(minconn=2,
                                          maxconn=8,
                                          host=config.get("Database", "dbhost"),
                                          user=config.get("Database", "dbuser"),
                                          database=config.get("Database", "dbname"),
                                          password=base64.b64decode(config.get("Database", "dbpass")),
                                          port=5432)

      self.sitedbp = psycopg2.pool.ThreadedConnectionPool(minconn=2,
                                          maxconn=8,
                                          host=config.get("Database", "sitedbhost"),
                                          user=config.get("Database", "sitedbuser"),
                                          database=config.get("Database", "sitedbname"),
                                          password=base64.b64decode(config.get("Database", "sitedbpass")),
                                          port=5432)
      
      self.ngasdb = psycopg2.pool.ThreadedConnectionPool(minconn=2,
                                           maxconn=8,
                                           host=config.get("Database", "ndbhost"),
                                           user=config.get("Database", "ndbuser"),
                                           database=config.get("Database", "ndbname"),
                                           password=config.get("Database", "ndbpass"),
                                           port=5432)
      
      self.dmgetHost = config.get("Pawsey", "dmgethost")
      self.dmgetPort = config.getint("Pawsey", "dmgetport")
      self.obslistfile = config.get("Processing", "obslistfile")
      self.webserver_port = config.getint("Processing", "webserver_port")

      # fill the queue with observations to process
      self.processRecentObs()
      
      self.cmdserver = MyHTTPServer(('', self.webserver_port), HTTPGetHandler)
      self.cmdserver.context = self

      self.cmdthread = threading.Thread(name='_commandLoop', target=self._commandLoop, args=(self.cmdserver,))
      self.cmdthread.setDaemon(True)
      self.cmdthread.start()
      
      signal.signal(signal.SIGINT, self._signalINT)
      signal.signal(signal.SIGTERM, self._signalINT)


   def processRecentObs(self):
      
      try:
         logger.info('Getting new observation set...')
  
         count = 0       
         rowset = self._getObsProcessingList()
         with self._qLock:
            for row in rowset:
               obsid = row

               if obsid in self._processq:
                  continue
              
               if obsid in self._q:
                  continue
              
               self._q.append(obsid)
               logger.info("added {0} to queue".format(obsid))
               count += 1
               
         logger.info('Number of new observations added: %s' % (count))
         
      except Exception as e:
         logger.error('processRecentObs: %s' % (str(e)))


   def _commandLoop(self, cmdserver):
      try:
         # start server
         cmdserver.serve_forever()
      except Exception as e:
         pass


   def _signalINT(self, signal, frame):
      self.stop()
      

   def _getObsProcessingList(self):
      
      if self.obslistfile:
        with open(self.obslistfile) as f:
            return sorted([x.strip('\n') for x in f.readlines()])


   def _processObs(self, obsid):
      
      try:         
         self.handler.processObs(obsid)
         
      except Exception as e:
         logger.exception("processObs: ObsID: %s " % str(obsid))
         time.sleep(1)

      finally:
         with self._qLock:
            self._threads.remove(threading.current_thread())
            self._processq.remove(obsid)
            
         self._sem.release()
         
      
   def stop(self):
      logger.info('Interrupted...')
      self._stop = True


   def start(self):

      while self._stop is False:

         length = None
         obsid = None

         self._sem.acquire()
         
         if self._stop is True:
            break

         try:
            with self._qLock:
               obsid = self._q.popleft()
               self._processq.append(obsid)
               length = len(self._q)
         except IndexError:
            time.sleep(1)
            continue
         
         logger.info('Queue size: %s' % (str(length)))

         t = threading.Thread(target = self._processObs, args = (obsid,))
         with self._qLock:
            self._threads.append(t)
         t.start()

      logger.info('Stopping processor, waiting for jobs to finish ...')
      # wait till they are all finished
      for t in self._threads:
         t.join()


def main():
   
   logger.info('Starting processor...')

   fh = BatchStageProcessor()
   fp = ProductProcessor(fh)
   fp.start()
   
   logger.info('Processor stopped')

if __name__ == "__main__":
   try:
      main()
      sys.exit(0)
   except Exception as e:
      logger.error(str(e))
      sys.exit(1)
