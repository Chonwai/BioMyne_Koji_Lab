[Skip to main content](https://arxiv.org/abs/2607.05691#content)

![](https://arxiv.org/static/base/1.0.1/images/icons/smileybones-small.svg)arXiv is now an independent nonprofit! [Learn more](https://info.arxiv.org/about) ×

Search arXiv

Press Enter to search · [Advanced search](https://arxiv.org/search/advanced)

# Computer Science > Computation and Language

**arXiv:2607.05691** (cs)


\[Submitted on 6 Jul 2026\]

# Title:Where to cut, how deep: BPE and Unigram-LM on chemistry SMILES

Authors: [Hunter Heidenreich](https://arxiv.org/search/cs?searchtype=author&query=Heidenreich,+H)

View a PDF of the paper titled Where to cut, how deep: BPE and Unigram-LM on chemistry SMILES, by Hunter Heidenreich

[View PDF](https://arxiv.org/pdf/2607.05691) [HTML (experimental)](https://arxiv.org/html/2607.05691v1)

> Abstract:Every chemical language model reading SMILES begins with a tokenizer, yet the field has inherited byte-pair encoding (BPE) from natural language with little scrutiny. In natural language, BPE's principal alternative, Unigram-LM, is known to build structurally different vocabularies. Whether that contrast survives in chemistry was open. We report a controlled comparison of BPE and Unigram-LM over a fixed 165-token chemistry base, at the small vocabulary sizes where token embeddings are learnable, across three corpus typologies (diverse, drug-like, natural-products) and both pre-tokenization boundary policies. The two do not converge. In all 22 matched conditions they build near-disjoint subword vocabularies: cross-algorithm Jaccard overlap on the learned pieces never exceeds 0.161, and at most 0.05 once weighted toward the high-frequency pieces a model updates most. Unigram-LM also segments held-out molecules into 29-41% more tokens; the arms largely agree on where to cut but not how deeply, so BPE's segmentation is a strict coarsening of Unigram-LM's on 80-99% of molecules. The separation holds across corpus, boundary, and vocabulary size, persisting even at eight times that scale. The subword algorithm is therefore a modeling decision, not a free default. The study trains no language models.

|     |     |
| --- | --- |
| Subjects: | Computation and Language (cs.CL); Machine Learning (cs.LG); Biomolecules (q-bio.BM) |
| Cite as: | [arXiv:2607.05691](https://arxiv.org/abs/2607.05691) \[cs.CL\] |
|  | (or [arXiv:2607.05691v1](https://arxiv.org/abs/2607.05691v1) \[cs.CL\] for this version) |
|  | [https://doi.org/10.48550/arXiv.2607.05691](https://doi.org/10.48550/arXiv.2607.05691)<br>Focus to learn more<br>arXiv-issued DOI via DataCite (pending registration) |

## Submission history

From: Hunter Heidenreich \[ [view email](https://arxiv.org/show-email/a4d6c93b/2607.05691)\]

**\[v1\]**
Mon, 6 Jul 2026 23:16:51 UTC (1,009 KB)

Full-text links:

## Access Paper:

View a PDF of the paper titled Where to cut, how deep: BPE and Unigram-LM on chemistry SMILES, by Hunter Heidenreich

- [View PDF](https://arxiv.org/pdf/2607.05691)
- [HTML (experimental)](https://arxiv.org/html/2607.05691v1)
- [TeX Source](https://arxiv.org/src/2607.05691)

[![license icon](https://arxiv.org/icons/licenses/by-4.0.png)view license](http://creativecommons.org/licenses/by/4.0/ "Rights to this article")

### Current browse context:

cs.CL

[< prev](https://arxiv.org/prevnext?id=2607.05691&function=prev&context=cs.CL "previous in cs.CL (accesskey p)")  \|  [next >](https://arxiv.org/prevnext?id=2607.05691&function=next&context=cs.CL "next in cs.CL (accesskey n)")

[new](https://arxiv.org/list/cs.CL/new) \| [recent](https://arxiv.org/list/cs.CL/recent) \| [2026-07](https://arxiv.org/list/cs.CL/2026-07)

Change to browse by:


[cs](https://arxiv.org/abs/2607.05691?context=cs)

[cs.LG](https://arxiv.org/abs/2607.05691?context=cs.LG)

[q-bio](https://arxiv.org/abs/2607.05691?context=q-bio)

[q-bio.BM](https://arxiv.org/abs/2607.05691?context=q-bio.BM)

### References & Citations

- [NASA ADS](https://ui.adsabs.harvard.edu/abs/arXiv:2607.05691)
- [Google Scholar](https://scholar.google.com/scholar_lookup?arxiv_id=2607.05691)
- [Semantic Scholar](https://api.semanticscholar.org/arXiv:2607.05691)

export BibTeX citation

### Bookmark

[![BibSonomy](https://arxiv.org/static/browse/0.3.4/images/icons/social/bibsonomy.png)](http://www.bibsonomy.org/BibtexHandler?requTask=upload&url=https://arxiv.org/abs/2607.05691&description=Where%20to%20cut,%20how%20deep:%20BPE%20and%20Unigram-LM%20on%20chemistry%20SMILES "Bookmark on BibSonomy") [![Reddit](https://arxiv.org/static/browse/0.3.4/images/icons/social/reddit.png)](https://reddit.com/submit?url=https://arxiv.org/abs/2607.05691&title=Where%20to%20cut,%20how%20deep:%20BPE%20and%20Unigram-LM%20on%20chemistry%20SMILES "Bookmark on Reddit")

Bibliographic Tools

# Bibliographic and Citation Tools

Bibliographic Explorer Toggle

Bibliographic Explorer _( [What is the Explorer?](https://info.arxiv.org/labs/showcase.html#arxiv-bibliographic-explorer))_

Connected Papers Toggle

Connected Papers _( [What is Connected Papers?](https://www.connectedpapers.com/about))_

Litmaps Toggle

Litmaps _( [What is Litmaps?](https://www.litmaps.co/))_

scite.ai Toggle

scite Smart Citations _( [What are Smart Citations?](https://www.scite.ai/))_

Code, Data, Media

# Code, Data and Media Associated with this Article

alphaXiv Toggle

alphaXiv _( [What is alphaXiv?](https://alphaxiv.org/))_

Links to Code Toggle

CatalyzeX Code Finder for Papers _( [What is CatalyzeX?](https://www.catalyzex.com/))_

DagsHub Toggle

DagsHub _( [What is DagsHub?](https://dagshub.com/))_

GotitPub Toggle

Gotit.pub _( [What is GotitPub?](http://gotit.pub/faq))_

Huggingface Toggle

Hugging Face _( [What is Huggingface?](https://huggingface.co/huggingface))_

ScienceCast Toggle

ScienceCast _( [What is ScienceCast?](https://sciencecast.org/welcome))_

Demos

# Demos

Replicate Toggle

Replicate _( [What is Replicate?](https://replicate.com/docs/arxiv/about))_

Spaces Toggle

Hugging Face Spaces _( [What is Spaces?](https://huggingface.co/docs/hub/spaces))_

Spaces Toggle

TXYZ.AI _( [What is TXYZ.AI?](https://txyz.ai/))_

Related Papers

# Recommenders and Search Tools

Link to Influence Flower

Influence Flower _( [What are Influence Flowers?](https://influencemap.cmlab.dev/))_

Core recommender toggle

CORE Recommender _( [What is CORE?](https://core.ac.uk/services/recommender))_

- Author
- Venue
- Institution
- Topic

About arXivLabs


# arXivLabs: experimental projects with community collaborators

arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.

Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.

Have an idea for a project that will add value for arXiv's community? [**Learn more about arXivLabs**](https://info.arxiv.org/labs/index.html).

[Which authors of this paper are endorsers?](https://arxiv.org/auth/show-endorsers/2607.05691) \|
Disable MathJax ( [What is MathJax?](https://info.arxiv.org/help/mathjax.html))