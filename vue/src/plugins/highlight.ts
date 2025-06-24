// import "highlight.js/styles/agate.css";
// import "highlight.js/styles/github.css";

import "highlight.js/styles/base16/circus.css";
import hljs from "highlight.js/lib/core";
import javascript from "highlight.js/lib/languages/javascript";
import xml from "highlight.js/lib/languages/xml";
import json from "highlight.js/lib/languages/json";
import hljsVuePlugin from "@highlightjs/vue-plugin";

hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("xml", xml);
hljs.registerLanguage("json", json);

export default hljsVuePlugin;
