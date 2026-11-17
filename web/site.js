"use strict";

function normalizeSearch(value) {
  return value.toLocaleLowerCase("de-CH").normalize("NFD")
    .replace(/\p{M}/gu, "").replace(/ae/g, "a").replace(/oe/g, "o")
    .replace(/ue/g, "u").replace(/ß/g, "ss").trim();
}

if (typeof document !== "undefined") {
  const search = document.querySelector("#search");
  const type = document.querySelector("#type");
  const rows = [...document.querySelectorAll("#municipalities tr")];
  const names = rows.map(row => normalizeSearch(row.cells[0].textContent));
  const count = document.querySelector("#result-count");

  function filterRows() {
    const query = normalizeSearch(search.value);
    let visible = 0;
    rows.forEach((row, index) => {
      row.hidden = !names[index].includes(query) ||
        (type.value !== "all" && row.dataset.type !== type.value);
      if (!row.hidden) visible += 1;
    });
    count.textContent = `${visible} von ${rows.length} Gemeinden`;
    document.querySelector("#no-results").hidden = visible !== 0;
  }

  search.addEventListener("input", filterRows);
  type.addEventListener("change", filterRows);
  document.querySelector("#clear").addEventListener("click", () => {
    search.value = "";
    type.value = "all";
    filterRows();
    search.focus();
  });
  document.querySelector("#filters").addEventListener("submit", event => event.preventDefault());
  document.querySelector("#filters").hidden = false;
  filterRows();
}

if (typeof module !== "undefined") module.exports = { normalizeSearch };
