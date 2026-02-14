# progressive-pdf-to-web

Progressively convert **user-uploaded PDFs** into **mobile-friendly web pages**, on demand.

## Core idea

- Free users: **30 pages/day**
- Paid users: **unlimited**
- Pages are rendered **only when requested**
- Users can convert **specific pages or ranges**

## MVP flow

1. Upload PDF → get `document_id`
2. Request page N
3. Server renders page → image
4. Return mobile-friendly HTML
5. Cache result

## Repo layout

- apps/api — backend API (upload, quota, render)
- apps/web — mobile reader
- docs — architecture and API
- infra — deployment notes
