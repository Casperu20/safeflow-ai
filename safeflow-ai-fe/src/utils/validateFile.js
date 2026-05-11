import { UPLOAD_LIMITS } from "../constants/upload.js";

export function validateFile(file, inputType) {
  const maxFileSizeBytes = UPLOAD_LIMITS.maxFileSizeMb * 1024 * 1024;

  if (file.size > maxFileSizeBytes) {
    return { isValid: false, message: `File size must be under ${UPLOAD_LIMITS.maxFileSizeMb}MB.` };
  }

  const acceptedTypes = inputType === "pdf" ? UPLOAD_LIMITS.acceptedPdfTypes : UPLOAD_LIMITS.acceptedImageTypes;

  if (!acceptedTypes.includes(file.type)) {
    return { isValid: false, message: "Unsupported file type." };
  }

  return { isValid: true };
}
