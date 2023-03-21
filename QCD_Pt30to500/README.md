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
    --maxEvents 100 --nJobs 5000 --queue short --globalTag 124X_mcRun3_2022_realistic_postEE_v1

- Step 1

- Step 2

- Step 3 (L1Ntuples)

Changes:
L1TNtuples/interface/L1AnalysisRecoJetDataFormat.h
- add
    L74:
        ecalEnergy.clear();
        hcalEnergy.clear();
        HoE.clear();
        HoTot.clear();
        EoTot.clear();
        PtHCAL.clear();
        PtECAL.clear();
    L138:
        std::vector<float> ecalEnergy;
        std::vector<float> hcalEnergy;
        std::vector<float> HoE;
        std::vector<float> HoTot;
        std::vector<float> EoTot;
        std::vector<float> PtHCAL;
        std::vector<float> PtECAL;

L1TNtuples/plugins/L1JetRecoTreeProducer.cc
- add
    L41:
        #include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
    L365:
        float myHCALenergy = 0;
        float myECALenergy = 0;
        
        std::vector<reco::PFCandidatePtr> pfConstituents = it->getPFConstituents();
        for (const reco::PFCandidate& pf : pfConstituents) {
        myHCALenergy += pf.hcalEnergy();
        myECALenergy += pf.ecalEnergy();
        }
        jet_data->ecalEnergy.push_back(myECALenergy);
        jet_data->hcalEnergy.push_back(myHCALenergy);
        jet_data->HoE.push_back(myHCALenergy/myECALenergy);
        jet_data->HoTot.push_back(myHCALenergy/it->et());
        jet_data->EoTot.push_back(myECALenergy/it->et());
        jet_data->PtHCAL.push_back(it->et()-myECALenergy);
        jet_data->PtECAL.push_back(it->et()-myHCALenergy);

L1TNtuples/python/L1NtupleAOD_cff.py
- comment
    L21:
    # +l1MuonRecoTree

L1TNtuples/src/L1AnalysisEvent.cc
- comment from line L39 to L91
- change:
    L93:
    `event_.puWeight = 1.;`