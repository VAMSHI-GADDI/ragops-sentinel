# RAGOps Sentinel Helm Chart

## Purpose

This Helm chart packages the RAGOps Sentinel API and Qdrant vector database for Kubernetes-style deployment.

## Components

- FastAPI RAGOps Sentinel API Deployment
- API ClusterIP Service
- Qdrant StatefulSet
- Qdrant Service
- ConfigMap-based runtime configuration
- Prometheus scrape annotations
- Health probes
- Resource requests and limits

## Render Locally

helm template ragops infra/helm/ragops-sentinel

## Install Example

helm install ragops infra/helm/ragops-sentinel

## Honest Limitation

This chart is deployment packaging. It does not claim a live production Kubernetes cluster deployment unless the chart is actually installed and verified on a cluster.
