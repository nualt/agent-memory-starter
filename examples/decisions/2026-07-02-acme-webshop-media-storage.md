---
title: Acme Webshop stores product media in Vercel Blob instead of Cloudflare R2
type: decision
project: acme-webshop
tags: [ecommerce, storage, vercel, cloudflare]
date: 2026-07-02
status: raw
related: [projects/acme-webshop.md]
---

# Acme Webshop stores product media in Vercel Blob instead of Cloudflare R2

## What happened

Acme Webshop, 2026-07-02: the first technical brief planned Cloudflare
R2 for product images. When the storefront moved to Vercel, keeping a
second provider for a few hundred files meant a second account, a second
set of credentials and a second bill for the client to follow.

## Why

Acme Webshop chose Vercel Blob because media then lives next to the
storefront, with one provider, one invoice and no bucket to configure.
Cloudflare R2 was rejected because its lower price only matters above a
traffic level the shop did not expect in its first year. The decision
is reversible: the upload code isolates the provider behind one module.

## Rule

Acme Webshop keeps media with the storefront provider until monthly
egress passes the level where R2 pricing wins, checked at each yearly
review.

## Where it now lives

The Acme Webshop media rule is recorded in the project file and is not
yet promoted to a procedure.
