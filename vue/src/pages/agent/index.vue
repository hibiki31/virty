<template>
  <div class="d-flex flex-column ga-4">
    <div class="d-flex align-center">
      <div>
        <h1 class="text-h5">Agent control</h1>
        <p class="text-body-2 text-medium-emphasis">
          Codex端末の登録、短命lease、mutation停止をWebAuthnで管理します。
        </p>
      </div>
      <v-spacer />
      <v-btn
        prepend-icon="mdi-refresh"
        variant="text"
        :loading="loading"
        @click="reload"
      >
        再読込
      </v-btn>
    </div>

    <v-alert
      v-if="message"
      :type="message.type"
      closable
      variant="tonal"
      @click:close="message = null"
    >
      {{ message.text }}
    </v-alert>

    <v-alert type="warning" variant="tonal">
      mutationを有効化すると、lease範囲内の操作は追加確認なしで実行されます。削除やnetwork変更は
      backup・帯域外復旧がない場合に元へ戻せません。
    </v-alert>

    <v-row>
      <v-col cols="12" lg="5">
        <v-card title="WebAuthn credential" height="100%">
          <v-card-text>
            <p class="text-body-2 mb-4">
              pairingや停止操作の承認に使うsecurity keyまたはplatform authenticatorを登録します。
              現在のpasswordは再認証だけに使われ、保存されません。
            </p>
            <v-text-field
              v-model="registration.credentialName"
              label="Credential name"
              maxlength="128"
              autocomplete="webauthn"
            />
            <v-text-field
              v-model="registration.currentPassword"
              label="Current password"
              type="password"
              maxlength="128"
              autocomplete="current-password"
            />
          </v-card-text>
          <v-card-actions>
            <v-btn
              color="primary"
              prepend-icon="mdi-key-chain"
              :loading="busy === 'webauthn-register'"
              :disabled="!registration.credentialName || !registration.currentPassword"
              @click="registerWebAuthn"
            >
              登録
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" lg="7">
        <v-card title="Global mutation control" height="100%">
          <v-card-text v-if="control">
            <v-switch
              v-model="controlForm.mutationsEnabled"
              color="error"
              label="Agent mutationを有効化"
              hide-details
            />
            <v-switch
              v-model="controlForm.shadowMode"
              color="warning"
              label="Shadow / read-only mode"
              hide-details
            />
            <v-select
              v-model="controlForm.enabledRiskLevels"
              class="mt-3"
              :items="riskLevels"
              label="有効なrisk level"
              multiple
              chips
            />
            <v-switch
              v-model="controlForm.allowDeleteWithoutRecovery"
              color="error"
              label="復旧手段なしの削除を許可"
              hide-details
            />
            <v-switch
              v-model="controlForm.allowNetworkChangeWithoutOob"
              color="error"
              label="帯域外復旧なしのnetwork変更を許可"
              hide-details
            />
            <v-textarea
              v-model="controlForm.reason"
              class="mt-3"
              label="変更理由（監査ログへ記録）"
              maxlength="2000"
              rows="2"
              auto-grow
            />
            <p class="text-caption text-medium-emphasis">
              最終更新: {{ formatDate(control.updatedAt) }} / {{ control.updatedBy || "-" }}
            </p>
          </v-card-text>
          <v-card-text v-else>
            <v-skeleton-loader type="paragraph" />
          </v-card-text>
          <v-card-actions>
            <v-btn
              color="error"
              prepend-icon="mdi-shield-key"
              :loading="busy === 'control'"
              :disabled="!control || !controlForm.reason.trim()"
              @click="updateControl"
            >
              WebAuthnで反映
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-card title="Pending device pairings">
      <v-card-text v-if="pairings.length === 0" class="text-medium-emphasis">
        承認待ちの端末はありません。
      </v-card-text>
      <v-table v-else>
        <thead>
          <tr>
            <th>Device</th>
            <th>Requested scopes</th>
            <th>Expires</th>
            <th>Pairing code</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr v-for="pairing in pairings" :key="pairing.pairingId">
            <td>
              {{ pairing.deviceName }}
              <div class="text-caption text-medium-emphasis">{{ pairing.deviceId }}</div>
            </td>
            <td>{{ pairing.requestedScopes.join(", ") }}</td>
            <td>{{ formatDate(pairing.expiresAt) }}</td>
            <td style="min-width: 16rem">
              <v-text-field
                v-model="pairingCodes[pairing.pairingId]"
                label="Helperに表示されたcode"
                density="compact"
                hide-details
                autocomplete="off"
              />
            </td>
            <td>
              <v-btn
                color="primary"
                size="small"
                :loading="busy === `pairing:${pairing.pairingId}`"
                :disabled="!pairingCodes[pairing.pairingId]"
                @click="approvePairing(pairing)"
              >
                承認
              </v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <v-card title="Pending capability leases">
      <v-card-text v-if="leaseRequests.length === 0" class="text-medium-emphasis">
        承認待ちのleaseはありません。
      </v-card-text>
      <v-table v-else>
        <thead>
          <tr>
            <th>Device / principal</th>
            <th>Scope and target constraints</th>
            <th>Risk grants</th>
            <th>Expires</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in leaseRequests" :key="request.requestId">
            <td>
              {{ request.deviceName }} / {{ request.principalId }}
              <div class="text-caption text-medium-emphasis">{{ request.deviceId }}</div>
            </td>
            <td>
              <div>{{ request.requestedScopes.join(", ") }}</div>
              <div class="text-caption">Projects: {{ request.projectIds.join(", ") || "all" }}</div>
              <div class="text-caption">Nodes: {{ request.nodeIds.join(", ") || "all" }}</div>
            </td>
            <td>
              max {{ request.maxMutations }} mutations
              <div class="text-caption">
                destructive={{ request.allowDestructive }}, delete-without-recovery={{
                  request.allowDeleteWithoutRecovery
                }}, network-without-OOB={{ request.allowNetworkChangeWithoutOob }}
              </div>
            </td>
            <td>{{ formatDate(request.expiresAt) }}</td>
            <td>
              <v-btn
                color="primary"
                size="small"
                :loading="busy === `lease-request:${request.requestId}`"
                @click="approveLease(request)"
              >
                承認
              </v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <v-card title="Unknown operations">
      <v-alert class="ma-4 mb-0" type="warning" variant="tonal">
        外部基盤の実状態を確認してから結果を確定してください。確認前の再実行は、同じ副作用を
        二重に発生させる可能性があります。
      </v-alert>
      <v-card-text v-if="unknownOperations.length === 0" class="text-medium-emphasis">
        整合確認待ちのoperationはありません。
      </v-card-text>
      <v-table v-else>
        <thead>
          <tr>
            <th>Operation / action</th>
            <th>Last message</th>
            <th>確認理由</th>
            <th>確認結果</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="operation in unknownOperations" :key="operation.operationId">
            <td>
              {{ operation.action }}
              <div class="text-caption text-medium-emphasis">{{ operation.operationId }}</div>
            </td>
            <td>{{ operation.message || "-" }}</td>
            <td style="min-width: 20rem">
              <v-textarea
                v-model="reconciliationReasons[operation.operationId]"
                label="実状態を確認した方法と根拠"
                maxlength="2000"
                rows="2"
                auto-grow
                hide-details
              />
            </td>
            <td class="text-no-wrap">
              <v-btn
                class="mr-2"
                color="success"
                size="small"
                variant="tonal"
                :loading="busy === `reconcile:${operation.operationId}:effect_confirmed`"
                :disabled="!reconciliationReasons[operation.operationId]?.trim()"
                @click="reconcileOperation(operation, 'effect_confirmed')"
              >
                効果あり
              </v-btn>
              <v-btn
                color="warning"
                size="small"
                variant="tonal"
                :loading="busy === `reconcile:${operation.operationId}:effect_absent`"
                :disabled="!reconciliationReasons[operation.operationId]?.trim()"
                @click="reconcileOperation(operation, 'effect_absent')"
              >
                効果なし
              </v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <v-row>
      <v-col cols="12" xl="6">
        <v-card title="Paired devices" height="100%">
          <v-card-text>
            <v-textarea
              v-model="managementReason"
              label="失効・breaker reset理由（監査ログへ記録）"
              maxlength="2000"
              rows="2"
              auto-grow
            />
          </v-card-text>
          <v-table>
            <thead>
              <tr>
                <th>Device</th>
                <th>Status</th>
                <th>Scopes</th>
                <th />
              </tr>
            </thead>
            <tbody>
              <tr v-for="device in devices" :key="device.id">
                <td>
                  {{ device.name }}
                  <div class="text-caption text-medium-emphasis">{{ device.id }}</div>
                </td>
                <td>
                  {{ device.status }}
                  <v-chip v-if="device.breakerOpenedAt" color="error" size="x-small">
                    breaker open
                  </v-chip>
                </td>
                <td>{{ device.allowedScopes.join(", ") }}</td>
                <td class="text-no-wrap">
                  <v-btn
                    v-if="device.breakerOpenedAt"
                    class="mr-2"
                    size="small"
                    variant="tonal"
                    :loading="busy === `breaker:${device.id}`"
                    :disabled="!managementReason.trim()"
                    @click="resetBreaker(device)"
                  >
                    Breaker reset
                  </v-btn>
                  <v-btn
                    color="error"
                    size="small"
                    variant="tonal"
                    :loading="busy === `device:${device.id}`"
                    :disabled="device.status === 'revoked' || !managementReason.trim()"
                    @click="revokeDevice(device)"
                  >
                    失効
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>

      <v-col cols="12" xl="6">
        <v-card title="Capability leases" height="100%">
          <v-table>
            <thead>
              <tr>
                <th>Lease</th>
                <th>Usage / expiry</th>
                <th>Scopes</th>
                <th />
              </tr>
            </thead>
            <tbody>
              <tr v-for="lease in leases" :key="lease.leaseId">
                <td>
                  {{ lease.leaseId }}
                  <div class="text-caption">Device: {{ lease.deviceId }}</div>
                </td>
                <td>
                  {{ lease.mutationsUsed }} / {{ lease.maxMutations }}
                  <div class="text-caption">{{ formatDate(lease.expiresAt) }}</div>
                  <v-chip v-if="lease.revokedAt" color="error" size="x-small">revoked</v-chip>
                </td>
                <td>{{ lease.scopes.join(", ") }}</td>
                <td>
                  <v-btn
                    color="error"
                    size="small"
                    variant="tonal"
                    :loading="busy === `lease:${lease.leaseId}`"
                    :disabled="Boolean(lease.revokedAt) || !managementReason.trim()"
                    @click="revokeLease(lease)"
                  >
                    失効
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<route lang="yaml">
meta:
  title: Virty - Agent control
  requiresAdmin: true
