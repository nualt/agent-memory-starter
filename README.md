# agent-memory-starter

Templates and writing conventions for a company knowledge base that AI
agents can actually retrieve.

Most companies already have the documents. What they lack is a way to
write them so that an agent memory, a knowledge graph, or a plain
retrieval pipeline pulls back *the decision and its reason*, not three
paragraphs that happen to resemble the question. This repository is the
smallest set of rules and files we found that makes the difference.

It was extracted from the knowledge base that runs
[Nualt](https://nualt.fr)'s own agents on [Cognee](https://www.cognee.ai/).
It does not depend on Cognee: the files it produces are Markdown, readable
by a person, ingestible by any memory engine, and useful with none.

## What is in here

```
templates/    three file skeletons: project, decision, procedure
examples/     one filled example of each
CONVENTIONS.md   the writing rules and why each one exists
scripts/check.py a pre-ingestion check for the rules that can be checked
LICENSE       MIT
```

## Three kinds of files

A company's operational knowledge fits in three shapes. Each has its own
template and its own folder.

- **project**, one file per client, product, site, or internal
  initiative. Facts, stack, key contacts, decisions, open items, history.
- **decision**, one file per decision, dated. What happened, why, what
  was rejected, where the rule now lives.
- **procedure**, one file per reusable method: onboarding a hire,
  handling a return, deploying a site. When to apply, steps, checks.

A decision that becomes a standing rule is promoted into a procedure, and
the decision file stays as provenance. Both link to each other.

## Why the rules look the way they do

A memory engine does not read a document the way a person does. It cuts
it into chunks of roughly a thousand tokens, runs a model on each chunk
to extract entities and relations, and merges entities by name. Retrieval
then walks those entities and relations. Every convention in this repo
follows from that:

1. **One name per thing, always spelled the same.** Node identity is the
   name. "Acme Webshop" and "the Acme site" become two nodes.
2. **Every section stands alone.** A chunk boundary can fall anywhere.
   Each section names its subject in its heading and its first sentence.
3. **Relations are short sentences.** Subject, verb, object. "Acme
   Webshop uses Medusa v2 for the catalogue." That sentence becomes an
   edge.
4. **Absolute dates.** `2026-06-03`, never "last week".
5. **Define an acronym once per file**, at first use.
6. **Frontmatter on every file**: `title`, `type`, `project`, `tags`,
   `date`, `status`, `related`. It anchors the entities and lets an
   ingestion script derive tags for scoped search.
7. **One concept per file.** Cross-reference by filename in `related:`,
   by entity name in the text.
8. **No secrets, no personal data.** Hosting facts are fine, credentials
   and customer PII are not. The base will be shared, versioned, and
   pushed.

`CONVENTIONS.md` expands each rule with the failure it prevents.

## How to use it

1. Copy `templates/` into your knowledge repository and keep the three
   folders: `projects/`, `decisions/`, `procedures/`.
2. Write from the templates. Look at `examples/` for the expected density.
3. Before ingesting, run the check:

   ```
   python3 scripts/check.py projects decisions procedures
   ```

   It verifies frontmatter, heading anchoring, relative dates, and a few
   secret patterns. It reports, it does not rewrite.
4. Ingest with your engine. Keep the files as the source of truth and the
   engine as a projection you can rebuild.

## If you use Cognee

Two things we learned in production, documented here so you do not
relearn them:

- Send each file as a named file, one at a time per dataset, in the
  background. Raw text uploads lose their names; parallel uploads to the
  same dataset fail on embedded graph stores.
- Datasets are the unit of access control. For a single user, a dataset
  per file type is convenient. For a company, make a dataset per access
  perimeter (`hr`, `finance`, `client-acme`) and keep the file type in
  the frontmatter. Rights follow the perimeter, retrieval follows the
  frontmatter.

## Status

This comes from one studio, with its own projects as material. The
templates were written for an ordinary company, a supplier choice, an
onboarding procedure, a client account, but they have only been used on
web development projects so far. Reports from other trades, and cases
where the rules fail, are welcome as issues.

## License

MIT. See `LICENSE`.
