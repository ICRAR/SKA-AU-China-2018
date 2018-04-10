#
# 
#
def transferMetadata(filename):
    # determine the obsid and source (ASKAP/MWA)
    if 1==1:
        # MWA
        obsid = 123
        url = "vo.mwatelescope.org:8000/asvo/tap"
    else:
        # ASKAP
        obsid = 123
        url = ""

    # get the metadata from the vo service
    obscore = getMetadataFromVOService(obsid, url)

    # write the metadata to the database if it doesn't already exist
    putMetadata(obscore)

def getMetadataFromVOService(obsid, url):
    # Make VO / TAP call and get the results
    return obscore

def putMetdataIntoDB(obscore):
    pass
