# BioMyne Koji — Intelligence Digest
**Date:** 2026-07-09 12:54:31
**Run ID:** c705d260-0616-4289-8169-65dafd557127
**Sources:** 11 | **Articles:** 51 | **Errors:** 0

---
### Incyte receives CRL over issues at Novo’s Indiana factory
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/incyte-receives-crl-over-issues-at-novos-indiana-factory

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/incyte-receives-crl-over-issues-at-novos-indiana-factory/&title=Incyte%20receives%20CRL%20over%20issues%20at%20Novo%27s%20Indiana%20factory&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Incyte%20receives%20CRL%20over%20issues%20at%20Novo%27s%20Indiana%20factory%20-%20https://endpoints.news/incyte-receives-crl-over-issues-a

---

### Data-Driven Soft Labeling Scales DNA Read Classification to Whole-Body Cell-Type Deconvolution
**Priority:** medium | **Tags:** genomics, machine-learning, cell-type-deconvolution, epigenetics, computational-biology
**URL:** https://arxiv.org/abs/2607.04987

Researchers Dmytro Rizdvanetskyi, Nathan Roos, and Pavlo Lutsik introduce Syto, a modular computational framework for read-level DNA methylation-based cell-type deconvolution that overcomes a key bottleneck in epigenetic analysis: existing methods aggregate methylation signals and discard single-read pattern information, while prior read-level approaches are restricted to few-class settings. The authors' core innovation is data-driven soft labeling—estimating the conditional probability distribution of cell types for each individual DNA read—which resolves the conflict between non-discriminative reads overwhelming classifiers and the many-to-many mapping between methylation patterns and cell types that prevents convergence. Evaluated on a whole-body atlas of 39 human cell types, Syto achieves a 2.56x reduction in mean squared error over state-of-the-art methods, with gains transferring to an out-of-distribution dataset spanning 16 tissues. For biotech operators and investors, this represents an advance in single-cell resolution multi-tissue deconvolution from bulk epigenetic samples, enabling more precise cell-inference pipelines without isolating single cells; the soft-labeling approach generalizes beyond genomics to any setting with a many-to-many signal-to-label mapping.

---

### Resource-Efficient Hybrid Quantum Neighborhood Selection for Large-Scale Molecular Diversity Optimization
**Priority:** medium | **Tags:** quantum computing, molecular optimization, compound screening
**URL:** https://arxiv.org/abs/2607.07336

Researchers Nicolas Mendes de Araujo and Lester de Abreu Faria present HQNS (Hybrid Quantum Neighborhood Selection), a framework that decomposes large dense QUBO optimization problems into bounded-width quantum subproblems via stochastic frontier selection. They benchmark it on the Maximum Diversity Subset Selection Problem (MDSSP), testing up to N=1000 candidate molecules. The method preserves 99.9908% of the mean diversity score achieved by an 11-restart parallel Simulated Annealing baseline, while cutting wall-clock time by 94.91%, peak CPU utilization by 64.68%, and peak memory usage by 88.61%. Critically, QPU execution time stays bounded within a 6–7 second envelope regardless of scale, indicating the quantum component is decoupled from global problem dimensionality when frontier size is fixed. For biotech operators evaluating hybrid quantum-classical pipelines—particularly in molecular design and library optimization—this demonstrates near-term practical value of QPU integration without waiting for unconditional quantum advantage.

---

### Towards a Pseudo-Labeling Workflow for Celltype-Classification from Explanted Brain Slice Recordings
**Priority:** low | **Tags:** neural recording, machine learning, single-cell analysis, MEAs
**URL:** https://arxiv.org/abs/2607.06569

Cora Jostock, Jonas Ort, Henner Koch, Gregor Schiele, and Andreas Erbslöh propose an unsupervised machine learning workflow for automatically classifying extracellular spikes recorded from MEA (microelectrode array) recordings of explanted human brain slices. The pre-processing pipeline applies bandpass filtering, threshold-based spike detection, frame alignment, and normalization to raw data acquisition outputs. The ML pipeline combines dimensionality reduction techniques (PCA, t-SNE, UMAP) with clustering methods (Gaussian Mixture Models, k-means) for initial classification, supplemented by template matching and OSort for potential online deployment. Validation uses within-cluster Pearson correlation, Silhouette score, and Calinski-Harabasz index across varying curations strictness levels. The authors find that applying stricter curation criteria improves separation of putative cell types (pyramidal neurons versus interneurons) at the cost of data inclusivity.

---

### Esports and Physiological Tremor: A StarCraft 2 Tournament Study
**Priority:** low | **Tags:** wearable biosensors, neuromuscular adaptation, esports science
**URL:** https://arxiv.org/abs/2607.06577

