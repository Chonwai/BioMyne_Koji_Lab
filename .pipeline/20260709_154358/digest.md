# BioMyne Koji — Intelligence Digest
**Date:** 2026-07-09 17:43:15
**Run ID:** 6a77e04a-bc02-4f03-a07a-cb8177f3b6a5
**Sources:** 11 | **Articles:** 85 | **Errors:** 0

---
### Phthalate Exposure Induces Inflammatory Signaling and Suppresses Mitochondrial Function in Marine Mammal and Human Cells
**Priority:** high | **Tags:** Toxicology, Marine Biology, Environmental Health, Mitochondrial Function, Ecotoxicology
**URL:** https://www.biorxiv.org/content/10.64898/2026.02.09.704935v2

A research team at UC Berkeley led by Elizabeth Piotrowski and Jose Pablo Vazquez-Medina investigated how monoethylhexyl phthalate (MEHP)—a common plasticizer metabolite—alters gene expression and mitochondrial bioenergetics in primary fibroblasts from northern elephant seals, common dolphins, and humans. Using RNA-seq, extracellular flux assays, and 3D confocal microscopy, they found MEHP triggered no cytotoxicity but produced striking species-specific responses. Human cells showed the strongest transcriptional shift: upregulated detoxification, antioxidant, and inflammatory pathways while downregulating lipid metabolism, with reduced mitochondrial respiration, increased fragmentation, and a metabolic reprogramming toward glycolysis. Elephant seal cells maintained respiration, delayed glycolytic shifts, and upregulated antioxidant, immune, and trafficking genes despite mitochondrial fragmentation. Dolphins showed minimal transcriptional changes but dose-dependent declines in both respiration and glycolysis at the lowest concentration while preserving structural integrity via stress and hypoxia gene induction. The findings reveal fundamental differences in species-level susceptibility to plastic-derived contaminants and underscore the need for marine-mammal-specific ecotoxicological risk assessments.

---

### A Hybrid ABM-PDE Framework for Real-World Infectious Disease Simulations
**Priority:** low | **Tags:** computational epidemiology, infectious disease modeling
**URL:** https://arxiv.org/abs/2504.08430

Researchers Kristina Kehrer and Tim O. F. Conrad from the multiagent systems / applied mathematics community present a hybrid computational framework that couples an Agent-Based Model (ABM) with a partial differential equation (PDE) model to simulate spatial spread of infectious diseases using a seven-state compartmental structure. The approach aims to reduce the computational complexity of full ABMs by splitting the population: individuals follow agent-level detail in one domain, while bulk population dynamics are approximated via density-based PDEs coupled across an interface. In practice the coupling removes agents entering the PDE zone (representing them as density contributions) and generates surplus new agents from mobile phone–derived mobility data within the PDE domain. The framework was validated on real-world mobility and infection data for the Berlin-Brandenburg region of Germany, showing it captures core epidemic dynamics with smaller errors across both 25% and 100% population subsamples while significantly reducing simulation runtime compared to standalone ABM approaches.

---

### FDA approves AstraZeneca’s baxdrostat for certain patient...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/fda-approves-astrazenecas-baxdrostat-for-certain-patients-with-hypertension

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/fda-approves-astrazenecas-baxdrostat-for-certain-patients-with-hypertension/&title=FDA%20approves%20AstraZeneca%E2%80%99s%20baxdrostat%20for%20certain%20patients%20with%20hypertension&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=FDA%20approves%20AstraZeneca%E2%80%99s%20baxdrostat%20for%20certain%20patients%20with%20hypert

---

### Experimentally accessible measurement of irreversibility in stochastic systems by categorizing single-molecule displacements
**Priority:** low | **Tags:** biophysics, single-molecule biophysics, protein folding, statistical mechanics
**URL:** https://arxiv.org/abs/2511.09183

A theoretical biophysics study by Alvaro Lanza, Inés Martinez-Martín, Rafael Tapia-Rojo, and Stefano Bo introduces a model-free method to quantify irreversibility and dissipation in stochastic Langevin systems using only single-molecule displacement observations. The approach categorizes displacements by initial and final position, allowing precise measurement of irreversibility without knowing the specific forces or fluctuation magnitudes acting on the system. Validation is performed on single-molecule force spectroscopy experiments of proteins subject to force ramps, demonstrating that irreversibility sensitivity reveals detailed features of the energy landscape underlying protein folding dynamics. The authors show a conditional fluctuation theorem relates their estimate to entropy production at short times, and for stationary protocols it provides a lower bound on average entropy production. This work offers a practical framework for experimentalists studying non-equilibrium biomolecular processes without requiring full force characterization.

---

### Activation in Vesicle-Mediated Signaling Shaped by Batch Arrival Statistics
**Priority:** low | **Tags:** systems-biology, computational-biophysics
**URL:** https://arxiv.org/abs/2605.06456

Researchers Jan Hauke, Julian B. Voits and Ulrich S. Schwarz at Heidelberg University derive an exact solution for the full time-dependent probability distribution of vesicle-mediated secretion using generating functions and a recursion relation in a general batch arrival degradation model. The framework enables analysis of first-passage times to concentration thresholds representing downstream activation in cellular communication processes such as neurotransmission and hormone release. Key finding: activation kinetics are not determined by mean dynamics alone but depend sensitively on the temporal statistics of arrival events, batch-size variability, and the rate of clearance/degradation. Different arrival processes with identical mean rates can produce qualitatively distinct first-passage behavior, revealing an important role for time-asymmetric fluctuations in signaling thresholds. The authors also discuss extensions incorporating vesicle depletion effects. This work provides a tractable theoretical link between stochastic release dynamics and activation timing that could inform modeling of drug delivery systems and biocomputing approaches built on engineered vesicle-based circuits.

---

### Can Tabular In-Context Learners Generalize to Biomolecular Property Prediction?
**Priority:** high | **Tags:** drug-discovery, bioinformatics
**URL:** https://arxiv.org/abs/2606.31126

This paper evaluates whether tabular in-context learning models—specifically TabPFN and TabICL, which are pretrained on synthetic tables from random causal graphs—can effectively predict biomolecular properties from limited labeled data. The authors find that coupling these models with ESM Cambrian representations achieves or exceeds state-of-the-art results on ProteinGym protein fitness regression tasks and outperforms task-specific supervised regressors on a diverse esterase catalytic activity dataset, addressing the central bottleneck in protein engineering and small-molecule design. For small-molecule classification using ECFP/RDKit descriptors across multiple benchmarks (TDC ADMET, MoleculeNet, FS-Mol, DrugOOD), no single predictor-representation pairing dominates universally but several remain competitive with task-specific state-of-the-art approaches. The key finding is that tabular foundation models serve as strong biomolecular predictors when paired with expressive pretrained representations, challenging the assumption that their synthetic causal-graph inductive bias has no transfer to biological data. This matters for biotech operators and investors because few-shot prediction capability could dramatically reduce the cost and time of experimental screening for enzyme engineering and drug candidate screening.

---

### An Investigation of the Channel Capacity of Bacterial Chemotactic Sensors for Low Chemoattractant Concentrations
**Priority:** low | **Tags:** synthetic-biology, systems-biology
**URL:** https://arxiv.org/abs/2601.02446

Theoretical biophysics paper by Ziyi Cui and Sarah Marzen analyzing the static sensing limits of mixed Tar/Tsr chemoreceptor clusters in Escherichia coli using a heterogeneous Monod-Wyman-Changeux (MWC) model. The authors perform a seven-dimensional parameter sweep to compute channel capacity, dynamic range, and effective Hill coefficient under conditions where cells experience persistently low chemoattractant concentrations without needing adaptation to new baselines. Key findings include upper bounds on trajectory mutual information rate, a tight quantitative connection between channel capacity and dynamic range, and a closed-form ceiling equation depending only on receptor baseline activity that all wild-type and mutant strains achieve within a few percent. The work establishes fundamental physical limits on bacterial sensory performance, paralleling prior work on natural scene statistics in visual systems. This is basic research with no immediate commercial applications or named entities.

---

### Feynman Kac Reweighted Schr\u00f6dinger Bridge Matching for Surface-Based Tau PET Harmonization
**Priority:** medium | **Tags:** AI/ML diagnostics, neurodegenerative disease, medical imaging
**URL:** https://arxiv.org/abs/2606.17420

Researchers Jianwei Zhang, Xinyu Nie, Jiaxin Yue, and Yonggang Shi propose FKRSBM (Feynman Kac Reweighted Schr\u00f6dinger Bridge Matching), a novel surface-based computational framework for harmonizing tau PET imaging across different radiotracers used in Alzheimer's disease research. The method addresses a critical gap: as the field adopts multiple tau PET tracers (AV-1451, PI-2620, MK-6240) with differing binding behaviors, previous harmonization approaches like CenTauR cannot adequately account for regional heterogeneity in tau pathology distribution. FKRSBM leverages Schr\u00f6dinger Bridge matching to learn direct stochastic transport between tracer domains without Gaussian-prior assumptions, introduces a Feynman-Kac reweighted endpoint penalty to favor biologically consistent bridge pairings based on shared tau pathology status, and employs spherical convolutional networks for vertex-level harmonization on cortical surface meshes. Evaluated on two large datasets (AV-1451 n=1,480 subjects; PI-2620 n=2,458 subjects), the method outperformed ComBat, CycleGAN, Diffusion Models, and unregularized Schr\u00f6dinger Bridge models in subgroup-level alignment, tau-positivity consistency, diagnostic classification, and preservation of subject-specific cortical topography. For biotech operators running multi-tracer PET studies across trials, this method could reduce scanner/tracer batch effects and improve cross-study comparability as a pre-processing step before statistical analysis.

---

### Linking sugar sensing to immunity in plants via O-glycosylation
**Priority:** medium | **Tags:** plant biology, immunology, crop science, synthetic biology
**URL:** https://www.biorxiv.org/content/10.64898/2026.05.04.722566v3

