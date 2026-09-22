import { TranslationError, translationRef } from "@/composables/i18n";

type JsonCredentialDescriptor = Omit<PublicKeyCredentialDescriptor, "id"> & {
  id: string;
};

type JsonCreationOptions = Omit<
  PublicKeyCredentialCreationOptions,
  "challenge" | "user" | "excludeCredentials"
> & {
  challenge: string;
  user: Omit<PublicKeyCredentialUserEntity, "id"> & { id: string };
  excludeCredentials?: JsonCredentialDescriptor[];
};

type JsonRequestOptions = Omit<
  PublicKeyCredentialRequestOptions,
  "challenge" | "allowCredentials"
> & {
  challenge: string;
  allowCredentials?: JsonCredentialDescriptor[];
};

export type WebAuthnCredentialJson = {
  id: string;
  rawId: string;
  type: "public-key";
  response: Record<string, string | string[]>;
  clientExtensionResults: Record<string, unknown>;
  authenticatorAttachment: string | null;
};

function decodeBase64Url(value: string): ArrayBuffer {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
  const bytes = Uint8Array.from(atob(padded), (character) => character.charCodeAt(0));
  return bytes.buffer;
}

function encodeBase64Url(value: ArrayBuffer): string {
  const bytes = new Uint8Array(value);
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function convertDescriptors(
  descriptors: JsonCredentialDescriptor[] | undefined,
): PublicKeyCredentialDescriptor[] | undefined {
  return descriptors?.map((descriptor) => ({
    ...descriptor,
    id: decodeBase64Url(descriptor.id),
  }));
}

export async function createWebAuthnCredential(
  options: Record<string, unknown>,
): Promise<WebAuthnCredentialJson> {
  const json = options as JsonCreationOptions;
  const publicKey: PublicKeyCredentialCreationOptions = {
    ...json,
    challenge: decodeBase64Url(json.challenge),
    user: { ...json.user, id: decodeBase64Url(json.user.id) },
    excludeCredentials: convertDescriptors(json.excludeCredentials),
  };
  const credential = await navigator.credentials.create({ publicKey });
  if (!(credential instanceof PublicKeyCredential)) {
    throw new TranslationError(translationRef("webauthn.credentialFailed"));
  }
  const response = credential.response as AuthenticatorAttestationResponse;
  return {
    id: credential.id,
    rawId: encodeBase64Url(credential.rawId),
    type: "public-key",
    response: {
      attestationObject: encodeBase64Url(response.attestationObject),
      clientDataJSON: encodeBase64Url(response.clientDataJSON),
      transports: response.getTransports?.() ?? [],
    },
    clientExtensionResults: { ...credential.getClientExtensionResults() },
    authenticatorAttachment: credential.authenticatorAttachment,
  };
}

export async function getWebAuthnAssertion(
  options: Record<string, unknown>,
): Promise<WebAuthnCredentialJson> {
  const json = options as JsonRequestOptions;
  const publicKey: PublicKeyCredentialRequestOptions = {
    ...json,
    challenge: decodeBase64Url(json.challenge),
    allowCredentials: convertDescriptors(json.allowCredentials),
  };
  const credential = await navigator.credentials.get({ publicKey });
  if (!(credential instanceof PublicKeyCredential)) {
    throw new TranslationError(translationRef("webauthn.assertionFailed"));
  }
  const response = credential.response as AuthenticatorAssertionResponse;
  const serializedResponse: Record<string, string> = {
    authenticatorData: encodeBase64Url(response.authenticatorData),
    clientDataJSON: encodeBase64Url(response.clientDataJSON),
    signature: encodeBase64Url(response.signature),
  };
  if (response.userHandle) {
    serializedResponse.userHandle = encodeBase64Url(response.userHandle);
  }
  return {
    id: credential.id,
    rawId: encodeBase64Url(credential.rawId),
    type: "public-key",
    response: serializedResponse,
    clientExtensionResults: { ...credential.getClientExtensionResults() },
    authenticatorAttachment: credential.authenticatorAttachment,
  };
}
