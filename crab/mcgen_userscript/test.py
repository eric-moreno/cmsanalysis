import os
import sys
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import ROOT
import numpy as np 
ROOT.gROOT.SetBatch(True)

# load FWLite C++ libraries
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.FWLiteEnabler.enable()

# load FWlite python libraries
from DataFormats.FWLite import Handle, Events


class Collections(object):

    def __init__(self):
        self.__collections = {}

    def add(self, name, cppType, label):
        self.__collections[name] = {'handle': Handle(cppType), 'label': label,}

    def get(self, name, event):
        label = self.__collections[name]['label']
        handle = self.__collections[name]['handle']
        event.getByLabel(label,handle)
        return handle.product()


def process(events,**kwargs):
    maxEvents = kwargs.pop('maxEvents',-1)
    reportEvery = kwargs.pop('reportEvery',1000)

    collections = Collections()

    # AODSIM
    collections.add("genParticles",     "std::vector<reco::GenParticle>",                                       "genParticles")
    #collections.add("hgcEERecHits",     "edm::SortedCollection<HGCRecHit,edm::StrictWeakOrdering<HGCRecHit> >", ("HGCalRecHit", "HGCEERecHits",  "RECO"))
    #collections.add("hgcHEBRecHits",    "edm::SortedCollection<HGCRecHit,edm::StrictWeakOrdering<HGCRecHit> >", ("HGCalRecHit", "HGCHEBRecHits", "RECO"))
    #collections.add("hgcHEFRecHits",    "edm::SortedCollection<HGCRecHit,edm::StrictWeakOrdering<HGCRecHit> >", ("HGCalRecHit", "HGCHEFRecHits", "RECO"))
    #collections.add("hgcClusters",      "std::vector<reco::CaloCluster>",                                       "hgcalLayerClusters")
    #collections.add("hgcMultiClusters", "std::vector<reco::HGCalMultiCluster>",                                 "hgcalLayerClusters")
    #collections.add("hgcPFClusters",    "vector<reco::PFCluster>",                                              "particleFlowClusterHGCal")
    #collections.add("hgcPFRecHits",     "vector<reco::PFRecHit>",                                               ("particleFlowRecHitHGC", "Cleaned", "RECO"))

    H_pTs = []
    numEvents = events.size()
    if maxEvents>=0: numEvents = min(numEvents,maxEvents)
    for i,event in enumerate(events):
        if maxEvents>=0 and i>maxEvents: break
        if i%reportEvery==0: print 'Processing event {0}/{1}'.format(i+1,numEvents)

        aux = event.eventAuxiliary()
        run, lumi, evt = aux.run(), aux.luminosityBlock(), aux.event()
        print ':'.join([str(x) for x in [run,lumi,evt]])

        genParticles = collections.get('genParticles',event)

        print 'genParticles'
        for gp in genParticles:
	    #print('new particle')
	    #print(gp.numberOfMothers())
	    #print(gp.numberOfDaughters())
	    #H_pTs.append(gp.pt()) 
	    if gp.pdgId() == 25 and gp.mother().pdgId() == 25 and gp.numberOfDaughters() == 2 : 
		daughters = [gp.daughter(i).pdgId() for i in range(gp.numberOfDaughters())]
		if daughters.count(5) == 1 and daughters.count(-5) == 1: 
			H_pTs.append(gp.pt())
            #print '    ', gp.pt(), gp.eta(), gp.phi(), gp.energy(), gp.pdgId()
	#if i>5: break
    bins = np.linspace(0, 1000, 11)
    eraText=r'2016 (13 TeV)'
    f, ax = plt.subplots(figsize = (10,10))
    ax.hist(H_pTs, bins = bins, lw = 2, normed=False, histtype='step')
    ax.set_xlabel(r'$\mathrm{p_T}$', ha='right', x=1.0)
    ax.set_ylabel(r'Normalized scale ({})'.format('Higgs'), ha='right', y=1.0)
    ax.annotate(eraText, xy=(0.75, 1.015), xycoords='axes fraction', fontname='Helvetica', ha='left', 
	bbox={'facecolor':'white', 'edgecolor':'white', 'alpha':0, 'pad':13}, annotation_clip=False)
    ax.annotate('$\mathbf{CMS}$', xy=(0, 1.015), xycoords='axes fraction', fontname='Helvetica', fontsize=24, fontweight='bold', ha='left',
	bbox={'facecolor':'white', 'edgecolor':'white', 'alpha':0, 'pad':13}, annotation_clip=False)
    ax.annotate('$Simulation\ Open\ Data$', xy=(0.105, 1.015), xycoords='axes fraction', fontsize=18, fontstyle='italic', ha='left', annotation_clip=False)	
    f.savefig('Higgs_pThist' + '.png')



files = [
    "file://./HIG-RunIIFall18wmLHEGS-00732.root"
]

for i,f in enumerate(files):
    events = Events(f)
    process(events)
