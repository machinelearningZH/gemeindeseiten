"use strict";

const assert = require("node:assert/strict");
const { normalizeSearch } = require("../web/site.js");

for (const query of ["Wädenswil", "Waedenswil", "Wadenswil", " WÄDENSWIL "]) {
  assert.equal(normalizeSearch(query), "wadenswil");
}
assert.equal(normalizeSearch("Dübendorf"), normalizeSearch("Duebendorf"));
assert.equal(normalizeSearch("Höri"), normalizeSearch("Hoeri"));
assert.equal(normalizeSearch("AEUGST AM ALBIS"), normalizeSearch("Aeugst am Albis"));
assert.equal(normalizeSearch(""), "");

const elements = Object.fromEntries(["search", "type", "clear", "filters", "result-count", "no-results"]
  .map(id => [id, { value: id === "type" ? "all" : "", hidden: true, handlers: {},
    addEventListener(event, handler) { this.handlers[event] = handler; }, focus() {} }]));
const rows = [
  { cells: [{ textContent: "Wädenswil" }], dataset: { type: "political" } },
  { cells: [{ textContent: "Primarschulgemeinde Wädenswil" }], dataset: { type: "primary" } },
  { cells: [{ textContent: "Sekundarschulgemeinde Wädenswil" }], dataset: { type: "secondary" } },
  { cells: [{ textContent: "Volksschulgemeinde Hittnau" }], dataset: { type: "combined" } },
];
global.document = {
  querySelector: selector => elements[selector.slice(1)],
  querySelectorAll: () => rows,
};
delete require.cache[require.resolve("../web/site.js")];
require("../web/site.js");
assert.equal(elements.filters.hidden, false);
assert.equal(elements["result-count"].textContent, "4 von 4 Gemeinden");

elements.search.value = "waedenswil";
elements.search.handlers.input();
assert.deepEqual(rows.map(row => row.hidden), [false, false, false, true]);
elements.type.value = "secondary";
elements.type.handlers.change();
assert.deepEqual(rows.map(row => row.hidden), [true, true, false, true]);
assert.equal(elements["result-count"].textContent, "1 von 4 Gemeinden");

elements.search.value = "missing";
elements.search.handlers.input();
assert.equal(elements["no-results"].hidden, false);
assert.ok(rows.every(row => row.hidden));
elements.clear.handlers.click();
assert.ok(rows.every(row => !row.hidden));
assert.equal(elements["no-results"].hidden, true);
assert.equal(elements.type.value, "all");
console.log("Search normalization, type filters, empty state and reset passed.");