</route>

<script lang="ts" setup>
import { apiClient } from "@/api";
import {
  createWebAuthnCredential,
  getWebAuthnAssertion,
} from "@/composables/webauthn";

type Pairing = {
  pairingId: string;
  deviceId: string;
  deviceName: string;
  requestedScopes: string[];
  expiresAt: string;
};

type LeaseRequest = {
  requestId: string;
  deviceId: string;
  deviceName: string;
  principalId: string;
  requestedScopes: string[];
  projectIds: string[];
  nodeIds: string[];
  maxMutations: number;
  allowDestructive: boolean;
  allowDeleteWithoutRecovery: boolean;
  allowNetworkChangeWithoutOob: boolean;
  expiresAt: string;
};

type Device = {
  id: string;
  name: string;
  status: string;
  allowedScopes: string[];
  breakerOpenedAt?: string | null;
};

type Lease = {
  leaseId: string;
  deviceId: string;
  scopes: string[];
  expiresAt: string;
  revokedAt?: string | null;
  mutationsUsed: number;
  maxMutations: number;
};

type RiskLevel = "R1" | "R2" | "R3";

type Control = {
  mutationsEnabled: boolean;
  shadowMode: boolean;
  enabledRiskLevels: RiskLevel[];
  allowDeleteWithoutRecovery: boolean;
  allowNetworkChangeWithoutOob: boolean;
  reason?: string | null;
  updatedAt: string;
  updatedBy?: string | null;
};

