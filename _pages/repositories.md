---
layout: page
permalink: /repositories/
title: tools & repositories
description: Software and tools developed by the EMERGE research group
nav: true
nav_order: 4
---

<style>
.tool-grid { display: flex; flex-wrap: wrap; gap: 1.2rem; margin-bottom: 2.5rem; }
.tool-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.2rem 1.4rem;
  width: 300px;
  background: var(--global-bg-color, #fff);
  transition: box-shadow 0.2s;
}
.tool-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.tool-card h4 { margin: 0 0 0.4rem 0; font-size: 1rem; }
.tool-card h4 a { text-decoration: none; }
.tool-card p { font-size: 0.85rem; color: #555; margin: 0; }
.lab-badge {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.badge-hvidsten { background: #e8f4e8; color: #2e7d32; }
.badge-sandve   { background: #e3f2fd; color: #1565c0; }
.badge-joint    { background: #fce4ec; color: #880e4f; }
</style>

## Hvidsten Lab

<div class="tool-grid">

<div class="tool-card">
  <span class="lab-badge badge-hvidsten">Hvidsten Lab</span>
  <h4><a href="https://github.com/shashank-KU/OmniCorr" target="_blank">OmniCorr</a></h4>
  <p>R package for visualizing host–microbiota interactions using multi-omics data.</p>
</div>

<div class="tool-card">
  <span class="lab-badge badge-hvidsten">Hvidsten Lab</span>
  <h4><a href="https://gitlab.com/hvidsten-lab/rcomplex" target="_blank">ComPlEx</a></h4>
  <p>R code for comparative analysis of plant co-expression networks.</p>
</div>

<div class="tool-card">
  <span class="lab-badge badge-hvidsten">Hvidsten Lab</span>
  <h4><a href="https://gitlab.com/hvidsten-lab/DiCE" target="_blank">DiCE</a></h4>
  <p>R code for differential co-expression network analysis.</p>
</div>

<div class="tool-card">
  <span class="lab-badge badge-hvidsten">Hvidsten Lab</span>
  <h4><a href="https://plantgenie.org" target="_blank">PlantGenIE</a></h4>
  <p>Plant Genome Integrated Explorer — tools for genomics research including co-expression network analysis.</p>
</div>

<div class="tool-card">
  <span class="lab-badge badge-hvidsten">Hvidsten Lab</span>
  <h4><a href="https://v2.salmobase.org/SalMotifDB/" target="_blank">SalMotifDB</a></h4>
  <p>Salmonid Motif DataBase — a resource for transcription factor binding motifs in salmonid genomes.</p>
</div>

<div class="tool-card">
  <span class="lab-badge badge-hvidsten">Hvidsten Lab</span>
  <h4><a href="http://www.lcb.uu.se/tools/rosetta/" target="_blank">Rosetta</a></h4>
  <p>Rough Set Toolkit for Analysis of data — a tool for machine learning and data analysis.</p>
</div>

</div>

## Sandve Lab

<div class="tool-grid">

<div class="tool-card">
  <span class="lab-badge badge-joint">Sandve &amp; Hvidsten</span>
  <h4><a href="https://gitlab.com/sandve-lab/evemodel" target="_blank">EVE (evemodel)</a></h4>
  <p>R implementation of the Expression Variance and Evolution model — a statistical framework for analysing how gene expression varies and evolves across species.</p>
</div>

</div>
