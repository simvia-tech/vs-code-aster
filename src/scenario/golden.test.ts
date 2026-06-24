import { describe, it, expect } from 'vitest';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { generateComm } from './generateComm';
import { generateExport } from './generateExport';
import { checkUnitsConsistent } from './units';
import type { StudySpec } from './spec';

const FIXTURES = path.join(__dirname, 'fixtures');
const UPDATE = !!process.env.UPDATE_GOLDENS;

const CASES = fs
  .readdirSync(FIXTURES)
  .filter((d) => fs.statSync(path.join(FIXTURES, d)).isDirectory());

function loadSpec(dir: string): StudySpec {
  return JSON.parse(fs.readFileSync(path.join(dir, 'spec.json'), 'utf8')) as StudySpec;
}

function golden(actual: string, file: string): void {
  if (UPDATE) {
    fs.writeFileSync(file, actual);
    return;
  }
  if (!fs.existsSync(file)) {
    throw new Error(`Missing golden ${path.basename(file)} — run \`npm run test:scenario:update\``);
  }
  expect(actual).toBe(fs.readFileSync(file, 'utf8'));
}

describe('scenario golden files', () => {
  expect(CASES.length).toBeGreaterThanOrEqual(5);

  for (const name of CASES) {
    const dir = path.join(FIXTURES, name);
    const spec = loadSpec(dir);

    it(`${name}: .comm matches golden`, () => {
      golden(generateComm(spec), path.join(dir, 'expected.comm'));
    });

    it(`${name}: .export matches golden`, () => {
      golden(generateExport(spec), path.join(dir, 'expected.export'));
    });

    it(`${name}: logical units agree between .comm and .export`, () => {
      const problems = checkUnitsConsistent(generateComm(spec), generateExport(spec));
      expect(problems).toEqual([]);
    });
  }
});
