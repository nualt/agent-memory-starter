---
title: Acme Webshop
type: project
project: acme-webshop
tags: [ecommerce, medusa, nextjs, vercel]
date: 2026-08-20
status: active
related: [decisions/2026-07-02-acme-webshop-media-storage.md, procedures/storefront-cache-invalidation.md]
---

# Acme Webshop

Acme Webshop is the online store of Acme, a maker of kitchen tools,
built with Medusa v2 for commerce and Next.js for the storefront.

## Acme Webshop: stack and hosting

Acme Webshop runs on Medusa v2 for catalogue, cart and orders, and on
Next.js for the storefront. The storefront is hosted on Vercel at
shop.acme.example. Product media is stored in Vercel Blob. Deploys happen
on every merge to `main`.

## Acme Webshop: people

Acme Webshop is owned by the operations manager at Acme and by the lead
developer on our side. Escalation goes to the studio founder.

## Acme Webshop: decisions

- 2026-07-02: Acme Webshop stores media in Vercel Blob because it removes
  a separate bucket to operate; Cloudflare R2 was rejected because the
  first estimate of traffic did not justify it. See
  `decisions/2026-07-02-acme-webshop-media-storage.md`.

## Acme Webshop: known constraints

- Acme Webshop must keep product pages cacheable for one hour, because
  the catalogue changes at most daily and traffic peaks on newsletter
  days.

## Acme Webshop: open items

- 2026-08-20: Acme Webshop still lacks a return flow in the account
  page, owned by the lead developer.

## Acme Webshop: history

- 2026-08-20: Acme Webshop moved storefront cache invalidation to the
  procedure `storefront-cache-invalidation`.
- 2026-07-02: Acme Webshop switched planned media storage from R2 to
  Vercel Blob.