type UnknownOperation = {
  operationId: string;
  action: string;
  message?: string | null;
};

type WebAuthnOptions = {
  challengeId: string;
  publicKey: Record<string, unknown>;
};

const loading = ref(false);
const busy = ref<string | null>(null);
const message = ref<{ type: "success" | "error" | "warning"; text: string } | null>(null);
const pairings = ref<Pairing[]>([]);
const leaseRequests = ref<LeaseRequest[]>([]);
const devices = ref<Device[]>([]);
const leases = ref<Lease[]>([]);
const unknownOperations = ref<UnknownOperation[]>([]);
const control = ref<Control | null>(null);
const pairingCodes = reactive<Record<string, string>>({});
const reconciliationReasons = reactive<Record<string, string>>({});
const managementReason = ref("");
const riskLevels: RiskLevel[] = ["R1", "R2", "R3"];
const registration = reactive({ credentialName: "", currentPassword: "" });
const controlForm = reactive({
  mutationsEnabled: false,
  shadowMode: true,
  enabledRiskLevels: ["R1"] as RiskLevel[],
  allowDeleteWithoutRecovery: false,
  allowNetworkChangeWithoutOob: false,
  reason: "",
});

function formatDate(value: string | null | undefined): string {
  if (!value) return "-";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "short",
    timeStyle: "medium",
  }).format(new Date(value));
}

