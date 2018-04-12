import os
import argparse
import commands
import zipfile

def parseResultDir(config_file) :
    resultDir = None

    with open(config_file, 'r') as configFile:
    	configfile_path = configFile.readline()
        with open(configfile_path, 'r') as fin:
            lines = fin.readlines()
            for line in lines:
        		if line.index('Selavy.resultsFile') > -1 :
        			resultDir = os.path.dirname(line.replace('Selavy.resultsFile = ', '').strip())

    return resultDir

def zipResult(result_dir):
	zipFileName = "%s/%s.zip" % (result_dir, os.path.basename(result_dir))

	zf = zipfile.ZipFile(zipFileName, "w", zipfile.zlib.DEFLATED)

    	filelist = os.listdir(result_dir)

	for file in filelist:
		zf.write(os.path.join(result_dir, file))

	zf.close()

	return zipFileName

if __name_ == '__main__':
    parser = argparse.ArgumentParser(description='Push to NGAS')
    # parser.add_argument('--configfile', dest='config_file', help='each line is an image path',
    #                     default=None, type=str)
    parser.add_argument('--config_file', dest='config_file', help='path of config file',
                        default=None, type=str) 
    parser.add_argument('--tar_file', dest='tar_file', help='path of tar file',
                        default=None, type=str) 
    args = parser.parse_args()
    resultDir = parseResultDir(args.config_file)
    zip_path = zipResult(resultDir)

    with open(args.tar_file) as fout:
    	fout.write(zip_path)


