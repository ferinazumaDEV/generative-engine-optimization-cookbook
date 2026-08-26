// The real content lives here, in JavaScript — so it only appears AFTER a
// browser downloads and executes this file. A fetch-only AI crawler (which
// reads index.html but does not run JS) never sees any of this text.
document.getElementById("root").innerHTML = `
  <article>
    <h1>How AI answer engines pick sources</h1>
    <p>Generative engines such as ChatGPT Search, Perplexity and Google AI
    Overviews do not return ten blue links. They compose a single answer and
    cite a handful of sources. To be one of them, your page has to be readable,
    quotable, and trustworthy to a machine.</p>
    <p>The first hurdle is mechanical: the crawler has to be able to read your
    content at all. Many AI crawlers fetch your HTML but do not run JavaScript,
    so anything your page paints on the client after load is invisible to them.</p>
    <p>If your main content only exists after a browser executes your bundle, a
    fetch-only crawler sees an empty shell — and an empty page is never cited.
    Rendering the content on the server (SSR) or at build time (SSG) puts it in
    the HTML itself, where every engine can read and quote it.</p>
  </article>`;