function errorText(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === "object" && error !== null) {
    const detail = (error as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (typeof detail === "object" && detail !== null) {
      const text = (detail as { message?: unknown }).message;
      if (typeof text === "string") return text;
    }
  }
  return "Agent API requestに失敗しました";
}

function showError(error: unknown): void {
  message.value = { type: "error", text: errorText(error) };
}

function requireData<T>(data: T | undefined, error: unknown): T {
  if (data === undefined) throw error;
  return data;
}

function applyControl(value: Control): void {
  control.value = value;
  controlForm.mutationsEnabled = value.mutationsEnabled;
  controlForm.shadowMode = value.shadowMode;
  controlForm.enabledRiskLevels = [...value.enabledRiskLevels];
  controlForm.allowDeleteWithoutRecovery = value.allowDeleteWithoutRecovery;
  controlForm.allowNetworkChangeWithoutOob = value.allowNetworkChangeWithoutOob;
  controlForm.reason = "";
}

async function reload(): Promise<void> {
  loading.value = true;
  try {
    const [
      pairingResponse,
      requestResponse,
      deviceResponse,
      leaseResponse,
      controlResponse,
      reconciliationResponse,
    ] =
      await Promise.all([
        apiClient.GET("/api/agent/v1/pairing-requests"),
        apiClient.GET("/api/agent/v1/lease-requests"),
        apiClient.GET("/api/agent/v1/devices"),
        apiClient.GET("/api/agent/v1/capability-leases"),
        apiClient.GET("/api/agent/v1/control"),
        apiClient.GET("/api/agent/v1/operation-reconciliations"),
      ]);
    pairings.value = requireData(pairingResponse.data, pairingResponse.error);
    leaseRequests.value = requireData(requestResponse.data, requestResponse.error);
    devices.value = requireData(deviceResponse.data, deviceResponse.error);
    leases.value = requireData(leaseResponse.data, leaseResponse.error);
    applyControl(requireData(controlResponse.data, controlResponse.error));
    unknownOperations.value = requireData(
      reconciliationResponse.data,
      reconciliationResponse.error,
    );
  } catch (error) {
    showError(error);
  } finally {
    loading.value = false;
  }
}

