# The careers form — for the AMS side

`careers.html` collects an application and a resume file. Point it at an
endpoint and it posts; leave it unset and it falls back to a pre-filled email.
Either way an application never disappears.

## Wiring it

Set the endpoint before the page's own script runs — same pattern as
`window.SAFEHOUSE_API` on the quote flow:

```html
<script>window.SAFEHOUSE_CAREERS_API = 'https://agentlogin.safehouseins.com/public-careers';</script>
```

The page reads it with `??`, so a value injected server-side or by another tag
is never clobbered.

## What it sends

`POST` as **`multipart/form-data`**, because a resume is a file:

| Field | Notes |
|---|---|
| `firstName`, `lastName` | last name may be empty |
| `phone` | validated to 10 digits before sending |
| `email` | validated; this is how we reply |
| `area` | Personal lines / Commercial lines / Customer service / Not sure yet |
| `licensed` | Texas General Lines / another state / willing to get licensed / no |
| `experience` | band, e.g. `3–5 years` |
| `languages` | English and Spanish / English only / Spanish only |
| `notes` | free text, may be empty |
| `resumeName` | the filename, also sent as a plain field so it survives a fallback |
| `resume` | the file itself — only present when one was attached |
| `source` | `safehouseins.com/careers` |
| `submittedAt` | ISO |

Accepted upload types are `.pdf .doc .docx .rtf .txt`. **Cap the size and check
the type server-side** — the `accept` attribute is a file-picker convenience,
not a control, and anything can be posted to an open endpoint.

Answer `200` on success. Anything else, or a network failure, drops the visitor
to the email fallback rather than showing an error.

## The fallback, and why it exists

With no endpoint configured — or when the endpoint fails — the page opens a
`mailto:` to `contact@safehouseins.com` with every answer already written into
the body, and the thank-you screen changes to say so and to ask the applicant
to attach the resume before sending.

It is worse than an upload. It is much better than "something went wrong, try
again later" on a page whose entire purpose is to collect one file from someone
who was willing to send it. The resume hint under the file input changes to
match, so nobody attaches a file believing it will be uploaded when it will not.

## Still to decide — not a website question

The page says nothing about pay, benefits, schedule or whether a role is
in-office. None of that is established anywhere, and a careers page is a bad
place to guess. When the agency settles on what it wants to say, it goes in
`tools/gencareers.py` and regenerates:

```
python3 tools/gencareers.py
```

Both `about.html` and `careers.html` are generated from `tools/shell.py`, which
is where the footer lives — call, text and email, with the two different
numbers. Edit them there, never in the HTML.
