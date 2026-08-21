import {
  isMap,
  isScalar,
  isSeq,
  LineCounter,
  parseAllDocuments,
  Scalar,
  type Document,
  type YAMLMap,
} from "yaml";

export const EMPTY_CLOUD_CONFIG = "#cloud-config\n{}\n";

export interface CloudInitFormState {
  username: string;
  password: string;
  passwordExpires: boolean;
  sshPasswordAuthentication: boolean;
  selectedPublicKeys: string[];
  manualPublicKeys: string;
  packageUpdate: boolean;
  packages: string;
  script: string;
}

export type CloudInitSuccess = {
  ok: true;
  value: string;
};

export type CloudInitFailure = {
  ok: false;
  errors: string[];
};

export type CloudInitResult = CloudInitSuccess | CloudInitFailure;
export type CloudInitValidationResult = CloudInitResult;
export type CloudInitMergeResult = CloudInitResult;

type ParsedDocument = ReturnType<typeof parseAllDocuments>[number];

type ParsedCloudInit = {
  ok: true;
  document: ParsedDocument;
  root: YAMLMap;
  lineCounter: LineCounter;
};

type NormalizedForm = {
  username: string;
  password: string;
  passwordExpires: boolean;
  sshPasswordAuthentication: boolean;
  publicKeys: string[];
  packageUpdate: boolean;
  packages: string[];
  script: string;
};

const USERNAME_PATTERN = /^[a-z_][a-z0-9_-]{0,31}$/;
const OPENSSH_PUBLIC_KEY_PATTERN =
  /^(?:ssh|ecdsa|sk)-[A-Za-z0-9@._+-]+[\t ]+[A-Za-z0-9+/]+={0,2}(?:[\t ]+[^\r\n]+)?$/;
const PRIVATE_KEY_MARKER = /-----BEGIN [^-\r\n]*PRIVATE KEY-----|-----END [^-\r\n]*PRIVATE KEY-----/i;

export function createCloudInitFormState(): CloudInitFormState {
  return {
    username: "",
    password: "",
    passwordExpires: false,
    sshPasswordAuthentication: false,
    selectedPublicKeys: [],
    manualPublicKeys: "",
    packageUpdate: false,
    packages: "",
    script: "",
  };
}

function formatPosition(
  lineCounter: LineCounter,
  offset: number,
  message: string,
): string {
  const { line, col } = lineCounter.linePos(Math.max(0, offset));
  return `Line ${line || 1}, column ${col || 1}: ${message}`;
}

function nodeOffset(node: unknown): number {
  if (typeof node !== "object" || node === null || !("range" in node)) {
    return 0;
  }

  const range = (node as { range?: unknown }).range;
  return Array.isArray(range) && typeof range[0] === "number" ? range[0] : 0;
}

function parseCloudInit(source: string): ParsedCloudInit | CloudInitFailure {
  const errors: string[] = [];
  const firstLine = source.match(/^[^\r\n]*/)?.[0] ?? "";

  if (firstLine !== "#cloud-config") {
    errors.push("Line 1, column 1: The first line must be exactly #cloud-config.");
  }

  const lineCounter = new LineCounter();
  const documents = parseAllDocuments(source, {
    lineCounter,
    prettyErrors: false,
    strict: true,
    uniqueKeys: true,
    version: "1.1",
  });

  for (const document of documents) {
    for (const error of document.errors) {
      errors.push(
        formatPosition(lineCounter, error.pos[0], error.message),
      );
    }
    for (const warning of document.warnings) {
      errors.push(
        formatPosition(lineCounter, warning.pos[0], warning.message),
      );
    }
  }

  if (documents.length !== 1) {
    const secondDocument = documents[1];
    errors.push(
      formatPosition(
        lineCounter,
        secondDocument?.range?.[0] ?? 0,
        "Cloud-init user-data must contain exactly one YAML document.",
      ),
    );
  }

  const document = documents[0];
  if (document && document.errors.length === 0 && !isMap(document.contents)) {
    errors.push(
      formatPosition(
        lineCounter,
        nodeOffset(document.contents),
        "The YAML document root must be a mapping.",
      ),
    );
  }

  if (errors.length > 0 || !document || !isMap(document.contents)) {
    return { ok: false, errors };
  }

  return {
    ok: true,
    document,
    root: document.contents,
    lineCounter,
  };
}

export function validateCloudInitYaml(
  source: string,
): CloudInitValidationResult {
  const parsed = parseCloudInit(source);
  return parsed.ok ? { ok: true, value: source } : parsed;
}

