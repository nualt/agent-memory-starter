# Writing conventions

Each rule below states what to do, then the failure it prevents. The
failures are real; the names have been changed.

## 1. One name per thing

Pick one spelling for each project, tool, person, or client, and use it
everywhere: in the title, in headings, in every paragraph. Do not rely on
"it", "this project", or "the fix" as the only reference in a paragraph.

*Failure:* a project written as "Acme Webshop" in its project file and
"the Acme site" in a decision produced two entities. A question about the
site's cache policy found the decision but not the project, and the agent
answered without the constraint that lived in the project file.

## 2. Every section stands alone

Each `##` heading carries the entity name, not "Overview" or "Context".
Decision files are the exception: their four headings are fixed. In
every file, the first sentence of each section restates its subject. Assume the
section will be read with nothing around it.

*Failure:* a section titled "Constraints" under a project heading was cut
from its parent at a chunk boundary. Retrieved alone, it listed
constraints with no project attached, and the agent applied them to the
wrong client.

## 3. Relations are sentences

State a relation as subject, verb, object, in one sentence. "Acme Webshop
uses Medusa v2." "On 2026-06-03, Atelier Vasseur chose Colissimo over
Chronopost because volume did not justify the price." Lists of nouns
without verbs produce entities without edges.

*Failure:* a stack listed as "Next.js, Payload, Vercel Blob" produced
three entities and no relation to the project. "Where are uploads
stored?" returned nothing.

## 4. Absolute dates

Write `2026-06-03`, never "yesterday", "last quarter", "recently". The
file will be read months later, without the conversation that produced
it.

## 5. Define terms once per file

The first time an acronym or an internal term appears in a file, define
it. Each file is processed on its own; a definition in another file does
not carry over.

## 6. Frontmatter on every file

```yaml
title:    <one line, contains the entity name>
type:     project | decision | procedure
project:  <slug of the project, or none>
tags:     [<domain>, <tools>]
date:     <YYYY-MM-DD of last update>
status:   <per template>
related:  [<other files, by path>]
```

The frontmatter anchors the entities. An ingestion script can derive a
tag set from it (type, project, tags) and scope searches without a
dataset per project.

## 7. One concept per file

One project per file in `projects/`, one decision per file in
`decisions/`, one method per file in `procedures/`. A file that mixes two
subjects produces a summary that mixes the two. Link files by path in
`related:` and by name in the text.

## 8. No secrets, no personal data

No credentials, tokens, or URLs that embed them. No customer personal
data. Hosting, configuration, and architecture facts are fine. The base
is versioned and will be shared with more people and more tools than you
plan for today.

## Promotion

A decision starts with `status: raw`. When it becomes a standing rule,
write or update the relevant procedure, set the decision to
`status: promoted`, and link both ways in `related:`. The decision file
stays: it is the record of why the rule exists.
