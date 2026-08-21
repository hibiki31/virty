import { spawnSync } from "node:child_process";
import {
  copyFileSync,
  cpSync,
  existsSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const generatedFiles = [
  "src/auto-imports.d.ts",
  "src/components.d.ts",
  "src/typed-router.d.ts",
];

function runVite(cwd) {
  const vite = join(projectRoot, "node_modules/vite/bin/vite.js");
  const result = spawnSync(process.execPath, [vite, "build"], {
    cwd,
    stdio: "inherit",
  });

  if (result.status !== 0) {
    throw new Error("Vite buildに失敗しました。");
  }
}

function checkGeneratedTypes() {
  const originals = new Map(
    generatedFiles.map((path) => [path, readFileSync(join(projectRoot, path))])
  );

  try {
    runVite(projectRoot);
    const changed = generatedFiles.filter(
      (path) =>
        !readFileSync(join(projectRoot, path)).equals(originals.get(path))
    );

    if (changed.length > 0) {
      throw new Error(
        `Vite生成型が古くなっています: ${changed.join(", ")}\n` +
          "devctl generate web-types を実行してください。"
      );
    }
  } finally {
    for (const [path, content] of originals) {
      writeFileSync(join(projectRoot, path), content);
    }
  }
}

function generateTypes() {
  const temporaryRoot = mkdtempSync(join(tmpdir(), "virty-web-types-"));

  try {
    cpSync(projectRoot, temporaryRoot, {
      recursive: true,
      filter(source) {
        const firstSegment = relative(projectRoot, source).split("/")[0];
        return !["node_modules", "dist", "coverage"].includes(firstSegment);
      },
    });
    symlinkSync(join(projectRoot, "node_modules"), join(temporaryRoot, "node_modules"));
    runVite(temporaryRoot);

    for (const path of generatedFiles) {
      const source = join(temporaryRoot, path);
      if (!existsSync(source)) {
        throw new Error(`生成されるはずの型がありません: ${path}`);
      }
      copyFileSync(source, join(projectRoot, path));
    }
  } finally {
    rmSync(temporaryRoot, { recursive: true, force: true });
  }
}

const mode = process.argv[2];

try {
  if (mode === "check") {
    checkGeneratedTypes();
  } else if (mode === "generate") {
    generateTypes();
  } else {
    throw new Error("引数にはcheckまたはgenerateを指定してください。");
  }
} catch (error) {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
}
