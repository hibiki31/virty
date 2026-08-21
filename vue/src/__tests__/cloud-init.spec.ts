import {
  EMPTY_CLOUD_CONFIG,
  createCloudInitFormState,
  mergeCloudInitForm,
  validateCloudInitYaml,
} from "@/composables/cloudInit";
import { parse } from "yaml";
import { describe, expect, it } from "vitest";

const ED25519_KEY =
  "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6 user@example";
const RSA_KEY =
  "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDCYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo= rsa@example";

function successfulValue(result: ReturnType<typeof mergeCloudInitForm>): string {
  if (!result.ok) {
    throw new Error(result.errors.join("\n"));
  }
  return result.value;
}

describe("cloud-init YAML helper", () => {
  it("有効な空設定と独立した初期フォームを返す", () => {
    const first = createCloudInitFormState();
    const second = createCloudInitFormState();

    first.selectedPublicKeys.push(ED25519_KEY);

    expect(second).toEqual({
      username: "",
      password: "",
      passwordExpires: false,
      sshPasswordAuthentication: false,
      selectedPublicKeys: [],
      manualPublicKeys: "",
      script: "",
    });
    expect(validateCloudInitYaml(EMPTY_CLOUD_CONFIG)).toEqual({
      ok: true,
      value: EMPTY_CLOUD_CONFIG,
    });
  });

  it("header、単一document、mapping rootを検証する", () => {
    const invalidHeader = validateCloudInitYaml(" #cloud-config\nfoo: bar\n");
    const multipleDocuments = validateCloudInitYaml(
      "#cloud-config\nfoo: bar\n---\nbaz: qux\n",
    );
    const sequenceRoot = validateCloudInitYaml("#cloud-config\n- value\n");

    expect(invalidHeader).toEqual({
      ok: false,
      errors: ["Line 1, column 1: The first line must be exactly #cloud-config."],
    });
    expect(multipleDocuments.ok).toBe(false);
    expect(
      multipleDocuments.ok ? [] : multipleDocuments.errors,
    ).toContainEqual(expect.stringContaining("exactly one YAML document"));
    expect(sequenceRoot.ok).toBe(false);
    expect(sequenceRoot.ok ? [] : sequenceRoot.errors).toContainEqual(
      expect.stringContaining("root must be a mapping"),
    );
  });

  it("YAMLのduplicate keyとsyntax errorへ行・列を付ける", () => {
    const duplicate = validateCloudInitYaml(
      "#cloud-config\nlocale: en_US\nlocale: ja_JP\n",
    );
    const syntax = validateCloudInitYaml("#cloud-config\npackages: [curl\n");

    expect(duplicate.ok).toBe(false);
    expect(duplicate.ok ? [] : duplicate.errors).toContainEqual(
      expect.stringMatching(/^Line \d+, column \d+: .*unique/i),
    );
    expect(syntax.ok).toBe(false);
    expect(syntax.ok ? [] : syntax.errors).toContainEqual(
      expect.stringMatching(/^Line \d+, column \d+:/),
    );
  });

  it("フォーム値をmergeし、未管理nodeとcommentを保持する", () => {
    const source = `#cloud-config
# root comment
timezone: Asia/Tokyo # keep timezone
user:
  name: old-user
  gecos: Existing User
chpasswd:
  expire: true
package_update: true
packages:
  - curl
  - vim
unowned:
  nested: true
`;
    const form = createCloudInitFormState();
    Object.assign(form, {
      username: "virty_user",
      password: 'a: "#secure" password',
      passwordExpires: false,
      sshPasswordAuthentication: true,
      selectedPublicKeys: [ED25519_KEY],
      manualPublicKeys: `  ${ED25519_KEY}  \n${RSA_KEY}\n`,
      script: "#!/bin/sh\necho hello\n",
    });

    const yaml = successfulValue(mergeCloudInitForm(source, form));
    const data = parse(yaml) as Record<string, unknown>;

    expect(yaml.startsWith("#cloud-config\n")).toBe(true);
    expect(yaml).toContain("# root comment");
    expect(yaml).toContain("# keep timezone");
    expect(data).toMatchObject({
      timezone: "Asia/Tokyo",
      user: { name: "virty_user", gecos: "Existing User" },
      password: 'a: "#secure" password',
      chpasswd: {
        expire: false,
      },
      ssh_pwauth: true,
      ssh_authorized_keys: [ED25519_KEY, RSA_KEY],
      package_update: true,
      packages: ["curl", "vim"],
      runcmd: ["#!/bin/sh\necho hello"],
      unowned: { nested: true },
    });
    expect(yaml).toMatch(/runcmd:\n\s+- \|/);
  });

  it("空のフォーム値は管理対象だけを削除し、空になった親だけを削除する", () => {
    const source = `#cloud-config
user:
  name: old-user
  gecos: Keep Me
chpasswd:
  expire: true
  list: keep-me
password: old-password
ssh_pwauth: true
ssh_authorized_keys:
  - ${ED25519_KEY}
package_update: true
packages:
  - curl
runcmd:
  - echo old
`;

    const yaml = successfulValue(
      mergeCloudInitForm(source, createCloudInitFormState()),
    );
    const data = parse(yaml) as Record<string, unknown>;

    expect(data).toMatchObject({
      user: { gecos: "Keep Me" },
      chpasswd: { list: "keep-me" },
      ssh_pwauth: false,
    });
    expect(data).not.toHaveProperty("password");
    expect(data).not.toHaveProperty("ssh_authorized_keys");
    expect(data).toHaveProperty("package_update", true);
    expect(data).toHaveProperty("packages", ["curl"]);
    expect(data).not.toHaveProperty("runcmd");

    const onlyOwnedParents = successfulValue(
      mergeCloudInitForm(
        "#cloud-config\nuser:\n  name: old\nchpasswd:\n  expire: true\n",
        createCloudInitFormState(),
      ),
    );
    const parents = parse(onlyOwnedParents) as Record<string, unknown>;
    expect(parents).not.toHaveProperty("user");
    expect(parents).not.toHaveProperty("chpasswd");
  });

  it("無効なフォーム入力と秘密鍵を拒否する", () => {
    const form = createCloudInitFormState();
    Object.assign(form, {
      username: "Invalid User",
      sshPasswordAuthentication: true,
      manualPublicKeys: "-----BEGIN OPENSSH PRIVATE KEY-----",
    });

    const result = mergeCloudInitForm(EMPTY_CLOUD_CONFIG, form);

    expect(result.ok).toBe(false);
    expect(result.ok ? [] : result.errors).toEqual(
      expect.arrayContaining([
        expect.stringContaining("Username must match"),
        expect.stringContaining("Password is required"),
        expect.stringContaining("private-key marker"),
      ]),
    );
  });

  it("OpenSSH形式ではない公開鍵を行単位で拒否する", () => {
    const form = createCloudInitFormState();
    form.manualPublicKeys =
      "ssh-ed25519 not.base64 user@example\nnot-a-key\nssh-ed25519 AAAA short";

    const result = mergeCloudInitForm(EMPTY_CLOUD_CONFIG, form);

    expect(result.ok).toBe(false);
    expect(result.ok ? [] : result.errors).toEqual([
      expect.stringContaining("Manual SSH key line 1"),
      expect.stringContaining("Manual SSH key line 2"),
      expect.stringContaining("Manual SSH key line 3"),
    ]);
  });

  it("YAML 1.1でbooleanになる文字列をquoted scalarとして出力する", () => {
    const form = createCloudInitFormState();
    form.username = "on";
    form.password = "yes";

    const yaml = successfulValue(mergeCloudInitForm(EMPTY_CLOUD_CONFIG, form));
    const data = parse(yaml, { version: "1.1" }) as {
      user: { name: unknown };
      password: unknown;
    };

    expect(data.user.name).toBe("on");
    expect(data.password).toBe("yes");
  });

  it("unknown YAML tagをwarningのまま許可しない", () => {
    const result = validateCloudInitYaml(
      "#cloud-config\ncustom: !unsupported value\n",
    );

    expect(result.ok).toBe(false);
    expect(result.ok ? [] : result.errors).toContainEqual(
      expect.stringMatching(/^Line 2, column \d+:/),
    );
  });

  it("default userを外すusers設定とformのaccount設定を競合として拒否する", () => {
    const form = createCloudInitFormState();
    form.username = "operator";

    const conflict = mergeCloudInitForm(
      "#cloud-config\nusers:\n  - name: custom-user\n",
      form,
    );
    const compatible = successfulValue(
      mergeCloudInitForm(
        "#cloud-config\nusers:\n  - default\n  - name: custom-user\n",
        form,
      ),
    );

    expect(conflict.ok).toBe(false);
    expect(conflict.ok ? [] : conflict.errors).toContainEqual(
      expect.stringContaining("must keep default as its first user"),
    );
    expect(parse(compatible, { version: "1.1" })).toMatchObject({
      users: ["default", { name: "custom-user" }],
      user: { name: "operator" },
    });
  });

  it("既存chpasswd credentialとform passwordの競合を拒否する", () => {
    const form = createCloudInitFormState();
    form.password = "new-password";

    const listConflict = mergeCloudInitForm(
      "#cloud-config\nchpasswd:\n  list: user:old-password\n",
      form,
    );
    const usersConflict = mergeCloudInitForm(
      "#cloud-config\nchpasswd:\n  users:\n    - name: user\n      password: old-password\n      type: text\n",
      form,
    );

    expect(listConflict.ok).toBe(false);
    expect(listConflict.ok ? [] : listConflict.errors).toContainEqual(
      expect.stringContaining("chpasswd.list conflicts"),
    );
    expect(usersConflict.ok).toBe(false);
    expect(usersConflict.ok ? [] : usersConflict.errors).toContainEqual(
      expect.stringContaining("chpasswd.users conflicts"),
    );
  });

  it("userまたはchpasswdがmappingでなければ上書きしない", () => {
    const userResult = mergeCloudInitForm(
      "#cloud-config\nuser: ubuntu\n",
      createCloudInitFormState(),
    );
    const chpasswdResult = mergeCloudInitForm(
      "#cloud-config\nchpasswd: false\n",
      createCloudInitFormState(),
    );

    expect(userResult.ok).toBe(false);
    expect(userResult.ok ? [] : userResult.errors).toContainEqual(
      expect.stringMatching(/^Line 2, column \d+: .*user value must be a mapping/),
    );
    expect(chpasswdResult.ok).toBe(false);
    expect(chpasswdResult.ok ? [] : chpasswdResult.errors).toContainEqual(
      expect.stringMatching(/^Line 2, column \d+: .*chpasswd value must be a mapping/),
    );
  });

  it("guided formの対象外であるpackage設定を保持する", () => {
    const yaml = successfulValue(
      mergeCloudInitForm(
        "#cloud-config\npackage_update: true\npackages:\n  - curl\ntimezone: UTC\n",
        createCloudInitFormState(),
      ),
    );

    expect(parse(yaml)).toEqual({
      package_update: true,
      packages: ["curl"],
      timezone: "UTC",
      ssh_pwauth: false,
    });
  });
});