function splitNonEmptyLines(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
}

function appendPublicKey(
  key: string,
  label: string,
  keys: string[],
  seen: Set<string>,
  errors: string[],
): void {
  if (PRIVATE_KEY_MARKER.test(key)) {
    errors.push(`${label} contains a private-key marker. Only public keys are allowed.`);
    return;
  }

  if (!OPENSSH_PUBLIC_KEY_PATTERN.test(key)) {
    errors.push(
      `${label} must use the OpenSSH format "type base64 [comment]".`,
    );
    return;
  }

  const [keyType, encodedKey] = key.split(/[\t ]+/, 2);
  if (decodeOpenSshAlgorithm(encodedKey) !== keyType) {
    errors.push(`${label} does not contain a valid OpenSSH public-key blob.`);
    return;
  }

  if (!seen.has(key)) {
    seen.add(key);
    keys.push(key);
  }
}

function decodeOpenSshAlgorithm(encodedKey: string): string | null {
  try {
    const decoded = atob(encodedKey);
    if (decoded.length < 5) {
      return null;
    }

    const bytes = Uint8Array.from(decoded, character => character.charCodeAt(0));
    const algorithmLength = new DataView(bytes.buffer).getUint32(0, false);
    const algorithmEnd = 4 + algorithmLength;
    if (algorithmLength === 0 || algorithmEnd >= bytes.length) {
      return null;
    }

    return String.fromCharCode(...bytes.slice(4, algorithmEnd));
  } catch {
    return null;
  }
}

function usesDefaultUser(node: unknown): boolean {
  if (isScalar(node)) {
    return node.value === "default";
  }
  if (!isSeq(node) || node.items.length === 0) {
    return false;
  }

  const firstUser = node.items[0];
  return isScalar(firstUser) && firstUser.value === "default";
}

function normalizeForm(form: CloudInitFormState): NormalizedForm | CloudInitFailure {
  const errors: string[] = [];

  if (form.username !== "" && !USERNAME_PATTERN.test(form.username)) {
    errors.push(
      "Username must match ^[a-z_][a-z0-9_-]{0,31}$ when provided.",
    );
  }

  if (form.sshPasswordAuthentication && form.password.length === 0) {
    errors.push(
      "Password is required when SSH password authentication is enabled.",
    );
  }

  const publicKeys: string[] = [];
  const seenPublicKeys = new Set<string>();

  form.selectedPublicKeys.forEach((value, index) => {
    const lines = splitNonEmptyLines(value);
    if (lines.length !== 1) {
      errors.push(`Selected SSH key ${index + 1} must contain exactly one public key.`);
      return;
    }
    appendPublicKey(
      lines[0],
      `Selected SSH key ${index + 1}`,
      publicKeys,
      seenPublicKeys,
      errors,
    );
  });

  form.manualPublicKeys.split(/\r?\n/).forEach((value, index) => {
    const key = value.trim();
    if (key === "") {
      return;
    }
    appendPublicKey(
      key,
      `Manual SSH key line ${index + 1}`,
      publicKeys,
      seenPublicKeys,
      errors,
    );
  });

  if (errors.length > 0) {
    return { ok: false, errors };
  }

  return {
    username: form.username,
    password: form.password,
    passwordExpires: form.passwordExpires,
    sshPasswordAuthentication: form.sshPasswordAuthentication,
    publicKeys,
    packageUpdate: form.packageUpdate,
    packages: [...new Set(splitNonEmptyLines(form.packages))],
    script: form.script.replace(/\r\n?/g, "\n").replace(/\n+$/, ""),
  };
}

function createBlockMap(document: Document): YAMLMap {
  const map = document.createNode({});
  if (!isMap(map)) {
    throw new Error("Failed to create a YAML mapping.");
  }
  map.flow = false;
  return map;
}

