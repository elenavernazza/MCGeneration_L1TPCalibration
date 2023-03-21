import os, glob
from datetime import datetime
from optparse import OptionParser

# Script to submit MC production
# ---------- Step 2 ----------
'''
python3 batchSubmitterMC_Step2_AOD.py --indir /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X/RAW \
--out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X/AOD \
--maxEvents -1 --queue short --globalTag 124X_mcRun3_2022_realistic_postEE_v1 #(DONE) 443+938=1381
python3 batchSubmitterMC_Step2_AOD.py --indir /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X_7000_10000/RAW \
--out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X_7000_10000/AOD \
--maxEvents -1 --queue short --globalTag 124X_mcRun3_2022_realistic_postEE_v1 #(DONE)
python3 batchSubmitterMC_Step2_AOD.py --indir /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X_15000_20000/RAW \
--out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X_15000_20000/AOD \
--maxEvents -1 --queue short --globalTag 124X_mcRun3_2022_realistic_postEE_v1
python3 batchSubmitterMC_Step2_AOD.py --indir /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X_20000_25000/RAW \
--out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X_20000_25000/AOD \
--maxEvents -1 --queue short --globalTag 124X_mcRun3_2022_realistic_postEE_v1
'''

if __name__ == "__main__" :

    parser = OptionParser()    
    parser.add_option("--indir",     dest="indir",     type=str,            default=None,                                       help="Input folder name")
    parser.add_option("--out",       dest="out",       type=str,            default=None,                                       help="Output folder name")
    parser.add_option("--maxEvents", dest="maxEvents", type=int,            default=-1,                                         help="Number of events per job")
    parser.add_option("--queue",     dest="queue",     type=str,            default='short',                                    help="long or short queue")
    parser.add_option("--globalTag", dest="globalTag", type=str,            default='124X_mcRun3_2022_realistic_postEE_v1',     help="Which globalTag to use")
    parser.add_option("--no_exec",   dest="no_exec",   action='store_true', default=False)
    parser.add_option("--resubmit",  dest="resubmit",  action='store_true', default=False)
    (options, args) = parser.parse_args()

    os.system('mkdir -p '+options.out)

    inRootNameList = glob.glob(options.indir+"/Ntuple_*.root")
    inRootNameList.sort()

    skipped = 0
    resubmitting = 0
    launched = 0

    for inRootName in inRootNameList:

        idx = inRootName.split(".root")[0].split("Ntuple")[1].split("_")[1]
        outJobName  = options.out + '/job_' + str(idx) + '.sh'
        outLogName  = options.out + '/log_' + str(idx) + '.txt'
        outRootName = options.out + '/Ntuple_' + str(idx) + '.root'

        PreviousStepLogName = options.indir + '/log_' + str(idx) + '.txt'
        # check if the previous step has finished
        if len(os.popen('grep "Time report complete in" '+PreviousStepLogName).read()) == 0:
            skipped = skipped + 1
            print('Skip')
            continue

        if options.resubmit:
            if os.path.isfile(outRootName):
                if len(os.popen('grep "Time report complete in" '+outLogName).read()) == 0:
                    resubmitting = resubmitting + 1
                else:
                    print('Done')
                    continue

        # if the outRootName already exists there is no need of resubmitting
        # but files not correctly closed (ex 99) have to be resubmitted
        # if os.path.isfile(outRootName):
        #     if len(os.popen('grep "Run 1, Event 2000," '+outLogName).read()) > 0:
        #         print("Skipping "+outRootName)
        #         skipped = skipped + 1
        #         continue

        # some of them were wrongly closed, it's not clear from the log but we notice from the nest step
        # NextStepLogName = options.indir.split('/GEN')[0] + '/L1Ntuples' + '/log_' + str(idx) + '.txt'
        # # print(NextStepLogName)
        # if os.path.isfile(NextStepLogName):
        #     if len(os.popen('grep "FileOpenError" '+NextStepLogName).read()) > 0:
        #         print('resubmitting')
        #         resubmitting = resubmitting + 1
        #     else:
        #         continue

        # random seed for MC production should every time we submit a new generation
        # it's obtained by summing current Y+M+D+H+M+S+job_number
        # now = datetime.now()
        # randseed = int(now.year) + int(now.month) + int(now.day) + int(now.hour) + int(now.minute) + int(now.second) + idx
        randseed = int(idx)+1 # to be reproducible

        cmsRun = "cmsRun MC_Step2_AOD_QCD_Pt30to500_cfg.py inputFiles=file:"+inRootName+" outputFile=file:"+outRootName
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
        if not options.no_exec: 
            os.system (command)
            launched = launched + 1 

    print("skipped = ",skipped)
    print("resubmitting = ",resubmitting)
    print("launched = ",launched)
