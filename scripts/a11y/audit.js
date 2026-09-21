const puppeteer = require("puppeteer-core");
const axe = require("axe-core");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const BASE = process.env.BASE || "http://localhost:8010";
const RUN = process.env.RUN || ""; // a saved run id; when empty, the run-view states are skipped

const states = [
  { name: "home / light", scheme: "light", url: "/", width: 1280 },
  { name: "home / dark", scheme: "dark", url: "/", width: 1280 },
  { name: "picker open, 2 chosen / light", scheme: "light", url: "/?mode=choose&pick=seo-onpage-audit,security-headers-review", width: 1280 },
  { name: "picker open / dark", scheme: "dark", url: "/?mode=choose&pick=seo-onpage-audit", width: 1280 },
  { name: "finished run + report / light", scheme: "light", url: `/?run=${RUN}`, width: 1280, wait: 2500 },
  { name: "finished run + report / dark", scheme: "dark", url: `/?run=${RUN}`, width: 1280, wait: 2500 },
  { name: "phone 375px / light", scheme: "light", url: `/?mode=choose&pick=seo-onpage-audit&run=${RUN}`, width: 375, wait: 2500 },
  { name: "skill dialog open / dark", scheme: "dark", url: "/", width: 1280, dialog: true },
];

(async () => {
  const list = RUN ? states : states.filter((s) => !s.url.includes("run="));
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
  let total = 0;
  for (const st of list) {
    const page = await browser.newPage();
    await page.setViewport({ width: st.width, height: 900 });
    await page.emulateMediaFeatures([{ name: "prefers-color-scheme", value: st.scheme }]);
    await page.goto(BASE + st.url, { waitUntil: "networkidle2" });
    await new Promise((r) => setTimeout(r, st.wait || 800));
    if (st.dialog) {
      await page.evaluate(() => { document.querySelector("#skillDialog").showModal(); document.querySelector("#skillTitle").textContent = "seo-onpage-audit"; document.querySelector("#skillBody").textContent = "sample"; });
    }
    await page.evaluate(axe.source);
    const res = await page.evaluate(async () => await axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"] } }));
    const extra = await page.evaluate(() => {
      const out = {};
      out.hOverflow = document.documentElement.scrollWidth > window.innerWidth + 1;
      out.small = [...document.querySelectorAll("button, a[href], input, select, textarea, summary")].filter((e) => e.offsetParent !== null).map((e) => { const r = e.getBoundingClientRect(); return { w: Math.round(r.width), h: Math.round(r.height), t: (e.textContent || e.id || e.type || e.tagName).trim().slice(0, 22) }; }).filter((x) => (x.w < 24 || x.h < 24) && x.w > 0);
      return out;
    });
    total += res.violations.length;
    console.log(`\n=== ${st.name}: ${res.violations.length} violations, ${res.passes.length} rules passed, ${res.incomplete.length} need manual review`);
    if (extra.hOverflow) console.log("  ! horizontal scroll at this width");
    if (extra.small.length) console.log("  ! targets under 24x24px:", JSON.stringify(extra.small.slice(0, 6)));
    for (const v of res.violations) {
      console.log(`  [${v.impact}] ${v.id}: ${v.help} (${v.nodes.length} node${v.nodes.length > 1 ? "s" : ""})`);
      for (const n of v.nodes.slice(0, 3)) console.log(`      ${n.target.join(" ")}  ->  ${(n.failureSummary || "").split("\n").slice(1, 3).join(" ").slice(0, 150)}`);
    }
    for (const v of res.incomplete.slice(0, 4)) console.log(`  (review) ${v.id}: ${v.nodes.length} node(s)`);
    await page.close();
  }
  process.exitCode = total ? 1 : 0;
  console.log(`\nTOTAL violations across ${list.length} states: ${total}`);
  await browser.close();
})();
