import os, glob
from datetime import datetime
from optparse import OptionParser

# Script to submit MC production
# ---------- Step 1 ----------
'''
python3 batchSubmitterMC_Step1_RAW.py --indir /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt20_500_TuneCP5_13p6TeV/GEN \
--out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt20_500_TuneCP5_13p6TeV/RAW \
--maxEvents -1 --queue short --globalTag 126X_mcRun3_2023_forPU65_v1
'''

if __name__ == "__main__" :

    parser = OptionParser()    
    parser.add_option("--indir",     dest="indir",     type=str,            default=None,                            help="Input folder name")
    parser.add_option("--out",       dest="out",       type=str,            default=None,                            help="Output folder name")
    parser.add_option("--maxEvents", dest="maxEvents", type=int,            default=-1,                              help="Number of events per job")
    parser.add_option("--queue",     dest="queue",     type=str,            default='short',                         help="long or short queue")
    parser.add_option("--globalTag", dest="globalTag", type=str,            default='126X_mcRun3_2023_forPU65_v1',   help="Which globalTag to use")
    parser.add_option("--no_exec",   dest="no_exec",   action='store_true', default=False)
    (options, args) = parser.parse_args()

    os.system('mkdir -p '+options.out)

    inRootNameList = glob.glob(options.indir+"/Ntuple_*.root")
    inRootNameList.sort()

    for inRootName in inRootNameList:

        idx = inRootName.split(".root")[0].split("Ntuple")[1].split("_")[1]
        outJobName  = options.out + '/job_' + str(idx) + '.sh'
        outLogName  = options.out + '/log_' + str(idx) + '.txt'
        outRootName = options.out + '/Ntuple_' + str(idx) + '.root'

        # random seed for MC production should every time we submit a new generation
        # it's obtained by summing current Y+M+D+H+M+S+job_number
        now = datetime.now()
        randseed = int(now.year) + int(now.month) + int(now.day) + int(now.hour) + int(now.minute) + int(now.second) + int(idx)

        cmsRun = "cmsRun MC_Step1_RAW_QCD_Pt30to500_cfg.py inputFiles=file:"+inRootName+" outputFile=file:"+outRootName
        cmsRun = cmsRun+" maxEvents="+str(options.maxEvents)+" randseed="+str(randseed)+" globalTag="+options.globalTag
        cmsRun = cmsRun+" >& "+outLogName

        skimjob = open (outJobName, 'w')
        skimjob.write ('#!/bin/bash\n')
        skimjob.write ('export X509_USER_PROXY=~/.t3/proxy.cert\n')
        skimjob.write ('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
        skimjob.write ('cd %s\n' %os.getcwd())
        skimjob.write ('export SCRAM_ARCH=slc6_amd64_gcc472\n')
        skimjob.write ('eval `scram r -sh`\n')
        skimjob.write ('cd %s\n' %os.getcwd())
        skimjob.write (cmsRun+'\n')
        skimjob.close ()

        os.system ('chmod u+rwx ' + outJobName)
        command = ('/home/llr/cms/evernazza/t3submit -'+options.queue+' \'' + outJobName +"\'")
        print(command)
        if not options.no_exec: os.system (command)
