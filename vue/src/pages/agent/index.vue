<template>
  <div class="d-flex flex-column ga-4">
    <div class="d-flex align-center">
      <div>
        <h1 class="text-h5">{{ t("agent.heading") }}</h1>
        <p class="text-body-2 text-medium-emphasis">
          {{ t("agent.description") }}
        </p>
      </div>
      <v-spacer />
      <v-btn
        prepend-icon="mdi-refresh"
        variant="text"
        :loading="loading"
        @click="reload"
      >
        {{ t("agent.actions.reload") }}
      </v-btn>
    </div>

    <v-alert
      v-if="message"
      :type="message.type"
      closable
      variant="tonal"
      @click:close="message = null"
    >
      {{ messageText }}
    </v-alert>

    <v-alert type="warning" variant="tonal">
      {{ t("agent.warnings.mutation") }}
    </v-alert>

    <v-row>
      <v-col cols="12" lg="5">
        <v-card :title="t('agent.webauthn.title')" height="100%">
          <v-card-text>
            <p class="text-body-2 mb-4">
              {{ t("agent.webauthn.description") }}
            </p>
            <v-text-field
              v-model="registration.credentialName"
              :label="t('agent.webauthn.credentialName')"
              maxlength="128"
              autocomplete="webauthn"
            />
            <v-text-field
              v-model="registration.currentPassword"
              :label="t('agent.webauthn.currentPassword')"
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
              {{ t("agent.actions.register") }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" lg="7">
        <v-card :title="t('agent.control.title')" height="100%">
          <v-card-text v-if="control">
            <v-switch
              v-model="controlForm.mutationsEnabled"
              color="error"
              :label="t('agent.control.mutationsEnabled')"
              hide-details
            />
            <v-switch
              v-model="controlForm.shadowMode"
              color="warning"
              :label="t('agent.control.shadowMode')"
              hide-details
            />
            <v-select
              v-model="controlForm.enabledRiskLevels"
              class="mt-3"
              :items="riskLevels"
              :label="t('agent.control.enabledRiskLevels')"
              multiple
              chips
            />
            <v-switch
              v-model="controlForm.allowDeleteWithoutRecovery"
              color="error"
              :label="t('agent.control.allowDeleteWithoutRecovery')"
              hide-details
            />
            <v-switch
              v-model="controlForm.allowNetworkChangeWithoutOob"
              color="error"
              :label="t('agent.control.allowNetworkChangeWithoutOob')"
              hide-details
            />
            <v-textarea
              v-model="controlForm.reason"
              class="mt-3"
              :label="t('agent.control.reason')"
              maxlength="2000"
              rows="2"
              auto-grow
            />
            <p class="text-caption text-medium-emphasis">
              {{ t("agent.control.lastUpdated", {
                date: displayDate(control.updatedAt),
                user: control.updatedBy || t("common.values.unknown"),
              }) }}
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
              {{ t("agent.actions.applyWithWebAuthn") }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-card :title="t('agent.pairings.title')">
      <v-card-text v-if="pairings.length === 0" class="text-medium-emphasis">
        {{ t("agent.pairings.empty") }}
      </v-card-text>
      <v-table v-else>
        <thead>
          <tr>
            <th>{{ t("agent.pairings.device") }}</th>
            <th>{{ t("agent.pairings.requestedScopes") }}</th>
            <th>{{ t("agent.pairings.expires") }}</th>
            <th>{{ t("agent.pairings.pairingCode") }}</th>
            <th>{{ t("agent.table.actions") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pairing in pairings" :key="pairing.pairingId">
            <td>
              {{ pairing.deviceName }}
              <div class="text-caption text-medium-emphasis">{{ pairing.deviceId }}</div>
            </td>
            <td>{{ agentScopeListLabel(pairing.requestedScopes) }}</td>
            <td>{{ displayDate(pairing.expiresAt) }}</td>
            <td style="min-width: 16rem">
              <v-text-field
                v-model="pairingCodes[pairing.pairingId]"
                :label="t('agent.pairings.codeLabel')"
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
                {{ t("agent.actions.approve") }}
              </v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <v-card :title="t('agent.leaseRequests.title')">
      <v-card-text v-if="leaseRequests.length === 0" class="text-medium-emphasis">
        {{ t("agent.leaseRequests.empty") }}
      </v-card-text>
      <v-table v-else>
        <thead>
          <tr>
            <th>{{ t("agent.leaseRequests.devicePrincipal") }}</th>
            <th>{{ t("agent.leaseRequests.constraints") }}</th>
            <th>{{ t("agent.leaseRequests.riskGrants") }}</th>
            <th>{{ t("agent.leaseRequests.expires") }}</th>
            <th>{{ t("agent.table.actions") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in leaseRequests" :key="request.requestId">
            <td>
              {{ request.deviceName }} / {{ request.principalId }}
              <div class="text-caption text-medium-emphasis">{{ request.deviceId }}</div>
            </td>
            <td>
              <div>{{ agentScopeListLabel(request.requestedScopes) }}</div>
              <div class="text-caption">
                {{ t("agent.leaseRequests.projects", {
                  projects: request.projectIds.join(", ") || t("common.values.all"),
                }) }}
              </div>
              <div class="text-caption">
                {{ t("agent.leaseRequests.nodes", {
                  nodes: request.nodeIds.join(", ") || t("common.values.all"),
                }) }}
              </div>
            </td>
            <td>
              {{ t("agent.leaseRequests.maxMutations", {
                count: formatNumber(request.maxMutations),
              }, request.maxMutations) }}
              <div class="text-caption">
                {{ t("agent.leaseRequests.riskDetails", {
                  destructive: booleanLabel(request.allowDestructive),
                  deleteWithoutRecovery: booleanLabel(request.allowDeleteWithoutRecovery),
                  networkWithoutOob: booleanLabel(request.allowNetworkChangeWithoutOob),
                }) }}
              </div>
            </td>
            <td>{{ displayDate(request.expiresAt) }}</td>
            <td>
              <v-btn
                color="primary"
                size="small"
                :loading="busy === `lease-request:${request.requestId}`"
                @click="approveLease(request)"
              >
                {{ t("agent.actions.approve") }}
              </v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <v-card :title="t('agent.unknownOperations.title')">
      <v-alert class="ma-4 mb-0" type="warning" variant="tonal">
        {{ t("agent.warnings.reconciliation") }}
      </v-alert>
      <v-card-text v-if="unknownOperations.length === 0" class="text-medium-emphasis">
        {{ t("agent.unknownOperations.empty") }}
      </v-card-text>
      <v-table v-else>
        <thead>
          <tr>
            <th>{{ t("agent.unknownOperations.operationAction") }}</th>
            <th>{{ t("agent.unknownOperations.lastMessage") }}</th>
            <th>{{ t("agent.unknownOperations.reason") }}</th>
            <th>{{ t("agent.unknownOperations.result") }}</th>
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
                :label="t('agent.unknownOperations.reasonLabel')"
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
                {{ t("agent.actions.effectConfirmed") }}
              </v-btn>
              <v-btn
                color="warning"
                size="small"
                variant="tonal"
                :loading="busy === `reconcile:${operation.operationId}:effect_absent`"
                :disabled="!reconciliationReasons[operation.operationId]?.trim()"
                @click="reconcileOperation(operation, 'effect_absent')"
              >
                {{ t("agent.actions.effectAbsent") }}
              </v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <v-row>
      <v-col cols="12" xl="6">
        <v-card :title="t('agent.devices.title')" height="100%">
          <v-card-text>
            <v-textarea
              v-model="managementReason"
              :label="t('agent.devices.reasonLabel')"
              maxlength="2000"
              rows="2"
              auto-grow
            />
          </v-card-text>
          <v-table>
            <thead>
              <tr>
                <th>{{ t("agent.devices.device") }}</th>
                <th>{{ t("agent.devices.status") }}</th>
                <th>{{ t("agent.devices.scopes") }}</th>
                <th>{{ t("agent.table.actions") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="device in devices" :key="device.id">
                <td>
                  {{ device.name }}
                  <div class="text-caption text-medium-emphasis">{{ device.id }}</div>
                </td>
                <td>
                  {{ agentStatusLabel(device.status) }}
                  <v-chip v-if="device.breakerOpenedAt" color="error" size="x-small">
                    {{ t("agent.devices.breakerOpen") }}
                  </v-chip>
                </td>
                <td>{{ agentScopeListLabel(device.allowedScopes) }}</td>
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
                    {{ t("agent.actions.resetBreaker") }}
                  </v-btn>
                  <v-btn
                    color="error"
                    size="small"
                    variant="tonal"
                    :loading="busy === `device:${device.id}`"
                    :disabled="device.status === 'revoked' || !managementReason.trim()"
                    @click="revokeDevice(device)"
                  >
                    {{ t("agent.actions.revoke") }}
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>

      <v-col cols="12" xl="6">
        <v-card :title="t('agent.leases.title')" height="100%">
          <v-table>
            <thead>
              <tr>
                <th>{{ t("agent.leases.lease") }}</th>
                <th>{{ t("agent.leases.usageExpiry") }}</th>
                <th>{{ t("agent.leases.scopes") }}</th>
                <th>{{ t("agent.table.actions") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lease in leases" :key="lease.leaseId">
                <td>
                  {{ lease.leaseId }}
                  <div class="text-caption">
                    {{ t("agent.leases.device", { device: lease.deviceId }) }}
                  </div>
                </td>
                <td>
                  {{ formatNumber(lease.mutationsUsed) }} / {{ formatNumber(lease.maxMutations) }}
                  <div class="text-caption">{{ displayDate(lease.expiresAt) }}</div>
                  <v-chip v-if="lease.revokedAt" color="error" size="x-small">
                    {{ t("agent.leases.revoked") }}
                  </v-chip>
                </td>
                <td>{{ agentScopeListLabel(lease.scopes) }}</td>
                <td>
                  <v-btn
                    color="error"
                    size="small"
                    variant="tonal"
                    :loading="busy === `lease:${lease.leaseId}`"
                    :disabled="Boolean(lease.revokedAt) || !managementReason.trim()"
                    @click="revokeLease(lease)"
                  >
                    {{ t("agent.actions.revoke") }}
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
  titleKey: agent.documentTitle
  requiresAdmin: true
</route>

<script lang="ts" setup>
import { apiClient } from "@/api";
import {
  createWebAuthnCredential,
  getWebAuthnAssertion,
} from "@/composables/webauthn";
import {
  formatNotificationText,
  notificationContentFromError,
  type NotificationContent,
} from "@/composables/notify";
import {
  agentScopeListLabel,
  agentStatusLabel,
  booleanLabel,
  formatDateTime,
  formatNumber,
  translationRef,
} from "@/composables/i18n";
import { useI18n } from "vue-i18n";

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

const { t } = useI18n({ useScope: "global" });

const loading = ref(false);
const busy = ref<string | null>(null);
const message = ref<{
  type: "success" | "error" | "warning";
  content: NotificationContent;
} | null>(null);
const messageText = computed(() =>
  message.value ? formatNotificationText(message.value.content) : "",
);
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

function displayDate(value: string | null | undefined): string {
  return formatDateTime(value, "medium") || t("common.values.unavailable");
}

function showError(error: unknown): void {
  message.value = { type: "error", content: notificationContentFromError(error) };
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
    message.value = {
      type: "success",
      content: translationRef("agent.notifications.webauthnRegistered"),
    };
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
    message.value = {
      type: "success",
      content: translationRef("agent.notifications.pairingApproved", {
        device: pairing.deviceName,
      }),
    };
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
    message.value = {
      type: "success",
      content: translationRef("agent.notifications.leaseApproved", {
        device: request.deviceName,
      }),
    };
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
    message.value = {
      type: "success",
      content: translationRef("agent.notifications.controlUpdated"),
    };
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
    message.value = {
      type: "success",
      content: translationRef("agent.notifications.deviceRevoked", { device: device.name }),
    };
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
    message.value = {
      type: "success",
      content: translationRef("agent.notifications.breakerReset", { device: device.name }),
    };
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
    message.value = {
      type: "success",
      content: translationRef("agent.notifications.leaseRevoked", { lease: lease.leaseId }),
    };
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
      content: translationRef("agent.notifications.operationReconciled", {
        operation: operation.operationId,
      }),
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