Researchers measured wrist accelerometer-based physiological tremor in 16 healthy adult male StarCraft 2 players across two consecutive tournament days, computing log power spectral density across four frequency bands and comparing to published population norms using linear mixed models. Key findings show significantly elevated tremor at 2–4 Hz and substantially reduced tremor at higher frequencies (Cohen's d = 1.6–2.3), suggesting long-term neuromuscular adaptation from fine-motor esports demands. Contrary to typical fatigue-related increases seen in traditional motor tasks, tremor indicators declined systematically over the course of each tournament day. Post-game tremor was not significantly predicted by game outcome or actions per minute, challenging assumptions that tremor could serve as a real-time performance predictor.

---

### Recovering Candidate Circadian Regulators of Arrhythmic Pituitary Hormone Genes Using Reliability-Weighted Magnetic Laplacian with rwMagLap
**Priority:** medium | **Tags:** chronobiology, computational-methods
**URL:** https://arxiv.org/abs/2607.06579

Shabnam Sodagari and Nick Jasperson present rwMagLap, a novel graph-based computational method designed to recover circadian-clock regulators that remain invisible in bulk tissue time-series data. The approach builds a Hermitian adjacency matrix on rhythmic backbone genes by encoding both 24-hour fit quality and peak-time phase as complex unit-circle values applied via a magnetic Laplacian, then inserts arrhythmic pituitary hormone genes as anchors through reliability-weighted nearest-neighbor projection. A soft teleport distribution feeds into complex personalized PageRank to rank candidates by their graph-propagated scores. Applied to pituitary data, the method detects all 11 women-health anchors as arrhythmic yet recovers a Top-50 candidate list showing 7.95-fold enrichment for KEGG circadian genes (BH p=4x10^-6) and 4.54-fold enrichment for Reactome circadian genes (BH p=1.6x10^-4); a phase-blind real-valued baseline recovers zero hits. Peak-time order within the pituitary backbone is recovered at 0.971 accuracy using the magnetic embedding versus chance without it.

---

### Trajectory Inference of Human Aging from Cross-Sectional DNA Methylation Data
**Priority:** medium | **Tags:** Epigenetic Clocks, Computational Biology, Quantitative Methods
**URL:** https://arxiv.org/abs/2607.06583

A team at arXiv (Chandan Gupta, Syed Haider, Pietro Lio) introduces a two-stage computational pipeline that frames human epigenetic aging as a trajectory inference problem rather than a static point-estimate regression. First, an age-regularized Variational Autoencoder maps high-dimensional CpG methylation profiles onto a chronologically ordered latent manifold with a generative decoder reconstructing the original methylation space. Second, Regularized Unbalanced Optimal Transport (RUOT) models continuous movement across that latent space by unifying deterministic drift, random diffusion, and non-conservative mass changes—accommodating population-level density shifts such as survivorship bias and cellular attrition without rigid biological priors. Evaluated on a large-scale 80-year pan-tissue dataset, the model reconstructs a prominent late-life surge in the learned growth field that mathematically captures variance expansion from stochastic epigenetic drift. By decoding continuous latent paths back to individual CpG sites, the authors empirically verify distinct biological aging archetypes, offering a generative framework for simulating human molecular aging trajectories.

---

### Polynomial encoding of rooted trees with branch lengths
**Priority:** low | **Tags:** computational-biology, phylogenetics
**URL:** https://arxiv.org/abs/2607.06591

Pengyu Liu, Joan Carles Pons, and Gerard Ribas introduce a bivariate polynomial encoding that incorporates branch lengths directly into a recursive computation across rooted phylogenetic trees. They prove that two rooted trees with branch lengths (and no degree-two vertices, which covers all standard phylogenetic trees) have the same polynomial if and only if their underlying unlabeled trees are isomorphic and corresponding edge branch lengths match. The authors apply the method to three published HIV-1 phylogenies sampled across different epidemiological settings and demonstrate that the encoding accurately separates the datasets by both topology and branch length, outperforming prior polynomial-based approaches. This represents a purely theoretical/computational contribution rather than an applied biotech development.

---

### Membrane Thickness Strain from Protein Inclusions: A Multiscale Simulation and X-Ray Scattering Study of Proteoliposomes
**Priority:** medium | **Tags:** biophysics, computational-biology
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.03.736288v1

Researchers at the University of Graz and Masaryk University developed an integrative methodology combining all-atom molecular dynamics simulations with multiscale small-angle X-ray scattering analysis to quantify membrane thickness deformations caused by integral membrane proteins. Using outer membrane phospholipase A (OmpLA) reconstituted into lipid bilayers with varying hydrophobic thicknesses, the team demonstrated that OmpLA induces anisotropic, oscillatory thickness changes extending up to eight times the radius of its first surrounding lipid shell, yet the net average membrane thickness shift remains below 1%. The approach leverages constrained Bayesian inference with simulation-derived priors to extract structural parameters from SAXS data, yielding quantitative protein/lipid molar ratios and average membrane strain measurements that show excellent agreement between experiment and simulation. In thinner bilayers, substantial protein loss was observed, underscoring bilayer stability as a critical factor in sample preparation. The study establishes a generalizable framework for quantifying protein-lipid interactions across molecular and mesoscale dimensions, relevant to understanding how embedded proteins remodel neighboring lipid environments.

---

### Reward Valuation in Vision Language Models: Causal Mechanisms Underlying Anhedonia
**Priority:** high | **Tags:** AI safety, neuroscience
**URL:** https://arxiv.org/abs/2607.06626

Researchers at Princeton (Melika Honarmand, Samin Mahdipour Aghabagher, and Martin Schrimpf) used a frameworks modeled on clinical anhedonia tests to functionally identify NAc-selective (Nucleus Accumbens) reward-anticipatory units in vision-language models, then tested their causal role through targeted perturbations. Disrupting these NAc-selective units induced behavioral effects mirroring human anhedonia: the model shifted toward low-effort, low-reward options in effort-based decision-making tasks. Crucially, this represented a specific deficit in reward valuation rather than mere loss of task capability, as perturbed models maintained baseline performance when reward-based choice was removed. The induced vulnerability aligned with clinical anhedonia and motivation scales including DARS (Dynamic Appraisal of State-Risk) and MAP-SR assessments. The findings reveal that reward valuation circuits in AI models parallel those found in human neurobiology, suggesting VLMs capture deep aspects of dopaminergic reward processing.

---

### STST-JEPA: Shallow-Target Spatio-Temporal Joint Embedding Prediction Architecture For EEG Self-Supervised Learning
**Priority:** medium | **Tags:** EEG, brain-age, self-supervised-learning, digital-health-biomarkers, neural-decoding
**URL:** https://arxiv.org/abs/2607.06629

Researchers Roy Segal, Yoni Svechinsky, and Tomer Fekete introduce STST-JEPA, a self-supervised transformer model for electroencephalography (EEG) that learns from 47,703 resting-state and task EEG sessions spanning ages 5-81 from the brain.space and Healthy Brain Network cohorts. The architecture combines a latent-prediction objective -- predicting masked-token representations against an exponential-moving-average-of-tokenizer target -- with auxiliary signal-reconstruction on 30-second multi-channel windows under spatiotemporal block masks. As a lightweight attentive probe trained on frozen embeddings, it achieves 3.06 years mean absolute error (R=0.924) for age regression on 3,367 held-out sessions against a predict-the-mean baseline of ~10 years. With light fine-tuning of final layers, the encoder reaches rank-1 placements on the NeuralBench EEG leaderboard: sex classification (balanced accuracy 0.911), age prediction (R=0.749), and psychopathology composite regression (R=0.215), using native 30-second windows. The age-prediction residual shows a negative correlation with cognitive efficiency across multiple examined tasks, suggesting clinically actionable biomarker signal in the prediction error itself.

---

### Selection Mechanisms, Stationary Distributions, and Reversibility in Multiallelic Moran Models
**Priority:** low | **Tags:** population genetics, theoretical biology, stochastic modeling
**URL:** https://arxiv.org/abs/2607.06732

Dan Braha and Marcus A M de Aguiar present a formal theoretical analysis of how the placement of selection within different variants of the Moran process affects stationary distributions in finite, well-mixed haploid populations with recurrent mutation. They compare three update kernels—selection during reproduction (Scheme I), fitness-biased mate choice followed by neutral copying (Scheme II), and selection at death (Scheme III)—showing that while all three favor fitter alleles, they define distinct Markov chains with different stationary laws even in the two-allele case. For three or more alleles, Schemes I and II are generally nonreversible when fitnesses are unequal, meaning no detailed-balance product form exists, whereas Scheme III remains reversible and admits a closed-form Dirichlet-multinomial stationary distribution modified by an explicit fitness factor. The authors further demonstrate that all three mechanisms can operate simultaneously in the two-allele case without losing exact solvability, deriving weak-selection expansions that show how small fitness differences tilt neutral beta-binomial and Dirichlet-multinomial benchmarks. This work contributes to population genetics theory rather than applied biotech or clinical research.

---

### Dimension-dependent continuum limits in tissue mechanics
**Priority:** low | **Tags:** tissue engineering, computational biology
**URL:** https://arxiv.org/abs/2607.07000

Matthew Simpson and Pascal Buenzli demonstrate that spatial dimensionality mathematically controls the relationship between cell-scale forces and tissue-scale transport in epithelial tissues. Their work shows long-time mechanical relaxation rates reveal generalized porous-media-type nonlinear transport phenomena, where diffusivity scales as D(ρ)∝ρ^γ with exponents fixed by microscopic mechanics and dimensionality. The finding provides a physical mechanism for emergent macroscopic transport behavior observed across biological systems. For biotech operators, this work bridges individual-based agent simulations to tractable continuum models when designing engineered tissues or interpreting organoid growth dynamics. As tissue engineering matures toward commercial-scale products, having predictive equations that collapse simulation complexity from per-cell tracking to field-based PDEs represents a meaningful computational leverage point for the tissue engineering pipeline.

---

### Enhanced sampling and cryo-EM data resolve magnesium binding to RNA
**Priority:** low | **Tags:** computational-biophysics, rna-structure, molecular-dynamics, cryo-em, ion-solvation
**URL:** https://arxiv.org/abs/2607.07186

Researchers Olivier Languin-Cattoën, Elisa Posani, and Giovanni Bussi present an enhanced-sampling methodology that accelerates magnesium ion (Mg2+) inner-shell binding to RNA by orders of magnitude. The approach combines barrier-flattening bias with Hamiltonian replica exchange to efficiently explore multiple equivalent binding sites in a large ribozyme, building on a method that ranked in the top at CASP16 for blind assessment of RNA solvation structure. Using cryo-electron microscopy density maps for validation, they develop a framework that infers population of individual binding motifs from experimental agreement on a site-by-site basis. They demonstrate that insufficient sampling of inner-shell binding leads to significantly poorer agreement with experiment, while force fields predicting different inner/outer binding equilibria remain indistinguishable at current cryo-EM resolution. These findings reveal the dominant role of sampling quality over force-field tuning in modeling divalent ion binding to RNA.

---

### Bayesian Learning of Distance Metrics Beyond RMSD for Biomolecule Alignment, Clustering, and Domain Identification
**Priority:** medium | **Tags:** computational-biology, structural-biology
**URL:** https://arxiv.org/abs/2607.07352

Researchers Saumyak Mukherjee and Gerhard Hummer introduce BRMSD (Bayes-optimal RMSD), a new computational framework that addresses a fundamental limitation in molecular dynamics structural comparison: classical RMSD gives equal weight to all atoms, allowing flexible loops and disordered regions to dominate global metrics while the rigid functional core contributes negligibly. The approach optimizes per-atom weights jointly with structural averages through Bayesian posterior maximization, using a position-fluctuation parameter sigma that transitions behavior from classical RMSD toward focused analysis on rigid cores. BRMSD provides modules for structural alignment, domain-focused alignment onto user-specified regions, trajectory smoothing, soft K-means conformational clustering, and automated rigid-domain identification—all packaged as an open-source Python tool. The framework was benchmarked on two molecular dynamics systems: the endoplasmic reticulum translocon-associated protein SND3 and the phosphotransferase adenylate kinase.

---

### Reliable mechanistic operator recovery with biologically-informed neural networks: principles for architecture and optimisation design
**Priority:** medium | **Tags:** computational-biology, deep-learning-methods, differential-equations
**URL:** https://arxiv.org/abs/2607.07425

Crossley, Yin, Waters, and Baker present a systematic empirical study of biologically-informed neural networks (BINNs), which embed mechanistic differential equations into neural network training to recover interpretable constitutive operators from sparse and noisy observational data. Using canonical 1D advection-diffusion-reaction PDE models as benchmarks, the authors systematically vary network expressivity, learning rate, loss weighting, and batch size to determine how each factor influences optimization behaviour and operator recovery accuracy. They find that moderately expressive architectures outperform overly complex networks, intermediate learning rates improve optimization stability, balanced data-vs-PDE loss weighting is essential for accurate recovery, and moderate batch sizes offer the best compromise between computational efficiency and reproducibility. The paper also identifies practical diagnostics for recognizing common failure modes—overfitting, unstable optimization, and poor mechanistic recovery when ground truth is unavailable—providing evidence-based deployment guidelines for BINN practitioners.

---

### Single-Entity Spiking Neuron Models: Survey
**Priority:** low | **Tags:** computational-neuroscience, survey
**URL:** https://arxiv.org/abs/2607.07429

Parepko, Shulepin, and Nasybullin survey mathematical modeling approaches for biologically plausible neural systems, classifying them by shared features and specialized use cases. The paper reviews spiking neuron models alongside discrete and continuous analogs aimed at accurately simulating biological processes such as membrane potential dynamics. It examines individual neurons and the various components within neural systems that influence their dynamics, selecting approaches based on prevalence and innovation potential to improve simulation fidelity. As a literature review published at the 2023 DCNA conference and cross-listed under both cs.NE and q-bio.NC, it serves as a reference for researchers building computational models of brain tissue. This is an academic survey with no named pharmaceutical companies, drugs, trials, or commercial deals.

---

### Collaborate to decorrelate in path space: Hamiltonian replica exchange transition interface sampling (HRETIS)
**Priority:** low | **Tags:** molecular simulation, computational chemistry
**URL:** https://arxiv.org/abs/2607.07453

Sina Safaei, Parham Rezaee, and An Ghysels present HRETIS, a novel path-sampling framework for computing kinetics of rare events in molecular systems with complex energy landscapes. The method introduces a helper potential inside a Hamiltonian replica exchange scheme, allowing multiple replicas to exchange Hamiltonians so that path ensembles better explore orthogonal conformational barriers. This design specifically targets systems like drug (un)binding where standard algorithms get trapped within individual pathways and converge slowly. A key demonstration involves coarse-grained simulations of amino acid permeation through a dipalmitoylphosphatidylcholine (DPPC) membrane, showing improved sampling efficiency and robust kinetic estimates. For biotech operators managing molecular simulation pipelines, HRETIS offers a potentially faster route to accurate binding/unbinding rate predictions compared with conventional rare-event samplers.


---

### Equivalence testing in pesticide risk assessment -- Evaluation and practical guidance for design, analysis and interpretation
**Priority:** medium | **Tags:** statistical methodology, pesticide regulation, bee ecology, risk assessment
**URL:** https://arxiv.org/abs/2607.07543

Researchers Wintermantel, Osterman, Mair, and Hartig evaluate statistical methodology for European Food Safety Authority (EFSA) honeybee pesticide risk assessments. They demonstrate that regulatory field studies have been statistically underpowered, potentially leading to approval of ecologically harmful pesticides. The paper simulates regulatory-grade honeybee trials to compare two equivalence testing approaches against EFSA's stated 10% colony size reduction protection goal (SPG). Results show only EFSA's original approach reliably identifies pesticides exceeding SPG at alpha=0.2, while a proposed alternative based on the lower bound of the control-group confidence interval does not perform equivalently. The authors provide R functions for anticlustering randomization and equivalence testing to reduce site-level replication requirements without sacrificing statistical power.

---

### Directional bias of a single polarized cell under confinement
**Priority:** low | **Tags:** cell biophysics, synthetic biology, cell migration
**URL:** https://arxiv.org/abs/2607.07578

Andreas Buttenschön and Calina Copos present a theoretical framework using dynamical systems analysis and computer simulations to explain how chiral (handed) cell motion arises in confined geometries. The paper identifies four distinct physical mechanisms that generate persistent directional bias: intrinsic torque within the polarized cytoskeleton, anisotropic cell-substrate friction coupled to a directional offset, a chiral wall-alignment response at boundaries, and mirror-symmetry-breaking substrate patterns such as dextral or sinistral ridges. These mechanisms converge on a unifying principle—directional bias emerges through shifts in the stability basins of attraction between clockwise and counter-clockwise motility states. The findings produce distinct testable predictions for experiments studying cellular chirality, including implications for understanding tissue morphogenesis, cytoskeletal organization, and engineered synthetic systems designed to exhibit programmable chiral motion.

---

### A hierarchical memory architecture overcomes context limits in long-horizon multi-agent computational modeling
**Priority:** medium | **Tags:** AI-for-drug-development, multi-agent-systems, QSP-pharmacokinetics
**URL:** https://arxiv.org/abs/2607.07666

Shivendra G. Tewari and Holly Kimko present Ensemble QSP, a multi-agent framework that applies a three-layer hierarchical memory architecture to enable sustained autonomous operation of large language models in quantitative systems pharmacology (QSP) workflows. The system assigns five specialist worker agents under domain-expert principal investigator oversight, enforcing physical constraints through physics-based checklists and structured-domain knowledge injection. Context remains bounded and constant irrespective of project duration by capping each state category and evicting completed work, keeping mid-term project states at a median of 301 tokens (maximum 4,050) across 104 benchmark runs. Comprehensive evaluation shows robust autonomous PK-PD model selection without human intervention, improved PK parameter recovery relative to single-agent baselines, and stable performance across diverse LLM tiers and linguistically varied prompts. Feature-level ablation of PBPK models demonstrates that PI-agent oversight improves debugging efficiency while preserving final modeling accuracy.

---

### Rethinking the Choice Behavior of Sugar Metabolism in Bacteria
**Priority:** medium | **Tags:** metabolic engineering, synthetic biology, systems biology
**URL:** https://arxiv.org/abs/2607.07677

Jeffrey D. Varner (Cornell University) recasts the decades-old cybernetic model of microbial enzyme synthesis into a formal linear programming framework drawn from microeconomic consumer theory. The model treats bacterial cells as rational actors allocating a limited proteome budget among competing catabolic enzymes to maximize a linear growth utility function subject to a fixed protein budget constraint. Because the utility is linear, the optimal solution is generically a corner solution—allocating the entire proteome to the single most profitable substrate—which geometrically explains diauxic (sequential) growth without invoking any distinct regulatory switching mechanism. Simultaneous co-utilization of multiple sugars arises only as a degenerate case when two substrates achieve equal profitability, causing iso-utility and budget-constraint slopes to coincide. The authors validated the LP framework on Klebsiella oxytoca batch cultures with glucose-xylose and glucose-xylose-lactose mixtures, reproducing diauxic and triauxic growth curves with accuracy comparable to the classical matching law, using parameters estimated independently from single-substrate experiments.

---

### Immunoinformatics-Guided Design and In Silico Evaluation of a Multi-Epitope Vaccine Against Influenza A H10N5 and H3N2 Strains Based on Hemagglutinin and Neuraminidase Proteins
**Priority:** medium | **Tags:** influenza vaccine, computational vaccinology, multi-epitope design, pandemic preparedness
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.03.736294v1

A multidisciplinary team led by Muhammad Zeeshan Shabbir at BioMind Research Institute has computationally designed and validated a multi-epitope subunit vaccine targeting conserved hemagglutinin (HA) and neuraminidase (NA) proteins shared by seasonal Influenza A H3N2 and the zoonotic H10N5 strain. The 419-amino-acid construct integrates predicted B-cell, CTL, and HTL epitopes alongside an avian beta-defensin adjuvant, with in silico evaluation yielding picomolar-range binding affinity to TLR3 and TLR7, strong structural stability confirmed by molecular dynamics, and successful codon optimization for E. coli expression. If validated experimentally, this computational vaccine candidate could address a critical gap: no current platform co-targets seasonal H3N2 influenza and the recently emerged zoonotic H10N5 threat—a subtype linked to the first confirmed human fatality in January 2024—potentially accelerating pan-influenza countermeasure development for pandemic preparedness.

---

### The hepatic mitochondrial landscape
**Priority:** low | **Tags:** liver metabolism, mitochondrial biology
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.03.736316v1

Researchers from the University of Maribor and EPFL Lausanne mapped how mitochondrial-encoded and nuclear-encoded genes supporting mitochondrial function vary across spatial gradients within the liver lobule and along the feeding-fasting cycle in mice. Combining transcriptomics with quantitative measurements of mitochondrial morphology, they found that hepatocyte subtypes diverge markedly based on mitochondrial gene expression—including a subset with exceptionally low mitochondrial transcripts and reduced secretory protein output—while periportal oxidative phosphorylation is driven by a disproportionately high mitochondrial transcript fraction localized to the cytoplasm. In human samples, higher periportal mitochondrial transcript abundance was recapitulated, and mitochondrial-function genes showed rhythmic expression patterns that were more pronounced in women. Together these data establish a spatially and temporally resolved reference dataset for hepatic mitochondrial regulation.

---

### SARS-CoV-2 membrane protein conformations induce distinct membrane curvatures
**Priority:** medium | **Tags:** Virology, Biophysics, SARS-CoV-2, Membrane Biophysics, Computational Biology
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.06.736641v1

Researchers Joseph McTiernan, Roya Zandi, Michael E. Colvin, and Ajay Gopinathan at the University of California (Merced and Riverside) used all-atom and Martini coarse-grained molecular dynamics simulations to demonstrate that the SARS-CoV-2 membrane (M) protein exists in two conformations—short and long—that each induce distinct membrane curvatures. The long form bends the membrane into a valley-like depression consistent with a budding virion's bulb region, while the short form produces an anisotropic ridge matching the virion's neck region. Coarse-grained simulations of M protein pairs revealed that these differing curvatures modulate long-range, membrane-mediated interactions between proteins, causing repulsion between dissimilar conformations that drives their natural segregation. This physical mechanism explains how the two M-protein forms self-organize to shape the virion's bulb and neck during assembly through the ERGIC membrane, potentially facilitating both genome encapsulation and membrane scission. The work provides a general biophysical framework suggesting that conformationally encoded curvature fields may be a universal principle underlying enveloped virus budding.

---

### Tis But a Scratch! Negligible fitness costs of AalDV2 infection in Aedes albopictus under fluctuating temperatures and implications for viral biocontrol
**Priority:** medium | **Tags:** mosquito biocontrol, viral vector control
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.06.736729v1

Researchers at ISEM (CNRS, IRD) in Montpellier tested whether the mosquito densovirus AalDV2 could serve as an effective biological control agent against Aedes albopictus, a major vector for arboviral diseases, under ecologically realistic fluctuating temperatures. Under 32-34°C thermal stress, chronic heat exposure alone significantly reduced mosquito median lifespan by approximately 10 days and increased pupal mortality — but AalDV2 infection inflicted negligible additional fitness costs: no significant effect on overall survival, stage-specific mortality, or adult lifespan was detected. A key interaction emerged: under the hottest regime (32-34°C), AalDV2-infected females showed prolonged larval and pupal development, extending their aquatic stage without increasing mortality. For biocontrol operators, this means AalDV2 lacks the lethal efficacy needed for direct population suppression, but the thermal-stress-dependent prolongation of mosquito development could indirectly alter disease transmission dynamics by keeping vectors in vulnerable aquatic stages longer — an effect that requires further investigation before field deployment.

---

### Emergence of large-scale polar microtubule swarms for dense molecular transport
**Priority:** medium | **Tags:** biophysics, bioengineering, synthetic-biology, drug-delivery
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.06.736790v1

Researchers at Princeton University (Meisam Zaferani, Ned S. Wingreen, Howard A. Stone, and Sabine Petry) demonstrated that dynamic self-amplifying branched microtubule networks, driven by kinesin-1 and cytoplasmic dynein motor proteins, can undergo collective swarming to form large-scale polar and orientationally aligned architectures on surfaces. The resulting microtubule bundles are dense, span millimeter scales, and persist for hours — overcoming a key limitation of prior reconstituted active-matter systems that relied on fixed-length filaments with no capacity for growth or regeneration. Critically, this emergent polarity enables molecular transport at high throughput: the team demonstrated up to six million motor complexes walking in parallel across millimeter-scale distances over hours, an order of magnitude beyond static microtubule-based transport platforms. For biotech operators and investors, these findings point toward a new paradigm for engineering scalable programmable soft materials and nanoscale transport systems with high molecular-cargo capacity, potentially relevant to drug delivery scaffolds, biosensing networks, and synthetic intracellular architectures.

---

### Low-molecular-weight Ulva lacinulata extract exhibiting anti-inflammatory and pro-autophagic activities in RAW 264.7 macrophages: a promising candidate for the development of active ingredients targeting low-grade inflammation
**Priority:** low | **Tags:** marine_bioactives, anti_inflammation, nutraceuticals
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.07.734444v1

Researchers from SEPROSYS, Abyss Ingredients, and multiple French research institutes (LIENSs, Nutrineuro) investigated a low-molecular-weight extract derived from the green macroalga Ulva lacinulata for its potential as a functional ingredient targeting chronic low-grade inflammation. Comprehensive compositional analysis using high-resolution mass spectrometry revealed the extract contains diverse bioactive molecules including peptides, amino acid derivatives, saccharides, fatty diacids, oxylipins, and minerals. In LPS-stimulated RAW 264.7 macrophages pre-treated for 6 hours, the extract dose-dependently reduced pro-inflammatory cytokines TNF-alpha and IL-6 while targeting the NF-kB signaling cascade. The extract also modulated the SIRT1-AMPK signaling axis and increased the LC3-II/LC3-I ratio, indicating activation of a controlled autophagic response that may support cellular homeostasis in inflammatory contexts. Funded by Bpifrance (grant NDOS0201317/00), this preprint positions marine-derived bioactive extracts as promising nutraceutical candidates for dietary supplements addressing age-related inflammation.

---

### Genome-wide meQTL mapping in cattle blood reveals cis and trans regulation of DNA methylation
**Priority:** medium | **Tags:** epigenetics, livestock genomics
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.07.736355v1

Researchers at Eliance and Valogene performed the largest-scale meQTL (methylation quantitative trait locus) mapping study in any livestock species, analyzing whole blood from 4,457 genotyped Holstein cows using the EpiChip epigenotyping array across 43,317 CpG sites. They estimated average DNA methylation heritability at 24.6% and found that cis-meQTLs regulate 80.1% of variable CpG sites, with sentinel SNPs clustered near their target regions. A two-step trans-meQTL analysis identified 31 genomic hotspots controlling up to 530 distant CpG sites each; three mapped near transcription factor genes (RUNX1, NFIC, FOXA3) whose DNA-binding motifs were enriched among regulated CpGs, while two others reside within KDM5A and KDM5B epigenetic regulators. These findings establish a regulatory blueprint for DNA methylation in cattle blood that is broadly applicable to understanding mammalian gene regulation more generally.

---

### Microscale assay to evaluate the minimum inhibitory concentration of purified compounds with limited sample volume
**Priority:** medium | **Tags:** antimicrobial, drug-discovery, microbiology, methodology
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.07.737130v1

Researchers Shashank Kashyap and Sumit Biswas at BITS Pilani Goa present a microscale protocol for determining the minimum inhibitory concentration (MIC) of antimicrobial compounds using minimal sample volumes. The method adapts standard microplate-based assays with two-fold serial dilutions to reduce reagent consumption, enabling MIC testing when only small quantities of purified compound are available—such as early-stage natural product isolates. The authors validated the approach by measuring kanamycin MIC against four bacterial strains (Staphylococcus aureus, Vibrio fischeri, Klebsiella pneumoniae, and Escherichia coli) and found results consistent with conventional broth microdilution. This protocol addresses a bottleneck in antimicrobial drug discovery where researchers need comprehensive microbiological assessment of scarce purified compounds but lack the volume standard MIC assays demand.

---

### Molecular Structure, DNA Binding, and Photophysical Properties of SYTOX Orange and SYTOX Green
**Priority:** medium | **Tags:** molecular biology, fluorescent dyes, DNA mechanics, single-molecule assays, biophysics
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.08.737150v1

A team at the University of Augsburg (led by Jan Lipfert) with collaborators from Utrecht University, LMU Munich, and TU Munich has definitively determined the molecular structures of SYTOX Orange and SYTOX Green, two widely used cyanine fluorescent dyes. SYTOX Orange was structurally characterized as a unique intermediate between SYBR Gold and other SYTOX family dyes, while SYTOX Green was found to be similar in structure to PicoGreen. Using magnetic tweezers, the authors measured DNA unwinding angles of 21.1 deg for SYTOX Orange and 20.5 deg for SYTOX Green, confirming intercalation as the binding mechanism. Critically, both dyes leave DNA bending persistence length and plectoneme size virtually unchanged (<10% change up to 1 uM), meaning they are well-suited for single-molecule assays probing DNA supercoiling without introducing confounding mechanical artifacts.

---

### Graph neural network modeling of receptor interaction kinetics from single-molecule imaging data
**Priority:** medium | **Tags:** computational-biology, drug-discovery-tools, cell-signaling, AI-methods
**URL:** https://www.biorxiv.org/content/10.64898/2026.07.08.737174v1

Researchers Khai Nguyen and Khuloud Jaqaman at UT Southwestern Medical Center, supported by NIH grant R35 GM119619, introduce Deep-FISIK — a computational method that uses graph neural networks with multi-head attention for message-passing to predict homotypic receptor interaction kinetics from single-molecule imaging (SMI) data. The key technical advance is that Deep-FISIK operates on SM detection outputs without requiring explicit molecule tracking, making it compatible with higher-labeling-fraction SMI experiments and thus improving prediction accuracy of interaction kinetic parameters over prior substoichiometricly-labeled approaches. The method demonstrates robustness across deviations from training data, suggesting applicability to diverse receptor systems and SMI experimental setups. This tool could enable computational drug discovery teams to derive more accurate binding and dissociation kinetics for membrane receptor targets without the experimental limitations traditionally imposed by sparse single-molecule labeling.

---

### #ADA25: Lilly’s bimagrumab boosts weight and fat loss whe...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/ada25-lillys-bimagrumab-boosts-weight-and-fat-loss-when-added-to-novos-wegovy

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/ada25-lillys-bimagrumab-boosts-weight-and-fat-loss-when-added-to-novos-wegovy/&title=%23ADA25%3A%20Lilly%E2%80%99s%20bimagrumab%20boosts%20weight%20and%20fat%20loss%20when%20added%20to%20Novo%27s%20Wegovy&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=%23ADA25%3A%20Lilly%E2%80%99s%20bimagrumab%20boosts%20weight%20and%20fat%

---

### Angelini fortifies neurology portfolio with $4.1B buyout ...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/angelini-fortifies-neurology-portfolio-with-4-1b-buyout-of-catalyst-pharma

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/angelini-fortifies-neurology-portfolio-with-4-1b-buyout-of-catalyst-pharma/&title=Angelini%20fortifies%20neurology%20portfolio%20with%20%244.1B%20buyout%20of%20Catalyst&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Angelini%20fortifies%20neurology%20portfolio%20with%20%244.1B%20buyout%20of%20Catalyst%20-%20https://endpoint

---

### Anti-aging biotech NewLimit raises $435M at $3B+ valuation
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/anti-aging-biotech-newlimit-raises-435m-at-3b-valuation

![](https://endpoints.news/wp-content/uploads/2025/05/GettyImages-2194507758-scaled.jpg) NewLimit co-founder Brian Armstrong (Photographer: Stefan Wermuth/Bloomberg via Getty Images) [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/anti-aging-biotech-newlimit-raises-435m-at-3b-valuation/&title=Anti-aging%20biotech%20NewLimit%20raises%20%24435M%20at%20%243B%2B%20valuation&source=https://endpoints.news/ "Share on LinkedIn")[Share on

---

### Biopharma’s top-paid CEOs of 2025: 25 making $25M+
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/biopharmas-top-paid-ceos-of-2025-25-making-25m

![](https://endpoints.news/wp-content/uploads/2026/06/ceo_pay_2025_fi@2x-1.jpg) [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/biopharmas-top-paid-ceos-of-2025-25-making-25m/&title=Biopharma%27s%20top-paid%20CEOs%20of%202025%3A%2025%20making%20%2425M%2B%C2%A0&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Biopharma%27s%20top-paid%20CEOs%20of%202025%3A%2025%20making%20%2

---

### Chinese startup begins first clinical trial using CRISPR ...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/chinese-startup-begins-first-clinical-trial-using-crispr-to-edit-cells-directly-in-the-bone-marrow

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/chinese-startup-begins-first-clinical-trial-using-crispr-to-edit-cells-directly-in-the-bone-marrow/&title=Chinese%20startup%20begins%20first%20clinical%20trial%20using%20CRISPR%20to%20edit%20cells%20directly%20in%20the%20bone%20marrow&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Chinese%20startup%20begins%20first%20clinic

---

### Exclusive: Forbion-backed cardio biotech rebrands to RyCa...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/exclusive-forbion-backed-cardio-biotech-rebrands-to-rycarma-with-phase-2-plans

![](https://endpoints.news/wp-content/uploads/2025/01/Adam-Rosenberg-RyCarma-feature.jpg) Adam Rosenberg, RyCarma Therapeutics CEO [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/exclusive-forbion-backed-cardio-biotech-rebrands-to-rycarma-with-phase-2-plans/&title=Exclusive%3A%20Forbion-backed%20cardio%20biotech%20rebrands%20to%20RyCarma%20with%20Phase%202%20plans&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitte

---

### Genmab halts enrollment for cancer drug from ProfoundBio ...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/genmab-halts-enrollment-for-cancer-drug-from-profoundbio-buyout

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/genmab-halts-enrollment-for-cancer-drug-from-profoundbio-buyout/&title=Genmab%20halts%20enrollment%20for%20cancer%20drug%20from%20ProfoundBio%20buyout&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Genmab%20halts%20enrollment%20for%20cancer%20drug%20from%20ProfoundBio%20buyout%20-%20https://endpoints.news/genmab-halts-enrol

---

### Merck winds down TIGIT, LAG-3 programs meant to temper Ke...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/merck-winds-down-tigit-lag-3-programs-meant-to-temper-keytruda-erosion

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/merck-winds-down-tigit-lag-3-programs-meant-to-temper-keytruda-erosion/&title=Merck%20winds%20down%20TIGIT%2C%20LAG-3%20programs%20meant%20to%20temper%20Keytruda%20erosion&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Merck%20winds%20down%20TIGIT%2C%20LAG-3%20programs%20meant%20to%20temper%20Keytruda%20erosion%20-%20https:

---

### NEJM retracts pivotal data for Amgen’s Tavneos
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/nejm-retracts-pivotal-data-for-amgens-tavneos

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/nejm-retracts-pivotal-data-for-amgens-tavneos/&title=NEJM%20retracts%20pivotal%20data%20for%20Amgen%27s%20Tavneos&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=NEJM%20retracts%20pivotal%20data%20for%20Amgen%27s%20Tavneos%20-%20https://endpoints.news/nejm-retracts-pivotal-data-for-amgens-tavneos/ "Share on Twitter") June 29

---

### Novo Nordisk pays $200M upfront for United Laboratories I...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/novo-nordisk-pays-200m-upfront-for-united-laboratories-international-holdings-triple-g-obesity-shot

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/novo-nordisk-pays-200m-upfront-for-united-laboratories-international-holdings-triple-g-obesity-shot/&title=Novo%20Nordisk%20pays%20%24200M%20upfront%20for%20United%20Laboratories%20International%20Holdings%27%20triple-G%20obesity%20shot&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Novo%20Nordisk%20pays%20%24200M%20upfront

---

### ObesityWeek rode the momentum of the field’s most dramati...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/obesityweek-rode-the-waves-of-the-fields-most-dramatic-week-in-months

![](https://endpoints.news/wp-content/uploads/2025/11/Obesity-Week-Atlanta-Credit_-Kyle-LaHucik-11.jpg) Credit: Kyle LaHucik [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/obesityweek-rode-the-waves-of-the-fields-most-dramatic-week-in-months/&title=ObesityWeek%20rode%20the%20momentum%20of%20the%20field%27s%20most%20dramatic%20week%20in%20months&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.

---

### PacBio, once slated to be acquired by Illumina, is taking...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/pacbio-once-slated-to-be-acquired-by-illumina-is-taking-on-the-dna-giant

![](https://endpoints.news/wp-content/uploads/2022/07/illumina_fi.jpg) [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/pacbio-once-slated-to-be-acquired-by-illumina-is-taking-on-the-dna-giant/&title=PacBio%2C%20once%20slated%20to%20be%20acquired%20by%20Illumina%2C%20is%20taking%20on%20the%20DNA%20giant&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=PacBio%2C%20once%20sla

---

### Pfizer buys China rights to Sciwind’s approved GLP-1 drug...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/pfizer-buys-china-rights-to-sciwinds-approved-glp-1-drug-in-metabolic-push

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/pfizer-buys-china-rights-to-sciwinds-approved-glp-1-drug-in-metabolic-push/&title=Pfizer%20buys%20China%20rights%20to%20Sciwind%E2%80%99s%20approved%20GLP-1%20drug%20in%20metabolic%20push&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Pfizer%20buys%20China%20rights%20to%20Sciwind%E2%80%99s%20approved%20GLP-1%20drug%20in%20m

---

### Riding the wave on latest obesity buyout; Slack interview...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/riding-the-wave-on-latest-obesity-buyout-slack-interview-with-anti-aging-researcher-two-new-ira-lawsuits-and-more

![](https://endpoints.news/wp-content/uploads/2021/05/endpts_weekly_FI@x2.jpg) [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/riding-the-wave-on-latest-obesity-buyout-slack-interview-with-anti-aging-researcher-two-new-ira-lawsuits-and-more/&title=Riding%20the%20wave%20on%20latest%20obesity%20buyout%3B%20Slack%20interview%20with%20anti-aging%20researcher%3B%20Two%20new%20IRA%20lawsuits%3B%20and%20more&source=https://endpoints.news

---

### Roche’s TIGIT drug tiragolumab fails Phase 3 lung cancer ...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/roches-tigit-drug-tiragolumab-fails-phase-3-lung-cancer-trial

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/roches-tigit-drug-tiragolumab-fails-phase-3-lung-cancer-trial/&title=Roche%E2%80%99s%20TIGIT%20drug%20tiragolumab%20fails%20Phase%203%20lung%20cancer%20trial&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=Roche%E2%80%99s%20TIGIT%20drug%20tiragolumab%20fails%20Phase%203%20lung%20cancer%20trial%20-%20https://endpoints.news/ro

---

### The very slow roll of Biogen’s Aduhelm: Neurologists weig...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/the-very-slow-roll-of-biogens-aduhelm-neurologists-weigh-in-on-patients-practices-and-payments-amid-ongoing-media-storm

[Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/the-very-slow-roll-of-biogens-aduhelm-neurologists-weigh-in-on-patients-practices-and-payments-amid-ongoing-media-storm/&title=The%20very%20slow%20roll%20of%20Biogen%27s%20Aduhelm%3A%20Neurologists%20weigh%20in%20on%20patients%2C%20practices%20and%20payments%20amid%20ongoing%20media%20storm&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/inte

---

### Tourmaline attracted small bidding war before $1.4B sale ...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/tourmaline-attracted-small-bidding-war-before-1-4b-sale-to-novartis

![](https://endpoints.news/wp-content/uploads/2023/06/Sandeep-Kulkarni.jpg) Sandeep Kulkarni, Tourmaline Bio CEO [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/tourmaline-attracted-small-bidding-war-before-1-4b-sale-to-novartis/&title=Tourmaline%20attracted%20small%20bidding%20war%20before%20%241.4B%20sale%20to%20Novartis&source=https://endpoints.news/ "Share on LinkedIn")[Share on Twitter](https://twitter.com/intent/tweet?text=T

---

### Weeks after launch, Alex Zhavoronkov’s AI-inspired longev...
**Priority:** low | **Tags:** N/A
**URL:** https://endpoints.news/weeks-after-launch-alex-zhavoronkovs-ai-inspired-longevity-spinout-sells-to-hong-kong-listed-group

![](https://endpoints.news/wp-content/uploads/2020/07/Alex-Zhavoronkov-Insilico-tile-scaled.jpg) Alex Zhavoronkov (Insilico) [Share on LinkedIn](http://www.linkedin.com/shareArticle?mini=true&url=https://endpoints.news/weeks-after-launch-alex-zhavoronkovs-ai-inspired-longevity-spinout-sells-to-hong-kong-listed-group/&title=Weeks%20after%20launch%2C%20Alex%20Zhavoronkov%27s%20AI-inspired%20longevity%20spinout%20sells%20to%20Hong%20Kong-listed%20group&source=https://endpoints.n

---

### Will CRISPR matter?
**Priority:** low | **Tags:** CRISPR, gene editing, in vivo therapies, ex vivo editing
**URL:** https://endpoints.news/topic-hub/crispr-and-gene-editing-the-push-for-in-vivo-therapies/page/365

This page is the 365th entry of Endpoints News's massive topic hub on CRISPR and in vivo gene editing, not a standalone article. Its top story, 'Will CRISPR matter?,' surveys how gene editing has transitioned from lab bench to clinic, chronicling Casgevy (Vertex/CRISPR Therapeutics) as the _ex vivo_ proof-of-concept for sickle cell disease and profiling the emerging race for in vivo therapies that edit genes inside the body. Key players mentioned include Jennifer Doudna's Azalea Therapeutics, Patrick Hsu's Stylus Medicine advancing gene writing and epigenetic editing platforms, and Chinese competitors YolTech and AccurEdit scaling their programs. The page itself is a directory with article links spanning years of R&D milestones, financing rounds, clinical trial failures, M&A activity across the broader biotech sector.

---