Researchers at the Carnegie Institution for Science (Stanford) and Stanford University demonstrate that O-glycosylation of pattern-triggered immunity (PTI) MAP kinase kinases MKK4 and MKK5 acts as a metabolic rheostat linking plant sugar availability to immune responses. Under sugar-replete conditions, MKK4/5 are glycosylated with O-GlcNAc and O-fucose on their activation loops, which blocks phosphorylation by upstream kinases and suppresses PTI signaling. Pathogen infection or sugar starvation reduces this O-glycosylation, releasing the brake on immunity; these effects are reversed by GDP-fucose treatment, confirming the metabolic mechanism. Chemical inhibition of O-fucosylation enhanced disease resistance in both Arabidopsis and tomato models. The work establishes a novel principle—metabolic sensing via O-glycosylation directly tunes plant immune output—which could inform engineering of crops with improved disease resistance while managing growth-yield tradeoffs.

---

### A Lake Charr Pangenome Reveals Highly Conserved Ohnologs as Drivers of Phenotypic Diversity
**Priority:** medium | **Tags:** genomics, evolutionary biology, conservation genetics, pangenome
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.03.729964v1

A multi-institutional team led by the University at Buffalo constructed a Lake Charr (Salvelinus namaycush) pangenome using 31 chromosome-level assemblies from diverse Great Lakes populations, characterizing 189,555 structural variants in fish carrying ~10% of genes retained as conserved polyploid duplicates following the Salmonid-Specific Fourth Round Whole-Genome Duplication. The study found that while such structurally variant genes are significantly less likely to affect ohnolog pairs retained as sequence-conserved duplicated pairs, those structural variants that do target conserved Ohnologs serve as potent drivers of adaptive evolution. Specifically, the authors identified a putative 938-kb interchromosomal translocation containing 25 genes with highly conserved Ohnologs in an untranslocated paralogous block, appearing to have facilitated divergence in ankrd11 and hp genes linked to craniofacial morphology and lipid metabolism in sympatric Lake Superior morphs. The work challenges the assumption that gene redundancy from whole-genome duplication renders ohnologs functionally redundant, revealing them instead as active reservoirs for adaptive change on contemporary evolutionary timescales. Funded by the Great Lakes Restoration Initiative, Great Lakes Research Consortium, and the University at Buffalo.

---

### Pulmonary delivery of antigen-enhanced BCG overcomes safety barriers in immunocompromised hosts and protects against TB in the absence of adaptive immunity
**Priority:** high | **Tags:** TB vaccine, recombinant BCG, trained immunity, immunology, pulmonary delivery
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.05.736631v1

Researchers at James Cook University and Institut Pasteur demonstrate that pulmonary delivery of recombinant BCG (rBCG) strains—BCG::RD1 and BCG::ESAT6-PE25SS—that secrete the Mycobacterium tuberculosis effector ESAT-6 overcomes safety concerns previously identified in intravenous SCID mouse models. Pulmonary administration was markedly better tolerated, improved survival, and reduced systemic dissemination and brain pathology in severely immunocompromised mice compared with intravenous routes. In wild-type, type 2 diabetic, and adaptive immunity-deficient Rag1-/Rag2-/Il2rg-/ mice, pulmonary rBCG vaccination conferred superior protective efficacy against aerosol Mtb challenge, with BCG::RD1 showing the strongest adaptive immunity-independent protection. Mechanistically, lung rBCG vaccination promoted innate immune activation in the lungs, expanded myeloid-biased progenitors in bone marrow, and enhanced antimycobacterial activity of macrophages consistent with a trained innate immunity phenotype. This challenges prior safety paradigms for ESAT-6-secreting rBCG and provides preclinical evidence for an inhalational BCG vaccine strategy that could protect TB-naive immunocompromised populations—critical for high-burden settings where HIV co-infection drives TB disease.

---

### FDA approves Orca Bio’s cell therapy to improve transplan...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/fda-approves-orca-bios-cell-therapy-to-improve-transplant-outcomes

