# MCGeneration_L1TPCalibration
MC generation for L1Trigger Primitives calibration

Steps are defined in this twiki
https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookGenIntro

- Step 0

Produce the GEN level Ntuples.
Select the CMSSW release according to the configuration you want to use. In this case 126X.

    ```js
    cmsrel CMSSW_12_6_0
    cd CMSSW_12_6_0/src/
    cmsenv
    ```

    ```js
    git clone git@github.com:cms-sw/genproductions.git genproductions Configuration/GenProduction/
    scram b -j 8
    ```

If you need to generate with a different configuration, get the fragment:

    ```
    curl -s --insecure https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_fragment/TSG-Run3Summer21GS-00003 --retry 2 --create-dirs -o Configuration/GenProduction/python/TSG-Run3Summer21GS-00003-fragment.py
    ```

produce the configuration file:

    ```js
    cmsDriver.py Configuration/GenProduction/python/TSG-Run3Summer21GS-00003_1_cfg.py --python_filename TSG-Run3Summer21GS-00003_1_cfg.py --eventcontent RAWSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM --fileout file:Ntuple_0_Step0.root --conditions 126X_mcRun3_2023_forPU65_v1 --beamspot Realistic25ns13p6TeVEarly2022Collision --step GEN,SIM --geometry DB:Extended --era Run3 --no_exec --mc -n 1000
    ```

and run a test with:

    ```js
    cmsRun TSG-Run3Summer21GS-00003_1_cfg.py
    ```

This part has already been run and the configuration file you need is 'MC_Step0_GEN_QCD_Pt30to500_cfg.py', so you only need to run the submitter.
Some configurations inside have been modified, mainly pthat min and max and the options to configure the full sample submission on tier3.

    ```js
    python3 batchSubmitterMC_Step0_GEN.py --out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt30_500_TuneCP5_13p6TeV/GEN \
    --maxEvents 2000 --nJobs 1000 --queue long --globalTag 126X_mcRun3_2023_forPU65_v1
    ```

The MC production takes on average 1 minute per event.

- Step 1

Produce the RAW level Ntuples.
If you need to generate with a different configuration, get one with:

    ```js
    cmsDriver.py step1 --python_filename Step_1_TSG-Run3Summer21GS-00003_1_cfg.py --eventcontent RAWSIM --pileup NoPileUp --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-RAW --fileout file:Ntuple_0_Step1.root --conditions 126X_mcRun3_2023_forPU65_v1 --step DIGI,L1,DIGI2RAW --nThreads 4 --geometry DB:Extended --filein file:Ntuple_0_Step0.root --era Run3 --no_exec --mc -n -1
    ```

and run a test with:

    ```js
    cmsRun Step_1_TSG-Run3Summer21GS-00003_1_cfg.py
    ```

This part has already been run and the configuration file you need is 'MC_Step1_RAW_QCD_Pt30to500_cfg.py', so you only need to run the submitter.

    ```js
    python3 batchSubmitterMC_Step1_RAW.py --indir /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt20_500_TuneCP5_13p6TeV/GEN \
    --out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt20_500_TuneCP5_13p6TeV/RAW \
    --maxEvents -1 --queue short --globalTag 126X_mcRun3_2023_forPU65_v1
    ```

- Step 2

Produce L1Ntuples.
You can use this repository https://github.com/jonamotta/CaloL1CalibrationProducer

    ```js
    cmsrel CMSSW_13_0_0_pre2
    cd CMSSW_13_0_0_pre2/src
    cmsenv
    git cms-init
    git remote add cms-l1t-offline git@github.com:cms-l1t-offline/cmssw.git
    git fetch cms-l1t-offline l1t-integration-CMSSW_13_0_0_pre2
    git cms-merge-topic -u cms-l1t-offline:l1t-integration-v142
    git clone https://github.com/cms-l1t-offline/L1Trigger-L1TCalorimeter.git L1Trigger/L1TCalorimeter/data
    git clone git@github.com:jonamotta/calol1calibrationproducer.git
    git cms-checkdeps -A -a

    scram b -j 12

    cd calol1calibrationproducer/L1NtupleLauncher

    python3 batchSubmitterMC_L1Ntuple.py --indir /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt20_500_TuneCP5_13p6TeV/RAW \
    --out /data_CMS/cms/motta/CaloL1calibraton/PrivateMC/QCD_Pt20_500_TuneCP5_13p6TeV/L1Ntuples \
    --maxEvents -1 --queue short --globalTag 126X_mcRun3_2023_forPU65_v1 --caloParams caloParams_2022_v0_6_cfi
    ```

