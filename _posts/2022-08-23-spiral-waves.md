---
title: 'Modelling the spiral waves of cell cycle oscillations'
date: 2022-08-23
permalink: /posts/2022/08/spiral-waves/
excerpt_separator: <!--more-->
header-includes:
   - \usepackage{bbm}
   - \usepackage{physics}
toc: true
tags:
  - physics
  - algorithm
  - biophysics
  - simulations
---

<style>
figcaption {
  font-style: italic;
  padding: 2px;
  text-align: center;
}
</style>

In oscillatory media, regions oscillating faster than their surroundings, as well as topological defects, can act as sources of waves which end up synchronizing the whole medium. In biological systems, these waves are a crucial way of transmitting information efficiently. At [GelensLab](https://www.gelenslab.org/){:target="_blank"},
interest in spiral wave phenomena is inspired by recent observations of such structures in cell cycle oscillations of _Xenopus laevis_ frogs. During my internship at GelensLab, my goal was to gain insight into properties of these wave phenomena through simulations of mathematical models.

<!--more-->

# Overview

In this post, I provide an introduction to the research performed during my internship, as well as briefly explain the mathematical model that we used for the numerical simulations.

The full report can be found [here](/files/pdf/research_internship_spiral_waves.pdf){:target="_blank"}, while my presentation on my work can be found [here](/files/pdf/research_internship_spiral_waves_presentation.pdf){:target="_blank"}.

# Introduction

Oscillations are present everywhere in Nature, from the orbits of planets and stars on cosmic scales, to cycles in the divison of cells in biological systems. Organisms rely on travelling wave phenomena and pattern formation to transmit information across large distances in an efficient way. Spiral waves and target wave patterns are particular examples of dynamical pattern formation appearing in complex spatiotemporal systems and have been observed in physical, chemical and biological contexts, such as the famous Belousov-Zhabotinsky reaction.

Travelling waves have been observed before by the team of GelensLab in the _Xenopus laevis_ frog's cell extracts. Since these waves and patterns play an important role in the coordination of the cell cycle oscillations, a lot of research has been dedicated to understanding these patterns, their properties and their origin through mathematical models which can be studied numerically.

Recently, spiral patterns have been observed the first time in experiments at GelensLab. The spirals appeared together with target patterns in droplets containing extract, which are two-dimensional extended spatial systems.

<p align="center">
  <img src="/images/posts/spirals/CyclinB.gif" alt="Video showing spiral waves observed in experiments." width="75%" height = "auto">
  <figcaption> Experiment showing the observation of spiral waves in the droplets containing extract of frog egg cells. Distances are in $\mu$m  </figcaption>
</p>

Motivated by this observation, we would like to model the formation of target patterns and spirals in two-dimensional systems in order to understand their properties, such as speeds of the waves spreading out and the speed by which these patterns entrain the medium, as a function of the model's parameters and details of the system. Given the observation that target and spiral patterns can appear simultaneously in a system, we also studied the interaction between these patterns, again as a function of parameters underlying the model of the oscillations.

# FitzHugh-Nagumo model

Whenever we want to model a complicated, biological system, we necessarily have to make a compromise between simplicity, ensuring that our analysis is tractable and solvable, and complexity that is inherently present in the system due to many biochemical interactions. Here, we employ a system of partial differential equations of two variables $u$ and $v$ which are capable to capture the main behaviour of target and spiral patterns. For our model, we take inspiration from earlier numerical work of the lab, related to travelling waves observed in one-dimensional extracts. To model the cell cycle oscillations, we make use of **FitzHugh-Nagumo** (FHN) equations related to the well-known Van der Pol oscillator. The equations are
\begin{equation}
\partial_t u = \varepsilon^{-1} (v - \tfrac14 d u (u^2 - b)) + D_u \nabla^2 u \equiv \varepsilon^{-1} (v - f(u)) + D_u \nabla^2 u
\end{equation}
\begin{equation}
\partial_t v = a - u + D_v \nabla^2 v
\end{equation}
The FHN equations depend on a number of parameters, which are explained in detail in the report. Most importantly, the parameter $\varepsilon$ is called the timescale separation between the variables $u$ and $v$, and determines the shape of the time series. For low values of, the oscillations are relaxation-like (with sudden, sharp jumps in values), while for high values, the oscillations have sinusoidal waveforms for both variables.

Due to the different nature of the terms, the above equations are called **reaction-diffusion** equations. The variables $u$ and $v$ represent chemical concentrations or activity which interact with each other, and both are allowed to diffuse in space. Focusing on the **reaction** part, the interaction is visualized in the diagram below. Since we have a negative feedback loop, the values of $u$ and $v$ will have an oscillatory behaviour as a function of time. This is an essential and desired feature of our model, as we want to be able to model cell cycle oscillations. If we turn off the spatial extent of the system (_i.e._, ignore the diffusion terms), the time series of $u$ and $v$ will be oscillations, as shown below.

<p align="center">
  <img src="/images/posts/spirals/spirals_FHN_illustrated.png" alt="Illustration of the FHN model equations" width="90%" height = "auto">
  <figcaption> A negative feedback loop causes the concentrations of $u$ and $v$ to develop an oscillatory behaviour. </figcaption>
</p>

In a spatially extended system, such as the extracts used in the experiments, individual oscillators are coupled to each other through **diffusion**. Combined with the reaction part of the FHN equations, which produced oscillations, coherent wave patterns can emerge. Hence, by simulating these equations on a computer, we can numerically study the **wave patterns** observed in the experiments.

# Wave patterns

Two competing wave patterns have been observed in experiments. Besides spiral waves, circular waves, called **target patterns** frequently arise in the cell cycle oscillations. Which kind of pattern emerges out of our simulation depends on the initial condition we start from. In both cases, we put an inhomogeneity in the system:

* Target patterns arise when we put a **pacemaker** in the system. Pacemakers are regions in space which oscillate faster than their surroundings ($P_i < P_o$).
* Spiral waves arise from a **topological defect**. These are heterogeneous distributions for $u$ and $v$ which have a singularity in the so-called phase field.

<p align="center">
  <img src="/images/posts/spirals/spirals_initial_conditions.png" alt="Illustration of initial conditions and the wave patterns that they create." width="90%" height = "auto">
  <figcaption> Initial conditions and the wave patterns that they create.  </figcaption>
</p>

More details on the numerical methods are provided in the report and presentation provided at the beginning of this page. In the remainder of this post, I'll focus on a few important results coming out of the internship. More results of the study are provided in the report.

# Periods of spiral waves

We first looked at a few properties of the spiral waves as observed in the experiments. After cleaning up some of the data, we computed the periods of the spiral waves that were observed by extracting a time series at different locations in the experimental set-up, as shown below.

<p align="center">
  <img src="/images/posts/spirals/spirals_data_analysis.png" alt="Illustration of extracting a time series out of the data." width="90%" height = "auto">
  <figcaption> From the data coming out of experiments, we are able to extract a time series from which we estimate the period of the spiral wave.  </figcaption>
</p>

Surprisingly, we found that the periods of spiral waves was on the order of 10 to 20 minutes. For comparison, earlier experiments involving target patterns had periods on the order of 40 minutes. It turned out that spiral waves were able to **reduce the period** of the oscillation.

In order to check if the simulations were able to reproduce this result, we varied the parameters of the model and computed the oscillation periods, scanning a large number of values. To make this computationally feasible, we made use of a **HPC cluster of supercomputers** from the VSC (more info can be found [here](https://www.vscentrum.be/){:target="_blank"}). As it turns out, simulations show that the period of spirals and target patterns is quite similar for oscillation-like dynamics, whereas spirals are able to produce a much lower period for relaxation-like dynamics, which is controlled by the parameter $\varepsilon$. Target patterns have a nearly constant period, likely due to the presence of a pacemaker region which enforces this period.

<p align="center">
  <img src="/images/posts/spirals/periods_spirals_and_targets.png" alt="Plot showing the period of spiral waves and target patterns while varying one of the parameters of the model." width="90%" height = "auto">
  <figcaption> Comparison between periods of spirals and target patterns from simulations. $P_i, P_o$ refer to the inner and outer period of the pacemaker and its surroundings for the target patterns. </figcaption>
</p>

(to finish!)
