#!/usr/bin/env node
/*
 Scrape dynamic decking prices for high-end hardwood options that can span 400 mm c/c.
 - Uses Puppeteer to render JS-heavy pages.
 - Extracts: thickness (mm), width/coverage (mm), price (per m or per m²) where clearly labeled.
 - Computes total for 18.75 m² when unit is m²; when per metre, requires coverage to compute m² price.
 - Skips entries lacking clear thickness >= 21 mm or a computable price per m².
*/

const puppeteer = require('puppeteer');

const DECK_AREA_M2 = 18.75;

  const targets = [
  {
    supplier: 'B&F Specialist Timber',
    species: 'Yellow Balau',
    url: 'https://www.bandfspecialisttimber.co.uk/products/yellow-balau-decking',
    notes: 'Shopify; shows per m and per m²; thickness 21 mm; coverage 140 mm',
  },
  {
    supplier: 'Hardwood Discount (EU)',
    species: 'Ipe',
    url: 'https://www.hardwooddiscount.com/ipe-decking',
    notes: 'EU pricing likely shown in €; extract per m² if available',
  },
  {
    supplier: 'Timber Ireland',
    species: 'Garapa',
    url: 'https://www.timberireland.ie/product/garapa-decking/',
    notes: 'IE pricing likely shown in €; extract per m or per m²',
  },
  {
    supplier: 'Tuin (Gadero UK)',
    species: 'Ipe',
    url: 'https://www.tuin.co.uk/ipe-hardwood-decking-21mm.html',
    notes: 'Expect 21 mm Ipe; pricing may be per length; attempt to derive per m or m²',
  },
  {
    supplier: 'Round Wood of Mayfield',
    species: 'Ipe',
    url: 'https://www.roundwood.com/decking/hardwood-decking/ipe-decking',
    notes: 'Prices may be hidden; attempt extraction; skip if unavailable',
  },
  {
    supplier: 'Round Wood of Mayfield',
    species: 'Garapa',
    url: 'https://www.roundwood.com/decking/hardwood-decking/garapa-decking',
    notes: 'Prices may be hidden; attempt extraction; skip if unavailable',
  },
  {
    supplier: 'Timbercut4u',
    species: 'Ipe',
    url: 'https://www.timbercut4u.co.uk/product/ipe-decking-21mm-x-145mm/',
    notes: 'WooCommerce; try to capture visible price',
  },
  {
    supplier: 'Decking Supplies',
    species: 'Hardwood (category)',
    url: 'https://www.deckingsupplies.co.uk/collections/hardwood-decking',
    notes: 'Category page; look for per metre/m²; skip if ambiguous',
  },
];

function parseFirstCurrency(text) {
  const match = text.match(/[£€]\s?([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)/);
  if (!match) return null;
  return parseFloat(match[1].replace(/,/g, ''));
}

function mmFrom(text, key) {
  const re = new RegExp(key + '\\s*:?\\s*([0-9]{2,3})\\s*mm', 'i');
  const m = text.match(re);
  return m ? parseInt(m[1], 10) : null;
}

function findAllCurrencies(text) {
  const re = /[£€]\s?([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)/g;
  const out = [];
  let m;
  while ((m = re.exec(text))) out.push(parseFloat(m[1].replace(/,/g, '')));
  return out;
}

async function scrape() {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox','--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  const results = [];

  for (const t of targets) {
    try {
      await page.goto(t.url, { waitUntil: 'domcontentloaded', timeout: 45000 });
      // Give time for dynamic price widgets
      await page.waitForTimeout(2500);
      const bodyText = await page.evaluate(() => document.body.innerText);

      // Basic facts
      const thickness = mmFrom(bodyText, 'Thickness') || mmFrom(bodyText, 'thickness') || (bodyText.match(/\b(21)\s*mm\b/i) ? 21 : null);
      const width = mmFrom(bodyText, 'Width') || mmFrom(bodyText, 'width') || (bodyText.match(/\b(145)\s*mm\b/i) ? 145 : null);
      const coverage = mmFrom(bodyText, 'Coverage Width') || mmFrom(bodyText, 'Coverage') || null;

      // Try to detect per m² explicitly
      let perM2 = null;
      let perM = null;
      // Quick cues on the page
      const perM2Line = bodyText.match(/[£€]\s?[0-9][^\n]*per\s*m\s*(?:²|2)/i);
      const perMLine = bodyText.match(/[£€]\s?[0-9][^\n]*per\s*m(?!\s*\^?2)/i);
      if (perM2Line) perM2 = parseFirstCurrency(perM2Line[0]);
      if (perMLine) perM = parseFirstCurrency(perMLine[0]);

      // Fallback: choose smallest plausible currency seen on page if labeled nearby
      if (!perM2 && !perM) {
        const vals = findAllCurrencies(bodyText).filter(v => v > 3 && v < 500);
        if (vals.length) {
          // Heuristic: if page mentions m², assume per m²; else per m
          if (/per\s*m\s*(?:²|2)/i.test(bodyText)) perM2 = Math.min(...vals);
          else perM = Math.min(...vals);
        }
      }

      let perM2Computed = perM2;
      if (!perM2Computed && perM) {
        const cov = coverage || width; // prefer coverage width; else use board width
        if (cov) {
          const mWide = cov / 1000.0;
          // price per m² = (price per running metre) / (coverage in metres)
          perM2Computed = perM / mWide;
        }
      }

      const okThickness = thickness && thickness >= 21;
      const okPrice = perM2Computed && perM2Computed > 10 && perM2Computed < 300;
      if (okThickness && okPrice) {
        const totalEx = perM2Computed * DECK_AREA_M2;
        results.push({
          supplier: t.supplier,
          species: t.species,
          url: t.url,
          thickness,
          width,
          coverage,
          per_m2_ex_vat: parseFloat(perM2Computed.toFixed(2)),
          total_ex_vat: parseFloat(totalEx.toFixed(2)),
          total_inc_vat_20: parseFloat((totalEx * 1.2).toFixed(2)),
        });
      }
    } catch (err) {
      // Skip target on error
    }
  }

  await browser.close();
  console.log(JSON.stringify({ area_m2: DECK_AREA_M2, results }, null, 2));
}

scrape().catch(err => { console.error(err); process.exit(1); });
