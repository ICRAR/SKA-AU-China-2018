# Currently we are hardcoding the names of the parsets/config-files etc. 
# But this script should be able to read the meta-data information from 
# NGAS and use appropriate naming conventions (including possibly DATA-ID etc).  
# 
#++++++++++++++++++++++++++++++++++++++
# Define the parset/config/log files: 
#++++++++++++++++++++++++++++++++++++++
app_name='cimager'
date_tag=`date +%Y-%m-%d-%H%M%S`
workdir=/tmp/${app_name} #_${date_tag}
mkdir -p ${workdir}
parset_name=${workdir}/cimager.in
cimager_config_name=${workdir}/cimager.config
log=${workdir}/cimager.log
indata=/home/ska_au_china_2018/SKA-AU-China-2018/src/pipelines/askap_imaging/singleSource_Continuum.ms
#indata=/home/cwu/askap_imaging/singleSource_Continuum.ms
outImageName="image.askap.test" 
#nchan=useful to decide resource needed; currently we are using fixed number of cores.
nppn=1
nnodes=1
pullFromNGAS=${workdir}/pull_from_NGAS.sh
push2NGAS=${workdir}/push_to_NGAS.sh
runfile_cimager=${workdir}/run_cimager.sh 
#++++++++++++++++++++++++++++++++++++++
echo "Writing to: `pwd`"

# 0. Pull data from NGAS:  
echo "command to pull data ${indata} from NGAS" >${pullFromNGAS}
#++++++++++++++++++++++++++++++++++++++

# 1. Generate parset for cimager: 
#++++++++++++++++++++++++++++++++++++++
echo "
Cimager.dataset                                = $indata
#
Cimager.datacolumn                             = DATA
#Cimager.Channels                               = [1, %w]
#
Cimager.usetmpfs                               = True
Cimager.tmpfs                                  = /dev/shm
Cimager.Images.Names                           = [${outImageName}] 
Cimager.Images.shape                           = [256,256]
Cimager.Images.cellsize                        = [3arcsec, 3arcsec]
# Need attention 
#Cimager.Images.${outImageName}.direction      = [hm, .., J2000]
Cimager.Images.${outImageName}.polarisation   = [ I ] #[I, Q, U, V]
#
# This is how many channels to write to the image - just a single one for continuum
Cimager.Images.${outImageName}.nchan          = 1 
# The following are needed for MFS clean
# This one defines the number of Taylor terms
Cimager.Images.${outImageName}.nterms         = 1 #1 #2
# This one assigns one worker for each of the Taylor terms
Cimager.nworkergroups                          = 1 #3 #1
# Leave 'Cimager.visweights' to be determined by Cimager, based on nterms
# Leave 'Cimager.visweights.MFS.reffreq' to be determined by Cimager
#
Cimager.gridder.alldatapsf                     = true
Cimager.gridder.snapshotimaging                = false #true
#Cimager.gridder.snapshotimaging.clipping       = 0.06 # 0.02
Cimager.gridder.snapshotimaging.weightsclipping       = 0.06 # 0.02
#Cimager.gridder.snapshotimaging.wtolerance     = 2600
#Cimager.gridder                                = SphFunc #WProject
Cimager.gridder                                = WProject
#Cimager.gridder.WProject.wmax                  = 2600
Cimager.gridder.WProject.nwplanes              = 33
Cimager.gridder.WProject.wstats                = true 
Cimager.gridder.WProject.oversample            = 4
Cimager.gridder.WProject.diameter              = 12m
Cimager.gridder.WProject.blockage              = 2m
Cimager.gridder.WProject.maxfeeds              = 1
Cimager.gridder.WProject.maxsupport            = 512
Cimager.gridder.WProject.variablesupport       = true
Cimager.gridder.WProject.offsetsupport         = true
Cimager.gridder.WProject.frequencydependent    = true
#
Cimager.solver                                 = Clean
Cimager.solver.Clean.algorithm                 = Hogbom #BasisfunctionMFS #Hogbom  
Cimager.solver.Clean.niter                     = 1 #200 #2000
Cimager.solver.Clean.gain                      = 0.1
Cimager.solver.Clean.scales                    = [0,3,10]
Cimager.solver.Clean.verbose                   = True
Cimager.solver.Clean.tolerance                 = 0.01
Cimager.solver.Clean.weightcutoff              = zero
Cimager.solver.Clean.weightcutoff.clean        = false
Cimager.solver.Clean.psfwidth                  = 256 #1024
Cimager.solver.Clean.logevery                  = 100
#Cimager.threshold.minorcycle                   = [15%, 0.2mJy] 
Cimager.threshold.minorcycle                   = [25%] 
Cimager.threshold.majorcycle                   = [0.2mJy] 
Cimager.threshold.masking                      = 0.9 #-1
Cimager.ncycles                                = 1 #5 #20
Cimager.Images.writeAtMajorCycle               = false #true
#
Cimager.restore                                = true
Cimager.restore.beam                           = fit  #[45arcsec, 45arcsec, 0deg]
#Cimager.restore.beam                           = [10arcsec, 10arcsec, 0deg]
#
Cimager.calibrate                              = false 
Cimager.calibrate.ignorebeam                   = true  
Cimager.calibaccess                            = table 
Cimager.calibaccess.table                      =  
# 
#Cimager.preconditioner.Names                   = None #[Wiener, GaussianTaper]
Cimager.preconditioner.Names                   = [Wiener,GaussianTaper]
Cimager.preconditioner.GaussianTaper           = [15arcsec, 15arcsec, 0deg]
#Cimager.preconditioner.Wiener.Taper             = [512, 512]
Cimager.preconditioner.Wiener.robustness       = -0.5
#Cimager.gentlepreconditioner                   = true 
Cimager.preconditioner.preservecf              = true 
	" >${parset_name}
#++++++++++++++++++++++++++++++++++++++

#++++++++++++++++++++++++++++++++++++++
# 2. Generate config file to execute cimager: 
# Load necessary modules: 
#++++++++++++++++++++++++++++++++++++++
echo "
module use /home/askap/Software/modulefiles
module load askapsoft
module load askapdata
cd ${workdir}
" >${cimager_config_name}
echo "srun --export=ALL --ntasks=${nnodes} --ntasks-per-node=${nppn} cimager -p -c ${parset_name} > ${log}" >>${cimager_config_name}
#++++++++++++++++++++++++++++++++++++++
# 3. Prepare the cimager execution command: 
echo "source ${cimager_config_name}" >${runfile_cimager}

# 4. Prepare push to NGAS: 
echo "command to push data ${outImageName} to NGAS" >${push2NGAS}
