# MCGeneration_L1TPCalibration
MC generation for L1Trigger Primitives calibration

Steps are defined in this twiki
https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookGenIntro

- Step 0

Produce the GEN level Ntuples.
Select the CMSSW release according to the configuration you want to use. In this case 126X.

    cmsrel CMSSW_12_4_13
    cd CMSSW_12_4_13/src/
    cmsenv

    git clone git@github.com:cms-sw/genproductions.git genproductions Configuration/GenProduction/
    scram b -j 8

    git clone git@github.com:elenavernazza/MCGeneration_L1TPCalibration.git

    cd MCGeneration_L1TPCalibration/QCD_Pt30to500
    cmsenv
    python3 batchSubmitterMC_Step0_GEN.py \
    --start_from <next consecutive seed> \
    --out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV_124X_<add where you start from>/GEN \
    --maxEvents 180 --nJobs 6000 --queue short --globalTag 124X_mcRun3_2022_realistic_postEE_v1