# Blocked-page recovery: the routes-that-lie catalogue

Read when a fetch "succeeds" with the wrong content, or when the
recovery ladder in tools.md returns something suspicious. The
dangerous failure is not the 403; it is the route that returns 200
and lies about it.

## Routes that lie

- Google Cache is dead but returns 200 with an interstitial page:
  a 200 from the cache host carries no snapshot and never did after
  its retirement. Treat cache-host 200s as empty.
- AMP-cache routes redirect to stub pages: a short AMP response with
  navigation chrome and no article body is a redirect stub, not the
  content.
- Some walled hosts return 429 bodies of several kilobytes: a large
  error body reads as content in byte-count heuristics. Check the
  status code before trusting size.
- archive.today rotates domains (`archive.ph`, `.md`, `.li`, `.is`):
  a domain-wide failure is rotation, not loss; move to the next
  mirror.
- The Wayback CDX API can 503 while the plain availability API
  still answers: fall back to the availability API before declaring
  no snapshot exists.
- Proxy relays can MITM the fetch: a proxied page is evidence about
  the proxy's view, not about the origin. Prefer direct or archive
  routes when provenance matters.

## Detection heuristics

Run all three on every "successful" recovery:

1. Title sniff: the served `<title>` must match the expected page
   or the query subject; a consent wall or portal title means the
   body is not the article.
2. Byte floor: recovered bodies below a few kilobytes are stubs;
   real articles are larger. Combine with the title sniff because
   interstitials can exceed the floor.
3. Redirect-stub check: follow the final redirect target and confirm
   it serves the payload itself, not another hop to a login or
   consent page.

## Snapshot provenance

Cite every recovered copy with its provenance: archive host, capture
date, and the fact it is a snapshot. A snapshot never stands in for
live data on freshness-sensitive questions.
