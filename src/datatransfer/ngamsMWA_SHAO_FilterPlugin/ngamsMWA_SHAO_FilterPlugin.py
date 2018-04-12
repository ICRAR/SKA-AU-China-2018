#
#    (c) University of Western Australia
#    International Centre of Radio Astronomy Research
#    M468/35 Stirling Hwy
#    Perth WA 6009
#    Australia
#
#    Copyright by UWA,
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
#******************************************************************************
# Who       When        What
# --------  ----------  -------------------------------------------------------
# gsleap    12/04/2018  Created
"""
Contains a Filter Plug-In used to filter out those files that
(1) have already been delivered to the remote destination
(2) belong to Solar observations with project_id 'c105' or 'c106'
"""

# only interested in these obsids
observation_list = ['1059319096',]

def ngamsMWA_SHAO_FilterPlugin(srvObj,
                               plugInPars,
                               filename,
                               fileId,
                               fileVersion = -1,
                               reqPropsObj = None):

    """
    srvObj:        Reference to NG/AMS Server Object (ngamsServer).

    plugInPars:    Parameters to take into account for the plug-in
                   execution (string).

    fileId:        File ID for file to test (string).

    filename:      Filename of (complete) (string).

    fileVersion:   Version of file to test (integer).

    reqPropsObj:   NG/AMS request properties object (ngamsReqProps).

    Returns:       0 if the file does not match, 1 if it matches the
                   conditions (integer/0|1).
    """
    # The fileId for MWA is the obsid
    this_obs_id = fileId[0:10]

    return this_obs_id in observation_list

# EOF