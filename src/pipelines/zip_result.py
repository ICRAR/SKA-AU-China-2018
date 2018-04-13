import os
import argparse
import zipfile

def parseResultDir(config_file_list) :
    resultDir = None

    with open(config_file_list, 'r') as in_config_file_list:
        configfile_path = in_config_file_list.readline()
        with open(configfile_path.strip(), 'r') as fin:
            lines = fin.readlines()
            for line in lines:
                if line.find('Selavy.resultsFile') > -1 :
                    resultDir = os.path.dirname(line.replace('Selavy.resultsFile = ', '').strip())

    return resultDir

def zipResult(result_dir):
    zipFileName = "%s/%s.zip" % (result_dir, os.path.basename(result_dir))
    if os.path.exists(zipFileName) :
        os.remove(zipFileName)

    filelist = os.listdir(result_dir)
    zf = zipfile.ZipFile(zipFileName, "w", zipfile.zlib.DEFLATED)

    print("zipping now")
    for file in filelist:
        print("adding %s" % file)
        zf.write(os.path.join(result_dir, file))

    zf.close()
    return zipFileName

def test():
    resultDir = parseResultDir("/temp/config_file_list.txt")
    zip_path = zipResult(resultDir)
    print(zip_path)

if __name__ == '__main__':
    # test()
    parser = argparse.ArgumentParser(description='Push to NGAS')
    # parser.add_argument('--configfile', dest='config_file', help='each line is an image path',
    #                     default=None, type=str)
    parser.add_argument('--config_file', dest='config_file', help='path of config file',
                        default=None, type=str) 
    parser.add_argument('--out_zip_file', dest='out_zip_file', help='path of zip file',
                        default=None, type=str) 
    args = parser.parse_args()
    resultDir = parseResultDir(args.config_file)
    zip_path = zipResult(resultDir)
    print(zip_path)
    with open(args.out_zip_file, 'w') as fout:
    	fout.write(zip_path)


