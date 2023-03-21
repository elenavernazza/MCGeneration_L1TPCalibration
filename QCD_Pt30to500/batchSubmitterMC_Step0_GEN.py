import os, glob
from datetime import datetime
from optparse import OptionParser

# Script to submit MC production
# ---------- Step 0 ----------

'''
python3 batchSubmitterMC_Step0_GEN.py --out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X/GEN \
--maxEvents 180 --nJobs 6000 --queue short --globalTag 124X_mcRun3_2022_realistic_postEE_v1
python3 batchSubmitterMC_Step0_GEN.py --out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X_6000_6500/GEN \
--maxEvents 500 --nJobs 150 --queue long --globalTag 124X_mcRun3_2022_realistic_postEE_v1 --start_from 6000
python3 batchSubmitterMC_Step0_GEN.py --out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X_7000_10000/GEN \
--maxEvents 100 --nJobs 3000 --queue short --globalTag 124X_mcRun3_2022_realistic_postEE_v1 --start_from 7000
python3 batchSubmitterMC_Step0_GEN.py --out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X_10000_15000/GEN \
--maxEvents 100 --nJobs 5000 --queue short --globalTag 124X_mcRun3_2022_realistic_postEE_v1 --start_from 10000
python3 batchSubmitterMC_Step0_GEN.py --out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X_15000_20000/GEN \
--maxEvents 100 --nJobs 5000 --queue short --globalTag 124X_mcRun3_2022_realistic_postEE_v1 --start_from 15000
python3 batchSubmitterMC_Step0_GEN.py --out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X_20000_25000/GEN \
--maxEvents 100 --nJobs 5000 --queue short --globalTag 124X_mcRun3_2022_realistic_postEE_v1 --start_from 20000 #(TO RESUBMIT)
'''

if __name__ == "__main__" :

    parser = OptionParser()    
    parser.add_option("--out",       dest="out",       type=str,            default=None,                            help="Output folder name")
    parser.add_option("--maxEvents", dest="maxEvents", type=int,            default=50,                              help="Number of events per job")
    parser.add_option("--nJobs",     dest="nJobs",     type=int,            default=1,                               help="Number of jobs")
    parser.add_option("--queue",     dest="queue",     type=str,            default='short',                         help="long or short queue")
    parser.add_option("--globalTag", dest="globalTag", type=str,            default='124X_mcRun3_2022_realistic_postEE_v1',   help="Which globalTag to use")
    parser.add_option("--start_from",dest="start_from",type=int,            default=0)
    parser.add_option("--no_exec",   dest="no_exec",   action='store_true', default=False)
    parser.add_option("--resubmit",  dest="resubmit",  action='store_true', default=False)
    (options, args) = parser.parse_args()

    os.system('mkdir -p '+options.out)

    resubmitting = 0

    starting_index = int(options.start_from)
    ending_index = starting_index + int(options.nJobs)
    print(starting_index, ending_index)
    for idx in range(starting_index, ending_index):

        outJobName  = options.out + '/job_' + str(idx) + '.sh'
        outLogName  = options.out + '/log_' + str(idx) + '.txt'
        outRootName = options.out + '/Ntuple_' + str(idx) + '.root'

        # random seed for MC production should every time we submit a new generation
        # it's obtained by summing current Y+M+D+H+M+S+job_number
        # now = datetime.now()
        # randseed = int(now.year) + int(now.month) + int(now.day) + int(now.hour) + int(now.minute) + int(now.second) + idx
        randseed = idx+1 # to be reproducible

        if options.resubmit:
            ListErrJobName = glob.glob(options.out + '/job_' + str(idx) + '.sh.e*')
            ListOutJobName = glob.glob(options.out + '/job_' + str(idx) + '.sh.o*')
            if len(ListErrJobName) > 0:
                if len(os.popen('grep "No such file or directory" '+ListErrJobName[-1]).read()) > 0:
                    print('resubmitting')
                    if not options.no_exec:
                        os.system('rm '+ListErrJobName[-1])
                        os.system('rm '+ListOutJobName[-1])
                    resubmitting = resubmitting + 1
                else:
                    continue
            else:
                continue

        cmsRun = "cmsRun MC_Step0_GEN_QCD_Pt30to500_cfg.py outputFile=file:"+outRootName
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