async function registerWebAuthn(): Promise<void> {
  busy.value = "webauthn-register";
  try {
    const optionsResponse = await apiClient.POST(
      "/api/agent/v1/webauthn/registration-options",
      { body: { ...registration } },
    );
    const options = requireData(optionsResponse.data, optionsResponse.error) as WebAuthnOptions;
    const credential = await createWebAuthnCredential(options.publicKey);
    const completeResponse = await apiClient.POST("/api/agent/v1/webauthn/registrations", {
      body: {
        challengeId: options.challengeId,
        credentialName: registration.credentialName,
        credential,
      },
    });
    requireData(completeResponse.data, completeResponse.error);
    registration.currentPassword = "";
    message.value = { type: "success", text: "WebAuthn credentialを登録しました" };
  } catch (error) {
    showError(error);
  } finally {
    busy.value = null;
  }
}

async function approvePairing(pairing: Pairing): Promise<void> {
  busy.value = `pairing:${pairing.pairingId}`;
  try {
    const pairingCode = pairingCodes[pairing.pairingId];
    const optionsResponse = await apiClient.POST(
      "/api/agent/v1/pairing-requests/{pairing_id}/approval-options",
      {
        params: { path: { pairing_id: pairing.pairingId } },
        body: { pairingCode },
      },
    );
    const options = requireData(optionsResponse.data, optionsResponse.error) as WebAuthnOptions;
    const credential = await getWebAuthnAssertion(options.publicKey);
    const approveResponse = await apiClient.POST(
      "/api/agent/v1/pairing-requests/{pairing_id}/approve",
      {
        params: { path: { pairing_id: pairing.pairingId } },
        body: { pairingCode, challengeId: options.challengeId, credential },
      },
    );
    requireData(approveResponse.data, approveResponse.error);
    delete pairingCodes[pairing.pairingId];
    message.value = { type: "success", text: `${pairing.deviceName}を承認しました` };
    await reload();
  } catch (error) {
    showError(error);
  } finally {
    busy.value = null;
  }
}

async function approveLease(request: LeaseRequest): Promise<void> {
  busy.value = `lease-request:${request.requestId}`;
  try {
    const optionsResponse = await apiClient.POST(
      "/api/agent/v1/lease-requests/{request_id}/approval-options",
      { params: { path: { request_id: request.requestId } } },
    );
    const options = requireData(optionsResponse.data, optionsResponse.error) as WebAuthnOptions;
    const credential = await getWebAuthnAssertion(options.publicKey);
    const approveResponse = await apiClient.POST(
      "/api/agent/v1/lease-requests/{request_id}/approve",
      {
        params: { path: { request_id: request.requestId } },
        body: { challengeId: options.challengeId, credential },
      },
    );
    requireData(approveResponse.data, approveResponse.error);
    message.value = { type: "success", text: `${request.deviceName}のleaseを承認しました` };
    await reload();
  } catch (error) {
    showError(error);
  } finally {
    busy.value = null;
  }
}

function controlChangeBody() {
  return {
    mutationsEnabled: controlForm.mutationsEnabled,
    shadowMode: controlForm.shadowMode,
    enabledRiskLevels: controlForm.enabledRiskLevels,
    allowDeleteWithoutRecovery: controlForm.allowDeleteWithoutRecovery,
    allowNetworkChangeWithoutOob: controlForm.allowNetworkChangeWithoutOob,
    reason: controlForm.reason,
  };
}

async function updateControl(): Promise<void> {
  busy.value = "control";
  try {
    const change = controlChangeBody();
    const optionsResponse = await apiClient.POST("/api/agent/v1/control/approval-options", {
      body: change,
    });
    const options = requireData(optionsResponse.data, optionsResponse.error) as WebAuthnOptions;
    const credential = await getWebAuthnAssertion(options.publicKey);
    const updateResponse = await apiClient.PUT("/api/agent/v1/control", {
      body: { ...change, challengeId: options.challengeId, credential },
    });
    applyControl(requireData(updateResponse.data, updateResponse.error));
    message.value = { type: "success", text: "Agent global controlを更新しました" };
  } catch (error) {
    showError(error);
  } finally {
    busy.value = null;
  }
}