function validateMergeCompatibility(
  root: YAMLMap,
  normalized: NormalizedForm,
  lineCounter: LineCounter,
):
  | { ok: true; userNode: unknown; chpasswdNode: unknown }
  | CloudInitFailure {
  const errors: string[] = [];
  const userNode = root.has("user") ? root.get("user", true) : undefined;
  const chpasswdNode = root.has("chpasswd")
    ? root.get("chpasswd", true)
    : undefined;
  const usersNode = root.has("users") ? root.get("users", true) : undefined;

  if (userNode !== undefined && !isMap(userNode)) {
    errors.push(
      formatPosition(
        lineCounter,
        nodeOffset(userNode),
        "The existing user value must be a mapping to update user.name.",
      ),
    );
  }
  if (chpasswdNode !== undefined && !isMap(chpasswdNode)) {
    errors.push(
      formatPosition(
        lineCounter,
        nodeOffset(chpasswdNode),
        "The existing chpasswd value must be a mapping to update chpasswd.expire.",
      ),
    );
  }

  const managesDefaultUser =
    normalized.username !== "" ||
    normalized.password !== "" ||
    normalized.publicKeys.length > 0;
  if (
    usersNode !== undefined &&
    managesDefaultUser &&
    !usesDefaultUser(usersNode)
  ) {
    errors.push(
      formatPosition(
        lineCounter,
        nodeOffset(usersNode),
        "The existing users value must keep default as its first user before applying default-user form settings.",
      ),
    );
  }

  if (isMap(chpasswdNode) && normalized.password !== "") {
    for (const key of ["users", "list"] as const) {
      if (chpasswdNode.has(key)) {
        errors.push(
          formatPosition(
            lineCounter,
            nodeOffset(chpasswdNode.get(key, true)),
            `The existing chpasswd.${key} conflicts with the form password. Remove it in YAML before applying the form.`,
          ),
        );
      }
    }
  }

  return errors.length > 0
    ? { ok: false, errors }
    : { ok: true, userNode, chpasswdNode };
}

export function mergeCloudInitForm(
  source: string,
  form: CloudInitFormState,
): CloudInitMergeResult {
  const parsed = parseCloudInit(source);
  if (!parsed.ok) {
    return parsed;
  }

  const normalized = normalizeForm(form);
  if (!("username" in normalized)) {
    return normalized;
  }

  const { document, root, lineCounter } = parsed;
  root.flow = false;
  const compatibility = validateMergeCompatibility(
    root,
    normalized,
    lineCounter,
  );
  if (!compatibility.ok) {
    return compatibility;
  }
  const { userNode, chpasswdNode } = compatibility;

  const userMap: YAMLMap | undefined = isMap(userNode)
    ? (userNode as YAMLMap)
    : undefined;
  if (normalized.username !== "") {
    const targetUserMap = userMap ?? createBlockMap(document);
    if (!userMap) {
      root.set("user", targetUserMap);
    }
    targetUserMap.set("name", normalized.username);
  } else if (userMap) {
    userMap.delete("name");
    if (userMap.items.length === 0) {
      root.delete("user");
    }
  }

  if (normalized.password !== "") {
    root.set("password", normalized.password);
  } else {
    root.delete("password");
  }

  const chpasswdMap: YAMLMap | undefined = isMap(chpasswdNode)
    ? (chpasswdNode as YAMLMap)
    : undefined;
  if (normalized.password !== "") {
    const targetChpasswdMap = chpasswdMap ?? createBlockMap(document);
    if (!chpasswdMap) {
      root.set("chpasswd", targetChpasswdMap);
    }
    targetChpasswdMap.set("expire", normalized.passwordExpires);
  } else if (chpasswdMap) {
    chpasswdMap.delete("expire");
    if (chpasswdMap.items.length === 0) {
      root.delete("chpasswd");
    }
  }

  root.set("ssh_pwauth", normalized.sshPasswordAuthentication);

  if (normalized.publicKeys.length > 0) {
    root.set("ssh_authorized_keys", normalized.publicKeys);
  } else {
    root.delete("ssh_authorized_keys");
  }

  if (normalized.packageUpdate) {
    root.set("package_update", true);
  } else {
    root.delete("package_update");
  }

  if (normalized.packages.length > 0) {
    root.set("packages", normalized.packages);
  } else {
    root.delete("packages");
  }

  if (normalized.script.trim() !== "") {
    const runcmd = document.createNode([normalized.script]);
    const scriptNode = isSeq(runcmd) ? runcmd.items[0] : undefined;
    if (!isSeq(runcmd) || !isScalar(scriptNode)) {
      return { ok: false, errors: ["Failed to create the runcmd YAML node."] };
    }
    scriptNode.type = Scalar.BLOCK_LITERAL;
    root.set("runcmd", runcmd);
  } else {
    root.delete("runcmd");
  }

  try {
    return { ok: true, value: document.toString({ lineWidth: 0 }) };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { ok: false, errors: [`Failed to serialize cloud-init YAML: ${message}`] };
  }
}
