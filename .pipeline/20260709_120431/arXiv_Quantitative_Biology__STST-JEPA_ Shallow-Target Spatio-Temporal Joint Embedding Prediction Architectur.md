[Skip to main content](https://arxiv.org/abs/2607.06629#content)

![](https://arxiv.org/static/base/1.0.1/images/icons/smileybones-small.svg)arXiv is now an independent nonprofit! [Learn more](https://info.arxiv.org/about) ×

Search arXiv

Press Enter to search · [Advanced search](https://arxiv.org/search/advanced)

# Computer Science > Machine Learning

**arXiv:2607.06629** (cs)


\[Submitted on 7 Jul 2026\]

# Title:STST-JEPA: Shallow-Target Spatio-Temporal Joint Embedding Prediction Architecture For EEG Self-Supervised Learning

Authors: [Roy Segal](https://arxiv.org/search/cs?searchtype=author&query=Segal,+R), [Yoni Svechinsky](https://arxiv.org/search/cs?searchtype=author&query=Svechinsky,+Y), [Tomer Fekete](https://arxiv.org/search/cs?searchtype=author&query=Fekete,+T)

View a PDF of the paper titled STST-JEPA: Shallow-Target Spatio-Temporal Joint Embedding Prediction Architecture For EEG Self-Supervised Learning, by Roy Segal and 2 other authors

[View PDF](https://arxiv.org/pdf/2607.06629) [HTML (experimental)](https://arxiv.org/html/2607.06629v1)

> Abstract:Brain age -- the age inferred from a physiological recording -- is an emerging biomarker whose deviation from chronological age tracks neurological and psychiatric burden, and EEG is an attractive substrate for it because it is cheap, portable, and temporally rich. Yet EEG brain-age models must contend with cross-site montage heterogeneity, small labelled cohorts, and dominant subject-level non-stationarity, and few EEG foundation models have been shown to deliver competitive age regression across the full pediatric-to-older-adult range in which such a biomarker would actually be deployed. We introduce STST-JEPA, a self-supervised transformer for resting-state and task EEG, pretrained on 47,703 sessions spanning ages 5-81 from the [this http URL](http://brain.space/) and Healthy Brain Network (HBN) corpora. The model combines a latent-prediction objective - predicting masked-token representations against an EMA-of-tokenizer target - with an auxiliary signal-reconstruction term, applied to 30-second multi-channel windows under spatiotemporal block masks. A lightweight attentive probe trained on frozen pretrained embeddings achieves a best held-out-validation mean absolute error of 3.06 years (r = 0.924) for age regression on 3,367 sessions, against a predict-the-mean baseline of approximately 10 years MAE. With light task-specific fine-tuning of the model's final layers, the same pretrained encoder achieves rank-1 placements - with the model's native 30-second windows - on the public NeuralBench x [this http URL](http://brain.space/) EEG leaderboard for sex classification (balanced accuracy 0.911), age prediction (r = 0.749), and psychopathology composite regression (r = 0.215). We further show that the model's age-prediction residual is negatively correlated with cognitive efficiency over several tasks we examined.

|     |     |
| --- | --- |
| Subjects: | Machine Learning (cs.LG); Neurons and Cognition (q-bio.NC) |
| Cite as: | [arXiv:2607.06629](https://arxiv.org/abs/2607.06629) \[cs.LG\] |
|  | (or [arXiv:2607.06629v1](https://arxiv.org/abs/2607.06629v1) \[cs.LG\] for this version) |
|  | [https://doi.org/10.48550/arXiv.2607.06629](https://doi.org/10.48550/arXiv.2607.06629)<br>Focus to learn more<br>arXiv-issued DOI via DataCite |

## Submission history

From: Tomer Fekete \[ [view email](https://arxiv.org/show-email/0c3d2283/2607.06629)\]

**\[v1\]**
Tue, 7 Jul 2026 12:19:54 UTC (638 KB)

Full-text links:

## Access Paper:

View a PDF of the paper titled STST-JEPA: Shallow-Target Spatio-Temporal Joint Embedding Prediction Architecture For EEG Self-Supervised Learning, by Roy Segal and 2 other authors

- [View PDF](https://arxiv.org/pdf/2607.06629)
- [HTML (experimental)](https://arxiv.org/html/2607.06629v1)
- [TeX Source](https://arxiv.org/src/2607.06629)

[view license](http://arxiv.org/licenses/nonexclusive-distrib/1.0/ "Rights to this article")

### Current browse context:

cs.LG

[< prev](https://arxiv.org/prevnext?id=2607.06629&function=prev&context=cs.LG "previous in cs.LG (accesskey p)")  \|  [next >](https://arxiv.org/prevnext?id=2607.06629&function=next&context=cs.LG "next in cs.LG (accesskey n)")

[new](https://arxiv.org/list/cs.LG/new) \| [recent](https://arxiv.org/list/cs.LG/recent) \| [2026-07](https://arxiv.org/list/cs.LG/2026-07)

Change to browse by:


[cs](https://arxiv.org/abs/2607.06629?context=cs)

[q-bio](https://arxiv.org/abs/2607.06629?context=q-bio)

[q-bio.NC](https://arxiv.org/abs/2607.06629?context=q-bio.NC)

### References & Citations

- [NASA ADS](https://ui.adsabs.harvard.edu/abs/arXiv:2607.06629)
- [Google Scholar](https://scholar.google.com/scholar_lookup?arxiv_id=2607.06629)
- [Semantic Scholar](https://api.semanticscholar.org/arXiv:2607.06629)

export BibTeX citation

### Bookmark

[![BibSonomy](https://arxiv.org/static/browse/0.3.4/images/icons/social/bibsonomy.png)](http://www.bibsonomy.org/BibtexHandler?requTask=upload&url=https://arxiv.org/abs/2607.06629&description=STST-JEPA:%20Shallow-Target%20Spatio-Temporal%20Joint%20Embedding%20Prediction%20Architecture%20For%20EEG%20Self-Supervised%20Learning "Bookmark on BibSonomy") [![Reddit](https://arxiv.org/static/browse/0.3.4/images/icons/social/reddit.png)](https://reddit.com/submit?url=https://arxiv.org/abs/2607.06629&title=STST-JEPA:%20Shallow-Target%20Spatio-Temporal%20Joint%20Embedding%20Prediction%20Architecture%20For%20EEG%20Self-Supervised%20Learning "Bookmark on Reddit")

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

IArxiv recommender toggle

IArxiv Recommender _( [What is IArxiv?](https://iarxiv.org/about))_

- Author
- Venue
- Institution
- Topic

About arXivLabs


# arXivLabs: experimental projects with community collaborators

arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.

Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.

Have an idea for a project that will add value for arXiv's community? [**Learn more about arXivLabs**](https://info.arxiv.org/labs/index.html).

[Which authors of this paper are endorsers?](https://arxiv.org/auth/show-endorsers/2607.06629) \|
Disable MathJax ( [What is MathJax?](https://info.arxiv.org/help/mathjax.html))