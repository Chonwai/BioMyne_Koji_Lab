[Skip to main content](https://www.biorxiv.org/content/10.64898/2026.07.05.736646v1#main-content)

New Results  Follow this preprint

# PINPOINT: Protease INhibitor PredictiOn at the plant–pathogen INTerface using protein language models and structural modeling

[View ORCID Profile](http://orcid.org/0000-0002-0600-4534) MuthusaravananSivaramakrishnan, [View ORCID Profile](http://orcid.org/0000-0001-5696-6777) BalakumaranChandrasekar

doi: https://doi.org/10.64898/2026.07.05.736646

This article is a preprint and has not been certified by peer review \[ [what does this mean?](https://www.biorxiv.org/about/FAQ#unrefereed)\].

Muthusaravanan Sivaramakrishnan

1 Department of Biological Sciences, Birla Institute of Technology and Science, Pilani (BITS Pilani), Rajasthan, India;


- [Find this author on Google Scholar](https://www.biorxiv.org/lookup/google-scholar?link_type=googlescholar&gs_type=author&author%5B0%5D=Muthusaravanan%2BSivaramakrishnan%2B "Open in new tab")
- [Find this author on PubMed](https://www.biorxiv.org/lookup/external-ref?access_num=Sivaramakrishnan%20M&link_type=AUTHORSEARCH "Open in new tab")
- [Search for this author on this site](https://www.biorxiv.org/search/author1%3AMuthusaravanan%2BSivaramakrishnan%2B)
- [ORCID record for Muthusaravanan Sivaramakrishnan](http://orcid.org/0000-0002-0600-4534 "Open in new tab")

Balakumaran Chandrasekar

2 Department of Bioscience and Bioengineering, Indian Institute of Technology Jodhpur (IIT Jodhpur), Jodhpur, Rajasthan, India


- [Find this author on Google Scholar](https://www.biorxiv.org/lookup/google-scholar?link_type=googlescholar&gs_type=author&author%5B0%5D=Balakumaran%2BChandrasekar%2B "Open in new tab")
- [Find this author on PubMed](https://www.biorxiv.org/lookup/external-ref?access_num=Chandrasekar%20B&link_type=AUTHORSEARCH "Open in new tab")
- [Search for this author on this site](https://www.biorxiv.org/search/author1%3ABalakumaran%2BChandrasekar%2B)
- [ORCID record for Balakumaran Chandrasekar](http://orcid.org/0000-0001-5696-6777 "Open in new tab")
- For correspondence:
[balakumaran@iitj.ac.in](mailto:balakumaran@iitj.ac.in)

- [Abstract](https://www.biorxiv.org/content/10.64898/2026.07.05.736646v1)
- [Info/History](https://www.biorxiv.org/content/10.64898/2026.07.05.736646v1.article-info)
- [Metrics](https://www.biorxiv.org/content/10.64898/2026.07.05.736646v1.article-metrics)
- [Supplementary material](https://www.biorxiv.org/content/10.64898/2026.07.05.736646v1.supplementary-material)
- [Data/Code](https://www.biorxiv.org/content/10.64898/2026.07.05.736646v1.external-links)
- [Preview PDF](https://www.biorxiv.org/content/10.64898/2026.07.05.736646v1.full.pdf+html)

![Loading](https://www.biorxiv.org/sites/all/modules/contrib/panels_ajax_tab/images/loading.gif)

## Abstract

Cysteine and serine proteases act as an immune hub in the plant apoplast to provide robust extracellular immunity during microbial colonisation. Microbial pathogens counteract these immune proteases by inhibiting their activity using small secreted proteins (SSPs). Traditionally, SSPs with protease-inhibitory activity are predicted using sequence-dependent database searches. However, in recent years, fungal SSPs have been shown to exhibit protease-inhibitory functions despite lacking the inhibitor domain that is annotated through sequence similarity searches. Hence, a large number of these novel SSPs with putative protease inhibitor functions are missed during detection and filtered out during sequence similarity searches. This necessitates the development of newer approaches to predict SSPs lacking an annotated inhibitor domain. Machine learning approaches, such as protein language models, have emerged as powerful tools for predicting protein functions. To date, no machine learning models have been developed to predict the protease-inhibitory activities of SSPs lacking an annotated inhibitor domain. Here, we introduce a protease inhibitor prediction pipeline, PINPOINT (Protease INhibitor PredictiOn at plant–pathogen INTerface). The PINPOINT pipeline combines fine-tuned protein language model classifiers, a structure-aware autoencoder, and effector prediction into a multi-level framework for identifying SSPs with predicted protease inhibitor functions. PINPOINT predicts protease inhibitors using SSPs sequences and monomeric structures with pre-computed structures obtained from the AlphaFold Protein Structure Database or predicted using the ESMFold public API. We successfully validated the PINPOINT platform using SSPs from the plant fungal pathogen Macrophomina phaseolina. Notably, the PINPOINT platform robustly predicted several of these SSPs as protease inhibitors including Sequence-unrelated but structurally similar (SUSS) effectors. We further validated the inhibitory potential of these predicted M. phaseolina SSPs using AlphaFold Multimer (AFM) screening against candidate apoplastic soybean cysteine and serine proteases. Additionally, this platform can be used as a pre-filtering step in AFM screening approaches to reduce the number of candidates for discovering novel SSPs with protease inhibitor function for cross-kingdom plant-microbe interaction studies. The PINPOINT platform will accelerate the prediction of novel SSPs including SUSS effectors with protease inhibitor functions in proteomes of any organisms. We made the PINPOINT pipeline accessible to the research community as a web-based notebook environment for interactive computing in Google Colab, available at https://github.com/iitj-mpg-lab/PINPOINT

### Competing Interest Statement

The authors have declared no competing interest.

## Footnotes

- [https://github.com/iitj-mpg-lab/PINPOINT](https://github.com/iitj-mpg-lab/PINPOINT)


## Funder Information Declared

Anusandhan National Research Foundation (ANRF), SRG grant (SRG/2022/000528), ARG grant (ANRF/ARG/2025/003442/LS)

Copyright

The copyright holder for this preprint is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under a [CC-BY 4.0 International license](http://creativecommons.org/licenses/by/4.0/).

bioRxiv and medRxiv thank the following for their generous financial support:

> The Chan Zuckerberg Initiative, Cold Spring Harbor Laboratory, the Sergey Brin Family Foundation, California Institute of Technology, Centre National de la Recherche Scientifique, Fred Hutchinson Cancer Center, Imperial College London, Massachusetts Institute of Technology, Stanford University, The University of Edinburgh, University of Washington, and Vrije Universiteit Amsterdam.

[Back to top](https://www.biorxiv.org/content/10.64898/2026.07.05.736646v1#page)

[Previous](https://www.biorxiv.org/content/10.64898/2026.07.07.737135v1 "A family of RRM-1 RNA binding proteins enables cold adaptation and environmental resilience in Bacteroides")[Next](https://www.biorxiv.org/content/10.64898/2026.01.19.700459v3 "Persistent Hypersensitivity after Repeat Concussion is Associated with Chronic Cognitive Dysfunction")

Posted July 08, 2026.

[Download PDF](https://www.biorxiv.org/content/10.64898/2026.07.05.736646v1.full.pdf)

Print/Save Options

[Download PDF](https://www.biorxiv.org/content/biorxiv/early/2026/07/08/2026.07.05.736646.full.pdf)Full Text & In-line FiguresXML

[More Info](https://www.biorxiv.org/about/FAQ#PrintOptions "More Information on Print/Save Options")

[Supplementary Material](https://www.biorxiv.org/content/10.64898/2026.07.05.736646v1.supplementary-material)

[Data/Code](https://www.biorxiv.org/content/early/2026/07/08/2026.07.05.736646.external-links)

[Email](https://www.biorxiv.org/ "Email this Article")

[Share](https://www.biorxiv.org/)

PINPOINT: Protease INhibitor PredictiOn at the plant–pathogen INTerface using protein language models and structural modeling

MuthusaravananSivaramakrishnan, BalakumaranChandrasekar

bioRxiv 2026.07.05.736646; doi: https://doi.org/10.64898/2026.07.05.736646

This article is a preprint and has not been certified by peer review \[ [what does this mean?](https://www.biorxiv.org/about/FAQ#unrefereed)\].

Share This Article:Copy

[![Twitter logo](https://www.biorxiv.org/sites/all/modules/highwire/highwire/images/twitter.png)](https://www.biorxiv.org/highwire_log/share/twitter?link=http%3A%2F%2Ftwitter.com%2Fshare%3Furl%3Dhttps%253A%2F%2Fwww.biorxiv.org%2Fcontent%2F10.64898%2F2026.07.05.736646v1%26text%3DPINPOINT%253A%2520Protease%2520INhibitor%2520PredictiOn%2520at%2520the%2520plant%25E2%2580%2593pathogen%2520INTerface%2520using%2520protein%2520language%2520models%2520and%2520structural%2520modeling "Share this on Twitter")[![Facebook logo](https://www.biorxiv.org/sites/all/modules/highwire/highwire/images/fb-blue.png)](https://www.biorxiv.org/highwire_log/share/facebook?link=http%3A%2F%2Fwww.facebook.com%2Fsharer.php%3Fu%3Dhttps%253A%2F%2Fwww.biorxiv.org%2Fcontent%2F10.64898%2F2026.07.05.736646v1%26t%3DPINPOINT%253A%2520Protease%2520INhibitor%2520PredictiOn%2520at%2520the%2520plant%25E2%2580%2593pathogen%2520INTerface%2520using%2520protein%2520language%2520models%2520and%2520structural%2520modeling "Share on Facebook")[![LinkedIn logo](https://www.biorxiv.org/sites/all/modules/highwire/highwire/images/linkedin-32px.png)](https://www.biorxiv.org/highwire_log/share/linkedin?link=http%3A%2F%2Fwww.linkedin.com%2FshareArticle%3Fmini%3Dtrue%26url%3Dhttps%253A%2F%2Fwww.biorxiv.org%2Fcontent%2F10.64898%2F2026.07.05.736646v1%26title%3DPINPOINT%253A%2520Protease%2520INhibitor%2520PredictiOn%2520at%2520the%2520plant%25E2%2580%2593pathogen%2520INTerface%2520using%2520protein%2520language%2520models%2520and%2520structural%2520modeling%26summary%3D%26source%3DbioRxiv "Publish this post to LinkedIn")[![Mendeley logo](https://www.biorxiv.org/sites/all/modules/highwire/highwire/images/mendeley.png)](https://www.biorxiv.org/highwire_log/share/mendeley?link=http%3A%2F%2Fwww.mendeley.com%2Fimport%2F%3Furl%3Dhttps%253A%2F%2Fwww.biorxiv.org%2Fcontent%2F10.64898%2F2026.07.05.736646v1%26title%3DPINPOINT%253A%2520Protease%2520INhibitor%2520PredictiOn%2520at%2520the%2520plant%25E2%2580%2593pathogen%2520INTerface%2520using%2520protein%2520language%2520models%2520and%2520structural%2520modeling "Share on Mendeley")

[Citation Tools](https://www.biorxiv.org/ "Citation Tools")

- Post Button

- Facebook


Reviews and Context

0

Comment

0

TRIP Peer Reviews

0

Community Reviews

0

Automated Services

0

Blogs/Media

0

Author Videos

**Subject Areas**

[**All Articles**](https://www.biorxiv.org/content/early/recent)

- [Animal Behavior and Cognition](https://www.biorxiv.org/collection/animal-behavior-and-cognition)(7776)

- [Biochemistry](https://www.biorxiv.org/collection/biochemistry)(18142)

- [Bioengineering](https://www.biorxiv.org/collection/bioengineering)(14314)

- [Bioinformatics](https://www.biorxiv.org/collection/bioinformatics)(42942)

- [Biophysics](https://www.biorxiv.org/collection/biophysics)(21895)

- [Cancer Biology](https://www.biorxiv.org/collection/cancer-biology)(18920)

- [Cell Biology](https://www.biorxiv.org/collection/cell-biology)(25899)

- [Clinical Trials](https://www.biorxiv.org/collection/clinical-trials)(138)

- [Developmental Biology](https://www.biorxiv.org/collection/developmental-biology)(13528)

- [Ecology](https://www.biorxiv.org/collection/ecology)(20321)

- [Epidemiology](https://www.biorxiv.org/collection/epidemiology)(2067)

- [Evolutionary Biology](https://www.biorxiv.org/collection/evolutionary-biology)(24785)

- [Genetics](https://www.biorxiv.org/collection/genetics)(15813)

- [Genomics](https://www.biorxiv.org/collection/genomics)(22910)

- [Immunology](https://www.biorxiv.org/collection/immunology)(18131)

- [Microbiology](https://www.biorxiv.org/collection/microbiology)(41199)

- [Molecular Biology](https://www.biorxiv.org/collection/molecular-biology)(17398)

- [Neuroscience](https://www.biorxiv.org/collection/neuroscience)(90502)

- [Paleontology](https://www.biorxiv.org/collection/paleontology)(679)

- [Pathology](https://www.biorxiv.org/collection/pathology)(2897)

- [Pharmacology and Toxicology](https://www.biorxiv.org/collection/pharmacology-and-toxicology)(4932)

- [Physiology](https://www.biorxiv.org/collection/physiology)(7850)

- [Plant Biology](https://www.biorxiv.org/collection/plant-biology)(15359)

- [Scientific Communication and Education](https://www.biorxiv.org/collection/scientific-communication-and-education)(2062)

- [Synthetic Biology](https://www.biorxiv.org/collection/synthetic-biology)(4374)

- [Systems Biology](https://www.biorxiv.org/collection/systems-biology)(9927)

- [Zoology](https://www.biorxiv.org/collection/zoology)(2311)


## Follow this preprint

X

You can now receive automatic notifications when a preprint is revised, withdrawn, commented on, peer reviewed, or published in a journal. Select the events you would like to follow below and click "Submit". To see all of the preprints you are currently following, please go to the [bioRxiv Alerts Page](https://biorxiv.org/alerts).

Sign In to Follow this Preprint

Email \*

Email this Articleclose

Thank you for your interest in spreading the word about bioRxiv.

NOTE: Your email address is requested solely to identify you as the sender of this article.

Your Email \*

Your Name \*

Send To \*

Enter multiple addresses on separate lines or separate them with commas.

You are going to email the following [PINPOINT: Protease INhibitor PredictiOn at the plant–pathogen INTerface using protein language models and structural modeling](https://www.biorxiv.org/content/10.64898/2026.07.05.736646v1)

Message Subject
(Your Name) has forwarded a page to you from bioRxiv

Message Body
(Your Name) thought you would like to see this page from the bioRxiv website.

Your Personal Message

CAPTCHA

This question is for testing whether or not you are a human visitor and to prevent automated spam submissions.

reCAPTCHA

Recaptcha requires verification.

I'm not a robot

reCAPTCHA

Citation Toolsclose

PINPOINT: Protease INhibitor PredictiOn at the plant–pathogen INTerface using protein language models and structural modeling

MuthusaravananSivaramakrishnan, BalakumaranChandrasekar

bioRxiv 2026.07.05.736646; doi: https://doi.org/10.64898/2026.07.05.736646

This article is a preprint and has not been certified by peer review \[ [what does this mean?](https://www.biorxiv.org/about/FAQ#unrefereed)\].

## Citation Manager Formats

- [BibTeX](https://www.biorxiv.org/highwire/citation/5612790/bibtext)
- [Bookends](https://www.biorxiv.org/highwire/citation/5612790/bookends)
- [EasyBib](https://www.biorxiv.org/highwire/citation/5612790/easybib)
- [EndNote (tagged)](https://www.biorxiv.org/highwire/citation/5612790/endnote-tagged)
- [EndNote 8 (xml)](https://www.biorxiv.org/highwire/citation/5612790/endnote-8-xml)
- [Medlars](https://www.biorxiv.org/highwire/citation/5612790/medlars)
- [Mendeley](https://www.biorxiv.org/highwire/citation/5612790/mendeley)
- [Papers](https://www.biorxiv.org/highwire/citation/5612790/papers)
- [RefWorks Tagged](https://www.biorxiv.org/highwire/citation/5612790/refworks-tagged)
- [Ref Manager](https://www.biorxiv.org/highwire/citation/5612790/reference-manager)
- [RIS](https://www.biorxiv.org/highwire/citation/5612790/ris)
- [Zotero](https://www.biorxiv.org/highwire/citation/5612790/zotero)

We use cookies on this site to enhance your user experience. By clicking any link on this page you are giving your consent for us to set cookies.

ContinueFind out more

Twitter Widget Iframe