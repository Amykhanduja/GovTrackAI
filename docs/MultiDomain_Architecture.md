# Multi-Domain Career Architecture

## Overview
GovTrack AI now supports an infinite number of independent career domains (e.g. Cyber Security, Foreign Languages, Law, Healthcare).

## 1. Domain Configuration
Domains are purely configuration-driven via `config/domains.json`. No core architecture needs to be rewritten to add a new domain.
You can map specific organizations or keyword signatures to domains.

## 2. The Many-To-Many Model
A single job can belong to multiple domains concurrently. For example, a "Cyber Security Analyst requiring Japanese proficiency" will mathematically map to both `cyber_tech` and `foreign_lang`. The `DomainManager` resolves this during the AI extraction phase.

## 3. UI Isolation
The Frontend now strictly passes `?domain=` parameters to all REST API endpoints. This creates an airtight visual isolation preventing "Data Leakage" between domains. When you are in the Cyber Security dashboard, no Language teaching jobs will pollute your KPI cards or search results.
