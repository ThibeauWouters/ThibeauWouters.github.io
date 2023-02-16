---
title: 'Gravitational waves'
permalink: /resources/gw/
---
<!--
<style>
figcaption {
  font-style: italic;
  padding: 2px;
  text-align: center;
}
</style>
-->

Here, I will store useful references for gravitational waves. This page was inspired by [this compilation of references](https://iphysresearch.github.io/Survey4GWML/){:target="blank"}, which focuses on using machine learning in GW.

# Textbooks

I still have to look for good references myself - check back soon!

# Papers

__Fast gravitational wave parameter estimation without compromises__ ([link](https://arxiv.org/abs/2302.05333){:target="blank"}):

Parameter estimation for GWs relies on matched filtering. To sample the posterior, the authors develop a new framework, which implements several techniques. Most exciting is the use of __normalizing flows__ which allows them to approximate the posterior distribution using __neural networks__ and use that as a proposal distribution to generate the samples. PE usually takes days or weeks of sampling time, but this paper reduces it to an astonishing __single minute__.

__Genetic-algorithm-optimized neural networks for gravitational wave classification__ ([link](https://arxiv.org/abs/2010.04340){:target="blank"}):

The authors make use of genetic algorithms to __design new neural network architectures__ for GW classification, specifically CNNs for matched filtering. They offer a very nice introduction to genetic algorithms and deep learning, for those new to these topics. They start from an existing network, and are able to find a new architecture with __78% fewer trainable parameters while obtaining an 11% increase in accuracy__. The downside is that this search for new architectures requires __massive amount of computation power__, which is infeasibe unless HPC is used.  