![](https://endpoints.news/wp-content/uploads/2026/07/Nate-Fernhoff-Orca-Bio-feature.jpg) Nate Fernhoff, Orca Bio CEO [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/fda-approves-orca-bios-cell-therapy-to-improve-transplant-outcomes/&title=FDA%20approves%20Orca%20Bio%E2%80%99s%20cell%20therapy%20to%20improve%20transplant%20outcomes&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/twe

---

### Clinical Trial and Ontology-Derived Positive and Negative Benchmark Datasets for Drug Repurposing Across Rare Diseases
**Priority:** medium | **Tags:** drug repurposing, rare diseases, benchmark datasets, graph machine learning, computational biology
**URL:** https://www.biorxiv.org/content/10.64898/2026.06.15.732135v2

Researchers from Alexion AstraZeneca Rare Disease, BioClarity AI, AstraZeneca, and Northeastern University/Santa Fe Institute released two open benchmark datasets for evaluating drug repurposing models in rare diseases. IxIDN is a positive benchmark derived from pharmaceutical clinical trial data, connecting disease pairs that received the same drug via 574 rare diseases and 5,336 edges representing real indication-expansion decisions. ORDON provides a biology-aware negative benchmark with 793 rare diseases and 5,000 edges of maximally distant disease pairs from the Orphanet Rare Disease Ontology, serving as hard negatives. Together these resources enable rigorous testing of Disease-Disease Association Learning (DDAL) models for cross-evidence generalization from clinical trials to ontology structures. The data is publicly available on Zenodo at zenodo.org/records/20694608.

---

### Target site and guide RNA multiplexing architecture shape homing gene drive efficiency in Drosophila suzukii
**Priority:** medium | **Tags:** gene drive, CRISPR-Cas9, pest control, synthetic biology
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.03.736304v2

Researchers from North Carolina State University and Peking University investigated how CRISPR/Cas9 homing gene drive design choices affect efficiency in Drosophila suzukii, a globally invasive pest of soft-skinned fruits that causes significant agricultural damage. Building on prior work achieving 94-99% inheritance targeting the doublesex female-specific exon, the team tested single-, two-, and three-guide RNA configurations to understand how target site selection and multiplexing architecture influence drive performance. Key findings include a splice junction-targeting gRNA supported high male inheritance but showed reduced female efficiency; combining it with a coding-sequence guide further degraded performance in females; tRNA-linked and independent-promoter configurations performed comparably at two guides; whereas a three-tRNA-guide construct produced consistently low inheritance across both sexes, indicating reduced Cas9 cleavage activity. The work demonstrates that target site choice, multiplexing strategy, and sex-specific germline environments all critically shape gene drive efficiency—providing design guidelines relevant to operators in agricultural biotech development.

---

### PINPOINT: Protease INhibitor PredictiOn at the plant-pathogen INTerface using protein language models and structural modeling
**Priority:** medium | **Tags:** computational-biology, plant-pathogen-interaction, protein-language-models, effector-discovery
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.05.736646v1

Researchers from BITS Pilani and IIT Jodhpur introduced PINPOINT, a computational pipeline that predicts small secreted proteins (SSPs) with protease-inhibitory function in plant-fungal interactions using protein language models and structural modeling. Unlike traditional sequence-dependent database searches, PINPOINT can identify SSPs that lack annotated inhibitor domains but retain protease-inhibitory activity through sequence-unrelated but structurally similar (SUSS) effectors. It combines fine-tuned protein language model classifiers, a structure-aware autoencoder, effector prediction, and AlphaFold Multimer (AFM) screening against candidate apoplastic cysteine and serine proteases. The team validated the platform using SSPs from Macrophomina phaseolina, the fungal pathogen causing charcoal rot of soybean and other crops. The tool is publicly available as an interactive Google Colab notebook at a GitHub repository, enabling researchers to pre-filter candidates for novel effector discovery in cross-kingdom plant-microbe interaction studies.

---

### Protein hydration and druggability
**Priority:** medium | **Tags:** drug discovery, computational biophysics, protein structure, ligand binding, molecular dynamics
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.06.736750v1

Researchers at the Petersburg Nuclear Physics Institute (Kurchatov Institute) propose a novel pre-Ligand approach to assess target protein druggability based on low-entropy water (LEW) content in the first hydration layer, rather than traditional accessible surface area (ASA) calculations. Analyzing 65 evolutionarily and structurally unrelated human enzymes, they demonstrate that LEW content is systematically higher in active sites than in other surface regions including inactive cavities—contradicting conventional ASA-based assumptions. The authors provide optimal criteria and a step-by-step procedure for identifying protein ligand binding sites using this framework, enabling medicinal suitability evaluation prior to any ligand design. They also validate molecular dynamics water simulations against experimental Raman spectroscopy data, comparing three widely-used water models (TIP3P, OPC3, TIP5P) for hydrogen bond network analysis.

---

### The Encyclopedia of DNA Elements
**Priority:** low | **Tags:** Genomics, Reference Database
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.06.731365v1

The ENCODE Project Consortium has released an expanded reference map of gene regulatory function covering more than 16,000 genome-wide experiments across primary human cells and tissues. The new ENCODE catalog identifies approximately 5.3 million DNase I hypersensitive sites delineating chromatin-accessible regulatory elements, adds roughly 18,000 novel long noncoding RNA genes and 150,000 novel transcript isoforms, and maps physical interactions between regulatory elements and their target genes across more than 100 human tissues at up to 10 base-pair resolution. Parallel studies in mice extend the resource into postnatal developmental maps of gene regulation. The work provides a foundational reference layer for interpreting non-coding genetic variation, designing functional genomics experiments, and supporting targeted drug discovery programs built on chromatin biology. Multiple contributing authors hold equity or advisory positions at leading biotech and pharma companies, underscoring ENCODE's utility as shared technical infrastructure.

---

### Conserved herpesvirus protein kinase (CHPK)-mediated phosphorylation of viral proteins associated with nucleocytoplasmic trafficking during natural infection
**Priority:** low | **Tags:** virology, herpesvirus, phosphoproteomics, viral pathogenesis, poultry science
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.07.737029v1

Researchers at the University of Illinois and US National Poultry Research Laboratory investigated how the conserved herpesvirus protein kinase (CHPK) directs Marek's disease virus (MDV) infection in chickens, combining RNA-seq with mass spectrometry-based phosphoproteomics. They compared wild-type MDV against a CHPK-null mutant across two tissue types: spleen and feather follicle epithelial skin cells from infected chickens. RNA-seq revealed minimal transcriptional differences attributable to CHPK status, but phosphoproteomics uncovered 21 differentially phosphorylated viral proteins whose serine/threonine residues map near predicted nuclear localization and nuclear export signals. Functional validation confirmed these phosphorylation events actively govern nucleocytoplasmic shuttling of the viral proteins. The findings demonstrate that CHPK's essential role in horizontal transmission is mediated primarily through post-translational modifications rather than transcriptional reprogramming, with implications for antiviral strategies targeting herpesvirus protein trafficking.

---

### A family of RRM-1 RNA binding proteins enables cold adaptation and environmental resilience in Bacteroides
**Priority:** medium | **Tags:** microbiology, RNA biology, cold stress adaptation, Bacteroides, post-transcriptional regulation
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.07.737135v1

Researchers Hyelan Lee, Anubhav Basu, and Carin K. Vanderpool at the University of Illinois Urbana-Champaign and University of Minnesota demonstrate that RRM-1 domain-containing RNA binding proteins (RBPs) serve as central regulators of cold stress adaptation in Bacteroides, a gut-associated bacterial genus. Simultaneous deletion of all rbp genes across multiple Bacteroides species produces a consistent cold-sensitive growth defect, revealing conserved functional redundancy among these typically eukaryotic-looking proteins. The study further shows that RBPs act cooperatively with BT1884, the sole canonical cold shock protein in Bacteroides thetaiotaomicron; combined loss of both systems causes severe synthetic cold sensitivity. Critically, rbp-deficient strains show impaired survival under combined cold and oxidative stress—mimicking the conditions Bacteroides encounters during host-to-host transmission—suggesting these RBPs are essential for bacterial environmental resilience between hosts.

---

### Identification of Viral and Cellular Proteins in Proximity to the HSV-2 pUL16 Tegument Protein in Infected Cells
**Priority:** low | **Tags:** virology, herpes simplex virus, protein-protein interactions, host-pathogen biology
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.07.737067v1

Researchers at Queen's University used BioID proximity labeling to map the interactome of HSV-2 pUL16, an essential tegument protein during human keratinocyte infection. Comparing pUL16-binding partners against those of its known partner pUL21, they identified proteins shared versus unique to each complex. A key finding: pUL16-pUL21 interactions appear to regulate which isoform of protein phosphatase 1 (PP1) is recruited to substrates, thereby controlling dephosphorylation specificity during HSV infection. The study provides a molecular map of pUL16’s functional scope in infected cells for the first time.

---

### Programmable control of bacterial operons with a single Cas13 RNA effector
**Priority:** high | **Tags:** synthetic biology, CRISPR-Cas, bacterial engineering
**URL:** https://www.nature.com/articles/s41587-026-03159-4

A Nature Biotechnology perspective piece by Tong et al. introduces the SONAR system, which uses a single engineered Cas13d effector to enable RNA-level control of bacterial operons through crRNA design alone. The atnCas13d-IF3 fusion can switch between transcript degradation, translation inhibition, and translation activation by adjusting only the guide RNA sequence—an advance over approaches requiring separate effectors for each modality. This consolidation is significant because polar effects in polycistronic operons have long limited combinatorial metabolic-engineering efforts; achieving multiple regulatory outputs from one effector simplifies design substantially. The work builds on a growing literature of high-fidelity Cas13 variants, dCas13-based repression schemes, and CRISPR-Cas13d eukaryotic studies now brought together in a unified bacterial platform.

---

### Attenuated Cas13d variants enable tunable, multiplexed RNA regulation in Escherichia coli
**Priority:** high | **Tags:** CRISPR-Cas13, synthetic biology, metabolic engineering
**URL:** https://www.nature.com/articles/s41587-026-03160-x

Researchers at Shanghai Jiao Tong University developed attenuated Cas13d (atnCas13d) variants through rational protein engineering targeting truncation of flexible regions, thereby reducing the inherent cytotoxicity and collateral cleavage that have hindered widespread use of Cas13-based RNA effectors in bacteria. The engineered system demonstrated a 2.2-fold improvement in growth optical density compared with wild-type Cas13d while maintaining effective transcript knockdown. By introducing proximal mismatches at the 5’ end of CRISPR RNA spacers, the team achieved functional switching between three modes: translation inhibition, polycistronic mRNA degradation, and IF3-fusion-based translation-level CRISPR activation (RNAa). The system was validated with programmable, orthogonal, multiplexed regulation of individual genes within polycistronic mRNAs and synthetic circuits. Application to lycopene biosynthesis optimization in E. coli demonstrated robust pathway rewiring and improved yields alongside fine-tuned modulation of essential and competing metabolic pathways.

---

### Self-organization from multicellularity to morphogenesis: principles and applications in regenerative strategies
**Priority:** medium | **Tags:** stem-cell biotechnology, embryo models, self-organization
**URL:** https://www.nature.com/articles/s41587-026-03161-w

This Perspective piece, authored by researchers at Zernicka-Goetz Lab including Maithem Al-Hariri and Kraser from Cambridge, traces cellular self-organization from evolutionary origins through biomechanical inevitability to regenerative medicine applications. The paper argues that multicellular coordination emerged as an evolutionary necessity driven by physical constraints like oxygen and nutrient transport, which generate collective behaviors such as cavitation, folding, and branching. These behaviors couple mechanics, signaling pathways, and gene regulation to build tissues with spatiotemporal precision through iterative layering of simple rules. Stem cell-derived models of embryogenesis are making these principles experimentally tractable, revealing both canonical developmental routes and alternative trajectories that expose bottlenecks and failure modes. The authors argue that decoding these morphogenic rules will enable rational engineering of living tissue architecture, though the piece remains theoretical rather than reporting specific experimental results.

---

### Structural motif search across the protein universe with Folddisco
**Priority:** medium | **Tags:** structural biology, protein engineering, bioinformatics tools
**URL:** https://www.nature.com/articles/s41587-026-03162-9

Researchers at Seoul National University (Hyunbin Kim, Rachel Seongeun Kim, Milot Mirdita, Jaewon Yoon, Martin Steinegger) have developed Folddisco, a computational tool that dramatically accelerates the detection of similar protein structural motifs within large protein structure databases. The tool uses an index of position-independent geometric features—including side-chain orientation—combined with a rarity-based (IDF-style) scoring system. Benchmarks show Folddisco is 20-fold faster in query speed and fourfold more storage-efficient than existing methods, while improving accuracy across the board. Published in June 2026 in Nature Biotechnology, this work follows the group's prior Foldseek publication (van Kempen et al., Nat. Biotechnol. 2024) and extends the MMseqs/Foldseek ecosystem for structural bioinformatics. Folddisco is freely available as GPLv3 open-source software via https://folddisco.foldseek.com/ along with a webserver, precomputed databases, and benchmark data on Zenodo.

---

### Artificial intelligence in drug discovery
**Priority:** medium | **Tags:** AI-drug-discovery, patents, intellectual-property
**URL:** https://www.nature.com/articles/s41587-026-03163-8

Nature Biotechnology published a perspective on June 16, 2026 covering recent patents related to methods and systems for applying artificial intelligence in drug discovery. The article surveys intellectual property developments at the intersection of AI and pharmaceutical research, mapping the patent landscape that defines how computational approaches are being protected and commercialized. For biotech operators, this provides a window into which AI methodologies firms are treating as proprietary competitive assets. The piece signals continued maturation of AI-driven drug discovery from an experimental capability toward a heavily patented, commercially defended domain.

---

### Reply to 'Methodological concerns and a lack of evidence for reforming regulatory exclusivities for pharmaceuticals'
**Priority:** low | **Tags:** pharmaceutical policy, regulatory exclusivity, Hatch-Waxman
**URL:** https://www.nature.com/articles/s41587-026-03164-7

Robin Feldman, Gideon Schor, and Ramy Alsaffar (University of California College of the Law, San Francisco) respond to a critical letter by K.M.L. Acri published in Nature Biotechnology that raised methodological concerns about their 2025 paper on the New Clinical Investigation (NCI) exclusivity provision under Hatch-Waxman. The authors argue Acri's rebuttal misunderstood both the study's goals and its conclusions, overstated their claims, and ignored the majority of the paper's results by falsely framing the work as resting on a single ancillary finding near the end. Their original 2025 research examines the outsized role and real-world impact of the NCI exclusivity compared to expectations from the Hatch-Waxman enactment history, including historical concerns raised by then-Representative Albert Gore Jr. that the exclusivity was a last-minute giveaway to a minority of industry members. The piece is significant for biotech operators navigating orphan drug exclusivity and pharmaceutical policy/regulatory strategy given its focus on one of the key regulatory exclusivity mechanisms in U.S. drug development.

---

### Methodological concerns and a lack of evidence for reforming regulatory exclusivities for pharmaceuticals
**Priority:** medium | **Tags:** drug-pricing, regulatory-exclusivity, pharmaceutical-policy
**URL:** https://www.nature.com/articles/s41587-026-03165-6

Kristina Acri of Colorado College publishes a methodological critique in Nature Biotechnology of a prior paper by Feldman, Schor and Alsaffar (Nat. Biotechnol. 43, 857–862, 2025) on New Clinical Investigation (NCI) exclusivity in the pharmaceutical sector. The Feldman study analyzed drugs from the 2019 Medicare Part D and Medicaid formularies, identifying 236 qualifying drugs of which 176 carried post-patent exclusities—with NCI comprising 70.5% of exclusivities expiring after core patents. Acri contends the data do not substantiate the claim that NCI exclusivity is a major driver of rising drug prices or stalled generic competition, nor does it justify proposed reform mechanisms such as capping the number of regulatory exclusivities per company or drug.

---

### Experiment-guided AlphaFold3 resolves measurement-consistent protein ensembles
**Priority:** high | **Tags:** structural biology, AI/ML, drug discovery
**URL:** https://www.nature.com/articles/s41587-026-03166-5

Researchers have modified AlphaFold3 to generate experimentally grounded structural ensembles rather than single static structures, using guidance terms derived from NMR spectroscopy data (NOE distance restraints and order parameters), X-ray crystallographic electron density maps, and cryo-EM electrostatic potential maps injected during the model reverse-diffusion sampling. Tested on ubiquitin as an NMR benchmark, NOE-guided AlphaFold3 reduced pairwise distance constraint violations in 70 of 91 cases (approximately 77%) compared to unguided AlphaFold3 and outperformed deposited PDB ensembles. The method also recovers alternate conformations, fills missing electron density regions, and resolves amyloid fibril structures that AlphaFold3 entirely mispredicts at the dimerization interface. Joint guidance combining cryo-EM, NMR and dihedral angle constraints on a RIPK3 human amyloid fibril produces further improvements. The authors demonstrate computational efficiency (minutes per target on H100 GPUs versus days of traditional molecular dynamics) and compare against BioEmu, AlphaFlow, AFCluster and ProteinEBM energy-based models. Published in Nature Biotechnology using Protenix, ByteDance AML's open-source PyTorch reimplementation of AlphaFold3, the work reframes diffuse predictors as sequence-conditioned priors steerable by experimental evidence to yield compact conformational ensembles consistent with measurements across multiple modalities.

---

### Author Correction: RIP-PEN-seq identifies a class of kink-turn RNAs as splicing regulators
**Priority:** low | **Tags:** RNA biology, splicing regulation, high-throughput screening
**URL:** https://www.nature.com/articles/s41587-026-03167-4

This is an author correction to a 2023 Nature Biotechnology paper published by researchers at Sun Yat-sen University and the Beckman Research Institute of City of Hope. The original study used RIP-PEN-seq (a high-throughput screening method) to identify kink-turn RNAs (bktRNAs) as regulators of local intron splicing. The correction addresses a data organization error in Figure 6d where values from the second biological replicate (rep2) were mistakenly duplicated in place of the third replicate (rep3). As a result, the count of bktRNAs showing statistically significant regulation of local intron splicing was revised downward from eight to seven. For operators and investors tracking RNA-based therapeutic platforms or splice-modulating technologies, this correction confirms that the core finding—bktRNAs function as splicing regulators—remains valid with slightly fewer confirmed hits.

---

### FDA approves Viridian’s eye drug, stoking competition wit...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/fda-approves-viridian-eye-drug-stoking-competition-with-amgens-tepezza

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/fda-approves-viridian-eye-drug-stoking-competition-with-amgens-tepezza/&title=FDA%20approves%20Viridian%27s%20eye%20drug%2C%20stoking%20competition%20with%20Amgen%27s%20Tepezza&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=FDA%20approves%20Viridian%27s%20eye%20drug%2C%20stoking%20competition%20with%20Amgen%27s%20Tepezza%20

---

### Educating for translation
**Priority:** low | **Tags:** translational medicine, education, workforce development
**URL:** https://www.nature.com/articles/s41587-026-03168-3

A perspective article by Scott Compton, Salvatore Albani, Charles B. Cairns, and Berent Prakden arguing that educational programs in translational medicine must evolve to prepare a workforce capable of both discovery and patient translation. The authors, affiliated with the Eureka Institute for Translational Medicine (Singapore), Duke-NUS Medical School, Drexel University College of Medicine, and University Medical Centre Utrecht, assert that fulfilling the promise of translational medicine requires systemic reform in how researchers are trained. The article references foundational critiques from the literature on reproducibility and clinical trial failures (Zerhouni 2005, Macleod 2014, Weggemans 2018, Clay 2019) to frame the educational gap.

---

### Five Questions with Ya-Wen Chen
**Priority:** low | **Tags:** stem cell therapy, regenerative medicine
**URL:** https://www.nature.com/articles/s41587-026-03169-2

Nature Biotechnology Senior Editor Michael Francisco interviews Ya-Wen Chen, a biologist described as motivated by the prospect of developing stem cell technologies capable of repairing damaged organs or creating new ones for transplantation. The article is an interview-style piece that explores Chen's research vision and career trajectory in regenerative medicine and stem cell biology. Specific details about organizations, therapies, trial outcomes, or commercial partnerships are not visible in the subscription-gated preview. The piece is part of Nature Biotechnology's recurring 'Five Questions with...' format, which profiles leading scientists and industry figures shaping biotech innovation.

---

### Programming biology: next-gen AI firms raise billions to design better medicines
**Priority:** high | **Tags:** AI drug discovery, venture funding, generative biology
**URL:** https://www.nature.com/articles/s41587-026-03170-9

Melanie Senior writes for Nature Biotechnology about the emerging wave of AI-driven drug discovery companies and their multi-billion-dollar fundraising rounds. The article covers how programmable therapeutics, optimized drug design, and faster discovery pipelines are being powered by next-generation AI/ML platforms. It notes that despite rapid progress in AI-based R&D, data access and development bottlenecks remain key constraints for the sector. A figure illustrating AI and ML-based venture funding trends is referenced, along with citations from Chai Discovery (bioRxiv preprint) and several other peer-reviewed works on generative models for biological discovery.

---

### Single-cell spatial pharmacobiology for imaging antibody-based therapies in solid tumors
**Priority:** high | **Tags:** drug delivery, cancer therapeutics, spatial biology, antibody therapy
**URL:** https://www.nature.com/articles/s41587-026-03171-8

This Nature Biotechnology perspective by Lu et al. introduces single-cell spatial pharmacobiology (SSP), a novel platform combining in situ imaging of systemically administered fluorescent therapeutic antibodies with high-plex spatial proteomics to map drug delivery at cellular resolution. Applied to resected head and neck and pancreatic tumor specimens from patients enrolled in phase 1 clinical trials, the SSP approach reveals marked spatial heterogeneity in both antibody delivery and target engagement across individual tumors. These distribution patterns are shaped by conserved stromal barriers that consistently impede therapeutic access within the tumor microenvironment. The work builds on prior findings using panitumumab-IRDye800CW (pan800) as an imaging agent for fluorescence-guided surgery in pancreatic ductal adenocarcinoma and head and neck cancers, extending those insights to a broader quantification framework for how antibodies traverse tissue in living tumors. The methodology has direct implications for optimizing antibody-based drug delivery strategies, designing antibody-drug conjugates (ADCs) that overcome stromal resistance, and interpreting variable therapeutic outcomes driven by tumor microenvironment architecture rather than molecular target expression alone.

---

### Hybrid solid-liquid optics enable scalable, high-resolution light-sheet microscopy across diverse immersion media
**Priority:** high | **Tags:** microscopy, tissue-imaging, light-sheet-microscopy, histopathology, brain-imaging
**URL:** https://www.nature.com/articles/s41587-026-03172-7

Researchers introduced HySIL (hybrid solid-liquid optics), a refractive design framework that pairs a solid optical element with refractive-index-matched liquid to form a continuous optical system for wavefront correction and numerical aperture enhancement. Implemented as the modular SCOPE device and its higher-performance Super-SCOPE variant, the technology enables submicron-resolution (<0.75 mu m lateral) imaging using inexpensive long-working-distance air objectives (34 mm working distance). Demonstrated across cleared and expanded mouse and salamander brains, iDISCO-cleared cavefish brains, iPSC-derived brain organoids co-cultured with microglia, and intact human breast tissue for 3D histopathology. HySIL achieves effective NA scaling as n for SCOPE and n^2 for Super-SCOPE, works across a broad RI range (1.38-1.56) without hardware modification, and integrates into both open-source pLSM and commercial SLICE platforms at significantly reduced cost compared to high-NA immersion objectives.

---

### Twin prime editing-based knockout system enables efficient multiplex gene knockout with orthogonal editors in crops
**Priority:** high | **Tags:** genome editing, prime editing, crop engineering, CRISPR, plant biotechnology
**URL:** https://www.nature.com/articles/s41587-026-03174-5

A novel twin prime editing-based knockout (TKO) system developed by Hongchao Li, Caixia Gao and colleagues at the Chinese Academy of Sciences installs stop codon clusters (SCCs) to achieve precise translational termination with minimal in-frame mutations, reaching knockout efficiencies of 70.5% in rice protoplasts, 58.6% in maize, and 75.1% in wheat. In hexaploid wheat, TKO outperforms standard Cas9 by 4.2-fold for triple-homolog knockouts, with heritable alleles established in 96.8% of regenerated rice plants. Orthogonal TKO editors using sequence-divergent SCCs enable simultaneous knockout of up to ten genes without cross-interference. Integrated with conventional prime editing as TRIM1, the system achieves 22.8% co-editing efficiency across four genes in rice; a further extension, TRIM2, combines a prime editor with recombinase systems for kilobase-scale modifications including 4.9-kb insertions at 1.2% efficiency.

---

### People -- Recent moves of note in and around the biotech and pharma industries
**Priority:** low | **Tags:** industry-news, biotech-pharma
**URL:** https://www.nature.com/articles/s41587-026-03176-3

This is a Nature Biotechnology column titled "People" (Nat Biotechnol 44, 1064, 2026) published on June 16, 2026, described only as covering "recent moves of note in and around the biotech and pharma industries." The actual article body is behind a paywall and not accessible from the provided content. The page reveals no named companies, drugs, clinical trials, approvals, or specific deal terms. Without access to the full subscription-gated content, no substantive analysis of biotech industry shifts, leadership changes, or scientific developments can be performed.

---

### Mapping the human cell–cell interactome: tools for decoding cellular communication
**Priority:** high | **Tags:** cell-cell interactome, single-cell transcriptomics, spatial biology, synthetic biology, therapeutic discovery
**URL:** https://www.nature.com/articles/s41587-026-03177-2

This Perspective in Nature Biotechnology calls on the scientific community to map and engineer a comprehensive human cell–cell interactome: a functional atlas systematically cataloguing the communication between all major human cell types. The article highlights that while single-cell transcriptomics and spatial profiling technologies can measure molecular states at individual resolution, a fundamental knowledge gap remains regarding how these cellular states influence one another within tissue context. As an inaugural 'moonshot,' the authors propose the Billion CellxCell Project, which would characterize the outcomes of defined cell–cell dyads across diverse cell types and conditions. The paper synthesizes emerging technologies including high-throughput screening approaches, synthetic biology tools for engineered receptors, proximity-based sequencing methods (such as SEC-seq), and computational inference frameworks (including CellPhoneDB v5, CellChat, and SpaCcLink) that together could make this vision achievable over multiple stages. This effort is positioned as foundational infrastructure to unlock new therapeutic discovery avenues by decoding the 'language' of cellular communication.

---

### Biotech news from around the world
**Priority:** high | **Tags:** AI_drug_discovery, biotech_policy, agricultural_biotechnology, pharma_investment
**URL:** https://www.nature.com/articles/s41587-026-03178-1

Boehringer Ingelheim announced a $200 million commitment to the UK innovation ecosystem over the next 10 years, including an AI and machine learning accelerator in King뼁s Cross, London that will onboard 50 AI experts within 18 months to strengthen AI applications across its global pharma R&D pipeline. Separately, Vietnam뼁s government issued Decree 43/2026/ND-CP updating agricultural biotech regulations, cutting standard approval timelines for genetically engineered food and feed products from 90 working days to 45 days for products already approved in at least five OECD or G20 nations. This regulatory reform aligns with Vietnam뼁s 2025 designation of biotechnology as a strategic pillar for agricultural growth, aimed at facilitating import trade and boosting domestic production capacity. Together, these developments signal major capital deployment into AI-enabled drug discovery by a top-tier pharma and aggressive regulatory liberalization in a key emerging-market agri-biotech jurisdiction.

---

### FDA to reduce regulatory red tape for biosimilars
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/fda-to-reduce-regulatory-red-tape-for-biosimilars

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/fda-to-reduce-regulatory-red-tape-for-biosimilars/&title=FDA%20to%20reduce%20regulatory%20red%20tape%20for%20biosimilars&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=FDA%20to%20reduce%20regulatory%20red%20tape%20for%20biosimilars%20-%20https://endpoints.news/fda-to-reduce-regulatory-red-tape-for-biosimilars/ "Share on Twi

---

### Biotech's coming of age
**Priority:** high | **Tags:** biotech-industry-outlook, china-biotech, ai-drug-discovery, biotech-investing
**URL:** https://www.nature.com/articles/s41587-026-03179-0

Melanie Senior publishes a commentary in Nature Biotechnology (10 June 2026) arguing that the biotech sector is re-entering a growth phase but under markedly different conditions than previous cycles. The article identifies three forces reshaping the industry: cautious institutional investors repricing risk after the 2021–2023 biotech boom, the accelerating rise of Chinese biotech firms as global competitors and deal-makers, and generative AI compressing discovery timelines. With only a headline-level preview available due to Nature's paywall, no specific drug candidates, company valuations, or deal figures are discernible. The piece likely serves as an industry outlook piece intended for biotech operators and venture investors navigating the new competitive landscape.

---

### Author Correction: DNA-guided CRISPR-Cas12a effectors for programmable RNA recognition and cleavage
**Priority:** low | **Tags:** CRISPR, RNA-targeting, molecular-biology, synthetic-biology, gene-editing
**URL:** https://www.nature.com/articles/s41587-026-03180-7

This is an author correction (not the original research article) to a Nature Biotechnology paper on DNA-guided CRISPR-Cas12a effectors enabling programmable RNA recognition and cleavage. The correction addresses two issues: (1) a Fig. 3f y-axis label error where the lower bound was corrected from 5.0 x 10^4 to 5.0 x 10^3, and (2) an added citation in the Discussion recommending Orosco et al.'s MedRxiv preprint on the catalytic scope flexibility of type V CRISPR nucleases. A subsequent change note updated the reference further to cite Orosco et al.'s formal Nat Biotech publication alongside the original preprint. The work originates from HKUST (I-Ming Hsing's lab) and has implications for engineered CRISPR systems targeting RNA.

---

### Efficient site-specific gene addition using R2 retrotransposons in tobacco and rice
**Priority:** high | **Tags:** genome editing, gene delivery, plant biotechnology, synthetic biology
**URL:** https://www.nature.com/articles/s41587-026-03181-6

Researchers repurpose non-long terminal repeat (non-LTR) R2 retrotransposons as a precision genome engineering tool for stable, site-specific transgene integration into the 28S ribosomal DNA (rDNA) safe-harbor locus in plants. Using R2 effectors from Taeniopygia guttata (R2-TG and optimized R2-TGopt), the team demonstrates targeted insertion of a 2.2 kb GFP cassette and recombinase-compatible landing pads (attP, lox66, FRT) into Nicotiana benthamiana rDNA, achieving up to 75% intact-cassette integration. A novel two-component delivery system—coupling in planta R2 effector expression with RNA virus-mediated donor RNA via TRV/TSWV viral vectors—temporally constrains donor availability and eliminates DNA intermediates. The approach extends to rice (Oryza sativa) callus, where kanamycin-resistance and ALS herbicide-resistance cassettes integrate at efficiencies up to 17%, establishing R2 as a double-strand break-free, RNA-templated platform for multikilobase gene stacking in crops without reliance on homology-directed repair.

---

### Marked for destruction
**Priority:** high | **Tags:** PROTAC, targeted protein degradation, oncology, breast cancer, ER degrader
**URL:** https://www.nature.com/articles/s41587-026-03182-5

Nature Biotechnology publishes an essay marking the FDA’s approval of the first proteolysis-targeting chimera (PROTAC), an estrogen receptor (ER) degrader for ER+ breast cancer patients carrying ESR1 resistance mutations. Unlike conventional ‘occupancy-driven’ drugs that merely inhibit target proteins, the PROTAC’s two-sided heterobifunctional molecule simultaneously binds ER on one side and cereblon E3 ligase on the other, recruiting ubiquitination machinery to tag the protein for proteasomal destruction before dissociating and repeating. In clinical testing against fulvestrant (an IV hormone therapy), the PROTAC delivered approximately three extra months of progression-free survival—a modest gain the author likens to early checkpoint inhibitor results in 2010, whose therapeutic significance was not yet apparent. The article’s core argument is that clinical magnitude matters less than proof-of-concept: this approval demonstrates that protein degradation is a viable therapeutic modality, opening a broader ecosystem of TPD approaches including molecular glues, LYTACs, and AUTACs for previously ‘undruggable’ targets.

---

### A tough scaffold for bacterial therapy
**Priority:** high | **Tags:** engineered bacteria, hydrogel scaffold, synthetic biology, drug delivery
**URL:** https://www.nature.com/articles/s41587-026-03183-4

Iris Marchal reports on a perspective by Harimoto et al. published in Science describing a novel hydrogel scaffold engineered to trap therapeutic bacteria in vivo while preserving their function. The scaffold uses polyvinyl alcohol as a base polymer embedded with gelatin microgels containing Escherichia coli, fabricated through optimized freeze-thaw cycles, dry annealing, and a salting-out process. The resulting material is described as stiff and tough, retaining E. coli for up to 6 months in culture without bacterial escape, even under mechanical stresses simulating physiological conditions. This approach addresses a critical bottleneck in translating engineered living therapeutics — controlling bacterial localization and growth within the body — by providing mechanical confinement without sacrificing bacterial viability or proliferation capacity.

---

### Efficient targeting of human glial progenitor cells in vivo with engineered AAV vectors and glymphatic delivery
**Priority:** high | **Tags:** gene therapy, AAV vectors, glial biology, neurotechnology, glymphatic delivery
**URL:** https://www.nature.com/articles/s41587-026-03185-2

Researchers at Nature Biotechnology developed engineered AAV5-based capsid variants that selectively target human glial progenitor cells (hGPCs) and their derived astrocyte and oligodendrocyte progeny in the brain. Using an in vivo M-CREATE screening strategy in human glial chimeric mice, they isolated 20 capsid variants (designated CM1-20) from a library of 4 x 10^5 randomly mutagenized AAV5 candidates. Two lead vectors were characterized: AAV-CM1 preferentially transduced hGPCs and oligodendroglial lineage cells (transducing 34.9% +/- 5.7% of human Olig2+ glia in the corpus callosum, a 5.3-fold improvement over WT AAV5), while AAV-CM6 selectively targeted astrocytes (transducing 22.2% +/- 3.9% of Sox9+ astrocytes, 3.8-fold above WT). Both vectors showed minimal off-target infection of liver, spleen, and kidney. The authors combined intracisternal injection with systemic hypertonic saline to exploit glymphatic transport, bypassing the blood-brain barrier and enabling brain-wide distribution at significantly reduced viral doses — a clinically feasible strategy that mitigates the systemic toxicity associated with high-dose intravenous AAV gene therapy.

---

### Retargeting serine integrase Bxb1 via modular integrase (MINT) system enables precise large-DNA insertion at desired human genomic loci
**Priority:** high | **Tags:** genome-editing, gene-therapy, serine-integrase, MINT, cell-therapy
**URL:** https://www.nature.com/articles/s41587-026-03186-1

Sangamo Therapeutics researchers developed a Modular Integrase for Targeting (MINT) system that retargets the bacteriophage Bxb1 serine integrase to user-specified human genomic loci. Using structural modeling combined with single-round directed evolution and screening directly in human cells, the team engineered Bxb1 specificity away from its native attachment site toward the AAVS1safe harbor locus and the TRAC locus for T-cell engineering. In K562 cells, MINT constructs paired with activity-increasing Bxb1 mutants and zinc-finger DNA-binding domains achieved 29% integration efficiency at the AAVS1 locus and 35% at the TRAC locus. The system was further validated in primary human T cells with 29% GFP integration at TRAC, demonstrating clinical viability for non-viral genome editing.

---

### Germinal: efficient de novo design of epitope-specific antibodies with nanomolar affinity
**Priority:** high | **Tags:** antibody design, generative AI, protein engineering
**URL:** https://www.nature.com/articles/s41587-026-03187-0

Researchers at Stanford University and the Arc Institute (led by Luis S. Mille-Fragoso and Brian L. Hie) have introduced Germinal, a generative AI pipeline that designs functional antibodies against specific protein epitopes with nanomolar binding affinities. The method co-optimizes antibody structure and sequence by integrating an AlphaFold-Miller (AF-M) structure predictor with an antibody-specific protein language model (IgLM), performing de novo design of complementarity-determining regions onto user-specified structural frameworks. When tested against four diverse protein targets, Germinal produced functional binders across all targets and multiple binder formats, requiring only 43 to 101 computational designs per antigen for validation. The designed antibodies exhibited robust expression in mammalian cells, high sequence novelty, and structurally novel CDR loops as confirmed by cryo-EM mapping (PDB 35TL, EMD-77181 for a PDL1 scFv complex). Code is freely available on GitHub (github.com/SantiagoMille/germinal) with full computational and experimental protocols in the Supplementary Information.

---

### DeepMind Spinout Raises $2.1 Billion
**Priority:** high | **Tags:** AI Drug Discovery, Biotech Funding, Generative Biology
**URL:** https://www.nature.com/articles/s41587-026-03189-y

London-based Isomorphic Labs, the DeepMind spinout focused on AI-driven drug discovery, secured $2.1 billion in a Series B funding round led by Thrive Capital with participation from Alphabet, marking one of the largest private biotech rounds in history. The capital will be used to scale up the IsoDDE (Isomorphic Labs Drug Design Engine), unveiled in February 2026, which reportedly surpasses AlphaFold 3 in predictive accuracy across predicting novel structures, estimating binding affinities, and identifying novel ligand pockets. On the Runs N’ Poses protein-ligand structure prediction benchmark, IsoDDE more than doubled AlphaFold 3's accuracy while also outperforming physics-based methods like FEP+ on antibody binding affinity benchmarks. Notably, IsoDDE accurately identified cryptic allosteric binding pockets for cereblon -- a clinically relevant target underlying immunomodulatory drugs such as thalidomide -- starting from sequence alone without a specified ligand. This round follows a $600 million raise the previous year and signals deep investor conviction in large-language-model approaches to structural biology as a path toward drug discovery.

---

### Meatly to scale cultivated meat for pets
**Priority:** medium | **Tags:** cultivated meat, pet food, cellular agriculture, Series A funding
**URL:** https://www.nature.com/articles/s41587-026-03190-5

British startup Meatly announced plans to build Europe's largest cultivated meat facility in London, a 20,000-liter pilot production site that will manufacture bioreactor-grown chicken meat for the pet food market. The project is funded by a £10.4 million (US $14 million) Series A raise also announced in May 2026. The move is notable because total cultivated meat sector investment has collapsed from a $1.4 billion peak in 2021 to just $74 million in 2025, according to data from the Washington-based Good Food Institute. Meatly's pivot toward pet food as an early commercial channel signals an industry adaptation strategy — targeting a less regulated, higher-margin market than human consumption amid investor fatigue. The announcement may help stabilize sentiment in a sector that has seen rapid funding contraction.

---

### Opinion: Your grandparents are using cannabis. Doctors can help them do it safely.
**Priority:** medium | **Tags:** medical-cannabis, geriatric-health, public-health, chronic-pain-management
**URL:** https://www.statnews.com/2026/07/09/cannabis-seniors-medical-marijuana-legal-thc-cbd-chronic-pain/

Peter Grinspoon, an addiction specialist at Massachusetts General Hospital and author of "Aging Well with Cannabis," argues that older patients are adopting medical cannabis faster than any other demographic but lack physician-guided safe-use frameworks. He opens with a personal anecdote from 2016 about a 70-year-old female acquaintance who experienced disorientation, anxiety, and collapse after consuming cannabis shortly after Massachusetts legalized adult use—she recovered after hospital evaluation with no lasting harm. The piece uses this case to underscore the need for clinician involvement in cannabis dosing, THC/CBD titration, and drug-interaction screening in elderly populations on multiple medications. Grinspoon asserts that over 25 years of treating medical cannabis patients he has seen "extremely few ill effects," suggesting that physician oversight is the critical variable separating safe outcomes from preventable adverse events. For biotech operators in the cannabis therapeutics space, this signals accelerating demand for evidence-based dosing frameworks and clinician education infrastructure.

---

### What happens on 'MAHA Monday'?
**Priority:** low | **Tags:** policy, public-health
**URL:** https://www.statnews.com/2026/07/09/maha-mondays-great-american-state-fair-status-report-alex-hogan/

STAT Washington correspondent Alex Hogan attended the second of two MAHA Mondays at the Great American State Fair in Washington, a two-week event promoting the Make America Healthy Again movement. The program featured speakers and administration officials discussing how health and wellness connect to American identity. Hogan interviewed Calley Means, HHS senior adviser under RFK Jr., who spoke about MAHA's broader mission. Acting Surgeon General Stephanie Haridopolos discussed her office's recent advisory on the harms of screen time use among children, linking it to a broader public health and wellness agenda tied to the administration's policy priorities.

---

### How one father built a biotech, Grace Science, to save his daughter
**Priority:** high | **Tags:** gene therapy, rare disease
**URL:** https://www.statnews.com/2026/07/09/matt-wilsey-grace-science-rare-disease-drug-development-ngly1/

Matt Wilsey spent a decade and $70 million building Grace Science to develop an NGLY1 gene therapy for his 15-year-old daughter Grace, who suffers from NGLY1 deficiency—an ultra-rare genetic disorder causing severe developmental challenges including inability to speak or walk. The company treated 10 patients in clinical trials but ran out of funding before securing FDA approval, as regulators say they still need more data. After the therapy was administered three weeks prior to reporting, Grace was hospitalized in a weakened state and appears to be deteriorating despite the experimental treatment. Wilsey is pushing the FDA for approval anyway, turning his own trial into a test case for how regulators evaluate treatments for ultra-rare, fatal diseases when no other options exist.

---

### Opinion: Who benefits from classifying obesity as a disease?
**Priority:** medium | **Tags:** obesity, pharmacology
**URL:** https://www.statnews.com/2026/07/09/obesity-disease-classification-glp-1-eli-lilly-novo-nordisk/

STAT News opinion piece by Max Moser, a psychology research fellow at University College London, examining the commercial logic behind the pharmaceutical industry's framing of obesity as a disease. The article notes that Eli Lilly has launched a website asserting obesity is 'a chronic and complex medical entity in its own right,' while Novo Nordisk more cautiously references World Health Organization recognition on its site. Moser argues that the disease-framing serves a clear commercial purpose: 'a medical solution requires a medical problem, and a chronic medical problem provides a rationale for long-term medical treatment.' The piece raises concerns that wholesale adoption of disease framing risks narrowing understanding of obesity's causes and solutions, without reaching consensus on what 'disease' precisely means in medicine. The full article body is behind a STAT+ paywall, limiting the analysis to available metadata and the opening paragraphs. Tags include chronic disease, Obesity, and weight loss.

---

### AstraZeneca, Ionis report major trial failure with heart disease drug
**Priority:** high | **Tags:** cardiovascular, drug development
**URL:** https://www.statnews.com/2026/07/09/astrazeneca-ionis-attr-wainua-trial-failure/

AstraZeneca and partner Ionis Pharmaceuticals announced that Wainua, an siRNA-based therapeutic targeting transthyretin-mediated amyloid cardiomyopathy (ATTR-CM), failed to outperform placebo in a pivotal trial. The drug did not reduce cardiovascular death or clinical events in ATTR-CM patients, dealing a significant blow to both companies' cardiovascular pipelines. Market reaction was swift: AstraZeneca's U.S. shares fell roughly 8% in premarket trading and London-listed shares dropped approximately 9%, while Ionis shares tumbled 12%. The failure is notable because ATTR-CM represents an estimated $15-billion-plus addressable market, making it a fiercely competitive target among multiple biopharma firms. This setback underscores the persistent difficulty of translating antisense and siRNA approaches into cardiovascular outcomes trials.

---

### AstraZeneca pens $2.1B Sino deal for challenger to Merck's COPD drug Ohtuvayre
**Priority:** high | **Tags:** licensing-deals, COPD, PDE3-4-inhibitor, challenger-drug
**URL:** https://www.fiercebiotech.com/biotech/astrazeneca-pays-sino-200m-challenger-mercks-copd-drug-ohtuvayre

AstraZeneca has agreed to pay Sino Biopharmaceutical $200 million upfront plus up to $1.9 billion in achievable milestones for exclusive ex-China rights to TQC3721, a late-phase PDE3/4 inhibitor targeting chronic obstructive pulmonary disease (COPD). Developed by Sino's Chia Tai Tianqing Pharmaceutical subsidiary, the nebulized formulation of TQC3721 has reached phase 3 in China, with a dry powder inhaler version in phase 2. The asset is positioned as a potential best-in-class challenger to Merck's Ohtuvayre (ensifentrine), which generates $131 million per quarter; head-to-head comparisons show TQC3721 achieved up to 147 mL peak FEV1 improvement in phase 2 versus Verona Pharma's reported 124 mL. The deal adds to AstraZeneca's broader COPD pipeline, including positive phase 3 data for anti-IL-33 antibody tozorakimab planned for regulatory submission. For investors, the $2.1B total deal value signals aggressive competition in the inhalation drug market following Merck's $10 billion acquisition of Verona Pharma.

---

### Boehringer bags PVT's viral vector platform for cancer vaccine R&D
**Priority:** medium | **Tags:** oncolytic virus, cancer vaccine, viral vectors, licensing deal
**URL:** https://www.fiercebiotech.com/biotech/boehringer-bags-pvts-viral-vector-platform-cancer-vaccine-rd

Boehringer Ingelheim has secured an exclusive license to Prime Vector Technologies' (PVT) Orf virus (ORFV) viral vector platform for next-generation cancer vaccine development, under terms featuring undisclosed upfront and milestone payments. PVT retains rights to pursue infectious diseases and other applications with the platform, which has already demonstrated clinical feasibility through its COVID-19 vaccine candidate Prime-2-CoV. ORFV, a parapoxvirus that infects sheep and goats, has been studied for over a decade as a potential cancer therapeutic due to its safety profile, support for repeat dosing, and immunogenic properties—though manufacturing scalability and human safety uncertainties have historically constrained development. The deal advances Boehringer's longstanding oncolytic virus strategy dating to 2016, including the VSV-GP (BI-1831169) program and its Austrian ViraTherapeutics facility.

---

### FDA Halts Release of New Drug Rejection Letters While Working to Formalize Policy
**Priority:** high | **Tags:** FDA regulation, drug approvals, policy transparency, biotech investors
**URL:** https://www.fiercebiotech.com/biotech/fda-halts-release-new-drug-rejection-letters-while-working-formalize-policy

The FDA has temporarily paused its controversial policy of publishing Complete Response Letters (CRLs) in real-time after an unnamed pharmaceutical company filed a citizen petition through Covington & Burling, arguing the letters exposed proprietary and unredacted confidential information. The agency originally announced the transparency program in September under Health Secretary Robert F. Kennedy Jr.'s radical transparency initiative and FDA Commissioner Marty Makary; the 89-letter database release following 200 prior CRLs included high-profile rejections from Ultragenyx, Capricor Therapeutics, and Replimune. The June 27 pause applies retroactively from April, leaving more recent drug denials like Sobi's gout drug without published CRLs despite prior precedent of full transparency. Meanwhile, the FDA has proposed a rule (RIN 0910-AJ16) that would expand the commissioner's authority to release CRLs by eliminating the presumption that marketing applications constitute confidential commercial information—legislative work Makary pursued before departing the agency in May. This pause represents a significant operational policy shift with material implications for how biotech and pharma companies navigate the regulatory submission process going forward.

---

### Fierce Biotech Fundraising Tracker '26: Celea raises $180M for phase 3 study of PureTech IPF drug
**Priority:** low | **Tags:** venture capital, fundraising, biotech IPO pipeline, anti-fibrotics, AI drug discovery, longevity
**URL:** https://www.fiercebiotech.com/biotech/fierce-biotech-fundraising-tracker-26

Fierce Biotech's annual Fundraising Tracker compiles biopharma venture capital deals of $50 million and above from Jan–Jul 2026. The July highlight features London-listed Celea Therapeutics, a PureTech spin-out, raising $180M in debut financing for its antifibrotic deupirfenidone to advance an IPF head-to-head phase 3 study against pirfenidone. The tracker catalogues ~40 rounds across multiple sectors: Ollin Biosciences ($330M Series B for VEGF/Ang2 bispecific OLN324), Isomorphic Labs ($2.1B Series B for AI drug discovery), NewLimit ($435M Series C for longevity/fatty liver assets), Beeline Medicines ($300M from Bain for autoimmune programs from BMS), and Parabilis/Corsera Health/Alveus among many others. Notable themes include AI-driven drug discovery, in vivo CAR-T, GLP-1/obesity, anti-amyloid antibodies, RNAi therapeutics, gene editing, ADCs, and male contraceptives—reflecting a market still flush with capital across diverse modalities.

---

### Fierce Biotech Layoff Tracker 2026: Novartis loses 322 US staffers; BioCryst ends internal programs
**Priority:** high | **Tags:** biotech layoffs, big pharma restructuring, clinical trial failures, M&A integration, biotech sector consolidation
**URL:** https://www.fiercebiotech.com/biotech/fierce-biotech-layoff-tracker-2026

Fierce Biotech's fifth annual layoff tracker compiles workforce reductions across the biopharma industry from January through July 2026, covering 80+ companies and highlighting the sector's accelerating contraction. The most consequential entries include Novartis cutting 472 total US positions across two separate rounds (322 in July plus 150 earlier), BioCryst shuttering all internal discovery programs and its Birmingham lab to pivot toward partnership-driven innovation, Biogen dismantling most of Apellis' research pipeline after its $5.6B acquisition, and ADC Therapeutics laying off 17% of its workforce following a safety scare with Zynlonta in a confirmatory trial. The tracker also documents several shutdowns—including IO Biotech's complete closure, f5 Therapeutics after six years, EveryOne Medicines closing before FDA guidance cleared, and Nido Biosciences shutting down post-Phase 2 failure—alongside major restructuring at Takeda (4,500 roles), BioNTech (1,860 manufacturing jobs), and Gilead/Arcellx ($7.8 billion acquisition integration). Clinical failures drove multiple layoffs: Neumora's navacaprant Phase 3 misses, Fulcrum scrapping its sickle-cell program after FDA pushback, Replimune's second melanoma rejection, and Urogenyx's dual brittle-bone study failures collectively triggered workforces cut across the mid-cap biotech segment.

---

### Advocacy group accuses Novo Nordisk of violating FDA’s ‘f...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/advocacy-group-accuses-novo-nordisk-of-violating-fdas-fair-balance-advertising-rules

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/advocacy-group-accuses-novo-nordisk-of-violating-fdas-fair-balance-advertising-rules/&title=Advocacy%20group%20accuses%20Novo%20Nordisk%20of%20violating%20FDA%27s%20%27fair%20balance%27%20advertising%20rules&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Advocacy%20group%20accuses%20Novo%20Nordisk%20of%20violating%20FDA%27s

---

### Biotech stocks are on a tear again
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/biotech-stocks-are-on-a-tear-again

![](https://endpoints.news/wp-content/uploads/2026/03/signal-insights-3.jpg) [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/biotech-stocks-are-on-a-tear-again/&title=Biotech%20stocks%20are%20on%20a%20tear%20again&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Biotech%20stocks%20are%20on%20a%20tear%20again%20-%20https://endpoints.news/biotech-stocks-are-on-a-tear-again/

---

### BridgeBio adds $1B as it prepares three more drug launches
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/bridgebio-adds-1b-as-it-prepares-three-more-drug-launches

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/bridgebio-adds-1b-as-it-prepares-three-more-drug-launches/&title=BridgeBio%20adds%20%241B%20as%20it%20prepares%20three%20more%20drug%20launches&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=BridgeBio%20adds%20%241B%20as%20it%20prepares%20three%20more%20drug%20launches%20-%20https://endpoints.news/bridgebio-adds-1b-as-it-pr

---

### Bristol Myers details Krazati confirmatory study failure ...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/bristol-myers-details-krazati-confirmatory-study-failure-in-colorectal-cancer

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/bristol-myers-details-krazati-confirmatory-study-failure-in-colorectal-cancer/&title=Bristol%20Myers%20details%20Krazati%20confirmatory%20study%20failure%20in%20colorectal%20cancer&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Bristol%20Myers%20details%20Krazati%20confirmatory%20study%20failure%20in%20colorectal%20cancer%2

---

### Catalent handed two Form 483s, including for Sarepta gene...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/catalent-handed-two-form-483s-for-maryland-gene-therapy-sites

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/catalent-handed-two-form-483s-for-maryland-gene-therapy-sites/&title=Catalent%20handed%20two%20Form%20483s%2C%20including%20for%20Sarepta%20gene%20therapy%20site&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Catalent%20handed%20two%20Form%20483s%2C%20including%20for%20Sarepta%20gene%20therapy%20site%20-%20https://endpoints

---

### European Commission seeks biopharma feedback on Novo-Cata...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/european-commission-seeks-biopharma-feedback-on-novo-catalent-deal-report

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/european-commission-seeks-biopharma-feedback-on-novo-catalent-deal-report/&title=European%20Commission%20seeks%20biopharma%20feedback%20on%20Novo-Catalent%20deal%20%E2%80%94%20report&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=European%20Commission%20seeks%20biopharma%20feedback%20on%20Novo-Catalent%20deal%20%E2%80%94%20

---

### French gene therapy biotech gets €33M to follow Krystal’s...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/french-gene-therapy-biotech-gets-e33m-to-follow-krystals-blueprint

![](https://endpoints.news/wp-content/uploads/2025/02/Philippe-Chambon.jpg) Philippe Chambon, Cyllene Therapeutics CEO [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/french-gene-therapy-biotech-gets-e33m-to-follow-krystals-blueprint/&title=French%20gene%20therapy%20biotech%20gets%20%E2%82%AC33M%20to%20follow%20Krystal%27s%20blueprint&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/

---

### GSK to acquire Nuvalent and its two cancer drugs under FD...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/gsk-to-acquire-nuvalent-and-its-two-cancer-drugs-under-fda-review-for-10-6b

![](https://endpoints.news/wp-content/uploads/2025/06/James-Porter-Nuvalent-tile.jpg) James Porter, Nuvalent CEO [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/gsk-to-acquire-nuvalent-and-its-two-cancer-drugs-under-fda-review-for-10-6b/&title=GSK%20to%20acquire%20Nuvalent%20and%20its%20two%20cancer%20drugs%20under%20FDA%20review%20for%20%2410.6B&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter

---

### GSK wins FDA approval for long-acting asthma drug
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/gsk-wins-fda-approval-for-long-acting-asthma-drug

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/gsk-wins-fda-approval-for-long-acting-asthma-drug/&title=GSK%20wins%20FDA%20approval%20for%20long-acting%20asthma%20drug&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=GSK%20wins%20FDA%20approval%20for%20long-acting%20asthma%20drug%20-%20https://endpoints.news/gsk-wins-fda-approval-for-long-acting-asthma-drug/ "Share on Twi

---

### Hengrui and Kailera’s injected incretin posts best-in-cla...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/hengrui-and-kaileras-injected-incretin-posts-best-in-class-obesity-data-in-phase-2-trial

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/hengrui-and-kaileras-injected-incretin-posts-best-in-class-obesity-data-in-phase-2-trial/&title=Hengrui%20and%20Kailera%E2%80%99s%20injected%20incretin%20posts%20best-in-class%20obesity%20data%20in%20Phase%202%20trial&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Hengrui%20and%20Kailera%E2%80%99s%20injected%20incretin%20po

---

### HHS lays groundwork for new FDA rule on releasing the CRLs
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/hhs-lays-groundwork-for-new-fda-rule-on-releasing-the-crls

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/hhs-lays-groundwork-for-new-fda-rule-on-releasing-the-crls/&title=HHS%20lays%20groundwork%20for%20new%20FDA%20rule%20on%20releasing%20the%20CRLs&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=HHS%20lays%20groundwork%20for%20new%20FDA%20rule%20on%20releasing%20the%20CRLs%20-%20https://endpoints.news/hhs-lays-groundwork-for-n

---

### Incyte advances atopic dermatitis campaign with a ‘reimag...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/incyte-advances-atopic-dermatitis-campaign-with-a-reimagine-theme

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/incyte-advances-atopic-dermatitis-campaign-with-a-reimagine-theme/&title=Incyte%20advances%20atopic%20dermatitis%20campaign%20with%20a%20%E2%80%98reimagine%E2%80%99%20theme%20%C2%A0&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Incyte%20advances%20atopic%20dermatitis%20campaign%20with%20a%20%E2%80%98reimagine%E2%80%99%20th

---

### Incyte to buy bleeding disorder biotech Vega Therapeutics...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/incyte-to-buy-bleeding-disorder-biotech-vega-therapeutics-in-1-25b-upfront-deal

![](https://endpoints.news/wp-content/uploads/2025/09/Adam-Rosenthal.jpg) Adam Rosenthal, Star Therapeutics CEO [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/incyte-to-buy-bleeding-disorder-biotech-vega-therapeutics-in-1-25b-upfront-deal/&title=Incyte%20to%20buy%20bleeding%20disorder%20biotech%20Vega%20Therapeutics%20in%20%241.25B%20upfront%20deal&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twit

---

### Intra-Cellular fingers a high placebo response explaining...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/intra-cellular-fingers-a-high-placebo-response-explaining-a-phiii-failure-as-lead-drug-goes-1-and-1-in-depression

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/intra-cellular-fingers-a-high-placebo-response-explaining-a-phiii-failure-as-lead-drug-goes-1-and-1-in-depression/&title=Intra-Cellular%20fingers%20a%20high%20placebo%20response%20explaining%20a%20PhIII%20failure%20as%20lead%20drug%20goes%201-and-1%20in%20depression&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Intra-Cellu

---

### Merck returns to lucrative eye disease market in up to $3...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/merck-returns-to-lucrative-eye-disease-market-in-up-to-3b-deal-for-eyebio

![](https://endpoints.news/wp-content/uploads/2024/04/GettyImages-2113284075-scaled.jpg) Rob Davis, Merck CEO (Jeenah Moon/Bloomberg via Getty Images) [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/merck-returns-to-lucrative-eye-disease-market-in-up-to-3b-deal-for-eyebio/&title=Merck%20returns%20to%20lucrative%20eye%20disease%20market%20in%20up%20to%20%243B%20deal%20for%20EyeBio&source=https://endpoints.news/ "Share on LinkedIn")

---

### New CDER appointment elevates longtime GLP-1 reviewer
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/new-cder-appointment-elevates-longtime-glp-1-reviewer

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/new-cder-appointment-elevates-longtime-glp-1-reviewer/&title=New%20CDER%20appointment%20elevates%20longtime%20GLP-1%20reviewer&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=New%20CDER%20appointment%20elevates%20longtime%20GLP-1%20reviewer%20-%20https://endpoints.news/new-cder-appointment-elevates-longtime-glp-1-reviewer/ "

---

### Novo Nordisk CEO to step down, timeline for successor unk...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/novo-nordisk-ceo-to-step-down-timeline-for-successor-unknown

![](https://endpoints.news/wp-content/uploads/2025/05/GettyImages-2197219596.jpg) Lars Fruergaard Jørgensen, Novo Nordisk CEO (Mads Claus Rasmussen/Ritzau Scanpix/AFP via Getty Images) [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/novo-nordisk-ceo-to-step-down-timeline-for-successor-unknown/&title=Novo%20Nordisk%20CEO%20to%20step%20down%2C%20timeline%20for%20successor%20unknown&source=https://endpoints.news/ "Share on LinkedIn")

---

### Updated: Novo Nordisk to buy MASH player Akero for $4.7B ...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/novo-nordisk-to-buy-mash-player-akero-for-4-7b-upfront

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/novo-nordisk-to-buy-mash-player-akero-for-4-7b-upfront/&title=Updated%3A%20Novo%20Nordisk%20to%20buy%20MASH%20player%20Akero%20for%20%244.7B%20upfront&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Updated%3A%20Novo%20Nordisk%20to%20buy%20MASH%20player%20Akero%20for%20%244.7B%20upfront%20-%20https://endpoints.news/novo-nord

---

### Pfizer gets obesity drug approval in China shortly after ...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/pfizer-gets-obesity-drug-approval-in-china-shortly-after-buying-local-rights

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/pfizer-gets-obesity-drug-approval-in-china-shortly-after-buying-local-rights/&title=Pfizer%20gets%20obesity%20drug%20approval%20in%20China%20shortly%20after%20buying%20local%20rights&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Pfizer%20gets%20obesity%20drug%20approval%20in%20China%20shortly%20after%20buying%20local%20rig

---

### Revolution Medicines shares promising data around KRAS dr...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/revolution-medicines-shares-promising-data-around-kras-drug-combination

![](https://endpoints.news/wp-content/uploads/2026/07/Revolution-Medicines-ASCO26-tile.jpg) (Credit: Kyle LaHucik for Endpoints News) [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/revolution-medicines-shares-promising-data-around-kras-drug-combination/&title=Revolution%20Medicines%20shares%20promising%20data%20around%20KRAS%20drug%20combination&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter

---

### Sanofi to buy early-stage vaccine maker Vicebio for $1.15...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/sanofi-to-buy-early-stage-vaccine-maker-vicebio-for-1-15b-upfront

![](https://endpoints.news/wp-content/uploads/2021/04/Emmanuel-Hanon-Viome-tile-scaled.jpg) Emmanuel Hanon, Vicebio CEO [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/sanofi-to-buy-early-stage-vaccine-maker-vicebio-for-1-15b-upfront/&title=Sanofi%20to%20buy%20early-stage%20vaccine%20maker%20Vicebio%20for%20%241.15B%20upfront&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?tex

---

### Sanofi walks away from $500M deal, leaving Revolution alo...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/sanofi-walks-away-from-500m-deal-leaving-revolution-alone-in-pushing-shp2-kras-combo

![](https://endpoints.news/wp-content/uploads/2022/07/GettyImages-1200565695-scaled.jpg) Mark Goldsmith, Revolution Medicines CEO (Mark Kauzlarich/Bloomberg via Getty Images) [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/sanofi-walks-away-from-500m-deal-leaving-revolution-alone-in-pushing-shp2-kras-combo/&title=Sanofi%20walks%20away%20from%20%24500M%20deal%2C%20leaving%20Revolution%20alone%20in%20pushing%20SHP2%2FKRAS%20combo&so

---

### Satellos gives early look at Duchenne pill in adults ahea...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/satellos-early-look-at-duchenne-pill-in-adults-ahead-of-key-data-in-children

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/satellos-early-look-at-duchenne-pill-in-adults-ahead-of-key-data-in-children/&title=Satellos%20gives%20early%20look%20at%20Duchenne%20pill%20in%20adults%20ahead%20of%20key%20data%20in%20children&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Satellos%20gives%20early%20look%20at%20Duchenne%20pill%20in%20adults%20ahead%20of%2

---

### UK waitlist for Novo’s Wegovy pill triples in week after ...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/uk-waitlist-for-novos-wegovy-pill-triples-in-week-after-approval-major-online-pharmacy-says

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/uk-waitlist-for-novos-wegovy-pill-triples-in-week-after-approval-major-online-pharmacy-says/&title=UK%20waitlist%20for%20Novo%27s%20Wegovy%20pill%20triples%20in%20week%20after%20approval%2C%20major%20online%20pharmacy%20says&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=UK%20waitlist%20for%20Novo%27s%20Wegovy%20pill%20trip

---

### IPO Tracker – Endpoints News
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/ipo-tracker

IPO TRACKER A real-time look at every biotech IPO filed and the amount raised in all the world's indexes. Compiled by editor Max Gelman. COMPANIES

---

