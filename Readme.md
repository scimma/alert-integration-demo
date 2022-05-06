# SCiMMA Alert Integration Demo

## Description

This repo contains the source code and deployment configuration for a prototype system designed for an end-to-end demonstration that will:

1. Subscribe to multiple Hopskotch topics to receive alerts from multiple data sources (e.g. GCN, LIGO, ICECUBE, ZTF).
1. Archive the incoming alerts in a database.
1. Analyze incoming alerts using processing pipelines that generate derived alerts.
1. Publish derived alerts to a dedicated Hopskotch topic.
1. Create a TOM based on the TOM Toolkit and subscribe to the derived alert Hopskotch topic via a custom alert broker module to generate targets that drive observation requests to an observatory.

## Repo structure

* `/apps` contains the ArgoCD manifests that drive the top-level deployment. The relevant `Application` manifest will be manually added as an app in the ArgoCD deployment accessible at https://antares.ncsa.illinois.edu/argo-cd/.
* `/charts` contains Helm chart definitions referenced by the ArgoCD applications.
* `/src` contains source code related to the constituent components. Dockerfiles that define container images are stored here.
* `/docs` contains documentation related to this project.

## Architecture

### Overview

The hop.SCiMMA service provides a centralized hub for publishing and subscribing to access-controlled alert streams via the Hopskotch protocol. Two 

<img src="./docs/architecture.drawio.png">

### Broker

<img src="./docs/broker.drawio.png">

## Links and references

* [SCiMMA public talk with Electromagnetic Counterpart Identification (El-CID) demo Jupyter notebooks](https://cloud.musesframework.io/s/X6N3aHdDr3tq3zX)
* [El-CID: A filter for Gravitational-wave Electromagnetic Counterpart Identification](https://arxiv.org/abs/2108.04166)
* [TOM Toolkit docs](https://tom-toolkit.readthedocs.io/en/latest/introduction/getting_started.html)
