# Testing

Use this when you test a Templ component, a handler, an HTMX partial, or a CSRF-protected form.

Test levels, file pairs, and the `stage` pattern are in [../../go-tests/SKILL.md](../../go-tests/SKILL.md). The rules here only add what is specific to HTMX apps.

## Choose the level

| What you test | Level |
|---------------|-------|
| A pure component render (data in, HTML out, no dependencies) | Unit |
| A handler, a full page, an HTMX partial, a form post, CSRF, status codes, headers | Integration or E2E |
| Behaviour that needs a real browser (swaps, indicators, `hx-on`, Alpine) | Browser test: [../../go-browser-tests/SKILL.md](../../go-browser-tests/SKILL.md) |

A handler test with a hand-built request and a recorder tests the handler against nothing real. Run the handler on a real server with its real dependencies, as an integration or E2E test, and send real HTTP requests to it.

## Component unit test

A unit test marks `// given`, `// when`, `// then`, passes `t.Context()`, and asserts one outcome.

```go
func TestHello_RendersName(t *testing.T) {
    // given
    var buf bytes.Buffer

    // when
    err := Hello("World").Render(t.Context(), &buf)

    // then
    require.NoError(t, err)
    require.Contains(t, buf.String(), "Hello, World!")
}
```

Assert on content a user sees or a stable `id` or `data-testid`. Do not assert on whole-markup strings.

## Handler tests in the stage pattern

An integration test sends the HTMX headers in a `given` method and asserts both the partial and the full page.

```go
func TestUser_HTMXRequest_ReturnsPartialOnly(t *testing.T) {
    given, when, then := newStage(t)

    given.
        appIsReady().and().
        aUser().and().
        anHTMXRequest()

    when.
        gettingUser()

    then.
        noError().and().
        statusIs(http.StatusOK).and().
        bodyContains(`id="user-row"`).and().
        bodyDoesNotContain("<html").and().
        headerContains("Vary", "HX-Request")
}

func TestUser_BoostedRequest_ReturnsFullPage(t *testing.T) {
    given, when, then := newStage(t)

    given.
        appIsReady().and().
        aUser().and().
        aBoostedRequest()

    when.
        gettingUser()

    then.
        noError().and().
        bodyContains("<html")
}
```

`anHTMXRequest()` sets `HX-Request: true`. `aBoostedRequest()` sets `HX-Request: true` and `HX-Boosted: true`. Both store the headers on `stage`, and `gettingUser()` sends them.

## CSRF-protected forms

The CSRF middleware needs the cookie from an earlier response and the token from the form. A `given` method does the first request, stores the cookie jar on `stage`, and reads the hidden field from the HTML. The `when` method then posts with both.

- Use one `http.Client` with a `cookiejar` for the whole stage.
- Add one test per rejection: no token, wrong token. Assert `403`.
- With `net/http` `CrossOriginProtection`, add a test that sends `Sec-Fetch-Site: cross-site` on a POST and expects `403`, and one that sends `same-origin` and expects success.

## Error handling

- Assert that a bad form post returns the fixed message (`invalid form`) and does not contain a field name or a Go type name from the decoder.
- Assert that a missing record returns `404` and an unexpected failure returns `500` with a generic body.
