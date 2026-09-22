import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import type { FullResult, Reporter, TestCase, TestResult } from "@playwright/test/reporter";

/** 認証情報・HTTP本文・DOM・任意の例外文字列を成果物へ含めない。 */
export default class SafeReporter implements Reporter {
  private readonly tests: Record<string, unknown>[] = [];
  private readonly output = path.resolve("fullstack-results");

  onTestEnd(test: TestCase, result: TestResult): void {
    const index = this.tests.length + 1;
    const failures = result.errors.map(error => error.location && ({
      file: path.relative(process.cwd(), error.location.file),
      line: error.location.line,
      column: error.location.column,
    })).filter(Boolean);
    this.tests.push({
      title: test.title,
      file: path.relative(process.cwd(), test.location.file),
      line: test.location.line,
      status: result.status,
      expectedStatus: test.expectedStatus,
      durationMs: result.duration,
      failures,
    });
    const diagnostic = result.attachments.find(attachment => attachment.name === "診断用のHTTP状態とtask状態");
    if (diagnostic?.body) {
      mkdirSync(path.join(this.output, "diagnostics"), { recursive: true });
      writeFileSync(path.join(this.output, "diagnostics", `${index}.json`), diagnostic.body, { mode: 0o600 });
    }
    process.stdout.write(`${result.status}: ${test.title} (${test.location.file}:${test.location.line})\n`);
    for (const failure of failures) process.stdout.write(`  assertion: ${failure!.file}:${failure!.line}\n`);
  }

  onEnd(result: FullResult): void {
    mkdirSync(this.output, { recursive: true });
    writeFileSync(path.join(this.output, "report.json"), JSON.stringify({
      status: result.status,
      durationMs: result.duration,
      tests: this.tests,
    }, null, 2), { mode: 0o600 });
    process.stdout.write(`全層E2E: ${result.status}, ${this.tests.length}件\n`);
  }
}
