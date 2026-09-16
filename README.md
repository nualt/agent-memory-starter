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
templates/         three file skeletons: project, decision, procedure
examples/          six filled files that reference each other
CONVENTIONS.md     the writing rules and why each one exists
datasets.json      which folder goes to which Cognee dataset
scripts/check.py   pre-ingestion check for the rules that can be checked
scripts/ingest.py  targeted ingestion into a self-hosted Cognee
LICENSE            MIT
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

## How to use it, without any engine

1. Copy `templates/` and `datasets.json` into a repository of your own and
   create the three folders: `projects/`, `decisions/`, `procedures/`.
2. Write from the templates. `examples/` shows the expected density; the
   six files there reference each other, so you can see how `related:`
   works.
3. Before sharing or ingesting, run the check from the repository root:

   ```
   python3 scripts/check.py projects decisions procedures
   ```

   It verifies frontmatter, heading anchoring, related files, relative
   dates and a few secret patterns. It reports and never rewrites.

The files are the source of truth. Whatever engine you put behind them
is a projection you can rebuild.

## From a fresh Cognee to a first correct answer

This is the path we run at Nualt, on a self-hosted
[Cognee](https://github.com/topoteretes/cognee) reached through its HTTP
API. Installing Cognee itself is out of scope here; its documentation
covers Docker and the API key.

1. **Point the script at your instance.** Set `COGNEE_BASE_URL` (default
   `http://localhost:8000`) and `COGNEE_API_KEY`, in the environment or
   in `~/.cognee/.env`. The script sends the key as `X-Api-Key`.
2. **Check the mapping.** `datasets.json` maps each folder to a dataset.
   The default is one dataset per file type. Datasets are the unit of
   access control in Cognee, so for a company you will want one dataset
   per access perimeter instead (see below).
3. **Check the files.** `python3 scripts/check.py projects decisions procedures`
   must report zero issues.
4. **Ingest.** First time, on an empty instance:

   ```
   python3 scripts/ingest.py --all
   ```

   Afterwards, only what changed:

   ```
   python3 scripts/ingest.py projects/acme-webshop.md decisions/2026-07-02-acme-webshop-media-storage.md
   ```

   The script adds each file as a named file, deletes a previous version
   of the same name, runs one `cognify` per touched dataset, waits for
   completion and prints the inventory. Count one to five minutes per
   dataset; the first full run of a few dozen files takes about fifteen.
5. **Verify.** The proof is not the script's output. It is the dataset
   inventory printed at the end, a `cognify` status without errors, and a
   search that answers a precise fact from one of the files correctly.
   From an MCP client this is a `recall`; from the API,
   `POST /api/v1/search` with `GRAPH_COMPLETION`.

### Things we learned the hard way

- Send files one at a time per dataset. Embedded graph stores such as
  Kuzu accept a single writer per file; parallel uploads to the same
  dataset fail with a lock error.
- Never upload raw text. A document sent as text is stored under a hash
  and becomes unreadable in the UI. `ingest.py` always sends a named
  file.
- A modified file is a new document. Delete the previous one first, or
  you will have two. The script does it by name.
- Do not verify presence with a search alone. When nothing matches, some
  search modes answer politely instead of saying so. List the dataset.
- If you run Cognee's MCP server next to the API, run it in API mode so
  that only one process touches the graph files.

### Datasets for a company

For one person, a dataset per file type is convenient. For a company,
rights matter more than types. Cognee grants read and write permissions
per dataset and per user, and a search only walks the datasets the
caller may read. So map folders to perimeters instead:

```json
{ "hr": "hr", "finance": "finance", "client-acme": "client-acme" }
```

Each perimeter folder then holds projects, decisions and procedures
together, and the file type stays in the frontmatter (`type:`), where
`ingest.py` picks it up as a tag. The simplest working model for a small
company is one writer per perimeter, everyone else read-only.

## Status

This comes from one studio, with its own projects as material. The
templates were written for an ordinary company, a supplier choice, an
onboarding procedure, a client account, but they have only been used on
web development projects so far. Reports from other trades, and cases
where the rules fail, are welcome as issues.

## License

MIT. See `LICENSE`.