async function revokeDevice(device: Device): Promise<void> {
  busy.value = `device:${device.id}`;
  try {
    const optionsResponse = await apiClient.POST(
      "/api/agent/v1/devices/{device_id}/revoke-options",
      { params: { path: { device_id: device.id } } },
    );
    const options = requireData(optionsResponse.data, optionsResponse.error) as WebAuthnOptions;
    const credential = await getWebAuthnAssertion(options.publicKey);
    const response = await apiClient.POST("/api/agent/v1/devices/{device_id}/revoke", {
      params: { path: { device_id: device.id } },
      body: {
        challengeId: options.challengeId,
        credential,
        reason: managementReason.value,
      },
    });
    requireData(response.data, response.error);
    message.value = { type: "success", text: `${device.name}を失効しました` };
    await reload();
  } catch (error) {
    showError(error);
  } finally {
    busy.value = null;
  }
}

async function resetBreaker(device: Device): Promise<void> {
  busy.value = `breaker:${device.id}`;
  try {
    const optionsResponse = await apiClient.POST(
      "/api/agent/v1/devices/{device_id}/breaker-reset-options",
      { params: { path: { device_id: device.id } } },
    );
    const options = requireData(optionsResponse.data, optionsResponse.error) as WebAuthnOptions;
    const credential = await getWebAuthnAssertion(options.publicKey);
    const response = await apiClient.POST(
      "/api/agent/v1/devices/{device_id}/breaker-reset",
      {
        params: { path: { device_id: device.id } },
        body: {
          challengeId: options.challengeId,
          credential,
          reason: managementReason.value,
        },
      },
    );
    requireData(response.data, response.error);
    message.value = { type: "success", text: `${device.name}のbreakerをresetしました` };
    await reload();
  } catch (error) {
    showError(error);
  } finally {
    busy.value = null;
  }
}

async function revokeLease(lease: Lease): Promise<void> {
  busy.value = `lease:${lease.leaseId}`;
  try {
    const optionsResponse = await apiClient.POST(
      "/api/agent/v1/capability-leases/{lease_id}/revoke-options",
      { params: { path: { lease_id: lease.leaseId } } },
    );
    const options = requireData(optionsResponse.data, optionsResponse.error) as WebAuthnOptions;
    const credential = await getWebAuthnAssertion(options.publicKey);
    const response = await apiClient.POST(
      "/api/agent/v1/capability-leases/{lease_id}/revoke",
      {
        params: { path: { lease_id: lease.leaseId } },
        body: {
          challengeId: options.challengeId,
          credential,
          reason: managementReason.value,
        },
      },
    );
    requireData(response.data, response.error);
    message.value = { type: "success", text: `${lease.leaseId}を失効しました` };
    await reload();
  } catch (error) {
    showError(error);
  } finally {
    busy.value = null;
  }
}

async function reconcileOperation(
  operation: UnknownOperation,
  resolution: "effect_confirmed" | "effect_absent",
): Promise<void> {
  busy.value = `reconcile:${operation.operationId}:${resolution}`;
  try {
    const reason = reconciliationReasons[operation.operationId]?.trim() || "";
    const body = { resolution, reason };
    const optionsResponse = await apiClient.POST(
      "/api/agent/v1/operation-reconciliations/{operation_id}/approval-options",
      {
        params: { path: { operation_id: operation.operationId } },
        body,
      },
    );
    const options = requireData(optionsResponse.data, optionsResponse.error) as WebAuthnOptions;
    const credential = await getWebAuthnAssertion(options.publicKey);
    const resolveResponse = await apiClient.POST(
      "/api/agent/v1/operation-reconciliations/{operation_id}/resolve",
      {
        params: { path: { operation_id: operation.operationId } },
        body: { ...body, challengeId: options.challengeId, credential },
      },
    );
    requireData(resolveResponse.data, resolveResponse.error);
    delete reconciliationReasons[operation.operationId];
    message.value = {
      type: "success",
      text: `${operation.operationId}の実状態を確定しました`,
    };
    await reload();
  } catch (error) {
    showError(error);
  } finally {
    busy.value = null;
  }
}

onMounted(reload);
</script>
